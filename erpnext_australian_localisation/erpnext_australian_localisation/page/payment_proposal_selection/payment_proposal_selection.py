import frappe


@frappe.whitelist()
def get_outstanding_invoices():

	outstanding_invoices = frappe.get_list(
		"Purchase Invoice",
		fields = ["name", "supplier", "rounded_total", "outstanding_amount"],
		filters=[["status", "in", ["Partly Paid", "Unpaid", "Overdue"]]],
	)

	return outstanding_invoices
