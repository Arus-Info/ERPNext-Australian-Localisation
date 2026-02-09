frappe.ui.form.on("*", {
	refresh(frm) {
		if (["Supplier", "Customer"].includes(frm.doctype)) {
			apply_abn_indicator(frm);
		}
	},
});

frappe.ui.form.on("Supplier", {
	tax_id(frm) {
		// fires on blur after typing/paste
		const tax_id = (frm.doc.tax_id || "").replace(/\D/g, "");

		// 🔴 PARTIAL OR CLEARED TAX ID
		if (tax_id.length !== 11) {
			clear_tax_id_fields(frm);
			frm._last_abn = null;
			return;
		}
		// Avoid duplicate calls for same value
		if (frm._last_abn === tax_id) return;
		frm._last_abn = tax_id;

		frappe
			.call({
				method: "erpnext_australian_localisation.overrides.abn_verification.fetch_and_update_abn",
				args: {
					tax_id: frm.doc.tax_id,
				},
				freeze: true,
				freeze_message: __("Validating Tax ID and GUID..."),
			})
			.then((r) => {
				// 🔴 INVALID ABN (API returned nothing)
				if (!r.message) {
					clear_tax_id_fields(frm);
					return;
				}

				show_tax_id_popup(frm, r.message);
			});
	},
});
frappe.ui.form.on("Customer", {
	tax_id(frm) {
		// fires on blur after typing/paste
		const tax_id = (frm.doc.tax_id || "").replace(/\D/g, "");

		// 🔴 PARTIAL OR CLEARED TAX ID
		if (tax_id.length !== 11) {
			clear_tax_id_fields(frm);
			frm._last_abn = null;
			return;
		}
		// Avoid duplicate calls for same value
		if (frm._last_abn === tax_id) return;
		frm._last_abn = tax_id;

		frappe
			.call({
				method: "erpnext_australian_localisation.overrides.abn_verification.fetch_and_update_abn",
				args: {
					tax_id: frm.doc.tax_id,
				},
				freeze: true,
				freeze_message: __("Validating Tax ID and GUID..."),
			})
			.then((r) => {
				// 🔴 INVALID ABN (API returned nothing)
				if (!r.message) {
					clear_tax_id_fields(frm);
					return;
				}

				show_tax_id_popup(frm, r.message);
			});
	},
});

function show_tax_id_popup(frm, data) {
	const d = new frappe.ui.Dialog({
		title: __("ABN Information"),
		fields: [
			{ label: "Entity Name", fieldname: "entity_name", fieldtype: "Data", read_only: 1 },
			{
				label: "Business Name",
				fieldname: "business_name",
				fieldtype: "Data",
				read_only: 1,
			},
			{ label: "Status", fieldname: "abn_status", fieldtype: "Data", read_only: 1 },
			{
				label: "Effective From",
				fieldname: "abn_effective_from",
				fieldtype: "Date",
				read_only: 1,
			},
			{ label: "Postcode", fieldname: "address_postcode", fieldtype: "Data", read_only: 1 },
			{ label: "State", fieldname: "address_state", fieldtype: "Data", read_only: 1 },
		],
		primary_action_label: __("OK"),
		primary_action() {
			apply_tax_id_details(frm, data);
			d.hide();
		},
	});

	d.set_values(data);
	d.show();

	// ✅ APPLY GREEN / RED DOT INSIDE POPUP
	setTimeout(() => {
		const status_field = d.fields_dict.abn_status;
		if (status_field && status_field.$wrapper) {
			apply_abn_indicator_to_wrapper(status_field.$wrapper, data.abn_status);
		}
	}, 0);
}

function apply_tax_id_details(frm, data) {
	frm.set_value("entity_name", data.entity_name);
	frm.set_value("business_name", data.business_name);
	frm.set_value("abn_status", data.abn_status);
	frm.set_value("abn_effective_from", data.abn_effective_from);
	frm.set_value("address_postcode", data.address_postcode);
	frm.set_value("address_state", data.address_state);

	frm.save();
}
function clear_tax_id_fields(frm) {
	frm.set_value({
		entity_name: null,
		business_name: null,
		abn_status: null,
		abn_effective_from: null,
		address_postcode: null,
		address_state: null,
	});
}
// for pop up field
function apply_abn_indicator_to_wrapper(wrapper, status) {
	const value_el = wrapper.find(".control-value.like-disabled-input");
	if (!value_el.length) return;

	const text = value_el.text().trim();
	value_el.empty();

	const static_area = $("<div>").addClass("static-area ellipsis");
	const indicator_span = $("<span>").addClass("abn-indicator").text(text);

	if (status === "Active") {
		indicator_span.addClass("green");
	} else {
		indicator_span.addClass("red");
	}

	static_area.append(indicator_span);
	value_el.append(static_area);
}
// for read only field
function apply_abn_indicator(frm) {
	// frm.fields_dict(dictionary of all fields)
	const field = frm.fields_dict.abn_status;
	// if field does not exist it exits quitely
	// .$wrapper jquery object of enitre field container
	if (!field || !field.$wrapper) return;

	// read only field will have this class we targetting here to make style
	const value_el = field.$wrapper.find(".control-value.like-disabled-input");
	if (!value_el.length) return;
	// checks whether class already added or not
	if (!value_el.find(".static-area").length) {
		// grts current abn  status value
		const text = value_el.text().trim();
		// removes current text inside .control-value
		value_el.empty();
		// abn-indicator is my custom class
		const static_area = $("<div>").addClass("static-area ellipsis");
		const indicator_span = $("<span>").addClass("abn-indicator").text(text);

		static_area.append(indicator_span);
		value_el.append(static_area);
	}
	// abn indictor is standard class for orange and blue dots
	const indicator_el = value_el.find(".abn-indicator");
	indicator_el.removeClass("indicator green red");

	if (frm.doc.abn_status === "Active") {
		indicator_el.addClass("indicator green");
	} else {
		indicator_el.addClass("indicator red");
	}
}
