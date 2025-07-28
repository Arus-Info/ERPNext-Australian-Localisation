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
		}
	],
	"Sales Invoice Item" : [
		{
			"fieldname": "input_taxed",
			"label": "Input-taxed Sales",
			"fieldtype": "Check",
			"insert_after": "au_tax_description",
			"module": "ERPNext Australian Localisation",
		}
	],
	"Purchase Invoice Item" : [
		{
			"fieldname": "input_taxed",
			"label": "Purchase for Input-taxed Sales",
			"fieldtype": "Check",
			"insert_after": "au_tax_description",
			"module": "ERPNext Australian Localisation",
		},
		{
			"fieldname": "private_use",
			"label": " Purchases for private use / not income tax deductible",
			"fieldtype": "Check",
			"insert_after": "input_taxed",
			"module": "ERPNext Australian Localisation",
		}
	],
	"Sales Taxes and Charges": [
		{
			"fieldname": "au_tax_code",
			"label": "AU Tax Code",
			"fieldtype": "Link",
			"options": "AU Tax Code",
			"insert_after": "account_head",
			"read_only" : 1,
			"module": "ERPNext Australian Localisation",
		}
	],
	"Purchase Taxes and Charges" : [
		{
			"fieldname": "au_tax_code",
			"label": "AU Tax Code",
			"fieldtype": "Link",
			"options": "AU Tax Code",
			"insert_after": "is_tax_withholding_account",
			"read_only" : 1,
			"module": "ERPNext Australian Localisation",
		}
	],
	"Sales Order Item" : [
		{
			"fieldname": "input_taxed",
			"label": "Input-taxed Sales",
			"fieldtype": "Check",
			"insert_after": "item_tax_template",
			"module": "ERPNext Australian Localisation",
		},
	]
}

HRMS_CUSTOM_FIELDS = {
	"Expense Claim Detail" : [
		{
			"fieldname": "au_tax_code",
			"label": "AU Tax Code",
			"fieldtype": "Link",
			"options": "AU Tax Code",
			"insert_after": "expense_date",
			"module": "ERPNext Australian Localisation",
		}
	],
	"Expense Taxes and Charges" : [
		{
			"fieldname": "au_tax_code",
			"label": "AU Tax Code",
			"fieldtype": "Link",
			"options": "AU Tax Code",
			"insert_after": "total",
			"read_only" : 1,
			"module": "ERPNext Australian Localisation",
		}
	],
}