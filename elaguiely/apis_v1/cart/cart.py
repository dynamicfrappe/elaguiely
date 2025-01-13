import frappe
import json
from frappe import _
from frappe.utils import today
from elaguiely.apis_v1.jwt_decorator import jwt_required
from elaguiely.apis_v1.utils import get_item_prices, stock_qty


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
		default_max_orders = frappe.db.get_single_value("Selling Settings", 'maximum_orders' )
		customer_max_orders = frappe.get_value("Customer", customer_id, "maximum_orders")
		max_orders = customer_max_orders if customer_max_orders > 0 else default_max_orders
		daily_orders = frappe.db.get_all("Sales Order", filters={'customer': customer_id, 'transaction_date': today()}, fields=['name'])
		price_list_name = frappe.get_value("Customer", customer_id, "default_price_list") or frappe.db.get_single_value("Selling Settings", "default_price_list")
		for item in cart.cart_item:
			uom_prices = get_item_prices(item.item, price_list_name)

			qty = int(stock_qty(customer_id, item.get('item')) or 0)
			print(qty)
			product = {
				"Id": item.get('item'),
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
				"actual_qty1": int(qty / uom_prices[0]['factor']) if uom_prices[0]['factor'] not in [0, None] else 0,
				"maximum_qty1": uom_prices[0]['max_qty'],
				"Unit2Name": uom_prices[1]['name'],
				"Unit2NameEng": uom_prices[1]['name'],
				"U_Code2": uom_prices[1]['name'],
				"Unit2OrignalPrice": uom_prices[1]['price'],
				"Unit2Price": uom_prices[1]['price'],
				"Unit2Point": 1.00,
				"Unit2Factor": uom_prices[1]['factor'],
				"actual_qty2": int(qty / uom_prices[1]['factor']) if uom_prices[1]['factor'] not in [0, None] else 0,
				"maximum_qty2": uom_prices[1]['max_qty'],
				"Unit3Name": uom_prices[2]['name'],
				"Unit3NameEng": uom_prices[2]['name'],
				"U_Code3": uom_prices[2]['name'],
				"Unit3OrignalPrice": uom_prices[2]['price'],
				"Unit3Price": uom_prices[2]['price'],
				"Unit3Point": 1.00,
				"Unit3Factor": uom_prices[2]['factor'],
				"actual_qty3": int(qty / uom_prices[2]['factor']) if uom_prices[2]['factor'] not in [0, None] else 0,
				"maximum_qty3": uom_prices[2]['max_qty'],
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
				"MinSalesOrder": 1,
				"Isbundle": None,
				"NotChangeUnit": None
			}
			products.append(product)
		frappe.local.response['http_status_code'] = 200
		response_data = {
			"isPriceChanged": False,  # You may want to add logic to calculate this
			"minimum_amount": frappe.db.get_single_value("Selling Settings", 'minimum_amount'),
			"max_orders": max_orders,
			"allow_order": len(daily_orders) < max_orders,
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
			
			# default_warehouse = frappe.db.get_single_value('Stock Settings', 'default_warehouse')
			# actual_qty = frappe.get_value("Bin" , {"item_code":product_data.get("id") , "warehouse":default_warehouse} , 'actual_qty')
			actual_qty = int(stock_qty(customer_id, product_data.get("id")) or 0 )
			if product_data.get("totalquantity", 0) > actual_qty :
					frappe.local.response['http_status_code'] = 400
					frappe.local.response['message'] = _("No quantity avaliable for this item.")
					return "No quantity avaliable for this item."
			

			existing_product = frappe.db.exists("Cart Item", {
				"item": product_data.get("id"),
				"parent": cart_doc.name
			})

			if existing_product:
				cart_item = frappe.get_doc("Cart Item", existing_product)
				# print(cart_item.parent)

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
		frappe.local.response['http_status_code'] = 404
		frappe.local.response['message'] = _("failed to save the cart: {0}").format(str(e))
		frappe.local.response['data'] = {"errors": str(e)}
		frappe.db.rollback()


@frappe.whitelist(allow_guest=True)
@jwt_required
def clear_shopping_cart(**kwargs):
	customer_id = kwargs.get("customerid")
	item_code = kwargs.get("ItemCode")  # Get the item code from the request
	print('item_code ==> ', item_code)
	try:
		# Fetch the cart for the specified customer
		cart = frappe.get_doc("Cart", {'customer': customer_id}, fields=['*'])

		# If an item_code is provided, remove only that item from the cart
		if item_code != "0":
			# Filter out the item with the specified item_code from the cart items
			updated_cart_items = [item for item in cart.get("cart_item") if item.item != item_code]
			# Set the updated list back to the cart
			cart.set("cart_item", updated_cart_items)
		else:
			# If no item_code is provided, clear the entire cart
			cart.set("cart_item", [])  # Clear the cart items

		# Save the updated cart
		cart.save(ignore_permissions=True)

		# Respond with success message
		frappe.local.response["message"] = _("Cart updated successfully")

	except frappe.DoesNotExistError:
		# Handle case where the cart or customer does not exist
		frappe.local.response["http_status_code"] = 404
		frappe.local.response["message"] = _("Customer or Cart does not exist")

	frappe.db.commit()

