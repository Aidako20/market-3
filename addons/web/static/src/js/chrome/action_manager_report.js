flectra.define('web.ReportActionManager',function(require){
"usestrict";

/**
 *ThepurposeofthisfileistoaddthesupportofFlectraactionsoftype
 *'ir.actions.report'totheActionManager.
 */

varActionManager=require('web.ActionManager');
varcore=require('web.core');
varframework=require('web.framework');
varsession=require('web.session');


var_t=core._t;
var_lt=core._lt;

//Messagesthatmightbeshowntotheuserdependeningonthestateofwkhtmltopdf
varlink='<br><br><ahref="http://wkhtmltopdf.org/"target="_blank">wkhtmltopdf.org</a>';
varWKHTMLTOPDF_MESSAGES={
    broken:_lt('YourinstallationofWkhtmltopdfseemstobebroken.Thereportwillbeshown'+
                'inhtml.')+link,
    install:_lt('UnabletofindWkhtmltopdfonthissystem.Thereportwillbeshownin'+
                 'html.')+link,
    upgrade:_lt('YoushouldupgradeyourversionofWkhtmltopdftoatleast0.12.0inorderto'+
                 'getacorrectdisplayofheadersandfootersaswellassupportfor'+
                 'table-breakingbetweenpages.')+link,
    workers:_lt('YouneedtostartFlectrawithatleasttwoworkerstoprintapdfversionof'+
                 'thereports.'),
};

ActionManager.include({
    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *DownloadsaPDFreportforthegivenurl.ItblockstheUIduringthe
     *reportgenerationanddownload.
     *
     *@param{string}url
     *@returns{Promise}resolvedwhenthereporthasbeendownloaded;
     *  rejectedifsomethingwentwrongduringthereportgeneration
     */
    _downloadReport:function(url){
        varself=this;
        framework.blockUI();
        returnnewPromise(function(resolve,reject){
            vartype='qweb-'+url.split('/')[2];
            varblocked=!session.get_file({
                url:'/report/download',
                data:{
                    data:JSON.stringify([url,type]),
                    context:JSON.stringify(session.user_context),
                },
                success:resolve,
                error:(error)=>{
                    self.call('crash_manager','rpc_error',error);
                    reject();
                },
                complete:framework.unblockUI,
            });
            if(blocked){
                //AAB:thischeckshouldbedoneinget_fileservicedirectly,
                //shouldnotbetheconcernofthecaller(andthatway,get_file
                //couldreturnapromise)
                varmessage=_t('Apopupwindowwithyourreportwasblocked.You'+
                                 'mayneedtochangeyourbrowsersettingstoallow'+
                                 'popupwindowsforthispage.');
                self.do_warn(_t('Warning'),message,true);
            }
        });
    },

    /**
     *Launchdownloadactionofthereport
     *
     *@private
     *@param{Object}actionthedescriptionoftheactiontoexecute
     *@param{Object}options@seedoActionfordetails
     *@returns{Promise}resolvedwhentheactionhasbeenexecuted
     */
    _triggerDownload:function(action,options,type){
        varself=this;
        varreportUrls=this._makeReportUrls(action);
        returnthis._downloadReport(reportUrls[type]).then(function(){
            if(action.close_on_report_download){
                varcloseAction={type:'ir.actions.act_window_close'};
                returnself.doAction(closeAction,_.pick(options,'on_close'));
            }else{
                returnoptions.on_close();
            }
        });
    },
    /**
     *Executesactionsoftype'ir.actions.report'.
     *
     *@private
     *@param{Object}actionthedescriptionoftheactiontoexecute
     *@param{Object}options@seedoActionfordetails
     *@returns{Promise}resolvedwhentheactionhasbeenexecuted
     */
    _executeReportAction:function(action,options){
        varself=this;

        if(action.report_type==='qweb-html'){
            returnthis._executeReportClientAction(action,options);
        }elseif(action.report_type==='qweb-pdf'){
            //checkthestateofwkhtmltopdfbeforeproceeding
            returnthis.call('report','checkWkhtmltopdf').then(function(state){
                //displayanotificationaccordingtowkhtmltopdf'sstate
                if(stateinWKHTMLTOPDF_MESSAGES){
                    self.do_notify(_t('Report'),WKHTMLTOPDF_MESSAGES[state],true);
                }

                if(state==='upgrade'||state==='ok'){
                    //triggerthedownloadofthePDFreport
                    returnself._triggerDownload(action,options,'pdf');
                }else{
                    //openthereportintheclientactionifgeneratingthePDFisnotpossible
                    returnself._executeReportClientAction(action,options);
                }
            });
        }elseif(action.report_type==='qweb-text'){
            returnself._triggerDownload(action,options,'text');
        }else{
            console.error("TheActionManagercan'thandlereportsoftype"+
                action.report_type,action);
            returnPromise.reject();
        }
    },
    /**
     *Executesthereportclientaction,eitherbecausethereport_typeis
     *'qweb-html',orbecausethePDFcan'tbegeneratedbywkhtmltopdf(in
     *thecaseof'qweb-pdf'reports).
     *
     *@param{Object}action
     *@param{Object}options
     *@returns{Promise}resolvedwhentheclientactionhasbeenexecuted
     */
    _executeReportClientAction:function(action,options){
        varurls=this._makeReportUrls(action);
        varclientActionOptions=_.extend({},options,{
            context:action.context,
            data:action.data,
            display_name:action.display_name,
            name:action.name,
            report_file:action.report_file,
            report_name:action.report_name,
            report_url:urls.html,
        });
        returnthis.doAction('report.client_action',clientActionOptions);
    },
    /**
     *Overridestohandlethe'ir.actions.report'actions.
     *
     *@override
     *@private
     */
    _handleAction:function(action,options){
        if(action.type==='ir.actions.report'){
            returnthis._executeReportAction(action,options);
        }
        returnthis._super.apply(this,arguments);
    },
    /**
     *Generatesanobjectcontainingthereport'surls(asvalue)forevery
     *qweb-typewesupport(askey).It'sconvenientbecausewemaywanttouse
     *anotherreport'stypeatsomepoint(forexample,when`qweb-pdf`isnot
     *available).
     *
     *@param{Object}action
     *@returns{Object}
     */
    _makeReportUrls:function(action){
        varreportUrls={
            html:'/report/html/'+action.report_name,
            pdf:'/report/pdf/'+action.report_name,
            text:'/report/text/'+action.report_name,
        };
        //Wemayhavetobuildaquerystringwith`action.data`.It'stheplace
        //werereport'susingawizardtocustomizetheoutputtraditionallyput
        //theiroptions.
        if(_.isUndefined(action.data)||_.isNull(action.data)||
            (_.isObject(action.data)&&_.isEmpty(action.data))){
            if(action.context.active_ids){
                varactiveIDsPath='/'+action.context.active_ids.join(',');
                reportUrls=_.mapObject(reportUrls,function(value){
                    returnvalue+=activeIDsPath;
                });
            }
            reportUrls.html+='?context='+encodeURIComponent(JSON.stringify(session.user_context));
        }else{
            varserializedOptionsPath='?options='+encodeURIComponent(JSON.stringify(action.data));
            serializedOptionsPath+='&context='+encodeURIComponent(JSON.stringify(action.context));
            reportUrls=_.mapObject(reportUrls,function(value){
                returnvalue+=serializedOptionsPath;
            });
        }
        returnreportUrls;
    },
});
});
