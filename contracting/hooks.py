from . import __version__ as app_version

app_name = "contracting"
app_title = "Contracting"
app_publisher = "kazem"
app_description = "contracting"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "kazemaraby@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/contracting/css/contracting.css"
# app_include_js = "/assets/contracting/js/contracting.js"

# include js, css files in header of web template
# web_include_css = "/assets/contracting/css/contracting.css"
# web_include_js = "/assets/contracting/js/contracting.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "contracting/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
              "Quotation":"public/js/quotation.js",
              "Contract Document" : "public/js/contract_document.js",
              "Material Request" : "public/js/material_request.js",
              "Purchase Order" : "public/js/purchase_order.js",
              "Purchase Invoice" : "public/js/purchase_invoice.js",
              "Sales Invoice" : "public/js/sales_invoice.js",
              "Task" : "public/js/task.js"
            }

# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "contracting.install.before_install"
# after_install = "contracting.contracting.api.install_app_requirements"
after_migrate=["contracting.contracting.api.install_app_requirements"]
# Uninstallation
# ------------

# before_uninstall = "contracting.uninstall.before_uninstall"
# after_uninstall = "contracting.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "contracting.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Quotation": "contracting.contracting.overrides.quotation.Quotation",
    "Purchase Invoice": "contracting.contracting.overrides.purchase_invoice.CustomPurchaseInvoice",
    "Sales Invoice": "contracting.contracting.overrides.sales_invoice.CustomSalesInvoice"
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    # "Project":{
    # "on_update":"contracting.contracting.project.re_calc_cost"
	# },
    "Task":{
    "validate":"contracting.contracting.controllers.task.merge_items"
	},
    
     "Purchase Order":{
		"validate":"contracting.contracting.controllers.purchase_order.validate_items_qty",
        "on_submit":"contracting.contracting.controllers.material_request.update_remaining_qty_on_submit",
		"on_cancel":"contracting.contracting.controllers.material_request.restore_qty_on_cancel_or_delete"
	},
     "Material Request":{
		"validate":"contracting.contracting.controllers.material_request.validate_items_qty",
		"on_submit":"contracting.contracting.controllers.material_request.update_remaining_qty_on_submit",
		"on_cancel":"contracting.contracting.controllers.material_request.restore_qty_on_cancel_or_delete",
        # "before_save":"contracting.contracting.controllers.material_request.get_project_type"
        
	},
      "Quotation":{
		"validate":"contracting.contracting.controllers.quotation.calculate_totals"
	},
    "Sales Invoice":{
		"on_submit":"contracting.contracting.controllers.sales_invoice.update_remaining_qty_on_submit",
        "on_cancel":"contracting.contracting.controllers.sales_invoice.restore_qty_on_cancel_or_delete"
        
	},
    "Purchase Invoice":{
		"on_submit":"contracting.contracting.controllers.sales_invoice.update_remaining_qty_on_submit",
        "on_cancel":"contracting.contracting.controllers.sales_invoice.restore_qty_on_cancel_or_delete"
        
	}

#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"contracting.tasks.all"
#	],
#	"daily": [
#		"contracting.tasks.daily"
#	],
#	"hourly": [
#		"contracting.tasks.hourly"
#	],
#	"weekly": [
#		"contracting.tasks.weekly"
#	]
#	"monthly": [
#		"contracting.tasks.monthly"
#	]
# }

# Testing
# -------

# before_tests = "contracting.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "contracting.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Project": "contracting.contracting.overrides.project_dashboard.get_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"contracting.auth.validate"
# ]

