import csv
import io
from datetime import datetime

import frappe
from dateutil.parser import parse
from frappe import _
from frappe.utils.file_manager import save_file


def after_save(doc, methods=None):
	if not doc.bs_import_file:
		return

	bank_statement_format = frappe.db.get_value("Bank Account", doc.bank_account, "bank_statement_format")

	if not bank_statement_format:
		frappe.throw(_("Please set Bank Statement Format in Bank Account"))

	format_doc = frappe.get_doc("AU Bank Statement Format", bank_statement_format)

	currency = frappe.db.get_value("Bank Account", doc.bank_account, "currency")

	if not currency:
		frappe.throw(_("Currency is missing in Bank Account"))

	file_doc = frappe.get_doc("File", {"file_url": doc.bs_import_file})
	content = file_doc.get_content()

	# ✅ PASS bank_account & currency
	converted_csv = convert_using_child_mapping(
		content=content, format_doc=format_doc, bank_account=doc.bank_account, currency=currency
	)

	new_file = save_file(
		fname=f"{doc.name}_erpnext.csv",
		content=converted_csv,
		dt="Bank Statement Import",
		dn=doc.name,
		is_private=1,
	)

	doc.db_set("import_file", new_file.file_url)


# --------------------------------tempalte------------------------------#
@frappe.whitelist()
def download_uploaded_csv_template(bank_account):
	if not bank_account:
		frappe.throw(_("Please select Bank Account"))

	bank_statement_format = frappe.db.get_value("Bank Account", bank_account, "bank_statement_format")

	# ✅ NAB CSV TEMPLATE WITH EXAMPLE VALUES
	if bank_statement_format == "NAB CSV Format":
		csv_content = (
			"Date,Amount,Account Number,,Transaction Type,"
			"Transaction Details,Balance,Category,Merchant Name\n"
			"29 Dec 25,-1200.00,234567819,,DEBIT,"
			"Monthly house rent,6856.50,Housing,Property Manager\n"
			"29 Dec 25,-250.00,234567819,,DEBIT,"
			"Online shopping,8056.50,Shopping,Amazon AU\n"
			"26 Dec 25,-65.00,234567819,,DEBIT,"
			"Fuel purchase,8306.50,Transport,BP Australia\n"
			"24 Dec 25,3500.00,234567819,,CREDIT,"
			"Salary payment,8371.50,Income,ABC Pty Ltd\n"
			"23 Dec 25,-120.00,234567819,,DEBIT,"
			"Grocery shopping,4871.50,Groceries,Woolworths\n"
			"22 Dec 25,-400.00,234567819,,DEBIT,"
			"Coffee purchase,4991.50,Food&Drink,Starbucks"
		)

		return {"filename": "NAB_Bank_Statement_Template.csv", "filecontent": csv_content}

	# ✅ COMMONWEALTH CSV TEMPLATES WITH EXAMPLE VALUES
	elif bank_statement_format == "Commonwealth Bank CSV Format":
		csv_content = (
			"Date,Amount,Description,Balance\n"
			"01/01/2025,5000.00,Salary Payment,15000.00\n"
			"02/01/2025,-150.50,Transfer Out,14849.50\n"
			"03/01/2025,-45.00,BPAY Payment,14804.50\n"
			"04/01/2025,+200.00,Refund,15004.50\n"
			"05/01/2025,-200.00,Grocery shopping,14804.50\n"
		)

		return {"filename": "CBA_Bank_Statement_Template.csv", "filecontent": csv_content}

	elif bank_statement_format == "Westpac CSV Format":
		csv_content = (
			"TRAN_DATE,ACCOUNT_NO,ACCOUNT_NAME,CCY,CLOSING_BAL,AMOUNT,TRAN_CODE,NARRATIVE,SERIAL\n"
			"20250101,032000123456,Business Account,AUD,15000.00,5000.00,050,Salary Payment,1234567\n"
			"20250102,032000123456,Business Account,AUD,14849.50,-150.50,009,Transfer Out,1234568\n"
			"20250103,032000123456,Business Account,AUD,14804.50,-45.00,013,BPAY Payment,1234569\n"
			"20250104,032000123456,Business Account,AUD,14904.50,100.00,014,Shopping,1234570\n"
			"20250105,032000123456,Business Account,AUD,18854.50,-50.00,017,BPAY Payment,1234571"
		)

		return {"filename": "Westpac_Bank_Statement_Template.csv", "filecontent": csv_content}
	elif bank_statement_format == "ANZ CSV Format":
		csv_content = (
			"Statement Number,Account Number,Account Name,Account Currency,Opening Available Balance,Opening Ledger Balance,Closing Available Balance,Closing Ledger Balance,Value Date,Post Date,Tran Type,Bank Reference,Narrative,Debits,Credits\n"
			"1,013-999-123456,Business Account,AUD,10000.00,10000.00,17418.75,17418.75,01-Jan-25,01-Jan-25,DEPOSIT,REF001,Salary Payment,0.00,5000.00\n"
			"1,013-999-123456,Business Account,AUD,15000.00,15000.00,14849.50,14849.50,02-Jan-25,02-Jan-25,PAYMENT,REF002,Transfer Out,150.50,0.00\n"
			"1,013-999-123456,Business Account,AUD,14849.50,14849.50,14804.50,14804.50,03-Jan-25,03-Jan-25,BPAY,REF003,BPAY Payment,45.00,0.00\n"
			"1,013-999-123456,Business Account,AUD,14804.50,14804.50,15204.50,15204.50,04-Jan-25,04-Jan-25,SHOPPING,REF004,Refund,0.00,400.00\n"
			"1,013-999-123456,Business Account,AUD,15204.50,15204.50,15159.50,15159.50,05-Jan-25,05-Jan-25,BPAY,REF005,BPAY Payment,45.00,0.00"
		)

		return {"filename": "ANZ_Bank_Statement_Template.csv", "filecontent": csv_content}


