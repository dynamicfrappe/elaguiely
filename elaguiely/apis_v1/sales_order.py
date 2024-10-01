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
        sales_order.transaction_date = frappe.utils.nowdate()  # You can customize this

        # Convert to datetime object
        date_object = datetime.strptime(kwargs.get("DeliveryDate"), "%Y-%m-%d")

        # Format as YYYY-MM-DD
        formatted_date = date_object.strftime("%Y-%m-%d")
        sales_order.delivery_date = formatted_date

        # Add cart items to the Sales Order items table
        for cart_item in cart.get("cart_item"):  # Replace 'items' with the correct field if different
            uom_prices = get_item_prices(cart_item.item)  # Assuming you get the UOM prices this way
            print(uom_prices)
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
        "Draft": 10,
        "Submitted": 20,
        "Completed": 30,
        # Map status to custom codes
    }
    return status_code_map.get(status, 0)

def format_date(date):
    return date.strftime("%d-%m-%Y %I:%M %p") if date else ""

def get_order_status_list(current_status):
    status_list = [
        {
            "ID": 1,
            "OrderStatusName": "معلق",
            "OrderStatusNameEng": None,
            "OrderStatusCode": 0,
            "SelectedStatus": "InProgress" if current_status == "Draft" else "NotStarted"
        },
        {
            "ID": 2,
            "OrderStatusName": "جاري المراجعه",
            "OrderStatusNameEng": None,
            "OrderStatusCode": 0,
            "SelectedStatus": "InProgress" if current_status == "Submitted" else "NotStarted"
        },
        {
            "ID": 3,
            "OrderStatusName": "تم التأكيد",
            "OrderStatusNameEng": None,
            "OrderStatusCode": 0,
            "SelectedStatus": "InProgress" if current_status == "Completed" else "NotStarted"
        },
        # Add more statuses as per your requirement
    ]
    return status_list


@frappe.whitelist(allow_guest=True)
@jwt_required
def get_order_list(**kwargs):
    customer = kwargs.get("cid")
    orders = frappe.get_all(
        "Sales Order",
        filters={"customer": customer},
        fields=["name", "grand_total", "status", "transaction_date"]
    )

    # Map the response to match your expected structure
    mapped_orders = []
    for order in orders:
        order_data = {
            "Id": order.get("name"),  # Assuming the Sales Order "name" is the ID
            "OrderTotal": order.get("grand_total"),
            "OrderStatusId": map_status_to_id(order.get("status")),  # You will define the mapping
            "StoreId": 0,  # This seems to be a static value in your response
            "CustomerId": customer,  # Directly from the input parameter
            "CustomerName": "",  # Populate with customer name if needed
            "CustomerNameEng": "",  # Populate if needed
            "OrderStatusName": map_status_name(order.get("status")),  # Map status to Arabic if needed
            "OrderStatusNameEng": map_status_name_eng(order.get("status")),  # English name of status
            "OrderStatusColor": get_status_color(order.get("status")),  # Define a function for the color
            "CreatedOnUtc": format_date(order.get("transaction_date")),  # Custom date formatting
            "OrderDate": "",  # Not provided in Sales Order, you can populate if available
            "OrderStatusCode": get_status_code(order.get("status")),  # Custom mapping for status code
            "isvisibleSurvey": True,  # Static or dynamic value based on logic
            "surveyid": None,  # Placeholder
            "OrderFromFollow": False,  # Static or dynamic based on logic
            "OrderStatusLst": get_order_status_list(order.get("status"))  # Dynamic list of statuses
        }
        mapped_orders.append(order_data)

    # Return the mapped response
    frappe.local.response["data"] = mapped_orders


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
            "NameEng": i.name,
            "Name": i.name,
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
            "ActualPrice": item.get("rate"),
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








        
    