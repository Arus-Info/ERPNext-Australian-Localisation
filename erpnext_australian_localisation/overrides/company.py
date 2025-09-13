import frappe
from frappe import _


def initial_company_setup(company: str | None = None) -> None:
	if company:
		company_list = [company]
	else:
		company_list = frappe.get_all(
			"Company",
			filters={"country": "Australia"},
			pluck="name",
		)

	if not company_list:
		frappe.logger().info("No Australian companies found for BAS setup.")
		return

	au_settings = frappe.get_cached_doc("AU Localisation Settings")

	for comp in company_list:
		exists = any(d.company == comp for d in au_settings.bas_reporting_period)
		if exists:
			continue

		au_settings.append("bas_reporting_period", {
			"company": comp,
			"reporting_period": "Monthly",
		})

	if au_settings.is_dirty():
		au_settings.save(ignore_permissions=True)
		frappe.msgprint(
			_("BAS Reporting Periods initialised for {0}").format(", ".join(company_list))
		)


def after_insert(doc, event: str) -> None:
	"""
	Hook: After inserting a Company, auto-create BAS setup if it's in Australia.
	"""
	if doc.country == "Australia":
		initial_company_setup(doc.name)
