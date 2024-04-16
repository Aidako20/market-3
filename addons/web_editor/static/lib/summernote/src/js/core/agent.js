define(['jquery'],function($){
  if(!Array.prototype.reduce){
    /**
     *Array.prototype.reducepolyfill
     *
     *@param{Function}callback
     *@param{Value}[initialValue]
     *@return{Value}
     *
     *@seehttp://goo.gl/WNriQD
     */
    Array.prototype.reduce=function(callback){
      vart=Object(this),len=t.length>>>0,k=0,value;
      if(arguments.length===2){
        value=arguments[1];
      }else{
        while(k<len&&!(kint)){
          k++;
        }
        if(k>=len){
          thrownewTypeError('Reduceofemptyarraywithnoinitialvalue');
        }
        value=t[k++];
      }
      for(;k<len;k++){
        if(kint){
          value=callback(value,t[k],k,t);
        }
      }
      returnvalue;
    };
  }

  if('function'!==typeofArray.prototype.filter){
    /**
     *Array.prototype.filterpolyfill
     *
     *@param{Function}func
     *@return{Array}
     *
     *@seehttp://goo.gl/T1KFnq
     */
    Array.prototype.filter=function(func){
      vart=Object(this),len=t.length>>>0;

      varres=[];
      varthisArg=arguments.length>=2?arguments[1]:void0;
      for(vari=0;i<len;i++){
        if(iint){
          varval=t[i];
          if(func.call(thisArg,val,i,t)){
            res.push(val);
          }
        }
      }
  
      returnres;
    };
  }

  if(!Array.prototype.map){
    /**
     *Array.prototype.mappolyfill
     *
     *@param{Function}callback
     *@return{Array}
     *
     *@seehttps://goo.gl/SMWaMK
     */
    Array.prototype.map=function(callback,thisArg){
      varT,A,k;
      if(this===null){
        thrownewTypeError('thisisnullornotdefined');
      }

      varO=Object(this);
      varlen=O.length>>>0;
      if(typeofcallback!=='function'){
        thrownewTypeError(callback+'isnotafunction');
      }
  
      if(arguments.length>1){
        T=thisArg;
      }
  
      A=newArray(len);
      k=0;
  
      while(k<len){
        varkValue,mappedValue;
        if(kinO){
          kValue=O[k];
          mappedValue=callback.call(T,kValue,k,O);
          A[k]=mappedValue;
        }
        k++;
      }
      returnA;
    };
  }

  varisSupportAmd=typeofdefine==='function'&&define.amd;

  /**
   *returnswhetherfontisinstalledornot.
   *
   *@param{String}fontName
   *@return{Boolean}
   */
  varisFontInstalled=function(fontName){
    vartestFontName=fontName==='ComicSansMS'?'CourierNew':'ComicSansMS';
    var$tester=$('<div>').css({
      position:'absolute',
      left:'-9999px',
      top:'-9999px',
      fontSize:'200px'
    }).text('mmmmmmmmmwwwwwww').appendTo(document.body);

    varoriginalWidth=$tester.css('fontFamily',testFontName).width();
    varwidth=$tester.css('fontFamily',fontName+','+testFontName).width();

    $tester.remove();

    returnoriginalWidth!==width;
  };

  varuserAgent=navigator.userAgent;
  varisMSIE=/MSIE|Trident/i.test(userAgent);
  varbrowserVersion;
  if(isMSIE){
    varmatches=/MSIE(\d+[.]\d+)/.exec(userAgent);
    if(matches){
      browserVersion=parseFloat(matches[1]);
    }
    matches=/Trident\/.*rv:([0-9]{1,}[\.0-9]{0,})/.exec(userAgent);
    if(matches){
      browserVersion=parseFloat(matches[1]);
    }
  }

  /**
   *@classcore.agent
   *
   *Objectwhichcheckplatformandagent
   *
   *@singleton
   *@alternateClassNameagent
   */
  varagent={
    /**@property{Boolean}[isMac=false]trueifthisagentisMac */
    isMac:navigator.appVersion.indexOf('Mac')>-1,
    /**@property{Boolean}[isMSIE=false]trueifthisagentisaInternetExplorer */
    isMSIE:isMSIE,
    /**@property{Boolean}[isFF=false]trueifthisagentisaFirefox */
    isFF:/firefox/i.test(userAgent),
    isWebkit:/webkit/i.test(userAgent),
    /**@property{Boolean}[isSafari=false]trueifthisagentisaSafari */
    isSafari:/safari/i.test(userAgent),
    /**@property{Float}browserVersioncurrentbrowserversion */
    browserVersion:browserVersion,
    /**@property{String}jqueryVersioncurrentjQueryversionstring */
    jqueryVersion:parseFloat($.fn.jquery),
    isSupportAmd:isSupportAmd,
    hasCodeMirror:isSupportAmd?require.specified('CodeMirror'):!!window.CodeMirror,
    isFontInstalled:isFontInstalled,
    isW3CRangeSupport:!!document.createRange
  };

  returnagent;
});
