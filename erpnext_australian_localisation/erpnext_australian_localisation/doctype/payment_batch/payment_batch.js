// Copyright (c) 2025, frappe.dev@arus.co.in and contributors
// For license information, please see license.txt
// to open print format
function open_remittance_print(pe_name) {
	// if pe doc loaded ok otherwise fetcrhd from server
	frappe.model.with_doc("Payment Entry", pe_name, function () {
		// loads doctypes metadata
		frappe.model.with_doctype("Payment Entry", function () {
			const f_meta = Object.create(frappe.get_meta("Payment Entry"));
			f_meta.default_print_format = "Remittance Advise";
			frappe.route_options = {
				frm: {
					doctype: "Payment Entry",
					docname: pe_name,
					doc: frappe.get_doc("Payment Entry", pe_name),
					meta: f_meta
				}
			};
			frappe.set_route("print", "Payment Entry", pe_name);
		});
	});
}

frappe.ui.form.on("Payment Batch", {
	refresh(frm) {
		frm.trigger("print_format_view");
		$('[data-fieldname="paid_invoices"]').find(".grid-remove-rows").hide();
		frm.$wrapper.find(".grid-add-row").hide();
		frm.$wrapper.find(".grid-body").css({ "overflow-y": "scroll", "max-height": "400px" });

		frm.set_query("bank_account", () => {
			return {
				filters: [
					["company", "=", frm.doc.company],
					["fi_abbr", "!=", ""],
					["branch_code", "!=", ""],
					["bank_account_no", "!=", ""],
					["apca_number", "!=", ""],
					["currency", "=", "AUD"]
				]
			};
		});

		if (!frm.is_new() && frm.doc.docstatus === 0) {
			frm.add_custom_button(
				__("Payment Entry"),
				() => {
					get_items(frm);
				},
				__("Get Items From")
			);
		}

		if (frm.doc.payment_created.length) {
			frm.add_custom_button(
				__("Generate Bank File"),
				function () {
					if (frm.doc.file_format !== "-None-") {
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
							}
						});
					} else {
						frappe.throw(
							__(
								"Bank file can't be generated. Please set the file format in Bank Account"
							)
						);
					}
				},
				"Bank File"
			);
		}

		if (frm.doc.bank_file_url) {
			frm.add_custom_button(
				__("<a style='padding-left: 8px' href={0}>Download Bank File</a>", [
					frm.doc.bank_file_url
				]),
				() => null,
				"Bank File"
			);
		}

		if (frm.doc.docstatus === 2) {
			frm.add_custom_button(__("Rework Batch"), () => {
				frappe.call({
					method: "erpnext_australian_localisation.erpnext_australian_localisation.doctype.payment_batch.payment_batch.create_payment_batch_again",
					args: {
						doc: frm.doc
					},
					callback: (data) => {
						frappe.set_route("payment-batch", data.message);
					}
				});
			});
		}

		function au_inject_preview() {
			frm.$wrapper
				.find('[data-fieldname="payment_created"] .grid-body .data-row')
				.each(function () {
					const $row = $(this);
					if ($row.find(".btn-preview-pe").length) return;
					const $btn = $(
						'<div class="col grid-static-col au-preview-col" style="flex:0 0 80px;max-width:80px;text-align:center;">' +
							'<button class="btn btn-xs btn-default btn-preview-pe">' +
							__("Preview") +
							"</button>" +
							"</div>"
					);
					$btn.on("click", function (e) {
						e.stopPropagation();
						e.preventDefault();
						const row = frappe.get_doc(
							"Payment Batch Item",
							$row.closest("[data-name]").attr("data-name")
						);
						if (row && row.payment_entry) open_remittance_print(row.payment_entry);
					});
					const $target = $row.find('[data-fieldname="amount"]');
					($target.length ? $target : $row).after($btn);
				});
		}

		setTimeout(au_inject_preview, 0);
		$(frm.wrapper)
			.off("grid-row-render.au_preview")
			.on("grid-row-render.au_preview", function (_e, grid_row) {
				if (grid_row.doctype === "Payment Batch Item") au_inject_preview();
			});
	},
	print_format_view(frm) {
		if (frm.doc.docstatus !== 1) return;

		frm.add_custom_button(__("Send Remittance"), () => {
			frappe.confirm(
				__("Are you sure you want to send the remittance advice PDF to the supplier?"),
				() => {
					frappe.call({
						method: "erpnext_australian_localisation.overrides.payment_batch.send_remittance_emails",
						args: { docname: frm.doc.name },
						freeze: true,
						freeze_message: __("Sending remittance emails..."),
						callback(r) {
							if (r.message) {
								frappe.show_alert({
									message: __("Remittance emails sent successfully"),
									indicator: "green"
								});
							}
						}
					});
				}
			);
		});
	},

	update_total_paid_amount(frm) {
		let total_paid_amount = 0;
		for (let i = 0; i < frm.doc.payment_created.length; i++) {
			total_paid_amount += frm.doc.payment_created[i].amount;
		}
		frm.set_value("total_paid_amount", total_paid_amount);
	}
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
	}
});

function get_items(frm) {
	erpnext.utils.map_current_doc({
		method: "erpnext_australian_localisation.erpnext_australian_localisation.doctype.payment_batch.payment_batch.update_payment_batch",
		source_doctype: "Payment Entry",
		date_field: "posting_date",
		target: frm,
		setters: [
			{
				fieldname: "party_name",
				label: __(frm.doc.type),
				fieldtype: "Data"
			},
			{
				fieldname: "base_paid_amount",
				label: __("Amount"),
				fieldtype: "Currency",
				hidden: 1
			}
		],
		get_query_filters: {
			docstatus: 0,
			company: frm.doc.company,
			bank_account: frm.doc.bank_account,
			party_type: frm.doc.party_type
		},
		get_query_method:
			"erpnext_australian_localisation.erpnext_australian_localisation.doctype.payment_batch.payment_batch.get_payment_entry"
	});

	setTimeout(() => {
		$("[data-fieldname='search_term']").hide();
		$(".filter-area").hide();
	}, 700);
}
