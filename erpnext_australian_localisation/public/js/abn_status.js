frappe.ui.form.on("*", {
	refresh(frm) {
		if (["Supplier", "Customer"].includes(frm.doctype)) {
			apply_abn_indicator(frm);
		}
	},
});

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
