import frappe
from frappe import _

from erpnext_australian_localisation.overrides.payment_batch import _send_remittance_email


@frappe.whitelist()
def check_party_email(docname: str, party_type: str):
	party = frappe.db.get_value("Payment Entry", docname, "party")

	email = frappe.db.get_value(
		"Contact",
		{"link_doctype": party_type, "link_name": party},
		"email_id",
	)
	if not email:
		frappe.throw(_("No email found for {0} {1}").format(party_type, party))
	return True


@frappe.whitelist()
def send_payment_receipt(docname: str):
	doc = frappe.get_doc("Payment Entry", docname)

	template = frappe.db.get_single_value("AU Localisation Settings", "payment_receipt_template")
	if not template:
		frappe.throw(_("Please set a Payment Receipt Template in AU Localisation Settings"))

	email = frappe.db.get_value(
		"Contact",
		{
			"link_doctype": "Customer",
			"link_name": doc.party,
		},
		"email_id",
	)

	pe_dict = doc.as_dict()

	template_data = frappe.get_attr("frappe.email.doctype.email_template.email_template.get_email_template")(
		template_name=template,
		doc=frappe.as_json(pe_dict),
	)

	if not template_data:
		frappe.throw(_("Could not render email template"))

	frappe.get_attr("frappe.core.doctype.communication.email.make")(
		doctype="Payment Entry",
		name=docname,
		recipients=email,
		subject=template_data.get("subject"),
		content=template_data.get("message"),
		send_email=1,
		print_format="Payment Receipt",
		print_letterhead=1,
		print_language="en",
		add_css=1,
	)

	return True


@frappe.whitelist()
def send_remittance_email(docname: str):

	template = frappe.db.get_single_value("AU Localisation Settings", "remittance_advice_template")
	if not template:
		frappe.throw(_("Please set a Remittance Advice Template in AU Localisation Settings"))
	party = frappe.db.get_value(
		"Payment Entry",
		docname,
		"party",
	)

	email = frappe.db.get_value(
		"Contact",
		{
			"link_doctype": "Supplier",
			"link_name": party,
		},
		"email_id",
	)

	if email:
		_send_remittance_email(
			payment_entry=docname,
			email=email,
			template=template,
		)
	return True
