# Copyright (c) 2025, frappe.dev@arus.co.in and contributors
# For license information, please see license.txt

import json
from datetime import datetime

import frappe
from frappe import _
from frappe.model.document import Document

from erpnext_australian_localisation.erpnext_australian_localisation.doctype.payment_batch.aba_file_generator import (
	generate_aba_file,
)


class PaymentBatch(Document):
	def on_submit(self):
		for row in self.payment_created:
			payment_entry = frappe.get_doc("Payment Entry", row.payment_entry)
			payment_entry.posting_date = self.posting_date
			payment_entry.submit()

	def on_cancel(self):
		for row in self.payment_created:
			payment_entry = frappe.get_doc("Payment Entry", row.payment_entry)
			payment_entry.cancel()

	@frappe.whitelist()
	def generate_bank_file(self):
		file_name = self.name + "." + self.file_format
		file = frappe.db.exists("File", {"file_name": file_name})
		if file:
			frappe.delete_doc("File", file)
			self.bank_file_url = ""
			self.save()
			# need to delete the previous file
			frappe.db.commit()  # nosemgrep

		file = frappe.get_doc({"doctype": "File", "is_private": 1, "file_name": file_name})

		if self.file_format == "ABA":
			file.content = generate_aba_file(self)
			file.save()
			self.bank_file_url = file.file_url
			self.save()

		return self.bank_file_url


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_payment_entry(doctype, txt, searchfield, start, page_len, filters):
	if filters.get("party"):
		filters["party"] += "%"
	else:
		filters["party"] = "%"

	return frappe.db.sql(
		"""
		select
			name, party, base_paid_amount
		from `tabPayment Entry`
		where docstatus=0 and party_type ='Supplier' and company=%(company)s and party like %(party)s and bank_account=%(bank_account)s

		EXCEPT
		select payment_entry, supplier, amount from `tabPayment Batch Item`
		""",
		filters,
		as_dict=True,
	)


@frappe.whitelist()
def update_payment_batch(source_name, target_doc=None):
	supplier = frappe.db.get_value(
		"Payment Entry",
		source_name,
		["party as supplier", "base_paid_amount as amount", "name as payment_entry"],
		as_dict=True,
	)

	account_details = frappe.db.get_value("Supplier", supplier.supplier, ["bank_account_no", "branch_code"])
	if account_details[0] and account_details[1]:
		row = frappe.new_doc("Payment Batch Item")
		row.update(supplier)

		target_doc = create_payment_batch_invoices(source_name, target_doc)
		target_doc.append("payment_created", row)
		target_doc = update_total_paid_amount(target_doc)

	else:
		frappe.msgprint(
			_("Can't add Payment Entry {0}. Bank details not available for {1}").format(
				source_name, supplier.supplier
			)
		)

	return target_doc


def create_payment_batch_invoices(source_name, target_doc=None):
	from frappe.model.mapper import get_mapped_doc

	doc = get_mapped_doc(
		"Payment Entry",
		source_name,
		{
			"Payment Entry": {"doctype": "Payment Batch"},
			"Payment Entry Reference": {
				"doctype": "Payment Batch Invoice",
				"field_map": {
					"reference_name": "purchase_invoice",
					"party": "supplier",
				},
			},
		},
		target_doc,
	)

	payment_entry = frappe.db.get_value(
		"Payment Entry", source_name, ["unallocated_amount", "party"], as_dict=True
	)
	if payment_entry.unallocated_amount:
		row = frappe.new_doc("Payment Batch Invoice")
		row.update(
			{
				"payment_entry": source_name,
				"supplier": payment_entry.party,
				"allocated_amount": payment_entry.unallocated_amount,
			}
		)
		doc.append("paid_invoices", row)

	return doc


def update_total_paid_amount(payment_batch):
	total_paid_amount = 0
	for i in payment_batch.payment_created:
		total_paid_amount += i.amount
	payment_batch.total_paid_amount = total_paid_amount

	return payment_batch


def update_on_payment_entry_updation(payment_entry):
	invoices = frappe.get_list(
		"Payment Batch Invoice",
		parent_doctype="Payment Batch",
		filters={"payment_entry": payment_entry, "docstatus": 0},
		fields=["name", "parent"],
	)
	if invoices:
		for i in invoices:
			frappe.delete_doc("Payment Batch Invoice", i.name)

		target_doc = frappe.get_doc("Payment Batch", invoices[0].parent)
		payment_batch = create_payment_batch_invoices(payment_entry, target_doc)
		payment_batch.save()

		update_total_paid_amount(payment_batch)
		payment_batch.save()


@frappe.whitelist()
def create_payment_batch_again(doc):
	doc = json.loads(doc)

	pb = frappe.new_doc("Payment Batch")
	pb.update(
		{"bank_account": doc["bank_account"], "company": doc["company"], "posting_date": doc["posting_date"]}
	)

	for payment in doc["payment_created"]:
		old_pe = frappe.get_doc("Payment Entry", payment["payment_entry"])
		pe = frappe.copy_doc(old_pe)
		pe.amended_from = payment["payment_entry"]
		pe.save()
		update_payment_batch(pe.name, pb)

	pb.save()
	return pb.name
