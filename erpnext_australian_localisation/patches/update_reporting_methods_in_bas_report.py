import frappe

from erpnext_australian_localisation.overrides.company import create_simpler_bas_report_setup


def execute():
	frappe.db.sql(
		"""
			UPDATE `tabAU BAS Report`
			SET
				reporting_method = 'Full reporting method'
		"""
	)
	frappe.db.sql(
		"""
			UPDATE `tabAU BAS Reporting Period`
			SET
				reporting_method = 'Full reporting method'
		"""
	)

	company_list = frappe.get_list(
		"Company", filters={"country": "Australia"}, fields=["name", "chart_of_accounts"]
	)

	for c in company_list:
		create_simpler_bas_report_setup(c["name"], c["chart_of_accounts"])
