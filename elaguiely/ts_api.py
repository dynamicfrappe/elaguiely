import frappe
from frappe import _
import requests

# done
@frappe.whitelist(allow_guest = True)
def get_all_zones():
    try:
        response = []
        governs = frappe.db.get_list("Zone", fields= ['zone_code', 'zone_name', 'city_code', 'gov_code'])
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

# done
@frappe.whitelist(allow_guest = True)
def get_all_cities():
    try:
        response = []
        governs = frappe.db.get_list("City", fields= ['city_code', 'city_name', 'gov_code'])
        for gov in governs:
            response.append({
                "City_code": gov.get('city_code'), 
                "City_name": gov.get('city_name'),
                "Gov_code": gov.get('gov_code'),
            })
        frappe.local.response.data = response 

    except Exception as e:
        frappe.local.response['message'] = str(e)

# done
@frappe.whitelist(allow_guest = True)
def get_all_governs():
    print('get_all_governs')
    try:
        response = []
        governs = frappe.db.get_list("Governorate", fields= ['gov_code', 'gov_name'])
        for gov in governs:
            response.append({
                "Gov_code": gov.get('gov_code'), 
                "Gov_name": gov.get('gov_name'),
            })
        frappe.local.response.data = response 
            
    except Exception as e:
        frappe.local.response['message'] = str(e)

# done
@frappe.whitelist(allow_guest = True)
def get_customer_class():
    try:
        
        response = []
        customer_groups = frappe.db.get_list("Customer Group", fields = ['name'])
        for group in customer_groups:
            response.append({
                "Class_code": group.get('name'), 
                "Class_name": group.get('name'),
            })

        frappe.local.response['data'] = response 
            
    except Exception as e:
        return { 'status_code': 404, 'message': str(e) }

# done
@frappe.whitelist(allow_guest = True)
def get_customer_profile(id):
    try:
        
        response = []
        c = frappe.get_doc("Customer", id)
        response.append({
            "FullName": c.customer_name,
            "BusinessName": None,
            "Business": None,
            "Email": c.email_id,
            "PhoneNumber": c.mobile_no,
            "StreetAddress": None,
            "Latitude": None,
            "Longitude": None,
            "Cusclass": c.customer_group,
            "City": None,
            "State": None,
            "Country": None,
            "ID": c.name,
            "CustomerPassword": None,
            "ConfirmPassword": None,
            "Cus_ID": None,
            "CusclassName": None,
            "CityName": None,
            "StateName": None,
            "CountryName": None,
            "sellerphone": None,
            "sellerphone2": None,
            "sellername": None,
            "ShopImg": None,
            "notificationNo": None,
            "UsernameEng": None
        })

        frappe.local.response['data'] = response 
            
    except Exception as e:
        return { 'status_code': 404, 'message': str(e) }

# done
@frappe.whitelist(allow_guest = True)
def get_all_suppliers():
    try:
        suppliers = frappe.db.get_list("Brand", fields=["name", "arabic_name", "image"])
        if not suppliers:
            return {"status": "success", "data": []}
        response = []
        for supplier in suppliers:
            subcategories = frappe.get_list("Brand Categories", fields=['category'], filters=[ {'parent': supplier.name}])
            response.append({
                "icon": None, 
                "name": supplier.get("arabic_name"),
                "nameeng": supplier.get("name"),  
                "sup_id": supplier.get("name"),  
                "imageName": None,  
                "advertisingId": None,
                "subcategories": subcategories
            })
        frappe.local.response['data'] = response
            
    except Exception as e:
        return { 'status_code': 404, 'message': str(e) }

# done
@frappe.whitelist(allow_guest = True)
def get_category_by_supplier(supplierid):
    response = []
    supplier = frappe.get_doc("Brand", supplierid)
    if not supplier:
        return { "message": "Invalid" , "data": []}

    response = frappe.get_list("Brand Categories", fields=['category'], filters=[ {'parent': supplier.name} ])
         
    frappe.local.response.data = response 

