import frappe
from frappe import _
from elaguiely.apis_v1.utils import get_bulk_item_prices , stock_qty
from elaguiely.apis_v1.jwt_decorator import jwt_required


@frappe.whitelist(allow_guest=True)
@jwt_required
def get_all_suppliers(**kwargs):
	try:
		suppliers = frappe.db.get_list(
			"Brand",
			fields=["name", "arabic_name", "image"],
			ignore_permissions=True
		)
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
	try:
		supplier = frappe.get_doc("Brand", supplierid)
		if not supplier:
			return {"message": "Invalid", "data": []}
		categories = frappe.get_list(
			"Brand Categories",
			fields=['category'],
			filters=[{'parent': supplier.name}],
			ignore_permissions=True
		)
		responses = []
		for category in categories:
			image = frappe.db.get_value("Item Group", category.get('category'), 'image')
			category["id"] = category.get("category")
			category["name"] = category.get("category")
			category["nameEng"] = category.get("category")
			category["icon"] = image 
			category["mgCode"] = category.get("category")
			category["sgCode"] = supplierid
			category["sg2Code"] = None
			responses.append(category)
			print(category["icon"])

		frappe.local.response.data = responses
	except Exception as e:
		frappe.local.response['http_status_code'] = 404
		frappe.local.response['message'] = _("failed to get supplier {0}: {1}").format(supplierid, str(e))
		frappe.local.response['data'] = {"errors": str(e)}


