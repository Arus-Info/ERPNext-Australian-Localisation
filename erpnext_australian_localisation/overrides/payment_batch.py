import frappe
from frappe import _


@frappe.whitelist()
def send_remittance_emails(docname):
	doc = frappe.get_doc("Payment Batch", docname)

	template = frappe.db.get_single_value(
		"AU Localisation Settings",
		"remittance_advice_template",
	)

	if not template:
		frappe.throw(_("Please set a Remittance Email Template in AU Localisation Settings"))

	for row in doc.payment_created or []:
		if not row.party_name:
			continue

		email = frappe.db.get_value(
			"Contact",
			{
				"link_doctype": "Supplier",
				"link_name": row.party_name,
			},
			"email_id",
		)

		if not email:
			continue

		payment_entry = frappe.get_doc("Payment Entry", row.payment_entry)

		pe_dict = payment_entry.as_dict()
		pe_dict["payment_batch"] = doc.as_dict()

		template_data = frappe.get_attr(
			"frappe.email.doctype.email_template.email_template.get_email_template"
		)(
			template_name=template,
			doc=frappe.as_json(pe_dict),
		)

		if not template_data:
			continue

		frappe.get_attr("frappe.core.doctype.communication.email.make")(
			doctype="Payment Entry",
			name=row.payment_entry,
			recipients=email,
			subject=template_data.get("subject"),
			content=template_data.get("message"),
			send_email=1,
			print_format="Remittance advise",
			print_letterhead=1,
			print_language="en",
			add_css=1,
		)

	return True
