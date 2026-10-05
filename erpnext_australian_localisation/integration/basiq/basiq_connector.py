import frappe
import requests

BASIQ_API_BASE = "https://au-api.basiq.io"
BASIQ_API_VERSION = "3.0"

# institution "authorization" -> Bank Account "MFA Requirement"
MFA_REQUIREMENTS = {
	"user-mfa": "Always",
	"user-mfa-intermittent": "Sometimes",
}


def get_access_token(client_access=False):
	settings = frappe.get_cached_doc("AU Localisation Settings")

	if client_access:
		cache_key = f"basiq_client_access_token:{settings.user_id}"
		data = {"scope": "CLIENT_ACCESS", "userId": settings.user_id}
	else:
		cache_key = "basiq_access_token"
		data = {"scope": "SERVER_ACCESS"}

	cache = frappe.cache()
	token = cache.get_value(cache_key)
	if token:
		return token

	response = requests.post(
		f"{BASIQ_API_BASE}/token",
		headers={
			"Authorization": f"Basic {settings.get_password('api_key')}",
			"Accept": "application/json",
			"Content-Type": "application/x-www-form-urlencoded",
			"basiq-version": BASIQ_API_VERSION,
		},
		data=data,
		timeout=30,
	)
	response.raise_for_status()

	token = response.json()["access_token"]
	cache.set_value(cache_key, token, expires_in_sec=3000)
	return token


def get_user_url():
	return f"{BASIQ_API_BASE}/users/{frappe.get_cached_doc('AU Localisation Settings').user_id}"


def _basiq_request(url, method="GET", timeout=30, client_access=False, **kwargs):
	headers = {
		"Authorization": f"Bearer {get_access_token(client_access)}",
		"Accept": "application/json",
		"basiq-version": BASIQ_API_VERSION,
	}
	response = requests.request(method, url, headers=headers, timeout=timeout, **kwargs)
	response.raise_for_status()
	return response.json() if response.content else {}


def _cached_request(cache_key, url, expires_in_sec):
	cache = frappe.cache()

	data = cache.get_value(cache_key)
	if data is None:
		data = _basiq_request(url)
		cache.set_value(cache_key, data, expires_in_sec=expires_in_sec)

	return data


def get_connections():
	return _cached_request("basiq_connections", f"{get_user_url()}/connections", 60).get("data", [])


def get_connection(connection_id):
	return _cached_request(
		f"basiq_connection:{connection_id}", f"{get_user_url()}/connections/{connection_id}", 86400
	)


def get_institutions():
	# one call for every institution instead of one call per connection
	cache = frappe.cache()

	institutions = cache.get_value("basiq_institutions")
	if institutions is None:
		institutions = {}
		url = f"{BASIQ_API_BASE}/institutions"
		while url:
			payload = _basiq_request(url, timeout=60)
			for institution in payload.get("data", []):
				# only keep what we read, the full list is large
				institutions[institution.get("id")] = {
					"id": institution.get("id"),
					"name": institution.get("name"),
					"authorization": institution.get("authorization"),
				}
			url = payload.get("links", {}).get("next")

		cache.set_value("basiq_institutions", institutions, expires_in_sec=86400)

	return institutions


def get_institution(institution):
	# connections give the institution either as an id or as {"id": ...}
	institution_id = institution.get("id") if isinstance(institution, dict) else institution

	# fall back to a single lookup for an institution added since the list was cached
	return get_institutions().get(institution_id) or _cached_request(
		f"basiq_institution:{institution_id}", f"{BASIQ_API_BASE}/institutions/{institution_id}", 86400
	)


def get_institution_name(institution):
	try:
		return get_institution(institution).get("name")
	except Exception:
		return None


def get_account_holder(connection):
	# the connection list may leave out the profile, so fall back to fetching the connection itself
	try:
		profile = connection.get("profile") or get_connection(connection.get("id")).get("profile") or {}
	except Exception:
		return None

	return profile.get("fullName") or " ".join(
		filter(None, [profile.get("firstName"), profile.get("lastName")])
	)


def get_mfa_requirement(connection_id):
	authorization = get_institution(get_connection(connection_id).get("institution")).get("authorization")
	return MFA_REQUIREMENTS.get(authorization, "Not Required")


def get_accounts(connection_id):
	accounts = _basiq_request(f"{get_user_url()}/accounts").get("data", [])
	return [account for account in accounts if account.get("connection") == connection_id]


def get_transactions(provider_account_id, sync_date=None):
	filter_expr = f"account.id.eq('{provider_account_id}')"
	if sync_date:
		filter_expr += f",transaction.postDate.gteq('{sync_date.strftime('%Y-%m-%d')}')"

	url = f"{get_user_url()}/transactions"
	params = {"filter": filter_expr, "limit": 500}

	transactions = []
	while url:
		payload = _basiq_request(url, params=params, timeout=60)
		transactions.extend(payload.get("data", []))

		# the next link already carries the filter
		url = payload.get("links", {}).get("next")
		params = None

	return transactions


@frappe.whitelist()
def refresh_connection(connection_id: str):
	return _basiq_request(f"{get_user_url()}/connections/{connection_id}/refresh", method="POST")


@frappe.whitelist()
def get_job(job_id: str):
	return _basiq_request(f"{BASIQ_API_BASE}/jobs/{job_id}")


@frappe.whitelist()
def submit_mfa_response(response_url: str, mfa_response: str | list):
	# the url comes from the browser, don't send a Basiq token anywhere else
	if not response_url.startswith(f"{BASIQ_API_BASE}/"):
		frappe.throw(frappe._("Invalid MFA response URL"))

	# this endpoint needs a client scope token, not the server one
	return _basiq_request(
		response_url,
		method="POST",
		client_access=True,
		json={"mfa-response": frappe.parse_json(mfa_response)},
	)
