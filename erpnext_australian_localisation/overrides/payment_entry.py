import frappe
from frappe import _

from erpnext_australian_localisation.erpnext_australian_localisation.doctype.payment_batch.payment_batch import (
	create_payment_batch_invoices,
)


def on_submit(doc, event):
	if frappe.db.exists("Payment Batch Item", {"payment_entry": doc.name, "docstatus": 0}):
		frappe.throw(_("Can't submit Payment Entry. Connected with Payment Batch"))


# def on_cancel(doc,event):
# 	if frappe.db.exists("Payment Batch Item",{"payment_entry": doc.name, "docstatus": 1}) :
# 		frappe.throw("Can't cancel Payment Entry. Connected with Payment Batch")


def on_update(doc, event):
	try:
		if not doc.is_child_table_same("references"):
			invoices = frappe.get_list(
				"Payment Batch Invoice",
				parent_doctype="Payment Batch",
				filters={"payment_entry": doc.name},
				fields=["name", "parent"],
			)
			if invoices:
				for i in invoices:
					frappe.delete_doc("Payment Batch Invoice", i.name)

				if doc.references:
					target_doc = frappe.get_doc("Payment Batch", invoices[0].parent)
					payment_batch = create_payment_batch_invoices(doc.name, target_doc)
					payment_batch.save()
	except AttributeError as e:
		print(e)
