frappe.ui.form.on("Employee", {
	bank_ac_no(frm) {
		const account_number = frm.doc.bank_ac_no || "";

		if (account_number.length === 10) {
			frm.set_df_property(
				"bank_ac_no",
				"description",
				__("10 digit bank account numbers will not be supported for abn file generation.")
			);
		} else {
			frm.set_df_property("bank_ac_no", "description", "");
		}
	}
});
