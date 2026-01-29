frappe.ui.form.on("AU Localisation Settings", {
	refresh(frm) {
		hide_value(frm);
	},
	abn_lookup_guid(frm) {
		hide_value(frm);
	},
});

function hide_value(frm) {
	// value of guid in form of dictionary
	const field = frm.fields_dict.abn_lookup_guid;
	console.log(field);
	// if field not there exits quitely
	// .$input is jquery object of html element
	// direct targets what is type of element like<input type="text">
	if (!field || !field.$input) return;

	// conversion of input type text  to password
	field.$input.attr("type", "password");
	console.log(field.$input);
}
