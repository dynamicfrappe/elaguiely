from dataclasses import fields

import frappe
import json
from frappe import _

from elaguiely.apis_v1.jwt_decorator import jwt_required
from elaguiely.apis_v1.utils import get_item_prices
from elaguiely.elaguiely.functions import (create_customer ,
					   								 create_cart ,
														 create_favorite)



from elaguiely.apis.item import get_items


# @frappe.whitelist(allow_guest=True)
# @jwt_required
# def cart_details(**kwargs):
#    print('cart details')
#    print('CustomerID', kwargs.get("CustomerID"))
#    customer = frappe.get_doc("Customer", kwargs.get("CustomerID"))
#    print(customer)
#    # print('cart details ==> ', frappe.session.user.customer)
#    # print('cart details ==> ', frappe.session.user.cart)
#    data = frappe.get_doc("Cart" , filter = {"customer": customer.name})
#    # data = []
#    print('data ==> ', data)
#    frappe.local.response["message"] = _(" Success ")
#    frappe.local.response['http_status_code'] = 200
#    frappe.local.response["data"] = data
# @frappe.whitelist()
# def add_to_cart(item, price=False, qty=False, offer=False, price_list=False, **kwargs):
#    """
#    Params:
#    - item: item_code  (REQUIRED)
#    - price: the real price after applying discount if there is one (REQUIRED)
#    - qty: quantity to add (default is one, use -1 or 'all' to remove) (OPTIONAL)
#    - offer: offer ID if available (OPTIONAL)
#    - price_list: price before discount if there's an offer (REQUIRED with offer)
#    """
#
#    # Default quantity
#    if not qty:
#       qty = 1
#
#    # Get current user and check for customer
#    user = frappe.get_doc('User', frappe.session.user)
#    customer = user.customer
#    if not customer:
#       frappe.local.response["message"] = _("Cannot find customer")
#       frappe.local.response['http_status_code'] = 404
#       frappe.local.response["data"] = {"error": _("Error request")}
#       return
#
#    # Set cache key and retrieve cart from cache
#    cart_key = f"{frappe.session.sid}_cart"
#    cart = frappe.cache().get_value(cart_key)
#
#    if cart:
#       try:
#          cart = frappe.get_doc("Cart", cart.get("name"))
#       except:
#          cart = None
#
#    if not cart:
#       cart = create_cart(user.customer)  # Assuming create_cart() is a valid function
#
#    # Validate item
#    try:
#       item_obj = frappe.get_doc('Item', item)
#    except Exception as e:
#       frappe.local.response["message"] = _("Cannot find item")
#       frappe.local.response['http_status_code'] = 404
#       frappe.local.response["data"] = {"error": str(e)}
#       return
#
#    # Message to track what happened
#    message = "No action"
#    in_cart = False
#
#    # Check if the item is already in the cart
#    for cart_item in cart.cart_item:
#       if cart_item.item == item_obj.name:
#          in_cart = True
#          # If quantity plus input is less than or equal to 0, remove item from cart
#          if float(cart_item.qty) + float(qty or 0) <= 0:
#             cart.remove(cart_item)
#             cart.save()
#             frappe.db.commit()
#             message = _(f"Item {item_obj.item_name} removed from cart")
#          else:
#             # Update quantity
#             cart_item.qty = float(cart_item.qty) + float(qty)
#             cart.save()
#             frappe.db.commit()
#             message = _(f"Item {item_obj.item_name} updated, quantity: {cart_item.qty}")
#
#    if not in_cart:
#       # Get item details and append to cart if not already present
#       item_details = get_items(filters={"item_code": item_obj.name})  # Assuming get_items() works
#       if item_details and len(item_details) > 0:
#          item = item_details[0]
#          cart.append("cart_item", {
#             "item": item_obj.name,
#             "qty": float(qty),
#             "offer": offer if offer else None,
#             "rate": float(item.after_discount or 0),
#             "discount_amount": item.item_discount
#          })
#          cart.save()
#          frappe.db.commit()
#          message = _(f"Item {item_obj.item_name} added to cart with quantity {qty}")
#
#    # Final response after operation
#    frappe.local.response["message"] = message
#    frappe.local.response['http_status_code'] = 200
#
#    # Fetch item data for response
#    item_details = get_items(filters={"item_code": item_obj.name})
#    if item_details and len(item_details) > 0:
#       frappe.local.response["data"] = item_details[0]
#
#    # Map the response to the required structure
#    mapped_response = {
#       "Id": item_obj.name,
#       "OrderTotal": price,  # The price after discount if available
#       "OrderStatusId": 0,  # You can add status mapping if required
#       "CustomerId": customer,
#       "CustomerName": user.full_name,
#       "OrderStatusName": "Added to cart",
#       "CreatedOnUtc": frappe.utils.now(),
#       "OrderStatusLst": []  # Can add more details about order status if needed
#    }
#
#    # Update response
#    frappe.local.response["data"] = mapped_response


