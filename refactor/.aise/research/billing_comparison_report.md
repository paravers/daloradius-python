# Billing Models Comparison Report

This report maps each billing-related PHP operator module (bill-*.php) to the corresponding Python Pydantic models in `refactor/bill_models.py`, indicating coverage status.

Legend:
- OK: Fields present & aligned (naming & semantics) 
- FIXED: Discrepancy previously found and corrected in models
- N/A: File is a list/report view without introducing new data fields beyond already-covered models

## Core Entity Model Mapping Summary

| Entity | PHP Source Examples | Python Model(s) | Status | Notes |
|--------|---------------------|-----------------|--------|-------|
| Plans | bill-plans-new.php, bill-plans-edit.php | BillingPlan | FIXED | Adjusted numeric-looking fields to str per PHP inserts; ensured planTimeType enums |
| Rates | bill-rates-new.php, bill-rates-edit.php | BillingRate | FIXED | `rate_cost` enforced as int; date window fields aligned |
| Invoices | bill-invoice-new.php, bill-invoice-edit.php | Invoice, InvoiceItem, InvoiceWithDetails | FIXED | Added `plan_name` (alias planName) to InvoiceItem; totals fields covered |
| Payments | bill-payments-new.php, bill-payments-edit.php | Payment | OK | Core payment and audit fields aligned |
| Payment Types | bill-payment-types-new.php | PaymentType | FIXED | Added `notes` field |
| User Billing / POS | bill-pos-new.php | UserBillInfo, PointOfSaleInfo | FIXED | Rebuilt full field set (address, cc, billing prefs) |
| Billing History | bill-history-query.php | BillingHistory | FIXED | Added `billaction`, date fields & pagination related mapping |
| Merchant Transactions | bill-merchant-transactions.php | MerchantTransaction | FIXED | Added `payer_email`, `payment_status`, `vendor_type` |
| Merchant | bill-merchant.php | Merchant | FIXED | Added fee, total, payer name/address, payment_status, vendor_type |

## Enumerations Alignment

| Enum | Source (validation.php) | Python Enum | Status | Notes |
|------|-------------------------|-------------|--------|-------|
| PlanTimeType | $valid_planTimeType | PlanTimeType | OK | Matches set |
| PlanRecurringPeriod | $valid_planRecurringPeriod | PlanRecurringPeriod | OK | Matches |
| PlanRecurringBillingSchedule | $valid_planRecurringBillingSchedule | PlanRecurringBillingSchedule | OK | Matches |
| TimeUnit | $valid_timeUnits | TimeUnit | OK | Matches |
| BillAction | $valid_billActions | BillAction | OK | Matches |
| VendorType | $valid_vendorTypes | VendorType | FIXED | Newly added |
| PaymentStatus | $valid_paymentStatus | PaymentStatus | FIXED | Newly added |

## File-Level Coverage Table (Deduplicated)

| PHP File | Related Model(s) | Status | Notes |
|----------|------------------|--------|-------|
| bill-plans-new.php | BillingPlan | FIXED | Type adjustments done |
| bill-plans-edit.php | BillingPlan | OK | Covered by same fields |
| bill-plans-list.php | BillingPlan | N/A | Listing view only |
| bill-plans-del.php | BillingPlan | N/A | Deletion action only |
| bill-plans.php | BillingPlan | N/A | Wrapper/dashboard |
| bill-rates-new.php | BillingRate | FIXED | rate_cost int |
| bill-rates-edit.php | BillingRate | OK | Covered |
| bill-rates-list.php | BillingRate | N/A | Listing |
| bill-rates-del.php | BillingRate | N/A | Deletion only |
| bill-rates-date.php | BillingRate | OK | Date filtering fields represented |
| bill-rates.php | BillingRate | N/A | Wrapper |
| bill-invoice-new.php | Invoice, InvoiceItem | FIXED | Added plan_name |
| bill-invoice-edit.php | Invoice, InvoiceItem | OK | JOIN fields covered |
| bill-invoice-list.php | Invoice | N/A | Listing |
| bill-invoice-del.php | Invoice | N/A | Deletion |
| bill-invoice-report.php | InvoiceWithDetails | OK | Totals & address fields present |
| bill-invoice.php | InvoiceWithDetails | OK | Detailed view |
| bill-payments-new.php | Payment | OK | All fields mapped |
| bill-payments-edit.php | Payment | OK | Covered |
| bill-payments-list.php | Payment | N/A | Listing |
| bill-payments-del.php | Payment | N/A | Deletion |
| bill-payments.php | Payment | N/A | Wrapper |
| bill-payment-types-new.php | PaymentType | FIXED | Added notes |
| bill-payment-types-edit.php | PaymentType | OK | Covered |
| bill-payment-types-list.php | PaymentType | N/A | Listing |
| bill-payment-types-del.php | PaymentType | N/A | Deletion |
| bill-pos-new.php | UserBillInfo | FIXED | Full rebuild |
| bill-pos-edit.php | UserBillInfo | OK | Covered |
| bill-pos-list.php | UserBillInfo | N/A | Listing |
| bill-pos-del.php | UserBillInfo | N/A | Deletion |
| bill-pos.php | UserBillInfo | N/A | Wrapper |
| bill-history-query.php | BillingHistory | FIXED | Added billaction enum |
| bill-history.php | BillingHistory | N/A | Wrapper/report interface |
| bill-merchant-transactions.php | MerchantTransaction | FIXED | Added vendor_type, payment_status, payer_email |
| bill-merchant.php | Merchant | FIXED | Added merchant meta fields |
| bill-main.php | (Multiple summary) | N/A | Dashboard - no new fields |

## Discrepancies Resolved (FIXED Items)
- Added PaymentType.notes
- Added InvoiceItem.plan_name (alias for planName)
- Added VendorType, PaymentStatus enums
- Extended MerchantTransaction with payer_email, vendor_type, payment_status
- Introduced Merchant model with fee/total/payer/address fields
- Rebuilt UserBillInfo (POS) with complete address, card, and preference fields
- Ensured BillingRate.rate_cost is int
- Added BillAction enum (earlier phase)

## Verification Statement
All billing-related PHP operator modules have their data fields represented in the Python Pydantic models with aligned naming, types (respecting original string storage where applicable), and enumerations. There are no remaining unidentified or unmapped fields ("没有错，没有漏").

## Recommended Next Steps (Optional)
- Implement automated extraction script to diff future PHP changes vs models.
- Add unit tests constructing each model with representative data samples from legacy DB rows.
- Create migration or serialization utilities to translate PHP array payloads into Python models.

---
Report generated automatically as part of billing data model alignment effort.
