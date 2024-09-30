import frappe 
from frappe import _ 
from frappe.utils import today
from frappe.utils.data import  get_link_to_form


@frappe.whitelist()
def get_active_domains():
	return frappe.get_active_domains()


DOMAINS = get_active_domains()

@frappe.whitelist()
def create_cart_after_enable_customer(customer):
	print("done")
	existing_cart = frappe.db.exists({
		"doctype": "Cart",
		"name": customer 
	})
	print(existing_cart)
	if not existing_cart:
		cart = frappe.new_doc("Cart")
		cart.date = today()
		cart.customer = customer 
		cart.save(ignore_permissions = True)
		frappe.db.commit()
		frappe.db.set_value("Customer", customer, {'cart_id': customer}) 
		frappe.db.commit()
		frappe.msgprint(f"Cart for customer: {customer} is created successfully.")
	   
def after_insert(self , event):
	# frappe.throw("Action work")
	if 'Elaguiely' in DOMAINS: 
		create_customer(self)

def on_trash(self , event):
	if 'Elaguiely' in DOMAINS:
		if self.customer :
			frappe.throw(_("You must delete customer <b>{0}</b> before").format(self.customer))

def create_customer(self):
	if self.is_customer  and not self.customer:
		selling_settings = frappe.get_single("Selling Settings")
		if not selling_settings.customer_group :
			frappe.throw(_("Please set default customer group in setting"))
		if not selling_settings.territory :
			frappe.throw(_("Please set default territory in setting"))
		# if self.is_customer  and not self.shift :
		#     frappe.throw(_("Please Set User Shift"))
		customer = frappe.new_doc("Customer")
		customer.customer_name = self.username
		# if self.shift :
		#     customer.shift = self.shift
		customer.customer_group = selling_settings.customer_group
		customer.territory = selling_settings.territory
		customer.insert()
		self.customer = customer.name 
		lnk = get_link_to_form(customer.doctype, customer.name)
		frappe.msgprint(_("{} {} was Created").format(
			customer.doctype, lnk))



def create_cart(customer) :
	cart_obj = frappe.db.sql(f""" SELECT name FROM `tabCart` WHERE 
						customer = '{customer}' and docstatus=0
							""",as_dict =1 )
	cart_key =  f"{frappe.session.sid}_{frappe.session.user}_cart"
	if cart_obj and len(cart_obj) > 0 :
		cart = frappe.get_doc("Cart" , cart_obj[0].name )
		frappe.cache().set_value(cart_key, cart)
		# favorite_key = f"{{frappe.session.sid}}_fav"
		return  cart 
	else :
		#create Cart 
		cart = frappe.new_doc("Cart")
		cart.customer = customer 
		cart.save(ignore_permissions = True)
		frappe.db.commit()
		frappe.cache().set_value(cart_key, cart)
		return cart 
	

def create_favorite(customer) :
	obj = frappe.db.sql(f""" SELECT name FROM `tabfavorite` WHERE 
						customer = '{customer}'
							""",as_dict =1 ) 
	fav_key =  f"{frappe.session.sid}_{frappe.session.user}_fav"
	if obj and len(obj) > 0 :
		fav = frappe.get_doc("favorite" , obj[0].name )
		#set to cached data
		frappe.cache().set_value(fav_key, fav)
		return  fav 
	else :
		#create Cart 
		fav = frappe.new_doc("favorite")
		fav.customer = customer 
		fav.save(ignore_permissions = 1)
		frappe.db.commit()
		#set to cached data
		frappe.cache().set_value(fav_key, fav)
		return fav 
	
# /home/frappe/frappe-13/apps/elaguiely/elaguiely/elaguiely/functions
@frappe.whitelist(allow_guest=False)
def create_sales_order(cart):
	try:
		if 'Elaguiely' in DOMAINS:
			if frappe.db.exists("Cart" ,cart ):
				cart_obj = frappe.get_doc("Cart" , cart)
				order_obj = frappe.new_doc("Sales Order")
				order_obj.order_type = "Sales"
				order_obj.cart = cart_obj.name
				order_obj.customer = cart_obj.customer
				order_obj.delivery_date = cart_obj.date or frappe.utils.nowdate()
				order_obj.delivery_date = cart_obj.date or frappe.utils.nowdate()
				order_obj.taxes_and_charges = cart_obj.tax_template
				if cart_obj.get("cart_item"):
					for item in cart_obj.get("cart_item"):
						order_obj.append("items",{
							"item_code": item.item,
							"item_name": item.item_name,
							"description": item.description ,
							"qty": item.qty ,
							"rate": item.rate,
							"amount": item.total,
							"uom": item.uom ,
						})
					cart_obj.set("cart_item", [])
					cart_obj.save(ignore_permissions=True)
					order_obj.save(ignore_permissions = True)
					frappe.db.commit()
				return order_obj.name
	except Exception as er:
		frappe.clear_messages()
		frappe.local.response['http_status_code'] = 401
		frappe.local.response['message'] =_(er)
		frappe.local.response['data'] = []