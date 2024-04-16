flectra.define('website_sale.payment',function(require){
'usestrict';

varpublicWidget=require('web.public.widget');

publicWidget.registry.WebsiteSalePayment=publicWidget.Widget.extend({
    selector:'#wrapwrap:has(#checkbox_cgv)',
    events:{
        'change#checkbox_cgv':'_onCGVCheckboxClick',
    },

    /**
     *@override
     */
    start:function(){
        this.$checkbox=this.$('#checkbox_cgv');
        this.$payButton=$('button#o_payment_form_pay');
        this.$checkbox.trigger('change');
        returnthis._super.apply(this,arguments);
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _adaptPayButton:function(){
        vardisabledReasons=this.$payButton.data('disabled_reasons')||{};
        disabledReasons.cgv=!this.$checkbox.prop('checked');
        this.$payButton.data('disabled_reasons',disabledReasons);

        this.$payButton.prop('disabled',_.contains(disabledReasons,true));
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _onCGVCheckboxClick:function(){
        this._adaptPayButton();
    },
});
});
