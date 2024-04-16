flectra.define('pos_restaurant_adyen.payment',function(require){
    "usestrict";

    varPaymentAdyen=require('pos_adyen.payment');
    varmodels=require('point_of_sale.models');

    PaymentAdyen.include({
        _adyen_pay_data:function(){
            vardata=this._super();

            if(data.SaleToPOIRequest.PaymentRequest.SaleData.SaleToAcquirerData){
                data.SaleToPOIRequest.PaymentRequest.SaleData.SaleToAcquirerData+="&authorisationType=PreAuth";
            }else{
                data.SaleToPOIRequest.PaymentRequest.SaleData.SaleToAcquirerData="authorisationType=PreAuth";
            }
    
            returndata;
        },

        send_payment_adjust:function(cid){
            varorder=this.pos.get_order();
            varline=order.get_paymentline(cid);
            vardata={
                originalReference:line.transaction_id,
                modificationAmount:{
                    value:parseInt(line.amount*Math.pow(10,this.pos.currency.decimals)),
                    currency:this.pos.currency.name,
                },
                merchantAccount:this.payment_method.adyen_merchant_account,
                additionalData:{
                    industryUsage:'DelayedCharge',
                },
            };

            returnthis._call_adyen(data,'adjust');
        },

        canBeAdjusted:function(cid){
            varorder=this.pos.get_order();
            varline=order.get_paymentline(cid);
            return['mc','visa','amex','discover'].includes(line.card_type);
        }
    });
});
