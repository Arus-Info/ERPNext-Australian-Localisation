frappe.provide("au_localisation.abn");

frappe.ui.form.on("Customer", {
	refresh(frm) {
		au_localisation.abn.setup(frm);
	},

	tax_id(frm) {
		if (!frm.doc.tax_id) {
			frm.trigger("clear_tax_id_fields");
		}
		if (frm.doc.is_verify_abn) {
			frm._is_abn_changed = true;
		}
	},

	is_verify_abn(frm) {
		frm._last_abn = null;
		frm._is_abn_changed = false;
		au_localisation.abn.handle_blur(frm);
	},

	clear_tax_id_fields(frm) {
		frm.set_value({
			entity_name: null,
			business_name: null,
			abn_status: null,
			abn_effective_from: null,
			address_postcode: null,
			address_state: null,
		});
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
