import frappe

from erpnext_australian_localisation.erpnext_australian_localisation.doctype.payment_batch.payment_batch import (
	update_on_payment_entry_updation,
)


def on_update(doc, event):
	if doc.taxes_and_charges:
		tax_template = frappe.db.get_value(
			"Purchase Taxes and Charges Template", doc.taxes_and_charges, "title"
		)
		for item in doc.items:
			if item.input_taxed or item.private_use:
				item.item_tax_template = frappe.db.get_value(
					"Item Tax Template",
					{"title": "GST Exempt Purchase", "company": doc.company},
					"name",
				)
				if item.input_taxed:
					item.au_tax_code = "AUPINPTAX"
				elif item.private_use:
					item.au_tax_code = "AUPPVTUSE"

			else:
				if item.item_tax_template:
					item_tax_template = frappe.db.get_value(
						"Item Tax Template", item.item_tax_template, "title"
					)
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

		for tax in doc.taxes:
			tax_code = frappe.db.get_value(
				"AU Tax Determination",
				{"bp_tax_template": tax_template, "item_tax_template": ""},
				"tax_code",
			)
			tax.au_tax_code = tax_code
			tax.save()


def on_cancel(doc, event):
	payment_entry = frappe.db.get_value(
		"Payment Batch Invoice", {"purchase_invoice": doc.name}, "payment_entry"
	)

	if payment_entry:
		update_on_payment_entry_updation(payment_entry)