@frappe.whitelist(allow_guest=True)
@jwt_required
def cart_details(**kwargs):
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
        cart = frappe.get_doc("Cart", {'customer': customer.name}, fields=['*'])
        if not cart:
            frappe.local.response["data"] = _("Cart not found")
            return
        products = []
        for item in cart.cart_item:
            print(item.item)
            print(item.get('uom'))
            print(item.rate)
            uom_prices = get_item_prices(item.item)
            product = {
                "Id": item.get('name'),
                "PreviewImage": item.get('image'),
                "NameEng": item.get('item_name'),
                "Name": item.get('arabic_name'),
                "Unit1Name": uom_prices[0]['name'],
                "Unit1NameEng": uom_prices[0]['name'],
                "U_Code1": uom_prices[0]['name'],
                "Unit1OrignalPrice": uom_prices[0]['price'],
                "Unit1Price": uom_prices[0]['price'],
                "Unit1Point": 1.00,
                "Unit1Factor": uom_prices[0]['factor'],
                "Unit2Name": uom_prices[1]['name'],
                "Unit2NameEng": uom_prices[1]['name'],
                "U_Code2": uom_prices[1]['name'],
                "Unit2OrignalPrice": uom_prices[1]['price'],
                "Unit2Price": uom_prices[1]['price'],
                "Unit2Point": 1.00,
                "Unit2Factor": uom_prices[1]['factor'],
                "Unit3Name": uom_prices[2]['name'],
                "Unit3NameEng": uom_prices[2]['name'],
                "U_Code3": uom_prices[2]['name'],
                "Unit3OrignalPrice": uom_prices[2]['price'],
                "Unit3Price": uom_prices[2]['price'],
                "Unit3Point": 1.00,
                "Unit3Factor": uom_prices[2]['factor'],
                "SummaryEng": "None",
                "DescriptionEng": "None",
                "Summary": "None",
                "Description": "None",
                "price": float(item.get('rate')),
                "FromItemCard": None,
                "SellUnitFactor": None,
                "OrignalPrice": float(item.get('rate')),
                "SellUnitOrignalPrice": float(item.get('rate')),
                "SellUnitPoint": float(item.get('rate')),
                "ActualPrice": float(item.get('rate')),
                "ItemTotalprice": float(item.get('rate')),
                "SellUnit": item.get('uom'),
                "SellUnitName": item.get('uom'),
                "SellUnitNameEng": item.get('uom'),
                "DiscountPrice": float(item.get('rate')),
                "DiscountPercent": None,
                "TotalQuantity": int(item.get('qty')) if item.get('qty') else 0,
                "MG_code": item.get('item_group'),
                "SG_Code": item.get('brand'),
                "IsFavourite": None,
                "SellPoint": None,
                "OrignalSellPoint": None,
                "MinSalesOrder": None,
                "Isbundle": None,
                "NotChangeUnit": None
            }
            products.append(product)
        frappe.local.response['http_status_code'] = 200
        response_data = {
            "isPriceChanged": False,  # You may want to add logic to calculate this
            "productlist": products,
        }
        frappe.local.response["data"] = response_data

    except frappe.DoesNotExistError:
        frappe.local.response["data"] = _("Customer does not exist")
        frappe.local.response['http_status_code'] = 404

    except Exception as e:
        frappe.local.response["data"] = _("An error occurred")
        frappe.local.response['http_status_code'] = 500
        frappe.local.response["error"] = str(e)


@frappe.whitelist(allow_guest=True)
@jwt_required
def save_shopping_cart(**kwargs):
    print('save_shopping_cart')
    try:
        cart_data = json.loads(frappe.request.data)
        customer_id = cart_data.get("CustomerID")
        customer = frappe.get_doc("Customer", customer_id)
        cart_id = customer.cart_id
        if cart_id:
            cart_doc = frappe.get_doc("Cart", cart_id)
            cart = frappe.db.exists("Cart", {'name': cart_id})
            product_data = cart_data.get("Product")
            print(product_data)
            existing_product = frappe.db.exists("Cart Item", {
                "item": product_data.get("id"),
                "parent": cart_doc.name
            })

            if existing_product:
                cart_item = frappe.get_doc("Cart Item", existing_product)
                print(cart_item.parent)
                cart_item.qty = product_data.get("totalquantity", 0)
                frappe.db.set_value("Cart Item", existing_product, {"uom": product_data.get("sellUnit", 0)})
                frappe.db.set_value("Cart Item", existing_product, {"rate": product_data.get("actualprice", 0)})
                frappe.db.set_value("Cart Item", existing_product, {"qty": product_data.get("totalquantity", 0)})
                frappe.db.commit()
            else:
                print('product_data.get("sellUnit") ===> ', product_data.get("sellUnit"))
                cart_item = frappe.get_doc({
                    "doctype": "Cart Item",
                    "parent": cart_doc.name,
                    "parenttype": "Cart",
                    "parentfield": "cart_item",
                    "item": product_data.get("id"),
                    "uom": product_data.get("sellUnit"),
                    "rate": product_data.get("actualprice"),
                    "qty": product_data.get("totalquantity")
                })
                cart_item.insert()
                frappe.db.commit()
                cart_item.set_value = product_data.get("sellUnit")
                frappe.db.commit()
                print("Item is inserted successfully.")

        else:
            print("Cart Not Exists")
            return "Cart Not Exists"

    except Exception as e:
        print(f"An error occurred: {e}")
        frappe.db.rollback()


def clear_shopping_cart():
    print('clear_shopping_cart')
