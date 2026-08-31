# Copyright (c) 2026, frappe.dev@arus.co.in and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from erpnext_australian_localisation.integration.basiq import basiq_connector


class ConnectedAccounts(Document):
	pass


@frappe.whitelist()
def sync_bank_connection(connection_id):
	return basiq_connector.refresh_connection(connection_id)


@frappe.whitelist()
def submit_mfa_response(response_url, inputs):
	inputs = frappe.parse_json(inputs) if isinstance(inputs, str) else inputs
	return basiq_connector.submit_mfa_response(response_url, inputs)
