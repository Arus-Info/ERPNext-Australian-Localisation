import json

import frappe


@frappe.whitelist()
def get_outstanding_invoices(filters):
	filters = json.loads(filters)
	print(filters)
	print(type(filters))
	data = frappe.db.sql(
		"""
		SELECT
			supplier_name, supplier,
			JSON_ARRAYAGG(JSON_OBJECT("name",name,"rounded_total", rounded_total,"outstanding_amount", outstanding_amount)) as purchase_invoice
		FROM `tabPurchase Invoice`
		WHERE
			status in ('Partly Paid', 'Unpaid', 'Overdue') and
			company = %(company)s
		GROUP BY supplier
		""",
		filters,
		as_dict=True,
	)
	return data


@frappe.whitelist()
def create_payment_batch(supplier_invoices):
	supplier_invoices = json.loads(supplier_invoices)

	for supplier in supplier_invoices:
		create_payment_entry(supplier, supplier_invoices[supplier])

		# print(si, i, invoices[i]["payment_amount"])


def create_payment_entry(supplier, invoices):
	payment_entry = frappe.new_doc("Payment Entry")

	payment_entry.update(
		{
			"payment_type": "Pay",
			"party_type": "Supplier",
			"party": supplier,
			"paid_from": "Bank Account - DC",
			"paid_amount": 0,
		}
	)

	for i in invoices:
		print(i, invoices[i])
		row = frappe.new_doc("Payment Entry Reference")
		row.update(
			{
				"reference_doctype": "Purchase Invoice",
				"reference_name": i,
				"allocated_amount": invoices[i]["payment_amount"],
			}
		)
		payment_entry.paid_amount += invoices[i]["payment_amount"]
		payment_entry.append("references", row)
	payment_entry.received_amount = payment_entry.paid_amount
	payment_entry.save()
