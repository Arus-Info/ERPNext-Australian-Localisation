import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from erpnext_australian_localisation.setup.custom_fields import EMPLOYEE_BANK_DETAILS


def execute():
	"""
	Update Payment Batch Item in way that it can be used for paying an Employee
	Update Payment Batch Invoice in way that it can used to refer an Expense Claim
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
			UPDATE `tabPayment Batch Item` as pbi
			INNER JOIN tabSupplier as s
			ON pbi.supplier = s.name
			SET
				pbi.party_type = 'Supplier' ,
				pbi.party = pbi.supplier ,
				pbi.party_name = s.supplier_name
		"""
	)

	frappe.db.sql(
		"""
			UPDATE `tabPayment Batch Invoice`
				SET
					reference_doctype = 'Purchase Invoice' ,
					reference_name = purchase_invoice ,
					party_type = 'Supplier' ,
					party = supplier
		"""
	)

	if "hrms" in frappe.get_installed_apps():
		create_custom_fields(EMPLOYEE_BANK_DETAILS, update=1)
