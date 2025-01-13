import frappe
from frappe import _
from elaguiely.apis_v1.utils import get_bulk_item_prices , stock_qty
from elaguiely.apis_v1.jwt_decorator import jwt_required

# First Testing DONE 
@frappe.whitelist(allow_guest=True)
@jwt_required
def get_best_selling_items(**kwargs):

	customer = kwargs.get('CustomerID')
	customer_group = frappe.get_value("Customer", customer, 'customer_group')
	item_groups = frappe.db.get_list("Customer Classes", filters={'customer_class': customer_group}, fields = ['parent'])

	items = []
	items_with_uom_and_prices = []

	for ig in item_groups:
		ig_items = frappe.db.get_all("Item", filters={'item_group' : ig.get("parent"), 'disabled':0, 'best_sell': 1}, fields=['name'])
		items.extend(ig_items)  
	item_names = [item['name'] for item in items]
	
	price_list_name = frappe.get_value("Customer", customer, "default_price_list") or frappe.db.get_single_value("Selling Settings", "default_price_list")

	item_prices = get_bulk_item_prices(item_names, price_list_name)
	# Fetch favorite items
	fav_items = frappe.get_list("Favorite Item", 
		filters={'parent': frappe.get_value("Favorite", {'customer': customer}, 'name')}, 
		fields=['item']) if frappe.get_value("Favorite", {'customer': customer}, 'name') else []
	fav_items = [item['item'] for item in fav_items]
	
	for item in items: 
		# Fetch favorite field
		default_fav = item['name'] in fav_items
		# Fetch prices related to the item
		i = frappe.get_doc("Item", item.get("name"))
		uom_prices = item_prices.get(item['name'], [])

		if uom_prices:  # Ensure prices exist for the item
			# Determine which UOM matches the default UOM (stock_uom)
			default_uom_price = next((uom for uom in uom_prices if uom['price_list'] == price_list_name), None)
			if any([
			uom_prices[0].get('price_list') == price_list_name,
			uom_prices[1].get('price_list') == price_list_name,
			uom_prices[2].get('price_list') == price_list_name
			]):
				qty = int(stock_qty(customer, item['name']) or 0 )
				print(qty)
				# Structure the item details with multiple UOMs
				item_details = {
					"Id": i.name or '',
					"PreviewImage": i.image or '',
					"NameEng": i.item_name or '',
					"Name": i.arabic_name or '',
					"Unit1Name": uom_prices[0]['name'],
					"Unit1NameEng": uom_prices[0]['name'],
					"U_Code1": uom_prices[0]['name'],
					"Unit1OrignalPrice": uom_prices[0]['price'],
					"Unit1Price": uom_prices[0]['price'],
					"Unit1Factor": uom_prices[0]['factor'],
					"actual_qty1": int(qty / uom_prices[0]['factor']) if uom_prices[0]['factor'] not in [0, None] else 0,
					"maximum_qty1": uom_prices[0]['max_qty'],
					"U_Code2": uom_prices[1]['name'],
					"Unit2Name": uom_prices[1]['name'],
					"Unit2NameEng": uom_prices[1]['name'],
					"Unit2OrignalPrice": uom_prices[1]['price'],
					"Unit2Price": uom_prices[1]['price'],
					"Unit2Factor": uom_prices[1]['factor'],
					"actual_qty2": int(qty / uom_prices[1]['factor']) if uom_prices[1]['factor'] not in [0, None] else 0,
					"maximum_qty2": uom_prices[1]['max_qty'],
					"U_Code3": uom_prices[2]['name'],
					"Unit3Name": uom_prices[2]['name'],
					"Unit3NameEng": uom_prices[2]['name'],
					"Unit3OrignalPrice": uom_prices[2]['price'],
					"Unit3Price": uom_prices[2]['price'],
					"Unit3Factor": uom_prices[2]['factor'],
					"actual_qty3": int(qty / uom_prices[2]['factor']) if uom_prices[2]['factor'] not in [0, None] else 0,
					"maximum_qty3": uom_prices[2]['max_qty'],
					"SummaryEng": None,
					"DescriptionEng": None,
					"Summary": None,
					"Description": item.get('description', ''),
					"price": None,
					"FromItemCard": None,
					"SellUnitFactor": None,
					"OrignalPrice": default_uom_price['price'] if default_uom_price else 0.00,
					"SellUnitOrignalPrice": default_uom_price['price'] if default_uom_price else 0.00,
					"SellUnit": i.stock_uom,
					"SellUnitName": i.stock_uom,
					"SellUnitNameEng": i.stock_uom,
					"SellUnitPoint": i.stock_uom,
					"ActualPrice": default_uom_price['price'] if default_uom_price else 0.00,
					"ItemTotalprice": None,
					"TotalQuantity": 1,
					"MG_code": i.item_group or '',
					"SG_Code": i.brand or '',
					"IsFavourite": default_fav,
					"SellPoint": None,
					"OrignalSellPoint": None,
					"MinSalesOrder": 1,
					"Isbundle": None,
					"NotChangeUnit": None
				}

				items_with_uom_and_prices.append(item_details)
	
	frappe.local.response["data"] = items_with_uom_and_prices



