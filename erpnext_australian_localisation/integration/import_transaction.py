import frappe
from frappe import _
from frappe.utils import add_to_date, get_datetime, getdate, now_datetime

from erpnext_australian_localisation.integration import basiq_connector


@frappe.whitelist()
def sync_account_transactions(bank_account: str, provider_account_id: str, sync_date: str):
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


def fetch_transactions():
	accounts = frappe.get_all(
		"Bank Account",
		filters={"enable_transaction_import": 1, "provider_account_id": ["is", "set"]},
		fields=["name", "provider_account_id", "last_sync"],
	)

	for account in accounts:
		sync_account_transactions(
			account.name,
			provider_account_id=account.provider_account_id,
			sync_date=account.last_sync,
		)

	return "Transactions Imported"


@frappe.whitelist()
def get_provider_accounts():
	accounts = basiq_connector.get_accounts()
	result = []
	for account in accounts:
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
