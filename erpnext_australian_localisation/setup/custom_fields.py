CUSTOM_FIELDS = {
	("Sales Invoice Item", "Purchase Invoice Item"): [
		{
			"fieldname": "au_tax_code",
			"label": "AU Tax Code",
			"fieldtype": "Link",
			"options": "AU Tax Code",
			"insert_after": "item_tax_template",
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