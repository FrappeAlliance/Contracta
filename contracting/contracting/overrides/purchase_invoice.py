# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe import _, qb, throw
from frappe.model.mapper import get_mapped_doc
from frappe.query_builder.functions import Sum
from frappe.utils import cint, cstr, flt, formatdate, get_link_to_form, getdate, nowdate

import erpnext
from erpnext.accounts.deferred_revenue import validate_service_stop_date
from erpnext.accounts.doctype.gl_entry.gl_entry import update_outstanding_amt
from erpnext.accounts.doctype.repost_accounting_ledger.repost_accounting_ledger import (
    validate_docs_for_deferred_accounting,
    validate_docs_for_voucher_types,
)
from erpnext.accounts.doctype.sales_invoice.sales_invoice import (
    check_if_return_invoice_linked_with_payment_entry,
    get_total_in_party_account_currency,
    is_overdue,
    unlink_inter_company_doc,
    update_linked_doc,
    validate_inter_company_party,
)
from erpnext.accounts.doctype.tax_withholding_category.tax_withholding_category import (
    get_party_tax_withholding_details,
)
from erpnext.accounts.general_ledger import (
    get_round_off_account_and_cost_center,
    make_gl_entries,
    make_reverse_gl_entries,
    merge_similar_entries,
)
from erpnext.accounts.party import get_due_date, get_party_account
from erpnext.accounts.utils import get_account_currency, get_fiscal_year
from erpnext.assets.doctype.asset.asset import is_cwip_accounting_enabled
from erpnext.assets.doctype.asset_category.asset_category import get_asset_category_account
from erpnext.buying.utils import check_on_hold_or_closed_status
from erpnext.controllers.accounts_controller import validate_account_head
from erpnext.controllers.buying_controller import BuyingController
from erpnext.stock import get_warehouse_account_map
from erpnext.stock.doctype.purchase_receipt.purchase_receipt import (
    get_item_account_wise_additional_cost,
    update_billed_amount_based_on_po,
)
from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import PurchaseInvoice

class WarehouseMissingError(frappe.ValidationError):
    pass


form_grid_templates = {"items": "templates/form_grid/item_grid.html"}


