// Copyright (c) 2025, frappe.dev@arus.co.in and contributors
// For license information, please see license.txt

let reporting_period = ""

frappe.ui.form.on("AU BAS Report", {
	refresh(frm) {

		frm.fields_dict["1a_details"].$wrapper.find('.grid-body')
			.css({ 'overflow-y': 'scroll', 'max-height': '200px' })
		frm.fields_dict["1b_details"].$wrapper.find('.grid-body')
			.css({ 'overflow-y': 'scroll', 'max-height': '200px' })
		frm.fields_dict["g1_details"].$wrapper.find('.grid-body')
			.css({ 'overflow-y': 'scroll', 'max-height': '200px' })
		frm.fields_dict["g2_details"].$wrapper.find('.grid-body')
			.css({ 'overflow-y': 'scroll', 'max-height': '200px' })
		frm.fields_dict["g3_details"].$wrapper.find('.grid-body')
			.css({ 'overflow-y': 'scroll', 'max-height': '200px' })
		frm.fields_dict["g4_details"].$wrapper.find('.grid-body')
			.css({ 'overflow-y': 'scroll', 'max-height': '200px' })
		frm.fields_dict["g10_details"].$wrapper.find('.grid-body')
			.css({ 'overflow-y': 'scroll', 'max-height': '200px' })
		frm.fields_dict["g11_details"].$wrapper.find('.grid-body')
			.css({ 'overflow-y': 'scroll', 'max-height': '200px' })
		frm.fields_dict["g14_details"].$wrapper.find('.grid-body')
            .css({ 'overflow-y' : 'scroll', 'max-height' : '200px' })


		if (frm.is_new()) {
		}
		else {
			frm.trigger("update_reporting_period")
			frm.add_custom_button(__("Update BAS Data"), () => {
				frappe.dom.freeze()
				// frappe.show_alert({ message:__("You'll be notified once the bas report is done"), indicator:'green' }, 5);
				frappe.call({
					method: "erpnext_australian_localisation.erpnext_australian_localisation.doctype.au_bas_report.au_bas_report.get_gst",
					args: {
						name : frm.doc.name,
						company: frm.doc.company,
						start_date: frm.doc.start_date,
						end_date: frm.doc.end_date
					},
					callback: function () {
						// frappe.show_alert({ message:__("You'll be notified once the bas report is done"), indicator:'green' }, 5);
						frappe.dom.unfreeze()
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
				frappe.throw("Please set reporting period in <a href='/app/au-localisation-settings/AU Localisation Settings' > ERPNext Australian Settings </a>")
			}
			else if (reporting_period) {
				if (reporting_period === "Monthly") {
					await frm.set_value("start_date", moment(frm.doc.start_date).startOf("month").format())
						.then((e) => {
							if (e === null) {
								frappe.msgprint("Start date is changed to " + moment(frm.doc.start_date).format('DD-MM-YY') + " to keep it in line with the " + reporting_period + " BAS setup")

							}
						})
					frm.set_value("end_date", moment(frm.doc.start_date).endOf("month").format())
				}
				else if (reporting_period === "Quarterly") {
					frappe.call({
						method: "erpnext_australian_localisation.erpnext_australian_localisation.doctype.au_bas_report.au_bas_report.get_quaterly_start_end_date",
						args: {
							"start_date": frm.doc.start_date
						},
						callback: async function (data) {
							await frm.set_value("start_date", data.message[0])
								.then((e) => {
									if (e === null) {
										frappe.msgprint("Start date is changed to " + moment(frm.doc.start_date).format('DD-MM-YY') + " to keep it in line with the " + reporting_period + " BAS setup")

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
		let brp = au_localisation_settings.bas_reporting_period
		reporting_period = ""
		for (let i = 0; i < brp.length; i++) {
			if (brp[i].company === frm.doc.company) {
				reporting_period = brp[i].reporting_period;
				break;
			}
		}
	}
});
