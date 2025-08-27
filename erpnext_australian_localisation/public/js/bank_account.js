frappe.ui.form.on("Bank Account", {
	refresh(frm) {
		frappe.db.get_value("Company", frm.doc.company, "country").then((data) => {
			if (data.message.country === "Australia") {
				// validate_bank_details(frm);
				// validate_apca_number(frm);
			}
		});
	},
});
