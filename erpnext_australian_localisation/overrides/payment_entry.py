import frappe
from frappe import _

from erpnext_australian_localisation.erpnext_australian_localisation.doctype.payment_batch.payment_batch import (
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
	if doc.payment_type == "Pay":
		payment_batch = frappe.db.get_value("Payment Batch Item", {"payment_entry": doc.name}, "parent")
		if payment_batch:
			bank_account = frappe.db.get_value("Payment Batch", payment_batch, "bank_account")
			if doc.bank_account != bank_account:
				frappe.throw(
					_(
						"Payment Entry is linked with Payment Batch <a href='/app/payment-batch/{0}'>{0}</a> which has Bank Account <a href='/app/bank-account/{1}'>{1}</a>."
					).format(payment_batch, bank_account)
				)
		for r in doc.references:
			payment = frappe.db.get_value(
				"Payment Batch Invoice",
				{"purchase_invoice": r.reference_name, "docstatus": 0},
				["payment_entry", "parent as payment_batch"],
			)
			if payment:
				if payment[0] != doc.name:
					frappe.throw(
						_(
							"Purchase Invoice already found in Payment Entry <a href='/app/payment-entry/{0}'>{0}</a> which is linked with Payment Batch <a href='/app/payment-batch/{1}'>{1}</a>."
						).format(*payment)
					)

		update_on_payment_entry_updation(doc.name)
