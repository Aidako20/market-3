flectra.define('point_of_sale.PaymentScreenPaymentLines',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');

    classPaymentScreenPaymentLinesextendsPosComponent{
        formatLineAmount(paymentline){
            returnthis.env.pos.format_currency_no_symbol(paymentline.get_amount());
        }
        selectedLineClass(line){
            return{'payment-terminal':line.get_payment_status()};
        }
        unselectedLineClass(line){
            return{};
        }
    }
    PaymentScreenPaymentLines.template='PaymentScreenPaymentLines';

    Registries.Component.add(PaymentScreenPaymentLines);

    returnPaymentScreenPaymentLines;
});
