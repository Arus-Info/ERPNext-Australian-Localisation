// Copyright (c) 2025, frappe.dev@arus.co.in and contributors
// For license information, please see license.txt

var is_company_deleted = 0;

frappe.ui.form.on("AU Localisation Settings", {
	refresh(frm) {
		rp = frm.doc.bas_reporting_period
		for (let i = 0; i < rp.length; i++) {
			frappe.call({
				method: "erpnext_australian_localisation.erpnext_australian_localisation.doctype.au_localisation_settings.au_localisation_settings.is_draft",
				args: {
					"company" : rp[i].company
				},
				callback: (r) => {
					frappe.meta.get_docfield(rp[i].doctype, "reporting_period", rp[i].name).read_only =  r.message
				}
			})
		}
	},
	before_save(frm) {
		if (is_company_deleted) {
			frappe.throw("Can't save please refresh the page");
		}
	},
	after_save(frm) {
		// sets latest values in frappe.boot for current user
		// other users will still need to refresh page
		Object.assign(au_localisation_settings, frm.doc);
	},
});


frappe.ui.form.on("AU BAS Reporting Period", {

	before_bas_reporting_period_remove(frm, cdt, cdn) { 
		row = locals[cdt][cdn]
		frappe.db.get_list("AU BAS Report",{
			// "doctype": "AU BAS Report", 
			"filters": { "company": row.company }
		})
			.then((data) => {
				is_company_deleted = 0;
				if (data.length) {
					frappe.show_alert({
						message: __("Sorry can't delete company."),
						indicator: 'red'
					}, 5);
					is_company_deleted = 1
				}
			})
	},
})

frappe.tour['AU Localisation Settings'] = [
	{
		fieldname: "make_tax_category_mandatory",
		title: "Make Tax Category Mandatory",
		description: "If this field is enabled, then Tax Category field in Supplier, Customer and Item (in Tax tab) Master will become mandatory",
		position: "Right"
	}
];