flectra.define('web.dom_ready',function(require){
'usestrict';

    returnnewPromise(function(resolve,reject){
        $(resolve);
    });
});
//==============================================================================

flectra.define('web.dom',function(require){
"usestrict";

/**
 *DOMUtilityhelpers
 *
 *WecollectinthisfilesomehelperstohelpintegratevariousDOM
 *functionalitieswiththeflectraframework. Acommonthemeinthesefunctions
 *istheuseofthemaincore.bus,whichhelpstheframeworkreactwhen
 *somethinghappensintheDOM.
 */

varconcurrency=require('web.concurrency');
varconfig=require('web.config');
varcore=require('web.core');
var_t=core._t;

/**
 *PrivatefunctiontonotifythatsomethinghasbeenattachedintheDOM
 *@param{htmlStringorElementorArrayorjQuery}[content]thecontentthat
 *hasbeenattachedintheDOM
 *@params{Array}[callbacks]arrayof{widget:w,callback_args:args}such
 *thaton_attach_callback()willbecalledoneachwwithargumentsargs
 */
function_notify(content,callbacks){
    callbacks.forEach(function(c){
        if(c.widget&&c.widget.on_attach_callback){
            c.widget.on_attach_callback(c.callback_args);
        }
    });
    core.bus.trigger('DOM_updated',content);
}

vardom={
    DEBOUNCE:400,

    /**
     *AppendscontentinajQueryobjectandoptionnallytriggersanevent
     *
     *@param{jQuery}[$target]thenodewherecontentwillbeappended
     *@param{htmlStringorElementorArrayorjQuery}[content]DOMelement,
     *  arrayofelements,HTMLstringorjQueryobjecttoappendto$target
     *@param{Boolean}[options.in_DOM]trueif$targetisintheDOM
     *@param{Array}[options.callbacks]arrayofobjectsdescribingthe
     *  callbackstoperform(see_notifyforacompletedescription)
     */
    append:function($target,content,options){
        $target.append(content);
        if(options&&options.in_DOM){
            _notify(content,options.callbacks);
        }
    },
    /**
     *Detectsif2elementsarecolliding.
     *
     *@param{Element}el1
     *@param{Element}el2
     *@returns{boolean}
     */
     areColliding(el1,el2){
        constel1Rect=el1.getBoundingClientRect();
        constel2Rect=el2.getBoundingClientRect();
        returnel1Rect.bottom>el2Rect.top
            &&el1Rect.top<el2Rect.bottom
            &&el1Rect.right>el2Rect.left
            &&el1Rect.left<el2Rect.right;
    },
    /**
     *Autoresizea$textareanode,byrecomputingitsheightwhennecessary
     *@param{number}[options.min_height]bydefault,50.
     *@param{Widget}[options.parent]ifset,autoresizewilllistentosome
     *  extraeventstodecidewhentoresizeitself. Thisisusefulfor
     *  widgetsthatarenotinthedomwhentheautoresizeisdeclared.
     */
    autoresize:function($textarea,options){
        if($textarea.data("auto_resize")){
            return;
        }

        var$fixedTextarea;
        varminHeight;

        functionresize(){
            $fixedTextarea.insertAfter($textarea);
            varheightOffset=0;
            varstyle=window.getComputedStyle($textarea[0],null);
            if(style.boxSizing==='border-box'){
                varpaddingHeight=parseFloat(style.paddingTop)+parseFloat(style.paddingBottom);
                varborderHeight=parseFloat(style.borderTopWidth)+parseFloat(style.borderBottomWidth);
                heightOffset=borderHeight+paddingHeight;
            }
            $fixedTextarea.width($textarea.width());
            $fixedTextarea.val($textarea.val());
            varheight=$fixedTextarea[0].scrollHeight;
            $textarea.css({height:Math.max(height+heightOffset,minHeight)});
        }

        functionremoveVerticalResize(){
            //Wealreadycomputethecorrectheight:
            //wedon'twanttheusertoresizeitvertically.
            //OnChromethisneedstobecalledaftertheDOMisready.
            varstyle=window.getComputedStyle($textarea[0],null);
            if(style.resize==='vertical'){
                $textarea[0].style.resize='none';
            }elseif(style.resize==='both'){
                $textarea[0].style.resize='horizontal';
            }
        }

        options=options||{};
        minHeight='min_height'inoptions?options.min_height:50;

        $fixedTextarea=$('<textareadisabled>',{
            class:$textarea[0].className,
        });

        vardirection=_t.database.parameters.direction==='rtl'?'right':'left';
        $fixedTextarea.css({
            position:'absolute',
            opacity:0,
            height:10,
            borderTopWidth:0,
            borderBottomWidth:0,
            padding:0,
            overflow:'hidden',
            top:-10000,
        }).css(direction,-10000);
        $fixedTextarea.data("auto_resize",true);

        //Thefollowinglineisnecessarytopreventthescrollbartoappear
        //onthetextareaonFirefoxwhenaddinganewlineifthecurrentline
        //hasjustenoughcharacterstocompletelyfilltheline.
        //Thisfixshouldbefinesincewecomputetheheightdependingonthe
        //content,thereshouldneverbeanoverflow.
        //TODOideallyunderstandwhyandfixthisanotherwayifpossible.
        $textarea.css({'overflow-y':'hidden'});

        resize();
        removeVerticalResize();
        $textarea.data("auto_resize",true);

        $textarea.on('inputfocuschange',resize);
        if(options.parent){
            core.bus.on('DOM_updated',options.parent,function(){
                resize();
                removeVerticalResize();
            });
        }
    },
    /**
     *@return{HTMLElement}
     */
    closestScrollable(el){
        return$(el).closestScrollable()[0];
    },
    /**
     *@param{HTMLElement}el
     *@see$.compensateScrollbar
     */
    compensateScrollbar(el,...rest){
        $(el).compensateScrollbar(...rest);
    },
    /**
     *jQueryfindfunctionbehavioris::
     *
     *     $('A').find('AB')<=>$('AAB')
     *
     *Thesearchesbehaviortofindoptions'DOMneedstobe::
     *
     *     $('A').find('AB')<=>$('AB')
     *
     *Thisiswhatthisfunctiondoes.
     *
     *@param{jQuery}$from-thejQueryelement(s)fromwhichtosearch
     *@param{string}selector-theCSSselectortomatch
     *@param{boolean}[addBack=false]-whetherornotthe$fromelement
     *                                 shouldbeconsideredintheresults
     *@returns{jQuery}
     */
    cssFind:function($from,selector,addBack){
        var$results;

        //NowaytocorrectlyparseacomplexjQueryselectorbuthavingno
        //spacesshouldbeagood-enoughconditiontouseasimplefind
        varmultiParts=selector.indexOf('')>=0;
        if(multiParts){
            $results=$from.find('*').filter(selector);
        }else{
            $results=$from.find(selector);
        }

        if(addBack&&$from.is(selector)){
            $results=$results.add($from);
        }

        return$results;
    },
    /**
     *DetacheswidgetsfromtheDOMandperformstheiron_detach_callback()
     *
     *@param{Array}[to_detach]arrayof{widget:w,callback_args:args}such
     *  thatw.$elwillbedetachedandw.on_detach_callback(args)willbe
     *  called
     *@param{jQuery}[options.$to_detach]ifgiven,detachedinsteadof
     *  widgets'$el
     *@return{jQuery}thedetachedelements
     */
    detach:function(to_detach,options){
        to_detach.forEach(function(d){
            if(d.widget.on_detach_callback){
                d.widget.on_detach_callback(d.callback_args);
            }
        });
        var$to_detach=options&&options.$to_detach;
        if(!$to_detach){
            $to_detach=$(to_detach.map(function(d){
                returnd.widget.el;
            }));
        }
        return$to_detach.detach();
    },
    /**
     *Returnstheselectionrangeofaninputortextarea
     *
     *@param{Object}nodeDOMiteminputortexteara
     *@returns{Object}range
     */
    getSelectionRange:function(node){
        return{
            start:node.selectionStart,
            end:node.selectionEnd,
        };
    },
    /**
     *ReturnsthedistancebetweenaDOMelementandthetop-leftcornerofthe
     *window
     *
     *@param{Object}eDOMelement(inputortexteara)
     *@return{Object}theleftandtopdistancesinpixels
     */
    getPosition:function(e){
        varposition={left:0,top:0};
        while(e){
            position.left+=e.offsetLeft;
            position.top+=e.offsetTop;
            e=e.offsetParent;
        }
        returnposition;
    },
    /**
     *@returns{HTMLElement}
     */
    getScrollingElement(){
        return$().getScrollingElement()[0];
    },
    /**
     *@param{HTMLElement}el
     *@returns{boolean}
     */
    hasScrollableContent(el){
        return$(el).hasScrollableContent();
    },
    /**
     *@param{HTMLElement}el
     *@returns{boolean}
     */
    isScrollable(el){
        return$(el).isScrollable();
    },
    /**
     *Protectsafunctionwhichistobeusedasahandlerbypreventingits
     *executionforthedurationofapreviouscalltoit(includingasync
     *partsofthatcall).
     *
     *Limitation:asthehandlerisignoredduringasyncactions,
     *the'preventDefault'or'stopPropagation'callsitmaywanttodo
     *willbeignoredtoo.Usingthe'preventDefault'and'stopPropagation'
     *argumentssolvesthatproblem.
     *
     *@param{function}fct
     *     Thefunctionwhichistobeusedasahandler.Ifapromise
     *     isreturned,itisusedtodeterminewhenthehandler'sactionis
     *     finished.Otherwise,thereturnisusedasjQueryusesit.
     *@param{function|boolean}preventDefault
     *@param{function|boolean}stopPropagation
     */
    makeAsyncHandler:function(fct,preventDefault,stopPropagation){
        varpending=false;
        function_isLocked(){
            returnpending;
        }
        function_lock(){
            pending=true;
        }
        function_unlock(){
            pending=false;
        }
        returnfunction(ev){
            if(preventDefault===true||preventDefault&&preventDefault()){
                ev.preventDefault();
            }
            if(stopPropagation===true||stopPropagation&&stopPropagation()){
                ev.stopPropagation();
            }

            if(_isLocked()){
                //Ifapreviouscalltothishandlerisstillpending,ignore
                //thenewcall.
                return;
            }

            _lock();
            varresult=fct.apply(this,arguments);
            Promise.resolve(result).then(_unlock).guardedCatch(_unlock);
            returnresult;
        };
    },
    /**
     *Createsadebouncedversionofafunctiontobeusedasabuttonclick
     *handler.Alsoimprovesthehandlertodisablethebuttonforthetimeof
     *thedebounceand/orthetimeoftheasyncactionsitperforms.
     *
     *Limitation:iftwohandlersareputonthesamebutton,thebuttonwill
     *becomeenabledagainonceanyhandler'sactionfinishes(multipleclick
     *handlersshouldhowevernotbebindedtothesamebutton).
     *
     *@param{function}fct
     *     Thefunctionwhichistobeusedasabuttonclickhandler.Ifa
     *     promiseisreturned,itisusedtodeterminewhenthebuttoncanbe
     *     re-enabled.Otherwise,thereturnisusedasjQueryusesit.
     */
    makeButtonHandler:function(fct){
        //Fallback:ifthefinalhandlerisnotbindedtoabutton,atleast
        //makeitanasynchandler(alsohandlesthecasewheresomeevents
        //mightignorethedisabledstateofthebutton).
        fct=dom.makeAsyncHandler(fct);

        returnfunction(ev){
            varresult=fct.apply(this,arguments);

            var$button=$(ev.target).closest('.btn');
            if(!$button.length){
                returnresult;
            }

            //Disablethebuttonforthedurationofthehandler'saction
            //oratleastforthedurationoftheclickdebounce.Thismakes
            //a'real'debouncecreationuseless.Also,duringthedebouncing
            //part,thebuttonisdisabledwithoutanyvisualeffect.
            $button.addClass('o_debounce_disabled');
            Promise.resolve(dom.DEBOUNCE&&concurrency.delay(dom.DEBOUNCE)).then(function(){
                $button.removeClass('o_debounce_disabled');
                constrestore=dom.addButtonLoadingEffect($button[0]);
                returnPromise.resolve(result).then(restore).guardedCatch(restore);
            });

            returnresult;
        };
    },
    /**
     *Givesthebuttonaloadingeffectbydisablingitandaddinga`fa`
     *spinnericon.
     *Theexistingbutton`fa`iconswillbehiddenthroughcss.
     *
     *@param{HTMLElement}btn-thebuttontodisable/load
     *@return{function}acallbackfunctionthatwillrestorethebutton
     *        initialstate
     */
    addButtonLoadingEffect:function(btn){
        const$btn=$(btn);
        $btn.addClass('o_website_btn_loadingdisabled');
        $btn.prop('disabled',true);
        const$loader=$('<span/>',{
            class:'fafa-refreshfa-spinmr-2',
        });
        $btn.prepend($loader);
        return()=>{
             $btn.removeClass('o_website_btn_loadingdisabled');
             $btn.prop('disabled',false);
             $loader.remove();
        };
    },
    /**
     *PrependscontentinajQueryobjectandoptionnallytriggersanevent
     *
     *@param{jQuery}[$target]thenodewherecontentwillbeprepended
     *@param{htmlStringorElementorArrayorjQuery}[content]DOMelement,
     *  arrayofelements,HTMLstringorjQueryobjecttoprependto$target
     *@param{Boolean}[options.in_DOM]trueif$targetisintheDOM
     *@param{Array}[options.callbacks]arrayofobjectsdescribingthe
     *  callbackstoperform(see_notifyforacompletedescription)
     */
    prepend:function($target,content,options){
        $target.prepend(content);
        if(options&&options.in_DOM){
            _notify(content,options.callbacks);
        }
    },
    /**
     *Rendersabuttonwithstandardflectratemplate.Thisdoesnotuseanyxml
     *templatetoavoidforcingthefrontendparttolazyloadaxmlfilefor
     *eachwidgetwhichmightwanttocreateasimplebutton.
     *
     *@param{Object}options
     *@param{Object}[options.attrs]-Attributestoputonthebuttonelement
     *@param{string}[options.attrs.type='button']
     *@param{string}[options.attrs.class='btn-secondary']
     *       Note:automaticallycompletedwith"btnbtn-X"
     *       (@seeoptions.sizeforthevalueofX)
     *@param{string}[options.size]-@seeoptions.attrs.class
     *@param{string}[options.icon]
     *       Thespecificfaiconclass(forexample"fa-home")oranURLfor
     *       animagetouseasicon.
     *@param{string}[options.text]-thebutton'stext
     *@returns{jQuery}
     */
    renderButton:function(options){
        varjQueryParams=_.extend({
            type:'button',
        },options.attrs||{});

        varextraClasses=jQueryParams.class;
        if(extraClasses){
            //Ifwegotextraclasses,checkifoldoe_highlight/oe_link
            //classesaregivenandswitchthemtotherightclasses(those
            //classeshavenostyleassociatedtothemanymore).
            //TODOideallythisshouldbedroppedatsomepoint.
            extraClasses=extraClasses.replace(/\boe_highlight\b/g,'btn-primary')
                                       .replace(/\boe_link\b/g,'btn-link');
        }

        jQueryParams.class='btn';
        if(options.size){
            jQueryParams.class+=('btn-'+options.size);
        }
        jQueryParams.class+=(''+(extraClasses||'btn-secondary'));

        var$button=$('<button/>',jQueryParams);

        if(options.icon){
            if(options.icon.substr(0,3)==='fa-'){
                $button.append($('<i/>',{
                    class:'fafa-fwo_button_icon'+options.icon,
                }));
            }else{
                $button.append($('<img/>',{
                    src:options.icon,
                }));
            }
        }
        if(options.text){
            $button.append($('<span/>',{
                text:options.text,
            }));
        }

        return$button;
    },
    /**
     *Rendersacheckboxwithstandardflectra/BStemplate.Thisdoesnotuseany
     *xmltemplatetoavoidforcingthefrontendparttolazyloadaxmlfile
     *foreachwidgetwhichmightwanttocreateasimplecheckbox.
     *
     *@param{Object}[options]
     *@param{Object}[options.prop]
     *       Allowstosettheinputproperties(disabledandcheckedstates).
     *@param{string}[options.text]
     *       Thecheckbox'sassociatedtext.Ifnoneisgiventhenasimple
     *       checkboxisrendered.
     *@returns{jQuery}
     */
    renderCheckbox:function(options){
        varid=_.uniqueId('checkbox-');
        var$container=$('<div/>',{
            class:'custom-controlcustom-checkbox',
        });
        var$input=$('<input/>',{
            type:'checkbox',
            id:id,
            class:'custom-control-input',
        });
        var$label=$('<label/>',{
            for:id,
            class:'custom-control-label',
            text:options&&options.text||'',
        });
        if(!options||!options.text){
            $label.html('&#8203;');//BScheckboxesneedsomelabelcontent(so
                                //addazero-widthspacewhenthereisnotext)
        }
        if(options&&options.prop){
            $input.prop(options.prop);
        }
        if(options&&options.role){
            $input.attr('role',options.role);
        }
        return$container.append($input,$label);
    },
    /**
     *Setstheselectionrangeofagiveninputortextarea
     *
     *@param{Object}nodeDOMelement(inputortextarea)
     *@param{integer}range.start
     *@param{integer}range.end
     */
    setSelectionRange:function(node,range){
        if(node.setSelectionRange){
            node.setSelectionRange(range.start,range.end);
        }elseif(node.createTextRange){
            node.createTextRange()
                .collapse(true)
                .moveEnd('character',range.start)
                .moveStart('character',range.end)
                .select();
        }
    },
    /**
     *Computesthesizebywhichascrollingpointshouldbedecreasedsothat
     *thetopfixedelementsofthepageappearabovethatscrollingpoint.
     *
     *@returns{number}
     */
    scrollFixedOffset(){
        letsize=0;
        for(constelof$('.o_top_fixed_element')){
            size+=$(el).outerHeight();
        }
        returnsize;
    },
    /**
     *@param{HTMLElement|string}el-theelementtoscrollto.If"el"isa
     *     string,itmustbeavalidselectorofanelementintheDOMor
     *     '#top'or'#bottom'.IfitisanHTMLelement,itmustbepresent
     *     intheDOM.
     *     Limitation:iftheelementisusingafixedposition,this
     *     functioncannotworkexceptifistheheader(elistheneithera
     *     stringsetto'#top'oranHTMLelementwiththe"top"id)orthe
     *     footer(elisthenastringsetto'#bottom'oranHTMLelement
     *     withthe"bottom"id)forwhichexceptionshavebeenmade.
     *@param{number}[options]-sameasanimateofjQuery
     *@param{number}[options.extraOffset=0]
     *     extraoffsettoaddontopoftheautomaticone(theautomaticone
     *     beingcomputedbasedonfixedheadersizes)
     *@param{number}[options.forcedOffset]
     *     offsetusedinsteadoftheautomaticone(extraOffsetwillbe
     *     ignoredtoo)
     *@return{Promise}
     */
    scrollTo(el,options={}){
        const$el=$(el);
        if(typeof(el)==='string'&&$el[0]){
            el=$el[0];
        }
        constisTopOrBottomHidden=(el==='#top'||el==='#bottom');
        const$topLevelScrollable=$().getScrollingElement();
        const$scrollable=isTopOrBottomHidden?$topLevelScrollable:$el.parent().closestScrollable();
        constisTopScroll=$scrollable.is($topLevelScrollable);

        function_computeScrollTop(){
            if(el==='#top'||el.id==='top'){
                return0;
            }
            if(el==='#bottom'||el.id==='bottom'){
                return$scrollable[0].scrollHeight-$scrollable[0].clientHeight;
            }

            letoffsetTop=$el.offset().top;
            if(el.classList.contains('d-none')){
                el.classList.remove('d-none');
                offsetTop=$el.offset().top;
                el.classList.add('d-none');
            }
            constisDocScrollingEl=$scrollable.is(el.ownerDocument.scrollingElement);
            constelPosition=offsetTop
                -($scrollable.offset().top-(isDocScrollingEl?0:$scrollable[0].scrollTop));
            letoffset=options.forcedOffset;
            if(offset===undefined){
                offset=(isTopScroll?dom.scrollFixedOffset():0)+(options.extraOffset||0);
            }
            returnMath.max(0,elPosition-offset);
        }

        constoriginalScrollTop=_computeScrollTop();

        returnnewPromise(resolve=>{
            constclonedOptions=Object.assign({},options);

            //Duringtheanimation,detectanychangeneededforthescroll
            //offset.Ifanyoccurs,stoptheanimationandcontinuingitto
            //thenewscrollpointfortheremainingtime.
            //Note:limitation,theanimationwon'tbeasfluidaspossibleif
            //theeasingmodeisdifferentof'linear'.
            clonedOptions.progress=function(a,b,remainingMs){
                if(options.progress){
                    options.progress.apply(this,...arguments);
                }
                constnewScrollTop=_computeScrollTop();
                if(Math.abs(newScrollTop-originalScrollTop)<=1.0
                        &&(isTopOrBottomHidden||!(el.classList.contains('o_transitioning')))){
                    return;
                }
                $scrollable.stop();
                dom.scrollTo(el,Object.assign({},options,{
                    duration:remainingMs,
                    easing:'linear',
                })).then(()=>resolve());
            };

            //Detecttheendoftheanimationtobeabletoindicateitto
            //thecallerviathereturnedPromise.
            clonedOptions.complete=function(){
                if(options.complete){
                    options.complete.apply(this,...arguments);
                }
                resolve();
            };

            $scrollable.animate({scrollTop:originalScrollTop},clonedOptions);
        });
    },
    /**
     *Createsanautomatic'more'dropdown-menuforasetofnavbaritems.
     *
     *@param{jQuery}$el
     *@param{Object}[options]
     *@param{string}[options.unfoldable='none']
     *@param{function}[options.maxWidth]
     *@param{string}[options.sizeClass='SM']
     */
    initAutoMoreMenu:function($el,options){
        options=_.extend({
            unfoldable:'none',
            maxWidth:false,
            sizeClass:'SM',
        },options||{});

        varautoMarginLeftRegex=/\bm[lx]?(?:-(?:sm|md|lg|xl))?-auto\b/;
        varautoMarginRightRegex=/\bm[rx]?(?:-(?:sm|md|lg|xl))?-auto\b/;

        var$extraItemsToggle=null;

        vardebouncedAdapt=_.debounce(_adapt,250);
        core.bus.on('resize',null,debouncedAdapt);
        _adapt();

        $el.data('dom:autoMoreMenu:adapt',_adapt);
        $el.data('dom:autoMoreMenu:destroy',function(){
            _restore();
            core.bus.off('resize',null,debouncedAdapt);
            $el.removeData(['dom:autoMoreMenu:destroy','dom:autoMoreMenu:adapt']);
        });

        function_restore(){
            if($extraItemsToggle===null){
                return;
            }
            var$items=$extraItemsToggle.children('.dropdown-menu').children();
            $items.addClass('nav-item');
            $items.children('.dropdown-item,a').removeClass('dropdown-item').addClass('nav-link');
            $items.insertBefore($extraItemsToggle);
            $extraItemsToggle.remove();
            $extraItemsToggle=null;
        }

        function_adapt(){
            _restore();

            if(!$el.is(':visible')||$el.closest('.show').length){
                //Nevertransformthemenuwhenitisnotvisibleyetorif
                //itisatoggleableone.
                return;
            }
            if(config.device.size_class<=config.device.SIZES[options.sizeClass]){
                return;
            }

            var$allItems=$el.children();
            var$unfoldableItems=$allItems.filter(options.unfoldable);
            var$items=$allItems.not($unfoldableItems);

            varmaxWidth=0;
            if(options.maxWidth){
                maxWidth=options.maxWidth();
            }else{
                maxWidth=computeFloatOuterWidthWithMargins($el[0],true,true,true);
                varstyle=window.getComputedStyle($el[0]);
                maxWidth-=(parseFloat(style.paddingLeft)+parseFloat(style.paddingRight)+parseFloat(style.borderLeftWidth)+parseFloat(style.borderRightWidth));
                maxWidth-=_.reduce($unfoldableItems,function(sum,el){
                    returnsum+computeFloatOuterWidthWithMargins(el,true,true,false);
                },0);
            }

            varnbItems=$items.length;
            varmenuItemsWidth=_.reduce($items,function(sum,el){
                returnsum+computeFloatOuterWidthWithMargins(el,true,true,false);
            },0);

            if(maxWidth-menuItemsWidth>=-0.001){
                return;
            }

            var$dropdownMenu=$('<ul/>',{class:'dropdown-menu'});
            $extraItemsToggle=$('<li/>',{class:'nav-itemdropdowno_extra_menu_items'})
                .append($('<a/>',{role:'button',href:'#',class:'nav-linkdropdown-toggleo-no-caret','data-toggle':'dropdown','aria-expanded':false})
                    .append($('<i/>',{class:'fafa-plus'})))
                .append($dropdownMenu);
            $extraItemsToggle.insertAfter($items.last());

            menuItemsWidth+=computeFloatOuterWidthWithMargins($extraItemsToggle[0],true,true,false);
            do{
                menuItemsWidth-=computeFloatOuterWidthWithMargins($items.eq(--nbItems)[0],true,true,false);
            }while(!(maxWidth-menuItemsWidth>=-0.001)&&(nbItems>0));

            var$extraItems=$items.slice(nbItems).detach();
            $extraItems.removeClass('nav-item');
            $extraItems.children('.nav-link,a').removeClass('nav-link').addClass('dropdown-item');
            $dropdownMenu.append($extraItems);
            $extraItemsToggle.find('.nav-link').toggleClass('active',$extraItems.children().hasClass('active'));
        }

        functioncomputeFloatOuterWidthWithMargins(el,mLeft,mRight,considerAutoMargins){
            varrect=el.getBoundingClientRect();
            varstyle=window.getComputedStyle(el);
            varouterWidth=rect.right-rect.left;
            if(mLeft!==false&&(considerAutoMargins||!autoMarginLeftRegex.test(el.getAttribute('class')))){
                outerWidth+=parseFloat(style.marginLeft);
            }
            if(mRight!==false&&(considerAutoMargins||!autoMarginRightRegex.test(el.getAttribute('class')))){
                outerWidth+=parseFloat(style.marginRight);
            }
            //WouldbeNaNforinvisibleelementsforexample
            returnisNaN(outerWidth)?0:outerWidth;
        }
    },
    /**
     *Cleanswhathasbeendoneby``initAutoMoreMenu``.
     *
     *@param{jQuery}$el
     */
    destroyAutoMoreMenu:function($el){
        vardestroyFunc=$el.data('dom:autoMoreMenu:destroy');
        if(destroyFunc){
            destroyFunc.call(null);
        }
    },
};
returndom;
});
