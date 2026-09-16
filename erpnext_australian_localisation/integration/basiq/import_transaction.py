from datetime import datetime

import frappe
from frappe.utils import add_to_date, get_datetime, getdate, now_datetime

from erpnext_australian_localisation.integration.basiq import basiq_connector


@frappe.whitelist()
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

		for txn in transactions:
			transaction_id = txn.get("id")

			if frappe.db.exists(
				"Bank Transaction",
				{"transaction_id": transaction_id},
			):
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
					"transaction_id": transaction_id,
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
def get_provider_accounts(connection_id: str | None = None):
	accounts = basiq_connector.get_accounts(connection_id=connection_id)

	linked_account_ids = set(
		frappe.get_all(
			"Bank Account",
			filters={"provider_account_id": ["is", "set"]},
			pluck="provider_account_id",
		)
	)

	result = []
	for account in accounts:
		if account.get("id") in linked_account_ids:
			continue

		result.append(
			{
				"id": account.get("id"),
				"name": account.get("name"),
				"display_name": account.get("displayName"),
				"account_no": account.get("accountNo"),
				"balance": account.get("balance"),
			}
		)
	return result


@frappe.whitelist()
def get_provider_connections():
	connections = basiq_connector.get_connections()
	result = []
	for connection in connections:
		institution_name = basiq_connector.get_institution_name(connection.get("institution"))

		result.append(
			{
				"id": connection.get("id"),
				"institution": institution_name,
			}
		)
	return result


@frappe.whitelist()
def ensure_connected_account(connection_id: str):
	settings = frappe.get_doc("AU Localisation Settings")

	existing_row = next((row for row in settings.table_talc if row.connection_id == connection_id), None)
	if existing_row:
		return

	connection = next((c for c in basiq_connector.get_connections() if c.get("id") == connection_id), None)

	institution_name = basiq_connector.get_institution_name(connection.get("institution"))
	mfa_challenge = 1 if connection.get("mfaEnabled") else 0

	settings.append(
		"table_talc",
		{
			"institution": institution_name,
			"connection_id": connection_id,
			"mfa_challenge": mfa_challenge,
		},
	)
	settings.save(ignore_permissions=True)


def get_non_mfa_connections():
	return frappe.get_all(
		"Connected Accounts",
		filters={"mfa_challenge": 0},
		fields=["connection_id"],
	)


@frappe.whitelist()
def get_connection_accounts(connection_id: str):
	return frappe.get_all(
		"Bank Account",
		filters={
			"connection_id": connection_id,
			"enable_transaction_import": 1,
			"provider_account_id": ["is", "set"],
		},
		fields=["name", "account_name", "provider_account_id", "last_sync"],
	)


@frappe.whitelist()
def sync_connection_transactions(connection_id: str | None = None, bank_account: str | None = None):
	if bank_account:
		accounts = [
			frappe.db.get_value(
				"Bank Account",
				bank_account,
				["name", "provider_account_id", "last_sync"],
				as_dict=True,
			)
		]
	else:
		accounts = get_connection_accounts(connection_id)

	for account in accounts:
		sync_account_transactions(
			account.name,
			provider_account_id=account.provider_account_id,
			sync_date=account.last_sync,
		)

	return "Transactions Imported"


def refresh_non_mfa_connections():
	for row in get_non_mfa_connections():
		basiq_connector.refresh_connection(row.connection_id)


def sync_non_mfa_connections():
	for row in get_non_mfa_connections():
		sync_connection_transactions(connection_id=row.connection_id)
