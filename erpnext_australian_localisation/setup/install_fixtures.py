import frappe
from frappe.desk.page.setup_wizard.setup_wizard import make_records


def create_default_records():
	records = []
	records.extend(get_au_tax_codes())
	records.extend(get_au_tax_determination())
	records.extend(get_au_bas_labels())
	records.extend(get_au_bas_label_setup())
	records.extend(get_au_bank_statement_format())

	make_records(records)


def get_au_tax_codes():
	records = [
		{
			"doctype": "AU Tax Code",
			"tax_code": "AUSGST",
			"tax_description": "Sales GST",
		},
		{
			"doctype": "AU Tax Code",
			"tax_code": "AUSFREX",
			"tax_description": "Sales Free or Exempt",
		},
		{
			"doctype": "AU Tax Code",
			"tax_code": "AUSEXP",
			"tax_description": "Sales Export",
		},
		{
			"doctype": "AU Tax Code",
			"tax_code": "AUSINPTAX",
			"tax_description": "Input Taxed Sales",
		},
		{
			"doctype": "AU Tax Code",
			"tax_code": "AUPCAGST",
			"tax_description": "Capital Purchase GST",
		},
		{
			"doctype": "AU Tax Code",
			"tax_code": "AUPCAFREX",
			"tax_description": "Capital Purchase GST Free/Exempt",
		},
		{
			"doctype": "AU Tax Code",
			"tax_code": "AUPNCAFR",
			"tax_description": "Non Capital Purchase GST Free/Exempt",
		},
		{
			"doctype": "AU Tax Code",
			"tax_code": "AUPNCASGT",
			"tax_description": "Non Capital Purchase GST",
		},
		{
			"doctype": "AU Tax Code",
			"tax_code": "AUPINPTAX",
			"tax_description": "Purchase for Input Tax Sales",
		},
		{
			"doctype": "AU Tax Code",
			"tax_code": "AUPPVTUSE",
			"tax_description": "Purchases for private use / not income tax deductible",
		},
	]
	return records


def get_au_tax_determination():
	records = [
		{
			"doctype": "AU Tax Determination",
			"type": "Purchase",
			"bp_tax_template": "AU Non Capital Purchase - GST",
			"item_tax_template": "",
			"tax_code": "AUPNCASGT",
		},
		{
			"doctype": "AU Tax Determination",
			"type": "Purchase",
			"bp_tax_template": "Import & GST-Free Purchase",
			"item_tax_template": "",
			"tax_code": "AUPNCAFR",
		},
		{
			"doctype": "AU Tax Determination",
			"type": "Purchase",
			"bp_tax_template": "AU Capital Purchase - GST",
			"item_tax_template": "",
			"tax_code": "AUPCAGST",
		},
		{
			"doctype": "AU Tax Determination",
			"type": "Purchase",
			"bp_tax_template": "AU Non Capital Purchase - GST",
			"item_tax_template": "GST Exempt Purchase",
			"tax_code": "AUPNCAFR",
		},
		{
			"doctype": "AU Tax Determination",
			"type": "Purchase",
			"bp_tax_template": "Import & GST-Free Purchase",
			"item_tax_template": "GST Exempt Purchase",
			"tax_code": "AUPNCAFR",
		},
		{
			"doctype": "AU Tax Determination",
			"type": "Purchase",
			"bp_tax_template": "AU Capital Purchase - GST",
			"item_tax_template": "GST Exempt Purchase",
			"tax_code": "AUPCAFREX",
		},
		{
			"doctype": "AU Tax Determination",
			"type": "Sales",
			"bp_tax_template": "AU Sales - GST",
			"item_tax_template": "",
			"tax_code": "AUSGST",
		},
		{
			"doctype": "AU Tax Determination",
			"type": "Sales",
			"bp_tax_template": "Export Sales - GST Free",
			"item_tax_template": "",
			"tax_code": "AUSEXP",
		},
		{
			"doctype": "AU Tax Determination",
			"type": "Sales",
			"bp_tax_template": "AU Sales - GST Free",
			"item_tax_template": "",
			"tax_code": "AUSFREX",
		},
		{
			"doctype": "AU Tax Determination",
			"type": "Sales",
			"bp_tax_template": "AU Sales - GST",
			"item_tax_template": "GST Exempt Sales",
			"tax_code": "AUSFREX",
		},
		{
			"doctype": "AU Tax Determination",
			"type": "Sales",
			"bp_tax_template": "Export Sales - GST Free",
			"item_tax_template": "GST Exempt Sales",
			"tax_code": "AUSEXP",
		},
		{
			"doctype": "AU Tax Determination",
			"type": "Sales",
			"bp_tax_template": "AU Sales - GST Free",
			"item_tax_template": "GST Exempt Sales",
			"tax_code": "AUSFREX",
		},
	]

	return records


