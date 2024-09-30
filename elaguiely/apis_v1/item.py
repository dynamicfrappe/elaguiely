import frappe
from frappe import _

from .jwt_decorator import jwt_required
from .utils import get_item_prices


@frappe.whitelist(allow_guest=True)
@jwt_required
def get_items_prices(**kwargs):
    items_with_uom_and_prices = []

    # Get all items
    items = frappe.get_all(
        'Item',
        fields=[
            'name', 'item_name', 'item_code', 'arabic_name', 'image', 'description', 'brand', 'item_group',
            'standard_rate', 'stock_uom'
        ],
        ignore_permissions=True
    )

    for item in items:
        # Fetch prices related to the item
        uom_prices = get_item_prices(item['name'])
        if any([uom_prices[0].get('name'), uom_prices[1].get('name'), uom_prices[2].get('name')]):
            # Determine which UOM matches the default UOM (stock_uom)
            default_uom_price = None
            for uom_price in uom_prices:
                if uom_price['name'] == item['stock_uom']:
                    default_uom_price = uom_price
                    break
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
                "U_Code2": uom_prices[1]['name'],
                "Unit2Name": uom_prices[1]['name'],
                "Unit2NameEng": uom_prices[1]['name'],
                "Unit2OrignalPrice": uom_prices[1]['price'],
                "Unit2Price": uom_prices[1]['price'],
                "Unit2Factor": uom_prices[1]['factor'],
                "U_Code3": uom_prices[2]['name'],
                "Unit3Name": uom_prices[2]['name'],
                "Unit3NameEng": uom_prices[2]['name'],
                "Unit3OrignalPrice": uom_prices[2]['price'],
                "Unit3Price": uom_prices[2]['price'],
                "Unit3Factor": uom_prices[2]['factor'],
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
                "MG_code": item['item_group'],
                "SG_Code": item['brand'],
                "IsFavourite": None,
                "SellPoint": None,
                "OrignalSellPoint": None,
                "MinSalesOrder": None,
                "Isbundle": None,
                "NotChangeUnit": None
            }
            customer_id = kwargs.get("CustomerID")
            if not customer_id:
                frappe.local.response["message"] = _("CustomerID is required")
                frappe.local.response['http_status_code'] = 400
                return

            # Fetch the customer document
            customer = frappe.get_doc("Customer", customer_id)
            cart = frappe.get_doc("Cart", {'customer': customer.name}, fields=['*'])
            if cart:
                for c_i in cart.cart_item:
                    if c_i.item == item['item_code']:
                        item_details.update({
                            "OrignalPrice": None,
                            "SellUnitOrignalPrice": float(c_i.get('rate')),
                            "SellUnit": c_i.get('uom'),
                            "SellUnitName": c_i.get('uom'),
                            "SellUnitNameEng": c_i.get('uom'),
                            "SellUnitPoint": c_i.get('uom'),
                            "ActualPrice": float(c_i.get('rate')) if c_i.get('rate') else None,
                        })
            items_with_uom_and_prices.append(item_details)
    frappe.local.response["data"] = items_with_uom_and_prices
