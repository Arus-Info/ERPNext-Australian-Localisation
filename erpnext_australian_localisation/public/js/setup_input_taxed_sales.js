const DOCTYPE = cur_frm.doctype

const CHILD_DOCTYPE = DOCTYPE + " Item"

frappe.ui.form.on(CHILD_DOCTYPE, {

	input_taxed(frm, cdt, cdn) {
		if (cdt.includes("Sales")) {
			update_sales_item_tax_template(frm,cdt,cdn)
		}
		if (cdt === "Purchase Invoice Item") {
			update_purchase_item_tax_template(frm,cdt,cdn)
		}
	},

	private_use(frm, cdt, cdn) {
		update_purchase_item_tax_template(frm,cdt,cdn)
	},
})

function get_item_tax_template(frm, cdt, cdn) {
	let item = locals[cdt][cdn]
	if (item.item_code && item.rate) {
		frappe.call({
			method: "erpnext.stock.get_item_details.get_item_tax_template",
			args: {
				args: {
					item_code: item.item_code,
					company: frm.doc.company,
					base_net_rate: item.base_net_rate,
					tax_category: frm.doc.tax_category,
					item_tax_template: item.item_tax_template,
					posting_date: frm.doc.posting_date,
					bill_date: frm.doc.bill_date,
					transaction_date: frm.doc.transaction_date,
				}
			},
			callback: function (r) {
				const item_tax_template = r.message;
				frappe.model.set_value(cdt, cdn, 'item_tax_template', item_tax_template);
			}
		});
	}
}

function update_sales_item_tax_template(frm,cdt,cdn) {
	var row = locals[cdt][cdn]
	if (!row.input_taxed) {
		get_item_tax_template(frm, cdt, cdn)
	}
	else {
		frappe.db.get_list("Item Tax Template", {
			filters: { "title": "GST Exempt Sales", "company": frm.doc.company },
			pluck: "name"
		})
			.then((data) => {
				frappe.model.set_value(cdt, cdn, "item_tax_template", data[0])
			})
	}
}

function update_purchase_item_tax_template(frm, cdt, cdn) {
	let row = locals[cdt][cdn]
	if (row.input_taxed && row.private_use) {
		frappe.model.set_value(cdt, cdn, "input_taxed", 0)
		frappe.model.set_value(cdt, cdn, "private_use", 0)
		frappe.throw("A Purchase Invoice Item cannot be classified as both 'Purchases for private use / not income tax deductible' and 'Purchase for Input-taxed Sales.")
	}
	else if (!row.input_taxed && !row.private_use) {
		get_item_tax_template(frm,cdt,cdn)
	}
	else {
		frappe.db.get_list("Item Tax Template", {
			filters: { "title": "GST Exempt Purchase", "company": frm.doc.company },
			pluck: "name"
		})
			.then((data) => {
				frappe.model.set_value(cdt, cdn, "item_tax_template", data[0])
			})
	}
}