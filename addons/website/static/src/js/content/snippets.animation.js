flectra.define('website.content.snippets.animation',function(require){
'usestrict';

/**
 *ProvidesawaytostartJScodeforsnippets'initializationandanimations.
 */

constajax=require('web.ajax');
varClass=require('web.Class');
varconfig=require('web.config');
varcore=require('web.core');
constdom=require('web.dom');
varmixins=require('web.mixins');
varpublicWidget=require('web.public.widget');
constwUtils=require('website.utils');

varqweb=core.qweb;

//InitializefallbacksfortheuseofrequestAnimationFrame,
//cancelAnimationFrameandperformance.now()
window.requestAnimationFrame=window.requestAnimationFrame
    ||window.webkitRequestAnimationFrame
    ||window.mozRequestAnimationFrame
    ||window.msRequestAnimationFrame
    ||window.oRequestAnimationFrame;
window.cancelAnimationFrame=window.cancelAnimationFrame
    ||window.webkitCancelAnimationFrame
    ||window.mozCancelAnimationFrame
    ||window.msCancelAnimationFrame
    ||window.oCancelAnimationFrame;
if(!window.performance||!window.performance.now){
    window.performance={
        now:function(){
            returnDate.now();
        }
    };
}

/**
 *Addthenotionofeditmodetopublicwidgets.
 */
publicWidget.Widget.include({
    /**
     *Indicatesifthewidgetshouldnotbeinstantiatedinedit.Thedefault
     *istrue,indeedmost(all?)definedwidgetsonlywanttoinitialize
     *eventsandstateswhichshouldnotbeactiveineditmode(thisis
     *especiallytruefornon-websitewidgets).
     *
     *@type{boolean}
     */
    disabledInEditableMode:true,
    /**
     *Actsas@seeWidget.eventsexceptthattheeventsareonlybindedifthe
     *Widgetinstanceisinstanciatedineditmode.Thepropertyisnot
     *consideredif@seedisabledInEditableModeisfalse.
     */
    edit_events:null,
    /**
     *Actsas@seeWidget.eventsexceptthattheeventsareonlybindedifthe
     *Widgetinstanceisinstanciatedinreadonlymode.Thepropertyonly
     *makessenseif@seedisabledInEditableModeisfalse,youshouldsimply
     *use@seeWidget.eventsotherwise.
     */
    read_events:null,

    /**
     *Initializestheeventsthatwillneedtobebindedaccordingtothe
     *givenmode.
     *
     *@constructor
     *@param{Object}parent
     *@param{Object}[options]
     *@param{boolean}[options.editableMode=false]
     *       trueifthepageisineditionmode
     */
    init:function(parent,options){
        this._super.apply(this,arguments);

        this.editableMode=this.options.editableMode||false;
        varextraEvents=this.editableMode?this.edit_events:this.read_events;
        if(extraEvents){
            this.events=_.extend({},this.events||{},extraEvents);
        }
    },
});

/**
 *InchargeofhandlingoneanimationloopusingtherequestAnimationFrame
 *feature.Thisisusedbythe`Animation`classbelowandshouldnotbecalled
 *directlybyanenddeveloper.
 *
 *ThisusesasimpleAPI:itcanbestarted,stopped,playedandpaused.
 */
varAnimationEffect=Class.extend(mixins.ParentedMixin,{
    /**
     *@constructor
     *@param{Object}parent
     *@param{function}updateCallback-theanimationupdatecallback
     *@param{string}[startEvents=scroll]
     *       spaceseparatedlistofeventswhichstartstheanimationloop
     *@param{jQuery|DOMElement}[$startTarget=window]
     *       theelement(s)onwhichthestartEventsarelistened
     *@param{Object}[options]
     *@param{function}[options.getStateCallback]
     *       afunctionwhichreturnsavaluewhichrepresentsthestateofthe
     *       animation,i.e.fortwosamevalue,norefreshingoftheanimation
     *       isneeded.Canbeusedforoptimization.Ifthe$startTargetis
     *       thewindowelement,thisdefaultstoreturningthecurrent
     *       scolloffsetofthewindoworthesizeofthewindowforthe
     *       scrollandresizeeventsrespectively.
     *@param{string}[options.endEvents]
     *       spaceseparatedlistofeventswhichpausetheanimationloop.If
     *       notgiven,theanimationisstoppedafterawhile(ifno
     *       startEventsisreceivedagain)
     *@param{jQuery|DOMElement}[options.$endTarget=$startTarget]
     *       theelement(s)onwhichtheendEventsarelistened
     *@param{boolean}[options.enableInModal]
     *       whenitistrue,itmeansthatthe'scroll'eventmustbe
     *       triggeredwhenscrollingamodal.
     */
    init:function(parent,updateCallback,startEvents,$startTarget,options){
        mixins.ParentedMixin.init.call(this);
        this.setParent(parent);

        options=options||{};
        this._minFrameTime=1000/(options.maxFPS||100);

        //InitializetheanimationstartEvents,startTarget,endEvents,endTargetandcallbacks
        this._updateCallback=updateCallback;
        this.startEvents=startEvents||'scroll';
        constmodalEl=options.enableInModal?parent.target.closest('.modal'):null;
        constmainScrollingElement=modalEl?modalEl:$().getScrollingElement()[0];
        constmainScrollingTarget=mainScrollingElement===document.documentElement?window:mainScrollingElement;
        this.$startTarget=$($startTarget?$startTarget:this.startEvents==='scroll'?mainScrollingTarget:window);
        if(options.getStateCallback){
            this._getStateCallback=options.getStateCallback;
        }elseif(this.startEvents==='scroll'&&this.$startTarget[0]===mainScrollingTarget){
            const$scrollable=this.$startTarget;
            this._getStateCallback=function(){
                return$scrollable.scrollTop();
            };
        }elseif(this.startEvents==='resize'&&this.$startTarget[0]===window){
            this._getStateCallback=function(){
                return{
                    width:window.innerWidth,
                    height:window.innerHeight,
                };
            };
        }else{
            this._getStateCallback=function(){
                returnundefined;
            };
        }
        this.endEvents=options.endEvents||false;
        this.$endTarget=options.$endTarget?$(options.$endTarget):this.$startTarget;

        this._updateCallback=this._updateCallback.bind(parent);
        this._getStateCallback=this._getStateCallback.bind(parent);

        //Addanamespacetoeventsusingthegenerateduid
        this._uid='_animationEffect'+_.uniqueId();
        this.startEvents=_processEvents(this.startEvents,this._uid);
        if(this.endEvents){
            this.endEvents=_processEvents(this.endEvents,this._uid);
        }

        function_processEvents(events,namespace){
            events=events.split('');
            return_.each(events,function(e,index){
                events[index]+=('.'+namespace);
            }).join('');
        }
    },
    /**
     *@override
     */
    destroy:function(){
        mixins.ParentedMixin.destroy.call(this);
        this.stop();
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *Initializeswhentheanimationmustbeplayedandpausedandinitializes
     *theanimationfirstframe.
     */
    start:function(){
        //Initializetheanimationfirstframe
        this._paused=false;
        this._rafID=window.requestAnimationFrame((function(t){
            this._update(t);
            this._paused=true;
        }).bind(this));

        //Initializetheanimationplay/pauseevents
        if(this.endEvents){
            /**
             *IfthereareendEvents,theanimationshouldbeginplayingwhen
             *thestartEventsaretriggeredonthe$startTargetandpausewhen
             *theendEventsaretriggeredonthe$endTarget.
             */
            this.$startTarget.on(this.startEvents,(function(e){
                if(this._paused){
                    _.defer(this.play.bind(this,e));
                }
            }).bind(this));
            this.$endTarget.on(this.endEvents,(function(){
                if(!this._paused){
                    _.defer(this.pause.bind(this));
                }
            }).bind(this));
        }else{
            /**
             *Else,ifthereisnoendEvents,theanimationshouldbeginplaying
             *whenthestartEventsare*continuously*triggeredonthe
             *$startTargetorfullyplayedonce.Toachievethis,theanimation
             *beginsplayingandisscheduledtopauseafter2seconds.Ifthe
             *startEventsaretriggeredduringthattime,thisisnotpaused
             *foranother2seconds.Thisallowstodescribean"effect"
             *animation(whichlastslessthan2seconds)orananimationwhich
             *mustbeplaying*during*anevent(scroll,mousemove,resize,
             *repeatedclicks,...).
             */
            varpauseTimer=null;
            this.$startTarget.on(this.startEvents,_.throttle((function(e){
                this.play(e);

                clearTimeout(pauseTimer);
                pauseTimer=_.delay((function(){
                    this.pause();
                    pauseTimer=null;
                }).bind(this),2000);
            }).bind(this),250,{trailing:false}));
        }
    },
    /**
     *Pausestheanimationanddestroystheattachedeventswhichtriggerthe
     *animationtobeplayedorpaused.
     */
    stop:function(){
        this.$startTarget.off(this.startEvents);
        if(this.endEvents){
            this.$endTarget.off(this.endEvents);
        }
        this.pause();
    },
    /**
     *ForcestherequestAnimationFramelooptostart.
     *
     *@param{Event}e-theeventwhichtriggeredtheanimationtoplay
     */
    play:function(e){
        this._newEvent=e;
        if(!this._paused){
            return;
        }
        this._paused=false;
        this._rafID=window.requestAnimationFrame(this._update.bind(this));
        this._lastUpdateTimestamp=undefined;
    },
    /**
     *ForcestherequestAnimationFramelooptostop.
     */
    pause:function(){
        if(this._paused){
            return;
        }
        this._paused=true;
        window.cancelAnimationFrame(this._rafID);
        this._lastUpdateTimestamp=undefined;
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *CallbackwhichisrepeatedlycalledbytherequestAnimationFrameloop.
     *Itcontrolsthemaxfpsatwhichtheanimationisrunningandinitializes
     *thevaluesthattheupdatecallbackneedstodescribetheanimation
     *(state,elapsedTime,triggeredevent).
     *
     *@private
     *@param{DOMHighResTimeStamp}timestamp
     */
    _update:function(timestamp){
        if(this._paused){
            return;
        }
        this._rafID=window.requestAnimationFrame(this._update.bind(this));

        //Checktheelapsedtimesincethelastupdatecallbackcall.
        //Considerit0ifthereisnoinfooflasttimestampandleavethis
        //_updatecallifitwascalledtoosoon(wouldoverflowthesetmaxFPS).
        varelapsedTime=0;
        if(this._lastUpdateTimestamp){
            elapsedTime=timestamp-this._lastUpdateTimestamp;
            if(elapsedTime<this._minFrameTime){
                return;
            }
        }

        //Checkthenewanimationstatethankstothegetstatecallbackand
        //storeitsnewvalue.Ifthestateisthesameasthepreviousone,
        //leavethis_updatecall,exceptifthereisaneventwhichtriggered
        //the"play"methodagain.
        varanimationState=this._getStateCallback(elapsedTime,this._newEvent);
        if(!this._newEvent
         &&animationState!==undefined
         &&_.isEqual(animationState,this._animationLastState)){
            return;
        }
        this._animationLastState=animationState;

        //Calltheupdatecallbackwithframeparameters
        this._updateCallback(this._animationLastState,elapsedTime,this._newEvent);
        this._lastUpdateTimestamp=timestamp;//Savethetimestampatwhichtheupdatecallbackwasreallycalled
        this._newEvent=undefined;//Forgettheeventwhichtriggeredthelast"play"call
    },
});

/**
 *AlsoregisterAnimationEffectautomatically(@seeeffects,_prepareEffects).
 */
varAnimation=publicWidget.Widget.extend({
    /**
     *ThemaxFPSatwhichalltheautomaticanimationeffectswillbe
     *runningbydefault.
     */
    maxFPS:100,
    /**
     *@seethis._prepareEffects
     *
     *@type{Object[]}
     *@type{string}startEvents
     *      Thenamesoftheeventswhichtriggertheeffecttobeginplaying.
     *@type{string}[startTarget]
     *      Aselectortofindthetargetwheretolistenforthestartevents
     *      (ifnoselector,thewindowtargetwillbeused).Ifthewhole
     *      $targetoftheanimationshouldbeused,usethe'selector'string.
     *@type{string}[endEvents]
     *      Thenameoftheeventswhichtriggertheendoftheeffect(ifnone
     *      isdefined,theanimationwillstopafterawhile
     *      @seeAnimationEffect.start).
     *@type{string}[endTarget]
     *      Aselectortofindthetargetwheretolistenfortheendevents
     *      (ifnoselector,thestartTargetwillbeused).Ifthewhole
     *      $targetoftheanimationshouldbeused,usethe'selector'string.
     *@type{string}update
     *      Astringwhichreferstoamethodwhichwillbeusedastheupdate
     *      callbackfortheeffect.Itreceives3arguments:theanimation
     *      state,theelapsedTimesincelastupdateandtheeventwhich
     *      triggeredtheanimation(undefinedifjustanewupdatecall
     *      withouttrigger).
     *@type{string}[getState]
     *      Theanimationstateisundefinedbydefault,thescrolloffsetfor
     *      theparticular{startEvents:'scroll'}effectandanobjectwith
     *      widthandheightfortheparticular{startEvents:'resize'}effect.
     *      ThereisthepossibilitytodefinethegetStatecallbackofthe
     *      animationeffectwiththiskey.Thisallowstoimproveperformance
     *      evenfurtherinsomecases.
     */
    effects:[],

    /**
     *Initializestheanimation.Themethodshouldnotbecalleddirectlyas
     *calledautomaticallyonanimationinstantiationandonrestart.
     *
     *Also,preparesanimation'seffectsandstartthemifany.
     *
     *@override
     */
    start:function(){
        this._prepareEffects();
        _.each(this._animationEffects,function(effect){
            effect.start();
        });
        returnthis._super.apply(this,arguments);
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Registers`AnimationEffect`instances.
     *
     *Thiscanbedonebyextendingthismethodandcallingthe@see_addEffect
     *methodinitor,better,byfillingthe@seeeffectsproperty.
     *
     *@private
     */
    _prepareEffects:function(){
        this._animationEffects=[];

        varself=this;
        _.each(this.effects,function(desc){
            self._addEffect(self[desc.update],desc.startEvents,_findTarget(desc.startTarget),{
                getStateCallback:desc.getState&&self[desc.getState],
                endEvents:desc.endEvents||undefined,
                $endTarget:_findTarget(desc.endTarget),
                maxFPS:self.maxFPS,
                enableInModal:desc.enableInModal||undefined,
            });

            //ReturntheDOMelementmatchingtheselectorintheform
            //describedabove.
            function_findTarget(selector){
                if(selector){
                    if(selector==='selector'){
                        returnself.$target;
                    }
                    returnself.$(selector);
                }
                returnundefined;
            }
        });
    },
    /**
     *Registersanew`AnimationEffect`accordingtogivenparameters.
     *
     *@private
     *@seeAnimationEffect.init
     */
    _addEffect:function(updateCallback,startEvents,$startTarget,options){
        this._animationEffects.push(
            newAnimationEffect(this,updateCallback,startEvents,$startTarget,options)
        );
    },
});

//::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

varregistry=publicWidget.registry;

registry.slider=publicWidget.Widget.extend({
    selector:'.carousel',
    disabledInEditableMode:false,
    edit_events:{
        'content_changed':'_onContentChanged',
    },

    /**
     *@override
     */
    start:function(){
        this.$('img').on('load.slider',()=>this._computeHeights());
        this._computeHeights();
        //Initializecarouselandpauseifineditmode.
        this.$target.carousel(this.editableMode?'pause':undefined);
        $(window).on('resize.slider',_.debounce(()=>this._computeHeights(),250));
        returnthis._super.apply(this,arguments);
    },
    /**
     *@override
     */
    destroy:function(){
        this._super.apply(this,arguments);
        this.$('img').off('.slider');
        this.$target.carousel('pause');
        this.$target.removeData('bs.carousel');
        _.each(this.$('.carousel-item'),function(el){
            $(el).css('min-height','');
        });
        $(window).off('.slider');
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _computeHeights:function(){
        varmaxHeight=0;
        var$items=this.$('.carousel-item');
        $items.css('min-height','');
        _.each($items,function(el){
            var$item=$(el);
            varisActive=$item.hasClass('active');
            $item.addClass('active');
            varheight=$item.outerHeight();
            if(height>maxHeight){
                maxHeight=height;
            }
            $item.toggleClass('active',isActive);
        });
        $items.css('min-height',maxHeight);
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _onContentChanged:function(ev){
        this._computeHeights();
    },
});

registry.Parallax=Animation.extend({
    selector:'.parallax',
    disabledInEditableMode:false,
    effects:[{
        startEvents:'scroll',
        update:'_onWindowScroll',
        enableInModal:true,
    }],

    /**
     *@override
     */
    start:function(){
        this._rebuild();
        $(window).on('resize.animation_parallax',_.debounce(this._rebuild.bind(this),500));
        this.modalEl=this.$target[0].closest('.modal');
        if(this.modalEl){
            $(this.modalEl).on('shown.bs.modal.animation_parallax',()=>{
                this._rebuild();
                this.modalEl.dispatchEvent(newEvent('scroll'));
            });
        }
        returnthis._super.apply(this,arguments);
    },
    /**
     *@override
     */
    destroy:function(){
        this._super.apply(this,arguments);
        $(window).off('.animation_parallax');
        if(this.modalEl){
            $(this.modalEl).off('.animation_parallax');
        }
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Preparesthebackgroundelementwhichwillscrollatadifferentspeed
     *accordingtotheviewportdimensionsandothersnippetparameters.
     *
     *@private
     */
    _rebuild:function(){
        //Add/findbgDOMelementtoholdtheparallaxbg(supportoldv10.0parallax)
        this.$bg=this.$('>.s_parallax_bg');

        //Getparallaxspeed
        this.speed=parseFloat(this.$target.attr('data-scroll-background-ratio')||0);

        //Resetoffsetifparallaxeffectwillnotbeperformedandleave
        varnoParallaxSpeed=(this.speed===0||this.speed===1);
        if(noParallaxSpeed){
            this.$bg.css({
                transform:'',
                top:'',
                bottom:'',
            });
            return;
        }

        //Initializeparallaxdataaccordingtosnippetandviewportdimensions
        this.viewport=document.body.clientHeight-$('#wrapwrap').position().top;
        this.visibleArea=[this.$target.offset().top];
        this.visibleArea.push(this.visibleArea[0]+this.$target.innerHeight()+this.viewport);
        this.ratio=this.speed*(this.viewport/10);

        //Providea"safe-area"tolimitparallax
        constabsoluteRatio=Math.abs(this.ratio);
        this.$bg.css({
            top:-absoluteRatio,
            bottom:-absoluteRatio,
        });
    },

    //--------------------------------------------------------------------------
    //Effects
    //--------------------------------------------------------------------------

    /**
     *Describeshowtoupdatethesnippetwhenthewindowscrolls.
     *
     *@private
     *@param{integer}scrollOffset
     */
    _onWindowScroll:function(scrollOffset){
        //Speed==0isnoeffectandspeed==1ishandledbyCSSonly
        if(this.speed===0||this.speed===1){
            return;
        }

        //Performtranslationiftheelementisvisibleonly
        varvpEndOffset=scrollOffset+this.viewport;
        if(vpEndOffset>=this.visibleArea[0]
         &&vpEndOffset<=this.visibleArea[1]){
            this.$bg.css('transform','translateY('+_getNormalizedPosition.call(this,vpEndOffset)+'px)');
        }

        function_getNormalizedPosition(pos){
            //Normalizescrollina1to0range
            varr=(pos-this.visibleArea[1])/(this.visibleArea[0]-this.visibleArea[1]);
            //Normalizeaccordinglytocurrentoptions
            returnMath.round(this.ratio*(2*r-1));
        }
    },
});

constMobileYoutubeAutoplayMixin={
    /**
     *Takescareofanynecessarysetupforautoplayingvideo.Inpractice,
     *thismethodwillloadtheyoutubeiframeAPIformobileenvironments
     *becausemobileenvironmentsdon'tsupporttheyoutubeautoplayparam
     *passedintheurl.
     *
     *@private
     *@param{string}src-Thesourceurlofthevideo
     */
    _setupAutoplay:function(src){
        letpromise=Promise.resolve();

        this.isYoutubeVideo=src.indexOf('youtube')>=0;
        this.isMobileEnv=config.device.size_class<=config.device.SIZES.LG&&config.device.touch;

        if(this.isYoutubeVideo&&this.isMobileEnv&&!window.YT){
            constoldOnYoutubeIframeAPIReady=window.onYouTubeIframeAPIReady;
            promise=newPromise(resolve=>{
                window.onYouTubeIframeAPIReady=()=>{
                    if(oldOnYoutubeIframeAPIReady){
                        oldOnYoutubeIframeAPIReady();
                    }
                    returnresolve();
                };
            });
            ajax.loadJS('https://www.youtube.com/iframe_api');
        }

        returnpromise;
    },
    /**
     *@private
     *@param{DOMElement}iframeEl-theiframecontainingthevideoplayer
     */
    _triggerAutoplay:function(iframeEl){
        //YouTubedoesnotallowtoauto-playvideoinmobiledevices,sowe
        //havetoplaythevideomanually.
        if(this.isMobileEnv&&this.isYoutubeVideo){
            newwindow.YT.Player(iframeEl,{
                events:{
                    onReady:ev=>ev.target.playVideo(),
                }
            });
        }
    },
};

registry.mediaVideo=publicWidget.Widget.extend(MobileYoutubeAutoplayMixin,{
    selector:'.media_iframe_video',

    /**
     *@override
     */
    start:function(){
        //TODO:thiscodeshouldberefactoredtomakemoresenseandbebetter
        //integratedwithFlectra(thisrefactoringshouldbedoneinmaster).

        constproms=[this._super.apply(this,arguments)];
        letiframeEl=this.$target[0].querySelector(':scope>iframe');

        //Thefollowingcodeisonlytheretoensurecompatibilitywith
        //videosaddedbeforebugfixesornewFlectraversionswherethe
        //<iframe/>elementisproperlysaved.
        if(!iframeEl){
            iframeEl=this._generateIframe();
        }

        if(!iframeEl){
            //Somethingwentwrong:noiframeispresentintheDOMandthe
            //widgetwasunabletocreateoneonthefly.
            returnPromise.all(proms);
        }

        proms.push(this._setupAutoplay(iframeEl.getAttribute('src')));
        returnPromise.all(proms).then(()=>{
            this._triggerAutoplay(iframeEl);
        });
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _generateIframe:function(){
        //Bugfix/compatibility:emptythe<div/>elementasallinformation
        //torebuildtheiframeshouldhavebeensavedonthe<div/>element
        this.$target.empty();

        //Addextracontentforsize/edition
        this.$target.append(
            '<divclass="css_editable_mode_display">&nbsp;</div>'+
            '<divclass="media_iframe_video_size">&nbsp;</div>'
        );

        //Rebuildtheiframe.Dependingonversion/compatibility/instance,
        //thesrcissavedinthe'data-src'attributeorthe
        //'data-oe-expression'one(thelatterisusedasaworkaroundin10.0
        //systembutshouldobviouslybereviewedinmaster).
        varsrc=_.escape(this.$target.data('oe-expression')||this.$target.data('src'));
        //Validatethesrctoonlyacceptsupporteddomainswecantrust
        varm=src.match(/^(?:https?:)?\/\/([^/?#]+)/);
        if(!m){
            //UnsupportedprotocolorwrongURLformat,don'tinjectiframe
            return;
        }
        vardomain=m[1].replace(/^www\./,'');
        varsupportedDomains=['youtu.be','youtube.com','youtube-nocookie.com','instagram.com','vine.co','player.vimeo.com','vimeo.com','dailymotion.com','player.youku.com','youku.com'];
        if(!_.contains(supportedDomains,domain)){
            //Unsupporteddomain,don'tinjectiframe
            return;
        }
        constiframeEl=$('<iframe/>',{
            src:src,
            frameborder:'0',
            allowfullscreen:'allowfullscreen',
        })[0];
        this.$target.append(iframeEl);
        returniframeEl;
    },
});

registry.backgroundVideo=publicWidget.Widget.extend(MobileYoutubeAutoplayMixin,{
    selector:'.o_background_video',
    xmlDependencies:['/website/static/src/xml/website.background.video.xml'],
    disabledInEditableMode:false,

    /**
     *@override
     */
    start:function(){
        varproms=[this._super(...arguments)];

        this.videoSrc=this.el.dataset.bgVideoSrc;
        this.iframeID=_.uniqueId('o_bg_video_iframe_');
        proms.push(this._setupAutoplay(this.videoSrc));
        if(this.isYoutubeVideo&&this.isMobileEnv&&!this.videoSrc.includes('enablejsapi=1')){
            //Compatibility:whenchoosinganautoplayyoutubevideoviathe
            //mediamanager,theAPIwasnotautomaticallyenabledbeforebut
            //onlyenabledhereinthecaseofbackgroundvideos.
            //TODOmigratethoseoldcasessothiscodecanberemoved?
            this.videoSrc+='&enablejsapi=1';
        }

        varthrottledUpdate=_.throttle(()=>this._adjustIframe(),50);

        var$dropdownMenu=this.$el.closest('.dropdown-menu');
        if($dropdownMenu.length){
            this.$dropdownParent=$dropdownMenu.parent();
            this.$dropdownParent.on('shown.bs.dropdown.backgroundVideo',throttledUpdate);
        }

        $(window).on('resize.'+this.iframeID,throttledUpdate);

        const$modal=this.$target.closest('.modal');
        if($modal.length){
            $modal.on('show.bs.modal',()=>{
                constvideoContainerEl=this.$target[0].querySelector('.o_bg_video_container');
                videoContainerEl.classList.add('d-none');
            });
            $modal.on('shown.bs.modal',()=>{
                this._adjustIframe();
                constvideoContainerEl=this.$target[0].querySelector('.o_bg_video_container');
                videoContainerEl.classList.remove('d-none');
            });
        }
        returnPromise.all(proms).then(()=>this._appendBgVideo());
    },
    /**
     *@override
     */
    destroy:function(){
        this._super.apply(this,arguments);

        if(this.$dropdownParent){
            this.$dropdownParent.off('.backgroundVideo');
        }

        $(window).off('resize.'+this.iframeID);

        if(this.$bgVideoContainer){
            this.$bgVideoContainer.remove();
        }
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Adjustsiframesizesandpositionsothatitfillsthecontainerandso
     *thatitiscenteredinit.
     *
     *@private
     */
    _adjustIframe:function(){
        if(!this.$iframe){
            return;
        }

        this.$iframe.removeClass('show');

        //Adjusttheiframe
        varwrapperWidth=this.$target.innerWidth();
        varwrapperHeight=this.$target.innerHeight();
        varrelativeRatio=(wrapperWidth/wrapperHeight)/(16/9);
        varstyle={};
        if(relativeRatio>=1.0){
            style['width']='100%';
            style['height']=(relativeRatio*100)+'%';
            style['left']='0';
            style['top']=(-(relativeRatio-1.0)/2*100)+'%';
        }else{
            style['width']=((1/relativeRatio)*100)+'%';
            style['height']='100%';
            style['left']=(-((1/relativeRatio)-1.0)/2*100)+'%';
            style['top']='0';
        }
        this.$iframe.css(style);

        voidthis.$iframe[0].offsetWidth;//Forcestyleaddition
        this.$iframe.addClass('show');
    },
    /**
     *Appendbackgroundvideorelatedelementstothetarget.
     *
     *@private
     */
    _appendBgVideo:function(){
        var$oldContainer=this.$bgVideoContainer||this.$('>.o_bg_video_container');
        this.$bgVideoContainer=$(qweb.render('website.background.video',{
            videoSrc:this.videoSrc,
            iframeID:this.iframeID,
        }));
        this.$iframe=this.$bgVideoContainer.find('.o_bg_video_iframe');
        this.$iframe.one('load',()=>{
            this.$bgVideoContainer.find('.o_bg_video_loading').remove();
        });
        this.$bgVideoContainer.prependTo(this.$target);
        $oldContainer.remove();

        this._adjustIframe();
        this._triggerAutoplay(this.$iframe[0]);
    },
});

registry.socialShare=publicWidget.Widget.extend({
    selector:'.oe_social_share',
    xmlDependencies:['/website/static/src/xml/website.share.xml'],
    events:{
        'mouseenter':'_onMouseEnter',
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _bindSocialEvent:function(){
        this.$('.oe_social_facebook').click($.proxy(this._renderSocial,this,'facebook'));
        this.$('.oe_social_twitter').click($.proxy(this._renderSocial,this,'twitter'));
        this.$('.oe_social_linkedin').click($.proxy(this._renderSocial,this,'linkedin'));
    },
    /**
     *@private
     */
    _render:function(){
        this.$el.popover({
            content:qweb.render('website.social_hover',{medias:this.socialList}),
            placement:'bottom',
            container:this.$el,
            html:true,
            trigger:'manual',
            animation:false,
        }).popover("show");

        this.$el.off('mouseleave.socialShare').on('mouseleave.socialShare',function(){
            varself=this;
            setTimeout(function(){
                if(!$(".popover:hover").length){
                    $(self).popover('dispose');
                }
            },200);
        });
    },
    /**
     *@private
     */
    _renderSocial:function(social){
        varurl=this.$el.data('urlshare')||document.URL.split(/[?#]/)[0];
        url=encodeURIComponent(url);
        vartitle=document.title.split("|")[0]; //getthepagetitlewithoutthecompanyname
        varhashtags='#'+document.title.split("|")[1].replace('','')+''+this.hashtags; //companynamewithoutspaces(forhashtag)
        varsocialNetworks={
            'facebook':'https://www.facebook.com/sharer/sharer.php?u='+url,
            'twitter':'https://twitter.com/intent/tweet?original_referer='+url+'&text='+encodeURIComponent(title+hashtags+'-')+url,
            'linkedin':'https://www.linkedin.com/sharing/share-offsite/?url='+url,
        };
        if(!_.contains(_.keys(socialNetworks),social)){
            return;
        }
        varwHeight=500;
        varwWidth=500;
        window.open(socialNetworks[social],'','menubar=no,toolbar=no,resizable=yes,scrollbar=yes,height='+wHeight+',width='+wWidth);
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Calledwhentheuserhoverstheanimationelement->openthesocial
     *linkspopover.
     *
     *@private
     */
    _onMouseEnter:function(){
        varsocial=this.$el.data('social');
        this.socialList=social?social.split(','):['facebook','twitter','linkedin'];
        this.hashtags=this.$el.data('hashtags')||'';

        this._render();
        this._bindSocialEvent();
    },
});

registry.anchorSlide=publicWidget.Widget.extend({
    selector:'a[href^="/"][href*="#"],a[href^="#"]',
    events:{
        'click':'_onAnimateClick',
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{jQuery}$eltheelementtoscrollto.
     *@param{string}[scrollValue='true']scrollvalue
     *@returns{Promise}
     */
    async_scrollTo($el,scrollValue='true'){
        returndom.scrollTo($el[0],{
            duration:scrollValue==='true'?500:0,
            extraOffset:this._computeExtraOffset(),
        });
    },
    /**
     *@private
     */
    _computeExtraOffset(){
        return0;
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _onAnimateClick:function(ev){
        if(this.$target[0].pathname!==window.location.pathname){
            return;
        }
        varhash=this.$target[0].hash;
        if(hash==='#top'||hash==='#bottom'){
            //Iftheanchortargets#topor#bottom,directlycallthe
            //"scrollTo"function.Thereasonisthattheheaderorthefooter
            //couldhavebeenremovedfromtheDOM.Byreceivingastringas
            //parameter,the"scrollTo"functionhandlesthescrolltothetop
            //ortothebottomofthedocumenteveniftheheaderorthe
            //footerisremovedfromtheDOM.
            dom.scrollTo(hash,{
                duration:500,
                extraOffset:this._computeExtraOffset(),
            });
            return;
        }
        if(!hash.length){
            return;
        }
        //EscapespecialcharacterstomakethejQueryselectortowork.
        hash='#'+$.escapeSelector(hash.substring(1));
        var$anchor=$(hash);
        constscrollValue=$anchor.attr('data-anchor');
        if(!$anchor.length||!scrollValue){
            return;
        }
        ev.preventDefault();
        this._scrollTo($anchor,scrollValue);
    },
});

registry.FullScreenHeight=publicWidget.Widget.extend({
    selector:'.o_full_screen_height',
    disabledInEditableMode:false,

    /**
     *@override
     */
    start(){
        this.inModal=!!this.el.closest('.modal');

        //TODOmaybereviewthewaythepublicwidgetsworkfornon-visible-at-
        //loadsnippets->probablybettertonotdoanythingforthemand
        //startthewidgetsonlyoncetheybecomevisible..?
        if(this.$el.is(':not(:visible)')||this.$el.outerHeight()>this._computeIdealHeight()){
            //Onlyinitializeiftallerthantheidealheightassomeextracss
            //rulesmayalterthefull-screen-heightclassbehaviorinsome
            //cases(blog...).
            this._adaptSize();
            $(window).on('resize.FullScreenHeight',_.debounce(()=>this._adaptSize(),250));
        }
        returnthis._super(...arguments);
    },
    /**
     *@override
     */
    destroy(){
        this._super(...arguments);
        $(window).off('.FullScreenHeight');
        this.el.style.setProperty('min-height','');
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _adaptSize(){
        constheight=this._computeIdealHeight();
        this.el.style.setProperty('min-height',`${height}px`,'important');
    },
    /**
     *@private
     */
    _computeIdealHeight(){
        constwindowHeight=$(window).outerHeight();
        if(this.inModal){
            return(windowHeight-$('#wrapwrap').position().top);
        }

        //Doingitthatwayallowstoconsidererfixedheaders,hiddenheaders,
        //connectedusers,...
        constfirstContentEl=$('#wrapwrap>main>:first-child')[0];//firstchildtoconsiderthepadding-topofmain
        constmainTopPos=firstContentEl.getBoundingClientRect().top+dom.closestScrollable(firstContentEl.parentNode).scrollTop;
        return(windowHeight-mainTopPos);
    },
});

registry.ScrollButton=registry.anchorSlide.extend({
    selector:'.o_scroll_button',

    /**
     *@override
     */
    _onAnimateClick:function(ev){
        ev.preventDefault();
        //Scrolltothenextvisibleelementafterthecurrentone.
        constcurrentSectionEl=this.el.closest('section');
        letnextEl=currentSectionEl.nextElementSibling;
        while(nextEl){
            if($(nextEl).is(':visible')){
                this._scrollTo($(nextEl));
                return;
            }
            nextEl=nextEl.nextElementSibling;
        }
    },
});

registry.FooterSlideout=publicWidget.Widget.extend({
    selector:'#wrapwrap:has(.o_footer_slideout)',
    disabledInEditableMode:false,

    /**
     *@override
     */
    asyncstart(){
        const$main=this.$('>main');
        constslideoutEffect=$main.outerHeight()>=$(window).outerHeight();
        this.el.classList.toggle('o_footer_effect_enable',slideoutEffect);

        //Addapixeldivoverthefooter,afterintheDOM,sothatthe
        //heightofthefooterisunderstoodbyFirefoxstickyimplementation
        //(whichitseemstonotunderstandbecauseofthecombinationof3
        //items:thefooteristhelast:visibleelementinthe#wrapwrap,the
        //#wrapwrapusesflexlayoutandthe#wrapwrapistheelementwitha
        //scrollbar).
        //TODOcheckifthehackisstillneededbyfuturebrowsers.
        this.__pixelEl=document.createElement('div');
        this.__pixelEl.style.width=`1px`;
        this.__pixelEl.style.height=`1px`;
        this.__pixelEl.style.marginTop=`-1px`;
        //Onsafari,addabackgroundattachmentfixedtofixtheglitchesthat
        //appearwhenscrollingthepagewithafooterslideout.
        if(this.el.classList.contains("o_safari_browser")){
            this.__pixelEl.style.backgroundColor="transparent";
            this.__pixelEl.style.backgroundAttachment="fixed";
            this.__pixelEl.style.backgroundImage="url(/website/static/src/img/website_logo.png)";
        }
        this.el.appendChild(this.__pixelEl);

        returnthis._super(...arguments);
    },
    /**
     *@override
     */
    destroy(){
        this._super(...arguments);
        this.el.classList.remove('o_footer_effect_enable');
        this.__pixelEl.remove();
    },
});

registry.TopMenuCollapse=publicWidget.Widget.extend({
    selector:"header#top_menu_collapse",

    /**
     *@override
     */
    asyncstart(){
        this.throttledResize=_.throttle(()=>this._onResize(),25);
        window.addEventListener("resize",this.throttledResize);
        returnthis._super(...arguments);
    },
    /**
     *@override
     */
    destroy(){
        this._super(...arguments);
        window.removeEventListener("resize",this.throttledResize);
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _onResize(){
        if(this.el.classList.contains("show")){
            consttogglerEl=this.el.closest("nav").querySelector(".navbar-toggler");
            if(getComputedStyle(togglerEl).display==="none"){
                this.$el.collapse("hide");
            }
        }
    },
});

registry.HeaderHamburgerFull=publicWidget.Widget.extend({
    selector:'header:has(.o_header_hamburger_full_toggler):not(:has(.o_offcanvas_menu_toggler))',
    events:{
        'click.o_header_hamburger_full_toggler':'_onToggleClick',
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _onToggleClick(){
        document.body.classList.add('overflow-hidden');
        setTimeout(()=>$(window).trigger('scroll'),100);
    },
});

registry.BottomFixedElement=publicWidget.Widget.extend({
    selector:'#wrapwrap',

    /**
     *@override
     */
    asyncstart(){
        this.$scrollingElement=$().getScrollingElement();
        this.__hideBottomFixedElements=_.debounce(()=>this._hideBottomFixedElements(),500);
        this.$scrollingElement.on('scroll.bottom_fixed_element',this.__hideBottomFixedElements);
        $(window).on('resize.bottom_fixed_element',this.__hideBottomFixedElements);
        returnthis._super(...arguments);
    },
    /**
     *@override
     */
    destroy(){
        this._super(...arguments);
        this.$scrollingElement.off('.bottom_fixed_element');
        $(window).off('.bottom_fixed_element');
        $('.o_bottom_fixed_element').removeClass('o_bottom_fixed_element_hidden');
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Hidestheelementsthatarefixedatthebottomofthescreenifthe
     *scrollreachesthebottomofthepageandiftheelementshideabutton.
     *
     *@private
     */
    _hideBottomFixedElements(){
        //Note:checkinthewholeDOMinsteadof#wrapwrapasunfortunately
        //somethingsarestillputoutsideofthe#wrapwrap(likethelivechat
        //buttonwhichisthemainreasonofthiscode).
        const$bottomFixedElements=$('.o_bottom_fixed_element');
        if(!$bottomFixedElements.length){
            return;
        }

        $bottomFixedElements.removeClass('o_bottom_fixed_element_hidden');
        if((this.$scrollingElement[0].offsetHeight+this.$scrollingElement[0].scrollTop)>=(this.$scrollingElement[0].scrollHeight-2)){
            constbuttonEls=[...this.$('.btn:visible')];
            for(constelof$bottomFixedElements){
                if(buttonEls.some(button=>dom.areColliding(button,el))){
                    el.classList.add('o_bottom_fixed_element_hidden');
                }
            }
        }
    },
});

/**
 *Thewebsites,bydefault,useimagelazyloadingviatheloading="lazy"
 *attributeon<img>elements.However,thisdoesnotworkgreatonall
 *browsers.Thiswidgetfixesthebehaviorswithaslesscodeaspossible.
 */
registry.ImagesLazyLoading=publicWidget.Widget.extend({
    selector:'#wrapwrap',

    /**
     *@override
     */
    start(){
        //Foreachimageonthepage,forcea1pxmin-heightsothatChrome
        //understandstheimageexistsondifferentzoomsizesofthebrowser.
        //Indeed,withoutthis,ona90%zoom,someimageswereneverloaded.
        //Oncetheimagehasbeenloaded,the1pxmin-heightisremoved.
        //Note:anotherpossiblesolutionwithoutJSwouldbethisCSSrule:
        //```
        //[loading="lazy"]{
        //    min-height:1px;
        //}
        //```
        //ThiswouldsolvetheproblemthesamewaywithaCSSrulewitha
        //verysmallpriority(anyclasssettingamin-heightwouldstillhave
        //priority).However,themin-heightwouldalwaysbeforcedevenonce
        //theimageisloaded,whichcouldmesswithsomelayoutsrelyingon
        //theimageintrinsicmin-height.
        constimgEls=this.$target[0].querySelectorAll('img[loading="lazy"]');
        for(constimgElofimgEls){
            //Writeinitialmin-heightonthedataset,sothatitcanalso
            //beproperlyrestoredonwidgetdestroy.
            imgEl.dataset.lazyLoadingInitialMinHeight=imgEl.style.minHeight;
            imgEl.style.minHeight='1px';
            wUtils.onceAllImagesLoaded($(imgEl)).then(()=>{
                if(this.isDestroyed()){
                    return;
                }
                this._restoreImage(imgEl);
            });
        }
        returnthis._super(...arguments);
    },
    /**
     *@override
     */
    destroy(){
        this._super(...arguments);
        constimgEls=this.$target[0].querySelectorAll('img[data-lazy-loading-initial-min-height]');
        for(constimgElofimgEls){
            this._restoreImage(imgEl);
        }
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{HTMLImageElement}imgEl
     */
    _restoreImage(imgEl){
        imgEl.style.minHeight=imgEl.dataset.lazyLoadingInitialMinHeight;
        deleteimgEl.dataset.lazyLoadingInitialMinHeight;
    },
});

/**
 *@todowhilethissolutionmitigatestheissue,itisnotfixingitentirely
 *butmainly,weshouldfindabettersolutionthanaJSsolutionassoonas
 *oneisavailableandideallywithouthavingtomakeuglypatchestotheSVGs.
 *
 *DuetoabugonChromewhenusingbrowserzoom,thereissometimesagap
 *betweensectionswithshapes.Thisgapisduetoaroundingissuewhen
 *positioningtheSVGbackgroundimages.Thiscodereducestheroundingerror
 *byensuringthatshapeelementsalwayshaveawidthvalueasclosetoan
 *integeraspossible.
 *
 *Note:agapalsoappearsbetweensomeshapeswithoutzoom.Thisislikely
 *duetoerrorintheshapesthemselves.Manythingsweredonetotryandfix
 *this,buttheremainingerrorswilllikelybefixedwithareviewofthe
 *shapesinfutureFlectraversions.
 *
 */!\
 *Ifabettersolutionforstablecomesup,thiswidgetbehaviormaybe
 *disabled,avoiddependingonitifpossible.
 */!\
 */
registry.ZoomedBackgroundShape=publicWidget.Widget.extend({
    selector:'.o_we_shape',
    disabledInEditableMode:false,

    /**
     *@override
     */
    start(){
        this._onBackgroundShapeResize();
        this.throttledShapeResize=_.throttle(()=>this._onBackgroundShapeResize(),25);
        window.addEventListener('resize',this.throttledShapeResize);
        returnthis._super(...arguments);
    },
    /**
     *@override
     */
    destroy(){
        this._updateShapePosition();
        window.removeEventListener('resize',this.throttledShapeResize);
        this._super(...arguments);
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Updatestheleftandrightoffsetoftheshape.
     *
     *@private
     *@param{string}offset
     */
    _updateShapePosition(offset=''){
        this.el.style.left=offset;
        this.el.style.right=offset;
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _onBackgroundShapeResize(){
        this._updateShapePosition();
        //Getthedecimalpartoftheshapeelementwidth.
        letdecimalPart=this.el.getBoundingClientRect().width%1;
        //Roundtotwodecimalplaces.
        decimalPart=Math.round((decimalPart+Number.EPSILON)*100)/100;
        //Ifthereisadecimalpart.(e.g.Chrome+browserzoomenabled)
        if(decimalPart>0){
            //Compensateforthegapbygivinganintegerwidthvaluetothe
            //shapebychangingits"right"and"left"positions.
            letoffset=(decimalPart<0.5?decimalPart:decimalPart-1)/2;
            //Thisnevercausesthehorizontalscrollbartoappearbecauseit
            //onlyappearsiftheoverflowtotherightexceeds0.333px.
            this._updateShapePosition(offset+'px');
        }
    },
});

return{
    Widget:publicWidget.Widget,
    Animation:Animation,
    registry:registry,

    Class:Animation,//Deprecated
};
});
