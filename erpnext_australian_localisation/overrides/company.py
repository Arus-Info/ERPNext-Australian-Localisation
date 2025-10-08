import frappe


def create_simpler_bas_report_setup(company, chart_of_accounts):
	if not frappe.db.get_value("AU Simpler BAS Report Setup", {"company": company}):
		doc = frappe.new_doc("AU Simpler BAS Report Setup")
		doc.company = company
		if chart_of_accounts == "Australia - Chart of Accounts with Account Numbers":
			accounts = frappe.get_list(
				"Account",
				filters=[
					[
						"account_name",
						"in",
						["Sales Income", "Freight Income", "Other Income", "Service Income"],
					],
					["account_number", "in", ["41010", "41020", "41030", "41040"]],
					["account_type", "=", "Income Account"],
					["company", "=", company],
				],
			)
			for account in accounts:
				child = frappe.new_doc("Income Account for Simpler BAS")
				child.account = account
				doc.append("accounts_g1", child)
			account_1a = frappe.db.get_value(
				"Account",
				{
					"account_name": "GST Collected (Payable)",
					"account_number": "22010",
					"account_type": "Tax",
					"company": company,
				},
				"name",
			)
			account_1b = frappe.db.get_value(
				"Account",
				{
					"account_name": "GST Paid (Receivable)",
					"account_number": "22020",
					"account_type": "Tax",
					"company": company,
				},
				"name",
			)

			if account_1a != account_1b:
				doc.update({"account_1a": account_1a, "account_1b": account_1b})

		doc.flags.ignore_mandatory = True
		doc.save()


def initial_company_setup():
	company_list = frappe.get_list("Company", filters={"country": "Australia"}, pluck="name")

	for c in company_list:
		update_aulocalisation_settings(c)
		create_simpler_bas_report_setup(c, frappe.db.get_value("Company", c, "chart_of_accounts"))


def after_insert(doc, event):
	if doc.country == "Australia":
		update_aulocalisation_settings(doc.name)


def on_update(doc, event):
	if doc.country == "Australia":
		create_simpler_bas_report_setup(doc.name, doc.chart_of_accounts)


def update_aulocalisation_settings(company):
	au_localisation_settings = frappe.get_cached_doc("AU Localisation Settings")
	row = frappe.new_doc("AU BAS Reporting Period")
	row.update(
		{
			"company": company,
			"reporting_period": "Monthly",
			"reporting_method": "Simpler BAS reporting method",
		}
	)
	au_localisation_settings.append("bas_reporting_period", row)
	au_localisation_settings.save()
