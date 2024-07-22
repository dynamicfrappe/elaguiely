from __future__ import unicode_literals
from ntpath import join
from frappe import _


"""
doctype to add fields add image if no image & arabic name 
1- Item 
2 - Brand 
3 - Item Group 


"""
data = {
    'custom_fields': {
           'User': [
            {
                "label": "Is Customer",
                "fieldname": "is_customer",
                "fieldtype": "Check",
                "insert_after": "enabled",
            },
            {
                "label": "Customer",
                "fieldname": "customer",
                "fieldtype": "Link",
                "insert_after": "is_customer",
                "options":"Customer" ,
                "read_only" : 1  ,
            
            },
          
            
            ],
            "Address":
            [
                {
                "fieldname"    : "building_no",
                "fieldtype"    : "Data",
                "insert_after" : "country",
                "label"        : _("Building NO"),
                },
                {
                "fieldname"    : "floor_no",
                "fieldtype"    : "Data",
                "insert_after" : "building_no",
                "label"        : _("Floor NO"),
                },
                {
                "fieldname"    : "apartment_no",
                "fieldtype"    : "Data",
                "insert_after" : "floor_no",
                "label"        : _("Apartment NO"),
                },
                 {
                "fieldname"    : "latitude",
                "fieldtype"    : "Float",
                "insert_after" : "apartment_no",
                "label"        : _("Latitude"),
                },
                 {
                "fieldname"    : "longitude",
                "fieldtype"    : "Float",
                "insert_after" : "latitude",
                "label"        : _("Longitude"),
                },


            ],
        "Item" :[
            {
               "fieldname"    : "arabic_name",
               "fieldtype"    : "Data",
               "insert_after" : "item_name",
               "label"        : _("Arabic Name"),
               "reqd" : True
            },
              {
               "fieldname"    : "category",
               "fieldtype"    : "Link",
               "insert_after" : "item_group",
               "options"      :"Category" ,
               "label"        : _("Category"),
               "reqd" : False ,
               
            },
              {
                "label": "Best Sell",
                "fieldname": "best_sell",
                "fieldtype": "Check",
                "insert_after": "stock_uom",
                "read_only" : 0  ,
            
            },
             {
                "label": "New Arrive",
                "fieldname": "new_arrive",
                "fieldtype": "Check",
                "insert_after": "best_sell",
                "read_only" : 0  ,
            
            },
           
             {
                "label": "Max Order QTY",
                "fieldname": "max_order",
                "fieldtype": "Data",
                "insert_after": "over_billing_allowance",
                "read_only" : 0  ,
            
            },
        ] ,
        "Brand" :[
            {
               "fieldname"    : "arabic_name",
               "fieldtype"    : "Data",
               "insert_after" : "brand",
               "label"        : _("Arabic Name"),
               "reqd" : True
                
            }
        ] ,
        "Pricing Rule":[
            {
                "fieldname"    : "image",
               "fieldtype"    : "Attach Image",
               "insert_after" : "disable",
               "label"        : _("Image"),
               "reqd" : 0

            }
        ],
        "Item Group" :[
            {
               "fieldname"    : "arabic_name",
               "fieldtype"    : "Data",
               "insert_after" : "item_group_name",
               "label"        : _("Arabic Name"),
               "reqd" : True
                 
            }
        ] ,
        "Stock Settings" :[
             {
               "fieldname"    : "default_e_warehouse",
               "fieldtype"    : "Link",
               "insert_after" : "default_warehouse",
               "label"        : _("Default e-commerce Warehouse"),
              "options" : "Warehouse"
                 
            }
        ]


    },
#  'on_setup': 'elaguiely.install.setup'
}