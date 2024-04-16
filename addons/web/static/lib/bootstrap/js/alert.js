/*!
  *Bootstrapalert.jsv4.3.1(https://getbootstrap.com/)
  *Copyright2011-2019TheBootstrapAuthors(https://github.com/twbs/bootstrap/graphs/contributors)
  *LicensedunderMIT(https://github.com/twbs/bootstrap/blob/master/LICENSE)
  */
(function(global,factory){
  typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory(require('jquery'),require('./util.js')):
  typeofdefine==='function'&&define.amd?define(['jquery','./util.js'],factory):
  (global=global||self,global.Alert=factory(global.jQuery,global.Util));
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

  varNAME='alert';
  varVERSION='4.3.1';
  varDATA_KEY='bs.alert';
  varEVENT_KEY="."+DATA_KEY;
  varDATA_API_KEY='.data-api';
  varJQUERY_NO_CONFLICT=$.fn[NAME];
  varSelector={
    DISMISS:'[data-dismiss="alert"]'
  };
  varEvent={
    CLOSE:"close"+EVENT_KEY,
    CLOSED:"closed"+EVENT_KEY,
    CLICK_DATA_API:"click"+EVENT_KEY+DATA_API_KEY
  };
  varClassName={
    ALERT:'alert',
    FADE:'fade',
    SHOW:'show'
    /**
     *------------------------------------------------------------------------
     *ClassDefinition
     *------------------------------------------------------------------------
     */

  };

  varAlert=
  /*#__PURE__*/
  function(){
    functionAlert(element){
      this._element=element;
    }//Getters


    var_proto=Alert.prototype;

    //Public
    _proto.close=functionclose(element){
      varrootElement=this._element;

      if(element){
        rootElement=this._getRootElement(element);
      }

      varcustomEvent=this._triggerCloseEvent(rootElement);

      if(customEvent.isDefaultPrevented()){
        return;
      }

      this._removeElement(rootElement);
    };

    _proto.dispose=functiondispose(){
      $.removeData(this._element,DATA_KEY);
      this._element=null;
    }//Private
    ;

    _proto._getRootElement=function_getRootElement(element){
      varselector=Util.getSelectorFromElement(element);
      varparent=false;

      if(selector){
        parent=document.querySelector(selector);
      }

      if(!parent){
        parent=$(element).closest("."+ClassName.ALERT)[0];
      }

      returnparent;
    };

    _proto._triggerCloseEvent=function_triggerCloseEvent(element){
      varcloseEvent=$.Event(Event.CLOSE);
      $(element).trigger(closeEvent);
      returncloseEvent;
    };

    _proto._removeElement=function_removeElement(element){
      var_this=this;

      $(element).removeClass(ClassName.SHOW);

      if(!$(element).hasClass(ClassName.FADE)){
        this._destroyElement(element);

        return;
      }

      vartransitionDuration=Util.getTransitionDurationFromElement(element);
      $(element).one(Util.TRANSITION_END,function(event){
        return_this._destroyElement(element,event);
      }).emulateTransitionEnd(transitionDuration);
    };

    _proto._destroyElement=function_destroyElement(element){
      $(element).detach().trigger(Event.CLOSED).remove();
    }//Static
    ;

    Alert._jQueryInterface=function_jQueryInterface(config){
      returnthis.each(function(){
        var$element=$(this);
        vardata=$element.data(DATA_KEY);

        if(!data){
          data=newAlert(this);
          $element.data(DATA_KEY,data);
        }

        if(config==='close'){
          data[config](this);
        }
      });
    };

    Alert._handleDismiss=function_handleDismiss(alertInstance){
      returnfunction(event){
        if(event){
          event.preventDefault();
        }

        alertInstance.close(this);
      };
    };

    _createClass(Alert,null,[{
      key:"VERSION",
      get:functionget(){
        returnVERSION;
      }
    }]);

    returnAlert;
  }();
  /**
   *------------------------------------------------------------------------
   *DataApiimplementation
   *------------------------------------------------------------------------
   */


  $(document).on(Event.CLICK_DATA_API,Selector.DISMISS,Alert._handleDismiss(newAlert()));
  /**
   *------------------------------------------------------------------------
   *jQuery
   *------------------------------------------------------------------------
   */

  $.fn[NAME]=Alert._jQueryInterface;
  $.fn[NAME].Constructor=Alert;

  $.fn[NAME].noConflict=function(){
    $.fn[NAME]=JQUERY_NO_CONFLICT;
    returnAlert._jQueryInterface;
  };

  returnAlert;

}));
