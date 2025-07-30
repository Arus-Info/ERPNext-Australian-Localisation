import frappe
import pandas as pd


def on_submit(doc, event):

	if doc.taxes_and_charges :
		result = []
		if doc.doctype in ["Sales Invoice"]:
			tax_allocation = "Collected Sales"
			account_type = "income_account"
			sum_depends_on = ['gst_pay_basis','gst_pay_amount']
		elif doc.doctype in ["Purchase Invoice"]:
			tax_allocation = "Deductible Purchase"
			account_type = "expense_account"
			sum_depends_on = ['gst_offset_basis','gst_offset_amount']

		for item in doc.items:
			if item.amount :
				bas_labels = frappe.get_all(
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
			if tax.tax_amount :
				bas_labels = frappe.get_all(
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
						'tax_code' : tax.au_tax_code
					}
					if tax_allocation == "Collected Sales" :
						temp['gst_pay_amount'] = tax.tax_amount
					else :
						temp['gst_offset_amount'] = tax.tax_amount
					result.append(temp)
		if result :
			result = pd.DataFrame(result)
			result = result.groupby(['bas_label','account','tax_code']).sum(sum_depends_on).reset_index()
			bas_entries = result.to_dict(orient='records')
			for bas_entry in bas_entries :
				bas_doc = frappe.new_doc("AU BAS Entry")
				bas_doc.update({
					**bas_entry,
					"date" : doc.posting_date,
					"voucher_type" : doc.doctype,
					"voucher_no" : doc.name,
					"company" : doc.company
				})
				bas_doc.save(ignore_permissions = True)


def on_cancel(doc, event):
	bas_entries = frappe.get_list("AU BAS Entry", filters={"voucher_no" : doc.name}, pluck="name")
	for bas_entry in bas_entries :
		frappe.delete_doc("AU BAS Entry", bas_entry, ignore_permissions = True)

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
