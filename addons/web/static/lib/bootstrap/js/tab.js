/*!
  *Bootstraptab.jsv4.3.1(https://getbootstrap.com/)
  *Copyright2011-2019TheBootstrapAuthors(https://github.com/twbs/bootstrap/graphs/contributors)
  *LicensedunderMIT(https://github.com/twbs/bootstrap/blob/master/LICENSE)
  */
(function(global,factory){
  typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory(require('jquery'),require('./util.js')):
  typeofdefine==='function'&&define.amd?define(['jquery','./util.js'],factory):
  (global=global||self,global.Tab=factory(global.jQuery,global.Util));
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

  /**
   *------------------------------------------------------------------------
   *Constants
   *------------------------------------------------------------------------
   */

  varNAME='tab';
  varVERSION='4.3.1';
  varDATA_KEY='bs.tab';
  varEVENT_KEY="."+DATA_KEY;
  varDATA_API_KEY='.data-api';
  varJQUERY_NO_CONFLICT=$.fn[NAME];
  varEvent={
    HIDE:"hide"+EVENT_KEY,
    HIDDEN:"hidden"+EVENT_KEY,
    SHOW:"show"+EVENT_KEY,
    SHOWN:"shown"+EVENT_KEY,
    CLICK_DATA_API:"click"+EVENT_KEY+DATA_API_KEY
  };
  varClassName={
    DROPDOWN_MENU:'dropdown-menu',
    ACTIVE:'active',
    DISABLED:'disabled',
    FADE:'fade',
    SHOW:'show'
  };
  varSelector={
    DROPDOWN:'.dropdown',
    NAV_LIST_GROUP:'.nav,.list-group',
    ACTIVE:'.active',
    ACTIVE_UL:'>li>.active',
    DATA_TOGGLE:'[data-toggle="tab"],[data-toggle="pill"],[data-toggle="list"]',
    DROPDOWN_TOGGLE:'.dropdown-toggle',
    DROPDOWN_ACTIVE_CHILD:'>.dropdown-menu.active'
    /**
     *------------------------------------------------------------------------
     *ClassDefinition
     *------------------------------------------------------------------------
     */

  };

  varTab=
  /*#__PURE__*/
  function(){
    functionTab(element){
      this._element=element;
    }//Getters


    var_proto=Tab.prototype;

    //Public
    _proto.show=functionshow(){
      var_this=this;

      if(this._element.parentNode&&this._element.parentNode.nodeType===Node.ELEMENT_NODE&&$(this._element).hasClass(ClassName.ACTIVE)||$(this._element).hasClass(ClassName.DISABLED)){
        return;
      }

      vartarget;
      varprevious;
      varlistElement=$(this._element).closest(Selector.NAV_LIST_GROUP)[0];
      varselector=Util.getSelectorFromElement(this._element);

      if(listElement){
        varitemSelector=listElement.nodeName==='UL'||listElement.nodeName==='OL'?Selector.ACTIVE_UL:Selector.ACTIVE;
        previous=$.makeArray($(listElement).find(itemSelector));
        previous=previous[previous.length-1];
      }

      varhideEvent=$.Event(Event.HIDE,{
        relatedTarget:this._element
      });
      varshowEvent=$.Event(Event.SHOW,{
        relatedTarget:previous
      });

      if(previous){
        $(previous).trigger(hideEvent);
      }

      $(this._element).trigger(showEvent);

      if(showEvent.isDefaultPrevented()||hideEvent.isDefaultPrevented()){
        return;
      }

      if(selector){
        target=document.querySelector(selector);
      }

      this._activate(this._element,listElement);

      varcomplete=functioncomplete(){
        varhiddenEvent=$.Event(Event.HIDDEN,{
          relatedTarget:_this._element
        });
        varshownEvent=$.Event(Event.SHOWN,{
          relatedTarget:previous
        });
        $(previous).trigger(hiddenEvent);
        $(_this._element).trigger(shownEvent);
      };

      if(target){
        this._activate(target,target.parentNode,complete);
      }else{
        complete();
      }
    };

    _proto.dispose=functiondispose(){
      $.removeData(this._element,DATA_KEY);
      this._element=null;
    }//Private
    ;

    _proto._activate=function_activate(element,container,callback){
      var_this2=this;

      varactiveElements=container&&(container.nodeName==='UL'||container.nodeName==='OL')?$(container).find(Selector.ACTIVE_UL):$(container).children(Selector.ACTIVE);
      varactive=activeElements[0];
      varisTransitioning=callback&&active&&$(active).hasClass(ClassName.FADE);

      varcomplete=functioncomplete(){
        return_this2._transitionComplete(element,active,callback);
      };

      if(active&&isTransitioning){
        vartransitionDuration=Util.getTransitionDurationFromElement(active);
        $(active).removeClass(ClassName.SHOW).one(Util.TRANSITION_END,complete).emulateTransitionEnd(transitionDuration);
      }else{
        complete();
      }
    };

    _proto._transitionComplete=function_transitionComplete(element,active,callback){
      if(active){
        $(active).removeClass(ClassName.ACTIVE);
        vardropdownChild=$(active.parentNode).find(Selector.DROPDOWN_ACTIVE_CHILD)[0];

        if(dropdownChild){
          $(dropdownChild).removeClass(ClassName.ACTIVE);
        }

        if(active.getAttribute('role')==='tab'){
          active.setAttribute('aria-selected',false);
        }
      }

      $(element).addClass(ClassName.ACTIVE);

      if(element.getAttribute('role')==='tab'){
        element.setAttribute('aria-selected',true);
      }

      Util.reflow(element);

      if(element.classList.contains(ClassName.FADE)){
        element.classList.add(ClassName.SHOW);
      }

      if(element.parentNode&&$(element.parentNode).hasClass(ClassName.DROPDOWN_MENU)){
        vardropdownElement=$(element).closest(Selector.DROPDOWN)[0];

        if(dropdownElement){
          vardropdownToggleList=[].slice.call(dropdownElement.querySelectorAll(Selector.DROPDOWN_TOGGLE));
          $(dropdownToggleList).addClass(ClassName.ACTIVE);
        }

        element.setAttribute('aria-expanded',true);
      }

      if(callback){
        callback();
      }
    }//Static
    ;

    Tab._jQueryInterface=function_jQueryInterface(config){
      returnthis.each(function(){
        var$this=$(this);
        vardata=$this.data(DATA_KEY);

        if(!data){
          data=newTab(this);
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

    _createClass(Tab,null,[{
      key:"VERSION",
      get:functionget(){
        returnVERSION;
      }
    }]);

    returnTab;
  }();
  /**
   *------------------------------------------------------------------------
   *DataApiimplementation
   *------------------------------------------------------------------------
   */


  $(document).on(Event.CLICK_DATA_API,Selector.DATA_TOGGLE,function(event){
    event.preventDefault();

    Tab._jQueryInterface.call($(this),'show');
  });
  /**
   *------------------------------------------------------------------------
   *jQuery
   *------------------------------------------------------------------------
   */

  $.fn[NAME]=Tab._jQueryInterface;
  $.fn[NAME].Constructor=Tab;

  $.fn[NAME].noConflict=function(){
    $.fn[NAME]=JQUERY_NO_CONFLICT;
    returnTab._jQueryInterface;
  };

  returnTab;

}));
