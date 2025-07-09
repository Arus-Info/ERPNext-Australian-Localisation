# Copyright (c) 2025, frappe.dev@arus.co.in and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = [], []

	columns = [
		{
			"fieldname": "G1",
			"fieldtype": "Currency",
			"label": "G1",
			"width" : 150
		},
		{
			"fieldname": "G2",
			"fieldtype": "Currency",
			"label": "G2",
			"width" : 150
		},
		{
			"fieldname": "G3",
			"fieldtype": "Currency",
			"label": "G3",
			"width" : 150
		},
		{
			"fieldname": "G9",
			"fieldtype": "Currency",
			"label": "G9",
			"width" : 150
		},
		{
			"fieldname": "G10",
			"fieldtype": "Currency",
			"label": "G10",
			"width" : 150
		},
		{
			"fieldname": "G11",
			"fieldtype": "Currency",
			"label": "G11",
			"width" : 150
		},
		{
			"fieldname": "G14",
			"fieldtype": "Currency",
			"label": "G14",
			"width" : 150
		},
		{
			"fieldname": "G20",
			"fieldtype": "Currency",
			"label": "G20",
			"width" : 150
		},
	]

	data = frappe.db.sql(
		"""
			select  SUM(g1) as G1,
					SUM(g2) as G2, 
					SUM(g3) as G3, 
					SUM(g9) as G9, 
					SUM(g10) as G10, 
					SUM(g11) as G11, 
					SUM(g14) as G14, 
					SUM(g20) as G20  
			from `tabBAS Entry`
		""",
		as_dict=True,
	)

	return columns, data
