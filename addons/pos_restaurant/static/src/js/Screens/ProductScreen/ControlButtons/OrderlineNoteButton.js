flectra.define('pos_restaurant.OrderlineNoteButton',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constProductScreen=require('point_of_sale.ProductScreen');
    const{useListener}=require('web.custom_hooks');
    constRegistries=require('point_of_sale.Registries');

    classOrderlineNoteButtonextendsPosComponent{
        constructor(){
            super(...arguments);
            useListener('click',this.onClick);
        }
        getselectedOrderline(){
            returnthis.env.pos.get_order().get_selected_orderline();
        }
        asynconClick(){
            if(!this.selectedOrderline)return;

            const{confirmed,payload:inputNote}=awaitthis.showPopup('TextAreaPopup',{
                startingValue:this.selectedOrderline.get_note(),
                title:this.env._t('AddNote'),
            });

            if(confirmed){
                this.selectedOrderline.set_note(inputNote);
            }
        }
    }
    OrderlineNoteButton.template='OrderlineNoteButton';

    ProductScreen.addControlButton({
        component:OrderlineNoteButton,
        condition:function(){
            returnthis.env.pos.config.module_pos_restaurant;
        },
    });

    Registries.Component.add(OrderlineNoteButton);

    returnOrderlineNoteButton;
});
