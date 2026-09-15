import frappe
import requests

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


def get_client_access_token(api_key, user_id):
	cache = frappe.cache()
	cache_key = f"basiq_client_access_token:{user_id}"

	token = cache.get_value(cache_key)
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
		data={"scope": "CLIENT_ACCESS", "userId": user_id},
		timeout=30,
	)
	response.raise_for_status()

	data = response.json()
	token = data["access_token"]

	cache.set_value(
		cache_key,
		token,
		expires_in_sec=3000,
	)
	return token


def get_client_headers(api_key, user_id):
	return {
		"Authorization": f"Bearer {get_client_access_token(api_key, user_id)}",
		"Accept": "application/json",
		"basiq-version": BASIQ_API_VERSION,
	}


def get_accounts(connection_id=None):
	settings = frappe.get_cached_doc("AU Localisation Settings")
	api_key = settings.get_password("api_key")

	url = f"{BASIQ_API_BASE}/users/{settings.user_id}/accounts"
	response = requests.get(url, headers=get_headers(api_key), timeout=30)
	response.raise_for_status()

	accounts = response.json().get("data", [])
	if connection_id:
		accounts = [account for account in accounts if account.get("connection") == connection_id]

	return accounts


def get_connections():
	settings = frappe.get_cached_doc("AU Localisation Settings")
	api_key = settings.get_password("api_key")

	url = f"{BASIQ_API_BASE}/users/{settings.user_id}/connections"
	response = requests.get(url, headers=get_headers(api_key), timeout=30)
	response.raise_for_status()

	return response.json().get("data", [])


def get_institution(institution_id):
	cache = frappe.cache()
	cache_key = f"basiq_institution:{institution_id}"

	institution = cache.get_value(cache_key)
	if institution:
		return institution

	settings = frappe.get_cached_doc("AU Localisation Settings")
	api_key = settings.get_password("api_key")

	url = f"{BASIQ_API_BASE}/institutions/{institution_id}"
	response = requests.get(url, headers=get_headers(api_key), timeout=30)
	response.raise_for_status()

	institution = response.json()
	cache.set_value(cache_key, institution, expires_in_sec=86400)
	return institution


def get_institution_name(institution):
	institution_id = institution.get("id") if isinstance(institution, dict) else institution
	try:
		return get_institution(institution_id).get("name") or institution_id
	except Exception:
		return institution_id


def refresh_connection(connection_id):
	settings = frappe.get_cached_doc("AU Localisation Settings")
	api_key = settings.get_password("api_key")

	url = f"{BASIQ_API_BASE}/users/{settings.user_id}/connections/{connection_id}/refresh"
	response = requests.post(url, headers=get_headers(api_key), timeout=30)
	response.raise_for_status()

	return response.json()


def get_job(job_id):
	settings = frappe.get_cached_doc("AU Localisation Settings")
	api_key = settings.get_password("api_key")

	url = f"{BASIQ_API_BASE}/jobs/{job_id}"
	response = requests.get(url, headers=get_headers(api_key), timeout=30)
	response.raise_for_status()

	return response.json()


def submit_mfa_response(response_url, mfa_response):
	settings = frappe.get_cached_doc("AU Localisation Settings")
	api_key = settings.get_password("api_key")

	headers = get_client_headers(api_key, settings.user_id)
	headers["Content-Type"] = "application/json"

	response = requests.post(
		response_url,
		headers=headers,
		json={"mfa-response": mfa_response},
		timeout=30,
	)
	response.raise_for_status()

	return response.json() if response.content else {}


def get_transactions(provider_account_id, sync_date=None):
	settings = frappe.get_cached_doc("AU Localisation Settings")
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
