// Copyright (c) 2025, frappe.dev@arus.co.in and contributors
// For license information, please see license.txt

frappe.ui.form.on("AU Localisation Settings", {
	refresh(frm) {
		let rp = frm.doc.bas_reporting_period;
		for (let i = 0; i < rp.length; i++) {
			frappe.call({
				method: "erpnext_australian_localisation.erpnext_australian_localisation.doctype.au_localisation_settings.au_localisation_settings.is_draft",
				args: {
					company: rp[i].company
				},
				callback: (r) => {
					frappe.meta.get_docfield(
						rp[i].doctype,
						"reporting_period",
						rp[i].name
					).read_only = r.message;
					frappe.meta.get_docfield(
						rp[i].doctype,
						"reporting_method",
						rp[i].name
					).read_only = r.message;
				}
			});
		}

		frm.set_query("company", "bas_reporting_period", () => {
			return {
				filters: { country: "Australia" }
			};
		});

		set_email_template_notice(frm);
	},

	make_tax_category_mandatory(frm) {
		if (!frm.doc.make_tax_category_mandatory) {
			frappe.confirm(
				"Please make a note that Unticking this option may lead to mismatch in BAS Report generation. Do you confirm to make Tax Category Optional ?",
				() => {},
				() => {
					frm.set_value("make_tax_category_mandatory", 1);
				}
			);
		}
	},

	after_save(frm) {
		// sets latest values in frappe.boot for current user
		// other users will still need to refresh page
		Object.assign(au_localisation_settings, frm.doc);
	}
});

async function set_email_template_notice(frm) {
	if (!frappe.boot.versions.crm) {
		return;
	}

	const { message: disabled } = await frappe.call({
		method: "erpnext_australian_localisation.erpnext_australian_localisation.doctype.au_localisation_settings.au_localisation_settings.get_disabled_email_templates"
	});

	if (!disabled?.length) {
		frm.set_df_property("remittance_advice_template", "description", "");
		return;
	}

	frm.set_df_property(
		"remittance_advice_template",
		"description",
		`If  ${frappe.utils.comma_and(disabled)} is not seen in the list of Email Templates,
		<a href="#" class="enable-email-templates">Click Here</a> to see.`
	);

	frm.get_field("remittance_advice_template")
		.$wrapper.off("click", ".enable-email-templates")
		.on("click", ".enable-email-templates", async function (e) {
			e.preventDefault();

			await frappe.call({
				method: "erpnext_australian_localisation.erpnext_australian_localisation.doctype.au_localisation_settings.au_localisation_settings.enable_email_templates",
				freeze: true
			});
			set_email_template_notice(frm);
		});
}

frappe.ui.form.on("AU BAS Reporting Period", {
	before_bas_reporting_period_remove: async function (frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		await frappe.db
			.get_list("AU BAS Report", {
				filters: { company: row.company }
			})
			.then((data) => {
				if (data.length) {
					frappe.throw(__("Sorry can't delete company"));
				}
			});
	}
});

frappe.tour["AU Localisation Settings"] = [
	{
		fieldname: "make_tax_category_mandatory",
		title: "Make Tax Category Mandatory",
		description:
			"Tax Category field in Supplier, Customer and Item (in Tax tab) Master will be mandatory to get the relevant AU Tax codes Updated",
		position: "Right"
	},
	{
		fieldname: "bas_reporting_period",
		title: "BAS Reporting Period",
		description:
			"BAS reports are configured to generate in a Monthly frequency. This can be changed to Quarterly frequency by changing it here",
		position: "Bottom"
	}
];
