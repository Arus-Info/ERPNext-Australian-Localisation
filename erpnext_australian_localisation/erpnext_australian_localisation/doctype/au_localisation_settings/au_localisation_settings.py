# Copyright (c) 2025, frappe.dev@arus.co.in and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AULocalisationSettings(Document):

	def on_update(self):
		frappe.cache.delete_keys("bootinfo")

@frappe.whitelist()
def is_draft(company):
	bas_report = frappe.get_list("AU BAS Report", filters = { "docstatus" : 0, "company" : company})
	if bas_report :
		return True
	return False

@frappe.whitelist()
def clear_transaction():
	if frappe.has_permission("AU BAS Report") :
		a = frappe.db.sql(
			"""
				truncate table `tabAU BAS Entry`
			"""
		)
		b = frappe.db.sql(
			"""
				truncate table `tabAU BAS Report`
			"""
		)
		frappe.db.sql(
			"""
				truncate table `tabAU BAS Report Entry`
			"""
		)

		print(a,b)