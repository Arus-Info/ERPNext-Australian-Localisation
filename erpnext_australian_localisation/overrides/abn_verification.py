import json

import frappe
import requests


def fetch_and_update_abn(doctype, docname):
	doc = frappe.get_doc(doctype, docname)

	settings = frappe.get_single("AU Localisation Settings")
	# no check in au localisation settings no api calls
	if not settings.is_verify_abn:
		return

	# get pwd from au localisation settings
	guid = settings.get_password("abn_lookup_guid")

	# no tax id no api call exits function
	if not doc.tax_id:
		return

	# api call
	response = requests.get(
		# this link gives value in jsonp format
		"https://abr.business.gov.au/json/AbnDetails.aspx",
		params={
			# sends abn num and remove spaces
			"abn": doc.tax_id.strip(),
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

	# # 🔴 ABR error
	# if data.get("Message"):
	# 	frappe.throw(data["Message"])

	# SAVE VALUES INTO DOCUMENT (THIS IS THE KEY)
	doc.entity_name = data.get("EntityName") or ""
	doc.business_name = ", ".join(data.get("BusinessName") or [])
	doc.abn_status = data.get("AbnStatus") or ""
	doc.abn_effective_from = data.get("AbnStatusEffectiveFrom") or ""
	doc.address_postcode = data.get("AddressPostcode") or ""
	doc.address_state = data.get("AddressState") or ""
