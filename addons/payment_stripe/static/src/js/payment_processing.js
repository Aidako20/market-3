flectra.define('payment_stripe.processing',function(require){
'usestrict';

varajax=require('web.ajax');
varrpc=require('web.rpc')
varpublicWidget=require('web.public.widget');

varPaymentProcessing=publicWidget.registry.PaymentProcessing;

returnPaymentProcessing.include({
    init:function(){
        this._super.apply(this,arguments);
        this._authInProgress=false;
    },
    willStart:function(){
        returnthis._super.apply(this,arguments).then(function(){
            returnajax.loadJS("https://js.stripe.com/v3/");
        })
    },
    _stripeAuthenticate:function(tx){
        varstripe=Stripe(tx.stripe_publishable_key);
        returnstripe.handleCardPayment(tx.stripe_payment_intent_secret)
        .then(function(result){
            if(result.error){
                returnrpc.query({
                    route:'/payment/stripe/s2s/process_payment_error',
                    params:_.extend({},{reference:tx.reference,
                        stripe_payment_intent_secret:tx.stripe_payment_intent_secret,
                        error:result.error.message})
                }).then(()=>Promise.reject({"message":{"data":{"message":result.error.message}}}));
            }
            returnrpc.query({
                route:'/payment/stripe/s2s/process_payment_intent',
                params:_.extend({},result.paymentIntent,{reference:tx.reference}),
            });
        }).then(function(){
            window.location='/payment/process';
        }).guardedCatch(function(){
            this._authInProgress=false;
        });
    },
    processPolledData:function(transactions){
        this._super.apply(this,arguments);
        for(varitx=0;itx<transactions.length;itx++){
            vartx=transactions[itx];
            if(tx.acquirer_provider==='stripe'&&tx.state==='pending'&&tx.stripe_payment_intent_secret&&!this._authInProgress){
                this._authInProgress=true;
                this._stripeAuthenticate(tx);
            }
        }
    },
});
});