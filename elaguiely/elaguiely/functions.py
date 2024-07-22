import frappe 
from frappe import _ 
from frappe.utils.data import  get_link_to_form 

DOMAINS = frappe.get_active_domains()


       
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