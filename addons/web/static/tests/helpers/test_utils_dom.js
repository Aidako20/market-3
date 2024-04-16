flectra.define('web.test_utils_dom',function(require){
    "usestrict";

    constconcurrency=require('web.concurrency');
    constWidget=require('web.Widget');

    /**
     *DOMTestUtils
     *
     *ThismoduledefinesvariousutilityfunctionstohelpsimulateDOMevents.
     *
     *Notethatallmethodsdefinedinthismoduleareexportedinthemain
     *testUtilsfile.
     */

    //-------------------------------------------------------------------------
    //Privatefunctions
    //-------------------------------------------------------------------------

    //TriggerEventhelpers
    constkeyboardEventBubble=args=>Object.assign({},args,{bubbles:true,keyCode:args.which});
    constmouseEventMapping=args=>Object.assign({},args,{
        bubbles:true,
        cancelable:true,
        clientX:args?args.clientX||args.pageX:undefined,
        clientY:args?args.clientY||args.pageY:undefined,
        view:window,
    });
    constmouseEventNoBubble=args=>Object.assign({},args,{
        bubbles:false,
        cancelable:false,
        clientX:args?args.clientX||args.pageX:undefined,
        clientY:args?args.clientY||args.pageY:undefined,
        view:window,
    });
    constnoBubble=args=>Object.assign({},args,{bubbles:false});
    constonlyBubble=args=>Object.assign({},args,{bubbles:true});
    //TriggerEventconstructor/argsprocessormapping
    constEVENT_TYPES={
        auxclick:{constructor:MouseEvent,processParameters:mouseEventMapping},
        click:{constructor:MouseEvent,processParameters:mouseEventMapping},
        contextmenu:{constructor:MouseEvent,processParameters:mouseEventMapping},
        dblclick:{constructor:MouseEvent,processParameters:mouseEventMapping},
        mousedown:{constructor:MouseEvent,processParameters:mouseEventMapping},
        mouseup:{constructor:MouseEvent,processParameters:mouseEventMapping},

        mousemove:{constructor:MouseEvent,processParameters:mouseEventMapping},
        mouseenter:{constructor:MouseEvent,processParameters:mouseEventNoBubble},
        mouseleave:{constructor:MouseEvent,processParameters:mouseEventNoBubble},
        mouseover:{constructor:MouseEvent,processParameters:mouseEventMapping},
        mouseout:{constructor:MouseEvent,processParameters:mouseEventMapping},

        focus:{constructor:FocusEvent,processParameters:noBubble},
        focusin:{constructor:FocusEvent,processParameters:onlyBubble},
        blur:{constructor:FocusEvent,processParameters:noBubble},

        cut:{constructor:ClipboardEvent,processParameters:onlyBubble},
        copy:{constructor:ClipboardEvent,processParameters:onlyBubble},
        paste:{constructor:ClipboardEvent,processParameters:onlyBubble},

        keydown:{constructor:KeyboardEvent,processParameters:keyboardEventBubble},
        keypress:{constructor:KeyboardEvent,processParameters:keyboardEventBubble},
        keyup:{constructor:KeyboardEvent,processParameters:keyboardEventBubble},

        drag:{constructor:DragEvent,processParameters:onlyBubble},
        dragend:{constructor:DragEvent,processParameters:onlyBubble},
        dragenter:{constructor:DragEvent,processParameters:onlyBubble},
        dragstart:{constructor:DragEvent,processParameters:onlyBubble},
        dragleave:{constructor:DragEvent,processParameters:onlyBubble},
        dragover:{constructor:DragEvent,processParameters:onlyBubble},
        drop:{constructor:DragEvent,processParameters:onlyBubble},

        input:{constructor:InputEvent,processParameters:onlyBubble},

        compositionstart:{constructor:CompositionEvent,processParameters:onlyBubble},
        compositionend:{constructor:CompositionEvent,processParameters:onlyBubble},
    };

    /**
     *CheckifanobjectisaninstanceofEventTarget.
     *
     *@param{Object}node
     *@returns{boolean}
     */
    function_isEventTarget(node){
        if(!node){
            thrownewError(`Providednodeis${node}.`);
        }
        if(nodeinstanceofwindow.top.EventTarget){
            returntrue;
        }
        constcontextWindow=node.defaultView||//document
            (node.ownerDocument&&node.ownerDocument.defaultView);//iframenode
        returncontextWindow&&nodeinstanceofcontextWindow.EventTarget;
    }

    //-------------------------------------------------------------------------
    //Publicfunctions
    //-------------------------------------------------------------------------

    /**
     *Clickonaspecifiedelement.Iftheoptionfirstorlastisnotspecified,
     *thismethodalsochecktheunicityandthevisibilityofthetarget.
     *
     *@param{string|EventTarget|EventTarget[]}el(ifstring:itisa(jquery)selector)
     *@param{Object}[options={}]clickoptions
     *@param{boolean}[options.allowInvisible=false]iftrue,clicksonthe
     *  elementeventifitisinvisible
     *@param{boolean}[options.first=false]iftrue,clicksonthefirstelement
     *@param{boolean}[options.last=false]iftrue,clicksonthelastelement
     *@returns{Promise}
     */
    asyncfunctionclick(el,options={}){
        letmatches,target;
        letselectorMsg="";
        if(typeofel==='string'){
            el=$(el);
        }
        if(el.disabled||(elinstanceofjQuery&&el.get(0).disabled)){
            thrownewError("Can'tclickonadisabledbutton");
        }
        if(_isEventTarget(el)){
            //EventTarget
            matches=[el];
        }else{
            //AnyotheriterableobjectcontainingEventTargetobjects(jQuery,HTMLCollection,etc.)
            matches=[...el];
        }

        constvalidMatches=options.allowInvisible?
            matches:matches.filter(t=>$(t).is(':visible'));

        if(options.first){
            if(validMatches.length===1){
                thrownewError(`Thereshouldbemorethanonevisibletarget${selectorMsg}. If`+
                    'youaresurethatthereisexactlyonetarget,pleaseusethe'+
                    'clickfunctioninsteadoftheclickFirstfunction');
            }
            target=validMatches[0];
        }elseif(options.last){
            if(validMatches.length===1){
                thrownewError(`Thereshouldbemorethanonevisibletarget${selectorMsg}. If`+
                    'youaresurethatthereisexactlyonetarget,pleaseusethe'+
                    'clickfunctioninsteadoftheclickLastfunction');
            }
            target=validMatches[validMatches.length-1];
        }elseif(validMatches.length!==1){
            thrownewError(`Found${validMatches.length}elementstoclickon,insteadof1${selectorMsg}`);
        }else{
            target=validMatches[0];
        }
        if(validMatches.length===0&&matches.length>0){
            thrownewError(`Elementtoclickonisnotvisible${selectorMsg}`);
        }

        returntriggerEvent(target,'click');
    }

    /**
     *Clickonthefirstelementofalistofelements. Notethatifthelisthas
     *onlyonevisibleelement,wetriggeranerror.Inthatcase,itisbetterto
     *usetheclickhelperinstead.
     *
     *@param{string|EventTarget|EventTarget[]}el(ifstring:itisa(jquery)selector)
     *@param{boolean}[options={}]clickoptions
     *@param{boolean}[options.allowInvisible=false]iftrue,clicksonthe
     *  elementeventifitisinvisible
     *@returns{Promise}
     */
    asyncfunctionclickFirst(el,options){
        returnclick(el,Object.assign({},options,{first:true}));
    }

    /**
     *Clickonthelastelementofalistofelements. Notethatifthelisthas
     *onlyonevisibleelement,wetriggeranerror.Inthatcase,itisbetterto
     *usetheclickhelperinstead.
     *
     *@param{string|EventTarget|EventTarget[]}el(ifstring:itisa(jquery)selector)
     *@param{boolean}[options={}]clickoptions
     *@param{boolean}[options.allowInvisible=false]iftrue,clicksonthe
     *  elementeventifitisinvisible
     *@returns{Promise}
     */
    asyncfunctionclickLast(el,options){
        returnclick(el,Object.assign({},options,{last:true}));
    }

    /**
     *Simulateadraganddropoperationbetween2jquerynodes:$eland$to.
     *Thisisacrudesimulation,withonlythemousedown,mousemoveandmouseup
     *events,butitisenoughtohelptestdraganddropoperationswithjqueryUI
     *sortable.
     *
     *@todo:removethewithTrailingClickoptionwhenthejqueryupdatebranchis
     *  merged. Thisisnotthedefaultasofnow,becausehandlersaretriggered
     *  synchronously,whichisnotthesameasthe'reality'.
     *
     *@param{jQuery|EventTarget}$el
     *@param{jQuery|EventTarget}$to
     *@param{Object}[options]
     *@param{string|Object}[options.position='center']targetposition:
     *  caneitherbeoneof{'top','bottom','left','right'}or
     *  anobjectwithtwoattributes(topandleft))
     *@param{boolean}[options.disableDrop=false]whethertotriggerthedropaction
     *@param{boolean}[options.continueMove=false]whethertotriggerthe
     *  mousedownaction(willonlyworkafteranothercallofthisfunctionwith
     *  withoutthisoption)
     *@param{boolean}[options.withTrailingClick=false]iftrue,thisutility
     *  functionwillalsotriggeraclickonthetargetafterthemouseupevent
     *  (thisisactuallywhathappenswhenadraganddropoperationisdone)
     *@param{jQuery|EventTarget}[options.mouseenterTarget=undefined]targetofthemouseenterevent
     *@param{jQuery|EventTarget}[options.mousedownTarget=undefined]targetofthemousedownevent
     *@param{jQuery|EventTarget}[options.mousemoveTarget=undefined]targetofthemousemoveevent
     *@param{jQuery|EventTarget}[options.mouseupTarget=undefined]targetofthemouseupevent
     *@param{jQuery|EventTarget}[options.ctrlKey=undefined]ifthectrlkeyshouldbeconsideredpressedatthetimeofmouseup
     *@returns{Promise}
     */
    asyncfunctiondragAndDrop($el,$to,options){
        letel=null;
        if(_isEventTarget($el)){
            el=$el;
            $el=$(el);
        }
        if(_isEventTarget($to)){
            $to=$($to);
        }
        options=options||{};
        constposition=options.position||'center';
        constelementCenter=$el.offset();
        consttoOffset=$to.offset();

        if(typeofposition==='object'){
            toOffset.top+=position.top+1;
            toOffset.left+=position.left+1;
        }else{
            toOffset.top+=$to.outerHeight()/2;
            toOffset.left+=$to.outerWidth()/2;
            constvertical_offset=(toOffset.top<elementCenter.top)?-1:1;
            if(position==='top'){
                toOffset.top-=$to.outerHeight()/2+vertical_offset;
            }elseif(position==='bottom'){
                toOffset.top+=$to.outerHeight()/2-vertical_offset;
            }elseif(position==='left'){
                toOffset.left-=$to.outerWidth()/2;
            }elseif(position==='right'){
                toOffset.left+=$to.outerWidth()/2;
            }
        }

        if($to[0].ownerDocument!==document){
            //weareinaniframe
            constbound=$('iframe')[0].getBoundingClientRect();
            toOffset.left+=bound.left;
            toOffset.top+=bound.top;
        }
        awaittriggerEvent(options.mouseenterTarget||el||$el,'mouseover',{},true);
        if(!(options.continueMove)){
            elementCenter.left+=$el.outerWidth()/2;
            elementCenter.top+=$el.outerHeight()/2;

            awaittriggerEvent(options.mousedownTarget||el||$el,'mousedown',{
                which:1,
                pageX:elementCenter.left,
                pageY:elementCenter.top
            },true);
        }
        awaittriggerEvent(options.mousemoveTarget||el||$el,'mousemove',{
            which:1,
            pageX:toOffset.left,
            pageY:toOffset.top
        },true);

        if(!options.disableDrop){
            awaittriggerEvent(options.mouseupTarget||el||$el,'mouseup',{
                which:1,
                pageX:toOffset.left,
                pageY:toOffset.top,
                ctrlKey:options.ctrlKey,
            },true);
            if(options.withTrailingClick){
                awaittriggerEvent(options.mouseupTarget||el||$el,'click',{},true);
            }
        }else{
            //It'simpossibletodraganotherelementwhenoneisalready
            //beingdragged.Soit'snecessarytofinishthedropwhenthetestis
            //overotherwiseit'simpossibleforthenextteststodragand
            //dropelements.
            $el.on('remove',function(){
                triggerEvent($el,'mouseup',{},true);
            });
        }
        returnreturnAfterNextAnimationFrame();
    }

    /**
     *Helpermethodtoretrieveadistinctitemfromacollectionofelementsdefined
     *bythegiven"selector"string.Itcaneitherbetheindexoftheitemorits
     *innertext.
     *@param{Element}el
     *@param{string}selector
     *@param{number|string}[elFinder=0]
     *@returns{Element|null}
     */
    functionfindItem(el,selector,elFinder=0){
        constelements=[...getNode(el).querySelectorAll(selector)];
        if(!elements.length){
            thrownewError(`Noelementfoundwithselector"${selector}".`);
        }
        switch(typeofelFinder){
            case"number":{
                constmatch=elements[elFinder];
                if(!match){
                    thrownewError(
                        `Noelementwithselector"${selector}"atindex${elFinder}.`
                    );
                }
                returnmatch;
            }
            case"string":{
                constmatch=elements.find(
                    (el)=>el.innerText.trim().toLowerCase()===elFinder.toLowerCase()
                );
                if(!match){
                    thrownewError(
                        `Noelementwithselector"${selector}"containing"${elFinder}".
                    `);
                }
                returnmatch;
            }
            default:thrownewError(
                `Invalidprovidedelementfinder:mustbeanumber|string|function.`
            );
        }
    }

    /**
     *HelperfunctionusedtoextractanHTMLEventTargetelementfromagiven
     *target.Theextractedelementwilldependonthetargettype:
     *-Component|Widget->el
     *-jQuery->associatedelement(musthave1)
     *-HTMLCollection(orsimilar)->firstelement(musthave1)
     *-string->resultofdocument.querySelectorwithstring
     *-else->asis
     *@private
     *@param{(Component|Widget|jQuery|HTMLCollection|HTMLElement|string)}target
     *@returns{EventTarget}
     */
    functiongetNode(target){
        letnodes;
        if(targetinstanceofowl.Component||targetinstanceofWidget){
            nodes=[target.el];
        }elseif(typeoftarget==='string'){
            nodes=document.querySelectorAll(target);
        }elseif(target===jQuery){//jQuery(or$)
            nodes=[document.body];
        }elseif(target.length){//jQueryinstance,HTMLCollectionorarray
            nodes=target;
        }else{
            nodes=[target];
        }
        if(nodes.length!==1){
            thrownewError(`Found${nodes.length}nodesinsteadof1.`);
        }
        constnode=nodes[0];
        if(!node){
            thrownewError(`Expectedanodeandgot${node}.`);
        }
        if(!_isEventTarget(node)){
            thrownewError(`ExpectednodetobeaninstanceofEventTargetandgot${node.constructor.name}.`);
        }
        returnnode;
    }

    /**
     *Openthedatepickerofagivenelement.
     *
     *@param{jQuery}$datepickerElelementtowhichadatepickerisattached
     */
    asyncfunctionopenDatepicker($datepickerEl){
        returnclick($datepickerEl.find('.o_datepicker_input'));
    }

    /**
     *ReturnsapromisethatwillberesolvedafterthenextAnimationFrameafter
     *thenexttick
     *
     *ThisisusefultoguaranteethatOWLhashadthetimetorender
     *
     *@returns{Promise}
     */
    asyncfunctionreturnAfterNextAnimationFrame(){
        awaitconcurrency.delay(0);
        awaitnewPromise(resolve=>{
            window.requestAnimationFrame(resolve);
        });
    }

    /**
     *Triggeraneventonthespecifiedtarget.
     *ThisfunctionwilldispatchanativeeventtoanEventTargetora
     *jQueryeventtoajQueryobject.Thisbehaviourcanbeoverriddenbythe
     *jqueryoption.
     *
     *@param{EventTarget|EventTarget[]}el
     *@param{string}eventTypeeventtype
     *@param{Object}[eventAttrs]eventattributes
     *  onajQueryelementwiththe`$.fn.trigger`function
     *@param{Boolean}[fast=false]trueifthetriggereventhavetowaitforasingletickinsteadofwaitingforthenextanimationframe
     *@returns{Promise}
     */
    asyncfunctiontriggerEvent(el,eventType,eventAttrs={},fast=false){
        letmatches;
        letselectorMsg="";
        if(_isEventTarget(el)){
            matches=[el];
        }else{
            matches=[...el];
        }

        if(matches.length!==1){
            thrownewError(`Found${matches.length}elementstotrigger"${eventType}"on,insteadof1${selectorMsg}`);
        }

        consttarget=matches[0];
        letevent;

        if(!EVENT_TYPES[eventType]&&!EVENT_TYPES[eventType.type]){
            event=newEvent(eventType,Object.assign({},eventAttrs,{bubbles:true}));
        }else{
            if(typeofeventType==="object"){
                const{constructor,processParameters}=EVENT_TYPES[eventType.type];
                consteventParameters=processParameters(eventType);
                event=newconstructor(eventType.type,eventParameters);
            }else{
                const{constructor,processParameters}=EVENT_TYPES[eventType];
                event=newconstructor(eventType,processParameters(eventAttrs));
            }
        }
        target.dispatchEvent(event);
        returnfast?undefined:returnAfterNextAnimationFrame();
    }

    /**
     *Triggermultipleeventsonthespecifiedelement.
     *
     *@param{EventTarget|EventTarget[]}el
     *@param{string[]}eventstheeventsyouwanttotrigger
     *@returns{Promise}
     */
    asyncfunctiontriggerEvents(el,events){
        if(elinstanceofjQuery){
            if(el.length!==1){
                thrownewError(`targethaslength${el.length}insteadof1`);
            }
        }
        if(typeofevents==='string'){
            events=[events];
        }

        for(lete=0;e<events.length;e++){
            awaittriggerEvent(el,events[e]);
        }
    }

    /**
     *Simulateakeypresseventforagivencharacter
     *
     *@param{string}charthecharacter,or'ENTER'
     *@returns{Promise}
     */
    asyncfunctiontriggerKeypressEvent(char){
        letkeycode;
        if(char==='Enter'){
            keycode=$.ui.keyCode.ENTER;
        }elseif(char==="Tab"){
            keycode=$.ui.keyCode.TAB;
        }else{
            keycode=char.charCodeAt(0);
        }
        returntriggerEvent(document.body,'keypress',{
            key:char,
            keyCode:keycode,
            which:keycode,
        });
    }

    /**
     *simulateamouseeventwithacustomeventwhoaddtheitemposition.Thisis
     *sometimesnecessarybecausethebasicwaytotriggeranevent(suchas
     *$el.trigger('mousemove'));)istoocrudeforsomeuses.
     *
     *@param{jQuery|EventTarget}$el
     *@param{string}typeamouseeventtype,suchas'mousedown'or'mousemove'
     *@returns{Promise}
     */
    asyncfunctiontriggerMouseEvent($el,type){
        constel=$elinstanceofjQuery?$el[0]:$el;
        if(!el){
            thrownewError(`notargetfoundtotriggerMouseEvent`);
        }
        constrect=el.getBoundingClientRect();
        //trytoclickaroundthecenteroftheelement,biasedtothebottom
        //rightaschrome messesupwhenclickingonthetop-leftcorner...
        constleft=rect.x+Math.ceil(rect.width/2);
        consttop=rect.y+Math.ceil(rect.height/2);
        returntriggerEvent(el,type,{which:1,clientX:left,clientY:top});
    }

    /**
     *simulateamouseeventwithacustomeventonapositionxandy.Thisis
     *sometimesnecessarybecausethebasicwaytotriggeranevent(suchas
     *$el.trigger('mousemove'));)istoocrudeforsomeuses.
     *
     *@param{integer}x
     *@param{integer}y
     *@param{string}typeamouseeventtype,suchas'mousedown'or'mousemove'
     *@returns{HTMLElement}
     */
    asyncfunctiontriggerPositionalMouseEvent(x,y,type){
        constev=document.createEvent("MouseEvent");
        constel=document.elementFromPoint(x,y);
        ev.initMouseEvent(
            type,
            true/*bubble*/,
            true/*cancelable*/,
            window,null,
            x,y,x,y,/*coordinates*/
            false,false,false,false,/*modifierkeys*/
            0/*leftbutton*/,null
        );
        el.dispatchEvent(ev);
        returnel;
    }

    return{
        click,
        clickFirst,
        clickLast,
        dragAndDrop,
        findItem,
        getNode,
        openDatepicker,
        returnAfterNextAnimationFrame,
        triggerEvent,
        triggerEvents,
        triggerKeypressEvent,
        triggerMouseEvent,
        triggerPositionalMouseEvent,
    };
});
