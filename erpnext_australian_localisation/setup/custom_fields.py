CUSTOM_FIELDS = {
	("Sales Invoice Item", "Purchase Invoice Item"): [
		{
			"fieldname": "au_tax_code",
			"label": "AU Tax Code",
			"fieldtype": "Link",
			"options": "AU Tax Code",
			"read_only": 1,
			"insert_after": "item_tax_template",
			"module": "ERPNext Australian Localisation",
		},
		{
			"fieldname": "au_tax_description",
			"label": "AU Tax Description",
			"fieldtype": "Data",
			"fetch_from": "au_tax_code.tax_description",
			"read_only": 1,
			"insert_after": "au_tax_code",
			"module": "ERPNext Australian Localisation",
		},
	],
	"Sales Invoice Item": [
		{
			"fieldname": "input_taxed",
			"label": "Input-taxed Sales",
			"fieldtype": "Check",
			"insert_after": "au_tax_description",
			"module": "ERPNext Australian Localisation",
		}
	],
	"Purchase Invoice Item": [
		{
			"fieldname": "input_taxed",
			"label": "Purchase for Input-taxed Sales",
			"fieldtype": "Check",
			"insert_after": "au_tax_description",
			"module": "ERPNext Australian Localisation",
		},
		{
			"fieldname": "private_use",
			"label": " Purchase for private use / not income tax deductible",
			"fieldtype": "Check",
			"insert_after": "input_taxed",
			"module": "ERPNext Australian Localisation",
		},
	],
	"Sales Taxes and Charges": [
		{
			"fieldname": "au_tax_code",
			"label": "AU Tax Code",
			"fieldtype": "Link",
			"options": "AU Tax Code",
			"insert_after": "account_head",
			"read_only": 1,
			"module": "ERPNext Australian Localisation",
		}
	],
	"Purchase Taxes and Charges": [
		{
			"fieldname": "au_tax_code",
			"label": "AU Tax Code",
			"fieldtype": "Link",
			"options": "AU Tax Code",
			"insert_after": "is_tax_withholding_account",
			"read_only": 1,
			"module": "ERPNext Australian Localisation",
		}
	],
	("Sales Order Item", "Delivery Note Item"): [
		{
			"fieldname": "input_taxed",
			"label": "Input-taxed Sales",
			"fieldtype": "Check",
			"insert_after": "item_tax_template",
			"module": "ERPNext Australian Localisation",
		},
	],
	("Purchase Receipt Item", "Purchase Order Item"): [
		{
			"fieldname": "input_taxed",
			"label": "Purchase for Input-taxed Sales",
			"fieldtype": "Check",
			"insert_after": "item_tax_template",
			"module": "ERPNext Australian Localisation",
		},
		{
			"fieldname": "private_use",
			"label": " Purchase for private use / not income tax deductible",
			"fieldtype": "Check",
			"insert_after": "input_taxed",
			"module": "ERPNext Australian Localisation",
		},
	],
}

HRMS_CUSTOM_FIELDS = {
	"Expense Claim Detail": [
		{
			"fieldname": "au_tax_code",
			"label": "AU Tax Code",
			"fieldtype": "Link",
			"options": "AU Tax Code",
			"insert_after": "expense_date",
			"module": "ERPNext Australian Localisation",
		}
	],
	"Expense Taxes and Charges": [
		{
			"fieldname": "au_tax_code",
			"label": "AU Tax Code",
			"fieldtype": "Link",
			"options": "AU Tax Code",
			"insert_after": "total",
			"read_only": 1,
			"module": "ERPNext Australian Localisation",
		}
	],
}

