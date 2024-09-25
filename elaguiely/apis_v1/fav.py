import frappe
from frappe import _ 
from elaguiely.elaguiely.functions import (create_customer ,
					   								 create_cart ,
														 create_favorite)
from elaguiely.apis.item import get_items

@frappe.whitelist(allow_guest =True)
def add_to_fav(item , qty =0) :
   user = frappe.get_doc('User', frappe.session.user)
   if not qty :
      qty = 1 
   customer = user.customer 
   if not customer :
      frappe.local.response["message"] = _("Can Not Find Customer")
      frappe.local.response['http_status_code'] = 404
      frappe.local.response["data"] = {_("error") : _("Error Request")}
      return
   
   fav_key = f"{{frappe.session.sid}}_fav"
   fav  = frappe.cache().get_value(fav_key)
   if fav :
      try :
         fav= frappe.get_doc("favorite" , fav.get("name"))
      except :
          """
          if error heppend then create new cart 
          """
          fav = None
   if not fav :
         fav = create_favorite(user.customer)
   item_obj = False 
   try :
       item_obj = frappe.get_doc('Item',item)
   except Exception as E :
      frappe.local.response["message"] = _("Can Not Find Item")
      frappe.local.response['http_status_code'] = 404
      frappe.local.response["data"] = {_("error") : _(f"{E}")}
   messgae = _(f"Item {item_obj.item_name} not in your list ") 
   
   if int(qty  ) > 0 :
      exit = 0 
      if len(fav.items) > 0 :
         for item in fav.items :
            if item.item == item_obj.name :
                exit = 1
                messgae = _(f"Item {item_obj.item_name} In you list ") 
      if not exit :
         row =  fav.append("items" ,{})
         row.item = item_obj.name 
         fav.save(ignore_permissions=True)
         frappe.db.commit()
         messgae = _(f"Item {item_obj.item_name} Added Successfuly ")
   if int(qty  ) <  0:
      if len(fav.items) > 0 :
         for item in fav.items :
            if item.item == item_obj.name :
               t_td = item
               fav.remove(t_td) 
               fav.save()  
               frappe.db.commit()
               messgae = _(f"Item {item_obj.item_name} Removed  Successfuly ") 

   #frappe.local.response["data"]
   #set item in response 
   d  = get_items( filters={"item_code" :item_obj.name }) 
   if frappe.local.response.get("data") :
      if len(frappe.local.response.get("data") ) > 0 :
         item = frappe.local.response.get("data")[0]
         frappe.local.response["data"] = item
   frappe.local.response['http_status_code'] = 200
   frappe.local.response["message"] =  messgae
   

