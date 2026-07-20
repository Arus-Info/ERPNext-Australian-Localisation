import frappe
from frappe.utils import add_to_date, get_datetime, getdate, now_datetime

from erpnext_australian_localisation.erpnext_australian_localisation.integration.basiq_connector import (
    BasiqConnector,
)


@frappe.whitelist()
def fetch_transactions():
    connector = BasiqConnector()

    accounts = frappe.get_all(
        "Bank Account",
        filters={"basiq_account_id": ["is", "set"]},
        fields=["name", "basiq_account_id", "last_sync"],
    )

    for account in accounts:
        sync_date = get_datetime(account.last_sync) if account.last_sync else None

        if sync_date:
            sync_date = add_to_date(sync_date, minutes=-30)

        now_time = now_datetime()
        transactions = connector.get_transactions(account.basiq_account_id, sync_date=sync_date)

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
                "bank_account": account.name,
                "date": getdate(txn.get("postDate")),
                "deposit": max(amount, 0.0),
                "withdrawal": abs(min(amount, 0.0)),
                "description": txn.get("description"),
                "transaction_id": transaction_id,
            })

            doc.insert(ignore_permissions=True)
            doc.submit()

        frappe.db.set_value("Bank Account", account.name, "last_sync", now_time)

    frappe.db.commit()

    return "Transactions Imported"
