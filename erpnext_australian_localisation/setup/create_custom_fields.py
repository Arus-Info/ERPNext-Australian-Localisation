import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from erpnext_australian_localisation.setup.custom_fields import CUSTOM_FIELDS
from erpnext_australian_localisation.setup.property_setters import PROPERTIES


def create_custom_field():
	create_custom_fields(CUSTOM_FIELDS, update=1)


def create_property_setter():
	for property_setter in PROPERTIES:
		frappe.make_property_setter(
			property_setter,
			validate_fields_for_doctype=False,
			is_system_generated=property_setter.get("is_system_generated", True),
		)

def initial_setup():
	create_custom_field()
	create_property_setter()