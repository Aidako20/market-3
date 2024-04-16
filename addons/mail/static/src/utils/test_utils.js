flectra.define('mail/static/src/utils/test_utils.js',function(require){
'usestrict';

constBusService=require('bus.BusService');

const{
    addMessagingToEnv,
    addTimeControlToEnv,
}=require('mail/static/src/env/test_env.js');
constModelManager=require('mail/static/src/model/model_manager.js');
constChatWindowService=require('mail/static/src/services/chat_window_service/chat_window_service.js');
constDialogService=require('mail/static/src/services/dialog_service/dialog_service.js');
const{nextTick}=require('mail/static/src/utils/utils.js');
constDiscussWidget=require('mail/static/src/widgets/discuss/discuss.js');
constMessagingMenuWidget=require('mail/static/src/widgets/messaging_menu/messaging_menu.js');
constMockModels=require('mail/static/tests/helpers/mock_models.js');

constAbstractStorageService=require('web.AbstractStorageService');
constNotificationService=require('web.NotificationService');
constRamStorage=require('web.RamStorage');
const{
    createActionManager,
    createView,
    makeTestPromise,
    mock:{
        addMockEnvironment,
        patch:legacyPatch,
        unpatch:legacyUnpatch,
    },
}=require('web.test_utils');
constWidget=require('web.Widget');

const{Component}=owl;

//------------------------------------------------------------------------------
//Private
//------------------------------------------------------------------------------

/**
 *Createafakeobject'dataTransfer',linkedtosomefiles,
 *whichispassedtodraganddropevents.
 *
 *@param{Object[]}files
 *@returns{Object}
 */
function_createFakeDataTransfer(files){
    return{
        dropEffect:'all',
        effectAllowed:'all',
        files,
        items:[],
        types:['Files'],
    };
}

/**
 *@private
 *@param{Object}callbacks
 *@param{function[]}callbacks.init
 *@param{function[]}callbacks.mount
 *@param{function[]}callbacks.destroy
 *@param{function[]}callbacks.return
 *@returns{Object}updatecallbacks
 */
function_useChatWindow(callbacks){
    const{
        mount:prevMount,
        destroy:prevDestroy,
    }=callbacks;
    returnObject.assign({},callbacks,{
        mount:prevMount.concat(async()=>{
            //triggermountingofchatwindowmanager
            awaitComponent.env.services['chat_window']._onWebClientReady();
        }),
        destroy:prevDestroy.concat(()=>{
            Component.env.services['chat_window'].destroy();
        }),
    });
}

/**
 *@private
 *@param{Object}callbacks
 *@param{function[]}callbacks.init
 *@param{function[]}callbacks.mount
 *@param{function[]}callbacks.destroy
 *@param{function[]}callbacks.return
 *@returns{Object}updatecallbacks
 */
function_useDialog(callbacks){
    const{
        mount:prevMount,
        destroy:prevDestroy,
    }=callbacks;
    returnObject.assign({},callbacks,{
        mount:prevMount.concat(async()=>{
            //triggermountingofdialogmanager
            awaitComponent.env.services['dialog']._onWebClientReady();
        }),
        destroy:prevDestroy.concat(()=>{
            Component.env.services['dialog'].destroy();
        }),
    });
}

/**
 *@private
 *@param{Object}callbacks
 *@param{function[]}callbacks.init
 *@param{function[]}callbacks.mount
 *@param{function[]}callbacks.destroy
 *@param{function[]}callbacks.return
 *@return{Object}updatecallbacks
 */
function_useDiscuss(callbacks){
    const{
        init:prevInit,
        mount:prevMount,
        return:prevReturn,
    }=callbacks;
    letdiscussWidget;
    conststate={
        autoOpenDiscuss:false,
        discussData:{},
    };
    returnObject.assign({},callbacks,{
        init:prevInit.concat(params=>{
            const{
                autoOpenDiscuss=state.autoOpenDiscuss,
                discuss:discussData=state.discussData
            }=params;
            Object.assign(state,{autoOpenDiscuss,discussData});
            deleteparams.autoOpenDiscuss;
            deleteparams.discuss;
        }),
        mount:prevMount.concat(asyncparams=>{
            const{selector,widget}=params;
            DiscussWidget.prototype._pushStateActionManager=()=>{};
            discussWidget=newDiscussWidget(widget,state.discussData);
            awaitdiscussWidget.appendTo($(selector));
            if(state.autoOpenDiscuss){
                awaitdiscussWidget.on_attach_callback();
            }
        }),
        return:prevReturn.concat(result=>{
            Object.assign(result,{discussWidget});
        }),
    });
}

/**
 *@private
 *@param{Object}callbacks
 *@param{function[]}callbacks.init
 *@param{function[]}callbacks.mount
 *@param{function[]}callbacks.destroy
 *@param{function[]}callbacks.return
 *@returns{Object}updatecallbacks
 */
function_useMessagingMenu(callbacks){
    const{
        mount:prevMount,
        return:prevReturn,
    }=callbacks;
    letmessagingMenuWidget;
    returnObject.assign({},callbacks,{
        mount:prevMount.concat(async({selector,widget})=>{
            messagingMenuWidget=newMessagingMenuWidget(widget,{});
            awaitmessagingMenuWidget.appendTo($(selector));
            awaitmessagingMenuWidget.on_attach_callback();
        }),
        return:prevReturn.concat(result=>{
            Object.assign(result,{messagingMenuWidget});
        }),
    });
}

//------------------------------------------------------------------------------
//Public:renderingtimers
//------------------------------------------------------------------------------

/**
 *Returnsapromiseresolvedatthenextanimationframe.
 *
 *@returns{Promise}
 */
functionnextAnimationFrame(){
    constrequestAnimationFrame=owl.Component.scheduler.requestAnimationFrame;
    returnnewPromise(function(resolve){
        setTimeout(()=>requestAnimationFrame(()=>resolve()));
    });
}

/**
 *ReturnsapromiseresolvedthenexttimeOWLstopsrendering.
 *
 *@param{function}funcfunctionwhich,whencalled,is
 *  expectedtotriggerOWLrender(s).
 *@param{number}[timeoutDelay=5000]inms
 *@returns{Promise}
 */
constafterNextRender=(function(){
    conststop=owl.Component.scheduler.stop;
    conststopPromises=[];

    owl.Component.scheduler.stop=function(){
        constwasRunning=this.isRunning;
        stop.call(this);
        if(wasRunning){
            while(stopPromises.length){
                stopPromises.pop().resolve();
            }
        }
    };

    asyncfunctionafterNextRender(func,timeoutDelay=5000){
        //Definethepotentialerrorsoutsideofthepromisetogetaproper
        //traceiftheyhappen.
        conststartError=newError("Timeout:therenderdidn'tstart.");
        conststopError=newError("Timeout:therenderdidn'tstop.");
        //Setupthetimeouttorejectifnorenderhappens.
        lettimeoutNoRender;
        consttimeoutProm=newPromise((resolve,reject)=>{
            timeoutNoRender=setTimeout(()=>{
                leterror=startError;
                if(owl.Component.scheduler.isRunning){
                    error=stopError;
                }
                console.error(error);
                reject(error);
            },timeoutDelay);
        });
        //Setupthepromisetoresolveifarenderhappens.
        constprom=makeTestPromise();
        stopPromises.push(prom);
        //Startthefunctionexpectedtotriggerarenderafterthepromise
        //hasbeenregisteredtonotmissanypotentialrender.
        constfuncRes=func();
        //Makethemrace(firsttoresolve/rejectwins).
        awaitPromise.race([prom,timeoutProm]);
        clearTimeout(timeoutNoRender);
        //Waittheendofthefunctiontoensureallpotentialeffectsare
        //takenintoaccountduringthefollowingverificationstep.
        awaitfuncRes;
        //Waitonemoreframetomakesurenonewrenderhasbeenqueued.
        awaitnextAnimationFrame();
        if(owl.Component.scheduler.isRunning){
            awaitafterNextRender(()=>{},timeoutDelay);
        }
    }

    returnafterNextRender;
})();


//------------------------------------------------------------------------------
//Public:testlifecycle
//------------------------------------------------------------------------------

functionbeforeEach(self){
    constdata=MockModels.generateData();

    data.partnerRootId=2;
    data['res.partner'].records.push({
        active:false,
        display_name:"FlectraBot",
        id:data.partnerRootId,
    });

    data.currentPartnerId=3;
    data['res.partner'].records.push({
        display_name:"YourCompany,MitchellAdmin",
        id:data.currentPartnerId,
        name:"MitchellAdmin",
    });
    data.currentUserId=2;
    data['res.users'].records.push({
        display_name:"YourCompany,MitchellAdmin",
        id:data.currentUserId,
        name:"MitchellAdmin",
        partner_id:data.currentPartnerId,
    });

    data.publicPartnerId=4;
    data['res.partner'].records.push({
        active:false,
        display_name:"Publicuser",
        id:data.publicPartnerId,
    });
    data.publicUserId=3;
    data['res.users'].records.push({
        active:false,
        display_name:"Publicuser",
        id:data.publicUserId,
        name:"Publicuser",
        partner_id:data.publicPartnerId,
    });

    constoriginals={
        '_.debounce':_.debounce,
        '_.throttle':_.throttle,
    };

    (functionpatch(){
        //patch_.debounceand_.throttletobefastandsynchronous
        _.debounce=_.identity;
        _.throttle=_.identity;
    })();

    functionunpatch(){
        _.debounce=originals['_.debounce'];
        _.throttle=originals['_.throttle'];
    }

    Object.assign(self,{
        components:[],
        data,
        unpatch,
        widget:undefined
    });
}

functionafterEach(self){
    if(self.env){
        self.env.bus.off('hide_home_menu',null);
        self.env.bus.off('show_home_menu',null);
        self.env.bus.off('will_hide_home_menu',null);
        self.env.bus.off('will_show_home_menu',null);
    }
    //Thecomponentsmustbedestroyedbeforethewidget,becausethe
    //widgetmightdestroythemodelsbeforedestroyingthecomponents,
    //andthecomponentsmightstillrelyonmessaging(orother)record(s).
    while(self.components.length>0){
        constcomponent=self.components.pop();
        component.destroy();
    }
    if(self.widget){
        self.widget.destroy();
        self.widget=undefined;
    }
    self.env=undefined;
    self.unpatch();
}

/**
 *CreatesandreturnsanewrootComponentwiththegivenpropsandmountsit
 *ontarget.
 *Assumesthatself.envissettothecorrectvalue.
 *Componentscreatedthiswayareautomaticallyregisteredforcleanupafter
 *thetest,whichwillhappenwhen`afterEach`iscalled.
 *
 *@param{Object}selfthecurrentQUnitinstance
 *@param{Class}Componentthecomponentclasstocreate
 *@param{Object}param2
 *@param{Object}[param2.props={}]forwardedtocomponentconstructor
 *@param{DOM.Element}param2.targetmounttargetforthecomponent
 *@returns{owl.Component}thenewcomponentinstance
 */
asyncfunctioncreateRootComponent(self,Component,{props={},target}){
    Component.env=self.env;
    constcomponent=newComponent(null,props);
    deleteComponent.env;
    self.components.push(component);
    awaitafterNextRender(()=>component.mount(target));
    returncomponent;
}

/**
 *Mainfunctionusedtomakeamockedenvironmentwithmockedmessagingenv.
 *
 *@param{Object}[param0={}]
 *@param{string}[param0.arch]makesonlysensewhen`param0.hasView`isset:
 *  thearchtouseincreateView.
 *@param{Object}[param0.archs]
 *@param{boolean}[param0.autoOpenDiscuss=false]makesonlysensewhen
 *  `param0.hasDiscuss`isset:determinewhethermounteddiscussshouldbe
 *  openinitially.
 *@param{boolean}[param0.debug=false]
 *@param{Object}[param0.data]makesonlysensewhen`param0.hasView`isset:
 *  thedatatouseincreateView.
 *@param{Object}[param0.discuss={}]makesonlysensewhen`param0.hasDiscuss`
 *  isset:providedatathatispassedtodiscusswidget(=clientaction)as
 *  2ndpositionalargument.
 *@param{Object}[param0.env={}]
 *@param{function}[param0.mockFetch]
 *@param{function}[param0.mockRPC]
 *@param{boolean}[param0.hasActionManager=false]ifset,use
 *  createActionManager.
 *@param{boolean}[param0.hasChatWindow=false]ifset,mountchatwindow
 *  service.
 *@param{boolean}[param0.hasDiscuss=false]ifset,mountdiscussapp.
 *@param{boolean}[param0.hasMessagingMenu=false]ifset,mountmessaging
 *  menu.
 *@param{boolean}[param0.hasTimeControl=false]ifset,allflowoftime
 *  with`env.browser.setTimeout`arefullycontrolledbytestitself.
 *    @seeaddTimeControlToEnvthatadds`advanceTime`functionin
 *    `env.testUtils`.
 *@param{boolean}[param0.hasView=false]ifset,usecreateViewtocreatea
 *  viewinsteadofagenericwidget.
 *@param{Deferred|Promise}[param0.messagingBeforeCreationDeferred=Promise.resolve()]
 *  Deferredthatlettestsblockmessagingcreationandsimulateresolution.
 *  Usefulfortestingworkingcomponentswhenmessagingisnotyetcreated.
 *@param{string}[param0.model]makesonlysensewhen`param0.hasView`isset:
 *  themodeltouseincreateView.
 *@param{integer}[param0.res_id]makesonlysensewhen`param0.hasView`isset:
 *  theres_idtouseincreateView.
 *@param{Object}[param0.services]
 *@param{Object}[param0.session]
 *@param{Object}[param0.View]makesonlysensewhen`param0.hasView`isset:
 *  theViewclasstouseincreateView.
 *@param{Object}[param0.viewOptions]makesonlysensewhen`param0.hasView`
 *  isset:theviewoptionstouseincreateView.
 *@param{Object}[param0.waitUntilEvent]
 *@param{String}[param0.waitUntilEvent.eventName]
 *@param{String}[param0.waitUntilEvent.message]
 *@param{function}[param0.waitUntilEvent.predicate]
 *@param{integer}[param0.waitUntilEvent.timeoutDelay]
 *@param{string}[param0.waitUntilMessagingCondition='initialized']Determines
 *  theconditionofmessagingwhenthisfunctionisresolved.
 *  Supportedvalues:['none','created','initialized'].
 *  -'none':thefunctionresolvesregardlessofwhethermessagingiscreated.
 *  -'created':thefunctionresolveswhenmessagingiscreated,but
 *    regardlessofwhethermessagingisinitialized.
 *  -'initialized'(default):thefunctionresolveswhenmessagingis
 *    initialized.
 *  Toguaranteemessagingisnotcreated,testshouldpassapendingdeferred
 *  asparamof`messagingBeforeCreationDeferred`.Tomakesuremessagingis
 *  notinitialized,testshouldmockRPC`mail/init_messaging`andblockits
 *  resolution.
 *@param{...Object}[param0.kwargs]
 *@throws{Error}incasesomeprovidedparametersarewrong,suchas
 *  `waitUntilMessagingCondition`.
 *@returns{Object}
 */
asyncfunctionstart(param0={}){
    letcallbacks={
        init:[],
        mount:[],
        destroy:[],
        return:[],
    };
    const{
        env:providedEnv,
        hasActionManager=false,
        hasChatWindow=false,
        hasDialog=false,
        hasDiscuss=false,
        hasMessagingMenu=false,
        hasTimeControl=false,
        hasView=false,
        messagingBeforeCreationDeferred=Promise.resolve(),
        waitUntilEvent,
        waitUntilMessagingCondition='initialized',
    }=param0;
    if(!['none','created','initialized'].includes(waitUntilMessagingCondition)){
        throwError(`Unknownparametervalue${waitUntilMessagingCondition}for'waitUntilMessaging'.`);
    }
    deleteparam0.env;
    deleteparam0.hasActionManager;
    deleteparam0.hasChatWindow;
    deleteparam0.hasDiscuss;
    deleteparam0.hasMessagingMenu;
    deleteparam0.hasTimeControl;
    deleteparam0.hasView;
    if(hasChatWindow){
        callbacks=_useChatWindow(callbacks);
    }
    if(hasDialog){
        callbacks=_useDialog(callbacks);
    }
    if(hasDiscuss){
        callbacks=_useDiscuss(callbacks);
    }
    if(hasMessagingMenu){
        callbacks=_useMessagingMenu(callbacks);
    }
    const{
        init:initCallbacks,
        mount:mountCallbacks,
        destroy:destroyCallbacks,
        return:returnCallbacks,
    }=callbacks;
    const{debug=false}=param0;
    initCallbacks.forEach(callback=>callback(param0));

    letenv=Object.assign(providedEnv||{});
    env.session=Object.assign(
        {
            is_bound:Promise.resolve(),
            url:s=>s,
        },
        env.session
    );
    env=addMessagingToEnv(env);
    if(hasTimeControl){
        env=addTimeControlToEnv(env);
    }

    constservices=Object.assign({},{
        bus_service:BusService.extend({
            _beep(){},//Donothing
            _poll(){},//Donothing
            _registerWindowUnload(){},//Donothing
            isFlectraFocused(){
                returntrue;
            },
            updateOption(){},
        }),
        chat_window:ChatWindowService.extend({
            _getParentNode(){
                returndocument.querySelector(debug?'body':'#qunit-fixture');
            },
            _listenHomeMenu:()=>{},
        }),
        dialog:DialogService.extend({
            _getParentNode(){
                returndocument.querySelector(debug?'body':'#qunit-fixture');
            },
            _listenHomeMenu:()=>{},
        }),
        local_storage:AbstractStorageService.extend({storage:newRamStorage()}),
        notification:NotificationService.extend(),
    },param0.services);

    constkwargs=Object.assign({},param0,{
        archs:Object.assign({},{
            'mail.message,false,search':'<search/>'
        },param0.archs),
        debug:param0.debug||false,
        services:Object.assign({},services,param0.services),
    },{env});
    letwidget;
    letmockServer;//onlyinbasicmode
    lettestEnv;
    constselector=debug?'body':'#qunit-fixture';
    if(hasView){
        widget=awaitcreateView(kwargs);
        legacyPatch(widget,{
            destroy(){
                destroyCallbacks.forEach(callback=>callback({widget}));
                this._super(...arguments);
                legacyUnpatch(widget);
                if(testEnv){
                    testEnv.destroyMessaging();
                }
            }
        });
    }elseif(hasActionManager){
        widget=awaitcreateActionManager(kwargs);
        legacyPatch(widget,{
            destroy(){
                destroyCallbacks.forEach(callback=>callback({widget}));
                this._super(...arguments);
                legacyUnpatch(widget);
                if(testEnv){
                    testEnv.destroyMessaging();
                }
            }
        });
    }else{
        constParent=Widget.extend({do_push_state(){}});
        constparent=newParent();
        mockServer=awaitaddMockEnvironment(parent,kwargs);
        widget=newWidget(parent);
        awaitwidget.appendTo($(selector));
        Object.assign(widget,{
            destroy(){
                deletewidget.destroy;
                destroyCallbacks.forEach(callback=>callback({widget}));
                parent.destroy();
                if(testEnv){
                    testEnv.destroyMessaging();
                }
            },
        });
    }

    testEnv=Component.env;

    /**
     *Componentscannotuseweb.bus,becausetheycannotuse
     *EventDispatcherMixin,andwebclientcannoteasilyaccessenv.
     *Communicationbetweenwebclientandcomponentsbycore.bus
     *(usablebywebclient)andmessagingBus(usablebycomponents),which
     *themessagingserviceactsasmediatorsinceitcaneasilyuseboth
     *kindsofbuses.
     */
    testEnv.bus.on(
        'hide_home_menu',
        null,
        ()=>testEnv.messagingBus.trigger('hide_home_menu')
    );
    testEnv.bus.on(
        'show_home_menu',
        null,
        ()=>testEnv.messagingBus.trigger('show_home_menu')
    );
    testEnv.bus.on(
        'will_hide_home_menu',
        null,
        ()=>testEnv.messagingBus.trigger('will_hide_home_menu')
    );
    testEnv.bus.on(
        'will_show_home_menu',
        null,
        ()=>testEnv.messagingBus.trigger('will_show_home_menu')
    );

    /**
     *Returnsapromiseresolvedaftertheexpectedeventisreceived.
     *
     *@param{Object}param0
     *@param{string}param0.eventNameeventtowait
     *@param{function}param0.funcfunctionwhich,whencalled,isexpectedto
     * triggertheevent
     *@param{string}[param0.message]assertionmessage
     *@param{function}[param0.predicate]predicatecalledwitheventdata.
     * Ifnotprovided,onlytheeventnamehastomatch.
     *@param{number}[param0.timeoutDelay=5000]howlongtowaitatmostinms
     *@returns{Promise}
     */
    constafterEvent=(async({eventName,func,message,predicate,timeoutDelay=5000})=>{
        //Setupthetimeouttorejectiftheeventisnottriggered.
        lettimeoutNoEvent;
        consttimeoutProm=newPromise((resolve,reject)=>{
            timeoutNoEvent=setTimeout(()=>{
                leterror=message
                    ?newError(message)
                    :newError(`Timeout:theevent${eventName}wasnottriggered.`);
                console.error(error);
                reject(error);
            },timeoutDelay);
        });
        //Setupthepromisetoresolveiftheeventistriggered.
        consteventProm=newPromise(resolve=>{
            testEnv.messagingBus.on(eventName,null,data=>{
                if(!predicate||predicate(data)){
                    resolve();
                }
            });
        });
        //Startthefunctionexpectedtotriggertheeventafterthe
        //promisehasbeenregisteredtonotmissanypotentialevent.
        constfuncRes=func();
        //Makethemrace(firsttoresolve/rejectwins).
        awaitPromise.race([eventProm,timeoutProm]);
        clearTimeout(timeoutNoEvent);
        //Iftheeventistriggeredbeforetheendoftheasyncfunction,
        //ensurethefunctionfinishesitsjobbeforereturning.
        awaitfuncRes;
    });

    constresult={
        afterEvent,
        env:testEnv,
        mockServer,
        widget,
    };

    conststart=async()=>{
        messagingBeforeCreationDeferred.then(async()=>{
            /**
             *Somemodelsrequiresessiondata,likelocaletextdirection
             *(dependsonfullyloadedtranslation).
             */
            awaitenv.session.is_bound;

            testEnv.modelManager=newModelManager(testEnv);
            testEnv.modelManager.start();
            /**
             *Createthemessagingsingletonrecord.
             */
            testEnv.messaging=testEnv.models['mail.messaging'].create();
            testEnv.messaging.start().then(()=>
                testEnv.messagingInitializedDeferred.resolve()
            );
            testEnv.messagingCreatedPromise.resolve();
        });
        if(waitUntilMessagingCondition==='created'){
            awaittestEnv.messagingCreatedPromise;
        }
        if(waitUntilMessagingCondition==='initialized'){
            awaittestEnv.messagingInitializedDeferred;
        }

        if(mountCallbacks.length>0){
            awaitafterNextRender(async()=>{
                awaitPromise.all(mountCallbacks.map(callback=>callback({selector,widget})));
            });
        }
        returnCallbacks.forEach(callback=>callback(result));
    };
    if(waitUntilEvent){
        awaitafterEvent(Object.assign({func:start},waitUntilEvent));
    }else{
        awaitstart();
    }
    returnresult;
}

//------------------------------------------------------------------------------
//Public:fileutilities
//------------------------------------------------------------------------------

/**
 *DragsomefilesoveraDOMelement
 *
 *@param{DOM.Element}el
 *@param{Object[]}filemusthavebeencreatebeforehand
 *  @seetestUtils.file.createFile
 */
functiondragenterFiles(el,files){
    constev=newEvent('dragenter',{bubbles:true});
    Object.defineProperty(ev,'dataTransfer',{
        value:_createFakeDataTransfer(files),
    });
    el.dispatchEvent(ev);
}

/**
 *DropsomefilesonaDOMelement
 *
 *@param{DOM.Element}el
 *@param{Object[]}filesmusthavebeencreatedbeforehand
 *  @seetestUtils.file.createFile
 */
functiondropFiles(el,files){
    constev=newEvent('drop',{bubbles:true});
    Object.defineProperty(ev,'dataTransfer',{
        value:_createFakeDataTransfer(files),
    });
    el.dispatchEvent(ev);
}

/**
 *PastesomefilesonaDOMelement
 *
 *@param{DOM.Element}el
 *@param{Object[]}filesmusthavebeencreatedbeforehand
 *  @seetestUtils.file.createFile
 */
functionpasteFiles(el,files){
    constev=newEvent('paste',{bubbles:true});
    Object.defineProperty(ev,'clipboardData',{
        value:_createFakeDataTransfer(files),
    });
    el.dispatchEvent(ev);
}

//------------------------------------------------------------------------------
//Public:DOMutilities
//------------------------------------------------------------------------------

/**
 *DetermineifaDOMelementhasbeentotallyscrolled
 *
 *A1pxmarginoferrorisgiventoaccomodatesubpixelroundingissuesand
 *Element.scrollHeightvaluebeingeitherintordecimal
 *
 *@param{DOM.Element}el
 *@returns{boolean}
 */
functionisScrolledToBottom(el){
    returnMath.abs(el.scrollHeight-el.clientHeight-el.scrollTop)<=1;
}

//------------------------------------------------------------------------------
//Export
//------------------------------------------------------------------------------

return{
    afterEach,
    afterNextRender,
    beforeEach,
    createRootComponent,
    dragenterFiles,
    dropFiles,
    isScrolledToBottom,
    nextAnimationFrame,
    nextTick,
    pasteFiles,
    start,
};

});
