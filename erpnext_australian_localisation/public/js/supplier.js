frappe.ui.form.on("Supplier", {
	refresh(frm) {
		console.log("here");
		if (frm.doc.country === "Australia") {
			validate_bank_details(frm);
		}
	},
});
