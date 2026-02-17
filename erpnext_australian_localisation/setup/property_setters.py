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
	{
		"doctype": "Payment Entry",
		"fieldname": "bank_account",
		"property": "reqd",
		"value": "1",
	},
	{
		"doctype": "Payment Entry",
		"fieldname": "paid_from",
		"property": "read_only",
		"value": "1",
	},
]

ABN_PROPERTIES = [
	{
		"doctype": "Supplier",
		"doctype_or_field": "DocType",
		"property": "field_order",
		"property_type": "Data",
		"value": (
			'["naming_series", "supplier_name", "country", "column_break0", '
			'"supplier_group", "supplier_type", "is_transporter", "image", '
			'"defaults_section", "default_currency", "default_bank_account", '
			'"column_break_10", "default_price_list", "section_break_au_localisation", '
			'"is_allowed_in_pp", "lodgement_reference", "column_break_s_au", '
			'"branch_code", "bank_account_no", "internal_supplier_section", '
			'"is_internal_supplier", "represents_company", "column_break_16", '
			'"companies", "column_break2", "supplier_details", "column_break_30", '
			'"website", "language", "customer_numbers", "dashboard_tab", "tax_tab", '
			'"tax_id", "tax_category", "column_break_27", "tax_withholding_category", '
			'"tax_withholding_group", "section_break_abn", "entity_name", "abn_status", '
			'"abn_effective_from", "column_break_abn", "address_postcode", '
			'"address_state", "business_name", "contact_and_address_tab", '
			'"address_contacts", "address_html", "column_break1", "contact_html", '
			'"primary_address_and_contact_detail_section", "column_break_44", '
			'"supplier_primary_address", "primary_address", "column_break_mglr", '
			'"supplier_primary_contact", "mobile_no", "email_id", "accounting_tab", '
			'"payment_terms", "default_accounts_section", "accounts", "settings_tab", '
			'"allow_purchase_invoice_creation_without_purchase_order", '
			'"allow_purchase_invoice_creation_without_purchase_receipt", '
			'"column_break_54", "is_frozen", "disabled", "warn_rfqs", "warn_pos", '
			'"prevent_rfqs", "prevent_pos", "block_supplier_section", "on_hold", '
			'"hold_type", "column_break_59", "release_date", "portal_users_tab", '
			'"portal_users", "column_break_1mqv"]'
		),
	},
	{
		"doctype": "Customer",
		"doctype_or_field": "DocType",
		"property": "field_order",
		"property_type": "Data",
		"value": (
			'["basic_info", "naming_series", "salutation", "customer_name", '
			'"customer_type", "customer_group", "column_break0", '
			'"territory", "gender", "lead_name", "opportunity_name", '
			'"prospect_name", "account_manager", "image", '
			'"defaults_tab", "default_currency", "default_bank_account", '
			'"column_break_14", "default_price_list", '
			'"internal_customer_section", "is_internal_customer", '
			'"represents_company", "column_break_70", "companies", '
			'"more_info", "market_segment", "industry", "customer_pos_id", '
			'"website", "language", "column_break_45", "customer_details", '
			'"supplier_numbers", '
			'"dashboard_tab", '
			'"contact_and_address_tab", "address_contacts", '
			'"address_html", "column_break1", "contact_html", '
			'"primary_address_and_contact_detail", "column_break_26", '
			'"customer_primary_address", "primary_address", '
			'"column_break_nwor", "customer_primary_contact", '
			'"mobile_no", "email_id", "first_name", "last_name", '
			'"tax_tab", "taxation_section", "tax_id", "tax_category", '
			'"column_break_21", "tax_withholding_category", '
			'"tax_withholding_group", '
			'"section_break_abn", '
			'"entity_name", "abn_status", "abn_effective_from", '
			'"column_break_abn", "address_postcode", '
			'"address_state", "business_name", '
			'"accounting_tab", "credit_limit_section", '
			'"payment_terms", "credit_limits", '
			'"default_receivable_accounts", "accounts", '
			'"loyalty_points_tab", "loyalty_program", '
			'"column_break_54", "loyalty_program_tier", '
			'"sales_team_tab", "sales_team", "sales_team_section", '
			'"default_sales_partner", "column_break_66", '
			'"default_commission_rate", '
			'"settings_tab", "so_required", "dn_required", '
			'"column_break_53", "is_frozen", "disabled", '
			'"portal_users_tab", "portal_users"]'
		),
	},
]
