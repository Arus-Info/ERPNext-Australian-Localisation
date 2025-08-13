from erpnext_australian_localisation.setup.delete_properties import remove_setup, delete_hrms_custom_fields
# from erpnext_australian_localisation.setup.install_fixtures import remove_roles


def before_uninstall():
	remove_setup()

# def after_uninstall():
# 	remove_roles()

def before_app_uninstall(app_name):
    if app_name == "hrms":
        delete_hrms_custom_fields()