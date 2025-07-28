import frappe


def on_update(doc, event):

	if doc.taxes_and_charges :
		tax_template = frappe.db.get_value(
			"Sales Taxes and Charges Template", doc.taxes_and_charges, "title"
		)
		for item in doc.items:
			if item.input_taxed :
				item.item_tax_template = frappe.db.get_value(
					"Item Tax Template", {"title" : "GST Exempt Sales", "company" : doc.company }, "name")
				item.au_tax_code = "AUSINPTAX" 

			else :
				if item.item_tax_template:
					item_tax_template = frappe.db.get_value(
						"Item Tax Template", item.item_tax_template, "title"
					)
				else :
					item_tax_template = ""
				tax_code = frappe.db.get_value(
					"AU Tax Determination",
					{"bp_tax_template": tax_template, "item_tax_template": item_tax_template},
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