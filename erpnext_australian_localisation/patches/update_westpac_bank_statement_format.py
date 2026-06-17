import frappe


def execute():
	if not frappe.db.exists("AU Bank Statement Format", "Westpac CSV Format"):
		return

	doc = frappe.get_doc("AU Bank Statement Format", "Westpac CSV Format")

	doc.credit_debit_mapping = "Single credit&debit"
	doc.acc_no_col = "Bank Account"
	doc.sample_data = (
		"Bank Account,Date,Narrative,Debit Amount,Credit Amount,Balance,Categories,Serial\n"
		"320001234561,20250101,Salary Payment,5000,,10000,,1234567\n"
		"320001234561,20250102,Transfer Out,150.5,,4849.5,,1234568\n"
		"320001234561,20250103,BPAY Payment,45,,4804.5,,1234569\n"
		"320001234561,20250104,Refund,,100,4904.5,,1234570\n"
		"320001234561,20250105,BPAY Payment,50,,4854.5,,1234571"
	)

	doc.set(
		"mapping_fields",
		[
			{"erpnext_column": "Date", "bank_statement_column": "Date"},
			{"erpnext_column": "Deposit", "bank_statement_column": "Credit Amount"},
			{"erpnext_column": "Withdrawal", "bank_statement_column": "Debit Amount"},
			{"erpnext_column": "Description", "bank_statement_column": "Narrative"},
			{"erpnext_column": "Reference Number", "bank_statement_column": "Serial"},
		],
	)

	doc.save()
