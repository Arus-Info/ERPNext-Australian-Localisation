import frappe
from frappe.utils import add_to_date, get_datetime, getdate, now_datetime

from erpnext_australian_localisation.integration.basiq_connector import (
    BasiqConnector,
)


@frappe.whitelist()
def sync_account_transactions(bank_account, provider_account_id=None, sync_date=None):

    connector = BasiqConnector()
    provider_account_id = provider_account_id or frappe.db.get_value(
        "Bank Account", bank_account, "provider_account_id"
    )
    transactions = connector.get_transactions(provider_account_id, sync_date=sync_date)

    for txn in transactions:
        transaction_id = txn.get("id")

        if frappe.db.exists(
            "Bank Transaction",
            {"transaction_id": transaction_id},
        ):
            continue

        amount = float(txn.get("amount", 0))

        doc = frappe.get_doc({
            "doctype": "Bank Transaction",
            "bank_account": bank_account,
            "date": getdate(txn.get("postDate")),
            "deposit": max(amount, 0.0),
            "withdrawal": abs(min(amount, 0.0)),
            "description": txn.get("description"),
            "transaction_id": transaction_id,
        })

        doc.insert(ignore_permissions=True)
        doc.submit()

    frappe.db.set_value("Bank Account", bank_account, "last_sync", now_datetime())


def fetch_transactions():
    accounts = frappe.get_all(
        "Bank Account",
        filters={"enable_transaction_import": 1, "provider_account_id": ["is", "set"]},
        fields=["name", "provider_account_id", "last_sync"],
    )

    for account in accounts:
        sync_date = get_datetime(account.last_sync) if account.last_sync else None
        if sync_date:
            sync_date = add_to_date(sync_date, minutes=-30)

        sync_account_transactions(
            account.name,
            provider_account_id=account.provider_account_id,
            sync_date=sync_date,
        )

    frappe.db.commit()

    return "Transactions Imported"

@frappe.whitelist()
def get_provider_accounts():
	connector = BasiqConnector()
	accounts = connector.get_accounts()
	return [
		{
			"id": account.get("id"),
			"name": account.get("name"),
			"display_name": account.get("displayName"),
			"account_no": account.get("accountNo"),
			"balance": account.get("balance"),
		}
		for account in accounts
	]