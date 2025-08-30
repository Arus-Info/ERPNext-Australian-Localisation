frappe.pages["payment-proposal-selection"].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Payment Proposal Selection"),
		single_column: true,
	});

	$(`<div class='payment-proposal-selection' style="padding-top: 15px"></div>`).appendTo(
		page.main
	);
};

frappe.pages["payment-proposal-selection"].refresh = function (wrapper) {
	const filter_dialog = new frappe.ui.Dialog({
		fields: [
			{
				fieldname: "company",
				label: __("Company"),
				fieldtype: "Link",
				options: "Company",
				reqd: 1,
			},
			{
				fieldname: "created_by",
				label: __("Created By User"),
				fieldtype: "Link",
				options: "User",
			},
			{
				fieldname: "from_due_date",
				label: __("From Due Date"),
				fieldtype: "Date",
			},
			{
				fieldname: "to_due_date",
				label: __("To Due Date"),
				fieldtype: "Date",
			},
		],
		primary_action_label: __("Continue with Payment Proposal Solution"),
		primary_action(values) {
			new PaymentProposalSelection(wrapper, values);
			filter_dialog.hide();
		},
	});

	filter_dialog.show();
};

class PaymentProposalSelection {
	constructor(wrapper, filters) {
		this.wrapper = wrapper;
		this.page = wrapper.page;
		this.body = $(wrapper).find(`.payment-proposal-selection`);
		this.filters = filters;

		this.get_filters();

		this.supplier_list = [];
		this.fields = [];
		this.field_group = {};
	}

	get_filters() {
		this.page.add_field({
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			read_only: 1,
			default: this.filters.company,
		});
		this.page.add_field({
			fieldname: "created_by",
			label: __("Created By User"),
			fieldtype: "Link",
			options: "User",
			read_only: 1,
			default: this.filters.created_by,
		});
		this.page.add_field({
			fieldname: "from_due_date",
			label: __("From Due Date"),
			fieldtype: "Date",
			read_only: 1,
			default: this.filters.from_due_date,
		});
		this.page.add_field({
			fieldname: "to_due_date",
			label: __("To Due Date"),
			fieldtype: "Date",
			read_only: 1,
			default: this.filters.to_due_date,
		});

		this.page.set_primary_action(__("Reset"), () => {
			window.location.reload();
		});

		this.get_invoices();
	}

	async get_invoices() {
		let total_paid_amount = 0;
		await frappe.call({
			method: "erpnext_australian_localisation.erpnext_australian_localisation.page.payment_proposal_selection.payment_proposal_selection.get_outstanding_invoices",
			args: {
				filters: {
					company: this.filters.company,
					from_due_date: this.filters.from_due_date ? this.filters.from_due_date : "",
					to_due_date: this.filters.to_due_date ? this.filters.to_due_date : "",
					created_by: this.filters.created_by ? this.filters.created_by : "",
				},
			},
			callback: (data) => {
				data = data.message;
				for (let d of data) {
					this.supplier_list.push({ supplier: d.supplier, is_included: d.is_included });
					total_paid_amount += d.total_outstanding;
					this.create_fields(d);
				}
			},
		});

		this.fields.push(
			{ fieldtype: "Section Break" },
			{
				label: __("Total Amount to be Paid"),
				fieldname: "total_paid_amount",
				fieldtype: "Currency",
				read_only: 1,
				default: total_paid_amount,
			},
			{ fieldtype: "Column Break" },
			{
				label: __("Create Payment Batch"),
				fieldtype: "Button",
				click: () => {
					this.create_payment_batch();
				},
			}
		);

		this.field_group = new frappe.ui.FieldGroup({
			fields: this.fields,
			body: this.body,
		});

		this.field_group.make();
		this.add_events();
	}

