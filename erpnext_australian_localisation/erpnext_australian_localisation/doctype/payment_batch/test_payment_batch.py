# Copyright (c) 2025, frappe.dev@arus.co.in and Contributors
# See license.txt

import frappe
from frappe.tests import FrappeTestCase

from erpnext_australian_localisation.erpnext_australian_localisation.doctype.payment_batch.aba_file_generator import (
	aba_account_field,
)


class TestPaymentBatch(FrappeTestCase):
	def test_aba_account_field_pads_to_nine(self):
		self.assertEqual(aba_account_field("123456", "Supplier S-0001"), "   123456")
		self.assertEqual(aba_account_field("123456789", "Supplier S-0001"), "123456789")

	def test_aba_account_field_refuses_ten_digits(self):
		with self.assertRaises(frappe.ValidationError):
			aba_account_field("1234567890", "Supplier S-0001")
