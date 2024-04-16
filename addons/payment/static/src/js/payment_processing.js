flectra.define('payment.processing',function(require){
    'usestrict';

    varpublicWidget=require('web.public.widget');
    varajax=require('web.ajax');
    varcore=require('web.core');

    var_t=core._t;

    $.blockUI.defaults.css.border='0';
    $.blockUI.defaults.css["background-color"]='';
    $.blockUI.defaults.overlayCSS["opacity"]='0.9';

    publicWidget.registry.PaymentProcessing=publicWidget.Widget.extend({
        selector:'.o_payment_processing',
        xmlDependencies:['/payment/static/src/xml/payment_processing.xml'],

        _pollCount:0,

        start:function(){
            this.displayLoading();
            this.poll();
            returnthis._super.apply(this,arguments);
        },
        /*Methods*/
        startPolling:function(){
            vartimeout=3000;
            //
            if(this._pollCount>=10&&this._pollCount<20){
                timeout=10000;
            }
            elseif(this._pollCount>=20){
                timeout=30000;
            }
            //
            setTimeout(this.poll.bind(this),timeout);
            this._pollCount++;
        },
        poll:function(){
            varself=this;
            ajax.jsonRpc('/payment/process/poll','call',{}).then(function(data){
                if(data.success===true){
                    self.processPolledData(data.transactions);
                }
                else{
                    switch(data.error){
                    case"tx_process_retry":
                        break;
                    case"no_tx_found":
                        self.displayContent("payment.no_tx_found",{});
                        break;
                    default://ifanexceptionisraised
                        self.displayContent("payment.exception",{exception_msg:data.error});
                        break;
                    }
                }
                self.startPolling();

            }).guardedCatch(function(){
                self.displayContent("payment.rpc_error",{});
                self.startPolling();
            });
        },
        processPolledData:function(transactions){
            varrender_values={
                'tx_draft':[],
                'tx_pending':[],
                'tx_authorized':[],
                'tx_done':[],
                'tx_cancel':[],
                'tx_error':[],
            };

            if(transactions.length>0&&['transfer','sepa_direct_debit'].indexOf(transactions[0].acquirer_provider)>=0){
                window.location=transactions[0].return_url;
                return;
            }

            //groupthetransactionaccordingtotheirstate
            transactions.forEach(function(tx){
                varkey='tx_'+tx.state;
                if(keyinrender_values){
                    render_values[key].push(tx);
                }
            });

            functioncountTxInState(states){
                varnbTx=0;
                for(varpropinrender_values){
                    if(states.indexOf(prop)>-1&&render_values.hasOwnProperty(prop)){
                        nbTx+=render_values[prop].length;
                    }
                }
                returnnbTx;
            }
                       
            /*
            *Whentheserversendsthelistofmonitoredtransactions,ittriestopost-process
            *allthesuccessfulones.Ifitsucceedsorifthepost-processhasalreadybeenmade,
            *thetransactionisremovedfromthelistofmonitoredtransactionsandwon'tbe
            *includedinthenextresponse.Weassumethatsuccessfulandpost-process
            *transactionsshouldalwaysprevailonothers,regardlessoftheirnumberorstate.
            */
            if(render_values['tx_done'].length===1&&
                render_values['tx_done'][0].is_processed){
                    window.location=render_values['tx_done'][0].return_url;
                    return;
            }
            //Iftherearemultipletransactionsmonitored,displaythemalltothecustomer.If
            //thereisonlyonetransactionmonitored,redirectdirectlythecustomertothe
            //landingroute.
            if(countTxInState(['tx_done','tx_error','tx_pending','tx_authorized'])===1){
                //Wedon'twanttoredirectcustomerstothelandingpagewhentheyhaveapending
                //transaction.Thesuccessfultransactionsaredealtwithbefore.
                vartx=render_values['tx_authorized'][0]||render_values['tx_error'][0];
                if(tx){
                    window.location=tx.return_url;
                    return;
                }
            }

            this.displayContent("payment.display_tx_list",render_values);
        },
        displayContent:function(xmlid,render_values){
            varhtml=core.qweb.render(xmlid,render_values);
            $.unblockUI();
            this.$el.find('.o_payment_processing_content').html(html);
        },
        displayLoading:function(){
            varmsg=_t("Weareprocessingyourpayment,pleasewait...");
            $.blockUI({
                'message':'<h2class="text-white"><imgsrc="/web/static/src/img/spin.png"class="fa-pulse"/>'+
                    '   <br/>'+msg+
                    '</h2>'
            });
        },
    });
});