def get_au_bas_labels():
	records = [
		{
			"doctype": "AU BAS Label",
			"bas_label": "1A",
			"bas_label_description": "GST On Sales",
		},
		{
			"doctype": "AU BAS Label",
			"bas_label": "1B",
			"bas_label_description": "GST On Purchases",
		},
		{
			"doctype": "AU BAS Label",
			"bas_label": "G1",
			"bas_label_description": "Total Sales (Including GST)",
		},
		{
			"doctype": "AU BAS Label",
			"bas_label": "G2",
			"bas_label_description": "Export Sales",
		},
		{
			"doctype": "AU BAS Label",
			"bas_label": "G3",
			"bas_label_description": "Other GST-Free Sales",
		},
		{
			"doctype": "AU BAS Label",
			"bas_label": "G4",
			"bas_label_description": "Input Taxed Sales",
		},
		{
			"doctype": "AU BAS Label",
			"bas_label": "G10",
			"bas_label_description": "Capital Purchases (Including GST)",
		},
		{
			"doctype": "AU BAS Label",
			"bas_label": "G11",
			"bas_label_description": "Non Capital Purchases (Including GST)",
		},
		{
			"doctype": "AU BAS Label",
			"bas_label": "G13",
			"bas_label_description": "Purchase for Input Taxed Sales",
		},
		{
			"doctype": "AU BAS Label",
			"bas_label": "G14",
			"bas_label_description": "Purchase without GST in the price",
		},
		{
			"doctype": "AU BAS Label",
			"bas_label": "G15",
			"bas_label_description": "Purchase for private use / not income tax deductible",
		},
	]
	return records


def get_au_bas_label_setup():
	records = [
		{
			"doctype": "AU BAS Label Setup",
			"bas_label": "1A",
			"tax_management": "Tax Account",
			"tax_allocation": "Collected Sales",
			"tax_code": "AUSGST",
		},
		{
			"doctype": "AU BAS Label Setup",
			"bas_label": "1B",
			"tax_management": "Tax Account",
			"tax_allocation": "Deductible Purchase",
			"tax_code": "AUPNCASGT",
		},
		{
			"doctype": "AU BAS Label Setup",
			"bas_label": "1B",
			"tax_management": "Tax Account",
			"tax_allocation": "Deductible Purchase",
			"tax_code": "AUPCAGST",
		},
		{
			"doctype": "AU BAS Label Setup",
			"bas_label": "G1",
			"tax_management": "Subjected",
			"tax_allocation": "Collected Sales",
			"tax_code": "AUSGST",
		},
		{
			"doctype": "AU BAS Label Setup",
			"bas_label": "G1",
			"tax_management": "Subjected",
			"tax_allocation": "Collected Sales",
			"tax_code": "AUSEXP",
		},
		{
			"doctype": "AU BAS Label Setup",
			"bas_label": "G1",
			"tax_management": "Subjected",
			"tax_allocation": "Collected Sales",
			"tax_code": "AUSFREX",
		},
		{
			"doctype": "AU BAS Label Setup",
			"bas_label": "G1",
			"tax_management": "Subjected",
			"tax_allocation": "Collected Sales",
			"tax_code": "AUSINPTAX",
		},
		{
			"doctype": "AU BAS Label Setup",
			"bas_label": "G1",
			"tax_management": "Tax Account",
			"tax_allocation": "Collected Sales",
			"tax_code": "AUSGST",
		},
		{
			"doctype": "AU BAS Label Setup",
			"bas_label": "G2",
			"tax_management": "Subjected",
			"tax_allocation": "Collected Sales",
			"tax_code": "AUSEXP",
		},
		{
			"doctype": "AU BAS Label Setup",
			"bas_label": "G3",
			"tax_management": "Subjected",
			"tax_allocation": "Collected Sales",
			"tax_code": "AUSFREX",
		},
		{
			"doctype": "AU BAS Label Setup",
			"bas_label": "G4",
			"tax_management": "Subjected",
			"tax_allocation": "Collected Sales",
			"tax_code": "AUSINPTAX",
		},
		{
			"doctype": "AU BAS Label Setup",
			"bas_label": "G10",
			"tax_management": "Subjected",
			"tax_allocation": "Deductible Purchase",
			"tax_code": "AUPCAGST",
		},
		{
			"doctype": "AU BAS Label Setup",
			"bas_label": "G10",
			"tax_management": "Subjected",
			"tax_allocation": "Deductible Purchase",
			"tax_code": "AUPCAFREX",
		},
		{
			"doctype": "AU BAS Label Setup",
			"bas_label": "G10",
			"tax_management": "Tax Account",
			"tax_allocation": "Deductible Purchase",
			"tax_code": "AUPCAGST",
		},
		{
			"doctype": "AU BAS Label Setup",
			"bas_label": "G11",
			"tax_management": "Subjected",
			"tax_allocation": "Deductible Purchase",
			"tax_code": "AUPNCASGT",
		},
		{
			"doctype": "AU BAS Label Setup",
			"bas_label": "G11",
			"tax_management": "Subjected",
			"tax_allocation": "Deductible Purchase",
			"tax_code": "AUPNCAFR",
		},
		{
			"doctype": "AU BAS Label Setup",
			"bas_label": "G11",
			"tax_management": "Subjected",
			"tax_allocation": "Deductible Purchase",
			"tax_code": "AUPINPTAX",
		},
		{
			"doctype": "AU BAS Label Setup",
			"bas_label": "G11",
			"tax_management": "Subjected",
			"tax_allocation": "Deductible Purchase",
			"tax_code": "AUPPVTUSE",
		},
		{
			"doctype": "AU BAS Label Setup",
			"bas_label": "G11",
			"tax_management": "Tax Account",
			"tax_allocation": "Deductible Purchase",
			"tax_code": "AUPNCASGT",
		},
		{
			"doctype": "AU BAS Label Setup",
			"bas_label": "G13",
			"tax_management": "Subjected",
			"tax_allocation": "Deductible Purchase",
			"tax_code": "AUPINPTAX",
		},
		{
			"doctype": "AU BAS Label Setup",
			"bas_label": "G14",
			"tax_management": "Subjected",
			"tax_allocation": "Deductible Purchase",
			"tax_code": "AUPCAFREX",
		},
		{
			"doctype": "AU BAS Label Setup",
			"bas_label": "G14",
			"tax_management": "Subjected",
			"tax_allocation": "Deductible Purchase",
			"tax_code": "AUPNCAFR",
		},
		{
			"doctype": "AU BAS Label Setup",
			"bas_label": "G15",
			"tax_management": "Subjected",
			"tax_allocation": "Deductible Purchase",
			"tax_code": "AUPPVTUSE",
		},
	]
	return records