	create_fields(data) {
		let purchase_invoices = JSON.parse(data.purchase_invoice);

		this.fields.push(
			{
				fieldtype: "Section Break",
				fieldname: "Section_" + data.supplier,
				label: __("Invoices for {0}", [data.supplier_name]),
			},
			{
				label: __("Supplier Warning"),
				fieldname: "warning" + data.supplier,
				fieldtype: "HTML",
				options: data.is_included
					? ""
					: __(
							"<p style='color: #ff1a1a'>Please update bank details in the supplier</p>"
					  ),
			},
			{
				label: __("Invoices"),
				fieldname: "invoices_" + data.supplier,
				fieldtype: "Table",
				cannot_add_rows: true,
				cannot_delete_rows: true,
				cannot_delete_all_rows: true,
				data: purchase_invoices,
				in_place_edit: true,
				fields: this.get_table_fields(data.supplier, data.is_included),
			},
			{ fieldtype: "Section Break" },
			{
				label: __("Reference No"),
				fieldname: "reference_no_" + data.supplier,
				fieldtype: "Data",
				reqd: data.is_included,
				default: data.lodgement_reference,
			},
			{ fieldtype: "Column Break" },
			{
				label: __("Total Paid to {0}", [data.supplier]),
				fieldname: "paid_to_supplier_" + data.supplier,
				fieldtype: "Currency",
				read_only: 1,
				default: data.total_outstanding,
				onchange: () => {
					let total_paid_amount = 0;
					for (let d of this.supplier_list) {
						let paid_to_supplier =
							this.field_group.fields_dict[
								"paid_to_supplier_" + d.supplier
							].get_value();
						if (paid_to_supplier) {
							total_paid_amount += paid_to_supplier;
						}
					}
					this.field_group.fields_dict["total_paid_amount"].set_value(total_paid_amount);
				},
			}
		);
	}

	get_table_fields(supplier, is_included) {
		return [
			{
				fieldname: "purchase_invoice",
				fieldtype: "Link",
				options: "Purchase Invoice",
				in_list_view: 1,
				label: __("Purchase Invoice"),
				read_only: 1,
			},
			{
				fieldname: "due_date",
				fieldtype: "Date",
				in_list_view: 1,
				label: __("Due Date"),
				columns: 1,
				read_only: 1,
			},
			{
				fieldname: "invoice_amount",
				fieldtype: "Currency",
				in_list_view: 1,
				options: "invoice_currency",
				label: __("Invoice Amount Total"),
				read_only: 1,
				columns: 1,
			},
			{
				fieldname: "invoice_currency",
				fieldtype: "Link",
				options: "Currency",
				label: __("Invoice Currency"),
				read_only: 1,
			},
			{
				fieldname: "rounded_total",
				fieldtype: "Currency",
				in_list_view: 1,
				label: __("Ledger Amount"),
				read_only: 1,
			},
			{
				fieldname: "outstanding_amount",
				fieldtype: "Currency",
				in_list_view: 1,
				label: __("Outstanding Amount"),
				read_only: 1,
			},
			{
				fieldname: "allocated_amount",
				fieldtype: "Currency",
				in_list_view: 1,
				label: __("Allocated Amount"),
				read_only: !is_included,
				onchange: (event) => {
					let chk = $(
						event.currentTarget.parentNode.parentNode.parentNode.parentNode.parentNode
					);

					let idx = chk.attr("data-idx") - 1;
					let grid_row =
						this.field_group.fields_dict["invoices_" + supplier].grid.grid_rows;
					let row = this.field_group.fields_dict["invoices_" + supplier].grid.data[idx];

					if (row.allocated_amount > row.outstanding_amount) {
						frappe.msgprint(
							__("Allocated amount can't be greater than Outstanding amount")
						);
						row.allocated_amount = row.outstanding_amount;
					} else if (row.allocated_amount > 0) {
						grid_row[idx].select(true);
						grid_row[idx].refresh_check();
					} else if (row.allocated_amount === 0 || row.allocated_amount === null) {
						if (row.allocated_amount === null) {
							row.allocated_amount = 0;
						}
						grid_row[idx].select(false);
						grid_row[idx].refresh_check();
					}

					this.field_group.fields_dict["invoices_" + supplier].refresh_input();

					this.update_total_paid_to_supplier(supplier);
				},
			},
		];
	}

	update_total_paid_to_supplier(supplier) {
		let invoices = this.field_group.fields_dict["invoices_" + supplier].get_value();
		let paid_amount_for_supplier = 0;
		for (let i of invoices) {
			paid_amount_for_supplier += i.allocated_amount;
		}
		this.field_group.fields_dict["paid_to_supplier_" + supplier].set_value(
			paid_amount_for_supplier
		);
	}

