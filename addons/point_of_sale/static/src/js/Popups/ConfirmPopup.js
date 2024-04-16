flectra.define('point_of_sale.ConfirmPopup',function(require){
    'usestrict';

    constAbstractAwaitablePopup=require('point_of_sale.AbstractAwaitablePopup');
    constRegistries=require('point_of_sale.Registries');

    //formerlyConfirmPopupWidget
    classConfirmPopupextendsAbstractAwaitablePopup{}
    ConfirmPopup.template='ConfirmPopup';
    ConfirmPopup.defaultProps={
        confirmText:'Ok',
        cancelText:'Cancel',
        title:'Confirm?',
        body:'',
    };

    Registries.Component.add(ConfirmPopup);

    returnConfirmPopup;
});
