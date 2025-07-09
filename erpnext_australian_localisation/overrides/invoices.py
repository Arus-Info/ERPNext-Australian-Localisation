import frappe

from erpnext.controllers.taxes_and_totals import (
	get_itemised_tax_breakup_data,
	get_rounded_tax_amount,
)


def on_submit(doc, event):

	bas = frappe.new_doc("BAS Entry")
	bas.voucher_type = doc.doctype
	bas.voucher_number = doc.name

	if doc.doctype in ["Sales Invoice"]:
		tax_template_doctype = "Sales Taxes and Charges Template"
		account_head = "GST Collected (Payable)"
	elif doc.doctype in ["Purchase Invoice"]:
		tax_template_doctype = "Purchase Taxes and Charges Template"
		account_head = "GST Paid (Receivable)"

	itemised_tax_data = get_itemised_tax_breakup_data(doc)
	get_rounded_tax_amount(itemised_tax_data, doc.precision("tax_amount", "taxes"))

	tax_template = frappe.db.get_value(
		tax_template_doctype, doc.taxes_and_charges, "title"
	)

	total, tax_amount, amount_0, amount_10 = get_total(itemised_tax_data, account_head)
	print(total, tax_amount, amount_0, amount_10)

	if "Sales" in tax_template_doctype:
		bas.g1 = total
		bas.g9 = tax_amount
		if tax_template == "Export Sales - GST Free":
			bas.g2 = total
		elif tax_template == "AU Sales - GST Free":
			bas.g3 = total
		elif tax_template == "AU Sales - GST ":
			bas.g3 = amount_0

	elif "Purchase" in tax_template_doctype:
		bas.g20 = tax_amount
		if tax_template == "AU Capital Purchase - GST":
			bas.g10 = total
		elif tax_template == "AU Non Capital Purchase - GST":
			bas.g11 = amount_10
			bas.g14 = amount_0
		elif tax_template == "Import & GST-Free Purchase":
			bas.g14 = total
	bas.save(ignore_permissions = 1)


def expense_on_submit(doc, event):
	bas = frappe.new_doc("BAS Entry")
	bas.voucher_type = doc.doctype
	bas.voucher_number = doc.name

	temp = {}

	if doc.total_taxes_and_charges:
		temp["g11"] = doc.total_sanctioned_amount
		temp["g20"] = doc.total_taxes_and_charges
	else:
		temp["g14"] = doc.total_sanctioned_amount

	bas.update(temp)

	bas.save(ignore_permissions = 1)


def get_total(tax_data, account_head):
	a_g_0 = 0  # amount for item with gst 0 %
	a_g_10 = 0  # amount for item with gst 10 %
	t_g_0 = 0  # tax amount for item with gst 0%
	t_g_10 = 0  # tax amount for item with gst 10%

	for i in tax_data:
		if i[account_head]["tax_rate"] == 0:
			t_g_0 += i[account_head]["tax_amount"]
			a_g_0 += i["taxable_amount"]

		elif i[account_head]["tax_rate"] == 10:
			t_g_10 += i[account_head]["tax_amount"]
			a_g_10 += i["taxable_amount"]

	a_g_0 += t_g_0
	a_g_10 += t_g_10
	tax_amount = t_g_0 + t_g_10
	total = a_g_0 + a_g_10

	return total, tax_amount, a_g_0, a_g_10

def on_cancel(doc,event):
	bas = frappe.db.exists("BAS Entry", { "voucher_number" : doc.name})

	if bas :
		frappe.delete_doc("BAS Entry", bas,  ignore_permissions=True)
