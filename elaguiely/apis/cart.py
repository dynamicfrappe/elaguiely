qimport frappe
from frappe import _ 
from elaguiely.elaguiely.functions import (create_customer ,
					   								 create_cart ,
														 create_favorite)



from elaguiely.apis.item import get_items


@frappe.whitelist()
def cart_details(cart):
   data =frappe.get_doc("Cart" , cart)
   frappe.local.response["message"] = _(" Success ")
   frappe.local.response['http_status_code'] = 200
   frappe.local.response["data"] = data

@frappe.whitelist()
def add_to_cart(item ,price = False,qty = False, 
                 offer = False, price_list= False , 
                *args ,**kwargs) :
   
   """
   params 
   item : item_code  ! REQUIRED 
   price : the real price after apply discount if there are discount  ! REQUIRED !
   qty : qty to add defaulte will be one if want to remove send -1 or all  to remove all  ! Not required !
   offer : offer id if there are offer  ! Not required !
   price_list : if there are offer then you should add price before discount here to validate it 
   ! REQUIRED only with offer ! 
   
   """

   
   user = frappe.get_doc('User', frappe.session.user)
   if not qty :
      qty = 1 
   customer = user.customer 
   if not customer :
      frappe.local.response["message"] = _("Can Not Find Customer")
      frappe.local.response['http_status_code'] = 404
      frappe.local.response["data"] = {_("error") : _("Error Request")}
      return
   #set Cached Data here 
   cart_key = f"{{frappe.session.sid}}_cart"
   cart  = frappe.cache().get_value(cart_key)
   if cart :
      try :
         cart = frappe.get_doc("Cart" , cart.get("name"))
      except :
          """
          if error heppend then create new cart 
          """
          cart = None
   if not cart :
         cart = create_cart(user.customer)
   #validate Item 
   item_obj = False 
   try :
       item_obj = frappe.get_doc('Item',item)

   except Exception as E :
      frappe.local.response["message"] = _("Can Not Find Item")
      frappe.local.response['http_status_code'] = 404
      frappe.local.response["data"] = {_("error") : _(f"{E}")}
   message = "No Action"
   in_cart = False
   for item in cart.cart_item :
      if item.item == item_obj.name :
         in_cart = True
         #check qty 
         if float(item.qty) + float(qty or 0) <= 0 :
            cart.remove(item)
            cart.save()
            frappe.db.commit()  
            message = _(f"Item { item_obj.item_name }removed From Cart ") 
         if float(item.qty)  +  float(qty or 0) > 0 : 
            item.qty = float(item.qty) + float(qty)
            cart.save()
            frappe.db.commit()
            message = _(f"Item { item_obj.item_name }updated qty  {item.qty }") 
   if not in_cart:
      d  = get_items( filters={"item_code" : item_obj.name })
      item = frappe.local.response.get("data")[0]              
      cart.append("cart_item" , {
         "item" :item_obj.name ,
         "qty" : float(qty) ,
         "offer" : offer if offer else  None , 
         "rate" : float(item.after_discount or 0) ,
         "discount_amount" : item.item_discount
      })
      cart.save()
      frappe.db.commit()
      message  = _(f"Item { item_obj.item_name }added To Cart   {item.qty }") 
   frappe.local.response["message"] = message
   frappe.local.response['http_status_code'] = 200
   d  = get_items( filters={"item_code" : item_obj.name })
   if frappe.local.response.get("data") :
      if len(frappe.local.response.get("data") ) > 0 :
         item = frappe.local.response.get("data")[0]
         frappe.local.response["data"] = item