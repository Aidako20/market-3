flectra.define('pos_restaurant.SplitBillButton',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constProductScreen=require('point_of_sale.ProductScreen');
    const{useListener}=require('web.custom_hooks');
    constRegistries=require('point_of_sale.Registries');

    classSplitBillButtonextendsPosComponent{
        constructor(){
            super(...arguments);
            useListener('click',this.onClick);
        }
        asynconClick(){
            constorder=this.env.pos.get_order();
            if(order.get_orderlines().length>0){
                this.showScreen('SplitBillScreen');
            }
        }
    }
    SplitBillButton.template='SplitBillButton';

    ProductScreen.addControlButton({
        component:SplitBillButton,
        condition:function(){
            returnthis.env.pos.config.iface_splitbill;
        },
    });

    Registries.Component.add(SplitBillButton);

    returnSplitBillButton;
});
