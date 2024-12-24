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
    }
})
