import frappe

from erpnext_australian_localisation.setup.create_properties import create_properties_for_bai2_file


def execute():
	create_properties_for_bai2_file()
	rename_properties_for_bank_file()


def rename_properties_for_bank_file():
	doctype = "Bank Account"
	fieldname = "file_format"
	new_label = "Payment File Format"
	# Get the Custom Field
	cf_name = f"{doctype}-{fieldname}"
	if frappe.db.exists("Custom Field", cf_name):
		frappe.db.set_value("Custom Field", cf_name, "label", new_label)

	else:
		print(f"Custom Field '{cf_name}' not found")
