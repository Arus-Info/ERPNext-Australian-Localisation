def get_property_setters():
	properties = [
		{
			"doctype": "Supplier",
			"fieldname": "tax_category",
			"property": "mandatory_depends_on",
			"value": "eval: australian_localisation_settings.make_tax_category_mandatory",
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
			"value": "eval: australian_localisation_settings.make_tax_category_mandatory",
		},
		{
			"doctype": "Customer",
			"fieldname": "tax_category",
			"property": "allow_in_quick_entry",
			"value": "1",
		},
	]

	return properties
