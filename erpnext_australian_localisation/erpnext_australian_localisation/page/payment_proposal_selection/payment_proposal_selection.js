frappe.pages["payment-proposal-selection"].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "Payment Proposal Selection",
		single_column: true,
	});

	$(
		`
		<div class='payment-proposal-selection' style="padding-top: 15px">
		</div>
		<style>
			td, th {
				padding: 10px;
				border: 1px solid var(--table-border-color);
			}
		</style>
		`
	).appendTo(page.main);

	new PaymentProposalSelection(wrapper);
};

class PaymentProposalSelection {
	constructor(wrapper) {
		this.wrapper = wrapper;
		this.page = wrapper.page;
		this.body = $(wrapper).find(`.payment-proposal-selection`);
		this.invoices = {};
		this.setup();
		this.add_events();
	}

	setup() {
		this.page.add_field({
			fieldname: "company",
			label: "Company",
			fieldtype: "Link",
			options: "Company",
			reqd: 1,
			// default : new Date(),
		});

		this.page.add_field({
			fieldname: "from_date",
			label: "From Date",
			fieldtype: "Date",
			// default : new Date(),
		});

		this.page.add_field({
			fieldname: "to_date",
			label: "To Date",
			fieldtype: "Date",
			// default : new Date(),
		});

		this.page.add_field({
			fieldtype: "Button",
			label: "Get Invoices",
			fieldname: "get_invoices",
			click: () => {
				if (this.page.fields_dict.company.value) {
					this.get_invoices();
				} else {
					frappe.throw(__("Please Select the company"));
				}
			},
		});
	}

	get_invoices(company) {
		this.body.html(`
			<div class="form-grid-container">
				<table style='width: 100%' class='form-grid' >
					<thead class='grid-heading-row'>
						<tr>
							<td></td>
							<td>Purchase Invoice</td>
							<td>Grand Total</td>
							<td>Outstanding Amount</td>
							<td>Payment Amount</td>
						</tr>
					<thead>
					<tbody id="purchase-invoices" class="grid-body">
					</tbody>
				</table>
				<button id = "create_payment"> Create Payment </button>
			</div>
		`);
		frappe.call({
			method: "erpnext_australian_localisation.erpnext_australian_localisation.page.payment_proposal_selection.payment_proposal_selection.get_outstanding_invoices",
			args: { company: this.page.fields_dict.company.value },
			callback: (data) => {
				data = data.message;
				for (let d of data) {
					$(`
						<tr>
							<td>
								<input class="supplier-checkbox" data-supplier-row="${d.supplier}" type="checkbox" />
							</td>
							<td colspan=4>${d.supplier_name}</td>
						</tr>
					`).appendTo(this.body.find("#purchase-invoices"));

					this.invoices[d.supplier] = {};
					this.body.find(`[data-supplier-row="${d.supplier}"]`).prop("checked", 1);
					let purchase_invoices = JSON.parse(d.purchase_invoice);

					for (let i of purchase_invoices) {
						$(`
							<tr class="grid-row" >
								<td>
									<input class="invoice-checkbox" data-supplier="${d.supplier}" data-purchase-invoice="${i.name}" type="checkbox" />
								</td>
								<td >${i.name}</td>
								<td style='text-align: right'>${i.rounded_total}</td>
								<td>${i.outstanding_amount}</td>
								<td>
									<input type='number' class="payment-amount form-control" data-supplier="${d.supplier}" id=${i.name} value="${i.outstanding_amount}" />
								</td>
							</tr>
						`).appendTo(this.body.find("#purchase-invoices"));

						this.invoices[d.supplier][i.name] = {
							payment_amount: i.outstanding_amount,
						};
					}
					this.body.find(`[data-supplier="${d.supplier}"]`).prop("checked", 1);
				}
			},
		});
	}

	add_events() {
		this.wrapper.page.body.on("click", '[id="create_payment"]', () => {
			console.log(this.invoices);
			frappe.call({
				method: "erpnext_australian_localisation.erpnext_australian_localisation.page.payment_proposal_selection.payment_proposal_selection.create_payment_batch",
				args: {
					supplier_invoices: this.invoices,
				},
				callback() {
					console.log("Done");
				},
			});
		});

		this.wrapper.page.body.on("click", ".supplier-checkbox ", (event) => {
			let chk = $(event.currentTarget);
			let supplier = chk.attr("data-supplier-row");
			if (!chk.prop("checked")) {
				console.log("running", chk.prop("checked"), "chevk");
				this.body.find(`[data-supplier="${supplier}"]`).prop("checked", 0);
				this.invoices[supplier] = {};
			} else {
				console.log("one time here");
				this.body.find(`[data-supplier="${supplier}"]`).click();
			}
		});

		this.wrapper.page.body.on("click", ".invoice-checkbox ", (event, code) => {
			let chk = $(event.currentTarget);
			console.log(chk, code);
			console.log("clicking");
			console.log($(event));
			let supplier = chk.attr("data-supplier");
			let purchase_invoice_no = chk.attr("data-purchase-invoice");
			let payment_amount = Number(document.getElementById(purchase_invoice_no).value);

			if (!chk.prop("checked")) {
				delete this.invoices[supplier][purchase_invoice_no];
			} else {
				this.invoices[supplier][purchase_invoice_no] = { payment_amount };
			}
			console.log(this.invoices);
		});

		this.wrapper.page.body.on("change", ".payment-amount", (event) => {
			let chk = $(event.currentTarget);
			let supplier = chk.attr("data-supplier");
			let purchase_invoice_no = chk.attr("id");
			let payment_amount = Number(document.getElementById(purchase_invoice_no).value);
			if (this.invoices[supplier][purchase_invoice_no]) {
				this.invoices[supplier][purchase_invoice_no] = { payment_amount };
			}
			console.log(this.invoices);
		});
	}
}
