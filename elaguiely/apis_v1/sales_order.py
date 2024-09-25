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
            self.append('status_table', {
                'status': self.status,
                'time': frappe.utils.now(),
            })

@frappe.whitelist()
def date_of_submit(self , *args , **kwargs):
    if 'Elaguiely' in DOMAINS:
        self.submit_datetime = frappe.utils.now()


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
        order_obj = frappe.get_doc("Sales Order" , order)
        items = frappe.db.sql(f"""select b.item_code , b.item_name , b.qty , b.rate , b.amount from `tabSales Order` a join `tabSales Order Item` b on a.name = b.parent where a.name = '{order}'""" , as_dict = 1)
        date_of_invoice = None
        date_of_deliverd = None
        per_billed = order_obj.per_billed
        if per_billed >0:
            date_of_invoice = frappe.db.sql(f"""select a.creation from `tabSales Invoice` a join `tabSales Invoice Item` b on a.name = b.parent where b.sales_order = '{order}'""" , as_dict = 1)
            date_of_invoice = str(date_of_invoice[0].get("creation"))

        per_delivered = order_obj.per_delivered
        if per_delivered > 0:
            date_of_deliverd = frappe.db.sql(f"""select a.creation from `tabDelivery Note` a join `tabDelivery Note Item` b on a.name = b.parent where b.against_sales_order = '{order}'""" , as_dict = 1)
            date_of_deliverd = str(date_of_deliverd[0].get("creation"))



        data = {
            'name': order_obj.name,
            'order_confirmed': order_obj.submit_datetime,
            "order_on_process":date_of_invoice,
            "order_on_deliverd":date_of_deliverd,
            'items': items,
            "total_amount": order_obj.grand_total
        }
        return data
    
