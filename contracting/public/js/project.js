// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt
frappe.ui.form.on("Project", {
	set_seriesline:function(frm){
		//console.log("hello",frm.doc.contracting_items_child)
		var index = 0
		var subindex = 1
        for(let i=0;i<frm.doc.contracting_items_child.length ; i++){
         
         
            if(frm.doc.contracting_items_child[i].is_group == 1){
				    index +=1 
					subindex = 1
					frm.doc.contracting_items_child[i].series = index
					
                    
            }else{
                
				frm.doc.contracting_items_child[i].series = index + "_" + subindex
				subindex = subindex +1
            }
             
        }
         frm.refresh_field("contracting_items_child")
    },
	validate(frm){
		if(frm.doc.contracting_items_child){
			frm.events.calc_totals(frm)
		}
	},
	after_save(frm){
		frappe.call({
			method:"contracting.contracting.api.calculate_qty",
			args:{
				"doc":frm.doc
			}
		})
	},
	calc_totals:(frm)=>{
		// var values_list = []
		var obj = {}
		frm.clear_table("items_summary")
		for(let i=0;i<frm.doc.contracting_items_child.length;i++){
			if(frm.doc.contracting_items_child[i].is_group == 0){
				if(obj[frm.doc.contracting_items_child[i].contracting_item_group] > 0){
			obj[frm.doc.contracting_items_child[i].contracting_item_group] += parseFloat(frm.doc.contracting_items_child[i].total)
				}else{
					obj[frm.doc.contracting_items_child[i].contracting_item_group] =parseFloat(frm.doc.contracting_items_child[i].total)
				}
			}
		}
		for(let i=0;i<frm.doc.contracting_items_child.length;i++){
			if(frm.doc.contracting_items_child[i].is_group){
					var row = cur_frm.add_child("items_summary");
					row.contracting_item_group = frm.doc.contracting_items_child[i].contracting_item_group
					row.total = obj[frm.doc.contracting_items_child[i].contracting_item_group]
			
			}
		}
	
		cur_frm.refresh_field("items_summary")
	},
	setup(frm) {
		frm.make_methods = {
			'Timesheet': () => {
				open_form(frm, "Timesheet", "Timesheet Detail", "time_logs");
			},
			'Purchase Order': () => {
				open_form(frm, "Purchase Order", "Purchase Order Item", "items");
			},
			'Purchase Receipt': () => {
				open_form(frm, "Purchase Receipt", "Purchase Receipt Item", "items");
			},
			'Purchase Invoice': () => {
				open_form(frm, "Purchase Invoice", "Purchase Invoice Item", "items");
			},
		};
	},
	onload: function (frm) {
		const so = frm.get_docfield("sales_order");
		so.get_route_options_for_new_doc = () => {
			if (frm.is_new()) return;
			return {
				"customer": frm.doc.customer,
				"project_name": frm.doc.name
			};
		};

		frm.set_query('customer', 'erpnext.controllers.queries.customer_query');

		frm.set_query("user", "users", function () {
			return {
				query: "erpnext.projects.doctype.project.project.get_users_for_project"
			};
		});

		// sales order
		frm.set_query('sales_order', function () {
			var filters = {
				'project': ["in", frm.doc.__islocal ? [""] : [frm.doc.name, ""]]
			};

			if (frm.doc.customer) {
				filters["customer"] = frm.doc.customer;
			}

			return {
				filters: filters
			};
		});
	},

	refresh: function (frm) {

		frm.fields_dict["contracting_items_child"].grid.get_field("contracting_items").get_query = function(doc, cdt, cdn) {
			var child = locals[cdt][cdn];
			return {    
				filters:[
					["item_group", '=', child["contracting_item_group"]]
				]
			}
		}
		
		if (frm.doc.__islocal) {
			frm.web_link && frm.web_link.remove();
		} else {
			frm.add_web_link("/projects?project=" + encodeURIComponent(frm.doc.name));

			frm.trigger('show_dashboard');
		}
		frm.events.set_buttons(frm);
	},

	set_buttons: function(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__('Create Costing Note'), () => {
				frappe.model.open_mapped_doc({
					method: "contracting.contracting.api.create_costing_note",
					frm: cur_frm
				})
			},__('Create'));
			
			frm.add_custom_button(__('Bank Gurantee'), () => {
				frappe.model.open_mapped_doc({
					method: "contracting.contracting.api.create_bank_gurantee",
					frm: cur_frm
				})
			},__('Create'));
			frm.add_custom_button(__('Payment Entry'), () => {
				frappe.model.open_mapped_doc({
					method: "contracting.contracting.api.create_payment_entry",
					frm: cur_frm
				})
			},__('Create'));
			
			frm.add_custom_button(__('Create Quotation'), () => {
				frappe.model.open_mapped_doc({
					method: "contracting.contracting.api.create_quotation",
					frm: cur_frm
				})
			},__('Create'));
			frm.add_custom_button(__('Duplicate Project with Tasks'), () => {
				frm.events.create_duplicate(frm);
			});

			frm.add_custom_button(__('Completed'), () => {
				frm.events.set_status(frm, 'Completed');
			}, __('Set Status'));

			frm.add_custom_button(__('Cancelled'), () => {
				frm.events.set_status(frm, 'Cancelled');
			}, __('Set Status'));


			if (frappe.model.can_read("Task")) {
				frm.add_custom_button(__("Gantt Chart"), function () {
					frappe.route_options = {
						"project": frm.doc.name
					};
					frappe.set_route("List", "Task", "Gantt");
				});

				frm.add_custom_button(__("Kanban Board"), () => {
					frappe.call('erpnext.projects.doctype.project.project.create_kanban_board_if_not_exists', {
						project: frm.doc.name
					}).then(() => {
						frappe.set_route('List', 'Task', 'Kanban', frm.doc.project_name);
					});
				});
			}
		}


	},

	create_duplicate: function(frm) {
		return new Promise(resolve => {
			frappe.prompt('Project Name', (data) => {
				frappe.xcall('erpnext.projects.doctype.project.project.create_duplicate_project',
					{
						prev_doc: frm.doc,
						project_name: data.value
					}).then(() => {
					frappe.set_route('Form', "Project", data.value);
					frappe.show_alert(__("Duplicate project has been created"));
				});
				resolve();
			});
		});
	},

	set_status: function(frm, status) {
		frappe.confirm(__('Set Project and all Tasks to status {0}?', [status.bold()]), () => {
			frappe.xcall('erpnext.projects.doctype.project.project.set_project_status',
				{project: frm.doc.name, status: status}).then(() => { /* page will auto reload */ });
		});
	},
	project_amount:(frm)=>{
		//frm.doc.final_insurance_amount =
		let insurance_amount = frm.doc. project_amount * frm.doc.final_insurance_percentage / 100
		frm.set_value("final_insurance_amount",insurance_amount)
		frm.refresh_field("final_insurance_amount")
	},
	final_insurance_percentage:(frm)=>{
		//frm.doc.final_insurance_amount =
		let insurance_amount = frm.doc. project_amount * frm.doc.final_insurance_percentage / 100
		frm.set_value("final_insurance_amount",insurance_amount)
		frm.refresh_field("final_insurance_amount")
	}


    

});

