from datetime import datetime

import frappe
from frappe import _

from elaguiely.apis_v1.jwt_decorator import jwt_required
from elaguiely.apis_v1.utils import get_item_prices


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

        # Convert to datetime object
        date_object = datetime.strptime(kwargs.get("DeliveryDate"), "%Y-%m-%d")

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


def map_status_to_id(status):
    status_map = {
        "Draft": 1,
        "Submitted": 2,
        "Completed": 3,
        # Add more status mappings as needed
    }
    return status_map.get(status, 0)


def map_status_name(status):
    status_map = {
        "Draft": "معلق",
        "Submitted": "تم التأكيد",
        "Completed": "تم التسليم",
        # Add more status translations as needed
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
        "Draft": 0,
        "On Hold": 1,
        "To Deliver and Bill": 2,
        "To Bill To Deliver": 3,
        "Completed": 4,
        "Cancelled": 5,
        "Closed": 6,
    }
    return status_code_map.get(status, 0)


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


@frappe.whitelist(allow_guest=True)
@jwt_required
def get_order_list(**kwargs):
    customer = kwargs.get("cid")
    orders = frappe.get_all(
        "Sales Order",
        filters={"customer": customer},
        fields=["name", "grand_total", "status", "transaction_date", "docstatus"],
    )

    # Map the response to match your expected structure
    mapped_orders = []
    for order in orders:
        current_status = order.get("status")  # Use 'status' for actual order status, not 'docstatus'
        order_data = {
            "Id": order.get("name"),  # Assuming the Sales Order "name" is the ID
            "OrderTotal": order.get("grand_total"),
            "OrderStatusId": map_status_to_id(current_status),  # Map status to numeric ID
            "StoreId": 0,  # This seems to be a static value in your response
            "CustomerId": customer,  # From the input parameter
            "CustomerName": "",  # Populate with customer name if needed
            "CustomerNameEng": "",  # Populate if needed
            "OrderStatusName": map_status_name(current_status),  # Map status to Arabic
            "OrderStatusNameEng": map_status_name_eng(current_status),  # English name of status
            "OrderStatusColor": get_status_color(current_status),  # Define a function for the color
            "CreatedOnUtc": format_date(order.get("transaction_date")),  # Custom date formatting
            "OrderDate": "",  # Not provided in Sales Order, populate if available
            "OrderStatusCode": map_status_to_id(current_status),  # Custom mapping for status code
            "isvisibleSurvey": True,  # Static or dynamic value based on logic
            "surveyid": None,  # Placeholder
            "OrderFromFollow": False,  # Static or dynamic based on logic
            "OrderStatusLst": get_order_status_list(current_status)  # Dynamic list of statuses
        }
        mapped_orders.append(order_data)

    # Return the mapped response
    frappe.local.response["data"] = mapped_orders
