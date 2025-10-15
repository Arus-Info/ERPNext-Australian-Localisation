import re

import frappe
from frappe import _


def validate(doc, event):
	if doc.branch_code:
		pattern = re.compile(r"^\d{6}$")
		branch_code = doc.branch_code.replace("-", "")
		if not pattern.match(branch_code):
			frappe.throw(_("Only 6-digit numbers are allowed in Branch code."))
		else:
			doc.branch_code = branch_code[0:3] + "-" + branch_code[3:]

	if doc.bank_account_no:
		pattern = re.compile(r"^\d{9}$")
		if not pattern.match(doc.bank_account_no):
			frappe.throw(_("Only 9-digit numbers are allowed in Bank Account Number."))


def bank_account_validation(doc, event):
	if doc.file_format != "-None-":
		if doc.apca_number:
			pattern = re.compile(r"^\d{6}$")
			if not pattern.match(doc.apca_number):
				frappe.throw(_("APCA Number must be exactly 6 digits."))

		if doc.fi_abbr:
			pattern = re.compile("^[A-Z]{3}$")
			if not pattern.match(doc.fi_abbr):
				frappe.throw(_("Financial Institution Abbreviation must be three capital letters."))

		validate(doc, event)
