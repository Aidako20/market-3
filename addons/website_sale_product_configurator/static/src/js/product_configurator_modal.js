flectra.define('website_sale_product_configurator.OptionalProductsModal',function(require){
    "usestrict";

varOptionalProductsModal=require('sale_product_configurator.OptionalProductsModal');

OptionalProductsModal.include({
    /**
     *Ifthe"isWebsite"paramistrue,willalsodisablethefollowingevents:
     *-change[data-attribute_exclusions]
     *-clickbutton.js_add_cart_json
     *
     *Thishastobedonebecausethoseeventsarealreadyregisteredatthe"website_sale"
     *componentlevel.
     *Thismodalispartoftheformthathastheseeventsregisteredandwe
     *wanttoavoidduplicates.
     *
     *@override
     *@param{$.Element}parentTheparentcontainer
     *@param{Object}params
     *@param{boolean}params.isWebsiteIfwe'reonawebshoppage,weneedsome
     *  custombehavior
     */
    init:function(parent,params){
        this._super.apply(this,arguments);
        this.isWebsite=params.isWebsite;

        this.dialogClass='oe_optional_products_modal'+(params.isWebsite?'oe_website_sale':'');
    },
    /**
     *@override
     *@private
     */
    _triggerPriceUpdateOnChangeQuantity:function(){
        return!this.isWebsite;
    }
});

});
