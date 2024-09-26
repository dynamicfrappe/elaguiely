import frappe
from frappe import _ 
from elaguiely.elaguiely.functions import (create_customer ,
					   								 create_cart ,
														 create_favorite)



from elaguiely.apis.item import get_items


@frappe.whitelist()
def cart_details(cart):
   data =frappe.get_doc("Cart" , cart)
   frappe.local.response["message"] = _(" Success ")
   frappe.local.response['http_status_code'] = 200
   frappe.local.response["data"] = data


@frappe.whitelist()
def add_to_cart(item, price=False, qty=False, offer=False, price_list=False, **kwargs):
   """
   Params:
   - item: item_code  (REQUIRED)
   - price: the real price after applying discount if there is one (REQUIRED)
   - qty: quantity to add (default is one, use -1 or 'all' to remove) (OPTIONAL)
   - offer: offer ID if available (OPTIONAL)
   - price_list: price before discount if there's an offer (REQUIRED with offer)
   """

   # Default quantity
   if not qty:
      qty = 1

   # Get current user and check for customer
   user = frappe.get_doc('User', frappe.session.user)
   customer = user.customer
   if not customer:
      frappe.local.response["message"] = _("Cannot find customer")
      frappe.local.response['http_status_code'] = 404
      frappe.local.response["data"] = {"error": _("Error request")}
      return

   # Set cache key and retrieve cart from cache
   cart_key = f"{frappe.session.sid}_cart"
   cart = frappe.cache().get_value(cart_key)

   if cart:
      try:
         cart = frappe.get_doc("Cart", cart.get("name"))
      except:
         cart = None

   if not cart:
      cart = create_cart(user.customer)  # Assuming create_cart() is a valid function

   # Validate item
   try:
      item_obj = frappe.get_doc('Item', item)
   except Exception as e:
      frappe.local.response["message"] = _("Cannot find item")
      frappe.local.response['http_status_code'] = 404
      frappe.local.response["data"] = {"error": str(e)}
      return

   # Message to track what happened
   message = "No action"
   in_cart = False

   # Check if the item is already in the cart
   for cart_item in cart.cart_item:
      if cart_item.item == item_obj.name:
         in_cart = True
         # If quantity plus input is less than or equal to 0, remove item from cart
         if float(cart_item.qty) + float(qty or 0) <= 0:
            cart.remove(cart_item)
            cart.save()
            frappe.db.commit()
            message = _(f"Item {item_obj.item_name} removed from cart")
         else:
            # Update quantity
            cart_item.qty = float(cart_item.qty) + float(qty)
            cart.save()
            frappe.db.commit()
            message = _(f"Item {item_obj.item_name} updated, quantity: {cart_item.qty}")

   if not in_cart:
      # Get item details and append to cart if not already present
      item_details = get_items(filters={"item_code": item_obj.name})  # Assuming get_items() works
      if item_details and len(item_details) > 0:
         item = item_details[0]
         cart.append("cart_item", {
            "item": item_obj.name,
            "qty": float(qty),
            "offer": offer if offer else None,
            "rate": float(item.after_discount or 0),
            "discount_amount": item.item_discount
         })
         cart.save()
         frappe.db.commit()
         message = _(f"Item {item_obj.item_name} added to cart with quantity {qty}")

   # Final response after operation
   frappe.local.response["message"] = message
   frappe.local.response['http_status_code'] = 200

   # Fetch item data for response
   item_details = get_items(filters={"item_code": item_obj.name})
   if item_details and len(item_details) > 0:
      frappe.local.response["data"] = item_details[0]

   # Map the response to the required structure
   mapped_response = {
      "Id": item_obj.name,
      "OrderTotal": price,  # The price after discount if available
      "OrderStatusId": 0,  # You can add status mapping if required
      "CustomerId": customer,
      "CustomerName": user.full_name,
      "OrderStatusName": "Added to cart",
      "CreatedOnUtc": frappe.utils.now(),
      "OrderStatusLst": []  # Can add more details about order status if needed
   }

   # Update response
   frappe.local.response["data"] = mapped_response


@frappe.whitelist(allow_guest = True)
def save_shopping_cart():
    try:
        cart_data = json.loads(frappe.request.data)
        cart_id = cart.data.get_doc("CID")

        if cart_id:
            cart_doc = frappe.get_doc("Shopping Cart", existing_cart)

            existing_product = frappe.db.exists("Cart Item", {
                "item": product_data.get("id"),
                "parent": cart_doc.name
            })

            if existing_product:
                cart_item = frappe.get_doc("Cart Item", existing_product)
                cart_item.qty += product_data.get("totalquantity", 0)
                cart_item.item_total_price += product_data.get("itemTotalprice", 0.0)
                cart_item.total_discount += product_data.get("discountpercent", 0.0)
                cart_item.total = cart_item.item_total_price - cart_item.total_discount
                cart_item.save()
            
            else:
                cart_doc.append("items", {
                    "item": product_data.get("id"),
                    "image": product_data.get("previewimage"),
                    "arabic_name": product_data.get("name"),
                    "description": product_data.get("description"),
                    "uom": product_data.get("sellUnit"),
                    "rate": product_data.get("actualprice", 0.0),
                    "item_total_price": product_data.get("itemTotalprice", 0.0),
                    "qty": product_data.get("totalquantity", 0),
                    "total_discount": product_data.get("discountpercent", 0.0),
                    "total": product_data.get("itemTotalprice", 0.0)
                })
                cart_doc.save()

        else:
            return "Cart Not Exists"
       
    except Exception as e:
        pass
