import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from erpnext_australian_localisation.setup.custom_fields import EMPLOYEE_BANK_DETAILS


def execute():
	"""
	Update Payment Batch Item in way that it can be used for paying an Employee
	Update Payment Batch Reference in way that it can used to refer an Expense Claim
	"""
	frappe.db.sql(
		"""
			UPDATE `tabPayment Batch`
			SET
				type = 'Supplier'
		"""
	)

	frappe.db.sql(
		"""
			UPDATE `tabPayment Batch Item`
			SET
				party_type = 'Supplier' ,
				party = supplier
		"""
	)

	frappe.db.sql(
		"""
			UPDATE `tabPayment Batch Reference`
				SET
					reference_doctype = 'Purchase Invoice' ,
					reference_name = purchase_invoice ,
					party_type = 'Supplier' ,
					party = supplier
		"""
	)

	create_custom_fields(EMPLOYEE_BANK_DETAILS, update=1)
