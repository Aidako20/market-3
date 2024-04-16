/*!
  *Bootstrapbutton.jsv4.3.1(https://getbootstrap.com/)
  *Copyright2011-2019TheBootstrapAuthors(https://github.com/twbs/bootstrap/graphs/contributors)
  *LicensedunderMIT(https://github.com/twbs/bootstrap/blob/master/LICENSE)
  */
(function(global,factory){
  typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory(require('jquery')):
  typeofdefine==='function'&&define.amd?define(['jquery'],factory):
  (global=global||self,global.Button=factory(global.jQuery));
}(this,function($){'usestrict';

  $=$&&$.hasOwnProperty('default')?$['default']:$;

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

  varNAME='button';
  varVERSION='4.3.1';
  varDATA_KEY='bs.button';
  varEVENT_KEY="."+DATA_KEY;
  varDATA_API_KEY='.data-api';
  varJQUERY_NO_CONFLICT=$.fn[NAME];
  varClassName={
    ACTIVE:'active',
    BUTTON:'btn',
    FOCUS:'focus'
  };
  varSelector={
    DATA_TOGGLE_CARROT:'[data-toggle^="button"]',
    DATA_TOGGLE:'[data-toggle="buttons"]',
    INPUT:'input:not([type="hidden"])',
    ACTIVE:'.active',
    BUTTON:'.btn'
  };
  varEvent={
    CLICK_DATA_API:"click"+EVENT_KEY+DATA_API_KEY,
    FOCUS_BLUR_DATA_API:"focus"+EVENT_KEY+DATA_API_KEY+""+("blur"+EVENT_KEY+DATA_API_KEY)
    /**
     *------------------------------------------------------------------------
     *ClassDefinition
     *------------------------------------------------------------------------
     */

  };

  varButton=
  /*#__PURE__*/
  function(){
    functionButton(element){
      this._element=element;
    }//Getters


    var_proto=Button.prototype;

    //Public
    _proto.toggle=functiontoggle(){
      vartriggerChangeEvent=true;
      varaddAriaPressed=true;
      varrootElement=$(this._element).closest(Selector.DATA_TOGGLE)[0];

      if(rootElement){
        varinput=this._element.querySelector(Selector.INPUT);

        if(input){
          if(input.type==='radio'){
            if(input.checked&&this._element.classList.contains(ClassName.ACTIVE)){
              triggerChangeEvent=false;
            }else{
              varactiveElement=rootElement.querySelector(Selector.ACTIVE);

              if(activeElement){
                $(activeElement).removeClass(ClassName.ACTIVE);
              }
            }
          }

          if(triggerChangeEvent){
            if(input.hasAttribute('disabled')||rootElement.hasAttribute('disabled')||input.classList.contains('disabled')||rootElement.classList.contains('disabled')){
              return;
            }

            input.checked=!this._element.classList.contains(ClassName.ACTIVE);
            $(input).trigger('change');
          }

          input.focus();
          addAriaPressed=false;
        }
      }

      if(addAriaPressed){
        this._element.setAttribute('aria-pressed',!this._element.classList.contains(ClassName.ACTIVE));
      }

      if(triggerChangeEvent){
        $(this._element).toggleClass(ClassName.ACTIVE);
      }
    };

    _proto.dispose=functiondispose(){
      $.removeData(this._element,DATA_KEY);
      this._element=null;
    }//Static
    ;

    Button._jQueryInterface=function_jQueryInterface(config){
      returnthis.each(function(){
        vardata=$(this).data(DATA_KEY);

        if(!data){
          data=newButton(this);
          $(this).data(DATA_KEY,data);
        }

        if(config==='toggle'){
          data[config]();
        }
      });
    };

    _createClass(Button,null,[{
      key:"VERSION",
      get:functionget(){
        returnVERSION;
      }
    }]);

    returnButton;
  }();
  /**
   *------------------------------------------------------------------------
   *DataApiimplementation
   *------------------------------------------------------------------------
   */


  $(document).on(Event.CLICK_DATA_API,Selector.DATA_TOGGLE_CARROT,function(event){
    event.preventDefault();
    varbutton=event.target;

    if(!$(button).hasClass(ClassName.BUTTON)){
      button=$(button).closest(Selector.BUTTON);
    }

    Button._jQueryInterface.call($(button),'toggle');
  }).on(Event.FOCUS_BLUR_DATA_API,Selector.DATA_TOGGLE_CARROT,function(event){
    varbutton=$(event.target).closest(Selector.BUTTON)[0];
    $(button).toggleClass(ClassName.FOCUS,/^focus(in)?$/.test(event.type));
  });
  /**
   *------------------------------------------------------------------------
   *jQuery
   *------------------------------------------------------------------------
   */

  $.fn[NAME]=Button._jQueryInterface;
  $.fn[NAME].Constructor=Button;

  $.fn[NAME].noConflict=function(){
    $.fn[NAME]=JQUERY_NO_CONFLICT;
    returnButton._jQueryInterface;
  };

  returnButton;

}));
