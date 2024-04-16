flectra.define('web.public.widget',function(require){
'usestrict';

/**
 *ProvidesawaytostartJScodeforpubliccontents.
 */

varClass=require('web.Class');
vardom=require('web.dom');
varmixins=require('web.mixins');
varsession=require('web.session');
varWidget=require('web.Widget');

/**
 *SpecializedWidgetwhichautomaticallyinstantiateschildwidgetstoattach
 *tointernalDOMelementsonceitisstarted.Thewidgetstoinstantiateare
 *knownthankstoalinkedregistrywhichcontainsinfoaboutthewidget
 *classesandjQueryselectorstousetofindtheelementstoattachthemto.
 *
 *@todoMergewith'PublicWidget'?
 */
varRootWidget=Widget.extend({
    custom_events:_.extend({},Widget.prototype.custom_events||{},{
        'registry_update':'_onRegistryUpdate',
        'get_session':'_onGetSession',
    }),
    /**
     *@constructor
     */
    init:function(){
        this._super.apply(this,arguments);
        this._widgets=[];
        this._listenToUpdates=false;
        this._getRegistry().setParent(this);
    },
    /**
     *@override
     *@see_attachComponents
     */
    start:function(){
        vardefs=[this._super.apply(this,arguments)];

        defs.push(this._attachComponents());
        this._listenToUpdates=true;

        returnPromise.all(defs);
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Instantiatesachildwidgetaccordingtothegivenregistrydata.
     *
     *@private
     *@param{Object}childInfo
     *@param{function}childInfo.Widget-thewidgetclasstoinstantiate
     *@param{string}childInfo.selector
     *       thejQueryselectortousetofindtheinternalDOMelementwhich
     *       needstobeattachedtotheinstantiatedwidget
     *@param{jQuery}[$from]-onlycheckDOMelementswhicharedescendantof
     *                        thegivenone.Ifnotgiven,usethis.$el.
     *@returns{Deferred}
     */
    _attachComponent:function(childInfo,$from){
        varself=this;
        var$elements=dom.cssFind($from||this.$el,childInfo.selector);
        vardefs=_.map($elements,function(element){
            varw=newchildInfo.Widget(self);
            self._widgets.push(w);
            returnw.attachTo(element);
        });
        returnPromise.all(defs);
    },
    /**
     *Instantiatesthechildwidgetsthatneedtobeaccordingtothelinked
     *registry.
     *
     *@private
     *@param{jQuery}[$from]-onlycheckDOMelementswhicharedescendantof
     *                        thegivenone.Ifnotgiven,usethis.$el.
     *@returns{Deferred}
     */
    _attachComponents:function($from){
        varself=this;
        varchildInfos=this._getRegistry().get();
        vardefs=_.map(childInfos,function(childInfo){
            returnself._attachComponent(childInfo,$from);
        });
        returnPromise.all(defs);
    },
    /**
     *Returnsthe`RootWidgetRegistry`instancethatislinkedtothis
     *`RootWidget`instance.
     *
     *@abstract
     *@private
     *@returns{RootWidgetRegistry}
     */
    _getRegistry:function(){},

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Getthecuruentsessionmodule.
     *
     *@private
     *@param{FlectraEvent}ev
     */
    _onGetSession:function(event){
        if(event.data.callback){
            event.data.callback(session);
        }
    },
    /**
     *Calledwhenthelinkedregistryisupdatedafterthis`RootWidget`
     *
     *@private
     *@param{FlectraEvent}ev
     */
    _onRegistryUpdate:function(ev){
        ev.stopPropagation();
        if(this._listenToUpdates){
            this._attachComponent(ev.data);
        }
    },
});

varRootWidgetRegistry=Class.extend(mixins.EventDispatcherMixin,{
    /**
     *@constructor
     */
    init:function(){
        mixins.EventDispatcherMixin.init.call(this);
        this._registry=[];
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *Addsanelementtotheregistry(infoofwhatandhowtoinstantiate).
     *
     *@param{function}Widget-thewidgetclasstoinstantiate
     *@param{string}selector
     *       thejQueryselectortousetofindtheinternalDOMelementwhich
     *       needstobeattachedtotheinstantiatedwidget
     */
    add:function(Widget,selector){
        varregistryInfo={
            Widget:Widget,
            selector:selector,
        };
        this._registry.push(registryInfo);
        this.trigger_up('registry_update',registryInfo);
    },
    /**
     *Retrievesalltheregistryelements.
     */
    get:function(){
        returnthis._registry;
    },
});

//::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

/**
 *ProvidesawayforexecutingcodeonceawebsiteDOMelementisloadedinthe
 *dom.
 */
varPublicWidget=Widget.extend({
    /**
     *Theselectorattribute,ifdefined,allowstoautomaticallycreatean
     *instanceofthiswidgetonpageloadforeachDOMelementwhich
     *matchesthisselector.The`PublicWidget.$target`elementwillthenbe
     *thatparticularDOMelement.Thisshouldbethemainwayofinstantiating
     *`PublicWidget`elements.
     *
     *@tododonotmakethispartoftheWidgetbutratheraninfotogivewhen
     *registeringthewidget.
     */
    selector:false,
    /**
     *Extensionof@seeWidget.events
     *
     *Adescriptionoftheeventhandlerstobind/delegateoncethewidget
     *hasbeenrendered::
     *
     *  'click.hello.world':'async_onHelloWorldClick',
     *    _^_     _^_          _^_       _^_
     *     |       |            |         |
     *     | (Optional)jQuery  | Handlermethodname
     *     | delegateselector  |
     *     |                     |_(Optional)spaceseparatedoptions
     *     |                         *async:usetheautomaticsystem
     *     |_Eventnamewith          makinghandlerspromise-ready(see
     *        potentialjQuery         makeButtonHandler,makeAsyncHandler)
     *        namespaces
     *
     *Note:thevaluesmaybereplacedbyafunctiondeclaration.Thisis
     *howeveradeprecatedbehavior.
     *
     *@type{Object}
     */
    events:{},

    /**
     *@constructor
     *@param{Object}parent
     *@param{Object}[options]
     */
    init:function(parent,options){
        this._super.apply(this,arguments);
        this.options=options||{};
    },
    /**
     *Destroysthewidgetandbasicallyrestoresthetargettothestateit
     *wasbeforethestartmethodwascalled(unlikestandardwidget,the
     *associated$elDOMisnotremoved,ifthiswasinstantiatedthankstothe
     *selectorproperty).
     */
    destroy:function(){
        if(this.selector){
            var$oldel=this.$el;
            //Thedifferencewiththedefaultbehavioristhatweunsetthe
            //associatedelementfirstsothat:
            //1)itseventsareunbinded
            //2)itisnotremovedfromtheDOM
            this.setElement(null);
        }

        this._super.apply(this,arguments);

        if(this.selector){
            //Reassignthevariablesafterwardstoallowextensionstousethem
            //aftercallingthe_supermethod
            this.$el=$oldel;
            this.el=$oldel[0];
            this.$target=this.$el;
            this.target=this.el;
        }
    },
    /**
     *@override
     */
    setElement:function(){
        this._super.apply(this,arguments);
        if(this.selector){
            this.$target=this.$el;
            this.target=this.el;
        }
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@seethis.events
     *@override
     */
    _delegateEvents:function(){
        varself=this;
        varoriginalEvents=this.events;

        varevents={};
        _.each(this.events,function(method,event){
            //Ifthemethodisafunction,usethedefaultWidgetsystem
            if(typeofmethod!=='string'){
                events[event]=method;
                return;
            }
            //Ifthemethodisonlyafunctionnamewithoutoptions,usethe
            //defaultWidgetsystem
            varmethodOptions=method.split('');
            if(methodOptions.length<=1){
                events[event]=method;
                return;
            }
            //Ifthemethodhasnomeaningfuloptions,usethedefaultWidget
            //system
            varisAsync=_.contains(methodOptions,'async');
            if(!isAsync){
                events[event]=method;
                return;
            }

            method=self.proxy(methodOptions[methodOptions.length-1]);
            if(_.str.startsWith(event,'click')){
                //Protectclickhandlertobecalledmultipletimesby
                //mistakebytheuserandaddavisualdisablingeffect
                //forbuttons.
                method=dom.makeButtonHandler(method);
            }else{
                //Protectallhandlerstoberecalledwhiletheprevious
                //asynchandlercallisnotfinished.
                method=dom.makeAsyncHandler(method);
            }
            events[event]=method;
        });

        this.events=events;
        this._super.apply(this,arguments);
        this.events=originalEvents;
    },
    /**
     *@private
     *@param{boolean}[extra=false]
     *@param{Object}[extraContext]
     *@returns{Object}
     */
    _getContext:function(extra,extraContext){
        varcontext;
        this.trigger_up('context_get',{
            extra:extra||false,
            context:extraContext,
            callback:function(ctx){
                context=ctx;
            },
        });
        returncontext;
    },
});

//::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

/**
 *Theregistryobjectcontainsthelistofwidgetsthatshouldbeinstantiated
 *thankstotheirselectorpropertyifany.
 */
varregistry={};

/**
 *Thisisafixforappledevice(<=IPhone4,IPad2)
 *Standardbootstraprequiresdata-toggle='collapse'elementtobe<a/>tags.
 *Unfortunatlysomelayoutsusea<div/>taginstead.Thefixforcesanempty
 *clickhandleronthesediv,whichallowsstandardbootstraptowork.
 */
registry._fixAppleCollapse=PublicWidget.extend({
    selector:'div[data-toggle="collapse"]',
    events:{
        'click':function(){},
    },
});

//TODO:removethiscodeinmasterandputitinitsownfile.
registry.login=PublicWidget.extend({
    selector:'.oe_login_form',
    events:{
        'submit':'_onSubmit',
    },

    //-------------------------------------------------------------------------
    //Handlers
    //-------------------------------------------------------------------------

    /**
     *Preventstheuserfromcrazyclicking:
     *GivesthebuttonaloadingeffectifpreventDefaultwasnotalready
     *calledandmodifiesthepreventDefaultfunctionoftheeventsothatthe
     *loadingeffectisremovedifpreventDefault()iscalledinafollowing
     *customization.
     *
     *@private
     *@param{Event}ev
     */
    _onSubmit(ev){
        if(!ev.isDefaultPrevented()){
            constbtnEl=ev.currentTarget.querySelector('button[type="submit"]');
            constremoveLoadingEffect=dom.addButtonLoadingEffect(btnEl);
            constoldPreventDefault=ev.preventDefault.bind(ev);
            ev.preventDefault=()=>{
                removeLoadingEffect();
                oldPreventDefault();
            };
        }
    },
});

return{
    RootWidget:RootWidget,
    RootWidgetRegistry:RootWidgetRegistry,
    Widget:PublicWidget,
    registry:registry,
};
});
