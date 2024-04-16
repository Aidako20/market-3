flectra.define('website_sale_stock.VariantMixin',function(require){
'usestrict';

varVariantMixin=require('sale.VariantMixin');
varpublicWidget=require('web.public.widget');
varajax=require('web.ajax');
varcore=require('web.core');
varQWeb=core.qweb;
varxml_load=ajax.loadXML(
    '/website_sale_stock/static/src/xml/website_sale_stock_product_availability.xml',
    QWeb
);

/**
 *Additiontothevariant_mixin._onChangeCombination
 *
 *Thiswillpreventtheuserfromselectingaquantitythatisnotavailableinthe
 *stockforthatproduct.
 *
 *Itwillalsodisplayvariousinfo/warningmessagesregardingtheselectproduct'sstock.
 *
 *Thisbehaviorisonlyappliedforthewebshop(andnotontheSOform)
 *andonlyforthemainproduct.
 *
 *@param{MouseEvent}ev
 *@param{$.Element}$parent
 *@param{Array}combination
 */
VariantMixin._onChangeCombinationStock=function(ev,$parent,combination){
    varproduct_id=0;
    //neededforlistviewofvariants
    if($parent.find('input.product_id:checked').length){
        product_id=$parent.find('input.product_id:checked').val();
    }else{
        product_id=$parent.find('.product_id').val();
    }
    varisMainProduct=combination.product_id&&
        ($parent.is('.js_main_product')||$parent.is('.main_product'))&&
        combination.product_id===parseInt(product_id);

    if(!this.isWebsite||!isMainProduct){
        return;
    }

    varqty=$parent.find('input[name="add_qty"]').val();

    $parent.find('#add_to_cart').removeClass('out_of_stock');
    $parent.find('#buy_now').removeClass('out_of_stock');
    if(combination.product_type==='product'&&_.contains(['always','threshold'],combination.inventory_availability)){
        combination.virtual_available-=parseInt(combination.cart_qty);
        if(combination.virtual_available<0){
            combination.virtual_available=0;
        }
        //Handlecasewhenmanuallywriteininput
        if(qty>combination.virtual_available){
            var$input_add_qty=$parent.find('input[name="add_qty"]');
            qty=combination.virtual_available||1;
            $input_add_qty.val(qty);
        }
        if(qty>combination.virtual_available
            ||combination.virtual_available<1||qty<1){
            $parent.find('#add_to_cart').addClass('disabledout_of_stock');
            $parent.find('#buy_now').addClass('disabledout_of_stock');
        }
    }

    xml_load.then(function(){
        $('.oe_website_sale')
            .find('.availability_message_'+combination.product_template)
            .remove();

        var$message=$(QWeb.render(
            'website_sale_stock.product_availability',
            combination
        ));
        $('div.availability_messages').html($message);
    });
};

publicWidget.registry.WebsiteSale.include({
    /**
     *Addsthestockcheckingtotheregular_onChangeCombinationmethod
     *@override
     */
    _onChangeCombination:function(){
        this._super.apply(this,arguments);
        VariantMixin._onChangeCombinationStock.apply(this,arguments);
    }
});

returnVariantMixin;

});
