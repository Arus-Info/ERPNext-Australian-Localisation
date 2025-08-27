// Copyright (c) 2025, frappe.dev@arus.co.in and contributors
// For license information, please see license.txt

let reporting_period = "";

frappe.ui.form.on("AU BAS Report", {
	refresh(frm) {
		frm.set_query("company", function () {
			return {
				filters: {
					country: "Australia",
				},
			};
		});

		frm.trigger("update_label");

		frm.fields_dict["1a_details"].$wrapper
			.find(".grid-body")
			.css({ "overflow-y": "scroll", "max-height": "200px" });
		frm.fields_dict["1b_details"].$wrapper
			.find(".grid-body")
			.css({ "overflow-y": "scroll", "max-height": "200px" });
		frm.fields_dict["g1_details"].$wrapper
			.find(".grid-body")
			.css({ "overflow-y": "scroll", "max-height": "200px" });
		frm.fields_dict["g2_details"].$wrapper
			.find(".grid-body")
			.css({ "overflow-y": "scroll", "max-height": "200px" });
		frm.fields_dict["g3_details"].$wrapper
			.find(".grid-body")
			.css({ "overflow-y": "scroll", "max-height": "200px" });
		frm.fields_dict["g4_details"].$wrapper
			.find(".grid-body")
			.css({ "overflow-y": "scroll", "max-height": "200px" });
		frm.fields_dict["g10_details"].$wrapper
			.find(".grid-body")
			.css({ "overflow-y": "scroll", "max-height": "200px" });
		frm.fields_dict["g11_details"].$wrapper
			.find(".grid-body")
			.css({ "overflow-y": "scroll", "max-height": "200px" });
		frm.fields_dict["g14_details"].$wrapper
			.find(".grid-body")
			.css({ "overflow-y": "scroll", "max-height": "200px" });

		if (frm.is_new()) {
			frm.set_df_property("reporting_status", "read_only", 1);
		} else {
			frm.set_df_property("reporting_status", "read_only", 0);
			frm.trigger("update_reporting_period");
			if (frm.doc.docstatus == 0) {
				frm.add_custom_button(__("Update BAS Data"), () => {
					if (frm.doc.reporting_status === "In Review") {
						frappe.realtime.on("bas_data_generator", () => {});
						frappe.call({
							method: "erpnext_australian_localisation.erpnext_australian_localisation.doctype.au_bas_report.au_bas_report.get_gst",
							args: {
								name: frm.doc.name,
								company: frm.doc.company,
								start_date: frm.doc.start_date,
								end_date: frm.doc.end_date,
							},
							callback: function () {},
						});
					} else {
						frappe.throw(
							__(
								'BAS data can be updated only "In Review" status. Please change the status back to "In Review" for updating the BAS data.'
							)
						);
					}
				});
			}
		}
	},
	company(frm) {
		frm.trigger("update_reporting_period");
		frm.trigger("update_end_date");
	},

	start_date(frm) {
		frm.trigger("update_end_date");
	},

	g7(frm) {
		frm.set_value("g8", frm.doc.g6 + frm.doc.g7);
		frm.set_value("g9", frm.doc.g8 / 11);
		frm.set_value("1a", frm.doc._1a_only + frm.doc.g7 / 11);
		frm.set_value("net_gst", Math.abs(frm.doc["1a"] - frm.doc["1b"]));
		frm.trigger("update_label");
	},

	g18(frm) {
		frm.set_value("g19", frm.doc.g17 + frm.doc.g18);
		frm.set_value("g20", frm.doc.g19 / 11);
		frm.set_value("1b", frm.doc._1b_only + frm.doc.g18 / 11);
		frm.set_value("net_gst", Math.abs(frm.doc["1a"] - frm.doc["1b"]));
		frm.trigger("update_label");
	},

	update_label(frm) {
		if (frm.doc["1b"] > frm.doc["1a"]) {
			frm.set_df_property("net_gst", "label", "GST Refund");
		} else {
			frm.set_df_property("net_gst", "label", "GST to Pay");
		}
		frm.trigger("check_data_correctness");
	},

	check_data_correctness(frm) {
		if (frm.doc["1b"] !== frm.doc["g20"]) {
			frm.fields_dict["1b"].$wrapper
				.find(".control-value")
				.css({ "background-color": "#ffb3b3" });
			frm.fields_dict["g20"].$wrapper
				.find(".control-value")
				.css({ "background-color": "#ffb3b3" });
			frm.set_df_property(
				"_1b_warning",
				"options",
				"<b> Please report the issue of 1B not matching with G20 <a href='https://github.com/Arus-Info/ERPNext-Australian-Localisation/issues/new?title=1B%20not%20matching%20with%20G20' target='blank'>here</a></b>"
			);
		} else {
			frm.fields_dict["1b"].$wrapper
				.find(".control-value")
				.css({ "background-color": "#f8f8f8" });
			frm.fields_dict["g20"].$wrapper
				.find(".control-value")
				.css({ "background-color": "#f8f8f8" });
			frm.set_df_property("_1b_warning", "options", " ");
		}
		if (frm.doc["1a"] !== frm.doc["g9"]) {
			frm.fields_dict["1a"].$wrapper
				.find(".control-value")
				.css({ "background-color": "#ffb3b3" });
			frm.fields_dict["g9"].$wrapper
				.find(".control-value")
				.css({ "background-color": "#ffb3b3" });
			frm.set_df_property(
				"_1a_warning",
				"options",
				"<b> Please report the issue of 1A not matching with G9 <a href='https://github.com/Arus-Info/ERPNext-Australian-Localisation/issues/new?title=1A%20not%20matching%20with%20G9 ' target='blank' >here</a> </b>"
			);
		} else {
			frm.fields_dict["1a"].$wrapper
				.find(".control-value")
				.css({ "background-color": "#f8f8f8" });
			frm.fields_dict["g9"].$wrapper
				.find(".control-value")
				.css({ "background-color": "#f8f8f8" });
			frm.set_df_property("_1a_warning", "options", " ");
		}
	},

	update_end_date: async function (frm) {
		if (frm.doc.start_date && frm.doc.company) {
			if (!reporting_period) {
				frappe.throw(
					__(
						"Please set reporting period in <a href='/app/au-localisation-settings/AU Localisation Settings' > ERPNext Australian Settings </a>"
					)
				);
			} else if (reporting_period) {
				if (reporting_period === "Monthly") {
					await frm
						.set_value(
							"start_date",
							moment(frm.doc.start_date).startOf("month").format()
						)
						.then((e) => {
							if (e === null) {
								frappe.msgprint(
									__(
										`Start date is changed to 
										${moment(frm.doc.start_date).format(
											"DD-MM-YY"
										)} to keep it in line with the ${reporting_period} + BAS setup`
									)
								);
							}
						});
					frm.set_value("end_date", moment(frm.doc.start_date).endOf("month").format());
				} else if (reporting_period === "Quarterly") {
					frappe.call({
						method: "erpnext_australian_localisation.erpnext_australian_localisation.doctype.au_bas_report.au_bas_report.get_quaterly_start_end_date",
						args: {
							start_date: frm.doc.start_date,
						},
						callback: async function (data) {
							await frm.set_value("start_date", data.message[0]).then((e) => {
								if (e === null) {
									frappe.msgprint(
										__(
											`Start date is changed to 
										${moment(frm.doc.start_date).format(
											"DD-MM-YY"
										)} to keep it in line with the ${reporting_period} + BAS setup`
										)
									);
								}
							});
							frm.set_value("end_date", data.message[1]);
						},
					});
				}
			}
		} else {
			frm.set_value("end_date", "");
		}
	},

	update_reporting_period(frm) {
		let brp = au_localisation_settings.bas_reporting_period;
		reporting_period = "";
		for (let i = 0; i < brp.length; i++) {
			if (brp[i].company === frm.doc.company) {
				reporting_period = brp[i].reporting_period;
				break;
			}
		}
	},
});

frappe.tour["AU BAS Report"] = [
	{
		fieldname: "company",
		title: "Company Selection",
		description: "Select the company for which BAS Report needs to be generated",
		position: "Right",
	},
	{
		fieldname: "reporting_status",
		title: "Reporting Status Selection",
		description:
			'Reporting status needs to be "In Review" while preparing the Report. BAS Report data can be recalculated till the Reporting Status is set to "Validated". Once BAS is lodged then BAS Report can be submitted. ',
		position: "Bottom",
	},
	{
		fieldname: "start_date",
		title: "Start Date Selection",
		description:
			"The BAS Reporting period start date needs to be selected. The system will update the reporting end date based on the frequency (Monthly/ Quarterly) in the AU Localisation Settings page",
		position: "Right",
	},
];
