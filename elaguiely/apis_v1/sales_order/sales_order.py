from crypt import methods
from datetime import datetime

import frappe
from frappe import _
from frappe.utils import today

from elaguiely.apis_v1.jwt_decorator import jwt_required
from elaguiely.apis_v1.utils import get_item_prices, stock_qty


@frappe.whitelist(allow_guest=True)
@jwt_required
def request_sales_order(**kwargs):
    try:
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
        # validate the maximum number of orders allowed
        daily_orders = frappe.db.get_all("Sales Order", filters={'customer': customer_id, 'transaction_date': today()}, fields=['name'])
        default_maximum_daily = frappe.db.get_single_value("Selling Settings", 'maximum_orders')
        special_maximum_daily = frappe.get_value("Customer", customer_id, 'maximum_orders')
        maximum_daily = special_maximum_daily if special_maximum_daily != 0 else default_maximum_daily
        if len(daily_orders) >= maximum_daily:
            frappe.local.response["message"] = _("Customer reached the maximum number of ordered allowed.")
            frappe.local.response['http_status_code'] = 300
            return

        # Validate the minimum amount of the order
        
        # Fetch the cart associated with this customer
        cart = frappe.get_doc("Cart", {'customer': customer.name}, fields=['*'])
        if not cart or not cart.get("cart_item"):  # Replace 'items' with the actual child table field
            frappe.local.response["message"] = _("Cart is empty or not found")
            frappe.local.response['http_status_code'] = 404
            return

        # Create Sales Order
        sales_order = frappe.new_doc("Sales Order")
        sales_order.customer = customer.name
        sales_order.transaction_date = frappe.utils.now()  # You can customize this
        sales_order.posa_notes = kwargs.get("notes")

        # Convert to datetime object
        date_object = datetime.strptime(kwargs.get("DeliveryDate"), "%Y-%m-%d")

        # Format as YYYY-MM-DD
        formatted_date = date_object.strftime("%Y-%m-%d")
        sales_order.delivery_date = formatted_date

        total_amount = 0.0
        # Add cart items to the Sales Order items table
        for cart_item in cart.get("cart_item"):  # Replace 'items' with the correct field if different

            # Validate Item Quantity
            qty = int(stock_qty(customer_id, cart_item.item or 0 ))
            max_qty = frappe.get_value("UOM Conversion Detail", filters={'parent': cart_item.item, 'uom': cart_item.uom}, fieldname='maximum_qty')
            max_qty = qty if max_qty == 0 else max_qty
            if not(int(cart_item.qty) <= qty and int(cart_item.qty) <= max_qty):
                frappe.local.response["message"] = _(f"Quantity required is higher than stock quantity or the allowed quantity for item: {cart_item.item}")
                frappe.local.response['http_status_code'] = 404
                return

            # Calculate the total amount
            total_amount += (float(cart_item.qty) * float(cart_item.rate))

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
        minimum_amount = frappe.db.get_single_value("Selling Settings", 'minimum_amount')
        if total_amount < minimum_amount:
            frappe.local.response["message"] = _(f"Total amount of the order should be more than the minimum amount.")
            frappe.local.response['http_status_code'] = 404
            return
            # print('sales_order ==> ', sales_order)
        sales_order.insert(ignore_permissions=True)
        # sales_order.submit()  # Submitting the order (optional, depending on your workflow)
        # Clear the Cart after the Sales Order is created
        cart.set("cart_item", [])  # Clear the items list
        cart.save()  # Save the changes to the cart
        frappe.db.commit()
        # Prepare response data
        frappe.local.response['http_status_code'] = 200
        frappe.local.response["data"] = _("Sales Order created successfully")
        frappe.local.response["sales_order"] = sales_order.name

    except frappe.DoesNotExistError:
        frappe.local.response["message"] = _("Customer does not exist")
        frappe.local.response['http_status_code'] = 404

    except Exception as e:
        frappe.local.response["message"] = _("An error occurred while creating Sales Order")
        frappe.local.response['http_status_code'] = 500
        frappe.local.response["error"] = str(e)


def map_status_name(status):
    status_map = {
        "Draft": "معلق",
        "Submitted": "تم التأكيد",
        "Completed": "تم التسليم",
    }
    return status_map.get(status, "معلق")


def map_status_name_eng(status):
    status_map_eng = {
        "Draft": "Pending",
        "Submitted": "Confirmed",
        "Completed": "Delivered",
        # Add more status mappings in English as needed
    }
    return status_map_eng.get(status, "Pending")


