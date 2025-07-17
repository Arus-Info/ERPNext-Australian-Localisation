import frappe
from erpnext_australian_localisation.setup.custom_fields import CUSTOM_FIELDS
from erpnext_australian_localisation.setup.property_setters import PROPERTIES

def delete_custom_field():
	for doctypes, fields in CUSTOM_FIELDS.items():
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
	delete_custom_field()
	delete_property_setter()