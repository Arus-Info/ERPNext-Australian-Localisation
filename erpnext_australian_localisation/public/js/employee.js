frappe.ui.form.on("Employee", {
	refresh(frm) {
		set_bank_account_description(frm);
	},

	bank_account_no(frm) {
		set_bank_account_description(frm);
	}
});

function set_bank_account_description(frm) {
	const account_number = frm.doc.bank_account_no || "";

	if (account_number.length === 10) {
		frm.set_df_property(
			"bank_account_no",
			"description",
			__("10 digit bank account numbers will not be supported for abn file generation.")
		);
	} else {
		frm.set_df_property("bank_account_no", "description", "");
	}
}
