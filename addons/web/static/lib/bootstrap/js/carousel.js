/*!
  *Bootstrapcarousel.jsv4.3.1(https://getbootstrap.com/)
  *Copyright2011-2019TheBootstrapAuthors(https://github.com/twbs/bootstrap/graphs/contributors)
  *LicensedunderMIT(https://github.com/twbs/bootstrap/blob/master/LICENSE)
  */
(function(global,factory){
  typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory(require('jquery'),require('./util.js')):
  typeofdefine==='function'&&define.amd?define(['jquery','./util.js'],factory):
  (global=global||self,global.Carousel=factory(global.jQuery,global.Util));
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

  varNAME='carousel';
  varVERSION='4.3.1';
  varDATA_KEY='bs.carousel';
  varEVENT_KEY="."+DATA_KEY;
  varDATA_API_KEY='.data-api';
  varJQUERY_NO_CONFLICT=$.fn[NAME];
  varARROW_LEFT_KEYCODE=37;//KeyboardEvent.whichvalueforleftarrowkey

  varARROW_RIGHT_KEYCODE=39;//KeyboardEvent.whichvalueforrightarrowkey

  varTOUCHEVENT_COMPAT_WAIT=500;//Timeformousecompateventstofireaftertouch

  varSWIPE_THRESHOLD=40;
  varDefault={
    interval:5000,
    keyboard:true,
    slide:false,
    pause:'hover',
    wrap:true,
    touch:true
  };
  varDefaultType={
    interval:'(number|boolean)',
    keyboard:'boolean',
    slide:'(boolean|string)',
    pause:'(string|boolean)',
    wrap:'boolean',
    touch:'boolean'
  };
  varDirection={
    NEXT:'next',
    PREV:'prev',
    LEFT:'left',
    RIGHT:'right'
  };
  varEvent={
    SLIDE:"slide"+EVENT_KEY,
    SLID:"slid"+EVENT_KEY,
    KEYDOWN:"keydown"+EVENT_KEY,
    MOUSEENTER:"mouseenter"+EVENT_KEY,
    MOUSELEAVE:"mouseleave"+EVENT_KEY,
    TOUCHSTART:"touchstart"+EVENT_KEY,
    TOUCHMOVE:"touchmove"+EVENT_KEY,
    TOUCHEND:"touchend"+EVENT_KEY,
    POINTERDOWN:"pointerdown"+EVENT_KEY,
    POINTERUP:"pointerup"+EVENT_KEY,
    DRAG_START:"dragstart"+EVENT_KEY,
    LOAD_DATA_API:"load"+EVENT_KEY+DATA_API_KEY,
    CLICK_DATA_API:"click"+EVENT_KEY+DATA_API_KEY
  };
  varClassName={
    CAROUSEL:'carousel',
    ACTIVE:'active',
    SLIDE:'slide',
    RIGHT:'carousel-item-right',
    LEFT:'carousel-item-left',
    NEXT:'carousel-item-next',
    PREV:'carousel-item-prev',
    ITEM:'carousel-item',
    POINTER_EVENT:'pointer-event'
  };
  varSelector={
    ACTIVE:'.active',
    ACTIVE_ITEM:'.active.carousel-item',
    ITEM:'.carousel-item',
    ITEM_IMG:'.carousel-itemimg',
    NEXT_PREV:'.carousel-item-next,.carousel-item-prev',
    INDICATORS:'.carousel-indicators',
    DATA_SLIDE:'[data-slide],[data-slide-to]',
    DATA_RIDE:'[data-ride="carousel"]'
  };
  varPointerType={
    TOUCH:'touch',
    PEN:'pen'
    /**
     *------------------------------------------------------------------------
     *ClassDefinition
     *------------------------------------------------------------------------
     */

  };

  varCarousel=
  /*#__PURE__*/
  function(){
    functionCarousel(element,config){
      this._items=null;
      this._interval=null;
      this._activeElement=null;
      this._isPaused=false;
      this._isSliding=false;
      this.touchTimeout=null;
      this.touchStartX=0;
      this.touchDeltaX=0;
      this._config=this._getConfig(config);
      this._element=element;
      this._indicatorsElement=this._element.querySelector(Selector.INDICATORS);
      this._touchSupported='ontouchstart'indocument.documentElement||navigator.maxTouchPoints>0;
      this._pointerEvent=Boolean(window.PointerEvent||window.MSPointerEvent);

      this._addEventListeners();
    }//Getters


    var_proto=Carousel.prototype;

    //Public
    _proto.next=functionnext(){
      if(!this._isSliding){
        this._slide(Direction.NEXT);
      }
    };

    _proto.nextWhenVisible=functionnextWhenVisible(){
      //Don'tcallnextwhenthepageisn'tvisible
      //orthecarouseloritsparentisn'tvisible
      if(!document.hidden&&$(this._element).is(':visible')&&$(this._element).css('visibility')!=='hidden'){
        this.next();
      }
    };

    _proto.prev=functionprev(){
      if(!this._isSliding){
        this._slide(Direction.PREV);
      }
    };

    _proto.pause=functionpause(event){
      if(!event){
        this._isPaused=true;
      }

      if(this._element.querySelector(Selector.NEXT_PREV)){
        Util.triggerTransitionEnd(this._element);
        this.cycle(true);
      }

      clearInterval(this._interval);
      this._interval=null;
    };

    _proto.cycle=functioncycle(event){
      if(!event){
        this._isPaused=false;
      }

      if(this._interval){
        clearInterval(this._interval);
        this._interval=null;
      }

      if(this._config.interval&&!this._isPaused){
        this._interval=setInterval((document.visibilityState?this.nextWhenVisible:this.next).bind(this),this._config.interval);
      }
    };

    _proto.to=functionto(index){
      var_this=this;

      this._activeElement=this._element.querySelector(Selector.ACTIVE_ITEM);

      varactiveIndex=this._getItemIndex(this._activeElement);

      if(index>this._items.length-1||index<0){
        return;
      }

      if(this._isSliding){
        $(this._element).one(Event.SLID,function(){
          return_this.to(index);
        });
        return;
      }

      if(activeIndex===index){
        this.pause();
        this.cycle();
        return;
      }

      vardirection=index>activeIndex?Direction.NEXT:Direction.PREV;

      this._slide(direction,this._items[index]);
    };

    _proto.dispose=functiondispose(){
      $(this._element).off(EVENT_KEY);
      $.removeData(this._element,DATA_KEY);
      this._items=null;
      this._config=null;
      this._element=null;
      this._interval=null;
      this._isPaused=null;
      this._isSliding=null;
      this._activeElement=null;
      this._indicatorsElement=null;
    }//Private
    ;

    _proto._getConfig=function_getConfig(config){
      config=_objectSpread({},Default,config);
      Util.typeCheckConfig(NAME,config,DefaultType);
      returnconfig;
    };

    _proto._handleSwipe=function_handleSwipe(){
      varabsDeltax=Math.abs(this.touchDeltaX);

      if(absDeltax<=SWIPE_THRESHOLD){
        return;
      }

      vardirection=absDeltax/this.touchDeltaX;//swipeleft

      if(direction>0){
        this.prev();
      }//swiperight


      if(direction<0){
        this.next();
      }
    };

    _proto._addEventListeners=function_addEventListeners(){
      var_this2=this;

      if(this._config.keyboard){
        $(this._element).on(Event.KEYDOWN,function(event){
          return_this2._keydown(event);
        });
      }

      if(this._config.pause==='hover'){
        $(this._element).on(Event.MOUSEENTER,function(event){
          return_this2.pause(event);
        }).on(Event.MOUSELEAVE,function(event){
          return_this2.cycle(event);
        });
      }

      if(this._config.touch){
        this._addTouchEventListeners();
      }
    };

    _proto._addTouchEventListeners=function_addTouchEventListeners(){
      var_this3=this;

      if(!this._touchSupported){
        return;
      }

      varstart=functionstart(event){
        if(_this3._pointerEvent&&PointerType[event.originalEvent.pointerType.toUpperCase()]){
          _this3.touchStartX=event.originalEvent.clientX;
        }elseif(!_this3._pointerEvent){
          _this3.touchStartX=event.originalEvent.touches[0].clientX;
        }
      };

      varmove=functionmove(event){
        //ensureswipingwithonetouchandnotpinching
        if(event.originalEvent.touches&&event.originalEvent.touches.length>1){
          _this3.touchDeltaX=0;
        }else{
          _this3.touchDeltaX=event.originalEvent.touches[0].clientX-_this3.touchStartX;
        }
      };

      varend=functionend(event){
        if(_this3._pointerEvent&&PointerType[event.originalEvent.pointerType.toUpperCase()]){
          _this3.touchDeltaX=event.originalEvent.clientX-_this3.touchStartX;
        }

        _this3._handleSwipe();

        if(_this3._config.pause==='hover'){
          //Ifit'satouch-enableddevice,mouseenter/leavearefiredas
          //partofthemousecompatibilityeventsonfirsttap-thecarousel
          //wouldstopcyclinguntilusertappedoutofit;
          //here,welistenfortouchend,explicitlypausethecarousel
          //(asifit'sthesecondtimewetaponit,mouseentercompatevent
          //isNOTfired)andafteratimeout(toallowformousecompatibility
          //eventstofire)weexplicitlyrestartcycling
          _this3.pause();

          if(_this3.touchTimeout){
            clearTimeout(_this3.touchTimeout);
          }

          _this3.touchTimeout=setTimeout(function(event){
            return_this3.cycle(event);
          },TOUCHEVENT_COMPAT_WAIT+_this3._config.interval);
        }
      };

      $(this._element.querySelectorAll(Selector.ITEM_IMG)).on(Event.DRAG_START,function(e){
        returne.preventDefault();
      });

      if(this._pointerEvent){
        $(this._element).on(Event.POINTERDOWN,function(event){
          returnstart(event);
        });
        $(this._element).on(Event.POINTERUP,function(event){
          returnend(event);
        });

        this._element.classList.add(ClassName.POINTER_EVENT);
      }else{
        $(this._element).on(Event.TOUCHSTART,function(event){
          returnstart(event);
        });
        $(this._element).on(Event.TOUCHMOVE,function(event){
          returnmove(event);
        });
        $(this._element).on(Event.TOUCHEND,function(event){
          returnend(event);
        });
      }
    };

    _proto._keydown=function_keydown(event){
      if(/input|textarea/i.test(event.target.tagName)){
        return;
      }

      switch(event.which){
        caseARROW_LEFT_KEYCODE:
          event.preventDefault();
          this.prev();
          break;

        caseARROW_RIGHT_KEYCODE:
          event.preventDefault();
          this.next();
          break;

        default:
      }
    };

    _proto._getItemIndex=function_getItemIndex(element){
      this._items=element&&element.parentNode?[].slice.call(element.parentNode.querySelectorAll(Selector.ITEM)):[];
      returnthis._items.indexOf(element);
    };

    _proto._getItemByDirection=function_getItemByDirection(direction,activeElement){
      varisNextDirection=direction===Direction.NEXT;
      varisPrevDirection=direction===Direction.PREV;

      varactiveIndex=this._getItemIndex(activeElement);

      varlastItemIndex=this._items.length-1;
      varisGoingToWrap=isPrevDirection&&activeIndex===0||isNextDirection&&activeIndex===lastItemIndex;

      if(isGoingToWrap&&!this._config.wrap){
        returnactiveElement;
      }

      vardelta=direction===Direction.PREV?-1:1;
      varitemIndex=(activeIndex+delta)%this._items.length;
      returnitemIndex===-1?this._items[this._items.length-1]:this._items[itemIndex];
    };

    _proto._triggerSlideEvent=function_triggerSlideEvent(relatedTarget,eventDirectionName){
      vartargetIndex=this._getItemIndex(relatedTarget);

      varfromIndex=this._getItemIndex(this._element.querySelector(Selector.ACTIVE_ITEM));

      varslideEvent=$.Event(Event.SLIDE,{
        relatedTarget:relatedTarget,
        direction:eventDirectionName,
        from:fromIndex,
        to:targetIndex
      });
      $(this._element).trigger(slideEvent);
      returnslideEvent;
    };

    _proto._setActiveIndicatorElement=function_setActiveIndicatorElement(element){
      if(this._indicatorsElement){
        varindicators=[].slice.call(this._indicatorsElement.querySelectorAll(Selector.ACTIVE));
        $(indicators).removeClass(ClassName.ACTIVE);

        varnextIndicator=this._indicatorsElement.children[this._getItemIndex(element)];

        if(nextIndicator){
          $(nextIndicator).addClass(ClassName.ACTIVE);
        }
      }
    };

    _proto._slide=function_slide(direction,element){
      var_this4=this;

      varactiveElement=this._element.querySelector(Selector.ACTIVE_ITEM);

      varactiveElementIndex=this._getItemIndex(activeElement);

      varnextElement=element||activeElement&&this._getItemByDirection(direction,activeElement);

      varnextElementIndex=this._getItemIndex(nextElement);

      varisCycling=Boolean(this._interval);
      vardirectionalClassName;
      varorderClassName;
      vareventDirectionName;

      if(direction===Direction.NEXT){
        directionalClassName=ClassName.LEFT;
        orderClassName=ClassName.NEXT;
        eventDirectionName=Direction.LEFT;
      }else{
        directionalClassName=ClassName.RIGHT;
        orderClassName=ClassName.PREV;
        eventDirectionName=Direction.RIGHT;
      }

      if(nextElement&&$(nextElement).hasClass(ClassName.ACTIVE)){
        this._isSliding=false;
        return;
      }

      varslideEvent=this._triggerSlideEvent(nextElement,eventDirectionName);

      if(slideEvent.isDefaultPrevented()){
        return;
      }

      if(!activeElement||!nextElement){
        //Someweirdnessishappening,sowebail
        return;
      }

      this._isSliding=true;

      if(isCycling){
        this.pause();
      }

      this._setActiveIndicatorElement(nextElement);

      varslidEvent=$.Event(Event.SLID,{
        relatedTarget:nextElement,
        direction:eventDirectionName,
        from:activeElementIndex,
        to:nextElementIndex
      });

      if($(this._element).hasClass(ClassName.SLIDE)){
        $(nextElement).addClass(orderClassName);
        Util.reflow(nextElement);
        $(activeElement).addClass(directionalClassName);
        $(nextElement).addClass(directionalClassName);
        varnextElementInterval=parseInt(nextElement.getAttribute('data-interval'),10);

        if(nextElementInterval){
          this._config.defaultInterval=this._config.defaultInterval||this._config.interval;
          this._config.interval=nextElementInterval;
        }else{
          this._config.interval=this._config.defaultInterval||this._config.interval;
        }

        vartransitionDuration=Util.getTransitionDurationFromElement(activeElement);
        $(activeElement).one(Util.TRANSITION_END,function(){
          $(nextElement).removeClass(directionalClassName+""+orderClassName).addClass(ClassName.ACTIVE);
          $(activeElement).removeClass(ClassName.ACTIVE+""+orderClassName+""+directionalClassName);
          _this4._isSliding=false;
          setTimeout(function(){
            return$(_this4._element).trigger(slidEvent);
          },0);
        }).emulateTransitionEnd(transitionDuration);
      }else{
        $(activeElement).removeClass(ClassName.ACTIVE);
        $(nextElement).addClass(ClassName.ACTIVE);
        this._isSliding=false;
        $(this._element).trigger(slidEvent);
      }

      if(isCycling){
        this.cycle();
      }
    }//Static
    ;

    Carousel._jQueryInterface=function_jQueryInterface(config){
      returnthis.each(function(){
        vardata=$(this).data(DATA_KEY);

        var_config=_objectSpread({},Default,$(this).data());

        if(typeofconfig==='object'){
          _config=_objectSpread({},_config,config);
        }

        varaction=typeofconfig==='string'?config:_config.slide;

        if(!data){
          data=newCarousel(this,_config);
          $(this).data(DATA_KEY,data);
        }

        if(typeofconfig==='number'){
          data.to(config);
        }elseif(typeofaction==='string'){
          if(typeofdata[action]==='undefined'){
            thrownewTypeError("Nomethodnamed\""+action+"\"");
          }

          data[action]();
        }elseif(_config.interval&&_config.ride){
          data.pause();
          data.cycle();
        }
      });
    };

    Carousel._dataApiClickHandler=function_dataApiClickHandler(event){
      varselector=Util.getSelectorFromElement(this);

      if(!selector){
        return;
      }

      vartarget=$(selector)[0];

      if(!target||!$(target).hasClass(ClassName.CAROUSEL)){
        return;
      }

      varconfig=_objectSpread({},$(target).data(),$(this).data());

      varslideIndex=this.getAttribute('data-slide-to');

      if(slideIndex){
        config.interval=false;
      }

      Carousel._jQueryInterface.call($(target),config);

      if(slideIndex){
        $(target).data(DATA_KEY).to(slideIndex);
      }

      event.preventDefault();
    };

    _createClass(Carousel,null,[{
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

    returnCarousel;
  }();
  /**
   *------------------------------------------------------------------------
   *DataApiimplementation
   *------------------------------------------------------------------------
   */


  $(document).on(Event.CLICK_DATA_API,Selector.DATA_SLIDE,Carousel._dataApiClickHandler);
  $(window).on(Event.LOAD_DATA_API,function(){
    varcarousels=[].slice.call(document.querySelectorAll(Selector.DATA_RIDE));

    for(vari=0,len=carousels.length;i<len;i++){
      var$carousel=$(carousels[i]);

      Carousel._jQueryInterface.call($carousel,$carousel.data());
    }
  });
  /**
   *------------------------------------------------------------------------
   *jQuery
   *------------------------------------------------------------------------
   */

  $.fn[NAME]=Carousel._jQueryInterface;
  $.fn[NAME].Constructor=Carousel;

  $.fn[NAME].noConflict=function(){
    $.fn[NAME]=JQUERY_NO_CONFLICT;
    returnCarousel._jQueryInterface;
  };

  returnCarousel;

}));
