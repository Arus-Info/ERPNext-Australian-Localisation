# Copyright (c) 2025, frappe.dev@arus.co.in and contributors
# For license information, please see license.txt

from datetime import datetime

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

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

		file = frappe.get_doc({"doctype": "File", "is_private": 1, "file_name": file_name})

		if self.file_format == "ABA":
			file.content = generate_aba_file(self)
			file.save()
			self.bank_file_url = file.file_url
			self.save()

		return self.bank_file_url


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_bank_account(doctype, txt, searchfield, start, page_len, filters):
	bank_with_fi_abbr = frappe.get_list("Bank", filters=[["fi_abbr", "!=", ""]], pluck="name")
	return frappe.get_list(
		"Bank Account",
		filters=[
			["bank", "in", bank_with_fi_abbr],
			["branch_code", "!=", ""],
			["bank_account_no", "!=", ""],
			["apca_number", "!=", ""],
		],
		as_list=True,
	)


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_payment_entry(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql(
		"""
		select name, party, paid_amount from `tabPayment Entry` where docstatus=0 and party_type ='Supplier'
		EXCEPT
		select payment_entry, supplier, amount from `tabPayment Batch Item`
		""",
		as_dict=True,
	)


@frappe.whitelist()
def update_payment_batch(source_name, target_doc=None, filters=None):
	supplier = frappe.db.get_value(
		"Payment Entry",
		source_name,
		["party as supplier", "paid_amount as amount", "name as payment_entry"],
		as_dict=True,
	)

	account_details = frappe.db.get_value("Supplier", supplier.supplier, ["bank_account_no", "bsb"])
	if not account_details[0] and not account_details[1]:
		frappe.msgprint(
			_("Can't add Payment Entry {0}. Bank details not available for {1}").format(
				source_name, supplier.supplier
			)
		)
	else:
		row = frappe.new_doc("Payment Batch Item")
		row.update(supplier)

		target_doc = create_payment_batch_invoices(source_name, target_doc)
		target_doc.append("payment_created", row)

	return target_doc


def create_payment_batch_invoices(source_name, target_doc=None):
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
