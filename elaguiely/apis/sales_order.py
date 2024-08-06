import frappe
from frappe import _
DOMAINS = frappe.get_active_domains()
import json


def on_change(self, event):
    if 'Elaguiely' in DOMAINS:
        if self.status_table is None:
            self.status_table = []

        entry_found = False
        for entry in self.status_table:
            if entry.get('status') == self.status:
                entry.time = frappe.utils.now()
                entry_found = True
                break

        if not entry_found:
            # self.db_set("status_table",{
            #     'status': self.status,
            #     'time': frappe.utils.now(),
            # })
            self.append('status_table', {
                'status': self.status,
                'time': frappe.utils.now(),
            })


@frappe.whitelist(allow_guest=False)
def get_orders( *args , **kwargs):
    if 'Elaguiely' in DOMAINS:
        user = frappe.session.user
        customer = frappe.db.get_value("User" , user , "customer")
        orders = frappe.get_list("Sales Order" , filters = {'customer':customer } , fields = ['name' , 'creation' , 'status' , 'grand_total'])
        for order in orders:
            order['can_edit'] = 1 if order['status'] == 'Draft' else 0
        return orders
    

@frappe.whitelist(allow_guest=False)
def get_order( *args , **kwargs):
    if 'Elaguiely' in DOMAINS:
        data = {}
        order = kwargs.get("order")
        sql = f"""
            SELECT 
                si.name,
                si.status
            """
        order_obj = frappe.get_doc("Sales Order" , order)
        data = {
            'name': order_obj.name,
            'status_log': order_obj.status_table,
            'items': order_obj.items,
        }
        return data
    
