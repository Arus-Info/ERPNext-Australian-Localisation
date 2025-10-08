import frappe


def execute():
	frappe.db.set_value(
		"Custom Field",
		{"dt": "Bank Account", "fieldname": "file_format"},
		{"options": "-None-\nABA", "default": "-None-"},
	)
