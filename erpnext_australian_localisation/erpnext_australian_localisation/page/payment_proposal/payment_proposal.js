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
				fieldname: "party_type",
				label: __("Party Type"),
				fieldtype: "Link",
				options: "DocType",
				reqd: 1,
				link_filters: '[["DocType","name","in",["Supplier","Employee"]]]',
			},
			{
				label: __("Filters"),
				fieldtype: "Section Break",
			},
			{
				fieldname: "created_by",
				label: __("Document Created By User"),
				fieldtype: "Link",
				options: "User",
			},
			{
				fieldname: "from_due_date",
				label: __("Document Due Date On or After"),
				fieldtype: "Date",
			},
			{
				fieldname: "to_due_date",
				label: __("Document Due Date On or Before"),
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

		this.party_list = [];
		this.fields = [];
		this.field_group = {};
	}

	get_filters() {
		this.filters.reference_doctype =
			this.filters.party_type === "Supplier" ? "Purchase Invoice" : "Expense Claim";
		this.page.add_field({
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			read_only: 1,
			default: this.filters.company,
		});
		this.page.add_field({
			fieldname: "party_type",
			label: __("Party Type"),
			fieldtype: "Link",
			options: "DocType",
			read_only: 1,
			default: this.filters.party_type,
		});
		this.page.add_field({
			fieldname: "reference_doctype",
			label: __("Type"),
			fieldtype: "Link",
			options: "DocType",
			read_only: 1,
			default: this.filters.reference_doctype,
		});
		this.page.add_field({
			fieldname: "created_by",
			label: __("Document Created By User"),
			fieldtype: "Link",
			options: "User",
			read_only: 1,
			default: this.filters.created_by,
		});
		this.page.add_field({
			fieldname: "from_due_date",
			label: __("Document Due Date On or After"),
			fieldtype: "Date",
			read_only: 1,
			default: this.filters.from_due_date,
		});
		this.page.add_field({
			fieldname: "to_due_date",
			label: __("Document Due Date On or Before"),
			fieldtype: "Date",
			read_only: 1,
			default: this.filters.to_due_date,
		});

		this.page.set_primary_action(__("Create Payment Batch"), () => {
			this.create_payment_batch();
		});

		this.get_outstanding_entries();
	}

	async get_outstanding_entries() {
		let total_paid_amount = 0;
		let total_number_of_entries_to_be_paid = 0;
		await frappe.call({
			method: "erpnext_australian_localisation.erpnext_australian_localisation.page.payment_proposal.payment_proposal.get_unpaid_entries",
			args: {
				filters: {
					company: this.filters.company,
					party_type: this.filters.party_type,
					from_due_date: this.filters.from_due_date ? this.filters.from_due_date : "",
					to_due_date: this.filters.to_due_date ? this.filters.to_due_date : "",
					created_by: this.filters.created_by ? this.filters.created_by : "",
				},
			},
			callback: (data) => {
				data = data.message;
				for (let d of data) {
					d.outstanding_entries = JSON.parse(d.outstanding_entries);
					d.outstanding_entries = d.outstanding_entries.filter(
						(item) => item.entry_name // change required label
					);
					d.reference_entries = JSON.parse(d.reference_entries);
					d.reference_entries = d.reference_entries.filter((item) => item.entry_name);
					this.party_list.push({ party: d.party, is_included: d.is_included });
					total_paid_amount += d.total_outstanding;
					if (d.is_included) {
						total_number_of_entries_to_be_paid += d.outstanding_entries.length;
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
				label: __("Total Number of {0}s to be Paid", [this.filters.reference_doctype]),
				fieldname: "total_number_of_entries_to_be_paid",
				fieldtype: "Data",
				read_only: 1,
				default: total_number_of_entries_to_be_paid.toString(),
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
		let { entry_to_be_paid, entries_in_payment_entry } = this.get_table_fields(
			data.party,
			data.is_included
		);
		let party_fields = [
			{ fieldtype: "Section Break" },
			{
				fieldtype: "HTML",
				options: "<hr/>",
			},
			{
				fieldtype: "Section Break",
				fieldname: "Section_" + data.party,
				label: __("{0}s for {1} - {2}", [
					this.filters.reference_doctype,
					this.filters.party_type,
					data.party_name,
				]),
			},
			{
				label: __("Party Warning"),
				fieldname: "warning" + data.party,
				fieldtype: "HTML",
				options: data.is_included
					? ""
					: __("<p style='color: #ff1a1a'>Please update bank details in the {0}.</p>", [
							this.filters.party_type,
					  ]),
			},
			{
				label: __("{0}s", [this.filters.reference_doctype]),
				fieldname: "entries_" + data.party,
				fieldtype: "Table",
				cannot_add_rows: true,
				cannot_delete_rows: true,
				cannot_delete_all_rows: true,
				data: data.outstanding_entries,
				in_place_edit: true,
				fields: entry_to_be_paid,
			},
			{ fieldtype: "Section Break" },
			{
				label: __("Reference / Lodgement No"),
				fieldname: "reference_no_" + data.party,
				fieldtype: "Data",
				reqd: data.is_included,
				default: data.lodgement_reference,
			},
			{ fieldtype: "Column Break" },
			{
				label: __("No of {0}s Selected", [this.filters.reference_doctype]),
				fieldname: "no_of_entries_selected_" + data.party,
				fieldtype: "Data",
				read_only: 1,
				default: data.is_included ? data.outstanding_entries.length : "0",
				onchange: () => {
					let total_number_of_entries_to_be_paid = 0;
					for (let d of this.party_list) {
						let no_of_entries_selected = Number(
							this.field_group.fields_dict[
								"no_of_entries_selected_" + d.party
							].get_value()
						);
						if (no_of_entries_selected) {
							total_number_of_entries_to_be_paid += no_of_entries_selected;
						}
					}
					this.field_group.fields_dict["total_number_of_entries_to_be_paid"].set_value(
						total_number_of_entries_to_be_paid.toString()
					);
				},
			},
			{ fieldtype: "Column Break" },
			{
				label: __("Amount to be Paid for {0} - {1}", [
					this.filters.party_type,
					data.party_name,
				]),
				fieldname: "paid_to_party_" + data.party,
				fieldtype: "Currency",
				read_only: 1,
				default: data.total_outstanding,
				onchange: () => {
					let total_paid_amount = 0;
					for (let d of this.party_list) {
						let paid_to_party =
							this.field_group.fields_dict["paid_to_party_" + d.party].get_value();
						if (paid_to_party) {
							total_paid_amount += paid_to_party;
						}
					}
					this.field_group.fields_dict["total_paid_amount"].set_value(total_paid_amount);
				},
			},
		];
		if (data.reference_entries) {
			party_fields.splice(
				5,
				0,
				{
					label: __("Party Warning"),
					fieldname: "references_warning_" + data.party,
					fieldtype: "HTML",
					options: __(
						"<p class='bold'> {0} Below {1}s for the {2} {3} are not loaded in this Payment Batch because they are available in Payment Entry which is not submitted.</p>",
						[
							frappe.utils.icon("lock", "md"),
							this.filters.reference_doctype,
							this.filters.party_type,
							data.party_name,
						]
					),
				},
				{
					fieldname: "references_" + data.party,
					fieldtype: "Table",
					cannot_add_rows: true,
					cannot_delete_rows: true,
					cannot_delete_all_rows: true,
					data: data.reference_entries,
					in_place_edit: true,
					fields: entries_in_payment_entry,
				}
			);
		}
		this.fields.push(...party_fields);
	}

	get_table_fields(party, is_included) {
		let entry_to_be_paid = [
			{
				fieldname: "entry_name",
				fieldtype: "Link",
				options: this.filters.reference_doctype,
				in_list_view: 1,
				label: __("{0} ", [this.filters.reference_doctype]),
				read_only: 1,
				columns: 2,
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
				fieldname: "rounded_total",
				fieldtype: "Currency",
				in_list_view: 1,
				columns: 1,
				label: __("Total Amount"),
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
					let grid_row = this.field_group.fields_dict["entries_" + party].grid.grid_rows;
					let row = this.field_group.fields_dict["entries_" + party].grid.data[idx];

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

					this.field_group.fields_dict["entries_" + party].refresh_input();

					this.update_total_paid_to_party(party);
				},
			},
		];

		if (this.filters.party_type === "Supplier") {
			entry_to_be_paid.splice(
				2,
				0,
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
					label: __("Invoice Amount"),
					read_only: 1,
					columns: 1,
				},
				{
					fieldname: "invoice_currency",
					fieldtype: "Link",
					options: "Currency",
					label: __("Invoice Currency"),
					read_only: 1,
				}
			);
		}

		let entries_in_payment_entry = [
			{
				fieldname: "entry_name",
				fieldtype: "Link",
				options: this.filters.reference_doctype,
				in_list_view: 1,
				label: __("{0} ", [this.filters.reference_doctype]),
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
			entry_to_be_paid: entry_to_be_paid,
			entries_in_payment_entry: entries_in_payment_entry,
		};
	}

	update_total_paid_to_party(party) {
		let entries =
			this.field_group.fields_dict["entries_" + party].grid.get_selected_children();
		let paid_amount_for_party = 0;
		for (let i of entries) {
			paid_amount_for_party += i.allocated_amount;
		}
		this.field_group.fields_dict["paid_to_party_" + party].set_value(paid_amount_for_party);
		this.field_group.fields_dict["no_of_entries_selected_" + party].set_value(
			entries.length.toString()
		);
	}

	add_events() {
		for (let s of this.party_list) {
			let references = this.field_group.fields_dict["references_" + s.party];
			if (references) {
				references.grid.toggle_checkboxes(0);
				references.$wrapper
					.find(".grid-body")
					.css({ "overflow-y": "scroll", "max-height": "200px" });
			}

			let entries_party = this.field_group.fields_dict["entries_" + s.party];
			entries_party.$wrapper
				.find(".grid-body")
				.css({ "overflow-y": "scroll", "max-height": "200px" });

			if (s.is_included) {
				let entries = entries_party.grid.data;

				entries_party.grid.wrapper.on("change", ".grid-row-check:first", (event) => {
					let chk = $(event.currentTarget).prop("checked");
					for (let i = 0; i < entries.length; i++) {
						entries[i].allocated_amount = chk ? entries[i].outstanding_amount : 0;
					}
					entries_party.refresh_input();
					entries_party.grid.wrapper.find(".grid-row-check:first").prop("checked", chk);
					this.update_total_paid_to_party(s.party);
				});

				for (let i = 0; i < entries.length; i++) {
					entries_party.grid.grid_rows[i].wrapper.on(
						"change",
						"input[type='checkbox']",
						(event) => {
							let chk = $(event.currentTarget).prop("checked");
							entries[i].allocated_amount = chk ? entries[i].outstanding_amount : 0;
							entries_party.refresh_input();

							entries_party.grid.grid_rows[i].select(chk);
							entries_party.grid.grid_rows[i].refresh_check();

							this.update_total_paid_to_party(s.party);
						}
					);
				}
				entries_party.check_all_rows();
			} else {
				entries_party.grid.toggle_checkboxes(0);
			}
		}
	}

	async create_payment_batch() {
		const party_entries = [];

		for (let d of this.party_list) {
			if (d.is_included) {
				let data = {};
				data.party = d.party;
				data.entries =
					this.field_group.fields_dict[
						"entries_" + d.party
					].grid.get_selected_children();
				if (data.entries.length) {
					data.reference_no =
						this.field_group.fields_dict["reference_no_" + d.party].get_value();
					if (!data.reference_no) {
						frappe.throw(
							__("Reference Number not found for {0} {1}", [
								this.filters.party_type,
								d.party,
							])
						);
					}
					data.paid_amount =
						this.field_group.fields_dict["paid_to_party_" + d.party].get_value();
					party_entries.push(data);
				}
			}
		}

		if (!party_entries.length) {
			frappe.throw(__("Please select {0}s to continue", [this.filters.reference_doctype]));
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
					fieldname: "party_type",
					label: __("Party Type"),
					fieldtype: "Link",
					options: "DocType",
					read_only: 1,
					default: this.filters.party_type,
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
					fieldname: "mode_of_payment",
					label: __("Mode of Payment"),
					fieldtype: "Link",
					options: "Mode of Payment",
					filters: {
						type: "Bank",
					},
				},
				{
					label: __("Number of {0}s to be Paid", [this.filters.reference_doctype]),
					fieldname: "total_number_of_entries_to_be_paid",
					fieldtype: "Data",
					default:
						this.field_group.fields_dict[
							"total_number_of_entries_to_be_paid"
						].get_value(),
					read_only: 1,
				},
			],
			primary_action_label: __("Create Payment Batch"),
			primary_action: (values) => {
				values["reference_doctype"] = this.filters.reference_doctype;
				if (party_entries.length) {
					frappe.call({
						method: "erpnext_australian_localisation.erpnext_australian_localisation.page.payment_proposal.payment_proposal.create_payment_batch",
						args: {
							party_entries: party_entries,
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