class CustomPurchaseInvoice(PurchaseInvoice):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from erpnext.accounts.doctype.advance_tax.advance_tax import AdvanceTax
        from erpnext.accounts.doctype.payment_schedule.payment_schedule import PaymentSchedule
        from erpnext.accounts.doctype.pricing_rule_detail.pricing_rule_detail import PricingRuleDetail
        from erpnext.accounts.doctype.purchase_invoice_advance.purchase_invoice_advance import (
            PurchaseInvoiceAdvance,
        )
        from erpnext.accounts.doctype.purchase_invoice_item.purchase_invoice_item import PurchaseInvoiceItem
        from erpnext.accounts.doctype.purchase_taxes_and_charges.purchase_taxes_and_charges import (
            PurchaseTaxesandCharges,
        )
        from erpnext.accounts.doctype.tax_withheld_vouchers.tax_withheld_vouchers import TaxWithheldVouchers
        from erpnext.buying.doctype.purchase_receipt_item_supplied.purchase_receipt_item_supplied import (
            PurchaseReceiptItemSupplied,
        )

        additional_discount_percentage: DF.Float
        address_display: DF.SmallText | None
        advance_tax: DF.Table[AdvanceTax]
        advances: DF.Table[PurchaseInvoiceAdvance]
        against_expense_account: DF.SmallText | None
        allocate_advances_automatically: DF.Check
        amended_from: DF.Link | None
        apply_discount_on: DF.Literal["", "Grand Total", "Net Total"]
        apply_tds: DF.Check
        auto_repeat: DF.Link | None
        base_discount_amount: DF.Currency
        base_grand_total: DF.Currency
        base_in_words: DF.Data | None
        base_net_total: DF.Currency
        base_paid_amount: DF.Currency
        base_rounded_total: DF.Currency
        base_rounding_adjustment: DF.Currency
        base_tax_withholding_net_total: DF.Currency
        base_taxes_and_charges_added: DF.Currency
        base_taxes_and_charges_deducted: DF.Currency
        base_total: DF.Currency
        base_total_taxes_and_charges: DF.Currency
        base_write_off_amount: DF.Currency
        bill_date: DF.Date | None
        bill_no: DF.Data | None
        billing_address: DF.Link | None
        billing_address_display: DF.SmallText | None
        buying_price_list: DF.Link | None
        cash_bank_account: DF.Link | None
        clearance_date: DF.Date | None
        company: DF.Link | None
        contact_display: DF.SmallText | None
        contact_email: DF.SmallText | None
        contact_mobile: DF.SmallText | None
        contact_person: DF.Link | None
        conversion_rate: DF.Float
        cost_center: DF.Link | None
        credit_to: DF.Link
        currency: DF.Link | None
        disable_rounded_total: DF.Check
        discount_amount: DF.Currency
        due_date: DF.Date | None
        from_date: DF.Date | None
        grand_total: DF.Currency
        group_same_items: DF.Check
        hold_comment: DF.SmallText | None
        ignore_default_payment_terms_template: DF.Check
        ignore_pricing_rule: DF.Check
        in_words: DF.Data | None
        incoterm: DF.Link | None
        inter_company_invoice_reference: DF.Link | None
        is_internal_supplier: DF.Check
        is_old_subcontracting_flow: DF.Check
        is_opening: DF.Literal["No", "Yes"]
        is_paid: DF.Check
        is_return: DF.Check
        is_subcontracted: DF.Check
        items: DF.Table[PurchaseInvoiceItem]
        language: DF.Data | None
        letter_head: DF.Link | None
        mode_of_payment: DF.Link | None
        named_place: DF.Data | None
        naming_series: DF.Literal["ACC-PINV-.YYYY.-", "ACC-PINV-RET-.YYYY.-"]
        net_total: DF.Currency
        on_hold: DF.Check
        only_include_allocated_payments: DF.Check
        other_charges_calculation: DF.TextEditor | None
        outstanding_amount: DF.Currency
        paid_amount: DF.Currency
        party_account_currency: DF.Link | None
        payment_schedule: DF.Table[PaymentSchedule]
        payment_terms_template: DF.Link | None
        per_received: DF.Percent
        plc_conversion_rate: DF.Float
        posting_date: DF.Date
        posting_time: DF.Time | None
        price_list_currency: DF.Link | None
        pricing_rules: DF.Table[PricingRuleDetail]
        project: DF.Link | None
        rejected_warehouse: DF.Link | None
        release_date: DF.Date | None
        remarks: DF.SmallText | None
        represents_company: DF.Link | None
        return_against: DF.Link | None
        rounded_total: DF.Currency
        rounding_adjustment: DF.Currency
        scan_barcode: DF.Data | None
        select_print_heading: DF.Link | None
        set_from_warehouse: DF.Link | None
        set_posting_time: DF.Check
        set_warehouse: DF.Link | None
        shipping_address: DF.Link | None
        shipping_address_display: DF.SmallText | None
        shipping_rule: DF.Link | None
        status: DF.Literal[
            "",
            "Draft",
            "Return",
            "Debit Note Issued",
            "Submitted",
            "Paid",
            "Partly Paid",
            "Unpaid",
            "Overdue",
            "Cancelled",
            "Internal Transfer",
        ]
        subscription: DF.Link | None
        supplied_items: DF.Table[PurchaseReceiptItemSupplied]
        supplier: DF.Link
        supplier_address: DF.Link | None
        supplier_name: DF.Data | None
        supplier_warehouse: DF.Link | None
        tax_category: DF.Link | None
        tax_id: DF.ReadOnly | None
        tax_withheld_vouchers: DF.Table[TaxWithheldVouchers]
        tax_withholding_category: DF.Link | None
        tax_withholding_net_total: DF.Currency
        taxes: DF.Table[PurchaseTaxesandCharges]
        taxes_and_charges: DF.Link | None
        taxes_and_charges_added: DF.Currency
        taxes_and_charges_deducted: DF.Currency
        tc_name: DF.Link | None
        terms: DF.TextEditor | None
        title: DF.Data | None
        to_date: DF.Date | None
        total: DF.Currency
        total_advance: DF.Currency
        total_net_weight: DF.Float
        total_qty: DF.Float
        total_taxes_and_charges: DF.Currency
        unrealized_profit_loss_account: DF.Link | None
        update_billed_amount_in_purchase_order: DF.Check
        update_billed_amount_in_purchase_receipt: DF.Check
        update_outstanding_for_self: DF.Check
        update_stock: DF.Check
        use_company_roundoff_cost_center: DF.Check
        use_transaction_date_exchange_rate: DF.Check
        write_off_account: DF.Link | None
        write_off_amount: DF.Currency
        write_off_cost_center: DF.Link | None
    # end: auto-generated types

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_updater = [
            {
                "source_dt": "Purchase Invoice Item",
                "target_dt": "Purchase Order Item",
                "join_field": "po_detail",
                "target_field": "billed_amt",
                "target_parent_dt": "Purchase Order",
                "target_parent_field": "per_billed",
                "target_ref_field": "amount",
                "source_field": "amount",
                "percent_join_field": "purchase_order",
                "overflow_type": "billing",
            }
        ]
    def on_submit(self):
        # super().on_submit()

        self.check_prev_docstatus()

        if self.is_return and not self.update_billed_amount_in_purchase_order:
            # NOTE status updating bypassed for is_return
            self.status_updater = []

        self.update_status_updater_args()
        self.update_prevdoc_status()

        frappe.get_doc("Authorization Control").validate_approving_authority(
            self.doctype, self.company, self.base_grand_total
        )

        if not self.is_return:
            self.update_against_document_in_jv()
            self.update_billing_status_for_zero_amount_refdoc("Purchase Receipt")
            self.update_billing_status_for_zero_amount_refdoc("Purchase Order")

        self.update_billing_status_in_pr()

        # Updating stock ledger should always be called after updating prevdoc status,
        # because updating ordered qty in bin depends upon updated ordered qty in PO
        if self.update_stock == 1:
            self.make_bundle_for_sales_purchase_return()
            self.make_bundle_using_old_serial_batch_fields()
            # self.update_stock_ledger()

            if self.is_old_subcontracting_flow:
                self.set_consumed_qty_in_subcontract_order()

        # this sequence because outstanding may get -negative
        self.make_gl_entries()

        if self.update_stock == 1:
            self.repost_future_sle_and_gle()

        if frappe.db.get_single_value("Buying Settings", "project_update_frequency") == "Each Transaction":
            self.update_project()

        update_linked_doc(self.doctype, self.name, self.inter_company_invoice_reference)
        self.update_advance_tax_references()

        self.process_common_party_accounting()
                    

    def make_gl_entries(self, gl_entries=None, from_repost=False):
            if not gl_entries:
                gl_entries = self.get_gl_entries()

            if gl_entries:
                update_outstanding = "No" # if (cint(self.is_paid) or self.write_off_account) else "Yes"

                if self.docstatus == 1:
                    make_gl_entries(
                        gl_entries,
                        update_outstanding=update_outstanding,
                        merge_entries=False,
                        from_repost=from_repost,
                    )
                    self.make_exchange_gain_loss_journal()
                elif self.docstatus == 2:
                    provisional_entries = [a for a in gl_entries if a.voucher_type == "Purchase Receipt"]
                    make_reverse_gl_entries(voucher_type=self.doctype, voucher_no=self.name)
                    if provisional_entries:
                        for entry in provisional_entries:
                            frappe.db.set_value(
                                "GL Entry",
                                {"voucher_type": "Purchase Receipt", "voucher_detail_no": entry.voucher_detail_no},
                                "is_cancelled",
                                1,
                            )

                if update_outstanding == "No":
                    update_outstanding_amt(
                        self.credit_to,
                        "Supplier",
                        self.supplier,
                        self.doctype,
                        self.return_against if cint(self.is_return) and self.return_against else self.name,
                    )

            elif self.docstatus == 2 and cint(self.update_stock) and self.auto_accounting_for_stock:
                make_reverse_gl_entries(voucher_type=self.doctype, voucher_no=self.name)



    def make_tax_gl_entries(self, gl_entries):
            # tax table gl entries
            valuation_tax = {}

            for tax in self.get("taxes"):
                amount, base_amount = self.get_tax_amounts(tax, None)
                if tax.category in ("Total", "Valuation and Total") and flt(base_amount):
                    account_currency = get_account_currency(tax.account_head)

                    dr_or_cr = "debit" if tax.add_deduct_tax == "Add" else "credit"

                    account_type = frappe.get_value(
                                        "Account", tax.account_head, "account_type"
                                    )
                    
                    if account_type in ["Payable", "Receivable"]:
                        gl_entries.append(
                        self.get_gl_dict(
                            {
                                "account": tax.account_head,
                                "party_type": tax.party_type,
                                "party": tax.party,
                                "against": self.supplier,
                                dr_or_cr: base_amount,
                                dr_or_cr + "_in_account_currency": base_amount
                                if account_currency == self.company_currency
                                else amount,
                                "cost_center": tax.cost_center,
                            },
                            account_currency,
                            item=tax,
                        )
                    )
                    else:

                        gl_entries.append(
                            self.get_gl_dict(
                                {
                                    "account": tax.account_head,
                                    "against": self.supplier,
                                    dr_or_cr: base_amount,
                                    dr_or_cr + "_in_account_currency": base_amount
                                    if account_currency == self.company_currency
                                    else amount,
                                    "cost_center": tax.cost_center,
                                },
                                account_currency,
                                item=tax,
                            )
                        )
                # accumulate valuation tax
                if (
                    self.is_opening == "No"
                    and tax.category in ("Valuation", "Valuation and Total")
                    and flt(base_amount)
                    and not self.is_internal_transfer()
                ):
                    if self.auto_accounting_for_stock and not tax.cost_center:
                        frappe.throw(
                            _("Cost Center is required in row {0} in Taxes table for type {1}").format(
                                tax.idx, _(tax.category)
                            )
                        )
                    valuation_tax.setdefault(tax.name, 0)
                    valuation_tax[tax.name] += (tax.add_deduct_tax == "Add" and 1 or -1) * flt(base_amount)

            if self.is_opening == "No" and self.negative_expense_to_be_booked and valuation_tax:
                # credit valuation tax amount in "Expenses Included In Valuation"
                # this will balance out valuation amount included in cost of goods sold

                total_valuation_amount = sum(valuation_tax.values())
                amount_including_divisional_loss = self.negative_expense_to_be_booked
                i = 1
                for tax in self.get("taxes"):
                    if valuation_tax.get(tax.name):
                        if i == len(valuation_tax):
                            applicable_amount = amount_including_divisional_loss
                        else:
                            applicable_amount = self.negative_expense_to_be_booked * (
                                valuation_tax[tax.name] / total_valuation_amount
                            )
                            amount_including_divisional_loss -= applicable_amount
                        
                        account_type = frappe.get_value(
                                        "Account", tax.account_head, "account_type"
                                    )
                    
                        if account_type in ["Payable", "Receivable"]:
                            gl_entries.append(
                                self.get_gl_dict(
                                    {
                                        "account": tax.account_head,
                                        "party_type": tax.party_type,
                                        "party": tax.party,
                                        "cost_center": tax.cost_center,
                                        "against": self.supplier,
                                        "credit": applicable_amount,
                                        "remarks": self.remarks or _("Accounting Entry for Stock"),
                                    },
                                    item=tax,
                                )
                            )
                        else:

                            gl_entries.append(
                                self.get_gl_dict(
                                    {
                                        "account": tax.account_head,
                                        "cost_center": tax.cost_center,
                                        "against": self.supplier,
                                        "credit": applicable_amount,
                                        "remarks": self.remarks or _("Accounting Entry for Stock"),
                                    },
                                    item=tax,
                                )
                            )

                        i += 1

            if self.auto_accounting_for_stock and self.update_stock and valuation_tax:
                for tax in self.get("taxes"):
                    if valuation_tax.get(tax.name):
                        account_type = frappe.get_value(
                                        "Account", tax.account_head, "account_type"
                                    )
                    
                        if account_type in ["Payable", "Receivable"]:
                            gl_entries.append(
                            self.get_gl_dict(
                                {
                                    "account": tax.account_head,
                                    "party_type": tax.party_type,
                                    "party": tax.party,
                                    "cost_center": tax.cost_center,
                                    "against": self.supplier,
                                    "credit": valuation_tax[tax.name],
                                    "remarks": self.remarks or _("Accounting Entry for Stock"),
                                },
                                item=tax,
                            )
                        )
                            
                        else:
                            gl_entries.append(
                                self.get_gl_dict(
                                    {
                                        "account": tax.account_head,
                                        "cost_center": tax.cost_center,
                                        "against": self.supplier,
                                        "credit": valuation_tax[tax.name],
                                        "remarks": self.remarks or _("Accounting Entry for Stock"),
                                    },
                                    item=tax,
                                )
                            )

@erpnext.allow_regional
def make_regional_gl_entries(gl_entries, doc):
    return gl_entries
