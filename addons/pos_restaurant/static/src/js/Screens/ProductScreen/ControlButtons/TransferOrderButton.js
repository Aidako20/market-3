flectra.define('pos_restaurant.TransferOrderButton',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constProductScreen=require('point_of_sale.ProductScreen');
    const{useListener}=require('web.custom_hooks');
    constRegistries=require('point_of_sale.Registries');

    classTransferOrderButtonextendsPosComponent{
        constructor(){
            super(...arguments);
            useListener('click',this.onClick);
        }
        onClick(){
            this.env.pos.transfer_order_to_different_table();
        }
    }
    TransferOrderButton.template='TransferOrderButton';

    ProductScreen.addControlButton({
        component:TransferOrderButton,
        condition:function(){
            returnthis.env.pos.config.iface_floorplan;
        },
    });

    Registries.Component.add(TransferOrderButton);

    returnTransferOrderButton;
});
