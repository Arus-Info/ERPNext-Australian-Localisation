import frappe
from frappe import _

from erpnext_australian_localisation.erpnext_australian_localisation.doctype.payment_batch.payment_batch import (
	is_payment_entry_references_exists,
	update_on_payment_entry_updation,
)


def on_submit(doc, event):
	payment_batch = frappe.db.get_value(
		"Payment Batch Item", {"payment_entry": doc.name, "docstatus": 0}, "parent"
	)
	if payment_batch:
		frappe.throw(
			_(
				"Cannot submit because Payment Entry is linked with Payment Batch <a href='/app/payment-batch/{0}'>{0}</a>."
			).format(payment_batch)
		)


def on_update(doc, event):
	"""
	Note: This Control is only applicable for Payment Entries and Purchase Invoices which are included in Payment Batch

	Check whether the Payment Entry is linked to any Payment Batch.
	If it is linked, verify that the Payment Entry has the same Bank Account as the Payment Batch.
	Next, check whether any Payment Entry References included in this Payment Entry is already present in any other Payment Entry.
	If it is not linked, check whether the Payment Entry References included here is not linked to any other Payment Batch Reference
	"""
	if doc.payment_type == "Pay":
		payment_batch = frappe.db.get_value("Payment Batch Item", {"payment_entry": doc.name}, "parent")
		if payment_batch:
			if doc.has_value_changed("bank_account"):
				bank_account = frappe.db.get_value("Payment Batch", payment_batch, "bank_account")
				if doc.bank_account != bank_account:
					frappe.throw(
						_(
							"Payment Entry is linked with Payment Batch <a href='/app/payment-batch/{0}'>{0}</a> which has Bank Account <a href='/app/bank-account/{1}'>{1}</a>."
						).format(payment_batch, bank_account)
					)
			for reference in doc.references:
				is_payment_entry_references_exists(doc.name, reference)
			update_on_payment_entry_updation(doc.name)  # update Payment Batch
		else:
			for r in doc.references:
				payment = frappe.db.get_value(
					"Payment Batch Reference",
					{"reference_name": r.reference_name, "docstatus": 0},
					["payment_entry", "parent as payment_batch"],
				)
				if payment:
					if payment[0] != doc.name:
						frappe.throw(
							_(
								"{0} already found in Payment Entry <a href='/app/payment-entry/{1}'>{1}</a> which is linked with Payment Batch <a href='/app/payment-batch/{2}'>{2}</a>."
							).format(r.reference_doctype, *payment)
						)
