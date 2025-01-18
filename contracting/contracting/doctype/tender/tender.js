// Copyright (c) 2024, kazem and contributors
// For license information, please see license.txt

frappe.ui.form.on('Tender', {
	setup: function(frm) {

		frm.set_query("contracting_item", "contracting_items", function (frm, cdt, cdn) {
			var row = locals[cdt][cdn];
			return {
				filters: {
					item_group : row.contracting_item_group
				
				},
			};
		});
	},
	refresh: function(frm){
		if (!frm.doc.__islocal ){
		frm.add_custom_button(__("Create Quotation"), () => {
			let items = []

			frm.doc.contracting_items.forEach(function(row) {
				items.push({
								is_group:row.is_group,
								status:row.status,
								series:row.series,
								contracting_item_group:row.contracting_item_group,
								contracting_item:row.contracting_item,
								uom:row.uom,
								qty:row.qty,
								rate:row.rate,
								description: row.description
				});
			});
	
		frappe.model.open_mapped_doc({
			method: "contracting.contracting.doctype.tender.tender.create_quotation",
			frm: cur_frm,
			args: {
				"party_name" : frm.doc.customer,
				"project": frm.doc.project,
				"tender" :frm.doc.name,
				"item": items
			
			}
		})
		})

		frm.add_custom_button(__("Create Journal Entry"), () => {

			let dialog = new frappe.ui.Dialog({
				title: __("Select Date"),
				fields: [
				  {
					fieldname: "credit_account",
					label: __("Credit Account"),
					fieldtype: "Link",
					options:"Account",
					reqd: 1
					
				  },
				  {
					fieldname: "amount",
					label: __("Amount"),
					fieldtype: "Currency",
					reqd: 1,
					default: frm.doc.tender_document_cost,
				  }
				],
				primary_action(data) {
				  frappe.call({
					method: "create_journal_entry",
					doc: frm.doc,
					args: {
						credit_account: data.credit_account,
						amount: data.amount,

					},
					callback: function (r) {
					  frm.refresh();
					},
				  });
	
				  dialog.hide();
				},
				
				primary_action_label: __("Create"),});
			dialog.show();
			
		})
	}
	frm.add_custom_button(__("Create Items"), () => {
		frappe.call({
			doc:frm.doc,
			method: "create_items",
			callback: function (r) {
			}
		});
	})}}
);

frappe.ui.form.on("Contracting Items Child", {
	
	cost_setup:async function(frm, cdt, cdn){
		var d = locals[cdt][cdn];
		frappe.model.open_mapped_doc({
			method: "contracting.contracting.doctype.tender.tender.make_costing_node",
			frm: cur_frm,
			args: {
				"customer" : frm.doc.customer,
				"project": frm.doc.project,
				"tender" :frm.doc.name,
				"row":d.name,
				"item": d.contracting_item,
				"group":d.contracting_item_group,
				"uom":d.uom,
				"qty":d.qty
			}
		})
	},


});


