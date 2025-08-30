import json

import frappe

from erpnext_australian_localisation.erpnext_australian_localisation.doctype.payment_batch.payment_batch import (
	update_payment_batch,
)


@frappe.whitelist()
def get_outstanding_invoices(filters):
	filters = json.loads(filters)

	filters["condition_based_on_due_date"] = ""
	if filters["from_due_date"]:
		filters["condition_based_on_due_date"] = f"and pi.due_date >= '{filters['from_due_date']}'"
	if filters["to_due_date"]:
		filters["condition_based_on_due_date"] += f" and pi.due_date <= '{filters['to_due_date']}'"

	query = f"""
		SELECT
			pi.supplier_name,
			pi.supplier,
			s.lodgement_reference,
			SUM(case when (NULLIF(s.bank_account_no,'') IS NOT NULL and NULLIF(s.branch_code,'') IS NOT NULL) then outstanding_amount else 0 end) as total_outstanding,
			case when (NULLIF(s.bank_account_no,'') IS NOT NULL and NULLIF(s.branch_code,'') IS NOT NULL) then 1 else 0 end as is_included,
			JSON_ARRAYAGG(
				JSON_OBJECT(
					"purchase_invoice", pi.name,
					"due_date", pi.due_date,
					"invoice_amount", pi.rounded_total,
					"invoice_currency", pi.currency,
					"rounded_total", pi.base_rounded_total,
					"outstanding_amount", pi.outstanding_amount,
					"allocated_amount", case when (NULLIF(s.bank_account_no,'') IS NOT NULL and NULLIF(s.branch_code,'') IS NOT NULL) then pi.outstanding_amount else 0 end
				)
			) as purchase_invoice
		FROM `tabPurchase Invoice` as pi
		LEFT JOIN tabSupplier as s
			ON s.name = pi.supplier
		WHERE
			status in ('Partly Paid', 'Unpaid', 'Overdue') and
			company ='{filters["company"]}'
			and pi.owner like '{filters["created_by"]}%'
			{filters["condition_based_on_due_date"]}
		GROUP BY supplier
		"""

	data = frappe.db.sql(query, as_dict=True)

	return data


@frappe.whitelist()
def create_payment_batch(supplier_invoices, data):
	supplier_invoices = json.loads(supplier_invoices)
	data = json.loads(data)

	payment_batch = frappe.new_doc("Payment Batch")
	payment_batch.update(data)

	for supplier in supplier_invoices:
		payment_entry = create_payment_entry(supplier, data)
		payment_batch = update_payment_batch(payment_entry, payment_batch)

	payment_batch.save()

	return payment_batch.name


def create_payment_entry(supplier, data):
	payment_entry = frappe.new_doc("Payment Entry")
	payment_entry.update(
		{
			**data,
			"payment_type": "Pay",
			"party_type": "Supplier",
			"party": supplier["supplier"],
			"paid_amount": supplier["paid_amount"],
			"received_amount": supplier["paid_amount"],
			"reference_no": supplier["reference_no"],
			"source_exchange_rate": 1,
		}
	)

	for i in supplier["invoices"]:
		row = frappe.new_doc("Payment Entry Reference")
		row.update(
			{
				"reference_doctype": "Purchase Invoice",
				"reference_name": i["purchase_invoice"],
				"allocated_amount": i["allocated_amount"],
			}
		)
		payment_entry.append("references", row)

	payment_entry.save()

	return payment_entry.name
