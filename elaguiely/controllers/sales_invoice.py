import frappe
from frappe import _

DOMAINS = frappe.get_active_domains()



@frappe.whitelist()
def validate(self ,event):
    if 'Elaguiely' in DOMAINS:
        validate_seeling_price_with_role(self)

def validate_seeling_price_with_role(self):
    validate_selling_price_with_role = frappe.db.get_single_value("Selling Settings", "validate_selling_price_with_role")
    if validate_selling_price_with_role == 1:
        
        roles = frappe.get_list("Roles Validation Selling",{"parent": "Selling Settings"}, pluck="role")
        user_roles = frappe.get_roles()
        
        items = self.get('items')
        if self.selling_price_list:
            for item in items:
                if item.rate < float(get_purchase_rate(item.item_code) or 0):
                    if not any(role in roles for role in user_roles):
                        # frappe.throw(_("You are not allowed to create sales invoice"))
                        frappe.throw(_("Item {0} price is greater than selling price list").format(item.item_code))



def get_purchase_rate(item_code):
    purchase_rate = frappe.db.get_value("Item", item_code, "last_purchase_rate")
    return purchase_rate