frappe.ui.form.on("Sales Order", {
	

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
});

// frappe.ui.form.on("Sales Order Item", {
   
//     item_code: function (frm, cdt, cdn) {
         
//         let row = locals[cdt][cdn];
//         console.log(row);
//         frappe.db.get_list('UOM Conversion Detail', {
//             fields: ['uom', 'conversion_factor'],
//             filters: {
//                 parent: row.item_code
//             }
//         }).then(records => {

//             let uoms = records.map(item => item.uom);
//             console.log(uoms);
//             frm.fields_dict.items.grid.get_field('uom').get_query =function(){
//                 return {
//                                 filters: {
//                                     name: ["in", uoms]
//                                 }
//                             }
//             }
//            

//             //frm.refresh_fields('items');
//             // if (row.item_code) {
//             //     frm.set_query('uom', 'items', () => {
//             //         return {
//             //             filters: {
//             //                 name: ["in", uoms]
//             //             }
//             //         }
//             //     })
                
//             // }
//         })
        
      
//     }
// });