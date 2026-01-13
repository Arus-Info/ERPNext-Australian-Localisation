frappe.ui.form.on("Bank Statement Import", {
	refresh(frm) {
		frm.trigger("toggle_import_fields");
	},
	bank_account(frm) {
		// Do NOT show bs_import_file immediately
		frm.trigger("toggle_import_fields");
	},
	after_save(frm) {
		// Re-evaluate AFTER save
		frm.trigger("toggle_import_fields");
	},
	bs_download_template(frm) {
		if (!frm.doc.bank_account) {
			frappe.msgprint(__("Please select Bank Account first"));
			return;
		}

		frappe.call({
			method: "erpnext_australian_localisation.overrides.bank_statement_import.download_uploaded_csv_template",
			args: {
				bank_account: frm.doc.bank_account,
			},
			callback(r) {
				if (!r.message) return;

				const blob = new Blob([r.message.filecontent], {
					type: "text/csv;charset=utf-8;",
				});

				const link = document.createElement("a");
				link.href = URL.createObjectURL(blob);
				link.download = r.message.filename;
				link.click();
			},
		});
	},
	toggle_import_fields(frm) {
		// If bank not selected → hide everything
		if (!frm.doc.bank_account) {
			frm.set_df_property("bs_import_file", "hidden", 1);
			return;
		}

		// If document NOT saved yet → hide custom field
		if (frm.is_new()) {
			frm.set_df_property("bs_import_file", "hidden", 1);
			return;
		}

		frappe.db.get_doc("Bank Account", frm.doc.bank_account).then((bank) => {
			if (
				bank.bank_statement_format === "NAB CSV Format" ||
				bank.bank_statement_format === "Commonwealth Bank CSV Format" ||
				bank.bank_statement_format === "Westpac CSV Format" ||
				bank.bank_statement_format === "ANZ CSV Format"
			) {
				frm.set_df_property("google_sheets_url", "hidden", 1);
				frm.set_df_property("import_file", "hidden", 1);
				frm.set_df_property("html_5", "hidden", 1);
				frm.set_df_property("download_template", "hidden", 1);
				frm.set_df_property("bs_import_file", "hidden", 0);
				frm.set_df_property("bs_download_template", "hidden", 0);
			} else {
				frm.set_df_property("google_sheets_url", "hidden", 0);
				frm.set_df_property("import_file", "hidden", 0);
				frm.set_df_property("html_5", "hidden", 0);
				frm.set_df_property("bs_import_file", "hidden", 1);
			}
		});
	},
});
