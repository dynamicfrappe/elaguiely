import frappe 



def create_role_profile(*args , **kwargs) :
   """
   Create Role for e-commerce user
   new Role Name e-commerce
   """
   # check if rile exit 
   role = frappe.db.exists("Role Profile" , 'e-commerce') 
   if not role :
      # create role if not role 
      role = frappe.new_doc("Role Profile")
      role.role_profile = 'e-commerce' 
      role.save()
      frappe.db.commit()

      #setup permissions 
      user_role = frappe.get_value("Role" , "Sales User" , "name")
      role.append("roles" , {
         "role":"Sales User"
      })

      role.save()
      frappe.db.commit()
   # frappe.get_doc("Role Profile" , 'e-commerce')



def setup(*args ,**kwargs) :
   """  
   domain   Elaguiely
   Role Profile e-commerce
   Role Sales User 
   """
   # check if domain exit to pass 
   dom = frappe.db.exists("Domain" , "Elaguiely")
   if dom :
      return True
      #create domain 
   dom = frappe.new_doc("Domain")
   dom.domain = "Elaguiely"
   dom.save()
   frappe.db.commit()
   create_role_profile()   
   return True 
