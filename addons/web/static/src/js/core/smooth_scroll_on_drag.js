flectra.define('web/static/src/js/core/smooth_scroll_on_drag.js',function(require){
"usestrict";

constClass=require('web.Class');
constmixins=require('web.mixins');

/**
 *ProvidesahelperforSmoothScrollOnDragoptions.offsetElements
 */
constOffsetElementsHelper=Class.extend({

    /**
     *@constructor
     *@param{Object}offsetElements
     *@param{jQuery}[offsetElements.$top]topoffsetelement
     *@param{jQuery}[offsetElements.$right]rightoffsetelement
     *@param{jQuery}[offsetElements.$bottom]bottomoffsetelement
     *@param{jQuery}[offsetElements.$left]leftoffsetelement
     */
    init:function(offsetElements){
        this.offsetElements=offsetElements;
    },
    top:function(){
        if(!this.offsetElements.$top||!this.offsetElements.$top.length){
            return0;
        }
        returnthis.offsetElements.$top.get(0).getBoundingClientRect().bottom;
    },
    right:function(){
        if(!this.offsetElements.$right||!this.offsetElements.$right.length){
            return0;
        }
        returnthis.offsetElements.$right.get(0).getBoundingClientRect().left;
    },
    bottom:function(){
        if(!this.offsetElements.$bottom||!this.offsetElements.$bottom.length){
            return0;
        }
        returnthis.offsetElements.$bottom.get(0).getBoundingClientRect().top;
    },
    left:function(){
        if(!this.offsetElements.$left||!this.offsetElements.$left.length){
            return0;
        }
        returnthis.offsetElements.$left.get(0).getBoundingClientRect().right;
    },
});

/**
 *Providessmoothscrollbehaviourondrag.
 */
constSmoothScrollOnDrag=Class.extend(mixins.ParentedMixin,{

    /**
     *@constructor
     *@param{Object}parentTheparentwidgetthatusesthisclass.
     *@param{jQuery}$elementTheelementthesmoothscrollondraghastobeseton.
     *@param{jQuery}$scrollTargetTheelementthescrollwillbetriggeredon.
     *@param{Object}[options={}]
     *@param{Object}[options.jQueryDraggableOptions={}]Theconfigurationtobepassedto
     *       thejQuerydraggablefunction(allwillbepassedexceptscrollwhichwill
     *       beoverriddentofalse).
     *@param{Number}[options.scrollOffsetThreshold=150](Integer)Thedistancefromthe
     *       bottom/topoftheoptions.$scrollTargetfromwhichthesmoothscrollwillbe
     *       triggered.
     *@param{Number}[options.scrollStep=20](Integer)Thestepofthescroll.
     *@param{Number}[options.scrollTimerInterval=5](Integer)Theinterval(inms)the
     *       scrollStepwillbeapplied.
     *@param{Object}[options.scrollBoundaries={}]Specifieswhetherscrollcanstillbetriggered
     *       whendragging$elementoutsideoftarget.
     *@param{Object}[options.scrollBoundaries.top=true]Specifieswhetherscrollcanstillbetriggered
     *       whendragging$elementabovethetopedgeoftarget.
     *@param{Object}[options.scrollBoundaries.right=true]Specifieswhetherscrollcanstillbetriggered
     *       whendragging$elementaftertherightedgeoftarget.
     *@param{Object}[options.scrollBoundaries.bottom=true]Specifieswhetherscrollcanstillbetriggered
     *       whendragging$elementbellowthebottomedgeoftarget.
     *@param{Object}[options.scrollBoundaries.left=true]Specifieswhetherscrollcanstillbetriggered
     *       whendragging$elementbeforetheleftedgeoftarget.
     *@param{Object}[options.offsetElements={}]Visibleelementsin$scrollTargetthat
     *       reduce$scrollTargetdragvisiblearea(scrollwillbetriggeredsoonerthan
     *       normally).Aselectorispassedsothatelementssuchasautomaticallyhidden
     *       menucanthenbecorrectlyhandled.
     *@param{jQuery}[options.offsetElements.$top]Visibletopoffsetelementwhichheightwill
     *       betakenintoaccountwhentriggeringscrollatthetopofthe$scrollTarget.
     *@param{jQuery}[options.offsetElements.$right]Visiblerightoffsetelementwhichwidth
     *       willbetakenintoaccountwhentriggeringscrollattherightsideofthe
     *       $scrollTarget.
     *@param{jQuery}[options.offsetElements.$bottom]Visiblebottomoffsetelementwhichheight
     *       willbetakenintoaccountwhentriggeringscrollatbottomofthe$scrollTarget.
     *@param{jQuery}[options.offsetElements.$left]Visibleleftoffsetelementwhichwidth
     *       willbetakenintoaccountwhentriggeringscrollattheleftsideofthe
     *       $scrollTarget.
     *@param{boolean}[options.disableHorizontalScroll=false]Disablehorizontalscrollifnotneeded.
     */
    init(parent,$element,$scrollTarget,options={}){
        mixins.ParentedMixin.init.call(this);
        this.setParent(parent);

        this.$element=$element;
        this.$scrollTarget=$scrollTarget;
        this.options=options;
        this.targetWindow=this.$element[0].ownerDocument.defaultView;
        constinsideIframe=this.targetWindow!==window.top;

        //Settingoptionaloptionstotheirdefaultvalueifnotprovided
        this.options.jQueryDraggableOptions=this.options.jQueryDraggableOptions||{};
        if(!this.options.jQueryDraggableOptions.cursorAt){
            this.$element.on('mousedown.smooth_scroll',this._onElementMouseDown.bind(this));
        }
        this.options.scrollOffsetThreshold=this.options.scrollOffsetThreshold||150;
        this.options.scrollStep=this.options.scrollStep||20;
        this.options.scrollTimerInterval=this.options.scrollTimerInterval||5;
        this.options.offsetElements=this.options.offsetElements||{};
        this.options.offsetElementsManager=newOffsetElementsHelper(this.options.offsetElements);
        this.options.scrollBoundaries=Object.assign({
            top:true,
            right:true,
            bottom:true,
            left:true
        },this.options.scrollBoundaries);

        this.autoScrollHandler=null;

        this.scrollStepDirectionEnum={
            up:-1,
            right:1,
            down:1,
            left:-1,
        };

        this.options.jQueryDraggableOptions.scroll=false;
        this.options.disableHorizontalScroll=this.options.disableHorizontalScroll||false;
        constdraggableOptions=Object.assign({},this.options.jQueryDraggableOptions,{
            start:(ev,ui)=>{
                this._onSmoothDragStart(ev,ui,this.options.jQueryDraggableOptions.start);
                if(insideIframe){
                    this.onParentWindowMouseup=this._onParentWindowMouseup.bind(this);
                    window.top.addEventListener('mouseup',this.onParentWindowMouseup,{once:true});
                }
            },
            drag:(ev,ui)=>this._onSmoothDrag(ev,ui,this.options.jQueryDraggableOptions.drag),
            stop:(ev,ui)=>{
                if(insideIframe){
                    window.top.removeEventListener('mouseup',this.onParentWindowMouseup,{once:true});
                }
                this._onSmoothDragStop(ev,ui,this.options.jQueryDraggableOptions.stop);
            }
        });
        this.$element.draggable(draggableOptions);
    },
    /**
     *@override
     */
    destroy:function(){
        mixins.ParentedMixin.destroy.call(this);
        this.$element.off('.smooth_scroll');
        this._stopSmoothScroll();
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Startsthescrollprocessusingtheoptions.
     *Theoptionswillbeupdateddynamicallywhenthehandler_onSmoothDrag
     *willbecalled.Theintervalwillbeclearedwhenthehandler
     *_onSmoothDragStopwillbecalled.
     *
     *@private
     *@param{Object}uiThejQuerydraghandleruiparameter.
     */
    _startSmoothScroll(ui){
        this._stopSmoothScroll();
        this.autoScrollHandler=setInterval(
            ()=>{
                //PreventsDelta'sfrombeingdifferentfrom0whenscrollshouldnotoccur(exceptwhen
                //helperisdraggedoutsideofthis.$scrollTarget'svisibleareaasitincreases
                //this.$scrollTarget'sscrollHeight).
                //Also,thiscodepreventsthehelperfrombeingincorrectlyrepositionedwhentargetis
                //achildofthis.$scrollTarget.
                this.verticalDelta=Math.min(
                    //Ensuresscrollingstopswhendraggingbellowthis.$scrollTargetbottom.
                    Math.max(
                        0,
                        this.$scrollTarget.get(0).scrollHeight
                        -(this.$scrollTarget.scrollTop()+this.$scrollTarget.innerHeight())
                    ),
                    //Ensuresscrollingstopswhendraggingabovethis.$scrollTargettop.
                    Math.max(
                        this.verticalDelta,
                        -this.$scrollTarget.scrollTop()
                    )
                );
                this.horizontalDelta=Math.min(
                    //Ensuresscrollingstopswhendragginglefttothis.$scrollTarget.
                    Math.max(
                        0,
                        this.$scrollTarget.get(0).scrollWidth
                        -(this.$scrollTarget.scrollLeft()+this.$scrollTarget.innerWidth())
                    ),
                    //Ensuresscrollingstopswhendraggingrighttothis.$scrollTarget.
                    Math.max(
                        this.horizontalDelta,
                        -this.$scrollTarget.scrollLeft()
                    )
                );

                //Keephelperatrightpositionwhilescrollingwhenhelperisachildofthis.$scrollTarget.
                if(this.scrollTargetIsParent){
                    constoffset=ui.helper.offset();
                    ui.helper.offset({
                        top:offset.top+this.verticalDelta,
                        left:offset.left+this.horizontalDelta
                    });
                }
                this.$scrollTarget.scrollTop(
                    this.$scrollTarget.scrollTop()+
                    this.verticalDelta
                );
                if(!this.options.disableHorizontalScroll){
                    this.$scrollTarget.scrollLeft(
                        this.$scrollTarget.scrollLeft()+
                        this.horizontalDelta
                    );
                }
            },
            this.options.scrollTimerInterval
        );
    },
    /**
     *Stopsthescrollprocessifanyisrunning.
     *
     *@private
     */
    _stopSmoothScroll(){
        clearInterval(this.autoScrollHandler);
    },
    /**
     *Updatestheoptionsdependingontheoffsetpositionofthedraggable
     *helper.Inthesametimeoptionsareusedbyanintervaltotrigger
     *scrollbehaviour.
     *@see{@link_startSmoothScroll}forintervalimplementationdetails.
     *
     *@private
     *@param{Object}uiThejQuerydraghandleruiparameter.
     */
    _updatePositionOptions(ui){
        constdraggableHelperOffset=ui.offset;
        constscrollTargetOffset=this.$scrollTarget.offset();
        letvisibleOffset={
            top:draggableHelperOffset.top
                -scrollTargetOffset.top
                +this.options.jQueryDraggableOptions.cursorAt.top
                -this.options.offsetElementsManager.top(),
            right:scrollTargetOffset.left+this.$scrollTarget.outerWidth()
                -draggableHelperOffset.left
                -this.options.jQueryDraggableOptions.cursorAt.left
                -this.options.offsetElementsManager.right(),
            bottom:scrollTargetOffset.top+this.$scrollTarget.outerHeight()
                -draggableHelperOffset.top
                -this.options.jQueryDraggableOptions.cursorAt.top
                -this.options.offsetElementsManager.bottom(),
            left:draggableHelperOffset.left
                -scrollTargetOffset.left
                +this.options.jQueryDraggableOptions.cursorAt.left
                -this.options.offsetElementsManager.left(),
        };

        //Ifthis.$scrollTargetisthehtmltag,weneedtotakethescrollpositionintoaccount
        //asoffsetspositionsarecalculatedrelativetothedocument(thus<html>).
        if(this.scrollTargetIsDocument){
            constscrollTargetScrollTop=this.$scrollTarget.scrollTop();
            constscrollTargetScrollLeft=this.$scrollTarget.scrollLeft();
            visibleOffset.top-=scrollTargetScrollTop;
            visibleOffset.right+=scrollTargetScrollLeft;
            visibleOffset.bottom+=scrollTargetScrollTop;
            visibleOffset.left-=scrollTargetScrollLeft;
        }

        constscrollDecelerator={
            vertical:0,
            horizontal:0,
        };

        constscrollStepDirection={
            vertical:this.scrollStepDirectionEnum.down,
            horizontal:this.scrollStepDirectionEnum.right,
        };

        //Preventscrollifoutsideofscrollboundaries
        if((!this.options.scrollBoundaries.top&&visibleOffset.top<0)||
            (!this.options.scrollBoundaries.right&&visibleOffset.right<0)||
            (!this.options.scrollBoundaries.bottom&&visibleOffset.bottom<0)||
            (!this.options.scrollBoundaries.left&&visibleOffset.left<0)){
                scrollDecelerator.horizontal=1;
                scrollDecelerator.vertical=1;
        }else{
            //Manageverticalscroll
            if(visibleOffset.bottom<=this.options.scrollOffsetThreshold){
                scrollDecelerator.vertical=Math.max(0,visibleOffset.bottom)
                                           /this.options.scrollOffsetThreshold;
            }elseif(visibleOffset.top<=this.options.scrollOffsetThreshold){
                scrollDecelerator.vertical=Math.max(0,visibleOffset.top)
                                           /this.options.scrollOffsetThreshold;
                scrollStepDirection.vertical=this.scrollStepDirectionEnum.up;
            }else{
                scrollDecelerator.vertical=1;
            }

            //Managehorizontalscroll
            if(visibleOffset.right<=this.options.scrollOffsetThreshold){
                scrollDecelerator.horizontal=Math.max(0,visibleOffset.right)
                                             /this.options.scrollOffsetThreshold;
            }elseif(visibleOffset.left<=this.options.scrollOffsetThreshold){
                scrollDecelerator.horizontal=Math.max(0,visibleOffset.left)
                                             /this.options.scrollOffsetThreshold;
                scrollStepDirection.horizontal=this.scrollStepDirectionEnum.left;
            }else{
                scrollDecelerator.horizontal=1;
            }
        }

        this.verticalDelta=Math.ceil(scrollStepDirection.vertical*
            this.options.scrollStep*
            (1-Math.sqrt(scrollDecelerator.vertical)));
        this.horizontalDelta=Math.ceil(scrollStepDirection.horizontal*
            this.options.scrollStep*
            (1-Math.sqrt(scrollDecelerator.horizontal)));
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Calledwhenmousebuttonisdownonthis.$element.
     *Updatesthemousecursorpositionvariable.
     *
     *@private
     *@param{Object}evThejQuerymousedownhandlereventparameter.
     */
    _onElementMouseDown(ev){
        constelementOffset=$(ev.target).offset();
        this.options.jQueryDraggableOptions.cursorAt={
            top:ev.pageY-elementOffset.top,
            left:ev.pageX-elementOffset.left,
        };
    },
    /**
     *Calledwhendraggingtheelement.
     *Updatesthepositionoptionsandcalltheprovidedcallbackifany.
     *
     *@private
     *@param{Object}evThejQuerydraghandlereventparameter.
     *@param{Object}uiThejQuerydraghandleruiparameter.
     *@param{Function}onDragCallbackThejQuerydragcallback.
     */
    _onSmoothDrag(ev,ui,onDragCallback){
        this._updatePositionOptions(ui);
        if(typeofonDragCallback==='function'){
            onDragCallback.call(ui.helper,ev,ui);
        }
    },
    /**
     *Calledwhenstartingtodragtheelement.
     *Updatesthepositionparams,startssmoothscrollingprocessandcallthe
     *providedcallbackifany.
     *
     *@private
     *@param{Object}evThejQuerydraghandlereventparameter.
     *@param{Object}uiThejQuerydraghandleruiparameter.
     *@param{Function}onDragStartCallBackThejQuerydragcallback.
     */
    _onSmoothDragStart(ev,ui,onDragStartCallBack){
        this.scrollTargetIsDocument=this.$scrollTarget.is('html');
        this.scrollTargetIsParent=this.$scrollTarget.get(0).contains(this.$element.get(0));
        this._updatePositionOptions(ui);
        this._startSmoothScroll(ui);
        if(typeofonDragStartCallBack==='function'){
            onDragStartCallBack.call(ui.helper,ev,ui);
        }
    },
    /**
     *Calledwhenstoppingtodragtheelement.
     *Stopsthesmoothscrollingprocessandcalltheprovidedcallbackifany.
     *
     *@private
     *@param{Object}evThejQuerydraghandlereventparameter.
     *@param{Object}uiThejQuerydraghandleruiparameter.
     *@param{Function}onDragEndCallBackThejQuerydragcallback.
     */
    _onSmoothDragStop(ev,ui,onDragEndCallBack){
        this._stopSmoothScroll();
        if(typeofonDragEndCallBack==='function'){
            onDragEndCallBack.call(ui.helper,ev,ui);
        }
    },
    /**
     *Calledwhenthemouseisreleasedoutsidethepageiframe(e.g.the
     *editorpanelinWebsite).ThisisonlyusefulinChrome,wherethe'stop'
     *eventofjQueryDraggabledoesnottriggera'mouseup'eventoutsideof
     *the"preview"pageiframe.
     *
     *@private
     */
    _onParentWindowMouseup(){
        this.targetWindow.document.dispatchEvent(newEvent('mouseup'));
    },
});

returnSmoothScrollOnDrag;
});
