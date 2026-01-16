import frappe
from frappe.desk.page.setup_wizard.setup_wizard import make_records


def create_default_records():
	records = []
	records.extend(get_au_tax_codes())
	records.extend(get_au_tax_determination())
	records.extend(get_au_bas_labels())
	records.extend(get_au_bas_label_setup())
	# records.extend(get_au_bank_statement_format())

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
		},
		{
			"doctype": "AU Bank Statement Format",
			"name": "Westpac CSV Format",
			"credit_debit_mapping": "Combined credit&debit",
			"date_format": "YYYYMMDD",
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
		},
		{
			"doctype": "AU Bank Statement Format",
			"name": "ANZ CSV Format",
			"credit_debit_mapping": "Single credit&debit",
			"date_format": "DD-MMM-YY",
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
