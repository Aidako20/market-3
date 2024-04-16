flectra.define('pos_restaurant.PaymentInterface',function(require){
    "usestrict";

    varPaymentInterface=require('point_of_sale.PaymentInterface');

    PaymentInterface.include({
        /**
         *Returntrueiftheamountthatwasauthorizedcanbemodified,
         *falseotherwise
         *@param{string}cid-Theidofthepaymentline
         */
        canBeAdjusted(cid){
            returnfalse;
        },

        /**
         *Calledwhentheamountauthorizedbyapaymentrequestshould
         *beadjustedtoaccountforaneworderline,itcanonlybecalledif
         *canBeAdjustedreturnsTrue
         *@param{string}cid-Theidofthepaymentline
         */
        send_payment_adjust:function(cid){},
    });
});
