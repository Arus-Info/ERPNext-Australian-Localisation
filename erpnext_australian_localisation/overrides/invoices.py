import frappe
import pandas as pd


def on_submit(doc, event):

	result = []
	if doc.doctype in ["Sales Invoice"]:
		tax_allocation = "Collected Sales"
		account_type = "income_account"
	elif doc.doctype in ["Purchase Invoice"]:
		tax_allocation = "Deductible Purchase"
		account_type = "expense_account"


	for item in doc.items:
		bas_labels = frappe.get_list(
			"AU BAS Label Setup",
			filters={
				"tax_management": "Subjected",
				"tax_allocation": tax_allocation,
				"tax_code" : item.au_tax_code
			},
			fields=["bas_label"]
		)
		for bas_label in bas_labels :
			temp = {
				'bas_label' : bas_label.bas_label,
				'account' : item.get(account_type),
				'tax_code' : item.au_tax_code
			}
			if tax_allocation == "Collected Sales" :
				temp['gst_pay_basis'] = item.amount
			else :
				temp['gst_offset_basis'] = item.amount
			result.append(temp)

	for tax in doc.taxes :
		bas_labels = frappe.get_list(
			"AU BAS Label Setup",
			filters={
				"tax_management": "Tax Account",
				"tax_allocation": tax_allocation,
				"tax_code" : tax.au_tax_code
			},
			fields=["bas_label"]
		)
		for bas_label in bas_labels :
			temp = {
				'bas_label' : bas_label.bas_label,
				'account' : tax.account_head,
				'tax_code' : tax.au_tax_code,
				'gst_pay_amount' : tax.tax_amount
			}
			if tax_allocation == "Collected Sales" :
				temp['gst_pay_amount'] = tax.tax_amount
			else :
				temp['gst_offset_amount'] = tax.tax_amount
			result.append(temp)

	result = pd.DataFrame(result)

	result = result.groupby(['bas_label','account','tax_code']).sum(['gst_pay_basis','gst_pay_amount']).reset_index()

	bas_entries = result.to_dict(orient='records')

	for bas_entry in bas_entries :
		bas_doc = frappe.new_doc("AU BAS Entry")
		bas_doc.update({
			**bas_entry,
			"date" : doc.posting_date,
			"voucher_type" : doc.doctype,
			"voucher_no" : doc.name
		})
		bas_doc.save(ignore_permissions = True)

def expense_on_submit(doc, event):
	bas = frappe.new_doc("BAS Entry")
	bas.voucher_type = doc.doctype
	bas.voucher_number = doc.name
	bas.company = doc.company

	temp = {}

	if doc.total_taxes_and_charges:
		temp["g11"] = doc.total_sanctioned_amount
		temp["g20"] = doc.total_taxes_and_charges
	else:
		temp["g14"] = doc.total_sanctioned_amount

	bas.update(temp)

	bas.save(ignore_permissions=1)


def on_update(doc, event):

	print("doctype")
	if doc.doctype in ["Sales Invoice"]:
		tax_template_doctype = "Sales Taxes and Charges Template"
	elif doc.doctype in ["Purchase Invoice"]:
		tax_template_doctype = "Purchase Taxes and Charges Template"

	tax_template = frappe.db.get_value(
		tax_template_doctype, doc.taxes_and_charges, "title"
	)

	for item in doc.items:
		if item.au_tax_code != "AUSINPTAX" :
			item_tax_template = frappe.db.get_value(
				"Item Tax Template", item.item_tax_template, "title"
			)
			tax_code = frappe.db.get_value(
				"AU Tax Determination",
				{"bp_tax_template": tax_template, "item_tax_template": item_tax_template if item_tax_template else ""},
				"tax_code",
			)
			item.au_tax_code = tax_code
			item.save()

	for tax in doc.taxes:
		tax_code = frappe.db.get_value(
			"AU Tax Determination",
			{"bp_tax_template": tax_template, "item_tax_template": ""},
			"tax_code",
		)
		tax.au_tax_code = tax_code
		tax.save()


# @frappe.whitelist()
# def get_au_tax_code(tax_template, item_tax_template, tax_template_doctype):
# 	if frappe.has_permission(tax_template_doctype, "read") :
# 		tax_template = frappe.db.get_value(
# 			tax_template_doctype, tax_template, "title"
# 		)
# 		if item_tax_template :
# 			item_tax_template = frappe.db.get_value(
# 				"Item Tax Template", item_tax_template, "title"
# 			)

# 		tax_code = frappe.db.get_value(
# 			"AU Tax Determination",
# 			{"bp_tax_template": tax_template, "item_tax_template": item_tax_template},
# 			"tax_code",
# 		)
# 		return tax_code
# 	else :
# 		frappe.throw("You don't have enough permission")
