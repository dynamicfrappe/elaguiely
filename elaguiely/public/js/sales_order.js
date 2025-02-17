frappe.ui.form.on('Sales Order Item' , {

    refressh:function(frm){

        window.onload = function() {
            if (localStorage.getItem("isReadOnly") === "true") {
              document.getElementById("price_list_rate").readOnly = true;
            }
        };
        
    },

})
