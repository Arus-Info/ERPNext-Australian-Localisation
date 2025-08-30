function validate_branch_code(frm) {
	if (frm.doc.branch_code) {
		let branch_code = frm.doc.branch_code.replace(/-/g, "");
		if (!/^\d+$/.test(branch_code)) {
			frappe.throw(__("Only numbers are allowed in Branch code."));
		}
		if (branch_code.length > 6) {
			frappe.msgprint(__("Removing extra digits. BSB number only has 6 digits"));
		} else if (branch_code.length < 6) {
			frappe.throw(__("Invalid BSB number. BSB must have 6-digits."));
		}
		frm.set_value("branch_code", branch_code.slice(0, 3) + "-" + branch_code.slice(3, 6));
		// frm.set_value("country", "Algeria");
	}
}

function validate_account_no(frm) {
	if (frm.doc.bank_account_no) {
		if (!/^\d{9}$/.test(frm.doc.bank_account_no)) {
			frappe.throw(__("Only 9-digit numbers are allowed in Bank Account Number."));
		}
	}
}
