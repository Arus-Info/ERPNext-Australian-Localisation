import frappe


def execute():
	doctypes = ["Supplier", "Employee"]

	for doctype in doctypes:
		custom_field = f"{doctype}-bank_account_no"
		if not frappe.db.exists("Custom Field", custom_field):
			continue
		doc = frappe.get_doc("Custom Field", custom_field)
		doc.length = 10
		doc.save()
