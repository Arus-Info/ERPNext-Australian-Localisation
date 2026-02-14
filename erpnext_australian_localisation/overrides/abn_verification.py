import json

import frappe
import requests
from frappe import _


@frappe.whitelist()
def fetch_and_update_abn(tax_id: str, guid: str) -> dict:
	response = requests.get(
		"https://abr.business.gov.au/json/AbnDetails.aspx",
		params={"abn": tax_id, "guid": guid},
		timeout=20,
	)
	# throws http error when api fails it is an requests library in python
	response.raise_for_status()
	raw = response.text.strip()
	# # JSONP → JSON
	if raw.startswith("callback("):
		raw = raw[len("callback(") : -1]

	data = json.loads(raw)
	message = (data.get("Message") or "").strip()

	if message:
		return {"success": False, "error": message}
	return {
		"success": True,
		"entity_name": data.get("EntityName") or "",
		"business_name": ", ".join(data.get("BusinessName") or [])[:140],
		"abn_status": data.get("AbnStatus") or "",
		"abn_effective_from": data.get("AbnStatusEffectiveFrom") or "",
		"address_postcode": data.get("AddressPostcode") or "",
		"address_state": data.get("AddressState") or "",
	}
