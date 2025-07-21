from erpnext_australian_localisation.setup.create_custom_fields import initial_setup
from erpnext_australian_localisation.setup.install_fixtures import create_default_records, create_roles
from erpnext_australian_localisation.overrides.company import update_au_localisation_settings


def after_install():
	initial_setup()
	create_default_records()
	update_au_localisation_settings()

def before_install():
	create_roles()