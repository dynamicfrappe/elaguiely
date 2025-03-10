from .setting import *
import frappe
from frappe import _
from frappe.utils import today
import time 

def memoize(func):
    cache = {}
    # Inner wrapper function to store the data in the cache
    def wrapper(*args):
        if args in cache:
            return cache[args]
        else:
            result = func(*args)
            cache[args] = result
            return result
    return wrapper

def get_customer_default_price_list(cutomer) :
   """
   customer : string customer name 
   return price list from customer default 
   """


from erpnext.accounts.report.customer_ledger_summary.customer_ledger_summary import execute

@frappe.whitelist()
def get_closing_balance_for_customer(customer):
	company = frappe.defaults.get_user_default("Company")
	from_date = frappe.defaults.get_user_default("fiscal_year_start_date")
	to_date = frappe.utils.today()
	party = customer
	customer_name = frappe.get_value("Customer", customer, "customer_name")
	filters = {
		"from_date": from_date,
		"to_date": to_date,
		"company": company,
		"party_type": "Customer",
		"party": party,
		"party_name": customer_name
	}
	data = execute(filters)
	if data and data[1] and data[1][0]:
		return data[1][0].get("closing_balance")
	else:
		return 0


def get_customer_price_list():
   price_list =  frappe.db.get_single_value('E Commerce Settings', 'price_list')
   try :
      customer = frappe.get_user().doc.customer 
      group = frappe.get_doc("Customer" , customer).customer_group
      if DEBUG :
         print(group)
      if group :
         price_list =frappe.get_value("Customer" ,customer ,"default_price_list") or  frappe.get_doc("Customer Group" ,group ).default_price_list
         if DEBUG :
            print(price_list)
   except :
      pass
   return price_list

def get_offer_items_codes():
   # st = time.time()
   # add memory optmize to cashed data and improvre perform 
   #item for item_code 
   price_list = get_customer_price_list()
   items = frappe.db.sql(f"""
   select name from `tabItem` WHERE 
      item_group in (select item_group FROM `tabPricing Rule Item Group`
        WHERE parent
   in (  
     SELECT name FROM `tabPricing Rule`  WHERE  '{today()}'  between date(valid_from) and date(valid_upto) 
     and disable = 0 and for_price_list = '{price_list}'
   )) 
      or item_code in ( SELECT item_code FROM `tabPricing Rule Item Code` 
         WHERE parent  
   in (  
     SELECT name FROM `tabPricing Rule`  WHERE  '{today()}'  between date(valid_from) and date(valid_upto)
      and disable = 0 and for_price_list = '{price_list}'
   ))
      or brand in (select brand  FROM `tabPricing Rule Brand`   WHERE parent
   in (  
     SELECT name FROM `tabPricing Rule`  WHERE  '{today()}'  between date(valid_from) and date(valid_upto)
      and disable = 0 and for_price_list = '{price_list}'
   )) 
   
   """)

   print("Out SQL" , items)
   data = []
   if items and len(items) > 0 :
      data = [code[0] for code in items ]
      print('Execution time:', data, 'seconds')
      return data
   return data
"""
Create decorator to override response 
"""

def get_reponse(fn ,*args,**kwargs) :
   def wrapper_func(*args,**kwargs):
      data_all  = fn( kwargs)
      user  = frappe.get_user().doc.full_name 
      if not user or user == "Guest":
         frappe.local.response["message"] = _("Authentication Error")
         frappe.local.response['http_status_code'] = 401
         frappe.local.response["data"] = {_("error") : _("Unauthorized")}
         
      for data in data_all :
         if data.get("en_name") and data.get("arabic_name") :
            user_obj = frappe.get_doc('User', frappe.session.user)
            lang = user_obj.language  if user_obj.language\
                        else frappe.db.get_single_value('System Settings', 'language') 
            if lang == "ar" :
               data["name"] = data.get("arabic_name") 
            else :
               data["name"]  = data.get("en_name") 
            try :
               del data["arabic_name"]
               del data["en_name"]
            except :
               pass
         if data.get("en_name") and not data.get("arabic_name") :
            data["name"]  = data.get("en_name") 
            try :
               del data["en_name"]
               del data["arabic_name"]
            except :
               pass
       
      frappe.local.response['http_status_code'] = 200
      frappe.local.response["data"] =data_all
      frappe.local.response["message"] = _("Success")
      # return  	frappe.local.response   
   return wrapper_func




