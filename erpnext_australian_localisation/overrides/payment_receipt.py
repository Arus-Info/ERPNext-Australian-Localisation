import frappe
from frappe import _


@frappe.whitelist()
def send_payment_receipt(docname):
	doc = frappe.get_doc("Payment Entry", docname)

	template = frappe.db.get_single_value("AU Localisation Settings", "payment_receipt_template")
	if not template:
		frappe.throw(_("Please set a Payment Receipt Template in AU Localisation Settings"))

	email = frappe.db.get_value(
		"Contact",
		{
			"link_doctype": "Customer",
			"link_name": doc.party_name,
		},
		"email_id",
	)
	if not email:
		frappe.throw(_("No email found for {0} {1}").format(doc.party_type, doc.party))

	payment_entry = frappe.get_doc("Payment Entry", doc.name)

	template_data = frappe.get_attr("frappe.email.doctype.email_template.email_template.get_email_template")(
		template_name=template,
		doc=frappe.as_json(payment_entry),
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
def send_remittance_email(docname):
	doc = frappe.get_doc("Payment Entry", docname)

	template = frappe.db.get_single_value("AU Localisation Settings", "remittance_advice_template")
	if not template:
		frappe.throw(_("Please set a Payment Receipt Template in AU Localisation Settings"))

	email = frappe.db.get_value(
		"Contact",
		{
			"link_doctype": "Supplier",
			"link_name": doc.party_name,
		},
		"email_id",
	)
	if not email:
		frappe.throw(_("No email found for {0} {1}").format(doc.party_type, doc.party))

	payment_entry = frappe.get_doc("Payment Entry", doc.name)

	pe_dict = payment_entry.as_dict()
	pe_dict["payment_batch"] = doc.as_dict()

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
