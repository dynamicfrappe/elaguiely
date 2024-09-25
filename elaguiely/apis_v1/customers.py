import frappe
import json 
from .utils import get_reponse 
from frappe import _ 


@frappe.whitelist()
def get_address(*args , **kwargs) :
   user = frappe.get_doc('User', frappe.session.user)
   frappe.local.response["message"] = _(" Success ")
   frappe.local.response['http_status_code'] = 200
   frappe.local.response["data"] = get_customer_address(user.customer)





@frappe.whitelist(allow_guest =True )
def address_info(address):
   print(frappe.local.request.method)
   data =frappe.get_doc("Address" , address)
   frappe.local.response["message"] = _(" Success ")
   frappe.local.response['http_status_code'] = 200
   frappe.local.response["data"] = data
def get_customer_address(customer ,name = None) :
   sql_str = f""" 
   SELECT a.parent as name ,
   b.address_title,
   b.address_line1,
   b.address_line2,
   b.city,
   b.state ,
   b.pincode ,
   b.country ,
   b.building_no ,
   b.floor_no ,
   b.phone ,
   b.latitude ,
   b.longitude, 
   b.apartment_no
   FROM `tabDynamic Link` a 
   INNER JOIN `tabAddress` b ON 
    a.parent = b.name
      WHERE a.parenttype ='Address' and a.link_doctype ="Customer" 
   and a.link_name  = '{customer}'
   """ 
   if name :
      sql_str = sql_str + f"AND b.address_title = '{name}'"
   data = frappe.db.sql(sql_str , as_dict =1)
   return data
@frappe.whitelist(allow_guest =True)
def create_address(*args , **kwargs):
   user = frappe.get_doc('User', frappe.session.user)
   shipping_address = kwargs 
   customer = frappe.get_doc("Customer" , user.customer)
   if shipping_address:
      # country = get_country_name(shipping_address.get("country"))
      # if not frappe.db.exists("Country", country):
      country = "Egypt"
      tiltel = f"{customer.name}-{frappe.generate_hash(length=6)}"
      try :
         frappe.get_doc({
               "doctype": "Address",
               "woocommerce_address_id": "Shipping",
               "address_title": tiltel ,
               "address_type": "Shipping",
               "address_line1": shipping_address.get("address_1") or "Address 1",
               "address_line2": shipping_address.get("address_2"),
               "city": shipping_address.get("city") or "City",
               "state": shipping_address.get("state"),
               "pincode": shipping_address.get("postcode"),
               "country": country,
               "building_no" : shipping_address.get("building_no"),
               "floor_no":shipping_address.get("floor_no"),
               "apartment_no":shipping_address.get("apartment_no"),
               "phone": shipping_address.get("phone"),
               "latitude" : shipping_address.get("latitude") , 
               "longitude" : shipping_address.get("longitude") , 
               "email_id": shipping_address.get("email"),
               "links": [{
                  "link_doctype": "Customer",
                  "link_name": customer.name
               }]
         }).insert()
         
      except Exception as e:
         error = frappe.new_doc("Error Log")
         error.method="create_customer_address"
         error.error = e
         error.save()
         frappe.local.response["message"] = _("Can Not create customer address")
         frappe.local.response['http_status_code'] = 404
         frappe.local.response["data"] = {_("error") : _("Error created") ,
                                          _("name") : error.name}
   frappe.local.response["message"] = _(" Address Created")
   frappe.local.response['http_status_code'] = 200
   frappe.local.response["data"] = get_customer_address(customer.name ,tiltel)[0]
  