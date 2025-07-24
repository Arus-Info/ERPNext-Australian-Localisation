# Copyright (c) 2025, frappe.dev@arus.co.in and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime
from frappe.model.document import Document


class AUBASReport(Document):

	def before_submit(self):
		if self.reporting_status != "Validated" :
			frappe.throw("Only BAS Report at Validated state can be submitted")

	def before_insert(self):
		this_year = frappe.get_list("AU BAS Report", filters=[["name" ,"like", "BAS-" + self.start_date[:4] + "%"]], fields=["start_date", "end_date"])
		for i in range(len(this_year)):
			date = datetime.strptime(self.start_date, "%Y-%m-%d").date() 
			if this_year[i].start_date <= date and date<= this_year[i].end_date :
				frappe.throw("BAS Report found for this period")


@frappe.whitelist()
def get_gst(name, company, start_date, end_date):
	from frappe.model.mapper import get_mapped_doc

	doc = frappe.get_doc("AU BAS Report", name)

	bas_labels = frappe.get_all("AU BAS Label", pluck="name")

	bas_label_details = [{'bas_label' : l, "fieldname" : l.lower() + "_details"} for l in bas_labels]

	for bas_label_detail in bas_label_details :
		doc.update({
			bas_label_detail['fieldname'] : []
		})
		total = 0
		bas_entries = frappe.get_list(
			"AU BAS Entry",
			filters=[
				["date", ">=", start_date],
				["date", "<=", end_date],
				["company", "=", company],
				["bas_label", "=", bas_label_detail['bas_label']],
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
				ignore_permissions=True
			)
			total += (
				bas_report_entry.gst_pay_basis
				+ bas_report_entry.gst_pay_amount
				+ bas_report_entry.gst_offset_basis
				+ bas_report_entry.gst_offset_amount
			)

			doc.append(bas_label_detail["fieldname"], bas_report_entry)

		doc.update({
			bas_label_detail['bas_label'].lower() : total
		})
	doc.net_gst = doc.get('1a') - doc.get('1b')
	doc.save()

@frappe.whitelist()
def get_quaterly_start_end_date(start_date):
	from frappe.utils.data import get_quarter_ending, get_quarter_start
	
	return get_quarter_start(start_date), get_quarter_ending(start_date)
