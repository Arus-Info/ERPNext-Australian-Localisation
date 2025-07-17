from erpnext_australian_localisation.setup.create_property_setters import remove_setup


def before_uninstall():
	remove_setup()