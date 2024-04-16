flectra.define('point_of_sale.SetPricelistButton',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constProductScreen=require('point_of_sale.ProductScreen');
    const{useListener}=require('web.custom_hooks');
    constRegistries=require('point_of_sale.Registries');

    classSetPricelistButtonextendsPosComponent{
        constructor(){
            super(...arguments);
            useListener('click',this.onClick);
        }
        mounted(){
            this.env.pos.get('orders').on('addremovechange',()=>this.render(),this);
            this.env.pos.on('change:selectedOrder',()=>this.render(),this);
        }
        willUnmount(){
            this.env.pos.get('orders').off('addremovechange',null,this);
            this.env.pos.off('change:selectedOrder',null,this);
        }
        getcurrentOrder(){
            returnthis.env.pos.get_order();
        }
        getcurrentPricelistName(){
            constorder=this.currentOrder;
            returnorder&&order.pricelist
                ?order.pricelist.display_name
                :this.env._t('Pricelist');
        }
        asynconClick(){
            //CreatethelisttobepassedtotheSelectionPopup.
            //Pricelistobjectispassedasiteminthelistbecauseit
            //istheobjectthatwillbereturnedwhenthepopupisconfirmed.
            constselectionList=this.env.pos.pricelists.map(pricelist=>({
                id:pricelist.id,
                label:pricelist.name,
                isSelected:pricelist.id===this.currentOrder.pricelist.id,
                item:pricelist,
            }));

            const{confirmed,payload:selectedPricelist}=awaitthis.showPopup(
                'SelectionPopup',
                {
                    title:this.env._t('Selectthepricelist'),
                    list:selectionList,
                }
            );

            if(confirmed){
                this.currentOrder.set_pricelist(selectedPricelist);
            }
        }
    }
    SetPricelistButton.template='SetPricelistButton';

    ProductScreen.addControlButton({
        component:SetPricelistButton,
        condition:function(){
            returnthis.env.pos.config.use_pricelist&&this.env.pos.pricelists.length>1;
        },
    });

    Registries.Component.add(SetPricelistButton);

    returnSetPricelistButton;
});
