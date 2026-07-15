frappe.ui.form.on("Payment Entry", {
	refresh(frm) {
		if (frm.doc.docstatus !== 1) return;

		if (frm.doc.party_type === "Customer") {
			frm.add_custom_button(__("Send Payment Receipt"), () => {
				frappe.call({
					method: "erpnext_australian_localisation.overrides.payment_receipt.check_party_email",
					args: { docname: frm.doc.name, party_type: "Customer" },
					callback() {
						frappe.confirm(
							__("Send payment receipt email to {0}?", [frm.doc.party]),
							() => {
								frappe.call({
									method: "erpnext_australian_localisation.overrides.payment_receipt.send_payment_receipt",
									args: { docname: frm.doc.name },
									freeze: true,
									freeze_message: __("Sending payment receipt..."),
									callback(r) {
										if (r.message) {
											frappe.show_alert({
												message: __("Payment receipt sent successfully"),
												indicator: "green"
											});
										}
									}
								});
							}
						);
					}
				});
			});
		} else if (frm.doc.party_type === "Supplier") {
			frm.add_custom_button(__("Send Remittance"), () => {
				frappe.call({
					method: "erpnext_australian_localisation.overrides.payment_receipt.check_party_email",
					args: { docname: frm.doc.name, party_type: "Supplier" },
					callback() {
						frappe.confirm(
							__("Send remittance advice email to {0}?", [frm.doc.party]),
							() => {
								frappe.call({
									method: "erpnext_australian_localisation.overrides.payment_receipt.send_remittance_email",
									args: { docname: frm.doc.name },
									freeze: true,
									freeze_message: __("Sending remittance email..."),
									callback(r) {
										if (r.message) {
											frappe.show_alert({
												message: __("Remittance email sent successfully"),
												indicator: "green"
											});
										}
									}
								});
							}
						);
					}
				});
			});
		}
	}
});
