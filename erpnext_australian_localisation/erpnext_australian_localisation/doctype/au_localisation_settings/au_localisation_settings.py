# Copyright (c) 2025, frappe.dev@arus.co.in and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AULocalisationSettings(Document):
	def on_update(self):
		frappe.cache.delete_keys("bootinfo")


@frappe.whitelist()
def is_draft(company):
	bas_report = frappe.get_list("AU BAS Report", filters={"docstatus": 0, "company": company})
	if bas_report:
		return True
	return False


def get_au_email_templates():
	from erpnext_australian_localisation.setup.install_fixtures import get_default_email_templates

	settings = frappe.get_single("AU Localisation Settings")

	templates = [row["name"] for row in get_default_email_templates()]

	templates += [
		settings.remittance_advice_template,
		settings.payment_receipt_template,
	]

	return list(set(filter(None, templates)))


@frappe.whitelist()
def get_disabled_email_templates():
	"""Templates that are not yet ticked as `enabled` for CRM."""
	if "crm" not in frappe.get_installed_apps():
		return []

	return frappe.get_all(
		"Email Template",
		filters={"name": ("in", get_au_email_templates()), "enabled": 0},
		pluck="name",
	)


@frappe.whitelist()
def enable_email_templates():
	if "crm" not in frappe.get_installed_apps():
		return []

	frappe.has_permission("Email Template", "write", throw=True)

	enabled = get_disabled_email_templates()
	for template in enabled:
		frappe.db.set_value("Email Template", template, "enabled", 1)

	return enabled
