from datetime import datetime

import frappe
from frappe import _

from elaguiely.apis_v1.utils import get_item_prices


# from elaguiely.apis_v1.jwt_decorator import jwt_required
#
# DOMAINS = frappe.get_active_domains()
# import json


# def on_change(self, event):
#     if 'Elaguiely' in DOMAINS:
#         if self.status_table is None:
#             self.status_table = []
#
#         entry_found = False
#         for entry in self.status_table:
#             if entry.get('status') == self.status:
#                 entry.time = frappe.utils.now()
#                 entry_found = True
#                 break
#
#         if not entry_found:
#             self.append('status_table', {
#                 'status': self.status,
#                 'time': frappe.utils.now(),
#             })
#
# @frappe.whitelist()
# def date_of_submit(self , *args , **kwargs):
#     if 'Elaguiely' in DOMAINS:
#         self.submit_datetime = frappe.utils.now()
#
#
# @frappe.whitelist(allow_guest=False)
# def get_orders( *args , **kwargs):
#     if 'Elaguiely' in DOMAINS:
#         user = frappe.session.user
#         customer = frappe.db.get_value("User" , user , "customer")
#         orders = frappe.get_list("Sales Order" , filters = {'customer':customer } , fields = ['name' , 'creation' , 'status' , 'grand_total'])
#         for order in orders:
#             order['can_edit'] = 1 if order['status'] == 'Draft' else 0
#         return orders
#
#
# @frappe.whitelist(allow_guest=False)
# def get_order( *args , **kwargs):
#     if 'Elaguiely' in DOMAINS:
#         data = {}
#         order = kwargs.get("order")
#         order_obj = frappe.get_doc("Sales Order" , order)
#         items = frappe.db.sql(f"""select b.item_code , b.item_name , b.qty , b.rate , b.amount from `tabSales Order` a join `tabSales Order Item` b on a.name = b.parent where a.name = '{order}'""" , as_dict = 1)
#         date_of_invoice = None
#         date_of_deliverd = None
#         per_billed = order_obj.per_billed
#         if per_billed >0:
#             date_of_invoice = frappe.db.sql(f"""select a.creation from `tabSales Invoice` a join `tabSales Invoice Item` b on a.name = b.parent where b.sales_order = '{order}'""" , as_dict = 1)
#             date_of_invoice = str(date_of_invoice[0].get("creation"))
#
#         per_delivered = order_obj.per_delivered
#         if per_delivered > 0:
#             date_of_deliverd = frappe.db.sql(f"""select a.creation from `tabDelivery Note` a join `tabDelivery Note Item` b on a.name = b.parent where b.against_sales_order = '{order}'""" , as_dict = 1)
#             date_of_deliverd = str(date_of_deliverd[0].get("creation"))
#
#
#
#         data = {
#             'name': order_obj.name,
#             'order_confirmed': order_obj.submit_datetime,
#             "order_on_process":date_of_invoice,
#             "order_on_deliverd":date_of_deliverd,
#             'items': items,
#             "total_amount": order_obj.grand_total
#         }
#         return data


@frappe.whitelist(allow_guest=True)
# @jwt_required
def request_sales_order(**kwargs):
    print('request_sales_order')
    try:
        # Extract CustomerID from the request parameters
        customer_id = kwargs.get("CustomerID")
        if not customer_id:
            frappe.local.response["message"] = _("CustomerID is required")
            frappe.local.response['http_status_code'] = 400
            return

        # Fetch the customer document
        customer = frappe.get_doc("Customer", customer_id)
        if not customer:
            frappe.local.response["message"] = _("Customer not found")
            frappe.local.response['http_status_code'] = 404
            return

        # Fetch the cart associated with this customer
        cart = frappe.get_doc("Cart", {'customer': customer.name}, fields=['*'])
        if not cart or not cart.get("cart_item"):  # Replace 'items' with the actual child table field
            frappe.local.response["message"] = _("Cart is empty or not found")
            frappe.local.response['http_status_code'] = 404
            return

        # Create Sales Order
        sales_order = frappe.new_doc("Sales Order")
        sales_order.customer = customer.name
        sales_order.transaction_date = frappe.utils.nowdate()  # You can customize this
        print(kwargs.get("DeliveryDate"))
        # Convert to datetime object
        date_object = datetime.strptime(kwargs.get("DeliveryDate"), "%d/%m/%Y")

        # Format as YYYY-MM-DD
        formatted_date = date_object.strftime("%Y-%m-%d")

        sales_order.delivery_date = formatted_date

        # Add cart items to the Sales Order items table
        for cart_item in cart.get("cart_item"):  # Replace 'items' with the correct field if different
            uom_prices = get_item_prices(cart_item.item)  # Assuming you get the UOM prices this way

            sales_order.append("items", {
                "item_code": cart_item.item,  # Ensure this field matches the actual one in your Cart item table
                "qty": cart_item.qty,
                "rate": cart_item.rate,
                "uom": cart_item.uom,  # Unit of Measurement, make sure it exists in cart_item
                "conversion_factor": 1,  # Change this based on your UOM data
                "stock_uom": uom_prices[0].get('name') if uom_prices else cart_item.uom,
                "description": cart_item.get('description') or cart_item.get('item_name')
            })

        # Insert the Sales Order into the database
        sales_order.insert()
        sales_order.submit()  # Submitting the order (optional, depending on your workflow)
        print('cart ==> ', cart)
        # Clear the Cart after the Sales Order is created
        cart.set("cart_item", [])  # Clear the items list
        print(cart.cart_item)
        cart.save()  # Save the changes to the cart
        frappe.db.commit()

        # Prepare response data
        frappe.local.response['http_status_code'] = 200
        frappe.local.response["message"] = _("Sales Order created successfully")
        frappe.local.response["sales_order"] = sales_order.name

    except frappe.DoesNotExistError:
        frappe.local.response["message"] = _("Customer does not exist")
        frappe.local.response['http_status_code'] = 404

    except Exception as e:
        frappe.local.response["message"] = _("An error occurred while creating Sales Order")
        frappe.local.response['http_status_code'] = 500
        frappe.local.response["error"] = str(e)
