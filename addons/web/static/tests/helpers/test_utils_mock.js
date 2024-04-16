flectra.define('web.test_utils_mock',function(require){
"usestrict";

/**
 *MockTestUtils
 *
 *Thismoduledefinesvariousutilityfunctionstohelpmockingdata.
 *
 *Notethatallmethodsdefinedinthismoduleareexportedinthemain
 *testUtilsfile.
 */

constAbstractStorageService=require('web.AbstractStorageService');
constAjaxService=require('web.AjaxService');
constbasic_fields=require('web.basic_fields');
constBus=require('web.Bus');
constconfig=require('web.config');
constcore=require('web.core');
constdom=require('web.dom');
constmakeTestEnvironment=require('web.test_env');
constMockServer=require('web.MockServer');
constRamStorage=require('web.RamStorage');
constsession=require('web.session');

constDebouncedField=basic_fields.DebouncedField;


//------------------------------------------------------------------------------
//Privatefunctions
//------------------------------------------------------------------------------

/**
 *ReturnsamockedenvironmenttobeusedbyOWLcomponentsintests,with
 *requestedservices(+ajax,local_storageandsession_storage)deployed.
 *
 *@private
 *@param{Object}params
 *@param{Bus}[params.bus]
 *@param{boolean}[params.debug]
 *@param{Object}[params.env]
 *@param{Bus}[params.env.bus]
 *@param{Object}[params.env.dataManager]
 *@param{Object}[params.env.services]
 *@param{Object[]}[params.favoriteFilters]
 *@param{Object}[params.services]
 *@param{Object}[params.session]
 *@param{MockServer}[mockServer]
 *@returns{Promise<Object>}env
 */
asyncfunction_getMockedOwlEnv(params,mockServer){
    params.env=params.env||{};

    //buildtheenv
    constfavoriteFilters=params.favoriteFilters;
    constdebug=params.debug;
    constservices={};
    constenv=Object.assign({},params.env,{
        browser:Object.assign({
            fetch:(resource,init)=>mockServer.performFetch(resource,init),
        },params.env.browser),
        bus:params.bus||params.env.bus||newBus(),
        dataManager:Object.assign({
            load_action:(actionID,context)=>{
                returnmockServer.performRpc('/web/action/load',{
                    action_id:actionID,
                    additional_context:context,
                });
            },
            load_views:(params,options)=>{
                returnmockServer.performRpc('/web/dataset/call_kw/'+params.model,{
                    args:[],
                    kwargs:{
                        context:params.context,
                        options:options,
                        views:params.views_descr,
                    },
                    method:'load_views',
                    model:params.model,
                }).then(function(views){
                    views=_.mapObject(views,viewParams=>{
                        returnfieldsViewGet(mockServer,viewParams);
                    });
                    if(favoriteFilters&&'search'inviews){
                        views.search.favoriteFilters=favoriteFilters;
                    }
                    returnviews;
                });
            },
            load_filters:params=>{
                if(debug){
                    console.log('[mock]load_filters',params);
                }
                returnPromise.resolve([]);
            },
        },params.env.dataManager),
        services:Object.assign(services,params.env.services),
        session:params.env.session||params.session||{},
    });

    //deployservicesintotheenv
    //determineservicestoinstantiate(classes),andalreadyregisterfunctionservices
    constservicesToDeploy={};
    for(constnameinparams.services||{}){
        constService=params.services[name];
        if(Service.constructor.name==='Class'){
            servicesToDeploy[name]=Service;
        }else{
            services[name]=Service;
        }
    }
    //alwaysdeployajax,localstorageandsessionstorage
    if(!servicesToDeploy.ajax){
        constMockedAjaxService=AjaxService.extend({
            rpc:mockServer.performRpc.bind(mockServer),
        });
        services.ajax=newMockedAjaxService(env);
    }
    constRamStorageService=AbstractStorageService.extend({
        storage:newRamStorage(),
    });
    if(!servicesToDeploy.local_storage){
        services.local_storage=newRamStorageService(env);
    }
    if(!servicesToDeploy.session_storage){
        services.session_storage=newRamStorageService(env);
    }
    //deployotherrequestedservices
    letdone=false;
    while(!done){
        constserviceName=Object.keys(servicesToDeploy).find(serviceName=>{
            constService=servicesToDeploy[serviceName];
            returnService.prototype.dependencies.every(depName=>{
                returnenv.services[depName];
            });
        });
        if(serviceName){
            constService=servicesToDeploy[serviceName];
            services[serviceName]=newService(env);
            deleteservicesToDeploy[serviceName];
            services[serviceName].start();
        }else{
            constserviceNames=_.keys(servicesToDeploy);
            if(serviceNames.length){
                console.warn("Nonloadedservices:",serviceNames);
            }
            done=true;
        }
    }
    //waitforasynchronousservicestoproperlystart
    awaitnewPromise(setTimeout);

    returnenv;
}
/**
 *Thisfunctionisusedtomockglobalobjects(session,config...)intests.
 *Itisnecessaryforlegacywidgets.ItreturnsacleanUpfunctiontocallat
 *theendofthetest.
 *
 *Thefunctioncouldberemovedassoonaswedonotsupportlegacywidgets
 *anymore.
 *
 *@private
 *@param{Object}params
 *@param{Object}[params.config]ifgiven,itisusedtoextendtheglobal
 *  config,
 *@param{Object}[params.session]ifgiven,itisusedtoextendthecurrent,
 *  realsession.
 *@param{Object}[params.translateParameters]ifgiven,itwillbeusedto
 *  extendthecore._t.database.parametersobject.
 *@returns{function}acleanUpfunctiontorestoreeverything,tocallatthe
 *  endofthetest
 */
function_mockGlobalObjects(params){
    //storeinitialsessionstate(forrestoration)
    constinitialSession=Object.assign({},session);
    constsessionPatch=Object.assign({
        getTZOffset(){return0;},
        asyncuser_has_group(){returnfalse;},
    },params.session);
    //patchsession
    Object.assign(session,sessionPatch);

    //patchconfig
    letinitialConfig;
    if('config'inparams){
        initialConfig=Object.assign({},config);
        initialConfig.device=Object.assign({},config.device);
        if('device'inparams.config){
            Object.assign(config.device,params.config.device);
        }
        if('debug'inparams.config){
            flectra.debug=params.config.debug;
        }
    }

    //patchtranslateparams
    letinitialParameters;
    if('translateParameters'inparams){
        initialParameters=Object.assign({},core._t.database.parameters);
        Object.assign(core._t.database.parameters,params.translateParameters);
    }

    //buildthecleanUpfunctiontorestoreeverythingattheendofthetest
    functioncleanUp(){
        letkey;
        for(keyinsessionPatch){
            deletesession[key];
        }
        Object.assign(session,initialSession);
        if('config'inparams){
            for(keyinconfig){
                deleteconfig[key];
            }
            _.extend(config,initialConfig);
        }
        if('translateParameters'inparams){
            for(keyincore._t.database.parameters){
                deletecore._t.database.parameters[key];
            }
            _.extend(core._t.database.parameters,initialParameters);
        }
    }

    returncleanUp;
}
/**
 *logsalleventgoingthroughthetargetwidget.
 *
 *@param{Widget}widget
 */
function_observe(widget){
    var_trigger_up=widget._trigger_up.bind(widget);
    widget._trigger_up=function(event){
        console.log('%c[event]'+event.name,'color:blue;font-weight:bold;',event);
        _trigger_up(event);
    };
}

//------------------------------------------------------------------------------
//Publicfunctions
//------------------------------------------------------------------------------

/**
 *performsafields_view_get,andmocksthepostprocessingdonebythe
 *data_managertoreturnanequivalentstructure.
 *
 *@param{MockServer}server
 *@param{Object}params
 *@param{string}params.model
 *@returns{Object}anobjectwith3keys:arch,fieldsandviewFields
 */
functionfieldsViewGet(server,params){
    varfieldsView=server.fieldsViewGet(params);
    //mockthestructureproducedbytheDataManager
    fieldsView.viewFields=fieldsView.fields;
    fieldsView.fields=server.fieldsGet(params.model);
    returnfieldsView;
}

/**
 *interceptsaneventbubblingupthewidgethierarchy.Theeventintercepted
 *mustbea"customevent",i.e.aneventgeneratedbythemethod'trigger_up'.
 *
 *Notethatthismethodreallyinterceptstheeventif@propagateisnotset.
 *Itwillnotbepropagatedfurther,andeventhehandlersonthetargetwill
 *notfire.
 *
 *@param{Widget}widgetthetargetwidget(anyFlectrawidget)
 *@param{string}eventNamedescriptionoftheevent
 *@param{function}fncallbackexecutedwhentheevenisintercepted
 *@param{boolean}[propagate=false]
 */
functionintercept(widget,eventName,fn,propagate){
    var_trigger_up=widget._trigger_up.bind(widget);
    widget._trigger_up=function(event){
        if(event.name===eventName){
            fn(event);
            if(!propagate){return;}
        }
        _trigger_up(event);
    };
}

/**
 *Removesthesrcattributeonimagesandiframestopreventnotfounderrors,
 *andoptionallytriggersanrpcwiththesrcurlasrouteonawidget.
 *Thismethodiscriticalandmustbefastest(=>nojQuery,nounderscore)
 *
 *@param{HTMLElement}el
 *@param{[function]}rpc
 */
functionremoveSrcAttribute(el,rpc){
    varnodes;
    if(el.nodeName==="#comment"){
        return;
    }
    el=el.nodeType===8?el.nextSibling:el;
    if(el.nodeName==='IMG'||el.nodeName==='IFRAME'){
        nodes=[el];
    }else{
        nodes=Array.prototype.slice.call(el.getElementsByTagName('img'))
            .concat(Array.prototype.slice.call(el.getElementsByTagName('iframe')));
    }
    varnode;
    while(node=nodes.pop()){
        varsrc=node.attributes.src&&node.attributes.src.value;
        if(src&&src!=='about:blank'){
            node.setAttribute('data-src',src);
            if(node.nodeName==='IMG'){
                node.attributes.removeNamedItem('src');
            }else{
                node.setAttribute('src','about:blank');
            }
            if(rpc){
                rpc(src,[]);
            }
            $(node).trigger('load');
        }
    }
}

/**
 *AddamockenvironmenttotestOwlComponents.Thisfunctiongeneratesatest
 *envandsetsitonthegivenComponent.Italsohasseveralsideeffects,
 *likepatchingtheglobalsessionorconfigobjects.Itreturnsacleanup
 *functiontocallattheendofthetest.
 *
 *@param{Component}Component
 *@param{Object}[params]
 *@param{Object}[params.actions]
 *@param{Object}[params.archs]
 *@param{string}[params.currentDate]
 *@param{Object}[params.data]
 *@param{boolean}[params.debug]
 *@param{function}[params.mockFetch]
 *@param{function}[params.mockRPC]
 *@param{number}[params.fieldDebounce=0]thevalueoftheDEBOUNCEattribute
 *  offields
 *@param{boolean}[params.debounce=true]iffalse,patch_.debouncetoremove
 *  itsbehavior
 *@param{boolean}[params.throttle=false]bydefault,_.throttleispatchedto
 *  removeitsbehavior,exceptifthisparamsissettotrue
 *@param{boolean}[params.mockSRC=false]iftrue,redirectsrcGETrequeststo
 *  themockServer
 *@param{MockServer}[mockServer]
 *@returns{Promise<function>}thecleanupfunction
 */
asyncfunctionaddMockEnvironmentOwl(Component,params,mockServer){
    params=params||{};

    //instantiateamockServerifnotprovided
    if(!mockServer){
        letServer=MockServer;
        if(params.mockFetch){
            Server=MockServer.extend({_performFetch:params.mockFetch});
        }
        if(params.mockRPC){
            Server=Server.extend({_performRpc:params.mockRPC});
        }
        mockServer=newServer(params.data,{
            actions:params.actions,
            archs:params.archs,
            currentDate:params.currentDate,
            debug:params.debug,
        });
    }

    //makesurethedebouncevalueforinputfieldsissetto0
    constinitialDebounceValue=DebouncedField.prototype.DEBOUNCE;
    DebouncedField.prototype.DEBOUNCE=params.fieldDebounce||0;
    constinitialDOMDebounceValue=dom.DEBOUNCE;
    dom.DEBOUNCE=0;

    //patchunderscoredebounce/throttlefunctions
    constinitialDebounce=_.debounce;
    if(params.debounce===false){
        _.debounce=function(func){
            returnfunc;
        };
    }
    //fixme:throttleisinactivebydefault,shouldwemakeitexplicit?
    constinitialThrottle=_.throttle;
    if(!('throttle'inparams)||!params.throttle){
        _.throttle=function(func){
            returnfunc;
        };
    }

    //makesureimagesdonottriggeraGETontheserver
    $('body').on('DOMNodeInserted.removeSRC',function(ev){
        letrpc;
        if(params.mockSRC){
            rpc=mockServer.performRpc.bind(mockServer);
        }
        removeSrcAttribute(ev.target,rpc);
    });

    //mockglobalobjectsforlegacywidgets(session,config...)
    constrestoreMockedGlobalObjects=_mockGlobalObjects(params);

    //setthetestenvonowlComponent
    constenv=await_getMockedOwlEnv(params,mockServer);
    constoriginalEnv=Component.env;
    Component.env=makeTestEnvironment(env,mockServer.performRpc.bind(mockServer));

    //whilewehaveamixbetweenOwlandlegacystuff,someofthemtriggering
    //eventsontheenv.bus(anewBusinstanceespeciallycreatedforthecurrent
    //test),theothersusingcore.bus,wehavetoensurethateventstriggered
    //onenv.busarealsotriggeredoncore.bus(notethatoutsidethetesting
    //environment,botharetheexactsameinstanceofBus)
    constenvBusTrigger=env.bus.trigger;
    env.bus.trigger=function(){
        core.bus.trigger(...arguments);
        envBusTrigger.call(env.bus,...arguments);
    };

    //buildthecleanupfunctiontocallattheendofthetest
    functioncleanUp(){
        env.bus.destroy();
        Object.keys(env.services).forEach(function(s){
            varservice=env.services[s];
            if(service.destroy&&!service.isDestroyed()){
                service.destroy();
            }
        });

        DebouncedField.prototype.DEBOUNCE=initialDebounceValue;
        dom.DEBOUNCE=initialDOMDebounceValue;
        _.debounce=initialDebounce;
        _.throttle=initialThrottle;

        //clearthecaches(e.g.data_manager,ModelFieldSelector)attheend
        //ofeachtesttoavoidcollisions
        core.bus.trigger('clear_cache');

        $('body').off('DOMNodeInserted.removeSRC');
        $('.blockUI').remove();//fixme:movetoqunit_configinFlectraAfterTestHook?

        restoreMockedGlobalObjects();

        Component.env=originalEnv;
    }

    returncleanUp;
}

/**
 *Addamockenvironmenttoawidget. Thishelperfunctioncansimulate
 *variouskindofsideeffects,suchasmockingRPCs,changingthesession,
 *orthetranslationsettings.
 *
 *Thesimulatedenvironmentlastsforthelifecycleofthewidget,meaningit
 *disappearswhenthewidgetisdestroyed. Itisparticularlyrelevantforthe
 *sessionmocks,becausetheprevioussessionisrestoredduringthedestroy
 *call. So,itmeansthatyouhavetobecarefulandmakesurethatitis
 *properlydestroyedbeforeanothertestisrun,otherwiseyouriskhaving
 *interferencesbetweentests.
 *
 *@param{Widget}widget
 *@param{Object}params
 *@param{Object}[params.archs]amapofstring[model,view_id,view_type]to
 *  aarchobject.Itisusedtomockanswersto'load_views'customevents.
 *  Thisisusefulwhenthewidgetinstantiateaformviewdialogthatneeds
 *  toloadaparticulararch.
 *@param{string}[params.currentDate]astringrepresentationofthecurrent
 *  date.Itisgiventothemockserver.
 *@param{Object}params.datathedatagiventothecreatedmockserver.Itis
 *  usedtogeneratemockanswersforeverykindofroutessupportedbyflectra
 *@param{number}[params.debug]ifsettotrue,logsRPCsanduncaughtFlectra
 *  events.
 *@param{Object}[params.bus]theinstanceofBusthatwillbeused(intheenv)
 *@param{function}[params.mockFetch]afunctionthatwillbeusedtooverride
 *  the_performFetchmethodfromthemockserver.Itisreallyusefultoadd
 *  somecustomfetchmocks,ortochecksomeassertions.
 *@param{function}[params.mockRPC]afunctionthatwillbeusedtooverride
 *  the_performRpcmethodfromthemockserver.Itisreallyusefultoadd
 *  somecustomrpcmocks,ortochecksomeassertions.
 *@param{Object}[params.session]ifitisgiven,itwillbeusedasanswer
 *  forallcallstothis.getSession()bythewidget,ofitschildren. Also,
 *  itwillbeusedtoextendthecurrent,realsession.Thissideeffectis
 *  undonewhenthewidgetisdestroyed.
 *@param{Object}[params.translateParameters]ifgiven,itwillbeusedto
 *  extendthecore._t.database.parametersobject.Afterthewidget
 *  destruction,theoriginalparameterswillberestored.
 *@param{Object}[params.intercepts]anobjectwitheventnamesaskey,and
 *  callbackasvalue. Eachkey,valuewillbeusedtointercepttheevent.
 *  Notethatthisisparticularlyusefulifyouwanttointercepteventsgoing
 *  upintheinitprocessoftheview,becausetherearenootherwaytodoit
 *  afterthismethodreturns.Someevents('call_service',"load_views",
 *  "get_session","load_filters")haveaspecialtreatmentbeforehand.
 *@param{Object}[params.services={}]listofservicestoloadin
 *  additiontotheajaxservice.Forinstance,ifatestneedsthelocal
 *  storageserviceinordertowork,itcanprovideamockversionofit.
 *@param{boolean}[debounce=true]settofalsetocompletelyremovethe
 *  debouncing,forcingthehandlertobecalleddirectly(notonthenext
 *  executionstack,likeitdoeswithdelay=0).
 *@param{boolean}[throttle=false]settotruetokeepthethrottling,which
 *  iscompletelyremovedbydefault.
 *
 *@returns{Promise<MockServer>}theinstanceofthemockserver,createdbythis
 *  function.ItisnecessaryforcreateViewsothatmethodcancallsome
 *  othermethodsonit.
 */
asyncfunctionaddMockEnvironment(widget,params){
    //logeventstriggeredupifdebugflagistrue
    if(params.debug){
        _observe(widget);
        varseparator=window.location.href.indexOf('?')!==-1?"&":"?";
        varurl=window.location.href+separator+'testId='+QUnit.config.current.testId;
        console.log('%c[debug]debugmodeactivated','color:blue;font-weight:bold;',url);
    }

    //instantiatemockserver
    varServer=MockServer;
    if(params.mockFetch){
        Server=MockServer.extend({_performFetch:params.mockFetch});
    }
    if(params.mockRPC){
        Server=Server.extend({_performRpc:params.mockRPC});
    }
    varmockServer=newServer(params.data,{
        actions:params.actions,
        archs:params.archs,
        currentDate:params.currentDate,
        debug:params.debug,
        widget:widget,
    });

    //buildandsettheOwlenvonComponent
    if(!('mockSRC'inparams)){//redirectsrcrpcstothemockserver
        params.mockSRC=true;
    }
    constcleanUp=awaitaddMockEnvironmentOwl(owl.Component,params,mockServer);
    constenv=owl.Component.env;

    //ensuretocleanupeverythingwhenthewidgetwillbedestroyed
    constdestroy=widget.destroy;
    widget.destroy=function(){
        cleanUp();
        destroy.call(this,...arguments);
    };

    //interceptservice/datamanagercallsandredirectthemtotheenv
    intercept(widget,'call_service',function(ev){
        if(env.services[ev.data.service]){
            varservice=env.services[ev.data.service];
            constresult=service[ev.data.method].apply(service,ev.data.args||[]);
            ev.data.callback(result);
        }
    });
    intercept(widget,'load_action',asyncev=>{
        constaction=awaitenv.dataManager.load_action(ev.data.actionID,ev.data.context);
        ev.data.on_success(action);
    });
    intercept(widget,"load_views",asyncev=>{
        constparams={
            model:ev.data.modelName,
            context:ev.data.context,
            views_descr:ev.data.views,
        };
        constviews=awaitenv.dataManager.load_views(params,ev.data.options);
        if('search'inviews&&params.favoriteFilters){
            views.search.favoriteFilters=params.favoriteFilters;
        }
        ev.data.on_success(views);
    });
    intercept(widget,"get_session",ev=>{
        ev.data.callback(session);
    });
    intercept(widget,"load_filters",asyncev=>{
        constfilters=awaitenv.dataManager.load_filters(ev.data);
        ev.data.on_success(filters);
    });

    //makesureallotherFlectraeventsbubblingupareintercepted
    Object.keys(params.intercepts||{}).forEach(function(name){
        intercept(widget,name,params.intercepts[name]);
    });

    returnmockServer;
}

/**
 *Patchwindow.DatesothatthetimestartsitsflowfromtheprovidedDate.
 *
 *Usage:
 *
 * ```
 * varunpatchDate=testUtils.mock.patchDate(2018,0,10,17,59,30)
 * newwindow.Date();//"WedJan10201817:59:30GMT+0100(CentralEuropeanStandardTime)"
 * ...//5hoursdelay
 * newwindow.Date();//"WedJan10201822:59:30GMT+0100(CentralEuropeanStandardTime)"
 * ...
 * unpatchDate();
 * newwindow.Date();//actualcurrentdatetime
 * ```
 *
 *@param{integer}year
 *@param{integer}monthindexofthemonth,startingfromzero.
 *@param{integer}daythedayofthemonth.
 *@param{integer}hoursthedigitsforhours(24h)
 *@param{integer}minutes
 *@param{integer}seconds
 *@returns{Function}acallbacktounpatchwindow.Date.
 */
functionpatchDate(year,month,day,hours,minutes,seconds){
    varRealDate=window.Date;
    varactualDate=newRealDate();
    varfakeDate=newRealDate(year,month,day,hours,minutes,seconds);
    vartimeInterval=actualDate.getTime()-(fakeDate.getTime());

    Date=(function(NativeDate){
        functionDate(Y,M,D,h,m,s,ms){
            varlength=arguments.length;
            if(arguments.length>0){
                vardate=length==1&&String(Y)===Y?//isString(Y)
                    //Weexplicitlypassitthroughparse:
                    newNativeDate(Date.parse(Y)):
                    //Wehavetomanuallymakecallsdependingonargument
                    //lengthhere
                    length>=7?newNativeDate(Y,M,D,h,m,s,ms):
                    length>=6?newNativeDate(Y,M,D,h,m,s):
                    length>=5?newNativeDate(Y,M,D,h,m):
                    length>=4?newNativeDate(Y,M,D,h):
                    length>=3?newNativeDate(Y,M,D):
                    length>=2?newNativeDate(Y,M):
                    length>=1?newNativeDate(Y):
                                  newNativeDate();
                //PreventmixupswithunfixedDateobject
                date.constructor=Date;
                returndate;
            }else{
                vardate=newNativeDate();
                vartime=date.getTime();
                time-=timeInterval;
                date.setTime(time);
                returndate;
            }
        }

        //Copyanycustommethodsa3rdpartylibrarymayhaveadded
        for(varkeyinNativeDate){
            Date[key]=NativeDate[key];
        }

        //Copy"native"methodsexplicitly;theymaybenon-enumerable
        //exception:'now'usesfakedateasreference
        Date.now=function(){
            vardate=newNativeDate();
            vartime=date.getTime();
            time-=timeInterval;
            returntime;
        };
        Date.UTC=NativeDate.UTC;
        Date.prototype=NativeDate.prototype;
        Date.prototype.constructor=Date;

        //UpgradeDate.parsetohandlesimplifiedISO8601strings
        Date.parse=NativeDate.parse;
        returnDate;
    })(Date);

    returnfunction(){window.Date=RealDate;};
}

varpatches={};
/**
 *PatchesagivenClassorObjectwiththegivenproperties.
 *
 *@param{Class|Object}target
 *@param{Object}props
 */
functionpatch(target,props){
    varpatchID=_.uniqueId('patch_');
    target.__patchID=patchID;
    patches[patchID]={
        target:target,
        otherPatchedProps:[],
        ownPatchedProps:[],
    };
    if(target.prototype){
        _.each(props,function(value,key){
            if(target.prototype.hasOwnProperty(key)){
                patches[patchID].ownPatchedProps.push({
                    key:key,
                    initialValue:target.prototype[key],
                });
            }else{
                patches[patchID].otherPatchedProps.push(key);
            }
        });
        target.include(props);
    }else{
        _.each(props,function(value,key){
            if(keyintarget){
                varoldValue=target[key];
                patches[patchID].ownPatchedProps.push({
                    key:key,
                    initialValue:oldValue,
                });
                if(typeofvalue==='function'){
                    target[key]=function(){
                        varoldSuper=this._super;
                        this._super=oldValue;
                        varresult=value.apply(this,arguments);
                        if(oldSuper===undefined){
                            deletethis._super;
                        }else{
                            this._super=oldSuper;
                        }
                        returnresult;
                    };
                }else{
                    target[key]=value;
                }
            }else{
                patches[patchID].otherPatchedProps.push(key);
                target[key]=value;
            }
        });
    }
}

/**
 *UnpatchesagivenClassorObject.
 *
 *@param{Class|Object}target
 */
functionunpatch(target){
    varpatchID=target.__patchID;
    varpatch=patches[patchID];
    if(target.prototype){
        _.each(patch.ownPatchedProps,function(p){
            target.prototype[p.key]=p.initialValue;
        });
        _.each(patch.otherPatchedProps,function(key){
            deletetarget.prototype[key];
        });
    }else{
        _.each(patch.ownPatchedProps,function(p){
            target[p.key]=p.initialValue;
        });
        _.each(patch.otherPatchedProps,function(key){
            deletetarget[key];
        });
    }
    deletepatches[patchID];
    deletetarget.__patchID;
}

window.originalSetTimeout=window.setTimeout;
functionpatchSetTimeout(){
    varoriginal=window.setTimeout;
    varself=this;
    window.setTimeout=function(handler,delay){
        console.log("callingsetTimeouton"+(handler.name||"somefunction")+"withdelayof"+delay);
        console.trace();
        varhandlerArguments=Array.prototype.slice.call(arguments,1);
        returnoriginal(function(){
            handler.bind(self,handlerArguments)();
            console.log('afterdoingtheactionofthesetTimeout');
        },delay);
    };

    returnfunction(){
        window.setTimeout=original;
    };
}

return{
    addMockEnvironment:addMockEnvironment,
    fieldsViewGet:fieldsViewGet,
    addMockEnvironmentOwl:addMockEnvironmentOwl,
    intercept:intercept,
    patchDate:patchDate,
    patch:patch,
    unpatch:unpatch,
    patchSetTimeout:patchSetTimeout,
};

});