# Working...
@frappe.whitelist(allow_guest = True)
def get_items_prices(main_group_id = None, sub_group1_id = None, sub_group2_id = None, supplier_id = None, customer_id = None, bouns_id = None, fav = False ):
    try:
        
        response = []
        
        items= []
        if customer_id and fav:
            customer = frappe.get_doc("Customer", customer_id)
            if not customer:
                 return { "message": "Invalid Customer" , "data": []}

            favourite = frappe.get_doc("favourite", filters = [{'customer_id': customer_id}])

            filters = {}
            filters["parent"] = favourite
            if main_group_id:
                filters["item_group"] = main_group_id
            if supplier_id:
                filters["brand"] = supplier_id
            
            
            items = frappe.db.get_list("favorite Item", fields = ['item'], filters = filters)

        if not fav:
            
            for item in items:
                i = frappe.get_doc("Item", item)
                uoms = frappe.get_all("UOM", i.uoms)
                
                response.append({
                    "Id": i.item_code,
                    "PreviewImage": None,
                    "NameEng": i.item_name,
                    "Name": i.arabic_name,
                    "Unit1Name": i.stock_uom,
                    "Unit1NameEng": i.stock_uom,
                    "U_Code1": i.stock_uom,
                    "Unit1OrignalPrice": None,
                    "Unit1Price": None,
                    "Unit1Point": None,
                    "Unit1Factor": None,
                    "Unit2Name": None,
                    "Unit2NameEng": None,
                    "U_Code2": None,
                    "Unit2OrignalPrice": None,
                    "Unit2Price": None,
                    "Unit2Point": None,
                    "Unit2Factor": None,
                    "Unit3Name": None,
                    "Unit3NameEng": None,
                    "U_Code3": None,
                    "Unit3OrignalPrice": None,
                    "Unit3Price": None,
                    "Unit3Point": None,
                    "Unit3Factor": None,
                    "SummaryEng": None,
                    "DescriptionEng": None,
                    "Summary": None,
                    "Description": None,
                    "price": None,
                    "FromItemCard": None,
                    "SellUnitFactor": None,
                    "OrignalPrice": None,
                    "SellUnitOrignalPrice": None,
                    "SellUnitPoint": None,
                    "ActualPrice": None,
                    "ItemTotalprice": None,
                    "SellUnit": None,
                    "SellUnitName": None,
                    "SellUnitNameEng": None,
                    "DiscountPrice": None,
                    "DiscountPercent": None,
                    "TotalQuantity": None,
                    "MG_code": None,
                    "SG_Code": None,
                    "IsFavourite": None,
                    "SellPoint": None,
                    "OrignalSellPoint": None,
                    "MinSalesOrder": None,
                    "Isbundle": None,
                    "NotChangeUnit": None
                })

            frappe.local.response['data'] = response

        
            
    except Exception as e:
        return { 'status_code': 404, 'message': str(e) }

# Working...
@frappe.whitelist(allow_guest = True)
def get_best_seller_items():
    try:
        response = []


        frappe.local.response['data'] = response      

    except Exception as e:
        return { 'status_code': 404, 'message': str(e) }

# Working...
@frappe.whitelist(allow_guest = True)
def get_categories():
    try:
        response = []


        frappe.local.response['data'] = response 
            
    except Exception as e:
        frappe.local.response['message'] = str(e)

# done
@frappe.whitelist(allow_guest = True)
def get_items_serach_list():
    try:  
        response = []
        items = frappe.db.get_all("Item", fields = ['name'])
        for item in items:
            response.append(item.get("name"))

        frappe.local.response['data'] = response 
         
    except Exception as e:
        frappe.local.response['message'] = str(e)


@frappe.whitelist(allow_guest = True)
def get_invoice():
    try:
        
        response = []


        frappe.local.response['data'] = response 
         
    except Exception as e:
        frappe.local.response['message'] = str(e)


@frappe.whitelist(allow_guest = True)
def evaluate_order():
    try:
        pass    

    except Exception as e:
        pass


@frappe.whitelist(allow_guest = True)
def cancel_order():
    try:
        pass
            
    except Exception as e:
        pass

