from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from erpnext_australian_localisation.setup.custom_fields import POS_INVOICE_CUSTOM_FIELDS


def execute():
	create_custom_fields(POS_INVOICE_CUSTOM_FIELDS, update=1)
