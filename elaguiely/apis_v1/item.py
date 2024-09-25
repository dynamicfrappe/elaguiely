import frappe
from frappe import _

from .jwt_decorator import jwt_required
from .utils import  update_items ,get_customer_price_list
from .setting import DEBUG
from elaguiely.elaguiely.functions import (
                                            create_cart ,
                                            create_favorite
                                          )
from elaguiely.apis.api import get_url

"""
response data  {
   "sid" : item code , done
   "name" : item name , done
   "item_group" : group ,done
   "barnd" : brand ,done
   "stock_uom" : UOM depend on price  done
   "description" : item description  ,done
   "item_in_cart" :  if item in cart , 
   "cart_qty" : "check item qty in cart if customer aleardy add to cart" done ,
   "cart_amount" : "total Item Prcie in cart " , 
   "in_favorites" : True or False item in favorite  done ,
   "item_price" item price list rate  done, 
   "item_discount" : discount amount  done,
   "after_discount" : 00  done, 
   "offer id" : to save the offer done  ,
   "image" : link to item image  , done
   "in_stock" : check if item has stock in any wharehouse  not done ,
   "avaliabe_stock" : caculate available qty to orderd from item stock  done ,
}


"""





# Api for get Brand / Item Group / Category / item detaild  
@frappe.whitelist(allow_guest = True)
@update_items
def get_items (filters = {} ,*args , **kwargs) :
   """
   cart_key = f"{{frappe.session.sid}}_{{frappe.session.user}}_cart"
   favorite_key = f"{{frappe.session.sid}}_{{frappe.session.user}}_fav"
   Get simple of item without filters 
   required data to get Price 
   price list / --from user info 
   price list defaulte value from e commerce settings  done
   update price list not done 
   """
   #update price list 
   if DEBUG :
       print ("user" , frappe.get_user().doc.full_name )
   price_list  = get_customer_price_list()   
   warehouse = False 
   sql_qty = "(SELECT SUM(actual_qty) - SUM(reserved_qty) FROM `tabBin` WHERE item_code =sid ) "
   try :
       warehouse = frappe.db.get_single_value('Stock Settings', 'default_e_warehouse')
       if warehouse:
         sql_qty = f"(SELECT SUM(actual_qty) - SUM(reserved_qty)  FROM `tabBin` WHERE item_code =sid and  warehouse = '{warehouse}') "
   except :
       warehouse = False
   # check stock in warehouses 
   if DEBUG :
       print("price list " , price_list)
   cart_key = f"{frappe.session.sid}_{frappe.session.user}_cart"
   favorite_key = f"{frappe.session.sid}_{frappe.session.user}_fav"
   cart = frappe.cache().get_value(cart_key) #create_cart(frappe.get_user().doc.customer)# frappe.cache().get_value(cart_key)
   favorire = frappe.cache().get_value(favorite_key) #create_favorite(frappe.get_user().doc.customer) 
   if DEBUG :
       print("Cart" , cart.name , "Favorite" , favorire)
   cart_sql = "0  as item_in_cart , 0 as cart_qty , 0 as cart_amount  "
   favorire_sql = '0'
   url = get_url()
   print(url)
   if cart :
       if cart.get("name") :
           print(cart.get("name"))
           cart_name = cart.get("name") 
           cart_sql = f"""
           0  as item_in_cart , 
           (SELECT SUM(b.qty) FROM  `tabCart Item`  b  INNER JOIN 
           `tabCart` a 
           ON b.parent = a.name  
                     WHERE a.name = '{cart_name}' and b.item = sid) as cart_qty ,
                     0 as cart_amount """
    
   data = f"""
         select a.name as sid  , a.item_name as en_name , a.arabic_name as arabic_name ,b.uom , 
         a.item_group , a.brand , a.description , a.image as image, 
          0 as in_favorites ,
         0 as has_offer ," " as offer ,a.max_order as max_order ,
         b.price_list_rate
            as item_price ,
         10 as item_discount ,
           b.price_list_rate as  after_discount ,
          {cart_sql}
          , 
           {sql_qty} as avaliabe_stock
            FROM  
         `tabItem` a 
         INNER JOIN
         `tabItem Price` b
         ON b.item_code = a.item_code 
            WHERE b.price_list='{price_list}' and b.selling = 1
      """
   if filters.get("best_sell") : 
      data = data + "AND a.best_sell = 1 "
   if filters.get("new_arrive") :
       data = data + "AND a.new_arrive = 1 "
   if filters.get("item_group") :
       data = data + f"""AND a.item_group = '{filters.get("item_group")}' """
   if filters.get("brand") :
        data = data + f"""AND a.brand = '{filters.get("brand")}' """
   #set offers 
   if filters.get("offer") :
      offer = filters.get("offer")
      data = data+ f"""
                        AND item_code in (
                                          select item_code from `tabItem` WHERE 
                                          item_group in (select item_group FROM `tabPricing Rule Item Group` WHERE parent='{offer}') 
                                          or item_code in ( SELECT item_code FROM
                                                                           `tabPricing Rule Item Code` WHERE parent='{offer}')
                                          or brand in (select brand  FROM `tabPricing Rule Brand` WHERE parent='{offer}')       
                                        )
                    """
      
   if filters.get("favorite") :
       data = data + f""" AND a.name in (select item FROM `tabfavorite Item` WHERE parent = '{filters.get("favorite")}')"""  
   # apply on single item code 
   if filters.get("filters") :
      try :
         if filters.get("filters").get("item_code") :
               print("FOT item Code " ,filters.get("filters").get("item_code"))
               b = filters.get("filters").get("item_code")
               data = data +f"""AND a.item_code ='{b}' """
      except :
          pass
   items = frappe.db.sql(data+"GROUP BY a.item_code ,b.uom" , as_dict =1)
