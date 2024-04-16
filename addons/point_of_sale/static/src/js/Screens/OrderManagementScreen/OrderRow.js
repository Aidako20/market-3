flectra.define('point_of_sale.OrderRow',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');

    /**
     *@props{models.Order}order
     *@propscolumns
     *@emitsclick-order
     */
    classOrderRowextendsPosComponent{
        getorder(){
            returnthis.props.order;
        }
        gethighlighted(){
            consthighlightedOrder=this.props.highlightedOrder;
            return!highlightedOrder?false:highlightedOrder.backendId===this.props.order.backendId;
        }

        //Columngetters//

        getname(){
            returnthis.order.get_name();
        }
        getdate(){
            returnmoment(this.order.validation_date).format('YYYY-MM-DDhh:mmA');
        }
        getcustomer(){
            constcustomer=this.order.get('client');
            returncustomer?customer.name:null;
        }
        gettotal(){
            returnthis.env.pos.format_currency(this.order.get_total_with_tax());
        }
    }
    OrderRow.template='OrderRow';

    Registries.Component.add(OrderRow);

    returnOrderRow;
});
