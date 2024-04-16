/*!
  *Bootstraputil.jsv4.3.1(https://getbootstrap.com/)
  *Copyright2011-2019TheBootstrapAuthors(https://github.com/twbs/bootstrap/graphs/contributors)
  *LicensedunderMIT(https://github.com/twbs/bootstrap/blob/master/LICENSE)
  */
(function(global,factory){
  typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory(require('jquery')):
  typeofdefine==='function'&&define.amd?define(['jquery'],factory):
  (global=global||self,global.Util=factory(global.jQuery));
}(this,function($){'usestrict';

  $=$&&$.hasOwnProperty('default')?$['default']:$;

  /**
   *--------------------------------------------------------------------------
   *Bootstrap(v4.3.1):util.js
   *LicensedunderMIT(https://github.com/twbs/bootstrap/blob/master/LICENSE)
   *--------------------------------------------------------------------------
   */
  /**
   *------------------------------------------------------------------------
   *PrivateTransitionEndHelpers
   *------------------------------------------------------------------------
   */

  varTRANSITION_END='transitionend';
  varMAX_UID=1000000;
  varMILLISECONDS_MULTIPLIER=1000;//ShoutoutAngusCroll(https://goo.gl/pxwQGp)

  functiontoType(obj){
    return{}.toString.call(obj).match(/\s([a-z]+)/i)[1].toLowerCase();
  }

  functiongetSpecialTransitionEndEvent(){
    return{
      bindType:TRANSITION_END,
      delegateType:TRANSITION_END,
      handle:functionhandle(event){
        if($(event.target).is(this)){
          returnevent.handleObj.handler.apply(this,arguments);//eslint-disable-lineprefer-rest-params
        }

        returnundefined;//eslint-disable-lineno-undefined
      }
    };
  }

  functiontransitionEndEmulator(duration){
    var_this=this;

    varcalled=false;
    $(this).one(Util.TRANSITION_END,function(){
      called=true;
    });
    setTimeout(function(){
      if(!called){
        Util.triggerTransitionEnd(_this);
      }
    },duration);
    returnthis;
  }

  functionsetTransitionEndSupport(){
    $.fn.emulateTransitionEnd=transitionEndEmulator;
    $.event.special[Util.TRANSITION_END]=getSpecialTransitionEndEvent();
  }
  /**
   *--------------------------------------------------------------------------
   *PublicUtilApi
   *--------------------------------------------------------------------------
   */


  varUtil={
    TRANSITION_END:'bsTransitionEnd',
    getUID:functiongetUID(prefix){
      do{
        //eslint-disable-next-lineno-bitwise
        prefix+=~~(Math.random()*MAX_UID);//"~~"actslikeafasterMath.floor()here
      }while(document.getElementById(prefix));

      returnprefix;
    },
    getSelectorFromElement:functiongetSelectorFromElement(element){
      varselector=element.getAttribute('data-target');

      if(!selector||selector==='#'){
        varhrefAttr=element.getAttribute('href');
        selector=hrefAttr&&hrefAttr!=='#'?hrefAttr.trim():'';
      }

      try{
        returndocument.querySelector(selector)?selector:null;
      }catch(err){
        returnnull;
      }
    },
    getTransitionDurationFromElement:functiongetTransitionDurationFromElement(element){
      if(!element){
        return0;
      }//Gettransition-durationoftheelement


      vartransitionDuration=$(element).css('transition-duration');
      vartransitionDelay=$(element).css('transition-delay');
      varfloatTransitionDuration=parseFloat(transitionDuration);
      varfloatTransitionDelay=parseFloat(transitionDelay);//Return0ifelementortransitiondurationisnotfound

      if(!floatTransitionDuration&&!floatTransitionDelay){
        return0;
      }//Ifmultipledurationsaredefined,takethefirst


      transitionDuration=transitionDuration.split(',')[0];
      transitionDelay=transitionDelay.split(',')[0];
      return(parseFloat(transitionDuration)+parseFloat(transitionDelay))*MILLISECONDS_MULTIPLIER;
    },
    reflow:functionreflow(element){
      returnelement.offsetHeight;
    },
    triggerTransitionEnd:functiontriggerTransitionEnd(element){
      $(element).trigger(TRANSITION_END);
    },
    //TODO:Removeinv5
    supportsTransitionEnd:functionsupportsTransitionEnd(){
      returnBoolean(TRANSITION_END);
    },
    isElement:functionisElement(obj){
      return(obj[0]||obj).nodeType;
    },
    typeCheckConfig:functiontypeCheckConfig(componentName,config,configTypes){
      for(varpropertyinconfigTypes){
        if(Object.prototype.hasOwnProperty.call(configTypes,property)){
          varexpectedTypes=configTypes[property];
          varvalue=config[property];
          varvalueType=value&&Util.isElement(value)?'element':toType(value);

          if(!newRegExp(expectedTypes).test(valueType)){
            thrownewError(componentName.toUpperCase()+":"+("Option\""+property+"\"providedtype\""+valueType+"\"")+("butexpectedtype\""+expectedTypes+"\"."));
          }
        }
      }
    },
    findShadowRoot:functionfindShadowRoot(element){
      if(!document.documentElement.attachShadow){
        returnnull;
      }//Canfindtheshadowroototherwiseit'llreturnthedocument


      if(typeofelement.getRootNode==='function'){
        varroot=element.getRootNode();
        returnrootinstanceofShadowRoot?root:null;
      }

      if(elementinstanceofShadowRoot){
        returnelement;
      }//whenwedon'tfindashadowroot


      if(!element.parentNode){
        returnnull;
      }

      returnUtil.findShadowRoot(element.parentNode);
    }
  };
  setTransitionEndSupport();

  returnUtil;

}));
