frappe.ui.form.on("Bank Statement Import", {
	refresh(frm) {
		frm.trigger("toggle_import_fields");
	},
	bs_download_template(frm) {
		if (!frm.doc.bank_account) {
			frappe.msgprint(__("Please select Bank Account first"));
			return;
		}
		open_url_post(
			"/api/method/erpnext_australian_localisation.overrides.bank_statement_import.download_uploaded_csv_template",
			{
				bank_account: frm.doc.bank_account,
			}
		);
	},

	toggle_import_fields(frm) {
		//  hide custom field which stores file
		if (frm.is_new()) {
			frm.set_df_property("bs_import_file", "hidden", 1);
			return;
		}

		frappe.db
			.get_value("Bank Account", frm.doc.bank_account, "bank_statement_format")
			.then((r) => {
				const format = r.message.bank_statement_format;

				if (format) {
					// If any bank statement format exists
					frm.set_df_property(
						"bs_import_file",
						"label",
						__("Import File {0}", [format])
					);
					frm.set_df_property("google_sheets_url", "hidden", 1);
					frm.set_df_property("import_file", "hidden", 1);
					frm.set_df_property("html_5", "hidden", 1);
					frm.set_df_property("download_template", "hidden", 1);
					frm.set_df_property("bs_import_file", "hidden", 0);
					frm.set_df_property("bs_download_template", "hidden", 0);
				} else {
					// If no format is set
					frm.set_df_property("google_sheets_url", "hidden", 0);
					frm.set_df_property("import_file", "hidden", 0);
					frm.set_df_property("html_5", "hidden", 0);
					frm.set_df_property("bs_import_file", "hidden", 1);
				}
			});
	},
});
