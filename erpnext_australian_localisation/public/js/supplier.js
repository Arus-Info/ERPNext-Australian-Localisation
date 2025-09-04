frappe.ui.form.on("Supplier", {
	before_save(frm) {
		if (frm.doc.country === "Australia") {
			validate_branch_code(frm); // eslint-disable-line no-undef
			validate_account_no(frm); // eslint-disable-line no-undef
		}
	},

	country(frm) {
		frm.set_value("is_allowed_in_pp", frm.doc.country === "Australia" ? 1 : 0);
	},
});
