let country;
frappe.ui.form.on("Bank Account", {
	refresh(frm) {
		if (frm.doc.is_company_account) {
			frappe.db.get_value("Company", frm.doc.company, "country").then((data) => {
				country = data.message.country;
			});
		}
	},

	before_save(frm) {
		if (country === "Australia") {
			validate_branch_code(frm); // eslint-disable-line no-undef
			validate_account_no(frm); // eslint-disable-line no-undef
			validate_apca_number(frm);
		}
	},

	company(frm) {
		if (frm.doc.is_company_account) {
			frappe.db.get_value("Company", frm.doc.company, "country").then((data) => {
				country = data.message.country;
			});
		}
	},

	is_company_account(frm) {
		if (frm.doc.is_company_account) {
			frappe.db.get_value("Company", frm.doc.company, "country").then((data) => {
				country = data.message.country;
			});
		} else {
			country = "";
		}
	},

	// branch_code(frm) {
	// 	if (country === "Australia") {
	// 		validate_branch_code(frm); // eslint-disable-line no-undef
	// 	}
	// },

	// bank_account_no(frm) {
	// 	if (country === "Australia") {
	// 		validate_account_no(frm); // eslint-disable-line no-undef
	// 	}
	// },

	// apca_number(frm) {
	// 	if (country === "Australia") {
	// 		validate_apca_number(frm);
	// 	}
	// },
});

function validate_apca_number(frm) {
	if (frm.doc.apca_number) {
		if (!/^\d{6}$/.test(frm.doc.apca_number)) {
			frappe.throw(__("APCA Number must be exactly 6 digits."));
		}
	}
}
