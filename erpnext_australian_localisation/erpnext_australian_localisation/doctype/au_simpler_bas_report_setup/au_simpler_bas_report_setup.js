// Copyright (c) 2025, frappe.dev@arus.co.in and contributors
// For license information, please see license.txt

frappe.ui.form.on("AU Simpler BAS Report Setup", {
	refresh(frm) {
		frm.set_query("account", "accounts_g1", () => {
			return {
				filters: {
					company: frm.doc.company,
					account_type: "Income Account",
				},
			};
		});
		frm.set_query("account_1a", () => {
			return {
				filters: {
					company: frm.doc.company,
					account_type: "Tax",
				},
			};
		});
		frm.set_query("account_1b", () => {
			return {
				filters: {
					company: frm.doc.company,
					account_type: "Tax",
				},
			};
		});
	},
	before_save(frm) {
		if (frm.doc.account_1a === frm.doc.account_1b) {
			frappe.throw(__("1A and 1B can't be reported in the same account"));
		}
	},
});
