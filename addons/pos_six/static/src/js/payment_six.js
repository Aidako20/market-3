flectra.define('pos_six.payment',function(require){
"usestrict";

const{Gui}=require('point_of_sale.Gui');
varcore=require('web.core');
varPaymentInterface=require('point_of_sale.PaymentInterface');

var_t=core._t;

onTimApiReady=function(){};
onTimApiPublishLogRecord=function(record){
    //Logonlywarningorerrors
    if(record.matchesLevel(timapi.LogRecord.LogLevel.warning)){
        timapi.log(String(record));
    }
};

varPaymentSix=PaymentInterface.extend({

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@override
     */
    init:function(){
        this._super.apply(this,arguments);
        this.enable_reversals();

        varterminal_ip=this.payment_method.six_terminal_ip;
        varinstanced_payment_method=_.find(this.pos.payment_methods,function(payment_method){
            returnpayment_method.use_payment_terminal==="six"
                &&payment_method.six_terminal_ip===terminal_ip
                &&payment_method.payment_terminal
        })
        if(instanced_payment_method!==undefined){
            varpayment_terminal=instanced_payment_method.payment_terminal;
            this.terminal=payment_terminal.terminal;
            this.terminalListener=payment_terminal.terminalListener;
            return;
        }

        varsettings=newtimapi.TerminalSettings();
        settings.connectionMode=timapi.constants.ConnectionMode.onFixIp;
        settings.connectionIPString=this.payment_method.six_terminal_ip;
        settings.connectionIPPort="80";
        settings.integratorId="175d97a0-2a88-4413-b920-e90037b582ac";
        settings.dcc=false;

        this.terminal=newtimapi.Terminal(settings);
        this.terminal.setPosId(this.pos.pos_session.name);
        this.terminal.setUserId(this.pos.pos_session.user_id[0]);

        this.terminalListener=newtimapi.DefaultTerminalListener();
        this.terminalListener.transactionCompleted=this._onTransactionComplete.bind(this);
        this.terminalListener.balanceCompleted=this._onBalanceComplete.bind(this);
        this.terminal.addListener(this.terminalListener);

        varrecipients=[timapi.constants.Recipient.merchant,timapi.constants.Recipient.cardholder];
        varoptions=[];
        _.forEach(recipients,(recipient)=>{
            varoption=newtimapi.PrintOption(
                recipient,
                timapi.constants.PrintFormat.normal,
                45,
                [timapi.constants.PrintFlag.suppressHeader,timapi.constants.PrintFlag.suppressEcrInfo]
            );
            options.push(option);
        });
        this.terminal.setPrintOptions(options);
    },

    /**
     *@override
     */
    send_payment_cancel:function(){
        this._super.apply(this,arguments);
        this.terminal.cancel();
        returnPromise.resolve();
    },

    /**
     *@override
     */
    send_payment_request:function(){
        this._super.apply(this,arguments);
        this.pos.get_order().selected_paymentline.set_payment_status('waitingCard');
        returnthis._sendTransaction(timapi.constants.TransactionType.purchase);
    },

    /**
     *@override
     */
    send_payment_reversal:function(){
        this._super.apply(this,arguments);
        this.pos.get_order().selected_paymentline.set_payment_status('reversing');
        returnthis._sendTransaction(timapi.constants.TransactionType.reversal);
    },

    send_balance:function(){
        this.terminal.balanceAsync();
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    _onTransactionComplete:function(event,data){
        timapi.DefaultTerminalListener.prototype.transactionCompleted(event,data);

        if(event.exception){
            if(event.exception.resultCode!==timapi.constants.ResultCode.apiCancelEcr){
                Gui.showPopup('ErrorPopup',{
                    title:_t('Transactionwasnotprocessedcorrectly'),
                    body:event.exception.errorText,
                });
            }

            this.transactionResolve();
        }else{
            if(data.printData){
                this._printReceipts(data.printData.receipts)
            }

            //StoreTransactionData
            vartransactionData=newtimapi.TransactionData();
            transactionData.transSeq=data.transactionInformation.transSeq;
            this.terminal.setTransactionData(transactionData);

            this.transactionResolve(true);
        }
    },

    _onBalanceComplete:function(event,data){
        if(event.exception){
            Gui.showPopup('ErrorPopup',{
                'title':_t('BalanceFailed'),
                'body': _t('Thebalanceoperationfailed.'),
            });
        }else{
            this._printReceipts(data.printData.receipts);
        }
    },

    _printReceipts:function(receipts){
        _.forEach(receipts,(receipt)=>{
            varvalue=receipt.value.replace(/\n/g,"<br/>");
            if(receipt.recipient===timapi.constants.Recipient.merchant&&this.pos.proxy.printer){
                this.pos.proxy.printer.print_receipt(
                    "<divclass='pos-receipt'><divclass='pos-payment-terminal-receipt'>"+
                        value+
                    "</div></div>"
                );
            }elseif(receipt.recipient===timapi.constants.Recipient.cardholder){
                this.pos.get_order().selected_paymentline.set_receipt_info(value);
            }
        });
    },

    _sendTransaction:function(transactionType){
        varamount=newtimapi.Amount(
            Math.round(this.pos.get_order().selected_paymentline.amount/this.pos.currency.rounding),
            timapi.constants.Currency[this.pos.currency.name],
            this.pos.currency.decimals
        );

        returnnewPromise((resolve)=>{
            this.transactionResolve=resolve;
            this.terminal.transactionAsync(transactionType,amount);
        });
    },
});

returnPaymentSix;

});
