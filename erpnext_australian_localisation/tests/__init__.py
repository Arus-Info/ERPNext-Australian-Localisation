import frappe
from frappe import _
from frappe.desk.page.setup_wizard.setup_wizard import setup_complete
from frappe.utils.data import now_datetime


def before_tests():
	frappe.clear_cache()

	if not frappe.db.a_row_exists("Company"):
		current_year = now_datetime().year
		setup_complete(
			{
				"currency": "AUD",
				"full_name": "_Test User",
				"company_name": "_Test AU Company",
				"timezone": "Australia/Melbourne",
				"company_abbr": "_TAU",
				"industry": "Manufacturing",
				"country": "Australia",
				"fy_start_date": f"{current_year}-01-01",
				"fy_end_date": f"{current_year}-12-31",
				"language": "english",
				"company_tagline": "Testing",
				"email": "test@erpnext.com",
				"password": "test",
				"chart_of_accounts": "Australia - Chart of Accounts with Account Numbers",
			}
		)