	add_events() {
		for (let s of this.supplier_list) {
			let invoices_supplier = this.field_group.fields_dict["invoices_" + s.supplier];

			invoices_supplier.$wrapper
				.find(".grid-body")
				.css({ "overflow-y": "scroll", "max-height": "200px" });

			if (s.is_included) {
				invoices_supplier.check_all_rows();

				let invoices = invoices_supplier.grid.data;

				invoices_supplier.grid.wrapper.on("change", ".grid-row-check:first", (event) => {
					let chk = $(event.currentTarget).prop("checked");
					for (let i = 0; i < invoices.length; i++) {
						invoices[i].allocated_amount = chk ? invoices[i].outstanding_amount : 0;
					}
					invoices_supplier.refresh_input();
					invoices_supplier.grid.wrapper
						.find(".grid-row-check:first")
						.prop("checked", chk);
					this.update_total_paid_to_supplier(s.supplier);
				});

				for (let i = 0; i < invoices.length; i++) {
					invoices_supplier.grid.grid_rows[i].wrapper.on(
						"change",
						"input[type='checkbox']",
						(event) => {
							let chk = $(event.currentTarget).prop("checked");
							invoices[i].allocated_amount = chk
								? invoices[i].outstanding_amount
								: 0;
							invoices_supplier.refresh_input();

							invoices_supplier.grid.grid_rows[i].select(chk);
							invoices_supplier.grid.grid_rows[i].refresh_check();

							this.update_total_paid_to_supplier(s.supplier);
						}
					);
				}
			} else {
				invoices_supplier.grid.toggle_checkboxes(0);
			}
		}
	}

	async create_payment_batch() {
		const supplier_invoices = [];

		for (let d of this.supplier_list) {
			if (d.is_included) {
				let data = {};
				data.supplier = d.supplier;
				data.invoices =
					this.field_group.fields_dict[
						"invoices_" + d.supplier
					].grid.get_selected_children();
				if (data.invoices.length) {
					data.reference_no =
						this.field_group.fields_dict["reference_no_" + d.supplier].get_value();
					if (!data.reference_no) {
						frappe.throw(
							__("Reference Number not found for Supplier {0}", [d.supplier])
						);
					}
					data.paid_amount =
						this.field_group.fields_dict["paid_to_supplier_" + d.supplier].get_value();
					supplier_invoices.push(data);
				}
			}
		}

		if (!supplier_invoices.length) {
			frappe.throw(__("Please select Purchase Invoices to continue"));
		}

		let bank_account;
		await frappe.db
			.get_value(
				"Bank Account",
				{
					is_company_account: 1,
					company: this.page.fields_dict.company.value,
					currency: "AUD",
				},
				["name", "account"]
			)
			.then((data) => {
				bank_account = data.message;
			});
		const Dialog = new frappe.ui.Dialog({
			title: __("Payment Batch Creation"),
			fields: [
				{
					label: __("Company"),
					fieldname: "company",
					fieldtype: "Link",
					options: "Company",
					read_only: 1,
					default: this.filters.company,
				},
				{
					label: __("Bank Account"),
					fieldname: "bank_account",
					fieldtype: "Link",
					options: "Bank Account",
					reqd: 1,
					filters: { company: this.filters.company, currency: "AUD" },
					default: bank_account.name,
				},
				{
					label: __("Account Paid From"),
					fieldname: "paid_from",
					fieldtype: "Link",
					options: "Account",
					reqd: 1,
					filters: {
						company: this.filters.company,
						account_type: "Bank",
						is_group: 0,
						account_currency: "AUD",
					},
					default: bank_account.account,
				},
				{
					label: __("Posting Date"),
					fieldname: "posting_date",
					fieldtype: "Date",
					default: "Today",
					reqd: 1,
				},
				{
					label: __("Reference Date"),
					fieldname: "reference_date",
					fieldtype: "Date",
					default: "Today",
					reqd: 1,
				},
				{
					label: __("Total Paid Amount"),
					fieldname: "total_paid_amount",
					fieldtype: "Currency",
					default: this.field_group.fields_dict["total_paid_amount"].get_value(),
					read_only: 1,
				},
			],
			primary_action_label: __("Create Payment Batch"),
			primary_action: (values) => {
				if (supplier_invoices.length) {
					frappe.call({
						method: "erpnext_australian_localisation.erpnext_australian_localisation.page.payment_proposal_selection.payment_proposal_selection.create_payment_batch",
						args: {
							supplier_invoices: supplier_invoices,
							data: values,
						},
						callback(data) {
							Dialog.hide();
							frappe.set_route("payment-batch", data.message);
						},
					});
				}
			},
		});

		Dialog.show();
	}
}
