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
		cache = frappe.cache()

		token = cache.get_value("basiq_access_token")
		if token:
			return token

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

		data = response.json()
		token = data["access_token"]

		expires_in = data.get("expires_in", 3600)

		# Store slightly less than actual expiry
		cache.set_value(
			"basiq_access_token",
			token,
			expires_in_sec=expires_in - 60,
		)
		return token

	def get_headers(self):
		return {
			"Authorization": f"Bearer {self.access_token}",
			"Accept": "application/json",
			"basiq-version": BASIQ_API_VERSION,
		}

	def get_accounts(self):
		url = f"{BASIQ_API_BASE}/users/{self.user_id}/accounts"
		response = requests.get(url, headers=self.get_headers(), timeout=30)
		response.raise_for_status()

		return response.json().get("data", [])

	def get_transactions(self, provider_account_id, sync_date=None):
		filter_expr = f"account.id.eq('{provider_account_id}')"
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
