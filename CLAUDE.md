# ERPNext Australian Localisation

Frappe app that adds Australian localisation to ERPNext (v16+): GST postings, BAS reporting
(Full and Simpler methods), Payment Batches with ABA bank file generation, bank statement
import, and ABN validation.

## Layout

- `erpnext_australian_localisation/hooks.py`: `doc_events`, `doctype_js`, scheduler and fixtures. Most behaviour on core ERPNext doctypes is wired here.
- `erpnext_australian_localisation/overrides/`: server-side hooks on core doctypes (invoices, payment entry, expense claim, company, ABN verification, bank details, bank statement import).
- `erpnext_australian_localisation/erpnext_australian_localisation/doctype/`: app doctypes (`au_*` for tax and BAS, `payment_batch*` for supplier and employee payments).
- `erpnext_australian_localisation/setup/`: custom fields, property setters and install fixtures, applied on install and migrate.
- `erpnext_australian_localisation/patches/` and `patches.txt`: data migrations.
- `erpnext_australian_localisation/tasks/`: scheduled jobs (monthly BAS report creation).
- `erpnext_australian_localisation/public/js/`: client scripts attached through `doctype_js`.

## Conventions

- Python is formatted with ruff using **tabs**, double quotes and a 110-character line length (see `pyproject.toml`). JS uses prettier and eslint. Pre-commit runs all of them.
- CI also runs the Frappe Semgrep rules (`frappe/semgrep-rules`), so follow them: no raw SQL built with string formatting, wrap user-facing strings in `_()`, and don't call `frappe.db.commit()` in request handlers.
- Add new custom fields or property setters in `setup/custom_fields.py` or `setup/property_setters.py`, not as JSON fixtures.
- Any change that has to update existing sites' data or schema needs a patch registered in `patches.txt`.
- Whitelisted methods (`@frappe.whitelist()`) must check permissions and must not trust client input.
- Use `frappe.throw(_("..."))` for validation errors.

## Domain rules to check in reviews

- **GST and BAS:** tax determination depends on the Customer or Supplier Tax Category (domestic, export, import, capital or non-capital) and on Item exemption. BAS label amounts (G1–G20, 1A, 1B) must stay consistent between the Full and Simpler reporting methods and must handle cancellations and amendments.
- **ABA files:** fixed-width records. BSB is `XXX-XXX`, account numbers are at most 9 digits, and amounts are in cents. Field padding and lengths must match the ABA specification exactly, or banks reject the file.
- **ABN:** looked up against the ABR web service (`overrides/abn_verification.py`, client side in `public/js/utils.js`). Handle API failures and timeouts gracefully.
- Currency is AUD. Use `flt` and the field precision for money, never plain float arithmetic.

## Tests

Run tests from a bench with the app installed:

```bash
bench --site <site> set-config allow_tests true
bench --site <site> run-tests --app erpnext_australian_localisation
```
