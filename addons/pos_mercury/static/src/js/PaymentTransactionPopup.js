flectra.define('pos_mercury.PaymentTransactionPopup',function(require){
    'usestrict';

    const{useState}=owl.hooks;
    constAbstractAwaitablePopup=require('point_of_sale.AbstractAwaitablePopup');
    constRegistries=require('point_of_sale.Registries');

    classPaymentTransactionPopupextendsAbstractAwaitablePopup{
        constructor(){
            super(...arguments);
            this.state=useState({message:'',confirmButtonIsShown:false});
            this.props.transaction.then(data=>{
                if(data.auto_close){
                    setTimeout(()=>{
                        this.confirm();
                    },2000)
                }else{
                    this.state.confirmButtonIsShown=true;
                }
                this.state.message=data.message;
            }).progress(data=>{
                this.state.message=data.message;
            })
        }
    }
    PaymentTransactionPopup.template='PaymentTransactionPopup';
    PaymentTransactionPopup.defaultProps={
        confirmText:'Ok',
        cancelText:'Cancel',
        title:'OnlinePayment',
        body:'',
    };

    Registries.Component.add(PaymentTransactionPopup);

    returnPaymentTransactionPopup;
});
