import frappe
from frappe import _
DOMAINS = frappe.get_active_domains()
import json


@frappe.whitelist(allow_guest=False)
def get_orders(filters = {} , *args , **kwargs):
    if 'Elaguiely' in DOMAINS:
        temp = None
        if filters.get("customer") :
            temp = "hi"
        return temp