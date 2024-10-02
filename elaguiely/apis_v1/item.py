import frappe
from frappe import _

from .jwt_decorator import jwt_required
from .utils import get_bulk_item_prices , stock_qty

@frappe.whitelist(allow_guest=True)
@jwt_required
def get_items_prices(**kwargs):
    items_with_uom_and_prices = []
    item_group = kwargs.get('MainGroupID')
    brand = kwargs.get('SubGroup1ID') or kwargs.get("SupplierID")
    customer_id = kwargs.get("CustomerID")
    item_name = kwargs.get("ItemName")
    is_fav = kwargs.get("fav")

    if not customer_id:
        frappe.local.response["message"] = _("CustomerID is required")
        frappe.local.response['http_status_code'] = 400
        return

    default_fav = False
    favorite_doc = frappe.get_value("Favorite", {'customer': customer_id}, 'name')
    fav_items_dict = {}
    if favorite_doc:
        fav_items_dict = frappe.db.get_list("Favorite Item", filters={'parent': favorite_doc}, fields=['item'])
    print(fav_items_dict)

    fav_items = []
    for i in fav_items_dict:
        fav_items.append( i.get("item") )
    print(fav_items)
    filters = {}
    if item_group:
        filters['item_group'] = item_group
    if brand:
        filters['brand'] = brand
    if item_name:
        filters['item_name'] = item_name
    if is_fav is not None:
        if is_fav:
            filters['name'] = ['in', fav_items]
            default_fav = True
        else:
            filters['name'] = ['not in', fav_items]


    # Fetch customer and cart in one go
    customer_name = frappe.get_value("Customer", customer_id, "name")
    price_list_name = frappe.get_value("Customer", customer_id, "default_price_list")
    print(price_list_name)
    cart_items = frappe.get_all(
        "Cart Item",
        filters={'parent': frappe.get_value("Cart", {"customer": customer_name}, "name")},
        fields=["item", "qty", "rate", "uom"]
    ) if customer_name else []

    # Convert cart items to a dictionary for quick lookup
    cart_dict = {item['item']: item for item in cart_items}

    # Fetch all items in one query
    items = frappe.get_all(
        'Item',
        fields=[
            'name', 'item_name', 'item_code', 'arabic_name', 'image', 'description', 'brand', 'item_group',
            'standard_rate', 'stock_uom'
        ],
        filters=filters,
        ignore_permissions=True
    )

    # Fetch item prices for all items at once
    item_names = [item['name'] for item in items]

    item_prices = get_bulk_item_prices(item_names)  # fetch prices for all items in one query

    for item in items:
        # Fetch favourite field
        if item['name'] in fav_items:
            default_fav = True
            
        # Fetch prices related to the item
        uom_prices = item_prices.get(item['name'], [])

        print(uom_prices)

        if uom_prices:  # Ensure prices exist for the item
            # Determine which UOM matches the default UOM (stock_uom)
            default_uom_price = next((uom for uom in uom_prices if uom['name'] == item['stock_uom'] and uom['price_list'] == price_list_name), None)
            if any([
            uom_prices[0].get('price_list') == price_list_name,
            uom_prices[1].get('price_list') == price_list_name,
            uom_prices[2].get('price_list') == price_list_name
        ]):
                # Structure the item details with multiple UOMs
                item_details = {
                    "Id": item['name'],
                    "PreviewImage": item.get('image', ''),
                    "NameEng": item.get('item_name', ''),
                    "Name": item['arabic_name'],
                    "Unit1Name": uom_prices[0]['name'],
                    "Unit1NameEng": uom_prices[0]['name'],
                    "U_Code1": uom_prices[0]['name'],
                    "Unit1OrignalPrice": uom_prices[0]['price'],
                    "Unit1Price": uom_prices[0]['price'],
                    "Unit1Factor": uom_prices[0]['factor'],
                    "actual_qty1":int(stock_qty(item['name'] , uom_prices[0]['name'] ) or 0),
                    "U_Code2": uom_prices[1]['name'],
                    "Unit2Name": uom_prices[1]['name'],
                    "Unit2NameEng": uom_prices[1]['name'],
                    "Unit2OrignalPrice": uom_prices[1]['price'],
                    "Unit2Price": uom_prices[1]['price'],
                    "Unit2Factor": uom_prices[1]['factor'],
                    "actual_qty2":int(stock_qty(item['name'] , uom_prices[1]['name'] ) or 0),
                    "U_Code3": uom_prices[2]['name'],
                    "Unit3Name": uom_prices[2]['name'],
                    "Unit3NameEng": uom_prices[2]['name'],
                    "Unit3OrignalPrice": uom_prices[2]['price'],
                    "Unit3Price": uom_prices[2]['price'],
                    "Unit3Factor": uom_prices[2]['factor'],
                    "actual_qty3":int(stock_qty(item['name'] , uom_prices[2]['name'] ) or 0),
                    "SummaryEng": None,
                    "DescriptionEng": None,
                    "Summary": None,
                    "Description": item.get('description', ''),
                    "price": None,
                    "FromItemCard": None,
                    "SellUnitFactor": None,
                    "OrignalPrice": default_uom_price['price'] if default_uom_price else 0.00,
                    "SellUnitOrignalPrice": default_uom_price['price'] if default_uom_price else 0.00,
                    "SellUnit": item.get('stock_uom'),
                    "SellUnitName": item.get('stock_uom'),
                    "SellUnitNameEng": item.get('stock_uom'),
                    "SellUnitPoint": item.get('stock_uom'),
                    "ActualPrice": default_uom_price['price'] if default_uom_price else 0.00,
                    "ItemTotalprice": None,
                    "TotalQuantity": 1,
                    "MG_code": item['item_group'],
                    "SG_Code": item['brand'],
                    "IsFavourite": default_fav,
                    "SellPoint": None,
                    "OrignalSellPoint": None,
                    "MinSalesOrder": 1,
                    "Isbundle": None,
                    "NotChangeUnit": None
                }

                # Check if the item is in the cart
                if item['item_code'] in cart_dict:
                    cart_item = cart_dict[item['item_code']]
                    item_details.update({
                        "OrignalPrice": None,
                        "SellUnitOrignalPrice": float(cart_item['rate']),
                        "SellUnit": cart_item['uom'],
                        "ActualPrice": float(cart_item['rate']),
                    })

                items_with_uom_and_prices.append(item_details)
    frappe.local.response["data"] = items_with_uom_and_prices


