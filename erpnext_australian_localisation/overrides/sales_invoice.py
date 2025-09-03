import frappe

from erpnext_australian_localisation.overrides.invoices import (
	update_tax_code_for_item,
	update_tax_code_for_taxes,
)


def on_update(doc, event):
	if doc.taxes_and_charges:
		tax_template = frappe.db.get_value("Sales Taxes and Charges Template", doc.taxes_and_charges, "title")
		for item in doc.items:
			if item.input_taxed:
				item.item_tax_template = frappe.db.get_value(
					"Item Tax Template",
					{"title": "GST Exempt Sales", "company": doc.company},
					"name",
				)
				item.au_tax_code = "AUSINPTAX"
				item.save()

			else:
				update_tax_code_for_item(item, tax_template)

		update_tax_code_for_taxes(doc.taxes, tax_template)
