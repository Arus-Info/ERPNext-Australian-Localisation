// Copyright (c) 2025, frappe.dev@arus.co.in and contributors
// For license information, please see license.txt

frappe.ui.form.on("AU Localisation Settings", {
	refresh(frm) {
		let rp = frm.doc.bas_reporting_period;
		for (let i = 0; i < rp.length; i++) {
			frappe.call({
				method: "erpnext_australian_localisation.erpnext_australian_localisation.doctype.au_localisation_settings.au_localisation_settings.is_draft",
				args: {
					company: rp[i].company
				},
				callback: (r) => {
					frappe.meta.get_docfield(
						rp[i].doctype,
						"reporting_period",
						rp[i].name
					).read_only = r.message;
					frappe.meta.get_docfield(
						rp[i].doctype,
						"reporting_method",
						rp[i].name
					).read_only = r.message;
				}
			});
		}

		frm.set_query("company", "bas_reporting_period", () => {
			return {
				filters: { country: "Australia" }
			};
		});

		disable_connected_accounts_row_actions(frm);

		set_email_template_notice(frm);
	},

	make_tax_category_mandatory(frm) {
		if (!frm.doc.make_tax_category_mandatory) {
			frappe.confirm(
				"Please make a note that Unticking this option may lead to mismatch in BAS Report generation. Do you confirm to make Tax Category Optional ?",
				() => {},
				() => {
					frm.set_value("make_tax_category_mandatory", 1);
				}
			);
		}
	},

	after_save(frm) {
		// sets latest values in frappe.boot for current user
		// other users will still need to refresh page
		Object.assign(au_localisation_settings, frm.doc);
	}
});

async function set_email_template_notice(frm) {
	if (!frappe.boot.versions.crm) {
		return;
	}

	const { message: disabled } = await frappe.call({
		method: "erpnext_australian_localisation.erpnext_australian_localisation.doctype.au_localisation_settings.au_localisation_settings.get_disabled_email_templates"
	});

	if (!disabled?.length) {
		frm.set_df_property("remittance_advice_template", "description", "");
		return;
	}

	frm.set_df_property(
		"remittance_advice_template",
		"description",
		`If  ${frappe.utils.comma_and(disabled)} is not seen in the list of Email Templates,
		<a href="#" class="enable-email-templates">Click Here</a> to see.`
	);

	frm.get_field("remittance_advice_template")
		.$wrapper.off("click", ".enable-email-templates")
		.on("click", ".enable-email-templates", async function (e) {
			e.preventDefault();

			await frappe.call({
				method: "erpnext_australian_localisation.erpnext_australian_localisation.doctype.au_localisation_settings.au_localisation_settings.enable_email_templates",
				freeze: true
			});
			set_email_template_notice(frm);
		});
}

function disable_connected_accounts_row_actions(frm) {
	frm.set_df_property("table_talc", "cannot_add_rows", true);
	frm.set_df_property("table_talc", "cannot_delete_rows", true);
}

const BASIQ_POLL_INTERVAL_MS = 2000;
const BASIQ_MAX_POLL_ATTEMPTS = 60;

frappe.ui.form.on("Connected Accounts", {
	sync_bank(frm, cdt, cdn) {
		show_connection_accounts_dialog(frm, locals[cdt][cdn].connection_id);
	}
});

function show_connection_accounts_dialog(frm, connection_id) {
	frappe.call({
		method: "erpnext_australian_localisation.integration.basiq.import_transaction.get_connection_accounts",
		args: { connection_id },
		callback(r) {
			const accounts = r.message || [];
			if (!accounts.length) {
				return frappe.msgprint(__("No accounts found for this connection"));
			}

			const rows = accounts
				.map(
					(account) => `
						<tr>
							<td>${account.account_name || account.name}</td>
							<td>${account.last_sync ? frappe.datetime.str_to_user(account.last_sync) : __("Never")}</td>
							<td style="text-align: right;">
								<button class="btn btn-xs btn-default sync-account-btn" data-name="${account.name}">${__(
						"Sync"
					)}</button>
							</td>
						</tr>`
				)
				.join("");

			const dialog = new frappe.ui.Dialog({
				title: __("Sync Bank"),
				size: "large",
				fields: [
					{
						fieldname: "accounts_html",
						fieldtype: "HTML",
						options: `
							<table class="table table-bordered">
								<thead><tr><th>${__("Account")}</th><th>${__("Last Sync")}</th><th></th></tr></thead>
								<tbody>${rows}</tbody>
							</table>`
					}
				],
				secondary_action_label: __("Cancel"),
				secondary_action: () => dialog.hide(),
				primary_action_label: __("Sync All"),
				primary_action() {
					dialog.hide();
					start_connection_sync(frm, connection_id);
				}
			});

			dialog.$wrapper.on("click", ".sync-account-btn", function () {
				const bank_account = $(this).attr("data-name");
				dialog.hide();
				start_connection_sync(frm, connection_id, bank_account);
			});

			dialog.show();
		}
	});
}

function start_connection_sync(frm, connection_id, bank_account) {
	frappe.call({
		method: "erpnext_australian_localisation.erpnext_australian_localisation.doctype.connected_accounts.connected_accounts.sync_bank_connection",
		args: { connection_id },
		callback: (r) => {
			const job_id = r.message?.id;
			if (!job_id) {
				return frappe.show_alert({
					message: __("Bank connection refresh initiated"),
					indicator: "green"
				});
			}

			const progress_dialog = new frappe.ui.Dialog({
				title: __("Sync Bank"),
				fields: [
					{
						fieldtype: "HTML",
						fieldname: "progress_msg",
						options: `<p>${__("Refreshing bank connection...")}</p>`
					}
				]
			});
			progress_dialog.get_close_btn().hide();
			progress_dialog.show();

			poll_basiq_sync_job(
				frm,
				job_id,
				progress_dialog,
				0,
				null,
				connection_id,
				bank_account
			);
		}
	});
}

