flectra.define('sale_product_matrix.sale_matrix_tour',function(require){
"usestrict";

vartour=require('web_tour.tour');

tour.register('sale_matrix_tour',{
    url:"/web",
    test:true,
},[tour.stepUtils.showAppsMenuItem(),{
    trigger:'.o_app[data-menu-xmlid="sale.sale_menu_root"]',
},{
    trigger:".o_list_button_add",
    extra_trigger:".o_sale_order"
},{
    trigger:'.o_required_modifier[name=partner_id]input',
    run:'textAgrolait',
},{
    trigger:'.ui-menu-item>a:contains("Agrolait")',
    auto:true,
},{
    trigger:'a:contains("Addaproduct")',
},{
    trigger:'.o_data_cell',
},{
    trigger:'div[name="product_template_id"]input',
    run:'textMatrix',
},{
    trigger:'ul.ui-autocompletea:contains("Matrix")',
},{
    trigger:'.o_product_variant_matrix',
    run:function(){
        //fillthewholematrixwith1's
        $('.o_matrix_input').val(1);
    }
},{
    trigger:'span:contains("Confirm")',
},{
    trigger:'.o_sale_order',
    //waitforqtytobe1=>checkthetotaltobesureallqtiesaresetto1
    extra_trigger:'.oe_subtotal_footer_separator:contains("18.40")',
},{
    trigger:'span:contains("Matrix(PAV11,PAV22,PAV31)\n\nPA4:PAV41")',
    extra_trigger:'.o_form_editable',
},{
    trigger:'.o_edit_product_configuration', //editthematrix
},{
    trigger:'.o_product_variant_matrix',
    run:function(){
        //setallqtiesto3
        $('.o_matrix_input').val(3);
    }
},{
    trigger:'span:contains("Confirm")', //applythematrix
},{
    trigger:'.o_sale_order',
    //waitforqtytobechanged=>checkthetotaltobesureallqtiesaresetto3
    extra_trigger:'.oe_subtotal_footer_separator:contains("55.20")',
},{
    trigger:'span:contains("Matrix(PAV11,PAV22,PAV31)\n\nPA4:PAV41")',
    extra_trigger:'.o_form_editable',
},{
    trigger:'.o_edit_product_configuration',
},{
    trigger:'.o_product_variant_matrix',
    run:function(){
        //resetallqtiesto1
        $('.o_matrix_input').val(1);
    }
},{
    trigger:'span:contains("Confirm")',
},{
    trigger:'.o_sale_order',
    //waitforqtytobe1=>checkthetotaltobesureallqtiesareresetto1
    extra_trigger:'.oe_subtotal_footer_separator:contains("18.40")',
},{
    trigger:'.o_form_button_save:contains("Save")', //SAVESalesOrder.
},
//Openthematrixthroughthepencilbuttonnexttotheproductinlineeditmode.
{
    trigger:'.o_form_button_edit:contains("Edit")',  //EditSalesOrder.
},{
    trigger:'span:contains("Matrix(PAV11,PAV22,PAV31)\n\nPA4:PAV41")',
    extra_trigger:'.o_form_editable',
},{
    trigger:'.o_edit_product_configuration', //editthematrix
},{
    trigger:'.o_product_variant_matrix',
    run:function(){
        //updatesomeofthematrixvalues.
        $('.o_matrix_input').slice(8,16).val(4);
    }//settheqtyto4forhalfofthematrixproducts.
},{
    trigger:'span:contains("Confirm")', //applythematrix
},{
    trigger:'.o_sale_order',
    //waitforqtytobechanged=>checkthetotaltobesureallqtiesaresettoeither1or4
    extra_trigger:'.oe_subtotal_footer_separator:contains("46.00")',
},{
    trigger:'.o_form_button_save:contains("Save")',
},{
    trigger:'.o_form_button_edit:contains("Edit")', //EditSalesOrder.
},
//Ensuresthematrixisopenedwiththevalues,whenaddingthesameproduct.
{
    trigger:"a:contains('Addaproduct')"
},{
    trigger:'div[name="product_template_id"]input',
    run:'textMatrix'
},{
    trigger:'ul.ui-autocompletea:contains("Matrix")',
},{
    trigger:"input[value='4']",
    run:function(){
        //updatesomevaluesofthematrix
        $("input[value='4']").slice(0,4).val(8.2);
    }
},{
    trigger:'span:contains("Confirm")',
},{
    trigger:'.o_sale_order',
    //waitforqtytobechanged=>checkthetotaltobesureallqtiesareset
    extra_trigger:'.oe_subtotal_footer_separator:contains("65.32")',
},{
    trigger:'.o_form_button_save:contains("Save")',
},{
    trigger:'.o_form_button_edit:contains("Edit")',
    run:function(){}, //Ensuretheformissavedbeforeclosingthebrowser
},
]);


});