CUSTOM_FIELDS_FOR_BANK_FILE = {
	"Supplier": [
		{
			"fieldname": "section_break_au_localisation",
			"label": "AU Localisation",
			"fieldtype": "Section Break",
			"insert_after": "default_price_list",
			"depends_on": "eval: doc.country === 'Australia'",
			"module": "ERPNext Australian Localisation",
		},
		{
			"fieldname": "is_allowed_in_pp",
			"label": "Is Allowed in Payment Proposal",
			"fieldtype": "Check",
			"default": 1,
			"insert_after": "section_break_au_localisation",
			"module": "ERPNext Australian Localisation",
		},
		{
			"fieldname": "lodgement_reference",
			"label": "Lodgement Reference",
			"fieldtype": "Data",
			"length": 18,
			"insert_after": "is_allowed_in_pp",
			"module": "ERPNext Australian Localisation",
		},
		{
			"fieldname": "column_break_s_au",
			"fieldtype": "Column Break",
			"insert_after": "lodgement_reference",
			"module": "ERPNext Australian Localisation",
		},
		{
			"fieldname": "branch_code",
			"label": "BSB",
			"fieldtype": "Data",
			"length": 7,
			"insert_after": "column_break_s_au",
			"module": "ERPNext Australian Localisation",
		},
		{
			"fieldname": "bank_account_no",
			"label": "Bank Account Number",
			"fieldtype": "Data",
			"length": 9,
			"insert_after": "branch_code",
			"module": "ERPNext Australian Localisation",
		},
	],
	"Bank Account": [
		{
			"fieldname": "section_break_payment_batch",
			"label": "Payment Batch Info",
			"fieldtype": "Section Break",
			"insert_after": "mask",
			"module": "ERPNext Australian Localisation",
		},
		{
			"fieldname": "fi_abbr",
			"label": "Financial Institution Abbreviation",
			"fieldtype": "Data",
			"length": 3,
			"insert_after": "section_break_payment_batch",
			"module": "ERPNext Australian Localisation",
		},
		{
			"fieldname": "apca_number",
			"label": "APCA Number",
			"fieldtype": "Data",
			"length": 6,
			"insert_after": "fi_abbr",
			"module": "ERPNext Australian Localisation",
		},
		{
			"fieldname": "currency",
			"label": "Currency",
			"fieldtype": "Link",
			"options": "Currency",
			"fetch_from": "account.account_currency",
			"insert_after": "apca_number",
			"module": "ERPNext Australian Localisation",
		},
		{
			"fieldname": "file_format",
			"label": "File Format",
			"fieldtype": "Select",
			"options": "ABA",
			"default": "ABA",
			"insert_after": "currency",
			"module": "ERPNext Australian Localisation",
		},
	],
}

EMPLOYEE_BANK_DETAILS = {
	"Employee": [
		{
			"fieldname": "section_break_bank_details",
			"fieldtype": "Section Break",
			"insert_after": "grade",
			"module": "ERPNext Australian Localisation",
		},
		{
			"fieldname": "lodgement_reference",
			"label": "Lodgement Reference",
			"fieldtype": "Data",
			"length": 18,
			"insert_after": "section_break_bank_details",
			"module": "ERPNext Australian Localisation",
		},
		{
			"fieldname": "branch_code",
			"label": "BSB",
			"fieldtype": "Data",
			"length": 7,
			"insert_after": "lodgement_reference",
			"module": "ERPNext Australian Localisation",
		},
		{
			"fieldname": "bank_account_no",
			"label": "Bank Account Number",
			"fieldtype": "Data",
			"length": 9,
			"insert_after": "branch_code",
			"module": "ERPNext Australian Localisation",
		},
	]
}

POS_INVOICE_CUSTOM_FIELDS = {
	"POS Invoice Item": [
		{
			"fieldname": "au_tax_code",
			"label": "AU Tax Code",
			"fieldtype": "Link",
			"options": "AU Tax Code",
			"read_only": 1,
			"insert_after": "item_tax_template",
			"module": "ERPNext Australian Localisation",
		},
		{
			"fieldname": "au_tax_description",
			"label": "AU Tax Description",
			"fieldtype": "Data",
			"fetch_from": "au_tax_code.tax_description",
			"read_only": 1,
			"insert_after": "au_tax_code",
			"module": "ERPNext Australian Localisation",
		},
	],
}
