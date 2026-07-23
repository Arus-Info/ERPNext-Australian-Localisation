import frappe
import requests
from frappe import _

BASIQ_API_BASE = "https://au-api.basiq.io"
BASIQ_API_VERSION = "3.0"


def get_access_token(api_key):
	cache = frappe.cache()

	token = cache.get_value("basiq_access_token")
	if token:
		return token

	response = requests.post(
		f"{BASIQ_API_BASE}/token",
		headers={
			"Authorization": f"Basic {api_key}",
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

	cache.set_value(
		"basiq_access_token",
		token,
		expires_in_sec=3000,
	)
	return token


def get_headers(api_key):
	return {
		"Authorization": f"Bearer {get_access_token(api_key)}",
		"Accept": "application/json",
		"basiq-version": BASIQ_API_VERSION,
	}


def get_accounts():
	settings = frappe.get_single("AU Localisation Settings")
	api_key = settings.get_password("api_key")

	url = f"{BASIQ_API_BASE}/users/{settings.user_id}/accounts"
	response = requests.get(url, headers=get_headers(api_key), timeout=30)
	response.raise_for_status()

	return response.json().get("data", [])


def get_transactions(provider_account_id, sync_date=None):
	settings = frappe.get_single("AU Localisation Settings")
	api_key = settings.get_password("api_key")

	filter_expr = f"account.id.eq('{provider_account_id}')"
	if sync_date:
		filter_expr += f",transaction.postDate.gteq('{sync_date.strftime('%Y-%m-%d')}')"

	url = f"{BASIQ_API_BASE}/users/{settings.user_id}/transactions"
	params = {
		"filter": filter_expr,
		"limit": 500,
	}

	transactions = []

	while url:
		response = requests.get(
			url,
			headers=get_headers(api_key),
			params=params,
			timeout=60,
		)
		response.raise_for_status()
		# pagination: get the next page of results if available
		payload = response.json()

		transactions.extend(payload.get("data", []))

		url = payload.get("links", {}).get("next")
		params = None

	return transactions
