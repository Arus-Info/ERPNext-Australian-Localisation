import frappe
import requests

BASIQ_API_BASE = "https://au-api.basiq.io"
BASIQ_API_VERSION = "3.0"


def _fetch_access_token(api_key, cache_key, data):
	cache = frappe.cache()

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
		data=data,
		timeout=30,
	)
	response.raise_for_status()

	token = response.json()["access_token"]

	cache.set_value(
		cache_key,
		token,
		expires_in_sec=3000,
	)
	return token


def get_headers(api_key, user_id=None):
	# user_id is unused here, it keeps the signature shared with get_client_headers
	data = {"scope": "SERVER_ACCESS"}
	token = _fetch_access_token(api_key, "basiq_access_token", data)

	return {
		"Authorization": f"Bearer {token}",
		"Accept": "application/json",
		"basiq-version": BASIQ_API_VERSION,
	}


def get_client_headers(api_key, user_id):
	data = {"scope": "CLIENT_ACCESS", "userId": user_id}
	token = _fetch_access_token(api_key, f"basiq_client_access_token:{user_id}", data)

	return {
		"Authorization": f"Bearer {token}",
		"Accept": "application/json",
		"basiq-version": BASIQ_API_VERSION,
	}


def get_user_id():
	return frappe.get_cached_doc("AU Localisation Settings").user_id


def _basiq_request(url, method="GET", headers_for=get_headers, extra_headers={}, timeout=30, **kwargs):
	settings = frappe.get_cached_doc("AU Localisation Settings")
	api_key = settings.get_password("api_key")

	headers = {**headers_for(api_key, settings.user_id), **extra_headers}

	response = requests.request(method, url, headers=headers, timeout=timeout, **kwargs)
	response.raise_for_status()

	return response


def get_accounts(connection_id=None):
	url = f"{BASIQ_API_BASE}/users/{get_user_id()}/accounts"
	response = _basiq_request(url)

	accounts = response.json().get("data", [])
	if connection_id:
		accounts = [account for account in accounts if account.get("connection") == connection_id]

	return accounts


def get_connections():
	user_id = get_user_id()

	cache = frappe.cache()
	cache_key = f"basiq_connections:{user_id}"

	connections = cache.get_value(cache_key)
	if connections:
		return connections

	url = f"{BASIQ_API_BASE}/users/{user_id}/connections"
	response = _basiq_request(url)

	connections = response.json().get("data", [])
	if connections:
		cache.set_value(cache_key, connections, expires_in_sec=60)

	return connections


def get_institution(institution_id):
	cache = frappe.cache()
	cache_key = f"basiq_institution:{institution_id}"

	institution = cache.get_value(cache_key)
	if institution:
		return institution

	url = f"{BASIQ_API_BASE}/institutions/{institution_id}"
	response = _basiq_request(url)

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
	url = f"{BASIQ_API_BASE}/users/{get_user_id()}/connections/{connection_id}/refresh"
	response = _basiq_request(url, method="POST")

	return response.json()


def get_job(job_id):
	url = f"{BASIQ_API_BASE}/jobs/{job_id}"
	response = _basiq_request(url)

	return response.json()


def submit_mfa_response(response_url, mfa_response):
	response = _basiq_request(
		response_url,
		method="POST",
		headers_for=get_client_headers,
		extra_headers={"Content-Type": "application/json"},
		json={"mfa-response": mfa_response},
	)

	return response.json() if response.content else {}


def get_transactions(provider_account_id, sync_date=None):
	filter_expr = f"account.id.eq('{provider_account_id}')"
	if sync_date:
		filter_expr += f",transaction.postDate.gteq('{sync_date.strftime('%Y-%m-%d')}')"

	url = f"{BASIQ_API_BASE}/users/{get_user_id()}/transactions"
	params = {
		"filter": filter_expr,
		"limit": 500,
	}

	transactions = []

	while url:
		response = _basiq_request(url, params=params, timeout=60)
		# pagination: get the next page of results if available
		payload = response.json()

		transactions.extend(payload.get("data", []))

		url = payload.get("links", {}).get("next")
		params = None

	return transactions
