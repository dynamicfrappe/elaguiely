import frappe
from frappe import _


DOMAINS = frappe.get_active_domains()


@frappe.whitelist()
def validate(self ,event):
    if 'Elaguiely' in DOMAINS:
        validate_seeling_price_with_role(self)
        valid_max_qty(self)

def get_user_roles(user):
    roles = frappe.get_all('Has Role', filters={'parent': user}, fields=['role'])
    role_names = [role['role'] for role in roles]
    return role_names



def validate_seeling_price_with_role(self):
    validate_selling_price_with_role = frappe.db.get_single_value("Selling Settings", "validate_selling_price_with_role")
    if validate_selling_price_with_role == 1:
        roles = frappe.get_list("Roles Validation Selling",{"parent": "Selling Settings"}, pluck="role")
        user = frappe.session.user        
        items = self.get('items')
        user_roles = get_user_roles(user)
        if self.selling_price_list:
            for item in items:
                if item.rate < float(get_price_list_rate(item.item_code) or 0):
                    if not any(role in roles for role in user_roles):
                        # frappe.throw(_("You are not allowed to create sales invoice"))
                        frappe.throw(_("Item {0} price is greater than selling price list").format(item.item_code))




def get_price_list_rate(item_code):
    rate_doc = frappe.get_last_doc('Item Price', filters={"item_code": item_code, "price_list": "Standard Buying"})
    
    if rate_doc:
        return rate_doc.price_list_rate  
    else:
        return None  

def valid_max_qty(self):#noha
             items = self.get('items')
             for cart_item in items: 
                   # Validate Item Quantity
                    max_qty = int(frappe.get_value("UOM Conversion Detail", filters={'parent': cart_item.item_code, 'uom': cart_item.uom}, fieldname='maximum_qty') or 0)
                    if int(cart_item.qty) > max_qty  &  max_qty>0:
                        frappe.throw(_(f"Quantity required is higher than  allowed quantity for item: {cart_item.item_code} max quantity can order is {max_qty}"))
                        