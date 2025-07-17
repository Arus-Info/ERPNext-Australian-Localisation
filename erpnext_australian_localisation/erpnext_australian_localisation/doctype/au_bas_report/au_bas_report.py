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
def get_gst(company, start_date, end_date):
	pass
	# if frappe.has_permission("BAS Entry"):
	# 	return frappe.db.sql(
	# 		"""
	# 			select 
	# 				SUM(1a) as 1a,
	# 				SUM(1b) as 1b, 
	# 				SUM(g1), 
	# 				SUM(g2), 
	# 				SUM(g3), 
	# 				SUM(g9), 
	# 				SUM(g10), 
	# 				SUM(g11), 
	# 				SUM(g14), 
	# 				SUM(g20) 
	# 			from `tabBAS Entry`
	# 		""",
	# 		{"company": company, "start_date": start_date, "end_date": end_date},
	# 		as_dict=True,
	# 	)


@frappe.whitelist()
def get_quaterly_start_end_date(start_date):
	from frappe.utils.data import get_quarter_ending, get_quarter_start
	
	return get_quarter_start(start_date), get_quarter_ending(start_date)

