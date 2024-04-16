flectra.define('web.Widget',function(require){
"usestrict";

varajax=require('web.ajax');
varcore=require('web.core');
varmixins=require('web.mixins');
varServicesMixin=require('web.ServicesMixin');

/**
 *Baseclassforallvisualcomponents.Providesalotoffunctionshelpful
 *forthemanagementofapartoftheDOM.
 *
 *Widgethandles:
 *
 *-RenderingwithQWeb.
 *-Life-cyclemanagementandparenting(whenaparentisdestroyed,allits
 *  childrenaredestroyedtoo).
 *-InsertioninDOM.
 *
 ***GuidetocreateimplementationsoftheWidgetclass**
 *
 *Hereisasamplechildclass::
 *
 *    varMyWidget=Widget.extend({
 *        //thenameoftheQWebtemplatetouseforrendering
 *        template:"MyQWebTemplate",
 *
 *        init:function(parent){
 *            this._super(parent);
 *            //stuffthatyouwanttoinitbeforetherendering
 *        },
 *        willStart:function(){
 *            //asyncworkthatneedtobedonebeforethewidgetisready
 *            //thismethodshouldreturnapromise
 *        },
 *        start:function(){
 *            //stuffyouwanttomakeaftertherendering,`this.$el`holdsacorrectvalue
 *            this.$(".my_button").click(/*anexampleofeventbinding*/);
 *
 *            //ifyouhavesomeasynchronousoperations,it'sagoodideatoreturn
 *            //apromiseinstart().Notethatthisisquiterare,andifyou
 *            //needtofetchsomedata,thisshouldprobablybedoneinthe
 *            //willStartmethod
 *            varpromise=this._rpc(...);
 *            returnpromise;
 *        }
 *    });
 *
 *Nowthisclasscansimplybeusedwiththefollowingsyntax::
 *
 *    varmyWidget=newMyWidget(this);
 *    myWidget.appendTo($(".some-div"));
 *
 *Withthesetwolines,theMyWidgetinstancewasinitialized,rendered,
 *insertedintotheDOMinsidethe``.some-div``divanditseventswere
 *bound.
 *
 *Andofcourse,whenyoudon'tneedthatwidgetanymore,justdo::
 *
 *    myWidget.destroy();
 *
 *Thatwillkillthewidgetinacleanwayanderaseitscontentfromthedom.
 */

