frappe.pages["payment-proposal"].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Payment Proposal"),
		single_column: true,
	});

	page.set_secondary_action(__("Reset Filters"), () => {
		window.location.reload();
	});

	$(`<div class='payment-proposal' style="padding-top: 15px"></div>`).appendTo(page.main);
};

frappe.pages["payment-proposal"].refresh = function (wrapper) {
	const filter_dialog = new frappe.ui.Dialog({
		fields: [
			{
				fieldname: "company",
				label: __("Company"),
				fieldtype: "Link",
				options: "Company",
				reqd: 1,
				filters: { default_currency: "AUD" },
			},
			{
				label: __("Filters"),
				fieldtype: "Section Break",
			},
			{
				fieldname: "created_by",
				label: __("Invoice Created By User"),
				fieldtype: "Link",
				options: "User",
			},
			{
				fieldname: "from_due_date",
				label: __("Invoice Due Date On or After"),
				fieldtype: "Date",
			},
			{
				fieldname: "to_due_date",
				label: __("Invoice Due Date On or Before"),
				fieldtype: "Date",
			},
		],
		primary_action_label: __("Continue with Payment Proposal"),
		primary_action(values) {
			new PaymentProposal(wrapper, values);
			filter_dialog.hide();
		},
	});

	filter_dialog.show();
};

