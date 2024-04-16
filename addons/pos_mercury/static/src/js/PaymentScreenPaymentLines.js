flectra.define('pos_mercury.PaymentScreenPaymentLines',function(require){
    'usestrict';

    constPaymentScreenPaymentLines=require('point_of_sale.PaymentScreenPaymentLines');
    constRegistries=require('point_of_sale.Registries');

    constPosMercuryPaymentLines=(PaymentScreenPaymentLines)=>
        classextendsPaymentScreenPaymentLines{
            /**
             *@override
             */
            selectedLineClass(line){
                returnObject.assign({},super.selectedLineClass(line),{
                    o_pos_mercury_swipe_pending:line.mercury_swipe_pending,
                });
            }
            /**
             *@override
             */
            unselectedLineClass(line){
                returnObject.assign({},super.unselectedLineClass(line),{
                    o_pos_mercury_swipe_pending:line.mercury_swipe_pending,
                });
            }
        };

    Registries.Component.extend(PaymentScreenPaymentLines,PosMercuryPaymentLines);

    returnPaymentScreenPaymentLines;
});
