flectra.define("website_sale.tour_shop_custom_attribute_value",function(require){
    "usestrict";

    vartour=require("web_tour.tour");

    tour.register("shop_custom_attribute_value",{
        url:"/shop?search=CustomizableDesk",
        test:true,
    },[{
        content:"clickonCustomizableDesk",
        trigger:'.oe_product_carta:contains("CustomizableDesk(TEST)")',
    },{
        trigger:'li.js_attribute_valuespan:contains(CustomTEST)',
        extra_trigger:'li.js_attribute_value',
        run:'click',
    },{
        trigger:'input.variant_custom_value',
        run:'textWood',
    },{
        id:'add_cart_step',
        trigger:'a:contains(AddtoCart)',
        run:'click',
    },{
        trigger:'span:contains(CustomTEST:Wood)',
        extra_trigger:'#cart_products',
        run:function(){},//check
    }]);
});
