import frappe
from frappe import _ 
from .utils import get_reponse 



"""
this fuction will return  
Brand 
Item Group 
Category 

"""

@frappe.whitelist(allow_guest =True )
@get_reponse
def get_brands(*args , **kwargs) :
   data = frappe.db.sql(""" SELECT brand as en_name , arabic_name  ,name as sid  ,image FROM    `tabBrand`  """ ,as_dict=1)
   return data

@frappe.whitelist(allow_guest =True )
@get_reponse
def get_item_groups(*args , **kwargs) :
   data = frappe.db.sql(""" SELECT item_group_name as en_name , arabic_name  ,name as sid , image FROM    `tabItem Group`  """ ,as_dict=1)
   return data

@frappe.whitelist(allow_guest =True )
@get_reponse
def get_category(*args , **kwargs) :
   data = frappe.db.sql(""" SELECT name1 as en_name , arabic_name  , name as sid  FROM    
   `tabCategory`  """ ,as_dict=1)
   return data



@frappe.whitelist(allow_guest =True )
@get_reponse
def get_offers(*args, **kwargs) :
   data = frappe.db.sql(""" 
   SELECT title  ,image ,name as sid
   FROM `tabPricing Rule` WHERE selling=1 and disable = 0
   """,as_dict =True)
   return data


