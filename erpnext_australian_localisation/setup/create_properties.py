import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from erpnext_australian_localisation.setup.custom_fields import CUSTOM_FIELDS, HRMS_CUSTOM_FIELDS
from erpnext_australian_localisation.setup.property_setters import PROPERTIES


def create_custom_field():
	create_custom_fields(CUSTOM_FIELDS, update=1)
	installed_apps = frappe.get_installed_apps()

	if "hrms" in installed_apps :
		create_hrms_custom_fields()


def create_property_setter(properties):
	for property_setter in properties:
		frappe.make_property_setter(
			property_setter,
			validate_fields_for_doctype=False,
			is_system_generated=property_setter.get("is_system_generated", True),
		)

def initial_setup():
	create_custom_field()
	create_property_setter(PROPERTIES)

def create_hrms_custom_fields():
	create_custom_fields(HRMS_CUSTOM_FIELDS, update = 1)