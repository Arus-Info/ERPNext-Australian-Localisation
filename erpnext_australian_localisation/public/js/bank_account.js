frappe.ui.form.on("Bank Account", {
	refresh(frm) {
		if (!frm.doc.enable_transaction_import) {
			return;
		}

		frm.set_df_property("last_sync", "read_only", frm.doc.last_sync ? 1 : 0);

		if (!frm.is_new()) {
			const sync_now_btn = frm.add_custom_button(__("Sync Now"), () => {
				sync_now_btn.prop("disabled", true);

				frappe.call({
					method: "erpnext_australian_localisation.integration.basiq.import_transaction.sync_account_transactions",
					args: {
						bank_account: frm.doc.name,
						provider_account_id: frm.doc.provider_account_id,
						sync_date: frm.doc.last_sync
					},

					callback(r) {
						frappe.msgprint({
							title: __("Sync Complete"),
							message: r.message || __("Transactions Imported"),
							indicator: "green"
						});
						frm.reload_doc();
					},

					always() {
						sync_now_btn.prop("disabled", false);
					}
				});
			});
		}
	},

	enable_transaction_import(frm) {
		frm.refresh();
	},

	validate(frm) {
		if (!frm.doc.enable_transaction_import || frm.doc.provider_account_id) {
			return;
		}

		frappe.validated = false;
		fetch_provider_accounts(frm);
	}
});

function fetch_provider_accounts(frm) {
	frappe.call({
		method: "erpnext_australian_localisation.integration.basiq.import_transaction.get_provider_accounts",

		callback(r) {
			const accounts = r.message || [];
			if (!accounts.length) {
				frappe.msgprint(__("No accounts found"));
				return;
			}

			const rows = accounts
				.map(
					(account, i) => `
						<tr data-value="${account.id}">
							<td style="width: 40px; text-align: center;">
								<input type="radio" name="provider_account" value="${account.id}" ${i === 0 ? "checked" : ""}>
							</td>
							<td>${account.name}
								<br><small class="text-muted">${account.display_name}</small>
							</td>
							<td>${account.account_no}</td>
							<td>${account.id}</td>
						</tr>`
				)
				.join("");

			const dialog = new frappe.ui.Dialog({
				title: __("Select Account"),
				size: "large",
				fields: [
					{
						fieldname: "accounts_html",
						fieldtype: "HTML",
						options: `
							<table class="table table-bordered">
								<thead>
									<tr>
										<th></th>
										<th>${__("Name")}</th>
										<th>${__("Account No")}</th>
										<th>${__("Account ID")}</th>
									</tr>
								</thead>
								<tbody>${rows}</tbody>
							</table>
						`
					}
				],
				primary_action_label: __("OK"),
				primary_action() {
					const selected = dialog.$wrapper
						.find('input[name="provider_account"]:checked')
						.val();
					frm.set_value("provider_account_id", selected).then(() => {
						dialog.hide();
						frm.save();
					});
				}
			});

			dialog.show();
		}
	});
}
