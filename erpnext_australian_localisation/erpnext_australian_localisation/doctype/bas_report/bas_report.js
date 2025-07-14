// Copyright (c) 2025, frappe.dev@arus.co.in and contributors
// For license information, please see license.txt

let reporting_period = ""

frappe.ui.form.on("BAS Report", {
	refresh(frm) {

		if (frm.is_new()) {
		}
		else {
			frm.trigger("update_reporting_period")
			frm.add_custom_button(__("Update BAS Data"), () => {
				frappe.call({
					method: "erpnext_australian_localisation.erpnext_australian_localisation.doctype.bas_report.bas_report.get_gst",
					args: {
						company: frm.doc.company,
						start_date: frm.doc.start_date,
						end_date: frm.doc.end_date
					},
					callback: function (data) {
						console.log(data.message)
					}
				})
			})
		}
	},
	company(frm) {
		frm.trigger("update_reporting_period")
		frm.trigger("update_end_date")
	},

	start_date(frm) {
		frm.trigger("update_end_date")
	},

	update_end_date: async function (frm) {
		if (frm.doc.start_date && frm.doc.company) {
			if (!reporting_period) {
				frappe.throw("Please set reporting period in <a href='/app/australian-localisation-settings/Australian Localisation Settings' > ERPNext Australian Settings </a>")
			}
			else if (reporting_period) {
				if (reporting_period === "Monthly") {
					await frm.set_value("start_date", moment(frm.doc.start_date).startOf("month").format())
						.then((e) => {
							if (e === null) {
								frappe.msgprint("Start date is changed to " + frm.doc.start_date + " to keep it in line with the " + reporting_period + " BAS setup")

							}
						})
					frm.set_value("end_date", moment(frm.doc.start_date).endOf("month").format())
				}
				else if (reporting_period === "Quarterly") {
					frappe.call({
						method: "erpnext_australian_localisation.erpnext_australian_localisation.doctype.bas_report.bas_report.get_quaterly_start_end_date",
						args: {
							"start_date": frm.doc.start_date
						},
						callback: async function (data) {
							await frm.set_value("start_date", data.message[0])
								.then((e) => {
									if (e === null) {
										frappe.msgprint("Start date is changed to " + frm.doc.start_date + " to keep it in line with the " + reporting_period + " BAS setup")

									}
								})
							frm.set_value("end_date", data.message[1])
						}
					})
				}
			}
		}
		else {
			frm.set_value("end_date", "")
		}
	},

	update_reporting_period(frm) {
		let brp = australian_localisation_settings.bas_reporting_period
		for (let i = 0; i < brp.length; i++) {
			if (brp[i].company === frm.doc.company) {
				reporting_period = brp[i].reporting_period;
				break;
			}
		}
	}

});
