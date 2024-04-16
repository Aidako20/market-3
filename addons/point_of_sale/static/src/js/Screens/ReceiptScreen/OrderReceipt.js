flectra.define('point_of_sale.OrderReceipt',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');

    classOrderReceiptextendsPosComponent{
        constructor(){
            super(...arguments);
            this._receiptEnv=this.props.order.getOrderReceiptEnv();
        }
        willUpdateProps(nextProps){
            this._receiptEnv=nextProps.order.getOrderReceiptEnv();
        }
        getreceipt(){
            returnthis.receiptEnv.receipt;
        }
        getorderlines(){
            returnthis.receiptEnv.orderlines;
        }
        getpaymentlines(){
            returnthis.receiptEnv.paymentlines;
        }
        getisTaxIncluded(){
            returnMath.abs(this.receipt.subtotal-this.receipt.total_with_tax)<=0.000001;
        }
        getreceiptEnv(){
          returnthis._receiptEnv;
        }
        isSimple(line){
            return(
                line.discount===0&&
                line.is_in_unit&&
                line.quantity===1&&
                !(
                    line.display_discount_policy=='without_discount'&&
                    line.price<line.price_lst
                )
            );
        }
    }
    OrderReceipt.template='OrderReceipt';

    Registries.Component.add(OrderReceipt);

    returnOrderReceipt;
});
