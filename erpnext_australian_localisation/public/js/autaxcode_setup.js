const DOCTYPE = cur_frm.doctype

const CHILD_DOCTYPES = DOCTYPE === "Sales Invoice" ?
	{ "child_doctype": "Sales Invoice Item", "tax_template": "Sales Taxes and Charges Template" } :
	{ "child_doctype": "Purchase Invoice Item", "tax_template": "Purchase Taxes and Charges Template" } ;

// frappe.ui.form.on(DOCTYPE, {
// 	refresh(frm) {
// 		if (!frm.is_new()) {
// 		}

//    }
// })

frappe.ui.form.on(CHILD_DOCTYPES['child_doctype'], {

	item_code(frm,cdt,cdn) {
		// update_au_tax_ode(frm.doc.taxes_and_charges, cdt, cdn)
	},

	item_tax_template(frm, cdt, cdn) {
		console.log("Changed",locals[cdt][cdn].item_tax_template)
		// update_au_tax_code(frm.doc.taxes_and_charges, cdt, cdn)
	},

})

function update_au_tax_code(tax_template,cdt,cdn) {
	row = locals[cdt][cdn]
	console.log(row.item_tax_template)
	frappe.call({
		method: "erpnext_australian_localisation.overrides.invoices.get_au_tax_code",
		args: {
			"tax_template" : tax_template,
			"item_tax_template": row.item_tax_template ? row.item_tax_template : null,
			"tax_template_doctype" : CHILD_DOCTYPES['tax_template']
		},
		callback: (data) => {
			console.log(data.message)
			row.au_tax_code = data.message
		}
	})
}