varWidget=core.Class.extend(mixins.PropertiesMixin,ServicesMixin,{
    //Backbone-ishAPI
    tagName:'div',
    id:null,
    className:null,
    attributes:{},
    events:{},
    /**
     *ThenameoftheQWebtemplatethatwillbeusedforrendering.Mustbe
     *redefinedinsubclassesorthedefaultrender()methodcannotbeused.
     *
     *@type{null|string}
     */
    template:null,
    /**
     *Listofpathstoxmlfilesthatneedtobeloadedbeforethewidgetcan
     *berendered.Thiswillnotinduceloadinganythingthathasalreadybeen
     *loaded.
     *
     *@type{null|string[]}
     */
    xmlDependencies:null,
    /**
     *Listofpathstocssfilesthatneedtobeloadedbeforethewidgetcan
     *berendered.Thiswillnotinduceloadinganythingthathasalreadybeen
     *loaded.
     *
     *@type{null|string[]}
     */
    cssLibs:null,
    /**
     *Listofpathstojsfilesthatneedtobeloadedbeforethewidgetcan
     *berendered.Thiswillnotinduceloadinganythingthathasalreadybeen
     *loaded.
     *
     *@type{null|string[]}
     */
    jsLibs:null,
    /**
     *ListofxmlIDthatneedtobeloadedbeforethewidgetcanberendered.
     *Thecontentcss(linkfileorstyletag)andjs(fileorinline)ofthe
     *assetsareloaded.
     *Thiswillnotinduceloadinganythingthathasalreadybeen
     *loaded.
     *
     *@type{null|string[]}
     */
    assetLibs:null,

    /**
     *Constructsthewidgetandsetsitsparentifaparentisgiven.
     *
     *@param{Widget|null}parentBindsthecurrentinstancetothegivenWidget
     *  instance.Whenthatwidgetisdestroyedbycallingdestroy(),the
     *  currentinstancewillbedestroyedtoo.Canbenull.
     */
    init:function(parent){
        mixins.PropertiesMixin.init.call(this);
        this.setParent(parent);
        //Bindon_/do_*methodstothis
        //Wemightremovethisautomaticbindinginthefuture
        for(varnameinthis){
            if(typeof(this[name])==="function"){
                if((/^on_|^do_/).test(name)){
                    this[name]=this[name].bind(this);
                }
            }
        }
    },
    /**
     *Methodcalledbetween@seeinitand@seestart.Performsasynchronous
     *callsrequiredbytherenderingandthestartmethod.
     *
     *ThismethodshouldreturnaPromosewhichisresolvedwhenstartcanbe
     *executed.
     *
     *@returns{Promise}
     */
    willStart:function(){
        varproms=[];
        if(this.xmlDependencies){
            proms.push.apply(proms,_.map(this.xmlDependencies,function(xmlPath){
                returnajax.loadXML(xmlPath,core.qweb);
            }));
        }
        if(this.jsLibs||this.cssLibs||this.assetLibs){
            proms.push(this._loadLibs(this));
        }
        returnPromise.all(proms);
    },
    /**
     *Methodcalledafterrendering.Mostlyusedtobindactions,perform
     *asynchronouscalls,etc...
     *
     *Byconvention,thismethodshouldreturnanobjectthatcanbepassedto
     *Promise.resolve()toinformthecallerwhenthiswidgethasbeeninitialized.
     *
     *Notethat,forhistoricreasons,manywidgetsstilldoworkinthestart
     *methodthatwouldbemoresuitedtothewillStartmethod.
     *
     *@returns{Promise}
     */
    start:function(){
        returnPromise.resolve();
    },
    /**
     *Destroysthecurrentwidget,alsodestroysallitschildrenbefore
     *destroyingitself.
     */
    destroy:function(){
        mixins.PropertiesMixin.destroy.call(this);
        if(this.$el){
            this.$el.remove();
        }
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *RendersthecurrentwidgetandappendsittothegivenjQueryobject.
     *
     *@param{jQuery}target
     *@returns{Promise}
     */
    appendTo:function(target){
        varself=this;
        returnthis._widgetRenderAndInsert(function(t){
            self.$el.appendTo(t);
        },target);
    },
    /**
     *Attachthecurrentwidgettoadomelement
     *
     *@param{jQuery}target
     *@returns{Promise}
     */
    attachTo:function(target){
        varself=this;
        this.setElement(target.$el||target);
        returnthis.willStart().then(function(){
            if(self.__parentedDestroyed){
                return;
            }
            returnself.start();
        });
    },
    /**
     *Hidesthewidget
     */
    do_hide:function(){
        if(this.$el){
            this.$el.addClass('o_hidden');
        }
    },
    /**
     *Displaysthewidget
     */
    do_show:function(){
        if(this.$el){
            this.$el.removeClass('o_hidden');
        }
    },
    /**
     *Displaysorhidesthewidget
     *@param{boolean}[display]usetruetoshowthewidgetorfalsetohideit
     */
    do_toggle:function(display){
        if(_.isBoolean(display)){
            display?this.do_show():this.do_hide();
        }elseif(this.$el){
            this.$el.hasClass('o_hidden')?this.do_show():this.do_hide();
        }
    },
    /**
     *RendersthecurrentwidgetandinsertsitaftertothegivenjQuery
     *object.
     *
     *@param{jQuery}target
     *@returns{Promise}
     */
    insertAfter:function(target){
        varself=this;
        returnthis._widgetRenderAndInsert(function(t){
            self.$el.insertAfter(t);
        },target);
    },
    /**
     *RendersthecurrentwidgetandinsertsitbeforetothegivenjQuery
     *object.
     *
     *@param{jQuery}target
     *@returns{Promise}
     */
    insertBefore:function(target){
        varself=this;
        returnthis._widgetRenderAndInsert(function(t){
            self.$el.insertBefore(t);
        },target);
    },
    /**
     *RendersthecurrentwidgetandprependsittothegivenjQueryobject.
     *
     *@param{jQuery}target
     *@returns{Promise}
     */
    prependTo:function(target){
        varself=this;
        returnthis._widgetRenderAndInsert(function(t){
            self.$el.prependTo(t);
        },target);
    },
    /**
     *Renderstheelement.Thedefaultimplementationrendersthewidgetusing
     *QWeb,`this.template`mustbedefined.ThecontextgiventoQWebcontains
     *the"widget"keythatreferences`this`.
     */
    renderElement:function(){
        var$el;
        if(this.template){
            $el=$(core.qweb.render(this.template,{widget:this}).trim());
        }else{
            $el=this._makeDescriptive();
        }
        this._replaceElement($el);
    },
    /**
     *RendersthecurrentwidgetandreplacesthegivenjQueryobject.
     *
     *@paramtargetAjQueryobjectoraWidgetinstance.
     *@returns{Promise}
     */
    replace:function(target){
        returnthis._widgetRenderAndInsert(_.bind(function(t){
            this.$el.replaceAll(t);
        },this),target);
    },
    /**
     *Re-setsthewidget'srootelement(el/$el/$el).
     *
     *Includes:
     *
     **re-delegatingevents
     **re-bindingsub-elements
     **ifthewidgetalreadyhadarootelement,replacingthepre-existing
     *  elementintheDOM
     *
     *@param{HTMLElement|jQuery}elementnewrootelementforthewidget
     *@return{Widget}this
     */
    setElement:function(element){
        if(this.$el){
            this._undelegateEvents();
        }

        this.$el=(elementinstanceof$)?element:$(element);
        this.el=this.$el[0];

        this._delegateEvents();

        returnthis;
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Helpermethod,for``this.$el.find(selector)``
     *
     *@private
     *@param{string}selectorCSSselector,rootedin$el
     *@returns{jQuery}selectormatch
     */
    $:function(selector){
        if(selector===undefined){
            returnthis.$el;
        }
        returnthis.$el.find(selector);
    },
    /**
     *Attacheventhandlersforeventsdescribedinthe'events'key
     *
     *@private
     */
    _delegateEvents:function(){
        varevents=this.events;
        if(_.isEmpty(events)){return;}

        for(varkeyinevents){
            if(!events.hasOwnProperty(key)){continue;}

            varmethod=this.proxy(events[key]);

            varmatch=/^(\S+)(\s+(.*))?$/.exec(key);
            varevent=match[1];
            varselector=match[3];

            event+='.widget_events';
            if(!selector){
                this.$el.on(event,method);
            }else{
                this.$el.on(event,selector,method);
            }
        }
    },
    /**
     *Makesapotentialrootelementfromthedeclarativebuilderofthe
     *widget
     *
     *@private
     *@return{jQuery}
     */
    _makeDescriptive:function(){
        varattrs=_.extend({},this.attributes||{});
        if(this.id){
            attrs.id=this.id;
        }
        if(this.className){
            attrs['class']=this.className;
        }
        var$el=$(document.createElement(this.tagName));
        if(!_.isEmpty(attrs)){
            $el.attr(attrs);
        }
        return$el;
    },
    /**
     *Re-setsthewidget'srootelementandreplacestheoldrootelement
     *(ifany)bythenewoneintheDOM.
     *
     *@private
     *@param{HTMLElement|jQuery}$el
     *@returns{Widget}thisinstance,soitcanbechained
     */
    _replaceElement:function($el){
        var$oldel=this.$el;
        this.setElement($el);
        if($oldel&&!$oldel.is(this.$el)){
            if($oldel.length>1){
                $oldel.wrapAll('<div/>');
                $oldel.parent().replaceWith(this.$el);
            }else{
                $oldel.replaceWith(this.$el);
            }
        }
        returnthis;
    },
    /**
     *Removeallhandlersregisteredonthis.$el
     *
     *@private
     */
    _undelegateEvents:function(){
        this.$el.off('.widget_events');
    },
    /**
     *Renderthewidget. Thisisaprivatemethod,andshouldreallyneverbe
     *calledbyanyone(exceptthiswidget). Itassumesthatthewidgetwas
     *notwillStartedyet.
     *
     *@private
     *@param{function:jQuery->any}insertion
     *@param{jQuery}target
     *@returns{Promise}
     */
    _widgetRenderAndInsert:function(insertion,target){
        varself=this;
        returnthis.willStart().then(function(){
            if(self.__parentedDestroyed){
                return;
            }
            self.renderElement();
            insertion(target);
            returnself.start();
        });
    },
});

returnWidget;

});
