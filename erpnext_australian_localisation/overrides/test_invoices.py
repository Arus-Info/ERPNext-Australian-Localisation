from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

import frappe

from erpnext_australian_localisation.overrides import invoices
from erpnext_australian_localisation.setup.install_fixtures import get_au_bas_label_setup


class Row(dict):
	def __getattr__(self, name):
		return self.get(name)

	def __setattr__(self, name, value):
		self[name] = value

	def save(self, **kwargs):
		pass


class TestPurchaseGSTEligibility(TestCase):
	def purchase(self, items, tax_amount=100, add_deduct_tax="Add", doctype="Purchase Invoice"):
		doc = SimpleNamespace(
			doctype=doctype,
			name="EXAMPLE-1",
			company="Example",
			posting_date="2026-07-01",
			taxes_and_charges="GST",
			conversion_rate=1.5,
			items=[Row(expense_account="Expense", income_account="Income", **item) for item in items],
			taxes=[
				Row(
					account_head="GST",
					add_deduct_tax=add_deduct_tax,
					base_tax_amount_after_discount_amount=tax_amount,
					tax_amount_after_discount_amount=tax_amount / 1.5,
				)
			],
		)
		created = []

		def new_doc(doctype):
			self.assertEqual(doctype, "AU BAS Entry")
			row = Row()
			created.append(row)
			return row

		def get_value(doctype, filters, field):
			if doctype == "Account":
				return "Tax"
			if doctype in ("Purchase Taxes and Charges Template", "Sales Taxes and Charges Template"):
				return filters
			if doctype == "AU Tax Determination" and doc.doctype == "Sales Invoice":
				return "AUSGST"
			if doctype == "AU Tax Determination":
				return "AUPNCASGT"
			raise AssertionError(doctype)

		def labels(doctype, filters, fields):
			self.assertEqual(doctype, "AU BAS Label Setup")
			return [
				Row(bas_label=row["bas_label"])
				for row in get_au_bas_label_setup()
				if all(row.get(key) == value for key, value in filters.items())
			]

		with (
			patch.object(frappe.db, "get_value", side_effect=get_value),
			patch.object(frappe, "get_all", side_effect=labels),
			patch.object(frappe, "new_doc", side_effect=new_doc),
		):
			invoices.before_submit(doc, "before_submit")
		totals = {}
		for row in created:
			totals[row.bas_label] = (
				totals.get(row.bas_label, 0)
				+ row.get("gst_offset_basis", 0)
				+ row.get("gst_offset_amount", 0)
				+ row.get("gst_pay_basis", 0)
				+ row.get("gst_pay_amount", 0)
			)
		return totals

	def test_foreign_currency_sale_reports_company_currency_gst(self):
		# The document tax is 66.67 at a 1.5 rate; BAS labels must use the AUD amount.
		self.assertEqual(
			self.purchase([{"item_code": "A", "base_net_amount": 1000}], doctype="Sales Invoice"),
			{"1A": 100, "G1": 1100},
		)

	def test_ordinary_purchase_keeps_its_credit(self):
		self.assertEqual(
			self.purchase([{"item_code": "A", "base_net_amount": 1000}]), {"1B": 100, "G11": 1100}
		)

	def test_deducted_tax_reduces_ordinary_purchase_credit(self):
		for sign in (1, -1):
			with self.subTest(sign=sign):
				self.assertEqual(
					self.purchase(
						[{"item_code": "B", "base_net_amount": sign * 1000}],
						tax_amount=sign * 100,
						add_deduct_tax="Deduct",
					),
					{"1B": sign * -100, "G11": sign * 900},
				)


class TestExemptItemTaxTemplateValidation(TestCase):
	NON_EXEMPT = "GST 10%"
	EXEMPT = "GST Exempt"

	def validate(self, doctype, **item):
		doc = SimpleNamespace(doctype=doctype, items=[Row(**item)])

		def exists(doctype, filters):
			self.assertEqual(doctype, "Item Tax Template Detail")
			return filters["parent"] == self.NON_EXEMPT

		with patch.object(frappe.db, "exists", side_effect=exists):
			invoices.on_save(doc, "validate")

	def test_ordinary_items_may_use_non_exempt_template(self):
		for doctype in ("Sales Invoice", "Purchase Invoice"):
			with self.subTest(doctype=doctype):
				self.validate(doctype, item_tax_template=self.NON_EXEMPT)
				self.validate(doctype, item_tax_template=None)

	def test_flagged_items_require_a_template(self):
		cases = [
			("Sales Invoice", {"input_taxed": 1}),
			("Purchase Invoice", {"input_taxed": 1}),
			("Purchase Invoice", {"private_use": 1}),
		]
		for doctype, flags in cases:
			with self.subTest(doctype=doctype, **flags):
				with self.assertRaisesRegex(frappe.ValidationError, "mandatory"):
					self.validate(doctype, item_tax_template=None, **flags)

	def test_flagged_items_reject_non_exempt_template(self):
		cases = [
			("Sales Invoice", {"input_taxed": 1}),
			("Purchase Invoice", {"input_taxed": 1}),
			("Purchase Invoice", {"private_use": 1}),
		]
		for doctype, flags in cases:
			with self.subTest(doctype=doctype, **flags):
				with self.assertRaisesRegex(frappe.ValidationError, "Exempt only"):
					self.validate(doctype, item_tax_template=self.NON_EXEMPT, **flags)
				self.validate(doctype, item_tax_template=self.EXEMPT, **flags)

	def test_sales_private_use_flag_is_ignored(self):
		self.validate("Sales Invoice", private_use=1, item_tax_template=self.NON_EXEMPT)
