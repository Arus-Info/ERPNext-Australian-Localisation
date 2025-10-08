frappe.ui.form.on("Bank Account", {
	before_save(frm) {
		if (frm.doc.file_format !== "-None-") {
			validate_branch_code(frm); // eslint-disable-line no-undef
			validate_account_no(frm); // eslint-disable-line no-undef
			validate_apca_number(frm);
			validate_fi_abbr(frm);
		}
	},
});

function validate_apca_number(frm) {
	if (frm.doc.apca_number) {
		if (!/^\d{6}$/.test(frm.doc.apca_number)) {
			frappe.throw(__("APCA Number must be exactly 6 digits."));
		}
	}
}

function validate_fi_abbr(frm) {
	if (frm.doc.fi_abbr) {
		if (!/^[A-Z]{3}$/.test(frm.doc.fi_abbr)) {
			frappe.throw(__("Financial Institution Abbreviation must be three capital letters."));
		}
	}
}
