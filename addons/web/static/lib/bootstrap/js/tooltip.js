/*!
  *Bootstraptooltip.jsv4.3.1(https://getbootstrap.com/)
  *Copyright2011-2019TheBootstrapAuthors(https://github.com/twbs/bootstrap/graphs/contributors)
  *LicensedunderMIT(https://github.com/twbs/bootstrap/blob/master/LICENSE)
  */
(function(global,factory){
  typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory(require('jquery'),require('popper.js'),require('./util.js')):
  typeofdefine==='function'&&define.amd?define(['jquery','popper.js','./util.js'],factory):
  (global=global||self,global.Tooltip=factory(global.jQuery,global.Popper,global.Util));
}(this,function($,Popper,Util){'usestrict';

  $=$&&$.hasOwnProperty('default')?$['default']:$;
  Popper=Popper&&Popper.hasOwnProperty('default')?Popper['default']:Popper;
  Util=Util&&Util.hasOwnProperty('default')?Util['default']:Util;

  function_defineProperties(target,props){
    for(vari=0;i<props.length;i++){
      vardescriptor=props[i];
      descriptor.enumerable=descriptor.enumerable||false;
      descriptor.configurable=true;
      if("value"indescriptor)descriptor.writable=true;
      Object.defineProperty(target,descriptor.key,descriptor);
    }
  }

  function_createClass(Constructor,protoProps,staticProps){
    if(protoProps)_defineProperties(Constructor.prototype,protoProps);
    if(staticProps)_defineProperties(Constructor,staticProps);
    returnConstructor;
  }

  function_defineProperty(obj,key,value){
    if(keyinobj){
      Object.defineProperty(obj,key,{
        value:value,
        enumerable:true,
        configurable:true,
        writable:true
      });
    }else{
      obj[key]=value;
    }

    returnobj;
  }

  function_objectSpread(target){
    for(vari=1;i<arguments.length;i++){
      varsource=arguments[i]!=null?arguments[i]:{};
      varownKeys=Object.keys(source);

      if(typeofObject.getOwnPropertySymbols==='function'){
        ownKeys=ownKeys.concat(Object.getOwnPropertySymbols(source).filter(function(sym){
          returnObject.getOwnPropertyDescriptor(source,sym).enumerable;
        }));
      }

      ownKeys.forEach(function(key){
        _defineProperty(target,key,source[key]);
      });
    }

    returntarget;
  }

  /**
   *--------------------------------------------------------------------------
   *Bootstrap(v4.3.1):tools/sanitizer.js
   *LicensedunderMIT(https://github.com/twbs/bootstrap/blob/master/LICENSE)
   *--------------------------------------------------------------------------
   */
  varuriAttrs=['background','cite','href','itemtype','longdesc','poster','src','xlink:href'];
  varARIA_ATTRIBUTE_PATTERN=/^aria-[\w-]*$/i;
  varDefaultWhitelist={
    //Globalattributesallowedonanysuppliedelementbelow.
    '*':['class','dir','id','lang','role',ARIA_ATTRIBUTE_PATTERN],
    a:['target','href','title','rel'],
    area:[],
    b:[],
    br:[],
    col:[],
    code:[],
    div:[],
    em:[],
    hr:[],
    h1:[],
    h2:[],
    h3:[],
    h4:[],
    h5:[],
    h6:[],
    i:[],
    img:['src','alt','title','width','height'],
    li:[],
    ol:[],
    p:[],
    pre:[],
    s:[],
    small:[],
    span:[],
    sub:[],
    sup:[],
    strong:[],
    u:[],
    ul:[]
    /**
     *ApatternthatrecognizesacommonlyusefulsubsetofURLsthataresafe.
     *
     *ShoutouttoAngular7https://github.com/angular/angular/blob/7.2.4/packages/core/src/sanitization/url_sanitizer.ts
     */

  };
  varSAFE_URL_PATTERN=/^(?:(?:https?|mailto|ftp|tel|file):|[^&:/?#]*(?:[/?#]|$))/gi;
  /**
   *ApatternthatmatchessafedataURLs.Onlymatchesimage,videoandaudiotypes.
   *
   *ShoutouttoAngular7https://github.com/angular/angular/blob/7.2.4/packages/core/src/sanitization/url_sanitizer.ts
   */

  varDATA_URL_PATTERN=/^data:(?:image\/(?:bmp|gif|jpeg|jpg|png|tiff|webp)|video\/(?:mpeg|mp4|ogg|webm)|audio\/(?:mp3|oga|ogg|opus));base64,[a-z0-9+/]+=*$/i;

  functionallowedAttribute(attr,allowedAttributeList){
    varattrName=attr.nodeName.toLowerCase();

    if(allowedAttributeList.indexOf(attrName)!==-1){
      if(uriAttrs.indexOf(attrName)!==-1){
        returnBoolean(attr.nodeValue.match(SAFE_URL_PATTERN)||attr.nodeValue.match(DATA_URL_PATTERN));
      }

      returntrue;
    }

    varregExp=allowedAttributeList.filter(function(attrRegex){
      returnattrRegexinstanceofRegExp;
    });//Checkifaregularexpressionvalidatestheattribute.

    for(vari=0,l=regExp.length;i<l;i++){
      if(attrName.match(regExp[i])){
        returntrue;
      }
    }

    returnfalse;
  }

  functionsanitizeHtml(unsafeHtml,whiteList,sanitizeFn){
    if(unsafeHtml.length===0){
      returnunsafeHtml;
    }

    if(sanitizeFn&&typeofsanitizeFn==='function'){
      returnsanitizeFn(unsafeHtml);
    }

    vardomParser=newwindow.DOMParser();
    varcreatedDocument=domParser.parseFromString(unsafeHtml,'text/html');
    varwhitelistKeys=Object.keys(whiteList);
    varelements=[].slice.call(createdDocument.body.querySelectorAll('*'));

    var_loop=function_loop(i,len){
      varel=elements[i];
      varelName=el.nodeName.toLowerCase();

      if(whitelistKeys.indexOf(el.nodeName.toLowerCase())===-1){
        el.parentNode.removeChild(el);
        return"continue";
      }

      varattributeList=[].slice.call(el.attributes);
      varwhitelistedAttributes=[].concat(whiteList['*']||[],whiteList[elName]||[]);
      attributeList.forEach(function(attr){
        if(!allowedAttribute(attr,whitelistedAttributes)){
          el.removeAttribute(attr.nodeName);
        }
      });
    };

    for(vari=0,len=elements.length;i<len;i++){
      var_ret=_loop(i,len);

      if(_ret==="continue")continue;
    }

    returncreatedDocument.body.innerHTML;
  }

  /**
   *------------------------------------------------------------------------
   *Constants
   *------------------------------------------------------------------------
   */

  varNAME='tooltip';
  varVERSION='4.3.1';
  varDATA_KEY='bs.tooltip';
  varEVENT_KEY="."+DATA_KEY;
  varJQUERY_NO_CONFLICT=$.fn[NAME];
  varCLASS_PREFIX='bs-tooltip';
  varBSCLS_PREFIX_REGEX=newRegExp("(^|\\s)"+CLASS_PREFIX+"\\S+",'g');
  varDISALLOWED_ATTRIBUTES=['sanitize','whiteList','sanitizeFn'];
  varDefaultType={
    animation:'boolean',
    template:'string',
    title:'(string|element|function)',
    trigger:'string',
    delay:'(number|object)',
    html:'boolean',
    selector:'(string|boolean)',
    placement:'(string|function)',
    offset:'(number|string|function)',
    container:'(string|element|boolean)',
    fallbackPlacement:'(string|array)',
    boundary:'(string|element)',
    sanitize:'boolean',
    sanitizeFn:'(null|function)',
    whiteList:'object'
  };
  varAttachmentMap={
    AUTO:'auto',
    TOP:'top',
    RIGHT:'right',
    BOTTOM:'bottom',
    LEFT:'left'
  };
  varDefault={
    animation:true,
    template:'<divclass="tooltip"role="tooltip">'+'<divclass="arrow"></div>'+'<divclass="tooltip-inner"></div></div>',
    trigger:'hoverfocus',
    title:'',
    delay:0,
    html:false,
    selector:false,
    placement:'top',
    offset:0,
    container:false,
    fallbackPlacement:'flip',
    boundary:'scrollParent',
    sanitize:true,
    sanitizeFn:null,
    whiteList:DefaultWhitelist
  };
  varHoverState={
    SHOW:'show',
    OUT:'out'
  };
  varEvent={
    HIDE:"hide"+EVENT_KEY,
    HIDDEN:"hidden"+EVENT_KEY,
    SHOW:"show"+EVENT_KEY,
    SHOWN:"shown"+EVENT_KEY,
    INSERTED:"inserted"+EVENT_KEY,
    CLICK:"click"+EVENT_KEY,
    FOCUSIN:"focusin"+EVENT_KEY,
    FOCUSOUT:"focusout"+EVENT_KEY,
    MOUSEENTER:"mouseenter"+EVENT_KEY,
    MOUSELEAVE:"mouseleave"+EVENT_KEY
  };
  varClassName={
    FADE:'fade',
    SHOW:'show'
  };
  varSelector={
    TOOLTIP:'.tooltip',
    TOOLTIP_INNER:'.tooltip-inner',
    ARROW:'.arrow'
  };
  varTrigger={
    HOVER:'hover',
    FOCUS:'focus',
    CLICK:'click',
    MANUAL:'manual'
    /**
     *------------------------------------------------------------------------
     *ClassDefinition
     *------------------------------------------------------------------------
     */

  };

  varTooltip=
  /*#__PURE__*/
  function(){
    functionTooltip(element,config){
      /**
       *CheckforPopperdependency
       *Popper-https://popper.js.org
       */
      if(typeofPopper==='undefined'){
        thrownewTypeError('Bootstrap\'stooltipsrequirePopper.js(https://popper.js.org/)');
      }//private


      this._isEnabled=true;
      this._timeout=0;
      this._hoverState='';
      this._activeTrigger={};
      this._popper=null;//Protected

      this.element=element;
      this.config=this._getConfig(config);
      this.tip=null;

      this._setListeners();
    }//Getters


    var_proto=Tooltip.prototype;

    //Public
    _proto.enable=functionenable(){
      this._isEnabled=true;
    };

    _proto.disable=functiondisable(){
      this._isEnabled=false;
    };

    _proto.toggleEnabled=functiontoggleEnabled(){
      this._isEnabled=!this._isEnabled;
    };

    _proto.toggle=functiontoggle(event){
      if(!this._isEnabled){
        return;
      }

      if(event){
        vardataKey=this.constructor.DATA_KEY;
        varcontext=$(event.currentTarget).data(dataKey);

        if(!context){
          context=newthis.constructor(event.currentTarget,this._getDelegateConfig());
          $(event.currentTarget).data(dataKey,context);
        }

        context._activeTrigger.click=!context._activeTrigger.click;

        if(context._isWithActiveTrigger()){
          context._enter(null,context);
        }else{
          context._leave(null,context);
        }
      }else{
        if($(this.getTipElement()).hasClass(ClassName.SHOW)){
          this._leave(null,this);

          return;
        }

        this._enter(null,this);
      }
    };

    _proto.dispose=functiondispose(){
      clearTimeout(this._timeout);
      $.removeData(this.element,this.constructor.DATA_KEY);
      $(this.element).off(this.constructor.EVENT_KEY);
      $(this.element).closest('.modal').off('hide.bs.modal');

      if(this.tip){
        $(this.tip).remove();
      }

      this._isEnabled=null;
      this._timeout=null;
      this._hoverState=null;
      this._activeTrigger=null;

      if(this._popper!==null){
        this._popper.destroy();
      }

      this._popper=null;
      this.element=null;
      this.config=null;
      this.tip=null;
    };

    _proto.show=functionshow(){
      var_this=this;

      if($(this.element).css('display')==='none'){
        thrownewError('Pleaseuseshowonvisibleelements');
      }

      varshowEvent=$.Event(this.constructor.Event.SHOW);

      if(this.isWithContent()&&this._isEnabled){
        $(this.element).trigger(showEvent);
        varshadowRoot=Util.findShadowRoot(this.element);
        varisInTheDom=$.contains(shadowRoot!==null?shadowRoot:this.element.ownerDocument.documentElement,this.element);

        if(showEvent.isDefaultPrevented()||!isInTheDom){
          return;
        }

        vartip=this.getTipElement();
        vartipId=Util.getUID(this.constructor.NAME);
        tip.setAttribute('id',tipId);
        this.element.setAttribute('aria-describedby',tipId);
        this.setContent();

        if(this.config.animation){
          $(tip).addClass(ClassName.FADE);
        }

        varplacement=typeofthis.config.placement==='function'?this.config.placement.call(this,tip,this.element):this.config.placement;

        varattachment=this._getAttachment(placement);

        this.addAttachmentClass(attachment);

        varcontainer=this._getContainer();

        $(tip).data(this.constructor.DATA_KEY,this);

        if(!$.contains(this.element.ownerDocument.documentElement,this.tip)){
          $(tip).appendTo(container);
        }

        $(this.element).trigger(this.constructor.Event.INSERTED);
        this._popper=newPopper(this.element,tip,{
          placement:attachment,
          modifiers:{
            offset:this._getOffset(),
            flip:{
              behavior:this.config.fallbackPlacement
            },
            arrow:{
              element:Selector.ARROW
            },
            preventOverflow:{
              boundariesElement:this.config.boundary
            }
          },
          onCreate:functiononCreate(data){
            if(data.originalPlacement!==data.placement){
              _this._handlePopperPlacementChange(data);
            }
          },
          onUpdate:functiononUpdate(data){
            return_this._handlePopperPlacementChange(data);
          }
        });
        $(tip).addClass(ClassName.SHOW);//Ifthisisatouch-enableddeviceweaddextra
        //emptymouseoverlistenerstothebody'simmediatechildren;
        //onlyneededbecauseofbrokeneventdelegationoniOS
        //https://www.quirksmode.org/blog/archives/2014/02/mouse_event_bub.html

        if('ontouchstart'indocument.documentElement){
          $(document.body).children().on('mouseover',null,$.noop);
        }

        varcomplete=functioncomplete(){
          if(_this.config.animation){
            _this._fixTransition();
          }

          varprevHoverState=_this._hoverState;
          _this._hoverState=null;
          $(_this.element).trigger(_this.constructor.Event.SHOWN);

          if(prevHoverState===HoverState.OUT){
            _this._leave(null,_this);
          }
        };

        if($(this.tip).hasClass(ClassName.FADE)){
          vartransitionDuration=Util.getTransitionDurationFromElement(this.tip);
          $(this.tip).one(Util.TRANSITION_END,complete).emulateTransitionEnd(transitionDuration);
        }else{
          complete();
        }
      }
    };

    _proto.hide=functionhide(callback){
      var_this2=this;

      vartip=this.getTipElement();
      varhideEvent=$.Event(this.constructor.Event.HIDE);

      varcomplete=functioncomplete(){
        if(_this2._hoverState!==HoverState.SHOW&&tip.parentNode){
          tip.parentNode.removeChild(tip);
        }

        _this2._cleanTipClass();

        _this2.element.removeAttribute('aria-describedby');

        $(_this2.element).trigger(_this2.constructor.Event.HIDDEN);

        if(_this2._popper!==null){
          _this2._popper.destroy();
        }

        if(callback){
          callback();
        }
      };

      $(this.element).trigger(hideEvent);

      if(hideEvent.isDefaultPrevented()){
        return;
      }

      $(tip).removeClass(ClassName.SHOW);//Ifthisisatouch-enableddeviceweremovetheextra
      //emptymouseoverlistenersweaddedforiOSsupport

      if('ontouchstart'indocument.documentElement){
        $(document.body).children().off('mouseover',null,$.noop);
      }

      this._activeTrigger[Trigger.CLICK]=false;
      this._activeTrigger[Trigger.FOCUS]=false;
      this._activeTrigger[Trigger.HOVER]=false;

      if($(this.tip).hasClass(ClassName.FADE)){
        vartransitionDuration=Util.getTransitionDurationFromElement(tip);
        $(tip).one(Util.TRANSITION_END,complete).emulateTransitionEnd(transitionDuration);
      }else{
        complete();
      }

      this._hoverState='';
    };

    _proto.update=functionupdate(){
      if(this._popper!==null){
        this._popper.scheduleUpdate();
      }
    }//Protected
    ;

    _proto.isWithContent=functionisWithContent(){
      returnBoolean(this.getTitle());
    };

    _proto.addAttachmentClass=functionaddAttachmentClass(attachment){
      $(this.getTipElement()).addClass(CLASS_PREFIX+"-"+attachment);
    };

    _proto.getTipElement=functiongetTipElement(){
      this.tip=this.tip||$(this.config.template)[0];
      returnthis.tip;
    };

    _proto.setContent=functionsetContent(){
      vartip=this.getTipElement();
      this.setElementContent($(tip.querySelectorAll(Selector.TOOLTIP_INNER)),this.getTitle());
      $(tip).removeClass(ClassName.FADE+""+ClassName.SHOW);
    };

    _proto.setElementContent=functionsetElementContent($element,content){
      if(typeofcontent==='object'&&(content.nodeType||content.jquery)){
        //ContentisaDOMnodeorajQuery
        if(this.config.html){
          if(!$(content).parent().is($element)){
            $element.empty().append(content);
          }
        }else{
          $element.text($(content).text());
        }

        return;
      }

      if(this.config.html){
        if(this.config.sanitize){
          content=sanitizeHtml(content,this.config.whiteList,this.config.sanitizeFn);
        }

        $element.html(content);
      }else{
        $element.text(content);
      }
    };

    _proto.getTitle=functiongetTitle(){
      vartitle=this.element.getAttribute('data-original-title');

      if(!title){
        title=typeofthis.config.title==='function'?this.config.title.call(this.element):this.config.title;
      }

      returntitle;
    }//Private
    ;

    _proto._getOffset=function_getOffset(){
      var_this3=this;

      varoffset={};

      if(typeofthis.config.offset==='function'){
        offset.fn=function(data){
          data.offsets=_objectSpread({},data.offsets,_this3.config.offset(data.offsets,_this3.element)||{});
          returndata;
        };
      }else{
        offset.offset=this.config.offset;
      }

      returnoffset;
    };

    _proto._getContainer=function_getContainer(){
      if(this.config.container===false){
        returndocument.body;
      }

      if(Util.isElement(this.config.container)){
        return$(this.config.container);
      }

      return$(document).find(this.config.container);
    };

    _proto._getAttachment=function_getAttachment(placement){
      returnAttachmentMap[placement.toUpperCase()];
    };

    _proto._setListeners=function_setListeners(){
      var_this4=this;

      vartriggers=this.config.trigger.split('');
      triggers.forEach(function(trigger){
        if(trigger==='click'){
          $(_this4.element).on(_this4.constructor.Event.CLICK,_this4.config.selector,function(event){
            return_this4.toggle(event);
          });
        }elseif(trigger!==Trigger.MANUAL){
          vareventIn=trigger===Trigger.HOVER?_this4.constructor.Event.MOUSEENTER:_this4.constructor.Event.FOCUSIN;
          vareventOut=trigger===Trigger.HOVER?_this4.constructor.Event.MOUSELEAVE:_this4.constructor.Event.FOCUSOUT;
          $(_this4.element).on(eventIn,_this4.config.selector,function(event){
            return_this4._enter(event);
          }).on(eventOut,_this4.config.selector,function(event){
            return_this4._leave(event);
          });
        }
      });
      $(this.element).closest('.modal').on('hide.bs.modal',function(){
        if(_this4.element){
          _this4.hide();
        }
      });

      if(this.config.selector){
        this.config=_objectSpread({},this.config,{
          trigger:'manual',
          selector:''
        });
      }else{
        this._fixTitle();
      }
    };

    _proto._fixTitle=function_fixTitle(){
      vartitleType=typeofthis.element.getAttribute('data-original-title');

      if(this.element.getAttribute('title')||titleType!=='string'){
        this.element.setAttribute('data-original-title',this.element.getAttribute('title')||'');
        this.element.setAttribute('title','');
      }
    };

    _proto._enter=function_enter(event,context){
      vardataKey=this.constructor.DATA_KEY;
      context=context||$(event.currentTarget).data(dataKey);

      if(!context){
        context=newthis.constructor(event.currentTarget,this._getDelegateConfig());
        $(event.currentTarget).data(dataKey,context);
      }

      if(event){
        context._activeTrigger[event.type==='focusin'?Trigger.FOCUS:Trigger.HOVER]=true;
      }

      if($(context.getTipElement()).hasClass(ClassName.SHOW)||context._hoverState===HoverState.SHOW){
        context._hoverState=HoverState.SHOW;
        return;
      }

      clearTimeout(context._timeout);
      context._hoverState=HoverState.SHOW;

      if(!context.config.delay||!context.config.delay.show){
        context.show();
        return;
      }

      context._timeout=setTimeout(function(){
        if(context._hoverState===HoverState.SHOW){
          context.show();
        }
      },context.config.delay.show);
    };

    _proto._leave=function_leave(event,context){
      vardataKey=this.constructor.DATA_KEY;
      context=context||$(event.currentTarget).data(dataKey);

      if(!context){
        context=newthis.constructor(event.currentTarget,this._getDelegateConfig());
        $(event.currentTarget).data(dataKey,context);
      }

      if(event){
        context._activeTrigger[event.type==='focusout'?Trigger.FOCUS:Trigger.HOVER]=false;
      }

      if(context._isWithActiveTrigger()){
        return;
      }

      clearTimeout(context._timeout);
      context._hoverState=HoverState.OUT;

      if(!context.config.delay||!context.config.delay.hide){
        context.hide();
        return;
      }

      context._timeout=setTimeout(function(){
        if(context._hoverState===HoverState.OUT){
          context.hide();
        }
      },context.config.delay.hide);
    };

    _proto._isWithActiveTrigger=function_isWithActiveTrigger(){
      for(vartriggerinthis._activeTrigger){
        if(this._activeTrigger[trigger]){
          returntrue;
        }
      }

      returnfalse;
    };

    _proto._getConfig=function_getConfig(config){
      vardataAttributes=$(this.element).data();
      Object.keys(dataAttributes).forEach(function(dataAttr){
        if(DISALLOWED_ATTRIBUTES.indexOf(dataAttr)!==-1){
          deletedataAttributes[dataAttr];
        }
      });
      config=_objectSpread({},this.constructor.Default,dataAttributes,typeofconfig==='object'&&config?config:{});

      if(typeofconfig.delay==='number'){
        config.delay={
          show:config.delay,
          hide:config.delay
        };
      }

      if(typeofconfig.title==='number'){
        config.title=config.title.toString();
      }

      if(typeofconfig.content==='number'){
        config.content=config.content.toString();
      }

      Util.typeCheckConfig(NAME,config,this.constructor.DefaultType);

      if(config.sanitize){
        config.template=sanitizeHtml(config.template,config.whiteList,config.sanitizeFn);
      }

      returnconfig;
    };

    _proto._getDelegateConfig=function_getDelegateConfig(){
      varconfig={};

      if(this.config){
        for(varkeyinthis.config){
          if(this.constructor.Default[key]!==this.config[key]){
            config[key]=this.config[key];
          }
        }
      }

      returnconfig;
    };

    _proto._cleanTipClass=function_cleanTipClass(){
      var$tip=$(this.getTipElement());
      vartabClass=$tip.attr('class').match(BSCLS_PREFIX_REGEX);

      if(tabClass!==null&&tabClass.length){
        $tip.removeClass(tabClass.join(''));
      }
    };

    _proto._handlePopperPlacementChange=function_handlePopperPlacementChange(popperData){
      varpopperInstance=popperData.instance;
      this.tip=popperInstance.popper;

      this._cleanTipClass();

      this.addAttachmentClass(this._getAttachment(popperData.placement));
    };

    _proto._fixTransition=function_fixTransition(){
      vartip=this.getTipElement();
      varinitConfigAnimation=this.config.animation;

      if(tip.getAttribute('x-placement')!==null){
        return;
      }

      $(tip).removeClass(ClassName.FADE);
      this.config.animation=false;
      this.hide();
      this.show();
      this.config.animation=initConfigAnimation;
    }//Static
    ;

    Tooltip._jQueryInterface=function_jQueryInterface(config){
      returnthis.each(function(){
        vardata=$(this).data(DATA_KEY);

        var_config=typeofconfig==='object'&&config;

        if(!data&&/dispose|hide/.test(config)){
          return;
        }

        if(!data){
          data=newTooltip(this,_config);
          $(this).data(DATA_KEY,data);
        }

        if(typeofconfig==='string'){
          if(typeofdata[config]==='undefined'){
            thrownewTypeError("Nomethodnamed\""+config+"\"");
          }

          data[config]();
        }
      });
    };

    _createClass(Tooltip,null,[{
      key:"VERSION",
      get:functionget(){
        returnVERSION;
      }
    },{
      key:"Default",
      get:functionget(){
        returnDefault;
      }
    },{
      key:"NAME",
      get:functionget(){
        returnNAME;
      }
    },{
      key:"DATA_KEY",
      get:functionget(){
        returnDATA_KEY;
      }
    },{
      key:"Event",
      get:functionget(){
        returnEvent;
      }
    },{
      key:"EVENT_KEY",
      get:functionget(){
        returnEVENT_KEY;
      }
    },{
      key:"DefaultType",
      get:functionget(){
        returnDefaultType;
      }
    }]);

    returnTooltip;
  }();
  /**
   *------------------------------------------------------------------------
   *jQuery
   *------------------------------------------------------------------------
   */


  $.fn[NAME]=Tooltip._jQueryInterface;
  $.fn[NAME].Constructor=Tooltip;

  $.fn[NAME].noConflict=function(){
    $.fn[NAME]=JQUERY_NO_CONFLICT;
    returnTooltip._jQueryInterface;
  };

  returnTooltip;

}));
