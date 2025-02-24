import frappe
from frappe import _


DOMAINS = frappe.get_active_domains()


@frappe.whitelist()
def validate(self ,event):
    if 'Elaguiely' in DOMAINS:
        valid_max_qty(self)



def valid_max_qty(self):#noha
             items = self.get('items')
             for cart_item in items: 
                   # Validate Item Quantity
                    max_qty = frappe.get_value("UOM Conversion Detail", filters={'parent': cart_item.item_code, 'uom': cart_item.uom}, fieldname='maximum_qty')
                    if int(cart_item.qty) >= max_qty  &  max_qty>0:
                        frappe.throw(_(f"Quantity required is higher than  allowed quantity for item: {cart_item.item_code} max quantity can order is {max_qty} unit{cart_item.uom}"))
                        