def get_status_color(status):
    color_map = {
        "Draft": "InProgress",
        "Submitted": "Completed",
        "Completed": "Completed",
    }
    return color_map.get(status, "NotStarted")


def get_status_code(status):
    status_code_map = {
        "Draft": 1,
        "On Hold": 1,
        "To Deliver and Bill": 2,
        "To Bill": 2,
        "To Deliver": 2,
        "To Bill To Deliver": 2,
        "Completed": 6,
        'Cancelled': 7
    }
    return status_code_map.get(status, 1)


def format_date(date):
    return date.strftime("%d-%m-%Y %I:%M %p") if date else ""


def get_order_status_list(current_status):
    status_list = [
        {
            "ID": 1,
            "OrderStatusName": "معلق",
            "OrderStatusNameEng": "Pending",
            "OrderStatusCode": 0,
            "SelectedStatus": "InProgress" if current_status == "Draft" else "NotStarted"
        },
        {
            "ID": 2,
            "OrderStatusName": "تم التأكيد",
            "OrderStatusNameEng": "Confirmed",
            "OrderStatusCode": 0,
            "SelectedStatus": "InProgress" if current_status == "Submitted" else "NotStarted"
        },
        {
            "ID": 3,
            "OrderStatusName": "تم التسليم",
            "OrderStatusNameEng": "Delivered",
            "OrderStatusCode": 1,
            "SelectedStatus": "InProgress" if current_status == "Completed" else "NotStarted"
        },
        {
            "ID": 4,
            "OrderStatusName": "جارى التحضير",
            "OrderStatusNameEng": "In Preparation",
            "OrderStatusCode": 0,
            "SelectedStatus": "NotStarted"
        },
        {
            "ID": 5,
            "OrderStatusName": "في الطريق",
            "OrderStatusNameEng": "On the Way",
            "OrderStatusCode": 0,
            "SelectedStatus": "NotStarted"
        },
        {
            "ID": 6,
            "OrderStatusName": "تم التسليم",
            "OrderStatusNameEng": "Delivered",
            "OrderStatusCode": 0,
            "SelectedStatus": "NotStarted"
        }
    ]
    return status_list


@frappe.whitelist(allow_guest=True, methods=["GET", "POST"])
@jwt_required
def get_order_list(**kwargs):
    if frappe.request.method == 'GET':
        customer = kwargs.get("cid")
        orders = frappe.get_all(
            "Sales Order",
            filters={
                "customer": customer,
            },
            fields=["name", "grand_total", "status", "transaction_date", "docstatus"],
            order_by='-modified'
        )
        # Map the response to match your expected structure
        mapped_orders = []
        for order in orders:
            current_status = order.get("status")  # Use 'status' for actual order status, not 'docstatus'
            order_data = {
                "Id": order.get("name"),  # Assuming the Sales Order "name" is the ID
                "OrderTotal": order.get("grand_total"),
                "OrderStatusId": get_status_code(current_status),  # Map status to numeric ID
                "StoreId": 0,
                "CustomerId": customer,
                "CustomerName": customer,
                "CustomerNameEng": customer,
                "OrderStatusName": map_status_name(current_status),
                "OrderStatusNameEng": map_status_name_eng(current_status),
                "OrderStatusColor": get_status_color(current_status),
                "CreatedOnUtc": format_date(order.get("transaction_date")),
                "OrderDate": format_date(order.get("transaction_date")),
                "OrderStatusCode": get_status_code(current_status),  # Custom mapping for status code
                "isvisibleSurvey": True,  # Static or dynamic value based on logic
                "surveyid": None,  # Placeholder
                "OrderFromFollow": False,  # Static or dynamic based on logic
                "OrderStatusLst": get_order_status_list(current_status)  # Dynamic list of statuses
            }
            mapped_orders.append(order_data)

        # Return the mapped response
        frappe.local.response["data"] = mapped_orders
    elif frappe.request.method == 'POST':
        print(kwargs)
        order_id = kwargs.get("orderid")
        cancel_order(order_id)


