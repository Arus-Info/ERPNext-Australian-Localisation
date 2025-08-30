import frappe
from frappe import _

from erpnext_australian_localisation.erpnext_australian_localisation.doctype.payment_batch.payment_batch import (
	update_on_payment_entry_updation,
)


def on_submit(doc, event):
	if frappe.db.exists("Payment Batch Item", {"payment_entry": doc.name, "docstatus": 0}):
		frappe.throw(_("Can't submit Payment Entry. Connected with Payment Batch"))


def on_update(doc, event):
	try:
		if not doc.is_child_table_same("references"):
			update_on_payment_entry_updation(doc.name, doc.paid_amount)

	except AttributeError as e:
		print(e)
