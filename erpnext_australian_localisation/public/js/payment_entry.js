frappe.ui.form.on("Payment Entry", {
	refresh(frm) {
		if (frm.doc.docstatus !== 1) return;

		if (frm.doc.payment_type === "Receive") {
			frm.add_custom_button(__("Send Payment Receipt"), () => {
				frappe.confirm(__("Send payment receipt email to the customer?"), () => {
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
				});
			});
		} else if (frm.doc.payment_type === "Pay") {
			frm.add_custom_button(__("Send Remittance"), () => {
				frappe.confirm(__("Send remittance advice email to the supplier"), () => {
					frappe.call({
						method: "erpnext_australian_localisation.overrides.payment_batch.send_remittance_emails",
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
				});
			});
		}
	}
});
