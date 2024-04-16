flectra.define('point_of_sale.ErrorBarcodePopup',function(require){
    'usestrict';

    constErrorPopup=require('point_of_sale.ErrorPopup');
    constRegistries=require('point_of_sale.Registries');

    //formerlyErrorBarcodePopupWidget
    classErrorBarcodePopupextendsErrorPopup{
        gettranslatedMessage(){
            returnthis.env._t(this.props.message);
        }
    }
    ErrorBarcodePopup.template='ErrorBarcodePopup';
    ErrorBarcodePopup.defaultProps={
        confirmText:'Ok',
        cancelText:'Cancel',
        title:'Error',
        body:'',
        message:
            'ThePointofSalecouldnotfindanyproduct,client,employeeoractionassociatedwiththescannedbarcode.',
    };

    Registries.Component.add(ErrorBarcodePopup);

    returnErrorBarcodePopup;
});
