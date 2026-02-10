import json

import frappe
import requests
from frappe import _


@frappe.whitelist()
def fetch_and_update_abn(tax_id: str) -> None:
	settings = frappe.get_cached_doc("AU Localisation Settings")
	# no check in au localisation settings no api call
	if not settings.is_verify_abn:
		return

	# get guid from au localisation settings

	guid = settings.abn_lookup_guid

	# Normalize ABN
	abn = "".join(ch for ch in (tax_id or "") if ch.isdigit())

	if len(abn) != 11:
		return {}

		# api call

	response = requests.get(
		# this link gives value in jsonp format
		"https://abr.business.gov.au/json/AbnDetails.aspx",
		params={
			# sends abn num
			"abn": abn,
			# sends guid and removes spaces
			"guid": guid.strip(),
			# tells abr to give jsonp format
			# callback is a parameter req for abr to give jsonp format
			"callback": "callback",
		},
		timeout=20,
	)
	# handles http error
	response.raise_for_status()

	# reads api response as plain text
	raw = response.text.strip()

	# JSONP → JSON
	if raw.startswith("callback("):
		raw = raw[len("callback(") : -1]

	# json string to python dict
	data = json.loads(raw)

	# this is abr error thows when guid in wrong
	message = (data.get("Message") or "").lower()

	# GUID problem → show error
	if "guid" in message:
		frappe.throw(_("The entered GUID is invalid. Unable to fetch ABN informations"))

	# save values into document
	return {
		"entity_name": data.get("EntityName") or "",
		"business_name": ", ".join(data.get("BusinessName") or [])[:140],
		"abn_status": data.get("AbnStatus") or "",
		"abn_effective_from": data.get("AbnStatusEffectiveFrom") or "",
		"address_postcode": data.get("AddressPostcode") or "",
		"address_state": data.get("AddressState") or "",
	}
