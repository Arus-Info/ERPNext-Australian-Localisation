frappe.ui.form.on("Bank Account", {
	refresh(frm) {
		if (!frm.doc.enable_transaction_import) {
			return;
		}

		frm.set_df_property("last_sync", "read_only", frm.doc.last_sync ? 1 : 0);

		if (
			!frm.is_new() &&
			!frm.doc.disabled &&
			frm.doc.connection_id &&
			frm.doc.provider_account_id &&
			au_localisation_settings.enable_open_banking
		) {
			frm.add_custom_button(__("Sync"), () => show_connection_accounts_dialog(frm));
		}
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

const IMPORT_TRANSACTION = "erpnext_australian_localisation.integration.basiq.import_transaction";
const BASIQ_CONNECTOR = "erpnext_australian_localisation.integration.basiq.basiq_connector";
const BASIQ_POLL_INTERVAL_MS = 2000;
const BASIQ_MAX_POLL_ATTEMPTS = 60;

// rows: [{ value, cells: [html, ...] }], every row starts selected for checkboxes, only the first for radios
function selection_table(input_type, headers, rows) {
	const header_cell =
		input_type === "checkbox" ? `<input type="checkbox" class="select-all" checked>` : "";

	const body = rows
		.map(
			(row, i) => `
				<tr>
					<td style="width: 40px; text-align: center;">
						<input type="${input_type}" name="selection" class="selection"
							value="${frappe.utils.escape_html(row.value)}"
							${input_type === "checkbox" || i === 0 ? "checked" : ""}>
					</td>
					${row.cells.map((cell) => `<td>${cell}</td>`).join("")}
				</tr>`
		)
		.join("");

	return `
		<table class="table table-bordered">
			<thead>
				<tr>
					<th style="width: 40px; text-align: center;">${header_cell}</th>
					${headers.map((header) => `<th>${header}</th>`).join("")}
				</tr>
			</thead>
			<tbody>${body}</tbody>
		</table>`;
}

function selection_dialog({ title, input_type = "radio", headers, rows, ...dialog_options }) {
	const dialog = new frappe.ui.Dialog({
		title,
		size: "large",
		fields: [
			{
				fieldname: "selection_html",
				fieldtype: "HTML",
				options: selection_table(input_type, headers, rows)
			}
		],
		...dialog_options
	});

	const $inputs = dialog.$wrapper.find(".selection");
	const $select_all = dialog.$wrapper.find(".select-all");
	$select_all.on("change", function () {
		$inputs.prop("checked", this.checked);
	});
	$inputs.on("change", () => {
		$select_all.prop("checked", $inputs.length === $inputs.filter(":checked").length);
	});

	dialog.get_selected = () =>
		$inputs
			.filter(":checked")
			.map((_, el) => el.value)
			.get();

	dialog.show();
	return dialog;
}

const escape_html = (value) => frappe.utils.escape_html(value || "");

function fetch_provider_connections(frm) {
	frappe.call({
		method: `${IMPORT_TRANSACTION}.get_provider_connections`,
		freeze: true,
		callback(r) {
			const connections = r.message || [];
			if (!connections.length) {
				return frappe.msgprint(__("No bank connections found"));
			}

			const dialog = selection_dialog({
				title: __("Select Bank Connection"),
				headers: [__("Institution"), __("Account Holder")],
				rows: connections.map((connection) => ({
					value: connection.id,
					cells: [
						escape_html(connection.institution || connection.id),
						escape_html(connection.account_holder)
					]
				})),
				primary_action_label: __("Next"),
				primary_action() {
					dialog.hide();
					fetch_provider_accounts(frm, dialog.get_selected()[0]);
				}
			});
		}
	});
}

function fetch_provider_accounts(frm, connection_id) {
	frappe.call({
		method: `${IMPORT_TRANSACTION}.get_provider_accounts`,
		args: { connection_id },
		freeze: true,
		freeze_message: __("Searching for accounts..."),
		callback(r) {
			const accounts = r.message || [];
			if (!accounts.length) {
				return frappe.msgprint(__("No accounts found"));
			}

			const dialog = selection_dialog({
				title: __("Select Account"),
				headers: [__("Name"), __("Account No"), __("Account ID")],
				rows: accounts.map((account) => ({
					value: account.id,
					cells: [
						`${escape_html(account.name)}<br><small class="text-muted">${escape_html(
							account.display_name
						)}</small>`,
						escape_html(account.account_no),
						escape_html(account.id)
					]
				})),
				primary_action_label: __("OK"),
				primary_action() {
					const account = accounts.find((a) => a.id === dialog.get_selected()[0]);
					frm.set_value({
						provider_account_id: account.id,
						provider_account_name: account.name,
						connection_id
					}).then(() => {
						dialog.hide();
						return frm.save();
					});
				},
				secondary_action_label: __("Back"),
				secondary_action() {
					dialog.hide();
					fetch_provider_connections(frm);
				}
			});
		}
	});
}

function show_connection_accounts_dialog(frm) {
	frappe.call({
		method: `${IMPORT_TRANSACTION}.get_connection_accounts`,
		args: { connection_id: frm.doc.connection_id },
		callback(r) {
			const accounts = r.message || [];
			if (!accounts.length) {
				return frappe.msgprint(__("No accounts found for this connection"));
			}

			const dialog = selection_dialog({
				title: __("Sync Bank Accounts"),
				input_type: "checkbox",
				headers: [__("Account"), __("Last Sync")],
				rows: accounts.map((account) => ({
					value: account.name,
					cells: [
						`${escape_html(
							account.account_name || account.name
						)}<br><small class="text-muted">${escape_html(account.bank)}</small>`,
						frappe.datetime.str_to_user(account.last_sync)
					]
				})),
				primary_action_label: __("Sync"),
				primary_action() {
					const bank_accounts = dialog.get_selected();
					if (!bank_accounts.length) {
						return frappe.msgprint(__("Please select at least one account to sync"));
					}

					dialog.hide();
					sync_connection(frm, bank_accounts);
				},
				secondary_action_label: __("Cancel"),
				secondary_action: () => dialog.hide()
			});
		}
	});
}

function sync_connection(frm, bank_accounts) {
	const connection_id = frm.doc.connection_id;

	const progress_dialog = new frappe.ui.Dialog({
		title: __("Sync Bank Accounts"),
		fields: [{ fieldtype: "HTML", fieldname: "progress_msg" }]
	});
	progress_dialog.get_close_btn().hide();

	const show_progress = (message) => {
		progress_dialog.fields_dict.progress_msg.$wrapper.html(`<p>${message}</p>`);
		progress_dialog.show();
	};

	const fail = (title, message, indicator = "red") => {
		progress_dialog.hide();
		frappe.msgprint({ title, message, indicator });
	};

	const import_transactions = () => {
		show_progress(__("Importing transactions..."));

		const finish = (message, indicator) => {
			progress_dialog.hide();
			frappe.show_alert({ message, indicator });
			frm.reload_doc();
		};

		frappe.call({
			method: `${IMPORT_TRANSACTION}.sync_connection_transactions`,
			args: { connection_id, bank_accounts },
			callback: () =>
				finish(__("Bank connection refreshed and transactions imported"), "green"),
			error: () =>
				finish(__("Bank connection refreshed, but transaction import failed"), "orange")
		});
	};

	// submitted_url is the MFA challenge already answered, so it isn't asked again while Basiq checks it
	const poll = (job_id, attempts = 0, submitted_url = null) => {
		frappe.call({
			method: `${BASIQ_CONNECTOR}.get_job`,
			args: { job_id },
			callback(r) {
				const steps = r.message.steps;
				const is_running = (step) => ["pending", "in-progress"].includes(step.status);

				const mfa_step = steps.find((s) => s.title === "mfa-challenge" && is_running(s));
				const response_url = mfa_step?.result?.links?.response || mfa_step?.result?.url;
				if (mfa_step && response_url !== submitted_url) {
					progress_dialog.hide();
					return show_mfa_dialog(mfa_step.result, response_url, (mfa_response) =>
						frappe.call({
							method: `${BASIQ_CONNECTOR}.submit_mfa_response`,
							args: { response_url, mfa_response },
							callback: () => {
								show_progress(__("Refreshing bank connection..."));
								poll(job_id, 0, response_url);
							}
						})
					);
				}

				const failed_step = steps.find((s) => s.status === "failed");
				if (failed_step) {
					return fail(
						__("Bank Connection Refresh Failed"),
						failed_step.title === "mfa-challenge"
							? __("Incorrect answer. Please try again.")
							: failed_step.result?.detail ||
									failed_step.result?.title ||
									__("Unknown error")
					);
				}

				if (!steps.some(is_running)) {
					return import_transactions();
				}

				if (attempts >= BASIQ_MAX_POLL_ATTEMPTS) {
					return fail(
						__("Bank Connection Refresh Timed Out"),
						__(
							"The bank is taking longer than expected to respond. Please try again later."
						),
						"orange"
					);
				}

				setTimeout(
					() => poll(job_id, attempts + 1, submitted_url),
					BASIQ_POLL_INTERVAL_MS
				);
			}
		});
	};

	frappe.call({
		method: `${BASIQ_CONNECTOR}.refresh_connection`,
		args: { connection_id },
		freeze: true,
		callback(r) {
			show_progress(__("Refreshing bank connection..."));
			poll(r.message.id);
		}
	});
}

function show_mfa_dialog(challenge, response_url, submit) {
	const questions = challenge.method === "security-questions" ? challenge.input || [] : [];
	const fields = [
		{
			fieldtype: "HTML",
			fieldname: "mfa_description",
			options: `<p class="text-muted">${escape_html(
				challenge.description || __("Enter the code provided by your bank.")
			)}</p>`
		},
		...(questions.length
			? questions.map((question, i) => ({
					fieldtype: "Data",
					fieldname: `mfa_answer_${i}`,
					label: question,
					reqd: 1
			  }))
			: [
					{
						fieldtype: "Data",
						fieldname: "mfa_code",
						label: __("Verification Code"),
						reqd: 1
					}
			  ])
	];

	let submitted = false;
	const dialog = new frappe.ui.Dialog({
		title: __("Bank Verification Required"),
		fields,
		primary_action_label: __("Submit"),
		primary_action(values) {
			submitted = true;
			dialog.hide();
			submit(
				questions.length
					? questions.map((_, i) => values[`mfa_answer_${i}`])
					: [values.mfa_code]
			);
		},
		on_hide() {
			if (!submitted) {
				frappe.show_alert({
					message: __("Bank verification cancelled"),
					indicator: "orange"
				});
			}
		}
	});

	dialog.show();
}
