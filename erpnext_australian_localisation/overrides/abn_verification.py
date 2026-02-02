import json

import frappe
import requests
from frappe import _


def clear_abn_fields(doc):
	doc.entity_name = ""
	doc.business_name = ""
	doc.abn_status = ""
	doc.abn_effective_from = ""
	doc.address_postcode = ""
	doc.address_state = ""


def fetch_and_update_abn(doctype, docname):
	doc = frappe.get_doc(doctype, docname)

	settings = frappe.get_single("AU Localisation Settings")

	# no check in au localisation settings no api calls
	if not settings.is_verify_abn:
		return

	# get guid from au localisation settings

	guid = settings.abn_lookup_guid

	# Normalize ABN
	abn = "".join(ch for ch in (doc.tax_id or "") if ch.isdigit())

	# Invalid / partial ABN → clear & exit
	if len(abn) != 11:
		clear_abn_fields(doc)
		return

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
	if data.get("Message"):
		frappe.throw(_("The entered GUID is invalid. Unable to fetch ABN informations"))

	# save values into document
	doc.entity_name = data.get("EntityName") or ""
	business_name = ", ".join(data.get("BusinessName") or [])
	doc.business_name = business_name[:140]  # 140 chars only
	doc.abn_status = data.get("AbnStatus") or ""
	doc.abn_effective_from = data.get("AbnStatusEffectiveFrom") or ""
	doc.address_postcode = data.get("AddressPostcode") or ""
	doc.address_state = data.get("AddressState") or ""
