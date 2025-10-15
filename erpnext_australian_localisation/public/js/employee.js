frappe.ui.form.on("Employee", {
	before_save(frm) {
		validate_branch_code(frm); // eslint-disable-line no-undef
		validate_account_no(frm); // eslint-disable-line no-undef
	},
});