function open_form(frm, doctype, child_doctype, parentfield) {
	frappe.model.with_doctype(doctype, () => {
		let new_doc = frappe.model.get_new_doc(doctype);

		// add a new row and set the project
		let new_child_doc = frappe.model.get_new_doc(child_doctype);
		new_child_doc.project = frm.doc.name;
		new_child_doc.parent = new_doc.name;
		new_child_doc.parentfield = parentfield;
		new_child_doc.parenttype = doctype;
		new_doc[parentfield] = [new_child_doc];
		new_doc.project = frm.doc.name;

		frappe.ui.form.make_quick_entry(doctype, null, null, new_doc);
	});

}
frappe.ui.form.on("Contracting Items Child",{
	
    is_group:(frm,cdt,cdn)=>{
        frm.events.set_seriesline(frm);
    },
    contracting_items_child_add(frm,cdt,cdn){
        frm.events.set_seriesline(frm);
    },
	qty:(frm,cdt,cdn)=>{
		var row = locals[cdt][cdn]
		row.total = row.qty * row.price
		frm.refresh_field("contracting_items_child")
	},
	price:(frm,cdt,cdn)=>{
		var row = locals[cdt][cdn]
		row.total = row.qty * row.price
		frm.refresh_field("contracting_items_child")
	},
	contracting_items_child_add:(frm,cdt,cdn)=>{
		var row = locals[cdt][cdn]
		var lc = cdn.split("-")
		if(lc[4] > 1){
			let  index  = lc[4] -1 ;
			let prev_cdn = "new-contracting-items-child-" + index; 
			var prev_row = locals[cdt][prev_cdn]
			row.contracting_item_group = prev_row.contracting_item_group
			frm.refresh_fields("contracting_items_child")
		}
	}
})