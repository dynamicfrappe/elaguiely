from . import __version__ as app_version

app_name = "elaguiely"
app_title = "elaguiely"
app_publisher = "elaguiely"
app_description = "elaguiely"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "elaguiely"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/elaguiely/css/elaguiely.css"
# app_include_js = "/assets/elaguiely/js/elaguiely.js"

# include js, css files in header of web template
# web_include_css = "/assets/elaguiely/css/elaguiely.css"
# web_include_js = "/assets/elaguiely/js/elaguiely.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "elaguiely/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	"Customer" : "public/js/customer.js"
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

# before_install = "elaguiely.install.before_install"
# after_install = "elaguiely.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "elaguiely.uninstall.before_uninstall"
# after_uninstall = "elaguiely.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "elaguiely.notifications.get_notification_config"

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

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"User": {
		"on_trash": "elaguiely.elaguiely.functions.on_trash"
	},
    "Sales Order": {
		"validate": [
            "elaguiely.apis.sales_order.on_change",
            "elaguiely.apis.sales_order.date_of_submit",
            ],
	},
	"Customer": {
		"on_update": "elaguiely.elaguiely.functions.create_cart_after_enable_customer",
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"elaguiely.tasks.all"
#	],
#	"daily": [
#		"elaguiely.tasks.daily"
#	],
#	"hourly": [
#		"elaguiely.tasks.hourly"
#	],
#	"weekly": [
#		"elaguiely.tasks.weekly"
#	]
#	"monthly": [
#		"elaguiely.tasks.monthly"
#	]
# }

# Testing
# -------

# before_tests = "elaguiely.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	"AllZone": "elaguiely.ts_api.get_all_zones",
	"AllCity": "elaguiely.ts_api.get_all_cities",
	"AllCusClass": "elaguiely.ts_api.get_customer_class",
	"CustomerReg": "elaguiely.ts_api.get_customer_profile",
	"BestSellerItems": "elaguiely.ts_api.get_best_seller_items",
	"EmployeeInvoice": "elaguiely.ts_api.get_invoice",
	"Survey": "elaguiely.ts_api.evaluate_order",
	"OrderHistory": "elaguiely.ts_api.cancel_order",
	"ItemsSearch": "elaguiely.ts_api.get_items_serach_list",
	"AllGov": "elaguiely.ts_api.get_all_governs",
	# "Category": "elaguiely.ts_api.get_categories",
	# "SaveShoppingCart" : "elaguiely.ts_api.save_shopping_cart",

	# Auth Routing
	"login_user": "elaguiely.apis_v1.auth.login",
	"CustomerReg": "elaguiely.apis_v1.auth.register",
	"ItemsPrice": "elaguiely.apis_v1.item.get_items_prices",
	"Supplier": "elaguiely.apis_v1.supplier.get_all_suppliers",
	"CategoryBySupplier": "elaguiely.apis_v1.supplier.get_category_by_supplier",
	"Category": "elaguiely.apis_v1.category.get_categories",
	"SaveShoppingCart" : "elaguiely.apis_v1.cart.save_shopping_cart",
	"Cart": "elaguiely.apis_v1.cart.cart_details",
	"DeleteShoppingCart": "elaguiely.apis_v1.cart.clear_shopping_cart",
	"CreateOrder": "elaguiely.apis_v1.sales_order.request_sales_order",
	"OrderHistory": "elaguiely.apis_v1.sales_order.get_order_list",
	"EmployeeInvoice": "elaguiely.apis_v1.sales_order.get_order_details",
    # "CancelOrder":"elaguiely.apis_v1.sales_order.cancel_order",
    # "ReOrder":"elaguiely.apis_v1.sales_order.reorder",
    
}

#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "elaguiely.task.get_dashboard_data"
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
#	"elaguiely.auth.validate"
# ]
after_install =[ "elaguiely.install.setup"]
after_migrate =[ "elaguiely.install.setup"]
domains = {
    "Elaguiely" : 'elaguiely.domains.elaguiely'
}