function poll_basiq_sync_job(
	frm,
	job_id,
	progress_dialog,
	attempts,
	submitted_url,
	connection_id,
	bank_account
) {
	frappe.call({
		method: "erpnext_australian_localisation.erpnext_australian_localisation.doctype.connected_accounts.connected_accounts.get_sync_job",
		args: { job_id },
		callback: (r) => {
			const steps = r.message.steps;

			const mfa_step = steps.find(
				(s) => s.title === "mfa-challenge" && ["pending", "in-progress"].includes(s.status)
			);
			const mfa_response_url =
				mfa_step && (mfa_step.result?.links?.response || mfa_step.result?.url);

			if (mfa_step && mfa_response_url !== submitted_url) {
				progress_dialog.hide();
				return show_basiq_mfa_dialog(
					frm,
					job_id,
					mfa_step,
					progress_dialog,
					connection_id,
					bank_account
				);
			}

			const failed_step = steps.find((s) => s.status === "failed");
			if (failed_step) {
				progress_dialog.hide();
				const is_mfa_failure = failed_step.title === "mfa-challenge";
				return frappe.msgprint({
					title: __("Bank Connection Refresh Failed"),
					message: is_mfa_failure
						? __("Incorrect answer. Please try again.")
						: failed_step.result?.detail ||
						  failed_step.result?.title ||
						  __("Unknown error"),
					indicator: "red"
				});
			}

			if (!steps.some((s) => ["pending", "in-progress"].includes(s.status))) {
				return import_bank_transactions(frm, progress_dialog, connection_id, bank_account);
			}

			if (attempts >= BASIQ_MAX_POLL_ATTEMPTS) {
				progress_dialog.hide();
				return frappe.msgprint({
					title: __("Bank Connection Refresh Timed Out"),
					message: __(
						"The bank is taking longer than expected to respond. Please try again later."
					),
					indicator: "orange"
				});
			}

			setTimeout(
				() =>
					poll_basiq_sync_job(
						frm,
						job_id,
						progress_dialog,
						attempts + 1,
						submitted_url,
						connection_id,
						bank_account
					),
				BASIQ_POLL_INTERVAL_MS
			);
		}
	});
}

function import_bank_transactions(frm, progress_dialog, connection_id, bank_account) {
	progress_dialog.fields_dict.progress_msg.$wrapper.html(
		`<p>${__("Importing transactions...")}</p>`
	);

	const finish = (message, indicator) => {
		progress_dialog.hide();
		frappe.show_alert({ message: __(message), indicator });
		frm.reload_doc();
	};

	frappe.call({
		method: "erpnext_australian_localisation.integration.basiq.import_transaction.sync_connection_transactions",
		args: bank_account ? { bank_account } : { connection_id },
		callback: () => finish("Bank connection refreshed and transactions imported", "green"),
		error: () => finish("Bank connection refreshed, but transaction import failed", "orange")
	});
}

function show_basiq_mfa_dialog(frm, job_id, step, progress_dialog, connection_id, bank_account) {
	const result = step.result;
	const response_url = result.links?.response || result.url;
	const is_security_question = result.method === "security-questions" && result.input?.length;
	let submitted = false;

	const fields = [
		{
			fieldtype: "HTML",
			fieldname: "mfa_description",
			options: `<p class="text-muted">${frappe.utils.escape_html(
				result.description || __("Enter the code provided by your bank.")
			)}</p>`
		}
	];

	if (is_security_question) {
		result.input.forEach((question, i) =>
			fields.push({
				fieldtype: "Data",
				fieldname: `mfa_answer_${i}`,
				label: question,
				reqd: 1
			})
		);
	} else {
		fields.push({
			fieldtype: "Data",
			fieldname: "mfa_code",
			label: __("Verification Code"),
			reqd: 1
		});
	}

	const d = new frappe.ui.Dialog({
		title: __("Bank Verification Required"),
		fields,
		primary_action_label: __("Submit"),
		primary_action(values) {
			submitted = true;
			d.hide();

			const mfa_response = is_security_question
				? result.input.map((_, i) => values[`mfa_answer_${i}`])
				: [values.mfa_code];

			frappe.call({
				method: "erpnext_australian_localisation.erpnext_australian_localisation.doctype.connected_accounts.connected_accounts.submit_mfa_response",
				args: { response_url, mfa_response },
				callback: () => {
					progress_dialog.show();
					poll_basiq_sync_job(
						frm,
						job_id,
						progress_dialog,
						0,
						response_url,
						connection_id,
						bank_account
					);
				}
			});
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

	d.show();
}

frappe.ui.form.on("AU BAS Reporting Period", {
	before_bas_reporting_period_remove: async function (frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		await frappe.db
			.get_list("AU BAS Report", {
				filters: { company: row.company }
			})
			.then((data) => {
				if (data.length) {
					frappe.throw(__("Sorry can't delete company"));
				}
			});
	}
});

frappe.tour["AU Localisation Settings"] = [
	{
		fieldname: "make_tax_category_mandatory",
		title: "Make Tax Category Mandatory",
		description:
			"Tax Category field in Supplier, Customer and Item (in Tax tab) Master will be mandatory to get the relevant AU Tax codes Updated",
		position: "Right"
	},
	{
		fieldname: "bas_reporting_period",
		title: "BAS Reporting Period",
		description:
			"BAS reports are configured to generate in a Monthly frequency. This can be changed to Quarterly frequency by changing it here",
		position: "Bottom"
	}
];
