flectra.define('point_of_sale.ErrorPopup',function(require){
    'usestrict';

    constAbstractAwaitablePopup=require('point_of_sale.AbstractAwaitablePopup');
    constRegistries=require('point_of_sale.Registries');

    //formerlyErrorPopupWidget
    classErrorPopupextendsAbstractAwaitablePopup{
        mounted(){
            this.playSound('error');
        }
    }
    ErrorPopup.template='ErrorPopup';
    ErrorPopup.defaultProps={
        confirmText:'Ok',
        cancelText:'Cancel',
        title:'Error',
        body:'',
    };

    Registries.Component.add(ErrorPopup);

    returnErrorPopup;
});
