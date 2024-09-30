import datetime
import json

import frappe
import jwt
from frappe import _

from .jwt_decorator import SECRET_KEY


def generate_jwt_token(user):
	payload = {
		'user': user,
		'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8)  # Token expiration
	}
	token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
	return token


@frappe.whitelist(allow_guest=True)
def login(UserName=None, Password=None, OneSignalUserID=None, deviceKey=None):
	# Check if the mobile or password is missing
	if not UserName or not Password:
		frappe.local.response["http_status_code"] = 400
		frappe.local.response["message"] = _('Mobile number and password are required')
		return

	# Fetch the user by mobile number
	user = frappe.db.get_value('User', {'mobile_no': UserName}, ['name', 'enabled'], as_dict=True)

	# Check if the user exists
	if not user:
		frappe.local.response["http_status_code"] = 404
		frappe.local.response["message"] = _('User not found')
		return

	# Check if the user is enabled
	if not user.enabled:
		frappe.local.response["http_status_code"] = 403
		frappe.local.response["message"] = _('User account is disabled')
		return

	# Check the password using Frappe's authentication mechanism
	try:
		frappe.auth.check_password(user.name, Password)
	except frappe.AuthenticationError:
		frappe.local.response["http_status_code"] = 401
		frappe.local.response["message"] = _('Invalid password')
		return

	# Generate JWT token for the user
	token = generate_jwt_token(user.name)

	# Fetch user document and related customer document
	user_doc = frappe.get_doc("User", user.name)
	customer = frappe.get_doc("Customer", user_doc.customer)

	# Prepare the response data
	frappe.local.response['data'] = {
		"msg": 0,
		"cuslist": [
			{
				"Cus_Id": customer.name,
				"Id": customer.name,
				"Location_lat": None,
				"Location_long": None,
				"CustomerName": customer.customer_name or "Unknown",
				"CustomerNameEng": None,
				"Address": None,
				"Password": None,  # Never return the password in the response
				"OneSignalUserID": OneSignalUserID,
				"Mob": user_doc.mobile_no,
				"FullName": user_doc.full_name,
				"BusinessName": None,
				"Business": None,
				"Email": user_doc.email,
				"PhoneNumber": user_doc.mobile_no,
				"StreetAddress": None,
				"City": None,
				"Country": None,
				"State": None,
				"Cusclass": customer.customer_group,
				"Active": True,
				"PolicyID": 2,
				"StoreCode": 10,
				"MinimumOrderValue": 1.000,
				"TotalSellPoint": 0.000,
				"TotalSellPointValue": 0.000,
				"MaxPoint": 0.000,
				"Deleted": False,
				"ChangeAddress": True,
				"DeliveryValue": 0.000,
				"Cus_class": customer.customer_group,
				"Token": token,
				"deviceKey": deviceKey,
				"imgserverpath": "http://92.205.178.113:8099/Content/img/"
			}
		]
	}

	# Clear unwanted keys from the response
	frappe.local.response.pop('message', None)
	frappe.local.response.pop('home_page', None)
	frappe.local.response.pop('full_name', None)

	# Commit the transaction (if necessary)
	frappe.db.commit()


@frappe.whitelist(allow_guest=True)
def register(**kwargs):
	selling_settings = frappe.get_single("Selling Settings")
	mobile_no = kwargs.get('mob')
	tel_no = kwargs.get('tel')
	store_name = kwargs.get('store_name')
	if frappe.db.exists("User", {"mobile_no": mobile_no}):
		frappe.local.response['http_status_code'] = 400
		frappe.local.response['message'] = _("Employee With Email And Phone Number Already Exist")
		return
	if selling_settings.customer_group and selling_settings.territory:
		try:
			customer = frappe.new_doc("Customer")
			customer.customer_name = kwargs.get('fname')
			customer.customer_group = kwargs.get('cusclass')
			customer.territory = selling_settings.territory
			customer.disabled = 1
			customer.customer_type = kwargs.get('customer_type') if  kwargs.get('customer_type') in ('Company','Individual') else "Individual"
			customer.insert(ignore_permissions=True)
			new_user = create_user_if_not_exists(customer.name, **kwargs)
			contact = frappe.new_doc('Contact')
			contact.first_name = customer.customer_name
			contact.append('phone_nos',{
				"phone": mobile_no,
				"is_primary_mobile_no": 1
			})
			contact.append('links',{
				"link_doctype":"Customer",
				"link_name":customer.name,
				"link_type":customer.customer_name,
			})
			contact.insert(ignore_permissions=True)
			if tel_no:
				contact = frappe.new_doc('Contact')
				contact.first_name = customer.customer_name
				contact.append('phone_nos', {
					"phone": tel_no,
					"is_primary_mobile_no": 0
				})
				contact.append('links', {
					"link_doctype": "Customer",
					"link_name": customer.name,
					"link_type": customer.customer_name,
				})
			address = frappe.new_doc('Address')
			address.address_title = customer.customer_name
			address.address_line1 = kwargs.get('address')
			address.city = kwargs.get('city')
			address.state = kwargs.get('gov')
			address.country = kwargs.get('country') or "Egypt"
			address.append('links',{
				"link_doctype":"Customer",
				"link_name":customer.name,
				"link_type":customer.customer_name,
			})
			address.insert(ignore_permissions=True)
			customer.customer_primary_contact = contact.name
			customer.customer_primary_address = address.name
			customer.mobile_no = contact.mobile_no
			customer.account_manager = new_user.name
			customer.save(ignore_permissions=True)
			frappe.db.commit()
		except Exception as er:
			frappe.local.response['http_status_code'] = 401
			frappe.local.response['message'] =str(er)
			frappe.local.response['data'] = {"errors" : "Not Completed Data"}
	else :
		frappe.local.response['http_status_code'] = 404
		frappe.local.response['message']  = "Please set customer group and territory"
		frappe.local.response['data'] = {"errors" : "Not Completed Data"}


@frappe.whitelist(allow_guest=True)
def create_user_if_not_exists(cst, **kwargs):
	"""
	this function will create user and set  role to e-commerce

	"""
	if frappe.db.exists("User", kwargs.get('tel')):
		return
	new_user = frappe.new_doc("User")
	new_user.update({
		"doctype": "User",
		"send_welcome_email": 0,
		"user_type": "System User",
		"first_name": kwargs.get('fname'),
		"email": kwargs.get('mob') + '@dynamic.com',
		"enabled": 1,
		"is_customer": 1,
		"customer": cst,
		"phone": kwargs.get('tel'),
		"mobile_no": kwargs.get('mob'),
		"new_password": kwargs.get('password'),
		"roles": [{"doctype": "Has Role", "role": "Customer"}],
		# "roles": [{"role": "Customer"}, {"role": "System Manager"}],
	})
	new_user.insert(ignore_permissions=True)
	new_user.save(ignore_permissions=True)
	role = frappe.get_doc("Role Profile", 'e-commerce')
	roles = [role.role for role in role.roles]
	new_user.add_roles(*roles)
	new_user.save()
	frappe.db.commit()
	return new_user
