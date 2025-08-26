import frappe
from erpnext_australian_localisation.setup.custom_fields import (
	CUSTOM_FIELDS,
	HRMS_CUSTOM_FIELDS,
	CUSTOM_FIELDS_FOR_BANK_FILE,
)
from erpnext_australian_localisation.setup.property_setters import PROPERTIES


def delete_custom_field(custom_fields):
	for doctypes, fields in custom_fields.items():
		if isinstance(fields, dict):
			fields = [fields]

		if isinstance(doctypes, str):
			doctypes = (doctypes,)

		for doctype in doctypes:
			frappe.db.delete(
				"Custom Field",
				{
					"fieldname": ("in", [field["fieldname"] for field in fields]),
					"dt": doctype,
				},
			)

			frappe.clear_cache(doctype=doctype)


def delete_property_setter():
	field_map = {
		"doctype": "doc_type",
		"fieldname": "field_name",
	}

	for property_setter in PROPERTIES:
		for key, fieldname in field_map.items():
			if key in property_setter:
				property_setter[fieldname] = property_setter.pop(key)

		frappe.db.delete("Property Setter", property_setter)


def remove_setup():
	delete_custom_field(CUSTOM_FIELDS)
	delete_custom_field(CUSTOM_FIELDS_FOR_BANK_FILE)
	delete_property_setter()


def delete_hrms_custom_fields():
	delete_custom_field(HRMS_CUSTOM_FIELDS)
