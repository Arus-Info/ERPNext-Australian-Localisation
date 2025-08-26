import frappe
from datetime import datetime


@frappe.whitelist()
def generate_aba_file(payment_batch):
	bank_account = frappe.db.get_value(
		"Bank Account",
		payment_batch.bank_account,
		["company", "apca_number", "bank_account_no", "branch_code", "bank.fi_abbr"],
		as_dict=True,
	)
	posting_date = datetime.strptime(payment_batch.posting_date, "%Y-%m-%d")

	# header
	content = "0"
	content += " " * 17
	content += "01"
	content += bank_account.fi_abbr
	content += " " * 7
	content += bank_account.company[0:26].ljust(26)
	content += bank_account.apca_number[0:6].rjust(6, "0")
	content += bank_account.company[0:12].ljust(12)
	content += posting_date.strftime("%d%m%y")
	content += " " * 40
	content += "\n"

	total_paid_amount = 0

	# for all receiver
	for payment_entry in payment_batch.payment_created:
		payment = frappe.db.get_value(
			"Payment Entry",
			payment_entry.payment_entry,
			["name", "party", "paid_amount", "lodgement_reference"],
			as_dict=True,
		)
		supplier_account_details = frappe.db.get_value(
			"Supplier", payment.party, ["bank_account_number", "bsb", "supplier_name"], as_dict=True
		)
		content += "1"
		content += supplier_account_details.bsb[0:7].ljust(7)
		content += supplier_account_details.bank_account_number[0:9].rjust(9)
		content += " "
		content += "50"
		content += str(round(payment.paid_amount * 100))[0:10].rjust(10, "0")
		content += supplier_account_details.supplier_name[0:32].ljust(32)
		if payment.lodgement_reference:
			content += payment.lodgement_reference.ljust(18)
		else:
			content += payment.name.ljust(18)
		content += bank_account.branch_code[0:7].ljust(7)
		content += bank_account.bank_account_no[0:9].rjust(9)
		content += bank_account.company[0:16].ljust(16)
		content += "0" * 8 + "\n"
		total_paid_amount += payment.paid_amount

	# footer
	content += "7"
	content += "999-999"
	content += " " * 12
	content += str(round(total_paid_amount * 100))[0:10].rjust(10, "0")
	content += str(round(total_paid_amount * 100))[0:10].rjust(10, "0")
	content += "0" * 10
	content += " " * 24
	content += str(len(payment_batch.payment_created)).rjust(6, "0")
	content += " " * 40
	content += "\n"

	return content
