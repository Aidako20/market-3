flectra.define('website_sale.tracking',function(require){

varpublicWidget=require('web.public.widget');

publicWidget.registry.websiteSaleTracking=publicWidget.Widget.extend({
    selector:'.oe_website_sale',
    events:{
        'clickform[action="/shop/cart/update"]a.a-submit':'_onAddProductIntoCart',
        'clicka[href="/shop/checkout"]':'_onCheckoutStart',
        'clickdiv.oe_carta[href^="/web?redirect"][href$="/shop/checkout"]':'_onCustomerSignin',
        'clickform[action="/shop/confirm_order"]a.a-submit':'_onOrder',
        'clickform[target="_self"]button[type=submit]':'_onOrderPayment',
    },

    /**
     *@override
     */
    start:function(){
        varself=this;

        //Watchingaproduct
        if(this.$el.is('#product_detail')){
            varproductID=this.$('input[name="product_id"]').attr('value');
            this._vpv('/stats/ecom/product_view/'+productID);
        }

        //...
        if(this.$('div.oe_website_sale_tx_status').length){
            this._trackGA('require','ecommerce');

            varorderID=this.$('div.oe_website_sale_tx_status').data('order-id');
            this._vpv('/stats/ecom/order_confirmed/'+orderID);

            this._rpc({
                route:'/shop/tracking_last_order/',
            }).then(function(o){
                self._trackGA('ecommerce:clear');

                if(o.transaction&&o.lines){
                    self._trackGA('ecommerce:addTransaction',o.transaction);
                    _.forEach(o.lines,function(line){
                        self._trackGA('ecommerce:addItem',line);
                    });
                }
                self._trackGA('ecommerce:send');
            });
        }

        returnthis._super.apply(this,arguments);
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _trackGA:function(){
        varwebsiteGA=window.ga||function(){};
        websiteGA.apply(this,arguments);
    },
    /**
     *@private
     */
    _vpv:function(page){//virtualpageview
        this._trackGA('send','pageview',{
          'page':page,
          'title':document.title,
        });
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _onAddProductIntoCart:function(){
        varproductID=this.$('input[name="product_id"]').attr('value');
        this._vpv('/stats/ecom/product_add_to_cart/'+productID);
    },
    /**
     *@private
     */
    _onCheckoutStart:function(){
        this._vpv('/stats/ecom/customer_checkout');
    },
    /**
     *@private
     */
    _onCustomerSignin:function(){
        this._vpv('/stats/ecom/customer_signin');
    },
    /**
     *@private
     */
    _onOrder:function(){
        if($('#top_menu[href="/web/login"]').length){
            this._vpv('/stats/ecom/customer_signup');
        }
        this._vpv('/stats/ecom/order_checkout');
    },
    /**
     *@private
     */
    _onOrderPayment:function(){
        varmethod=$('#payment_methodinput[name=acquirer]:checked').nextAll('span:first').text();
        this._vpv('/stats/ecom/order_payment/'+method);
    },
});
});
