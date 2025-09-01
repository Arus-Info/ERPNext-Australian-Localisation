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
		WITH
		supplier AS
		(
			SELECT
				name as supplier,
				lodgement_reference,
				case when (NULLIF(bank_account_no,'') IS NOT NULL and NULLIF(branch_code,'') IS NOT NULL) then 1 else 0 end as is_included
			FROM tabSupplier
		),

		payment_reference_entry AS
		(
			SELECT
				per.reference_name,
				pe.party,
				JSON_ARRAYAGG(
					JSON_OBJECT(
						"purchase_invoice", per.reference_name,
						"rounded_total", per.total_amount,
						"outstanding_amount", per.outstanding_amount,
						"payment_entry", per.parent,
						"allocated_amount", per.allocated_amount
					)
				) as reference_invoices
			FROM `tabPayment Entry Reference` as per
			LEFT JOIN `tabPayment Entry` as pe
			ON
				pe.name = per.parent
			WHERE
				per.docstatus = 0
				and per.reference_doctype = 'Purchase Invoice'
				and pe.company = '{filters["company"]}'
			GROUP BY pe.party
		)

		SELECT
			pi.supplier_name,
			pi.supplier,
			s.lodgement_reference,
			SUM(case when s.is_included then pi.outstanding_amount else 0 end) as total_outstanding,
			s.is_included,
			JSON_ARRAYAGG(
				case
				when per.reference_name IS NULL
				then
					JSON_OBJECT(
						"purchase_invoice", pi.name,
						"due_date", pi.due_date,
						"invoice_amount", pi.rounded_total,
						"invoice_currency", pi.currency,
						"rounded_total", pi.base_rounded_total,
						"outstanding_amount", pi.outstanding_amount
					)
				else JSON_OBJECT()
				end)
			as purchase_invoices,
			reference_invoices
		FROM `tabPurchase Invoice` as pi
		LEFT JOIN `tabPayment Entry Reference` as per
		ON
			per.reference_name = pi.name and per.docstatus = 0
		LEFT JOIN supplier as s
			ON s.supplier = pi.supplier
		LEFT JOIN payment_reference_entry
			ON payment_reference_entry.party = s.supplier
		WHERE
			pi.docstatus = 1
			and pi.outstanding_amount > 0
			and pi.company ='{filters["company"]}'
			and pi.owner like '{filters["created_by"]}%'
			{filters["condition_based_on_due_date"]}
		GROUP BY pi.supplier
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
