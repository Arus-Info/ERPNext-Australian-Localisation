const DOCTYPE = cur_frm.doctype

frappe.ui.form.on(DOCTYPE, {
	refresh(frm) {
		$('[data-fieldname="branch_code"').blur(() => {
			if (frm.doc.branch_code) {
				let branch_code = frm.doc.branch_code.replace(/-/g, "")
				if (!(/^\d+$/).test(branch_code)) {
					console.log(branch_code)
					frappe.throw("Only numbers are allowed. ")
				}
				if (branch_code.length > 6) {
					frappe.msgprint("Removing extra digits. BSB number only has 6 digits")
				}
				frm.set_value("branch_code", branch_code.slice(0, 3) + '-' + branch_code.slice(3, 6))
			}
		})
	}
})