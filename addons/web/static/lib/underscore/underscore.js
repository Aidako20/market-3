//    Underscore.js1.8.2
//    http://underscorejs.org
//    (c)2009-2015JeremyAshkenas,DocumentCloudandInvestigativeReporters&Editors
//    UnderscoremaybefreelydistributedundertheMITlicense.

(function(){

  //Baselinesetup
  //--------------

  //Establishtherootobject,`window`inthebrowser,or`exports`ontheserver.
  varroot=this;

  //Savethepreviousvalueofthe`_`variable.
  varpreviousUnderscore=root._;

  //Savebytesintheminified(butnotgzipped)version:
  varArrayProto=Array.prototype,ObjProto=Object.prototype,FuncProto=Function.prototype;

  //Createquickreferencevariablesforspeedaccesstocoreprototypes.
  var
    push            =ArrayProto.push,
    slice           =ArrayProto.slice,
    toString        =ObjProto.toString,
    hasOwnProperty  =ObjProto.hasOwnProperty;

  //All**ECMAScript5**nativefunctionimplementationsthatwehopetouse
  //aredeclaredhere.
  var
    nativeIsArray     =Array.isArray,
    nativeKeys        =Object.keys,
    nativeBind        =FuncProto.bind,
    nativeCreate      =Object.create;

  //Nakedfunctionreferenceforsurrogate-prototype-swapping.
  varCtor=function(){};

  //CreateasafereferencetotheUnderscoreobjectforusebelow.
  var_=function(obj){
    if(objinstanceof_)returnobj;
    if(!(thisinstanceof_))returnnew_(obj);
    this._wrapped=obj;
  };

  //ExporttheUnderscoreobjectfor**Node.js**,with
  //backwards-compatibilityfortheold`require()`API.Ifwe'rein
  //thebrowser,add`_`asaglobalobject.
  if(typeofexports!=='undefined'){
    if(typeofmodule!=='undefined'&&module.exports){
      exports=module.exports=_;
    }
    exports._=_;
  }else{
    root._=_;
  }

  //Currentversion.
  _.VERSION='1.8.2';

  //Internalfunctionthatreturnsanefficient(forcurrentengines)version
  //ofthepassed-incallback,toberepeatedlyappliedinotherUnderscore
  //functions.
  varoptimizeCb=function(func,context,argCount){
    if(context===void0)returnfunc;
    switch(argCount==null?3:argCount){
      case1:returnfunction(value){
        returnfunc.call(context,value);
      };
      case2:returnfunction(value,other){
        returnfunc.call(context,value,other);
      };
      case3:returnfunction(value,index,collection){
        returnfunc.call(context,value,index,collection);
      };
      case4:returnfunction(accumulator,value,index,collection){
        returnfunc.call(context,accumulator,value,index,collection);
      };
    }
    returnfunction(){
      returnfunc.apply(context,arguments);
    };
  };

  //Amostly-internalfunctiontogeneratecallbacksthatcanbeapplied
  //toeachelementinacollection,returningthedesiredresult—either
  //identity,anarbitrarycallback,apropertymatcher,orapropertyaccessor.
  varcb=function(value,context,argCount){
    if(value==null)return_.identity;
    if(_.isFunction(value))returnoptimizeCb(value,context,argCount);
    if(_.isObject(value))return_.matcher(value);
    return_.property(value);
  };
  _.iteratee=function(value,context){
    returncb(value,context,Infinity);
  };

  //Aninternalfunctionforcreatingassignerfunctions.
  varcreateAssigner=function(keysFunc,undefinedOnly){
    returnfunction(obj){
      varlength=arguments.length;
      if(length<2||obj==null)returnobj;
      for(varindex=1;index<length;index++){
        varsource=arguments[index],
            keys=keysFunc(source),
            l=keys.length;
        for(vari=0;i<l;i++){
          varkey=keys[i];
          if(!undefinedOnly||obj[key]===void0)obj[key]=source[key];
        }
      }
      returnobj;
    };
  };

  //Aninternalfunctionforcreatinganewobjectthatinheritsfromanother.
  varbaseCreate=function(prototype){
    if(!_.isObject(prototype))return{};
    if(nativeCreate)returnnativeCreate(prototype);
    Ctor.prototype=prototype;
    varresult=newCtor;
    Ctor.prototype=null;
    returnresult;
  };

  //Helperforcollectionmethodstodeterminewhetheracollection
  //shouldbeiteratedasanarrayorasanobject
  //Related:http://people.mozilla.org/~jorendorff/es6-draft.html#sec-tolength
  varMAX_ARRAY_INDEX=Math.pow(2,53)-1;
  varisArrayLike=function(collection){
    varlength=collection&&collection.length;
    returntypeoflength=='number'&&length>=0&&length<=MAX_ARRAY_INDEX;
  };

  //CollectionFunctions
  //--------------------

  //Thecornerstone,an`each`implementation,aka`forEach`.
  //Handlesrawobjectsinadditiontoarray-likes.Treatsall
  //sparsearray-likesasiftheyweredense.
  _.each=_.forEach=function(obj,iteratee,context){
    iteratee=optimizeCb(iteratee,context);
    vari,length;
    if(isArrayLike(obj)){
      for(i=0,length=obj.length;i<length;i++){
        iteratee(obj[i],i,obj);
      }
    }else{
      varkeys=_.keys(obj);
      for(i=0,length=keys.length;i<length;i++){
        iteratee(obj[keys[i]],keys[i],obj);
      }
    }
    returnobj;
  };

  //Returntheresultsofapplyingtheiterateetoeachelement.
  _.map=_.collect=function(obj,iteratee,context){
    iteratee=cb(iteratee,context);
    varkeys=!isArrayLike(obj)&&_.keys(obj),
        length=(keys||obj).length,
        results=Array(length);
    for(varindex=0;index<length;index++){
      varcurrentKey=keys?keys[index]:index;
      results[index]=iteratee(obj[currentKey],currentKey,obj);
    }
    returnresults;
  };

  //Createareducingfunctioniteratingleftorright.
  functioncreateReduce(dir){
    //Optimizediteratorfunctionasusingarguments.length
    //inthemainfunctionwilldeoptimizethe,see#1991.
    functioniterator(obj,iteratee,memo,keys,index,length){
      for(;index>=0&&index<length;index+=dir){
        varcurrentKey=keys?keys[index]:index;
        memo=iteratee(memo,obj[currentKey],currentKey,obj);
      }
      returnmemo;
    }

    returnfunction(obj,iteratee,memo,context){
      iteratee=optimizeCb(iteratee,context,4);
      varkeys=!isArrayLike(obj)&&_.keys(obj),
          length=(keys||obj).length,
          index=dir>0?0:length-1;
      //Determinetheinitialvalueifnoneisprovided.
      if(arguments.length<3){
        memo=obj[keys?keys[index]:index];
        index+=dir;
      }
      returniterator(obj,iteratee,memo,keys,index,length);
    };
  }

  //**Reduce**buildsupasingleresultfromalistofvalues,aka`inject`,
  //or`foldl`.
  _.reduce=_.foldl=_.inject=createReduce(1);

  //Theright-associativeversionofreduce,alsoknownas`foldr`.
  _.reduceRight=_.foldr=createReduce(-1);

  //Returnthefirstvaluewhichpassesatruthtest.Aliasedas`detect`.
  _.find=_.detect=function(obj,predicate,context){
    varkey;
    if(isArrayLike(obj)){
      key=_.findIndex(obj,predicate,context);
    }else{
      key=_.findKey(obj,predicate,context);
    }
    if(key!==void0&&key!==-1)returnobj[key];
  };

  //Returnalltheelementsthatpassatruthtest.
  //Aliasedas`select`.
  _.filter=_.select=function(obj,predicate,context){
    varresults=[];
    predicate=cb(predicate,context);
    _.each(obj,function(value,index,list){
      if(predicate(value,index,list))results.push(value);
    });
    returnresults;
  };

  //Returnalltheelementsforwhichatruthtestfails.
  _.reject=function(obj,predicate,context){
    return_.filter(obj,_.negate(cb(predicate)),context);
  };

  //Determinewhetheralloftheelementsmatchatruthtest.
  //Aliasedas`all`.
  _.every=_.all=function(obj,predicate,context){
    predicate=cb(predicate,context);
    varkeys=!isArrayLike(obj)&&_.keys(obj),
        length=(keys||obj).length;
    for(varindex=0;index<length;index++){
      varcurrentKey=keys?keys[index]:index;
      if(!predicate(obj[currentKey],currentKey,obj))returnfalse;
    }
    returntrue;
  };

  //Determineifatleastoneelementintheobjectmatchesatruthtest.
  //Aliasedas`any`.
  _.some=_.any=function(obj,predicate,context){
    predicate=cb(predicate,context);
    varkeys=!isArrayLike(obj)&&_.keys(obj),
        length=(keys||obj).length;
    for(varindex=0;index<length;index++){
      varcurrentKey=keys?keys[index]:index;
      if(predicate(obj[currentKey],currentKey,obj))returntrue;
    }
    returnfalse;
  };

  //Determineifthearrayorobjectcontainsagivenvalue(using`===`).
  //Aliasedas`includes`and`include`.
  _.contains=_.includes=_.include=function(obj,target,fromIndex){
    if(!isArrayLike(obj))obj=_.values(obj);
    return_.indexOf(obj,target,typeoffromIndex=='number'&&fromIndex)>=0;
  };

  //Invokeamethod(witharguments)oneveryiteminacollection.
  _.invoke=function(obj,method){
    varargs=slice.call(arguments,2);
    varisFunc=_.isFunction(method);
    return_.map(obj,function(value){
      varfunc=isFunc?method:value[method];
      returnfunc==null?func:func.apply(value,args);
    });
  };

  //Convenienceversionofacommonusecaseof`map`:fetchingaproperty.
  _.pluck=function(obj,key){
    return_.map(obj,_.property(key));
  };

  //Convenienceversionofacommonusecaseof`filter`:selectingonlyobjects
  //containingspecific`key:value`pairs.
  _.where=function(obj,attrs){
    return_.filter(obj,_.matcher(attrs));
  };

  //Convenienceversionofacommonusecaseof`find`:gettingthefirstobject
  //containingspecific`key:value`pairs.
  _.findWhere=function(obj,attrs){
    return_.find(obj,_.matcher(attrs));
  };

  //Returnthemaximumelement(orelement-basedcomputation).
  _.max=function(obj,iteratee,context){
    varresult=-Infinity,lastComputed=-Infinity,
        value,computed;
    if(iteratee==null&&obj!=null){
      obj=isArrayLike(obj)?obj:_.values(obj);
      for(vari=0,length=obj.length;i<length;i++){
        value=obj[i];
        if(value>result){
          result=value;
        }
      }
    }else{
      iteratee=cb(iteratee,context);
      _.each(obj,function(value,index,list){
        computed=iteratee(value,index,list);
        if(computed>lastComputed||computed===-Infinity&&result===-Infinity){
          result=value;
          lastComputed=computed;
        }
      });
    }
    returnresult;
  };

  //Returntheminimumelement(orelement-basedcomputation).
  _.min=function(obj,iteratee,context){
    varresult=Infinity,lastComputed=Infinity,
        value,computed;
    if(iteratee==null&&obj!=null){
      obj=isArrayLike(obj)?obj:_.values(obj);
      for(vari=0,length=obj.length;i<length;i++){
        value=obj[i];
        if(value<result){
          result=value;
        }
      }
    }else{
      iteratee=cb(iteratee,context);
      _.each(obj,function(value,index,list){
        computed=iteratee(value,index,list);
        if(computed<lastComputed||computed===Infinity&&result===Infinity){
          result=value;
          lastComputed=computed;
        }
      });
    }
    returnresult;
  };

  //Shuffleacollection,usingthemodernversionofthe
  //[Fisher-Yatesshuffle](http://en.wikipedia.org/wiki/Fisher–Yates_shuffle).
  _.shuffle=function(obj){
    varset=isArrayLike(obj)?obj:_.values(obj);
    varlength=set.length;
    varshuffled=Array(length);
    for(varindex=0,rand;index<length;index++){
      rand=_.random(0,index);
      if(rand!==index)shuffled[index]=shuffled[rand];
      shuffled[rand]=set[index];
    }
    returnshuffled;
  };

  //Sample**n**randomvaluesfromacollection.
  //If**n**isnotspecified,returnsasinglerandomelement.
  //Theinternal`guard`argumentallowsittoworkwith`map`.
  _.sample=function(obj,n,guard){
    if(n==null||guard){
      if(!isArrayLike(obj))obj=_.values(obj);
      returnobj[_.random(obj.length-1)];
    }
    return_.shuffle(obj).slice(0,Math.max(0,n));
  };

  //Sorttheobject'svaluesbyacriterionproducedbyaniteratee.
  _.sortBy=function(obj,iteratee,context){
    iteratee=cb(iteratee,context);
    return_.pluck(_.map(obj,function(value,index,list){
      return{
        value:value,
        index:index,
        criteria:iteratee(value,index,list)
      };
    }).sort(function(left,right){
      vara=left.criteria;
      varb=right.criteria;
      if(a!==b){
        if(a>b||a===void0)return1;
        if(a<b||b===void0)return-1;
      }
      returnleft.index-right.index;
    }),'value');
  };

  //Aninternalfunctionusedforaggregate"groupby"operations.
  vargroup=function(behavior){
    returnfunction(obj,iteratee,context){
      varresult={};
      iteratee=cb(iteratee,context);
      _.each(obj,function(value,index){
        varkey=iteratee(value,index,obj);
        behavior(result,value,key);
      });
      returnresult;
    };
  };

  //Groupstheobject'svaluesbyacriterion.Passeitherastringattribute
  //togroupby,orafunctionthatreturnsthecriterion.
  _.groupBy=group(function(result,value,key){
    if(_.has(result,key))result[key].push(value);elseresult[key]=[value];
  });

  //Indexestheobject'svaluesbyacriterion,similarto`groupBy`,butfor
  //whenyouknowthatyourindexvalueswillbeunique.
  _.indexBy=group(function(result,value,key){
    result[key]=value;
  });

  //Countsinstancesofanobjectthatgroupbyacertaincriterion.Pass
  //eitherastringattributetocountby,orafunctionthatreturnsthe
  //criterion.
  _.countBy=group(function(result,value,key){
    if(_.has(result,key))result[key]++;elseresult[key]=1;
  });

  //Safelycreateareal,livearrayfromanythingiterable.
  _.toArray=function(obj){
    if(!obj)return[];
    if(_.isArray(obj))returnslice.call(obj);
    if(isArrayLike(obj))return_.map(obj,_.identity);
    return_.values(obj);
  };

  //Returnthenumberofelementsinanobject.
  _.size=function(obj){
    if(obj==null)return0;
    returnisArrayLike(obj)?obj.length:_.keys(obj).length;
  };

  //Splitacollectionintotwoarrays:onewhoseelementsallsatisfythegiven
  //predicate,andonewhoseelementsalldonotsatisfythepredicate.
  _.partition=function(obj,predicate,context){
    predicate=cb(predicate,context);
    varpass=[],fail=[];
    _.each(obj,function(value,key,obj){
      (predicate(value,key,obj)?pass:fail).push(value);
    });
    return[pass,fail];
  };

  //ArrayFunctions
  //---------------

  //Getthefirstelementofanarray.Passing**n**willreturnthefirstN
  //valuesinthearray.Aliasedas`head`and`take`.The**guard**check
  //allowsittoworkwith`_.map`.
  _.first=_.head=_.take=function(array,n,guard){
    if(array==null)returnvoid0;
    if(n==null||guard)returnarray[0];
    return_.initial(array,array.length-n);
  };

  //Returnseverythingbutthelastentryofthearray.Especiallyusefulon
  //theargumentsobject.Passing**n**willreturnallthevaluesin
  //thearray,excludingthelastN.
  _.initial=function(array,n,guard){
    returnslice.call(array,0,Math.max(0,array.length-(n==null||guard?1:n)));
  };

  //Getthelastelementofanarray.Passing**n**willreturnthelastN
  //valuesinthearray.
  _.last=function(array,n,guard){
    if(array==null)returnvoid0;
    if(n==null||guard)returnarray[array.length-1];
    return_.rest(array,Math.max(0,array.length-n));
  };

  //Returnseverythingbutthefirstentryofthearray.Aliasedas`tail`and`drop`.
  //Especiallyusefulontheargumentsobject.Passingan**n**willreturn
  //therestNvaluesinthearray.
  _.rest=_.tail=_.drop=function(array,n,guard){
    returnslice.call(array,n==null||guard?1:n);
  };

  //Trimoutallfalsyvaluesfromanarray.
  _.compact=function(array){
    return_.filter(array,_.identity);
  };

  //Internalimplementationofarecursive`flatten`function.
  varflatten=function(input,shallow,strict,startIndex){
    varoutput=[],idx=0;
    for(vari=startIndex||0,length=input&&input.length;i<length;i++){
      varvalue=input[i];
      if(isArrayLike(value)&&(_.isArray(value)||_.isArguments(value))){
        //flattencurrentlevelofarrayorargumentsobject
        if(!shallow)value=flatten(value,shallow,strict);
        varj=0,len=value.length;
        output.length+=len;
        while(j<len){
          output[idx++]=value[j++];
        }
      }elseif(!strict){
        output[idx++]=value;
      }
    }
    returnoutput;
  };

  //Flattenoutanarray,eitherrecursively(bydefault),orjustonelevel.
  _.flatten=function(array,shallow){
    returnflatten(array,shallow,false);
  };

  //Returnaversionofthearraythatdoesnotcontainthespecifiedvalue(s).
  _.without=function(array){
    return_.difference(array,slice.call(arguments,1));
  };

  //Produceaduplicate-freeversionofthearray.Ifthearrayhasalready
  //beensorted,youhavetheoptionofusingafasteralgorithm.
  //Aliasedas`unique`.
  _.uniq=_.unique=function(array,isSorted,iteratee,context){
    if(array==null)return[];
    if(!_.isBoolean(isSorted)){
      context=iteratee;
      iteratee=isSorted;
      isSorted=false;
    }
    if(iteratee!=null)iteratee=cb(iteratee,context);
    varresult=[];
    varseen=[];
    for(vari=0,length=array.length;i<length;i++){
      varvalue=array[i],
          computed=iteratee?iteratee(value,i,array):value;
      if(isSorted){
        if(!i||seen!==computed)result.push(value);
        seen=computed;
      }elseif(iteratee){
        if(!_.contains(seen,computed)){
          seen.push(computed);
          result.push(value);
        }
      }elseif(!_.contains(result,value)){
        result.push(value);
      }
    }
    returnresult;
  };

  //Produceanarraythatcontainstheunion:eachdistinctelementfromallof
  //thepassed-inarrays.
  _.union=function(){
    return_.uniq(flatten(arguments,true,true));
  };

  //Produceanarraythatcontainseveryitemsharedbetweenallthe
  //passed-inarrays.
  _.intersection=function(array){
    if(array==null)return[];
    varresult=[];
    varargsLength=arguments.length;
    for(vari=0,length=array.length;i<length;i++){
      varitem=array[i];
      if(_.contains(result,item))continue;
      for(varj=1;j<argsLength;j++){
        if(!_.contains(arguments[j],item))break;
      }
      if(j===argsLength)result.push(item);
    }
    returnresult;
  };

  //Takethedifferencebetweenonearrayandanumberofotherarrays.
  //Onlytheelementspresentinjustthefirstarraywillremain.
  _.difference=function(array){
    varrest=flatten(arguments,true,true,1);
    return_.filter(array,function(value){
      return!_.contains(rest,value);
    });
  };

  //Ziptogethermultiplelistsintoasinglearray--elementsthatshare
  //anindexgotogether.
  _.zip=function(){
    return_.unzip(arguments);
  };

  //Complementof_.zip.Unzipacceptsanarrayofarraysandgroups
  //eacharray'selementsonsharedindices
  _.unzip=function(array){
    varlength=array&&_.max(array,'length').length||0;
    varresult=Array(length);

    for(varindex=0;index<length;index++){
      result[index]=_.pluck(array,index);
    }
    returnresult;
  };

  //Convertslistsintoobjects.Passeitherasinglearrayof`[key,value]`
  //pairs,ortwoparallelarraysofthesamelength--oneofkeys,andoneof
  //thecorrespondingvalues.
  _.object=function(list,values){
    varresult={};
    for(vari=0,length=list&&list.length;i<length;i++){
      if(values){
        result[list[i]]=values[i];
      }else{
        result[list[i][0]]=list[i][1];
      }
    }
    returnresult;
  };

  //Returnthepositionofthefirstoccurrenceofaniteminanarray,
  //or-1iftheitemisnotincludedinthearray.
  //Ifthearrayislargeandalreadyinsortorder,pass`true`
  //for**isSorted**tousebinarysearch.
  _.indexOf=function(array,item,isSorted){
    vari=0,length=array&&array.length;
    if(typeofisSorted=='number'){
      i=isSorted<0?Math.max(0,length+isSorted):isSorted;
    }elseif(isSorted&&length){
      i=_.sortedIndex(array,item);
      returnarray[i]===item?i:-1;
    }
    if(item!==item){
      return_.findIndex(slice.call(array,i),_.isNaN);
    }
    for(;i<length;i++)if(array[i]===item)returni;
    return-1;
  };

  _.lastIndexOf=function(array,item,from){
    varidx=array?array.length:0;
    if(typeoffrom=='number'){
      idx=from<0?idx+from+1:Math.min(idx,from+1);
    }
    if(item!==item){
      return_.findLastIndex(slice.call(array,0,idx),_.isNaN);
    }
    while(--idx>=0)if(array[idx]===item)returnidx;
    return-1;
  };

  //GeneratorfunctiontocreatethefindIndexandfindLastIndexfunctions
  functioncreateIndexFinder(dir){
    returnfunction(array,predicate,context){
      predicate=cb(predicate,context);
      varlength=array!=null&&array.length;
      varindex=dir>0?0:length-1;
      for(;index>=0&&index<length;index+=dir){
        if(predicate(array[index],index,array))returnindex;
      }
      return-1;
    };
  }

  //Returnsthefirstindexonanarray-likethatpassesapredicatetest
  _.findIndex=createIndexFinder(1);

  _.findLastIndex=createIndexFinder(-1);

  //Useacomparatorfunctiontofigureoutthesmallestindexatwhich
  //anobjectshouldbeinsertedsoastomaintainorder.Usesbinarysearch.
  _.sortedIndex=function(array,obj,iteratee,context){
    iteratee=cb(iteratee,context,1);
    varvalue=iteratee(obj);
    varlow=0,high=array.length;
    while(low<high){
      varmid=Math.floor((low+high)/2);
      if(iteratee(array[mid])<value)low=mid+1;elsehigh=mid;
    }
    returnlow;
  };

  //GenerateanintegerArraycontaininganarithmeticprogression.Aportof
  //thenativePython`range()`function.See
  //[thePythondocumentation](http://docs.python.org/library/functions.html#range).
  _.range=function(start,stop,step){
    if(arguments.length<=1){
      stop=start||0;
      start=0;
    }
    step=step||1;

    varlength=Math.max(Math.ceil((stop-start)/step),0);
    varrange=Array(length);

    for(varidx=0;idx<length;idx++,start+=step){
      range[idx]=start;
    }

    returnrange;
  };

  //Function(ahem)Functions
  //------------------

  //Determineswhethertoexecuteafunctionasaconstructor
  //oranormalfunctionwiththeprovidedarguments
  varexecuteBound=function(sourceFunc,boundFunc,context,callingContext,args){
    if(!(callingContextinstanceofboundFunc))returnsourceFunc.apply(context,args);
    varself=baseCreate(sourceFunc.prototype);
    varresult=sourceFunc.apply(self,args);
    if(_.isObject(result))returnresult;
    returnself;
  };

  //Createafunctionboundtoagivenobject(assigning`this`,andarguments,
  //optionally).Delegatesto**ECMAScript5**'snative`Function.bind`if
  //available.
  _.bind=function(func,context){
    if(nativeBind&&func.bind===nativeBind)returnnativeBind.apply(func,slice.call(arguments,1));
    if(!_.isFunction(func))thrownewTypeError('Bindmustbecalledonafunction');
    varargs=slice.call(arguments,2);
    varbound=function(){
      returnexecuteBound(func,bound,context,this,args.concat(slice.call(arguments)));
    };
    returnbound;
  };

  //Partiallyapplyafunctionbycreatingaversionthathashadsomeofits
  //argumentspre-filled,withoutchangingitsdynamic`this`context._acts
  //asaplaceholder,allowinganycombinationofargumentstobepre-filled.
  _.partial=function(func){
    varboundArgs=slice.call(arguments,1);
    varbound=function(){
      varposition=0,length=boundArgs.length;
      varargs=Array(length);
      for(vari=0;i<length;i++){
        args[i]=boundArgs[i]===_?arguments[position++]:boundArgs[i];
      }
      while(position<arguments.length)args.push(arguments[position++]);
      returnexecuteBound(func,bound,this,this,args);
    };
    returnbound;
  };

  //Bindanumberofanobject'smethodstothatobject.Remainingarguments
  //arethemethodnamestobebound.Usefulforensuringthatallcallbacks
  //definedonanobjectbelongtoit.
  _.bindAll=function(obj){
    vari,length=arguments.length,key;
    if(length<=1)thrownewError('bindAllmustbepassedfunctionnames');
    for(i=1;i<length;i++){
      key=arguments[i];
      obj[key]=_.bind(obj[key],obj);
    }
    returnobj;
  };

  //Memoizeanexpensivefunctionbystoringitsresults.
  _.memoize=function(func,hasher){
    varmemoize=function(key){
      varcache=memoize.cache;
      varaddress=''+(hasher?hasher.apply(this,arguments):key);
      if(!_.has(cache,address))cache[address]=func.apply(this,arguments);
      returncache[address];
    };
    memoize.cache={};
    returnmemoize;
  };

  //Delaysafunctionforthegivennumberofmilliseconds,andthencalls
  //itwiththeargumentssupplied.
  _.delay=function(func,wait){
    varargs=slice.call(arguments,2);
    returnsetTimeout(function(){
      returnfunc.apply(null,args);
    },wait);
  };

  //Defersafunction,schedulingittorunafterthecurrentcallstackhas
  //cleared.
  _.defer=_.partial(_.delay,_,1);

  //Returnsafunction,that,wheninvoked,willonlybetriggeredatmostonce
  //duringagivenwindowoftime.Normally,thethrottledfunctionwillrun
  //asmuchasitcan,withoutevergoingmorethanonceper`wait`duration;
  //butifyou'dliketodisabletheexecutionontheleadingedge,pass
  //`{leading:false}`.Todisableexecutiononthetrailingedge,ditto.
  _.throttle=function(func,wait,options){
    varcontext,args,result;
    vartimeout=null;
    varprevious=0;
    if(!options)options={};
    varlater=function(){
      previous=options.leading===false?0:_.now();
      timeout=null;
      result=func.apply(context,args);
      if(!timeout)context=args=null;
    };
    returnfunction(){
      varnow=_.now();
      if(!previous&&options.leading===false)previous=now;
      varremaining=wait-(now-previous);
      context=this;
      args=arguments;
      if(remaining<=0||remaining>wait){
        if(timeout){
          clearTimeout(timeout);
          timeout=null;
        }
        previous=now;
        result=func.apply(context,args);
        if(!timeout)context=args=null;
      }elseif(!timeout&&options.trailing!==false){
        timeout=setTimeout(later,remaining);
      }
      returnresult;
    };
  };

  //Returnsafunction,that,aslongasitcontinuestobeinvoked,willnot
  //betriggered.Thefunctionwillbecalledafteritstopsbeingcalledfor
  //Nmilliseconds.If`immediate`ispassed,triggerthefunctiononthe
  //leadingedge,insteadofthetrailing.
  _.debounce=function(func,wait,immediate){
    vartimeout,args,context,timestamp,result;

    varlater=function(){
      varlast=_.now()-timestamp;

      if(last<wait&&last>=0){
        timeout=setTimeout(later,wait-last);
      }else{
        timeout=null;
        if(!immediate){
          result=func.apply(context,args);
          if(!timeout)context=args=null;
        }
      }
    };

    returnfunction(){
      context=this;
      args=arguments;
      timestamp=_.now();
      varcallNow=immediate&&!timeout;
      if(!timeout)timeout=setTimeout(later,wait);
      if(callNow){
        result=func.apply(context,args);
        context=args=null;
      }

      returnresult;
    };
  };

  //Returnsthefirstfunctionpassedasanargumenttothesecond,
  //allowingyoutoadjustarguments,runcodebeforeandafter,and
  //conditionallyexecutetheoriginalfunction.
  _.wrap=function(func,wrapper){
    return_.partial(wrapper,func);
  };

  //Returnsanegatedversionofthepassed-inpredicate.
  _.negate=function(predicate){
    returnfunction(){
      return!predicate.apply(this,arguments);
    };
  };

  //Returnsafunctionthatisthecompositionofalistoffunctions,each
  //consumingthereturnvalueofthefunctionthatfollows.
  _.compose=function(){
    varargs=arguments;
    varstart=args.length-1;
    returnfunction(){
      vari=start;
      varresult=args[start].apply(this,arguments);
      while(i--)result=args[i].call(this,result);
      returnresult;
    };
  };

  //ReturnsafunctionthatwillonlybeexecutedonandaftertheNthcall.
  _.after=function(times,func){
    returnfunction(){
      if(--times<1){
        returnfunc.apply(this,arguments);
      }
    };
  };

  //Returnsafunctionthatwillonlybeexecutedupto(butnotincluding)theNthcall.
  _.before=function(times,func){
    varmemo;
    returnfunction(){
      if(--times>0){
        memo=func.apply(this,arguments);
      }
      if(times<=1)func=null;
      returnmemo;
    };
  };

  //Returnsafunctionthatwillbeexecutedatmostonetime,nomatterhow
  //oftenyoucallit.Usefulforlazyinitialization.
  _.once=_.partial(_.before,2);

  //ObjectFunctions
  //----------------

  //KeysinIE<9thatwon'tbeiteratedby`forkeyin...`andthusmissed.
  varhasEnumBug=!{toString:null}.propertyIsEnumerable('toString');
  varnonEnumerableProps=['valueOf','isPrototypeOf','toString',
                      'propertyIsEnumerable','hasOwnProperty','toLocaleString'];

  functioncollectNonEnumProps(obj,keys){
    varnonEnumIdx=nonEnumerableProps.length;
    varconstructor=obj.constructor;
    varproto=(_.isFunction(constructor)&&constructor.prototype)||ObjProto;

    //Constructorisaspecialcase.
    varprop='constructor';
    if(_.has(obj,prop)&&!_.contains(keys,prop))keys.push(prop);

    while(nonEnumIdx--){
      prop=nonEnumerableProps[nonEnumIdx];
      if(propinobj&&obj[prop]!==proto[prop]&&!_.contains(keys,prop)){
        keys.push(prop);
      }
    }
  }

  //Retrievethenamesofanobject'sownproperties.
  //Delegatesto**ECMAScript5**'snative`Object.keys`
  _.keys=function(obj){
    if(!_.isObject(obj))return[];
    if(nativeKeys)returnnativeKeys(obj);
    varkeys=[];
    for(varkeyinobj)if(_.has(obj,key))keys.push(key);
    //Ahem,IE<9.
    if(hasEnumBug)collectNonEnumProps(obj,keys);
    returnkeys;
  };

  //Retrieveallthepropertynamesofanobject.
  _.allKeys=function(obj){
    if(!_.isObject(obj))return[];
    varkeys=[];
    for(varkeyinobj)keys.push(key);
    //Ahem,IE<9.
    if(hasEnumBug)collectNonEnumProps(obj,keys);
    returnkeys;
  };

  //Retrievethevaluesofanobject'sproperties.
  _.values=function(obj){
    varkeys=_.keys(obj);
    varlength=keys.length;
    varvalues=Array(length);
    for(vari=0;i<length;i++){
      values[i]=obj[keys[i]];
    }
    returnvalues;
  };

  //Returnstheresultsofapplyingtheiterateetoeachelementoftheobject
  //Incontrastto_.mapitreturnsanobject
  _.mapObject=function(obj,iteratee,context){
    iteratee=cb(iteratee,context);
    varkeys= _.keys(obj),
          length=keys.length,
          results={},
          currentKey;
      for(varindex=0;index<length;index++){
        currentKey=keys[index];
        results[currentKey]=iteratee(obj[currentKey],currentKey,obj);
      }
      returnresults;
  };

  //Convertanobjectintoalistof`[key,value]`pairs.
  _.pairs=function(obj){
    varkeys=_.keys(obj);
    varlength=keys.length;
    varpairs=Array(length);
    for(vari=0;i<length;i++){
      pairs[i]=[keys[i],obj[keys[i]]];
    }
    returnpairs;
  };

  //Invertthekeysandvaluesofanobject.Thevaluesmustbeserializable.
  _.invert=function(obj){
    varresult={};
    varkeys=_.keys(obj);
    for(vari=0,length=keys.length;i<length;i++){
      result[obj[keys[i]]]=keys[i];
    }
    returnresult;
  };

  //Returnasortedlistofthefunctionnamesavailableontheobject.
  //Aliasedas`methods`
  _.functions=_.methods=function(obj){
    varnames=[];
    for(varkeyinobj){
      if(_.isFunction(obj[key]))names.push(key);
    }
    returnnames.sort();
  };

  //Extendagivenobjectwithallthepropertiesinpassed-inobject(s).
  _.extend=createAssigner(_.allKeys);

  //Assignsagivenobjectwithalltheownpropertiesinthepassed-inobject(s)
  //(https://developer.mozilla.org/docs/Web/JavaScript/Reference/Global_Objects/Object/assign)
  _.extendOwn=_.assign=createAssigner(_.keys);

  //Returnsthefirstkeyonanobjectthatpassesapredicatetest
  _.findKey=function(obj,predicate,context){
    predicate=cb(predicate,context);
    varkeys=_.keys(obj),key;
    for(vari=0,length=keys.length;i<length;i++){
      key=keys[i];
      if(predicate(obj[key],key,obj))returnkey;
    }
  };

  //Returnacopyoftheobjectonlycontainingthewhitelistedproperties.
  _.pick=function(object,oiteratee,context){
    varresult={},obj=object,iteratee,keys;
    if(obj==null)returnresult;
    if(_.isFunction(oiteratee)){
      keys=_.allKeys(obj);
      iteratee=optimizeCb(oiteratee,context);
    }else{
      keys=flatten(arguments,false,false,1);
      iteratee=function(value,key,obj){returnkeyinobj;};
      obj=Object(obj);
    }
    for(vari=0,length=keys.length;i<length;i++){
      varkey=keys[i];
      varvalue=obj[key];
      if(iteratee(value,key,obj))result[key]=value;
    }
    returnresult;
  };

   //Returnacopyoftheobjectwithouttheblacklistedproperties.
  _.omit=function(obj,iteratee,context){
    if(_.isFunction(iteratee)){
      iteratee=_.negate(iteratee);
    }else{
      varkeys=_.map(flatten(arguments,false,false,1),String);
      iteratee=function(value,key){
        return!_.contains(keys,key);
      };
    }
    return_.pick(obj,iteratee,context);
  };

  //Fillinagivenobjectwithdefaultproperties.
  _.defaults=createAssigner(_.allKeys,true);

  //Createa(shallow-cloned)duplicateofanobject.
  _.clone=function(obj){
    if(!_.isObject(obj))returnobj;
    return_.isArray(obj)?obj.slice():_.extend({},obj);
  };

  //Invokesinterceptorwiththeobj,andthenreturnsobj.
  //Theprimarypurposeofthismethodisto"tapinto"amethodchain,in
  //ordertoperformoperationsonintermediateresultswithinthechain.
  _.tap=function(obj,interceptor){
    interceptor(obj);
    returnobj;
  };

  //Returnswhetheranobjecthasagivensetof`key:value`pairs.
  _.isMatch=function(object,attrs){
    varkeys=_.keys(attrs),length=keys.length;
    if(object==null)return!length;
    varobj=Object(object);
    for(vari=0;i<length;i++){
      varkey=keys[i];
      if(attrs[key]!==obj[key]||!(keyinobj))returnfalse;
    }
    returntrue;
  };


  //Internalrecursivecomparisonfunctionfor`isEqual`.
  vareq=function(a,b,aStack,bStack){
    //Identicalobjectsareequal.`0===-0`,buttheyaren'tidentical.
    //Seethe[Harmony`egal`proposal](http://wiki.ecmascript.org/doku.php?id=harmony:egal).
    if(a===b)returna!==0||1/a===1/b;
    //Astrictcomparisonisnecessarybecause`null==undefined`.
    if(a==null||b==null)returna===b;
    //Unwrapanywrappedobjects.
    if(ainstanceof_)a=a._wrapped;
    if(binstanceof_)b=b._wrapped;
    //Compare`[[Class]]`names.
    varclassName=toString.call(a);
    if(className!==toString.call(b))returnfalse;
    switch(className){
      //Strings,numbers,regularexpressions,dates,andbooleansarecomparedbyvalue.
      case'[objectRegExp]':
      //RegExpsarecoercedtostringsforcomparison(Note:''+/a/i==='/a/i')
      case'[objectString]':
        //Primitivesandtheircorrespondingobjectwrappersareequivalent;thus,`"5"`is
        //equivalentto`newString("5")`.
        return''+a===''+b;
      case'[objectNumber]':
        //`NaN`sareequivalent,butnon-reflexive.
        //Object(NaN)isequivalenttoNaN
        if(+a!==+a)return+b!==+b;
        //An`egal`comparisonisperformedforothernumericvalues.
        return+a===0?1/+a===1/b:+a===+b;
      case'[objectDate]':
      case'[objectBoolean]':
        //Coercedatesandbooleanstonumericprimitivevalues.Datesarecomparedbytheir
        //millisecondrepresentations.Notethatinvaliddateswithmillisecondrepresentations
        //of`NaN`arenotequivalent.
        return+a===+b;
    }

    varareArrays=className==='[objectArray]';
    if(!areArrays){
      if(typeofa!='object'||typeofb!='object')returnfalse;

      //Objectswithdifferentconstructorsarenotequivalent,but`Object`sor`Array`s
      //fromdifferentframesare.
      varaCtor=a.constructor,bCtor=b.constructor;
      if(aCtor!==bCtor&&!(_.isFunction(aCtor)&&aCtorinstanceofaCtor&&
                               _.isFunction(bCtor)&&bCtorinstanceofbCtor)
                          &&('constructor'ina&&'constructor'inb)){
        returnfalse;
      }
    }
    //Assumeequalityforcyclicstructures.Thealgorithmfordetectingcyclic
    //structuresisadaptedfromES5.1section15.12.3,abstractoperation`JO`.
    
    //Initializingstackoftraversedobjects.
    //It'sdoneheresinceweonlyneedthemforobjectsandarrayscomparison.
    aStack=aStack||[];
    bStack=bStack||[];
    varlength=aStack.length;
    while(length--){
      //Linearsearch.Performanceisinverselyproportionaltothenumberof
      //uniquenestedstructures.
      if(aStack[length]===a)returnbStack[length]===b;
    }

    //Addthefirstobjecttothestackoftraversedobjects.
    aStack.push(a);
    bStack.push(b);

    //Recursivelycompareobjectsandarrays.
    if(areArrays){
      //Comparearraylengthstodetermineifadeepcomparisonisnecessary.
      length=a.length;
      if(length!==b.length)returnfalse;
      //Deepcomparethecontents,ignoringnon-numericproperties.
      while(length--){
        if(!eq(a[length],b[length],aStack,bStack))returnfalse;
      }
    }else{
      //Deepcompareobjects.
      varkeys=_.keys(a),key;
      length=keys.length;
      //Ensurethatbothobjectscontainthesamenumberofpropertiesbeforecomparingdeepequality.
      if(_.keys(b).length!==length)returnfalse;
      while(length--){
        //Deepcompareeachmember
        key=keys[length];
        if(!(_.has(b,key)&&eq(a[key],b[key],aStack,bStack)))returnfalse;
      }
    }
    //Removethefirstobjectfromthestackoftraversedobjects.
    aStack.pop();
    bStack.pop();
    returntrue;
  };

  //Performadeepcomparisontocheckiftwoobjectsareequal.
  _.isEqual=function(a,b){
    returneq(a,b);
  };

  //Isagivenarray,string,orobjectempty?
  //An"empty"objecthasnoenumerableown-properties.
  _.isEmpty=function(obj){
    if(obj==null)returntrue;
    if(isArrayLike(obj)&&(_.isArray(obj)||_.isString(obj)||_.isArguments(obj)))returnobj.length===0;
    return_.keys(obj).length===0;
  };

  //IsagivenvalueaDOMelement?
  _.isElement=function(obj){
    return!!(obj&&obj.nodeType===1);
  };

  //Isagivenvalueanarray?
  //DelegatestoECMA5'snativeArray.isArray
  _.isArray=nativeIsArray||function(obj){
    returntoString.call(obj)==='[objectArray]';
  };

  //Isagivenvariableanobject?
  _.isObject=function(obj){
    vartype=typeofobj;
    returntype==='function'||type==='object'&&!!obj;
  };

  //AddsomeisTypemethods:isArguments,isFunction,isString,isNumber,isDate,isRegExp,isError.
  _.each(['Arguments','Function','String','Number','Date','RegExp','Error'],function(name){
    _['is'+name]=function(obj){
      returntoString.call(obj)==='[object'+name+']';
    };
  });

  //Defineafallbackversionofthemethodinbrowsers(ahem,IE<9),where
  //thereisn'tanyinspectable"Arguments"type.
  if(!_.isArguments(arguments)){
    _.isArguments=function(obj){
      return_.has(obj,'callee');
    };
  }

  //Optimize`isFunction`ifappropriate.Workaroundsometypeofbugsinoldv8,
  //IE11(#1621),andinSafari8(#1929).
  if(typeof/./!='function'&&typeofInt8Array!='object'){
    _.isFunction=function(obj){
      returntypeofobj=='function'||false;
    };
  }

  //Isagivenobjectafinitenumber?
  _.isFinite=function(obj){
    returnisFinite(obj)&&!isNaN(parseFloat(obj));
  };

  //Isthegivenvalue`NaN`?(NaNistheonlynumberwhichdoesnotequalitself).
  _.isNaN=function(obj){
    return_.isNumber(obj)&&obj!==+obj;
  };

  //Isagivenvalueaboolean?
  _.isBoolean=function(obj){
    returnobj===true||obj===false||toString.call(obj)==='[objectBoolean]';
  };

  //Isagivenvalueequaltonull?
  _.isNull=function(obj){
    returnobj===null;
  };

  //Isagivenvariableundefined?
  _.isUndefined=function(obj){
    returnobj===void0;
  };

  //Shortcutfunctionforcheckingifanobjecthasagivenpropertydirectly
  //onitself(inotherwords,notonaprototype).
  _.has=function(obj,key){
    returnobj!=null&&hasOwnProperty.call(obj,key);
  };

  //UtilityFunctions
  //-----------------

  //RunUnderscore.jsin*noConflict*mode,returningthe`_`variabletoits
  //previousowner.ReturnsareferencetotheUnderscoreobject.
  _.noConflict=function(){
    root._=previousUnderscore;
    returnthis;
  };

  //Keeptheidentityfunctionaroundfordefaultiteratees.
  _.identity=function(value){
    returnvalue;
  };

  //Predicate-generatingfunctions.OftenusefuloutsideofUnderscore.
  _.constant=function(value){
    returnfunction(){
      returnvalue;
    };
  };

  _.noop=function(){};

  _.property=function(key){
    returnfunction(obj){
      returnobj==null?void0:obj[key];
    };
  };

  //Generatesafunctionforagivenobjectthatreturnsagivenproperty.
  _.propertyOf=function(obj){
    returnobj==null?function(){}:function(key){
      returnobj[key];
    };
  };

  //Returnsapredicateforcheckingwhetheranobjecthasagivensetof
  //`key:value`pairs.
  _.matcher=_.matches=function(attrs){
    attrs=_.extendOwn({},attrs);
    returnfunction(obj){
      return_.isMatch(obj,attrs);
    };
  };

  //Runafunction**n**times.
  _.times=function(n,iteratee,context){
    varaccum=Array(Math.max(0,n));
    iteratee=optimizeCb(iteratee,context,1);
    for(vari=0;i<n;i++)accum[i]=iteratee(i);
    returnaccum;
  };

  //Returnarandomintegerbetweenminandmax(inclusive).
  _.random=function(min,max){
    if(max==null){
      max=min;
      min=0;
    }
    returnmin+Math.floor(Math.random()*(max-min+1));
  };

  //A(possiblyfaster)waytogetthecurrenttimestampasaninteger.
  _.now=Date.now||function(){
    returnnewDate().getTime();
  };

   //ListofHTMLentitiesforescaping.
  varescapeMap={
    '&':'&amp;',
    '<':'&lt;',
    '>':'&gt;',
    '"':'&quot;',
    "'":'&#x27;',
    '`':'&#x60;'
  };
  varunescapeMap=_.invert(escapeMap);

  //Functionsforescapingandunescapingstringsto/fromHTMLinterpolation.
  varcreateEscaper=function(map){
    varescaper=function(match){
      returnmap[match];
    };
    //Regexesforidentifyingakeythatneedstobeescaped
    varsource='(?:'+_.keys(map).join('|')+')';
    vartestRegexp=RegExp(source);
    varreplaceRegexp=RegExp(source,'g');
    returnfunction(string){
      string=string==null?'':''+string;
      returntestRegexp.test(string)?string.replace(replaceRegexp,escaper):string;
    };
  };
  _.escape=createEscaper(escapeMap);
  _.unescape=createEscaper(unescapeMap);

  //Ifthevalueofthenamed`property`isafunctiontheninvokeitwiththe
  //`object`ascontext;otherwise,returnit.
  _.result=function(object,property,fallback){
    varvalue=object==null?void0:object[property];
    if(value===void0){
      value=fallback;
    }
    return_.isFunction(value)?value.call(object):value;
  };

  //Generateauniqueintegerid(uniquewithintheentireclientsession).
  //UsefulfortemporaryDOMids.
  varidCounter=0;
  _.uniqueId=function(prefix){
    varid=++idCounter+'';
    returnprefix?prefix+id:id;
  };

  //Bydefault,UnderscoreusesERB-styletemplatedelimiters,changethe
  //followingtemplatesettingstousealternativedelimiters.
  _.templateSettings={
    evaluate   :/<%([\s\S]+?)%>/g,
    interpolate:/<%=([\s\S]+?)%>/g,
    escape     :/<%-([\s\S]+?)%>/g
  };

  //Whencustomizing`templateSettings`,ifyoudon'twanttodefinean
  //interpolation,evaluationorescapingregex,weneedonethatis
  //guaranteednottomatch.
  varnoMatch=/(.)^/;

  //Certaincharactersneedtobeescapedsothattheycanbeputintoa
  //stringliteral.
  varescapes={
    "'":     "'",
    '\\':    '\\',
    '\r':    'r',
    '\n':    'n',
    '\u2028':'u2028',
    '\u2029':'u2029'
  };

  varescaper=/\\|'|\r|\n|\u2028|\u2029/g;

  varescapeChar=function(match){
    return'\\'+escapes[match];
  };

  //JavaScriptmicro-templating,similartoJohnResig'simplementation.
  //Underscoretemplatinghandlesarbitrarydelimiters,preserveswhitespace,
  //andcorrectlyescapesquoteswithininterpolatedcode.
  //NB:`oldSettings`onlyexistsforbackwardscompatibility.
  _.template=function(text,settings,oldSettings){
    if(!settings&&oldSettings)settings=oldSettings;
    settings=_.defaults({},settings,_.templateSettings);

    //Combinedelimitersintooneregularexpressionviaalternation.
    varmatcher=RegExp([
      (settings.escape||noMatch).source,
      (settings.interpolate||noMatch).source,
      (settings.evaluate||noMatch).source
    ].join('|')+'|$','g');

    //Compilethetemplatesource,escapingstringliteralsappropriately.
    varindex=0;
    varsource="__p+='";
    text.replace(matcher,function(match,escape,interpolate,evaluate,offset){
      source+=text.slice(index,offset).replace(escaper,escapeChar);
      index=offset+match.length;

      if(escape){
        source+="'+\n((__t=("+escape+"))==null?'':_.escape(__t))+\n'";
      }elseif(interpolate){
        source+="'+\n((__t=("+interpolate+"))==null?'':__t)+\n'";
      }elseif(evaluate){
        source+="';\n"+evaluate+"\n__p+='";
      }

      //AdobeVMsneedthematchreturnedtoproducethecorrectoffest.
      returnmatch;
    });
    source+="';\n";

    //Ifavariableisnotspecified,placedatavaluesinlocalscope.
    if(!settings.variable)source='with(obj||{}){\n'+source+'}\n';

    source="var__t,__p='',__j=Array.prototype.join,"+
      "print=function(){__p+=__j.call(arguments,'');};\n"+
      source+'return__p;\n';

    try{
      varrender=newFunction(settings.variable||'obj','_',source);
    }catch(e){
      e.source=source;
      throwe;
    }

    vartemplate=function(data){
      returnrender.call(this,data,_);
    };

    //Providethecompiledsourceasaconvenienceforprecompilation.
    varargument=settings.variable||'obj';
    template.source='function('+argument+'){\n'+source+'}';

    returntemplate;
  };

  //Adda"chain"function.StartchainingawrappedUnderscoreobject.
  _.chain=function(obj){
    varinstance=_(obj);
    instance._chain=true;
    returninstance;
  };

  //OOP
  //---------------
  //IfUnderscoreiscalledasafunction,itreturnsawrappedobjectthat
  //canbeusedOO-style.Thiswrapperholdsalteredversionsofallthe
  //underscorefunctions.Wrappedobjectsmaybechained.

  //Helperfunctiontocontinuechainingintermediateresults.
  varresult=function(instance,obj){
    returninstance._chain?_(obj).chain():obj;
  };

  //AddyourowncustomfunctionstotheUnderscoreobject.
  _.mixin=function(obj){
    _.each(_.functions(obj),function(name){
      varfunc=_[name]=obj[name];
      _.prototype[name]=function(){
        varargs=[this._wrapped];
        push.apply(args,arguments);
        returnresult(this,func.apply(_,args));
      };
    });
  };

  //AddalloftheUnderscorefunctionstothewrapperobject.
  _.mixin(_);

  //AddallmutatorArrayfunctionstothewrapper.
  _.each(['pop','push','reverse','shift','sort','splice','unshift'],function(name){
    varmethod=ArrayProto[name];
    _.prototype[name]=function(){
      varobj=this._wrapped;
      method.apply(obj,arguments);
      if((name==='shift'||name==='splice')&&obj.length===0)deleteobj[0];
      returnresult(this,obj);
    };
  });

  //AddallaccessorArrayfunctionstothewrapper.
  _.each(['concat','join','slice'],function(name){
    varmethod=ArrayProto[name];
    _.prototype[name]=function(){
      returnresult(this,method.apply(this._wrapped,arguments));
    };
  });

  //Extractstheresultfromawrappedandchainedobject.
  _.prototype.value=function(){
    returnthis._wrapped;
  };

  //Provideunwrappingproxyforsomemethodsusedinengineoperations
  //suchasarithmeticandJSONstringification.
  _.prototype.valueOf=_.prototype.toJSON=_.prototype.value;
  
  _.prototype.toString=function(){
    return''+this._wrapped;
  };

  //AMDregistrationhappensattheendforcompatibilitywithAMDloaders
  //thatmaynotenforcenext-turnsemanticsonmodules.Eventhoughgeneral
  //practiceforAMDregistrationistobeanonymous,underscoreregisters
  //asanamedmodulebecause,likejQuery,itisabaselibrarythatis
  //popularenoughtobebundledinathirdpartylib,butnotbepartof
  //anAMDloadrequest.Thosecasescouldgenerateanerrorwhenan
  //anonymousdefine()iscalledoutsideofaloaderrequest.
  if(typeofdefine==='function'&&define.amd){
    define('underscore',[],function(){
      return_;
    });
  }
}.call(this));