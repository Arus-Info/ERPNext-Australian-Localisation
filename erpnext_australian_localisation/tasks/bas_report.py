from datetime import datetime

import frappe


def create_scheduled_bas_reports():
	"""Scheduler entry point (runs monthly, on the 1st).

	Creates a draft AU BAS Report for each company based on its reporting period:
	- Monthly companies: one report every month.
	- Quarterly companies: one report at the start of each quarter (Jan/Apr/Jul/Oct).
	"""
	today = datetime.today()

	reporting_periods = frappe.get_all(
		"AU BAS Reporting Period",
		fields=["company", "reporting_period"],
	)

	for row in reporting_periods:
		if not row.company:
			continue

		# Quarterly reports are only created at the beginning of a quarter
		if row.reporting_period == "Quarterly" and today.month not in (1, 4, 7, 10):
			continue

		create_bas_report(row.company)


def create_bas_report(company):
	from frappe.utils.data import get_last_day, get_quarter_ending, get_quarter_start

	today = datetime.today()

	reporting_period = frappe.db.get_value(
		"AU BAS Reporting Period", {"company": company}, "reporting_period"
	)

	if reporting_period == "Monthly":
		start_date = today.replace(day=1).strftime("%Y-%m-%d")
		end_date = get_last_day(today).strftime("%Y-%m-%d")
	else:
		start_date = get_quarter_start(today).strftime("%Y-%m-%d")
		end_date = get_quarter_ending(today).strftime("%Y-%m-%d")

	# Avoid creating a duplicate report for the same company and period
	if frappe.db.exists(
		"AU BAS Report",
		{"company": company, "start_date": start_date, "end_date": end_date},
	):
		return

	report = frappe.new_doc("AU BAS Report")
	report.company = company
	report.start_date = start_date
	report.end_date = end_date
	report.save()
