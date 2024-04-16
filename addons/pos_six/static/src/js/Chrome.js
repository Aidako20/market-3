flectra.define('pos_six.chrome',function(require){
    'usestrict';

    constChrome=require('point_of_sale.Chrome');
    constRegistries=require('point_of_sale.Registries');

    constPosSixChrome=(Chrome)=>
        classextendsChrome{
            getbalanceButtonIsShown(){
                returnthis.env.pos.payment_methods.some(pm=>pm.use_payment_terminal==='six');
            }
        };

    Registries.Component.extend(Chrome,PosSixChrome);

    returnChrome;
});
