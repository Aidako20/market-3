flectra.define('barcodes.BarcodeEvents',function(require){
"usestrict";

varconfig=require('web.config');
varcore=require('web.core');
varmixins=require('web.mixins');
varsession=require('web.session');


//ForIE>=9,usethis,newCustomEvent(),insteadofnewEvent()
functionCustomEvent(event,params){
    params=params||{bubbles:false,cancelable:false,detail:undefined};
    varevt=document.createEvent('CustomEvent');
    evt.initCustomEvent(event,params.bubbles,params.cancelable,params.detail);
    returnevt;
   }
CustomEvent.prototype=window.Event.prototype;

varBarcodeEvents=core.Class.extend(mixins.PropertiesMixin,{
    timeout:null,
    key_pressed:{},
    buffered_key_events:[],
    //Regexptomatchabarcodeinputandextractitspayload
    //Note:tobuildininit()ifprefix/suffixcanbeconfigured
    regexp:/(.{3,})[\n\r\t]*/,
    //Byknowingtheterminalcharacterwecaninterpretbufferedkeys
    //asabarcodeassoonasit'sencountered(insteadofwaitingxms)
    suffix:/[\n\r\t]+/,
    //Keysfromabarcodescannerareusuallyprocessedasquickaspossible,
    //butsomescannerscanuseanintercharacterdelay(wesupport<=50ms)
    max_time_between_keys_in_ms:session.max_time_between_keys_in_ms||100,
    //Tobeabletoreceivethebarcodevalue,aninputmustbefocused.
    //Onmobiledevices,thiscausesthevirtualkeyboardtoopen.
    //Unfortunatelyitisnotpossibletoavoidthisbehavior...
    //Toavoidkeyboardflickeringateachdetectionofabarcodevalue,
    //wewanttokeepitopenforawhile(800ms).
    inputTimeOut:800,

    init:function(){
        mixins.PropertiesMixin.init.call(this);
        //Keepareferenceofthehandlerfunctionstousewhenaddingandremovingeventlisteners
        this.__keydown_handler=_.bind(this.keydown_handler,this);
        this.__keyup_handler=_.bind(this.keyup_handler,this);
        this.__handler=_.bind(this.handler,this);
        //BindeventhandleroncetheDOMisloaded
        //TODO:findawaytobeactiveonlywhentherearelistenersonthebus
        $(_.bind(this.start,this,false));

        //Mobiledevicedetection
        this.isChromeMobile=config.device.isMobileDevice&&navigator.userAgent.match(/Chrome/i);

        //Createsaninputwhowillreceivethebarcodescannervalue.
        this.$barcodeInput=$('<input/>',{
            name:'barcode',
            type:'text',
            css:{
                'position':'fixed',
                'top':'50%',
                'transform':'translateY(-50%)',
                'z-index':'-1',
                'opacity':'0',
            },
        });
        //Avoidtoshowautocompleteforanonappearinginput
        this.$barcodeInput.attr('autocomplete','off');

        this.__blurBarcodeInput=_.debounce(this._blurBarcodeInput,this.inputTimeOut);
    },

    handle_buffered_keys:function(){
        varstr=this.buffered_key_events.reduce(function(memo,e){returnmemo+String.fromCharCode(e.which)},'');
        varmatch=str.match(this.regexp);

        if(match){
            varbarcode=match[1];

            //Sendthetargetincasethereareseveralbarcodewidgetsonthesamepage(e.g.
            //registeringthelotnumbersinastockpicking)
            core.bus.trigger('barcode_scanned',barcode,this.buffered_key_events[0].target);

            //Dispatchabarcode_scannedDOMeventtoelementsthathavebarcode_events="true"set.
            if(this.buffered_key_events[0].target.getAttribute("barcode_events")==="true")
                $(this.buffered_key_events[0].target).trigger('barcode_scanned',barcode);
        }else{
            this.resend_buffered_keys();
        }

        this.buffered_key_events=[];
    },

    resend_buffered_keys:function(){
        varold_event,new_event;
        for(vari=0;i<this.buffered_key_events.length;i++){
            old_event=this.buffered_key_events[i];

            if(old_event.which!==13){//ignorereturns
                //Wedonotcreatea'real'keypresseventthrough
                //eg.KeyboardEventbecausethereareseveralissues
                //withthemthatmakethemverydifferentfrom
                //genuinekeypresses.Chromeperexamplehashada
                //bugforthelongesttimethatcauseskeyCodeand
                //charCodetonotbesetforeventscreatedthisway:
                //https://bugs.webkit.org/show_bug.cgi?id=16735
                varparams={
                    'bubbles':old_event.bubbles,
                    'cancelable':old_event.cancelable,
                };
                new_event=$.Event('keypress',params);
                new_event.viewArg=old_event.viewArg;
                new_event.ctrl=old_event.ctrl;
                new_event.alt=old_event.alt;
                new_event.shift=old_event.shift;
                new_event.meta=old_event.meta;
                new_event.char=old_event.char;
                new_event.key=old_event.key;
                new_event.charCode=old_event.charCode;
                new_event.keyCode=old_event.keyCode||old_event.which;//Firefoxdoesn'tsetkeyCodeforkeypresses,onlykeyup/down
                new_event.which=old_event.which;
                new_event.dispatched_by_barcode_reader=true;

                $(old_event.target).trigger(new_event);
            }
        }
    },

    element_is_editable:function(element){
        return$(element).is('input,textarea,[contenteditable="true"]');
    },

    //ThischecksthatakeypresseventiseitherESC,TAB,anarrow
    //keyorafunctionkey.ThisisFirefoxspecific,inChrom{e,ium}
    //keypresseventsarenotfiredforthesetypesofkeys,only
    //keyup/keydown.
    is_special_key:function(e){
        if(e.key==="ArrowLeft"||e.key==="ArrowRight"||
            e.key==="ArrowUp"||e.key==="ArrowDown"||
            e.key==="Escape"||e.key==="Tab"||
            e.key==="Backspace"||e.key==="Delete"||
            e.key==="Home"||e.key==="End"||
            e.key==="PageUp"||e.key==="PageDown"||
            e.key==="Unidentified"||/F\d\d?/.test(e.key)){
            returntrue;
        }else{
            returnfalse;
        }
    },

    //Thekeydownandkeyuphandlersareheretodisallowkey
    //repeat.WhenpreventDefault()iscalledonakeydownevent
    //thekeypressthatnormallyfollowsiscancelled.
    keydown_handler:function(e){
        if(this.key_pressed[e.which]){
            e.preventDefault();
        }else{
            this.key_pressed[e.which]=true;
        }
    },

    keyup_handler:function(e){
        this.key_pressed[e.which]=false;
    },

    handler:function(e){
        //Don'tcatcheventsweresent
        if(e.dispatched_by_barcode_reader)
            return;
        //Don'tcatchnon-printablekeysforwhichFirefoxtriggersakeypress
        if(this.is_special_key(e))
            return;
        //Don'tcatchkeypresseswhichcouldhaveaUXpurpose(likeshortcuts)
        if(e.ctrlKey||e.metaKey||e.altKey)
            return;
        //Don'tcatchReturnwhennothingisbuffered.Thiswayusers
        //canstilluseReturnto'click'onfocusedbuttonsorlinks.
        if(e.which===13&&this.buffered_key_events.length===0)
            return;
        //Don'tcatcheventstargetingelementsthatareeditablebecausewe
        //havenowayofredispatching'genuine'keyevents.Resentevents
        //don'ttriggernativeeventhandlersofelements.Sothismeansthat
        //ourfakeeventswillnotappearineg.an<input>element.
        if((this.element_is_editable(e.target)&&!$(e.target).data('enableBarcode'))&&e.target.getAttribute("barcode_events")!=="true")
            return;

        //Catchandbuffertheevent
        this.buffered_key_events.push(e);
        e.preventDefault();
        e.stopImmediatePropagation();

        //Handlebufferedkeysimmediatelyifthekeypressmarkstheend
        //ofabarcodeorafterxmillisecondswithoutanewkeypress
        clearTimeout(this.timeout);
        if(String.fromCharCode(e.which).match(this.suffix)){
            this.handle_buffered_keys();
        }else{
            this.timeout=setTimeout(_.bind(this.handle_buffered_keys,this),this.max_time_between_keys_in_ms);
        }
    },

    /**
     *Trytodetectthebarcodevaluebylisteningallkeydownevents:
     *Checksifadomelementwhomaycontainstextvaluehasthefocus.
     *Ifnot,it'sprobablybecausetheseeventsaretriggeredbyabarcodescanner.
     *Tobeabletohandlethisvalue,afocusedinputwillbecreated.
     *
     *Thisfunctionalsohastheresponsibilitytodetecttheendofthebarcodevalue.
     *(1)Inmostofcases,anoptionalkey(taborenter)issenttomarktheendofthevalue.
     *So,wedirecltyhandlethevalue.
     *(2)Ifnoendkeyisconfigured,wehavetocalculatethedelaybetweeneachkeydowns.
     *'max_time_between_keys_in_ms'dependsofthedeviceandmaybeconfigured.
     *Exceededthistimeout,weconsiderthatthebarcodevalueisentirelysent.
     *
     *@private
     *@param {jQuery.Event}ekeydownevent
     */
    _listenBarcodeScanner:function(e){
        if($(document.activeElement).not('input:text,textarea,[contenteditable],'+
            '[type="email"],[type="number"],[type="password"],[type="tel"],[type="search"]').length){
            $('body').append(this.$barcodeInput);
            this.$barcodeInput.focus();
        }
        if(this.$barcodeInput.is(":focus")){
            //Handlebufferedkeysimmediatelyifthekeypressmarkstheend
            //ofabarcodeorafterxmillisecondswithoutanewkeypress.
            clearTimeout(this.timeout);
            //Onchromemobile,e.whichonlyworksforsomespecialcharacterslikeENTERorTAB.
            if(String.fromCharCode(e.which).match(this.suffix)){
                this._handleBarcodeValue(e);
            }else{
                this.timeout=setTimeout(this._handleBarcodeValue.bind(this,e),
                    this.max_time_between_keys_in_ms);
            }
            //ifthebarcodeinputdoesn'treceivekeydownforawhile,removeit.
            this.__blurBarcodeInput();
        }
    },

    /**
     *Retrievesthebarcodevaluefromthetemporaryinputelement.
     *Thischecksthisvalueandtriggeritonthebus.
     *
     *@private
     *@param {jQuery.Event}keydownevent
     */
    _handleBarcodeValue:function(e){
        varbarcodeValue=this.$barcodeInput.val();
        if(barcodeValue.match(this.regexp)){
            core.bus.trigger('barcode_scanned',barcodeValue,$(e.target).parent()[0]);
            this._blurBarcodeInput();
        }
    },

    /**
     *Removesthevalueandfocusfromthebarcodeinput.
     *Ifnothinghappens,thefocuswillbelostand
     *thevirtualkeyboardonmobiledeviceswillbeclosed.
     *
     *@private
     */
    _blurBarcodeInput:function(){
        //Closethevirtualkeyboardonmobilebrowsers
        //FIXME:actuallywecan'tpreventkeyboardfromopening
        this.$barcodeInput.val('').blur();
    },

    start:function(prevent_key_repeat){
        //ChromeMobileisn'ttriggeringkeypressevent.
        //ThisismarkedasLegacyintheDOM-Level-3Standard.
        //See:https://www.w3.org/TR/uievents/#legacy-keyboardevent-event-types
        //ThisfixisonlyappliedforGoogleChromeMobilebutitshouldworkfor
        //allothercases.
        //Inmaster,wecouldremovethebehaviorwithkeypressandonlyusekeydown.
        if(this.isChromeMobile){
            $('body').on("keydown",this._listenBarcodeScanner.bind(this));
        }else{
            $('body').bind("keypress",this.__handler);
        }
        if(prevent_key_repeat===true){
            $('body').bind("keydown",this.__keydown_handler);
            $('body').bind('keyup',this.__keyup_handler);
        }
    },

    stop:function(){
        $('body').off("keypress",this.__handler);
        $('body').off("keydown",this.__keydown_handler);
        $('body').off('keyup',this.__keyup_handler);
    },
});

return{
    /**Singletonthatemitsbarcode_scannedeventsoncore.bus*/
    BarcodeEvents:newBarcodeEvents(),
    /**
     *Listofbarcodeprefixesthatarereservedforinternalpurposes
     *@typeArray
     */
    ReservedBarcodePrefixes:['O-CMD'],
};

});