class PaymentProposal {
	constructor(wrapper, filters) {
		this.wrapper = wrapper;
		this.page = wrapper.page;
		this.body = $(wrapper).find(`.payment-proposal`);
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
			label: __("Invoice Created By User"),
			fieldtype: "Link",
			options: "User",
			read_only: 1,
			default: this.filters.created_by,
		});
		this.page.add_field({
			fieldname: "from_due_date",
			label: __("Invoice Due Date After"),
			fieldtype: "Date",
			read_only: 1,
			default: this.filters.from_due_date,
		});
		this.page.add_field({
			fieldname: "to_due_date",
			label: __("Invoice Due Date Before"),
			fieldtype: "Date",
			read_only: 1,
			default: this.filters.to_due_date,
		});

		this.page.set_primary_action(__("Create Payment Batch"), () => {
			this.create_payment_batch();
		});

		this.get_invoices();
	}

	async get_invoices() {
		let total_paid_amount = 0;
		let total_number_of_invoices_to_be_paid = 0;
		await frappe.call({
			method: "erpnext_australian_localisation.erpnext_australian_localisation.page.payment_proposal.payment_proposal.get_outstanding_invoices",
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
					d.purchase_invoices = JSON.parse(d.purchase_invoices);
					d.purchase_invoices = d.purchase_invoices.filter(
						(item) => item.purchase_invoice
					);
					d.reference_invoices = JSON.parse(d.reference_invoices);
					d.reference_invoices = d.reference_invoices.filter(
						(item) => item.purchase_invoice
					);
					this.supplier_list.push({ supplier: d.supplier, is_included: d.is_included });
					total_paid_amount += d.total_outstanding;
					if (d.is_included) {
						total_number_of_invoices_to_be_paid += d.purchase_invoices.length;
					}
					this.create_fields(d);
				}
			},
		});

		this.fields.unshift(
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
				label: __("Total Number of Invoices to be Paid"),
				fieldname: "total_number_of_invoices_to_be_paid",
				fieldtype: "Data",
				read_only: 1,
				default: total_number_of_invoices_to_be_paid.toString(),
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
		let { invoice_to_be_paid, invoices_in_payment_entry } = this.get_table_fields(
			data.supplier,
			data.is_included
		);
		let supplier_fields = [
			{ fieldtype: "Section Break" },
			{
				fieldtype: "HTML",
				options: "<hr/>",
			},
			{
				fieldtype: "Section Break",
				fieldname: "Section_" + data.supplier,
				label: __("Invoices for Supplier - {0}", [data.supplier_name]),
			},
			{
				label: __("Supplier Warning"),
				fieldname: "warning" + data.supplier,
				fieldtype: "HTML",
				options: data.is_included
					? ""
					: __(
							"<p style='color: #ff1a1a'>Please update bank details in the Supplier.</p>"
					  ),
			},
			{
				label: __("Invoices"),
				fieldname: "invoices_" + data.supplier,
				fieldtype: "Table",
				cannot_add_rows: true,
				cannot_delete_rows: true,
				cannot_delete_all_rows: true,
				data: data.purchase_invoices,
				in_place_edit: true,
				fields: invoice_to_be_paid,
			},
			{ fieldtype: "Section Break" },
			{
				label: __("Reference / Lodgement No"),
				fieldname: "reference_no_" + data.supplier,
				fieldtype: "Data",
				reqd: data.is_included,
				default: data.lodgement_reference,
			},
			{ fieldtype: "Column Break" },
			{
				label: __("No of Invoices Selected"),
				fieldname: "no_of_invoices_selected_" + data.supplier,
				fieldtype: "Data",
				read_only: 1,
				default: data.is_included ? data.purchase_invoices.length : "0",
				onchange: () => {
					let total_number_of_invoices_to_be_paid = 0;
					for (let d of this.supplier_list) {
						let no_of_invoices_selected = Number(
							this.field_group.fields_dict[
								"no_of_invoices_selected_" + d.supplier
							].get_value()
						);
						if (no_of_invoices_selected) {
							total_number_of_invoices_to_be_paid += no_of_invoices_selected;
						}
					}
					this.field_group.fields_dict["total_number_of_invoices_to_be_paid"].set_value(
						total_number_of_invoices_to_be_paid.toString()
					);
				},
			},
			{ fieldtype: "Column Break" },
			{
				label: __("Amount to be Paid for Supplier - {0}", [data.supplier_name]),
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
			},
		];
		if (data.reference_invoices) {
			supplier_fields.splice(
				5,
				0,
				{
					label: __("Supplier Warning"),
					fieldname: "references_warning_" + data.supplier,
					fieldtype: "HTML",
					options: __(
						"<p class='bold'> {0} Below Purchase Invoices for the supplier {1} are not loaded in this Payment Batch as they are not Submitted.</p>",
						[frappe.utils.icon("lock", "md"), data.supplier_name]
					),
				},
				{
					fieldname: "references_" + data.supplier,
					fieldtype: "Table",
					cannot_add_rows: true,
					cannot_delete_rows: true,
					cannot_delete_all_rows: true,
					data: data.reference_invoices,
					in_place_edit: true,
					fields: invoices_in_payment_entry,
				}
			);
		}
		this.fields.push(...supplier_fields);
	}

	get_table_fields(supplier, is_included) {
		let invoice_to_be_paid = [
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
				columns: 1,
				label: __("Ledger Amount"),
				read_only: 1,
			},
			{
				fieldname: "outstanding_amount",
				fieldtype: "Currency",
				in_list_view: 1,
				columns: 1,
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

		let invoices_in_payment_entry = [
			{
				fieldname: "purchase_invoice",
				fieldtype: "Link",
				options: "Purchase Invoice",
				in_list_view: 1,
				label: __("Purchase Invoice"),
				read_only: 1,
			},
			{
				fieldname: "rounded_total",
				fieldtype: "Currency",
				in_list_view: 1,
				label: __("Grand Total"),
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
				fieldname: "payment_entry",
				fieldtype: "Link",
				options: "Payment Entry",
				in_list_view: 1,
				label: __("Payment Entry not Submitted"),
				read_only: 1,
			},
			{
				fieldname: "allocated_amount",
				fieldtype: "Currency",
				in_list_view: 1,
				label: __("Allocated Amount"),
				read_only: 1,
			},
		];

		return {
			invoice_to_be_paid: invoice_to_be_paid,
			invoices_in_payment_entry: invoices_in_payment_entry,
		};
	}

	update_total_paid_to_supplier(supplier) {
		let invoices =
			this.field_group.fields_dict["invoices_" + supplier].grid.get_selected_children();
		let paid_amount_for_supplier = 0;
		for (let i of invoices) {
			paid_amount_for_supplier += i.allocated_amount;
		}
		this.field_group.fields_dict["paid_to_supplier_" + supplier].set_value(
			paid_amount_for_supplier
		);
		this.field_group.fields_dict["no_of_invoices_selected_" + supplier].set_value(
			invoices.length.toString()
		);
	}

	add_events() {
		for (let s of this.supplier_list) {
			let references = this.field_group.fields_dict["references_" + s.supplier];
			if (references) {
				references.grid.toggle_checkboxes(0);
				references.$wrapper
					.find(".grid-body")
					.css({ "overflow-y": "scroll", "max-height": "200px" });
			}

			let invoices_supplier = this.field_group.fields_dict["invoices_" + s.supplier];
			invoices_supplier.$wrapper
				.find(".grid-body")
				.css({ "overflow-y": "scroll", "max-height": "200px" });

			if (s.is_included) {
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
				invoices_supplier.check_all_rows();
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
				"name"
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
					filters: {
						company: this.filters.company,
						fi_abbr: ["!=", ""],
						branch_code: ["!=", ""],
						bank_account_no: ["!=", ""],
						apca_number: ["!=", ""],
						currency: "AUD",
					},
					default: bank_account.name,
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
					label: __("Amount to be Paid"),
					fieldname: "total_paid_amount",
					fieldtype: "Currency",
					default: this.field_group.fields_dict["total_paid_amount"].get_value(),
					read_only: 1,
				},
				{
					label: __("Number of Invoices to be Paid"),
					fieldname: "total_number_of_invoices_to_be_paid",
					fieldtype: "Data",
					default:
						this.field_group.fields_dict[
							"total_number_of_invoices_to_be_paid"
						].get_value(),
					read_only: 1,
				},
			],
			primary_action_label: __("Create Payment Batch"),
			primary_action: (values) => {
				if (supplier_invoices.length) {
					frappe.call({
						method: "erpnext_australian_localisation.erpnext_australian_localisation.page.payment_proposal.payment_proposal.create_payment_batch",
						args: {
							supplier_invoices: supplier_invoices,
							data: values,
						},
						callback(data) {
							Dialog.hide();
							frappe.set_route("payment-batch", data.message);
							window.location.reload();
						},
					});
				}
			},
		});

		Dialog.show();
	}
}
