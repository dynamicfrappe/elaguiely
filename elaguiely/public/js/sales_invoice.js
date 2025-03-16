frappe.ui.form.on('Sales Invoice', {
    customer:function(frm){
        if(frm.doc.customer){
            frappe.call({
                method: "dynamic.api.get_active_domains",
                callback: function (r) {
                    if (r.message && r.message.length) {
                        if (r.message.includes("Elaguiely")) {
                            frappe.call({
                                method: 'elaguiely.apis.utils.get_closing_balance_for_customer',
                                args: {
                                    customer: frm.doc.customer
                                },
                                callback: function(r){
                                    if(r.message){
                                        console.log(r.message);
                                        frm.set_value('closing_balance', parseFloat(r.message));
                                        frm.refresh_field('closing_balance');
                                    }
                                }
                            })
                        }
                    }
                }
            })
                
        }
    },

    onload: function(frm) {
       
		
		frm.set_query('uom', 'items', function(doc, cdt, cdn) {
			let row  = locals[cdt][cdn];
			let query = {
				filters: [
				]
			};
			if (row.item_code) {
				query.query = "elaguiely.controllers.queries.uom_query";
				query.filters.push(["parent", "=", row.item_code]);
                
			}
			return query;
		});

        
	},
})
frappe.ui.form.on('Sales Invoice Item' , {

    refressh:function(frm){

        window.onload = function() {
            if (localStorage.getItem("isReadOnly") === "true") {
              document.getElementById("price_list_rate").readOnly = true;
            }
        };
        
    },

})
