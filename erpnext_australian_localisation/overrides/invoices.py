import frappe
import pandas as pd


def on_submit(doc, event):
	if doc.taxes_and_charges:
		result = []
		if doc.doctype in ["Sales Invoice"]:
			tax_allocation = "Collected Sales"
			account_type = "income_account"
			sum_depends_on = ["gst_pay_basis", "gst_pay_amount"]
		elif doc.doctype in ["Purchase Invoice"]:
			tax_allocation = "Deductible Purchase"
			account_type = "expense_account"
			sum_depends_on = ["gst_offset_basis", "gst_offset_amount"]

		for item in doc.items:
			result.extend(
				generate_bas_labels_for_items(
					tax_allocation,
					item.au_tax_code,
					item.get(account_type),
					item.base_amount,
					sum_depends_on[0],
				)
			)

		for tax in doc.taxes:
			temp = generate_bas_labels_for_tax(
				tax_allocation, tax.account_head, tax.au_tax_code, tax.base_tax_amount, sum_depends_on[1]
			)
			result.extend(temp)

		create_au_bas_entries(doc.doctype, doc.name, doc.company, doc.posting_date, result, sum_depends_on)


def on_cancel(doc, event):
	bas_entries = frappe.get_list("AU BAS Entry", filters={"voucher_no": doc.name}, pluck="name")
	for bas_entry in bas_entries:
		frappe.delete_doc("AU BAS Entry", bas_entry, ignore_permissions=True)


def generate_bas_labels_for_items(tax_allocation, au_tax_code, account, amount, amount_label):
	res = []
	if amount:
		bas_labels = frappe.get_all(
			"AU BAS Label Setup",
			filters={
				"tax_management": "Subjected",
				"tax_allocation": tax_allocation,
				"tax_code": au_tax_code,
			},
			fields=["bas_label"],
		)
		for bas_label in bas_labels:
			temp = {
				"bas_label": bas_label.bas_label,
				"account": account,
				"tax_code": au_tax_code,
				amount_label: amount,
			}
			res.append(temp)
	return res


def generate_bas_labels_for_tax(tax_allocation, account_head, au_tax_code, tax_amount, tax_amount_label):
	res = []
	if tax_amount:
		bas_labels = frappe.get_all(
			"AU BAS Label Setup",
			filters={
				"tax_management": "Tax Account",
				"tax_allocation": tax_allocation,
				"tax_code": au_tax_code,
			},
			fields=["bas_label"],
		)
		for bas_label in bas_labels:
			temp = {
				"bas_label": bas_label.bas_label,
				"account": account_head,
				"tax_code": au_tax_code,
				tax_amount_label: tax_amount,
			}
			res.append(temp)

	return res


def create_au_bas_entries(doctype, docname, company, posting_date, result, sum_depends_on):
	if result:
		result = pd.DataFrame(result)
		result = result.groupby(["bas_label", "account", "tax_code"]).sum(sum_depends_on).reset_index()
		bas_entries = result.to_dict(orient="records")
		for bas_entry in bas_entries:
			bas_doc = frappe.new_doc("AU BAS Entry")
			bas_doc.update(
				{
					**bas_entry,
					"date": posting_date,
					"voucher_type": doctype,
					"voucher_no": docname,
					"company": company,
				}
			)
			bas_doc.save(ignore_permissions=True)


def update_tax_code_for_item(item, tax_template):
	if item.item_tax_template:
		item_tax_template = frappe.db.get_value("Item Tax Template", item.item_tax_template, "title")
	else:
		item_tax_template = ""
	tax_code = frappe.db.get_value(
		"AU Tax Determination",
		{
			"bp_tax_template": tax_template,
			"item_tax_template": item_tax_template,
		},
		"tax_code",
	)
	item.au_tax_code = tax_code
	item.save()


def update_tax_code_for_taxes(taxes, tax_template):
	for tax in taxes:
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
