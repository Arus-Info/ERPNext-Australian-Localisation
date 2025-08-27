// Copyright (c) 2025, frappe.dev@arus.co.in and contributors
// For license information, please see license.txt

frappe.ui.form.on("Payment Batch", {
	refresh(frm) {
		$('[data-fieldname="payment_created"]').find(".grid-add-row").hide();
		$('[data-fieldname="paid_invoices"]').find(".grid-add-row").hide();
		$('[data-fieldname="paid_invoices"]').find(".grid-remove-rows").hide();
		frm.get_field("payment_created").grid.cannot_add_rows = true;
		frm.get_field("paid_invoices").grid.cannot_add_rows = true;

		frm.set_query("bank_account", () => {
			return {
				query: "erpnext_australian_localisation.erpnext_australian_localisation.doctype.payment_batch.payment_batch.get_bank_account",
			};
		});

		frm.add_custom_button(
			__("Payment Entry"),
			function () {
				erpnext.utils.map_current_doc({
					method: "erpnext_australian_localisation.erpnext_australian_localisation.doctype.payment_batch.payment_batch.update_payment_batch",
					source_doctype: "Payment Entry",
					target: frm,
					setters: {
						party: "",
						paid_amount: 0,
					},
					get_query_filters: {
						docstatus: 0,
					},
					get_query_method:
						"erpnext_australian_localisation.erpnext_australian_localisation.doctype.payment_batch.payment_batch.get_payment_entry",
				});
			},
			__("Get Items From")
		);

		frm.add_custom_button(
			"Generate Bank File",
			function () {
				frappe.call({
					doc: frm.doc,
					method: "generate_bank_file",
					callback: (url) => {
						frappe.msgprint(
							__(
								"Bank File Generated. Click <a href={0}>here</a> to download the file.",
								[url.message]
							)
						);
					},
				});
			},
			"Bank File"
		);

		frm.add_custom_button(
			`<a style='padding-left: 8px' href=${frm.doc.bank_file_url}>Downloading Bank File</a>`,
			() => null,
			"Bank File"
		);
	},
});

frappe.ui.form.on("Payment Batch Item", {
	before_payment_created_remove(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		for (let i = frm.doc.paid_invoices.length - 1; i >= 0; i--) {
			if (row.payment_entry === frm.doc.paid_invoices[i].payment_entry)
				frm.get_field("paid_invoices").grid.grid_rows[i].remove();
		}
	},
});
