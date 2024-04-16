flectra.define('pos_restaurant.TableGuestsButton',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constProductScreen=require('point_of_sale.ProductScreen');
    const{useListener}=require('web.custom_hooks');
    constRegistries=require('point_of_sale.Registries');

    classTableGuestsButtonextendsPosComponent{
        constructor(){
            super(...arguments);
            useListener('click',this.onClick);
        }
        getcurrentOrder(){
            returnthis.env.pos.get_order();
        }
        getnGuests(){
            returnthis.currentOrder?this.currentOrder.get_customer_count():0;
        }
        asynconClick(){
            const{confirmed,payload:inputNumber}=awaitthis.showPopup('NumberPopup',{
                startingValue:this.nGuests,
                cheap:true,
                title:this.env._t('Guests?'),
            });

            if(confirmed){
                this.env.pos.get_order().set_customer_count(parseInt(inputNumber,10)||1);
            }
        }
    }
    TableGuestsButton.template='TableGuestsButton';

    ProductScreen.addControlButton({
        component:TableGuestsButton,
        condition:function(){
            returnthis.env.pos.config.module_pos_restaurant;
        },
    });

    Registries.Component.add(TableGuestsButton);

    returnTableGuestsButton;
});