# favorite functuion 
def chek_item_in_favorit(item ) :
   """
   this fuction to set item in_favorites value
   """
   fav_key = f"{{frappe.session.sid}}_fav"
   fav = frappe.cache().get_value(fav_key)
   user = frappe.get_doc('User', frappe.session.user)
   if not fav :
         fav =  create_favorite(user.customer)
   fav = frappe.get_doc("favorite" , fav.get("name") )
   ext = 0
   for fav_item in fav.items :
      if fav_item.item == item :
         ext =1
   return ext 

# offer Fuction 
# price rule will apply in only price condetion 
def apply_roles(item , rules=[]) :
   discont = float(item.get("item_discount") or 0 )
   price   = float(item.get("item_price") or 0 )
   last_price = float(item.get("item_price") or 0 )
   offer =" " #rules
   for rule in rules :
      r = frappe.get_doc("Pricing Rule" , rule) 
      # get caculated method  Discount Amount
      if r.rate_or_discount == "Rate" :  
         last_price  = r.rate
      if r.rate_or_discount == "Discount Percentage" :  
         last_price = last_price - (( float(r.discount_percentage or 0 ) /100) * last_price)
      if r.rate_or_discount == "Discount Amount" :
         #  Discount Amount	
          last_price = last_price -  float(r.discount_amount or 0 )
   item["after_discount"] =last_price 
   item["item_discount"] = float(price) - float(last_price or 0)
   item["offer"] = offer
   # return item
def caculate_item_base_on_offer(item) :
   #get offers apply on item
   price_list = get_customer_price_list()
   data = frappe.db.sql(f""" 
   SELECT name FROM `tabPricing Rule` WHERE name in 
   (
   SELECT parent FROM `tabPricing Rule Item Group` 
   WHERE item_group = '{item.get("item_group")}'
   AND  for_price_list = '{price_list}' 
   AND disable = 0
   ) 
   or name in
   (
   SELECT parent FROM `tabPricing Rule Brand` 
   WHERE brand = '{item.get("brand")}'
   AND  for_price_list = '{price_list}' 
   AND disable = 0
   )
   or name in 
   (
   SELECT parent FROM `tabPricing Rule Item Code` 
   WHERE item_code = '{item.get("sid")}'
   AND  for_price_list = '{price_list}' 
   AND disable = 0
   )
   """ ,as_dict=1) 
   if DEBUG :
      print("DATA" ,data)
   apply_roles(item , data)
   # return item 
def check_item_offer_to_apply(item) :
   """
      this fuction to set item has_offer value
      and if item has offer
      set offer name and update item price 

   """
   codes = get_offer_items_codes() or []
   if DEBUG :
      print("Codes" , codes)
   try :
      if item.get("sid") in codes :
         item["has_offer"] = True
         item = caculate_item_base_on_offer(item)
   except :pass
      # get _item _offer 
   # return item


def update_items(fn,*args,**kwargs) :
   """
    this decoreator is set for items to update item price 
    chage brand name and item group name in tanslate
    update item name 

    """
   def item_func(*args,**kwargs):
      items = fn( kwargs)
      user  = frappe.get_user().doc.full_name 
      # if not user or user == "Guest":
      #    frappe.local.response["message"] = _("Authentication Error")
      #    frappe.local.response['http_status_code'] = 401
      #    frappe.local.response["data"] = {_("error") : _("Unauthorized")}
      for item in items: 
         #set Arabic Name 
         if item.get("en_name") and item.get("arabic_name") :
            user_obj = frappe.get_doc('User', frappe.session.user)
            lang = user_obj.language  if user_obj.language\
                        else frappe.db.get_single_value('System Settings', 'language') 
            if lang == "ar" :
               item["name"] = item.get("arabic_name") 
            else :
               item["name"]  =item.get("en_name") 
            try :
               del item["arabic_name"]
               del item["en_name"]
            except :
               pass
         if item.get("en_name") and not item.get("arabic_name") :
            item["name"]  =item.get("en_name") 
            try :
               del item["en_name"]
               del item["arabic_name"]
            except :
               pass
         #check if 
         item = check_item_offer_to_apply(item)  
         # check vaforite 
         try :
          if item :
             item["in_favorites"] =chek_item_in_favorit(item.sid)
         except Exception as E :
            #create error 
            frappe.local.response["error"] = f"{E}"
            pass
      if DEBUG :
         print("Returm Items  DEBUG Message" ,items)
      frappe.local.response['http_status_code'] = 200
      frappe.local.response["data"] =items
      frappe.local.response["message"] = _("Success")
      # return items
   return item_func