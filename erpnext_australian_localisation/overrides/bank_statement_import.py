import csv
import io
import re
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

	# pass bank_account & currency
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


# --------------------------------template------------------------------#
@frappe.whitelist()
def download_uploaded_csv_template(bank_account):
	if not bank_account:
		frappe.throw(_("Please select Bank Account"))

	bank_statement_format = frappe.db.get_value("Bank Account", bank_account, "bank_statement_format")

	if not bank_statement_format:
		frappe.throw(_("Please set Bank Statement Format in Bank Account"))

	format_doc = frappe.get_doc("AU Bank Statement Format", bank_statement_format)

	if not format_doc.sample_data:
		frappe.throw(_("CSV Template not configured for this Bank Statement Format"))

	return {
		"filename": f"{bank_statement_format}.csv",
		"filecontent": format_doc.sample_data,
	}


# ----------------FUNCTIONS ----------------


def convert_using_child_mapping(content, format_doc, bank_account, currency):
	output = io.StringIO()
	writer = csv.writer(output)

	reader = csv.DictReader(io.StringIO(content))

	# validation of bank account number
	validate_account_and_branch(reader=reader, format_doc=format_doc, bank_account=bank_account)

	# Reset reader after validation
	reader = csv.DictReader(io.StringIO(content))

	# mapping from child table
	# -------------------------------
	mapping = {}
	for row in format_doc.mapping_fields:
		if row.erpnext_column and row.bank_statement_column:
			mapping[row.erpnext_column] = row.bank_statement_column

	# ERPNext headers
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

		out["Description"] = csv_row.get(mapping.get("Description"))

		if "Reference Number" in mapping:
			out["Reference Number"] = csv_row.get(mapping.get("Reference Number"), "")

		# ---------------- SYSTEM FIELDS ----------------
		out["Bank Account"] = bank_account
		out["Currency"] = currency

		writer.writerow([out.get(col) for col in headers])

	return output.getvalue()


# DATE
# --------------------------------------------------
def normalize_date(value, row_no=None):
	if not value:
		frappe.throw(f"Missing Date at row {row_no}")

	value = value.strip()

	try:
		#  Handles YYYYMMDD (20250102)
		if value.isdigit() and len(value) == 8:
			dt = datetime.strptime(value, "%Y%m%d")
		else:
			# Handles: 01/01/2025, 01-Jan-25, 2025-01-02, etc
			dt = parse(value, dayfirst=True)

		return dt.strftime("%Y-%m-%d")

	except Exception:
		frappe.throw(f"Invalid date '{value}' at row {row_no}")


# ------------------------------------------------------------------------


def validate_account_and_branch(reader, format_doc, bank_account):
	bank_acc_no = frappe.db.get_value("Bank Account", bank_account, "bank_account_no")
	branch_code = frappe.db.get_value("Bank Account", bank_account, "branch_code")
	# this is for csv header name(account number) there or not
	acc_col = format_doc.acc_no_col
	# if header not there exits silently
	if not acc_col:
		return

	def validate_format(val, row_no):
		# Allow ONLY digits and hyphen
		if not re.fullmatch(r"[0-9\-]+", val):
			frappe.throw(
				_("Invalid Account Number format at row {0}. Only digits and '-' are allowed.").format(row_no)
			)

	# this is for empty csv file if there is
	row_found = False

	# iterates csv rows
	for row_no, row in enumerate(reader, start=2):
		# this row_found insists that csv has atleast one row
		row_found = True
		# reads acc no from csv and removes spaces and values are configured
		raw_val = (row.get(acc_col) or "").strip()
		# csv acc no and entire col missing throws error
		if not raw_val:
			frappe.throw(_("Account Number is missing in CSV at row {0}").format(row_no))
		validate_format(raw_val, row_no)
		# Remove spaces ONLY (not hyphen)
		csv_val = raw_val.replace(" ", "")

		# ANZ → branch + account must match
		if format_doc.name == "ANZ CSV Format":
			if not branch_code:
				frappe.throw(_("Branch Code is mandatory for ANZ bank accounts."))

			expected = f"{branch_code}-{bank_acc_no}"

			if csv_val != expected:
				frappe.throw(
					_(
						"Account Number mismatch at row {0}.<br><b>Bank Account Number :</b> {1}<br><b>CSV Value:</b> {2}"
					).format(row_no, expected, raw_val)
				)
		# NAB / Westpac → only account number
		else:
			expected = bank_acc_no.replace(" ", "")

			if csv_val != expected:
				frappe.throw(
					_(
						"Account Number mismatch at row {0}.<br><b>Bank Account Number :</b> {1}<br><b>CSV Value:</b> {2}"
					).format(row_no, expected, raw_val)
				)

	if not row_found:
		frappe.throw(_("CSV file is empty"))

	frappe.msgprint(_("Bank Account validation successfully passed for all rows"), indicator="green")
