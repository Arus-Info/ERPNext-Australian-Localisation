# Copyright (c) 2026, Adhi and contributors
# For license information, please see license.txt

import frappe
import requests
from frappe import _

BASIQ_API_BASE = "https://au-api.basiq.io"
BASIQ_API_VERSION = "3.0"


class BasiqConnector:
	def __init__(self):
		self.settings = frappe.get_single("AU Localisation Settings")
		self.api_key = self.settings.get_password("api_key")
		self.user_id = self.settings.user_id
		self.access_token = self.get_access_token()

	def get_access_token(self):
		# This connector only runs once a day from the cron job, so we just
		# fetch a fresh token every time instead of caching/checking expiry.
		response = requests.post(
			f"{BASIQ_API_BASE}/token",
			headers={
				"Authorization": f"Basic {self.api_key}",
				"Accept": "application/json",
				"Content-Type": "application/x-www-form-urlencoded",
				"basiq-version": BASIQ_API_VERSION,
			},
			data={"scope": "SERVER_ACCESS"},
			timeout=30,
		)
		response.raise_for_status()
		token = response.json()["access_token"]
		frappe.db.commit()

		return token

	def get_headers(self):
		return {
			"Authorization": f"Bearer {self.access_token}",
			"Accept": "application/json",
			"basiq-version": BASIQ_API_VERSION,
		}

	def get_accounts(self):
		url = f"{BASIQ_API_BASE}/users/{self.user_id}/accounts"
		accounts = []

		while url:
			response = requests.get(
				url,
				headers=self.get_headers(),
				timeout=60,
			)
			response.raise_for_status()
			payload = response.json()

			accounts.extend(payload.get("data", []))

			url = payload.get("links", {}).get("next")

		return accounts

	def get_institution(self, institution_id):
		response = requests.get(
			f"{BASIQ_API_BASE}/institutions/{institution_id}",
			headers=self.get_headers(),
			timeout=30,
		)
		response.raise_for_status()

		return response.json()

	def get_transactions(self, basiq_account_id, sync_date=None):
		filter_expr = f"account.id.eq('{basiq_account_id}')"
		if sync_date:
			filter_expr += f",transaction.postDate.gteq('{sync_date.strftime('%Y-%m-%d')}')"

		url = f"{BASIQ_API_BASE}/users/{self.user_id}/transactions"
		params = {
			"filter": filter_expr,
			"limit": 500,
		}

		transactions = []

		while url:
			response = requests.get(
				url,
				headers=self.get_headers(),
				params=params,
				timeout=60,
			)
			response.raise_for_status()
			payload = response.json()

			transactions.extend(payload.get("data", []))

			url = payload.get("links", {}).get("next")
			params = None

		return transactions
