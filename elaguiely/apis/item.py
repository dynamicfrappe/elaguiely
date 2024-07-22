import frappe
from frappe import _ 
from .utils import  update_items ,get_customer_price_list
from .setting import DEBUG
from elaguiely.elaguiely.functions import (
                                            create_cart ,
                                            create_favorite
                                          )


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
@frappe.whitelist(allow_guest =0)
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
         a.item_group , a.brand , a.description , a.image , 
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
   return items

