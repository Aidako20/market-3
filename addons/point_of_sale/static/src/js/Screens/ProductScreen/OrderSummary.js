flectra.define('point_of_sale.OrderSummary',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');

    classOrderSummaryextendsPosComponent{}
    OrderSummary.template='OrderSummary';

    Registries.Component.add(OrderSummary);

    returnOrderSummary;
});
