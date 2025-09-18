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
def get_gst(name, company, start_date, end_date):
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


@frappe.whitelist()
def get_quaterly_start_end_date(start_date):
	from frappe.utils.data import get_quarter_ending, get_quarter_start

	return get_quarter_start(start_date), get_quarter_ending(start_date)
