import frappe
from frappe import _

from erpnext_australian_localisation.erpnext_australian_localisation.doctype.payment_batch.payment_batch import (
	update_on_payment_entry_updation,
)


# if a Purchase Invoice is connected with a Payment Batch, update the Payment Batch
def on_cancel(doc, event):
	payment_entry = frappe.db.get_value(
		"Payment Batch Invoice", {"reference_name": doc.name}, "payment_entry"
	)
	if payment_entry:
		update_on_payment_entry_updation(payment_entry)


def on_save(doc, event):
	for item in doc.items:
		if item.input_taxed or item.private_use:
			if not item.item_tax_template:
				frappe.throw(
					_(
						"Item Tax Template is mandatory when 'Purchase for Input-taxed Sales' or "
						"'Purchase for private use' is checked, because GST credit cannot be claimed "
						"on these purchases. Please select an Exempt Item Tax Template."
					)
				)

			if frappe.db.exists(
				"Item Tax Template Detail",
				{"parent": item.item_tax_template, "tax_rate": ["!=", 0]},
			):
				frappe.throw(
					_("Item Tax Template must be Exempt only. Other Item Tax Templates are not allowed.")
				)
