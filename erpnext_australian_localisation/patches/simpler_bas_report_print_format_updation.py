import frappe

from erpnext_australian_localisation.setup.delete_properties import delete_custom_field

POS_INVOICE_CUSTOM_FIELDS = {
	"POS Invoice Item": [
		{
			"fieldname": "au_tax_code",
			"label": "AU Tax Code",
			"fieldtype": "Link",
			"options": "AU Tax Code",
			"read_only": 1,
			"insert_after": "item_tax_template",
			"module": "ERPNext Australian Localisation",
		},
		{
			"fieldname": "au_tax_description",
			"label": "AU Tax Description",
			"fieldtype": "Data",
			"fetch_from": "au_tax_code.tax_description",
			"read_only": 1,
			"insert_after": "au_tax_code",
			"module": "ERPNext Australian Localisation",
		},
	],
}


def execute():
	frappe.db.set_value(
		"Custom Field",
		{"dt": "Bank Account", "fieldname": "file_format"},
		{"options": "-None-\nABA", "default": "-None-"},
	)

	delete_custom_field(POS_INVOICE_CUSTOM_FIELDS)

	try:
		frappe.rename_doc("Print Format", "AU BAS Report Format", "AU Full BAS Report Format")
	except Exception:
		frappe.logger().info("Print Format already renamed")
