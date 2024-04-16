/*!
  *Bootstrapcollapse.jsv4.3.1(https://getbootstrap.com/)
  *Copyright2011-2019TheBootstrapAuthors(https://github.com/twbs/bootstrap/graphs/contributors)
  *LicensedunderMIT(https://github.com/twbs/bootstrap/blob/master/LICENSE)
  */
(function(global,factory){
  typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory(require('jquery'),require('./util.js')):
  typeofdefine==='function'&&define.amd?define(['jquery','./util.js'],factory):
  (global=global||self,global.Collapse=factory(global.jQuery,global.Util));
}(this,function($,Util){'usestrict';

  $=$&&$.hasOwnProperty('default')?$['default']:$;
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

  varNAME='collapse';
  varVERSION='4.3.1';
  varDATA_KEY='bs.collapse';
  varEVENT_KEY="."+DATA_KEY;
  varDATA_API_KEY='.data-api';
  varJQUERY_NO_CONFLICT=$.fn[NAME];
  varDefault={
    toggle:true,
    parent:''
  };
  varDefaultType={
    toggle:'boolean',
    parent:'(string|element)'
  };
  varEvent={
    SHOW:"show"+EVENT_KEY,
    SHOWN:"shown"+EVENT_KEY,
    HIDE:"hide"+EVENT_KEY,
    HIDDEN:"hidden"+EVENT_KEY,
    CLICK_DATA_API:"click"+EVENT_KEY+DATA_API_KEY
  };
  varClassName={
    SHOW:'show',
    COLLAPSE:'collapse',
    COLLAPSING:'collapsing',
    COLLAPSED:'collapsed'
  };
  varDimension={
    WIDTH:'width',
    HEIGHT:'height'
  };
  varSelector={
    ACTIVES:'.show,.collapsing',
    DATA_TOGGLE:'[data-toggle="collapse"]'
    /**
     *------------------------------------------------------------------------
     *ClassDefinition
     *------------------------------------------------------------------------
     */

  };

  varCollapse=
  /*#__PURE__*/
  function(){
    functionCollapse(element,config){
      this._isTransitioning=false;
      this._element=element;
      this._config=this._getConfig(config);
      this._triggerArray=[].slice.call(document.querySelectorAll("[data-toggle=\"collapse\"][href=\"#"+element.id+"\"],"+("[data-toggle=\"collapse\"][data-target=\"#"+element.id+"\"]")));
      vartoggleList=[].slice.call(document.querySelectorAll(Selector.DATA_TOGGLE));

      for(vari=0,len=toggleList.length;i<len;i++){
        varelem=toggleList[i];
        varselector=Util.getSelectorFromElement(elem);
        varfilterElement=[].slice.call(document.querySelectorAll(selector)).filter(function(foundElem){
          returnfoundElem===element;
        });

        if(selector!==null&&filterElement.length>0){
          this._selector=selector;

          this._triggerArray.push(elem);
        }
      }

      this._parent=this._config.parent?this._getParent():null;

      if(!this._config.parent){
        this._addAriaAndCollapsedClass(this._element,this._triggerArray);
      }

      if(this._config.toggle){
        this.toggle();
      }
    }//Getters


    var_proto=Collapse.prototype;

    //Public
    _proto.toggle=functiontoggle(){
      if($(this._element).hasClass(ClassName.SHOW)){
        this.hide();
      }else{
        this.show();
      }
    };

    _proto.show=functionshow(){
      var_this=this;

      if(this._isTransitioning||$(this._element).hasClass(ClassName.SHOW)){
        return;
      }

      varactives;
      varactivesData;

      if(this._parent){
        actives=[].slice.call(this._parent.querySelectorAll(Selector.ACTIVES)).filter(function(elem){
          if(typeof_this._config.parent==='string'){
            returnelem.getAttribute('data-parent')===_this._config.parent;
          }

          returnelem.classList.contains(ClassName.COLLAPSE);
        });

        if(actives.length===0){
          actives=null;
        }
      }

      if(actives){
        activesData=$(actives).not(this._selector).data(DATA_KEY);

        if(activesData&&activesData._isTransitioning){
          return;
        }
      }

      varstartEvent=$.Event(Event.SHOW);
      $(this._element).trigger(startEvent);

      if(startEvent.isDefaultPrevented()){
        return;
      }

      if(actives){
        Collapse._jQueryInterface.call($(actives).not(this._selector),'hide');

        if(!activesData){
          $(actives).data(DATA_KEY,null);
        }
      }

      vardimension=this._getDimension();

      $(this._element).removeClass(ClassName.COLLAPSE).addClass(ClassName.COLLAPSING);
      this._element.style[dimension]=0;

      if(this._triggerArray.length){
        $(this._triggerArray).removeClass(ClassName.COLLAPSED).attr('aria-expanded',true);
      }

      this.setTransitioning(true);

      varcomplete=functioncomplete(){
        $(_this._element).removeClass(ClassName.COLLAPSING).addClass(ClassName.COLLAPSE).addClass(ClassName.SHOW);
        _this._element.style[dimension]='';

        _this.setTransitioning(false);

        $(_this._element).trigger(Event.SHOWN);
      };

      varcapitalizedDimension=dimension[0].toUpperCase()+dimension.slice(1);
      varscrollSize="scroll"+capitalizedDimension;
      vartransitionDuration=Util.getTransitionDurationFromElement(this._element);
      $(this._element).one(Util.TRANSITION_END,complete).emulateTransitionEnd(transitionDuration);
      this._element.style[dimension]=this._element[scrollSize]+"px";
    };

    _proto.hide=functionhide(){
      var_this2=this;

      if(this._isTransitioning||!$(this._element).hasClass(ClassName.SHOW)){
        return;
      }

      varstartEvent=$.Event(Event.HIDE);
      $(this._element).trigger(startEvent);

      if(startEvent.isDefaultPrevented()){
        return;
      }

      vardimension=this._getDimension();

      this._element.style[dimension]=this._element.getBoundingClientRect()[dimension]+"px";
      Util.reflow(this._element);
      $(this._element).addClass(ClassName.COLLAPSING).removeClass(ClassName.COLLAPSE).removeClass(ClassName.SHOW);
      vartriggerArrayLength=this._triggerArray.length;

      if(triggerArrayLength>0){
        for(vari=0;i<triggerArrayLength;i++){
          vartrigger=this._triggerArray[i];
          varselector=Util.getSelectorFromElement(trigger);

          if(selector!==null){
            var$elem=$([].slice.call(document.querySelectorAll(selector)));

            if(!$elem.hasClass(ClassName.SHOW)){
              $(trigger).addClass(ClassName.COLLAPSED).attr('aria-expanded',false);
            }
          }
        }
      }

      this.setTransitioning(true);

      varcomplete=functioncomplete(){
        _this2.setTransitioning(false);

        $(_this2._element).removeClass(ClassName.COLLAPSING).addClass(ClassName.COLLAPSE).trigger(Event.HIDDEN);
      };

      this._element.style[dimension]='';
      vartransitionDuration=Util.getTransitionDurationFromElement(this._element);
      $(this._element).one(Util.TRANSITION_END,complete).emulateTransitionEnd(transitionDuration);
    };

    _proto.setTransitioning=functionsetTransitioning(isTransitioning){
      this._isTransitioning=isTransitioning;
    };

    _proto.dispose=functiondispose(){
      $.removeData(this._element,DATA_KEY);
      this._config=null;
      this._parent=null;
      this._element=null;
      this._triggerArray=null;
      this._isTransitioning=null;
    }//Private
    ;

    _proto._getConfig=function_getConfig(config){
      config=_objectSpread({},Default,config);
      config.toggle=Boolean(config.toggle);//Coercestringvalues

      Util.typeCheckConfig(NAME,config,DefaultType);
      returnconfig;
    };

    _proto._getDimension=function_getDimension(){
      varhasWidth=$(this._element).hasClass(Dimension.WIDTH);
      returnhasWidth?Dimension.WIDTH:Dimension.HEIGHT;
    };

    _proto._getParent=function_getParent(){
      var_this3=this;

      varparent;

      if(Util.isElement(this._config.parent)){
        parent=this._config.parent;//It'sajQueryobject

        if(typeofthis._config.parent.jquery!=='undefined'){
          parent=this._config.parent[0];
        }
      }else{
        parent=document.querySelector(this._config.parent);
      }

      varselector="[data-toggle=\"collapse\"][data-parent=\""+this._config.parent+"\"]";
      varchildren=[].slice.call(parent.querySelectorAll(selector));
      $(children).each(function(i,element){
        _this3._addAriaAndCollapsedClass(Collapse._getTargetFromElement(element),[element]);
      });
      returnparent;
    };

    _proto._addAriaAndCollapsedClass=function_addAriaAndCollapsedClass(element,triggerArray){
      varisOpen=$(element).hasClass(ClassName.SHOW);

      if(triggerArray.length){
        $(triggerArray).toggleClass(ClassName.COLLAPSED,!isOpen).attr('aria-expanded',isOpen);
      }
    }//Static
    ;

    Collapse._getTargetFromElement=function_getTargetFromElement(element){
      varselector=Util.getSelectorFromElement(element);
      returnselector?document.querySelector(selector):null;
    };

    Collapse._jQueryInterface=function_jQueryInterface(config){
      returnthis.each(function(){
        var$this=$(this);
        vardata=$this.data(DATA_KEY);

        var_config=_objectSpread({},Default,$this.data(),typeofconfig==='object'&&config?config:{});

        if(!data&&_config.toggle&&/show|hide/.test(config)){
          _config.toggle=false;
        }

        if(!data){
          data=newCollapse(this,_config);
          $this.data(DATA_KEY,data);
        }

        if(typeofconfig==='string'){
          if(typeofdata[config]==='undefined'){
            thrownewTypeError("Nomethodnamed\""+config+"\"");
          }

          data[config]();
        }
      });
    };

    _createClass(Collapse,null,[{
      key:"VERSION",
      get:functionget(){
        returnVERSION;
      }
    },{
      key:"Default",
      get:functionget(){
        returnDefault;
      }
    }]);

    returnCollapse;
  }();
  /**
   *------------------------------------------------------------------------
   *DataApiimplementation
   *------------------------------------------------------------------------
   */


  $(document).on(Event.CLICK_DATA_API,Selector.DATA_TOGGLE,function(event){
    //preventDefaultonlyfor<a>elements(whichchangetheURL)notinsidethecollapsibleelement
    if(event.currentTarget.tagName==='A'){
      event.preventDefault();
    }

    var$trigger=$(this);
    varselector=Util.getSelectorFromElement(this);
    varselectors=[].slice.call(document.querySelectorAll(selector));
    $(selectors).each(function(){
      var$target=$(this);
      vardata=$target.data(DATA_KEY);
      varconfig=data?'toggle':$trigger.data();

      Collapse._jQueryInterface.call($target,config);
    });
  });
  /**
   *------------------------------------------------------------------------
   *jQuery
   *------------------------------------------------------------------------
   */

  $.fn[NAME]=Collapse._jQueryInterface;
  $.fn[NAME].Constructor=Collapse;

  $.fn[NAME].noConflict=function(){
    $.fn[NAME]=JQUERY_NO_CONFLICT;
    returnCollapse._jQueryInterface;
  };

  returnCollapse;

}));
