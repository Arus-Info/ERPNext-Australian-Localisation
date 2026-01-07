import csv
import io

import frappe
from frappe import _
from frappe.utils import getdate
from frappe.utils.file_manager import save_file


def after_save(doc, methos=None):
	# Run only if file & bank account exist(this is for safety check either needed or not needed)
	if not doc.bs_import_file:
		return

	# Get uploaded file doc safely
	file_doc = frappe.get_doc("File", {"file_url": doc.bs_import_file})

	# Read file content safely (str or bytes)
	content = file_doc.get_content()

	# Convert CSV to ERPNext format
	converted_csv = convert_to_erpnext_csv(content, doc.bank_account)

	# Save converted CSV properly
	new_file = save_file(
		fname=f"{doc.name}_erpnext.csv",
		content=converted_csv,
		dt="Bank Statement Import",
		dn=doc.name,
		is_private=1,
	)

	# Attach converted CSV to import_file
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
			"01/01/2025,-150.00,123456789,,DEBIT,"
			"Coffee Shop,12000.00,Food,Starbucks\n"
			"02/01/2025,2000.00,123456789,,CREDIT,"
			"Salary Credit,10000.00,Income,Employer\n"
			"03/01/2025,-300.00,123456789,,DEBIT,"
			"ecommerce,9700.00,Shopping,Flipkart\n"
			"04/01/2025,+1000.00,123456789,,CREDIT,"
			"Refund from flipkart,11700.00,Shopping,Flipkart\n"
			"05/01/2025,-400.00,123456789,,DEBIT,"
			"Hypermarket,11300.00,Grocery,lulu\n"
		)

		return {"filename": "NAB_Bank_Statement_Template.csv", "filecontent": csv_content}


# ---------------- HELPER FUNCTIONS ----------------


def convert_to_erpnext_csv(content, bank_account):
	output = io.StringIO()
	writer = csv.writer(output)

	# ERPNext required headers
	writer.writerow(["Date", "Deposit", "Withdrawal", "Description", "Bank Account", "Currency"])

	reader = csv.DictReader(io.StringIO(content))

	# Detect columns automatically
	date_col = find_column(reader.fieldnames, ["date"])
	amount_col = find_column(reader.fieldnames, ["amount"])
	desc_col = find_column(reader.fieldnames, ["transaction details"])

	bank = frappe.get_doc("Bank Account", bank_account)
	currency = bank.currency

	for row in reader:
		amount = float(row.get(amount_col) or 0)

		writer.writerow(
			[
				normalize_date(row.get(date_col)),
				amount if amount > 0 else "",
				abs(amount) if amount < 0 else "",
				row.get(desc_col),
				bank_account,
				currency,
			]
		)

	return output.getvalue()


def find_column(columns, keywords):
	for col in columns:
		for key in keywords:
			if key in col.lower():
				return col
	frappe.throw(f"Required column not found: {keywords}")


def normalize_date(date_str):
	try:
		return getdate(date_str).strftime("%Y-%m-%d")
	except Exception:
		frappe.throw(f"Invalid date format: {date_str}")
