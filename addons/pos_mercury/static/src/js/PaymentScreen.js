flectra.define('pos_mercury.PaymentScreen',function(require){
    'usestrict';

    const{_t}=require('web.core');
    constPaymentScreen=require('point_of_sale.PaymentScreen');
    constRegistries=require('point_of_sale.Registries');
    constNumberBuffer=require('point_of_sale.NumberBuffer');
    const{useBarcodeReader}=require('point_of_sale.custom_hooks');

    //Lookuptabletostorestatusanderrormessages
    constlookUpCodeTransaction={
        Approved:{
            '000000':_t('Transactionapproved'),
        },
        TimeoutError:{
            '001006':'GlobalAPINotInitialized',
            '001007':'TimeoutonResponse',
            '003003':'SocketErrorsendingrequest',
            '003004':'Socketalreadyopenorinuse',
            '003005':'SocketCreationFailed',
            '003006':'SocketConnectionFailed',
            '003007':'ConnectionLost',
            '003008':'TCP/IPFailedtoInitialize',
            '003010':'TimeOutwaitingforserverresponse',
            '003011':'ConnectCanceled',
            '003053':'InitializeFailed',
            '009999':'UnknownError',
        },
        FatalError:{
            '-1':'Timeouterror',
            '001001':'GeneralFailure',
            '001003':'InvalidCommandFormat',
            '001004':'InsufficientFields',
            '001011':'EmptyCommandString',
            '002000':'PasswordVerified',
            '002001':'QueueFull',
            '002002':'PasswordFailed–Disconnecting',
            '002003':'SystemGoingOffline',
            '002004':'DisconnectingSocket',
            '002006':'Refused‘MaxConnections’',
            '002008':'DuplicateSerialNumberDetected',
            '002009':'PasswordFailed(Client/Server)',
            '002010':'Passwordfailed(Challenge/Response)',
            '002011':'InternalServerError–CallProvider',
            '003002':'InProcesswithserver',
            '003009':'Controlfailedtofindbrandedserial(passwordlookupfailed)',
            '003012':'128bitCryptoAPIfailed',
            '003014':'ThreadedAuthStartedExpectResponse',
            '003017':'FailedtostartEventThread.',
            '003050':'XMLParseError',
            '003051':'AllConnectionsFailed',
            '003052':'ServerLoginFailed',
            '004001':'GlobalResponseLengthError(TooShort)',
            '004002':'UnabletoParseResponsefromGlobal(Indistinguishable)',
            '004003':'GlobalStringError',
            '004004':'WeakEncryptionRequestNotSupported',
            '004005':'ClearTextRequestNotSupported',
            '004010':'UnrecognizedRequestFormat',
            '004011':'ErrorOccurredWhileDecryptingRequest',
            '004017':'InvalidCheckDigit',
            '004018':'MerchantIDMissing',
            '004019':'TStreamTypeMissing',
            '004020':'CouldNotEncryptResponse-CallProvider',
            '100201':'InvalidTransactionType',
            '100202':'InvalidOperatorID',
            '100203':'InvalidMemo',
            '100204':'InvalidAccountNumber',
            '100205':'InvalidExpirationDate',
            '100206':'InvalidAuthorizationCode',
            '100207':'InvalidAuthorizationCode',
            '100208':'InvalidAuthorizationAmount',
            '100209':'InvalidCashBackAmount',
            '100210':'InvalidGratuityAmount',
            '100211':'InvalidPurchaseAmount',
            '100212':'InvalidMagneticStripeData',
            '100213':'InvalidPINBlockData',
            '100214':'InvalidDerivedKeyData',
            '100215':'InvalidStateCode',
            '100216':'InvalidDateofBirth',
            '100217':'InvalidCheckType',
            '100218':'InvalidRoutingNumber',
            '100219':'InvalidTranCode',
            '100220':'InvalidMerchantID',
            '100221':'InvalidTStreamType',
            '100222':'InvalidBatchNumber',
            '100223':'InvalidBatchItemCount',
            '100224':'InvalidMICRInputType',
            '100225':'InvalidDriver’sLicense',
            '100226':'InvalidSequenceNumber',
            '100227':'InvalidPassData',
            '100228':'InvalidCardType',
        },
    };

    constPosMercuryPaymentScreen=(PaymentScreen)=>
        classextendsPaymentScreen{
            constructor(){
                super(...arguments);
                if(this.env.pos.getOnlinePaymentMethods().length!==0){
                    useBarcodeReader({
                        credit:this.credit_code_action,
                    });
                }
                //Howlongwewaitfortheflectraservertodelivertheresponseof
                //aVantivtransaction
                this.server_timeout_in_ms=95000;

                //HowmanyVantivtransactionswesendwithoutreceivinga
                //response
                this.server_retries=3;
            }

            /**
             *Thecardreaderactsasabarcodescanner.Thissetsup
             *theNumberBuffertonotimmediatelyactonkeyboard
             *input.
             *
             *@override
             */
            get_getNumberBufferConfig(){
                constres=super._getNumberBufferConfig;
                res['useWithBarcode']=true;
                returnres;
            }

            /**
             *Finishanypendinginputbeforetryingtovalidate.
             *
             *@override
             */
            asyncvalidateOrder(isForceValidate){
                NumberBuffer.capture();
                returnsuper.validateOrder(...arguments);
            }

            _get_swipe_pending_line(){
                vari=0;
                varlines=this.env.pos.get_order().get_paymentlines();

                for(i=0;i<lines.length;i++){
                    if(lines[i].mercury_swipe_pending){
                        returnlines[i];
                    }
                }

                return0;
            }

            _does_credit_payment_line_exist(amount,card_number,card_brand,card_owner_name){
                vari=0;
                varlines=this.env.pos.get_order().get_paymentlines();

                for(i=0;i<lines.length;i++){
                    if(
                        lines[i].mercury_amount===amount&&
                        lines[i].mercury_card_number===card_number&&
                        lines[i].mercury_card_brand===card_brand&&
                        lines[i].mercury_card_owner_name===card_owner_name
                    ){
                        returntrue;
                    }
                }

                returnfalse;
            }

            retry_mercury_transaction(
                def,
                response,
                retry_nr,
                can_connect_to_server,
                callback,
                args
            ){
                varself=this;
                varmessage='';

                if(retry_nr<self.server_retries){
                    if(response){
                        message='Retry#'+(retry_nr+1)+'...<br/><br/>'+response.message;
                    }else{
                        message='Retry#'+(retry_nr+1)+'...';
                    }
                    def.notify({
                        message:message,
                    });

                    setTimeout(function(){
                        callback.apply(self,args);
                    },1000);
                }else{
                    if(response){
                        message=
                            'Error'+
                            response.error+
                            ':'+
                            lookUpCodeTransaction['TimeoutError'][response.error]+
                            '<br/>'+
                            response.message;
                    }else{
                        if(can_connect_to_server){
                            message=self.env._t('NoresponsefromVantiv(Vantivdown?)');
                        }else{
                            message=self.env._t(
                                'Noresponsefromserver(connectedtonetwork?)'
                            );
                        }
                    }
                    def.resolve({
                        message:message,
                        auto_close:false,
                    });
                }
            }

            //Handlertomanagethecardreaderstring
            credit_code_transaction(parsed_result,old_deferred,retry_nr){
                varorder=this.env.pos.get_order();
                if(order.get_due(order.selected_paymentline)<0){
                    this.showPopup('ErrorPopup',{
                        title:this.env._t('Refundsnotsupported'),
                        body:this.env._t(
                            "Creditcardrefundsarenotsupported.Insteadselectyourcreditcardpaymentmethod,click'Validate'andrefundtheoriginalchargemanuallythroughtheVantivbackend."
                        ),
                    });
                    return;
                }

                if(this.env.pos.getOnlinePaymentMethods().length===0){
                    return;
                }

                varself=this;
                vardecodedMagtek=self.env.pos.decodeMagtek(parsed_result.code);

                if(!decodedMagtek){
                    this.showPopup('ErrorPopup',{
                        title:this.env._t('Couldnotreadcard'),
                        body:this.env._t(
                            'ThiscanbecausedbyabadlyexecutedswipeorbynothavingyourkeyboardlayoutsettoUSQWERTY(notUSInternational).'
                        ),
                    });
                    return;
                }

                varswipe_pending_line=self._get_swipe_pending_line();
                varpurchase_amount=0;

                if(swipe_pending_line){
                    purchase_amount=swipe_pending_line.get_amount();
                }else{
                    purchase_amount=self.env.pos.get_order().get_due();
                }

                vartransaction={
                    encrypted_key:decodedMagtek['encrypted_key'],
                    encrypted_block:decodedMagtek['encrypted_block'],
                    transaction_type:'Credit',
                    transaction_code:'Sale',
                    invoice_no:self.env.pos.get_order().uid.replace(/-/g,''),
                    purchase:purchase_amount,
                    payment_method_id:parsed_result.payment_method_id,
                };

                vardef=old_deferred||new$.Deferred();
                retry_nr=retry_nr||0;

                //showthetransactionpopup.
                //thetransactiondeferredisusedtoupdatetransactionstatus
                //ifwehaveapreviousdeferreditindicatesthatthisisaretry
                if(!old_deferred){
                    self.showPopup('PaymentTransactionPopup',{
                        transaction:def,
                    });
                    def.notify({
                        message:this.env._t('Handlingtransaction...'),
                    });
                }

                this.rpc(
                    {
                        model:'pos_mercury.mercury_transaction',
                        method:'do_payment',
                        args:[transaction],
                    },
                    {
                        timeout:self.server_timeout_in_ms,
                    }
                )
                    .then(function(data){
                        //ifnotreceivingaresponsefromVantiv,weshouldretry
                        if(data==='timeout'){
                            self.retry_mercury_transaction(
                                def,
                                null,
                                retry_nr,
                                true,
                                self.credit_code_transaction,
                                [parsed_result,def,retry_nr+1]
                            );
                            return;
                        }

                        if(data==='notsetup'){
                            def.resolve({
                                message:self.env._t('PleasesetupyourVantivmerchantaccount.'),
                            });
                            return;
                        }

                        if(data==='internalerror'){
                            def.resolve({
                                message:self.env._t('Flectraerrorwhileprocessingtransaction.'),
                            });
                            return;
                        }

                        varresponse=self.env.pos.decodeMercuryResponse(data);
                        response.payment_method_id=parsed_result.payment_method_id;

                        if(response.status==='Approved'){
                            //AP*indicatesaduplicaterequest,sodon'taddanythingforthose
                            if(
                                response.message==='AP*'&&
                                self._does_credit_payment_line_exist(
                                    response.authorize,
                                    decodedMagtek['number'],
                                    response.card_type,
                                    decodedMagtek['name']
                                )
                            ){
                                def.resolve({
                                    message:lookUpCodeTransaction['Approved'][response.error],
                                    auto_close:true,
                                });
                            }else{
                                //Ifthepaymentisapproved,addapaymentline
                                varorder=self.env.pos.get_order();

                                if(swipe_pending_line){
                                    order.select_paymentline(swipe_pending_line);
                                }else{
                                    order.add_paymentline(
                                        self.payment_methods_by_id[parsed_result.payment_method_id]
                                    );
                                }

                                order.selected_paymentline.paid=true;
                                order.selected_paymentline.mercury_swipe_pending=false;
                                order.selected_paymentline.mercury_amount=response.authorize;
                                order.selected_paymentline.set_amount(response.authorize);
                                order.selected_paymentline.mercury_card_number=
                                    decodedMagtek['number'];
                                order.selected_paymentline.mercury_card_brand=response.card_type;
                                order.selected_paymentline.mercury_card_owner_name=
                                    decodedMagtek['name'];
                                order.selected_paymentline.mercury_ref_no=response.ref_no;
                                order.selected_paymentline.mercury_record_no=response.record_no;
                                order.selected_paymentline.mercury_invoice_no=response.invoice_no;
                                order.selected_paymentline.mercury_auth_code=response.auth_code;
                                order.selected_paymentline.mercury_data=response;//usedtoreversetransactions
                                order.selected_paymentline.set_credit_card_name();

                                NumberBuffer.reset();
                                order.trigger('change',order);//neededsothatexport_to_JSONgetstriggered
                                self.render();

                                if(response.message==='PARTIALAP'){
                                    def.resolve({
                                        message:self.env._t('Partiallyapproved'),
                                        auto_close:false,
                                    });
                                }else{
                                    def.resolve({
                                        message:lookUpCodeTransaction['Approved'][response.error],
                                        auto_close:true,
                                    });
                                }
                            }
                        }

                        //ifanerrorrelatedtotimeoutorconnectivityissuesarised,thenretrythesametransaction
                        else{
                            if(lookUpCodeTransaction['TimeoutError'][response.error]){
                                //recoverableerror
                                self.retry_mercury_transaction(
                                    def,
                                    response,
                                    retry_nr,
                                    true,
                                    self.credit_code_transaction,
                                    [parsed_result,def,retry_nr+1]
                                );
                            }else{
                                //notrecoverable
                                def.resolve({
                                    message:
                                        'Error'+response.error+':<br/>'+response.message,
                                    auto_close:false,
                                });
                            }
                        }
                    })
                    .catch(function(){
                        self.retry_mercury_transaction(
                            def,
                            null,
                            retry_nr,
                            false,
                            self.credit_code_transaction,
                            [parsed_result,def,retry_nr+1]
                        );
                    });
            }

            credit_code_cancel(){
                return;
            }

            credit_code_action(parsed_result){
                varonline_payment_methods=this.env.pos.getOnlinePaymentMethods();

                if(online_payment_methods.length===1){
                    parsed_result.payment_method_id=online_payment_methods[0].item;
                    this.credit_code_transaction(parsed_result);
                }else{
                    //thisisforsupportinganotherpaymentsystemlikemercury
                    constselectionList=online_payment_methods.map((paymentMethod)=>({
                        id:paymentMethod.item,
                        label:paymentMethod.label,
                        isSelected:false,
                        item:paymentMethod.item,
                    }));
                    this.showPopup('SelectionPopup',{
                        title:this.env._t('Paywith:'),
                        list:selectionList,
                    }).then(({confirmed,payload:selectedPaymentMethod})=>{
                        if(confirmed){
                            parsed_result.payment_method_id=selectedPaymentMethod;
                            this.credit_code_transaction(parsed_result);
                        }else{
                            this.credit_code_cancel();
                        }
                    });
                }
            }

            remove_paymentline_by_ref(line){
                this.env.pos.get_order().remove_paymentline(line);
                NumberBuffer.reset();
                this.render();
            }

            do_reversal(line,is_voidsale,old_deferred,retry_nr){
                vardef=old_deferred||new$.Deferred();
                varself=this;
                retry_nr=retry_nr||0;

                //showthetransactionpopup.
                //thetransactiondeferredisusedtoupdatetransactionstatus
                this.showPopup('PaymentTransactionPopup',{
                    transaction:def,
                });

                varrequest_data=_.extend(
                    {
                        transaction_type:'Credit',
                        transaction_code:'VoidSaleByRecordNo',
                    },
                    line.mercury_data
                );

                varmessage='';
                varrpc_method='';

                if(is_voidsale){
                    message=this.env._t('Reversalfailed,sendingVoidSale...');
                    rpc_method='do_voidsale';
                }else{
                    message=this.env._t('Sendingreversal...');
                    rpc_method='do_reversal';
                }

                if(!old_deferred){
                    def.notify({
                        message:message,
                    });
                }

                this.rpc(
                    {
                        model:'pos_mercury.mercury_transaction',
                        method:rpc_method,
                        args:[request_data],
                    },
                    {
                        timeout:self.server_timeout_in_ms,
                    }
                )
                    .then(function(data){
                        if(data==='timeout'){
                            self.retry_mercury_transaction(
                                def,
                                null,
                                retry_nr,
                                true,
                                self.do_reversal,
                                [line,is_voidsale,def,retry_nr+1]
                            );
                            return;
                        }

                        if(data==='internalerror'){
                            def.resolve({
                                message:self.env._t('Flectraerrorwhileprocessingtransaction.'),
                            });
                            return;
                        }

                        varresponse=self.env.pos.decodeMercuryResponse(data);

                        if(!is_voidsale){
                            if(response.status!='Approved'||response.message!='REVERSED'){
                                //reversalwasnotsuccessful,sendvoidsale
                                self.do_reversal(line,true);
                            }else{
                                //reversalwassuccessful
                                def.resolve({
                                    message:self.env._t('Reversalsucceeded'),
                                });

                                self.remove_paymentline_by_ref(line);
                            }
                        }else{
                            //voidsaleended,nothingmorewecando
                            if(response.status==='Approved'){
                                def.resolve({
                                    message:self.env._t('VoidSalesucceeded'),
                                });

                                self.remove_paymentline_by_ref(line);
                            }else{
                                def.resolve({
                                    message:
                                        'Error'+response.error+':<br/>'+response.message,
                                });
                            }
                        }
                    })
                    .catch(function(){
                        self.retry_mercury_transaction(
                            def,
                            null,
                            retry_nr,
                            false,
                            self.do_reversal,
                            [line,is_voidsale,def,retry_nr+1]
                        );
                    });
            }

            /**
             *@override
             */
            deletePaymentLine(event){
                const{cid}=event.detail;
                constline=this.paymentLines.find((line)=>line.cid===cid);
                if(line.mercury_data){
                    this.do_reversal(line,false);
                }else{
                    super.deletePaymentLine(event);
                }
            }

            /**
             *@override
             */
            addNewPaymentLine({detail:paymentMethod}){
                constorder=this.env.pos.get_order();
                constres=super.addNewPaymentLine(...arguments);
                if(res&&paymentMethod.pos_mercury_config_id){
                    order.selected_paymentline.mercury_swipe_pending=true;
                    order.trigger('change',order);
                    this.render();
                }
            }
        };

    Registries.Component.extend(PaymentScreen,PosMercuryPaymentScreen);

    returnPaymentScreen;
});