@frappe.whitelist(allow_guest=True)
@jwt_required
def get_items_search(**kwargs):
    # Fetch all items with 'item_name' field
    items = frappe.get_all(
        'Item',
        fields=['item_name'],
        ignore_permissions=True
    )
    # Extract only the item_name values
    item_names = [item['item_name'] for item in items]
    # Return the list of item names
    frappe.local.response["data"] = item_names


@frappe.whitelist(allow_guest=True)
@jwt_required
def save_favourite_item(**kwargs):
    print(11111111111)
    customer_id = kwargs.get("Cus_Id")
    item_code = kwargs.get("itemcode")
    favorite_doc = frappe.get_value("Favorite", {'customer': customer_id}, 'name')
    fav_items_dict = frappe.db.get_list("Favorite Item", filters={'parent': favorite_doc}, fields=['item', 'name'])
    for i in fav_items_dict:
        if item_code == i.get("item"):
            frappe.db.delete("Favorite Item", i.get("name"))
            frappe.db.commit()
            return "Marked as unFavourite!"
    print(8888888888888888)
    new_fav_item = frappe.get_doc({
        'doctype': 'Favorite Item',
        'parent': favorite_doc,
        'parenttype': 'Favorite',
        'parentfield': 'items',
        'item': item_code
    })
    new_fav_item.insert()
    frappe.db.commit()
    return "Marked as Favourite!"


def get_best_selling_items(**kwargs):
    customer = kwargs.get('CustomerID')
    # Fetch all items with 'item_name' field
    items = frappe.get_all(
        'Item',
        fields=['item_name'],
        ignore_permissions=True
    )
    # Extract only the item_name values
    item_names = [item['item_name'] for item in items]
    # Return the list of item names
    frappe.local.response["data"] = item_names
