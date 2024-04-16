flectra.define('iap.buy_more_credits',function(require){
'usestrict';

varwidgetRegistry=require('web.widget_registry');
varWidget=require('web.Widget');

varcore=require('web.core');

varQWeb=core.qweb;

varIAPBuyMoreCreditsWidget=Widget.extend({
    className:'o_field_iap_buy_more_credits',

    /**
     *@constructor
     *Preparesthebasicrenderingofeditmodebysettingtheroottobea
     *div.dropdown.open.
     *@seeFieldChar.init
     */
    init:function(parent,data,options){
        this._super.apply(this,arguments);
        this.service_name=options.attrs.service_name;
    },

    /**
     *@override
     */
    start:function(){
        this.$widget=$(QWeb.render('iap.buy_more_credits'));
        this.$buyLink=this.$widget.find('.buy_credits');
        this.$widget.appendTo(this.$el);
        this.$buyLink.click(this._getLink.bind(this));
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------
    _getLink:function(){
        varself=this;
        returnthis._rpc({
            model:'iap.account',
            method:'get_credits_url',
            args:[this.service_name],
        },{
            shadow:true,
        }).then(function(url){
            returnself.do_action({
                type:'ir.actions.act_url',
                url:url,
            });
        });
    },
});

widgetRegistry.add('iap_buy_more_credits',IAPBuyMoreCreditsWidget);

returnIAPBuyMoreCreditsWidget;
});
