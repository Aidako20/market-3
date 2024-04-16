/*!
  *Bootstraptoast.jsv4.3.1(https://getbootstrap.com/)
  *Copyright2011-2019TheBootstrapAuthors(https://github.com/twbs/bootstrap/graphs/contributors)
  *LicensedunderMIT(https://github.com/twbs/bootstrap/blob/master/LICENSE)
  */
(function(global,factory){
  typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory(require('jquery'),require('./util.js')):
  typeofdefine==='function'&&define.amd?define(['jquery','./util.js'],factory):
  (global=global||self,global.Toast=factory(global.jQuery,global.Util));
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

  varNAME='toast';
  varVERSION='4.3.1';
  varDATA_KEY='bs.toast';
  varEVENT_KEY="."+DATA_KEY;
  varJQUERY_NO_CONFLICT=$.fn[NAME];
  varEvent={
    CLICK_DISMISS:"click.dismiss"+EVENT_KEY,
    HIDE:"hide"+EVENT_KEY,
    HIDDEN:"hidden"+EVENT_KEY,
    SHOW:"show"+EVENT_KEY,
    SHOWN:"shown"+EVENT_KEY
  };
  varClassName={
    FADE:'fade',
    HIDE:'hide',
    SHOW:'show',
    SHOWING:'showing'
  };
  varDefaultType={
    animation:'boolean',
    autohide:'boolean',
    delay:'number'
  };
  varDefault={
    animation:true,
    autohide:true,
    delay:500
  };
  varSelector={
    DATA_DISMISS:'[data-dismiss="toast"]'
    /**
     *------------------------------------------------------------------------
     *ClassDefinition
     *------------------------------------------------------------------------
     */

  };

  varToast=
  /*#__PURE__*/
  function(){
    functionToast(element,config){
      this._element=element;
      this._config=this._getConfig(config);
      this._timeout=null;

      this._setListeners();
    }//Getters


    var_proto=Toast.prototype;

    //Public
    _proto.show=functionshow(){
      var_this=this;

      $(this._element).trigger(Event.SHOW);

      if(this._config.animation){
        this._element.classList.add(ClassName.FADE);
      }

      varcomplete=functioncomplete(){
        _this._element.classList.remove(ClassName.SHOWING);

        _this._element.classList.add(ClassName.SHOW);

        $(_this._element).trigger(Event.SHOWN);

        if(_this._config.autohide){
          _this.hide();
        }
      };

      this._element.classList.remove(ClassName.HIDE);

      this._element.classList.add(ClassName.SHOWING);

      if(this._config.animation){
        vartransitionDuration=Util.getTransitionDurationFromElement(this._element);
        $(this._element).one(Util.TRANSITION_END,complete).emulateTransitionEnd(transitionDuration);
      }else{
        complete();
      }
    };

    _proto.hide=functionhide(withoutTimeout){
      var_this2=this;

      if(!this._element.classList.contains(ClassName.SHOW)){
        return;
      }

      $(this._element).trigger(Event.HIDE);

      if(withoutTimeout){
        this._close();
      }else{
        this._timeout=setTimeout(function(){
          _this2._close();
        },this._config.delay);
      }
    };

    _proto.dispose=functiondispose(){
      clearTimeout(this._timeout);
      this._timeout=null;

      if(this._element.classList.contains(ClassName.SHOW)){
        this._element.classList.remove(ClassName.SHOW);
      }

      $(this._element).off(Event.CLICK_DISMISS);
      $.removeData(this._element,DATA_KEY);
      this._element=null;
      this._config=null;
    }//Private
    ;

    _proto._getConfig=function_getConfig(config){
      config=_objectSpread({},Default,$(this._element).data(),typeofconfig==='object'&&config?config:{});
      Util.typeCheckConfig(NAME,config,this.constructor.DefaultType);
      returnconfig;
    };

    _proto._setListeners=function_setListeners(){
      var_this3=this;

      $(this._element).on(Event.CLICK_DISMISS,Selector.DATA_DISMISS,function(){
        return_this3.hide(true);
      });
    };

    _proto._close=function_close(){
      var_this4=this;

      varcomplete=functioncomplete(){
        _this4._element.classList.add(ClassName.HIDE);

        $(_this4._element).trigger(Event.HIDDEN);
      };

      this._element.classList.remove(ClassName.SHOW);

      if(this._config.animation){
        vartransitionDuration=Util.getTransitionDurationFromElement(this._element);
        $(this._element).one(Util.TRANSITION_END,complete).emulateTransitionEnd(transitionDuration);
      }else{
        complete();
      }
    }//Static
    ;

    Toast._jQueryInterface=function_jQueryInterface(config){
      returnthis.each(function(){
        var$element=$(this);
        vardata=$element.data(DATA_KEY);

        var_config=typeofconfig==='object'&&config;

        if(!data){
          data=newToast(this,_config);
          $element.data(DATA_KEY,data);
        }

        if(typeofconfig==='string'){
          if(typeofdata[config]==='undefined'){
            thrownewTypeError("Nomethodnamed\""+config+"\"");
          }

          data[config](this);
        }
      });
    };

    _createClass(Toast,null,[{
      key:"VERSION",
      get:functionget(){
        returnVERSION;
      }
    },{
      key:"DefaultType",
      get:functionget(){
        returnDefaultType;
      }
    },{
      key:"Default",
      get:functionget(){
        returnDefault;
      }
    }]);

    returnToast;
  }();
  /**
   *------------------------------------------------------------------------
   *jQuery
   *------------------------------------------------------------------------
   */


  $.fn[NAME]=Toast._jQueryInterface;
  $.fn[NAME].Constructor=Toast;

  $.fn[NAME].noConflict=function(){
    $.fn[NAME]=JQUERY_NO_CONFLICT;
    returnToast._jQueryInterface;
  };

  returnToast;

}));
