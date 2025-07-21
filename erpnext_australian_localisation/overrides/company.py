import frappe


def update_au_localisation_settings(company = None):
	if company:
		company_list = [company]
	else :
		company_list = frappe.get_list("Company", filters={"country" : "Australia"}, pluck="name")
	
	au_localisation_settings = frappe.get_doc("AU Localisation Settings")

	for c in company_list :
		child = frappe.new_doc("AU BAS Reporting Period")
		child.update({
			"company" : c,
			"reporting_period" : "Monthly"
		})

		au_localisation_settings.append("bas_reporting_period", child)

	au_localisation_settings.save()


def after_insert(doc,event):
	update_au_localisation_settings(doc.name)