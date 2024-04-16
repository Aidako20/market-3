flectra.define('web.ErrorDialogRegistry',function(require){
"usestrict";

varRegistry=require('web.Registry');

returnnewRegistry();
});

flectra.define('web.CrashManager',function(require){
"usestrict";

constAbstractService=require('web.AbstractService');
varajax=require('web.ajax');
constBrowserDetection=require('web.BrowserDetection');
constconfig=require("web.config");
varcore=require('web.core');
varDialog=require('web.Dialog');
varErrorDialogRegistry=require('web.ErrorDialogRegistry');
constsession=require('web.session');
varWidget=require('web.Widget');

var_t=core._t;
var_lt=core._lt;

//Registerthiseventlistenerbeforequnitdoes.
//Someerrorsneedstobenegatedbythecrash_manager.
window.addEventListener('unhandledrejection',ev=>
    core.bus.trigger('crash_manager_unhandledrejection',ev)
);

letactive=true;

/**
 *AnextensionofDialogWidgettorenderthewarningsanderrorsonthewebsite.
 *ExtenditwithyourtemplateofchoicelikeErrorDialog/WarningDialog
 */
varCrashManagerDialog=Dialog.extend({
    xmlDependencies:(Dialog.prototype.xmlDependencies||[]).concat(
        ['/web/static/src/xml/crash_manager.xml']
    ),

    /**
     *@param{Object}error
     *@param{string}error.message   themessageinWarning/ErrorDialog
     *@param{string}error.traceback thetracebackinErrorDialog
     *
     *@constructor
     */
    init:function(parent,options,error){
        this._super.apply(this,[parent,options]);
        this.message=error.message;
        this.traceback=error.traceback;
        core.bus.off('close_dialogs',this);
    },
});

varErrorDialog=CrashManagerDialog.extend({
    template:'CrashManager.error',
});

varWarningDialog=CrashManagerDialog.extend({
    template:'CrashManager.warning',

    /**
     *Setssizetomediumbydefault.
     *
     *@override
     */
    init:function(parent,options,error){
        this._super(parent,_.extend({
            size:'medium',
       },options),error);
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *Focusestheokbutton.
     *
     *@override
     */
    open:function(){
        this._super({shouldFocusButtons:true});
    },
});

varCrashManager=AbstractService.extend({
    init:function(){
        varself=this;
        active=true;
        this.isConnected=true;
        this.flectraExceptionTitleMap={
            'flectra.addons.base.models.ir_mail_server.MailDeliveryException':_lt("MailDeliveryException"),
            'flectra.exceptions.AccessDenied':_lt("AccessDenied"),
            'flectra.exceptions.AccessError':_lt("AccessError"),
            'flectra.exceptions.MissingError':_lt("MissingRecord"),
            'flectra.exceptions.UserError':_lt("UserError"),
            'flectra.exceptions.ValidationError':_lt("ValidationError"),
            'flectra.exceptions.Warning':_lt("Warning"),
        };

        this.browserDetection=newBrowserDetection();
        this._super.apply(this,arguments);

        //crashmanagerintegration
        core.bus.on('rpc_error',this,this.rpc_error);
        window.onerror=function(message,file,line,col,error){
            //ScriptsinjectedinDOM(eg:googleAPI'sjsfiles)won'treturnacleanerroronwindow.onerror.
            //Thebrowserwilljustgiveyoua'Scripterror.'asmessageandnothingelseforsecurityissue.
            //ToenableonerrortoworkproperlywithCORSfile,youshould:
            //  1.addcrossorigin="anonymous"toyour<script>tagloadingthefile
            //  2.enabling'Access-Control-Allow-Origin'ontheserverservingthefile.
            //Sinceinsomecaseitwontbepossibletotothis,thishandleshouldhavethepossibilitytobe
            //handledbythescriptmanipulatingtheinjectedfile.Forthis,youwillusewindow.onOriginError
            //Ifitisnothandled,weshoulddisplaysomethingclearerthanthecommoncrash_managererrordialog
            //sinceitwon'tshowanythingexcept"Scripterror."
            //Thislinkwillprobablyexplainitbetter:https://blog.sentry.io/2016/05/17/what-is-script-error.html
            if(!file&&!line&&!col){
                //ChromeandOperaset"Scripterror."onthe`message`andhidethe`error`
                //Firefoxhandlesthe"Scripterror."directly.ItsetstheerrorthrownbytheCORSfileinto`error`
                if(window.onOriginError){
                    window.onOriginError();
                    deletewindow.onOriginError;
                }else{
                    //InSafari16.4+(asofJun14th2023),anerroroccurs
                    //whengoingbackandforwardthroughthebrowserwhenthe
                    //cacheisenabled.Afeedbackhasbeenreportedbutinthe
                    //meantime,hideanyscripterrorintheseversions.
                    if(
                        config.device.isIOS
                        &&message==="Scripterror."
                        &&session.is_frontend
                        &&flectra.debug!=="assets"
                    ){
                        return;
                    }
                    self.show_error({
                        type:_t("FlectraClientError"),
                        message:_t("UnknownCORSerror"),
                        data:{debug:_t("AnunknownCORSerroroccured.TheerrorprobablyoriginatesfromaJavaScriptfileservedfromadifferentorigin.(Openingyourbrowserconsolemightgiveyouahintontheerror.)")},
                    });
                }
            }else{
                //ignoreChromevideointernalerror:https://crbug.com/809574
                if(!error&&message==='ResizeObserverlooplimitexceeded'){
                    return;
                }
                vartraceback=error?error.stack:'';
                self.show_error({
                    type:_t("FlectraClientError"),
                    message:message,
                    data:{debug:file+':'+line+"\n"+_t('Traceback:')+"\n"+traceback},
                });
            }
        };

        //listentounhandledrejectedpromises,andthrowanerrorwhenthe
        //promisehasbeenrejectedduetoacrash
        core.bus.on('crash_manager_unhandledrejection',this,function(ev){
            if(ev.reason&&ev.reasoninstanceofError){
                //Error.prototype.stackisnon-standard.
                //https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Error
                //However,mostenginesprovideanimplementation.
                //Inparticular,ChromeformatsthecontentsofError.stack
                //https://v8.dev/docs/stack-trace-api#compatibility
                lettraceback;
                if(self.browserDetection.isBrowserChrome()){
                    traceback=ev.reason.stack;
                }else{
                    traceback=`${_t("Error:")}${ev.reason.message}\n${ev.reason.stack}`;
                }
                self.show_error({
                    type:_t("FlectraClientError"),
                    message:'',
                    data:{debug:_t('Traceback:')+"\n"+traceback},
                });
            }else{
                //therejectionisnotduetoanError,sopreventthebrowser
                //fromdisplayingan'unhandledrejection'errorintheconsole
                ev.stopPropagation();
                ev.stopImmediatePropagation();
                ev.preventDefault();
            }
        });
    },
    enable:function(){
        active=true;
    },
    disable:function(){
        active=false;
    },
    handleLostConnection:function(){
        varself=this;
        if(!this.isConnected){
            //alreadyhandled,nothingtodo. Thiscanhappenwhenseveral
            //rpcsaredoneinparallelandfailbecauseofalostconnection.
            return;
        }
        this.isConnected=false;
        vardelay=2000;
        core.bus.trigger('connection_lost');

        setTimeout(functioncheckConnection(){
            ajax.jsonRpc('/web/webclient/version_info','call',{},{shadow:true}).then(function(){
                core.bus.trigger('connection_restored');
                self.isConnected=true;
            }).guardedCatch(function(){
                //exponentialbackoff,withsomejitter
                delay=(delay*1.5)+500*Math.random();
                setTimeout(checkConnection,delay);
            });
        },delay);
    },
    rpc_error:function(error){
        //SomequnittestsproduceserrorsbeforetheDOMisset.
        //Thisproducesanerrorloopasthemodal/toasthasnoDOMtoattachto.
        if(!document.body||!active||this.connection_lost)return;

        //Connectionlosterror
        if(error.code===-32098){
            this.handleLostConnection();
            return;
        }

        //Specialexceptionhandlers,seecrash_registrybellow
        varhandler=core.crash_registry.get(error.data.name,true);
        if(handler){
            new(handler)(this,error).display();
            return;
        }

        //Flectracustomexception:UserError,AccessError,...
        if(_.has(this.flectraExceptionTitleMap,error.data.name)){
            error=_.extend({},error,{
                data:_.extend({},error.data,{
                    message:error.data.arguments[0],
                    title:this.flectraExceptionTitleMap[error.data.name],
                }),
            });
            this.show_warning(error);
            return;
        }

        //AnyotherPythonexception
        this.show_error(error);
    },
    show_warning:function(error,options){
        if(!active){
            return;
        }
        varmessage=error.data?error.data.message:error.message;
        vartitle=_t("Somethingwentwrong!");
        if(error.type){
            title=_.str.capitalize(error.type);
        }elseif(error.data&&error.data.title){
            title=_.str.capitalize(error.data.title);
        }
        returnthis._displayWarning(message,title,options);
    },
    show_error:function(error){
        if(!active){
            return;
        }
        error.traceback=error.data.debug;
        vardialogClass=error.data.context&&ErrorDialogRegistry.get(error.data.context.exception_class)||ErrorDialog;
        vardialog=newdialogClass(this,{
            title:_.str.capitalize(error.type)||_t("FlectraError"),
        },error);


        //Whenthedialogopens,initializethecopyfeatureanddestroyitwhenthedialogisclosed
        var$clipboardBtn;
        varclipboard;
        dialog.opened(function(){
            //Whenthefulltracebackisshown,scrollittotheend(usefulforbetterpythonerrorreporting)
            dialog.$(".o_error_detail").on("shown.bs.collapse",function(e){
                e.target.scrollTop=e.target.scrollHeight;
            });

            $clipboardBtn=dialog.$(".o_clipboard_button");
            $clipboardBtn.tooltip({title:_t("Copied!"),trigger:"manual",placement:"left"});
            clipboard=newwindow.ClipboardJS($clipboardBtn[0],{
                text:function(){
                    return(_t("Error")+":\n"+error.message+"\n\n"+error.data.debug).trim();
                },
                //ContaineraddedbecauseofBootstrapmodalthatgivethefocustoanotherelement.
                //WeneedtogivetocorrectfocustoClipboardJS(seeinClipboardJSdoc)
                //https://github.com/zenorocha/clipboard.js/issues/155
                container:dialog.el,
            });
            clipboard.on("success",function(e){
                _.defer(function(){
                    $clipboardBtn.tooltip("show");
                    _.delay(function(){
                        $clipboardBtn.tooltip("hide");
                    },800);
                });
            });
        });
        dialog.on("closed",this,function(){
            $clipboardBtn.tooltip('dispose');
            clipboard.destroy();
        });

        returndialog.open();
    },
    show_message:function(exception){
        returnthis.show_error({
            type:_t("FlectraClientError"),
            message:exception,
            data:{debug:""}
        });
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{string}message
     *@param{string}title
     *@param{Object}options
     */
    _displayWarning:function(message,title,options){
        returnnewWarningDialog(this,Object.assign({},options,{
            title,
        }),{
            message,
        }).open();
    },
});

/**
 *Aninterfacetoimplementtohandleexceptions.Registerimplementationininstance.web.crash_manager_registry.
*/
varExceptionHandler={
    /**
     *@paramparentTheparent.
     *@paramerrorTheerrorobjectasreturnedbytheJSON-RPCimplementation.
     */
    init:function(parent,error){},
    /**
     *Calledtoinformtodisplaythewidget,ifnecessary.Atypicalwaywouldbetoimplement
     *thisinterfaceinaclassextendinginstance.web.Dialogandsimplydisplaythedialoginthis
     *method.
     */
    display:function(){},
};


/**
 *Handleredirectionwarnings,whichbehavemoreorlesslikearegular
 *warning,withanadditionalredirectionbutton.
 */
varRedirectWarningHandler=Widget.extend(ExceptionHandler,{
    init:function(parent,error){
        this._super(parent);
        this.error=error;
    },
    display:function(){
        varself=this;
        varerror=this.error;
        varadditional_context=_.extend({},this.context,error.data.arguments[3]);

        newWarningDialog(this,{
            title:_.str.capitalize(error.type)||_t("FlectraWarning"),
            buttons:[
                {text:error.data.arguments[2],classes:"btn-primary",click:function(){
                    self.do_action(
                        error.data.arguments[1],
                        {
                            additional_context:additional_context,
                        });
                        self.destroy();
                },close:true},
                {text:_t("Cancel"),click:function(){self.destroy();},close:true}
            ]
        },{
            message:error.data.arguments[0],
        }).open();
    }
});

core.crash_registry.add('flectra.exceptions.RedirectWarning',RedirectWarningHandler);

functionsession_expired(cm){
    return{
        display:function(){
            constnotif={
                type:_t("FlectraSessionExpired"),
                message:_t("YourFlectrasessionexpired.Thecurrentpageisabouttoberefreshed."),
            };
            constoptions={
                buttons:[{
                    text:_t("Ok"),
                    click:()=>window.location.reload(true),
                    close:true
                }],
            };
            cm.show_warning(notif,options);
        }
    };
}
core.crash_registry.add('flectra.http.SessionExpiredException',session_expired);
core.crash_registry.add('werkzeug.exceptions.Forbidden',session_expired);

core.crash_registry.add('504',function(cm){
    return{
        display:function(){
            cm.show_warning({
                type:_t("Requesttimeout"),
                message:_t("Theoperationwasinterrupted.Thisusuallymeansthatthecurrentoperationistakingtoomuchtime.")});
        }
    };
});

return{
    CrashManager:CrashManager,
    ErrorDialog:ErrorDialog,
    WarningDialog:WarningDialog,
    disable:()=>active=false,
};
});
