from erpnext_australian_localisation.setup.create_property_setters import remove_setup
from erpnext_australian_localisation.setup.install_fixtures import remove_roles


def before_uninstall():
	remove_setup()

def after_uninstall():
	remove_roles()