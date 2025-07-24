import frappe
import pandas as pd
from datetime import date

def on_update(doc, event):

	tax_template = "AU Non Capital Purchase - GST"

	if doc.taxes :
		item_tax_template = ""
	else :
		item_tax_template = "GST Exempt Purchase"
	
	for field in ["expenses","taxes"] :
		for i in doc.get(field):
			if i.au_tax_code != "AUSINPTAX" :
				tax_code = frappe.db.get_value(
					"AU Tax Determination",
					{"bp_tax_template": tax_template, "item_tax_template": item_tax_template},
					"tax_code",
				)
				i.au_tax_code = tax_code
				i.save()

def on_submit(doc,event):

	result = []
	
	for expense in doc.expenses :
		bas_labels = frappe.get_all(
			"AU BAS Label Setup",
			filters={
				"tax_management": "Subjected",
				"tax_allocation": "Deductible Purchase",
				"tax_code" : expense.au_tax_code
			},
			fields=["bas_label"]
		)
		for bas_label in bas_labels :
			account = frappe.db.get_value("Expense Claim Account",{"parent" : expense.expense_type, "company" : doc.company}, "default_account")
			temp = {
				'bas_label' : bas_label.bas_label,
				'account' : account,
				'tax_code' : expense.au_tax_code,
				'gst_offset_basis' : expense.sanctioned_amount
			}
			result.append(temp)

	for tax in doc.taxes :
		bas_labels = frappe.get_all(
			"AU BAS Label Setup",
			filters={
				"tax_management": "Tax Account",
				"tax_allocation": "Deductible Purchase",
				"tax_code" : tax.au_tax_code
			},
			fields=["bas_label"]
		)
		for bas_label in bas_labels :
			temp = {
				'bas_label' : bas_label.bas_label,
				'account' : tax.account_head,
				'tax_code' : tax.au_tax_code,
				'gst_offset_amount' : tax.tax_amount
			}
			result.append(temp)
	if result :
		result = pd.DataFrame(result)
		result = result.groupby(['bas_label','account','tax_code']).sum(['gst_offset_basis','gst_offset_amount']).reset_index()
		bas_entries = result.to_dict(orient='records')
		for bas_entry in bas_entries :
			bas_doc = frappe.new_doc("AU BAS Entry")
			bas_doc.update({
				**bas_entry,
				'date' : date.today(),
				"voucher_type" : doc.doctype,
				"voucher_no" : doc.name,
				"company" : doc.company
			})
			bas_doc.save(ignore_permissions = True)