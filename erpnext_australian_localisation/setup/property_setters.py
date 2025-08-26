PROPERTIES = [
	{
		"doctype": "Supplier",
		"fieldname": "tax_category",
		"property": "mandatory_depends_on",
		"value": "eval: au_localisation_settings.make_tax_category_mandatory",
	},
	{
		"doctype": "Supplier",
		"fieldname": "tax_category",
		"property": "allow_in_quick_entry",
		"value": "1",
	},
	{
		"doctype": "Customer",
		"fieldname": "tax_category",
		"property": "mandatory_depends_on",
		"value": "eval: au_localisation_settings.make_tax_category_mandatory",
	},
	{
		"doctype": "Customer",
		"fieldname": "tax_category",
		"property": "allow_in_quick_entry",
		"value": "1",
	},
	{
		"doctype": "AU BAS Report",
		"property": "default_print_format",
		"property_type": "Data",
		"value": "AU BAS Report Format",
	},
]
