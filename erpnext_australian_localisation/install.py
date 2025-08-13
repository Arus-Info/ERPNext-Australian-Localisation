from erpnext_australian_localisation.setup.create_properties import initial_setup, create_hrms_custom_fields
from erpnext_australian_localisation.setup.install_fixtures import create_default_records, create_roles
from erpnext_australian_localisation.overrides.company import initial_company_setup


def after_install():
	initial_setup()
	create_default_records()
	initial_company_setup()

def before_install():
	create_roles()

def after_app_install(app_name):
	if app_name == "hrms":
		create_hrms_custom_fields()