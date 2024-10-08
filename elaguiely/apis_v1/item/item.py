import frappe
from frappe import _

from elaguiely.apis_v1.jwt_decorator import jwt_required
from elaguiely.apis_v1.utils import get_bulk_item_prices , stock_qty

# First Testing DONE 
@frappe.whitelist(allow_guest=True)
@jwt_required
def get_items_prices(**kwargs):
    items_with_uom_and_prices = []
    # Fetching coming values
    item_group = kwargs.get('MainGroupID')
    brand = kwargs.get('SubGroup1ID') or kwargs.get("SupplierID")
    customer_id = kwargs.get("CustomerID")
    item_name = kwargs.get("ItemName")
    is_fav = kwargs.get("fav")
    
    if not customer_id:
        frappe.local.response["message"] = _("CustomerID is required")
        frappe.local.response['http_status_code'] = 400
        return
    
    # Fetch customer and cart in one go
    customer_name = frappe.get_value("Customer", customer_id, "name")
    price_list_name = frappe.get_value("Customer", customer_id, "default_price_list") or ""
    cart_items = frappe.get_all(
        "Cart Item",
        filters={'parent': frappe.get_value("Cart", {"customer": customer_name}, "name")},
        fields=["item", "qty", "rate", "uom"]
    ) if customer_name else []

    # Convert cart items to a dictionary for quick lookup
    cart_dict = {item['item']: item for item in cart_items}

    # Fetch favorite items
    fav_items = frappe.get_list("Favorite Item", 
        filters={'parent': frappe.get_value("Favorite", {'customer': customer_id}, 'name')}, 
        fields=['item']) if frappe.get_value("Favorite", {'customer': customer_id}, 'name') else []
    fav_items = [item['item'] for item in fav_items]

    filters = {}
    
    if item_group:
        filters['item_group'] = item_group
    if brand:
        filters['brand'] = brand
    if item_name:
        filters['name'] = item_name
    if is_fav:
        filters['name'] = ['in', fav_items]

    # Fetch all items in one query
    items = frappe.db.get_all(
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
    # Fetch prices for all items in one query
    item_prices = get_bulk_item_prices(item_names)  

    for item in items:
        # Fetch favorite field
        default_fav = item['name'] in fav_items
        # Fetch prices related to the item
        uom_prices = item_prices.get(item['name'], [])

        if uom_prices:  # Ensure prices exist for the item
            # Determine which UOM matches the default UOM (stock_uom)
            default_uom_price = next((uom for uom in uom_prices if uom['price_list'] == price_list_name), None)
            if any([
            uom_prices[0].get('price_list') == price_list_name,
            uom_prices[1].get('price_list') == price_list_name,
            uom_prices[2].get('price_list') == price_list_name
            ]):
                # Total Quantity available in stock_uom
                qty = int(stock_qty(customer_name, item['name']) or 0 )
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

# Testing DONE
@frappe.whitelist(allow_guest=True)
@jwt_required
def get_items_search(**kwargs):
    customer = frappe.local.user.customer
    if not customer:
        frappe.throw(_("Customer not found for the user."), frappe.DoesNotExistError)

    # Fetch the default price list for the customer
    price_list_name = frappe.get_value("Customer", customer, "default_price_list")
    if not price_list_name:
        frappe.throw(_("Default price list not set for the customer."), frappe.DoesNotExistError)

    items = frappe.get_all('Item', fields=['name', 'item_name'], ignore_permissions=True )
    response = []
    for item in items:
        # Check if there is a price exists for that item before listing it
        item_enabled = frappe.db.exists("Item Price", {"item_code": item['name'], "price_list": price_list_name})
        if item_enabled: 
            response.append(item.item_name)

    frappe.local.response["data"] = response

# Testing DONE
@frappe.whitelist(allow_guest=True)
@jwt_required
def save_favorite_item(**kwargs):
    customer_id = kwargs.get("Cus_Id")
    item_code = kwargs.get("itemcode")

    if not customer_id or not item_code:
        frappe.throw(_("Customer ID and Item Code are required."), frappe.MandatoryError)

    favorite_doc_name = frappe.get_value("Favorite", {'customer': customer_id}, 'name')

    if not favorite_doc_name:
        frappe.throw(_("No favorite doc found for this customer."), frappe.DoesNotExistError)
    
    fav_item = frappe.db.get_value("Favorite Item", {"parent": favorite_doc_name, "item": item_code}, "name")

    if fav_item:
        # Item is already marked as favorite, so un-favorite it
        frappe.delete_doc("Favorite Item", fav_item, force=1)
        frappe.db.commit()  # Commit deletion
        frappe.logger().info(f"Item {item_code} removed from favorites for customer {customer_id}.")
        return _("Marked as unFavorite!")
    try:
        # Check if the item exists
        if not frappe.db.exists("Item", item_code):
            frappe.throw(_("The item {0} does not exist.").format(item_code), frappe.DoesNotExistError)

        new_fav_item = frappe.get_doc({
            'doctype': 'Favorite Item',
            'parent': favorite_doc_name,
            'parenttype': 'Favorite',
            'parentfield': 'items',
            'item': item_code
        })
        new_fav_item.insert(ignore_permissions=True)
        frappe.db.commit()  # Commit insertion
        frappe.logger().info(f"Item {item_code} marked as favorite for customer {customer_id}.")
        return _("Marked as Favorite!")
    
    except Exception as e:
        frappe.logger().error(f"Error marking item {item_code} as favorite for customer {customer_id}: {str(e)}")
        frappe.throw(_("An error occurred while marking the item as favorite. Please try again."))


