frappe.ui.form.on("Supplier", {
	before_save(frm) {
		if (frm.doc.country === "Australia") {
			validate_branch_code(frm); // eslint-disable-line no-undef
			validate_account_no(frm); // eslint-disable-line no-undef
		}
	},

	// branch_code(frm) {
	// 	if (frm.doc.country === "Australia") {
	// 		validate_branch_code(frm); // eslint-disable-line no-undef
	// 	}
	// },

	// bank_account_no(frm) {
	// 	if (frm.doc.country === "Australia") {
	// 		validate_account_no(frm); // eslint-disable-line no-undef
	// 	}
	// },
});
