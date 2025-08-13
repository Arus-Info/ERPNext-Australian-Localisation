import frappe
from datetime import datetime


def create_bas_report(company):
	from frappe.utils.data import get_last_day, get_quarter_ending, get_quarter_start

	report = frappe.new_doc("AU BAS Report")
	today = datetime.today()

	reporting_period = frappe.db.get_value("AU BAS Reporting Period", {"company": company}, "reporting_period")

	if reporting_period == "Monthly":
		report.start_date = today.replace(day=1).strftime("%Y-%m-%d")
		report.end_date = get_last_day(today).strftime("%Y-%m-%d")
	else :
		report.start_date = get_quarter_start(today).strftime("%Y-%m-%d")
		report.end_date = get_quarter_ending(today).strftime("%Y-%m-%d")
	
	report.company = company
	report.save()