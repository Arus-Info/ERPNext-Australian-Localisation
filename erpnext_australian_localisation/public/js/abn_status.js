frappe.ui.form.on("*", {
	refresh(frm) {
		if (["Supplier", "Customer"].includes(frm.doctype));
		frm.last_abn = (frm.doc.tax_id || "").replace(/\D/g, "");

		if (!frm.fields_dict.tax_id) return;
		frm.fields_dict.tax_id.$wrapper.find("input").on("blur", () => handle_tax_id_blur(frm));
		apply_abn_indicator(frm.fields_dict.abn_status.$wrapper, frm.doc.abn_status);
	},
});

function handle_tax_id_blur(frm) {
	// fires on blur after typing/paste
	const tax_id = (frm.doc.tax_id || "").replace(/\D/g, "");

	//PARTIAL OR CLEARED TAX ID
	if (tax_id.length !== 11) {
		clear_tax_id_fields(frm);
		frm.last_abn = null;
		return;
	}
	// Avoid duplicate calls for same value
	if (frm.last_abn === tax_id) return;
	// new abn value stored
	frm.last_abn = tax_id;

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
			// INVALID ABN (API returned nothing)
			if (!r.message) {
				clear_tax_id_fields(frm);
				return;
			}

			show_tax_id_popup(frm, r.message);
		});
}

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
		// for popup abn status
		apply_abn_indicator(d.fields_dict.abn_status.$wrapper, data.abn_status);
	}, 0);
}

function apply_tax_id_details(frm, data) {
	frm.set_value("entity_name", data.entity_name);
	frm.set_value("business_name", data.business_name);
	frm.set_value("abn_status", data.abn_status);
	frm.set_value("abn_effective_from", data.abn_effective_from);
	frm.set_value("address_postcode", data.address_postcode);
	frm.set_value("address_state", data.address_state);
	// re-apply dot after values set
	setTimeout(() => {
		apply_abn_indicator(frm.fields_dict.abn_status.$wrapper, data.abn_status);
	}, 0);
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

function apply_abn_indicator(wrapper, status) {
	if (!wrapper || !status) return;

	const value_el = wrapper.find(".control-value.like-disabled-input");
	if (!value_el.length) return;

	// prevent duplicate dots
	value_el.find(".abn-indicator").remove();

	const indicator = $("<span>")
		.addClass("indicator abn-indicator")
		.addClass(status === "Active" ? "green" : "red");

	value_el.prepend(indicator);
}
