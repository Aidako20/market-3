flectra.define('website_sale_wishlist.tour',function(require){
'usestrict';

varrpc=require('web.rpc');
vartour=require("web_tour.tour");

tour.register('shop_wishlist',{
    test:true,
    url:'/shop?search=CustomizableDesk',
},
    [
        {
            content:"clickonaddtowishlist",
            trigger:'.o_add_wishlist',
        },
        {
            content:"gotowishlist",
            extra_trigger:'a[href="/shop/wishlist"].badge:contains(1)',
            trigger:'a[href="/shop/wishlist"]',
        },
        {
            content:"removefirstiteminwhishlist",
            trigger:'.o_wish_rm:first',
        },
        {
            content:"gobacktothestore",
            trigger:"a[href='/shop']"
        },
        {
            content:"clickonaddtowishlist",
            trigger:'.o_add_wishlist',
        },
        {
            content:"checkvalueofwishlistandgotologin",
            extra_trigger:".my_wish_quantity:contains(1)",
            trigger:'a[href="/web/login"]',
        },
        {
            content:"submitlogin",
            trigger:".oe_login_form",
            run:function(){
                $('.oe_login_forminput[name="login"]').val("admin");
                $('.oe_login_forminput[name="password"]').val("admin");
                $('.oe_login_forminput[name="redirect"]').val("/shop?search=CustomizableDesk");
                $('.oe_login_form').submit();
            },
        },
        {
            content:"checkthatloggedin",
            trigger:"lispan:contains('MitchellAdmin')",
            run:function(){},
        },
        {
            content:"clickonCustomizableDesk(TEST)",
            trigger:'.oe_product_carta:contains("CustomizableDesk(TEST)")',
        },
        {
            content:"checkthefirstvariantisalreadyinwishlist",
            trigger:'#product_detail.o_add_wishlist_dyn:disabled',
            run:function(){},
        },
        {
            content:"changevariant",
            extra_trigger:'#product_detaillabel:contains(Aluminium)input',
            trigger:'label:contains(Aluminium)input',
        },
        {
            content:"waitbuttonenableandclickonaddtowishlist",
            extra_trigger:'#product_detail.o_add_wishlist_dyn:not(:disabled)',
            trigger:'#product_detail.o_add_wishlist_dyn',
        },
        {
            content:"checkthatwishlistcontains2itemsandgotowishlist",
            extra_trigger:'a[href="/shop/wishlist"].badge:contains(2)',
            trigger:'a[href="/shop/wishlist"]',
        },
        {
            content:"removeCustomizableDesk(TEST)",
            trigger:'tr:contains("CustomizableDesk(TEST)").o_wish_rm:first',
        },
        {
            content:"checkthatwishlistcontains1item",
            trigger:".my_wish_quantity:contains(1)",
            run:function(){},
        },
        {
            content:"checkB2Bwishlistmode",
            trigger:"input#b2b_wish",
        },
        {
            content:"additemtocart",
            trigger:'.o_wish_add:eq(1)',
        },
        {
            content:"checkthatcartcontains1item",
            trigger:".my_cart_quantity:contains(1)",
            run:function(){},
        },
        {
            content:"checkthatwishlistcontains1item",
            trigger:".my_wish_quantity:contains(1)",
            run:function(){},
        },
        {
            content:"removeB2Bwishlistmode",
            trigger:"input#b2b_wish",
        },
        {
            content:"addlastitemtocart",
            trigger:'.o_wish_add:eq(1)',
        },
        {
            content:"checkthatuserisredirect-wishlistisempty",
            trigger:"#wrap#cart_products",
            run:function(){},
        },
        {
            content:"checkthatcartcontains2items",
            trigger:".my_cart_quantity:contains(2)",
            run:function(){},
        },
        {
            content:"checkthatwishlistisemptyandnomorevisible",
            trigger:":not(:has(.my_wish_quantity:visible))",
            run:function(){},
        },
        //Testdynamicattributes
        {
            content:"Createaproductwithdynamicattributeanditsvalues.",
            trigger:'body',
            run:function(){
                rpc.query({
                    model:'product.attribute',
                    method:'create',
                    args:[{
                        'name':"color",
                        'display_type':'color',
                        'create_variant':'dynamic'
                    }],
                }).then(function(attributeId){
                    returnrpc.query({
                        model:'product.template',
                        method:'create',
                        args:[{
                            'name':"Bottle",
                            'is_published':true,
                            'attribute_line_ids':[[0,0,{
                                'attribute_id':attributeId,
                                'value_ids':[
                                    [0,0,{
                                        'name':"red",
                                        'attribute_id':attributeId,
                                    }],
                                    [0,0,{
                                        'name':"blue",
                                        'attribute_id':attributeId,
                                    }],
                                    [0,0,{
                                        'name':"black",
                                        'attribute_id':attributeId,
                                    }],
                                ]
                            }]],
                        }],
                    });
                }).then(function(){
                    window.location.href='/web/session/logout?redirect=/shop?search=Bottle';
                });
            },
        },
        {
            content:"AddBottletowishlistfrom/shop",
            extra_trigger:'.oe_product_cart:contains("Bottle")',
            trigger:'.oe_product_cart:contains("Bottle").o_add_wishlist',
        },
        {
            content:"Checkthatwishlistcontains1item",
            trigger:'.my_wish_quantity:contains(1)',
            run:function(){},
        },
        {
            content:"Clickonproduct",
            extra_trigger:'.oe_product_cart:contains("Bottle").o_add_wishlist.disabled',
            trigger:'.oe_product_carta:contains("Bottle")',
        },
        {
            content:"SelectBottlewithsecondvariantfrom/product",
            trigger:'.js_variant_change[data-value_name="blue"]',
        },
        {
            content:"Addproductinwishlist",
            extra_trigger:'#product_detail.o_add_wishlist_dyn:not(".disabled")',
            trigger:'#product_detail.o_add_wishlist_dyn',
        },
        {
            content:"SelectBottlewiththirdvariantfrom/product",
            trigger:'.js_variant_change[data-value_name="black"]',
        },
        {
            content:"Addproductinwishlist",
            extra_trigger:'#product_detail.o_add_wishlist_dyn:not(".disabled")',
            trigger:'#product_detail.o_add_wishlist_dyn',
        },
        {
            content:"Checkthatwishlistcontains3itemsandgotowishlist",
            trigger:'.my_wish_quantity:contains(3)',
            run:function(){
                window.location.href='/shop/wishlist';
            },
        },
        {
            content:"Checkwishlistcontainsfirstvariant",
            trigger:'#o_comparelist_tabletr:contains("red")',
            run:function(){},
        },
        {
            content:"Checkwishlistcontainssecondvariant",
            trigger:'#o_comparelist_tabletr:contains("blue")',
            run:function(){},
        },
        {
            content:"Checkwishlistcontainsthirdvariant,thengotologin",
            trigger:'#o_comparelist_tabletr:contains("black")',
            run:function(){
                window.location.href="/web/login";
            },
        },
        {
            content:"Submitloginasadmin",
            trigger:'.oe_login_form',
            run:function(){
                $('.oe_login_forminput[name="login"]').val("admin");
                $('.oe_login_forminput[name="password"]').val("admin");
                $('.oe_login_forminput[name="redirect"]').val("/");
                $('.oe_login_form').submit();
            },
        },
        //Testoneimpossiblecombinationwhileothercombinationsarepossible
        {
            content:"Archivethefirstvariant",
            trigger:'#top_menu:contains("MitchellAdmin")',
            run:function(){
                rpc.query({
                    model:'product.product',
                    method:'search',
                    args:[[['name','=',"Bottle"]]],
                })
                .then(function(productIds){
                    returnrpc.query({
                        model:'product.product',
                        method:'write',
                        args:[productIds[0],{active:false}],
                    });
                })
                .then(function(){
                    window.location.href='/web/session/logout?redirect=/shop?search=Bottle';
                });
            },
        },
        {
            content:"Checkthereiswishlistbuttononproductfrom/shop",
            extra_trigger:'.js_sale',
            trigger:'.oe_product_cart:contains("Bottle").o_add_wishlist',
            run:function(){},
        },
        {
            content:"Clickonproduct",
            trigger:'.oe_product_carta:contains("Bottle")',
        },
        {
            content:"SelectBottlewithfirstvariant(red)from/product",
            trigger:'.js_variant_change[data-value_name="red"]',
        },
        {
            content:"Checkthereisnowishlistbuttonwhenselectingimpossiblevariant",
            trigger:'#product_detail:not(:has(.o_add_wishlist))',
            run:function(){},
        },
        {
            content:"SelectBottlewithsecondvariant(blue)from/product",
            trigger:'.js_variant_change[data-value_name="blue"]',
        },
        {
            content:"Clickonwishlistwhenselectingapossiblevariantfrom/product",
            trigger:'#product_detail.o_add_wishlist_dyn:not(.disabled)',
        },
        {
            content:"Checkproductaddedtowishlistandgotologin",
            trigger:'.my_wish_quantity:contains(1)',
            run:function(){
                window.location.href="/web/login";
            },
        },
        {
            content:"Submitlogin",
            trigger:'.oe_login_form',
            run:function(){
                $('.oe_login_forminput[name="login"]').val("admin");
                $('.oe_login_forminput[name="password"]').val("admin");
                $('.oe_login_forminput[name="redirect"]').val("/");
                $('.oe_login_form').submit();
            },
        },
        //testwhenallcombinationsareimpossible
        {
            content:"Archiveallvariants",
            trigger:'#top_menu:contains("MitchellAdmin")',
            run:function(){
                rpc.query({
                    model:'product.product',
                    method:'search',
                    args:[[['name','=',"Bottle"]]],
                })
                .then(function(productIds){
                    returnrpc.query({
                        model:'product.product',
                        method:'write',
                        args:[productIds,{active:false}],
                    });
                })
                .then(function(){
                    window.location.href='/web/session/logout?redirect=/shop?search=Bottle';
                });
            }
        },
        {
            content:"Checkthatthereisnowishlistbuttonfrom/shop",
            extra_trigger:'.js_sale',
            trigger:'.oe_product_cart:contains("Bottle"):not(:has(.o_add_wishlist))',
            run:function(){},
        },
        {
            content:"Clickonproduct",
            trigger:'.oe_product_carta:contains("Bottle")',
        },
        {
            content:"Checkthatthereisnowishlistbuttonfrom/product",
            trigger:'#product_detail:not(:has(.o_add_wishlist_dyn))',
            run:function(){},
        },
    ]
);

});
