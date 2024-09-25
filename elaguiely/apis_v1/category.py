import frappe

from elaguiely.apis_v1.jwt_decorator import jwt_required


@frappe.whitelist(allow_guest=True)
@jwt_required
def get_all_categories(**kwargs):
    try:
        categories = frappe.db.get_list("Item Group", fields=["name", "arabic_name", "image"])
        if not categories:
            return {"status": "success", "data": []}
        response = []
        for category in categories:
            subcategories = frappe.get_list("Brand Categories", fields=['category'],
                                            filters=[{'parent': category.name}])
            response.append({
                "icon": category.get("image"),
                "name": category.get("arabic_name"),
                "nameeng": category.get("name"),
                "sup_id": category.get("name"),
                "imageName": category.get("image"),
                "advertisingId": None,
                "subcategories": subcategories
            })
        frappe.local.response['data'] = response

    except Exception as e:
        return {'status_code': 404, 'message': str(e)}


@frappe.whitelist(allow_guest=True)
@jwt_required
def get_supplier_by_category(supplierid, **kwargs):
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
        category["mgCode"] = None
        category["sgCode"] = None
        category["sg2Code"] = None
        responses.append(category)
    frappe.local.response.data = responses
