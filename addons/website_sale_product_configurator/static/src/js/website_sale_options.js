flectra.define('website_sale_options.website_sale',function(require){
'usestrict';

varajax=require('web.ajax');
varcore=require('web.core');
varpublicWidget=require('web.public.widget');
varOptionalProductsModal=require('sale_product_configurator.OptionalProductsModal');
require('website_sale.website_sale');

var_t=core._t;

publicWidget.registry.WebsiteSale.include({

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    _onProductReady:function(){
        if(this.isBuyNow){
            returnthis._submitForm();
        }
        this.optionalProductsModal=newOptionalProductsModal(this.$form,{
            rootProduct:this.rootProduct,
            isWebsite:true,
            okButtonText:_t('ProceedtoCheckout'),
            cancelButtonText:_t('ContinueShopping'),
            title:_t('Addtocart'),
            context:this._getContext(),
        }).open();

        this.optionalProductsModal.on('options_empty',null,this._submitForm.bind(this));
        this.optionalProductsModal.on('update_quantity',null,this._onOptionsUpdateQuantity.bind(this));
        this.optionalProductsModal.on('confirm',null,this._onModalSubmit.bind(this,true));
        this.optionalProductsModal.on('back',null,this._onModalSubmit.bind(this,false));

        returnthis.optionalProductsModal.opened();
    },

    /**
     *Updatewebshopbaseformquantity
     *whenquantityisupdatedintheoptionalproductswindow
     *
     *@private
     *@param{integer}quantity
     */
    _onOptionsUpdateQuantity:function(quantity){
        var$qtyInput=this.$form
            .find('.js_main_productinput[name="add_qty"]')
            .first();

        if($qtyInput.length){
            $qtyInput.val(quantity).trigger('change');
        }else{
            //Thishandlesthecasewhenthe"SelectQuantity"customizeshow
            //isdisabled,andthereforetheaboveselectordoesnotfindan
            //element.
            //ToavoidduplicatingallRPC,onlytriggerthevariantchangeif
            //itisnotalreadydonefromtheabovetrigger.
            this.optionalProductsModal.triggerVariantChange(this.optionalProductsModal.$el);
        }
    },

    /**
     *Submitstheformwithadditionalparameters
     *-lang
     *-product_custom_attribute_values:Theproductscustomvariantvalues
     *
     *@private
     *@param{Boolean}goToShopTriggersapagerefreshtotheurl"shop/cart"
     */
    _onModalSubmit:function(goToShop){
        varproductAndOptions=JSON.stringify(
            this.optionalProductsModal.getSelectedProducts()
        );

        ajax.post('/shop/cart/update_option',{
            product_and_options:productAndOptions
        }).then(function(quantity){
            if(goToShop){
                varpath="/shop/cart";
                window.location.pathname=path;
            }
            var$quantity=$(".my_cart_quantity");
            $quantity.parent().parent().removeClass('d-none');
            $quantity.html(quantity).hide().fadeIn(600);
        });
    },
});

returnpublicWidget.registry.WebsiteSaleOptions;

});
