import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from erpnext_australian_localisation.setup.custom_fields import (
	CUSTOM_FIELDS,
	CUSTOM_FIELDS_FOR_BANK_FILE,
	EMPLOYEE_BANK_DETAILS,
	HRMS_CUSTOM_FIELDS,
)
from erpnext_australian_localisation.setup.property_setters import PROPERTIES


def create_property_setter(properties):
	for property_setter in properties:
		frappe.make_property_setter(
			property_setter,
			validate_fields_for_doctype=False,
			is_system_generated=property_setter.get("is_system_generated", True),
		)


def initial_setup():
	create_custom_fields(CUSTOM_FIELDS, update=1)
	create_properties_for_bank_file()
	create_property_setter(PROPERTIES)

	installed_apps = frappe.get_installed_apps()
	if "hrms" in installed_apps:
		create_hrms_custom_fields()


def create_hrms_custom_fields():
	create_custom_fields(HRMS_CUSTOM_FIELDS, update=1)
	create_custom_fields(EMPLOYEE_BANK_DETAILS, update=1)


def create_properties_for_bank_file():
	create_custom_fields(CUSTOM_FIELDS_FOR_BANK_FILE, update=1)
