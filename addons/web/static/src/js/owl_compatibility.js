flectra.define('web.OwlCompatibility',function(){
    "usestrict";

    /**
     *ThisfiledefinesthenecessarytoolsforthetransitionphasewhereFlectra
     *legacywidgetsandOwlcomponentswillcoexist.Therearetwopossible
     *scenarios:
     * 1)AnOwlcomponenthastoinstantiatelegacywidgets
     * 2)AlegacywidgethastoinstantiateOwlcomponents
     */

    const{Component,hooks,tags}=owl;
    const{useRef,useSubEnv}=hooks;
    const{xml}=tags;

    constwidgetSymbol=flectra.widgetSymbol;
    constchildren=newWeakMap();//associateslegacywidgetswiththeirOwlchildren

    /**
     *Case1)AnOwlcomponenthastoinstantiatelegacywidgets
     *----------------------------------------------------------
     *
     *TheComponentAdapterisanOwlcomponentmeanttobeusedasuniversal
     *adapterforOwlcomponentsthatembedFlectralegacywidgets(ordynamically
     *bothOwlcomponentsandFlectralegacywidgets),e.g.:
     *
     *                          OwlComponent
     *                                |
     *                        ComponentAdapter(Owlcomponent)
     *                                |
     *                      LegacyWidget(s)(orOwlcomponent(s))
     *
     *
     *Theadaptertakesthecomponent/widgetclassas'Component'prop,andthe
     *arguments(exceptfirstarg'parent')toinitializeitasprops.
     *Forinstance:
     *    <ComponentAdapterComponent="LegacyWidget"params="params"/>
     *willbetranslatedto:
     *    constLegacyWidget=this.props.Component;
     *    constlegacyWidget=newLegacyWidget(this,this.props.params);
     *
     *Ifmorethanoneargument(inadditionto'parent')isgiventoinitialize
     *thelegacywidget,theargumentsorder(toinitializethesubwidget)has
     *tobesomehowspecified.Therearetwoalternatives.Onecaneither(1)
     *specifytheprop'widgetArgs',correspondingtothearrayofarguments,
     *otherwise(2)asubclassofComponentAdapterhastobedefined.This
     *subclassmustoverridethe'widgetArgs'gettertotranslatearguments
     *receivedaspropstoanarrayofargumentsforthecalltoinit.
     *Forinstance:
     *    (1)<ComponentAdapterComponent="LegacyWidget"firstArg="a"secondArg="b"widgetsArgs="[a,b]"/>
     *    (2)classSpecificAdapterextendsComponentAdapter{
     *            getwidgetArgs(){
     *                return[this.props.firstArg,this.props.secondArg];
     *            }
     *        }
     *        <SpecificAdapterComponent="LegacyWidget"firstArg="a"secondArg="b"/>
     *
     *Ifthelegacywidgethastobeupdatedwhenpropschange,onemustdefine
     *asubclassofComponentAdaptertooverride'updateWidget'and'renderWidget'.The
     *'updateWidget'functiontakesthenextPropsasargument,andshouldupdatethe
     *internalstateofthewidget(mightbeasync,andreturnaPromise).
     *However,toensurethattheDOMisupdatedallatonce,itshouldn'tdo
     *are-rendering.Thisistheroleoffunction'renderWidget',whichwillbe
     *calledjustbeforepatchingtheDOM,andwhichthusmustbesynchronous.
     *Forinstance:
     *    classSpecificAdapterextendsComponentAdapter{
     *        updateWidget(nextProps){
     *            returnthis.widget.updateState(nextProps);
     *        }
     *        renderWidget(){
     *            returnthis.widget.render();
     *        }
     *    }
     */
    classComponentAdapterextendsComponent{
        /**
         *Createsthetemplateon-the-fly,dependingonthetypeofComponent
         *(legacywidgetorOwlcomponent).
         *
         *@override
         */
        constructor(parent,props){
            if(!props.Component){
                throwError(`ComponentAdapter:'Component'propismissing.`);
            }
            lettemplate;
            if(!(props.Component.prototypeinstanceofComponent)){
                template=tags.xml`<div/>`;
            }else{
                letpropsStr='';
                for(letpinprops){
                    if(p!=='Component'){
                        propsStr+=`${p}="props.${p}"`;
                    }
                }
                template=tags.xml`<tt-component="props.Component"${propsStr}/>`;
            }
            ComponentAdapter.template=template;
            super(...arguments);
            this.template=template;
            ComponentAdapter.template=null;

            this.widget=null;//widgetinstance,ifComponentisalegacywidget
        }

        /**
         *Startsthelegacywidget(notintheDOMyet)
         *
         *@override
         */
        willStart(){
            if(!(this.props.Component.prototypeinstanceofComponent)){
                this.widget=newthis.props.Component(this,...this.widgetArgs);
                returnthis.widget._widgetRenderAndInsert(()=>{});
            }
        }

        /**
         *Updatestheinternalstateofthelegacywidget(butdoesn'tre-render
         *ityet).
         *
         *@override
         */
        willUpdateProps(nextProps){
            if(this.widget){
                returnthis.updateWidget(nextProps);
            }
        }

        /**
         *Hooksjustbeforetheactualpatchtoreplacethefakedivinthe
         *vnodebytheactualnodeofthelegacywidget.Ifthewidgethasto
         *bere-render(becauseithaspreviouslybeenupdated),re-renderit.
         *Thismustbesynchronous.
         *
         *@override
         */
        __patch(target,vnode){
            if(this.widget){
                if(this.__owl__.vnode){//notatfirstrendering
                    this.renderWidget();
                }
                vnode.elm=this.widget.el;
            }
            constresult=super.__patch(...arguments);
            if(this.widget&&this.el!==this.widget.el){
                this.__owl__.vnode.elm=this.widget.el;
            }
            returnresult;
        }

        /**
         *@override
         */
        mounted(){
            if(this.widget&&this.widget.on_attach_callback){
                this.widget.on_attach_callback();
            }
        }

        /**
         *@override
         */
        willUnmount(){
            if(this.widget&&this.widget.on_detach_callback){
                this.widget.on_detach_callback();
            }
        }

        /**
         *@override
         */
        __destroy(){
            super.__destroy(...arguments);
            if(this.widget){
                this.widget.destroy();
            }
        }

        /**
         *Getterthattranslatestheprops(except'Component')intothearray
         *ofargumentsusedtoinitializethelegacywidget.
         *
         *Mustbeoverridenifatleasttwoprops(otherthatComponent)are
         *given.
         *
         *@returns{Array}
         */
        getwidgetArgs(){
            if(this.props.widgetArgs){
                returnthis.props.widgetArgs;
            }
            constargs=Object.keys(this.props);
            args.splice(args.indexOf('Component'),1);
            if(args.length>1){
                thrownewError(`ComponentAdapterhasmorethan1argument,'widgetArgs'mustbeoverriden.`);
            }
            returnargs.map(a=>this.props[a]);
        }

        /**
         *Canbeoverridentoupdatetheinternalstateofthewidgetwhenprops
         *change.ToensurethattheDOMisupdatedatonce,thisfunctionshould
         *notdoare-rendering(whichshouldbedoneby'render'instead).
         *
         *@param{Object}nextProps
         *@returns{Promise}
         */
        updateWidget(/*nextProps*/){
            if(this.env.isDebug('assets')){
                console.warn(`ComponentAdapter:Widgetcouldnotbeupdated,maybeoverride'updateWidget'function?`);
            }
        }

        /**
         *Canbeoverridentore-renderthewidgetafteranupdate.This
         *functionwillbecalledjustbeforepatchintheDOM,s.t.theDOMis
         *updatedatonce.Itmustbesynchronous
         */
        renderWidget(){
            if(this.env.isDebug('assets')){
                console.warn(`ComponentAdapter:Widgetcouldnotbere-rendered,maybeoverride'renderWidget'function?`);
            }
        }

        /**
         *Mocks_trigger_uptoredirectFlectralegacyeventstoOWLevents.
         *
         *@private
         *@param{FlectraEvent}ev
         */
        _trigger_up(ev){
            constevType=ev.name;
            constpayload=ev.data;
            if(evType==='call_service'){
                letargs=payload.args||[];
                if(payload.service==='ajax'&&payload.method==='rpc'){
                    //ajaxserviceusesanextra'target'argumentforrpc
                    args=args.concat(ev.target);
                }
                constservice=this.env.services[payload.service];
                constresult=service[payload.method].apply(service,args);
                payload.callback(result);
            }elseif(evType==='get_session'){
                if(payload.callback){
                    payload.callback(this.env.session);
                }
            }elseif(evType==='load_views'){
                constparams={
                    model:payload.modelName,
                    context:payload.context,
                    views_descr:payload.views,
                };
                this.env.dataManager
                    .load_views(params,payload.options||{})
                    .then(payload.on_success);
            }elseif(evType==='load_filters'){
                returnthis.env.dataManager
                    .load_filters(payload)
                    .then(payload.on_success);
            }else{
                payload.__targetWidget=ev.target;
                this.trigger(evType.replace(/_/g,'-'),payload);
            }
        }
    }


    /**
     *Case2)AlegacywidgethastoinstantiateOwlcomponents
     *---------------------------------------------------------
     *
     *TheWidgetAdapterMixinandtheComponentWrapperaremeanttobeused
     *togetherwhenanFlectralegacywidgetneedstoinstantiateOwlcomponents.
     *Inthiscase,thewidgets/componentshierarchywouldlooklike:
     *
     *            LegacyWidget+WidgetAdapterMixin
     *                         |
     *                ComponentWrapper(Owlcomponent)
     *                         |
     *                   OwlComponent
     *
     *Inthiscase,theparentlegacywidgetmustusetheWidgetAdapterMixin,
     *whichensuresthatOwlhooks(mounted,willUnmount,destroy...)are
     *properlycalledonthesubcomponents.Moreover,itmustinstantiatea
     *ComponentWrapper,andprovideittheOwlcomponentclasstousealongside
     *itsprops.ThiswrapperwillensurethattheOwlcomponentwillbe
     *correctlyupdated(withwillUpdateProps)likeitwouldbeifitwasembed
     *inanOwlhierarchy.Moreover,thiswrapperautomaticallyredirectsall
     *eventstriggeredbytheOwlcomponent(oritsdescendants)tolegacy
     *customevents(trigger_up)ontheparentlegacywidget.

     *Forexample:
     *     classMyComponentextendsComponent{}
     *     MyComponent.template=xml`<div>Owlcomponentwithvalue<tt-esc="props.value"/></div>`;
     *     constMyWidget=Widget.extend(WidgetAdapterMixin,{
     *         start(){
     *             this.component=newComponentWrapper(this,MyComponent,{value:44});
     *             returnthis.component.mount(this.el);
     *         },
     *         update(){
     *             returnthis.component.update({value:45});
     *         },
     *     });
     */
    constWidgetAdapterMixin={
        /**
         *Callson_attach_callbackoneachchildComponentWrapper,whichwill
         *call__callMountedoneachsubcomponent(recursively),tomarkthem
         *asmounted.
         */
        on_attach_callback(){
            for(constcomponentofchildren.get(this)||[]){
                component.on_attach_callback();
            }
        },
        /**
         *Callson_detach_callbackoneachchildComponentWrapper,whichwill
         *call__callWillUnmounttomarkitselfanditschildrenasnolonger
         *mounted.
         */
        on_detach_callback(){
            for(constcomponentofchildren.get(this)||[]){
                component.on_detach_callback();
            }
        },
        /**
         *Destroyseachsubcomponentwhenthewidgetisdestroyed.Wecallthe
         *private__destroyfunctionasthereisnoneedtoremovetheelfrom
         *theDOM(willberemovedalongsidethiswidget).
         */
        destroy(){
            for(constcomponentofchildren.get(this)||[]){
                component.__destroy();
            }
            children.delete(this);
        },
    };
    classComponentWrapperextendsComponent{
        /**
         *Storesthereferenceoftheinstanceintheparent(in__components).
         *Alsocreatesasubenvironmentwithafunctionthatwillbecalled
         *justbeforeeventsaretriggered(seecomponent_extension.js).This
         *allowstoaddDOMeventlistenerson-the-fly,toredirectthoseOwl
         *custom(yetDOM)eventstolegacycustomevents(trigger_up).
         *
         *@override
         *@param{Widget|null}parent
         *@param{Component}ComponentthisisaClass,notaninstance
         *@param{Object}props
         */
        constructor(parent,Component,props){
            if(parentinstanceofComponent){
                thrownewError('ComponentWrappermustbeusedwithalegacyWidgetasparent');
            }
            super(null,props);
            if(parent){
                this._register(parent);
            }
            useSubEnv({
                [widgetSymbol]:this._addListener.bind(this)
            });

            this.parentWidget=parent;
            this.Component=Component;
            this.props=props||{};
            this._handledEvents=newSet();//Owleventsweareredirecting

            this.componentRef=useRef("component");
        }

        /**
         *Calls__callMountedonitselfandoneachsubcomponent(asthis
         *functionisn'trecursive)whenthecomponentisappendedintotheDOM.
         */
        on_attach_callback(){
            functionrecursiveCallMounted(component){
                const{status,currentFiber}=component.__owl__;

                if(status===2&&currentFiber&&!currentFiber.isCompleted){
                    //thecomponentisrenderedbutanotherrenderingisbeingdone
                    //itwouldbefoolishtodeclarethecomponentandchildrenasmounted
                    return;
                }
                if(
                   status!==2/*RENDERED*/&&
                   status!==3/*MOUNTED*/&&
                   status!==4/*UNMOUNTED*/
                ){
                    //Avoidcallingmountedonacomponentthatisnoteven
                    //rendered.Doingotherwisewillleadtoacrashifa
                    //specificmountedcallbackislegitimatelyrelyingonthe
                    //componentbeingmounted.
                    return;
                }
                for(constkeyincomponent.__owl__.children){
                    recursiveCallMounted(component.__owl__.children[key]);
                }
                component.__callMounted();
            }
            recursiveCallMounted(this);
        }
        /**
         *Calls__callWillUnmounttonotifythecomponentitwillbeunmounted.
         */
        on_detach_callback(){
            this.__callWillUnmount();
        }

        /**
         *Overridestoremovethereferencetothiscomponentintheparent.
         *
         *@override
         */
        destroy(){
            if(this.parentWidget){
                constparentChildren=children.get(this.parentWidget);
                if(parentChildren){
                    constindex=parentChildren.indexOf(this);
                    children.get(this.parentWidget).splice(index,1);
                }
            }
            super.destroy();
        }

        /**
         *Changestheparentofthewrappercomponent.Thisisafunctionofthe
         *legacywidgets(ParentedMixin),sowehavetohandleitsomeway.
         *Itsimplyremovesthereferenceofthiscomponentinthecurrent
         *parent(iftherewasone),andaddsthereferencetothenewone.
         *
         *Wehaveatleastoneusecaseforthis:inviews,therendereris
         *instantiatedwithoutparent,thenacontrollerisinstantiatedwith
         *therendererasargument,andfinally,setParentiscalledtosetthe
         *controllerasparentoftherenderer.ThisimpliesthatOwlrenderers
         *can'ttriggereventsintheirconstructor.
         *
         *@param{Widget}parent
         */
        setParent(parent){
            if(parentinstanceofComponent){
                thrownewError('ComponentWrappermustbeusedwithalegacyWidgetasparent');
            }
            this._register(parent);
            if(this.parentWidget){
                constparentChildren=children.get(this.parentWidget);
                parentChildren.splice(parentChildren.indexOf(this),1);
            }
            this.parentWidget=parent;
        }

        /**
         *Updatesthepropsandre-renderthecomponent.
         *
         *@async
         *@param{Object}props
         *@return{Promise}
         */
        asyncupdate(props={}){
            if(this.__owl__.status===5/*destroyed*/){
                returnnewPromise(()=>{});
            }

            Object.assign(this.props,props);

            letprom;
            if(this.__owl__.status===3/*mounted*/){
                prom=this.render();
            }else{
                //wemaynotbeintheDOM,butactuallywanttoberedrawn
                //(e.g.weweredetachedfromtheDOM,andnowwe'regoingto
                //bere-attached,butweneedtobereloadedfirst).Inthis
                //case,wehavetocall'mount'asOwlwouldskiptherendering
                //ifwesimplycallrender.
                prom=this.mount(...this._mountArgs);
            }
            returnprom;
        }

        /**
         *AddsaneventhandlerthatwillredirectthegivenOwleventtoan
         *Flectralegacyevent.Thisfunctioniscalledjustbeforetheeventis
         *actuallytriggered.
         *
         *@private
         *@param{string}evType
         */
        _addListener(evType){
            if(this.parentWidget&&!this._handledEvents.has(evType)){
                this._handledEvents.add(evType);
                this.el.addEventListener(evType,ev=>{
                    //astheWrappeComponenthasthesamerootnodeasthe
                    //actualsubComponent,wehavetocheckthattheevent
                    //hasn'tbeenstoppedbythatcomponent(itwouldnaturally
                    //callstopPropagation,whereasitshouldactuallycall
                    //stopImmediatePropagationtopreventfromgettinghere)
                    if(!ev.cancelBubble){
                        ev.stopPropagation();
                        constdetail=Object.assign({},ev.detail,{
                            __originalComponent:ev.originalComponent,
                        });
                        this.parentWidget.trigger_up(ev.type.replace(/-/g,'_'),detail);
                    }
                });
            }
        }

        /**
         *Registersthisinstanceasachildofthegivenparentinthe
         *'children'weakMap.
         *
         *@private
         *@param{Widget}parent
         */
        _register(parent){
            letparentChildren=children.get(parent);
            if(!parentChildren){
                parentChildren=[];
                children.set(parent,parentChildren);
            }
            parentChildren.push(this);
        }
        /**
         *Storesmounttargetandpositionatfirstmount.Thatway,whenupdating
         *whileoutofDOM,weknowwhereandhowtoremount.
         *@seeupdate()
         *@override
         */
        asyncmount(target,options){
            if(options&&options.position==='self'){
                thrownewError(
                    'Unsupportedposition:"self"isnotallowedforwrappercomponents.'+
                    'ContacttheJSFrameworkteamoropenanissueifyourusecaseisrelevant.'
                );
            }
            this._mountArgs=arguments;
            returnsuper.mount(...arguments);
        }
    }
    ComponentWrapper.template=xml`<tt-component="Component"t-props="props"t-ref="component"/>`;

    return{
        ComponentAdapter,
        ComponentWrapper,
        WidgetAdapterMixin,
    };
});
