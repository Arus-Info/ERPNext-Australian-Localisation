import frappe
from frappe.desk.page.setup_wizard.setup_wizard import make_records

from erpnext_australian_localisation.setup.install_fixtures import get_default_email_templates


def execute():
	make_records(get_default_email_templates())
