flectra.define('payment_stripe.stripe',function(require){
"usestrict";

varajax=require('web.ajax');
varcore=require('web.core');

varqweb=core.qweb;
var_t=core._t;

ajax.loadXML('/payment_stripe/static/src/xml/stripe_templates.xml',qweb);

if($.blockUI){
    //ourmessageneedstoappearabovethemodaldialog
    $.blockUI.defaults.baseZ=2147483647;//samez-indexasStripeCheckout
    $.blockUI.defaults.css.border='0';
    $.blockUI.defaults.css["background-color"]='';
    $.blockUI.defaults.overlayCSS["opacity"]='0.9';
}

require('web.dom_ready');
if(!$('.o_payment_form').length){
    returnPromise.reject("DOMdoesn'tcontain'.o_payment_form'");
}

varobserver=newMutationObserver(function(mutations,observer){
    for(vari=0;i<mutations.length;++i){
        for(varj=0;j<mutations[i].addedNodes.length;++j){
            if(mutations[i].addedNodes[j].tagName.toLowerCase()==="form"&&mutations[i].addedNodes[j].getAttribute('provider')==='stripe'){
                _redirectToStripeCheckout($(mutations[i].addedNodes[j]));
            }
        }
    }
});

functiondisplayError(message){
    varwizard=$(qweb.render('stripe.error',{'msg':message||_t('Paymenterror')}));
    wizard.appendTo($('body')).modal({'keyboard':true});
    if($.blockUI){
        $.unblockUI();
    }
    $("#o_payment_form_pay").removeAttr('disabled');
}


function_redirectToStripeCheckout(providerForm){
    //OpenCheckoutwithfurtheroptions
    if($.blockUI){
        varmsg=_t("Justonemoresecond,WeareredirectingyoutoStripe...");
        $.blockUI({
            'message':'<h2class="text-white"><imgsrc="/web/static/src/img/spin.png"class="fa-pulse"/>'+
                    '   <br/>'+msg+
                    '</h2>'
        });
    }

    varpaymentForm=$('.o_payment_form');
    if(!paymentForm.find('i').length){
        paymentForm.append('<iclass="fafa-spinnerfa-spin"/>');
        paymentForm.attr('disabled','disabled');
    }

    var_getStripeInputValue=function(name){
        returnproviderForm.find('input[name="'+name+'"]').val();
    };

    varstripe=Stripe(_getStripeInputValue('stripe_key'));

    stripe.redirectToCheckout({
        sessionId:_getStripeInputValue('session_id')
    }).then(function(result){
        if(result.error){
            displayError(result.error.message);
        }
    });
}

$.getScript("https://js.stripe.com/v3/",function(data,textStatus,jqxhr){
    observer.observe(document.body,{childList:true});
    _redirectToStripeCheckout($('form[provider="stripe"]'));
});
});
