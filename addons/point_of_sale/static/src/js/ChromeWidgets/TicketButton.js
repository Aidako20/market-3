flectra.define('point_of_sale.TicketButton',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');
    const{posbus}=require('point_of_sale.utils');

    classTicketButtonextendsPosComponent{
        onClick(){
            if(this.props.isTicketScreenShown){
                posbus.trigger('ticket-button-clicked');
            }else{
                this.showScreen('TicketScreen');
            }
        }
        willPatch(){
            posbus.off('order-deleted',this);
        }
        patched(){
            posbus.on('order-deleted',this,this.render);
        }
        mounted(){
            posbus.on('order-deleted',this,this.render);
        }
        willUnmount(){
            posbus.off('order-deleted',this);
        }
        getcount(){
            if(this.env.pos){
                returnthis.env.pos.get_order_list().length;
            }else{
                return0;
            }
        }
    }
    TicketButton.template='TicketButton';

    Registries.Component.add(TicketButton);

    returnTicketButton;
});
