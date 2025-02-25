from .setting import *
import frappe
from frappe import _
from frappe.utils import today
import time 
from dynamic.controllers.sales_order import get_all_qty_reserved

domains = frappe.get_active_domains()

def get_item_prices(item_name, price_list_name=None):
	# Fetch all prices for the given item
	prices = frappe.db.get_list(
		'Item Price',
		fields=['uom', 'price_list_rate', 'price_list'],
		filters={'item_code': item_name, 'price_list': price_list_name},
		ignore_permissions=True
	)

	# Prepare a placeholder for up to 3 UOMs
	uom_prices = [{'name': None, 'price': None, 'factor': None, 'price_list': None, 'max_qty': None} for _ in range(3)]

	# Populate UOM data into respective slots (up to 3 UOMs)
	for idx, price in enumerate(prices[:3]):
		factor = frappe.get_value("UOM Conversion Detail", filters={'parent': item_name, 'uom': price['uom']}, fieldname='conversion_factor')
		max_qty = int(frappe.get_value("UOM Conversion Detail", filters={'parent': item_name, 'uom': price['uom']}, fieldname='maximum_qty') or 0)
		uom_prices[idx] = {
			'name': price['uom'],
			'price': price['price_list_rate'],
			'price_list': price['price_list'],
			'factor': factor, 
			'max_qty': max_qty
		}
	return uom_prices


def get_bulk_item_prices(item_names, price_list_name=None):
	# Fetch all prices for the given list of items in a single query
	prices = frappe.db.get_all(
		'Item Price',
		fields=['item_code', 'uom', 'price_list_rate', 'price_list'],
		filters={'item_code': ['in', item_names], 'price_list': price_list_name},
		ignore_permissions=True
	)

	# Prepare a dictionary to hold prices by item
	item_prices = {item: [{'name': None, 'price': None, 'factor': None, 'price_list': None, 'max_qty': None} for _ in range(3)] for item in item_names}
	# Populate the dictionary with UOM data for up to 3 UOMs per item
	item_uom_count = {item: 0 for item in item_names}  # Track UOM count for each item
	for price in prices:
		item_code = price['item_code']
		idx = item_uom_count[item_code]

		if idx < 3:  # We only store up to 3 UOMs
			factor = frappe.get_value("UOM Conversion Detail", filters={'parent': item_code, 'uom': price['uom']}, fieldname='conversion_factor')
			max_qty = frappe.get_value("UOM Conversion Detail", filters={'parent': item_code, 'uom': price['uom']}, fieldname='maximum_qty')
			item_prices[item_code][idx] = {
				'name': price['uom'],
				'price': price['price_list_rate'],
				'factor': factor,
				'max_qty': max_qty,
				'price_list': price['price_list']
			}
			item_uom_count[item_code] += 1

	return item_prices


def stock_qty (customer, item_code) :
	# Validate firstly on warehouse set in customer or get default warehouse from stock settings
	default_warehouse = frappe.db.get_single_value('Stock Settings', 'default_warehouse')
	warehouse = frappe.get_value('Customer', customer, 'warehouse')
	
	# Actual qty in BIN
	if "Stock Reservation" not in domains:
		available_qty = frappe.get_value("Bin" , {"item_code":item_code , "warehouse": (warehouse or default_warehouse) } , 'actual_qty')
	else:
		# Available qty (actual_qty in bin - reserved qty)
		available_qty = get_all_qty_reserved(item_code, warehouse or default_warehouse)

	return available_qty




