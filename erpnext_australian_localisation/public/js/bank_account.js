frappe.ui.form.on("Bank Account", {
	refresh(frm) {
			frm.add_custom_button(__("Sync Now"), () => {
				frappe.call({
					method: "erpnext_australian_localisation.erpnext_australian_localisation.integration.import_transaction.fetch_transactions",
					callback(r) {
						frappe.msgprint({
							title: __("Sync Complete"),
							message: r.message || __("Transactions Imported"),
							indicator: "green",
						});
						frm.reload_doc();
					},
				});
			});
			},
});
