flectra.define('web.test_utils_create',function(require){
    "usestrict";

    /**
     *CreateTestUtils
     *
     *Thismoduledefinesvariousutilityfunctionstohelpcreatingmockwidgets
     *
     *Notethatallmethodsdefinedinthismoduleareexportedinthemain
     *testUtilsfile.
     */

    constActionManager=require('web.ActionManager');
    constActionMenus=require('web.ActionMenus');
    constconcurrency=require('web.concurrency');
    constconfig=require('web.config');
    constControlPanel=require('web.ControlPanel');
    constcustomHooks=require('web.custom_hooks');
    constDebugManager=require('web.DebugManager.Backend');
    constdom=require('web.dom');
    constmakeTestEnvironment=require('web.test_env');
    constActionModel=require('web/static/src/js/views/action_model.js');
    constRegistry=require('web.Registry');
    consttestUtilsMock=require('web.test_utils_mock');
    constWidget=require('web.Widget');

    const{Component}=owl;
    const{useRef,useState}=owl.hooks;
    const{xml}=owl.tags;

    /**
     *CreateandreturnaninstanceofActionManagerwithallrpcsgoingthrougha
     *mockmethodusingthedata,actionsandarchsobjectsassources.
     *
     *@param{Object}[params={}]
     *@param{Object}[params.actions]theactionsgiventothemockserver
     *@param{Object}[params.archs]thisarchsgiventothemockserver
     *@param{Object}[params.data]thebusinessdatagiventothemockserver
     *@param{function}[params.mockRPC]
     *@returns{Promise<ActionManager>}
     */
    asyncfunctioncreateActionManager(params={}){
        consttarget=prepareTarget(params.debug);

        constwidget=newWidget();
        //when'document'addonisinstalled,thesidebardoesa'search_read'on
        //model'ir_attachment'eachtimearecordisopen,sowemonkey-patch
        //'mockRPC'tomutethoseRPCs,sothatthetestscanbewrittenuniformly,
        //whetherornot'document'isinstalled
        constmockRPC=params.mockRPC;
        Object.assign(params,{
            asyncmockRPC(route,args){
                if(args.model==='ir.attachment'){
                    return[];
                }
                if(mockRPC){
                    returnmockRPC.apply(this,arguments);
                }
                returnthis._super(...arguments);
            },
        });
        constmockServer=awaittestUtilsMock.addMockEnvironment(widget,Object.assign({debounce:false},params));
        awaitwidget.prependTo(target);
        widget.el.classList.add('o_web_client');
        if(config.device.isMobile){
            widget.el.classList.add('o_touch_device');
        }

        params.server=mockServer;

        constuserContext=params.context&&params.context.user_context||{};
        constactionManager=newActionManager(widget,userContext);

        //OverridetheActionMenusregistryunlesstoldotherwise.
        letactionMenusRegistry=ActionMenus.registry;
        if(params.actionMenusRegistry!==true){
            ActionMenus.registry=newRegistry();
        }

        constoriginalDestroy=ActionManager.prototype.destroy;
        actionManager.destroy=function(){
            actionManager.destroy=originalDestroy;
            widget.destroy();
            if(params.actionMenusRegistry!==true){
                ActionMenus.registry=actionMenusRegistry;
            }
        };
        constfragment=document.createDocumentFragment();
        awaitactionManager.appendTo(fragment);
        dom.append(widget.el,fragment,{
            callbacks:[{widget:actionManager}],
            in_DOM:true,
        });
        returnactionManager;
    }

    /**
     *SimilarascreateView,butspecificforcalendarviews.Somecalendar
     *testsneedtotriggerpositionalclicksontheDOMproducedbyfullcalendar.
     *ThosetestsmustusethishelperwithoptionpositionalClickssettotrue.
     *Thiswillmovetherenderedcalendartothebody(requiredtodopositional
     *clicks),andwaitforasetTimeout(0)beforereturning,becausefullcalendar
     *makesthecalendarscrollto6:00inasetTimeout(0),whichmighthavean
     *impactaccordingtowherewewanttotriggerpositionalclicks.
     *
     *@param{Object}params@seecreateView
     *@param{Object}[options]
     *@param{boolean}[options.positionalClicks=false]
     *@returns{Promise<CalendarController>}
     */
    asyncfunctioncreateCalendarView(params,options){
        constcalendar=awaitcreateView(params);
        if(!options||!options.positionalClicks){
            returncalendar;
        }
        constviewElements=[...document.getElementById('qunit-fixture').children];
        //prependresetthescrollToptozerosowerestoreitmanually
        letfcScroller=document.querySelector('.fc-scroller');
        constscrollPosition=fcScroller.scrollTop;
        viewElements.forEach(el=>document.body.prepend(el));
        fcScroller=document.querySelector('.fc-scroller');
        fcScroller.scrollTop=scrollPosition;

        constdestroy=calendar.destroy;
        calendar.destroy=()=>{
            viewElements.forEach(el=>el.remove());
            destroy();
        };
        awaitconcurrency.delay(0);
        returncalendar;
    }

    /**
     *CreateasimplecomponentenvironmentwithabasicParentcomponent,an
     *extensibleenvandamockedserver.Thereturnedvalueistheinstanceof
     *thegivenconstructor.
     *@param{class}constructorComponentclasstoinstantiate
     *@param{Object}[params={}]
     *@param{boolean}[params.debug]
     *@param{Object}[params.env]
     *@param{Object}[params.intercepts]objectinwhichthekeysrepresentthe
     *     interceptedeventnamesandthevaluesaretheircallbacks.
     *@param{Object}[params.props]
     *@returns{Promise<Component>}instanceof`constructor`
     */
    asyncfunctioncreateComponent(constructor,params={}){
        if(!constructor){
            thrownewError(`Missingargument"constructor".`);
        }
        if(!(constructor.prototypeinstanceofComponent)){
            thrownewError(`Argument"constructor"mustbeanOwlComponent.`);
        }
        constcleanUp=awaittestUtilsMock.addMockEnvironmentOwl(Component,params);
        classParentextendsComponent{
            constructor(){
                super(...arguments);
                this.Component=constructor;
                this.state=useState(params.props||{});
                this.component=useRef('component');
                for(consteventNameinparams.intercepts||{}){
                    customHooks.useListener(eventName,params.intercepts[eventName]);
                }
            }
        }
        Parent.template=xml`<tt-component="Component"t-props="state"t-ref="component"/>`;
        constparent=newParent();
        awaitparent.mount(prepareTarget(params.debug),{position:'first-child'});
        constchild=parent.component.comp;
        constoriginalDestroy=child.destroy;
        child.destroy=function(){
            child.destroy=originalDestroy;
            cleanUp();
            parent.destroy();
        };
        returnchild;
    }

    /**
     *CreateaControlPanelinstance,withanextensibleenvironmentand
     *itsrelatedControlPanelModel.Eventinterceptionisdonethrough
     *params['get-controller-query-params']andparams.search,forthetwo
     *availableeventhandlersrespectively.
     *@param{Object}[params={}]
     *@param{Object}[params.cpProps]
     *@param{Object}[params.cpModelConfig]
     *@param{boolean}[params.debug]
     *@param{Object}[params.env]
     *@returns{Object}usefulcontrolpaneltestingelements:
     * -controlPanel:thecontrolpanelinstance
     * -el:thecontrolpanelHTMLelement
     * -helpers:asuiteofboundhelpers(seeabovefunctionsforall
     *   availablehelpers)
     */
    asyncfunctioncreateControlPanel(params={}){
        constdebug=params.debug||false;
        constenv=makeTestEnvironment(params.env||{});
        constprops=Object.assign({
            action:{},
            fields:{},
        },params.cpProps);
        constglobalConfig=Object.assign({
            context:{},
            domain:[],
        },params.cpModelConfig);

        if(globalConfig.arch&&globalConfig.fields){
            constmodel="__mockmodel__";
            constserverParams={
                model,
                data:{[model]:{fields:globalConfig.fields,records:[]}},
            };
            constmockServer=awaittestUtilsMock.addMockEnvironment(
                newWidget(),
                serverParams,
            );
            const{arch,fields}=testUtilsMock.fieldsViewGet(mockServer,{
                arch:globalConfig.arch,
                fields:globalConfig.fields,
                model,
                viewOptions:{context:globalConfig.context},
            });
            Object.assign(globalConfig,{arch,fields});
        }

        globalConfig.env=env;
        constarchs=(globalConfig.arch&&{search:globalConfig.arch,})||{};
        const{ControlPanel:controlPanelInfo,}=ActionModel.extractArchInfo(archs);
        constextensions={
            ControlPanel:{archNodes:controlPanelInfo.children,},
        };

        classParentextendsComponent{
            constructor(){
                super();
                this.searchModel=newActionModel(extensions,globalConfig);
                this.state=useState(props);
                this.controlPanel=useRef("controlPanel");
            }
            asyncwillStart(){
                awaitthis.searchModel.load();
            }
            mounted(){
                if(params['get-controller-query-params']){
                    this.searchModel.on('get-controller-query-params',this,
                        params['get-controller-query-params']);
                }
                if(params.search){
                    this.searchModel.on('search',this,params.search);
                }
            }
        }
        Parent.components={ControlPanel};
        Parent.env=env;
        Parent.template=xml`
            <ControlPanel
                t-ref="controlPanel"
                t-props="state"
                searchModel="searchModel"
            />`;

        constparent=newParent();
        awaitparent.mount(prepareTarget(debug),{position:'first-child'});

        constcontrolPanel=parent.controlPanel.comp;
        constdestroy=controlPanel.destroy;
        controlPanel.destroy=function(){
            controlPanel.destroy=destroy;
            parent.destroy();
        };
        controlPanel.getQuery=()=>parent.searchModel.get('query');

        returncontrolPanel;
    }

    /**
     *CreateandreturnaninstanceofDebugManagerwithallrpcsgoingthrougha
     *mockmethod,assumingthattheuserhasaccessrights,andisanadmin.
     *
     *@param{Object}[params={}]
     *@returns{Promise<DebugManager>}
     */
    asyncfunctioncreateDebugManager(params={}){
        constmockRPC=params.mockRPC;
        Object.assign(params,{
            asyncmockRPC(route,args){
                if(args.method==='check_access_rights'){
                    returntrue;
                }
                if(args.method==='xmlid_to_res_id'){
                    returntrue;
                }
                if(mockRPC){
                    returnmockRPC.apply(this,arguments);
                }
                returnthis._super(...arguments);
            },
            session:{
                asyncuser_has_group(group){
                    if(group==='base.group_no_one'){
                        returntrue;
                    }
                    returnthis._super(...arguments);
                },
            },
        });
        constdebugManager=newDebugManager();
        awaittestUtilsMock.addMockEnvironment(debugManager,params);
        returndebugManager;
    }

    /**
     *Createamodelfromgivenparameters.
     *
     *@param{Object}paramsThisobjectwillbegiventoaddMockEnvironment,so
     *  anyparametersfromthatmethodapplies
     *@param{Class}params.Modelthemodelclasstouse
     *@returns{Model}
     */
    asyncfunctioncreateModel(params){
        constwidget=newWidget();

        constmodel=newparams.Model(widget,params);

        awaittestUtilsMock.addMockEnvironment(widget,params);

        //overridethemodel's'destroy'sothatitcalls'destroy'onthewidget
        //instead,asthewidgetistheparentofthemodelandthemockServer.
        model.destroy=function(){
            //removetheoverridetoproperlydestroythemodelwhenitwillbe
            //calledthesecondtime(byitsparent)
            deletemodel.destroy;
            widget.destroy();
        };

        returnmodel;
    }

    /**
     *Createawidgetparentfromgivenparameters.
     *
     *@param{Object}paramsThisobjectwillbegiventoaddMockEnvironment,so
     *  anyparametersfromthatmethodapplies
     *@returns{Promise<Widget>}
     */
    asyncfunctioncreateParent(params){
        constwidget=newWidget();
        awaittestUtilsMock.addMockEnvironment(widget,params);
        returnwidget;
    }

    /**
     *Createaviewfromvariousparameters. Here,aviewmeansajavascript
     *instanceofanAbstractViewclass,suchasaformview,alistviewora
     *kanbanview.
     *
     *Itreturnstheinstanceoftheview,properlycreated,withallrpcsgoing
     *throughamockmethodusingthedataobjectassource,andalreadyloaded/
     *started.
     *
     *@param{Object}params
     *@param{string}params.archthexml(arch)oftheviewtobeinstantiated
     *@param{any[]}[params.domain]theinitialdomainfortheview
     *@param{Object}[params.context]theinitialcontextfortheview
     *@param{string[]}[params.groupBy]theinitialgroupByfortheview
     *@param{Object[]}[params.favoriteFilters]thefavoritefiltersonewouldliketohaveatinitialization
     *@param{integer}[params.fieldDebounce=0]thedebouncevaluetouseforthe
     *  durationofthetest.
     *@param{AbstractView}params.Viewtheclassthatwillbeinstantiated
     *@param{string}params.modelamodelname,willbegiventotheview
     *@param{Object}params.interceptsanobjectwitheventnamesaskey,and
     *  callbackasvalue. Eachkey,valuewillbeusedtointercepttheevent.
     *  Notethatthisisparticularlyusefulifyouwanttointercepteventsgoing
     *  upintheinitprocessoftheview,becausetherearenootherwaytodoit
     *  afterthismethodreturns
     *@param{Boolean}[params.doNotDisableAHref=false]willnotpreventDefaultontheAelementsoftheviewiftrue.
     *   Defaultisfalse.
     *@returns{Promise<AbstractController>}theinstanceoftheview
     */
    asyncfunctioncreateView(params){
        consttarget=prepareTarget(params.debug);
        constwidget=newWidget();
        //reproducetheDOMenvironmentofviews
        constwebClient=Object.assign(document.createElement('div'),{
            className:'o_web_client',
        });
        constactionManager=Object.assign(document.createElement('div'),{
            className:'o_action_manager',
        });
        target.prepend(webClient);
        webClient.append(actionManager);

        //addmockenvironment:mockserver,session,fieldviewget,...
        constmockServer=awaittestUtilsMock.addMockEnvironment(widget,params);
        constviewInfo=testUtilsMock.fieldsViewGet(mockServer,params);

        params.server=mockServer;

        //createtheview
        constView=params.View;
        constmodelName=params.model||'foo';
        constdefaultAction={
            res_model:modelName,
            context:{},
        };
        constviewOptions=Object.assign({
            action:Object.assign(defaultAction,params.action),
            view:viewInfo,
            modelName:modelName,
            ids:'res_id'inparams?[params.res_id]:undefined,
            currentId:'res_id'inparams?params.res_id:undefined,
            domain:params.domain||[],
            context:params.context||{},
            hasActionMenus:false,
        },params.viewOptions);
        //patchtheViewtohandlethegroupBygiveninparams,aswecan'tgiveit
        //ininit(unlikethedomainandcontextwhichcanbesetintheaction)
        testUtilsMock.patch(View,{
            _updateMVCParams(){
                this._super(...arguments);
                this.loadParams.groupedBy=params.groupBy||viewOptions.groupBy||[];
                testUtilsMock.unpatch(View);
            },
        });
        if('hasSelectors'inparams){
            viewOptions.hasSelectors=params.hasSelectors;
        }

        letview;
        if(viewInfo.type==='controlpanel'||viewInfo.type==='search'){
            //TODO:probablyneedstocreateanhelperjustforthat
            view=newparams.View({viewInfo,modelName});
        }else{
            viewOptions.controlPanelFieldsView=Object.assign(testUtilsMock.fieldsViewGet(mockServer,{
                arch:params.archs&&params.archs[params.model+',false,search']||'<search/>',
                fields:viewInfo.fields,
                model:params.model,
            }),{favoriteFilters:params.favoriteFilters});

            view=newparams.View(viewInfo,viewOptions);
        }

        if(params.interceptsPropagate){
            for(constnameinparams.interceptsPropagate){
                testUtilsMock.intercept(widget,name,params.interceptsPropagate[name],true);
            }
        }

        //OverridetheActionMenusregistryunlesstoldotherwise.
        letactionMenusRegistry=ActionMenus.registry;
        if(params.actionMenusRegistry!==true){
            ActionMenus.registry=newRegistry();
        }

        constviewController=awaitview.getController(widget);
        //overridetheview's'destroy'sothatitcalls'destroy'onthewidget
        //instead,asthewidgetistheparentoftheviewandthemockServer.
        viewController.__destroy=viewController.destroy;
        viewController.destroy=function(){
            //removetheoverridetoproperlydestroytheviewControlleranditschildren
            //whenitwillbecalledthesecondtime(byitsparent)
            deleteviewController.destroy;
            widget.destroy();
            webClient.remove();
            if(params.actionMenusRegistry!==true){
                ActionMenus.registry=actionMenusRegistry;
            }
        };

        //rendertheviewControllerinafragmentastheymustbeabletorendercorrectly
        //withoutbeingintheDOM
        constfragment=document.createDocumentFragment();
        awaitviewController.appendTo(fragment);
        dom.prepend(actionManager,fragment,{
            callbacks:[{widget:viewController}],
            in_DOM:true,
        });

        if(!params.doNotDisableAHref){
            [...viewController.el.getElementsByTagName('A')].forEach(elem=>{
                elem.addEventListener('click',ev=>{
                    ev.preventDefault();
                });
            });
        }
        returnviewController;
    }

    /**
     *Getthetarget(fixtureorbody)ofthedocumentandaddseventlisteners
     *tointerceptcustomorDOMevents.
     *
     *@param{boolean}[debug=false]iftrue,thewidgetwillbeappendedin
     *     theDOM.Also,RPCsanduncaughtFlectraEventwillbelogged
     *@returns{HTMLElement}
     */
    functionprepareTarget(debug=false){
        document.body.classList.toggle('debug',debug);
        returndebug?document.body:document.getElementById('qunit-fixture');
    }

    return{
        createActionManager,
        createCalendarView,
        createComponent,
        createControlPanel,
        createDebugManager,
        createModel,
        createParent,
        createView,
        prepareTarget,
    };
});
