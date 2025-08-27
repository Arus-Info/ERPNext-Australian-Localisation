import frappe

from erpnext_australian_localisation.tasks.bas_report import create_bas_report


def initial_company_setup(company=None):
	if company:
		company_list = [company]
	else:
		company_list = frappe.get_list("Company", filters={"country": "Australia"}, pluck="name")

	au_localisation_settings = frappe.get_cached_doc("AU Localisation Settings")

	for c in company_list:
		child = frappe.new_doc("AU BAS Reporting Period")
		child.update({"company": c, "reporting_period": "Monthly"})

		au_localisation_settings.append("bas_reporting_period", child)

		au_localisation_settings.save()
		create_bas_report(c)


def after_insert(doc, event):
	if doc.country == "Australia":
		initial_company_setup(doc.name)
