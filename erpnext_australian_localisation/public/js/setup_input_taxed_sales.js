const DOCTYPE = cur_frm.doctype

const CHILD_DOCTYPE = DOCTYPE === "Sales Invoice" ? "Sales Invoice Item" : "Purchase Invoice Item"

frappe.ui.form.on( DOCTYPE , {
	
})

frappe.ui.form.on(CHILD_DOCTYPE, {
	item_code(frm,cdt,cdn) {
		frappe.model.set_value(cdt,cdn,"input_taxed",frm.doc.input_taxed)
	}
})