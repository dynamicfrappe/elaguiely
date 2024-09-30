frappe.ui.form.on('Customer', {
	refresh(frm){

    },
     after_save(frm) {
        frappe.call({
            method: "elaguiely.elaguiely.functions.get_active_domains",
            callback: function (r) {
              if (r.message && r.message.length) {
                if (r.message.includes("Elaguiely")) {
                    if (frm.doc.disabled === 0){

                        frappe.call({
                            method: "elaguiely.elaguiely.functions.create_cart_after_enable_customer",
                            args: {
                                customer: frm.docname
                            },
                            callback: function (r) {
                              
                            } 
                        });
                    }
                }  
              } 
            }  
        });
    },
})