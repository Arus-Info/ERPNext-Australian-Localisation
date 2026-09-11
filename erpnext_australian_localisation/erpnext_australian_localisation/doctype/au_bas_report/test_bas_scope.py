from unittest import TestCase
from unittest.mock import patch

import frappe

from erpnext_australian_localisation.erpnext_australian_localisation.doctype.au_bas_report import (
	au_bas_report as bas,
)


class Record(dict):
	def __getattr__(self, name):
		return self.get(name, 0)

	def __setattr__(self, name, value):
		self[name] = value

	def append(self, field, value):
		self.setdefault(field, []).append(value)

	def save(self, **kwargs):
		pass


class TestBASScope(TestCase):
	def test_simpler_report_refuses_item_exclusions_that_its_gl_totals_cannot_apply(self):
		doc = Record(
			company="Example",
			accounting_basis="Non-cash",
			reporting_method="Simpler",
			start_date="2026-07-01",
			end_date="2026-07-31",
		)
		with patch.object(frappe.db, "get_value", return_value="AUD"):
			with patch.object(frappe.db, "exists", return_value=None):
				bas.validate_reporting_scope(doc)
			with (
				patch.object(frappe.db, "exists", return_value="EXCLUDED-PURCHASE"),
				self.assertRaises(frappe.ValidationError),
			):
				bas.validate_reporting_scope(doc)
			doc.reporting_method = "Full reporting method"
			with patch.object(frappe.db, "exists", return_value="EXCLUDED-PURCHASE"):
				bas.validate_reporting_scope(doc)

	def test_generation_and_submission_refuse_excluded_simpler_report(self):
		doc = Record(
			company="Example",
			reporting_method="Simpler",
			reporting_status="Validated",
			start_date="2026-07-01",
			end_date="2026-07-31",
		)
		with patch.object(frappe.db, "exists", return_value="EXCLUDED-PURCHASE"):
			with self.assertRaises(frappe.ValidationError):
				bas.AUBASReport.before_submit(doc)
			with patch.object(frappe, "get_doc", return_value=doc):
				with self.assertRaises(frappe.ValidationError):
					bas.get_gst("EXAMPLE-REPORT")
