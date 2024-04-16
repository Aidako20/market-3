flectra.define('pos_restaurant.OrderRow',function(require){
    'usestrict';

    constOrderRow=require('point_of_sale.OrderRow');
    constRegistries=require('point_of_sale.Registries');

    constPosResOrderRow=(OrderRow)=>
        classextendsOrderRow{
            gettable(){
                returnthis.order.table?this.order.table.name:'';
            }
        };

    Registries.Component.extend(OrderRow,PosResOrderRow);

    returnOrderRow;
});
