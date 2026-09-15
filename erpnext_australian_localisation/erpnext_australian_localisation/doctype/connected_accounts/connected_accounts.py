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
def get_sync_job(job_id):
	return basiq_connector.get_job(job_id)


@frappe.whitelist()
def submit_mfa_response(response_url, mfa_response):
	mfa_response = frappe.parse_json(mfa_response) if isinstance(mfa_response, str) else mfa_response
	return basiq_connector.submit_mfa_response(response_url, mfa_response)
