frappe.provide("au_localisation.abn");

frappe.ui.form.on("Supplier", {
	country(frm) {
		frm.set_value("is_allowed_in_pp", frm.doc.country === "Australia" ? 1 : 0);
	},
	refresh(frm) {
		au_localisation.abn.setup(frm);
	},

	tax_id(frm) {
		// if (!frm.doc.tax_id) {
		// 	au_localisation.abn.clear_tax_id_fields(frm);
		// }
		if (frm.doc.is_verify_abn) {
			frm._is_abn_changed = true;
		}
	},

	is_verify_abn(frm) {
		frm._last_abn = null;
		frm._is_abn_changed = false;
		au_localisation.abn.handle_blur(frm);
	},

	validate(frm) {
		frm.fields_dict.tax_id.$wrapper.find("input").off("blur");
		if (frm._is_abn_changed) {
			frappe.validated = false;
			frm._last_abn = null;
			au_localisation.abn.handle_blur(frm);
		}
	},
});
