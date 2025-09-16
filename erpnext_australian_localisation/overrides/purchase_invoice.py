import frappe

from erpnext_australian_localisation.erpnext_australian_localisation.doctype.payment_batch.payment_batch import (
	update_on_payment_entry_updation,
)


def on_cancel(doc, event):
	payment_entry = frappe.db.get_value(
		"Payment Batch Invoice", {"purchase_invoice": doc.name}, "payment_entry"
	)
	if payment_entry:
		update_on_payment_entry_updation(payment_entry)
