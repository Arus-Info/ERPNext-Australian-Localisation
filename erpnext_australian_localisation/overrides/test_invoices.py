from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

import frappe

from erpnext_australian_localisation.erpnext_australian_localisation.doctype.au_bas_report import (
	au_bas_report as bas,
)
from erpnext_australian_localisation.overrides import invoices
from erpnext_australian_localisation.setup.install_fixtures import get_au_bas_label_setup


class Row(dict):
	def __getattr__(self, name):
		return self.get(name)

	def __setattr__(self, name, value):
		self[name] = value

	def save(self, **kwargs):
		pass

	def append(self, field, value):
		self.setdefault(field, []).append(value)


class TestPurchaseGSTEligibility(TestCase):
	def purchase(self, items, tax_amount=100, detail=None):
		doc = SimpleNamespace(
			doctype="Purchase Invoice",
			name="EXAMPLE-1",
			company="Example",
			posting_date="2026-07-01",
			taxes_and_charges="GST",
			conversion_rate=1.5,
			items=[Row(expense_account="Expense", **item) for item in items],
			taxes=[
				Row(
					account_head="GST",
					base_tax_amount_after_discount_amount=tax_amount,
					tax_amount_after_discount_amount=tax_amount / 1.5,
				)
			],
		)
		for index, item in enumerate(doc.items):
			item.name = f"item-{index}"
		doc._item_wise_tax_details = []
		for key, value in (detail or {}).items():
			item = next((item for item in doc.items if key in (item.name, item.item_code)), Row())
			doc._item_wise_tax_details.append(
				Row(
					item=item,
					tax=doc.taxes[0],
					amount=value[1] if isinstance(value, list) and len(value) == 2 else "invalid",
				)
			)
		created = []

		def new_doc(doctype):
			self.assertEqual(doctype, "AU BAS Entry")
			row = Row()
			created.append(row)
			return row

		def get_value(doctype, filters, field):
			if doctype == "Company":
				return "AUD"
			if doctype == "Account":
				return "Tax"
			if doctype in ("Item Tax Template", "Purchase Taxes and Charges Template"):
				return filters
			if doctype == "AU Tax Determination":
				return "AUPNCAFR" if filters.get("item_tax_template") == "GST-free" else "AUPNCASGT"
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
			)
		self.created = created
		return totals

	def test_full_report_keeps_only_the_eligible_invoice_credit(self):
		labels = ["G1", "G2", "G3", "G4", "G7", "G10", "G11", "G13", "G14", "G15", "G18", "1A", "1B"]
		for flag, exclusion in [("private_use", "g15"), ("input_taxed", "g13")]:
			with self.subTest(flag=flag):
				self.purchase(
					[
						{"item_code": "P", "base_net_amount": 300, flag: 1},
						{"item_code": "B", "base_net_amount": 700},
					],
					detail={"P": [10, 30], "B": [10, 70]},
				)
				report = Row(company="Example", start_date="2026-07-01", end_date="2026-07-31")

				def entries(doctype, filters, pluck):
					self.assertEqual(doctype, "AU BAS Entry")
					label = next(value for field, operator, value in filters if field == "bas_label")
					return [str(i) for i, row in enumerate(self.created) if row.bas_label == label]

				def mapped(doctype, name, *args, **kwargs):
					row = Row(gst_pay_basis=0, gst_pay_amount=0, gst_offset_basis=0, gst_offset_amount=0)
					row.update(self.created[int(name)])
					return row

				with (
					patch.object(frappe, "get_all", return_value=labels),
					patch.object(frappe, "get_list", side_effect=entries),
					patch.object(frappe.db, "get_value", return_value="AUD"),
					patch.object(frappe, "publish_progress"),
					patch("frappe.model.mapper.get_mapped_doc", side_effect=mapped),
				):
					bas.update_full_bas_report(report)
				self.assertEqual(report.get("1b"), 70)
				self.assertEqual(report.g20, 70)
				self.assertEqual(report.g11, 1100)
				self.assertEqual(report.get(exclusion), 330)

	def test_private_and_input_taxed_purchases_have_no_credit(self):
		for flag, label in [("private_use", "G15"), ("input_taxed", "G13")]:
			with self.subTest(flag=flag):
				totals = self.purchase([{"item_code": "A", "base_net_amount": 1000, flag: 1}])
				self.assertEqual(totals.get("1B", 0), 0)
				self.assertEqual(totals["G11"], 1100)
				self.assertEqual(totals[label], 1100)

	def test_ordinary_purchase_keeps_its_credit(self):
		self.assertEqual(
			self.purchase([{"item_code": "A", "base_net_amount": 1000}]), {"1B": 100, "G11": 1100}
		)

	def test_mixed_purchase_uses_item_tax_in_company_currency(self):
		totals = self.purchase(
			[
				{"item_code": "P", "base_net_amount": 300, "private_use": 1},
				{"item_code": "B", "base_net_amount": 700},
			],
			detail={"P": [10, 30], "B": [10, 70]},
		)
		self.assertEqual(totals, {"1B": 70, "G11": 1100, "G15": 330})

	def test_gst_free_business_item_does_not_receive_private_items_tax(self):
		totals = self.purchase(
			[
				{"item_code": "P", "base_net_amount": 300, "private_use": 1},
				{"item_code": "B", "base_net_amount": 700, "item_tax_template": "GST-free"},
			],
			tax_amount=30,
			detail={"P": [10, 30], "B": [0, 0]},
		)
		self.assertEqual(totals, {"G11": 1030, "G14": 700, "G15": 330})

	def test_mixed_credit_note_reverses_only_the_eligible_credit(self):
		totals = self.purchase(
			[
				{"item_code": "P", "base_net_amount": -300, "private_use": 1},
				{"item_code": "B", "base_net_amount": -700},
			],
			tax_amount=-100,
			detail={"P": [10, -30], "B": [10, -70]},
		)
		self.assertEqual(totals, {"1B": -70, "G11": -1100, "G15": -330})

	def test_mixed_purchase_refuses_missing_or_unreconciled_item_tax(self):
		for detail in [
			None,
			{},
			{"P": [10, 30]},
			{"P": [10, 30], "B": [10, 90]},
			{"P": [10, "NaN"], "B": [10, 70]},
			{"P": [10, 30], "B": "invalid"},
		]:
			with self.subTest(detail=detail), self.assertRaises(frappe.ValidationError):
				self.purchase(
					[
						{"item_code": "P", "base_net_amount": 300, "private_use": 1},
						{"item_code": "B", "base_net_amount": 700},
					],
					detail=detail,
				)

	def test_zero_net_tax_preserves_the_business_credit(self):
		totals = self.purchase(
			[
				{"item_code": "P", "base_net_amount": -300, "private_use": 1},
				{"item_code": "B", "base_net_amount": 300},
			],
			tax_amount=0,
			detail={"P": [10, -30], "B": [10, 30]},
		)
		self.assertEqual(totals, {"1B": 30, "G11": 0, "G15": -330})

	def test_fractional_item_tax_reconciles_for_purchases_and_returns(self):
		for sign in (1, -1):
			with self.subTest(sign=sign):
				totals = self.purchase(
					[
						{"item_code": "P", "base_net_amount": sign * 0.05, "private_use": 1},
						{"item_code": "B", "base_net_amount": sign * 0.05},
					],
					tax_amount=sign * 0.01,
					detail={"P": [10, sign * 0.005], "B": [10, sign * 0.005]},
				)
				self.assertAlmostEqual(totals["G11"], sign * 0.11)
				self.assertAlmostEqual(totals["G15"], sign * 0.05)
				self.assertAlmostEqual(totals["1B"], sign * 0.01)

	def test_same_item_code_with_separate_rows_preserves_eligibility(self):
		totals = self.purchase(
			[
				{"item_code": "A", "base_net_amount": 300, "private_use": 1},
				{"item_code": "A", "base_net_amount": 700},
			],
			detail={"item-0": [10, 30], "item-1": [10, 70]},
		)
		self.assertEqual(totals, {"1B": 70, "G11": 1100, "G15": 330})
