/*!
  *Bootstrapdropdown.jsv4.3.1(https://getbootstrap.com/)
  *Copyright2011-2019TheBootstrapAuthors(https://github.com/twbs/bootstrap/graphs/contributors)
  *LicensedunderMIT(https://github.com/twbs/bootstrap/blob/master/LICENSE)
  */
(function(global,factory){
  typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory(require('jquery'),require('popper.js'),require('./util.js')):
  typeofdefine==='function'&&define.amd?define(['jquery','popper.js','./util.js'],factory):
  (global=global||self,global.Dropdown=factory(global.jQuery,global.Popper,global.Util));
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
   *------------------------------------------------------------------------
   *Constants
   *------------------------------------------------------------------------
   */

  varNAME='dropdown';
  varVERSION='4.3.1';
  varDATA_KEY='bs.dropdown';
  varEVENT_KEY="."+DATA_KEY;
  varDATA_API_KEY='.data-api';
  varJQUERY_NO_CONFLICT=$.fn[NAME];
  varESCAPE_KEYCODE=27;//KeyboardEvent.whichvalueforEscape(Esc)key

  varSPACE_KEYCODE=32;//KeyboardEvent.whichvalueforspacekey

  varTAB_KEYCODE=9;//KeyboardEvent.whichvaluefortabkey

  varARROW_UP_KEYCODE=38;//KeyboardEvent.whichvalueforuparrowkey

  varARROW_DOWN_KEYCODE=40;//KeyboardEvent.whichvaluefordownarrowkey

  varRIGHT_MOUSE_BUTTON_WHICH=3;//MouseEvent.whichvaluefortherightbutton(assumingaright-handedmouse)

  varREGEXP_KEYDOWN=newRegExp(ARROW_UP_KEYCODE+"|"+ARROW_DOWN_KEYCODE+"|"+ESCAPE_KEYCODE);
  varEvent={
    HIDE:"hide"+EVENT_KEY,
    HIDDEN:"hidden"+EVENT_KEY,
    SHOW:"show"+EVENT_KEY,
    SHOWN:"shown"+EVENT_KEY,
    CLICK:"click"+EVENT_KEY,
    CLICK_DATA_API:"click"+EVENT_KEY+DATA_API_KEY,
    KEYDOWN_DATA_API:"keydown"+EVENT_KEY+DATA_API_KEY,
    KEYUP_DATA_API:"keyup"+EVENT_KEY+DATA_API_KEY
  };
  varClassName={
    DISABLED:'disabled',
    SHOW:'show',
    DROPUP:'dropup',
    DROPRIGHT:'dropright',
    DROPLEFT:'dropleft',
    MENURIGHT:'dropdown-menu-right',
    MENULEFT:'dropdown-menu-left',
    POSITION_STATIC:'position-static'
  };
  varSelector={
    DATA_TOGGLE:'[data-toggle="dropdown"]',
    FORM_CHILD:'.dropdownform',
    MENU:'.dropdown-menu',
    NAVBAR_NAV:'.navbar-nav',
    VISIBLE_ITEMS:'.dropdown-menu.dropdown-item:not(.disabled):not(:disabled)'
  };
  varAttachmentMap={
    TOP:'top-start',
    TOPEND:'top-end',
    BOTTOM:'bottom-start',
    BOTTOMEND:'bottom-end',
    RIGHT:'right-start',
    RIGHTEND:'right-end',
    LEFT:'left-start',
    LEFTEND:'left-end'
  };
  varDefault={
    offset:0,
    flip:true,
    boundary:'scrollParent',
    reference:'toggle',
    display:'dynamic'
  };
  varDefaultType={
    offset:'(number|string|function)',
    flip:'boolean',
    boundary:'(string|element)',
    reference:'(string|element)',
    display:'string'
    /**
     *------------------------------------------------------------------------
     *ClassDefinition
     *------------------------------------------------------------------------
     */

  };

  varDropdown=
  /*#__PURE__*/
  function(){
    functionDropdown(element,config){
      this._element=element;
      this._popper=null;
      this._config=this._getConfig(config);
      this._menu=this._getMenuElement();
      this._inNavbar=this._detectNavbar();

      this._addEventListeners();
    }//Getters


    var_proto=Dropdown.prototype;

    //Public
    _proto.toggle=functiontoggle(){
      if(this._element.disabled||$(this._element).hasClass(ClassName.DISABLED)){
        return;
      }

      varparent=Dropdown._getParentFromElement(this._element);

      varisActive=$(this._menu).hasClass(ClassName.SHOW);

      Dropdown._clearMenus();

      if(isActive){
        return;
      }

      varrelatedTarget={
        relatedTarget:this._element
      };
      varshowEvent=$.Event(Event.SHOW,relatedTarget);
      $(parent).trigger(showEvent);

      if(showEvent.isDefaultPrevented()){
        return;
      }//DisabletotallyPopper.jsforDropdowninNavbar


      if(!this._inNavbar){
        /**
         *CheckforPopperdependency
         *Popper-https://popper.js.org
         */
        if(typeofPopper==='undefined'){
          thrownewTypeError('Bootstrap\'sdropdownsrequirePopper.js(https://popper.js.org/)');
        }

        varreferenceElement=this._element;

        if(this._config.reference==='parent'){
          referenceElement=parent;
        }elseif(Util.isElement(this._config.reference)){
          referenceElement=this._config.reference;//Checkifit'sjQueryelement

          if(typeofthis._config.reference.jquery!=='undefined'){
            referenceElement=this._config.reference[0];
          }
        }//Ifboundaryisnot`scrollParent`,thensetpositionto`static`
        //toallowthemenuto"escape"thescrollparent'sboundaries
        //https://github.com/twbs/bootstrap/issues/24251


        if(this._config.boundary!=='scrollParent'){
          $(parent).addClass(ClassName.POSITION_STATIC);
        }

        this._popper=newPopper(referenceElement,this._menu,this._getPopperConfig());
      }//Ifthisisatouch-enableddeviceweaddextra
      //emptymouseoverlistenerstothebody'simmediatechildren;
      //onlyneededbecauseofbrokeneventdelegationoniOS
      //https://www.quirksmode.org/blog/archives/2014/02/mouse_event_bub.html


      if('ontouchstart'indocument.documentElement&&$(parent).closest(Selector.NAVBAR_NAV).length===0){
        $(document.body).children().on('mouseover',null,$.noop);
      }

      this._element.focus();

      this._element.setAttribute('aria-expanded',true);

      $(this._menu).toggleClass(ClassName.SHOW);
      $(parent).toggleClass(ClassName.SHOW).trigger($.Event(Event.SHOWN,relatedTarget));
    };

    _proto.show=functionshow(){
      if(this._element.disabled||$(this._element).hasClass(ClassName.DISABLED)||$(this._menu).hasClass(ClassName.SHOW)){
        return;
      }

      varrelatedTarget={
        relatedTarget:this._element
      };
      varshowEvent=$.Event(Event.SHOW,relatedTarget);

      varparent=Dropdown._getParentFromElement(this._element);

      $(parent).trigger(showEvent);

      if(showEvent.isDefaultPrevented()){
        return;
      }

      $(this._menu).toggleClass(ClassName.SHOW);
      $(parent).toggleClass(ClassName.SHOW).trigger($.Event(Event.SHOWN,relatedTarget));
    };

    _proto.hide=functionhide(){
      if(this._element.disabled||$(this._element).hasClass(ClassName.DISABLED)||!$(this._menu).hasClass(ClassName.SHOW)){
        return;
      }

      varrelatedTarget={
        relatedTarget:this._element
      };
      varhideEvent=$.Event(Event.HIDE,relatedTarget);

      varparent=Dropdown._getParentFromElement(this._element);

      $(parent).trigger(hideEvent);

      if(hideEvent.isDefaultPrevented()){
        return;
      }

      $(this._menu).toggleClass(ClassName.SHOW);
      $(parent).toggleClass(ClassName.SHOW).trigger($.Event(Event.HIDDEN,relatedTarget));
    };

    _proto.dispose=functiondispose(){
      $.removeData(this._element,DATA_KEY);
      $(this._element).off(EVENT_KEY);
      this._element=null;
      this._menu=null;

      if(this._popper!==null){
        this._popper.destroy();

        this._popper=null;
      }
    };

    _proto.update=functionupdate(){
      this._inNavbar=this._detectNavbar();

      if(this._popper!==null){
        this._popper.scheduleUpdate();
      }
    }//Private
    ;

    _proto._addEventListeners=function_addEventListeners(){
      var_this=this;

      $(this._element).on(Event.CLICK,function(event){
        event.preventDefault();
        event.stopPropagation();

        _this.toggle();
      });
    };

    _proto._getConfig=function_getConfig(config){
      config=_objectSpread({},this.constructor.Default,$(this._element).data(),config);
      Util.typeCheckConfig(NAME,config,this.constructor.DefaultType);
      returnconfig;
    };

    _proto._getMenuElement=function_getMenuElement(){
      if(!this._menu){
        varparent=Dropdown._getParentFromElement(this._element);

        if(parent){
          this._menu=parent.querySelector(Selector.MENU);
        }
      }

      returnthis._menu;
    };

    _proto._getPlacement=function_getPlacement(){
      var$parentDropdown=$(this._element.parentNode);
      varplacement=AttachmentMap.BOTTOM;//Handledropup

      if($parentDropdown.hasClass(ClassName.DROPUP)){
        placement=AttachmentMap.TOP;

        if($(this._menu).hasClass(ClassName.MENURIGHT)){
          placement=AttachmentMap.TOPEND;
        }
      }elseif($parentDropdown.hasClass(ClassName.DROPRIGHT)){
        placement=AttachmentMap.RIGHT;
      }elseif($parentDropdown.hasClass(ClassName.DROPLEFT)){
        placement=AttachmentMap.LEFT;
      }elseif($(this._menu).hasClass(ClassName.MENURIGHT)){
        placement=AttachmentMap.BOTTOMEND;
      }

      returnplacement;
    };

    _proto._detectNavbar=function_detectNavbar(){
      return$(this._element).closest('.navbar').length>0;
    };

    _proto._getOffset=function_getOffset(){
      var_this2=this;

      varoffset={};

      if(typeofthis._config.offset==='function'){
        offset.fn=function(data){
          data.offsets=_objectSpread({},data.offsets,_this2._config.offset(data.offsets,_this2._element)||{});
          returndata;
        };
      }else{
        offset.offset=this._config.offset;
      }

      returnoffset;
    };

    _proto._getPopperConfig=function_getPopperConfig(){
      varpopperConfig={
        placement:this._getPlacement(),
        modifiers:{
          offset:this._getOffset(),
          flip:{
            enabled:this._config.flip
          },
          preventOverflow:{
            boundariesElement:this._config.boundary
          }
        }//DisablePopper.jsifwehaveastaticdisplay

      };

      if(this._config.display==='static'){
        popperConfig.modifiers.applyStyle={
          enabled:false
        };
      }

      returnpopperConfig;
    }//Static
    ;

    Dropdown._jQueryInterface=function_jQueryInterface(config){
      returnthis.each(function(){
        vardata=$(this).data(DATA_KEY);

        var_config=typeofconfig==='object'?config:null;

        if(!data){
          data=newDropdown(this,_config);
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

    Dropdown._clearMenus=function_clearMenus(event){
      if(event&&(event.which===RIGHT_MOUSE_BUTTON_WHICH||event.type==='keyup'&&event.which!==TAB_KEYCODE)){
        return;
      }

      vartoggles=[].slice.call(document.querySelectorAll(Selector.DATA_TOGGLE));

      for(vari=0,len=toggles.length;i<len;i++){
        varparent=Dropdown._getParentFromElement(toggles[i]);

        varcontext=$(toggles[i]).data(DATA_KEY);
        varrelatedTarget={
          relatedTarget:toggles[i]
        };

        if(event&&event.type==='click'){
          relatedTarget.clickEvent=event;
        }

        if(!context){
          continue;
        }

        vardropdownMenu=context._menu;

        if(!$(parent).hasClass(ClassName.SHOW)){
          continue;
        }

        if(event&&(event.type==='click'&&/input|textarea/i.test(event.target.tagName)||event.type==='keyup'&&event.which===TAB_KEYCODE)&&$.contains(parent,event.target)){
          continue;
        }

        varhideEvent=$.Event(Event.HIDE,relatedTarget);
        $(parent).trigger(hideEvent);

        if(hideEvent.isDefaultPrevented()){
          continue;
        }//Ifthisisatouch-enableddeviceweremovetheextra
        //emptymouseoverlistenersweaddedforiOSsupport


        if('ontouchstart'indocument.documentElement){
          $(document.body).children().off('mouseover',null,$.noop);
        }

        toggles[i].setAttribute('aria-expanded','false');
        $(dropdownMenu).removeClass(ClassName.SHOW);
        $(parent).removeClass(ClassName.SHOW).trigger($.Event(Event.HIDDEN,relatedTarget));
      }
    };

    Dropdown._getParentFromElement=function_getParentFromElement(element){
      varparent;
      varselector=Util.getSelectorFromElement(element);

      if(selector){
        parent=document.querySelector(selector);
      }

      returnparent||element.parentNode;
    }//eslint-disable-next-linecomplexity
    ;

    Dropdown._dataApiKeydownHandler=function_dataApiKeydownHandler(event){
      //Ifnotinput/textarea:
      // -AndnotakeyinREGEXP_KEYDOWN=>notadropdowncommand
      //Ifinput/textarea:
      // -Ifspacekey=>notadropdowncommand
      // -Ifkeyisotherthanescape
      //   -Ifkeyisnotupordown=>notadropdowncommand
      //   -Iftriggerinsidethemenu=>notadropdowncommand
      if(/input|textarea/i.test(event.target.tagName)?event.which===SPACE_KEYCODE||event.which!==ESCAPE_KEYCODE&&(event.which!==ARROW_DOWN_KEYCODE&&event.which!==ARROW_UP_KEYCODE||$(event.target).closest(Selector.MENU).length):!REGEXP_KEYDOWN.test(event.which)){
        return;
      }

      event.preventDefault();
      event.stopPropagation();

      if(this.disabled||$(this).hasClass(ClassName.DISABLED)){
        return;
      }

      varparent=Dropdown._getParentFromElement(this);

      varisActive=$(parent).hasClass(ClassName.SHOW);

      if(!isActive||isActive&&(event.which===ESCAPE_KEYCODE||event.which===SPACE_KEYCODE)){
        if(event.which===ESCAPE_KEYCODE){
          vartoggle=parent.querySelector(Selector.DATA_TOGGLE);
          $(toggle).trigger('focus');
        }

        $(this).trigger('click');
        return;
      }

      varitems=[].slice.call(parent.querySelectorAll(Selector.VISIBLE_ITEMS));

      if(items.length===0){
        return;
      }

      varindex=items.indexOf(event.target);

      if(event.which===ARROW_UP_KEYCODE&&index>0){
        //Up
        index--;
      }

      if(event.which===ARROW_DOWN_KEYCODE&&index<items.length-1){
        //Down
        index++;
      }

      if(index<0){
        index=0;
      }

      items[index].focus();
    };

    _createClass(Dropdown,null,[{
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
      key:"DefaultType",
      get:functionget(){
        returnDefaultType;
      }
    }]);

    returnDropdown;
  }();
  /**
   *------------------------------------------------------------------------
   *DataApiimplementation
   *------------------------------------------------------------------------
   */


  $(document).on(Event.KEYDOWN_DATA_API,Selector.DATA_TOGGLE,Dropdown._dataApiKeydownHandler).on(Event.KEYDOWN_DATA_API,Selector.MENU,Dropdown._dataApiKeydownHandler).on(Event.CLICK_DATA_API+""+Event.KEYUP_DATA_API,Dropdown._clearMenus).on(Event.CLICK_DATA_API,Selector.DATA_TOGGLE,function(event){
    event.preventDefault();
    event.stopPropagation();

    Dropdown._jQueryInterface.call($(this),'toggle');
  }).on(Event.CLICK_DATA_API,Selector.FORM_CHILD,function(e){
    e.stopPropagation();
  });
  /**
   *------------------------------------------------------------------------
   *jQuery
   *------------------------------------------------------------------------
   */

  $.fn[NAME]=Dropdown._jQueryInterface;
  $.fn[NAME].Constructor=Dropdown;

  $.fn[NAME].noConflict=function(){
    $.fn[NAME]=JQUERY_NO_CONFLICT;
    returnDropdown._jQueryInterface;
  };

  returnDropdown;

}));
