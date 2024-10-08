import frappe

from elaguiely.apis_v1.jwt_decorator import jwt_required


@frappe.whitelist(allow_guest=True)
@jwt_required
def get_categories(ParentId=None, classcode=None, **kwargs):
    try:
        response = []
        if classcode:
            class_codes = frappe.get_list("Customer Classes", filters={'customer_class': classcode}, fields=['parent'])
            class_code_names = [code['parent'] for code in class_codes]

            main_groups = frappe.db.get_all("Item Group", filters={'name': ['in', class_code_names]},
                                            fields=["name", 'arabic_name', 'item_group_name', 'image'])
            if not main_groups:
                frappe.local.response['data'] = response

            for main_group in main_groups:
                response.append({
                    "Id": main_group.get("name"),
                    "Name": main_group.get("arabic_name"),
                    "NameEng": main_group.get("name"),
                    "Icon": main_group.get("image"),
                    "MG_code": main_group.get("name"),
                    "SG_Code": None,
                    "SG2_Code": None,
                    "DisplayOrder": None
                })
        else:
            subcategories = frappe.db.get_list("Brand Categories", fields=['parent'], filters=[{'category': ParentId}])
            for subcategory in subcategories:
                suppliers = frappe.db.get_list("Brand", filters={'name': subcategory.get("parent")},
                                               fields={'name', 'arabic_name', 'image'})
                for supplier in suppliers:
                    image = frappe.db.get_value('Brand', supplier.get('name'), "image")
                    response.append({
                        "Id": supplier.get('name'),
                        "Name": supplier.get('arabic_name'),
                        "NameEng": supplier.get('name'),
                        "Icon": image,
                        "MG_code": ParentId,
                        "SG_Code": supplier.get('name'),
                        "SG2_Code": None,
                        "DisplayOrder": None
                    })
                    
        frappe.local.response['data'] = response

    except Exception as e:
        pass

