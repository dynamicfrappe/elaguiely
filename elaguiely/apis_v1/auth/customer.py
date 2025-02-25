import datetime
import frappe
from frappe import _

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
        frappe.local.response['message'] = _("خظأ فى تصنيف العميل: {0}").format(str(e))
        frappe.local.response['data'] = {"خظأ": str(e)}


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

      