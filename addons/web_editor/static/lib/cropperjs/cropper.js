/*!
 *Cropper.jsv1.5.5
 *https://fengyuanchen.github.io/cropperjs
 *
 *Copyright2015-presentChenFengyuan
 *ReleasedundertheMITlicense
 *
 *Date:2019-08-04T02:26:31.160Z
 */

(function(global,factory){
  typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
  typeofdefine==='function'&&define.amd?define(factory):
  (global=global||self,global.Cropper=factory());
}(this,function(){'usestrict';

  function_typeof(obj){
    if(typeofSymbol==="function"&&typeofSymbol.iterator==="symbol"){
      _typeof=function(obj){
        returntypeofobj;
      };
    }else{
      _typeof=function(obj){
        returnobj&&typeofSymbol==="function"&&obj.constructor===Symbol&&obj!==Symbol.prototype?"symbol":typeofobj;
      };
    }

    return_typeof(obj);
  }

  function_classCallCheck(instance,Constructor){
    if(!(instanceinstanceofConstructor)){
      thrownewTypeError("Cannotcallaclassasafunction");
    }
  }

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

  function_toConsumableArray(arr){
    return_arrayWithoutHoles(arr)||_iterableToArray(arr)||_nonIterableSpread();
  }

  function_arrayWithoutHoles(arr){
    if(Array.isArray(arr)){
      for(vari=0,arr2=newArray(arr.length);i<arr.length;i++)arr2[i]=arr[i];

      returnarr2;
    }
  }

  function_iterableToArray(iter){
    if(Symbol.iteratorinObject(iter)||Object.prototype.toString.call(iter)==="[objectArguments]")returnArray.from(iter);
  }

  function_nonIterableSpread(){
    thrownewTypeError("Invalidattempttospreadnon-iterableinstance");
  }

  varIS_BROWSER=typeofwindow!=='undefined'&&typeofwindow.document!=='undefined';
  varWINDOW=IS_BROWSER?window:{};
  varIS_TOUCH_DEVICE=IS_BROWSER?'ontouchstart'inWINDOW.document.documentElement:false;
  varHAS_POINTER_EVENT=IS_BROWSER?'PointerEvent'inWINDOW:false;
  varNAMESPACE='cropper';//Actions

  varACTION_ALL='all';
  varACTION_CROP='crop';
  varACTION_MOVE='move';
  varACTION_ZOOM='zoom';
  varACTION_EAST='e';
  varACTION_WEST='w';
  varACTION_SOUTH='s';
  varACTION_NORTH='n';
  varACTION_NORTH_EAST='ne';
  varACTION_NORTH_WEST='nw';
  varACTION_SOUTH_EAST='se';
  varACTION_SOUTH_WEST='sw';//Classes

  varCLASS_CROP="".concat(NAMESPACE,"-crop");
  varCLASS_DISABLED="".concat(NAMESPACE,"-disabled");
  varCLASS_HIDDEN="".concat(NAMESPACE,"-hidden");
  varCLASS_HIDE="".concat(NAMESPACE,"-hide");
  varCLASS_INVISIBLE="".concat(NAMESPACE,"-invisible");
  varCLASS_MODAL="".concat(NAMESPACE,"-modal");
  varCLASS_MOVE="".concat(NAMESPACE,"-move");//Datakeys

  varDATA_ACTION="".concat(NAMESPACE,"Action");
  varDATA_PREVIEW="".concat(NAMESPACE,"Preview");//Dragmodes

  varDRAG_MODE_CROP='crop';
  varDRAG_MODE_MOVE='move';
  varDRAG_MODE_NONE='none';//Events

  varEVENT_CROP='crop';
  varEVENT_CROP_END='cropend';
  varEVENT_CROP_MOVE='cropmove';
  varEVENT_CROP_START='cropstart';
  varEVENT_DBLCLICK='dblclick';
  varEVENT_TOUCH_START=IS_TOUCH_DEVICE?'touchstart':'mousedown';
  varEVENT_TOUCH_MOVE=IS_TOUCH_DEVICE?'touchmove':'mousemove';
  varEVENT_TOUCH_END=IS_TOUCH_DEVICE?'touchendtouchcancel':'mouseup';
  varEVENT_POINTER_DOWN=HAS_POINTER_EVENT?'pointerdown':EVENT_TOUCH_START;
  varEVENT_POINTER_MOVE=HAS_POINTER_EVENT?'pointermove':EVENT_TOUCH_MOVE;
  varEVENT_POINTER_UP=HAS_POINTER_EVENT?'pointeruppointercancel':EVENT_TOUCH_END;
  varEVENT_READY='ready';
  varEVENT_RESIZE='resize';
  varEVENT_WHEEL='wheel';
  varEVENT_ZOOM='zoom';//Mimetypes

  varMIME_TYPE_JPEG='image/jpeg';//RegExps

  varREGEXP_ACTIONS=/^e|w|s|n|se|sw|ne|nw|all|crop|move|zoom$/;
  varREGEXP_DATA_URL=/^data:/;
  varREGEXP_DATA_URL_JPEG=/^data:image\/jpeg;base64,/;
  varREGEXP_TAG_NAME=/^img|canvas$/i;//Misc
  //Inspiredbythedefaultwidthandheightofacanvaselement.

  varMIN_CONTAINER_WIDTH=200;
  varMIN_CONTAINER_HEIGHT=100;

  varDEFAULTS={
    //Definetheviewmodeofthecropper
    viewMode:0,
    //0,1,2,3
    //Definethedraggingmodeofthecropper
    dragMode:DRAG_MODE_CROP,
    //'crop','move'or'none'
    //Definetheinitialaspectratioofthecropbox
    initialAspectRatio:NaN,
    //Definetheaspectratioofthecropbox
    aspectRatio:NaN,
    //Anobjectwiththepreviouscroppingresultdata
    data:null,
    //Aselectorforaddingextracontainerstopreview
    preview:'',
    //Re-renderthecropperwhenresizethewindow
    responsive:true,
    //Restorethecroppedareaafterresizethewindow
    restore:true,
    //Checkifthecurrentimageisacross-originimage
    checkCrossOrigin:true,
    //Checkthecurrentimage'sExifOrientationinformation
    checkOrientation:true,
    //Showtheblackmodal
    modal:true,
    //Showthedashedlinesforguiding
    guides:true,
    //Showthecenterindicatorforguiding
    center:true,
    //Showthewhitemodaltohighlightthecropbox
    highlight:true,
    //Showthegridbackground
    background:true,
    //Enabletocroptheimageautomaticallywheninitialize
    autoCrop:true,
    //Definethepercentageofautomaticcroppingareawheninitializes
    autoCropArea:0.8,
    //Enabletomovetheimage
    movable:true,
    //Enabletorotatetheimage
    rotatable:true,
    //Enabletoscaletheimage
    scalable:true,
    //Enabletozoomtheimage
    zoomable:true,
    //Enabletozoomtheimagebydraggingtouch
    zoomOnTouch:true,
    //Enabletozoomtheimagebywheelingmouse
    zoomOnWheel:true,
    //Definezoomratiowhenzoomtheimagebywheelingmouse
    wheelZoomRatio:0.1,
    //Enabletomovethecropbox
    cropBoxMovable:true,
    //Enabletoresizethecropbox
    cropBoxResizable:true,
    //Toggledragmodebetween"crop"and"move"whenclicktwiceonthecropper
    toggleDragModeOnDblclick:true,
    //Sizelimitation
    minCanvasWidth:0,
    minCanvasHeight:0,
    minCropBoxWidth:0,
    minCropBoxHeight:0,
    minContainerWidth:200,
    minContainerHeight:100,
    //Shortcutsofevents
    ready:null,
    cropstart:null,
    cropmove:null,
    cropend:null,
    crop:null,
    zoom:null
  };

  varTEMPLATE='<divclass="cropper-container"touch-action="none">'+'<divclass="cropper-wrap-box">'+'<divclass="cropper-canvas"></div>'+'</div>'+'<divclass="cropper-drag-box"></div>'+'<divclass="cropper-crop-box">'+'<spanclass="cropper-view-box"></span>'+'<spanclass="cropper-dasheddashed-h"></span>'+'<spanclass="cropper-dasheddashed-v"></span>'+'<spanclass="cropper-center"></span>'+'<spanclass="cropper-face"></span>'+'<spanclass="cropper-lineline-e"data-cropper-action="e"></span>'+'<spanclass="cropper-lineline-n"data-cropper-action="n"></span>'+'<spanclass="cropper-lineline-w"data-cropper-action="w"></span>'+'<spanclass="cropper-lineline-s"data-cropper-action="s"></span>'+'<spanclass="cropper-pointpoint-e"data-cropper-action="e"></span>'+'<spanclass="cropper-pointpoint-n"data-cropper-action="n"></span>'+'<spanclass="cropper-pointpoint-w"data-cropper-action="w"></span>'+'<spanclass="cropper-pointpoint-s"data-cropper-action="s"></span>'+'<spanclass="cropper-pointpoint-ne"data-cropper-action="ne"></span>'+'<spanclass="cropper-pointpoint-nw"data-cropper-action="nw"></span>'+'<spanclass="cropper-pointpoint-sw"data-cropper-action="sw"></span>'+'<spanclass="cropper-pointpoint-se"data-cropper-action="se"></span>'+'</div>'+'</div>';

  /**
   *Checkifthegivenvalueisnotanumber.
   */

  varisNaN=Number.isNaN||WINDOW.isNaN;
  /**
   *Checkifthegivenvalueisanumber.
   *@param{*}value-Thevaluetocheck.
   *@returns{boolean}Returns`true`ifthegivenvalueisanumber,else`false`.
   */

  functionisNumber(value){
    returntypeofvalue==='number'&&!isNaN(value);
  }
  /**
   *Checkifthegivenvalueisapositivenumber.
   *@param{*}value-Thevaluetocheck.
   *@returns{boolean}Returns`true`ifthegivenvalueisapositivenumber,else`false`.
   */

  varisPositiveNumber=functionisPositiveNumber(value){
    returnvalue>0&&value<Infinity;
  };
  /**
   *Checkifthegivenvalueisundefined.
   *@param{*}value-Thevaluetocheck.
   *@returns{boolean}Returns`true`ifthegivenvalueisundefined,else`false`.
   */

  functionisUndefined(value){
    returntypeofvalue==='undefined';
  }
  /**
   *Checkifthegivenvalueisanobject.
   *@param{*}value-Thevaluetocheck.
   *@returns{boolean}Returns`true`ifthegivenvalueisanobject,else`false`.
   */

  functionisObject(value){
    return_typeof(value)==='object'&&value!==null;
  }
  varhasOwnProperty=Object.prototype.hasOwnProperty;
  /**
   *Checkifthegivenvalueisaplainobject.
   *@param{*}value-Thevaluetocheck.
   *@returns{boolean}Returns`true`ifthegivenvalueisaplainobject,else`false`.
   */

  functionisPlainObject(value){
    if(!isObject(value)){
      returnfalse;
    }

    try{
      var_constructor=value.constructor;
      varprototype=_constructor.prototype;
      return_constructor&&prototype&&hasOwnProperty.call(prototype,'isPrototypeOf');
    }catch(error){
      returnfalse;
    }
  }
  /**
   *Checkifthegivenvalueisafunction.
   *@param{*}value-Thevaluetocheck.
   *@returns{boolean}Returns`true`ifthegivenvalueisafunction,else`false`.
   */

  functionisFunction(value){
    returntypeofvalue==='function';
  }
  varslice=Array.prototype.slice;
  /**
   *Convertarray-likeoriterableobjecttoanarray.
   *@param{*}value-Thevaluetoconvert.
   *@returns{Array}Returnsanewarray.
   */

  functiontoArray(value){
    returnArray.from?Array.from(value):slice.call(value);
  }
  /**
   *Iteratethegivendata.
   *@param{*}data-Thedatatoiterate.
   *@param{Function}callback-Theprocessfunctionforeachelement.
   *@returns{*}Theoriginaldata.
   */

  functionforEach(data,callback){
    if(data&&isFunction(callback)){
      if(Array.isArray(data)||isNumber(data.length)
      /*array-like*/
      ){
          toArray(data).forEach(function(value,key){
            callback.call(data,value,key,data);
          });
        }elseif(isObject(data)){
        Object.keys(data).forEach(function(key){
          callback.call(data,data[key],key,data);
        });
      }
    }

    returndata;
  }
  /**
   *Extendthegivenobject.
   *@param{*}target-Thetargetobjecttoextend.
   *@param{*}args-Therestobjectsformergingtothetargetobject.
   *@returns{Object}Theextendedobject.
   */

  varassign=Object.assign||functionassign(target){
    for(var_len=arguments.length,args=newArray(_len>1?_len-1:0),_key=1;_key<_len;_key++){
      args[_key-1]=arguments[_key];
    }

    if(isObject(target)&&args.length>0){
      args.forEach(function(arg){
        if(isObject(arg)){
          Object.keys(arg).forEach(function(key){
            target[key]=arg[key];
          });
        }
      });
    }

    returntarget;
  };
  varREGEXP_DECIMALS=/\.\d*(?:0|9){12}\d*$/;
  /**
   *Normalizedecimalnumber.
   *Checkout{@linkhttp://0.30000000000000004.com/}
   *@param{number}value-Thevaluetonormalize.
   *@param{number}[times=100000000000]-Thetimesfornormalizing.
   *@returns{number}Returnsthenormalizednumber.
   */

  functionnormalizeDecimalNumber(value){
    vartimes=arguments.length>1&&arguments[1]!==undefined?arguments[1]:100000000000;
    returnREGEXP_DECIMALS.test(value)?Math.round(value*times)/times:value;
  }
  varREGEXP_SUFFIX=/^width|height|left|top|marginLeft|marginTop$/;
  /**
   *Applystylestothegivenelement.
   *@param{Element}element-Thetargetelement.
   *@param{Object}styles-Thestylesforapplying.
   */

  functionsetStyle(element,styles){
    varstyle=element.style;
    forEach(styles,function(value,property){
      if(REGEXP_SUFFIX.test(property)&&isNumber(value)){
        value="".concat(value,"px");
      }

      style[property]=value;
    });
  }
  /**
   *Checkifthegivenelementhasaspecialclass.
   *@param{Element}element-Theelementtocheck.
   *@param{string}value-Theclasstosearch.
   *@returns{boolean}Returns`true`ifthespecialclasswasfound.
   */

  functionhasClass(element,value){
    returnelement.classList?element.classList.contains(value):element.className.indexOf(value)>-1;
  }
  /**
   *Addclassestothegivenelement.
   *@param{Element}element-Thetargetelement.
   *@param{string}value-Theclassestobeadded.
   */

  functionaddClass(element,value){
    if(!value){
      return;
    }

    if(isNumber(element.length)){
      forEach(element,function(elem){
        addClass(elem,value);
      });
      return;
    }

    if(element.classList){
      element.classList.add(value);
      return;
    }

    varclassName=element.className.trim();

    if(!className){
      element.className=value;
    }elseif(className.indexOf(value)<0){
      element.className="".concat(className,"").concat(value);
    }
  }
  /**
   *Removeclassesfromthegivenelement.
   *@param{Element}element-Thetargetelement.
   *@param{string}value-Theclassestoberemoved.
   */

  functionremoveClass(element,value){
    if(!value){
      return;
    }

    if(isNumber(element.length)){
      forEach(element,function(elem){
        removeClass(elem,value);
      });
      return;
    }

    if(element.classList){
      element.classList.remove(value);
      return;
    }

    if(element.className.indexOf(value)>=0){
      element.className=element.className.replace(value,'');
    }
  }
  /**
   *Addorremoveclassesfromthegivenelement.
   *@param{Element}element-Thetargetelement.
   *@param{string}value-Theclassestobetoggled.
   *@param{boolean}added-Addonly.
   */

  functiontoggleClass(element,value,added){
    if(!value){
      return;
    }

    if(isNumber(element.length)){
      forEach(element,function(elem){
        toggleClass(elem,value,added);
      });
      return;
    }//IE10-11doesn'tsupportthesecondparameterof`classList.toggle`


    if(added){
      addClass(element,value);
    }else{
      removeClass(element,value);
    }
  }
  varREGEXP_CAMEL_CASE=/([a-z\d])([A-Z])/g;
  /**
   *TransformthegivenstringfromcamelCasetokebab-case
   *@param{string}value-Thevaluetotransform.
   *@returns{string}Thetransformedvalue.
   */

  functiontoParamCase(value){
    returnvalue.replace(REGEXP_CAMEL_CASE,'$1-$2').toLowerCase();
  }
  /**
   *Getdatafromthegivenelement.
   *@param{Element}element-Thetargetelement.
   *@param{string}name-Thedatakeytoget.
   *@returns{string}Thedatavalue.
   */

  functiongetData(element,name){
    if(isObject(element[name])){
      returnelement[name];
    }

    if(element.dataset){
      returnelement.dataset[name];
    }

    returnelement.getAttribute("data-".concat(toParamCase(name)));
  }
  /**
   *Setdatatothegivenelement.
   *@param{Element}element-Thetargetelement.
   *@param{string}name-Thedatakeytoset.
   *@param{string}data-Thedatavalue.
   */

  functionsetData(element,name,data){
    if(isObject(data)){
      element[name]=data;
    }elseif(element.dataset){
      element.dataset[name]=data;
    }else{
      element.setAttribute("data-".concat(toParamCase(name)),data);
    }
  }
  /**
   *Removedatafromthegivenelement.
   *@param{Element}element-Thetargetelement.
   *@param{string}name-Thedatakeytoremove.
   */

  functionremoveData(element,name){
    if(isObject(element[name])){
      try{
        deleteelement[name];
      }catch(error){
        element[name]=undefined;
      }
    }elseif(element.dataset){
      //#128Safarinotallowstodeletedatasetproperty
      try{
        deleteelement.dataset[name];
      }catch(error){
        element.dataset[name]=undefined;
      }
    }else{
      element.removeAttribute("data-".concat(toParamCase(name)));
    }
  }
  varREGEXP_SPACES=/\s\s*/;

  varonceSupported=function(){
    varsupported=false;

    if(IS_BROWSER){
      varonce=false;

      varlistener=functionlistener(){};

      varoptions=Object.defineProperty({},'once',{
        get:functionget(){
          supported=true;
          returnonce;
        },

        /**
         *Thissettercanfixa`TypeError`instrictmode
         *{@linkhttps://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Errors/Getter_only}
         *@param{boolean}value-Thevaluetoset
         */
        set:functionset(value){
          once=value;
        }
      });
      WINDOW.addEventListener('test',listener,options);
      WINDOW.removeEventListener('test',listener,options);
    }

    returnsupported;
  }();
  /**
   *Removeeventlistenerfromthetargetelement.
   *@param{Element}element-Theeventtarget.
   *@param{string}type-Theeventtype(s).
   *@param{Function}listener-Theeventlistener.
   *@param{Object}options-Theeventoptions.
   */


  functionremoveListener(element,type,listener){
    varoptions=arguments.length>3&&arguments[3]!==undefined?arguments[3]:{};
    varhandler=listener;
    type.trim().split(REGEXP_SPACES).forEach(function(event){
      if(!onceSupported){
        varlisteners=element.listeners;

        if(listeners&&listeners[event]&&listeners[event][listener]){
          handler=listeners[event][listener];
          deletelisteners[event][listener];

          if(Object.keys(listeners[event]).length===0){
            deletelisteners[event];
          }

          if(Object.keys(listeners).length===0){
            deleteelement.listeners;
          }
        }
      }

      element.removeEventListener(event,handler,options);
    });
  }
  /**
   *Addeventlistenertothetargetelement.
   *@param{Element}element-Theeventtarget.
   *@param{string}type-Theeventtype(s).
   *@param{Function}listener-Theeventlistener.
   *@param{Object}options-Theeventoptions.
   */

  functionaddListener(element,type,listener){
    varoptions=arguments.length>3&&arguments[3]!==undefined?arguments[3]:{};
    var_handler=listener;
    type.trim().split(REGEXP_SPACES).forEach(function(event){
      if(options.once&&!onceSupported){
        var_element$listeners=element.listeners,
            listeners=_element$listeners===void0?{}:_element$listeners;

        _handler=functionhandler(){
          deletelisteners[event][listener];
          element.removeEventListener(event,_handler,options);

          for(var_len2=arguments.length,args=newArray(_len2),_key2=0;_key2<_len2;_key2++){
            args[_key2]=arguments[_key2];
          }

          listener.apply(element,args);
        };

        if(!listeners[event]){
          listeners[event]={};
        }

        if(listeners[event][listener]){
          element.removeEventListener(event,listeners[event][listener],options);
        }

        listeners[event][listener]=_handler;
        element.listeners=listeners;
      }

      element.addEventListener(event,_handler,options);
    });
  }
  /**
   *Dispatcheventonthetargetelement.
   *@param{Element}element-Theeventtarget.
   *@param{string}type-Theeventtype(s).
   *@param{Object}data-Theadditionaleventdata.
   *@returns{boolean}Indicateiftheeventisdefaultpreventedornot.
   */

  functiondispatchEvent(element,type,data){
    varevent;//EventandCustomEventonIE9-11areglobalobjects,notconstructors

    if(isFunction(Event)&&isFunction(CustomEvent)){
      event=newCustomEvent(type,{
        detail:data,
        bubbles:true,
        cancelable:true
      });
    }else{
      event=document.createEvent('CustomEvent');
      event.initCustomEvent(type,true,true,data);
    }

    returnelement.dispatchEvent(event);
  }
  /**
   *Gettheoffsetbaseonthedocument.
   *@param{Element}element-Thetargetelement.
   *@returns{Object}Theoffsetdata.
   */

  functiongetOffset(element){
    varbox=element.getBoundingClientRect();
    return{
      left:box.left+(window.pageXOffset-document.documentElement.clientLeft),
      top:box.top+(window.pageYOffset-document.documentElement.clientTop)
    };
  }
  varlocation=WINDOW.location;
  varREGEXP_ORIGINS=/^(\w+:)\/\/([^:/?#]*):?(\d*)/i;
  /**
   *CheckifthegivenURLisacrossoriginURL.
   *@param{string}url-ThetargetURL.
   *@returns{boolean}Returns`true`ifthegivenURLisacrossoriginURL,else`false`.
   */

  functionisCrossOriginURL(url){
    varparts=url.match(REGEXP_ORIGINS);
    returnparts!==null&&(parts[1]!==location.protocol||parts[2]!==location.hostname||parts[3]!==location.port);
  }
  /**
   *AddtimestamptothegivenURL.
   *@param{string}url-ThetargetURL.
   *@returns{string}TheresultURL.
   */

  functionaddTimestamp(url){
    vartimestamp="timestamp=".concat(newDate().getTime());
    returnurl+(url.indexOf('?')===-1?'?':'&')+timestamp;
  }
  /**
   *Gettransformsbaseonthegivenobject.
   *@param{Object}obj-Thetargetobject.
   *@returns{string}Astringcontainstransformvalues.
   */

  functiongetTransforms(_ref){
    varrotate=_ref.rotate,
        scaleX=_ref.scaleX,
        scaleY=_ref.scaleY,
        translateX=_ref.translateX,
        translateY=_ref.translateY;
    varvalues=[];

    if(isNumber(translateX)&&translateX!==0){
      values.push("translateX(".concat(translateX,"px)"));
    }

    if(isNumber(translateY)&&translateY!==0){
      values.push("translateY(".concat(translateY,"px)"));
    }//Rotateshouldcomefirstbeforescaletomatchorientationtransform


    if(isNumber(rotate)&&rotate!==0){
      values.push("rotate(".concat(rotate,"deg)"));
    }

    if(isNumber(scaleX)&&scaleX!==1){
      values.push("scaleX(".concat(scaleX,")"));
    }

    if(isNumber(scaleY)&&scaleY!==1){
      values.push("scaleY(".concat(scaleY,")"));
    }

    vartransform=values.length?values.join(''):'none';
    return{
      WebkitTransform:transform,
      msTransform:transform,
      transform:transform
    };
  }
  /**
   *Getthemaxratioofagroupofpointers.
   *@param{string}pointers-Thetargetpointers.
   *@returns{number}Theresultratio.
   */

  functiongetMaxZoomRatio(pointers){
    varpointers2=assign({},pointers);
    varratios=[];
    forEach(pointers,function(pointer,pointerId){
      deletepointers2[pointerId];
      forEach(pointers2,function(pointer2){
        varx1=Math.abs(pointer.startX-pointer2.startX);
        vary1=Math.abs(pointer.startY-pointer2.startY);
        varx2=Math.abs(pointer.endX-pointer2.endX);
        vary2=Math.abs(pointer.endY-pointer2.endY);
        varz1=Math.sqrt(x1*x1+y1*y1);
        varz2=Math.sqrt(x2*x2+y2*y2);
        varratio=(z2-z1)/z1;
        ratios.push(ratio);
      });
    });
    ratios.sort(function(a,b){
      returnMath.abs(a)<Math.abs(b);
    });
    returnratios[0];
  }
  /**
   *Getapointerfromaneventobject.
   *@param{Object}event-Thetargeteventobject.
   *@param{boolean}endOnly-Indicatesifonlyreturnstheendpointcoordinateornot.
   *@returns{Object}Theresultpointercontainsstartand/orendpointcoordinates.
   */

  functiongetPointer(_ref2,endOnly){
    varpageX=_ref2.pageX,
        pageY=_ref2.pageY;
    varend={
      endX:pageX,
      endY:pageY
    };
    returnendOnly?end:assign({
      startX:pageX,
      startY:pageY
    },end);
  }
  /**
   *Getthecenterpointcoordinateofagroupofpointers.
   *@param{Object}pointers-Thetargetpointers.
   *@returns{Object}Thecenterpointcoordinate.
   */

  functiongetPointersCenter(pointers){
    varpageX=0;
    varpageY=0;
    varcount=0;
    forEach(pointers,function(_ref3){
      varstartX=_ref3.startX,
          startY=_ref3.startY;
      pageX+=startX;
      pageY+=startY;
      count+=1;
    });
    pageX/=count;
    pageY/=count;
    return{
      pageX:pageX,
      pageY:pageY
    };
  }
  /**
   *Getthemaxsizesinarectangleunderthegivenaspectratio.
   *@param{Object}data-Theoriginalsizes.
   *@param{string}[type='contain']-Theadjusttype.
   *@returns{Object}Theresultsizes.
   */

  functiongetAdjustedSizes(_ref4)//or'cover'
  {
    varaspectRatio=_ref4.aspectRatio,
        height=_ref4.height,
        width=_ref4.width;
    vartype=arguments.length>1&&arguments[1]!==undefined?arguments[1]:'contain';
    varisValidWidth=isPositiveNumber(width);
    varisValidHeight=isPositiveNumber(height);

    if(isValidWidth&&isValidHeight){
      varadjustedWidth=height*aspectRatio;

      if(type==='contain'&&adjustedWidth>width||type==='cover'&&adjustedWidth<width){
        height=width/aspectRatio;
      }else{
        width=height*aspectRatio;
      }
    }elseif(isValidWidth){
      height=width/aspectRatio;
    }elseif(isValidHeight){
      width=height*aspectRatio;
    }

    return{
      width:width,
      height:height
    };
  }
  /**
   *Getthenewsizesofarectangleafterrotated.
   *@param{Object}data-Theoriginalsizes.
   *@returns{Object}Theresultsizes.
   */

  functiongetRotatedSizes(_ref5){
    varwidth=_ref5.width,
        height=_ref5.height,
        degree=_ref5.degree;
    degree=Math.abs(degree)%180;

    if(degree===90){
      return{
        width:height,
        height:width
      };
    }

    vararc=degree%90*Math.PI/180;
    varsinArc=Math.sin(arc);
    varcosArc=Math.cos(arc);
    varnewWidth=width*cosArc+height*sinArc;
    varnewHeight=width*sinArc+height*cosArc;
    returndegree>90?{
      width:newHeight,
      height:newWidth
    }:{
      width:newWidth,
      height:newHeight
    };
  }
  /**
   *Getacanvaswhichdrewthegivenimage.
   *@param{HTMLImageElement}image-Theimagefordrawing.
   *@param{Object}imageData-Theimagedata.
   *@param{Object}canvasData-Thecanvasdata.
   *@param{Object}options-Theoptions.
   *@returns{HTMLCanvasElement}Theresultcanvas.
   */

  functiongetSourceCanvas(image,_ref6,_ref7,_ref8){
    varimageAspectRatio=_ref6.aspectRatio,
        imageNaturalWidth=_ref6.naturalWidth,
        imageNaturalHeight=_ref6.naturalHeight,
        _ref6$rotate=_ref6.rotate,
        rotate=_ref6$rotate===void0?0:_ref6$rotate,
        _ref6$scaleX=_ref6.scaleX,
        scaleX=_ref6$scaleX===void0?1:_ref6$scaleX,
        _ref6$scaleY=_ref6.scaleY,
        scaleY=_ref6$scaleY===void0?1:_ref6$scaleY;
    varaspectRatio=_ref7.aspectRatio,
        naturalWidth=_ref7.naturalWidth,
        naturalHeight=_ref7.naturalHeight;
    var_ref8$fillColor=_ref8.fillColor,
        fillColor=_ref8$fillColor===void0?'transparent':_ref8$fillColor,
        _ref8$imageSmoothingE=_ref8.imageSmoothingEnabled,
        imageSmoothingEnabled=_ref8$imageSmoothingE===void0?true:_ref8$imageSmoothingE,
        _ref8$imageSmoothingQ=_ref8.imageSmoothingQuality,
        imageSmoothingQuality=_ref8$imageSmoothingQ===void0?'low':_ref8$imageSmoothingQ,
        _ref8$maxWidth=_ref8.maxWidth,
        maxWidth=_ref8$maxWidth===void0?Infinity:_ref8$maxWidth,
        _ref8$maxHeight=_ref8.maxHeight,
        maxHeight=_ref8$maxHeight===void0?Infinity:_ref8$maxHeight,
        _ref8$minWidth=_ref8.minWidth,
        minWidth=_ref8$minWidth===void0?0:_ref8$minWidth,
        _ref8$minHeight=_ref8.minHeight,
        minHeight=_ref8$minHeight===void0?0:_ref8$minHeight;
    varcanvas=document.createElement('canvas');
    varcontext=canvas.getContext('2d');
    varmaxSizes=getAdjustedSizes({
      aspectRatio:aspectRatio,
      width:maxWidth,
      height:maxHeight
    });
    varminSizes=getAdjustedSizes({
      aspectRatio:aspectRatio,
      width:minWidth,
      height:minHeight
    },'cover');
    varwidth=Math.min(maxSizes.width,Math.max(minSizes.width,naturalWidth));
    varheight=Math.min(maxSizes.height,Math.max(minSizes.height,naturalHeight));//Note:shouldalwaysuseimage'snaturalsizesfordrawingas
    //imageData.naturalWidth===canvasData.naturalHeightwhenrotate%180===90

    vardestMaxSizes=getAdjustedSizes({
      aspectRatio:imageAspectRatio,
      width:maxWidth,
      height:maxHeight
    });
    vardestMinSizes=getAdjustedSizes({
      aspectRatio:imageAspectRatio,
      width:minWidth,
      height:minHeight
    },'cover');
    vardestWidth=Math.min(destMaxSizes.width,Math.max(destMinSizes.width,imageNaturalWidth));
    vardestHeight=Math.min(destMaxSizes.height,Math.max(destMinSizes.height,imageNaturalHeight));
    varparams=[-destWidth/2,-destHeight/2,destWidth,destHeight];
    canvas.width=normalizeDecimalNumber(width);
    canvas.height=normalizeDecimalNumber(height);
    context.fillStyle=fillColor;
    context.fillRect(0,0,width,height);
    context.save();
    context.translate(width/2,height/2);
    context.rotate(rotate*Math.PI/180);
    context.scale(scaleX,scaleY);
    context.imageSmoothingEnabled=imageSmoothingEnabled;
    context.imageSmoothingQuality=imageSmoothingQuality;
    /**
     *FLECTRAFIXSTART
     *
     *Canevasistranslatedandthentranslatedback.Forthesecondtranslationthe
     *translationdistanceswereroundedtothenearestintegerbelowwhenitshould
     *notsincethedistancesofthefirsttranslationareeitheranintegerorthe
     *halfofaninteger.
     *
     *Fixproposedbyhttps://github.com/fengyuanchen/cropperjs/pull/866
     */
    params=params.map(normalizeDecimalNumber);
    context.drawImage(image,params[0],params[1],Math.floor(params[2]),Math.floor(params[3]));
    //FLECTRAFIXEND
    context.restore();
    returncanvas;
  }
  varfromCharCode=String.fromCharCode;
  /**
   *Getstringfromcharcodeindataview.
   *@param{DataView}dataView-Thedataviewforread.
   *@param{number}start-Thestartindex.
   *@param{number}length-Thereadlength.
   *@returns{string}Thereadresult.
   */

  functiongetStringFromCharCode(dataView,start,length){
    varstr='';
    length+=start;

    for(vari=start;i<length;i+=1){
      str+=fromCharCode(dataView.getUint8(i));
    }

    returnstr;
  }
  varREGEXP_DATA_URL_HEAD=/^data:.*,/;
  /**
   *TransformDataURLtoarraybuffer.
   *@param{string}dataURL-TheDataURLtotransform.
   *@returns{ArrayBuffer}Theresultarraybuffer.
   */

  functiondataURLToArrayBuffer(dataURL){
    varbase64=dataURL.replace(REGEXP_DATA_URL_HEAD,'');
    varbinary=atob(base64);
    vararrayBuffer=newArrayBuffer(binary.length);
    varuint8=newUint8Array(arrayBuffer);
    forEach(uint8,function(value,i){
      uint8[i]=binary.charCodeAt(i);
    });
    returnarrayBuffer;
  }
  /**
   *TransformarraybuffertoDataURL.
   *@param{ArrayBuffer}arrayBuffer-Thearraybuffertotransform.
   *@param{string}mimeType-ThemimetypeoftheDataURL.
   *@returns{string}TheresultDataURL.
   */

  functionarrayBufferToDataURL(arrayBuffer,mimeType){
    varchunks=[];//ChunkTypedArrayforbetterperformance(#435)

    varchunkSize=8192;
    varuint8=newUint8Array(arrayBuffer);

    while(uint8.length>0){
      //XXX:Babel's`toConsumableArray`helperwillthrowerrorinIEorSafari9
      //eslint-disable-next-lineprefer-spread
      chunks.push(fromCharCode.apply(null,toArray(uint8.subarray(0,chunkSize))));
      uint8=uint8.subarray(chunkSize);
    }

    return"data:".concat(mimeType,";base64,").concat(btoa(chunks.join('')));
  }
  /**
   *Getorientationvaluefromgivenarraybuffer.
   *@param{ArrayBuffer}arrayBuffer-Thearraybuffertoread.
   *@returns{number}Thereadorientationvalue.
   */

  functionresetAndGetOrientation(arrayBuffer){
    vardataView=newDataView(arrayBuffer);
    varorientation;//IgnoresrangeerrorwhentheimagedoesnothavecorrectExifinformation

    try{
      varlittleEndian;
      varapp1Start;
      varifdStart;//OnlyhandleJPEGimage(startby0xFFD8)

      if(dataView.getUint8(0)===0xFF&&dataView.getUint8(1)===0xD8){
        varlength=dataView.byteLength;
        varoffset=2;

        while(offset+1<length){
          if(dataView.getUint8(offset)===0xFF&&dataView.getUint8(offset+1)===0xE1){
            app1Start=offset;
            break;
          }

          offset+=1;
        }
      }

      if(app1Start){
        varexifIDCode=app1Start+4;
        vartiffOffset=app1Start+10;

        if(getStringFromCharCode(dataView,exifIDCode,4)==='Exif'){
          varendianness=dataView.getUint16(tiffOffset);
          littleEndian=endianness===0x4949;

          if(littleEndian||endianness===0x4D4D
          /*bigEndian*/
          ){
              if(dataView.getUint16(tiffOffset+2,littleEndian)===0x002A){
                varfirstIFDOffset=dataView.getUint32(tiffOffset+4,littleEndian);

                if(firstIFDOffset>=0x00000008){
                  ifdStart=tiffOffset+firstIFDOffset;
                }
              }
            }
        }
      }

      if(ifdStart){
        var_length=dataView.getUint16(ifdStart,littleEndian);

        var_offset;

        vari;

        for(i=0;i<_length;i+=1){
          _offset=ifdStart+i*12+2;

          if(dataView.getUint16(_offset,littleEndian)===0x0112
          /*Orientation*/
          ){
              //8istheoffsetofthecurrenttag'svalue
              _offset+=8;//Gettheoriginalorientationvalue

              orientation=dataView.getUint16(_offset,littleEndian);//Overridetheorientationwithitsdefaultvalue

              dataView.setUint16(_offset,1,littleEndian);
              break;
            }
        }
      }
    }catch(error){
      orientation=1;
    }

    returnorientation;
  }
  /**
   *ParseExifOrientationvalue.
   *@param{number}orientation-Theorientationtoparse.
   *@returns{Object}Theparsedresult.
   */

  functionparseOrientation(orientation){
    varrotate=0;
    varscaleX=1;
    varscaleY=1;

    switch(orientation){
      //Fliphorizontal
      case2:
        scaleX=-1;
        break;
      //Rotateleft180°

      case3:
        rotate=-180;
        break;
      //Flipvertical

      case4:
        scaleY=-1;
        break;
      //Flipverticalandrotateright90°

      case5:
        rotate=90;
        scaleY=-1;
        break;
      //Rotateright90°

      case6:
        rotate=90;
        break;
      //Fliphorizontalandrotateright90°

      case7:
        rotate=90;
        scaleX=-1;
        break;
      //Rotateleft90°

      case8:
        rotate=-90;
        break;

      default:
    }

    return{
      rotate:rotate,
      scaleX:scaleX,
      scaleY:scaleY
    };
  }

  varrender={
    render:functionrender(){
      this.initContainer();
      this.initCanvas();
      this.initCropBox();
      this.renderCanvas();

      if(this.cropped){
        this.renderCropBox();
      }
    },
    initContainer:functioninitContainer(){
      varelement=this.element,
          options=this.options,
          container=this.container,
          cropper=this.cropper;
      addClass(cropper,CLASS_HIDDEN);
      removeClass(element,CLASS_HIDDEN);
      varcontainerData={
        width:Math.max(container.offsetWidth,Number(options.minContainerWidth)||200),
        height:Math.max(container.offsetHeight,Number(options.minContainerHeight)||100)
      };
      this.containerData=containerData;
      setStyle(cropper,{
        width:containerData.width,
        height:containerData.height
      });
      addClass(element,CLASS_HIDDEN);
      removeClass(cropper,CLASS_HIDDEN);
    },
    //Canvas(imagewrapper)
    initCanvas:functioninitCanvas(){
      varcontainerData=this.containerData,
          imageData=this.imageData;
      varviewMode=this.options.viewMode;
      varrotated=Math.abs(imageData.rotate)%180===90;
      varnaturalWidth=rotated?imageData.naturalHeight:imageData.naturalWidth;
      varnaturalHeight=rotated?imageData.naturalWidth:imageData.naturalHeight;
      varaspectRatio=naturalWidth/naturalHeight;
      varcanvasWidth=containerData.width;
      varcanvasHeight=containerData.height;

      if(containerData.height*aspectRatio>containerData.width){
        if(viewMode===3){
          canvasWidth=containerData.height*aspectRatio;
        }else{
          canvasHeight=containerData.width/aspectRatio;
        }
      }elseif(viewMode===3){
        canvasHeight=containerData.width/aspectRatio;
      }else{
        canvasWidth=containerData.height*aspectRatio;
      }

      varcanvasData={
        aspectRatio:aspectRatio,
        naturalWidth:naturalWidth,
        naturalHeight:naturalHeight,
        width:canvasWidth,
        height:canvasHeight
      };
      canvasData.left=(containerData.width-canvasWidth)/2;
      canvasData.top=(containerData.height-canvasHeight)/2;
      canvasData.oldLeft=canvasData.left;
      canvasData.oldTop=canvasData.top;
      this.canvasData=canvasData;
      this.limited=viewMode===1||viewMode===2;
      this.limitCanvas(true,true);
      this.initialImageData=assign({},imageData);
      this.initialCanvasData=assign({},canvasData);
    },
    limitCanvas:functionlimitCanvas(sizeLimited,positionLimited){
      varoptions=this.options,
          containerData=this.containerData,
          canvasData=this.canvasData,
          cropBoxData=this.cropBoxData;
      varviewMode=options.viewMode;
      varaspectRatio=canvasData.aspectRatio;
      varcropped=this.cropped&&cropBoxData;

      if(sizeLimited){
        varminCanvasWidth=Number(options.minCanvasWidth)||0;
        varminCanvasHeight=Number(options.minCanvasHeight)||0;

        if(viewMode>1){
          minCanvasWidth=Math.max(minCanvasWidth,containerData.width);
          minCanvasHeight=Math.max(minCanvasHeight,containerData.height);

          if(viewMode===3){
            if(minCanvasHeight*aspectRatio>minCanvasWidth){
              minCanvasWidth=minCanvasHeight*aspectRatio;
            }else{
              minCanvasHeight=minCanvasWidth/aspectRatio;
            }
          }
        }elseif(viewMode>0){
          if(minCanvasWidth){
            minCanvasWidth=Math.max(minCanvasWidth,cropped?cropBoxData.width:0);
          }elseif(minCanvasHeight){
            minCanvasHeight=Math.max(minCanvasHeight,cropped?cropBoxData.height:0);
          }elseif(cropped){
            minCanvasWidth=cropBoxData.width;
            minCanvasHeight=cropBoxData.height;

            if(minCanvasHeight*aspectRatio>minCanvasWidth){
              minCanvasWidth=minCanvasHeight*aspectRatio;
            }else{
              minCanvasHeight=minCanvasWidth/aspectRatio;
            }
          }
        }

        var_getAdjustedSizes=getAdjustedSizes({
          aspectRatio:aspectRatio,
          width:minCanvasWidth,
          height:minCanvasHeight
        });

        minCanvasWidth=_getAdjustedSizes.width;
        minCanvasHeight=_getAdjustedSizes.height;
        canvasData.minWidth=minCanvasWidth;
        canvasData.minHeight=minCanvasHeight;
        canvasData.maxWidth=Infinity;
        canvasData.maxHeight=Infinity;
      }

      if(positionLimited){
        if(viewMode>(cropped?0:1)){
          varnewCanvasLeft=containerData.width-canvasData.width;
          varnewCanvasTop=containerData.height-canvasData.height;
          canvasData.minLeft=Math.min(0,newCanvasLeft);
          canvasData.minTop=Math.min(0,newCanvasTop);
          canvasData.maxLeft=Math.max(0,newCanvasLeft);
          canvasData.maxTop=Math.max(0,newCanvasTop);

          if(cropped&&this.limited){
            canvasData.minLeft=Math.min(cropBoxData.left,cropBoxData.left+(cropBoxData.width-canvasData.width));
            canvasData.minTop=Math.min(cropBoxData.top,cropBoxData.top+(cropBoxData.height-canvasData.height));
            canvasData.maxLeft=cropBoxData.left;
            canvasData.maxTop=cropBoxData.top;

            if(viewMode===2){
              if(canvasData.width>=containerData.width){
                canvasData.minLeft=Math.min(0,newCanvasLeft);
                canvasData.maxLeft=Math.max(0,newCanvasLeft);
              }

              if(canvasData.height>=containerData.height){
                canvasData.minTop=Math.min(0,newCanvasTop);
                canvasData.maxTop=Math.max(0,newCanvasTop);
              }
            }
          }
        }else{
          canvasData.minLeft=-canvasData.width;
          canvasData.minTop=-canvasData.height;
          canvasData.maxLeft=containerData.width;
          canvasData.maxTop=containerData.height;
        }
      }
    },
    renderCanvas:functionrenderCanvas(changed,transformed){
      varcanvasData=this.canvasData,
          imageData=this.imageData;

      if(transformed){
        var_getRotatedSizes=getRotatedSizes({
          width:imageData.naturalWidth*Math.abs(imageData.scaleX||1),
          height:imageData.naturalHeight*Math.abs(imageData.scaleY||1),
          degree:imageData.rotate||0
        }),
            naturalWidth=_getRotatedSizes.width,
            naturalHeight=_getRotatedSizes.height;

        varwidth=canvasData.width*(naturalWidth/canvasData.naturalWidth);
        varheight=canvasData.height*(naturalHeight/canvasData.naturalHeight);
        canvasData.left-=(width-canvasData.width)/2;
        canvasData.top-=(height-canvasData.height)/2;
        canvasData.width=width;
        canvasData.height=height;
        canvasData.aspectRatio=naturalWidth/naturalHeight;
        canvasData.naturalWidth=naturalWidth;
        canvasData.naturalHeight=naturalHeight;
        this.limitCanvas(true,false);
      }

      if(canvasData.width>canvasData.maxWidth||canvasData.width<canvasData.minWidth){
        canvasData.left=canvasData.oldLeft;
      }

      if(canvasData.height>canvasData.maxHeight||canvasData.height<canvasData.minHeight){
        canvasData.top=canvasData.oldTop;
      }

      canvasData.width=Math.min(Math.max(canvasData.width,canvasData.minWidth),canvasData.maxWidth);
      canvasData.height=Math.min(Math.max(canvasData.height,canvasData.minHeight),canvasData.maxHeight);
      this.limitCanvas(false,true);
      canvasData.left=Math.min(Math.max(canvasData.left,canvasData.minLeft),canvasData.maxLeft);
      canvasData.top=Math.min(Math.max(canvasData.top,canvasData.minTop),canvasData.maxTop);
      canvasData.oldLeft=canvasData.left;
      canvasData.oldTop=canvasData.top;
      setStyle(this.canvas,assign({
        width:canvasData.width,
        height:canvasData.height
      },getTransforms({
        translateX:canvasData.left,
        translateY:canvasData.top
      })));
      this.renderImage(changed);

      if(this.cropped&&this.limited){
        this.limitCropBox(true,true);
      }
    },
    renderImage:functionrenderImage(changed){
      varcanvasData=this.canvasData,
          imageData=this.imageData;
      varwidth=imageData.naturalWidth*(canvasData.width/canvasData.naturalWidth);
      varheight=imageData.naturalHeight*(canvasData.height/canvasData.naturalHeight);
      assign(imageData,{
        width:width,
        height:height,
        left:(canvasData.width-width)/2,
        top:(canvasData.height-height)/2
      });
      setStyle(this.image,assign({
        width:imageData.width,
        height:imageData.height
      },getTransforms(assign({
        translateX:imageData.left,
        translateY:imageData.top
      },imageData))));

      if(changed){
        this.output();
      }
    },
    initCropBox:functioninitCropBox(){
      varoptions=this.options,
          canvasData=this.canvasData;
      varaspectRatio=options.aspectRatio||options.initialAspectRatio;
      varautoCropArea=Number(options.autoCropArea)||0.8;
      varcropBoxData={
        width:canvasData.width,
        height:canvasData.height
      };

      if(aspectRatio){
        if(canvasData.height*aspectRatio>canvasData.width){
          cropBoxData.height=cropBoxData.width/aspectRatio;
        }else{
          cropBoxData.width=cropBoxData.height*aspectRatio;
        }
      }

      this.cropBoxData=cropBoxData;
      this.limitCropBox(true,true);//Initializeautocroparea

      cropBoxData.width=Math.min(Math.max(cropBoxData.width,cropBoxData.minWidth),cropBoxData.maxWidth);
      cropBoxData.height=Math.min(Math.max(cropBoxData.height,cropBoxData.minHeight),cropBoxData.maxHeight);//Thewidth/heightofautocropareamustlargethan"minWidth/Height"

      cropBoxData.width=Math.max(cropBoxData.minWidth,cropBoxData.width*autoCropArea);
      cropBoxData.height=Math.max(cropBoxData.minHeight,cropBoxData.height*autoCropArea);
      cropBoxData.left=canvasData.left+(canvasData.width-cropBoxData.width)/2;
      cropBoxData.top=canvasData.top+(canvasData.height-cropBoxData.height)/2;
      cropBoxData.oldLeft=cropBoxData.left;
      cropBoxData.oldTop=cropBoxData.top;
      this.initialCropBoxData=assign({},cropBoxData);
    },
    limitCropBox:functionlimitCropBox(sizeLimited,positionLimited){
      varoptions=this.options,
          containerData=this.containerData,
          canvasData=this.canvasData,
          cropBoxData=this.cropBoxData,
          limited=this.limited;
      varaspectRatio=options.aspectRatio;

      if(sizeLimited){
        varminCropBoxWidth=Number(options.minCropBoxWidth)||0;
        varminCropBoxHeight=Number(options.minCropBoxHeight)||0;
        varmaxCropBoxWidth=limited?Math.min(containerData.width,canvasData.width,canvasData.width+canvasData.left,containerData.width-canvasData.left):containerData.width;
        varmaxCropBoxHeight=limited?Math.min(containerData.height,canvasData.height,canvasData.height+canvasData.top,containerData.height-canvasData.top):containerData.height;//Themin/maxCropBoxWidth/Heightmustbelessthancontainer'swidth/height

        minCropBoxWidth=Math.min(minCropBoxWidth,containerData.width);
        minCropBoxHeight=Math.min(minCropBoxHeight,containerData.height);

        if(aspectRatio){
          if(minCropBoxWidth&&minCropBoxHeight){
            if(minCropBoxHeight*aspectRatio>minCropBoxWidth){
              minCropBoxHeight=minCropBoxWidth/aspectRatio;
            }else{
              minCropBoxWidth=minCropBoxHeight*aspectRatio;
            }
          }elseif(minCropBoxWidth){
            minCropBoxHeight=minCropBoxWidth/aspectRatio;
          }elseif(minCropBoxHeight){
            minCropBoxWidth=minCropBoxHeight*aspectRatio;
          }

          if(maxCropBoxHeight*aspectRatio>maxCropBoxWidth){
            maxCropBoxHeight=maxCropBoxWidth/aspectRatio;
          }else{
            maxCropBoxWidth=maxCropBoxHeight*aspectRatio;
          }
        }//TheminWidth/HeightmustbelessthanmaxWidth/Height


        cropBoxData.minWidth=Math.min(minCropBoxWidth,maxCropBoxWidth);
        cropBoxData.minHeight=Math.min(minCropBoxHeight,maxCropBoxHeight);
        cropBoxData.maxWidth=maxCropBoxWidth;
        cropBoxData.maxHeight=maxCropBoxHeight;
      }

      if(positionLimited){
        if(limited){
          cropBoxData.minLeft=Math.max(0,canvasData.left);
          cropBoxData.minTop=Math.max(0,canvasData.top);
          cropBoxData.maxLeft=Math.min(containerData.width,canvasData.left+canvasData.width)-cropBoxData.width;
          cropBoxData.maxTop=Math.min(containerData.height,canvasData.top+canvasData.height)-cropBoxData.height;
        }else{
          cropBoxData.minLeft=0;
          cropBoxData.minTop=0;
          cropBoxData.maxLeft=containerData.width-cropBoxData.width;
          cropBoxData.maxTop=containerData.height-cropBoxData.height;
        }
      }
    },
    renderCropBox:functionrenderCropBox(){
      varoptions=this.options,
          containerData=this.containerData,
          cropBoxData=this.cropBoxData;

      if(cropBoxData.width>cropBoxData.maxWidth||cropBoxData.width<cropBoxData.minWidth){
        cropBoxData.left=cropBoxData.oldLeft;
      }

      if(cropBoxData.height>cropBoxData.maxHeight||cropBoxData.height<cropBoxData.minHeight){
        cropBoxData.top=cropBoxData.oldTop;
      }

      cropBoxData.width=Math.min(Math.max(cropBoxData.width,cropBoxData.minWidth),cropBoxData.maxWidth);
      cropBoxData.height=Math.min(Math.max(cropBoxData.height,cropBoxData.minHeight),cropBoxData.maxHeight);
      this.limitCropBox(false,true);
      cropBoxData.left=Math.min(Math.max(cropBoxData.left,cropBoxData.minLeft),cropBoxData.maxLeft);
      cropBoxData.top=Math.min(Math.max(cropBoxData.top,cropBoxData.minTop),cropBoxData.maxTop);
      cropBoxData.oldLeft=cropBoxData.left;
      cropBoxData.oldTop=cropBoxData.top;

      if(options.movable&&options.cropBoxMovable){
        //Turntomovethecanvaswhenthecropboxisequaltothecontainer
        setData(this.face,DATA_ACTION,cropBoxData.width>=containerData.width&&cropBoxData.height>=containerData.height?ACTION_MOVE:ACTION_ALL);
      }

      setStyle(this.cropBox,assign({
        width:cropBoxData.width,
        height:cropBoxData.height
      },getTransforms({
        translateX:cropBoxData.left,
        translateY:cropBoxData.top
      })));

      if(this.cropped&&this.limited){
        this.limitCanvas(true,true);
      }

      if(!this.disabled){
        this.output();
      }
    },
    output:functionoutput(){
      this.preview();
      dispatchEvent(this.element,EVENT_CROP,this.getData());
    }
  };

  varpreview={
    initPreview:functioninitPreview(){
      varelement=this.element,
          crossOrigin=this.crossOrigin;
      varpreview=this.options.preview;
      varurl=crossOrigin?this.crossOriginUrl:this.url;
      varalt=element.alt||'Theimagetopreview';
      varimage=document.createElement('img');

      if(crossOrigin){
        image.crossOrigin=crossOrigin;
      }

      image.src=url;
      image.alt=alt;
      this.viewBox.appendChild(image);
      this.viewBoxImage=image;

      if(!preview){
        return;
      }

      varpreviews=preview;

      if(typeofpreview==='string'){
        previews=element.ownerDocument.querySelectorAll(preview);
      }elseif(preview.querySelector){
        previews=[preview];
      }

      this.previews=previews;
      forEach(previews,function(el){
        varimg=document.createElement('img');//Savetheoriginalsizeforrecover

        setData(el,DATA_PREVIEW,{
          width:el.offsetWidth,
          height:el.offsetHeight,
          html:el.innerHTML
        });

        if(crossOrigin){
          img.crossOrigin=crossOrigin;
        }

        img.src=url;
        img.alt=alt;
        /**
         *Overrideimgelementstyles
         *Add`display:block`toavoidmargintopissue
         *Add`height:auto`tooverride`height`attributeonIE8
         *(Occuronlywhenmargin-top<=-height)
         */

        img.style.cssText='display:block;'+'width:100%;'+'height:auto;'+'min-width:0!important;'+'min-height:0!important;'+'max-width:none!important;'+'max-height:none!important;'+'image-orientation:0deg!important;"';
        el.innerHTML='';
        el.appendChild(img);
      });
    },
    resetPreview:functionresetPreview(){
      forEach(this.previews,function(element){
        vardata=getData(element,DATA_PREVIEW);
        setStyle(element,{
          width:data.width,
          height:data.height
        });
        element.innerHTML=data.html;
        removeData(element,DATA_PREVIEW);
      });
    },
    preview:functionpreview(){
      varimageData=this.imageData,
          canvasData=this.canvasData,
          cropBoxData=this.cropBoxData;
      varcropBoxWidth=cropBoxData.width,
          cropBoxHeight=cropBoxData.height;
      varwidth=imageData.width,
          height=imageData.height;
      varleft=cropBoxData.left-canvasData.left-imageData.left;
      vartop=cropBoxData.top-canvasData.top-imageData.top;

      if(!this.cropped||this.disabled){
        return;
      }

      setStyle(this.viewBoxImage,assign({
        width:width,
        height:height
      },getTransforms(assign({
        translateX:-left,
        translateY:-top
      },imageData))));
      forEach(this.previews,function(element){
        vardata=getData(element,DATA_PREVIEW);
        varoriginalWidth=data.width;
        varoriginalHeight=data.height;
        varnewWidth=originalWidth;
        varnewHeight=originalHeight;
        varratio=1;

        if(cropBoxWidth){
          ratio=originalWidth/cropBoxWidth;
          newHeight=cropBoxHeight*ratio;
        }

        if(cropBoxHeight&&newHeight>originalHeight){
          ratio=originalHeight/cropBoxHeight;
          newWidth=cropBoxWidth*ratio;
          newHeight=originalHeight;
        }

        setStyle(element,{
          width:newWidth,
          height:newHeight
        });
        setStyle(element.getElementsByTagName('img')[0],assign({
          width:width*ratio,
          height:height*ratio
        },getTransforms(assign({
          translateX:-left*ratio,
          translateY:-top*ratio
        },imageData))));
      });
    }
  };

  varevents={
    bind:functionbind(){
      varelement=this.element,
          options=this.options,
          cropper=this.cropper;

      if(isFunction(options.cropstart)){
        addListener(element,EVENT_CROP_START,options.cropstart);
      }

      if(isFunction(options.cropmove)){
        addListener(element,EVENT_CROP_MOVE,options.cropmove);
      }

      if(isFunction(options.cropend)){
        addListener(element,EVENT_CROP_END,options.cropend);
      }

      if(isFunction(options.crop)){
        addListener(element,EVENT_CROP,options.crop);
      }

      if(isFunction(options.zoom)){
        addListener(element,EVENT_ZOOM,options.zoom);
      }

      addListener(cropper,EVENT_POINTER_DOWN,this.onCropStart=this.cropStart.bind(this));

      if(options.zoomable&&options.zoomOnWheel){
        addListener(cropper,EVENT_WHEEL,this.onWheel=this.wheel.bind(this),{
          passive:false,
          capture:true
        });
      }

      if(options.toggleDragModeOnDblclick){
        addListener(cropper,EVENT_DBLCLICK,this.onDblclick=this.dblclick.bind(this));
      }

      addListener(element.ownerDocument,EVENT_POINTER_MOVE,this.onCropMove=this.cropMove.bind(this));
      addListener(element.ownerDocument,EVENT_POINTER_UP,this.onCropEnd=this.cropEnd.bind(this));

      if(options.responsive){
        addListener(window,EVENT_RESIZE,this.onResize=this.resize.bind(this));
      }
    },
    unbind:functionunbind(){
      varelement=this.element,
          options=this.options,
          cropper=this.cropper;

      if(isFunction(options.cropstart)){
        removeListener(element,EVENT_CROP_START,options.cropstart);
      }

      if(isFunction(options.cropmove)){
        removeListener(element,EVENT_CROP_MOVE,options.cropmove);
      }

      if(isFunction(options.cropend)){
        removeListener(element,EVENT_CROP_END,options.cropend);
      }

      if(isFunction(options.crop)){
        removeListener(element,EVENT_CROP,options.crop);
      }

      if(isFunction(options.zoom)){
        removeListener(element,EVENT_ZOOM,options.zoom);
      }

      removeListener(cropper,EVENT_POINTER_DOWN,this.onCropStart);

      if(options.zoomable&&options.zoomOnWheel){
        removeListener(cropper,EVENT_WHEEL,this.onWheel,{
          passive:false,
          capture:true
        });
      }

      if(options.toggleDragModeOnDblclick){
        removeListener(cropper,EVENT_DBLCLICK,this.onDblclick);
      }

      removeListener(element.ownerDocument,EVENT_POINTER_MOVE,this.onCropMove);
      removeListener(element.ownerDocument,EVENT_POINTER_UP,this.onCropEnd);

      if(options.responsive){
        removeListener(window,EVENT_RESIZE,this.onResize);
      }
    }
  };

  varhandlers={
    resize:functionresize(){
      varoptions=this.options,
          container=this.container,
          containerData=this.containerData;
      varminContainerWidth=Number(options.minContainerWidth)||MIN_CONTAINER_WIDTH;
      varminContainerHeight=Number(options.minContainerHeight)||MIN_CONTAINER_HEIGHT;

      if(this.disabled||containerData.width<=minContainerWidth||containerData.height<=minContainerHeight){
        return;
      }

      varratio=container.offsetWidth/containerData.width;//Resizewhenwidthchangedorheightchanged

      if(ratio!==1||container.offsetHeight!==containerData.height){
        varcanvasData;
        varcropBoxData;

        if(options.restore){
          canvasData=this.getCanvasData();
          cropBoxData=this.getCropBoxData();
        }

        this.render();

        if(options.restore){
          this.setCanvasData(forEach(canvasData,function(n,i){
            canvasData[i]=n*ratio;
          }));
          this.setCropBoxData(forEach(cropBoxData,function(n,i){
            cropBoxData[i]=n*ratio;
          }));
        }
      }
    },
    dblclick:functiondblclick(){
      if(this.disabled||this.options.dragMode===DRAG_MODE_NONE){
        return;
      }

      this.setDragMode(hasClass(this.dragBox,CLASS_CROP)?DRAG_MODE_MOVE:DRAG_MODE_CROP);
    },
    wheel:functionwheel(event){
      var_this=this;

      varratio=Number(this.options.wheelZoomRatio)||0.1;
      vardelta=1;

      if(this.disabled){
        return;
      }

      event.preventDefault();//Limitwheelspeedtopreventzoomtoofast(#21)

      if(this.wheeling){
        return;
      }

      this.wheeling=true;
      setTimeout(function(){
        _this.wheeling=false;
      },50);

      if(event.deltaY){
        delta=event.deltaY>0?1:-1;
      }elseif(event.wheelDelta){
        delta=-event.wheelDelta/120;
      }elseif(event.detail){
        delta=event.detail>0?1:-1;
      }

      this.zoom(-delta*ratio,event);
    },
    cropStart:functioncropStart(event){
      varbuttons=event.buttons,
          button=event.button;

      if(this.disabled//Noprimarybutton(Usuallytheleftbutton)
      //Notethattoucheventshaveno`buttons`or`button`property
      ||isNumber(buttons)&&buttons!==1||isNumber(button)&&button!==0//Opencontextmenu
      ||event.ctrlKey){
        return;
      }

      varoptions=this.options,
          pointers=this.pointers;
      varaction;

      if(event.changedTouches){
        //Handletouchevent
        forEach(event.changedTouches,function(touch){
          pointers[touch.identifier]=getPointer(touch);
        });
      }else{
        //Handlemouseeventandpointerevent
        pointers[event.pointerId||0]=getPointer(event);
      }

      if(Object.keys(pointers).length>1&&options.zoomable&&options.zoomOnTouch){
        action=ACTION_ZOOM;
      }else{
        action=getData(event.target,DATA_ACTION);
      }

      if(!REGEXP_ACTIONS.test(action)){
        return;
      }

      if(dispatchEvent(this.element,EVENT_CROP_START,{
        originalEvent:event,
        action:action
      })===false){
        return;
      }//ThislineisrequiredforpreventingpagezoominginiOSbrowsers


      event.preventDefault();
      this.action=action;
      this.cropping=false;

      if(action===ACTION_CROP){
        this.cropping=true;
        addClass(this.dragBox,CLASS_MODAL);
      }
    },
    cropMove:functioncropMove(event){
      varaction=this.action;

      if(this.disabled||!action){
        return;
      }

      varpointers=this.pointers;
      event.preventDefault();

      if(dispatchEvent(this.element,EVENT_CROP_MOVE,{
        originalEvent:event,
        action:action
      })===false){
        return;
      }

      if(event.changedTouches){
        forEach(event.changedTouches,function(touch){
          //Thefirstparametershouldnotbeundefined(#432)
          assign(pointers[touch.identifier]||{},getPointer(touch,true));
        });
      }else{
        assign(pointers[event.pointerId||0]||{},getPointer(event,true));
      }

      this.change(event);
    },
    cropEnd:functioncropEnd(event){
      if(this.disabled){
        return;
      }

      varaction=this.action,
          pointers=this.pointers;

      if(event.changedTouches){
        forEach(event.changedTouches,function(touch){
          deletepointers[touch.identifier];
        });
      }else{
        deletepointers[event.pointerId||0];
      }

      if(!action){
        return;
      }

      event.preventDefault();

      if(!Object.keys(pointers).length){
        this.action='';
      }

      if(this.cropping){
        this.cropping=false;
        toggleClass(this.dragBox,CLASS_MODAL,this.cropped&&this.options.modal);
      }

      dispatchEvent(this.element,EVENT_CROP_END,{
        originalEvent:event,
        action:action
      });
    }
  };

  varchange={
    change:functionchange(event){
      varoptions=this.options,
          canvasData=this.canvasData,
          containerData=this.containerData,
          cropBoxData=this.cropBoxData,
          pointers=this.pointers;
      varaction=this.action;
      varaspectRatio=options.aspectRatio;
      varleft=cropBoxData.left,
          top=cropBoxData.top,
          width=cropBoxData.width,
          height=cropBoxData.height;
      varright=left+width;
      varbottom=top+height;
      varminLeft=0;
      varminTop=0;
      varmaxWidth=containerData.width;
      varmaxHeight=containerData.height;
      varrenderable=true;
      varoffset;//Lockingaspectratioin"freemode"byholdingshiftkey

      if(!aspectRatio&&event.shiftKey){
        aspectRatio=width&&height?width/height:1;
      }

      if(this.limited){
        minLeft=cropBoxData.minLeft;
        minTop=cropBoxData.minTop;
        maxWidth=minLeft+Math.min(containerData.width,canvasData.width,canvasData.left+canvasData.width);
        maxHeight=minTop+Math.min(containerData.height,canvasData.height,canvasData.top+canvasData.height);
      }

      varpointer=pointers[Object.keys(pointers)[0]];
      varrange={
        x:pointer.endX-pointer.startX,
        y:pointer.endY-pointer.startY
      };

      varcheck=functioncheck(side){
        switch(side){
          caseACTION_EAST:
            if(right+range.x>maxWidth){
              range.x=maxWidth-right;
            }

            break;

          caseACTION_WEST:
            if(left+range.x<minLeft){
              range.x=minLeft-left;
            }

            break;

          caseACTION_NORTH:
            if(top+range.y<minTop){
              range.y=minTop-top;
            }

            break;

          caseACTION_SOUTH:
            if(bottom+range.y>maxHeight){
              range.y=maxHeight-bottom;
            }

            break;

          default:
        }
      };

      switch(action){
        //Movecropbox
        caseACTION_ALL:
          left+=range.x;
          top+=range.y;
          break;
        //Resizecropbox

        caseACTION_EAST:
          if(range.x>=0&&(right>=maxWidth||aspectRatio&&(top<=minTop||bottom>=maxHeight))){
            renderable=false;
            break;
          }

          check(ACTION_EAST);
          width+=range.x;

          if(width<0){
            action=ACTION_WEST;
            width=-width;
            left-=width;
          }

          if(aspectRatio){
            height=width/aspectRatio;
            top+=(cropBoxData.height-height)/2;
          }

          break;

        caseACTION_NORTH:
          if(range.y<=0&&(top<=minTop||aspectRatio&&(left<=minLeft||right>=maxWidth))){
            renderable=false;
            break;
          }

          check(ACTION_NORTH);
          height-=range.y;
          top+=range.y;

          if(height<0){
            action=ACTION_SOUTH;
            height=-height;
            top-=height;
          }

          if(aspectRatio){
            width=height*aspectRatio;
            left+=(cropBoxData.width-width)/2;
          }

          break;

        caseACTION_WEST:
          if(range.x<=0&&(left<=minLeft||aspectRatio&&(top<=minTop||bottom>=maxHeight))){
            renderable=false;
            break;
          }

          check(ACTION_WEST);
          width-=range.x;
          left+=range.x;

          if(width<0){
            action=ACTION_EAST;
            width=-width;
            left-=width;
          }

          if(aspectRatio){
            height=width/aspectRatio;
            top+=(cropBoxData.height-height)/2;
          }

          break;

        caseACTION_SOUTH:
          if(range.y>=0&&(bottom>=maxHeight||aspectRatio&&(left<=minLeft||right>=maxWidth))){
            renderable=false;
            break;
          }

          check(ACTION_SOUTH);
          height+=range.y;

          if(height<0){
            action=ACTION_NORTH;
            height=-height;
            top-=height;
          }

          if(aspectRatio){
            width=height*aspectRatio;
            left+=(cropBoxData.width-width)/2;
          }

          break;

        caseACTION_NORTH_EAST:
          if(aspectRatio){
            if(range.y<=0&&(top<=minTop||right>=maxWidth)){
              renderable=false;
              break;
            }

            check(ACTION_NORTH);
            height-=range.y;
            top+=range.y;
            width=height*aspectRatio;
          }else{
            check(ACTION_NORTH);
            check(ACTION_EAST);

            if(range.x>=0){
              if(right<maxWidth){
                width+=range.x;
              }elseif(range.y<=0&&top<=minTop){
                renderable=false;
              }
            }else{
              width+=range.x;
            }

            if(range.y<=0){
              if(top>minTop){
                height-=range.y;
                top+=range.y;
              }
            }else{
              height-=range.y;
              top+=range.y;
            }
          }

          if(width<0&&height<0){
            action=ACTION_SOUTH_WEST;
            height=-height;
            width=-width;
            top-=height;
            left-=width;
          }elseif(width<0){
            action=ACTION_NORTH_WEST;
            width=-width;
            left-=width;
          }elseif(height<0){
            action=ACTION_SOUTH_EAST;
            height=-height;
            top-=height;
          }

          break;

        caseACTION_NORTH_WEST:
          if(aspectRatio){
            if(range.y<=0&&(top<=minTop||left<=minLeft)){
              renderable=false;
              break;
            }

            check(ACTION_NORTH);
            height-=range.y;
            top+=range.y;
            width=height*aspectRatio;
            left+=cropBoxData.width-width;
          }else{
            check(ACTION_NORTH);
            check(ACTION_WEST);

            if(range.x<=0){
              if(left>minLeft){
                width-=range.x;
                left+=range.x;
              }elseif(range.y<=0&&top<=minTop){
                renderable=false;
              }
            }else{
              width-=range.x;
              left+=range.x;
            }

            if(range.y<=0){
              if(top>minTop){
                height-=range.y;
                top+=range.y;
              }
            }else{
              height-=range.y;
              top+=range.y;
            }
          }

          if(width<0&&height<0){
            action=ACTION_SOUTH_EAST;
            height=-height;
            width=-width;
            top-=height;
            left-=width;
          }elseif(width<0){
            action=ACTION_NORTH_EAST;
            width=-width;
            left-=width;
          }elseif(height<0){
            action=ACTION_SOUTH_WEST;
            height=-height;
            top-=height;
          }

          break;

        caseACTION_SOUTH_WEST:
          if(aspectRatio){
            if(range.x<=0&&(left<=minLeft||bottom>=maxHeight)){
              renderable=false;
              break;
            }

            check(ACTION_WEST);
            width-=range.x;
            left+=range.x;
            height=width/aspectRatio;
          }else{
            check(ACTION_SOUTH);
            check(ACTION_WEST);

            if(range.x<=0){
              if(left>minLeft){
                width-=range.x;
                left+=range.x;
              }elseif(range.y>=0&&bottom>=maxHeight){
                renderable=false;
              }
            }else{
              width-=range.x;
              left+=range.x;
            }

            if(range.y>=0){
              if(bottom<maxHeight){
                height+=range.y;
              }
            }else{
              height+=range.y;
            }
          }

          if(width<0&&height<0){
            action=ACTION_NORTH_EAST;
            height=-height;
            width=-width;
            top-=height;
            left-=width;
          }elseif(width<0){
            action=ACTION_SOUTH_EAST;
            width=-width;
            left-=width;
          }elseif(height<0){
            action=ACTION_NORTH_WEST;
            height=-height;
            top-=height;
          }

          break;

        caseACTION_SOUTH_EAST:
          if(aspectRatio){
            if(range.x>=0&&(right>=maxWidth||bottom>=maxHeight)){
              renderable=false;
              break;
            }

            check(ACTION_EAST);
            width+=range.x;
            height=width/aspectRatio;
          }else{
            check(ACTION_SOUTH);
            check(ACTION_EAST);

            if(range.x>=0){
              if(right<maxWidth){
                width+=range.x;
              }elseif(range.y>=0&&bottom>=maxHeight){
                renderable=false;
              }
            }else{
              width+=range.x;
            }

            if(range.y>=0){
              if(bottom<maxHeight){
                height+=range.y;
              }
            }else{
              height+=range.y;
            }
          }

          if(width<0&&height<0){
            action=ACTION_NORTH_WEST;
            height=-height;
            width=-width;
            top-=height;
            left-=width;
          }elseif(width<0){
            action=ACTION_SOUTH_WEST;
            width=-width;
            left-=width;
          }elseif(height<0){
            action=ACTION_NORTH_EAST;
            height=-height;
            top-=height;
          }

          break;
        //Movecanvas

        caseACTION_MOVE:
          this.move(range.x,range.y);
          renderable=false;
          break;
        //Zoomcanvas

        caseACTION_ZOOM:
          this.zoom(getMaxZoomRatio(pointers),event);
          renderable=false;
          break;
        //Createcropbox

        caseACTION_CROP:
          if(!range.x||!range.y){
            renderable=false;
            break;
          }

          offset=getOffset(this.cropper);
          left=pointer.startX-offset.left;
          top=pointer.startY-offset.top;
          width=cropBoxData.minWidth;
          height=cropBoxData.minHeight;

          if(range.x>0){
            action=range.y>0?ACTION_SOUTH_EAST:ACTION_NORTH_EAST;
          }elseif(range.x<0){
            left-=width;
            action=range.y>0?ACTION_SOUTH_WEST:ACTION_NORTH_WEST;
          }

          if(range.y<0){
            top-=height;
          }//Showthecropboxifishidden


          if(!this.cropped){
            removeClass(this.cropBox,CLASS_HIDDEN);
            this.cropped=true;

            if(this.limited){
              this.limitCropBox(true,true);
            }
          }

          break;

        default:
      }

      if(renderable){
        cropBoxData.width=width;
        cropBoxData.height=height;
        cropBoxData.left=left;
        cropBoxData.top=top;
        this.action=action;
        this.renderCropBox();
      }//Override


      forEach(pointers,function(p){
        p.startX=p.endX;
        p.startY=p.endY;
      });
    }
  };

  varmethods={
    //Showthecropboxmanually
    crop:functioncrop(){
      if(this.ready&&!this.cropped&&!this.disabled){
        this.cropped=true;
        this.limitCropBox(true,true);

        if(this.options.modal){
          addClass(this.dragBox,CLASS_MODAL);
        }

        removeClass(this.cropBox,CLASS_HIDDEN);
        this.setCropBoxData(this.initialCropBoxData);
      }

      returnthis;
    },
    //Resettheimageandcropboxtotheirinitialstates
    reset:functionreset(){
      if(this.ready&&!this.disabled){
        this.imageData=assign({},this.initialImageData);
        this.canvasData=assign({},this.initialCanvasData);
        this.cropBoxData=assign({},this.initialCropBoxData);
        this.renderCanvas();

        if(this.cropped){
          this.renderCropBox();
        }
      }

      returnthis;
    },
    //Clearthecropbox
    clear:functionclear(){
      if(this.cropped&&!this.disabled){
        assign(this.cropBoxData,{
          left:0,
          top:0,
          width:0,
          height:0
        });
        this.cropped=false;
        this.renderCropBox();
        this.limitCanvas(true,true);//Rendercanvasaftercropboxrendered

        this.renderCanvas();
        removeClass(this.dragBox,CLASS_MODAL);
        addClass(this.cropBox,CLASS_HIDDEN);
      }

      returnthis;
    },

    /**
     *Replacetheimage'ssrcandrebuildthecropper
     *@param{string}url-ThenewURL.
     *@param{boolean}[hasSameSize]-Indicateifthenewimagehasthesamesizeastheoldone.
     *@returns{Cropper}this
     */
    replace:functionreplace(url){
      varhasSameSize=arguments.length>1&&arguments[1]!==undefined?arguments[1]:false;

      if(!this.disabled&&url){
        if(this.isImg){
          this.element.src=url;
        }

        if(hasSameSize){
          this.url=url;
          this.image.src=url;

          if(this.ready){
            this.viewBoxImage.src=url;
            forEach(this.previews,function(element){
              element.getElementsByTagName('img')[0].src=url;
            });
          }
        }else{
          if(this.isImg){
            this.replaced=true;
          }

          this.options.data=null;
          this.uncreate();
          this.load(url);
        }
      }

      returnthis;
    },
    //Enable(unfreeze)thecropper
    enable:functionenable(){
      if(this.ready&&this.disabled){
        this.disabled=false;
        removeClass(this.cropper,CLASS_DISABLED);
      }

      returnthis;
    },
    //Disable(freeze)thecropper
    disable:functiondisable(){
      if(this.ready&&!this.disabled){
        this.disabled=true;
        addClass(this.cropper,CLASS_DISABLED);
      }

      returnthis;
    },

    /**
     *Destroythecropperandremovetheinstancefromtheimage
     *@returns{Cropper}this
     */
    destroy:functiondestroy(){
      varelement=this.element;

      if(!element[NAMESPACE]){
        returnthis;
      }

      element[NAMESPACE]=undefined;

      if(this.isImg&&this.replaced){
        element.src=this.originalUrl;
      }

      this.uncreate();
      returnthis;
    },

    /**
     *Movethecanvaswithrelativeoffsets
     *@param{number}offsetX-Therelativeoffsetdistanceonthex-axis.
     *@param{number}[offsetY=offsetX]-Therelativeoffsetdistanceonthey-axis.
     *@returns{Cropper}this
     */
    move:functionmove(offsetX){
      varoffsetY=arguments.length>1&&arguments[1]!==undefined?arguments[1]:offsetX;
      var_this$canvasData=this.canvasData,
          left=_this$canvasData.left,
          top=_this$canvasData.top;
      returnthis.moveTo(isUndefined(offsetX)?offsetX:left+Number(offsetX),isUndefined(offsetY)?offsetY:top+Number(offsetY));
    },

    /**
     *Movethecanvastoanabsolutepoint
     *@param{number}x-Thex-axiscoordinate.
     *@param{number}[y=x]-They-axiscoordinate.
     *@returns{Cropper}this
     */
    moveTo:functionmoveTo(x){
      vary=arguments.length>1&&arguments[1]!==undefined?arguments[1]:x;
      varcanvasData=this.canvasData;
      varchanged=false;
      x=Number(x);
      y=Number(y);

      if(this.ready&&!this.disabled&&this.options.movable){
        if(isNumber(x)){
          canvasData.left=x;
          changed=true;
        }

        if(isNumber(y)){
          canvasData.top=y;
          changed=true;
        }

        if(changed){
          this.renderCanvas(true);
        }
      }

      returnthis;
    },

    /**
     *Zoomthecanvaswitharelativeratio
     *@param{number}ratio-Thetargetratio.
     *@param{Event}_originalEvent-Theoriginaleventifany.
     *@returns{Cropper}this
     */
    zoom:functionzoom(ratio,_originalEvent){
      varcanvasData=this.canvasData;
      ratio=Number(ratio);

      if(ratio<0){
        ratio=1/(1-ratio);
      }else{
        ratio=1+ratio;
      }

      returnthis.zoomTo(canvasData.width*ratio/canvasData.naturalWidth,null,_originalEvent);
    },

    /**
     *Zoomthecanvastoanabsoluteratio
     *@param{number}ratio-Thetargetratio.
     *@param{Object}pivot-Thezoompivotpointcoordinate.
     *@param{Event}_originalEvent-Theoriginaleventifany.
     *@returns{Cropper}this
     */
    zoomTo:functionzoomTo(ratio,pivot,_originalEvent){
      varoptions=this.options,
          canvasData=this.canvasData;
      varwidth=canvasData.width,
          height=canvasData.height,
          naturalWidth=canvasData.naturalWidth,
          naturalHeight=canvasData.naturalHeight;
      ratio=Number(ratio);

      if(ratio>=0&&this.ready&&!this.disabled&&options.zoomable){
        varnewWidth=naturalWidth*ratio;
        varnewHeight=naturalHeight*ratio;

        if(dispatchEvent(this.element,EVENT_ZOOM,{
          ratio:ratio,
          oldRatio:width/naturalWidth,
          originalEvent:_originalEvent
        })===false){
          returnthis;
        }

        if(_originalEvent){
          varpointers=this.pointers;
          varoffset=getOffset(this.cropper);
          varcenter=pointers&&Object.keys(pointers).length?getPointersCenter(pointers):{
            pageX:_originalEvent.pageX,
            pageY:_originalEvent.pageY
          };//Zoomfromthetriggeringpointoftheevent

          canvasData.left-=(newWidth-width)*((center.pageX-offset.left-canvasData.left)/width);
          canvasData.top-=(newHeight-height)*((center.pageY-offset.top-canvasData.top)/height);
        }elseif(isPlainObject(pivot)&&isNumber(pivot.x)&&isNumber(pivot.y)){
          canvasData.left-=(newWidth-width)*((pivot.x-canvasData.left)/width);
          canvasData.top-=(newHeight-height)*((pivot.y-canvasData.top)/height);
        }else{
          //Zoomfromthecenterofthecanvas
          canvasData.left-=(newWidth-width)/2;
          canvasData.top-=(newHeight-height)/2;
        }

        canvasData.width=newWidth;
        canvasData.height=newHeight;
        this.renderCanvas(true);
      }

      returnthis;
    },

    /**
     *Rotatethecanvaswitharelativedegree
     *@param{number}degree-Therotatedegree.
     *@returns{Cropper}this
     */
    rotate:functionrotate(degree){
      returnthis.rotateTo((this.imageData.rotate||0)+Number(degree));
    },

    /**
     *Rotatethecanvastoanabsolutedegree
     *@param{number}degree-Therotatedegree.
     *@returns{Cropper}this
     */
    rotateTo:functionrotateTo(degree){
      degree=Number(degree);

      if(isNumber(degree)&&this.ready&&!this.disabled&&this.options.rotatable){
        this.imageData.rotate=degree%360;
        this.renderCanvas(true,true);
      }

      returnthis;
    },

    /**
     *Scaletheimageonthex-axis.
     *@param{number}scaleX-Thescaleratioonthex-axis.
     *@returns{Cropper}this
     */
    scaleX:functionscaleX(_scaleX){
      varscaleY=this.imageData.scaleY;
      returnthis.scale(_scaleX,isNumber(scaleY)?scaleY:1);
    },

    /**
     *Scaletheimageonthey-axis.
     *@param{number}scaleY-Thescaleratioonthey-axis.
     *@returns{Cropper}this
     */
    scaleY:functionscaleY(_scaleY){
      varscaleX=this.imageData.scaleX;
      returnthis.scale(isNumber(scaleX)?scaleX:1,_scaleY);
    },

    /**
     *Scaletheimage
     *@param{number}scaleX-Thescaleratioonthex-axis.
     *@param{number}[scaleY=scaleX]-Thescaleratioonthey-axis.
     *@returns{Cropper}this
     */
    scale:functionscale(scaleX){
      varscaleY=arguments.length>1&&arguments[1]!==undefined?arguments[1]:scaleX;
      varimageData=this.imageData;
      vartransformed=false;
      scaleX=Number(scaleX);
      scaleY=Number(scaleY);

      if(this.ready&&!this.disabled&&this.options.scalable){
        if(isNumber(scaleX)){
          imageData.scaleX=scaleX;
          transformed=true;
        }

        if(isNumber(scaleY)){
          imageData.scaleY=scaleY;
          transformed=true;
        }

        if(transformed){
          this.renderCanvas(true,true);
        }
      }

      returnthis;
    },

    /**
     *Getthecroppedareapositionandsizedata(baseontheoriginalimage)
     *@param{boolean}[rounded=false]-Indicateifroundthedatavaluesornot.
     *@returns{Object}Theresultcroppeddata.
     */
    getData:functiongetData(){
      varrounded=arguments.length>0&&arguments[0]!==undefined?arguments[0]:false;
      varoptions=this.options,
          imageData=this.imageData,
          canvasData=this.canvasData,
          cropBoxData=this.cropBoxData;
      vardata;

      if(this.ready&&this.cropped){
        data={
          x:cropBoxData.left-canvasData.left,
          y:cropBoxData.top-canvasData.top,
          width:cropBoxData.width,
          height:cropBoxData.height
        };
        varratio=imageData.width/imageData.naturalWidth;
        forEach(data,function(n,i){
          data[i]=n/ratio;
        });

        if(rounded){
          //Incaseroundingoffleadstoextra1pxinrightorbottomborder
          //weshouldroundthetop-leftcornerandthedimension(#343).
          varbottom=Math.round(data.y+data.height);
          varright=Math.round(data.x+data.width);
          data.x=Math.round(data.x);
          data.y=Math.round(data.y);
          data.width=right-data.x;
          data.height=bottom-data.y;
        }
      }else{
        data={
          x:0,
          y:0,
          width:0,
          height:0
        };
      }

      if(options.rotatable){
        data.rotate=imageData.rotate||0;
      }

      if(options.scalable){
        data.scaleX=imageData.scaleX||1;
        data.scaleY=imageData.scaleY||1;
      }

      returndata;
    },

    /**
     *Setthecroppedareapositionandsizewithnewdata
     *@param{Object}data-Thenewdata.
     *@returns{Cropper}this
     */
    setData:functionsetData(data){
      varoptions=this.options,
          imageData=this.imageData,
          canvasData=this.canvasData;
      varcropBoxData={};

      if(this.ready&&!this.disabled&&isPlainObject(data)){
        vartransformed=false;

        if(options.rotatable){
          if(isNumber(data.rotate)&&data.rotate!==imageData.rotate){
            imageData.rotate=data.rotate;
            transformed=true;
          }
        }

        if(options.scalable){
          if(isNumber(data.scaleX)&&data.scaleX!==imageData.scaleX){
            imageData.scaleX=data.scaleX;
            transformed=true;
          }

          if(isNumber(data.scaleY)&&data.scaleY!==imageData.scaleY){
            imageData.scaleY=data.scaleY;
            transformed=true;
          }
        }

        if(transformed){
          this.renderCanvas(true,true);
        }

        varratio=imageData.width/imageData.naturalWidth;

        if(isNumber(data.x)){
          cropBoxData.left=data.x*ratio+canvasData.left;
        }

        if(isNumber(data.y)){
          cropBoxData.top=data.y*ratio+canvasData.top;
        }

        if(isNumber(data.width)){
          cropBoxData.width=data.width*ratio;
        }

        if(isNumber(data.height)){
          cropBoxData.height=data.height*ratio;
        }

        this.setCropBoxData(cropBoxData);
      }

      returnthis;
    },

    /**
     *Getthecontainersizedata.
     *@returns{Object}Theresultcontainerdata.
     */
    getContainerData:functiongetContainerData(){
      returnthis.ready?assign({},this.containerData):{};
    },

    /**
     *Gettheimagepositionandsizedata.
     *@returns{Object}Theresultimagedata.
     */
    getImageData:functiongetImageData(){
      returnthis.sized?assign({},this.imageData):{};
    },

    /**
     *Getthecanvaspositionandsizedata.
     *@returns{Object}Theresultcanvasdata.
     */
    getCanvasData:functiongetCanvasData(){
      varcanvasData=this.canvasData;
      vardata={};

      if(this.ready){
        forEach(['left','top','width','height','naturalWidth','naturalHeight'],function(n){
          data[n]=canvasData[n];
        });
      }

      returndata;
    },

    /**
     *Setthecanvaspositionandsizewithnewdata.
     *@param{Object}data-Thenewcanvasdata.
     *@returns{Cropper}this
     */
    setCanvasData:functionsetCanvasData(data){
      varcanvasData=this.canvasData;
      varaspectRatio=canvasData.aspectRatio;

      if(this.ready&&!this.disabled&&isPlainObject(data)){
        if(isNumber(data.left)){
          canvasData.left=data.left;
        }

        if(isNumber(data.top)){
          canvasData.top=data.top;
        }

        if(isNumber(data.width)){
          canvasData.width=data.width;
          canvasData.height=data.width/aspectRatio;
        }elseif(isNumber(data.height)){
          canvasData.height=data.height;
          canvasData.width=data.height*aspectRatio;
        }

        this.renderCanvas(true);
      }

      returnthis;
    },

    /**
     *Getthecropboxpositionandsizedata.
     *@returns{Object}Theresultcropboxdata.
     */
    getCropBoxData:functiongetCropBoxData(){
      varcropBoxData=this.cropBoxData;
      vardata;

      if(this.ready&&this.cropped){
        data={
          left:cropBoxData.left,
          top:cropBoxData.top,
          width:cropBoxData.width,
          height:cropBoxData.height
        };
      }

      returndata||{};
    },

    /**
     *Setthecropboxpositionandsizewithnewdata.
     *@param{Object}data-Thenewcropboxdata.
     *@returns{Cropper}this
     */
    setCropBoxData:functionsetCropBoxData(data){
      varcropBoxData=this.cropBoxData;
      varaspectRatio=this.options.aspectRatio;
      varwidthChanged;
      varheightChanged;

      if(this.ready&&this.cropped&&!this.disabled&&isPlainObject(data)){
        if(isNumber(data.left)){
          cropBoxData.left=data.left;
        }

        if(isNumber(data.top)){
          cropBoxData.top=data.top;
        }

        if(isNumber(data.width)&&data.width!==cropBoxData.width){
          widthChanged=true;
          cropBoxData.width=data.width;
        }

        if(isNumber(data.height)&&data.height!==cropBoxData.height){
          heightChanged=true;
          cropBoxData.height=data.height;
        }

        if(aspectRatio){
          if(widthChanged){
            cropBoxData.height=cropBoxData.width/aspectRatio;
          }elseif(heightChanged){
            cropBoxData.width=cropBoxData.height*aspectRatio;
          }
        }

        this.renderCropBox();
      }

      returnthis;
    },

    /**
     *Getacanvasdrawnthecroppedimage.
     *@param{Object}[options={}]-Theconfigoptions.
     *@returns{HTMLCanvasElement}-Theresultcanvas.
     */
    getCroppedCanvas:functiongetCroppedCanvas(){
      varoptions=arguments.length>0&&arguments[0]!==undefined?arguments[0]:{};

      if(!this.ready||!window.HTMLCanvasElement){
        returnnull;
      }

      varcanvasData=this.canvasData;
      varsource=getSourceCanvas(this.image,this.imageData,canvasData,options);//Returnsthesourcecanvasifitisnotcropped.

      if(!this.cropped){
        returnsource;
      }

      var_this$getData=this.getData(),
          initialX=_this$getData.x,
          initialY=_this$getData.y,
          initialWidth=_this$getData.width,
          initialHeight=_this$getData.height;

      varratio=source.width/Math.floor(canvasData.naturalWidth);

      if(ratio!==1){
        initialX*=ratio;
        initialY*=ratio;
        initialWidth*=ratio;
        initialHeight*=ratio;
      }

      varaspectRatio=initialWidth/initialHeight;
      varmaxSizes=getAdjustedSizes({
        aspectRatio:aspectRatio,
        width:options.maxWidth||Infinity,
        height:options.maxHeight||Infinity
      });
      varminSizes=getAdjustedSizes({
        aspectRatio:aspectRatio,
        width:options.minWidth||0,
        height:options.minHeight||0
      },'cover');

      var_getAdjustedSizes=getAdjustedSizes({
        aspectRatio:aspectRatio,
        width:options.width||(ratio!==1?source.width:initialWidth),
        height:options.height||(ratio!==1?source.height:initialHeight)
      }),
          width=_getAdjustedSizes.width,
          height=_getAdjustedSizes.height;

      width=Math.min(maxSizes.width,Math.max(minSizes.width,width));
      height=Math.min(maxSizes.height,Math.max(minSizes.height,height));
      varcanvas=document.createElement('canvas');
      varcontext=canvas.getContext('2d');
      canvas.width=normalizeDecimalNumber(width);
      canvas.height=normalizeDecimalNumber(height);
      context.fillStyle=options.fillColor||'transparent';
      context.fillRect(0,0,width,height);
      var_options$imageSmoothi=options.imageSmoothingEnabled,
          imageSmoothingEnabled=_options$imageSmoothi===void0?true:_options$imageSmoothi,
          imageSmoothingQuality=options.imageSmoothingQuality;
      context.imageSmoothingEnabled=imageSmoothingEnabled;

      if(imageSmoothingQuality){
        context.imageSmoothingQuality=imageSmoothingQuality;
      }//https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D.drawImage


      varsourceWidth=source.width;
      varsourceHeight=source.height;//Sourcecanvasparameters

      varsrcX=initialX;
      varsrcY=initialY;
      varsrcWidth;
      varsrcHeight;//Destinationcanvasparameters

      vardstX;
      vardstY;
      vardstWidth;
      vardstHeight;

      if(srcX<=-initialWidth||srcX>sourceWidth){
        srcX=0;
        srcWidth=0;
        dstX=0;
        dstWidth=0;
      }elseif(srcX<=0){
        dstX=-srcX;
        srcX=0;
        srcWidth=Math.min(sourceWidth,initialWidth+srcX);
        dstWidth=srcWidth;
      }elseif(srcX<=sourceWidth){
        dstX=0;
        srcWidth=Math.min(initialWidth,sourceWidth-srcX);
        dstWidth=srcWidth;
      }

      if(srcWidth<=0||srcY<=-initialHeight||srcY>sourceHeight){
        srcY=0;
        srcHeight=0;
        dstY=0;
        dstHeight=0;
      }elseif(srcY<=0){
        dstY=-srcY;
        srcY=0;
        srcHeight=Math.min(sourceHeight,initialHeight+srcY);
        dstHeight=srcHeight;
      }elseif(srcY<=sourceHeight){
        dstY=0;
        srcHeight=Math.min(initialHeight,sourceHeight-srcY);
        dstHeight=srcHeight;
      }

      varparams=[srcX,srcY,srcWidth,srcHeight];//Avoid"IndexSizeError"

      if(dstWidth>0&&dstHeight>0){
        varscale=width/initialWidth;
        params.push(dstX*scale,dstY*scale,dstWidth*scale,dstHeight*scale);
      }//Allthenumericalparametersshouldbeintegerfor`drawImage`
      //https://github.com/fengyuanchen/cropper/issues/476


      context.drawImage.apply(context,[source].concat(_toConsumableArray(params.map(function(param){
        returnMath.floor(normalizeDecimalNumber(param));
      }))));
      returncanvas;
    },

    /**
     *Changetheaspectratioofthecropbox.
     *@param{number}aspectRatio-Thenewaspectratio.
     *@returns{Cropper}this
     */
    setAspectRatio:functionsetAspectRatio(aspectRatio){
      varoptions=this.options;

      if(!this.disabled&&!isUndefined(aspectRatio)){
        //0->NaN
        options.aspectRatio=Math.max(0,aspectRatio)||NaN;

        if(this.ready){
          this.initCropBox();

          if(this.cropped){
            this.renderCropBox();
          }
        }
      }

      returnthis;
    },

    /**
     *Changethedragmode.
     *@param{string}mode-Thenewdragmode.
     *@returns{Cropper}this
     */
    setDragMode:functionsetDragMode(mode){
      varoptions=this.options,
          dragBox=this.dragBox,
          face=this.face;

      if(this.ready&&!this.disabled){
        varcroppable=mode===DRAG_MODE_CROP;
        varmovable=options.movable&&mode===DRAG_MODE_MOVE;
        mode=croppable||movable?mode:DRAG_MODE_NONE;
        options.dragMode=mode;
        setData(dragBox,DATA_ACTION,mode);
        toggleClass(dragBox,CLASS_CROP,croppable);
        toggleClass(dragBox,CLASS_MOVE,movable);

        if(!options.cropBoxMovable){
          //Syncdragmodetocropboxwhenitisnotmovable
          setData(face,DATA_ACTION,mode);
          toggleClass(face,CLASS_CROP,croppable);
          toggleClass(face,CLASS_MOVE,movable);
        }
      }

      returnthis;
    }
  };

  varAnotherCropper=WINDOW.Cropper;

  varCropper=
  /*#__PURE__*/
  function(){
    /**
     *CreateanewCropper.
     *@param{Element}element-Thetargetelementforcropping.
     *@param{Object}[options={}]-Theconfigurationoptions.
     */
    functionCropper(element){
      varoptions=arguments.length>1&&arguments[1]!==undefined?arguments[1]:{};

      _classCallCheck(this,Cropper);

      if(!element||!REGEXP_TAG_NAME.test(element.tagName)){
        thrownewError('Thefirstargumentisrequiredandmustbean<img>or<canvas>element.');
      }

      this.element=element;
      this.options=assign({},DEFAULTS,isPlainObject(options)&&options);
      this.cropped=false;
      this.disabled=false;
      this.pointers={};
      this.ready=false;
      this.reloading=false;
      this.replaced=false;
      this.sized=false;
      this.sizing=false;
      this.init();
    }

    _createClass(Cropper,[{
      key:"init",
      value:functioninit(){
        varelement=this.element;
        vartagName=element.tagName.toLowerCase();
        varurl;

        if(element[NAMESPACE]){
          return;
        }

        element[NAMESPACE]=this;

        if(tagName==='img'){
          this.isImg=true;//e.g.:"img/picture.jpg"

          url=element.getAttribute('src')||'';
          this.originalUrl=url;//Stopwhenit'sablankimage

          if(!url){
            return;
          }//e.g.:"http://example.com/img/picture.jpg"


          url=element.src;
        }elseif(tagName==='canvas'&&window.HTMLCanvasElement){
          url=element.toDataURL();
        }

        this.load(url);
      }
    },{
      key:"load",
      value:functionload(url){
        var_this=this;

        if(!url){
          return;
        }

        this.url=url;
        this.imageData={};
        varelement=this.element,
            options=this.options;

        if(!options.rotatable&&!options.scalable){
          options.checkOrientation=false;
        }//OnlyIE10+supportsTypedArrays


        if(!options.checkOrientation||!window.ArrayBuffer){
          this.clone();
          return;
        }//DetectthemimetypeoftheimagedirectlyifitisaDataURL


        if(REGEXP_DATA_URL.test(url)){
          //ReadArrayBufferfromDataURLofJPEGimagesdirectlyforbetterperformance
          if(REGEXP_DATA_URL_JPEG.test(url)){
            this.read(dataURLToArrayBuffer(url));
          }else{
            //OnlyaJPEGimagemaycontainsExifOrientationinformation,
            //theresttypesofDataURLsarenotnecessarytocheckorientationatall.
            this.clone();
          }

          return;
        }//1.DetectthemimetypeoftheimagebyaXMLHttpRequest.
        //2.LoadtheimageasArrayBufferforreadingorientationifitsaJPEGimage.


        varxhr=newXMLHttpRequest();
        varclone=this.clone.bind(this);
        this.reloading=true;
        this.xhr=xhr;//1.Crossoriginrequestsareonlysupportedforprotocolschemes:
        //http,https,data,chrome,chrome-extension.
        //2.AccesstoXMLHttpRequestfromaDataURLwillbeblockedbyCORSpolicy
        //insomebrowsersasIE11andSafari.

        xhr.onabort=clone;
        xhr.onerror=clone;
        xhr.ontimeout=clone;

        xhr.onprogress=function(){
          //AborttherequestdirectlyifitnotaJPEGimageforbetterperformance
          if(xhr.getResponseHeader('content-type')!==MIME_TYPE_JPEG){
            xhr.abort();
          }
        };

        xhr.onload=function(){
          _this.read(xhr.response);
        };

        xhr.onloadend=function(){
          _this.reloading=false;
          _this.xhr=null;
        };//Bustcachewhenthereisa"crossOrigin"propertytoavoidbrowsercacheerror


        if(options.checkCrossOrigin&&isCrossOriginURL(url)&&element.crossOrigin){
          url=addTimestamp(url);
        }

        xhr.open('GET',url);
        xhr.responseType='arraybuffer';
        xhr.withCredentials=element.crossOrigin==='use-credentials';
        xhr.send();
      }
    },{
      key:"read",
      value:functionread(arrayBuffer){
        varoptions=this.options,
            imageData=this.imageData;//Resettheorientationvaluetoitsdefaultvalue1
        //assomeiOSbrowserswillrenderimagewithitsorientation

        varorientation=resetAndGetOrientation(arrayBuffer);
        varrotate=0;
        varscaleX=1;
        varscaleY=1;

        if(orientation>1){
          //GenerateanewURLwhichhasthedefaultorientationvalue
          this.url=arrayBufferToDataURL(arrayBuffer,MIME_TYPE_JPEG);

          var_parseOrientation=parseOrientation(orientation);

          rotate=_parseOrientation.rotate;
          scaleX=_parseOrientation.scaleX;
          scaleY=_parseOrientation.scaleY;
        }

        if(options.rotatable){
          imageData.rotate=rotate;
        }

        if(options.scalable){
          imageData.scaleX=scaleX;
          imageData.scaleY=scaleY;
        }

        this.clone();
      }
    },{
      key:"clone",
      value:functionclone(){
        varelement=this.element,
            url=this.url;
        varcrossOrigin=element.crossOrigin;
        varcrossOriginUrl=url;

        if(this.options.checkCrossOrigin&&isCrossOriginURL(url)){
          if(!crossOrigin){
            crossOrigin='anonymous';
          }//Bustcachewhenthereisnota"crossOrigin"property(#519)


          crossOriginUrl=addTimestamp(url);
        }

        this.crossOrigin=crossOrigin;
        this.crossOriginUrl=crossOriginUrl;
        varimage=document.createElement('img');

        if(crossOrigin){
          image.crossOrigin=crossOrigin;
        }

        image.src=crossOriginUrl||url;
        image.alt=element.alt||'Theimagetocrop';
        this.image=image;
        image.onload=this.start.bind(this);
        image.onerror=this.stop.bind(this);
        addClass(image,CLASS_HIDE);
        element.parentNode.insertBefore(image,element.nextSibling);
      }
    },{
      key:"start",
      value:functionstart(){
        var_this2=this;

        varimage=this.image;
        image.onload=null;
        image.onerror=null;
        this.sizing=true;//MatchallbrowsersthatuseWebKitasthelayoutengineiniOSdevices,
        //suchasSafariforiOS,ChromeforiOS,andin-appbrowsers.

        varisIOSWebKit=WINDOW.navigator&&/(?:iPad|iPhone|iPod).*?AppleWebKit/i.test(WINDOW.navigator.userAgent);

        vardone=functiondone(naturalWidth,naturalHeight){
          assign(_this2.imageData,{
            naturalWidth:naturalWidth,
            naturalHeight:naturalHeight,
            aspectRatio:naturalWidth/naturalHeight
          });
          _this2.sizing=false;
          _this2.sized=true;

          _this2.build();
        };//Mostmodernbrowsers(exceptsiOSWebKit)


        if(image.naturalWidth&&!isIOSWebKit){
          done(image.naturalWidth,image.naturalHeight);
          return;
        }

        varsizingImage=document.createElement('img');
        varbody=document.body||document.documentElement;
        this.sizingImage=sizingImage;

        sizingImage.onload=function(){
          done(sizingImage.width,sizingImage.height);

          if(!isIOSWebKit){
            body.removeChild(sizingImage);
          }
        };

        sizingImage.src=image.src;//iOSWebKitwillconverttheimageautomatically
        //withitsorientationonceappenditintoDOM(#279)

        if(!isIOSWebKit){
          sizingImage.style.cssText='left:0;'+'max-height:none!important;'+'max-width:none!important;'+'min-height:0!important;'+'min-width:0!important;'+'opacity:0;'+'position:absolute;'+'top:0;'+'z-index:-1;';
          body.appendChild(sizingImage);
        }
      }
    },{
      key:"stop",
      value:functionstop(){
        varimage=this.image;
        image.onload=null;
        image.onerror=null;
        image.parentNode.removeChild(image);
        this.image=null;
      }
    },{
      key:"build",
      value:functionbuild(){
        if(!this.sized||this.ready){
          return;
        }

        varelement=this.element,
            options=this.options,
            image=this.image;//Createcropperelements

        varcontainer=element.parentNode;
        vartemplate=document.createElement('div');
        template.innerHTML=TEMPLATE;
        varcropper=template.querySelector(".".concat(NAMESPACE,"-container"));
        varcanvas=cropper.querySelector(".".concat(NAMESPACE,"-canvas"));
        vardragBox=cropper.querySelector(".".concat(NAMESPACE,"-drag-box"));
        varcropBox=cropper.querySelector(".".concat(NAMESPACE,"-crop-box"));
        varface=cropBox.querySelector(".".concat(NAMESPACE,"-face"));
        this.container=container;
        this.cropper=cropper;
        this.canvas=canvas;
        this.dragBox=dragBox;
        this.cropBox=cropBox;
        this.viewBox=cropper.querySelector(".".concat(NAMESPACE,"-view-box"));
        this.face=face;
        canvas.appendChild(image);//Hidetheoriginalimage

        addClass(element,CLASS_HIDDEN);//Insertsthecropperaftertothecurrentimage

        container.insertBefore(cropper,element.nextSibling);//Showtheimageifishidden

        if(!this.isImg){
          removeClass(image,CLASS_HIDE);
        }

        this.initPreview();
        this.bind();
        options.initialAspectRatio=Math.max(0,options.initialAspectRatio)||NaN;
        options.aspectRatio=Math.max(0,options.aspectRatio)||NaN;
        options.viewMode=Math.max(0,Math.min(3,Math.round(options.viewMode)))||0;
        addClass(cropBox,CLASS_HIDDEN);

        if(!options.guides){
          addClass(cropBox.getElementsByClassName("".concat(NAMESPACE,"-dashed")),CLASS_HIDDEN);
        }

        if(!options.center){
          addClass(cropBox.getElementsByClassName("".concat(NAMESPACE,"-center")),CLASS_HIDDEN);
        }

        if(options.background){
          addClass(cropper,"".concat(NAMESPACE,"-bg"));
        }

        if(!options.highlight){
          addClass(face,CLASS_INVISIBLE);
        }

        if(options.cropBoxMovable){
          addClass(face,CLASS_MOVE);
          setData(face,DATA_ACTION,ACTION_ALL);
        }

        if(!options.cropBoxResizable){
          addClass(cropBox.getElementsByClassName("".concat(NAMESPACE,"-line")),CLASS_HIDDEN);
          addClass(cropBox.getElementsByClassName("".concat(NAMESPACE,"-point")),CLASS_HIDDEN);
        }

        this.render();
        this.ready=true;
        this.setDragMode(options.dragMode);

        if(options.autoCrop){
          this.crop();
        }

        this.setData(options.data);

        if(isFunction(options.ready)){
          addListener(element,EVENT_READY,options.ready,{
            once:true
          });
        }

        dispatchEvent(element,EVENT_READY);
      }
    },{
      key:"unbuild",
      value:functionunbuild(){
        if(!this.ready){
          return;
        }

        this.ready=false;
        this.unbind();
        this.resetPreview();
        this.cropper.parentNode.removeChild(this.cropper);
        removeClass(this.element,CLASS_HIDDEN);
      }
    },{
      key:"uncreate",
      value:functionuncreate(){
        if(this.ready){
          this.unbuild();
          this.ready=false;
          this.cropped=false;
        }elseif(this.sizing){
          this.sizingImage.onload=null;
          this.sizing=false;
          this.sized=false;
        }elseif(this.reloading){
          this.xhr.onabort=null;
          this.xhr.abort();
        }elseif(this.image){
          this.stop();
        }
      }
      /**
       *Getthenoconflictcropperclass.
       *@returns{Cropper}Thecropperclass.
       */

    }],[{
      key:"noConflict",
      value:functionnoConflict(){
        window.Cropper=AnotherCropper;
        returnCropper;
      }
      /**
       *Changethedefaultoptions.
       *@param{Object}options-Thenewdefaultoptions.
       */

    },{
      key:"setDefaults",
      value:functionsetDefaults(options){
        assign(DEFAULTS,isPlainObject(options)&&options);
      }
    }]);

    returnCropper;
  }();

  assign(Cropper.prototype,render,preview,events,handlers,change,methods);

  returnCropper;

}));
