flectra.define('pos_mercury.ProductScreen',function(require){
    'usestrict';

    constProductScreen=require('point_of_sale.ProductScreen');
    constRegistries=require('point_of_sale.Registries');
    const{useBarcodeReader}=require('point_of_sale.custom_hooks');

    constPosMercuryProductScreen=(ProductScreen)=>
        classextendsProductScreen{
            constructor(){
                super(...arguments);
                useBarcodeReader({
                    credit:this.credit_error_action,
                });
            }
            credit_error_action(){
                this.showPopup('ErrorPopup',{
                    body:this.env._t('Gotopaymentscreentousecards'),
                });
            }
        };

    Registries.Component.extend(ProductScreen,PosMercuryProductScreen);

    returnProductScreen;
});
