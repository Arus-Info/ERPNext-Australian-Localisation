frappe.ui.form.on("Supplier", {
	country(frm) {
		frm.set_value("is_allowed_in_pp", frm.doc.country === "Australia" ? 1 : 0);
	},
});
