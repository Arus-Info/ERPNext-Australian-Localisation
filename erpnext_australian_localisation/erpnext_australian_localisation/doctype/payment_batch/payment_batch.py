# Copyright (c) 2025, frappe.dev@arus.co.in and contributors
# For license information, please see license.txt

import json

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
	"""
	Return Payment Entries that are posted in the given Bank Account and are in draft state,
	except those that are already included in another Payment Batch
	"""
	if filters.get("party_name"):
		filters["party_name"] += "%"
	else:
		filters["party_name"] = "%"

	return frappe.db.sql(
		"""
		select
			name, party_name, base_paid_amount
		from `tabPayment Entry`
		where docstatus=0 and party_type =%(party_type)s and company=%(company)s and party_name like %(party_name)s and bank_account=%(bank_account)s

		EXCEPT
		select payment_entry, party_name, amount from `tabPayment Batch Item`
		""",
		filters,
		as_dict=True,
	)


@frappe.whitelist()
def update_payment_batch(source_name, target_doc=None):
	"""
	Update the Payment Batch by adding the Payment Entry
		source_name : str (PaymentEntry)
		target_doc: str of json PaymentBatch
	"""
	party = frappe.db.get_value(
		"Payment Entry",
		source_name,
		["party", "party_type", "party_name", "base_paid_amount as amount", "name as payment_entry"],
		as_dict=True,
	)

	account_details = frappe.db.get_value(party.party_type, party.party, ["bank_account_no", "branch_code"])
	if account_details[0] and account_details[1]:
		row = frappe.new_doc("Payment Batch Item")
		row.update(party)

		target_doc = create_payment_batch_references(source_name, target_doc)
		target_doc.append("payment_created", row)
		target_doc = update_total_paid_amount(target_doc)

	else:
		frappe.msgprint(
			_("Can't add Payment Entry {0}. Bank details not available for {1}").format(
				source_name, party.party
			)
		)

	return target_doc


# check whether any Payment Entry Invoice in the given Payment Entry is already present in another Payment Entry
def is_payment_entry_references_exists(name, reference):
	payment_entries = frappe.get_list(
		"Payment Entry Invoice",
		parent_doctype="Payment Entry",
		filters={
			"reference_name": reference.reference_name,
			"docstatus": 0,
			"parent": ["!=", name],
		},
		fields=["parent"],
		pluck="parent",
	)
	if payment_entries:
		frappe.throw(
			_(
				"Payment Entry {0}: {1} {2} already found in Payment Entry  <a href='/app/payment-entry/{3}'>{3}</a>"
			).format(name, reference.reference_doctype, reference.reference_name, payment_entries[0])
		)
		# return True
	else:
		return True


# create Payment Batch Invoices for Payment Entry Invoices
def create_payment_batch_references(source_name, target_doc=None):
	from frappe.model.mapper import get_mapped_doc

	# update party details in every Payment Batch Invoice
	def update_party_details(payment_entry_reference, payment_batch_reference, payment_entry):
		payment_batch_reference.update(
			{
				"party": payment_entry.party,
				"party_type": payment_entry.party_type,
				"party_name": payment_entry.party_name,
			}
		)

	def condition(doc):
		return is_payment_entry_references_exists(source_name, doc)

	# map all Payment Entry Invoice to Payment Batch Invoice
	doc = get_mapped_doc(
		"Payment Entry",
		source_name,
		{
			"Payment Entry": {"doctype": "Payment Batch"},
			"Payment Entry Invoice": {
				"doctype": "Payment Batch Invoice",
				"condition": condition,
				"postprocess": update_party_details,
			},
		},
		target_doc,
	)

	payment_entry = frappe.db.get_value(
		"Payment Entry",
		source_name,
		["unallocated_amount as allocated_amount", "party", "party_type", "party_name"],
		as_dict=True,
	)

	# add a Payment Batch Invoice if an unallocated amount exists.
	if payment_entry.allocated_amount:
		row = frappe.new_doc("Payment Batch Invoice")
		row.update({"payment_entry": source_name, **payment_entry})
		doc.append("paid_invoices", row)

	return doc


# update the total paid amount of the given Payment Batch
def update_total_paid_amount(payment_batch):
	total_paid_amount = 0
	for i in payment_batch.payment_created:
		total_paid_amount += i.amount
	payment_batch.total_paid_amount = total_paid_amount

	return payment_batch


# if Payment Entry is updated, update the linked Payment Batch
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
		payment_batch = create_payment_batch_references(payment_entry, target_doc)
		payment_batch.save()

		update_total_paid_amount(payment_batch)
		payment_batch.save()


@frappe.whitelist()
def create_payment_batch_again(doc):
	"""
	Rework Batch
	Amend all cancelled Payment Entry to create a new Payment Batch
	"""
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
