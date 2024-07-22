# Copyright (c) 2023, elaguiely and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class Cart(Document):

	def caculate_items(self) :
		total = 0 
		for item in self.cart_item : 
			item.total = float(item.qty) * float(item.rate)
			total = total + item.total 
		self.total = total
		self.grand_total = total 
	def validate(self) :
		if self.cart_item and len( self.cart_item) > 0 : 
			self.caculate_items()

			