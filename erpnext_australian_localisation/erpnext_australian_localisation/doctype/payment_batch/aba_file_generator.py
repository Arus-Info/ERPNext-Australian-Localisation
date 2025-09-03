from datetime import datetime

import frappe
from frappe import _


@frappe.whitelist()
def generate_aba_file(payment_batch):
	bank_account = frappe.db.get_value(
		"Bank Account",
		payment_batch.bank_account,
		["company", "apca_number", "bank_account_no", "branch_code", "fi_abbr"],
		as_dict=True,
	)
	posting_date = datetime.strptime(payment_batch.posting_date, "%Y-%m-%d")

	# header
	content = "0"
	content += " " * 17
	content += "01"
	if bank_account.fi_abbr:
		content += bank_account.fi_abbr
	else:
		frappe.throw(
			_("Financial Institution Abbreviation not found for Bank Account {0}").format(
				payment_batch.bank_account
			)
		)
	content += " " * 7
	content += bank_account.company[0:26].ljust(26)
	if bank_account.apca_number:
		content += bank_account.apca_number[0:6].rjust(6, "0")
	else:
		frappe.throw(_("APCA Number not found for Bank Account {0}").format(payment_batch.bank_account))
	content += bank_account.company[0:12].ljust(12)
	content += posting_date.strftime("%d%m%y")
	content += " " * 40
	content += "\n"

	# for all receiver
	for payment_entry in payment_batch.payment_created:
		reference_no = frappe.db.get_value(
			"Payment Entry",
			payment_entry.payment_entry,
			"reference_no",
		)
		supplier_account_details = frappe.db.get_value(
			"Supplier",
			payment_entry.supplier,
			["bank_account_no", "branch_code", "supplier_name"],
			as_dict=True,
		)
		content += "1"

		if supplier_account_details.branch_code:
			content += supplier_account_details.branch_code[0:7].ljust(7)
		else:
			frappe.throw(_("Branch code not found for Supplier {0}").format(payment_entry.supplier))

		if supplier_account_details.bank_account_no:
			content += supplier_account_details.bank_account_no[0:9].rjust(9)
		else:
			frappe.throw(_("Bank account number not found for Supplier {0}").format(payment_entry.supplier))

		content += " "
		content += "50"
		content += str(round(payment_entry.amount * 100))[0:10].rjust(10, "0")
		content += supplier_account_details.supplier_name[0:32].ljust(32)
		content += reference_no[0:18].ljust(18)

		if bank_account.branch_code:
			content += bank_account.branch_code[0:7].ljust(7)
		else:
			frappe.throw(_("Branch code not found for Bank Account {0}").format(payment_batch.bank_account))

		if bank_account.bank_account_no:
			content += bank_account.bank_account_no[0:9].rjust(9)
		else:
			frappe.throw(
				_("Bank account number not found for Bank Account {0}").format(payment_batch.bank_account)
			)
		content += bank_account.company[0:16].ljust(16)
		content += "0" * 8
		content += "\n"

	# footer
	content += "7"
	content += "999-999"
	content += " " * 12
	content += str(round(payment_batch.total_paid_amount * 100))[0:10].rjust(10, "0")
	content += str(round(payment_batch.total_paid_amount * 100))[0:10].rjust(10, "0")
	content += "0" * 10
	content += " " * 24
	content += str(len(payment_batch.payment_created)).rjust(6, "0")
	content += " " * 40
	content += "\n"

	return content
