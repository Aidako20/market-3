flectra.define('pos_adyen.payment',function(require){
"usestrict";

varcore=require('web.core');
varrpc=require('web.rpc');
varPaymentInterface=require('point_of_sale.PaymentInterface');
const{Gui}=require('point_of_sale.Gui');

var_t=core._t;

varPaymentAdyen=PaymentInterface.extend({
    send_payment_request:function(cid){
        this._super.apply(this,arguments);
        this._reset_state();
        returnthis._adyen_pay(cid);
    },
    send_payment_cancel:function(order,cid){
        this._super.apply(this,arguments);
        returnthis._adyen_cancel();
    },
    close:function(){
        this._super.apply(this,arguments);
    },

    set_most_recent_service_id(id){
        this.most_recent_service_id=id;
    },

    pending_adyen_line(){
      returnthis.pos.get_order().paymentlines.find(
        paymentLine=>paymentLine.payment_method.use_payment_terminal==='adyen'&&(!paymentLine.is_done()));
    },

    //privatemethods
    _reset_state:function(){
        this.was_cancelled=false;
        this.remaining_polls=4;
        clearTimeout(this.polling);
    },

    _handle_flectra_connection_failure:function(data){
        //handletimeout
        varline=this.pending_adyen_line();
        if(line){
            line.set_payment_status('retry');
        }
        this._show_error(_t('CouldnotconnecttotheFlectraserver,pleasecheckyourinternetconnectionandtryagain.'));

        returnPromise.reject(data);//preventsubsequentonFullFilled'sfrombeingcalled
    },

    _call_adyen:function(data,operation){
        returnrpc.query({
            model:'pos.payment.method',
            method:'proxy_adyen_request',
            args:[[this.payment_method.id],data,operation],
        },{
            //WhenapaymentterminalisdisconnectedittakesAdyen
            //awhiletoreturnanerror(~6s).Sowait10seconds
            //beforeconcludingFlectraisunreachable.
            timeout:10000,
            shadow:true,
        }).catch(this._handle_flectra_connection_failure.bind(this));
    },

    _adyen_get_sale_id:function(){
        varconfig=this.pos.config;
        return_.str.sprintf('%s(ID:%s)',config.display_name,config.id);
    },

    _adyen_common_message_header:function(){
        varconfig=this.pos.config;
        this.most_recent_service_id=Math.floor(Math.random()*Math.pow(2,64)).toString();//randomIDtoidentifyrequest/responsepairs
        this.most_recent_service_id=this.most_recent_service_id.substring(0,10);//maxlengthis10

        return{
            'ProtocolVersion':'3.0',
            'MessageClass':'Service',
            'MessageType':'Request',
            'SaleID':this._adyen_get_sale_id(config),
            'ServiceID':this.most_recent_service_id,
            'POIID':this.payment_method.adyen_terminal_identifier
        };
    },

    _adyen_pay_data:function(){
        varorder=this.pos.get_order();
        varconfig=this.pos.config;
        varline=order.selected_paymentline;
        vardata={
            'SaleToPOIRequest':{
                'MessageHeader':_.extend(this._adyen_common_message_header(),{
                    'MessageCategory':'Payment',
                }),
                'PaymentRequest':{
                    'SaleData':{
                        'SaleTransactionID':{
                            'TransactionID':order.uid,
                            'TimeStamp':moment().format(),//isoformat:'2018-01-10T11:30:15+00:00'
                        }
                    },
                    'PaymentTransaction':{
                        'AmountsReq':{
                            'Currency':this.pos.currency.name,
                            'RequestedAmount':line.amount,
                        }
                    }
                }
            }
        };

        if(config.adyen_ask_customer_for_tip){
            data.SaleToPOIRequest.PaymentRequest.SaleData.SaleToAcquirerData="tenderOption=AskGratuity";
        }

        returndata;
    },

    _adyen_pay:function(cid){
        varself=this;
        varorder=this.pos.get_order();

        if(order.selected_paymentline.amount<0){
            this._show_error(_t('Cannotprocesstransactionswithnegativeamount.'));
            returnPromise.resolve();
        }

        if(order===this.poll_error_order){
            deletethis.poll_error_order;
            returnself._adyen_handle_response({});
        }

        vardata=this._adyen_pay_data();
        varline=order.paymentlines.find(paymentLine=>paymentLine.cid===cid);
        line.setTerminalServiceId(this.most_recent_service_id);
        returnthis._call_adyen(data).then(function(data){
            returnself._adyen_handle_response(data);
        });
    },

    _adyen_cancel:function(ignore_error){
        varself=this;
        varconfig=this.pos.config;
        varprevious_service_id=this.most_recent_service_id;
        varheader=_.extend(this._adyen_common_message_header(),{
            'MessageCategory':'Abort',
        });

        vardata={
            'SaleToPOIRequest':{
                'MessageHeader':header,
                'AbortRequest':{
                    'AbortReason':'MerchantAbort',
                    'MessageReference':{
                        'MessageCategory':'Payment',
                        'SaleID':this._adyen_get_sale_id(config),
                        'ServiceID':previous_service_id,
                    }
                },
            }
        };

        returnthis._call_adyen(data).then(function(data){
            //Onlyvalidresponseisa200OKHTTPresponsewhichis
            //representedbytrue.
            if(!ignore_error&&data!==true){
                self._show_error(_t('Cancellingthepaymentfailed.Pleasecancelitmanuallyonthepaymentterminal.'));
                self.was_cancelled=!!self.polling;
            }
        });
    },

    _convert_receipt_info:function(output_text){
        returnoutput_text.reduce(function(acc,entry){
            varparams=newURLSearchParams(entry.Text);

            if(params.get('name')&&!params.get('value')){
                returnacc+_.str.sprintf('<br/>%s',params.get('name'));
            }elseif(params.get('name')&&params.get('value')){
                returnacc+_.str.sprintf('<br/>%s:%s',params.get('name'),params.get('value'));
            }

            returnacc;
        },'');
    },

    _poll_for_response:function(resolve,reject){
        varself=this;
        if(this.was_cancelled){
            resolve(false);
            returnPromise.resolve();
        }

        returnrpc.query({
            model:'pos.payment.method',
            method:'get_latest_adyen_status',
            args:[[this.payment_method.id],this._adyen_get_sale_id()],
        },{
            timeout:5000,
            shadow:true,
        }).catch(function(data){
            if(self.remaining_polls!=0){
                self.remaining_polls--;
            }else{
                reject();
                self.poll_error_order=self.pos.get_order();
                returnself._handle_flectra_connection_failure(data);
            }
            //Thisistomakesurethatif'data'isnotaninstanceofError(i.e.timeouterror),
            //thispromisedon'tresolve--thatis,itdoesn'tgotothe'then'clause.
            returnPromise.reject(data);
        }).then(function(status){
            varnotification=status.latest_response;
            varorder=self.pos.get_order();
            varline=self.pending_adyen_line()||resolve(false);

            if(notification&&notification.SaleToPOIResponse.MessageHeader.ServiceID==line.terminalServiceId){
                varresponse=notification.SaleToPOIResponse.PaymentResponse.Response;
                varadditional_response=newURLSearchParams(response.AdditionalResponse);

                if(response.Result=='Success'){
                    varconfig=self.pos.config;
                    varpayment_response=notification.SaleToPOIResponse.PaymentResponse;
                    varpayment_result=payment_response.PaymentResult;

                    varcashier_receipt=payment_response.PaymentReceipt.find(function(receipt){
                        returnreceipt.DocumentQualifier=='CashierReceipt';
                    });

                    if(cashier_receipt){
                        line.set_cashier_receipt(self._convert_receipt_info(cashier_receipt.OutputContent.OutputText));
                    }

                    varcustomer_receipt=payment_response.PaymentReceipt.find(function(receipt){
                        returnreceipt.DocumentQualifier=='CustomerReceipt';
                    });

                    if(customer_receipt){
                        line.set_receipt_info(self._convert_receipt_info(customer_receipt.OutputContent.OutputText));
                    }

                    vartip_amount=payment_result.AmountsResp.TipAmount;
                    if(config.adyen_ask_customer_for_tip&&tip_amount>0){
                        order.set_tip(tip_amount);
                        line.set_amount(payment_result.AmountsResp.AuthorizedAmount);
                    }

                    line.transaction_id=additional_response.get('pspReference');
                    line.card_type=additional_response.get('cardType');
                    line.cardholder_name=additional_response.get('cardHolderName')||'';
                    resolve(true);
                }else{
                    varmessage=additional_response.get('message');
                    self._show_error(_.str.sprintf(_t('MessagefromAdyen:%s'),message));

                    //thismeansthetransactionwascancelledbypressingthecancelbuttononthedevice
                    if(message.startsWith('108')){
                        resolve(false);
                    }else{
                        line.set_payment_status('retry');
                        reject();
                    }
                }
            }else{
                line.set_payment_status('waitingCard')
            }
        });
    },

    _adyen_handle_response:function(response){
        varline=this.pending_adyen_line();

        if(response.error&&response.error.status_code==401){
            this._show_error(_t('Authenticationfailed.PleasecheckyourAdyencredentials.'));
            line.set_payment_status('force_done');
            returnPromise.resolve();
        }

        response=response.SaleToPOIRequest;
        if(response&&response.EventNotification&&response.EventNotification.EventToNotify=='Reject'){
            console.error('errorfromAdyen',response);

            varmsg='';
            if(response.EventNotification){
                varparams=newURLSearchParams(response.EventNotification.EventDetails);
                msg=params.get('message');
            }

            this._show_error(_.str.sprintf(_t('Anunexpectederroroccured.MessagefromAdyen:%s'),msg));
            if(line){
                line.set_payment_status('force_done');
            }

            returnPromise.resolve();
        }else{
            line.set_payment_status('waitingCard');
            returnthis.start_get_status_polling()
        }
    },

    start_get_status_polling(){
        varself=this;
        varres=newPromise(function(resolve,reject){
            //clearpreviousintervalsjustincase,otherwise
            //it'llrunforever
            clearTimeout(self.polling);
            self._poll_for_response(resolve,reject);
            self.polling=setInterval(function(){
                self._poll_for_response(resolve,reject);
            },5500);
        });

        //makesuretostoppollingwhenwe'redone
        res.finally(function(){
            self._reset_state();
        });

        returnres;
    },

    _show_error:function(msg,title){
        if(!title){
            title= _t('AdyenError');
        }
        Gui.showPopup('ErrorPopup',{
            'title':title,
            'body':msg,
        });
    },
});

returnPaymentAdyen;
});
