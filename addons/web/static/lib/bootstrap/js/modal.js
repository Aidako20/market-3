/*!
  *Bootstrapmodal.jsv4.3.1(https://getbootstrap.com/)
  *Copyright2011-2019TheBootstrapAuthors(https://github.com/twbs/bootstrap/graphs/contributors)
  *LicensedunderMIT(https://github.com/twbs/bootstrap/blob/master/LICENSE)
  */
(function(global,factory){
  typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory(require('jquery'),require('./util.js')):
  typeofdefine==='function'&&define.amd?define(['jquery','./util.js'],factory):
  (global=global||self,global.Modal=factory(global.jQuery,global.Util));
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

  varNAME='modal';
  varVERSION='4.3.1';
  varDATA_KEY='bs.modal';
  varEVENT_KEY="."+DATA_KEY;
  varDATA_API_KEY='.data-api';
  varJQUERY_NO_CONFLICT=$.fn[NAME];
  varESCAPE_KEYCODE=27;//KeyboardEvent.whichvalueforEscape(Esc)key

  varDefault={
    backdrop:true,
    keyboard:true,
    focus:true,
    show:true
  };
  varDefaultType={
    backdrop:'(boolean|string)',
    keyboard:'boolean',
    focus:'boolean',
    show:'boolean'
  };
  varEvent={
    HIDE:"hide"+EVENT_KEY,
    HIDDEN:"hidden"+EVENT_KEY,
    SHOW:"show"+EVENT_KEY,
    SHOWN:"shown"+EVENT_KEY,
    FOCUSIN:"focusin"+EVENT_KEY,
    RESIZE:"resize"+EVENT_KEY,
    CLICK_DISMISS:"click.dismiss"+EVENT_KEY,
    KEYDOWN_DISMISS:"keydown.dismiss"+EVENT_KEY,
    MOUSEUP_DISMISS:"mouseup.dismiss"+EVENT_KEY,
    MOUSEDOWN_DISMISS:"mousedown.dismiss"+EVENT_KEY,
    CLICK_DATA_API:"click"+EVENT_KEY+DATA_API_KEY
  };
  varClassName={
    SCROLLABLE:'modal-dialog-scrollable',
    SCROLLBAR_MEASURER:'modal-scrollbar-measure',
    BACKDROP:'modal-backdrop',
    OPEN:'modal-open',
    FADE:'fade',
    SHOW:'show'
  };
  varSelector={
    DIALOG:'.modal-dialog',
    MODAL_BODY:'.modal-body',
    DATA_TOGGLE:'[data-toggle="modal"]',
    DATA_DISMISS:'[data-dismiss="modal"]',
    FIXED_CONTENT:'.fixed-top,.fixed-bottom,.is-fixed,.sticky-top',
    STICKY_CONTENT:'.sticky-top'
    /**
     *------------------------------------------------------------------------
     *ClassDefinition
     *------------------------------------------------------------------------
     */

  };

  varModal=
  /*#__PURE__*/
  function(){
    functionModal(element,config){
      this._config=this._getConfig(config);
      this._element=element;
      this._dialog=element.querySelector(Selector.DIALOG);
      this._backdrop=null;
      this._isShown=false;
      this._isBodyOverflowing=false;
      this._ignoreBackdropClick=false;
      this._isTransitioning=false;
      this._scrollbarWidth=0;
    }//Getters


    var_proto=Modal.prototype;

    //Public
    _proto.toggle=functiontoggle(relatedTarget){
      returnthis._isShown?this.hide():this.show(relatedTarget);
    };

    _proto.show=functionshow(relatedTarget){
      var_this=this;

      if(this._isShown||this._isTransitioning){
        return;
      }

      if($(this._element).hasClass(ClassName.FADE)){
        this._isTransitioning=true;
      }

      varshowEvent=$.Event(Event.SHOW,{
        relatedTarget:relatedTarget
      });
      $(this._element).trigger(showEvent);

      if(this._isShown||showEvent.isDefaultPrevented()){
        return;
      }

      this._isShown=true;

      this._checkScrollbar();

      this._setScrollbar();

      this._adjustDialog();

      this._setEscapeEvent();

      this._setResizeEvent();

      $(this._element).on(Event.CLICK_DISMISS,Selector.DATA_DISMISS,function(event){
        return_this.hide(event);
      });
      $(this._dialog).on(Event.MOUSEDOWN_DISMISS,function(){
        $(_this._element).one(Event.MOUSEUP_DISMISS,function(event){
          if($(event.target).is(_this._element)){
            _this._ignoreBackdropClick=true;
          }
        });
      });

      this._showBackdrop(function(){
        return_this._showElement(relatedTarget);
      });
    };

    _proto.hide=functionhide(event){
      var_this2=this;

      if(event){
        event.preventDefault();
      }

      if(!this._isShown||this._isTransitioning){
        return;
      }

      varhideEvent=$.Event(Event.HIDE);
      $(this._element).trigger(hideEvent);

      if(!this._isShown||hideEvent.isDefaultPrevented()){
        return;
      }

      this._isShown=false;
      vartransition=$(this._element).hasClass(ClassName.FADE);

      if(transition){
        this._isTransitioning=true;
      }

      this._setEscapeEvent();

      this._setResizeEvent();

      $(document).off(Event.FOCUSIN);
      $(this._element).removeClass(ClassName.SHOW);
      $(this._element).off(Event.CLICK_DISMISS);
      $(this._dialog).off(Event.MOUSEDOWN_DISMISS);

      if(transition){
        vartransitionDuration=Util.getTransitionDurationFromElement(this._element);
        $(this._element).one(Util.TRANSITION_END,function(event){
          return_this2._hideModal(event);
        }).emulateTransitionEnd(transitionDuration);
      }else{
        this._hideModal();
      }
    };

    _proto.dispose=functiondispose(){
      [window,this._element,this._dialog].forEach(function(htmlElement){
        return$(htmlElement).off(EVENT_KEY);
      });
      /**
       *`document`has2events`Event.FOCUSIN`and`Event.CLICK_DATA_API`
       *Donotmove`document`in`htmlElements`array
       *Itwillremove`Event.CLICK_DATA_API`eventthatshouldremain
       */

      $(document).off(Event.FOCUSIN);
      $.removeData(this._element,DATA_KEY);
      this._config=null;
      this._element=null;
      this._dialog=null;
      this._backdrop=null;
      this._isShown=null;
      this._isBodyOverflowing=null;
      this._ignoreBackdropClick=null;
      this._isTransitioning=null;
      this._scrollbarWidth=null;
    };

    _proto.handleUpdate=functionhandleUpdate(){
      this._adjustDialog();
    }//Private
    ;

    _proto._getConfig=function_getConfig(config){
      config=_objectSpread({},Default,config);
      Util.typeCheckConfig(NAME,config,DefaultType);
      returnconfig;
    };

    _proto._showElement=function_showElement(relatedTarget){
      var_this3=this;

      vartransition=$(this._element).hasClass(ClassName.FADE);

      if(!this._element.parentNode||this._element.parentNode.nodeType!==Node.ELEMENT_NODE){
        //Don'tmovemodal'sDOMposition
        document.body.appendChild(this._element);
      }

      this._element.style.display='block';

      this._element.removeAttribute('aria-hidden');

      this._element.setAttribute('aria-modal',true);

      if($(this._dialog).hasClass(ClassName.SCROLLABLE)){
        this._dialog.querySelector(Selector.MODAL_BODY).scrollTop=0;
      }else{
        this._element.scrollTop=0;
      }

      if(transition){
        Util.reflow(this._element);
      }

      $(this._element).addClass(ClassName.SHOW);

      if(this._config.focus){
        this._enforceFocus();
      }

      varshownEvent=$.Event(Event.SHOWN,{
        relatedTarget:relatedTarget
      });

      vartransitionComplete=functiontransitionComplete(){
        if(_this3._config.focus){
          _this3._element.focus();
        }

        _this3._isTransitioning=false;
        $(_this3._element).trigger(shownEvent);
      };

      if(transition){
        vartransitionDuration=Util.getTransitionDurationFromElement(this._dialog);
        $(this._dialog).one(Util.TRANSITION_END,transitionComplete).emulateTransitionEnd(transitionDuration);
      }else{
        transitionComplete();
      }
    };

    _proto._enforceFocus=function_enforceFocus(){
      var_this4=this;

      $(document).off(Event.FOCUSIN)//Guardagainstinfinitefocusloop
      .on(Event.FOCUSIN,function(event){
        if(document!==event.target&&_this4._element!==event.target&&$(_this4._element).has(event.target).length===0){
          _this4._element.focus();
        }
      });
    };

    _proto._setEscapeEvent=function_setEscapeEvent(){
      var_this5=this;

      if(this._isShown&&this._config.keyboard){
        $(this._element).on(Event.KEYDOWN_DISMISS,function(event){
          if(event.which===ESCAPE_KEYCODE){
            event.preventDefault();

            _this5.hide();
          }
        });
      }elseif(!this._isShown){
        $(this._element).off(Event.KEYDOWN_DISMISS);
      }
    };

    _proto._setResizeEvent=function_setResizeEvent(){
      var_this6=this;

      if(this._isShown){
        $(window).on(Event.RESIZE,function(event){
          return_this6.handleUpdate(event);
        });
      }else{
        $(window).off(Event.RESIZE);
      }
    };

    _proto._hideModal=function_hideModal(){
      var_this7=this;

      this._element.style.display='none';

      this._element.setAttribute('aria-hidden',true);

      this._element.removeAttribute('aria-modal');

      this._isTransitioning=false;

      this._showBackdrop(function(){
        $(document.body).removeClass(ClassName.OPEN);

        _this7._resetAdjustments();

        _this7._resetScrollbar();

        $(_this7._element).trigger(Event.HIDDEN);
      });
    };

    _proto._removeBackdrop=function_removeBackdrop(){
      if(this._backdrop){
        $(this._backdrop).remove();
        this._backdrop=null;
      }
    };

    _proto._showBackdrop=function_showBackdrop(callback){
      var_this8=this;

      varanimate=$(this._element).hasClass(ClassName.FADE)?ClassName.FADE:'';

      if(this._isShown&&this._config.backdrop){
        this._backdrop=document.createElement('div');
        this._backdrop.className=ClassName.BACKDROP;

        if(animate){
          this._backdrop.classList.add(animate);
        }

        $(this._backdrop).appendTo(document.body);
        $(this._element).on(Event.CLICK_DISMISS,function(event){
          if(_this8._ignoreBackdropClick){
            _this8._ignoreBackdropClick=false;
            return;
          }

          if(event.target!==event.currentTarget){
            return;
          }

          if(_this8._config.backdrop==='static'){
            _this8._element.focus();
          }else{
            _this8.hide();
          }
        });

        if(animate){
          Util.reflow(this._backdrop);
        }

        $(this._backdrop).addClass(ClassName.SHOW);

        if(!callback){
          return;
        }

        if(!animate){
          callback();
          return;
        }

        varbackdropTransitionDuration=Util.getTransitionDurationFromElement(this._backdrop);
        $(this._backdrop).one(Util.TRANSITION_END,callback).emulateTransitionEnd(backdropTransitionDuration);
      }elseif(!this._isShown&&this._backdrop){
        $(this._backdrop).removeClass(ClassName.SHOW);

        varcallbackRemove=functioncallbackRemove(){
          _this8._removeBackdrop();

          if(callback){
            callback();
          }
        };

        if($(this._element).hasClass(ClassName.FADE)){
          var_backdropTransitionDuration=Util.getTransitionDurationFromElement(this._backdrop);

          $(this._backdrop).one(Util.TRANSITION_END,callbackRemove).emulateTransitionEnd(_backdropTransitionDuration);
        }else{
          callbackRemove();
        }
      }elseif(callback){
        callback();
      }
    }//----------------------------------------------------------------------
    //thefollowingmethodsareusedtohandleoverflowingmodals
    //todo(fat):theseshouldprobablyberefactoredoutofmodal.js
    //----------------------------------------------------------------------
    ;

    _proto._adjustDialog=function_adjustDialog(){
      varisModalOverflowing=this._element.scrollHeight>document.documentElement.clientHeight;

      if(!this._isBodyOverflowing&&isModalOverflowing){
        this._element.style.paddingLeft=this._scrollbarWidth+"px";
      }

      if(this._isBodyOverflowing&&!isModalOverflowing){
        this._element.style.paddingRight=this._scrollbarWidth+"px";
      }
    };

    _proto._resetAdjustments=function_resetAdjustments(){
      this._element.style.paddingLeft='';
      this._element.style.paddingRight='';
    };

    _proto._checkScrollbar=function_checkScrollbar(){
      varrect=document.body.getBoundingClientRect();
      this._isBodyOverflowing=rect.left+rect.right<window.innerWidth;
      this._scrollbarWidth=this._getScrollbarWidth();
    };

    _proto._setScrollbar=function_setScrollbar(){
      var_this9=this;

      if(this._isBodyOverflowing){
        //Note:DOMNode.style.paddingRightreturnstheactualvalueor''ifnotset
        //  while$(DOMNode).css('padding-right')returnsthecalculatedvalueor0ifnotset
        varfixedContent=[].slice.call(document.querySelectorAll(Selector.FIXED_CONTENT));
        varstickyContent=[].slice.call(document.querySelectorAll(Selector.STICKY_CONTENT));//Adjustfixedcontentpadding

        $(fixedContent).each(function(index,element){
          varactualPadding=element.style.paddingRight;
          varcalculatedPadding=$(element).css('padding-right');
          $(element).data('padding-right',actualPadding).css('padding-right',parseFloat(calculatedPadding)+_this9._scrollbarWidth+"px");
        });//Adjuststickycontentmargin

        $(stickyContent).each(function(index,element){
          varactualMargin=element.style.marginRight;
          varcalculatedMargin=$(element).css('margin-right');
          $(element).data('margin-right',actualMargin).css('margin-right',parseFloat(calculatedMargin)-_this9._scrollbarWidth+"px");
        });//Adjustbodypadding

        varactualPadding=document.body.style.paddingRight;
        varcalculatedPadding=$(document.body).css('padding-right');
        $(document.body).data('padding-right',actualPadding).css('padding-right',parseFloat(calculatedPadding)+this._scrollbarWidth+"px");
      }

      $(document.body).addClass(ClassName.OPEN);
    };

    _proto._resetScrollbar=function_resetScrollbar(){
      //Restorefixedcontentpadding
      varfixedContent=[].slice.call(document.querySelectorAll(Selector.FIXED_CONTENT));
      $(fixedContent).each(function(index,element){
        varpadding=$(element).data('padding-right');
        $(element).removeData('padding-right');
        element.style.paddingRight=padding?padding:'';
      });//Restorestickycontent

      varelements=[].slice.call(document.querySelectorAll(""+Selector.STICKY_CONTENT));
      $(elements).each(function(index,element){
        varmargin=$(element).data('margin-right');

        if(typeofmargin!=='undefined'){
          $(element).css('margin-right',margin).removeData('margin-right');
        }
      });//Restorebodypadding

      varpadding=$(document.body).data('padding-right');
      $(document.body).removeData('padding-right');
      document.body.style.paddingRight=padding?padding:'';
    };

    _proto._getScrollbarWidth=function_getScrollbarWidth(){
      //thxd.walsh
      varscrollDiv=document.createElement('div');
      scrollDiv.className=ClassName.SCROLLBAR_MEASURER;
      document.body.appendChild(scrollDiv);
      varscrollbarWidth=scrollDiv.getBoundingClientRect().width-scrollDiv.clientWidth;
      document.body.removeChild(scrollDiv);
      returnscrollbarWidth;
    }//Static
    ;

    Modal._jQueryInterface=function_jQueryInterface(config,relatedTarget){
      returnthis.each(function(){
        vardata=$(this).data(DATA_KEY);

        var_config=_objectSpread({},Default,$(this).data(),typeofconfig==='object'&&config?config:{});

        if(!data){
          data=newModal(this,_config);
          $(this).data(DATA_KEY,data);
        }

        if(typeofconfig==='string'){
          if(typeofdata[config]==='undefined'){
            thrownewTypeError("Nomethodnamed\""+config+"\"");
          }

          data[config](relatedTarget);
        }elseif(_config.show){
          data.show(relatedTarget);
        }
      });
    };

    _createClass(Modal,null,[{
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

    returnModal;
  }();
  /**
   *------------------------------------------------------------------------
   *DataApiimplementation
   *------------------------------------------------------------------------
   */


  $(document).on(Event.CLICK_DATA_API,Selector.DATA_TOGGLE,function(event){
    var_this10=this;

    vartarget;
    varselector=Util.getSelectorFromElement(this);

    if(selector){
      target=document.querySelector(selector);
    }

    varconfig=$(target).data(DATA_KEY)?'toggle':_objectSpread({},$(target).data(),$(this).data());

    if(this.tagName==='A'||this.tagName==='AREA'){
      event.preventDefault();
    }

    var$target=$(target).one(Event.SHOW,function(showEvent){
      if(showEvent.isDefaultPrevented()){
        //Onlyregisterfocusrestorerifmodalwillactuallygetshown
        return;
      }

      $target.one(Event.HIDDEN,function(){
        if($(_this10).is(':visible')){
          _this10.focus();
        }
      });
    });

    Modal._jQueryInterface.call($(target),config,this);
  });
  /**
   *------------------------------------------------------------------------
   *jQuery
   *------------------------------------------------------------------------
   */

  $.fn[NAME]=Modal._jQueryInterface;
  $.fn[NAME].Constructor=Modal;

  $.fn[NAME].noConflict=function(){
    $.fn[NAME]=JQUERY_NO_CONFLICT;
    returnModal._jQueryInterface;
  };

  returnModal;

}));
