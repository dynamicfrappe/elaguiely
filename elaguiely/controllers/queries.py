import frappe
from frappe.model.document import Document
from collections import defaultdict
from frappe.desk.reportview import get_filters_cond, get_match_cond

@frappe.whitelist()
def uom_query(doctype, txt, searchfield, start, page_len, filters):
	# Should be used when item code is passed in filters.
	doctype = "UOM Conversion Detail"
	conditions, bin_conditions = [], []
	filter_dict = get_doctype_wise_filters(filters)
	
	query = """select uom
		from `tabUOM Conversion Detail`
		where 1=1 {fcond} order by name
		limit
			{start}, {page_len}
		""".format(		
		fcond=get_filters_cond(doctype, filter_dict.get("parent"), conditions),		
		start=start,
		page_len=page_len,
		txt=frappe.db.escape("%{0}%".format(txt)),
	) 
	
	return frappe.db.sql(query)


def get_doctype_wise_filters(filters):
	# Helper function to seperate filters doctype_wise
	filter_dict = defaultdict(list)
	for row in filters:
		filter_dict[row[0]].append(row)
	return filter_dict


