import frappe
from frappe import _


@frappe.whitelist()
def get_missing_email_suppliers(docname: str):
	doc = frappe.get_doc("Payment Batch", docname)
	no_email = []
	for row in doc.payment_created or []:
		if not row.party:
			continue
		email = frappe.db.get_value(
			"Contact",
			{"link_doctype": "Supplier", "link_name": row.party},
			"email_id",
		)
		if not email:
			no_email.append(row.party_name or row.party)
	return no_email


@frappe.whitelist()
def send_remittance_email_from_pb(docname: str):
	doc = frappe.get_doc("Payment Batch", docname)

	template = frappe.db.get_single_value(
		"AU Localisation Settings",
		"remittance_advice_template",
	)

	if not template:
		frappe.throw(_("Please set a Remittance Email Template in AU Localisation Settings"))

	for row in doc.payment_created or []:
		if not row.party:
			continue

		email = frappe.db.get_value(
			"Contact",
			{
				"link_doctype": "Supplier",
				"link_name": row.party,
			},
			"email_id",
		)

		payment_entry = frappe.get_doc("Payment Entry", row.payment_entry)

		_send_remittance_email(
			payment_entry=payment_entry,
			email=email,
			template=template,
			payment_batch=doc,
		)

	return True


def _send_remittance_email(payment_entry, email, template, payment_batch=None):
	pe_dict = payment_entry.as_dict()
	pe_dict["payment_batch"] = payment_batch.as_dict() if payment_batch else {}

	template_data = frappe.get_attr("frappe.email.doctype.email_template.email_template.get_email_template")(
		template_name=template,
		doc=frappe.as_json(pe_dict),
	)

	if not template_data:
		frappe.throw(_("Could not render email template"))

	frappe.get_attr("frappe.core.doctype.communication.email.make")(
		doctype="Payment Entry",
		name=payment_entry.name,
		recipients=email,
		subject=template_data.get("subject"),
		content=template_data.get("message"),
		send_email=1,
		print_format="Remittance advise",
		print_letterhead=1,
		print_language="en",
		add_css=1,
	)
