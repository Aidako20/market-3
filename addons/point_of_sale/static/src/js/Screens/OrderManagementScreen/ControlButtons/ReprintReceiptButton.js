flectra.define('point_of_sale.ReprintReceiptButton',function(require){
    'usestrict';

    const{useListener}=require('web.custom_hooks');
    const{useContext}=owl.hooks;
    constPosComponent=require('point_of_sale.PosComponent');
    constOrderManagementScreen=require('point_of_sale.OrderManagementScreen');
    constRegistries=require('point_of_sale.Registries');
    constcontexts=require('point_of_sale.PosContext');

    classReprintReceiptButtonextendsPosComponent{
        constructor(){
            super(...arguments);
            useListener('click',this._onClick);
            this.orderManagementContext=useContext(contexts.orderManagement);
        }
        async_onClick(){
            constorder=this.orderManagementContext.selectedOrder;
            if(!order)return;

            this.showScreen('ReprintReceiptScreen',{order:order});
        }
    }
    ReprintReceiptButton.template='ReprintReceiptButton';

    OrderManagementScreen.addControlButton({
        component:ReprintReceiptButton,
        condition:function(){
            returntrue;
        },
    });

    Registries.Component.add(ReprintReceiptButton);

    returnReprintReceiptButton;
});
