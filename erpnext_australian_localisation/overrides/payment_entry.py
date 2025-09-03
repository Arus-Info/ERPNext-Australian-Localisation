import frappe
from frappe import _

from erpnext_australian_localisation.erpnext_australian_localisation.doctype.payment_batch.payment_batch import (
	update_on_payment_entry_updation,
)


def on_submit(doc, event):
	if frappe.db.exists("Payment Batch Item", {"payment_entry": doc.name, "docstatus": 0}):
		frappe.throw(_("Can't submit Payment Entry. Connected with Payment Batch."))


def on_update(doc, event):
	if doc.payment_type == "Pay":
		for r in doc.references:
			payment = frappe.db.get_value(
				"Payment Batch Invoice",
				{"purchase_invoice": r.reference_name},
				["payment_entry", "parent as payment_batch"],
			)
			if payment:
				if payment[0] != doc.name:
					frappe.throw(
						_(
							"Purchase Invoice already found in Payment Entry {0} connected with Payment Batch {1}."
						).format(*payment)
					)

		update_on_payment_entry_updation(doc.name)