#    items = get_item_price_from_uom(items)
   return items



def get_item_price_from_uom(items , price_list):
    item_price = {}
    for item in items:
        item_code = item.get("sid") 
        item_price = frappe.db.sql(f""" select uom , price_list_rate from `tabItem Price` where item_code = '{item_code}' and selling = 1  and price_list = '{price_list}';""" , as_dict = 1)
        item['item_price'] = item_price
        # item["after_discount"] = item.get('item_price') - item.get('item_discount')
    return items


# Working...
@frappe.whitelist(allow_guest=True)
@jwt_required
def get_items_prices(fav=None, customer_id=None, MainGroupID=None, SubGroup1ID=None, SubGroup2ID=None, SupplierID=None,
                     CustomerID=None, BounsId=None, fromadv=None, advId=None, advtype=None, **kwargs):
    try:
        response = []
        items = []
        filters = {}
        # filters["parent"] = favourite
        if MainGroupID:
            filters["item_group"] = MainGroupID
        if SupplierID:
            filters["brand"] = SupplierID
        if customer_id and fav:
            customer = frappe.get_doc("Customer", customer_id)
            if not customer:
                return {"message": "Invalid Customer", "data": []}
            favourite = frappe.get_doc("favourite", filters=[{'customer_id': customer_id}])
            filters = {}
            filters["parent"] = favourite

            if MainGroupID:
                filters["item_group"] = MainGroupID
            if SupplierID:
                filters["brand"] = SupplierID
            items = frappe.db.get_list("favorite Item", fields=['item'], filters=filters)
        if not fav:
            items = frappe.db.get_list("Item", fields=['*'], filters=filters)

            for item in items:
                uoms = frappe.get_all("UOM Conversion Detail", filters={"parent": item.name},
                                      fields=["uom", "conversion_factor", ])
                print(uoms)
                # Prepare UOM details and fetch prices
                def get_price(item_code, uom):
                    price_list_name = "Standard Selling"  # Adjust this to your price list name
                    price = frappe.db.get_value("Item Price",
                                                {"item_code": item_code, "uom": uom, "price_list": price_list_name},
                                                "price_list_rate")
                    return price or 0  # Return 0 if no price found

                # Fetch UOMs and their corresponding prices
                unit_1 = uoms[0] if len(uoms) > 0 else None
                unit_2 = uoms[1] if len(uoms) > 1 else None
                unit_3 = uoms[2] if len(uoms) > 2 else None

                unit_1_price = get_price(item.item_code, unit_1.uom if unit_1 else item.stock_uom)
                unit_2_price = get_price(item.item_code, unit_2.uom) if unit_2 else None
                unit_3_price = get_price(item.item_code, unit_3.uom) if unit_3 else None

                response.append({
                    "Id": item.item_code,
                    "PreviewImage": None,
                    "NameEng": item.item_name,
                    "Name": item.arabic_name,
                    "Unit1Name": unit_1.uom if unit_1 else item.stock_uom,
                    "Unit1NameEng": unit_1.uom if unit_1 else item.stock_uom,
                    "U_Code1": unit_1.uom if unit_1 else item.stock_uom,
                    "Unit1OrignalPrice": None,
                    "Unit1Price": 20.00,
                    "Unit1Point": None,
                    "Unit1Factor": unit_1.conversion_factor if unit_1 else None,
                    "Unit2Name": unit_2.uom if unit_2 else None,
                    "Unit2NameEng": unit_2.uom if unit_2 else None,
                    "U_Code2": unit_2.uom if unit_2 else None,
                    "Unit2OrignalPrice": None,
                    "Unit2Price": unit_2_price,
                    "Unit2Point": None,
                    "Unit2Factor": unit_2.conversion_factor if unit_2 else None,
                    "Unit3Name": unit_3.uom if unit_3 else None,
                    "Unit3NameEng": unit_3.uom if unit_3 else None,
                    "U_Code3": unit_3.uom if unit_3 else None,
                    "Unit3OrignalPrice": None,
                    "Unit3Price": unit_3_price,
                    "Unit3Point": None,
                    "Unit3Factor": unit_3.conversion_factor if unit_3 else None,
                    "SummaryEng": None,
                    "DescriptionEng": None,
                    "Summary": None,
                    "Description": None,
                    "price": None,
                    "FromItemCard": None,
                    "SellUnitFactor": None,
                    "OrignalPrice": None,
                    "SellUnitOrignalPrice": None,
                    "SellUnitPoint": None,
                    "ActualPrice": 20.00,  # Default to unit_1 price as ActualPrice
                    "ItemTotalprice": None,
                    "SellUnit": None,
                    "SellUnitName": None,
                    "SellUnitNameEng": None,
                    "DiscountPrice": None,
                    "DiscountPercent": None,
                    "TotalQuantity": None,
                    "MG_code": None,
                    "SG_Code": None,
                    "IsFavourite": None,
                    "SellPoint": None,
                    "OrignalSellPoint": None,
                    "MinSalesOrder": None,
                    "Isbundle": None,
                    "NotChangeUnit": None
                })
            frappe.local.response['data'] = response
    except Exception as e:
        return {'status_code': 404, 'message': str(e)}


