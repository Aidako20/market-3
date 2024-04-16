flectra.define('point_of_sale.PaymentInterface',function(require){
"usestrict";

varcore=require('web.core');

/**
 *ImplementthisinterfacetosupportanewpaymentmethodinthePOS:
 *
 *varPaymentInterface=require('point_of_sale.PaymentInterface');
 *varMyPayment=PaymentInterface.extend({
 *    ...
 *})
 *
 *Toconnecttheinterfacetotherightpaymentmethodsregisterit:
 *
 *varmodels=require('point_of_sale.models');
 *models.register_payment_method('my_payment',MyPayment);
 *
 *my_paymentisthetechnicalnameoftheaddedselectionin
 *use_payment_terminal.
 *
 *Ifnecessarynewfieldscanbeloadedonanymodel:
 *
 *models.load_fields('pos.payment.method',['new_field1','new_field2']);
 */
varPaymentInterface=core.Class.extend({
    init:function(pos,payment_method){
        this.pos=pos;
        this.payment_method=payment_method;
        this.supports_reversals=false;
    },

    /**
     *CallthisfunctiontoenableUIelementsthatallowauserto
     *reverseapayment.Thisrequiresthatyouimplement
     *send_payment_reversal.
     */
    enable_reversals:function(){
        this.supports_reversals=true;
    },

    /**
     *Calledwhenauserclicksthe"Send"buttoninthe
     *interface.Thisshouldinitiateapaymentrequestandreturna
     *Promisethatresolveswhenthefinalstatusofthepaymentline
     *issetwithset_payment_status.
     *
     *Forsuccessfultransactionsset_receipt_info()shouldbeused
     *tosetinfothatshouldtobeprintedonthereceipt.You
     *shouldalsosetcard_typeandtransaction_idonthelinefor
     *successfultransactions.
     *
     *@param{string}cid-Theidofthepaymentline
     *@returns{Promise}resolvedwithabooleanthatisfalsewhen
     *thepaymentshouldberetried.Rejectedwhenthestatusofthe
     *paymentlinewillbemanuallyupdated.
     */
    send_payment_request:function(cid){},

    /**
     *Calledwhenauserremovesapaymentlinethat'sstillwaiting
     *onsend_payment_requesttocomplete.Shouldexecutesome
     *requesttoensurethecurrentpaymentrequestis
     *cancelled.Thisisnottorefundpayments,onlytocancel
     *them.Thepaymentlinebeingcancelledwillbedeleted
     *automaticallyafterthereturnedpromiseresolves.
     *
     *@param{}order-Theorderofthepaymentline
     *@param{string}cid-Theidofthepaymentline
     *@returns{Promise}
     */
    send_payment_cancel:function(order,cid){},

    /**
     *Thisisanoptionalmethod.Whenimplementingthismakesureto
     *callenable_reversals()intheconstructorofyour
     *interface.Thisshouldreverseapreviouspaymentwithstatus
     *'done'.Thepaymentlinewillberemovedbasedonreturned
     *Promise.
     *
     *@param{string}cid-Theidofthepaymentline
     *@returns{Promise}returnstrueifthereversalwassuccessful.
     */
    send_payment_reversal:function(cid){},

    /**
     *CalledwhenthepaymentscreeninthePOSisclosed(by
     *e.g.clickingthe"Back"button).Couldbeusedtocancelin
     *progresspayments.
     */
    close:function(){},
});

returnPaymentInterface;
});
