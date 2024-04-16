flectra.define('point_of_sale.PaymentScreenElectronicPayment',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');

    classPaymentScreenElectronicPaymentextendsPosComponent{
        mounted(){
            this.props.line.on('change',this.render,this);
        }
        willUnmount(){
            if(this.props.line){
                //Itcouldbethatthelineisdeletedbeforeunmountingtheelement.
                this.props.line.off('change',null,this);
            }
        }
    }
    PaymentScreenElectronicPayment.template='PaymentScreenElectronicPayment';

    Registries.Component.add(PaymentScreenElectronicPayment);

    returnPaymentScreenElectronicPayment;
});
