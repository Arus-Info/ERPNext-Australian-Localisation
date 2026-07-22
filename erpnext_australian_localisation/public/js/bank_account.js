frappe.ui.form.on("Bank Account", {
	refresh(frm) {
		if (!frm.doc.enable_transaction_import) {
			return;
		}

		const fetch_account_btn = frm.add_custom_button(__("Fetch Account ID"), () => {
			if (frm.__fetching_provider_accounts) {
				return;
			}
			frm.__fetching_provider_accounts = true;
			fetch_account_btn.prop("disabled", true);

			frappe.call({
				method: "erpnext_australian_localisation.integration.import_transaction.get_provider_accounts",

				callback(r) {
					const accounts = r.message || [];
					if (!accounts.length) {
						frappe.msgprint(__("No accounts found"));
						return;
					}
					show_provider_account_dialog(frm, accounts);
				},

				always() {
					frm.__fetching_provider_accounts = false;
					fetch_account_btn.prop("disabled", false);
				},
			});
		});

		const sync_now_btn = frm.add_custom_button(__("Sync Now"), () => {
			if (frm.__syncing_account_transactions) {
				return;
			}
			frm.__syncing_account_transactions = true;
			sync_now_btn.prop("disabled", true);

			frappe.call({
				method: "erpnext_australian_localisation.integration.import_transaction.sync_account_transactions",
				args: { bank_account: frm.doc.name },

				callback(r) {
					frappe.msgprint({
						title: __("Sync Complete"),
						message: r.message || __("Transactions Imported"),
						indicator: "green",
					});
					frm.reload_doc();
				},

				always() {
					frm.__syncing_account_transactions = false;
					sync_now_btn.prop("disabled", false);
				},
			});
		});
	},

	enable_transaction_import(frm) {
		frm.refresh();
	},
});

function show_provider_account_dialog(frm, accounts) {
	const rows = accounts
		.map(
			(account, i) => `
				<tr data-value="${frappe.utils.escape_html(account.id)}">
					<td style="width: 40px; text-align: center;">
						<input type="radio" name="provider_account" value="${frappe.utils.escape_html(account.id)}" ${
				i === 0 ? "checked" : ""
			}>
					</td>
					<td>${frappe.utils.escape_html(account.name || "")}<br><small class="text-muted">${frappe.utils.escape_html(account.display_name || "")}</small></td>
					<td>${frappe.utils.escape_html(account.account_no || "")}</td>
					<td>${frappe.utils.escape_html(account.id || "")}</td>
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
				`,
			},
		],
		primary_action_label: __("OK"),
		primary_action() {
			const selected = dialog.$wrapper.find('input[name="provider_account"]:checked').val();
			frm.set_value("provider_account_id", selected);
			dialog.hide();
		},
	});

	dialog.$wrapper.find("tbody tr").on("click", function () {
		$(this).find('input[type="radio"]').prop("checked", true);
	});

	dialog.show();
}
