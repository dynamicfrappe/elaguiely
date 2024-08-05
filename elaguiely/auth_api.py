
import frappe
from frappe import _
from elaguiely.elaguiely.functions import (create_customer ,
					   								 create_cart ,
														 create_favorite)


from frappe.core.doctype.user.user import generate_keys
"""
defaulte respons 
{
	"statusCode": "SUCCESS", //"Failure"
	"message": "message from back-end in case of failure",
	"data": {
		"id": 18,
		"name": "Afifi",
		"phone": "01020456040"
	}
}



"""
#elaguiely.auth_api
@frappe.whitelist(allow_guest=True)
def login(usr=False, pwd=False ,cmd= False , *args ,**kwargs):
	
	try:
		login_manager = frappe.auth.LoginManager()
		login_manager.authenticate(user=usr, pwd=pwd)
		login_manager.post_login()
	except Exception as er:
		frappe.clear_messages()
		frappe.local.response['http_status_code'] = 401
		frappe.local.response['message'] =_("user name or password not valid")
		frappe.local.response['data'] = {"errors" : "Authentication Error"}
		return	
	api_generate = generate_keys(frappe.session.user)
	
	if api_generate :
		cart = False
		user = frappe.get_doc('User', frappe.session.user)
		frappe.local.response['http_status_code'] = 200
		frappe.local.response["message"] = _("Authentication success") 
		if user.customer : 
			# _{{frappe.session.user}}_
			cart_key = f"{frappe.session.sid}_{frappe.session.user}_cart"
			favorite_key = f"{frappe.session.sid}_{frappe.session.user}_fav"
			cart = create_cart(user.customer)
			fav =  create_favorite(user.customer)
		try :
			del frappe.local.response["exc_type"]
		except :
			pass
		cart_key = f"{frappe.session.sid}_{frappe.session.user}_cart"
		favorite_key = f"{frappe.session.sid}_{frappe.session.user}_fav"
		#set user data to cach
		user_key =  f"{frappe.session.sid}_{user.username}"
		
		data =  {
			
			"sid":frappe.session.sid,
			"api_key":user.api_key,
			"api_secret":api_generate.get("api_secret"),
			"language" : user.language  if user.language\
							else frappe.db.get_single_value('System Settings', 'language'), 
			"phone" : user.phone  , 
			"username":user.username,
			"email":user.email , 
			"customer" : user.customer , 
			"cart" : cart.name , 
			"cart_items"  : len(cart.cart_item) ,
			"fav" :fav.name , 
			"fav_count" : len(fav.items)
			 
		}
		frappe.db.commit()
		#frappe.cache().set_value(user_key, data)
		frappe.local.response["data"] = data
	else :
		frappe.local.response['http_status_code'] = 400
		frappe.response["message"] =_("Generate Keys Error")
		frappe.local.response['data'] = {}

# def generate_keys(user):
# 	try :
# 		user_details = frappe.get_doc('User', user)
# 		api_secret = frappe.generate_hash(length=15)
# 		if not user_details.api_key:
# 			api_key = frappe.generate_hash(length=15)
# 			user_details.api_key = api_key
# 		user_details.api_secret = api_secret
# 		user_details.save(ignore_permissions=True)
# 		if user_details.is_customer and not user_details.customer :
# 			#create user 
# 			create_customer(user_details)
# 		return api_secret
# 	except :
# 		return False

@frappe.whitelist( allow_guest=True )
def check_usr():
	return frappe.session.use



@frappe.whitelist(allow_guest=True)
def register(*args ,**kwargs):
	return register_create_customer(**kwargs)
	


def register_create_customer(**kwargs):
	selling_settings = frappe.get_single("Selling Settings")
	if  frappe.db.exists("User",{"phone":kwargs.get("phone"),"email":kwargs.get("email")}):
		frappe.local.response['http_status_code'] = 400
		frappe.local.response['message'] = _("Employee With Email And Phone Number Already Exist")
		return
	if  selling_settings.customer_group and  selling_settings.territory:
		try:
			customer = frappe.new_doc("Customer")
			customer.customer_name = kwargs.get('username')
			customer.customer_group = selling_settings.customer_group
			customer.territory = selling_settings.territory
			customer.customer_type = kwargs.get('customer_type') if  kwargs.get('customer_type') in ('Company','Individual') else "Individual"
			customer.insert(ignore_permissions=True)
			#**create contact
			contact = frappe.new_doc('Contact')
			contact.first_name = customer.customer_name
			contact.append('phone_nos',{
				"phone":kwargs.get('phone'),
				"is_primary_mobile_no":1
			})
			contact.append('links',{
				"link_doctype":"Customer",
				"link_name":customer.name,
				"link_type":customer.customer_name,
			})
			contact.append('email_ids',{
				"email_id":kwargs.get("email"),
				"is_primary":1
			})
			contact.insert(ignore_permissions=True)
			#** create user 
			new_user = create_user_if_not_exists(customer.name,**kwargs)
			#**link cst with contact
			contact_name = frappe.db.get_value('Dynamic Link',{'link_doctype':'Customer', 'link_name':customer.name}, ['parent'])
			# return {"contact_name":contact_name}
			customer.customer_primary_contact = contact_name
			customer.mobile_no = contact.mobile_no
			customer.account_manager = new_user.name
			customer.save(ignore_permissions=True)
			frappe.db.commit()
			return  login(usr=new_user.email, pwd=kwargs.get('password'))
		except Exception as er:
			frappe.local.response['http_status_code'] = 401
			frappe.local.response['message'] =str(er)
			frappe.local.response['data'] = {"errors" : "Not Completed Data"}
			return
	else :
		frappe.local.response['http_status_code'] = 404
		frappe.local.response['message']  = "Please set customer group and territory"
		frappe.local.response['data'] = {"errors" : "Not Completed Data"}



@frappe.whitelist(allow_guest=True)
def create_user_if_not_exists(cst,**kwargs):
	"""
	this function will create user and set  role to e-commerce
	
	"""
	if frappe.db.exists("User", kwargs.get('email')):
		return
	new_user = frappe.new_doc("User")
	new_user.update({
			"doctype": "User",
			"send_welcome_email": 0,
			"user_type": "System User",
			"first_name": kwargs.get('username'),
			"email": kwargs.get('email'),
			"enabled": 0,
			"is_customer": 1,
			"customer": cst,
			"phone": kwargs.get('phone'),
			"new_password":kwargs.get('password'),
			# "roles": [{"doctype": "Has Role", "role": "Customer"}],
			"roles": [{ "role": "Customer"} ,{"role" :"System Manager"}],
		})
		
	new_user.insert(ignore_permissions=True)
	new_user.save(ignore_permissions=True)
	role = frappe.get_doc("Role Profile" , 'e-commerce')
	roles = [role.role for role in role.roles]
	new_user.add_roles(*roles)
	new_user.save()
	frappe.db.commit()
	return new_user
		




		


	