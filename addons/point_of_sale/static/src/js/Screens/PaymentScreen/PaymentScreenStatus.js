flectra.define('point_of_sale.PaymentScreenStatus',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');

    classPaymentScreenStatusextendsPosComponent{
        getchangeText(){
            returnthis.env.pos.format_currency(this.currentOrder.get_change());
        }
        gettotalDueText(){
            returnthis.env.pos.format_currency(
                this.currentOrder.get_total_with_tax()+this.currentOrder.get_rounding_applied()
            );
        }
        getremainingText(){
            returnthis.env.pos.format_currency(
                this.currentOrder.get_due()>0?this.currentOrder.get_due():0
            );
        }
        getcurrentOrder(){
            returnthis.env.pos.get_order();
        }
    }
    PaymentScreenStatus.template='PaymentScreenStatus';

    Registries.Component.add(PaymentScreenStatus);

    returnPaymentScreenStatus;
});
