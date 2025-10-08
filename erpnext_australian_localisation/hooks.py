app_name = "erpnext_australian_localisation"
app_title = "ERPNext Australian Localisation"
app_publisher = "frappe.dev@arus.co.in"
app_description = "Australian Localisation for ERPNext"
app_email = "frappe.dev@arus.co.in"
app_license = "gpl-3.0"
required_apps = ["erpnext"]

# Apps
# ------------------
app_include_js = "australian_localisation.bundle.js"

fixtures = [{"dt": "Custom HTML Block", "filters": {"name": "Australian Localisation"}}]

company_data_to_be_ignored = ["Tax Rule"]

after_app_install = "erpnext_australian_localisation.install.after_app_install"
before_app_uninstall = "erpnext_australian_localisation.uninstall.before_app_uninstall"

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "erpnext_australian_localisation",
# 		"logo": "/assets/erpnext_australian_localisation/logo.png",
# 		"title": "ERPNext Australian Localisation",
# 		"route": "/erpnext_australian_localisation",
# 		"has_permission": "erpnext_australian_localisation.api.permission.has_app_permission"
# 	}
# ]


# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/erpnext_australian_localisation/css/erpnext_australian_localisation.css"
# app_include_js = "/assets/erpnext_australian_localisation/js/erpnext_australian_localisation.js"

# include js, css files in header of web template
# web_include_css = "/assets/erpnext_australian_localisation/css/erpnext_australian_localisation.css"
# web_include_js = "/assets/erpnext_australian_localisation/js/erpnext_australian_localisation.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "erpnext_australian_localisation/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

doctype_js = {
	"Item": "public/js/item.js",
	"Sales Invoice": "public/js/setup_input_taxed_sales.js",
	"Sales Order": "public/js/setup_input_taxed_sales.js",
	"Delivery Note": "public/js/setup_input_taxed_sales.js",
	"Purchase Invoice": "public/js/setup_input_taxed_sales.js",
	"Purchase Order": "public/js/setup_input_taxed_sales.js",
	"Purchase Receipt": "public/js/setup_input_taxed_sales.js",
	"Supplier": ["public/js/validate_bank_details.js", "public/js/supplier.js"],
	"Employee": ["public/js/validate_bank_details.js", "public/js/employee.js"],
	"Bank Account": ["public/js/validate_bank_details.js", "public/js/bank_account.js"],
}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "erpnext_australian_localisation/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "erpnext_australian_localisation.utils.jinja_methods",
# 	"filters": "erpnext_australian_localisation.utils.jinja_filters"
# }

# Installation
# ------------

boot_session = "erpnext_australian_localisation.boot.set_bootinfo"
before_install = "erpnext_australian_localisation.install.before_install"
after_install = "erpnext_australian_localisation.install.after_install"

# Uninstallation
# ------------

before_uninstall = "erpnext_australian_localisation.uninstall.before_uninstall"
# after_uninstall = "erpnext_australian_localisation.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "erpnext_australian_localisation.utils.before_app_install"
# after_app_install = "erpnext_australian_localisation.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "erpnext_australian_localisation.utils.before_app_uninstall"
# after_app_uninstall = "erpnext_australian_localisation.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "erpnext_australian_localisation.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

doc_events = {
	"Sales Invoice": {
		"before_submit": "erpnext_australian_localisation.overrides.invoices.before_submit",
		"on_cancel": "erpnext_australian_localisation.overrides.invoices.on_cancel",
	},
	"Purchase Invoice": {
		"before_submit": "erpnext_australian_localisation.overrides.invoices.before_submit",
		"on_cancel": [
			"erpnext_australian_localisation.overrides.invoices.on_cancel",
			"erpnext_australian_localisation.overrides.purchase_invoice.on_cancel",
		],
	},
	"POS Invoice": {
		"before_submit": "erpnext_australian_localisation.overrides.invoices.before_submit",
		"on_cancel": "erpnext_australian_localisation.overrides.invoices.on_cancel",
	},
	"Company": {
		"after_insert": "erpnext_australian_localisation.overrides.company.after_insert",
		"on_update": "erpnext_australian_localisation.overrides.company.on_update",
	},
	"Expense Claim": {
		"before_submit": "erpnext_australian_localisation.overrides.expense_claim.before_submit",
		"on_update": "erpnext_australian_localisation.overrides.expense_claim.on_update",
		"on_cancel": "erpnext_australian_localisation.overrides.invoices.on_cancel",
	},
	"Payment Entry": {
		"on_submit": "erpnext_australian_localisation.overrides.payment_entry.on_submit",
		"on_update": "erpnext_australian_localisation.overrides.payment_entry.on_update",
	},
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"erpnext_australian_localisation.tasks.all"
# 	],
# 	"daily": [
# 		"erpnext_australian_localisation.tasks.daily"
# 	],
# 	"hourly": [
# 		"erpnext_australian_localisation.tasks.hourly"
# 	],
# 	"weekly": [
# 		"erpnext_australian_localisation.tasks.weekly"
# 	],
# 	"monthly": [
# 		"erpnext_australian_localisation.tasks.monthly"
# 	],
# }

scheduler_events = {"monthly": ["erpnext_australian_localisation.tasks.bas_report.create_bas_report"]}

# Testing
# -------

# before_tests = "erpnext_australian_localisation.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "erpnext_australian_localisation.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "erpnext_australian_localisation.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["erpnext_australian_localisation.utils.before_request"]
# after_request = ["erpnext_australian_localisation.utils.after_request"]

# Job Events
# ----------
# before_job = ["erpnext_australian_localisation.utils.before_job"]
# after_job = ["erpnext_australian_localisation.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"erpnext_australian_localisation.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }
