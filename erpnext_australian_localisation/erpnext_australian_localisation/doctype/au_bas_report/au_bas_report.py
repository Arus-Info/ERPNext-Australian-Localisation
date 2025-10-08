# Copyright (c) 2025, frappe.dev@arus.co.in and contributors
# For license information, please see license.txt

import math
from datetime import datetime

import frappe
from frappe import _
from frappe.model.document import Document


class AUBASReport(Document):
	def before_submit(self):
		if self.reporting_status != "Validated":
			frappe.throw(_("Only BAS Report at Validated state can be submitted"))

	def before_insert(self):
		this_year = frappe.get_list(
			"AU BAS Report",
			filters=[
				["name", "like", "BAS-" + self.start_date[:4] + "%"],
				["company", "=", self.company],
			],
			fields=["start_date", "end_date"],
		)
		start_date = datetime.strptime(self.start_date, "%Y-%m-%d").date()
		end_date = datetime.strptime(self.end_date, "%Y-%m-%d").date()
		for i in range(len(this_year)):
			if (start_date <= this_year[i].start_date and end_date >= this_year[i].start_date) or (
				this_year[i].start_date <= start_date and start_date <= this_year[i].end_date
			):
				frappe.throw(_("BAS Report found for this period"))


@frappe.whitelist()
def get_gst(name, company, start_date, end_date, reporting_method):
	if reporting_method == "Full reporting method":
		update_full_bas_report(name, company, start_date, end_date)
	else:
		update_simpler_bas_report(name, company, start_date, end_date)


def update_full_bas_report(name, company, start_date, end_date):
	from frappe.model.mapper import get_mapped_doc

	frappe.publish_realtime("bas_data_generator", user=frappe.session.user)

	doc = frappe.get_doc("AU BAS Report", name)

	bas_labels = frappe.get_all("AU BAS Label", pluck="name")

	bas_label_details = [{"bas_label": l, "fieldname": l.lower() + "_details"} for l in bas_labels]
	progress = 10
	frappe.publish_progress(1, title="BAS Label Generating..", description="getting ready...")
	for bas_label_detail in bas_label_details:
		frappe.publish_progress(
			progress,
			title="BAS Label Generating..",
			description=bas_label_detail["bas_label"],
		)
		progress += 10
		doc.update({bas_label_detail["fieldname"]: []})
		total = 0
		bas_entries = frappe.get_list(
			"AU BAS Entry",
			filters=[
				["date", ">=", start_date],
				["date", "<=", end_date],
				["company", "=", company],
				["bas_label", "=", bas_label_detail["bas_label"]],
			],
			pluck="name",
		)
		for bas_entry in bas_entries:
			bas_report_entry = get_mapped_doc(
				"AU BAS Entry",
				bas_entry,
				{
					"AU BAS Entry": {
						"doctype": "AU BAS Report Entry",
					}
				},
				ignore_permissions=True,
			)
			total += (
				bas_report_entry.gst_pay_basis
				+ bas_report_entry.gst_pay_amount
				+ bas_report_entry.gst_offset_basis
				+ bas_report_entry.gst_offset_amount
			)
			doc.append(bas_label_detail["fieldname"], bas_report_entry)
		doc.update({bas_label_detail["bas_label"].lower(): math.floor(total)})

	doc._1a_only = doc.get("1a")
	doc._1b_only = doc.get("1b")

	doc.g5 = doc.g2 + doc.g3 + doc.g4
	doc.g6 = doc.g1 - doc.g5
	doc.g8 = doc.g6 + doc.g7
	doc.g9 = math.floor(doc.g8 / 11)

	doc.g12 = doc.g10 + doc.g11
	doc.g16 = doc.g13 + doc.g14 + doc.g15
	doc.g17 = doc.g12 - doc.g16
	doc.g19 = doc.g17 + doc.g18
	doc.g20 = math.floor(doc.g19 / 11)

	doc.update({"1a": doc._1a_only + math.floor(doc.g7 / 11), "1b": doc._1b_only + math.floor(doc.g18 / 11)})

	doc.net_gst = abs(doc.get("1a") - doc.get("1b"))
	doc.save()


def update_simpler_bas_report(name, company, start_date, end_date):
	frappe.publish_realtime("bas_data_generator", user=frappe.session.user)

	doc = frappe.get_doc("AU BAS Report", name)

	frappe.publish_progress(10, title="BAS Label Generating..", description="getting ready...")

	accounts_g1 = frappe.get_list(
		"Income Account for Simpler BAS",
		parent_doctype="AU Simpler BAS Report Setup",
		filters={"parent": company},
		fields=["account"],
		pluck="account",
	)
	(account_1a, account_1b) = frappe.db.get_value(
		"AU Simpler BAS Report Setup", company, ["account_1a", "account_1b"]
	)
	if not (accounts_g1 and account_1a and account_1b):
		frappe.throw(
			_(
				"Please Setup All the necessary accounts in <a href='/app/au-simpler-bas-report-setup/{0}'>AU Simpler BAS Report Setup</a>",
			).format(company)
		)

	doc.update({"g1_details": []})
	doc.update({"1b_details": []})
	doc.update({"1a_details": []})

	frappe.publish_progress(40, title="BAS Label Generating..", description="G1")
	field_with_expression = "( - debit_in_account_currency + credit_in_account_currency) as gst_pay_basis"
	entries = get_gl_entries_for_accounts(start_date, end_date, company, accounts_g1, field_with_expression)
	for e in entries:
		row = frappe.new_doc("AU BAS Report Entry")
		row.update(e)
		doc.g1 += e.gst_pay_basis
		doc.append("g1_details", row)
	frappe.publish_progress(70, title="BAS Label Generating..", description="1A")
	field_with_expression = "( - debit_in_account_currency + credit_in_account_currency) as gst_pay_amount"
	entries = get_gl_entries_for_accounts(start_date, end_date, company, account_1a, field_with_expression)
	for e in entries:
		row = frappe.new_doc("AU BAS Report Entry")
		row.update(e)
		doc.update({"1a": doc.get("1a") + e.gst_pay_amount})
		doc.append("1a_details", row)
	for e in entries:
		row = frappe.new_doc("AU BAS Report Entry")
		row.update(e)
		doc.g1 += e.gst_pay_amount
		doc.append("g1_details", row)

	frappe.publish_progress(100, title="BAS Label Generating..", description="1B")
	field_with_expression = "(debit_in_account_currency - credit_in_account_currency) as gst_offset_amount"
	entries = get_gl_entries_for_accounts(start_date, end_date, company, account_1b, field_with_expression)
	for e in entries:
		row = frappe.new_doc("AU BAS Report Entry")
		row.update(e)
		doc.update({"1b": doc.get("1b") + e.gst_offset_amount})
		doc.append("1b_details", row)
	doc.net_gst = abs(doc.get("1a") - doc.get("1b"))
	doc.save()


def get_gl_entries_for_accounts(start_date, end_date, company, accounts, field_with_expression):
	gl_entries = frappe.get_list(
		"GL Entry",
		filters=[
			["posting_date", ">=", start_date],
			["posting_date", "<=", end_date],
			["company", "=", company],
			["account", "in", accounts],
		],
		fields=[
			"posting_date as date",
			"voucher_type",
			"voucher_no",
			"account",
			field_with_expression,
		],
	)
	return gl_entries


@frappe.whitelist()
def get_quaterly_start_end_date(start_date):
	from frappe.utils.data import get_quarter_ending, get_quarter_start

	return get_quarter_start(start_date), get_quarter_ending(start_date)
