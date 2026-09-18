frappe.ui.form.on("Bank Account", {
	refresh(frm) {
		if (!frm.doc.enable_transaction_import) {
			return;
		}

		frm.set_df_property("last_sync", "read_only", frm.doc.last_sync ? 1 : 0);
	},

	enable_transaction_import(frm) {
		frm.refresh();
	},

	validate(frm) {
		if (
			!frm.doc.enable_transaction_import ||
			frm.doc.provider_account_id ||
			!au_localisation_settings.enable_open_banking
		) {
			return;
		}

		frappe.validated = false;
		fetch_provider_connections(frm);
	}
});

function fetch_provider_connections(frm) {
	frappe.call({
		method: "erpnext_australian_localisation.integration.basiq.import_transaction.get_provider_connections",
		freeze: true,

		callback(r) {
			const connections = r.message || [];
			if (!connections.length) {
				frappe.msgprint(__("No bank connections found"));
				return;
			}

			const rows = connections
				.map(
					(connection, i) => `
						<tr>
							<td style="width: 40px; text-align: center;">
								<input type="radio" name="provider_connection" value="${connection.id}" ${
						i === 0 ? "checked" : ""
					}>
							</td>
							<td>${connection.institution || connection.id}</td>
						</tr>`
				)
				.join("");

			const dialog = new frappe.ui.Dialog({
				title: __("Select Bank Connection"),
				size: "large",
				fields: [
					{
						fieldname: "connections_html",
						fieldtype: "HTML",
						options: `
							<table class="table table-bordered">
								<thead>
									<tr>
										<th></th>
										<th>${__("Institution")}</th>
									</tr>
								</thead>
								<tbody>${rows}</tbody>
							</table>
						`
					}
				],
				primary_action_label: __("Next"),
				primary_action() {
					const selected = dialog.$wrapper
						.find('input[name="provider_connection"]:checked')
						.val();
					dialog.hide();
					fetch_provider_accounts(frm, selected);
				}
			});

			dialog.show();
		}
	});
}

function fetch_provider_accounts(frm, connection_id) {
	frappe.msgprint(__("Searching for accounts..."));

	frappe.call({
		method: "erpnext_australian_localisation.integration.basiq.import_transaction.get_provider_accounts",
		args: { connection_id },
		freeze: true,

		callback(r) {
			frappe.hide_msgprint(true);

			const accounts = r.message || [];
			if (!accounts.length) {
				frappe.msgprint(__("No accounts found"));
				return;
			}

			const rows = accounts
				.map(
					(account, i) => `
						<tr>
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
					frm.set_value("provider_account_id", selected)
						.then(() => frm.set_value("connection_id", connection_id))
						.then(() => {
							dialog.hide();
							return frm.save();
						})
						.then(() =>
							frappe.call({
								method: "erpnext_australian_localisation.integration.basiq.import_transaction.ensure_connected_account",
								args: { connection_id }
							})
						);
				},
				secondary_action_label: __("Back"),
				secondary_action() {
					dialog.hide();
					fetch_provider_connections(frm);
				}
			});

			dialog.show();
		}
	});
}
