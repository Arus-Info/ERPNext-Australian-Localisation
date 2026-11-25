from datetime import datetime

import frappe
from frappe.utils import add_to_date, get_datetime, getdate, now_datetime

from erpnext_australian_localisation.integration.basiq import basiq_connector


def sync_account_transactions(bank_account: str, provider_account_id: str, sync_date: datetime | str):
	log = frappe.get_doc(
		{
			"doctype": "AU Bank Statement Import Log",
			"transaction_creation_at": now_datetime(),
			"bank_account": bank_account,
			"status": "Success",
		}
	).insert(ignore_permissions=True)

	try:
		# 30 mins buffer to avoid missing transactions due to time zone differences
		from_date = add_to_date(get_datetime(sync_date), minutes=-30)
		transactions = basiq_connector.get_transactions(provider_account_id, sync_date=from_date)

		existing_ids = set(
			frappe.get_all(
				"Bank Transaction",
				filters={"transaction_id": ["in", [txn.get("id") for txn in transactions]]},
				pluck="transaction_id",
			)
		)

		for txn in transactions:
			if txn.get("id") in existing_ids:
				continue

			amount = float(txn.get("amount", 0))
			doc = frappe.get_doc(
				{
					"doctype": "Bank Transaction",
					"bank_account": bank_account,
					"date": getdate(txn.get("postDate")),
					"deposit": max(amount, 0.0),
					"withdrawal": abs(min(amount, 0.0)),
					"description": txn.get("description"),
					"transaction_id": txn.get("id"),
					"au_bank_statement_import_log": log.name,
				}
			)
			doc.insert(ignore_permissions=True)
			doc.submit()

		frappe.db.set_value("Bank Account", bank_account, "last_sync", now_datetime())
	except Exception as e:
		frappe.log_error(f"Bank Transaction Sync Error: {e!s}")
		log.status = "Failed"
		log.error_message = str(e)
		log.save(ignore_permissions=True)


@frappe.whitelist()
def get_provider_connections():
	return [
		{
			"id": connection.get("id"),
			"institution": basiq_connector.get_institution_name(connection.get("institution")),
			"account_holder": basiq_connector.get_account_holder(connection),
		}
		for connection in basiq_connector.get_connections()
	]


@frappe.whitelist()
def get_provider_accounts(connection_id: str):
	linked_account_ids = set(
		frappe.get_all(
			"Bank Account", filters={"provider_account_id": ["is", "set"]}, pluck="provider_account_id"
		)
	)

	return [
		{
			"id": account.get("id"),
			"name": account.get("name"),
			"display_name": account.get("displayName"),
			"account_no": account.get("accountNo"),
		}
		for account in basiq_connector.get_accounts(connection_id)
		if account.get("id") not in linked_account_ids
	]


def set_mfa_requirement(doc, method=None):
	if not doc.has_value_changed("connection_id"):
		return

	doc.mfa_requirement = None
	if not doc.connection_id:
		return

	try:
		doc.mfa_requirement = basiq_connector.get_mfa_requirement(doc.connection_id)
	except Exception:
		# don't block saving the bank account, the nightly refresh finds out if it needs MFA
		frappe.log_error(title="Basiq MFA Requirement Lookup Failed", message=frappe.get_traceback())


@frappe.whitelist()
def get_connection_accounts(connection_id: str):
	return frappe.get_all(
		"Bank Account",
		filters={
			"connection_id": connection_id,
			"enable_transaction_import": 1,
			"disabled": 0,
			"provider_account_id": ["is", "set"],
		},
		fields=["name", "account_name", "bank", "provider_account_id", "last_sync"],
		order_by="account_name",
	)


@frappe.whitelist()
def sync_connection_transactions(connection_id: str, bank_accounts: str | list | None = None):
	accounts = get_connection_accounts(connection_id)
	if bank_accounts:
		bank_accounts = frappe.parse_json(bank_accounts)
		accounts = [account for account in accounts if account.name in bank_accounts]

	for account in accounts:
		sync_account_transactions(
			account.name,
			provider_account_id=account.provider_account_id,
			sync_date=account.last_sync,
		)


def get_scheduled_connections():
	if not frappe.get_cached_doc("AU Localisation Settings").enable_open_banking:
		return []

	# connections that always ask for a code can only be synced from the Sync button
	return frappe.get_all(
		"Bank Account",
		filters={
			"enable_transaction_import": 1,
			"disabled": 0,
			"connection_id": ["is", "set"],
			"provider_account_id": ["is", "set"],
			"mfa_requirement": ["!=", "Always"],
		},
		pluck="connection_id",
		distinct=True,
	)


def get_refresh_job_cache_key(connection_id):
	return f"basiq_refresh_job:{connection_id}"


def refresh_non_mfa_connections():
	for connection_id in get_scheduled_connections():
		try:
			job = basiq_connector.refresh_connection(connection_id)
		except Exception:
			frappe.log_error(
				title=f"Basiq Connection Refresh Failed: {connection_id}", message=frappe.get_traceback()
			)
			continue

		# sync_non_mfa_connections checks this job before importing
		frappe.cache().set_value(get_refresh_job_cache_key(connection_id), job.get("id"), expires_in_sec=3600)


def sync_non_mfa_connections():
	cache = frappe.cache()

	for connection_id in get_scheduled_connections():
		cache_key = get_refresh_job_cache_key(connection_id)
		job_id = cache.get_value(cache_key)
		if not job_id:
			# the refresh didn't start, and that failure is already logged
			continue

		cache.delete_value(cache_key)

		try:
			steps = basiq_connector.get_job(job_id).get("steps", [])
		except Exception:
			frappe.log_error(
				title=f"Basiq Refresh Job Check Failed: {connection_id}", message=frappe.get_traceback()
			)
			continue

		unfinished_step = next((step for step in steps if step.get("status") != "success"), None)
		if unfinished_step:
			message = (
				f"Step {unfinished_step.get('title')} of job {job_id} is {unfinished_step.get('status')}, "
				"so transactions were not imported."
			)
			if unfinished_step.get("title") == "mfa-challenge":
				message += " The bank asked for a verification code, use the Sync button on the bank account instead."

			frappe.log_error(title=f"Basiq Connection Refresh Incomplete: {connection_id}", message=message)
			continue

		sync_connection_transactions(connection_id)
