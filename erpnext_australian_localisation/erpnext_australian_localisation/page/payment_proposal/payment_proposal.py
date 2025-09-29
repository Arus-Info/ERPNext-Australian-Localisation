import json

import frappe
from frappe import _

from erpnext_australian_localisation.erpnext_australian_localisation.doctype.payment_batch.payment_batch import (
	update_payment_batch,
)


@frappe.whitelist()
def get_unpaid_entries(filters):
	filters = json.loads(filters)

	filters["condition_based_on_due_date"] = ""
	if filters["from_due_date"]:
		filters["condition_based_on_due_date"] = f"and pi.due_date >= '{filters['from_due_date']}'"
	if filters["to_due_date"]:
		filters["condition_based_on_due_date"] += f" and pi.due_date <= '{filters['to_due_date']}'"

	if filters["party_type"] == "Supplier":
		query = get_query_for_supplier_outstanding_entries(filters)
	else:
		query = get_query_for_employee_outstanding_expense(filters)

	data = frappe.db.sql(query, as_dict=True)

	print(data)

	return data


@frappe.whitelist()
def create_payment_batch(party_entries, data):
	party_entries = json.loads(party_entries)
	data = json.loads(data)

	data["paid_from"] = frappe.db.get_value("Bank Account", data["bank_account"], "account")
	if not data["paid_from"]:
		frappe.throw(_("Bank Account {0} is not associated with any account.").format(data["bank_account"]))

	payment_batch = frappe.new_doc("Payment Batch")
	payment_batch.update(data)

	for party in party_entries:
		payment_entry = create_payment_entry(party, data)
		payment_batch = update_payment_batch(payment_entry, payment_batch)

	payment_batch.save()

	return payment_batch.name


def create_payment_entry(party, data):
	payment_entry = frappe.new_doc("Payment Entry")
	payment_entry.update(
		{
			**data,
			"payment_type": "Pay",
			"party": party["party"],
			"paid_amount": party["paid_amount"],
			"received_amount": party["paid_amount"],
			"reference_no": party["reference_no"],
			"source_exchange_rate": 1,
		}
	)

	for i in party["entries"]:
		row = frappe.new_doc("Payment Entry Reference")
		row.update(
			{
				"reference_doctype": data["reference_doctype"],
				"reference_name": i["entry_name"],
				"allocated_amount": i["allocated_amount"],
			}
		)
		payment_entry.append("references", row)

	payment_entry.save()

	return payment_entry.name


def get_query_for_supplier_outstanding_entries(filters):
	"""
	Returns the query for getting the Purchase Invoice under some conditions specified as follows.
	"""
	query = f"""
		WITH
		supplier AS
		(
			SELECT
				name as supplier,
				lodgement_reference,
				case when (NULLIF(bank_account_no,'') IS NOT NULL and NULLIF(branch_code,'') IS NOT NULL) then 1 else 0 end as is_included
			FROM tabSupplier
			WHERE is_allowed_in_pp = 1
		)

		SELECT
			pi.supplier_name as party_name,
			pi.supplier as party,
			s.lodgement_reference,
			SUM(case when s.is_included then pi.outstanding_amount else 0 end) as total_outstanding,
			s.is_included,
			JSON_ARRAYAGG(
				if(
					per.reference_name IS NULL,
					JSON_OBJECT(
						"entry_name", pi.name,
						"due_date", pi.due_date,
						"invoice_amount", pi.rounded_total,
						"invoice_currency", pi.currency,
						"rounded_total", pi.base_rounded_total,
						"outstanding_amount", pi.outstanding_amount
					),
					JSON_OBJECT())
			) as outstanding_entries,
			JSON_ARRAYAGG(
				if(
					per.reference_name IS NOT NULL,
					JSON_OBJECT(
						"entry_name", per.reference_name,
						"rounded_total", per.total_amount,
						"outstanding_amount", per.outstanding_amount,
						"payment_entry", per.parent,
						"allocated_amount", per.allocated_amount
					),
					JSON_OBJECT())
			) as reference_entries
		FROM supplier as s
		LEFT JOIN `tabPurchase Invoice` as pi
			ON s.supplier = pi.supplier
		LEFT JOIN `tabPayment Entry Reference` as per
			ON per.reference_name = pi.name and per.docstatus = 0
		WHERE
			pi.docstatus = 1
			and pi.outstanding_amount > 0
			and pi.company ='{filters["company"]}'
			and pi.owner like '{filters["created_by"]}%'
			{filters["condition_based_on_due_date"]}
		GROUP BY s.supplier
		"""
	return query


def get_query_for_employee_outstanding_expense(filters):
	query = f"""
	WITH
		employee AS
		(
			SELECT
				name as employee,
				lodgement_reference,
				case when (NULLIF(bank_account_no,'') IS NOT NULL and NULLIF(branch_code,'') IS NOT NULL) then 1 else 0 end as is_included
			FROM tabEmployee
			WHERE company = '{filters["company"]}'
		)

		SELECT
			ec.employee_name as party_name,
			ec.employee as party,
			e.lodgement_reference,
			SUM(case when e.is_included then ec.total_sanctioned_amount - ec.total_amount_reimbursed else 0 end) as total_outstanding,
			e.is_included,
			JSON_ARRAYAGG(
				if(
					per.reference_name IS NULL,
					JSON_OBJECT(
						"entry_name", ec.name,
						"rounded_total", ec.total_sanctioned_amount,
						"outstanding_amount", ec.total_sanctioned_amount - ec.total_amount_reimbursed
					),
					JSON_OBJECT())
			) as outstanding_entries,
			JSON_ARRAYAGG(
				if(
					per.reference_name IS NOT NULL,
					JSON_OBJECT(
						"entry_name", per.reference_name,
						"rounded_total", per.total_amount,
						"outstanding_amount", per.outstanding_amount,
						"payment_entry", per.parent,
						"allocated_amount", per.allocated_amount
					),
					JSON_OBJECT())
			) as reference_entries
		FROM employee as e
		LEFT JOIN `tabExpense Claim` as ec
			ON e.employee = ec.employee
		LEFT JOIN `tabPayment Entry Reference` as per
			ON per.reference_name = ec.name and per.docstatus = 0
		WHERE
			ec.docstatus = 1
			and ec.status = 'Unpaid'
			and ec.company ='{filters["company"]}'
			and ec.owner like '{filters["created_by"]}%'
			{filters["condition_based_on_due_date"]}
		GROUP BY e.employee
		"""
	return query
