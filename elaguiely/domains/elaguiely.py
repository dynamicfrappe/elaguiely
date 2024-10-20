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
            "Customer":[
                {
                    "label" : "Cart ID",
                    "fieldname": "cart_id",
                    "fieldtype": "Link",
                    "insert_after": "warehouse",
                    "options": "Cart" ,
                    "read_only" : 1  ,
                },
                {
                    "label" : "Warehouse",
                    "fieldname": "warehouse",
                    "fieldtype": "Link",
                    "insert_after": "tax_category",
                    "options": "Warehouse" ,
                },
                {  
                    "label" : "Maximum Number of Orders:",
                    "fieldname": "maximum_orders",
                    "fieldtype": "Int",
                    "insert_after": "warehouse",
                }
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
               "fieldname" : "arabic_name",
               "fieldtype" : "Data",
               "insert_after" : "brand",
               "label" : _("Arabic Name"),
               "reqd" : 1 ,
            },
            {
                "fieldname" : "sub_catgories",
                "fieldtype" : "Table",
                "insert_after" : "description",
                "label" : _("Sub Categories"),
                "options": "Brand Categories",
                "reqd" : 0 ,
            }
        ] ,
        "Pricing Rule":[
            {
                "fieldname"    : "image",
                "fieldtype"    : "Attach Image",
                "insert_after" : "disable",
                "label"        : _("Image"),
                "reqd" : 0 ,

            }
        ],
        "Selling Settings":[
            {
                "fieldname"    : "minimum_amount",
                "fieldtype"    : "Float",
                "insert_after" : "customer_group",
                "label"        : _("Minimum Amount"),
                "default" : 0.0
            },
            {  
                "label" : "Maximum Number of Orders:",
                "fieldname": "maximum_orders",
                "fieldtype": "Int",
                "insert_after": "minimum_amount",
                "default" : 0
            }
        ],
        "Item Group" :[
            {
               "fieldname"    : "arabic_name",
               "fieldtype"    : "Data",
               "insert_after" : "item_group_name",
               "label"        : _("Arabic Name"),
               "reqd" : True
                 
            },
            {
               "fieldname"    : "customer_classes",
               "fieldtype"    : "Table",
               "insert_after" : "column_break_5",
               "label"        : _("Customer Classes"),
               "options": "Customer Classes",
                 
            },
        ] ,
        "Stock Settings" :[
             {
               "fieldname"    : "default_e_warehouse",
               "fieldtype"    : "Link",
               "insert_after" : "default_warehouse",
               "label"        : _("Default e-commerce Warehouse"),
              "options" : "Warehouse"
                 
            }
        ],
        "Sales Order" :[
            {
                "fieldname"    : "cart",
                "fieldtype"    : "Link",
                "insert_after" : "customer",
                "label"        : _("Cart"),
                "options" : "Cart"    
            },
            {
                "fieldname"    : "status_table",
                "fieldtype"    : "Table",
                "insert_after" : "more_info",
                "label"        : _("Status Table"),
                "options" : "Status Table"    
            },
            {
                "fieldname"    : "submit_datetime",
                "fieldtype"    : "Datetime",
                "insert_after" : "status_table",
                "label"        : _("submit_datetime"),
                # "hidden": 1,
            },

        ],
        "UOM Conversion Detail" : [
            {
                "fieldname"    : "maximum_qty",
                "fieldtype"    : "Int",
                "insert_after" : "conversion_factor",
                "label"        : _("Maximum Quantity"),
            }
        ]
    },

    "properties": [
        {
            "doctype":"Address",
            "doctype_or_field":"DocField",
            "fieldname":"city",
            "property":"options",
            "property_type":"Small Text",
            "value": "City",
        },
        {
            "doctype":"Address",
            "doctype_or_field":"DocField",
            "fieldname":"city",
            "property":"fieldtype",
            "property_type":"Select",
            "value": "Link",
        },
        {
            "doctype":"Address",
            "doctype_or_field":"DocField",
            "fieldname":"county",
            "property":"options",
            "property_type":"Small Text",
            "value": "Zone",
        },
        {
            "doctype":"Address",
            "doctype_or_field":"DocField",
            "fieldname": "county",
            "property":"fieldtype",
            "property_type":"Select",
            "value": "Link",
        },
        {
            "doctype":"Address",
            "doctype_or_field":"DocField",
            "fieldname":"state",
            "property":"options",
            "property_type":"Small Text",
            "value": "Governorate",
        },
        {
            "doctype":"Address",
            "doctype_or_field":"DocField",
            "fieldname":"state",
            "property":"fieldtype",
            "property_type":"Select",
            "value": "Link",
        },
        {
            "doctype": "User",
            "doctype_or_field": "DocField",
            "fieldname": "email",
            "property": "reqd",
            "property_type": "Check",
            "value": "0",
        },
        {
            "doctype": "User",
            "doctype_or_field": "DocField",
            "fieldname": "email",
            "property": "options",
            "property_type": "Small Text",
            "value": "",
        },
    ],
#  'on_setup': 'elaguiely.install.setup'
}