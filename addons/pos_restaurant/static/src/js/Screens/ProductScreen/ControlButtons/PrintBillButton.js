flectra.define('pos_restaurant.PrintBillButton',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constProductScreen=require('point_of_sale.ProductScreen');
    const{useListener}=require('web.custom_hooks');
    constRegistries=require('point_of_sale.Registries');

    classPrintBillButtonextendsPosComponent{
        constructor(){
            super(...arguments);
            useListener('click',this.onClick);
        }
        asynconClick(){
            constorder=this.env.pos.get_order();
            if(order.get_orderlines().length>0){
                order.initialize_validation_date();
                awaitthis.showTempScreen('BillScreen');
            }else{
                awaitthis.showPopup('ErrorPopup',{
                    title:this.env._t('NothingtoPrint'),
                    body:this.env._t('Therearenoorderlines'),
                });
            }
        }
    }
    PrintBillButton.template='PrintBillButton';

    ProductScreen.addControlButton({
        component:PrintBillButton,
        condition:function(){
            returnthis.env.pos.config.iface_printbill;
        },
    });

    Registries.Component.add(PrintBillButton);

    returnPrintBillButton;
});
