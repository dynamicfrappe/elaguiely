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


def get_url():
	base_url = frappe.utils.get_url()
	site_config = frappe.get_site_config()
	domains = site_config.get("domains", [])

	url = ""

	if isinstance(domains, list) and domains:

		domain_info = domains[0]
		url = domain_info.get("domain") if isinstance(domain_info, dict) else None
	else:

		port = site_config.get('nginx_port', 8002)  
		url = f"{base_url}:{port}"

	return url


@frappe.whitelist(allow_guest = 0)
def profile(*args , **kwargs):
	user = frappe.session.user
	if user:
		customer = frappe.get_value("User", user , 'customer')
		profile = frappe.db.sql(f""" select customer_name , customer_type , mobile_no , email_id , primary_address as address , customer_primary_address from `tabCustomer` where name = '{customer}' """ , as_dict = 1 )
		if profile:
			if profile[0].get('customer_primary_address'):
				address = frappe.get_value("Address" , profile[0].get('customer_primary_address') , ['address_line1 as address_line' , 'city as area' , 'state as city' , 'country'],as_dict=1)
				profile[0]['address'] = address

		frappe.response["message"] =_("the profile data")
		frappe.local.response["data"] = profile
		frappe.local.response['http_status_code'] = 200
	else:
		frappe.local.response['http_status_code'] = 400
		frappe.response["message"] =_("Error with auth")
		frappe.local.response['data'] = {}

