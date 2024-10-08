import frappe
from frappe import _
from .utils import get_bulk_item_prices , stock_qty
from elaguiely.apis_v1.jwt_decorator import jwt_required


@frappe.whitelist(allow_guest=True)
@jwt_required
def get_categories(ParentId=None, classcode=None, **kwargs):
	try:
		response = []
		if classcode:
			class_codes = frappe.get_list("Customer Classes", filters={'customer_class': classcode}, fields=['parent'])
			class_code_names = [code['parent'] for code in class_codes]

			main_groups = frappe.db.get_all("Item Group", filters={'name': ['in', class_code_names]},
											fields=["name", 'arabic_name', 'item_group_name', 'image'])
			if not main_groups:
				frappe.local.response['data'] = response

			for main_group in main_groups:
				response.append({
					"Id": main_group.get("name"),
					"Name": main_group.get("arabic_name"),
					"NameEng": main_group.get("name"),
					"Icon": main_group.get("image"),
					"MG_code": main_group.get("name"),
					"SG_Code": None,
					"SG2_Code": None,
					"DisplayOrder": None
				})
		else:
			subcategories = frappe.db.get_list("Brand Categories", fields=['parent'], filters=[{'category': ParentId}])
			for subcategory in subcategories:
				suppliers = frappe.db.get_list("Brand", filters={'name': subcategory.get("parent")},
											   fields={'name', 'arabic_name', 'image'})
				for supplier in suppliers:
					image = frappe.db.get_value('Brand', supplier.get('name'), "image")
					response.append({
						"Id": supplier.get('name'),
						"Name": supplier.get('arabic_name'),
						"NameEng": supplier.get('name'),
						"Icon": image,
						"MG_code": ParentId,
						"SG_Code": supplier.get('name'),
						"SG2_Code": None,
						"DisplayOrder": None
					})
					
		frappe.local.response['data'] = response

	except Exception as e:
		frappe.local.response['http_status_code'] = 404
		frappe.local.response['message'] = _("failed : {0}").format(str(e))
		frappe.local.response['data'] = {"errors": str(e)}


@frappe.whitelist(allow_guest=True)
@jwt_required
def get_all_suppliers(**kwargs):
	try:
		suppliers = frappe.db.get_list(
			"Brand",
			fields=["name", "arabic_name", "image"],
			ignore_permissions=True
		)
		if not suppliers:
			return {"status": "success", "data": []}
		response = []
		for supplier in suppliers:
			subcategories = frappe.get_list("Brand Categories", fields=['category'],
											filters=[{'parent': supplier.name}])
			response.append({
				"icon": supplier.get("image"),
				"name": supplier.get("arabic_name"),
				"nameeng": supplier.get("name"),
				"sup_id": supplier.get("name"),
				"imageName": supplier.get("image"),
				"advertisingId": None,
				"subcategories": subcategories
			})
		frappe.local.response['data'] = response

	except Exception as e:
		return {'status_code': 404, 'message': str(e)}


@frappe.whitelist(allow_guest=True)
@jwt_required
def get_category_by_supplier(supplierid, **kwargs):
	try:
		supplier = frappe.get_doc("Brand", supplierid)
		if not supplier:
			return {"message": "Invalid", "data": []}
		categories = frappe.get_list(
			"Brand Categories",
			fields=['category'],
			filters=[{'parent': supplier.name}],
			ignore_permissions=True
		)
		responses = []
		for category in categories:
			image = frappe.db.get_value("Item Group", category.get('category'), 'image')
			category["id"] = category.get("category")
			category["name"] = category.get("category")
			category["nameEng"] = category.get("category")
			category["icon"] = image 
			category["mgCode"] = category.get("category")
			category["sgCode"] = supplierid
			category["sg2Code"] = None
			responses.append(category)
			print(category["icon"])

		frappe.local.response.data = responses
	except Exception as e:
		frappe.local.response['http_status_code'] = 404
		frappe.local.response['message'] = _("failed to get supplier {0}: {1}").format(supplierid, str(e))
		frappe.local.response['data'] = {"errors": str(e)}


@frappe.whitelist(allow_guest=True)
@jwt_required
def get_best_selling_items(**kwargs):

	customer = kwargs.get('CustomerID')
	customer_group = frappe.get_value("Customer", customer, 'customer_group')
	item_groups = frappe.db.get_list("Customer Classes", filters={'customer_class': customer_group}, fields = ['parent'])

	items = []
	items_with_uom_and_prices = []

	for ig in item_groups:
		ig_items = frappe.db.get_all("Item", filters={'item_group' : ig.get("parent"), 'best_sell': 1}, fields=['name'])
		items.extend(ig_items)  
	item_names = [item['name'] for item in items]

	item_prices = get_bulk_item_prices(item_names)
	price_list_name = frappe.get_value("Customer", customer, "default_price_list") or ""

	for item in items: 
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
					"U_Code2": uom_prices[1]['name'],
					"Unit2Name": uom_prices[1]['name'],
					"Unit2NameEng": uom_prices[1]['name'],
					"Unit2OrignalPrice": uom_prices[1]['price'],
					"Unit2Price": uom_prices[1]['price'],
					"Unit2Factor": uom_prices[1]['factor'],
					"actual_qty2": int(qty / uom_prices[1]['factor']) if uom_prices[1]['factor'] not in [0, None] else 0,
					"U_Code3": uom_prices[2]['name'],
					"Unit3Name": uom_prices[2]['name'],
					"Unit3NameEng": uom_prices[2]['name'],
					"Unit3OrignalPrice": uom_prices[2]['price'],
					"Unit3Price": uom_prices[2]['price'],
					"Unit3Factor": uom_prices[2]['factor'],
					"actual_qty3": int(qty / uom_prices[2]['factor']) if uom_prices[2]['factor'] not in [0, None] else 0,
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
					"IsFavourite": False,
					"SellPoint": None,
					"OrignalSellPoint": None,
					"MinSalesOrder": 1,
					"Isbundle": None,
					"NotChangeUnit": None
				}

				items_with_uom_and_prices.append(item_details)
	
	frappe.local.response["data"] = items_with_uom_and_prices



