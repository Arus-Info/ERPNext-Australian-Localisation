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

	gst_status = "Registered for GST" if data.get("Gst") else "Not currently Registered for GST"

	return {
		"success": True,
		"entity_name": data.get("EntityName") or "",
		"business_name": ", ".join(data.get("BusinessName") or [])[:140],
		"abn_status": data.get("AbnStatus") or "",
		"abn_effective_from": data.get("AbnStatusEffectiveFrom") or "",
		"address_postcode": data.get("AddressPostcode") or "",
		"address_state": data.get("AddressState") or "",
		"gst_status": gst_status,
	}


def refresh_abn_details():
	guid = frappe.db.get_single_value("AU Localisation Settings", "abn_lookup_guid")

	for doctype in ("Customer", "Supplier"):
		records = frappe.get_all(
			doctype,
			filters={"is_verify_abn": 1, "tax_id": ["is", "set"]},
			fields=["name", "tax_id"],
		)

		for row in records:
			tax_id = (row.tax_id or "").replace(" ", "")
			data = fetch_and_update_abn(tax_id, guid)

			frappe.db.set_value(
				doctype,
				row.name,
				{
					"entity_name": data.get("entity_name"),
					"business_name": data.get("business_name"),
					"abn_status": data.get("abn_status"),
					"abn_effective_from": data.get("abn_effective_from"),
					"address_postcode": data.get("address_postcode"),
					"address_state": data.get("address_state"),
					"gst_status": data.get("gst_status"),
				},
			)
