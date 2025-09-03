frappe.ui.form.on("Item", {
	before_save(frm) {
		if (au_localisation_settings.make_tax_category_mandatory) {
			for (let i = 0; i < frm.doc.taxes.length; i++) {
				if (frm.doc.taxes[i].tax_category) {
					continue;
				} else {
					frappe.throw(__("Tax Catgory Mandatory"));
				}
			}
		}
	},
});

frappe.ui.form.on("Item Tax", {
	async item_tax_template(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		let tax_category = "";
		const { message } = await frappe.db.get_value(
			"Item Tax Template",
			row.item_tax_template,
			"title"
		);
		if (message.title === "GST Exempt Sales") {
			tax_category = "Domestic GST Customer";
		} else if (message.title === "GST Exempt Purchase") {
			tax_category = "Domestic GST Supplier";
		}
		frappe.model.set_value(cdt, cdn, "tax_category", tax_category);
	},
});