@frappe.whitelist(allow_guest=True)
@jwt_required
def get_order_details(**kwargs):
    sales_order_id = kwargs.get("InvoiceID")
    sales_order = frappe.get_doc("Sales Order", sales_order_id)
    mapped_order = []
    items = sales_order.items
    for item in items:
        i = frappe.get_doc("Item", item.item_code)
        item_data = {
            "PreviewImage": i.image,
            "NameEng": i.item_name,
            "Name": i.item_name,
            "Unit1Name": item.get("uom"),
            "Unit1NameEng": item.get("uom"),
            "U_Code1": item.get("uom"),
            "Unit1OrignalPrice": None,
            "Unit1Price": None,
            "Unit1Point": None,
            "Unit1Factor": None,
            "Unit2Name": None,
            "Unit2NameEng": None,
            "U_Code2": None,
            "Unit2OrignalPrice": None,
            "Unit2Price": None,
            "Unit2Point": None,
            "Unit2Factor": None,
            "Unit3Name": None,
            "Unit3NameEng": None,
            "U_Code3": None,
            "Unit3OrignalPrice": None,
            "Unit3Price": None,
            "Unit3Point": None,
            "Unit3Factor": None,
            "SummaryEng": None,
            "DescriptionEng": None,
            "Summary": None,
            "Description": None,
            "price":item.get("rate"),
            "FromItemCard": 0,
            "SellUnitFactor": 0.0,
            "OrignalPrice": 0.0,
            "SellUnitOrignalPrice": 0.0,
            "SellUnitPoint": 0.0,
            "ActualPrice": item.get("amount"),
            "ItemTotalprice": item.get("amount"),
            "SellUnit": item.get("uom"),
            "SellUnitName": item.get("uom"),
            "SellUnitNameEng": item.get("uom"),
            "DiscountPrice": None,
            "DiscountPercent": None,
            "TotalQuantity": item.get("qty"),
            "MG_code": None,
            "SG_Code": None,
            "IsFavourite": None,
            "SellPoint": None,
            "OrignalSellPoint": None,
            "MinSalesOrder": None,
            "Isbundle": None,
            "NotChangeUnit": None
        }
        mapped_order.append(item_data)

    # Return the mapped response
    frappe.local.response["data"] = mapped_order


def cancel_order(order):
    if frappe.db.exists("Sales Order" , order):
        doc = frappe.get_doc("Sales Order" , order)
        if doc.customer == frappe.local.user.get("customer"):
            if doc.docstatus == 2 :
                frappe.local.response['http_status_code'] = 400
                frappe.local.response['message'] = "Order already canceled"
                return "Order already canceled"
            try:
                if doc.docstatus != 1:
                    doc.docstatus = 1
                    doc.save(ignore_permissions=True)
                    frappe.db.commit()
                doc.docstatus = 2
                doc.save(ignore_permissions=True)
                frappe.db.commit()
                frappe.local.response['http_status_code'] = 200
                frappe.local.response['message'] = _("The Order Canceled")
                return "The Order Canceled."
            except Exception as e:
                frappe.local.response['http_status_code'] = 400
                frappe.local.response['message'] = _(e)


        else:
            frappe.local.response['http_status_code'] = 400
            frappe.local.response['message'] = _("This Customer not owner for this order")
            return "No order found like this."
    else:
        frappe.local.response['http_status_code'] = 400
        frappe.local.response['message'] = _("No order found like this.")
    return "No order found like this."
	


@frappe.whitelist(allow_guest=True)
@jwt_required
def reorder(**kwargs):
    order = kwargs.get("OrderID")
    if frappe.db.exists("Sales Order" , order):
        doc = frappe.get_doc("Sales Order" , order)
        if doc.customer == frappe.local.user.get("customer"):
            cart = frappe.get_doc("Cart" , frappe.get_value("Customer" , frappe.local.user.get("customer") , 'cart_id' ))
            cart.set("cart_item", [])  # Clear the items list
            cart.save()  # Save the changes to the cart
            frappe.db.commit()
            for i in doc.get("items"):
                cart.append("cart_item",{
                    "item": i.item_code,
                    "item_group": i.item_group,
                    "rate": i.rate,
                    "qty":i.qty
                })
            cart.save()
            frappe.db.commit()
            frappe.local.response['http_status_code'] = 200
            frappe.local.response['message'] = _("The order items set in cart")

        else:
            frappe.local.response['http_status_code'] = 400
            frappe.local.response['message'] = _("This Customer not owner for this order")
            return "No order found like this."
    else:
        frappe.local.response['http_status_code'] = 400
        frappe.local.response['message'] = _("No order found like this.")
        return "No order found like this."
