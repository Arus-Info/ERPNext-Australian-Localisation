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
            .css({ 'overflow-y': 'scroll', 'max-height': '200px' })


		if (frm.is_new()) {
			frm.set_df_property("reporting_status", "read_only", 1 )
		}
		else {
			frm.set_df_property("reporting_status", "read_only", 0 )
			frm.trigger("update_reporting_period")
			frm.add_custom_button(__("Update BAS Data"), () => {
				frappe.dom.freeze()
				frappe.call({
					method: "erpnext_australian_localisation.erpnext_australian_localisation.doctype.au_bas_report.au_bas_report.get_gst",
					args: {
						name : frm.doc.name,
						company: frm.doc.company,
						start_date: frm.doc.start_date,
						end_date: frm.doc.end_date
					},
					callback: function () {
						frappe.dom.unfreeze()
						frappe.msgprint("BAS Report Updated")
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


frappe.tour['AU BAS Report'] = [
	{
		fieldname: "company",
		title: "Company Selection",
		description: "Select the company for which BAS Report needs to be generated",
		position: "Right"
	},
	{
		fieldname: "reporting_status",
		title: "Reporting Status Selection",
		description: "Reporting status needs to be \"In Review\" while preparing the Report. BAS Report data can be recalculated till the Reporting Status is set to \"Validated\". Once BAS is lodged then BAS Report can be submitted. ",
		position: "Bottom"
	},
	{
		fieldname: "start_date",
		title: "Start Date Selection",
		description: "The BAS Reporting period start date needs to be selected. The system will update the reporting end date based on the frequency (Monthly/ Quarterly) in the AU Localisation Settings page",
		position: "Right"
	}
]
// bas data can be updated omly in review staut. pls change the stauts baxk toin review for updating the bas data