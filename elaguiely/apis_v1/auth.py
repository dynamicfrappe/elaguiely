import datetime
import frappe
from frappe import _
import jwt
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
		# Perform the actual login action
		frappe.local.login_manager.authenticate(user.name, Password)
		frappe.local.login_manager.post_login()
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
				"customer_enabled": not customer.disabled,
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
	# Fetch selling settings
	selling_settings = frappe.get_single("Selling Settings")

	# Validate required fields (phone and email)
	name = kwargs.get("name")
	phone = kwargs.get("mob")
	email = kwargs.get("email")
	customer_id = kwargs.get("id")
	if not phone and not email:
		if id:
			# User / customer data
			customer_details = frappe.db.get_all("Customer", filters={'name': customer_id}, fields=['customer_name', 'image', 'customer_group', 'customer_primary_address'])
			customer_name = customer_details[0].get('customer_name')
			customer_image = customer_details[0].get('image')
			customer_group = customer_details[0].get('customer_group')
			customer_address = customer_details[0].get('customer_primary_address')
			address = frappe.db.get_list("Address", filters={'name': customer_address}, fields= ['city', 'county', 'state', 'country', 'latitude', 'longitude', 'address_line1'])
			print(address)
			user = frappe.db.get_all('User', filters={'customer': customer_name}, fields=['email','mobile_no', 'name'])
			if user:
				email = user[0].get("email")
				phone_number = user[0].get("mobile_no")
				engname = user[0].get("name")
				
				# Append response
				response = {
					"FullName": customer_name,
					"BusinessName": customer_name,
					"Business": customer_group,
					"Email": email or "",
					"PhoneNumber": phone_number,
					"StreetAddress": address[0].get("address_line1") if address else "",
					"Latitude": address[0].get("latitude") if address else "",
					"Longitude": address[0].get("longitude") if address else "",
					"Cusclass": customer_group,
					"City": address[0].get("city")  if address else "",
					"State": address[0].get("state")  if address else "",
					"Country": address[0].get("country")  if address else "",
					"ID": customer_name,
					"CustomerPassword": None,
					"ConfirmPassword": None,
					"Cus_ID": None,
					"CusclassName": customer_group,
					"CityName": address[0].get("city") if address else "",
					"StateName": address[0].get("state") if address else "",
					"CountryName": address[0].get("country") if address else "",
					"sellerphone": None,
					"sellerphone2": None,
					"sellername": None,
					"ShopImg": customer_image or "",
					"notificationNo": None,
					"UsernameEng": engname
				}

			frappe.local.response['data'] = response 
			return
		else:
			frappe.local.response['http_status_code'] = 400
			frappe.local.response['message'] = _("Phone number or email are required")
		return

	# Check if a user with the provided phone and email already exists
	if frappe.db.exists("User", {"username": name}):
		frappe.local.response['http_status_code'] = 400
		frappe.local.response['message'] = _("User with the provided store name already exists")
		return
	elif frappe.db.exists("User", {"email": email}):
		frappe.local.response['http_status_code'] = 400
		frappe.local.response['message'] = _("User with the provided email already exists")
		return
	elif frappe.db.exists("User", {"phone": phone}):
		frappe.local.response['http_status_code'] = 400
		frappe.local.response['message'] = _("User with the provided phone already exists")
		return

	# Ensure that customer group and territory are set in Selling Settings
	if not (selling_settings.customer_group and selling_settings.territory):
		frappe.local.response['http_status_code'] = 404
		frappe.local.response['message'] = _("Please set customer group and territory in Selling Settings")
		frappe.local.response['data'] = {"errors": "Missing Selling Settings"}
		return

	try:
		# Create a new customer document
		customer = frappe.new_doc("Customer")
		customer.customer_name = kwargs.get('name')
		customer.customer_group = selling_settings.customer_group
		customer.territory = selling_settings.territory
		customer.disabled = 1
		customer.customer_type = kwargs.get('customer_type') if kwargs.get('customer_type') in (
		'Company', 'Individual') else "Individual"
		customer.insert(ignore_permissions=True)

		# Create contact document
		contact = create_contact(kwargs, customer)

		# Create address document
		address = create_address(kwargs, customer)

		# Create the user (or retrieve if it already exists)
		new_user = create_user_if_not_exists(customer.name, **kwargs)

		# Update the customer document with contact, address, and user details
		customer.customer_primary_contact = contact.name
		customer.customer_primary_address = address.name
		customer.mobile_no = contact.mobile_no
		customer.account_manager = new_user.name
		customer.save(ignore_permissions=True)

		frappe.db.commit()

		# Success response
		frappe.local.response['http_status_code'] = 200
		frappe.local.response['message'] = _("Customer registration successful")
		frappe.local.response['data'] = {
			"customer_name": customer.customer_name,
			"contact_name": contact.name,
			"address": address.name
		}
	except Exception as e:
		frappe.local.response['http_status_code'] = 500
		frappe.local.response['message'] = _("Registration failed: {0}").format(str(e))
		frappe.local.response['data'] = {"errors": str(e)}


