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
				filters: {
					company: frm.doc.company,
				},
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
						company: frm.doc.company,
					},
					get_query_method:
						"erpnext_australian_localisation.erpnext_australian_localisation.doctype.payment_batch.payment_batch.get_payment_entry",
				});
			},
			__("Get Items From")
		);

		if (frm.doc.payment_created.length) {
			frm.add_custom_button(
				__("Generate Bank File"),
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
		}

		if (frm.doc.bank_file_url) {
			frm.add_custom_button(
				__("<a style='padding-left: 8px' href={0}>Downloading Bank File</a>", [
					frm.doc.bank_file_url,
				]),
				() => null,
				"Bank File"
			);
		}
	},

	update_total_paid_amount(frm) {
		let total_paid_amount = 0;
		for (let i = 0; i < frm.doc.payment_created.length; i++) {
			total_paid_amount += frm.doc.payment_created[i].amount;
		}
		frm.set_value("total_paid_amount", total_paid_amount);
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
	payment_created_remove(frm) {
		frm.trigger("update_total_paid_amount");
	},
});
