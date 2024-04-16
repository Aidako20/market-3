flectra.define('point_of_sale.OrderDetails',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');

    /**
     *@props{models.Order}order
     */
    classOrderDetailsextendsPosComponent{
        getorder(){
            returnthis.props.order;
        }
        getorderlines(){
            returnthis.order?this.order.orderlines.models:[];
        }
        gettotal(){
            returnthis.env.pos.format_currency(this.order?this.order.get_total_with_tax():0);
        }
        gettax(){
            returnthis.env.pos.format_currency(this.order?this.order.get_total_tax():0)
        }
    }
    OrderDetails.template='OrderDetails';

    Registries.Component.add(OrderDetails);

    returnOrderDetails;
});