# ---------------- HELPER FUNCTIONS ----------------


def convert_using_child_mapping(content, format_doc, bank_account, currency):
	output = io.StringIO()
	writer = csv.writer(output)

	reader = csv.DictReader(io.StringIO(content))

	# Build mapping from child table
	# -------------------------------
	mapping = {}
	for row in format_doc.mapping_fields:
		if row.erpnext_column and row.bank_statement_column:
			mapping[row.erpnext_column] = row.bank_statement_column

	# Build ERPNext headers dynamically
	# -------------------------------
	headers = ["Date", "Deposit", "Withdrawal", "Description"]

	if "Reference Number" in mapping:
		headers.append("Reference Number")

	headers += ["Bank Account", "Currency"]
	writer.writerow(headers)

	# Process rows

	for row_no, csv_row in enumerate(reader, start=2):
		out = {}

		# ---------------- DATE ----------------
		date_value = csv_row.get(mapping.get("Date"))
		out["Date"] = normalize_date(date_value, row_no=row_no)

		# ---------------- AMOUNT ----------------

		deposit = ""
		withdrawal = ""

		credit_debit_mapping = format_doc.credit_debit_mapping  # Select field

		# CASE 1: Combined Credit and Debit (single amount column)
		if credit_debit_mapping == "Combined credit&debit":
			amount_col = mapping.get("Deposit") or mapping.get("Withdrawal")
			amount_raw = csv_row.get(amount_col)

			if amount_raw:
				val = amount_raw.strip()
				if val.startswith("-"):
					withdrawal = val.lstrip("-")
				else:
					deposit = val.lstrip("+")

		# CASE 2: Single Credit and Debit (separate columns)
		elif credit_debit_mapping == "Single credit&debit":
			if "Deposit" in mapping:
				deposit = csv_row.get(mapping.get("Deposit"), "")

			if "Withdrawal" in mapping:
				withdrawal = csv_row.get(mapping.get("Withdrawal"), "")
		out["Deposit"] = deposit
		out["Withdrawal"] = withdrawal

		# ---------------- DESCRIPTION ----------------

		out["Description"] = csv_row.get(mapping.get("Description"))

		if "Reference Number" in mapping:
			out["Reference Number"] = csv_row.get(mapping.get("Reference Number"), "")

		# ---------------- SYSTEM FIELDS ----------------
		out["Bank Account"] = bank_account
		out["Currency"] = currency

		writer.writerow([out.get(col) for col in headers])

	return output.getvalue()


# --------------------------------------------------
# DATE NORMALIZATION
# --------------------------------------------------
def normalize_date(value, row_no=None):
	if not value:
		frappe.throw(f"Missing Date at row {row_no}")

	value = value.strip()

	try:
		# ✅ Handle YYYYMMDD (20250102)
		if value.isdigit() and len(value) == 8:
			dt = datetime.strptime(value, "%Y%m%d")
		else:
			# Handles: 01/01/2025, 01-Jan-25, 2025-01-02, etc
			dt = parse(value, dayfirst=True)

		return dt.strftime("%Y-%m-%d")

	except Exception:
		frappe.throw(f"Invalid date '{value}' at row {row_no}")
