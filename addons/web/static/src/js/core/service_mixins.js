flectra.define('web.ServiceProviderMixin',function(require){
"usestrict";

varcore=require('web.core');

//ServiceProviderMixinisdeprecated.ItisonlyusedbytheProjectTimesheet
//app.Assoonasitnolongerusesit,wecanremoveit.
varServiceProviderMixin={
    services:{},//dictcontainingdeployedserviceinstances
    UndeployedServices:{},//dictcontainingclassesofundeployedservices
    /**
     *@override
     */
    init:function(parent){
        varself=this;
        //toproperlyinstantiateserviceswiththisasparent,thismixin
        //assumesthatitisusedalongtheEventDispatcherMixin,andthat
        //EventDispatchedMixin'sinitiscalledfirst
        //asEventDispatcherMixin'sinitisalreadycalled,thishandlerhas
        //tobeboundmanually
        this.on('call_service',this,this._call_service.bind(this));

        //addalreadyregisteredservicesfromtheserviceregistry
        _.each(core.serviceRegistry.map,function(Service,serviceName){
            if(serviceNameinself.UndeployedServices){
                thrownewError('Service"'+serviceName+'"isalreadyloaded.');
            }
            self.UndeployedServices[serviceName]=Service;
        });
        this._deployServices();

        //listenonnewlyaddedservices
        core.serviceRegistry.onAdd(function(serviceName,Service){
            if(serviceNameinself.services||serviceNameinself.UndeployedServices){
                thrownewError('Service"'+serviceName+'"isalreadyloaded.');
            }
            self.UndeployedServices[serviceName]=Service;
            self._deployServices();
        });
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _deployServices:function(){
        varself=this;
        vardone=false;
        while(!done){
            varserviceName=_.findKey(this.UndeployedServices,function(Service){
                //nomissingdependency
                return!_.some(Service.prototype.dependencies,function(depName){
                    return!self.services[depName];
                });
            });
            if(serviceName){
                varservice=newthis.UndeployedServices[serviceName](this);
                this.services[serviceName]=service;
                deletethis.UndeployedServices[serviceName];
                service.start();
            }else{
                done=true;
            }
        }
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Callthe'service',usingdatafromthe'event'that
     *hastriggeredtheservicecall.
     *
     *Fortheajaxservice,theargumentsareextendedwith
     *thetargetsothatitcancallbackthecaller.
     *
     *@private
     *@param {FlectraEvent}event
     */
    _call_service:function(event){
        varargs=event.data.args||[];
        if(event.data.service==='ajax'&&event.data.method==='rpc'){
            //ajaxserviceusesanextra'target'argumentforrpc
            args=args.concat(event.target);
        }
        varservice=this.services[event.data.service];
        varresult=service[event.data.method].apply(service,args);
        event.data.callback(result);
    },
};

returnServiceProviderMixin;

});

flectra.define('web.ServicesMixin',function(require){
"usestrict";

varrpc=require('web.rpc');

/**
 *@mixin
 *@nameServicesMixin
 */
varServicesMixin={
    /**
     *@param {string}service
     *@param {string}method
     *@return{any}resultoftheservicecalled
     */
    call:function(service,method){
        varargs=Array.prototype.slice.call(arguments,2);
        varresult;
        this.trigger_up('call_service',{
            service:service,
            method:method,
            args:args,
            callback:function(r){
                result=r;
            },
        });
        returnresult;
    },
    /**
     *@private
     *@param{Object}libs-@seeajax.loadLibs
     *@param{Object}[context]-@seeajax.loadLibs
     *@param{Object}[tplRoute=this._loadLibsTplRoute]-@seeajax.loadLibs
     *@returns{Promise}
     */
    _loadLibs:function(libs,context,tplRoute){
        returnthis.call('ajax','loadLibs',libs,context,tplRoute||this._loadLibsTplRoute);
    },
    /**
     *BuildsandexecutesRPCquery.Returnsapromiseresolvedwith
     *theRPCresult.
     *
     *@param{string}paramseitherarouteoramodel
     *@param{string}optionsifamodelisgiven,thisargumentisamethod
     *@returns{Promise}
     */
    _rpc:function(params,options){
        varquery=rpc.buildQuery(params);
        varprom=this.call('ajax','rpc',query.route,query.params,options,this);
        if(!prom){
            prom=newPromise(function(){});
            prom.abort=function(){};
        }
        varabort=prom.abort?prom.abort:prom.reject;
        if(!abort){
            thrownewError("arpcpromiseshouldalwayshavearejectfunction");
        }
        prom.abort=abort.bind(prom);
        returnprom;
    },
    loadFieldView:function(modelName,context,view_id,view_type,options){
        returnthis.loadViews(modelName,context,[[view_id,view_type]],options).then(function(result){
            returnresult[view_type];
        });
    },
    loadViews:function(modelName,context,views,options){
        varself=this;
        returnnewPromise(function(resolve){
            self.trigger_up('load_views',{
                modelName:modelName,
                context:context,
                views:views,
                options:options,
                on_success:resolve,
            });
        });
    },
    loadFilters:function(modelName,actionId,context){
        varself=this;
        returnnewPromise(function(resolve,reject){
            self.trigger_up('load_filters',{
                modelName:modelName,
                actionId:actionId,
                context:context,
                on_success:resolve,
            });
        });
    },
    createFilter:function(filter){
        varself=this;
        returnnewPromise(function(resolve,reject){
            self.trigger_up('create_filter',{
                filter:filter,
                on_success:resolve,
            });
        });
    },
    deleteFilter:function(filterId){
        varself=this;
        returnnewPromise(function(resolve,reject){
            self.trigger_up('delete_filter',{
                filterId:filterId,
                on_success:resolve,
            });
        });
    },
    //Sessionstuff
    getSession:function(){
        varsession;
        this.trigger_up('get_session',{
            callback:function(result){
                session=result;
            }
        });
        returnsession;
    },
    /**
     *Informstheactionmanagertodoanaction.Thissupposesthattheaction
     *managercanbefoundamongsttheancestorsofthecurrentwidget.
     *Ifthat'snotthecasethismethodwillsimplyreturnanunresolved
     *promise.
     *
     *@param{any}action
     *@param{any}options
     *@returns{Promise}
     */
    do_action:function(action,options){
        varself=this;
        returnnewPromise(function(resolve,reject){
            self.trigger_up('do_action',{
                action:action,
                options:options,
                on_success:resolve,
                on_fail:reject,
            });
        });
    },
    /**
     *Displaysanotification.
     *
     *@param{Object}options
     *@param{string}options.title
     *@param{string}[options.subtitle]
     *@param{string}[options.message]
     *@param{string}[options.type='warning']'info','success','warning','danger'or''
     *@param{boolean}[options.sticky=false]
     *@param{string}[options.className]
     */
    displayNotification:function(options){
        returnthis.call('notification','notify',options);
    },
    /**
     *@deprecatedwillberemovedassoonasthenotificationsystemisreviewed
     *@seedisplayNotification
     */
    do_notify:function(title=false,message,sticky,className){
        returnthis.displayNotification({
            type:'warning',
            title:title,
            message:message,
            sticky:sticky,
            className:className,
        });
    },
    /**
     *@deprecatedwillberemovedassoonasthenotificationsystemisreviewed
     *@seedisplayNotification
     */
    do_warn:function(title=false,message,sticky,className){
        console.warn(title,message);
        returnthis.displayNotification({
            type:'danger',
            title:title,
            message:message,
            sticky:sticky,
            className:className,
        });
    },
};

returnServicesMixin;

});
