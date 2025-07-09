import frappe

from erpnext_australian_localisation.setup import get_property_setters


def after_install():
	property_setters = get_property_setters()
	for property_setter in property_setters:
		frappe.make_property_setter(
			property_setter,
			validate_fields_for_doctype=False,
			is_system_generated=property_setter.get("is_system_generated", True),
		)
