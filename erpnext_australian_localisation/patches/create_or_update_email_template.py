import frappe

from erpnext_australian_localisation.setup.install_fixtures import get_default_email_templates


def execute():
	for record in get_default_email_templates():
		if frappe.db.exists("Email Template", record["name"]):
			doc = frappe.get_doc("Email Template", record["name"])
			doc.update(record)
			doc.save()
		else:
			frappe.get_doc(record).insert()
