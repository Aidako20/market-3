flectra.define('point_of_sale.OrderImportPopup',function(require){
    'usestrict';

    constAbstractAwaitablePopup=require('point_of_sale.AbstractAwaitablePopup');
    constRegistries=require('point_of_sale.Registries');

    //formerlyOrderImportPopupWidget
    classOrderImportPopupextendsAbstractAwaitablePopup{
        getunpaidSkipped(){
            return(
                (this.props.report.unpaid_skipped_existing||0)+
                (this.props.report.unpaid_skipped_session||0)
            );
        }
        getPayload(){}
    }
    OrderImportPopup.template='OrderImportPopup';
    OrderImportPopup.defaultProps={
        confirmText:'Ok',
        cancelText:'Cancel',
        body:'',
    };

    Registries.Component.add(OrderImportPopup);

    returnOrderImportPopup;
});