@frappe.whitelist(allow_guest=True)
@jwt_required
def get_items_prices(fav=None, customer_id=None, MainGroupID=None, SubGroup1ID=None, SubGroup2ID=None, SupplierID=None,
                     CustomerID=None, BounsId=None, fromadv=None, advId=None, advtype=None, **kwargs):
    try:
        response = []
        items = []
        filters = {}
        # filters["parent"] = favourite
        if MainGroupID:
            filters["item_group"] = MainGroupID
        if SupplierID:
            filters["brand"] = SupplierID
        if customer_id and fav:
            customer = frappe.get_doc("Customer", customer_id)
            if not customer:
                return {"message": "Invalid Customer", "data": []}
            favourite = frappe.get_doc("favourite", filters=[{'customer_id': customer_id}])
            filters = {}
            filters["parent"] = favourite

            if MainGroupID:
                filters["item_group"] = MainGroupID
            if SupplierID:
                filters["brand"] = SupplierID

            items = frappe.db.get_list("favorite Item", fields=['item'], filters=filters)
        if not fav:
            # items = frappe.db.get_list("Item", fields=['*'], filters=filters)
            sql_query = """
                    SELECT
                        item.name as item_code,
                        item.item_name,
                        item.stock_uom,
                        item.arabic_name,
                        unit1.conversion_factor AS unit1_factor,
                        unit2.conversion_factor AS unit2_factor,
                        unit3.conversion_factor AS unit3_factor,
                        unit1.uom AS unit1_name,
                        unit2.uom AS unit2_name,
                        unit3.uom AS unit3_name,
                        item_price.price_list_rate AS unit1_price
                    FROM
                        `tabItem` AS item
                    LEFT JOIN
                        `tabUOM Conversion Detail` AS unit1
                    ON
                        unit1.parent = item.name
                    LEFT JOIN
                        `tabUOM Conversion Detail` AS unit2
                    ON
                        unit2.parent = item.name
                    LEFT JOIN
                        `tabUOM Conversion Detail` AS unit3
                    ON
                        unit3.parent = item.name
                    LEFT JOIN
                        `tabItem Price` AS item_price
                    ON
                        item.name = item_price.item_code
                    WHERE
                        item.disabled = 0  -- Exclude disabled items
            """
            if filters:
                sql_query += " AND " + " AND ".join([f"item.{key} = '{value}'" for key, value in filters.items()])
            items = frappe.db.sql(sql_query, as_dict=True)
            response = []
            for item in items:
                unit_2_price = None
                unit_3_price = None
                mapped_item = {
                    "Id": item['item_code'],
                    "PreviewImage": None,
                    "NameEng": item['item_name'],
                    "Name": item.get('arabic_name'),
                    "Unit1Name": item['unit1_name'] if item['unit1_name'] else item['stock_uom'],
                    "Unit1NameEng": item['unit1_name'] if item['unit1_name'] else item['stock_uom'],
                    "U_Code1": item['unit1_name'] if item['unit1_name'] else item['stock_uom'],
                    "Unit1OrignalPrice": None,
                    "Unit1Price": item['unit1_price'] if item['unit1_price'] else 20.00,
                    "Unit1Point": None,
                    "Unit1Factor": item['unit1_factor'] if item['unit1_factor'] else None,
                    "Unit2Name": item['unit2_name'] if item['unit2_name'] else None,
                    "Unit2NameEng": item['unit2_name'] if item['unit2_name'] else None,
                    "U_Code2": item['unit2_name'] if item['unit2_name'] else None,
                    "Unit2OrignalPrice": None,
                    "Unit2Price": unit_2_price,
                    "Unit2Point": None,
                    "Unit2Factor": item['unit2_factor'] if item['unit2_factor'] else None,
                    "Unit3Name": item['unit3_name'] if item['unit3_name'] else None,
                    "Unit3NameEng": item['unit3_name'] if item['unit3_name'] else None,
                    "U_Code3": item['unit3_name'] if item['unit3_name'] else None,
                    "Unit3OrignalPrice": None,
                    "Unit3Price": unit_3_price,
                    "Unit3Point": None,
                    "Unit3Factor": item['unit3_factor'] if item['unit3_factor'] else None,
                    "SummaryEng": None,
                    "DescriptionEng": None,
                    "Summary": None,
                    "Description": None,
                    "price": None,
                    "FromItemCard": None,
                    "SellUnitFactor": None,
                    "OrignalPrice": None,
                    "SellUnitOrignalPrice": None,
                    "SellUnitPoint": None,
                    "ActualPrice": item['unit1_price'] if item['unit1_price'] else 20.00,
                    "ItemTotalprice": None,
                    "SellUnit": None,
                    "SellUnitName": None,
                    "SellUnitNameEng": None,
                    "DiscountPrice": None,
                    "DiscountPercent": None,
                    "TotalQuantity": None,
                    "MG_code": None,
                    "SG_Code": None,
                    "IsFavourite": None,
                    "SellPoint": None,
                    "OrignalSellPoint": None,
                    "MinSalesOrder": None,
                    "Isbundle": None,
                    "NotChangeUnit": None
                }
                response.append(mapped_item)
            frappe.local.response['data'] = response
    except Exception as e:
        return {'status_code': 404, 'message': str(e)}