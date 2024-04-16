/*!
  *Bootstrappopover.jsv4.3.1(https://getbootstrap.com/)
  *Copyright2011-2019TheBootstrapAuthors(https://github.com/twbs/bootstrap/graphs/contributors)
  *LicensedunderMIT(https://github.com/twbs/bootstrap/blob/master/LICENSE)
  */
(function(global,factory){
  typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory(require('jquery'),require('./tooltip.js')):
  typeofdefine==='function'&&define.amd?define(['jquery','./tooltip.js'],factory):
  (global=global||self,global.Popover=factory(global.jQuery,global.Tooltip));
}(this,function($,Tooltip){'usestrict';

  $=$&&$.hasOwnProperty('default')?$['default']:$;
  Tooltip=Tooltip&&Tooltip.hasOwnProperty('default')?Tooltip['default']:Tooltip;

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

  function_inheritsLoose(subClass,superClass){
    subClass.prototype=Object.create(superClass.prototype);
    subClass.prototype.constructor=subClass;
    subClass.__proto__=superClass;
  }

  /**
   *------------------------------------------------------------------------
   *Constants
   *------------------------------------------------------------------------
   */

  varNAME='popover';
  varVERSION='4.3.1';
  varDATA_KEY='bs.popover';
  varEVENT_KEY="."+DATA_KEY;
  varJQUERY_NO_CONFLICT=$.fn[NAME];
  varCLASS_PREFIX='bs-popover';
  varBSCLS_PREFIX_REGEX=newRegExp("(^|\\s)"+CLASS_PREFIX+"\\S+",'g');

  varDefault=_objectSpread({},Tooltip.Default,{
    placement:'right',
    trigger:'click',
    content:'',
    template:'<divclass="popover"role="tooltip">'+'<divclass="arrow"></div>'+'<h3class="popover-header"></h3>'+'<divclass="popover-body"></div></div>'
  });

  varDefaultType=_objectSpread({},Tooltip.DefaultType,{
    content:'(string|element|function)'
  });

  varClassName={
    FADE:'fade',
    SHOW:'show'
  };
  varSelector={
    TITLE:'.popover-header',
    CONTENT:'.popover-body'
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
    /**
     *------------------------------------------------------------------------
     *ClassDefinition
     *------------------------------------------------------------------------
     */

  };

  varPopover=
  /*#__PURE__*/
  function(_Tooltip){
    _inheritsLoose(Popover,_Tooltip);

    functionPopover(){
      return_Tooltip.apply(this,arguments)||this;
    }

    var_proto=Popover.prototype;

    //Overrides
    _proto.isWithContent=functionisWithContent(){
      returnthis.getTitle()||this._getContent();
    };

    _proto.addAttachmentClass=functionaddAttachmentClass(attachment){
      $(this.getTipElement()).addClass(CLASS_PREFIX+"-"+attachment);
    };

    _proto.getTipElement=functiongetTipElement(){
      this.tip=this.tip||$(this.config.template)[0];
      returnthis.tip;
    };

    _proto.setContent=functionsetContent(){
      var$tip=$(this.getTipElement());//Weuseappendforhtmlobjectstomaintainjsevents

      this.setElementContent($tip.find(Selector.TITLE),this.getTitle());

      varcontent=this._getContent();

      if(typeofcontent==='function'){
        content=content.call(this.element);
      }

      this.setElementContent($tip.find(Selector.CONTENT),content);
      $tip.removeClass(ClassName.FADE+""+ClassName.SHOW);
    }//Private
    ;

    _proto._getContent=function_getContent(){
      returnthis.element.getAttribute('data-content')||this.config.content;
    };

    _proto._cleanTipClass=function_cleanTipClass(){
      var$tip=$(this.getTipElement());
      vartabClass=$tip.attr('class').match(BSCLS_PREFIX_REGEX);

      if(tabClass!==null&&tabClass.length>0){
        $tip.removeClass(tabClass.join(''));
      }
    }//Static
    ;

    Popover._jQueryInterface=function_jQueryInterface(config){
      returnthis.each(function(){
        vardata=$(this).data(DATA_KEY);

        var_config=typeofconfig==='object'?config:null;

        if(!data&&/dispose|hide/.test(config)){
          return;
        }

        if(!data){
          data=newPopover(this,_config);
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

    _createClass(Popover,null,[{
      key:"VERSION",
      //Getters
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

    returnPopover;
  }(Tooltip);
  /**
   *------------------------------------------------------------------------
   *jQuery
   *------------------------------------------------------------------------
   */


  $.fn[NAME]=Popover._jQueryInterface;
  $.fn[NAME].Constructor=Popover;

  $.fn[NAME].noConflict=function(){
    $.fn[NAME]=JQUERY_NO_CONFLICT;
    returnPopover._jQueryInterface;
  };

  returnPopover;

}));
