import frappe

from erpnext_australian_localisation.erpnext_australian_localisation.doctype.payment_batch.payment_batch import (
	update_on_payment_entry_updation,
)
from erpnext_australian_localisation.overrides.invoices import (
	create_au_bas_entries,
	generate_bas_labels,
)


def on_update(doc, event):
	if doc.docstatus == 0:
		tax_template = "AU Non Capital Purchase - GST"

		if doc.taxes:
			item_tax_template = ""
		else:
			item_tax_template = "GST Exempt Purchase"

		for field in ["expenses", "taxes"]:
			for i in doc.get(field):
				if i.au_tax_code != "AUSINPTAX":
					tax_code = frappe.db.get_value(
						"AU Tax Determination",
						{
							"bp_tax_template": tax_template,
							"item_tax_template": item_tax_template,
						},
						"tax_code",
					)
					i.au_tax_code = tax_code
					i.save()


def before_submit(doc, event):
	result = []

	sum_depends_on = ["gst_offset_basis", "gst_offset_amount"]

	for expense in doc.expenses:
		account = frappe.db.get_value(
			"Expense Claim Account",
			{"parent": expense.expense_type, "company": doc.company},
			"default_account",
		)
		result.extend(
			generate_bas_labels(
				"Subjected",
				"Deductible Purchase",
				expense.au_tax_code,
				account,
				round(expense.sanctioned_amount, 2),
				sum_depends_on[0],
			)
		)

	for tax in doc.taxes:
		result.extend(
			generate_bas_labels(
				"Tax Account",
				"Deductible Purchase",
				tax.au_tax_code,
				tax.account_head,
				round(tax.tax_amount, 2),
				sum_depends_on[1],
			)
		)

	create_au_bas_entries(doc.doctype, doc.name, doc.company, doc.posting_date, result, sum_depends_on)


# if a Expense Claim Invoice is connected with a Payment Batch, update the Payment Batch
# def on_cancel(doc, event):
# 	payment_entry = frappe.db.get_value(
# 		"Payment Batch Invoice", {"reference_name": doc.name}, "payment_entry"
# 	)
# 	if payment_entry:
# 		update_on_payment_entry_updation(payment_entry)
