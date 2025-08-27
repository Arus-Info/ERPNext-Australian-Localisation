function validate_bank_details(frm) {
	$('[data-fieldname="branch_code"]').blur(() => {
		if (frm.doc.branch_code) {
			let branch_code = frm.doc.branch_code.replace(/-/g, "");
			if (!/^\d+$/.test(branch_code)) {
				console.log(branch_code);
				frappe.throw(__("Only numbers are allowed. "));
			}
			if (branch_code.length > 6) {
				frappe.msgprint(__("Removing extra digits. BSB number only has 6 digits"));
			} else if (branch_code.length < 6) {
				frappe.throw(__("Invalid number. BSB has 6-digits."));
			}
			frm.set_value("branch_code", branch_code.slice(0, 3) + "-" + branch_code.slice(3, 6));
		}
	});

	$('[data-fieldname="bank_account_no"]').blur(() => {
		if (frm.doc.bank_account_no) {
			if (!/^\d{9}$/.test(frm.doc.bank_account_no)) {
				frappe.throw(__("Only 9-digit numbers are allowed."));
			}
		}
	});
}

function validate_apca_number(frm) {
	$('[data-fieldname="apca_number"]').blur(() => {
		if (frm.doc.apca_number) {
			if (!/^\d{6}$/.test(frm.doc.apca_number)) {
				frappe.throw(__("Only numbers are allowed."));
			}
		}
	});
}
