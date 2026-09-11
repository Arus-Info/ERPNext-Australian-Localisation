from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

import frappe
import pandas as pd


def before_submit(doc, event):
	if doc.taxes_and_charges:
		result = []
		if doc.doctype in ["Sales Invoice"]:
			tax_allocation = "Collected Sales"
			account_type = "income_account"
			sum_depends_on = ["gst_pay_basis", "gst_pay_amount"]
			tax_template_doctype = "Sales Taxes and Charges Template"
		elif doc.doctype in ["Purchase Invoice"]:
			tax_allocation = "Deductible Purchase"
			account_type = "expense_account"
			sum_depends_on = ["gst_offset_basis", "gst_offset_amount"]
			tax_template_doctype = "Purchase Taxes and Charges Template"

		tax_template = frappe.db.get_value(tax_template_doctype, doc.taxes_and_charges, "title")

		if doc.doctype == "Sales Invoice":
			update_tax_code_for_sales_invoice_item(doc.items, tax_template)
		elif doc.doctype == "Purchase Invoice":
			update_tax_code_for_purchase_invoice_item(doc.items, tax_template)

		for item in doc.items:
			result.extend(
				generate_bas_labels(
					"Subjected",
					tax_allocation,
					item.au_tax_code,
					item.get(account_type),
					round(item.base_net_amount, 2),
					sum_depends_on[0],
				)
			)

		for tax in doc.taxes:
			update_tax_code_for_tax(tax, tax_template)
			tax_management = (
				"Tax Account"
				if frappe.db.get_value("Account", tax.account_head, "account_type") == "Tax"
				else "Subjected"
			)
			allocations = [(tax.au_tax_code, round(tax.base_tax_amount_after_discount_amount, 2))]
			if doc.doctype == "Purchase Invoice":
				allocations = get_purchase_tax_allocations(doc, tax)
			for tax_code, amount in allocations:
				# Excluded GST forms part of the purchase and its G13/G15 exclusion.
				management = "Subjected" if tax_code in {"AUPPVTUSE", "AUPINPTAX"} else tax_management
				result.extend(
					generate_bas_labels(
						management, tax_allocation, tax_code, tax.account_head, amount, sum_depends_on[1]
					)
				)

		create_au_bas_entries(doc.doctype, doc.name, doc.company, doc.posting_date, result, sum_depends_on)


def get_purchase_tax_allocations(doc, tax):
	"""Use ERPNext v16's company-currency item tax amounts for mixed eligibility."""
	cent = Decimal("0.01")
	total = Decimal(str(tax.base_tax_amount_after_discount_amount)).quantize(cent, rounding=ROUND_HALF_UP)
	if tax.get("add_deduct_tax") == "Deduct":
		total = -total
	codes = {item.au_tax_code for item in doc.items}
	if not codes & {"AUPPVTUSE", "AUPINPTAX"}:
		return [(tax.au_tax_code, float(total))]
	if len(codes) == 1:
		return [(next(iter(codes)), float(total))]

	message = frappe._(
		"Mixed purchase GST requires item tax amounts that reconcile to the company-currency tax total. "
		"Recalculate the invoice taxes and check each item's eligibility before submitting."
	)
	try:
		item_codes = {id(item): item.au_tax_code for item in doc.items}
		seen = set()
		amounts = {}
		for row in getattr(doc, "_item_wise_tax_details", None) or []:
			if row.tax is not tax:
				continue
			key = id(row.item)
			if key not in item_codes or key in seen:
				raise ValueError
			seen.add(key)
			amount = Decimal(str(row.amount))
			if not amount.is_finite():
				raise ValueError
			code = item_codes[key]
			amounts[code] = amounts.get(code, Decimal(0)) + amount
		if seen != set(item_codes) or sum(amounts.values()).quantize(cent, rounding=ROUND_HALF_UP) != total:
			raise ValueError
	except (ValueError, TypeError, InvalidOperation):
		frappe.throw(message)

	allocated = {code: amount.quantize(cent, rounding=ROUND_HALF_UP) for code, amount in amounts.items()}
	residual = total - sum(allocated.values())
	for code in sorted(amounts, key=lambda code: abs(amounts[code]), reverse=True):
		if not residual:
			break
		adjustment = (
			max(-allocated[code], residual) if amounts[code] >= 0 else min(-allocated[code], residual)
		)
		allocated[code] += adjustment
		residual -= adjustment
	return [(code, float(amount)) for code, amount in allocated.items()]


# Generate BAS Labels for the given tax_allocation, au_tax_code and account
def generate_bas_labels(tax_management, tax_allocation, au_tax_code, account, amount, amount_label):
	res = []
	if amount:
		bas_labels = frappe.get_all(
			"AU BAS Label Setup",
			filters={
				"tax_management": tax_management,
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


def create_au_bas_entries(doctype, docname, company, posting_date, result, sum_depends_on):
	"""
	Group all the BAS Labels depending on the account and au_tax_code.
	Then create AU BAS Entries
	"""
	if result:
		result = pd.DataFrame(result)
		cols_to_sum = [c for c in sum_depends_on if c in result.columns]
		result = result.groupby(["bas_label", "account", "tax_code"], as_index=False)[cols_to_sum].sum()
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


# update au_tax_code for Sales Invoice Items
def update_tax_code_for_sales_invoice_item(items, tax_template):
	for item in items:
		if item.input_taxed:
			item.au_tax_code = "AUSINPTAX"
		else:
			update_tax_code_for_item(item, tax_template)


# update au_tax_code for Purchase Invoice Items
def update_tax_code_for_purchase_invoice_item(items, tax_template):
	for item in items:
		if item.input_taxed:
			item.au_tax_code = "AUPINPTAX"
		elif item.private_use:
			item.au_tax_code = "AUPPVTUSE"
		else:
			update_tax_code_for_item(item, tax_template)


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


# update au_tax_code for Taxes and Charges
def update_tax_code_for_tax(tax, tax_template):
	tax_code = frappe.db.get_value(
		"AU Tax Determination",
		{"bp_tax_template": tax_template, "item_tax_template": ""},
		"tax_code",
	)
	tax.au_tax_code = tax_code


def on_cancel(doc, event):
	bas_entries = frappe.get_list("AU BAS Entry", filters={"voucher_no": doc.name}, pluck="name")
	for bas_entry in bas_entries:
		frappe.delete_doc("AU BAS Entry", bas_entry, ignore_permissions=True)
