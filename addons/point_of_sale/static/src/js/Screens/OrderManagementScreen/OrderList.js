flectra.define('point_of_sale.OrderList',function(require){
    'usestrict';

    const{useState}=owl.hooks;
    const{useListener}=require('web.custom_hooks');
    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');

    /**
     *@props{models.Order}[initHighlightedOrder]initiallyhighligtedorder
     *@props{Array<models.Order>}orders
     */
    classOrderListextendsPosComponent{
        constructor(){
            super(...arguments);
            useListener('click-order',this._onClickOrder);
            this.state=useState({highlightedOrder:this.props.initHighlightedOrder||null});
        }
        gethighlightedOrder(){
            returnthis.state.highlightedOrder;
        }
        _onClickOrder({detail:order}){
            this.state.highlightedOrder=order;
        }
    }
    OrderList.template='OrderList';

    Registries.Component.add(OrderList);

    returnOrderList;
});
