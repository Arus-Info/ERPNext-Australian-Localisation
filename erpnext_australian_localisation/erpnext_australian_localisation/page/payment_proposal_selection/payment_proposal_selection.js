frappe.pages['payment-proposal-selection'].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Payment Proposal Selection',
		single_column: true
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

	new PaymentProposalSelection(wrapper)
}

class PaymentProposalSelection {
	constructor(wrapper) {
		this.wrapper = wrapper
		this.page = wrapper.page
		this.body = $(wrapper).find(`.payment-proposal-selection`)
		this.invoices = []
		this.setup()
		this.create_payment()
	}

	setup() {
		console.log("Hai")

		this.page.add_field({
			fieldname: "from_date",
			label: "From Date",
			fieldtype: "Date",
			// default : new Date(),
		})

		this.page.add_field({
			fieldname: "to_date",
			label: "To Date",
			fieldtype: "Date",
			// default : new Date(),
		})

		this.page.add_field({
			fieldtype: "Button",
			label: "Get Invoices",
			fieldname: "get_invoices",
			click: () => {
				this.get_invoices()
				// this.refresh()
			}
		})
	}

	get_invoices() {
		this.invoices = {}
		this.body.html(`
			<div class="form-grid-container">
				<table style='width: 100%' class='form-grid' >
					<thead class='grid-heading-row'>
						<tr>
						<td></td>
							<td>Purchase Invoice</td>
							<td>Supplier</td>
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
		`)
		frappe.call({
			method: "erpnext_australian_localisation.erpnext_australian_localisation.page.payment_proposal_selection.payment_proposal_selection.get_outstanding_invoices",
			callback: (data) => {
				let invoices = data.message
				console.log(invoices)
				for (let i of invoices) {
					$(`
						<tr class="grid-row" >
						<td>
						<input class="invoice-checkbox" name="${i.name}" type="checkbox" />
						</td>
						<td >${i.name}</td>
						<td>${i.supplier}</td>
						<td>${i.rounded_total}</td>
						<td>${i.outstanding_amount}</td>
						<td>
						<input type='number' data-purchase-invoice="${i.name}" value=${i.outstanding_amount} />
						</td>
						</tr>
						`).appendTo(this.body.find('#purchase-invoices'))

					this.invoices[i.name] = { "payment_amount": i.outstanding_amount }

					this.body.find(`[name="${i.name}"]`).prop("checked", 1)
				}
			}
		})
	}

	create_payment() {
		this.wrapper.page.body.on("click", '[id="create_payment"]', () => {
			console.log(this.invoices)
		})

		this.wrapper.page.body.on("click", '.invoice-checkbox ', (event) => {

			console.log(event)
			let chk = $(event.currentTarget)
			console.log(this.body.find(`[data-purchase-invoice="${chk.attr("name")}"]`).attr("value"))

			if (!chk.prop("checked")) {
				delete this.invoices[chk.attr("name")]
			}
			else {
				this.invoices[chk.attr("name")] = { "payment_amount": 0 }
			}
			console.log(this.invoices)

		})
	}
}