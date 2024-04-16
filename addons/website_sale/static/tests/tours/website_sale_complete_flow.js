flectra.define('website_sale_tour.tour',function(require){
    'usestrict';

    vartour=require("web_tour.tour");
    varrpc=require("web.rpc");

    tour.register('website_sale_tour',{
        test:true,
        url:'/shop?search=StorageBoxTest',
    },[
    //Testingb2cwithTax-ExcludedPrices
    {
        content:"Openproductpage",
        trigger:'.oe_product_carta:contains("StorageBoxTest")',
    },
    {
        content:"Addonemorestoragebox",
        trigger:'.js_add_cart_json:eq(1)',
    },
    {
        content:"Checkb2bTax-ExcludedPrices",
        trigger:'.product_price.oe_price.oe_currency_value:containsExact(79.00)',
        run:function(){},//it'sacheck
    },
    {
        content:"Clickonaddtocart",
        trigger:'#add_to_cart',
    },
    {
        content:"Checkfor2productsincartandproceedtocheckout",
        extra_trigger:'#cart_productstr:contains("StorageBoxTest")input.js_quantity:propValue(2)',
        trigger:'a[href*="/shop/checkout"]',
    },
    {
        content:"CheckPriceb2bsubtotal",
        trigger:'tr#order_total_untaxed.oe_currency_value:containsExact(158.00)',
        run:function(){},//it'sacheck
    },
    {
        content:"CheckPriceb2bSaleTax(15%)",
        trigger:'tr#order_total_taxes.oe_currency_value:containsExact(23.70)',
        run:function(){},//it'sacheck
    },
    {
        content:"CheckPriceb2bTotalamount",
        trigger:'tr#order_total.oe_currency_value:containsExact(181.70)',
        run:function(){},//it'sacheck
    },
    {
        content:"Fulfillbillingaddressform",
        trigger:'select[name="country_id"]',
        run:function(){
            $('input[name="name"]').val('abc');
            $('input[name="phone"]').val('99999999');
            $('input[name="email"]').val('abc@flectrahq.com');
            $('input[name="street"]').val('SO1BillingStreet,33');
            $('input[name="city"]').val('SO1BillingCity');
            $('input[name="zip"]').val('10000');
            $('#country_idoption:eq(1)').attr('selected',true);
        },
    },
    {
        content:"Shippingaddressisnotsameasbillingaddress",
        trigger:'#shipping_use_same',
    },
    {
        content:"Clickonnextbutton",
        trigger:'.oe_cart.btn:contains("Next")',
    },
    {
        content:"Fulfillshippingaddressform",
        trigger:'select[name="country_id"]',
        extra_trigger:'h2:contains("ShippingAddress")',
        run:function(){
            $('input[name="name"]').val('def');
            $('input[name="phone"]').val('8888888888');
            $('input[name="street"]').val('17,SO1ShippingRoad');
            $('input[name="city"]').val('SO1ShippingCity');
            $('input[name="zip"]').val('10000');
            $('#country_idoption:eq(1)').attr('selected',true);
        },
    },
    {
        content:"Clickonnextbutton",
        trigger:'.oe_cart.btn:contains("Next")',
    },
    {
        content:"Checkselectedbillingaddressissameastypedinpreviousstep",
        trigger:'#shipping_and_billing:contains(SO1BillingStreet,33):contains(SO1BillingCity):contains(Afghanistan)',
        run:function(){},//it'sacheck
    },
    {
        content:"Checkselectedshippingaddressissameastypedinpreviousstep",
        trigger:'#shipping_and_billing:contains(17,SO1ShippingRoad):contains(SO1ShippingCity):contains(Afghanistan)',
        run:function(){},//it'sacheck
    },
    {
        content:"Clickforeditaddress",
        trigger:'a:contains("Edit")i',
    },
    {
        content:"Clickforeditbillingaddress",
        trigger:'.js_edit_address:first',
    },
    {
        content:"Changebillingaddressform",
        trigger:'select[name="country_id"]',
        extra_trigger:'h2:contains("YourAddress")',
        run:function(){
            $('input[name="name"]').val('abcd');
            $('input[name="phone"]').val('11111111');
            $('input[name="street"]').val('SO1BillingStreetEdited,33');
            $('input[name="city"]').val('SO1BillingCityEdited');
        },
    },
    {
        content:"Clickonnextbutton",
        trigger:'.oe_cart.btn:contains("Next")',
    },
    {
        content:"ConfirmAddress",
        trigger:'a.btn:contains("Confirm")',
    },
    {
        content:"Checkselectedbillingaddressissameastypedinpreviousstep",
        trigger:'#shipping_and_billing:contains(SO1BillingStreetEdited,33):contains(SO1BillingCityEdited):contains(Afghanistan)',
        run:function(){},//it'sacheck
    },
    {
        content:"Select`WireTransfer`paymentmethod",
        trigger:'#payment_methodlabel:contains("WireTransfer")',
    },
    {
        content:"PayNow",
        extra_trigger:'#payment_methodlabel:contains("WireTransfer")input:checked,#payment_method:not(:has("input:radio:visible"))',
        trigger:'button[id="o_payment_form_pay"]:visible:not(:disabled)',
    },
    {
        content:"Signup",
        trigger:'.oe_carta:contains("SignUp")',
    },
    {
        content:"Submitlogin",
        trigger:'.oe_signup_form',
        run:function(){
            $('.oe_signup_forminput[name="password"]').val("1admin@admin");
            $('.oe_signup_forminput[name="confirm_password"]').val("1admin@admin");
            $('.oe_signup_form').submit();
        },
    },
    {
        content:"SeeQuotations",
        trigger:'.o_portal_docsa:contains("Quotations")',
    },
    //Signinasadminchangeconfigauth_signup->b2b,sale_show_tax->totalandLogout
    {
        content:"OpenDropdownforlogout",
        trigger:'#top_menuli.dropdown:visiblea:contains("abcd")',
    },
    {
        content:"Logout",
        trigger:'#o_logout:contains("Logout")',
    },
    {
        content:"Signinasadmin",
        trigger:'headera[href="/web/login"]',
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
    {
        content:"ConfigurationSettingsfor'TaxIncluded'andsignup'OnInvitation'",
        extra_trigger:'.o_connected_user#wrapwrap',
        trigger:'#wrapwrap',
        run:function(){
            vardef1=rpc.query({
                model:'res.config.settings',
                method:'create',
                args:[{
                    'auth_signup_uninvited':'b2b',
                    'show_line_subtotals_tax_selection':'tax_included',
                    'group_show_line_subtotals_tax_excluded':false,
                    'group_show_line_subtotals_tax_included':true,
                }],
            });
            vardef2=def1.then(function(resId){
                returnrpc.query({
                    model:'res.config.settings',
                    method:'execute',
                    args:[[resId]],
                });
            });
            def2.then(function(){
                window.location.href='/web/session/logout?redirect=/shop?search=StorageBoxTest';
            });
        },
    },
    //Testingb2bwithTax-IncludedPrices
    {
        content:"Openproductpage",
        trigger:'.oe_product_carta:contains("StorageBoxTest")',
    },
    {
        content:"AddonemoreStorageBoxTest",
        trigger:'.js_add_cart_json:eq(1)',
    },
    {
        content:"Checkb2cTax-IncludedPrices",
        trigger:'.product_price.oe_price.oe_currency_value:containsExact(90.85)',
        run:function(){},//it'sacheck
    },
    {
        content:"Clickonaddtocart",
        trigger:'#add_to_cart',
    },
    {
        content:"Checkfor2productsincartandproceedtocheckout",
        extra_trigger:'#cart_productstr:contains("StorageBoxTest")input.js_quantity:propValue(2)',
        trigger:'a[href*="/shop/checkout"]',
    },
    {
        content:"CheckPriceb2ctotal",
        trigger:'tr#order_total_untaxed.oe_currency_value:containsExact(158.00)',
        run:function(){},//it'sacheck
    },
    {
        content:"CheckPriceb2cSaleTax(15%)",
        trigger:'tr#order_total_taxes.oe_currency_value:containsExact(23.70)',
        run:function(){},//it'sacheck
    },
    {
        content:"CheckPriceb2cTotalamount",
        trigger:'tr#order_total.oe_currency_value:containsExact(181.70)',
        run:function(){},//it'sacheck
    },
    {
        content:"ClickonLoginButton",
        trigger:'.oe_carta.btn:contains("LogIn")',
    },
    {
        content:"Submitlogin",
        trigger:'.oe_login_form',
        run:function(){
            $('.oe_login_forminput[name="login"]').val("abc@flectrahq.com");
            $('.oe_login_forminput[name="password"]').val("1admin@admin");
            $('.oe_login_form').submit();
        },
    },
    {
        content:"Addnewshippingaddress",
        trigger:'.one_kanbanform[action^="/shop/address"].btn',
    },
    {
        content:"Fulfillshippingaddressform",
        trigger:'select[name="country_id"]',
        run:function(){
            $('input[name="name"]').val('ghi');
            $('input[name="phone"]').val('7777777777');
            $('input[name="street"]').val('SO2NewShippingStreet,5');
            $('input[name="city"]').val('SO2NewShipping');
            $('input[name="zip"]').val('1200');
            $('#country_idoption:eq(1)').attr('selected',true);
        },
    },
    {
        content:"Clickonnextbutton",
        trigger:'.oe_cart.btn:contains("Next")',
    },
    {
        content:"Select`WireTransfer`paymentmethod",
        trigger:'#payment_methodlabel:contains("WireTransfer")',
    },
    {
        content:"PayNow",
        extra_trigger:'#payment_methodlabel:contains("WireTransfer")input:checked,#payment_method:not(:has("input:radio:visible"))',
        trigger:'button[id="o_payment_form_pay"]:visible:not(:disabled)',
    },
    {
        content:"OpenDropdownforSeequotation",
        extra_trigger:'.oe_cart.oe_website_sale_tx_status',
        trigger:'#top_menuli.dropdown:visiblea:contains("abc")',
    },
    {
        content:"Myaccount",
        extra_trigger:'#top_menuli.dropdown.js_usermenu.show',
        trigger:'#top_menu.dropdown-menua[href="/my/home"]:visible',
    },
    {
        content:"SeeQuotations",
        trigger:'.o_portal_docsa:contains("Quotations").badge:containsExact(2)',
    },

    //enableextrasteponwebsitecheckoutandcheckextrasteponcheckoutprocess
    {
        content:"OpenDropdownforlogout",
        trigger:'#top_menuli.dropdown:visiblea:contains("abc")',
    },
    {
        content:"Logout",
        trigger:'#o_logout:contains("Logout")',
    },
    {
        content:"Signinasadmin",
        trigger:'headera[href="/web/login"]',
    },
    {
        content:"Submitlogin",
        trigger:'.oe_login_form',
        run:function(){
            $('.oe_login_forminput[name="login"]').val("admin");
            $('.oe_login_forminput[name="password"]').val("admin");
            $('.oe_login_forminput[name="redirect"]').val("/shop/cart");
            $('.oe_login_form').submit();
        },
    },
    {
        content:"OpenCustomizemenu",
        trigger:'.o_menu_sectionsa:contains("Customize")',
    },
    {
        content:"EnableExtrastep",
        trigger:'a.dropdown-itemlabel:contains("ExtraStepOption")',
    },
    {
        content:"OpenDropdownforlogout",
        extra_trigger:'.progress-wizard-step:contains("ExtraInfo")',
        trigger:'#top_menuli.dropdown:visiblea:contains("MitchellAdmin")',
    },
    {
        content:"Logout",
        trigger:'#o_logout:contains("Logout")',
    },
    {
        content:"Signinasabc",
        trigger:'headera[href="/web/login"]',
    },
    {
        content:"Submitlogin",
        trigger:'.oe_login_form',
        run:function(){
            $('.oe_login_forminput[name="login"]').val("abc@flectrahq.com");
            $('.oe_login_forminput[name="password"]').val("1admin@admin");
            $('.oe_login_forminput[name="redirect"]').val("/shop?search=StorageBoxTest");
            $('.oe_login_form').submit();
        },
    },
    {
        content:"Openproductpage",
        trigger:'.oe_product_carta:contains("StorageBoxTest")',
    },
    {
        content:"Clickonaddtocart",
        trigger:'#add_to_cart',
    },
    {
        content:"Proceedtocheckout",
        trigger:'a[href*="/shop/checkout"]',
    },
    {
        content:"Clickonnextbutton",
        trigger:'.oe_cart.btn:contains("Next")',
    },
    {
        content:"Checkselectedbillingaddressissameastypedinpreviousstep",
        trigger:'#shipping_and_billing:contains(SO1BillingStreetEdited,33):contains(SO1BillingCityEdited):contains(Afghanistan)',
        run:function(){},//it'sacheck
    },
    {
        content:"Checkselectedshippingaddressissameastypedinpreviousstep",
        trigger:'#shipping_and_billing:contains(SO2NewShippingStreet,5):contains(SO2NewShipping):contains(Afghanistan)',
        run:function(){},//it'sacheck
    },
    {
        content:"Select`WireTransfer`paymentmethod",
        trigger:'#payment_methodlabel:contains("WireTransfer")',
    },
    {
        content:"PayNow",
        extra_trigger:'#payment_methodlabel:contains("WireTransfer")input:checked,#payment_method:not(:has("input:radio:visible"))',
        trigger:'button[id="o_payment_form_pay"]:visible',
    }]);
});
