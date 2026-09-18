from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

GST_STATUS_FIELD = {
	("Supplier", "Customer"): [
		{
			"fieldname": "gst_status",
			"label": "GST Status",
			"fieldtype": "Data",
			"insert_after": "business_name",
			"read_only": 1,
			"module": "ERPNext Australian Localisation",
		},
	],
}


def execute():
	create_custom_fields(GST_STATUS_FIELD, update=1)
