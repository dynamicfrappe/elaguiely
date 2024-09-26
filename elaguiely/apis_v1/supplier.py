import frappe

from elaguiely.apis_v1.jwt_decorator import jwt_required


@frappe.whitelist(allow_guest=True)
@jwt_required
def get_all_suppliers(**kwargs):
    try:
        suppliers = frappe.db.get_list("Brand", fields=["name", "arabic_name", "image"])
        if not suppliers:
            return {"status": "success", "data": []}
        response = []
        for supplier in suppliers:
            subcategories = frappe.get_list("Brand Categories", fields=['category'],
                                            filters=[{'parent': supplier.name}])
            response.append({
                "icon": supplier.get("image"),
                "name": supplier.get("arabic_name"),
                "nameeng": supplier.get("name"),
                "sup_id": supplier.get("name"),
                "imageName": supplier.get("image"),
                "advertisingId": None,
                "subcategories": subcategories
            })
        frappe.local.response['data'] = response

    except Exception as e:
        return {'status_code': 404, 'message': str(e)}


@frappe.whitelist(allow_guest=True)
@jwt_required
def get_category_by_supplier(supplierid, **kwargs):
    supplier = frappe.get_doc("Brand", supplierid)
    if not supplier:
        return {"message": "Invalid", "data": []}
    categories = frappe.get_list(
        "Brand Categories", fields=['name'], filters=[{'parent': supplier.name}]
    )
    print('categories ==> ', categories)
    responses = []
    for category in categories:
        category["id"] = category.get("name")
        category["name"] = category.get("name")
        category["nameEng"] = category.get("name_eng")
        category["icon"] = category.get("image")
        category["mgCode"] = category.get("name")
        category["sgCode"] = supplierid
        category["sg2Code"] = None
        responses.append(category)
    frappe.local.response.data = responses
