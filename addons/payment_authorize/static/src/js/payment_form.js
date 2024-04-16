flectra.define('payment_authorize.payment_form',function(require){
"usestrict";

varajax=require('web.ajax');
varcore=require('web.core');
varPaymentForm=require('payment.payment_form');

var_t=core._t;

PaymentForm.include({

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *ReturnstheparametersfortheAcceptUIbuttonthatAcceptJSwilluse.
     *
     *@private
     *@param{Object}formDatadataobtainedbygetFormData
     *@returns{Object}paramsfortheAcceptJSbutton
     */
    _acceptJsParams:function(formData){
        return{
            'class':'AcceptUId-none',
            'data-apiLoginID':formData.login_id,
            'data-clientKey':formData.client_key,
            'data-billingAddressOptions':'{"show":false,"required":false}',
            'data-responseHandler':'responseHandler'
        };
    },

    /**
     *calledwhenclickingonpaynoworaddpaymenteventtocreatetokenforcreditcard/debitcard.
     *
     *@private
     *@param{Event}ev
     *@param{DOMElement}checkedRadio
     *@param{Boolean}addPmEvent
     */
    _createAuthorizeToken:function(ev,$checkedRadio,addPmEvent){
        varself=this;
        if(ev.type==='submit'){
            varbutton=$(ev.target).find('*[type="submit"]')[0]
        }else{
            varbutton=ev.target;
        }
        varacquirerID=this.getAcquirerIdFromRadio($checkedRadio);
        varacquirerForm=this.$('#o_payment_add_token_acq_'+acquirerID);
        varinputsForm=$('input',acquirerForm);
        varformData=self.getFormData(inputsForm);
        if(this.options.partnerId===undefined){
            console.warn('payment_form:unsetpartner_idwhenaddingnewtoken;thingscouldgowrong');
        }
        varAcceptJs=false;
        if(formData.acquirer_state==='enabled'){
            AcceptJs='https://js.authorize.net/v3/AcceptUI.js';
        }else{
            AcceptJs='https://jstest.authorize.net/v3/AcceptUI.js';
        }

        window.responseHandler=function(response){
            _.extend(formData,response);

            if(response.messages.resultCode==="Error"){
                varerrorMessage="";
                _.each(response.messages.message,function(message){
                    errorMessage+=message.code+":"+message.text;
                })
                acquirerForm.removeClass('d-none');
                returnself.displayError(_t('ServerError'),errorMessage);
            }

            self._rpc({
                route:formData.data_set,
                params:formData
            }).then(function(data){
                if(addPmEvent){
                    if(formData.return_url){
                        window.location=formData.return_url;
                    }else{
                        window.location.reload();
                    }
                }else{
                    $checkedRadio.val(data.id);
                    self.el.submit();
                }
            }).guardedCatch(function(error){
                //iftherpcfails,prettyobvious
                error.event.preventDefault();
                acquirerForm.removeClass('d-none');
                self.displayError(
                    _t('ServerError'),
                    _t("Wearenotabletoaddyourpaymentmethodatthemoment.")+
                        self._parseError(error)
                );
            });
        };

        if(this.$button===undefined){
            this.$button=$('<button>',this._acceptJsParams(formData));
            this.$button.appendTo('body');
        }
        ajax.loadJS(AcceptJs).then(function(){
            self.$button.trigger('click');
        });
    },
    /**
     *@override
     */
    updateNewPaymentDisplayStatus:function(){
        var$checkedRadio=this.$('input[type="radio"]:checked');

        if($checkedRadio.length!==1){
            return;
        }

        // hideaddtokenformforauthorize
        if($checkedRadio.data('provider')==='authorize'&&this.isNewPaymentRadio($checkedRadio)){
            this.$('[id*="o_payment_add_token_acq_"]').addClass('d-none');
        }else{
            this._super.apply(this,arguments);
        }
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@override
     */
    payEvent:function(ev){
        ev.preventDefault();
        var$checkedRadio=this.$('input[type="radio"]:checked');

        //firstwecheckthattheuserhasselectedaauthorizeass2spaymentmethod
        if($checkedRadio.length===1&&this.isNewPaymentRadio($checkedRadio)&&$checkedRadio.data('provider')==='authorize'){
            this._createAuthorizeToken(ev,$checkedRadio);
        }else{
            this._super.apply(this,arguments);
        }
    },
    /**
     *@override
     */
    addPmEvent:function(ev){
        ev.stopPropagation();
        ev.preventDefault();
        var$checkedRadio=this.$('input[type="radio"]:checked');

        //firstwecheckthattheuserhasselectedaauthorizeasaddpaymentmethod
        if($checkedRadio.length===1&&this.isNewPaymentRadio($checkedRadio)&&$checkedRadio.data('provider')==='authorize'){
            this._createAuthorizeToken(ev,$checkedRadio,true);
        }else{
            this._super.apply(this,arguments);
        }
    },
});
});
