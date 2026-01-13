import frappe

from erpnext_australian_localisation.setup.create_properties import create_properties_for_bai2_file
from erpnext_australian_localisation.setup.install_fixtures import get_au_bank_statement_format


def execute():
	create_properties_for_bai2_file()
	rename_properties_for_bank_file()
	for record in get_au_bank_statement_format():
		create_or_update_format(record)


def rename_properties_for_bank_file():
	doctype = "Bank Account"
	fieldname = "file_format"
	new_label = "Payment File Format"
	# Get the Custom Field
	cf_name = f"{doctype}-{fieldname}"
	if frappe.db.exists("Custom Field", cf_name):
		frappe.db.set_value("Custom Field", cf_name, "label", new_label)

	else:
		frappe.logger("bank_file_setup").info(f"Custom Field '{cf_name}' not found")


def create_or_update_format(record):
	name = record.get("name")

	if frappe.db.exists("AU Bank Statement Format", name):
		doc = frappe.get_doc("AU Bank Statement Format", name)
	else:
		doc = frappe.new_doc("AU Bank Statement Format")
		doc.name = name  # _newname doctypes

	# Parent fields
	doc.credit_debit_mapping = record["credit_debit_mapping"]
	doc.date_format = record["date_format"]

	# 🔑 Correct child table fieldname
	child_field = "table_avar"

	# Clear + re-add child rows
	doc.set(child_field, [])

	for row in record["table_avar"]:
		doc.append(
			child_field,
			{
				"erpnext_column": row["erpnext_column"],
				"bank_statement_column": row["bank_statement_column"],
			},
		)
	doc.save()
