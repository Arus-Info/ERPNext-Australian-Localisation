window.au_localisation_settings = frappe.boot.au_localisation_settings;

frappe.provide("au_localisation.abn");

au_localisation.abn.setup = function (frm) {
	frm._last_abn = (frm.doc.tax_id || "").replace(/ /g, "");
	if (frm.fields_dict.abn_status) {
		au_localisation.abn.apply_indicator(
			frm.fields_dict.abn_status.$wrapper,
			frm.doc.abn_status
		);
	}
	au_localisation.abn.bind_events(frm);
};

au_localisation.abn.bind_events = function (frm) {
	if (!frm.fields_dict.tax_id) return;

	frm.fields_dict.tax_id.$wrapper
		.find("input")
		.off("blur")
		.on("blur", () => {
			au_localisation.abn.handle_blur(frm);
		});
};

au_localisation.abn.handle_blur = function (frm) {
	const tax_id = (frm.doc.tax_id || "").replace(/ /g, "");
	if (!tax_id) {
		au_localisation.abn.clear_tax_id_fields(frm);
		frm._last_abn = null;
		frm._is_abn_changed = false;
		return;
	}
	if (frm._last_abn === tax_id) return;
	frm._last_abn = tax_id;
	au_localisation.abn.clear_tax_id_fields(frm);

	if (!frm.doc.is_verify_abn) return;
	const guid = au_localisation_settings.abn_lookup_guid;

	if (!guid) {
		frappe.msgprint(
			__(
				"Please enter GUID in <a href='/desk/au-localisation-settings/' target='_blank'>AU Localisation Settings</a>"
			)
		);
		au_localisation.abn.clear_tax_id_fields(frm);
		frm.set_value("is_verify_abn", 0);
		return;
	}

	frappe
		.call({
			method: "erpnext_australian_localisation.overrides.abn_verification.fetch_and_update_abn",
			args: { tax_id, guid },
			freeze: true,
			freeze_message: __("Validating Tax ID..."),
		})
		.then((r) => {
			const data = r.message;

			if (data.success) {
				frm._is_abn_changed = false;
				au_localisation.abn.show_popup(frm, data);
				au_localisation.abn.apply_details(frm, data);
			} else {
				au_localisation.abn.handle_error(frm, data.error);
			}
		});
};

au_localisation.abn.handle_error = function (frm, error) {
	if (error == "The GUID entered is not recognised as a Registered Party") {
		frappe.throw(
			__(
				"The GUID entered in the <a href='/desk/au-localisation-settings/' target='_blank'>AU Localisation Settings</a> is invalid. Unable to fetch ABN information"
			)
		);
	}

	if (error == "Search text is not a valid ABN or ACN") {
		au_localisation.abn.clear_tax_id_fields(frm);
		frappe.throw(__("Invalid ABN ID. Please enter a valid ABN."));
	}

	frappe.throw(__("Unexpected Error: {0}", [error]));
};

au_localisation.abn.show_popup = function (frm, data) {
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
			d.hide();
			frm.save();
		},
	});

	d.set_values(data);
	d.show();
	setTimeout(() => {
		au_localisation.abn.apply_indicator(d.fields_dict.abn_status.$wrapper, data.abn_status);
	}, 0);
};

au_localisation.abn.apply_details = function (frm, data) {
	frm.set_value("entity_name", data.entity_name);
	frm.set_value("business_name", data.business_name);
	frm.set_value("abn_status", data.abn_status);
	frm.set_value("abn_effective_from", data.abn_effective_from);
	frm.set_value("address_postcode", data.address_postcode);
	frm.set_value("address_state", data.address_state);

	au_localisation.abn.apply_indicator(frm.fields_dict.abn_status.$wrapper, data.abn_status);
};

au_localisation.abn.clear_tax_id_fields = function (frm) {
	frm.set_value({
		entity_name: null,
		business_name: null,
		abn_status: null,
		abn_effective_from: null,
		address_postcode: null,
		address_state: null,
	});
};

au_localisation.abn.apply_indicator = function (wrapper, status) {
	if (!wrapper) return;

	const value_el = wrapper.find(".control-value.like-disabled-input");
	value_el.find(".abn-indicator").remove();

	const indicator = $("<span>")
		.addClass("indicator abn-indicator")
		.addClass(status === "Active" ? "green" : "red");

	value_el.prepend(indicator);
};