def create_contact(kwargs, customer):
	contact = frappe.new_doc('Contact')
	contact.first_name = customer.customer_name
	contact.append('phone_nos', {
		"phone": kwargs.get('mob'),
		"is_primary_mobile_no": 1
	})
	contact.append('links', {
		"link_doctype": "Customer",
		"link_name": customer.name,
		"link_type": customer.customer_name,
	})
	contact.insert(ignore_permissions=True)
	return contact


def create_address(kwargs, customer):
	address = frappe.new_doc('Address')
	address.address_title = customer.customer_name
	address.address_line1 = kwargs.get('address')
	address.city = kwargs.get('city')
	address.state = kwargs.get('gov')
	address.country = kwargs.get('country') or "Egypt"
	address.append('links', {
		"link_doctype": "Customer",
		"link_name": customer.name,
		"link_type": customer.customer_name,
	})
	address.insert(ignore_permissions=True)
	return address

# Why it's whitelisted?
@frappe.whitelist(allow_guest=True)
def create_user_if_not_exists(customer_name, **kwargs):
    """
    Create a user if it does not exist, and assign appropriate roles.
    """
    phone = kwargs.get('mob')

    # Check if a user with the given phone already exists
    if frappe.db.exists("User", {"mobile_no": phone}):
        return frappe.get_doc("User", {"mobile_no": phone})

    # Validate required fields for user creation
    if not kwargs.get('pass'):
        frappe.throw(_("Password is required for new user registration"))

    # Create a new user
    new_user = frappe.new_doc("User")
    new_user.update({
        "doctype": "User",
        "send_welcome_email": 0,
        "user_type": "System User",
        "first_name": kwargs.get('name'),
        "email": kwargs.get('email'),  # Use a more dynamic email generator if needed
        "enabled": 1,
        "is_customer": 1,
        "customer": customer_name,
        "phone": phone,
        "mobile_no": phone,
        "new_password": kwargs.get('pass'),
        "roles": [{"doctype": "Has Role", "role": "Customer"}]
    })
    new_user.insert(ignore_permissions=True)

    # Add additional roles from the role profile
    assign_roles(new_user, 'e-commerce')

    return new_user


def assign_roles(user, role_profile_name):
    """
    Assign roles to the user from a given role profile.
    """
    role_profile = frappe.get_doc("Role Profile", role_profile_name)
    roles = [role.role for role in role_profile.roles]
    user.add_roles(*roles)


@frappe.whitelist(allow_guest = True)
def get_customer_class():
    try:
        response = []
        customer_groups = frappe.db.get_list("Customer Group", fields = ['name'], ignore_permissions=True)
        for group in customer_groups:
            response.append({
                "Class_code": group.get('name'), 
                "Class_name": group.get('name'),
            })

        frappe.local.response['data'] = response 
            
    except Exception as e:
        frappe.local.response['http_status_code'] = 500
        frappe.local.response['message'] = _("failed to get customer classes: {0}").format(str(e))
        frappe.local.response['data'] = {"errors": str(e)}


@frappe.whitelist(allow_guest = True)
def get_all_zones():
    try:
        response = []
        governs = frappe.db.get_list("Zone", fields= ['zone_code', 'zone_name', 'city_code', 'gov_code'], ignore_permissions=True)
        for gov in governs:
            response.append({
                "Z_code": gov.get('zone_code'), 
                "Z_name": gov.get('zone_name'),
                "Gov_code": gov.get('gov_code'),
                "City_code": gov.get('city_code'),
                "DeliveryPeriod": None
            })

        frappe.local.response.data = response


    except Exception as e:
        frappe.local.response['message'] = str(e)


@frappe.whitelist(allow_guest = True)
def get_all_cities():
    try:
        response = []
        governs = frappe.db.get_list("City", fields= ['city_code', 'city_name', 'gov_code'], ignore_permissions=True)
        for gov in governs:
            response.append({
                "City_code": gov.get('city_code'), 
                "City_name": gov.get('city_name'),
                "Gov_code": gov.get('gov_code'),
            })
        frappe.local.response.data = response 

    except Exception as e:
        frappe.local.response['message'] = str(e)


@frappe.whitelist(allow_guest = True)
def get_all_governs():
    print('get_all_governs')
    try:
        response = []
        governs = frappe.db.get_list("Governorate", fields= ['gov_code', 'gov_name'], ignore_permissions=True)
        for gov in governs:
            response.append({
                "Gov_code": gov.get('gov_code'), 
                "Gov_name": gov.get('gov_name'),
            })
        frappe.local.response.data = response 
            
    except Exception as e:
        frappe.local.response['message'] = str(e)

      