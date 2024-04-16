/*!
 *Benchmark.js<https://benchmarkjs.com/>
 *Copyright2010-2016MathiasBynens<https://mths.be/>
 *BasedonJSLitmus.js,copyrightRobertKieffer<http://broofa.com/>
 *ModifiedbyJohn-DavidDalton<http://allyoucanleet.com/>
 *AvailableunderMITlicense<https://mths.be/mit>
 */
;(function(){
  'usestrict';

  /**Usedasasafereferencefor`undefined`inpreES5environments.*/
  varundefined;

  /**UsedtodetermineifvaluesareofthelanguagetypeObject.*/
  varobjectTypes={
    'function':true,
    'object':true
  };

  /**Usedasareferencetotheglobalobject.*/
  varroot=(objectTypes[typeofwindow]&&window)||this;

  /**Detectfreevariable`define`.*/
  varfreeDefine=typeofdefine=='function'&&typeofdefine.amd=='object'&&define.amd&&define;

  /**Detectfreevariable`exports`.*/
  varfreeExports=objectTypes[typeofexports]&&exports&&!exports.nodeType&&exports;

  /**Detectfreevariable`module`.*/
  varfreeModule=objectTypes[typeofmodule]&&module&&!module.nodeType&&module;

  /**Detectfreevariable`global`fromNode.jsorBrowserifiedcodeanduseitas`root`.*/
  varfreeGlobal=freeExports&&freeModule&&typeofglobal=='object'&&global;
  if(freeGlobal&&(freeGlobal.global===freeGlobal||freeGlobal.window===freeGlobal||freeGlobal.self===freeGlobal)){
    root=freeGlobal;
  }

  /**Detectfreevariable`require`.*/
  varfreeRequire=typeofrequire=='function'&&require;

  /**Usedtoassigneachbenchmarkanincrementedid.*/
  varcounter=0;

  /**DetectthepopularCommonJSextension`module.exports`.*/
  varmoduleExports=freeModule&&freeModule.exports===freeExports&&freeExports;

  /**Usedtodetectprimitivetypes.*/
  varrePrimitive=/^(?:boolean|number|string|undefined)$/;

  /**Usedtomakeeverycompiledtestunique.*/
  varuidCounter=0;

  /**Usedtoassigndefault`context`objectproperties.*/
  varcontextProps=[
    'Array','Date','Function','Math','Object','RegExp','String','_',
    'clearTimeout','chrome','chromium','document','navigator','phantom',
    'platform','process','runtime','setTimeout'
  ];

  /**UsedtoavoidhzofInfinity.*/
  vardivisors={
    '1':4096,
    '2':512,
    '3':64,
    '4':8,
    '5':0
  };

  /**
   *T-Distributiontwo-tailedcriticalvaluesfor95%confidence.
   *Formoreinfoseehttp://www.itl.nist.gov/div898/handbook/eda/section3/eda3672.htm.
   */
  vartTable={
    '1': 12.706,'2': 4.303,'3': 3.182,'4': 2.776,'5': 2.571,'6': 2.447,
    '7': 2.365, '8': 2.306,'9': 2.262,'10':2.228,'11':2.201,'12':2.179,
    '13':2.16,  '14':2.145,'15':2.131,'16':2.12, '17':2.11, '18':2.101,
    '19':2.093, '20':2.086,'21':2.08, '22':2.074,'23':2.069,'24':2.064,
    '25':2.06,  '26':2.056,'27':2.052,'28':2.048,'29':2.045,'30':2.042,
    'infinity':1.96
  };

  /**
   *CriticalMann-WhitneyU-valuesfor95%confidence.
   *Formoreinfoseehttp://www.saburchill.com/IBbiology/stats/003.html.
   */
  varuTable={
    '5': [0,1,2],
    '6': [1,2,3,5],
    '7': [1,3,5,6,8],
    '8': [2,4,6,8,10,13],
    '9': [2,4,7,10,12,15,17],
    '10':[3,5,8,11,14,17,20,23],
    '11':[3,6,9,13,16,19,23,26,30],
    '12':[4,7,11,14,18,22,26,29,33,37],
    '13':[4,8,12,16,20,24,28,33,37,41,45],
    '14':[5,9,13,17,22,26,31,36,40,45,50,55],
    '15':[5,10,14,19,24,29,34,39,44,49,54,59,64],
    '16':[6,11,15,21,26,31,37,42,47,53,59,64,70,75],
    '17':[6,11,17,22,28,34,39,45,51,57,63,67,75,81,87],
    '18':[7,12,18,24,30,36,42,48,55,61,67,74,80,86,93,99],
    '19':[7,13,19,25,32,38,45,52,58,65,72,78,85,92,99,106,113],
    '20':[8,14,20,27,34,41,48,55,62,69,76,83,90,98,105,112,119,127],
    '21':[8,15,22,29,36,43,50,58,65,73,80,88,96,103,111,119,126,134,142],
    '22':[9,16,23,30,38,45,53,61,69,77,85,93,101,109,117,125,133,141,150,158],
    '23':[9,17,24,32,40,48,56,64,73,81,89,98,106,115,123,132,140,149,157,166,175],
    '24':[10,17,25,33,42,50,59,67,76,85,94,102,111,120,129,138,147,156,165,174,183,192],
    '25':[10,18,27,35,44,53,62,71,80,89,98,107,117,126,135,145,154,163,173,182,192,201,211],
    '26':[11,19,28,37,46,55,64,74,83,93,102,112,122,132,141,151,161,171,181,191,200,210,220,230],
    '27':[11,20,29,38,48,57,67,77,87,97,107,118,125,138,147,158,168,178,188,199,209,219,230,240,250],
    '28':[12,21,30,40,50,60,70,80,90,101,111,122,132,143,154,164,175,186,196,207,218,228,239,250,261,272],
    '29':[13,22,32,42,52,62,73,83,94,105,116,127,138,149,160,171,182,193,204,215,226,238,249,260,271,282,294],
    '30':[13,23,33,43,54,65,76,87,98,109,120,131,143,154,166,177,189,200,212,223,235,247,258,270,282,293,305,317]
  };

  /*--------------------------------------------------------------------------*/

  /**
   *Createanew`Benchmark`functionusingthegiven`context`object.
   *
   *@static
   *@memberOfBenchmark
   *@param{Object}[context=root]Thecontextobject.
   *@returns{Function}Returnsanew`Benchmark`function.
   */
  functionrunInContext(context){
    //Exitearlyifunabletoacquirelodash.
    var_=context&&context._||require('lodash')||root._;
    if(!_){
      Benchmark.runInContext=runInContext;
      returnBenchmark;
    }
    //AvoidissueswithsomeES3environmentsthatattempttousevalues,named
    //afterbuilt-inconstructorslike`Object`,forthecreationofliterals.
    //ES5clearsthisupbystatingthatliteralsmustusebuilt-inconstructors.
    //Seehttp://es5.github.io/#x11.1.5.
    context=context?_.defaults(root.Object(),context,_.pick(root,contextProps)):root;

    /**Nativeconstructorreferences.*/
    varArray=context.Array,
        Date=context.Date,
        Function=context.Function,
        Math=context.Math,
        Object=context.Object,
        RegExp=context.RegExp,
        String=context.String;

    /**Usedfor`Array`and`Object`methodreferences.*/
    vararrayRef=[],
        objectProto=Object.prototype;

    /**Nativemethodshortcuts.*/
    varabs=Math.abs,
        clearTimeout=context.clearTimeout,
        floor=Math.floor,
        log=Math.log,
        max=Math.max,
        min=Math.min,
        pow=Math.pow,
        push=arrayRef.push,
        setTimeout=context.setTimeout,
        shift=arrayRef.shift,
        slice=arrayRef.slice,
        sqrt=Math.sqrt,
        toString=objectProto.toString,
        unshift=arrayRef.unshift;

    /**UsedtoavoidinclusioninBrowserifiedbundles.*/
    varreq=require;

    /**DetectDOMdocumentobject.*/
    vardoc=isHostType(context,'document')&&context.document;

    /**UsedtoaccessWadeSimmons'Node.js`microtime`module.*/
    varmicrotimeObject=req('microtime');

    /**UsedtoaccessNode.js'shighresolutiontimer.*/
    varprocessObject=isHostType(context,'process')&&context.process;

    /**Usedtopreventa`removeChild`memoryleakinIE<9.*/
    vartrash=doc&&doc.createElement('div');

    /**Usedtointegritycheckcompiledtests.*/
    varuid='uid'+_.now();

    /**Usedtoavoidinfiniterecursionwhenmethodscalleachother.*/
    varcalledBy={};

    /**
     *Anobjectusedtoflagenvironments/features.
     *
     *@static
     *@memberOfBenchmark
     *@typeObject
     */
    varsupport={};

    (function(){

      /**
       *Detectifrunninginabrowserenvironment.
       *
       *@memberOfBenchmark.support
       *@typeboolean
       */
      support.browser=doc&&isHostType(context,'navigator')&&!isHostType(context,'phantom');

      /**
       *DetectiftheTimersAPIexists.
       *
       *@memberOfBenchmark.support
       *@typeboolean
       */
      support.timeout=isHostType(context,'setTimeout')&&isHostType(context,'clearTimeout');

      /**
       *Detectiffunctiondecompilationissupport.
       *
       *@namedecompilation
       *@memberOfBenchmark.support
       *@typeboolean
       */
      try{
        //Safari2.xremovescommasinobjectliteralsfrom`Function#toString`results.
        //Seehttp://webk.it/11609formoredetails.
        //Firefox3.6andOpera9.25stripgroupingparenthesesfrom`Function#toString`results.
        //Seehttp://bugzil.la/559438formoredetails.
        support.decompilation=Function(
          ('return('+(function(x){return{'x':''+(1+x)+'','y':0};})+')')
          //AvoidissueswithcodeaddedbyIstanbul.
          .replace(/__cov__[^;]+;/g,'')
        )()(0).x==='1';
      }catch(e){
        support.decompilation=false;
      }
    }());

    /**
     *Timerobjectusedby`clock()`and`Deferred#resolve`.
     *
     *@private
     *@typeObject
     */
    vartimer={

      /**
       *Thetimernamespaceobjectorconstructor.
       *
       *@private
       *@memberOftimer
       *@type{Function|Object}
       */
      'ns':Date,

      /**
       *Startsthedeferredtimer.
       *
       *@private
       *@memberOftimer
       *@param{Object}deferredThedeferredinstance.
       */
      'start':null,//Lazydefinedin`clock()`.

      /**
       *Stopsthedeferredtimer.
       *
       *@private
       *@memberOftimer
       *@param{Object}deferredThedeferredinstance.
       */
      'stop':null//Lazydefinedin`clock()`.
    };

    /*------------------------------------------------------------------------*/

    /**
     *TheBenchmarkconstructor.
     *
     *Note:TheBenchmarkconstructorexposesahandfuloflodashmethodsto
     *makeworkingwitharrays,collections,andobjectseasier.Thelodash
     *methodsare:
     *[`each/forEach`](https://lodash.com/docs#forEach),[`forOwn`](https://lodash.com/docs#forOwn),
     *[`has`](https://lodash.com/docs#has),[`indexOf`](https://lodash.com/docs#indexOf),
     *[`map`](https://lodash.com/docs#map),and[`reduce`](https://lodash.com/docs#reduce)
     *
     *@constructor
     *@param{string}nameAnametoidentifythebenchmark.
     *@param{Function|string}fnThetesttobenchmark.
     *@param{Object}[options={}]Optionsobject.
     *@example
     *
     *//basicusage(the`new`operatorisoptional)
     *varbench=newBenchmark(fn);
     *
     *//orusinganamefirst
     *varbench=newBenchmark('foo',fn);
     *
     *//orwithoptions
     *varbench=newBenchmark('foo',fn,{
     *
     *  //displayedby`Benchmark#toString`if`name`isnotavailable
     *  'id':'xyz',
     *
     *  //calledwhenthebenchmarkstartsrunning
     *  'onStart':onStart,
     *
     *  //calledaftereachruncycle
     *  'onCycle':onCycle,
     *
     *  //calledwhenaborted
     *  'onAbort':onAbort,
     *
     *  //calledwhenatesterrors
     *  'onError':onError,
     *
     *  //calledwhenreset
     *  'onReset':onReset,
     *
     *  //calledwhenthebenchmarkcompletesrunning
     *  'onComplete':onComplete,
     *
     *  //compiled/calledbeforethetestloop
     *  'setup':setup,
     *
     *  //compiled/calledafterthetestloop
     *  'teardown':teardown
     *});
     *
     *//ornameandoptions
     *varbench=newBenchmark('foo',{
     *
     *  //aflagtoindicatethebenchmarkisdeferred
     *  'defer':true,
     *
     *  //benchmarktestfunction
     *  'fn':function(deferred){
     *    //call`Deferred#resolve`whenthedeferredtestisfinished
     *    deferred.resolve();
     *  }
     *});
     *
     *//oroptionsonly
     *varbench=newBenchmark({
     *
     *  //benchmarkname
     *  'name':'foo',
     *
     *  //benchmarktestasastring
     *  'fn':'[1,2,3,4].sort()'
     *});
     *
     *//atest's`this`bindingissettothebenchmarkinstance
     *varbench=newBenchmark('foo',function(){
     *  'Mynameis'.concat(this.name);//"Mynameisfoo"
     *});
     */
    functionBenchmark(name,fn,options){
      varbench=this;

      //Allowinstancecreationwithoutthe`new`operator.
      if(!(benchinstanceofBenchmark)){
        returnnewBenchmark(name,fn,options);
      }
      //Jugglearguments.
      if(_.isPlainObject(name)){
        //1argument(options).
        options=name;
      }
      elseif(_.isFunction(name)){
        //2arguments(fn,options).
        options=fn;
        fn=name;
      }
      elseif(_.isPlainObject(fn)){
        //2arguments(name,options).
        options=fn;
        fn=null;
        bench.name=name;
      }
      else{
        //3arguments(name,fn[,options]).
        bench.name=name;
      }
      setOptions(bench,options);

      bench.id||(bench.id=++counter);
      bench.fn==null&&(bench.fn=fn);

      bench.stats=cloneDeep(bench.stats);
      bench.times=cloneDeep(bench.times);
    }

    /**
     *TheDeferredconstructor.
     *
     *@constructor
     *@memberOfBenchmark
     *@param{Object}cloneTheclonedbenchmarkinstance.
     */
    functionDeferred(clone){
      vardeferred=this;
      if(!(deferredinstanceofDeferred)){
        returnnewDeferred(clone);
      }
      deferred.benchmark=clone;
      clock(deferred);
    }

    /**
     *TheEventconstructor.
     *
     *@constructor
     *@memberOfBenchmark
     *@param{Object|string}typeTheeventtype.
     */
    functionEvent(type){
      varevent=this;
      if(typeinstanceofEvent){
        returntype;
      }
      return(eventinstanceofEvent)
        ?_.assign(event,{'timeStamp':_.now()},typeoftype=='string'?{'type':type}:type)
        :newEvent(type);
    }

    /**
     *TheSuiteconstructor.
     *
     *Note:EachSuiteinstancehasahandfulofwrappedlodashmethodsto
     *makeworkingwithSuiteseasier.Thewrappedlodashmethodsare:
     *[`each/forEach`](https://lodash.com/docs#forEach),[`indexOf`](https://lodash.com/docs#indexOf),
     *[`map`](https://lodash.com/docs#map),and[`reduce`](https://lodash.com/docs#reduce)
     *
     *@constructor
     *@memberOfBenchmark
     *@param{string}nameAnametoidentifythesuite.
     *@param{Object}[options={}]Optionsobject.
     *@example
     *
     *//basicusage(the`new`operatorisoptional)
     *varsuite=newBenchmark.Suite;
     *
     *//orusinganamefirst
     *varsuite=newBenchmark.Suite('foo');
     *
     *//orwithoptions
     *varsuite=newBenchmark.Suite('foo',{
     *
     *  //calledwhenthesuitestartsrunning
     *  'onStart':onStart,
     *
     *  //calledbetweenrunningbenchmarks
     *  'onCycle':onCycle,
     *
     *  //calledwhenaborted
     *  'onAbort':onAbort,
     *
     *  //calledwhenatesterrors
     *  'onError':onError,
     *
     *  //calledwhenreset
     *  'onReset':onReset,
     *
     *  //calledwhenthesuitecompletesrunning
     *  'onComplete':onComplete
     *});
     */
    functionSuite(name,options){
      varsuite=this;

      //Allowinstancecreationwithoutthe`new`operator.
      if(!(suiteinstanceofSuite)){
        returnnewSuite(name,options);
      }
      //Jugglearguments.
      if(_.isPlainObject(name)){
        //1argument(options).
        options=name;
      }else{
        //2arguments(name[,options]).
        suite.name=name;
      }
      setOptions(suite,options);
    }

    /*------------------------------------------------------------------------*/

    /**
     *Aspecializedversionof`_.cloneDeep`whichonlyclonesarraysandplain
     *objectsassigningallothervaluesbyreference.
     *
     *@private
     *@param{*}valueThevaluetoclone.
     *@returns{*}Theclonedvalue.
     */
    varcloneDeep=_.partial(_.cloneDeepWith,_,function(value){
      //Onlycloneprimitives,arrays,andplainobjects.
      if(!_.isArray(value)&&!_.isPlainObject(value)){
        returnvalue;
      }
    });

    /**
     *Createsafunctionfromthegivenargumentsstringandbody.
     *
     *@private
     *@param{string}argsThecommaseparatedfunctionarguments.
     *@param{string}bodyThefunctionbody.
     *@returns{Function}Thenewfunction.
     */
    functioncreateFunction(){
      //Lazydefine.
      createFunction=function(args,body){
        varresult,
            anchor=freeDefine?freeDefine.amd:Benchmark,
            prop=uid+'createFunction';

        runScript((freeDefine?'define.amd.':'Benchmark.')+prop+'=function('+args+'){'+body+'}');
        result=anchor[prop];
        deleteanchor[prop];
        returnresult;
      };
      //FixJaegerMonkeybug.
      //Formoreinformationseehttp://bugzil.la/639720.
      createFunction=support.browser&&(createFunction('','return"'+uid+'"')||_.noop)()==uid?createFunction:Function;
      returncreateFunction.apply(null,arguments);
    }

    /**
     *Delaytheexecutionofafunctionbasedonthebenchmark's`delay`property.
     *
     *@private
     *@param{Object}benchThebenchmarkinstance.
     *@param{Object}fnThefunctiontoexecute.
     */
    functiondelay(bench,fn){
      bench._timerId=_.delay(fn,bench.delay*1e3);
    }

    /**
     *Destroysthegivenelement.
     *
     *@private
     *@param{Element}elementTheelementtodestroy.
     */
    functiondestroyElement(element){
      trash.appendChild(element);
      trash.innerHTML='';
    }

    /**
     *Getsthenameofthefirstargumentfromafunction'ssource.
     *
     *@private
     *@param{Function}fnThefunction.
     *@returns{string}Theargumentname.
     */
    functiongetFirstArgument(fn){
      return(!_.has(fn,'toString')&&
        (/^[\s(]*function[^(]*\(([^\s,)]+)/.exec(fn)||0)[1])||'';
    }

    /**
     *Computesthearithmeticmeanofasample.
     *
     *@private
     *@param{Array}sampleThesample.
     *@returns{number}Themean.
     */
    functiongetMean(sample){
      return(_.reduce(sample,function(sum,x){
        returnsum+x;
      })/sample.length)||0;
    }

    /**
     *Getsthesourcecodeofafunction.
     *
     *@private
     *@param{Function}fnThefunction.
     *@returns{string}Thefunction'ssourcecode.
     */
    functiongetSource(fn){
      varresult='';
      if(isStringable(fn)){
        result=String(fn);
      }elseif(support.decompilation){
        //Escapethe`{`forFirefox1.
        result=_.result(/^[^{]+\{([\s\S]*)\}\s*$/.exec(fn),1);
      }
      //Trimstring.
      result=(result||'').replace(/^\s+|\s+$/g,'');

      //Detectstringscontainingonlythe"usestrict"directive.
      return/^(?:\/\*+[\w\W]*?\*\/|\/\/.*?[\n\r\u2028\u2029]|\s)*(["'])usestrict\1;?$/.test(result)
        ?''
        :result;
    }

    /**
     *Checksifanobjectisofthespecifiedclass.
     *
     *@private
     *@param{*}valueThevaluetocheck.
     *@param{string}nameThenameoftheclass.
     *@returns{boolean}Returns`true`ifthevalueisofthespecifiedclass,else`false`.
     */
    functionisClassOf(value,name){
      returnvalue!=null&&toString.call(value)=='[object'+name+']';
    }

    /**
     *Hostobjectscanreturntypevaluesthataredifferentfromtheiractual
     *datatype.Theobjectsweareconcernedwithusuallyreturnnon-primitive
     *typesof"object","function",or"unknown".
     *
     *@private
     *@param{*}objectTheowneroftheproperty.
     *@param{string}propertyThepropertytocheck.
     *@returns{boolean}Returns`true`ifthepropertyvalueisanon-primitive,else`false`.
     */
    functionisHostType(object,property){
      if(object==null){
        returnfalse;
      }
      vartype=typeofobject[property];
      return!rePrimitive.test(type)&&(type!='object'||!!object[property]);
    }

    /**
     *Checksifavaluecanbesafelycoercedtoastring.
     *
     *@private
     *@param{*}valueThevaluetocheck.
     *@returns{boolean}Returns`true`ifthevaluecanbecoerced,else`false`.
     */
    functionisStringable(value){
      return_.isString(value)||(_.has(value,'toString')&&_.isFunction(value.toString));
    }

    /**
     *Awrapperaround`require`tosuppress`modulemissing`errors.
     *
     *@private
     *@param{string}idThemoduleid.
     *@returns{*}Theexportedmoduleor`null`.
     */
    functionrequire(id){
      try{
        varresult=freeExports&&freeRequire(id);
      }catch(e){}
      returnresult||null;
    }

    /**
     *RunsasnippetofJavaScriptviascriptinjection.
     *
     *@private
     *@param{string}codeThecodetorun.
     */
    functionrunScript(code){
      varanchor=freeDefine?define.amd:Benchmark,
          script=doc.createElement('script'),
          sibling=doc.getElementsByTagName('script')[0],
          parent=sibling.parentNode,
          prop=uid+'runScript',
          prefix='('+(freeDefine?'define.amd.':'Benchmark.')+prop+'||function(){})();';

      //Firefox2.0.0.2cannotusescriptinjectionasintendedbecauseitexecutes
      //asynchronously,butthat'sOKbecausescriptinjectionisonlyusedtoavoid
      //thepreviouslycommentedJaegerMonkeybug.
      try{
        //Removetheinsertedscript*before*runningthecodetoavoiddifferences
        //intheexpectedscriptelementcount/orderofthedocument.
        script.appendChild(doc.createTextNode(prefix+code));
        anchor[prop]=function(){destroyElement(script);};
      }catch(e){
        parent=parent.cloneNode(false);
        sibling=null;
        script.text=code;
      }
      parent.insertBefore(script,sibling);
      deleteanchor[prop];
    }

    /**
     *Ahelperfunctionforsettingoptions/eventhandlers.
     *
     *@private
     *@param{Object}objectThebenchmarkorsuiteinstance.
     *@param{Object}[options={}]Optionsobject.
     */
    functionsetOptions(object,options){
      options=object.options=_.assign({},cloneDeep(object.constructor.options),cloneDeep(options));

      _.forOwn(options,function(value,key){
        if(value!=null){
          //Addeventlisteners.
          if(/^on[A-Z]/.test(key)){
            _.each(key.split(''),function(key){
              object.on(key.slice(2).toLowerCase(),value);
            });
          }elseif(!_.has(object,key)){
            object[key]=cloneDeep(value);
          }
        }
      });
    }

    /*------------------------------------------------------------------------*/

    /**
     *Handlescycling/completingthedeferredbenchmark.
     *
     *@memberOfBenchmark.Deferred
     */
    functionresolve(){
      vardeferred=this,
          clone=deferred.benchmark,
          bench=clone._original;

      if(bench.aborted){
        //cycle()->clonecycle/completeevent->compute()'sinvokedbench.run()cycle/complete.
        deferred.teardown();
        clone.running=false;
        cycle(deferred);
      }
      elseif(++deferred.cycles<clone.count){
        clone.compiled.call(deferred,context,timer);
      }
      else{
        timer.stop(deferred);
        deferred.teardown();
        delay(clone,function(){cycle(deferred);});
      }
    }

    /*------------------------------------------------------------------------*/

    /**
     *Ageneric`Array#filter`likemethod.
     *
     *@static
     *@memberOfBenchmark
     *@param{Array}arrayThearraytoiterateover.
     *@param{Function|string}callbackThefunction/aliascalledperiteration.
     *@returns{Array}Anewarrayofvaluesthatpassedcallbackfilter.
     *@example
     *
     *//getoddnumbers
     *Benchmark.filter([1,2,3,4,5],function(n){
     *  returnn%2;
     *});//->[1,3,5];
     *
     *//getfastestbenchmarks
     *Benchmark.filter(benches,'fastest');
     *
     *//getslowestbenchmarks
     *Benchmark.filter(benches,'slowest');
     *
     *//getbenchmarksthatcompletedwithouterroring
     *Benchmark.filter(benches,'successful');
     */
    functionfilter(array,callback){
      if(callback==='successful'){
        //Callbacktoexcludethosethatareerrored,unrun,orhavehzofInfinity.
        callback=function(bench){
          returnbench.cycles&&_.isFinite(bench.hz)&&!bench.error;
        };
      }
      elseif(callback==='fastest'||callback==='slowest'){
        //Getsuccessful,sortbyperiod+marginoferror,andfilterfastest/slowest.
        varresult=filter(array,'successful').sort(function(a,b){
          a=a.stats;b=b.stats;
          return(a.mean+a.moe>b.mean+b.moe?1:-1)*(callback==='fastest'?1:-1);
        });

        return_.filter(result,function(bench){
          returnresult[0].compare(bench)==0;
        });
      }
      return_.filter(array,callback);
    }

    /**
     *Convertsanumbertoamorereadablecomma-separatedstringrepresentation.
     *
     *@static
     *@memberOfBenchmark
     *@param{number}numberThenumbertoconvert.
     *@returns{string}Themorereadablestringrepresentation.
     */
    functionformatNumber(number){
      number=String(number).split('.');
      returnnumber[0].replace(/(?=(?:\d{3})+$)(?!\b)/g,',')+
        (number[1]?'.'+number[1]:'');
    }

    /**
     *Invokesamethodonallitemsinanarray.
     *
     *@static
     *@memberOfBenchmark
     *@param{Array}benchesArrayofbenchmarkstoiterateover.
     *@param{Object|string}nameThenameofthemethodtoinvokeORoptionsobject.
     *@param{...*}[args]Argumentstoinvokethemethodwith.
     *@returns{Array}Anewarrayofvaluesreturnedfromeachmethodinvoked.
     *@example
     *
     *//invoke`reset`onallbenchmarks
     *Benchmark.invoke(benches,'reset');
     *
     *//invoke`emit`witharguments
     *Benchmark.invoke(benches,'emit','complete',listener);
     *
     *//invoke`run(true)`,treatbenchmarksasaqueue,andregisterinvokecallbacks
     *Benchmark.invoke(benches,{
     *
     *  //invokethe`run`method
     *  'name':'run',
     *
     *  //passasingleargument
     *  'args':true,
     *
     *  //treatasqueue,removingbenchmarksfromfrontof`benches`untilempty
     *  'queued':true,
     *
     *  //calledbeforeanybenchmarkshavebeeninvoked.
     *  'onStart':onStart,
     *
     *  //calledbetweeninvokingbenchmarks
     *  'onCycle':onCycle,
     *
     *  //calledafterallbenchmarkshavebeeninvoked.
     *  'onComplete':onComplete
     *});
     */
    functioninvoke(benches,name){
      varargs,
          bench,
          queued,
          index=-1,
          eventProps={'currentTarget':benches},
          options={'onStart':_.noop,'onCycle':_.noop,'onComplete':_.noop},
          result=_.toArray(benches);

      /**
       *Invokesthemethodofthecurrentobjectandifsynchronous,fetchesthenext.
       */
      functionexecute(){
        varlisteners,
            async=isAsync(bench);

        if(async){
          //Use`getNext`asthefirstlistener.
          bench.on('complete',getNext);
          listeners=bench.events.complete;
          listeners.splice(0,0,listeners.pop());
        }
        //Executemethod.
        result[index]=_.isFunction(bench&&bench[name])?bench[name].apply(bench,args):undefined;
        //Ifsynchronousreturn`true`untilfinished.
        return!async&&getNext();
      }

      /**
       *Fetchesthenextbenchorexecutes`onComplete`callback.
       */
      functiongetNext(event){
        varcycleEvent,
            last=bench,
            async=isAsync(last);

        if(async){
          last.off('complete',getNext);
          last.emit('complete');
        }
        //Emit"cycle"event.
        eventProps.type='cycle';
        eventProps.target=last;
        cycleEvent=Event(eventProps);
        options.onCycle.call(benches,cycleEvent);

        //Choosenextbenchmarkifnotexitingearly.
        if(!cycleEvent.aborted&&raiseIndex()!==false){
          bench=queued?benches[0]:result[index];
          if(isAsync(bench)){
            delay(bench,execute);
          }
          elseif(async){
            //Resumeexecutionifpreviouslyasynchronousbutnowsynchronous.
            while(execute()){}
          }
          else{
            //Continuesynchronousexecution.
            returntrue;
          }
        }else{
          //Emit"complete"event.
          eventProps.type='complete';
          options.onComplete.call(benches,Event(eventProps));
        }
        //Whenusedasalistener`event.aborted=true`willcanceltherestof
        //the"complete"listenersbecausetheywerealreadycalledaboveandwhen
        //usedaspartof`getNext`the`returnfalse`willexittheexecutionwhile-loop.
        if(event){
          event.aborted=true;
        }else{
          returnfalse;
        }
      }

      /**
       *Checksifinvoking`Benchmark#run`withasynchronouscycles.
       */
      functionisAsync(object){
        //Avoidusing`instanceof`herebecauseofIEmemoryleakissueswithhostobjects.
        varasync=args[0]&&args[0].async;
        returnname=='run'&&(objectinstanceofBenchmark)&&
          ((async==null?object.options.async:async)&&support.timeout||object.defer);
      }

      /**
       *Raises`index`tothenextdefinedindexorreturns`false`.
       */
      functionraiseIndex(){
        index++;

        //Ifqueuedremovethepreviousbench.
        if(queued&&index>0){
          shift.call(benches);
        }
        //Ifwereachedthelastindexthenreturn`false`.
        return(queued?benches.length:index<result.length)
          ?index
          :(index=false);
      }
      //Jugglearguments.
      if(_.isString(name)){
        //2arguments(array,name).
        args=slice.call(arguments,2);
      }else{
        //2arguments(array,options).
        options=_.assign(options,name);
        name=options.name;
        args=_.isArray(args='args'inoptions?options.args:[])?args:[args];
        queued=options.queued;
      }
      //Startiteratingoverthearray.
      if(raiseIndex()!==false){
        //Emit"start"event.
        bench=result[index];
        eventProps.type='start';
        eventProps.target=bench;
        options.onStart.call(benches,Event(eventProps));

        //Endearlyifthesuitewasabortedinan"onStart"listener.
        if(name=='run'&&(benchesinstanceofSuite)&&benches.aborted){
          //Emit"cycle"event.
          eventProps.type='cycle';
          options.onCycle.call(benches,Event(eventProps));
          //Emit"complete"event.
          eventProps.type='complete';
          options.onComplete.call(benches,Event(eventProps));
        }
        //Startmethodexecution.
        else{
          if(isAsync(bench)){
            delay(bench,execute);
          }else{
            while(execute()){}
          }
        }
      }
      returnresult;
    }

    /**
     *Createsastringofjoinedarrayvaluesorobjectkey-valuepairs.
     *
     *@static
     *@memberOfBenchmark
     *@param{Array|Object}objectTheobjecttooperateon.
     *@param{string}[separator1=',']Theseparatorusedbetweenkey-valuepairs.
     *@param{string}[separator2=':']Theseparatorusedbetweenkeysandvalues.
     *@returns{string}Thejoinedresult.
     */
    functionjoin(object,separator1,separator2){
      varresult=[],
          length=(object=Object(object)).length,
          arrayLike=length===length>>>0;

      separator2||(separator2=':');
      _.each(object,function(value,key){
        result.push(arrayLike?value:key+separator2+value);
      });
      returnresult.join(separator1||',');
    }

    /*------------------------------------------------------------------------*/

    /**
     *Abortsallbenchmarksinthesuite.
     *
     *@nameabort
     *@memberOfBenchmark.Suite
     *@returns{Object}Thesuiteinstance.
     */
    functionabortSuite(){
      varevent,
          suite=this,
          resetting=calledBy.resetSuite;

      if(suite.running){
        event=Event('abort');
        suite.emit(event);
        if(!event.cancelled||resetting){
          //Avoidinfiniterecursion.
          calledBy.abortSuite=true;
          suite.reset();
          deletecalledBy.abortSuite;

          if(!resetting){
            suite.aborted=true;
            invoke(suite,'abort');
          }
        }
      }
      returnsuite;
    }

    /**
     *Addsatesttothebenchmarksuite.
     *
     *@memberOfBenchmark.Suite
     *@param{string}nameAnametoidentifythebenchmark.
     *@param{Function|string}fnThetesttobenchmark.
     *@param{Object}[options={}]Optionsobject.
     *@returns{Object}Thesuiteinstance.
     *@example
     *
     *//basicusage
     *suite.add(fn);
     *
     *//orusinganamefirst
     *suite.add('foo',fn);
     *
     *//orwithoptions
     *suite.add('foo',fn,{
     *  'onCycle':onCycle,
     *  'onComplete':onComplete
     *});
     *
     *//ornameandoptions
     *suite.add('foo',{
     *  'fn':fn,
     *  'onCycle':onCycle,
     *  'onComplete':onComplete
     *});
     *
     *//oroptionsonly
     *suite.add({
     *  'name':'foo',
     *  'fn':fn,
     *  'onCycle':onCycle,
     *  'onComplete':onComplete
     *});
     */
    functionadd(name,fn,options){
      varsuite=this,
          bench=newBenchmark(name,fn,options),
          event=Event({'type':'add','target':bench});

      if(suite.emit(event),!event.cancelled){
        suite.push(bench);
      }
      returnsuite;
    }

    /**
     *Createsanewsuitewithclonedbenchmarks.
     *
     *@nameclone
     *@memberOfBenchmark.Suite
     *@param{Object}optionsOptionsobjecttooverwriteclonedoptions.
     *@returns{Object}Thenewsuiteinstance.
     */
    functioncloneSuite(options){
      varsuite=this,
          result=newsuite.constructor(_.assign({},suite.options,options));

      //Copyownproperties.
      _.forOwn(suite,function(value,key){
        if(!_.has(result,key)){
          result[key]=_.isFunction(_.get(value,'clone'))
            ?value.clone()
            :cloneDeep(value);
        }
      });
      returnresult;
    }

    /**
     *An`Array#filter`likemethod.
     *
     *@namefilter
     *@memberOfBenchmark.Suite
     *@param{Function|string}callbackThefunction/aliascalledperiteration.
     *@returns{Object}Anewsuiteofbenchmarksthatpassedcallbackfilter.
     */
    functionfilterSuite(callback){
      varsuite=this,
          result=newsuite.constructor(suite.options);

      result.push.apply(result,filter(suite,callback));
      returnresult;
    }

    /**
     *Resetsallbenchmarksinthesuite.
     *
     *@namereset
     *@memberOfBenchmark.Suite
     *@returns{Object}Thesuiteinstance.
     */
    functionresetSuite(){
      varevent,
          suite=this,
          aborting=calledBy.abortSuite;

      if(suite.running&&!aborting){
        //Noworries,`resetSuite()`iscalledwithin`abortSuite()`.
        calledBy.resetSuite=true;
        suite.abort();
        deletecalledBy.resetSuite;
      }
      //Resetifthestatehaschanged.
      elseif((suite.aborted||suite.running)&&
          (suite.emit(event=Event('reset')),!event.cancelled)){
        suite.aborted=suite.running=false;
        if(!aborting){
          invoke(suite,'reset');
        }
      }
      returnsuite;
    }

    /**
     *Runsthesuite.
     *
     *@namerun
     *@memberOfBenchmark.Suite
     *@param{Object}[options={}]Optionsobject.
     *@returns{Object}Thesuiteinstance.
     *@example
     *
     *//basicusage
     *suite.run();
     *
     *//orwithoptions
     *suite.run({'async':true,'queued':true});
     */
    functionrunSuite(options){
      varsuite=this;

      suite.reset();
      suite.running=true;
      options||(options={});

      invoke(suite,{
        'name':'run',
        'args':options,
        'queued':options.queued,
        'onStart':function(event){
          suite.emit(event);
        },
        'onCycle':function(event){
          varbench=event.target;
          if(bench.error){
            suite.emit({'type':'error','target':bench});
          }
          suite.emit(event);
          event.aborted=suite.aborted;
        },
        'onComplete':function(event){
          suite.running=false;
          suite.emit(event);
        }
      });
      returnsuite;
    }

    /*------------------------------------------------------------------------*/

    /**
     *Executesallregisteredlistenersofthespecifiedeventtype.
     *
     *@memberOfBenchmark,Benchmark.Suite
     *@param{Object|string}typeTheeventtypeorobject.
     *@param{...*}[args]Argumentstoinvokethelistenerwith.
     *@returns{*}Returnsthereturnvalueofthelastlistenerexecuted.
     */
    functionemit(type){
      varlisteners,
          object=this,
          event=Event(type),
          events=object.events,
          args=(arguments[0]=event,arguments);

      event.currentTarget||(event.currentTarget=object);
      event.target||(event.target=object);
      deleteevent.result;

      if(events&&(listeners=_.has(events,event.type)&&events[event.type])){
        _.each(listeners.slice(),function(listener){
          if((event.result=listener.apply(object,args))===false){
            event.cancelled=true;
          }
          return!event.aborted;
        });
      }
      returnevent.result;
    }

    /**
     *Returnsanarrayofeventlistenersforagiventypethatcanbemanipulated
     *toaddorremovelisteners.
     *
     *@memberOfBenchmark,Benchmark.Suite
     *@param{string}typeTheeventtype.
     *@returns{Array}Thelistenersarray.
     */
    functionlisteners(type){
      varobject=this,
          events=object.events||(object.events={});

      return_.has(events,type)?events[type]:(events[type]=[]);
    }

    /**
     *Unregistersalistenerforthespecifiedeventtype(s),
     *orunregistersalllistenersforthespecifiedeventtype(s),
     *orunregistersalllistenersforalleventtypes.
     *
     *@memberOfBenchmark,Benchmark.Suite
     *@param{string}[type]Theeventtype.
     *@param{Function}[listener]Thefunctiontounregister.
     *@returns{Object}Thecurrentinstance.
     *@example
     *
     *//unregisteralistenerforaneventtype
     *bench.off('cycle',listener);
     *
     *//unregisteralistenerformultipleeventtypes
     *bench.off('startcycle',listener);
     *
     *//unregisteralllistenersforaneventtype
     *bench.off('cycle');
     *
     *//unregisteralllistenersformultipleeventtypes
     *bench.off('startcyclecomplete');
     *
     *//unregisteralllistenersforalleventtypes
     *bench.off();
     */
    functionoff(type,listener){
      varobject=this,
          events=object.events;

      if(!events){
        returnobject;
      }
      _.each(type?type.split(''):events,function(listeners,type){
        varindex;
        if(typeoflisteners=='string'){
          type=listeners;
          listeners=_.has(events,type)&&events[type];
        }
        if(listeners){
          if(listener){
            index=_.indexOf(listeners,listener);
            if(index>-1){
              listeners.splice(index,1);
            }
          }else{
            listeners.length=0;
          }
        }
      });
      returnobject;
    }

    /**
     *Registersalistenerforthespecifiedeventtype(s).
     *
     *@memberOfBenchmark,Benchmark.Suite
     *@param{string}typeTheeventtype.
     *@param{Function}listenerThefunctiontoregister.
     *@returns{Object}Thecurrentinstance.
     *@example
     *
     *//registeralistenerforaneventtype
     *bench.on('cycle',listener);
     *
     *//registeralistenerformultipleeventtypes
     *bench.on('startcycle',listener);
     */
    functionon(type,listener){
      varobject=this,
          events=object.events||(object.events={});

      _.each(type.split(''),function(type){
        (_.has(events,type)
          ?events[type]
          :(events[type]=[])
        ).push(listener);
      });
      returnobject;
    }

    /*------------------------------------------------------------------------*/

    /**
     *Abortsthebenchmarkwithoutrecordingtimes.
     *
     *@memberOfBenchmark
     *@returns{Object}Thebenchmarkinstance.
     */
    functionabort(){
      varevent,
          bench=this,
          resetting=calledBy.reset;

      if(bench.running){
        event=Event('abort');
        bench.emit(event);
        if(!event.cancelled||resetting){
          //Avoidinfiniterecursion.
          calledBy.abort=true;
          bench.reset();
          deletecalledBy.abort;

          if(support.timeout){
            clearTimeout(bench._timerId);
            deletebench._timerId;
          }
          if(!resetting){
            bench.aborted=true;
            bench.running=false;
          }
        }
      }
      returnbench;
    }

    /**
     *Createsanewbenchmarkusingthesametestandoptions.
     *
     *@memberOfBenchmark
     *@param{Object}optionsOptionsobjecttooverwriteclonedoptions.
     *@returns{Object}Thenewbenchmarkinstance.
     *@example
     *
     *varbizarro=bench.clone({
     *  'name':'doppelganger'
     *});
     */
    functionclone(options){
      varbench=this,
          result=newbench.constructor(_.assign({},bench,options));

      //Correctthe`options`object.
      result.options=_.assign({},cloneDeep(bench.options),cloneDeep(options));

      //Copyowncustomproperties.
      _.forOwn(bench,function(value,key){
        if(!_.has(result,key)){
          result[key]=cloneDeep(value);
        }
      });

      returnresult;
    }

    /**
     *Determinesifabenchmarkisfasterthananother.
     *
     *@memberOfBenchmark
     *@param{Object}otherThebenchmarktocompare.
     *@returns{number}Returns`-1`ifslower,`1`iffaster,and`0`ifindeterminate.
     */
    functioncompare(other){
      varbench=this;

      //Exitearlyifcomparingthesamebenchmark.
      if(bench==other){
        return0;
      }
      varcritical,
          zStat,
          sample1=bench.stats.sample,
          sample2=other.stats.sample,
          size1=sample1.length,
          size2=sample2.length,
          maxSize=max(size1,size2),
          minSize=min(size1,size2),
          u1=getU(sample1,sample2),
          u2=getU(sample2,sample1),
          u=min(u1,u2);

      functiongetScore(xA,sampleB){
        return_.reduce(sampleB,function(total,xB){
          returntotal+(xB>xA?0:xB<xA?1:0.5);
        },0);
      }

      functiongetU(sampleA,sampleB){
        return_.reduce(sampleA,function(total,xA){
          returntotal+getScore(xA,sampleB);
        },0);
      }

      functiongetZ(u){
        return(u-((size1*size2)/2))/sqrt((size1*size2*(size1+size2+1))/12);
      }
      //Rejectthenullhypothesisthetwosamplescomefromthe
      //samepopulation(i.e.havethesamemedian)if...
      if(size1+size2>30){
        //...thez-statisgreaterthan1.96orlessthan-1.96
        //http://www.statisticslectures.com/topics/mannwhitneyu/
        zStat=getZ(u);
        returnabs(zStat)>1.96?(u==u1?1:-1):0;
      }
      //...theUvalueislessthanorequalthecriticalUvalue.
      critical=maxSize<5||minSize<3?0:uTable[maxSize][minSize-3];
      returnu<=critical?(u==u1?1:-1):0;
    }

    /**
     *Resetpropertiesandabortifrunning.
     *
     *@memberOfBenchmark
     *@returns{Object}Thebenchmarkinstance.
     */
    functionreset(){
      varbench=this;
      if(bench.running&&!calledBy.abort){
        //Noworries,`reset()`iscalledwithin`abort()`.
        calledBy.reset=true;
        bench.abort();
        deletecalledBy.reset;
        returnbench;
      }
      varevent,
          index=0,
          changes=[],
          queue=[];

      //Anon-recursivesolutiontocheckifpropertieshavechanged.
      //Formoreinformationseehttp://www.jslab.dk/articles/non.recursive.preorder.traversal.part4.
      vardata={
        'destination':bench,
        'source':_.assign({},cloneDeep(bench.constructor.prototype),cloneDeep(bench.options))
      };

      do{
        _.forOwn(data.source,function(value,key){
          varchanged,
              destination=data.destination,
              currValue=destination[key];

          //Skippseudoprivatepropertiesandeventlisteners.
          if(/^_|^events$|^on[A-Z]/.test(key)){
            return;
          }
          if(_.isObjectLike(value)){
            if(_.isArray(value)){
              //Checkifanarrayvaluehaschangedtoanon-arrayvalue.
              if(!_.isArray(currValue)){
                changed=true;
                currValue=[];
              }
              //Checkifanarrayhaschangeditslength.
              if(currValue.length!=value.length){
                changed=true;
                currValue=currValue.slice(0,value.length);
                currValue.length=value.length;
              }
            }
            //Checkifanobjecthaschangedtoanon-objectvalue.
            elseif(!_.isObjectLike(currValue)){
              changed=true;
              currValue={};
            }
            //Registerachangedobject.
            if(changed){
              changes.push({'destination':destination,'key':key,'value':currValue});
            }
            queue.push({'destination':currValue,'source':value});
          }
          //Registerachangedprimitive.
          elseif(!_.eq(currValue,value)&&value!==undefined){
            changes.push({'destination':destination,'key':key,'value':value});
          }
        });
      }
      while((data=queue[index++]));

      //Ifchangedemitthe`reset`eventandifitisn'tcancelledresetthebenchmark.
      if(changes.length&&
          (bench.emit(event=Event('reset')),!event.cancelled)){
        _.each(changes,function(data){
          data.destination[data.key]=data.value;
        });
      }
      returnbench;
    }

    /**
     *Displaysrelevantbenchmarkinformationwhencoercedtoastring.
     *
     *@nametoString
     *@memberOfBenchmark
     *@returns{string}Astringrepresentationofthebenchmarkinstance.
     */
    functiontoStringBench(){
      varbench=this,
          error=bench.error,
          hz=bench.hz,
          id=bench.id,
          stats=bench.stats,
          size=stats.sample.length,
          pm='\xb1',
          result=bench.name||(_.isNaN(id)?id:'<Test#'+id+'>');

      if(error){
        varerrorStr;
        if(!_.isObject(error)){
          errorStr=String(error);
        }elseif(!_.isError(Error)){
          errorStr=join(error);
        }else{
          //Error#nameandError#messagepropertiesarenon-enumerable.
          errorStr=join(_.assign({'name':error.name,'message':error.message},error));
        }
        result+=':'+errorStr;
      }
      else{
        result+='x'+formatNumber(hz.toFixed(hz<100?2:0))+'ops/sec'+pm+
          stats.rme.toFixed(2)+'%('+size+'run'+(size==1?'':'s')+'sampled)';
      }
      returnresult;
    }

    /*------------------------------------------------------------------------*/

    /**
     *Clocksthetimetakentoexecuteatestpercycle(secs).
     *
     *@private
     *@param{Object}benchThebenchmarkinstance.
     *@returns{number}Thetimetaken.
     */
    functionclock(){
      varoptions=Benchmark.options,
          templateData={},
          timers=[{'ns':timer.ns,'res':max(0.0015,getRes('ms')),'unit':'ms'}];

      //Lazydefineforhi-restimers.
      clock=function(clone){
        vardeferred;

        if(cloneinstanceofDeferred){
          deferred=clone;
          clone=deferred.benchmark;
        }
        varbench=clone._original,
            stringable=isStringable(bench.fn),
            count=bench.count=clone.count,
            decompilable=stringable||(support.decompilation&&(clone.setup!==_.noop||clone.teardown!==_.noop)),
            id=bench.id,
            name=bench.name||(typeofid=='number'?'<Test#'+id+'>':id),
            result=0;

        //Init`minTime`ifneeded.
        clone.minTime=bench.minTime||(bench.minTime=bench.options.minTime=options.minTime);

        //Compileinsetup/teardownfunctionsandthetestloop.
        //Createanewcompiledtest,insteadofusingthecached`bench.compiled`,
        //toavoidpotentialengineoptimizationsenabledoverthelifeofthetest.
        varfuncBody=deferred
          ?'vard#=this,${fnArg}=d#,m#=d#.benchmark._original,f#=m#.fn,su#=m#.setup,td#=m#.teardown;'+
            //When`deferred.cycles`is`0`then...
            'if(!d#.cycles){'+
            //set`deferred.fn`,
            'd#.fn=function(){var${fnArg}=d#;if(typeoff#=="function"){try{${fn}\n}catch(e#){f#(d#)}}else{${fn}\n}};'+
            //set`deferred.teardown`,
            'd#.teardown=function(){d#.cycles=0;if(typeoftd#=="function"){try{${teardown}\n}catch(e#){td#()}}else{${teardown}\n}};'+
            //executethebenchmark's`setup`,
            'if(typeofsu#=="function"){try{${setup}\n}catch(e#){su#()}}else{${setup}\n};'+
            //starttimer,
            't#.start(d#);'+
            //andthenexecute`deferred.fn`andreturnadummyobject.
            '}d#.fn();return{uid:"${uid}"}'

          :'varr#,s#,m#=this,f#=m#.fn,i#=m#.count,n#=t#.ns;${setup}\n${begin};'+
            'while(i#--){${fn}\n}${end};${teardown}\nreturn{elapsed:r#,uid:"${uid}"}';

        varcompiled=bench.compiled=clone.compiled=createCompiled(bench,decompilable,deferred,funcBody),
            isEmpty=!(templateData.fn||stringable);

        try{
          if(isEmpty){
            //Firefoxmayremovedeadcodefrom`Function#toString`results.
            //Formoreinformationseehttp://bugzil.la/536085.
            thrownewError('Thetest"'+name+'"isempty.Thismaybetheresultofdeadcoderemoval.');
          }
          elseif(!deferred){
            //Pretesttodetermineifcompiledcodeexitsearly,usuallybya
            //rogue`return`statement,bycheckingforareturnobjectwiththeuid.
            bench.count=1;
            compiled=decompilable&&(compiled.call(bench,context,timer)||{}).uid==templateData.uid&&compiled;
            bench.count=count;
          }
        }catch(e){
          compiled=null;
          clone.error=e||newError(String(e));
          bench.count=count;
        }
        //Fallbackwhenatestexitsearlyorerrorsduringpretest.
        if(!compiled&&!deferred&&!isEmpty){
          funcBody=(
            stringable||(decompilable&&!clone.error)
              ?'functionf#(){${fn}\n}varr#,s#,m#=this,i#=m#.count'
              :'varr#,s#,m#=this,f#=m#.fn,i#=m#.count'
            )+
            ',n#=t#.ns;${setup}\n${begin};m#.f#=f#;while(i#--){m#.f#()}${end};'+
            'deletem#.f#;${teardown}\nreturn{elapsed:r#}';

          compiled=createCompiled(bench,decompilable,deferred,funcBody);

          try{
            //Pretestonemoretimetocheckforerrors.
            bench.count=1;
            compiled.call(bench,context,timer);
            bench.count=count;
            deleteclone.error;
          }
          catch(e){
            bench.count=count;
            if(!clone.error){
              clone.error=e||newError(String(e));
            }
          }
        }
        //Ifnoerrorsrunthefulltestloop.
        if(!clone.error){
          compiled=bench.compiled=clone.compiled=createCompiled(bench,decompilable,deferred,funcBody);
          result=compiled.call(deferred||bench,context,timer).elapsed;
        }
        returnresult;
      };

      /*----------------------------------------------------------------------*/

      /**
       *Createsacompiledfunctionfromthegivenfunction`body`.
       */
      functioncreateCompiled(bench,decompilable,deferred,body){
        varfn=bench.fn,
            fnArg=deferred?getFirstArgument(fn)||'deferred':'';

        templateData.uid=uid+uidCounter++;

        _.assign(templateData,{
          'setup':decompilable?getSource(bench.setup):interpolate('m#.setup()'),
          'fn':decompilable?getSource(fn):interpolate('m#.fn('+fnArg+')'),
          'fnArg':fnArg,
          'teardown':decompilable?getSource(bench.teardown):interpolate('m#.teardown()')
        });

        //UseAPIofchosentimer.
        if(timer.unit=='ns'){
          _.assign(templateData,{
            'begin':interpolate('s#=n#()'),
            'end':interpolate('r#=n#(s#);r#=r#[0]+(r#[1]/1e9)')
          });
        }
        elseif(timer.unit=='us'){
          if(timer.ns.stop){
            _.assign(templateData,{
              'begin':interpolate('s#=n#.start()'),
              'end':interpolate('r#=n#.microseconds()/1e6')
            });
          }else{
            _.assign(templateData,{
              'begin':interpolate('s#=n#()'),
              'end':interpolate('r#=(n#()-s#)/1e6')
            });
          }
        }
        elseif(timer.ns.now){
          _.assign(templateData,{
            'begin':interpolate('s#=n#.now()'),
            'end':interpolate('r#=(n#.now()-s#)/1e3')
          });
        }
        else{
          _.assign(templateData,{
            'begin':interpolate('s#=newn#().getTime()'),
            'end':interpolate('r#=(newn#().getTime()-s#)/1e3')
          });
        }
        //Define`timer`methods.
        timer.start=createFunction(
          interpolate('o#'),
          interpolate('varn#=this.ns,${begin};o#.elapsed=0;o#.timeStamp=s#')
        );

        timer.stop=createFunction(
          interpolate('o#'),
          interpolate('varn#=this.ns,s#=o#.timeStamp,${end};o#.elapsed=r#')
        );

        //Createcompiledtest.
        returncreateFunction(
          interpolate('window,t#'),
          'varglobal=window,clearTimeout=global.clearTimeout,setTimeout=global.setTimeout;\n'+
          interpolate(body)
        );
      }

      /**
       *Getsthecurrenttimer'sminimumresolution(secs).
       */
      functiongetRes(unit){
        varmeasured,
            begin,
            count=30,
            divisor=1e3,
            ns=timer.ns,
            sample=[];

        //Getaveragesmallestmeasurabletime.
        while(count--){
          if(unit=='us'){
            divisor=1e6;
            if(ns.stop){
              ns.start();
              while(!(measured=ns.microseconds())){}
            }else{
              begin=ns();
              while(!(measured=ns()-begin)){}
            }
          }
          elseif(unit=='ns'){
            divisor=1e9;
            begin=(begin=ns())[0]+(begin[1]/divisor);
            while(!(measured=((measured=ns())[0]+(measured[1]/divisor))-begin)){}
            divisor=1;
          }
          elseif(ns.now){
            begin=ns.now();
            while(!(measured=ns.now()-begin)){}
          }
          else{
            begin=newns().getTime();
            while(!(measured=newns().getTime()-begin)){}
          }
          //Checkforbrokentimers.
          if(measured>0){
            sample.push(measured);
          }else{
            sample.push(Infinity);
            break;
          }
        }
        //Converttoseconds.
        returngetMean(sample)/divisor;
      }

      /**
       *Interpolatesagiventemplatestring.
       */
      functioninterpolate(string){
        //Replacesalloccurrencesof`#`withauniquenumberandtemplatetokenswithcontent.
        return_.template(string.replace(/\#/g,/\d+/.exec(templateData.uid)))(templateData);
      }

      /*----------------------------------------------------------------------*/

      //DetectChrome'smicrosecondtimer:
      //enablebenchmarkingviathe--enable-benchmarkingcommand
      //lineswitchinatleastChrome7tousechrome.Interval
      try{
        if((timer.ns=new(context.chrome||context.chromium).Interval)){
          timers.push({'ns':timer.ns,'res':getRes('us'),'unit':'us'});
        }
      }catch(e){}

      //DetectNode.js'snanosecondresolutiontimeravailableinNode.js>=0.8.
      if(processObject&&typeof(timer.ns=processObject.hrtime)=='function'){
        timers.push({'ns':timer.ns,'res':getRes('ns'),'unit':'ns'});
      }
      //DetectWadeSimmons'Node.js`microtime`module.
      if(microtimeObject&&typeof(timer.ns=microtimeObject.now)=='function'){
        timers.push({'ns':timer.ns, 'res':getRes('us'),'unit':'us'});
      }
      //Picktimerwithhighestresolution.
      timer=_.minBy(timers,'res');

      //Erroriftherearenoworkingtimers.
      if(timer.res==Infinity){
        thrownewError('Benchmark.jswasunabletofindaworkingtimer.');
      }
      //Resolvetimespanrequiredtoachieveapercentuncertaintyofatmost1%.
      //Formoreinformationseehttp://spiff.rit.edu/classes/phys273/uncert/uncert.html.
      options.minTime||(options.minTime=max(timer.res/2/0.01,0.05));
      returnclock.apply(null,arguments);
    }

    /*------------------------------------------------------------------------*/

    /**
     *Computesstatsonbenchmarkresults.
     *
     *@private
     *@param{Object}benchThebenchmarkinstance.
     *@param{Object}optionsTheoptionsobject.
     */
    functioncompute(bench,options){
      options||(options={});

      varasync=options.async,
          elapsed=0,
          initCount=bench.initCount,
          minSamples=bench.minSamples,
          queue=[],
          sample=bench.stats.sample;

      /**
       *Addsaclonetothequeue.
       */
      functionenqueue(){
        queue.push(_.assign(bench.clone(),{
          '_original':bench,
          'events':{
            'abort':[update],
            'cycle':[update],
            'error':[update],
            'start':[update]
          }
        }));
      }

      /**
       *Updatestheclone/originalbenchmarkstokeeptheirdatainsync.
       */
      functionupdate(event){
        varclone=this,
            type=event.type;

        if(bench.running){
          if(type=='start'){
            //Note:`clone.minTime`propisinitedin`clock()`.
            clone.count=bench.initCount;
          }
          else{
            if(type=='error'){
              bench.error=clone.error;
            }
            if(type=='abort'){
              bench.abort();
              bench.emit('cycle');
            }else{
              event.currentTarget=event.target=bench;
              bench.emit(event);
            }
          }
        }elseif(bench.aborted){
          //Clearabortlistenerstoavoidtriggeringbench'sabort/cycleagain.
          clone.events.abort.length=0;
          clone.abort();
        }
      }

      /**
       *Determinesifmoreclonesshouldbequeuedorifcyclingshouldstop.
       */
      functionevaluate(event){
        varcritical,
            df,
            mean,
            moe,
            rme,
            sd,
            sem,
            variance,
            clone=event.target,
            done=bench.aborted,
            now=_.now(),
            size=sample.push(clone.times.period),
            maxedOut=size>=minSamples&&(elapsed+=now-clone.times.timeStamp)/1e3>bench.maxTime,
            times=bench.times,
            varOf=function(sum,x){returnsum+pow(x-mean,2);};

        //Exitearlyforabortedorunclockabletests.
        if(done||clone.hz==Infinity){
          maxedOut=!(size=sample.length=queue.length=0);
        }

        if(!done){
          //Computethesamplemean(estimateofthepopulationmean).
          mean=getMean(sample);
          //Computethesamplevariance(estimateofthepopulationvariance).
          variance=_.reduce(sample,varOf,0)/(size-1)||0;
          //Computethesamplestandarddeviation(estimateofthepopulationstandarddeviation).
          sd=sqrt(variance);
          //Computethestandarderrorofthemean(a.k.a.thestandarddeviationofthesamplingdistributionofthesamplemean).
          sem=sd/sqrt(size);
          //Computethedegreesoffreedom.
          df=size-1;
          //Computethecriticalvalue.
          critical=tTable[Math.round(df)||1]||tTable.infinity;
          //Computethemarginoferror.
          moe=sem*critical;
          //Computetherelativemarginoferror.
          rme=(moe/mean)*100||0;

          _.assign(bench.stats,{
            'deviation':sd,
            'mean':mean,
            'moe':moe,
            'rme':rme,
            'sem':sem,
            'variance':variance
          });

          //Abortthecycleloopwhentheminimumsamplesizehasbeencollected
          //andtheelapsedtimeexceedsthemaximumtimeallowedperbenchmark.
          //Wedon'tcountcycledelaystowardthemaxtimebecausedelaysmaybe
          //increasedbybrowsersthatclamptimeoutsforinactivetabs.Formore
          //informationseehttps://developer.mozilla.org/en/window.setTimeout#Inactive_tabs.
          if(maxedOut){
            //Resetthe`initCount`incasethebenchmarkisrerun.
            bench.initCount=initCount;
            bench.running=false;
            done=true;
            times.elapsed=(now-times.timeStamp)/1e3;
          }
          if(bench.hz!=Infinity){
            bench.hz=1/mean;
            times.cycle=mean*bench.count;
            times.period=mean;
          }
        }
        //Iftimepermits,increasesamplesizetoreducethemarginoferror.
        if(queue.length<2&&!maxedOut){
          enqueue();
        }
        //Abortthe`invoke`cyclewhendone.
        event.aborted=done;
      }

      //Initqueueandbegin.
      enqueue();
      invoke(queue,{
        'name':'run',
        'args':{'async':async},
        'queued':true,
        'onCycle':evaluate,
        'onComplete':function(){bench.emit('complete');}
      });
    }

    /*------------------------------------------------------------------------*/

    /**
     *Cyclesabenchmarkuntilarun`count`canbeestablished.
     *
     *@private
     *@param{Object}cloneTheclonedbenchmarkinstance.
     *@param{Object}optionsTheoptionsobject.
     */
    functioncycle(clone,options){
      options||(options={});

      vardeferred;
      if(cloneinstanceofDeferred){
        deferred=clone;
        clone=clone.benchmark;
      }
      varclocked,
          cycles,
          divisor,
          event,
          minTime,
          period,
          async=options.async,
          bench=clone._original,
          count=clone.count,
          times=clone.times;

      //Continue,ifnotabortedbetweencycles.
      if(clone.running){
        //`minTime`issetto`Benchmark.options.minTime`in`clock()`.
        cycles=++clone.cycles;
        clocked=deferred?deferred.elapsed:clock(clone);
        minTime=clone.minTime;

        if(cycles>bench.cycles){
          bench.cycles=cycles;
        }
        if(clone.error){
          event=Event('error');
          event.message=clone.error;
          clone.emit(event);
          if(!event.cancelled){
            clone.abort();
          }
        }
      }
      //Continue,ifnoterrored.
      if(clone.running){
        //Computethetimetakentocompletelasttestcycle.
        bench.times.cycle=times.cycle=clocked;
        //Computethesecondsperoperation.
        period=bench.times.period=times.period=clocked/count;
        //Computetheopspersecond.
        bench.hz=clone.hz=1/period;
        //Avoidworkingourwayuptothisnexttime.
        bench.initCount=clone.initCount=count;
        //Doweneedtodoanothercycle?
        clone.running=clocked<minTime;

        if(clone.running){
          //Testsmayclockat`0`when`initCount`isasmallnumber,
          //toavoidthatwesetitscounttosomethingabithigher.
          if(!clocked&&(divisor=divisors[clone.cycles])!=null){
            count=floor(4e6/divisor);
          }
          //Calculatehowmanymoreiterationsitwilltaketoachievethe`minTime`.
          if(count<=clone.count){
            count+=Math.ceil((minTime-clocked)/period);
          }
          clone.running=count!=Infinity;
        }
      }
      //Shouldweexitearly?
      event=Event('cycle');
      clone.emit(event);
      if(event.aborted){
        clone.abort();
      }
      //Figureoutwhattodonext.
      if(clone.running){
        //Startanewcycle.
        clone.count=count;
        if(deferred){
          clone.compiled.call(deferred,context,timer);
        }elseif(async){
          delay(clone,function(){cycle(clone,options);});
        }else{
          cycle(clone);
        }
      }
      else{
        //FixTraceMonkeybugassociatedwithclockfallbacks.
        //Formoreinformationseehttp://bugzil.la/509069.
        if(support.browser){
          runScript(uid+'=1;delete'+uid);
        }
        //We'redone.
        clone.emit('complete');
      }
    }

    /*------------------------------------------------------------------------*/

    /**
     *Runsthebenchmark.
     *
     *@memberOfBenchmark
     *@param{Object}[options={}]Optionsobject.
     *@returns{Object}Thebenchmarkinstance.
     *@example
     *
     *//basicusage
     *bench.run();
     *
     *//orwithoptions
     *bench.run({'async':true});
     */
    functionrun(options){
      varbench=this,
          event=Event('start');

      //Set`running`to`false`so`reset()`won'tcall`abort()`.
      bench.running=false;
      bench.reset();
      bench.running=true;

      bench.count=bench.initCount;
      bench.times.timeStamp=_.now();
      bench.emit(event);

      if(!event.cancelled){
        options={'async':((options=options&&options.async)==null?bench.async:options)&&support.timeout};

        //Forclonescreatedwithin`compute()`.
        if(bench._original){
          if(bench.defer){
            Deferred(bench);
          }else{
            cycle(bench,options);
          }
        }
        //Fororiginalbenchmarks.
        else{
          compute(bench,options);
        }
      }
      returnbench;
    }

    /*------------------------------------------------------------------------*/

    //Firefox1erroneouslydefinesvariableandargumentnamesoffunctionson
    //thefunctionitselfasnon-configurablepropertieswith`undefined`values.
    //Thebugginesscontinuesasthe`Benchmark`constructorhasanargument
    //named`options`andFirefox1willnotassignavalueto`Benchmark.options`,
    //makingitnon-writableintheprocess,unlessitisthefirstproperty
    //assignedbyfor-inloopof`_.assign()`.
    _.assign(Benchmark,{

      /**
       *Thedefaultoptionscopiedbybenchmarkinstances.
       *
       *@static
       *@memberOfBenchmark
       *@typeObject
       */
      'options':{

        /**
         *Aflagtoindicatethatbenchmarkcycleswillexecuteasynchronously
         *bydefault.
         *
         *@memberOfBenchmark.options
         *@typeboolean
         */
        'async':false,

        /**
         *Aflagtoindicatethatthebenchmarkclockisdeferred.
         *
         *@memberOfBenchmark.options
         *@typeboolean
         */
        'defer':false,

        /**
         *Thedelaybetweentestcycles(secs).
         *@memberOfBenchmark.options
         *@typenumber
         */
        'delay':0.005,

        /**
         *Displayedby`Benchmark#toString`whena`name`isnotavailable
         *(auto-generatedifabsent).
         *
         *@memberOfBenchmark.options
         *@typestring
         */
        'id':undefined,

        /**
         *Thedefaultnumberoftimestoexecuteatestonabenchmark'sfirstcycle.
         *
         *@memberOfBenchmark.options
         *@typenumber
         */
        'initCount':1,

        /**
         *Themaximumtimeabenchmarkisallowedtorunbeforefinishing(secs).
         *
         *Note:Cycledelaysaren'tcountedtowardthemaximumtime.
         *
         *@memberOfBenchmark.options
         *@typenumber
         */
        'maxTime':5,

        /**
         *Theminimumsamplesizerequiredtoperformstatisticalanalysis.
         *
         *@memberOfBenchmark.options
         *@typenumber
         */
        'minSamples':5,

        /**
         *Thetimeneededtoreducethepercentuncertaintyofmeasurementto1%(secs).
         *
         *@memberOfBenchmark.options
         *@typenumber
         */
        'minTime':0,

        /**
         *Thenameofthebenchmark.
         *
         *@memberOfBenchmark.options
         *@typestring
         */
        'name':undefined,

        /**
         *Aneventlistenercalledwhenthebenchmarkisaborted.
         *
         *@memberOfBenchmark.options
         *@typeFunction
         */
        'onAbort':undefined,

        /**
         *Aneventlistenercalledwhenthebenchmarkcompletesrunning.
         *
         *@memberOfBenchmark.options
         *@typeFunction
         */
        'onComplete':undefined,

        /**
         *Aneventlistenercalledaftereachruncycle.
         *
         *@memberOfBenchmark.options
         *@typeFunction
         */
        'onCycle':undefined,

        /**
         *Aneventlistenercalledwhenatesterrors.
         *
         *@memberOfBenchmark.options
         *@typeFunction
         */
        'onError':undefined,

        /**
         *Aneventlistenercalledwhenthebenchmarkisreset.
         *
         *@memberOfBenchmark.options
         *@typeFunction
         */
        'onReset':undefined,

        /**
         *Aneventlistenercalledwhenthebenchmarkstartsrunning.
         *
         *@memberOfBenchmark.options
         *@typeFunction
         */
        'onStart':undefined
      },

      /**
       *Platformobjectwithpropertiesdescribingthingslikebrowsername,
       *version,andoperatingsystem.See[`platform.js`](https://mths.be/platform).
       *
       *@static
       *@memberOfBenchmark
       *@typeObject
       */
      'platform':context.platform||require('platform')||({
        'description':context.navigator&&context.navigator.userAgent||null,
        'layout':null,
        'product':null,
        'name':null,
        'manufacturer':null,
        'os':null,
        'prerelease':null,
        'version':null,
        'toString':function(){
          returnthis.description||'';
        }
      }),

      /**
       *Thesemanticversionnumber.
       *
       *@static
       *@memberOfBenchmark
       *@typestring
       */
      'version':'2.1.4'
    });

    _.assign(Benchmark,{
      'filter':filter,
      'formatNumber':formatNumber,
      'invoke':invoke,
      'join':join,
      'runInContext':runInContext,
      'support':support
    });

    //AddlodashmethodstoBenchmark.
    _.each(['each','forEach','forOwn','has','indexOf','map','reduce'],function(methodName){
      Benchmark[methodName]=_[methodName];
    });

    /*------------------------------------------------------------------------*/

    _.assign(Benchmark.prototype,{

      /**
       *Thenumberoftimesatestwasexecuted.
       *
       *@memberOfBenchmark
       *@typenumber
       */
      'count':0,

      /**
       *Thenumberofcyclesperformedwhilebenchmarking.
       *
       *@memberOfBenchmark
       *@typenumber
       */
      'cycles':0,

      /**
       *Thenumberofexecutionspersecond.
       *
       *@memberOfBenchmark
       *@typenumber
       */
      'hz':0,

      /**
       *Thecompiledtestfunction.
       *
       *@memberOfBenchmark
       *@type{Function|string}
       */
      'compiled':undefined,

      /**
       *Theerrorobjectifthetestfailed.
       *
       *@memberOfBenchmark
       *@typeObject
       */
      'error':undefined,

      /**
       *Thetesttobenchmark.
       *
       *@memberOfBenchmark
       *@type{Function|string}
       */
      'fn':undefined,

      /**
       *Aflagtoindicateifthebenchmarkisaborted.
       *
       *@memberOfBenchmark
       *@typeboolean
       */
      'aborted':false,

      /**
       *Aflagtoindicateifthebenchmarkisrunning.
       *
       *@memberOfBenchmark
       *@typeboolean
       */
      'running':false,

      /**
       *Compiledintothetestandexecutedimmediately**before**thetestloop.
       *
       *@memberOfBenchmark
       *@type{Function|string}
       *@example
       *
       *//basicusage
       *varbench=Benchmark({
       *  'setup':function(){
       *    varc=this.count,
       *        element=document.getElementById('container');
       *    while(c--){
       *      element.appendChild(document.createElement('div'));
       *    }
       *  },
       *  'fn':function(){
       *    element.removeChild(element.lastChild);
       *  }
       *});
       *
       *//compilestosomethinglike:
       *varc=this.count,
       *    element=document.getElementById('container');
       *while(c--){
       *  element.appendChild(document.createElement('div'));
       *}
       *varstart=newDate;
       *while(count--){
       *  element.removeChild(element.lastChild);
       *}
       *varend=newDate-start;
       *
       *//orusingstrings
       *varbench=Benchmark({
       *  'setup':'\
       *    vara=0;\n\
       *    (function(){\n\
       *      (function(){\n\
       *        (function(){',
       *  'fn':'a+=1;',
       *  'teardown':'\
       *         }())\n\
       *       }())\n\
       *     }())'
       *});
       *
       *//compilestosomethinglike:
       *vara=0;
       *(function(){
       *  (function(){
       *    (function(){
       *      varstart=newDate;
       *      while(count--){
       *        a+=1;
       *      }
       *      varend=newDate-start;
       *    }())
       *  }())
       *}())
       */
      'setup':_.noop,

      /**
       *Compiledintothetestandexecutedimmediately**after**thetestloop.
       *
       *@memberOfBenchmark
       *@type{Function|string}
       */
      'teardown':_.noop,

      /**
       *Anobjectofstatsincludingmean,marginorerror,andstandarddeviation.
       *
       *@memberOfBenchmark
       *@typeObject
       */
      'stats':{

        /**
         *Themarginoferror.
         *
         *@memberOfBenchmark#stats
         *@typenumber
         */
        'moe':0,

        /**
         *Therelativemarginoferror(expressedasapercentageofthemean).
         *
         *@memberOfBenchmark#stats
         *@typenumber
         */
        'rme':0,

        /**
         *Thestandarderrorofthemean.
         *
         *@memberOfBenchmark#stats
         *@typenumber
         */
        'sem':0,

        /**
         *Thesamplestandarddeviation.
         *
         *@memberOfBenchmark#stats
         *@typenumber
         */
        'deviation':0,

        /**
         *Thesamplearithmeticmean(secs).
         *
         *@memberOfBenchmark#stats
         *@typenumber
         */
        'mean':0,

        /**
         *Thearrayofsampledperiods.
         *
         *@memberOfBenchmark#stats
         *@typeArray
         */
        'sample':[],

        /**
         *Thesamplevariance.
         *
         *@memberOfBenchmark#stats
         *@typenumber
         */
        'variance':0
      },

      /**
       *Anobjectoftimingdataincludingcycle,elapsed,period,start,andstop.
       *
       *@memberOfBenchmark
       *@typeObject
       */
      'times':{

        /**
         *Thetimetakentocompletethelastcycle(secs).
         *
         *@memberOfBenchmark#times
         *@typenumber
         */
        'cycle':0,

        /**
         *Thetimetakentocompletethebenchmark(secs).
         *
         *@memberOfBenchmark#times
         *@typenumber
         */
        'elapsed':0,

        /**
         *Thetimetakentoexecutethetestonce(secs).
         *
         *@memberOfBenchmark#times
         *@typenumber
         */
        'period':0,

        /**
         *Atimestampofwhenthebenchmarkstarted(ms).
         *
         *@memberOfBenchmark#times
         *@typenumber
         */
        'timeStamp':0
      }
    });

    _.assign(Benchmark.prototype,{
      'abort':abort,
      'clone':clone,
      'compare':compare,
      'emit':emit,
      'listeners':listeners,
      'off':off,
      'on':on,
      'reset':reset,
      'run':run,
      'toString':toStringBench
    });

    /*------------------------------------------------------------------------*/

    _.assign(Deferred.prototype,{

      /**
       *Thedeferredbenchmarkinstance.
       *
       *@memberOfBenchmark.Deferred
       *@typeObject
       */
      'benchmark':null,

      /**
       *Thenumberofdeferredcyclesperformedwhilebenchmarking.
       *
       *@memberOfBenchmark.Deferred
       *@typenumber
       */
      'cycles':0,

      /**
       *Thetimetakentocompletethedeferredbenchmark(secs).
       *
       *@memberOfBenchmark.Deferred
       *@typenumber
       */
      'elapsed':0,

      /**
       *Atimestampofwhenthedeferredbenchmarkstarted(ms).
       *
       *@memberOfBenchmark.Deferred
       *@typenumber
       */
      'timeStamp':0
    });

    _.assign(Deferred.prototype,{
      'resolve':resolve
    });

    /*------------------------------------------------------------------------*/

    _.assign(Event.prototype,{

      /**
       *Aflagtoindicateiftheemitterslisteneriterationisaborted.
       *
       *@memberOfBenchmark.Event
       *@typeboolean
       */
      'aborted':false,

      /**
       *Aflagtoindicateifthedefaultactioniscancelled.
       *
       *@memberOfBenchmark.Event
       *@typeboolean
       */
      'cancelled':false,

      /**
       *Theobjectwhoselistenersarecurrentlybeingprocessed.
       *
       *@memberOfBenchmark.Event
       *@typeObject
       */
      'currentTarget':undefined,

      /**
       *Thereturnvalueofthelastexecutedlistener.
       *
       *@memberOfBenchmark.Event
       *@typeMixed
       */
      'result':undefined,

      /**
       *Theobjecttowhichtheeventwasoriginallyemitted.
       *
       *@memberOfBenchmark.Event
       *@typeObject
       */
      'target':undefined,

      /**
       *Atimestampofwhentheeventwascreated(ms).
       *
       *@memberOfBenchmark.Event
       *@typenumber
       */
      'timeStamp':0,

      /**
       *Theeventtype.
       *
       *@memberOfBenchmark.Event
       *@typestring
       */
      'type':''
    });

    /*------------------------------------------------------------------------*/

    /**
     *Thedefaultoptionscopiedbysuiteinstances.
     *
     *@static
     *@memberOfBenchmark.Suite
     *@typeObject
     */
    Suite.options={

      /**
       *Thenameofthesuite.
       *
       *@memberOfBenchmark.Suite.options
       *@typestring
       */
      'name':undefined
    };

    /*------------------------------------------------------------------------*/

    _.assign(Suite.prototype,{

      /**
       *Thenumberofbenchmarksinthesuite.
       *
       *@memberOfBenchmark.Suite
       *@typenumber
       */
      'length':0,

      /**
       *Aflagtoindicateifthesuiteisaborted.
       *
       *@memberOfBenchmark.Suite
       *@typeboolean
       */
      'aborted':false,

      /**
       *Aflagtoindicateifthesuiteisrunning.
       *
       *@memberOfBenchmark.Suite
       *@typeboolean
       */
      'running':false
    });

    _.assign(Suite.prototype,{
      'abort':abortSuite,
      'add':add,
      'clone':cloneSuite,
      'emit':emit,
      'filter':filterSuite,
      'join':arrayRef.join,
      'listeners':listeners,
      'off':off,
      'on':on,
      'pop':arrayRef.pop,
      'push':push,
      'reset':resetSuite,
      'run':runSuite,
      'reverse':arrayRef.reverse,
      'shift':shift,
      'slice':slice,
      'sort':arrayRef.sort,
      'splice':arrayRef.splice,
      'unshift':unshift
    });

    /*------------------------------------------------------------------------*/

    //ExposeDeferred,Event,andSuite.
    _.assign(Benchmark,{
      'Deferred':Deferred,
      'Event':Event,
      'Suite':Suite
    });

    /*------------------------------------------------------------------------*/

    //AddlodashmethodsasSuitemethods.
    _.each(['each','forEach','indexOf','map','reduce'],function(methodName){
      varfunc=_[methodName];
      Suite.prototype[methodName]=function(){
        varargs=[this];
        push.apply(args,arguments);
        returnfunc.apply(_,args);
      };
    });

    //Avoidarray-likeobjectbugswith`Array#shift`and`Array#splice`
    //inFirefox<10andIE<9.
    _.each(['pop','shift','splice'],function(methodName){
      varfunc=arrayRef[methodName];

      Suite.prototype[methodName]=function(){
        varvalue=this,
            result=func.apply(value,arguments);

        if(value.length===0){
          deletevalue[0];
        }
        returnresult;
      };
    });

    //Avoidbuggy`Array#unshift`inIE<8whichdoesn'treturnthenew
    //lengthofthearray.
    Suite.prototype.unshift=function(){
      varvalue=this;
      unshift.apply(value,arguments);
      returnvalue.length;
    };

    returnBenchmark;
  }

  /*--------------------------------------------------------------------------*/

  //ExportBenchmark.
  //SomeAMDbuildoptimizers,liker.js,checkforconditionpatternslikethefollowing:
  if(typeofdefine=='function'&&typeofdefine.amd=='object'&&define.amd){
    //Defineasananonymousmoduleso,throughpathmapping,itcanbealiased.
    define(['lodash','platform'],function(_,platform){
      returnrunInContext({
        '_':_,
        'platform':platform
      });
    });
  }
  else{
    varBenchmark=runInContext();

    //Checkfor`exports`after`define`incaseabuildoptimizeraddsan`exports`object.
    if(freeExports&&freeModule){
      //ExportforNode.js.
      if(moduleExports){
        (freeModule.exports=Benchmark).Benchmark=Benchmark;
      }
      //ExportforCommonJSsupport.
      freeExports.Benchmark=Benchmark;
    }
    else{
      //Exporttotheglobalobject.
      root.Benchmark=Benchmark;
    }
  }
}.call(this));
