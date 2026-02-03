import frappe

from erpnext_australian_localisation.setup.create_properties import create_properties_for_abn_guid


def execute():
	create_properties_for_abn_guid()