def get_au_bank_statement_format():
	records = [
		{
			"doctype": "AU Bank Statement Format",
			"name": "NAB CSV Format",
			"credit_debit_mapping": "Combined credit&debit",
			"date_format": "DD MMM YYYY",
			"acc_no_col": "Account Number",
			"mapping_fields": [
				{
					"erpnext_column": "Date",
					"bank_statement_column": "Date",
				},
				{
					"erpnext_column": "Deposit",
					"bank_statement_column": "Amount",
				},
				{
					"erpnext_column": "Withdrawal",
					"bank_statement_column": "Amount",
				},
				{
					"erpnext_column": "Description",
					"bank_statement_column": "Transaction Details",
				},
			],
			"sample_data": (
				"Date,Amount,Account Number,,Transaction Type,Transaction Details,Balance,Category,Merchant Name\n"
				"30-Dec-25,-2000,234567819,,DEBIT,Salary payment,1356.5,Income,ABC Pty Ltd\n"
				"29-Dec-25,-1200,234567819,,DEBIT,Monthly house rent,3356.5,Housing,Property Manager\n"
				"29-Dec-25,-250,234567819,,DEBIT,Online shopping,4556.5,Shopping,Amazon AU\n"
				"26-Dec-25,-65,234567819,,DEBIT,Fuel purchase,4806.5,Transport,BP Australia\n"
				"23-Dec-25,-120,234567819,,DEBIT,Grocery shopping,4871.5,Groceries,Woolworths\n"
				"22-Dec-25,-400,234567819,,DEBIT,Coffee purchase,4991.5,Food&Drink,Starbucks"
			),
		},
		{
			"doctype": "AU Bank Statement Format",
			"name": "Westpac CSV Format",
			"credit_debit_mapping": "Combined credit&debit",
			"date_format": "YYYYMMDD",
			"acc_no_col": "ACCOUNT_NO",
			"mapping_fields": [
				{
					"erpnext_column": "Date",
					"bank_statement_column": "TRAN_DATE",
				},
				{
					"erpnext_column": "Deposit",
					"bank_statement_column": "AMOUNT",
				},
				{
					"erpnext_column": "Withdrawal",
					"bank_statement_column": "AMOUNT",
				},
				{
					"erpnext_column": "Description",
					"bank_statement_column": "NARRATIVE",
				},
				{
					"erpnext_column": "Reference Number",
					"bank_statement_column": "SERIAL",
				},
			],
			"sample_data": (
				"TRAN_DATE,ACCOUNT_NO,ACCOUNT_NAME,CCY,CLOSING_BAL,AMOUNT,TRAN_CODE,NARRATIVE,SERIAL\n"
				"20250101,32000123456,Business Account,AUD,5000,-5000,50,Salary Payment,1234567\n"
				"20250102,32000123456,Business Account,AUD,4849.5,-150.5,9,Transfer Out,1234568\n"
				"20250103,32000123456,Business Account,AUD,4804.5,-45,13,BPAY Payment,1234569\n"
				"20250104,32000123456,Business Account,AUD,4904.5,100,14,Shopping,1234570\n"
				"20250105,32000123456,Business Account,AUD,4854.5,-50,17,BPAY Payment,1234571"
			),
		},
		{
			"doctype": "AU Bank Statement Format",
			"name": "ANZ CSV Format",
			"credit_debit_mapping": "Single credit&debit",
			"date_format": "DD-MMM-YY",
			"acc_no_col": "Account Number",
			"mapping_fields": [
				{
					"erpnext_column": "Date",
					"bank_statement_column": "Post Date",
				},
				{
					"erpnext_column": "Deposit",
					"bank_statement_column": "Credits",
				},
				{
					"erpnext_column": "Withdrawal",
					"bank_statement_column": "Debits",
				},
				{
					"erpnext_column": "Description",
					"bank_statement_column": "Narrative",
				},
				{
					"erpnext_column": "Reference Number",
					"bank_statement_column": "Bank Reference",
				},
			],
			"sample_data": (
				"Statement Number,Account Number,Account Name,Account Currency,Opening Available Balance,Opening Ledger Balance,Closing Available Balance,Closing Ledger Balance,Value Date,Post Date,Tran Type,Bank Reference,Narrative,Debits,Credits\n"
				"1,013-999-123456,Business Account,AUD,10000,10000,5000,5000,01-Jan-25,01-Jan-25,PAYMENT,REF001,Salary Payment,5000,0\n"
				"1,013-999-123456,Business Account,AUD,5000,5000,4849.5,4849.5,02-Jan-25,02-Jan-25,PAYMENT,REF002,Transfer Out,150.5,0\n"
				"1,013-999-123456,Business Account,AUD,4849.5,4849.5,4804.5,4804.5,03-Jan-25,03-Jan-25,BPAY,REF003,BPAY Payment,45,0\n"
				"1,013-999-123456,Business Account,AUD,4804.5,4804.5,5204.5,5204.5,04-Jan-25,04-Jan-25,SHOPPING,REF004,Refund,0,400\n"
				"1,013-999-123456,Business Account,AUD,5204.5,5204.5,5159.5,5159.5,05-Jan-25,05-Jan-25,BPAY,REF005,BPAY Payment,45,0"
			),
		},
		{
			"doctype": "AU Bank Statement Format",
			"name": "Commonwealth Bank CSV Format",
			"credit_debit_mapping": "Combined credit&debit",
			"date_format": "DD/MM/YYYY",
			"mapping_fields": [
				{
					"erpnext_column": "Date",
					"bank_statement_column": "Date",
				},
				{
					"erpnext_column": "Deposit",
					"bank_statement_column": "Amount",
				},
				{
					"erpnext_column": "Withdrawal",
					"bank_statement_column": "Amount",
				},
				{
					"erpnext_column": "Description",
					"bank_statement_column": "Description",
				},
			],
			"sample_data": (
				"Date,Amount,Description,Balance\n"
				"01/01/2025,5000,Salary Payment,15000\n"
				"02/01/2025,-150.5,Transfer Out,14849.5\n"
				"03/01/2025,-45.00,BPAY Payment,14804.5\n"
				"04/01/2025,+200,Refund,15004.5\n"
				"05/01/2025,-200,Grocery shopping,14804.5\n"
			),
		},
	]
	return records


ROLES = [
	{"doctype": "Role", "role_name": "AU Localisation Admin", "name": "AU Localisation Admin"},
]


def create_roles():
	make_records(ROLES)


# def remove_roles():
# 	for role in ROLES :
# 		if frappe.db.exists("Role", role['name']):
# 			has_role_list = frappe.get_list("Has Role", filters={"role": role['name']})
# 			for has_role in has_role_list:
# 				frappe.delete_doc("Has Role", has_role.name)
# 			frappe.delete_doc("Role", role['name'])
# 	frappe.db.commit()
