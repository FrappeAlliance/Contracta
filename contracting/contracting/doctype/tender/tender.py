# Copyright (c) 2024, kazem and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe.model.document import Document
from erpnext.accounts.utils import get_balance_on
from frappe.model.mapper import get_mapped_doc
from frappe import _
from erpnext import get_company_currency, get_default_company
from frappe.utils import today

class Tender(Document):
    def validate(self):
        self.item_group_series()

  

    @frappe.whitelist()
    def create_journal_entry(self,credit_account,amount):
        je = frappe.new_doc("Journal Entry")
        je.posting_date = today()
        je.tender = self.name
        debit_account = frappe.get_value("Contracting Settings","Contracting Settings","expense_debit_account")

        if not debit_account:
            frappe.throw(_("Please set expense debit account in the settings"))

        je.append("accounts",
                  {
                      "account": credit_account,
                      "credit_in_account_currency":amount,
                      "project":  self.project
                  })
        je.append("accounts",
                  {
                      "account": debit_account,
                      "debit_in_account_currency":amount,
                      "project":  self.project

                  })
        
        je.insert()
        link_to_je = frappe.utils.get_url_to_form("Journal Entry", je.name)
        frappe.msgprint(
            _("Journal Entry created successfully. <a href='{0}'>{1}</a>").format(link_to_je, je.name),
            alert=True,
            indicator="green",
        )
    

    @frappe.whitelist()
    def create_items(self):
        for item in self.contracting_items:
            if  item.contracting_item_group:
                if not frappe.db.exists("Item Group" , item.contracting_item_group):
                    group = frappe.new_doc("Item Group")
                    group.item_group_name = item.contracting_item_group
                    group.insert()
                    group = group.name
                    frappe.msgprint(
                _("Item Group created successfully."),
                alert=True,
                indicator="green",
                    )
                else:
                    group = item.contracting_item_group

    
            
            if  item.contracting_item:
                if not frappe.db.exists("Item" , item.contracting_item):
                    nitem = frappe.new_doc("Item")
                    nitem.item_code = item.contracting_item
                    nitem.stock_uom = item.uom
                    nitem.item_group = group
                    nitem.insert()

                    frappe.msgprint(
                    _("Item created successfully."),
                    alert=True,
                    indicator="green",
                )
    


    def item_group_series(self):
        group_series_map = {}
        next_series = 1  # Initialize next_series for group items
        next_series_map = {}  # Initialize next_series_map for non-group items
        
        for idx, item in enumerate(self.contracting_items):
            is_group = item.get('is_group')
            item_group = item.get('contracting_item_group')
            
            if is_group:
                if item_group not in group_series_map:
                    group_series_map[item_group] = next_series
                    next_series += 1
                item.series = group_series_map[item_group]
            else:
                if item_group in next_series_map:
                    item.series = f"{group_series_map[item_group]}-{next_series_map[item_group]}"
                else:
                    if item_group not in group_series_map:
                        frappe.throw(str("Please set parent for this group"))
                    item.series = f"{group_series_map[item_group]}-1"
                    next_series_map[item_group] = 1
                next_series_map[item_group] += 1


@frappe.whitelist()
def create_quotation(source_name, target_doc=None):
    doc = frappe.new_doc("Quotation")
    doc.project =frappe.flags.args.project
    doc.party_name =frappe.flags.args.party_name
    doc.tender =frappe.flags.args.tender
    doc.from_tender = 1
    doc.conversion_rate = 1
    doc.plc_conversion_rate = 1
    doc.price_list_currency = erpnext.get_company_currency(erpnext.get_default_company())

    for x in frappe.flags.args.item:
        doc.append("tender_items",{
                        "is_group":x.get("is_group"),
                        "status":x.get("status"),
                        "series":x.get("series"),
                        "contracting_item_group":x.get("contracting_item_group"),
                        "contracting_item":x.get("contracting_item"),
                        "uom":x.get("uom"),
                        "qty":x.get("qty"),
                        "rate":x.get("rate"),
                        "description": x.get("description")
 
            } )


    return doc


@frappe.whitelist()
def make_costing_node(source_name, target_doc=None):
    doc = frappe.new_doc("Costing Note")
    doc.tender = frappe.flags.args.tender
    doc.customer = frappe.flags.args.customer
    doc.project = frappe.flags.args.project
    doc.unit = frappe.flags.args.uom
    doc.item = frappe.flags.args.item
    doc.contracting_item_group =frappe.flags.args.group
    doc.row = frappe.flags.args.row
    doc.project_qty = frappe.flags.args.qty

    return doc