import frappe


def execute():
	frappe.db.delete(
		"Property Setter",
		{
			"doc_type": "Payment Entry",
			"field_name": "bank_account",
			"property": "reqd",
		},
	)

	frappe.clear_cache(doctype="Payment Entry")
