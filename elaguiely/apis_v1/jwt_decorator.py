from functools import wraps

import frappe
import jwt
from frappe import _

# Secret key for encoding and decoding JWT tokens
SECRET_KEY = '12b6c68d653941aeaf9048f142f1c79c'


def jwt_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		token = frappe.request.headers.get('Authorization')
		if not token:
			frappe.local.response["http_status_code"] = 401
			frappe.local.response['message'] = _('Token is missing')
			return
		try:
			token = token.split(' ')[-1]
			payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
			frappe.local.user = frappe.get_doc("User", payload['user'])
		except jwt.ExpiredSignatureError:
			frappe.local.response["http_status_code"] = 401
			frappe.local.response['message'] = _('Token is missing')
			return
		except jwt.InvalidTokenError:
			frappe.local.response["http_status_code"] = 401
			frappe.local.response['message'] = _('Invalid Token')
			return
		return f(*args, **kwargs)
	return decorated_function
