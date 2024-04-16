/*!
 *QUnit2.9.1
 *https://qunitjs.com/
 *
 *CopyrightjQueryFoundationandothercontributors
 *ReleasedundertheMITlicense
 *https://jquery.org/license
 *
 *Date:2019-01-07T16:37Z
 */
(function(global$1){
  'usestrict';

  global$1=global$1&&global$1.hasOwnProperty('default')?global$1['default']:global$1;

  varwindow$1=global$1.window;
  varself$1=global$1.self;
  varconsole=global$1.console;
  varsetTimeout$1=global$1.setTimeout;
  varclearTimeout=global$1.clearTimeout;

  vardocument$1=window$1&&window$1.document;
  varnavigator=window$1&&window$1.navigator;

  varlocalSessionStorage=function(){
  	varx="qunit-test-string";
  	try{
  		global$1.sessionStorage.setItem(x,x);
  		global$1.sessionStorage.removeItem(x);
  		returnglobal$1.sessionStorage;
  	}catch(e){
  		returnundefined;
  	}
  }();

  /**
   *Returnsafunctionthatproxiestothegivenmethodnameontheglobals
   *consoleobject.Theproxywillalsodetectiftheconsoledoesn'texistand
   *willappropriatelyno-op.ThisallowssupportforIE9,whichdoesn'thavea
   *consoleifthedevelopertoolsarenotopen.
   */
  functionconsoleProxy(method){
  	returnfunction(){
  		if(console){
  			console[method].apply(console,arguments);
  		}
  	};
  }

  varLogger={
  	warn:consoleProxy("warn")
  };

  var_typeof=typeofSymbol==="function"&&typeofSymbol.iterator==="symbol"?function(obj){
    returntypeofobj;
  }:function(obj){
    returnobj&&typeofSymbol==="function"&&obj.constructor===Symbol&&obj!==Symbol.prototype?"symbol":typeofobj;
  };











  varclassCallCheck=function(instance,Constructor){
    if(!(instanceinstanceofConstructor)){
      thrownewTypeError("Cannotcallaclassasafunction");
    }
  };

  varcreateClass=function(){
    functiondefineProperties(target,props){
      for(vari=0;i<props.length;i++){
        vardescriptor=props[i];
        descriptor.enumerable=descriptor.enumerable||false;
        descriptor.configurable=true;
        if("value"indescriptor)descriptor.writable=true;
        Object.defineProperty(target,descriptor.key,descriptor);
      }
    }

    returnfunction(Constructor,protoProps,staticProps){
      if(protoProps)defineProperties(Constructor.prototype,protoProps);
      if(staticProps)defineProperties(Constructor,staticProps);
      returnConstructor;
    };
  }();









































  vartoConsumableArray=function(arr){
    if(Array.isArray(arr)){
      for(vari=0,arr2=Array(arr.length);i<arr.length;i++)arr2[i]=arr[i];

      returnarr2;
    }else{
      returnArray.from(arr);
    }
  };

  vartoString=Object.prototype.toString;
  varhasOwn=Object.prototype.hasOwnProperty;
  varnow=Date.now||function(){
  	returnnewDate().getTime();
  };

  varhasPerformanceApi=detectPerformanceApi();
  varperformance=hasPerformanceApi?window$1.performance:undefined;
  varperformanceNow=hasPerformanceApi?performance.now.bind(performance):now;

  functiondetectPerformanceApi(){
  	returnwindow$1&&typeofwindow$1.performance!=="undefined"&&typeofwindow$1.performance.mark==="function"&&typeofwindow$1.performance.measure==="function";
  }

  functionmeasure(comment,startMark,endMark){

  	//`performance.measure`mayfailifthemarkcouldnotbefound.
  	//reasonsaspecificmarkcouldnotbefoundinclude:outsidecodeinvoking`performance.clearMarks()`
  	try{
  		performance.measure(comment,startMark,endMark);
  	}catch(ex){
  		Logger.warn("performance.measurecouldnotbeexecutedbecauseof",ex.message);
  	}
  }

  vardefined={
  	document:window$1&&window$1.document!==undefined,
  	setTimeout:setTimeout$1!==undefined
  };

  //ReturnsanewArraywiththeelementsthatareinabutnotinb
  functiondiff(a,b){
  	vari,
  	   j,
  	   result=a.slice();

  	for(i=0;i<result.length;i++){
  		for(j=0;j<b.length;j++){
  			if(result[i]===b[j]){
  				result.splice(i,1);
  				i--;
  				break;
  			}
  		}
  	}
  	returnresult;
  }

  /**
   *Determineswhetheranelementexistsinagivenarrayornot.
   *
   *@methodinArray
   *@param{Any}elem
   *@param{Array}array
   *@return{Boolean}
   */
  functioninArray(elem,array){
  	returnarray.indexOf(elem)!==-1;
  }

  /**
   *MakesacloneofanobjectusingonlyArrayorObjectasbase,
   *andcopiesovertheownenumerableproperties.
   *
   *@param{Object}obj
   *@return{Object}Newobjectwithonlytheownproperties(recursively).
   */
  functionobjectValues(obj){
  	varkey,
  	   val,
  	   vals=is("array",obj)?[]:{};
  	for(keyinobj){
  		if(hasOwn.call(obj,key)){
  			val=obj[key];
  			vals[key]=val===Object(val)?objectValues(val):val;
  		}
  	}
  	returnvals;
  }

  functionextend(a,b,undefOnly){
  	for(varpropinb){
  		if(hasOwn.call(b,prop)){
  			if(b[prop]===undefined){
  				deletea[prop];
  			}elseif(!(undefOnly&&typeofa[prop]!=="undefined")){
  				a[prop]=b[prop];
  			}
  		}
  	}

  	returna;
  }

  functionobjectType(obj){
  	if(typeofobj==="undefined"){
  		return"undefined";
  	}

  	//Consider:typeofnull===object
  	if(obj===null){
  		return"null";
  	}

  	varmatch=toString.call(obj).match(/^\[object\s(.*)\]$/),
  	   type=match&&match[1];

  	switch(type){
  		case"Number":
  			if(isNaN(obj)){
  				return"nan";
  			}
  			return"number";
  		case"String":
  		case"Boolean":
  		case"Array":
  		case"Set":
  		case"Map":
  		case"Date":
  		case"RegExp":
  		case"Function":
  		case"Symbol":
  			returntype.toLowerCase();
  		default:
  			returntypeofobj==="undefined"?"undefined":_typeof(obj);
  	}
  }

  //Safeobjecttypechecking
  functionis(type,obj){
  	returnobjectType(obj)===type;
  }

  //BasedonJava'sString.hashCode,asimplebutnot
  //rigorouslycollisionresistanthashingfunction
  functiongenerateHash(module,testName){
  	varstr=module+"\x1C"+testName;
  	varhash=0;

  	for(vari=0;i<str.length;i++){
  		hash=(hash<<5)-hash+str.charCodeAt(i);
  		hash|=0;
  	}

  	//Convertthepossiblynegativeintegerhashcodeintoan8characterhexstring,whichisn't
  	//strictlynecessarybutincreasesuserunderstandingthattheidisaSHA-likehash
  	varhex=(0x100000000+hash).toString(16);
  	if(hex.length<8){
  		hex="0000000"+hex;
  	}

  	returnhex.slice(-8);
  }

  //TestforequalityanyJavaScripttype.
  //Authors:PhilippeRathé<prathe@gmail.com>,DavidChan<david@troi.org>
  varequiv=(function(){

  	//Valuepairsqueuedforcomparison.Usedforbreadth-firstprocessingorder,recursion
  	//detectionandavoidingrepeatedcomparison(seebelowfordetails).
  	//Elementsare{a:val,b:val}.
  	varpairs=[];

  	vargetProto=Object.getPrototypeOf||function(obj){
  		returnobj.__proto__;
  	};

  	functionuseStrictEquality(a,b){

  		//Thisonlygetscalledifaandbarenotstrictequal,andisusedtocompareon
  		//theprimitivevaluesinsideobjectwrappers.Forexample:
  		//`vari=1;`
  		//`varj=newNumber(1);`
  		//Neitheranorbcanbenull,asa!==bandtheyhavethesametype.
  		if((typeofa==="undefined"?"undefined":_typeof(a))==="object"){
  			a=a.valueOf();
  		}
  		if((typeofb==="undefined"?"undefined":_typeof(b))==="object"){
  			b=b.valueOf();
  		}

  		returna===b;
  	}

  	functioncompareConstructors(a,b){
  		varprotoA=getProto(a);
  		varprotoB=getProto(b);

  		//Comparingconstructorsismorestrictthanusing`instanceof`
  		if(a.constructor===b.constructor){
  			returntrue;
  		}

  		//Ref#851
  		//Iftheobjprototypedescendsfromanullconstructor,treatit
  		//asanullprototype.
  		if(protoA&&protoA.constructor===null){
  			protoA=null;
  		}
  		if(protoB&&protoB.constructor===null){
  			protoB=null;
  		}

  		//Allowobjectswithnoprototypetobeequivalentto
  		//objectswithObjectastheirconstructor.
  		if(protoA===null&&protoB===Object.prototype||protoB===null&&protoA===Object.prototype){
  			returntrue;
  		}

  		returnfalse;
  	}

  	functiongetRegExpFlags(regexp){
  		return"flags"inregexp?regexp.flags:regexp.toString().match(/[gimuy]*$/)[0];
  	}

  	functionisContainer(val){
  		return["object","array","map","set"].indexOf(objectType(val))!==-1;
  	}

  	functionbreadthFirstCompareChild(a,b){

  		//Ifaisacontainernotreference-equaltob,postponethecomparisontothe
  		//endofthepairsqueue--unless(a,b)hasbeenseenbefore,inwhichcaseskip
  		//overthepair.
  		if(a===b){
  			returntrue;
  		}
  		if(!isContainer(a)){
  			returntypeEquiv(a,b);
  		}
  		if(pairs.every(function(pair){
  			returnpair.a!==a||pair.b!==b;
  		})){

  			//Notyetstartedcomparingthispair
  			pairs.push({a:a,b:b});
  		}
  		returntrue;
  	}

  	varcallbacks={
  		"string":useStrictEquality,
  		"boolean":useStrictEquality,
  		"number":useStrictEquality,
  		"null":useStrictEquality,
  		"undefined":useStrictEquality,
  		"symbol":useStrictEquality,
  		"date":useStrictEquality,

  		"nan":functionnan(){
  			returntrue;
  		},

  		"regexp":functionregexp(a,b){
  			returna.source===b.source&&

  			//Includeflagsinthecomparison
  			getRegExpFlags(a)===getRegExpFlags(b);
  		},

  		//abort(identicalreferences/instancemethodswereskippedearlier)
  		"function":function_function(){
  			returnfalse;
  		},

  		"array":functionarray(a,b){
  			vari,len;

  			len=a.length;
  			if(len!==b.length){

  				//Safeandfaster
  				returnfalse;
  			}

  			for(i=0;i<len;i++){

  				//Comparenon-containers;queuenon-reference-equalcontainers
  				if(!breadthFirstCompareChild(a[i],b[i])){
  					returnfalse;
  				}
  			}
  			returntrue;
  		},

  		//DefinesetsaandbtobeequivalentifforeachelementaValina,there
  		//issomeelementbValinbsuchthataValandbValareequivalent.Element
  		//repetitionsarenotcounted,sotheseareequivalent:
  		//a=newSet([{},[],[]]);
  		//b=newSet([{},{},[]]);
  		"set":functionset$$1(a,b){
  			varinnerEq,
  			   outerEq=true;

  			if(a.size!==b.size){

  				//Thisoptimizationhascertainquirksbecauseofthelackof
  				//repetitioncounting.Forinstance,addingthesame
  				//(reference-identical)elementtotwoequivalentsetscan
  				//makethemnon-equivalent.
  				returnfalse;
  			}

  			a.forEach(function(aVal){

  				//Short-circuitiftheresultisalreadyknown.(Usingfor...of
  				//withabreakclausewouldbecleanerhere,butitwouldcause
  				//asyntaxerroronolderJavascriptimplementationsevenif
  				//Setisunused)
  				if(!outerEq){
  					return;
  				}

  				innerEq=false;

  				b.forEach(function(bVal){
  					varparentPairs;

  					//Likewise,short-circuitiftheresultisalreadyknown
  					if(innerEq){
  						return;
  					}

  					//Swapouttheglobalpairslist,asthenestedcallto
  					//innerEquivwillclobberitscontents
  					parentPairs=pairs;
  					if(innerEquiv(bVal,aVal)){
  						innerEq=true;
  					}

  					//Replacetheglobalpairslist
  					pairs=parentPairs;
  				});

  				if(!innerEq){
  					outerEq=false;
  				}
  			});

  			returnouterEq;
  		},

  		//Definemapsaandbtobeequivalentifforeachkey-valuepair(aKey,aVal)
  		//ina,thereissomekey-valuepair(bKey,bVal)inbsuchthat
  		//[aKey,aVal]and[bKey,bVal]areequivalent.Keyrepetitionsarenot
  		//counted,sotheseareequivalent:
  		//a=newMap([[{},1],[{},1],[[],1]]);
  		//b=newMap([[{},1],[[],1],[[],1]]);
  		"map":functionmap(a,b){
  			varinnerEq,
  			   outerEq=true;

  			if(a.size!==b.size){

  				//Thisoptimizationhascertainquirksbecauseofthelackof
  				//repetitioncounting.Forinstance,addingthesame
  				//(reference-identical)key-valuepairtotwoequivalentmaps
  				//canmakethemnon-equivalent.
  				returnfalse;
  			}

  			a.forEach(function(aVal,aKey){

  				//Short-circuitiftheresultisalreadyknown.(Usingfor...of
  				//withabreakclausewouldbecleanerhere,butitwouldcause
  				//asyntaxerroronolderJavascriptimplementationsevenif
  				//Mapisunused)
  				if(!outerEq){
  					return;
  				}

  				innerEq=false;

  				b.forEach(function(bVal,bKey){
  					varparentPairs;

  					//Likewise,short-circuitiftheresultisalreadyknown
  					if(innerEq){
  						return;
  					}

  					//Swapouttheglobalpairslist,asthenestedcallto
  					//innerEquivwillclobberitscontents
  					parentPairs=pairs;
  					if(innerEquiv([bVal,bKey],[aVal,aKey])){
  						innerEq=true;
  					}

  					//Replacetheglobalpairslist
  					pairs=parentPairs;
  				});

  				if(!innerEq){
  					outerEq=false;
  				}
  			});

  			returnouterEq;
  		},

  		"object":functionobject(a,b){
  			vari,
  			   aProperties=[],
  			   bProperties=[];

  			if(compareConstructors(a,b)===false){
  				returnfalse;
  			}

  			//Bestrict:don'tensurehasOwnPropertyandgodeep
  			for(iina){

  				//Collecta'sproperties
  				aProperties.push(i);

  				//SkipOOPmethodsthatlookthesame
  				if(a.constructor!==Object&&typeofa.constructor!=="undefined"&&typeofa[i]==="function"&&typeofb[i]==="function"&&a[i].toString()===b[i].toString()){
  					continue;
  				}

  				//Comparenon-containers;queuenon-reference-equalcontainers
  				if(!breadthFirstCompareChild(a[i],b[i])){
  					returnfalse;
  				}
  			}

  			for(iinb){

  				//Collectb'sproperties
  				bProperties.push(i);
  			}

  			//Ensuresidenticalpropertiesname
  			returntypeEquiv(aProperties.sort(),bProperties.sort());
  		}
  	};

  	functiontypeEquiv(a,b){
  		vartype=objectType(a);

  		//Callbacksforcontainerswillappendtothepairsqueuetoachievebreadth-first
  		//searchorder.Thepairsqueueisalsousedtoavoidreprocessinganypairof
  		//containersthatarereference-equaltoapreviouslyvisitedpair(aspecialcase
  		//thisbeingrecursiondetection).
  		//
  		//Becauseofthisapproach,oncetypeEquivreturnsafalsevalue,itshouldnotbe
  		//calledagainwithoutclearingthepairqueueelseitmaywronglyreportavisited
  		//pairasbeingequivalent.
  		returnobjectType(b)===type&&callbacks[type](a,b);
  	}

  	functioninnerEquiv(a,b){
  		vari,pair;

  		//We'redonewhenthere'snothingmoretocompare
  		if(arguments.length<2){
  			returntrue;
  		}

  		//Cleartheglobalpairqueueandaddthetop-levelvaluesbeingcompared
  		pairs=[{a:a,b:b}];

  		for(i=0;i<pairs.length;i++){
  			pair=pairs[i];

  			//Performtype-specificcomparisononanypairsthatarenotstrictly
  			//equal.Forcontainertypes,thatcomparisonwillpostponecomparison
  			//ofanysub-containerpairtotheendofthepairqueue.Thisgives
  			//breadth-firstsearchorder.Italsoavoidsthereprocessingof
  			//reference-equalsiblings,cousinsetc,whichcanhaveasignificantspeed
  			//impactwhencomparingacontainerofsmallobjectseachofwhichhasa
  			//referencetothesame(singleton)largeobject.
  			if(pair.a!==pair.b&&!typeEquiv(pair.a,pair.b)){
  				returnfalse;
  			}
  		}

  		//...acrossallconsecutiveargumentpairs
  		returnarguments.length===2||innerEquiv.apply(this,[].slice.call(arguments,1));
  	}

  	returnfunction(){
  		varresult=innerEquiv.apply(undefined,arguments);

  		//Releaseanyretainedobjects
  		pairs.length=0;
  		returnresult;
  	};
  })();

  /**
   *Configobject:Maintaininternalstate
   *LaterexposedasQUnit.config
   *`config`initializedattopofscope
   */
  varconfig={

  	//Thequeueofteststorun
  	queue:[],

  	//Blockuntildocumentready
  	blocking:true,

  	//Bydefault,runpreviouslyfailedtestsfirst
  	//veryusefulincombinationwith"Hidepassedtests"checked
  	reorder:true,

  	//Bydefault,modifydocument.titlewhensuiteisdone
  	altertitle:true,

  	//HTMLReporter:collapseeverytestexceptthefirstfailingtest
  	//Iffalse,allfailingtestswillbeexpanded
  	collapse:true,

  	//Bydefault,scrolltotopofthepagewhensuiteisdone
  	scrolltop:true,

  	//Depthup-towhichobjectwillbedumped
  	maxDepth:5,

  	//Whenenabled,alltestsmustcallexpect()
  	requireExpects:false,

  	//Placeholderforuser-configurableform-exposedURLparameters
  	urlConfig:[],

  	//Setofallmodules.
  	modules:[],

  	//Thefirstunnamedmodule
  	currentModule:{
  		name:"",
  		tests:[],
  		childModules:[],
  		testsRun:0,
  		unskippedTestsRun:0,
  		hooks:{
  			before:[],
  			beforeEach:[],
  			afterEach:[],
  			after:[]
  		}
  	},

  	callbacks:{},

  	//Thestoragemoduletouseforreorderingtests
  	storage:localSessionStorage
  };

  //takeapredefinedQUnit.configandextendthedefaults
  varglobalConfig=window$1&&window$1.QUnit&&window$1.QUnit.config;

  //onlyextendtheglobalconfigifthereisnoQUnitoverload
  if(window$1&&window$1.QUnit&&!window$1.QUnit.version){
  	extend(config,globalConfig);
  }

  //Pushalooseunnamedmoduletothemodulescollection
  config.modules.push(config.currentModule);

  //BasedonjsDumpbyArielFlesler
  //http://flesler.blogspot.com/2008/05/jsdump-pretty-dump-of-any-javascript.html
  vardump=(function(){
  	functionquote(str){
  		return"\""+str.toString().replace(/\\/g,"\\\\").replace(/"/g,"\\\"")+"\"";
  	}
  	functionliteral(o){
  		returno+"";
  	}
  	functionjoin(pre,arr,post){
  		vars=dump.separator(),
  		   base=dump.indent(),
  		   inner=dump.indent(1);
  		if(arr.join){
  			arr=arr.join(","+s+inner);
  		}
  		if(!arr){
  			returnpre+post;
  		}
  		return[pre,inner+arr,base+post].join(s);
  	}
  	functionarray(arr,stack){
  		vari=arr.length,
  		   ret=newArray(i);

  		if(dump.maxDepth&&dump.depth>dump.maxDepth){
  			return"[objectArray]";
  		}

  		this.up();
  		while(i--){
  			ret[i]=this.parse(arr[i],undefined,stack);
  		}
  		this.down();
  		returnjoin("[",ret,"]");
  	}

  	functionisArray(obj){
  		return(

  			//NativeArrays
  			toString.call(obj)==="[objectArray]"||

  			//NodeListobjects
  			typeofobj.length==="number"&&obj.item!==undefined&&(obj.length?obj.item(0)===obj[0]:obj.item(0)===null&&obj[0]===undefined)
  		);
  	}

  	varreName=/^function(\w+)/,
  	   dump={

  		//TheobjTypeisusedmostlyinternally,youcanfixa(custom)typeinadvance
  		parse:functionparse(obj,objType,stack){
  			stack=stack||[];
  			varres,
  			   parser,
  			   parserType,
  			   objIndex=stack.indexOf(obj);

  			if(objIndex!==-1){
  				return"recursion("+(objIndex-stack.length)+")";
  			}

  			objType=objType||this.typeOf(obj);
  			parser=this.parsers[objType];
  			parserType=typeofparser==="undefined"?"undefined":_typeof(parser);

  			if(parserType==="function"){
  				stack.push(obj);
  				res=parser.call(this,obj,stack);
  				stack.pop();
  				returnres;
  			}
  			returnparserType==="string"?parser:this.parsers.error;
  		},
  		typeOf:functiontypeOf(obj){
  			vartype;

  			if(obj===null){
  				type="null";
  			}elseif(typeofobj==="undefined"){
  				type="undefined";
  			}elseif(is("regexp",obj)){
  				type="regexp";
  			}elseif(is("date",obj)){
  				type="date";
  			}elseif(is("function",obj)){
  				type="function";
  			}elseif(obj.setInterval!==undefined&&obj.document!==undefined&&obj.nodeType===undefined){
  				type="window";
  			}elseif(obj.nodeType===9){
  				type="document";
  			}elseif(obj.nodeType){
  				type="node";
  			}elseif(isArray(obj)){
  				type="array";
  			}elseif(obj.constructor===Error.prototype.constructor){
  				type="error";
  			}else{
  				type=typeofobj==="undefined"?"undefined":_typeof(obj);
  			}
  			returntype;
  		},

  		separator:functionseparator(){
  			if(this.multiline){
  				returnthis.HTML?"<br/>":"\n";
  			}else{
  				returnthis.HTML?"&#160;":"";
  			}
  		},

  		//Extracanbeanumber,shortcutforincreasing-calling-decreasing
  		indent:functionindent(extra){
  			if(!this.multiline){
  				return"";
  			}
  			varchr=this.indentChar;
  			if(this.HTML){
  				chr=chr.replace(/\t/g,"  ").replace(//g,"&#160;");
  			}
  			returnnewArray(this.depth+(extra||0)).join(chr);
  		},
  		up:functionup(a){
  			this.depth+=a||1;
  		},
  		down:functiondown(a){
  			this.depth-=a||1;
  		},
  		setParser:functionsetParser(name,parser){
  			this.parsers[name]=parser;
  		},

  		//Thenext3areexposedsoyoucanusethem
  		quote:quote,
  		literal:literal,
  		join:join,
  		depth:1,
  		maxDepth:config.maxDepth,

  		//Thisisthelistofparsers,tomodifythem,usedump.setParser
  		parsers:{
  			window:"[Window]",
  			document:"[Document]",
  			error:functionerror(_error){
  				return"Error(\""+_error.message+"\")";
  			},
  			unknown:"[Unknown]",
  			"null":"null",
  			"undefined":"undefined",
  			"function":function_function(fn){
  				varret="function",


  				//FunctionsneverhavenameinIE
  				name="name"infn?fn.name:(reName.exec(fn)||[])[1];

  				if(name){
  					ret+=""+name;
  				}
  				ret+="(";

  				ret=[ret,dump.parse(fn,"functionArgs"),"){"].join("");
  				returnjoin(ret,dump.parse(fn,"functionCode"),"}");
  			},
  			array:array,
  			nodelist:array,
  			"arguments":array,
  			object:functionobject(map,stack){
  				varkeys,
  				   key,
  				   val,
  				   i,
  				   nonEnumerableProperties,
  				   ret=[];

  				if(dump.maxDepth&&dump.depth>dump.maxDepth){
  					return"[objectObject]";
  				}

  				dump.up();
  				keys=[];
  				for(keyinmap){
  					keys.push(key);
  				}

  				//SomepropertiesarenotalwaysenumerableonErrorobjects.
  				nonEnumerableProperties=["message","name"];
  				for(iinnonEnumerableProperties){
  					key=nonEnumerableProperties[i];
  					if(keyinmap&&!inArray(key,keys)){
  						keys.push(key);
  					}
  				}
  				keys.sort();
  				for(i=0;i<keys.length;i++){
  					key=keys[i];
  					val=map[key];
  					ret.push(dump.parse(key,"key")+":"+dump.parse(val,undefined,stack));
  				}
  				dump.down();
  				returnjoin("{",ret,"}");
  			},
  			node:functionnode(_node){
  				varlen,
  				   i,
  				   val,
  				   open=dump.HTML?"&lt;":"<",
  				   close=dump.HTML?"&gt;":">",
  				   tag=_node.nodeName.toLowerCase(),
  				   ret=open+tag,
  				   attrs=_node.attributes;

  				if(attrs){
  					for(i=0,len=attrs.length;i<len;i++){
  						val=attrs[i].nodeValue;

  						//IE6includesallattributesin.attributes,evenonesnotexplicitly
  						//set.Thosehavevalueslikeundefined,null,0,false,""or
  						//"inherit".
  						if(val&&val!=="inherit"){
  							ret+=""+attrs[i].nodeName+"="+dump.parse(val,"attribute");
  						}
  					}
  				}
  				ret+=close;

  				//ShowcontentofTextNodeorCDATASection
  				if(_node.nodeType===3||_node.nodeType===4){
  					ret+=_node.nodeValue;
  				}

  				returnret+open+"/"+tag+close;
  			},

  			//Functioncallsitinternally,it'stheargumentspartofthefunction
  			functionArgs:functionfunctionArgs(fn){
  				varargs,
  				   l=fn.length;

  				if(!l){
  					return"";
  				}

  				args=newArray(l);
  				while(l--){

  					//97is'a'
  					args[l]=String.fromCharCode(97+l);
  				}
  				return""+args.join(",")+"";
  			},

  			//Objectcallsitinternally,thekeypartofaniteminamap
  			key:quote,

  			//Functioncallsitinternally,it'sthecontentofthefunction
  			functionCode:"[code]",

  			//Nodecallsitinternally,it'sahtmlattributevalue
  			attribute:quote,
  			string:quote,
  			date:quote,
  			regexp:literal,
  			number:literal,
  			"boolean":literal,
  			symbol:functionsymbol(sym){
  				returnsym.toString();
  			}
  		},

  		//Iftrue,entitiesareescaped(<,>,\t,spaceand\n)
  		HTML:false,

  		//Indentationunit
  		indentChar:" ",

  		//Iftrue,itemsinacollection,areseparatedbya\n,elsejustaspace.
  		multiline:true
  	};

  	returndump;
  })();

  varSuiteReport=function(){
  	functionSuiteReport(name,parentSuite){
  		classCallCheck(this,SuiteReport);

  		this.name=name;
  		this.fullName=parentSuite?parentSuite.fullName.concat(name):[];

  		this.tests=[];
  		this.childSuites=[];

  		if(parentSuite){
  			parentSuite.pushChildSuite(this);
  		}
  	}

  	createClass(SuiteReport,[{
  		key:"start",
  		value:functionstart(recordTime){
  			if(recordTime){
  				this._startTime=performanceNow();

  				if(performance){
  					varsuiteLevel=this.fullName.length;
  					performance.mark("qunit_suite_"+suiteLevel+"_start");
  				}
  			}

  			return{
  				name:this.name,
  				fullName:this.fullName.slice(),
  				tests:this.tests.map(function(test){
  					returntest.start();
  				}),
  				childSuites:this.childSuites.map(function(suite){
  					returnsuite.start();
  				}),
  				testCounts:{
  					total:this.getTestCounts().total
  				}
  			};
  		}
  	},{
  		key:"end",
  		value:functionend(recordTime){
  			if(recordTime){
  				this._endTime=performanceNow();

  				if(performance){
  					varsuiteLevel=this.fullName.length;
  					performance.mark("qunit_suite_"+suiteLevel+"_end");

  					varsuiteName=this.fullName.join("–");

  					measure(suiteLevel===0?"QUnitTestRun":"QUnitTestSuite:"+suiteName,"qunit_suite_"+suiteLevel+"_start","qunit_suite_"+suiteLevel+"_end");
  				}
  			}

  			return{
  				name:this.name,
  				fullName:this.fullName.slice(),
  				tests:this.tests.map(function(test){
  					returntest.end();
  				}),
  				childSuites:this.childSuites.map(function(suite){
  					returnsuite.end();
  				}),
  				testCounts:this.getTestCounts(),
  				runtime:this.getRuntime(),
  				status:this.getStatus()
  			};
  		}
  	},{
  		key:"pushChildSuite",
  		value:functionpushChildSuite(suite){
  			this.childSuites.push(suite);
  		}
  	},{
  		key:"pushTest",
  		value:functionpushTest(test){
  			this.tests.push(test);
  		}
  	},{
  		key:"getRuntime",
  		value:functiongetRuntime(){
  			returnthis._endTime-this._startTime;
  		}
  	},{
  		key:"getTestCounts",
  		value:functiongetTestCounts(){
  			varcounts=arguments.length>0&&arguments[0]!==undefined?arguments[0]:{passed:0,failed:0,skipped:0,todo:0,total:0};

  			counts=this.tests.reduce(function(counts,test){
  				if(test.valid){
  					counts[test.getStatus()]++;
  					counts.total++;
  				}

  				returncounts;
  			},counts);

  			returnthis.childSuites.reduce(function(counts,suite){
  				returnsuite.getTestCounts(counts);
  			},counts);
  		}
  	},{
  		key:"getStatus",
  		value:functiongetStatus(){
  			var_getTestCounts=this.getTestCounts(),
  			   total=_getTestCounts.total,
  			   failed=_getTestCounts.failed,
  			   skipped=_getTestCounts.skipped,
  			   todo=_getTestCounts.todo;

  			if(failed){
  				return"failed";
  			}else{
  				if(skipped===total){
  					return"skipped";
  				}elseif(todo===total){
  					return"todo";
  				}else{
  					return"passed";
  				}
  			}
  		}
  	}]);
  	returnSuiteReport;
  }();

  varfocused=false;

  varmoduleStack=[];

  functioncreateModule(name,testEnvironment,modifiers){
  	varparentModule=moduleStack.length?moduleStack.slice(-1)[0]:null;
  	varmoduleName=parentModule!==null?[parentModule.name,name].join(">"):name;
  	varparentSuite=parentModule?parentModule.suiteReport:globalSuite;

  	varskip=parentModule!==null&&parentModule.skip||modifiers.skip;
  	vartodo=parentModule!==null&&parentModule.todo||modifiers.todo;

  	varmodule={
  		name:moduleName,
  		parentModule:parentModule,
  		tests:[],
  		moduleId:generateHash(moduleName),
  		testsRun:0,
  		unskippedTestsRun:0,
  		childModules:[],
  		suiteReport:newSuiteReport(name,parentSuite),

  		//Passalong`skip`and`todo`propertiesfromparentmodule,incase
  		//thereisone,tochilds.Anduseownotherwise.
  		//Thispropertywillbeusedtomarkowntestsandtestsofchildsuites
  		//aseither`skipped`or`todo`.
  		skip:skip,
  		todo:skip?false:todo
  	};

  	varenv={};
  	if(parentModule){
  		parentModule.childModules.push(module);
  		extend(env,parentModule.testEnvironment);
  	}
  	extend(env,testEnvironment);
  	module.testEnvironment=env;

  	config.modules.push(module);
  	returnmodule;
  }

  functionprocessModule(name,options,executeNow){
  	varmodifiers=arguments.length>3&&arguments[3]!==undefined?arguments[3]:{};

  	if(objectType(options)==="function"){
  		executeNow=options;
  		options=undefined;
  	}

  	varmodule=createModule(name,options,modifiers);

  	//Moveanyhookstoa'hooks'object
  	vartestEnvironment=module.testEnvironment;
  	varhooks=module.hooks={};

  	setHookFromEnvironment(hooks,testEnvironment,"before");
  	setHookFromEnvironment(hooks,testEnvironment,"beforeEach");
  	setHookFromEnvironment(hooks,testEnvironment,"afterEach");
  	setHookFromEnvironment(hooks,testEnvironment,"after");

  	varmoduleFns={
  		before:setHookFunction(module,"before"),
  		beforeEach:setHookFunction(module,"beforeEach"),
  		afterEach:setHookFunction(module,"afterEach"),
  		after:setHookFunction(module,"after")
  	};

  	varcurrentModule=config.currentModule;
  	if(objectType(executeNow)==="function"){
  		moduleStack.push(module);
  		config.currentModule=module;
  		executeNow.call(module.testEnvironment,moduleFns);
  		moduleStack.pop();
  		module=module.parentModule||currentModule;
  	}

  	config.currentModule=module;

  	functionsetHookFromEnvironment(hooks,environment,name){
  		varpotentialHook=environment[name];
  		hooks[name]=typeofpotentialHook==="function"?[potentialHook]:[];
  		deleteenvironment[name];
  	}

  	functionsetHookFunction(module,hookName){
  		returnfunctionsetHook(callback){
  			module.hooks[hookName].push(callback);
  		};
  	}
  }

  functionmodule$1(name,options,executeNow){
  	if(focused){
  		return;
  	}

  	processModule(name,options,executeNow);
  }

  module$1.only=function(){
  	if(focused){
  		return;
  	}

  	config.modules.length=0;
  	config.queue.length=0;

  	module$1.apply(undefined,arguments);

  	focused=true;
  };

  module$1.skip=function(name,options,executeNow){
  	if(focused){
  		return;
  	}

  	processModule(name,options,executeNow,{skip:true});
  };

  module$1.todo=function(name,options,executeNow){
  	if(focused){
  		return;
  	}

  	processModule(name,options,executeNow,{todo:true});
  };

  varLISTENERS=Object.create(null);
  varSUPPORTED_EVENTS=["runStart","suiteStart","testStart","assertion","testEnd","suiteEnd","runEnd"];
  SUPPORTED_EVENTS.push("FlectraBeforeTestHook","FlectraAfterTestHook");//Flectracustomization

  /**
   *Emitsaneventwiththespecifieddatatoallcurrentlyregisteredlisteners.
   *Callbackswillfireintheorderinwhichtheyareregistered(FIFO).This
   *functionisnotexposedpublicly;itisusedbyQUnitinternalstoemit
   *loggingevents.
   *
   *@private
   *@methodemit
   *@param{String}eventName
   *@param{Object}data
   *@return{Void}
   */
  functionemit(eventName,data){
  	if(objectType(eventName)!=="string"){
  		thrownewTypeError("eventNamemustbeastringwhenemittinganevent");
  	}

  	//Clonethecallbacksincaseoneofthemregistersanewcallback
  	varoriginalCallbacks=LISTENERS[eventName];
  	varcallbacks=originalCallbacks?[].concat(toConsumableArray(originalCallbacks)):[];

  	for(vari=0;i<callbacks.length;i++){
  		callbacks[i](data);
  	}
  }

  /**
   *Registersacallbackasalistenertothespecifiedevent.
   *
   *@public
   *@methodon
   *@param{String}eventName
   *@param{Function}callback
   *@return{Void}
   */
  functionon(eventName,callback){
  	if(objectType(eventName)!=="string"){
  		thrownewTypeError("eventNamemustbeastringwhenregisteringalistener");
  	}elseif(!inArray(eventName,SUPPORTED_EVENTS)){
  		varevents=SUPPORTED_EVENTS.join(",");
  		thrownewError("\""+eventName+"\"isnotavalidevent;mustbeoneof:"+events+".");
  	}elseif(objectType(callback)!=="function"){
  		thrownewTypeError("callbackmustbeafunctionwhenregisteringalistener");
  	}

  	if(!LISTENERS[eventName]){
  		LISTENERS[eventName]=[];
  	}

  	//Don'tregisterthesamecallbackmorethanonce
  	if(!inArray(callback,LISTENERS[eventName])){
  		LISTENERS[eventName].push(callback);
  	}
  }

  functionobjectOrFunction(x){
    vartype=typeofx==='undefined'?'undefined':_typeof(x);
    returnx!==null&&(type==='object'||type==='function');
  }

  functionisFunction(x){
    returntypeofx==='function';
  }



  var_isArray=void0;
  if(Array.isArray){
    _isArray=Array.isArray;
  }else{
    _isArray=function_isArray(x){
      returnObject.prototype.toString.call(x)==='[objectArray]';
    };
  }

  varisArray=_isArray;

  varlen=0;
  varvertxNext=void0;
  varcustomSchedulerFn=void0;

  varasap=functionasap(callback,arg){
    queue[len]=callback;
    queue[len+1]=arg;
    len+=2;
    if(len===2){
      //Iflenis2,thatmeansthatweneedtoscheduleanasyncflush.
      //Ifadditionalcallbacksarequeuedbeforethequeueisflushed,they
      //willbeprocessedbythisflushthatwearescheduling.
      if(customSchedulerFn){
        customSchedulerFn(flush);
      }else{
        scheduleFlush();
      }
    }
  };

  functionsetScheduler(scheduleFn){
    customSchedulerFn=scheduleFn;
  }

  functionsetAsap(asapFn){
    asap=asapFn;
  }

  varbrowserWindow=typeofwindow!=='undefined'?window:undefined;
  varbrowserGlobal=browserWindow||{};
  varBrowserMutationObserver=browserGlobal.MutationObserver||browserGlobal.WebKitMutationObserver;
  varisNode=typeofself==='undefined'&&typeofprocess!=='undefined'&&{}.toString.call(process)==='[objectprocess]';

  //testforwebworkerbutnotinIE10
  varisWorker=typeofUint8ClampedArray!=='undefined'&&typeofimportScripts!=='undefined'&&typeofMessageChannel!=='undefined';

  //node
  functionuseNextTick(){
    //nodeversion0.10.xdisplaysadeprecationwarningwhennextTickisusedrecursively
    //seehttps://github.com/cujojs/when/issues/410fordetails
    returnfunction(){
      returnprocess.nextTick(flush);
    };
  }

  //vertx
  functionuseVertxTimer(){
    if(typeofvertxNext!=='undefined'){
      returnfunction(){
        vertxNext(flush);
      };
    }

    returnuseSetTimeout();
  }

  functionuseMutationObserver(){
    variterations=0;
    varobserver=newBrowserMutationObserver(flush);
    varnode=document.createTextNode('');
    observer.observe(node,{characterData:true});

    returnfunction(){
      node.data=iterations=++iterations%2;
    };
  }

  //webworker
  functionuseMessageChannel(){
    varchannel=newMessageChannel();
    channel.port1.onmessage=flush;
    returnfunction(){
      returnchannel.port2.postMessage(0);
    };
  }

  functionuseSetTimeout(){
    //StoresetTimeoutreferencesoes6-promisewillbeunaffectedby
    //othercodemodifyingsetTimeout(likesinon.useFakeTimers())
    varglobalSetTimeout=setTimeout;
    returnfunction(){
      returnglobalSetTimeout(flush,1);
    };
  }

  varqueue=newArray(1000);
  functionflush(){
    for(vari=0;i<len;i+=2){
      varcallback=queue[i];
      vararg=queue[i+1];

      callback(arg);

      queue[i]=undefined;
      queue[i+1]=undefined;
    }

    len=0;
  }

  functionattemptVertx(){
    try{
      varvertx=Function('returnthis')().require('vertx');
      vertxNext=vertx.runOnLoop||vertx.runOnContext;
      returnuseVertxTimer();
    }catch(e){
      returnuseSetTimeout();
    }
  }

  varscheduleFlush=void0;
  //Decidewhatasyncmethodtousetotriggeringprocessingofqueuedcallbacks:
  if(isNode){
    scheduleFlush=useNextTick();
  }elseif(BrowserMutationObserver){
    scheduleFlush=useMutationObserver();
  }elseif(isWorker){
    scheduleFlush=useMessageChannel();
  }elseif(browserWindow===undefined&&typeofrequire==='function'){
    scheduleFlush=attemptVertx();
  }else{
    scheduleFlush=useSetTimeout();
  }

  functionthen(onFulfillment,onRejection){
    varparent=this;

    varchild=newthis.constructor(noop);

    if(child[PROMISE_ID]===undefined){
      makePromise(child);
    }

    var_state=parent._state;


    if(_state){
      varcallback=arguments[_state-1];
      asap(function(){
        returninvokeCallback(_state,child,callback,parent._result);
      });
    }else{
      subscribe(parent,child,onFulfillment,onRejection);
    }

    returnchild;
  }

  /**
    `Promise.resolve`returnsapromisethatwillbecomeresolvedwiththe
    passed`value`.Itisshorthandforthefollowing:

    ```javascript
    letpromise=newPromise(function(resolve,reject){
      resolve(1);
    });

    promise.then(function(value){
      //value===1
    });
    ```

    Insteadofwritingtheabove,yourcodenowsimplybecomesthefollowing:

    ```javascript
    letpromise=Promise.resolve(1);

    promise.then(function(value){
      //value===1
    });
    ```

    @methodresolve
    @static
    @param{Any}valuevaluethatthereturnedpromisewillberesolvedwith
    Usefulfortooling.
    @return{Promise}apromisethatwillbecomefulfilledwiththegiven
    `value`
  */
  functionresolve$1(object){
    /*jshintvalidthis:true*/
    varConstructor=this;

    if(object&&(typeofobject==='undefined'?'undefined':_typeof(object))==='object'&&object.constructor===Constructor){
      returnobject;
    }

    varpromise=newConstructor(noop);
    resolve(promise,object);
    returnpromise;
  }

  varPROMISE_ID=Math.random().toString(36).substring(2);

  functionnoop(){}

  varPENDING=void0;
  varFULFILLED=1;
  varREJECTED=2;

  varTRY_CATCH_ERROR={error:null};

  functionselfFulfillment(){
    returnnewTypeError("Youcannotresolveapromisewithitself");
  }

  functioncannotReturnOwn(){
    returnnewTypeError('Apromisescallbackcannotreturnthatsamepromise.');
  }

  functiongetThen(promise){
    try{
      returnpromise.then;
    }catch(error){
      TRY_CATCH_ERROR.error=error;
      returnTRY_CATCH_ERROR;
    }
  }

  functiontryThen(then$$1,value,fulfillmentHandler,rejectionHandler){
    try{
      then$$1.call(value,fulfillmentHandler,rejectionHandler);
    }catch(e){
      returne;
    }
  }

  functionhandleForeignThenable(promise,thenable,then$$1){
    asap(function(promise){
      varsealed=false;
      varerror=tryThen(then$$1,thenable,function(value){
        if(sealed){
          return;
        }
        sealed=true;
        if(thenable!==value){
          resolve(promise,value);
        }else{
          fulfill(promise,value);
        }
      },function(reason){
        if(sealed){
          return;
        }
        sealed=true;

        reject(promise,reason);
      },'Settle:'+(promise._label||'unknownpromise'));

      if(!sealed&&error){
        sealed=true;
        reject(promise,error);
      }
    },promise);
  }

  functionhandleOwnThenable(promise,thenable){
    if(thenable._state===FULFILLED){
      fulfill(promise,thenable._result);
    }elseif(thenable._state===REJECTED){
      reject(promise,thenable._result);
    }else{
      subscribe(thenable,undefined,function(value){
        returnresolve(promise,value);
      },function(reason){
        returnreject(promise,reason);
      });
    }
  }

  functionhandleMaybeThenable(promise,maybeThenable,then$$1){
    if(maybeThenable.constructor===promise.constructor&&then$$1===then&&maybeThenable.constructor.resolve===resolve$1){
      handleOwnThenable(promise,maybeThenable);
    }else{
      if(then$$1===TRY_CATCH_ERROR){
        reject(promise,TRY_CATCH_ERROR.error);
        TRY_CATCH_ERROR.error=null;
      }elseif(then$$1===undefined){
        fulfill(promise,maybeThenable);
      }elseif(isFunction(then$$1)){
        handleForeignThenable(promise,maybeThenable,then$$1);
      }else{
        fulfill(promise,maybeThenable);
      }
    }
  }

  functionresolve(promise,value){
    if(promise===value){
      reject(promise,selfFulfillment());
    }elseif(objectOrFunction(value)){
      handleMaybeThenable(promise,value,getThen(value));
    }else{
      fulfill(promise,value);
    }
  }

  functionpublishRejection(promise){
    if(promise._onerror){
      promise._onerror(promise._result);
    }

    publish(promise);
  }

  functionfulfill(promise,value){
    if(promise._state!==PENDING){
      return;
    }

    promise._result=value;
    promise._state=FULFILLED;

    if(promise._subscribers.length!==0){
      asap(publish,promise);
    }
  }

  functionreject(promise,reason){
    if(promise._state!==PENDING){
      return;
    }
    promise._state=REJECTED;
    promise._result=reason;

    asap(publishRejection,promise);
  }

  functionsubscribe(parent,child,onFulfillment,onRejection){
    var_subscribers=parent._subscribers;
    varlength=_subscribers.length;


    parent._onerror=null;

    _subscribers[length]=child;
    _subscribers[length+FULFILLED]=onFulfillment;
    _subscribers[length+REJECTED]=onRejection;

    if(length===0&&parent._state){
      asap(publish,parent);
    }
  }

  functionpublish(promise){
    varsubscribers=promise._subscribers;
    varsettled=promise._state;

    if(subscribers.length===0){
      return;
    }

    varchild=void0,
        callback=void0,
        detail=promise._result;

    for(vari=0;i<subscribers.length;i+=3){
      child=subscribers[i];
      callback=subscribers[i+settled];

      if(child){
        invokeCallback(settled,child,callback,detail);
      }else{
        callback(detail);
      }
    }

    promise._subscribers.length=0;
  }

  functiontryCatch(callback,detail){
    try{
      returncallback(detail);
    }catch(e){
      TRY_CATCH_ERROR.error=e;
      returnTRY_CATCH_ERROR;
    }
  }

  functioninvokeCallback(settled,promise,callback,detail){
    varhasCallback=isFunction(callback),
        value=void0,
        error=void0,
        succeeded=void0,
        failed=void0;

    if(hasCallback){
      value=tryCatch(callback,detail);

      if(value===TRY_CATCH_ERROR){
        failed=true;
        error=value.error;
        value.error=null;
      }else{
        succeeded=true;
      }

      if(promise===value){
        reject(promise,cannotReturnOwn());
        return;
      }
    }else{
      value=detail;
      succeeded=true;
    }

    if(promise._state!==PENDING){
      //noop
    }elseif(hasCallback&&succeeded){
      resolve(promise,value);
    }elseif(failed){
      reject(promise,error);
    }elseif(settled===FULFILLED){
      fulfill(promise,value);
    }elseif(settled===REJECTED){
      reject(promise,value);
    }
  }

  functioninitializePromise(promise,resolver){
    try{
      resolver(functionresolvePromise(value){
        resolve(promise,value);
      },functionrejectPromise(reason){
        reject(promise,reason);
      });
    }catch(e){
      reject(promise,e);
    }
  }

  varid=0;
  functionnextId(){
    returnid++;
  }

  functionmakePromise(promise){
    promise[PROMISE_ID]=id++;
    promise._state=undefined;
    promise._result=undefined;
    promise._subscribers=[];
  }

  functionvalidationError(){
    returnnewError('ArrayMethodsmustbeprovidedanArray');
  }

  varEnumerator=function(){
    functionEnumerator(Constructor,input){
      classCallCheck(this,Enumerator);

      this._instanceConstructor=Constructor;
      this.promise=newConstructor(noop);

      if(!this.promise[PROMISE_ID]){
        makePromise(this.promise);
      }

      if(isArray(input)){
        this.length=input.length;
        this._remaining=input.length;

        this._result=newArray(this.length);

        if(this.length===0){
          fulfill(this.promise,this._result);
        }else{
          this.length=this.length||0;
          this._enumerate(input);
          if(this._remaining===0){
            fulfill(this.promise,this._result);
          }
        }
      }else{
        reject(this.promise,validationError());
      }
    }

    createClass(Enumerator,[{
      key:'_enumerate',
      value:function_enumerate(input){
        for(vari=0;this._state===PENDING&&i<input.length;i++){
          this._eachEntry(input[i],i);
        }
      }
    },{
      key:'_eachEntry',
      value:function_eachEntry(entry,i){
        varc=this._instanceConstructor;
        varresolve$$1=c.resolve;


        if(resolve$$1===resolve$1){
          var_then=getThen(entry);

          if(_then===then&&entry._state!==PENDING){
            this._settledAt(entry._state,i,entry._result);
          }elseif(typeof_then!=='function'){
            this._remaining--;
            this._result[i]=entry;
          }elseif(c===Promise$2){
            varpromise=newc(noop);
            handleMaybeThenable(promise,entry,_then);
            this._willSettleAt(promise,i);
          }else{
            this._willSettleAt(newc(function(resolve$$1){
              returnresolve$$1(entry);
            }),i);
          }
        }else{
          this._willSettleAt(resolve$$1(entry),i);
        }
      }
    },{
      key:'_settledAt',
      value:function_settledAt(state,i,value){
        varpromise=this.promise;


        if(promise._state===PENDING){
          this._remaining--;

          if(state===REJECTED){
            reject(promise,value);
          }else{
            this._result[i]=value;
          }
        }

        if(this._remaining===0){
          fulfill(promise,this._result);
        }
      }
    },{
      key:'_willSettleAt',
      value:function_willSettleAt(promise,i){
        varenumerator=this;

        subscribe(promise,undefined,function(value){
          returnenumerator._settledAt(FULFILLED,i,value);
        },function(reason){
          returnenumerator._settledAt(REJECTED,i,reason);
        });
      }
    }]);
    returnEnumerator;
  }();

  /**
    `Promise.all`acceptsanarrayofpromises,andreturnsanewpromisewhich
    isfulfilledwithanarrayoffulfillmentvaluesforthepassedpromises,or
    rejectedwiththereasonofthefirstpassedpromisetoberejected.Itcastsall
    elementsofthepassediterabletopromisesasitrunsthisalgorithm.

    Example:

    ```javascript
    letpromise1=resolve(1);
    letpromise2=resolve(2);
    letpromise3=resolve(3);
    letpromises=[promise1,promise2,promise3];

    Promise.all(promises).then(function(array){
      //Thearrayherewouldbe[1,2,3];
    });
    ```

    Ifanyofthe`promises`givento`all`arerejected,thefirstpromise
    thatisrejectedwillbegivenasanargumenttothereturnedpromises's
    rejectionhandler.Forexample:

    Example:

    ```javascript
    letpromise1=resolve(1);
    letpromise2=reject(newError("2"));
    letpromise3=reject(newError("3"));
    letpromises=[promise1,promise2,promise3];

    Promise.all(promises).then(function(array){
      //Codehereneverrunsbecausetherearerejectedpromises!
    },function(error){
      //error.message==="2"
    });
    ```

    @methodall
    @static
    @param{Array}entriesarrayofpromises
    @param{String}labeloptionalstringforlabelingthepromise.
    Usefulfortooling.
    @return{Promise}promisethatisfulfilledwhenall`promises`havebeen
    fulfilled,orrejectedifanyofthembecomerejected.
    @static
  */
  functionall(entries){
    returnnewEnumerator(this,entries).promise;
  }

  /**
    `Promise.race`returnsanewpromisewhichissettledinthesamewayasthe
    firstpassedpromisetosettle.

    Example:

    ```javascript
    letpromise1=newPromise(function(resolve,reject){
      setTimeout(function(){
        resolve('promise1');
      },200);
    });

    letpromise2=newPromise(function(resolve,reject){
      setTimeout(function(){
        resolve('promise2');
      },100);
    });

    Promise.race([promise1,promise2]).then(function(result){
      //result==='promise2'becauseitwasresolvedbeforepromise1
      //wasresolved.
    });
    ```

    `Promise.race`isdeterministicinthatonlythestateofthefirst
    settledpromisematters.Forexample,evenifotherpromisesgiventothe
    `promises`arrayargumentareresolved,butthefirstsettledpromisehas
    becomerejectedbeforetheotherpromisesbecamefulfilled,thereturned
    promisewillbecomerejected:

    ```javascript
    letpromise1=newPromise(function(resolve,reject){
      setTimeout(function(){
        resolve('promise1');
      },200);
    });

    letpromise2=newPromise(function(resolve,reject){
      setTimeout(function(){
        reject(newError('promise2'));
      },100);
    });

    Promise.race([promise1,promise2]).then(function(result){
      //Codehereneverruns
    },function(reason){
      //reason.message==='promise2'becausepromise2becamerejectedbefore
      //promise1becamefulfilled
    });
    ```

    Anexamplereal-worldusecaseisimplementingtimeouts:

    ```javascript
    Promise.race([ajax('foo.json'),timeout(5000)])
    ```

    @methodrace
    @static
    @param{Array}promisesarrayofpromisestoobserve
    Usefulfortooling.
    @return{Promise}apromisewhichsettlesinthesamewayasthefirstpassed
    promisetosettle.
  */
  functionrace(entries){
    /*jshintvalidthis:true*/
    varConstructor=this;

    if(!isArray(entries)){
      returnnewConstructor(function(_,reject){
        returnreject(newTypeError('Youmustpassanarraytorace.'));
      });
    }else{
      returnnewConstructor(function(resolve,reject){
        varlength=entries.length;
        for(vari=0;i<length;i++){
          Constructor.resolve(entries[i]).then(resolve,reject);
        }
      });
    }
  }

  /**
    `Promise.reject`returnsapromiserejectedwiththepassed`reason`.
    Itisshorthandforthefollowing:

    ```javascript
    letpromise=newPromise(function(resolve,reject){
      reject(newError('WHOOPS'));
    });

    promise.then(function(value){
      //Codeheredoesn'trunbecausethepromiseisrejected!
    },function(reason){
      //reason.message==='WHOOPS'
    });
    ```

    Insteadofwritingtheabove,yourcodenowsimplybecomesthefollowing:

    ```javascript
    letpromise=Promise.reject(newError('WHOOPS'));

    promise.then(function(value){
      //Codeheredoesn'trunbecausethepromiseisrejected!
    },function(reason){
      //reason.message==='WHOOPS'
    });
    ```

    @methodreject
    @static
    @param{Any}reasonvaluethatthereturnedpromisewillberejectedwith.
    Usefulfortooling.
    @return{Promise}apromiserejectedwiththegiven`reason`.
  */
  functionreject$1(reason){
    /*jshintvalidthis:true*/
    varConstructor=this;
    varpromise=newConstructor(noop);
    reject(promise,reason);
    returnpromise;
  }

  functionneedsResolver(){
    thrownewTypeError('Youmustpassaresolverfunctionasthefirstargumenttothepromiseconstructor');
  }

  functionneedsNew(){
    thrownewTypeError("Failedtoconstruct'Promise':Pleaseusethe'new'operator,thisobjectconstructorcannotbecalledasafunction.");
  }

  /**
    Promiseobjectsrepresenttheeventualresultofanasynchronousoperation.The
    primarywayofinteractingwithapromiseisthroughits`then`method,which
    registerscallbackstoreceiveeitherapromise'seventualvalueorthereason
    whythepromisecannotbefulfilled.

    Terminology
    -----------

    -`promise`isanobjectorfunctionwitha`then`methodwhosebehaviorconformstothisspecification.
    -`thenable`isanobjectorfunctionthatdefinesa`then`method.
    -`value`isanylegalJavaScriptvalue(includingundefined,athenable,orapromise).
    -`exception`isavaluethatisthrownusingthethrowstatement.
    -`reason`isavaluethatindicateswhyapromisewasrejected.
    -`settled`thefinalrestingstateofapromise,fulfilledorrejected.

    Apromisecanbeinoneofthreestates:pending,fulfilled,orrejected.

    Promisesthatarefulfilledhaveafulfillmentvalueandareinthefulfilled
    state. Promisesthatarerejectedhavearejectionreasonandareinthe
    rejectedstate. Afulfillmentvalueisneverathenable.

    Promisescanalsobesaidto*resolve*avalue. Ifthisvalueisalsoa
    promise,thentheoriginalpromise'ssettledstatewillmatchthevalue's
    settledstate. Soapromisethat*resolves*apromisethatrejectswill
    itselfreject,andapromisethat*resolves*apromisethatfulfillswill
    itselffulfill.


    BasicUsage:
    ------------

    ```js
    letpromise=newPromise(function(resolve,reject){
      //onsuccess
      resolve(value);

      //onfailure
      reject(reason);
    });

    promise.then(function(value){
      //onfulfillment
    },function(reason){
      //onrejection
    });
    ```

    AdvancedUsage:
    ---------------

    Promisesshinewhenabstractingawayasynchronousinteractionssuchas
    `XMLHttpRequest`s.

    ```js
    functiongetJSON(url){
      returnnewPromise(function(resolve,reject){
        letxhr=newXMLHttpRequest();

        xhr.open('GET',url);
        xhr.onreadystatechange=handler;
        xhr.responseType='json';
        xhr.setRequestHeader('Accept','application/json');
        xhr.send();

        functionhandler(){
          if(this.readyState===this.DONE){
            if(this.status===200){
              resolve(this.response);
            }else{
              reject(newError('getJSON:`'+url+'`failedwithstatus:['+this.status+']'));
            }
          }
        };
      });
    }

    getJSON('/posts.json').then(function(json){
      //onfulfillment
    },function(reason){
      //onrejection
    });
    ```

    Unlikecallbacks,promisesaregreatcomposableprimitives.

    ```js
    Promise.all([
      getJSON('/posts'),
      getJSON('/comments')
    ]).then(function(values){
      values[0]//=>postsJSON
      values[1]//=>commentsJSON

      returnvalues;
    });
    ```

    @classPromise
    @param{Function}resolver
    Usefulfortooling.
    @constructor
  */

  varPromise$2=function(){
    functionPromise(resolver){
      classCallCheck(this,Promise);

      this[PROMISE_ID]=nextId();
      this._result=this._state=undefined;
      this._subscribers=[];

      if(noop!==resolver){
        typeofresolver!=='function'&&needsResolver();
        thisinstanceofPromise?initializePromise(this,resolver):needsNew();
      }
    }

    /**
    Theprimarywayofinteractingwithapromiseisthroughits`then`method,
    whichregisterscallbackstoreceiveeitherapromise'seventualvalueorthe
    reasonwhythepromisecannotbefulfilled.
     ```js
    findUser().then(function(user){
      //userisavailable
    },function(reason){
      //userisunavailable,andyouaregiventhereasonwhy
    });
    ```
     Chaining
    --------
     Thereturnvalueof`then`isitselfapromise. Thissecond,'downstream'
    promiseisresolvedwiththereturnvalueofthefirstpromise'sfulfillment
    orrejectionhandler,orrejectedifthehandlerthrowsanexception.
     ```js
    findUser().then(function(user){
      returnuser.name;
    },function(reason){
      return'defaultname';
    }).then(function(userName){
      //If`findUser`fulfilled,`userName`willbetheuser'sname,otherwiseit
      //willbe`'defaultname'`
    });
     findUser().then(function(user){
      thrownewError('Founduser,butstillunhappy');
    },function(reason){
      thrownewError('`findUser`rejectedandwe'reunhappy');
    }).then(function(value){
      //neverreached
    },function(reason){
      //if`findUser`fulfilled,`reason`willbe'Founduser,butstillunhappy'.
      //If`findUser`rejected,`reason`willbe'`findUser`rejectedandwe'reunhappy'.
    });
    ```
    Ifthedownstreampromisedoesnotspecifyarejectionhandler,rejectionreasonswillbepropagatedfurtherdownstream.
     ```js
    findUser().then(function(user){
      thrownewPedagogicalException('Upstreamerror');
    }).then(function(value){
      //neverreached
    }).then(function(value){
      //neverreached
    },function(reason){
      //The`PedgagocialException`ispropagatedallthewaydowntohere
    });
    ```
     Assimilation
    ------------
     Sometimesthevalueyouwanttopropagatetoadownstreampromisecanonlybe
    retrievedasynchronously.Thiscanbeachievedbyreturningapromiseinthe
    fulfillmentorrejectionhandler.Thedownstreampromisewillthenbepending
    untilthereturnedpromiseissettled.Thisiscalled*assimilation*.
     ```js
    findUser().then(function(user){
      returnfindCommentsByAuthor(user);
    }).then(function(comments){
      //Theuser'scommentsarenowavailable
    });
    ```
     Iftheassimliatedpromiserejects,thenthedownstreampromisewillalsoreject.
     ```js
    findUser().then(function(user){
      returnfindCommentsByAuthor(user);
    }).then(function(comments){
      //If`findCommentsByAuthor`fulfills,we'llhavethevaluehere
    },function(reason){
      //If`findCommentsByAuthor`rejects,we'llhavethereasonhere
    });
    ```
     SimpleExample
    --------------
     SynchronousExample
     ```javascript
    letresult;
     try{
      result=findResult();
      //success
    }catch(reason){
      //failure
    }
    ```
     ErrbackExample
     ```js
    findResult(function(result,err){
      if(err){
        //failure
      }else{
        //success
      }
    });
    ```
     PromiseExample;
     ```javascript
    findResult().then(function(result){
      //success
    },function(reason){
      //failure
    });
    ```
     AdvancedExample
    --------------
     SynchronousExample
     ```javascript
    letauthor,books;
     try{
      author=findAuthor();
      books =findBooksByAuthor(author);
      //success
    }catch(reason){
      //failure
    }
    ```
     ErrbackExample
     ```js
     functionfoundBooks(books){
     }
     functionfailure(reason){
     }
     findAuthor(function(author,err){
      if(err){
        failure(err);
        //failure
      }else{
        try{
          findBoooksByAuthor(author,function(books,err){
            if(err){
              failure(err);
            }else{
              try{
                foundBooks(books);
              }catch(reason){
                failure(reason);
              }
            }
          });
        }catch(error){
          failure(err);
        }
        //success
      }
    });
    ```
     PromiseExample;
     ```javascript
    findAuthor().
      then(findBooksByAuthor).
      then(function(books){
        //foundbooks
    }).catch(function(reason){
      //somethingwentwrong
    });
    ```
     @methodthen
    @param{Function}onFulfilled
    @param{Function}onRejected
    Usefulfortooling.
    @return{Promise}
    */

    /**
    `catch`issimplysugarfor`then(undefined,onRejection)`whichmakesitthesame
    asthecatchblockofatry/catchstatement.
    ```js
    functionfindAuthor(){
    thrownewError('couldn'tfindthatauthor');
    }
    //synchronous
    try{
    findAuthor();
    }catch(reason){
    //somethingwentwrong
    }
    //asyncwithpromises
    findAuthor().catch(function(reason){
    //somethingwentwrong
    });
    ```
    @methodcatch
    @param{Function}onRejection
    Usefulfortooling.
    @return{Promise}
    */


    createClass(Promise,[{
      key:'catch',
      value:function_catch(onRejection){
        returnthis.then(null,onRejection);
      }

      /**
        `finally`willbeinvokedregardlessofthepromise'sfatejustasnative
        try/catch/finallybehaves

        Synchronousexample:

        ```js
        findAuthor(){
          if(Math.random()>0.5){
            thrownewError();
          }
          returnnewAuthor();
        }

        try{
          returnfindAuthor();//succeedorfail
        }catch(error){
          returnfindOtherAuther();
        }finally{
          //alwaysruns
          //doesn'taffectthereturnvalue
        }
        ```

        Asynchronousexample:

        ```js
        findAuthor().catch(function(reason){
          returnfindOtherAuther();
        }).finally(function(){
          //authorwaseitherfound,ornot
        });
        ```

        @methodfinally
        @param{Function}callback
        @return{Promise}
      */

    },{
      key:'finally',
      value:function_finally(callback){
        varpromise=this;
        varconstructor=promise.constructor;

        if(isFunction(callback)){
          returnpromise.then(function(value){
            returnconstructor.resolve(callback()).then(function(){
              returnvalue;
            });
          },function(reason){
            returnconstructor.resolve(callback()).then(function(){
              throwreason;
            });
          });
        }

        returnpromise.then(callback,callback);
      }
    }]);
    returnPromise;
  }();

  Promise$2.prototype.then=then;
  Promise$2.all=all;
  Promise$2.race=race;
  Promise$2.resolve=resolve$1;
  Promise$2.reject=reject$1;
  Promise$2._setScheduler=setScheduler;
  Promise$2._setAsap=setAsap;
  Promise$2._asap=asap;

  /*globalself*/
  functionpolyfill(){
    varlocal=void0;

    if(typeofglobal!=='undefined'){
      local=global;
    }elseif(typeofself!=='undefined'){
      local=self;
    }else{
      try{
        local=Function('returnthis')();
      }catch(e){
        thrownewError('polyfillfailedbecauseglobalobjectisunavailableinthisenvironment');
      }
    }

    varP=local.Promise;

    if(P){
      varpromiseToString=null;
      try{
        promiseToString=Object.prototype.toString.call(P.resolve());
      }catch(e){
        //silentlyignored
      }

      if(promiseToString==='[objectPromise]'&&!P.cast){
        return;
      }
    }

    local.Promise=Promise$2;
  }

  //Strangecompat..
  Promise$2.polyfill=polyfill;
  Promise$2.Promise=Promise$2;

  varPromise$1=typeofPromise!=="undefined"?Promise:Promise$2;

  //Registerloggingcallbacks
  functionregisterLoggingCallbacks(obj){
  	vari,
  	   l,
  	   key,
  	   callbackNames=["begin","done","log","testStart","testDone","moduleStart","moduleDone"];

  	functionregisterLoggingCallback(key){
  		varloggingCallback=functionloggingCallback(callback){
  			if(objectType(callback)!=="function"){
  				thrownewError("QUnitloggingmethodsrequireacallbackfunctionastheirfirstparameters.");
  			}

  			config.callbacks[key].push(callback);
  		};

  		returnloggingCallback;
  	}

  	for(i=0,l=callbackNames.length;i<l;i++){
  		key=callbackNames[i];

  		//Initializekeycollectionofloggingcallback
  		if(objectType(config.callbacks[key])==="undefined"){
  			config.callbacks[key]=[];
  		}

  		obj[key]=registerLoggingCallback(key);
  	}
  }

  functionrunLoggingCallbacks(key,args){
  	varcallbacks=config.callbacks[key];

  	//Handling'log'callbacksseparately.Unliketheothercallbacks,
  	//thelogcallbackisnotcontrolledbytheprocessingqueue,
  	//butratherusedbyasserts.Hencetopromisfythe'log'callback
  	//wouldmeanpromisfyingeachstepofatest
  	if(key==="log"){
  		callbacks.map(function(callback){
  			returncallback(args);
  		});
  		return;
  	}

  	//ensurethateachcallbackisexecutedserially
  	returncallbacks.reduce(function(promiseChain,callback){
  		returnpromiseChain.then(function(){
  			returnPromise$1.resolve(callback(args));
  		});
  	},Promise$1.resolve([]));
  }

  //Doesn'tsupportIE9,itwillreturnundefinedonthesebrowsers
  //Seealsohttps://developer.mozilla.org/en/JavaScript/Reference/Global_Objects/Error/Stack
  varfileName=(sourceFromStacktrace(0)||"").replace(/(:\d+)+\)?/,"").replace(/.+\//,"");

  functionextractStacktrace(e,offset){
  	offset=offset===undefined?4:offset;

  	varstack,include,i;

  	if(e&&e.stack){
  		stack=e.stack.split("\n");
  		if(/^error$/i.test(stack[0])){
  			stack.shift();
  		}
  		if(fileName){
  			include=[];
  			for(i=offset;i<stack.length;i++){
  				if(stack[i].indexOf(fileName)!==-1){
  					break;
  				}
  				include.push(stack[i]);
  			}
  			if(include.length){
  				returninclude.join("\n");
  			}
  		}
  		returnstack[offset];
  	}
  }

  functionsourceFromStacktrace(offset){
  	varerror=newError();

  	//Support:Safari<=7only,IE<=10-11only
  	//Notallbrowsersgeneratethe`stack`propertyfor`newError()`,seealso#636
  	if(!error.stack){
  		try{
  			throwerror;
  		}catch(err){
  			error=err;
  		}
  	}

  	returnextractStacktrace(error,offset);
  }

  varpriorityCount=0;
  varunitSampler=void0;

  //Thisisaqueueoffunctionsthataretaskswithinasingletest.
  //Aftertestsaredequeuedfromconfig.queuetheyareexpandedinto
  //asetoftasksinthisqueue.
  vartaskQueue=[];

  /**
   *AdvancesthetaskQueuetothenexttask.IfthetaskQueueisempty,
   *processthetestQueue
   */
  functionadvance(){
  	advanceTaskQueue();

  	if(!taskQueue.length&&!config.blocking&&!config.current){
  		advanceTestQueue();
  	}
  }

  /**
   *AdvancesthetaskQueuewithanincreaseddepth
   */
  functionadvanceTaskQueue(){
  	varstart=now();
  	config.depth=(config.depth||0)+1;

  	processTaskQueue(start);

  	config.depth--;
  }

  /**
   *ProcessthefirsttaskonthetaskQueueasapromise.
   *Eachtaskisafunctionreturnedbyhttps://github.com/qunitjs/qunit/blob/master/src/test.js#L381
   */
  functionprocessTaskQueue(start){
  	if(taskQueue.length&&!config.blocking){
  		varelapsedTime=now()-start;

  		if(!defined.setTimeout||config.updateRate<=0||elapsedTime<config.updateRate){
  			vartask=taskQueue.shift();
  			Promise$1.resolve(task()).then(function(){
  				if(!taskQueue.length){
  					advance();
  				}else{
  					processTaskQueue(start);
  				}
  			});
  		}else{
  			setTimeout$1(advance);
  		}
  	}
  }

  /**
   *AdvancethetestQueuetothenexttesttoprocess.Calldone()iftestQueuecompletes.
   */
  functionadvanceTestQueue(){
  	if(!config.blocking&&!config.queue.length&&config.depth===0){
  		done();
  		return;
  	}

  	vartestTasks=config.queue.shift();
  	addToTaskQueue(testTasks());

  	if(priorityCount>0){
  		priorityCount--;
  	}

  	advance();
  }

  /**
   *Enqueuethetasksforatestintothetaskqueue.
   *@param{Array}tasksArray
   */
  functionaddToTaskQueue(tasksArray){
  	taskQueue.push.apply(taskQueue,toConsumableArray(tasksArray));
  }

  /**
   *Returnthenumberoftasksremaininginthetaskqueuetobeprocessed.
   *@return{Number}
   */
  functiontaskQueueLength(){
  	returntaskQueue.length;
  }

  /**
   *AddsatesttotheTestQueueforexecution.
   *@param{Function}testTasksFunc
   *@param{Boolean}prioritize
   *@param{String}seed
   */
  functionaddToTestQueue(testTasksFunc,prioritize,seed){
  	if(prioritize){
  		config.queue.splice(priorityCount++,0,testTasksFunc);
  	}elseif(seed){
  		if(!unitSampler){
  			unitSampler=unitSamplerGenerator(seed);
  		}

  		//Insertintoarandompositionafterallprioritizeditems
  		varindex=Math.floor(unitSampler()*(config.queue.length-priorityCount+1));
  		config.queue.splice(priorityCount+index,0,testTasksFunc);
  	}else{
  		config.queue.push(testTasksFunc);
  	}
  }

  /**
   *Createsaseeded"sample"generatorwhichisusedforrandomizingtests.
   */
  functionunitSamplerGenerator(seed){

  	//32-bitxorshift,requiresonlyanonzeroseed
  	//http://excamera.com/sphinx/article-xorshift.html
  	varsample=parseInt(generateHash(seed),16)||-1;
  	returnfunction(){
  		sample^=sample<<13;
  		sample^=sample>>>17;
  		sample^=sample<<5;

  		//ECMAScripthasnounsignednumbertype
  		if(sample<0){
  			sample+=0x100000000;
  		}

  		returnsample/0x100000000;
  	};
  }

  /**
   *ThisfunctioniscalledwhentheProcessingQueueisdoneprocessingall
   *items.Ithandlesemittingthefinalrunevents.
   */
  functiondone(){
  	varstorage=config.storage;

  	ProcessingQueue.finished=true;

  	varruntime=now()-config.started;
  	varpassed=config.stats.all-config.stats.bad;

  	if(config.stats.all===0){

  		if(config.filter&&config.filter.length){
  			thrownewError("Notestsmatchedthefilter\""+config.filter+"\".");
  		}

  		if(config.module&&config.module.length){
  			thrownewError("Notestsmatchedthemodule\""+config.module+"\".");
  		}

  		if(config.moduleId&&config.moduleId.length){
  			thrownewError("NotestsmatchedthemoduleId\""+config.moduleId+"\".");
  		}

  		if(config.testId&&config.testId.length){
  			thrownewError("NotestsmatchedthetestId\""+config.testId+"\".");
  		}

  		thrownewError("Notestswererun.");
  	}

  	emit("runEnd",globalSuite.end(true));
  	runLoggingCallbacks("done",{
  		passed:passed,
  		failed:config.stats.bad,
  		total:config.stats.all,
  		runtime:runtime
  	}).then(function(){

  		//Clearownstorageitemsifalltestspassed
  		if(storage&&config.stats.bad===0){
  			for(vari=storage.length-1;i>=0;i--){
  				varkey=storage.key(i);

  				if(key.indexOf("qunit-test-")===0){
  					storage.removeItem(key);
  				}
  			}
  		}
  	});
  }

  varProcessingQueue={
  	finished:false,
  	add:addToTestQueue,
  	advance:advance,
  	taskCount:taskQueueLength
  };

  varTestReport=function(){
  	functionTestReport(name,suite,options){
  		classCallCheck(this,TestReport);

  		this.name=name;
  		this.suiteName=suite.name;
  		this.fullName=suite.fullName.concat(name);
  		this.runtime=0;
  		this.assertions=[];

  		this.skipped=!!options.skip;
  		this.todo=!!options.todo;

  		this.valid=options.valid;

  		this._startTime=0;
  		this._endTime=0;

  		suite.pushTest(this);
  	}

  	createClass(TestReport,[{
  		key:"start",
  		value:functionstart(recordTime){
  			if(recordTime){
  				this._startTime=performanceNow();
  				if(performance){
  					performance.mark("qunit_test_start");
  				}
  			}

  			return{
  				name:this.name,
  				suiteName:this.suiteName,
  				fullName:this.fullName.slice()
  			};
  		}
  	},{
  		key:"end",
  		value:functionend(recordTime){
  			if(recordTime){
  				this._endTime=performanceNow();
  				if(performance){
  					performance.mark("qunit_test_end");

  					vartestName=this.fullName.join("–");

  					measure("QUnitTest:"+testName,"qunit_test_start","qunit_test_end");
  				}
  			}

  			returnextend(this.start(),{
  				runtime:this.getRuntime(),
  				status:this.getStatus(),
  				errors:this.getFailedAssertions(),
  				assertions:this.getAssertions()
  			});
  		}
  	},{
  		key:"pushAssertion",
  		value:functionpushAssertion(assertion){
  			this.assertions.push(assertion);
  		}
  	},{
  		key:"getRuntime",
  		value:functiongetRuntime(){
  			returnthis._endTime-this._startTime;
  		}
  	},{
  		key:"getStatus",
  		value:functiongetStatus(){
  			if(this.skipped){
  				return"skipped";
  			}

  			vartestPassed=this.getFailedAssertions().length>0?this.todo:!this.todo;

  			if(!testPassed){
  				return"failed";
  			}elseif(this.todo){
  				return"todo";
  			}else{
  				return"passed";
  			}
  		}
  	},{
  		key:"getFailedAssertions",
  		value:functiongetFailedAssertions(){
  			returnthis.assertions.filter(function(assertion){
  				return!assertion.passed;
  			});
  		}
  	},{
  		key:"getAssertions",
  		value:functiongetAssertions(){
  			returnthis.assertions.slice();
  		}

  		//Removeactualandexpectedvaluesfromassertions.Thisistoprevent
  		//leakingmemorythroughoutatestsuite.

  	},{
  		key:"slimAssertions",
  		value:functionslimAssertions(){
  			this.assertions=this.assertions.map(function(assertion){
  				deleteassertion.actual;
  				deleteassertion.expected;
  				returnassertion;
  			});
  		}
  	}]);
  	returnTestReport;
  }();

  varfocused$1=false;

  functionTest(settings){
  	vari,l;

  	++Test.count;

  	this.expected=null;
  	this.assertions=[];
  	this.semaphore=0;
  	this.module=config.currentModule;
  	this.stack=sourceFromStacktrace(3);
  	this.steps=[];
  	this.timeout=undefined;

  	//Ifamoduleisskipped,allitstestsandthetestsofthechildsuites
  	//shouldbetreatedasskippedeveniftheyaredefinedas`only`or`todo`.
  	//Asfor`todo`module,allitstestswillbetreatedas`todo`exceptfor
  	//testsdefinedas`skip`whichwillbeleftintact.
  	//
  	//So,ifatestisdefinedas`todo`andisinsideaskippedmodule,weshould
  	//thentreatthattestasifwasdefinedas`skip`.
  	if(this.module.skip){
  		settings.skip=true;
  		settings.todo=false;

  		//Skippedtestsshouldbeleftintact
  	}elseif(this.module.todo&&!settings.skip){
  		settings.todo=true;
  	}

  	extend(this,settings);

  	this.testReport=newTestReport(settings.testName,this.module.suiteReport,{
  		todo:settings.todo,
  		skip:settings.skip,
  		valid:this.valid()
  	});

  	//Registeruniquestrings
  	for(i=0,l=this.module.tests;i<l.length;i++){
  		if(this.module.tests[i].name===this.testName){
  			this.testName+="";
  		}
  	}

  	this.testId=generateHash(this.module.name,this.testName);

  	this.module.tests.push({
  		name:this.testName,
  		testId:this.testId,
  		skip:!!settings.skip
  	});

  	if(settings.skip){

  		//Skippedtestswillfullyignoreanysentcallback
  		this.callback=function(){};
  		this.async=false;
  		this.expected=0;
  	}else{
  		if(typeofthis.callback!=="function"){
  			varmethod=this.todo?"todo":"test";

  			//eslint-disable-next-linemax-len
  			thrownewTypeError("YoumustprovideafunctionasatestcallbacktoQUnit."+method+"(\""+settings.testName+"\")");
  		}

  		this.assert=newAssert(this);
  	}
  }

  Test.count=0;

  functiongetNotStartedModules(startModule){
  	varmodule=startModule,
  	   modules=[];

  	while(module&&module.testsRun===0){
  		modules.push(module);
  		module=module.parentModule;
  	}

  	//Theabovepushmodulesfromthechildtotheparent
  	//returnareversedorderwiththetopbeingthetopmostparentmodule
  	returnmodules.reverse();
  }

  Test.prototype={
  	getmoduleName(){returnthis.module.name;},
  	before:functionbefore(){
  		var_this=this;

  		varmodule=this.module,
  		   notStartedModules=getNotStartedModules(module);

  		//ensurethecallbacksareexecutedseriallyforeachmodule
  		varcallbackPromises=notStartedModules.reduce(function(promiseChain,startModule){
  			returnpromiseChain.then(function(){
  				startModule.stats={all:0,bad:0,started:now()};
  				emit("suiteStart",startModule.suiteReport.start(true));
  				returnrunLoggingCallbacks("moduleStart",{
  					name:startModule.name,
  					tests:startModule.tests
  				});
  			});
  		},Promise$1.resolve([]));

  		returncallbackPromises.then(function(){
  			config.current=_this;

  			_this.testEnvironment=extend({},module.testEnvironment);

  			_this.started=now();
			emit("testStart",_this.testReport.start(true));
			emit("FlectraBeforeTestHook");//Flectracustomization
  			returnrunLoggingCallbacks("testStart",{
  				name:_this.testName,
  				module:module.name,
  				testId:_this.testId,
  				previousFailure:_this.previousFailure
  			}).then(function(){
  				if(!config.pollution){
  					saveGlobal();
  				}
  			});
  		});
  	},

  	run:functionrun(){
  		varpromise;

  		config.current=this;

  		this.callbackStarted=now();

  		if(config.notrycatch){
  			runTest(this);
  			return;
  		}

  		try{
  			runTest(this);
  		}catch(e){
  			this.pushFailure("Diedontest#"+(this.assertions.length+1)+""+this.stack+":"+(e.message||e),extractStacktrace(e,0));

  			//Elsenexttestwillcarrytheresponsibility
  			saveGlobal();

  			//Restartthetestsifthey'reblocking
  			if(config.blocking){
  				internalRecover(this);
  			}
  		}

  		functionrunTest(test){
  			promise=test.callback.call(test.testEnvironment,test.assert);
  			test.resolvePromise(promise);

  			//Ifthetesthasa"lock"onit,butthetimeoutis0,thenwepusha
  			//failureasthetestshouldbesynchronous.
  			if(test.timeout===0&&test.semaphore!==0){
  				pushFailure("Testdidnotfinishsynchronouslyeventhoughassert.timeout(0)wasused.",sourceFromStacktrace(2));
  			}
  		}
  	},

  	after:functionafter(){
  		checkPollution();
  	},

  	queueHook:functionqueueHook(hook,hookName,hookOwner){
  		var_this2=this;

  		varcallHook=functioncallHook(){
  			varpromise=hook.call(_this2.testEnvironment,_this2.assert);
  			_this2.resolvePromise(promise,hookName);
  		};

  		varrunHook=functionrunHook(){
  			if(hookName==="before"){
  				if(hookOwner.unskippedTestsRun!==0){
  					return;
  				}

  				_this2.preserveEnvironment=true;
  			}

  			//The'after'hookshouldonlyexecutewhentherearenottestsleftand
  			//whenthe'after'and'finish'tasksaretheonlytaskslefttoprocess
  			if(hookName==="after"&&hookOwner.unskippedTestsRun!==numberOfUnskippedTests(hookOwner)-1&&(config.queue.length>0||ProcessingQueue.taskCount()>2)){
  				return;
  			}

  			config.current=_this2;
  			if(config.notrycatch){
  				callHook();
  				return;
  			}
  			try{
  				callHook();
  			}catch(error){
  				_this2.pushFailure(hookName+"failedon"+_this2.testName+":"+(error.message||error),extractStacktrace(error,0));
  			}
  		};

  		returnrunHook;
  	},


  	//Currentlyonlyusedformodulelevelhooks,canbeusedtoaddgloballevelones
  	hooks:functionhooks(handler){
  		varhooks=[];

  		functionprocessHooks(test,module){
  			if(module.parentModule){
  				processHooks(test,module.parentModule);
  			}

  			if(module.hooks[handler].length){
  				for(vari=0;i<module.hooks[handler].length;i++){
  					hooks.push(test.queueHook(module.hooks[handler][i],handler,module));
  				}
  			}
  		}

  		//Hooksareignoredonskippedtests
  		if(!this.skip){
  			processHooks(this,this.module);
  		}

  		returnhooks;
  	},


  	finish:functionfinish(){
  		config.current=this;

  		//Releasethetestcallbacktoensurethatanythingreferencedhasbeen
  		//releasedtobegarbagecollected.
  		this.callback=undefined;

  		if(this.steps.length){
  			varstepsList=this.steps.join(",");
  			this.pushFailure("Expectedassert.verifySteps()tobecalledbeforeendoftest"+("afterusingassert.step().Unverifiedsteps:"+stepsList),this.stack);
  		}

  		if(config.requireExpects&&this.expected===null){
  			this.pushFailure("Expectednumberofassertionstobedefined,butexpect()was"+"notcalled.",this.stack);
  		}elseif(this.expected!==null&&this.expected!==this.assertions.length){
  			this.pushFailure("Expected"+this.expected+"assertions,but"+this.assertions.length+"wererun",this.stack);
  		}elseif(this.expected===null&&!this.assertions.length){
  			this.pushFailure("Expectedatleastoneassertion,butnonewererun-call"+"expect(0)toacceptzeroassertions.",this.stack);
  		}

        emit("FlectraAfterTestHook",this);//Flectracustomization

  		vari,
  		   module=this.module,
  		   moduleName=module.name,
  		   testName=this.testName,
  		   skipped=!!this.skip,
  		   todo=!!this.todo,
  		   bad=0,
  		   storage=config.storage;

  		this.runtime=now()-this.started;

  		config.stats.all+=this.assertions.length;
  		module.stats.all+=this.assertions.length;

  		for(i=0;i<this.assertions.length;i++){
  			if(!this.assertions[i].result){
  				bad++;
  				config.stats.bad++;
  				module.stats.bad++;
  			}
  		}

  		notifyTestsRan(module,skipped);

  		//Storeresultwhenpossible
  		if(storage){
  			if(bad){
  				storage.setItem("qunit-test-"+moduleName+"-"+testName,bad);
  			}else{
  				storage.removeItem("qunit-test-"+moduleName+"-"+testName);
  			}
  		}

  		//Afteremittingthejs-reporterseventwecleanuptheassertiondatato
  		//avoidleakingit.ItisnotusedbythelegacytestDonecallbacks.
  		emit("testEnd",this.testReport.end(true));
  		this.testReport.slimAssertions();

  		returnrunLoggingCallbacks("testDone",{
  			name:testName,
  			module:moduleName,
  			skipped:skipped,
  			todo:todo,
  			failed:bad,
  			passed:this.assertions.length-bad,
  			total:this.assertions.length,
  			runtime:skipped?0:this.runtime,

  			//HTMLReporteruse
  			assertions:this.assertions,
  			testId:this.testId,

  			//SourceofTest
  			source:this.stack
  		}).then(function(){
  			if(module.testsRun===numberOfTests(module)){
  				varcompletedModules=[module];

  				//Checkiftheparentmodules,iteratively,aredone.Ifthatthecase,
  				//weemitthe`suiteEnd`eventandtrigger`moduleDone`callback.
  				varparent=module.parentModule;
  				while(parent&&parent.testsRun===numberOfTests(parent)){
  					completedModules.push(parent);
  					parent=parent.parentModule;
  				}

  				returncompletedModules.reduce(function(promiseChain,completedModule){
  					returnpromiseChain.then(function(){
  						returnlogSuiteEnd(completedModule);
  					});
  				},Promise$1.resolve([]));
  			}
  		}).then(function(){
  			config.current=undefined;
  		});

  		functionlogSuiteEnd(module){

  			//Reset`module.hooks`toensurethatanythingreferencedinthesehooks
  			//hasbeenreleasedtobegarbagecollected.
  			module.hooks={};

  			emit("suiteEnd",module.suiteReport.end(true));
  			returnrunLoggingCallbacks("moduleDone",{
  				name:module.name,
  				tests:module.tests,
  				failed:module.stats.bad,
  				passed:module.stats.all-module.stats.bad,
  				total:module.stats.all,
  				runtime:now()-module.stats.started
  			});
  		}
  	},

  	preserveTestEnvironment:functionpreserveTestEnvironment(){
  		if(this.preserveEnvironment){
  			this.module.testEnvironment=this.testEnvironment;
  			this.testEnvironment=extend({},this.module.testEnvironment);
  		}
  	},

  	queue:functionqueue(){
  		vartest=this;

  		if(!this.valid()){
  			return;
  		}

  		functionrunTest(){
  			return[function(){
  				returntest.before();
  			}].concat(toConsumableArray(test.hooks("before")),[function(){
  				test.preserveTestEnvironment();
  			}],toConsumableArray(test.hooks("beforeEach")),[function(){
  				test.run();
  			}],toConsumableArray(test.hooks("afterEach").reverse()),toConsumableArray(test.hooks("after").reverse()),[function(){
  				test.after();
  			},function(){
  				returntest.finish();
  			}]);
  		}

  		varpreviousFailCount=config.storage&&+config.storage.getItem("qunit-test-"+this.module.name+"-"+this.testName);

  		//Prioritizepreviouslyfailedtests,detectedfromstorage
  		varprioritize=config.reorder&&!!previousFailCount;

  		this.previousFailure=!!previousFailCount;

  		ProcessingQueue.add(runTest,prioritize,config.seed);

  		//Ifthequeuehasalreadyfinished,wemanuallyprocessthenewtest
  		if(ProcessingQueue.finished){
  			ProcessingQueue.advance();
  		}
  	},


  	pushResult:functionpushResult(resultInfo){
  		if(this!==config.current){
  			thrownewError("Assertionoccurredaftertesthadfinished.");
  		}

  		//DestructureofresultInfo={result,actual,expected,message,negative}
  		varsource,
  		   details={
  			module:this.module.name,
  			name:this.testName,
  			result:resultInfo.result,
  			message:resultInfo.message,
  			actual:resultInfo.actual,
  			testId:this.testId,
  			negative:resultInfo.negative||false,
  			runtime:now()-this.started,
  			todo:!!this.todo
  		};

  		if(hasOwn.call(resultInfo,"expected")){
  			details.expected=resultInfo.expected;
  		}

  		if(!resultInfo.result){
  			source=resultInfo.source||sourceFromStacktrace();

  			if(source){
  				details.source=source;
  			}
  		}

  		this.logAssertion(details);

  		this.assertions.push({
  			result:!!resultInfo.result,
  			message:resultInfo.message
  		});
  	},

  	pushFailure:functionpushFailure(message,source,actual){
  		if(!(thisinstanceofTest)){
  			thrownewError("pushFailure()assertionoutsidetestcontext,was"+sourceFromStacktrace(2));
  		}

  		this.pushResult({
  			result:false,
  			message:message||"error",
  			actual:actual||null,
  			source:source
  		});
  	},

  	/**
    *LogassertiondetailsusingboththeoldQUnit.loginterfaceand
    *QUnit.on("assertion")interface.
    *
    *@private
    */
  	logAssertion:functionlogAssertion(details){
  		runLoggingCallbacks("log",details);

  		varassertion={
  			passed:details.result,
  			actual:details.actual,
  			expected:details.expected,
  			message:details.message,
  			stack:details.source,
  			todo:details.todo
  		};
  		this.testReport.pushAssertion(assertion);
  		emit("assertion",assertion);
  	},


  	resolvePromise:functionresolvePromise(promise,phase){
  		varthen,
  		   resume,
  		   message,
  		   test=this;
  		if(promise!=null){
  			then=promise.then;
  			if(objectType(then)==="function"){
  				resume=internalStop(test);
  				if(config.notrycatch){
  					then.call(promise,function(){
  						resume();
  					});
  				}else{
  					then.call(promise,function(){
  						resume();
  					},function(error){
  						message="Promiserejected"+(!phase?"during":phase.replace(/Each$/,""))+"\""+test.testName+"\":"+(error&&error.message||error);
  						test.pushFailure(message,extractStacktrace(error,0));

  						//Elsenexttestwillcarrytheresponsibility
  						saveGlobal();

  						//Unblock
  						internalRecover(test);
  					});
  				}
  			}
  		}
  	},

  	valid:functionvalid(){
  		varfilter=config.filter,
  		   regexFilter=/^(!?)\/([\w\W]*)\/(i?$)/.exec(filter),
  		   module=config.module&&config.module.toLowerCase(),
  		   fullName=this.module.name+":"+this.testName;

  		functionmoduleChainNameMatch(testModule){
  			vartestModuleName=testModule.name?testModule.name.toLowerCase():null;
  			if(testModuleName===module){
  				returntrue;
  			}elseif(testModule.parentModule){
  				returnmoduleChainNameMatch(testModule.parentModule);
  			}else{
  				returnfalse;
  			}
  		}

  		functionmoduleChainIdMatch(testModule){
  			returninArray(testModule.moduleId,config.moduleId)||testModule.parentModule&&moduleChainIdMatch(testModule.parentModule);
  		}

  		//Internally-generatedtestsarealwaysvalid
  		if(this.callback&&this.callback.validTest){
  			returntrue;
  		}

  		if(config.moduleId&&config.moduleId.length>0&&!moduleChainIdMatch(this.module)){

  			returnfalse;
  		}

  		if(config.testId&&config.testId.length>0&&!inArray(this.testId,config.testId)){

  			returnfalse;
  		}

  		if(module&&!moduleChainNameMatch(this.module)){
  			returnfalse;
  		}

  		if(!filter){
  			returntrue;
  		}

  		returnregexFilter?this.regexFilter(!!regexFilter[1],regexFilter[2],regexFilter[3],fullName):this.stringFilter(filter,fullName);
  	},

  	regexFilter:functionregexFilter(exclude,pattern,flags,fullName){
  		varregex=newRegExp(pattern,flags);
  		varmatch=regex.test(fullName);

  		returnmatch!==exclude;
  	},

  	stringFilter:functionstringFilter(filter,fullName){
  		filter=filter.toLowerCase();
  		fullName=fullName.toLowerCase();

  		varinclude=filter.charAt(0)!=="!";
  		if(!include){
  			filter=filter.slice(1);
  		}

  		//Ifthefiltermatches,weneedtohonourinclude
  		if(fullName.indexOf(filter)!==-1){
  			returninclude;
  		}

  		//Otherwise,dotheopposite
  		return!include;
  	}
  };

  functionpushFailure(){
  	if(!config.current){
  		thrownewError("pushFailure()assertionoutsidetestcontext,in"+sourceFromStacktrace(2));
  	}

  	//Getscurrenttestobj
  	varcurrentTest=config.current;

  	returncurrentTest.pushFailure.apply(currentTest,arguments);
  }

  functionsaveGlobal(){
  	config.pollution=[];

  	if(config.noglobals){
  		for(varkeyinglobal$1){
  			if(hasOwn.call(global$1,key)){

  				//InOperasometimesDOMelementidsshowuphere,ignorethem
  				if(/^qunit-test-output/.test(key)){
  					continue;
  				}
  				config.pollution.push(key);
  			}
  		}
  	}
  }

  functioncheckPollution(){
  	varnewGlobals,
  	   deletedGlobals,
  	   old=config.pollution;

  	saveGlobal();

  	newGlobals=diff(config.pollution,old);
  	if(newGlobals.length>0){
  		pushFailure("Introducedglobalvariable(s):"+newGlobals.join(","));
  	}

  	deletedGlobals=diff(old,config.pollution);
  	if(deletedGlobals.length>0){
  		pushFailure("Deletedglobalvariable(s):"+deletedGlobals.join(","));
  	}
  }

  //WillbeexposedasQUnit.test
  functiontest(testName,callback){
  	if(focused$1){
  		return;
  	}

  	varnewTest=newTest({
  		testName:testName,
  		callback:callback
  	});

  	newTest.queue();
  }

  functiontodo(testName,callback){
  	if(focused$1){
  		return;
  	}

  	varnewTest=newTest({
  		testName:testName,
  		callback:callback,
  		todo:true
  	});

  	newTest.queue();
  }

  //WillbeexposedasQUnit.skip
  functionskip(testName){
  	if(focused$1){
  		return;
  	}

  	vartest=newTest({
  		testName:testName,
  		skip:true
  	});

  	test.queue();
  }

  //WillbeexposedasQUnit.only
  functiononly(testName,callback){
  	if(focused$1){
  		return;
  	}

  	config.queue.length=0;
  	focused$1=true;

  	varnewTest=newTest({
  		testName:testName,
  		callback:callback
  	});

  	newTest.queue();
  }

  //Putaholdonprocessingandreturnafunctionthatwillreleaseit.
  functioninternalStop(test){
  	test.semaphore+=1;
  	config.blocking=true;

  	//Setarecoverytimeout,ifsoconfigured.
  	if(defined.setTimeout){
  		vartimeoutDuration=void0;

  		if(typeoftest.timeout==="number"){
  			timeoutDuration=test.timeout;
  		}elseif(typeofconfig.testTimeout==="number"){
  			timeoutDuration=config.testTimeout;
  		}

  		if(typeoftimeoutDuration==="number"&&timeoutDuration>0){
  			clearTimeout(config.timeout);
  			config.timeout=setTimeout$1(function(){
  				pushFailure("Testtooklongerthan"+timeoutDuration+"ms;testtimedout.",sourceFromStacktrace(2));
  				internalRecover(test);
  			},timeoutDuration);
  		}
  	}

  	varreleased=false;
  	returnfunctionresume(){
  		if(released){
  			return;
  		}

  		released=true;
  		test.semaphore-=1;
  		internalStart(test);
  	};
  }

  //Forcefullyreleaseallprocessingholds.
  functioninternalRecover(test){
  	test.semaphore=0;
  	internalStart(test);
  }

  //Releaseaprocessinghold,schedulingaresumptionattemptifnoholdsremain.
  functioninternalStart(test){

  	//Ifsemaphoreisnon-numeric,throwerror
  	if(isNaN(test.semaphore)){
  		test.semaphore=0;

  		pushFailure("Invalidvalueontest.semaphore",sourceFromStacktrace(2));
  		return;
  	}

  	//Don'tstartuntilequalnumberofstop-calls
  	if(test.semaphore>0){
  		return;
  	}

  	//ThrowanErrorifstartiscalledmoreoftenthanstop
  	if(test.semaphore<0){
  		test.semaphore=0;

  		pushFailure("Triedtorestarttestwhilealreadystarted(test'ssemaphorewas0already)",sourceFromStacktrace(2));
  		return;
  	}

  	//Addaslightdelaytoallowmoreassertionsetc.
  	if(defined.setTimeout){
  		if(config.timeout){
  			clearTimeout(config.timeout);
  		}
  		config.timeout=setTimeout$1(function(){
  			if(test.semaphore>0){
  				return;
  			}

  			if(config.timeout){
  				clearTimeout(config.timeout);
  			}

  			begin();
  		});
  	}else{
  		begin();
  	}
  }

  functioncollectTests(module){
  	vartests=[].concat(module.tests);
  	varmodules=[].concat(toConsumableArray(module.childModules));

  	//Doabreadth-firsttraversalofthechildmodules
  	while(modules.length){
  		varnextModule=modules.shift();
  		tests.push.apply(tests,nextModule.tests);
  		modules.push.apply(modules,toConsumableArray(nextModule.childModules));
  	}

  	returntests;
  }

  functionnumberOfTests(module){
  	returncollectTests(module).length;
  }

  functionnumberOfUnskippedTests(module){
  	returncollectTests(module).filter(function(test){
  		return!test.skip;
  	}).length;
  }

  functionnotifyTestsRan(module,skipped){
  	module.testsRun++;
  	if(!skipped){
  		module.unskippedTestsRun++;
  	}
  	while(module=module.parentModule){
  		module.testsRun++;
  		if(!skipped){
  			module.unskippedTestsRun++;
  		}
  	}
  }

  varAssert=function(){
  	functionAssert(testContext){
  		classCallCheck(this,Assert);

  		this.test=testContext;
  	}

  	//Asserthelpers

  	createClass(Assert,[{
  		key:"timeout",
  		value:functiontimeout(duration){
  			if(typeofduration!=="number"){
  				thrownewError("Youmustpassanumberasthedurationtoassert.timeout");
  			}

  			this.test.timeout=duration;
  		}

  		//Documentsa"step",whichisastringvalue,inatestasapassingassertion

  	},{
  		key:"step",
  		value:functionstep(message){
  			varassertionMessage=message;
  			varresult=!!message;

  			this.test.steps.push(message);

  			if(objectType(message)==="undefined"||message===""){
  				assertionMessage="Youmustprovideamessagetoassert.step";
  			}elseif(objectType(message)!=="string"){
  				assertionMessage="Youmustprovideastringvaluetoassert.step";
  				result=false;
  			}

  			this.pushResult({
  				result:result,
  				message:assertionMessage
  			});
  		}

  		//Verifiesthestepsinatestmatchagivenarrayofstringvalues

  	},{
  		key:"verifySteps",
  		value:functionverifySteps(steps,message){

  			//Sincethestepsarrayisjuststringvalues,wecanclonewithslice
  			varactualStepsClone=this.test.steps.slice();
  			this.deepEqual(actualStepsClone,steps,message);
  			this.test.steps.length=0;
  		}

  		//Specifythenumberofexpectedassertionstoguaranteethatfailedtest
  		//(noassertionsarerunatall)don'tslipthrough.

  	},{
  		key:"expect",
  		value:functionexpect(asserts){
  			if(arguments.length===1){
  				this.test.expected=asserts;
  			}else{
  				returnthis.test.expected;
  			}
  		}

  		//Putaholdonprocessingandreturnafunctionthatwillreleaseitamaximumofonce.

  	},{
  		key:"async",
  		value:functionasync(count){
  			vartest$$1=this.test;

  			varpopped=false,
  			   acceptCallCount=count;

  			if(typeofacceptCallCount==="undefined"){
  				acceptCallCount=1;
  			}

  			varresume=internalStop(test$$1);

  			returnfunctiondone(){
  				if(config.current!==test$$1){
  					throwError("assert.asynccallbackcalledaftertestfinished.");
  				}

  				if(popped){
  					test$$1.pushFailure("Toomanycallstothe`assert.async`callback",sourceFromStacktrace(2));
  					return;
  				}

  				acceptCallCount-=1;
  				if(acceptCallCount>0){
  					return;
  				}

  				popped=true;
  				resume();
  			};
  		}

  		//Exportstest.push()totheuserAPI
  		//AliasofpushResult.

  	},{
  		key:"push",
  		value:functionpush(result,actual,expected,message,negative){
  			Logger.warn("assert.pushisdeprecatedandwillberemovedinQUnit3.0."+"Pleaseuseassert.pushResultinstead(https://api.qunitjs.com/assert/pushResult).");

  			varcurrentAssert=thisinstanceofAssert?this:config.current.assert;
  			returncurrentAssert.pushResult({
  				result:result,
  				actual:actual,
  				expected:expected,
  				message:message,
  				negative:negative
  			});
  		}
  	},{
  		key:"pushResult",
  		value:functionpushResult(resultInfo){

  			//DestructureofresultInfo={result,actual,expected,message,negative}
  			varassert=this;
  			varcurrentTest=assertinstanceofAssert&&assert.test||config.current;

  			//Backwardscompatibilityfix.
  			//AllowsthedirectuseofglobalexportedassertionsandQUnit.assert.*
  			//Although,it'suseisnotrecommendedasitcanleakassertions
  			//toothertestsfromasynctests,becauseweonlygetareferencetothecurrenttest,
  			//notexactlythetestwhereassertionwereintendedtobecalled.
  			if(!currentTest){
  				thrownewError("assertionoutsidetestcontext,in"+sourceFromStacktrace(2));
  			}

  			if(!(assertinstanceofAssert)){
  				assert=currentTest.assert;
  			}

  			returnassert.test.pushResult(resultInfo);
  		}
  	},{
  		key:"ok",
  		value:functionok(result,message){
  			if(!message){
  				message=result?"okay":"failed,expectedargumenttobetruthy,was:"+dump.parse(result);
  			}

  			this.pushResult({
  				result:!!result,
  				actual:result,
  				expected:true,
  				message:message
  			});
  		}
  	},{
  		key:"notOk",
  		value:functionnotOk(result,message){
  			if(!message){
  				message=!result?"okay":"failed,expectedargumenttobefalsy,was:"+dump.parse(result);
  			}

  			this.pushResult({
  				result:!result,
  				actual:result,
  				expected:false,
  				message:message
  			});
  		}
  	},{
  		key:"equal",
  		value:functionequal(actual,expected,message){

  			//eslint-disable-next-lineeqeqeq
  			varresult=expected==actual;

  			this.pushResult({
  				result:result,
  				actual:actual,
  				expected:expected,
  				message:message
  			});
  		}
  	},{
  		key:"notEqual",
  		value:functionnotEqual(actual,expected,message){

  			//eslint-disable-next-lineeqeqeq
  			varresult=expected!=actual;

  			this.pushResult({
  				result:result,
  				actual:actual,
  				expected:expected,
  				message:message,
  				negative:true
  			});
  		}
  	},{
  		key:"propEqual",
  		value:functionpropEqual(actual,expected,message){
  			actual=objectValues(actual);
  			expected=objectValues(expected);

  			this.pushResult({
  				result:equiv(actual,expected),
  				actual:actual,
  				expected:expected,
  				message:message
  			});
  		}
  	},{
  		key:"notPropEqual",
  		value:functionnotPropEqual(actual,expected,message){
  			actual=objectValues(actual);
  			expected=objectValues(expected);

  			this.pushResult({
  				result:!equiv(actual,expected),
  				actual:actual,
  				expected:expected,
  				message:message,
  				negative:true
  			});
  		}
  	},{
  		key:"deepEqual",
  		value:functiondeepEqual(actual,expected,message){
  			this.pushResult({
  				result:equiv(actual,expected),
  				actual:actual,
  				expected:expected,
  				message:message
  			});
  		}
  	},{
  		key:"notDeepEqual",
  		value:functionnotDeepEqual(actual,expected,message){
  			this.pushResult({
  				result:!equiv(actual,expected),
  				actual:actual,
  				expected:expected,
  				message:message,
  				negative:true
  			});
  		}
  	},{
  		key:"strictEqual",
  		value:functionstrictEqual(actual,expected,message){
  			this.pushResult({
  				result:expected===actual,
  				actual:actual,
  				expected:expected,
  				message:message
  			});
  		}
  	},{
  		key:"notStrictEqual",
  		value:functionnotStrictEqual(actual,expected,message){
  			this.pushResult({
  				result:expected!==actual,
  				actual:actual,
  				expected:expected,
  				message:message,
  				negative:true
  			});
  		}
  	},{
  		key:"throws",
  		value:functionthrows(block,expected,message){
  			varactual=void0,
  			   result=false;

  			varcurrentTest=thisinstanceofAssert&&this.test||config.current;

  			//'expected'isoptionalunlessdoingstringcomparison
  			if(objectType(expected)==="string"){
  				if(message==null){
  					message=expected;
  					expected=null;
  				}else{
  					thrownewError("throws/raisesdoesnotacceptastringvaluefortheexpectedargument.\n"+"Useanon-stringobjectvalue(e.g.regExp)insteadifit'snecessary.");
  				}
  			}

  			currentTest.ignoreGlobalErrors=true;
  			try{
  				block.call(currentTest.testEnvironment);
  			}catch(e){
  				actual=e;
  			}
  			currentTest.ignoreGlobalErrors=false;

  			if(actual){
  				varexpectedType=objectType(expected);

  				//Wedon'twanttovalidatethrownerror
  				if(!expected){
  					result=true;

  					//Expectedisaregexp
  				}elseif(expectedType==="regexp"){
  					result=expected.test(errorString(actual));

  					//Logthestringformoftheregexp
  					expected=String(expected);

  					//Expectedisaconstructor,maybeanErrorconstructor
  				}elseif(expectedType==="function"&&actualinstanceofexpected){
  					result=true;

  					//ExpectedisanErrorobject
  				}elseif(expectedType==="object"){
  					result=actualinstanceofexpected.constructor&&actual.name===expected.name&&actual.message===expected.message;

  					//LogthestringformoftheErrorobject
  					expected=errorString(expected);

  					//Expectedisavalidationfunctionwhichreturnstrueifvalidationpassed
  				}elseif(expectedType==="function"&&expected.call({},actual)===true){
  					expected=null;
  					result=true;
  				}
  			}

  			currentTest.assert.pushResult({
  				result:result,

  				//undefinedifitdidn'tthrow
  				actual:actual&&errorString(actual),
  				expected:expected,
  				message:message
  			});
  		}
  	},{
  		key:"rejects",
  		value:functionrejects(promise,expected,message){
  			varresult=false;

  			varcurrentTest=thisinstanceofAssert&&this.test||config.current;

  			//'expected'isoptionalunlessdoingstringcomparison
  			if(objectType(expected)==="string"){
  				if(message===undefined){
  					message=expected;
  					expected=undefined;
  				}else{
  					message="assert.rejectsdoesnotacceptastringvaluefortheexpected"+"argument.\nUseanon-stringobjectvalue(e.g.validatorfunction)instead"+"ifnecessary.";

  					currentTest.assert.pushResult({
  						result:false,
  						message:message
  					});

  					return;
  				}
  			}

  			varthen=promise&&promise.then;
  			if(objectType(then)!=="function"){
  				var_message="Thevalueprovidedto`assert.rejects`in"+"\""+currentTest.testName+"\"wasnotapromise.";

  				currentTest.assert.pushResult({
  					result:false,
  					message:_message,
  					actual:promise
  				});

  				return;
  			}

  			vardone=this.async();

  			returnthen.call(promise,functionhandleFulfillment(){
  				varmessage="Thepromisereturnedbythe`assert.rejects`callbackin"+"\""+currentTest.testName+"\"didnotreject.";

  				currentTest.assert.pushResult({
  					result:false,
  					message:message,
  					actual:promise
  				});

  				done();
  			},functionhandleRejection(actual){
  				varexpectedType=objectType(expected);

  				//Wedon'twanttovalidate
  				if(expected===undefined){
  					result=true;

  					//Expectedisaregexp
  				}elseif(expectedType==="regexp"){
  					result=expected.test(errorString(actual));

  					//Logthestringformoftheregexp
  					expected=String(expected);

  					//Expectedisaconstructor,maybeanErrorconstructor
  				}elseif(expectedType==="function"&&actualinstanceofexpected){
  					result=true;

  					//ExpectedisanErrorobject
  				}elseif(expectedType==="object"){
  					result=actualinstanceofexpected.constructor&&actual.name===expected.name&&actual.message===expected.message;

  					//LogthestringformoftheErrorobject
  					expected=errorString(expected);

  					//Expectedisavalidationfunctionwhichreturnstrueifvalidationpassed
  				}else{
  					if(expectedType==="function"){
  						result=expected.call({},actual)===true;
  						expected=null;

  						//Expectedissomeotherinvalidtype
  					}else{
  						result=false;
  						message="invalidexpectedvalueprovidedto`assert.rejects`"+"callbackin\""+currentTest.testName+"\":"+expectedType+".";
  					}
  				}

  				currentTest.assert.pushResult({
  					result:result,

  					//leaverejectionvalueofundefinedas-is
  					actual:actual&&errorString(actual),
  					expected:expected,
  					message:message
  				});

  				done();
  			});
  		}
  	}]);
  	returnAssert;
  }();

  //Provideanalternativetoassert.throws(),forenvironmentsthatconsiderthrowsareservedword
  //Knowntousare:ClosureCompiler,Narwhal
  //eslint-disable-next-linedot-notation


  Assert.prototype.raises=Assert.prototype["throws"];

  /**
   *Convertsanerrorintoasimplestringforcomparisons.
   *
   *@param{Error|Object}error
   *@return{String}
   */
  functionerrorString(error){
  	varresultErrorString=error.toString();

  	//Iftheerrorwasn'tasubclassofErrorbutsomethinglike
  	//anobjectliteralwithnameandmessageproperties...
  	if(resultErrorString.substring(0,7)==="[object"){
  		varname=error.name?error.name.toString():"Error";
  		varmessage=error.message?error.message.toString():"";

  		if(name&&message){
  			returnname+":"+message;
  		}elseif(name){
  			returnname;
  		}elseif(message){
  			returnmessage;
  		}else{
  			return"Error";
  		}
  	}else{
  		returnresultErrorString;
  	}
  }

  /*globalmodule,exports,define*/
  functionexportQUnit(QUnit){

  	if(defined.document){

  		//QUnitmaybedefinedwhenitispreconfiguredbutthenonlyQUnitandQUnit.configmaybedefined.
  		if(window$1.QUnit&&window$1.QUnit.version){
  			thrownewError("QUnithasalreadybeendefined.");
  		}

  		window$1.QUnit=QUnit;
  	}

  	//Fornodejs
  	if(typeofmodule!=="undefined"&&module&&module.exports){
  		module.exports=QUnit;

  		//ForconsistencywithCommonJSenvironments'exports
  		module.exports.QUnit=QUnit;
  	}

  	//ForCommonJSwithexports,butwithoutmodule.exports,likeRhino
  	if(typeofexports!=="undefined"&&exports){
  		exports.QUnit=QUnit;
  	}

  	if(typeofdefine==="function"&&define.amd){
  		define(function(){
  			returnQUnit;
  		});
  		QUnit.config.autostart=false;
  	}

  	//ForWeb/ServiceWorkers
  	if(self$1&&self$1.WorkerGlobalScope&&self$1instanceofself$1.WorkerGlobalScope){
  		self$1.QUnit=QUnit;
  	}
  }

  //Handleanunhandledexception.Byconvention,returnstrueiffurther
  //errorhandlingshouldbesuppressedandfalseotherwise.
  //Inthiscase,wewillonlysuppressfurthererrorhandlingifthe
  //"ignoreGlobalErrors"configurationoptionisenabled.
  functiononError(error){
  	for(var_len=arguments.length,args=Array(_len>1?_len-1:0),_key=1;_key<_len;_key++){
  		args[_key-1]=arguments[_key];
  	}

  	if(config.current){
  		if(config.current.ignoreGlobalErrors){
  			returntrue;
  		}
  		pushFailure.apply(undefined,[error.message,error.stacktrace||error.fileName+":"+error.lineNumber].concat(args));
  	}else{
  		test("globalfailure",extend(function(){
  			pushFailure.apply(undefined,[error.message,error.stacktrace||error.fileName+":"+error.lineNumber].concat(args));
  		},{validTest:true}));
  	}

  	returnfalse;
  }

  //Handleanunhandledrejection
  functiononUnhandledRejection(reason){
  	varresultInfo={
  		result:false,
  		message:reason.message||"error",
  		actual:reason,
  		source:reason.stack||sourceFromStacktrace(3)
  	};

  	varcurrentTest=config.current;
  	if(currentTest){
  		currentTest.assert.pushResult(resultInfo);
  	}else{
  		test("globalfailure",extend(function(assert){
  			assert.pushResult(resultInfo);
  		},{validTest:true}));
  	}
  }

  varQUnit={};
  varglobalSuite=newSuiteReport();

  //Theinitial"currentModule"representstheglobal(ortop-level)modulethat
  //isnotexplicitlydefinedbytheuser,thereforeweaddthe"globalSuite"to
  //itsinceeachmodulehasasuiteReportassociatedwithit.
  config.currentModule.suiteReport=globalSuite;

  varglobalStartCalled=false;
  varrunStarted=false;

  //Figureoutifwe'rerunningthetestsfromaserverornot
  QUnit.isLocal=!(defined.document&&window$1.location.protocol!=="file:");

  //ExposethecurrentQUnitversion
  QUnit.version="2.9.1";

  extend(QUnit,{
  	on:on,

  	module:module$1,

  	test:test,

  	todo:todo,

  	skip:skip,

  	only:only,

  	start:functionstart(count){
  		varglobalStartAlreadyCalled=globalStartCalled;

  		if(!config.current){
  			globalStartCalled=true;

  			if(runStarted){
  				thrownewError("Calledstart()whiletestalreadystartedrunning");
  			}elseif(globalStartAlreadyCalled||count>1){
  				thrownewError("Calledstart()outsideofatestcontexttoomanytimes");
  			}elseif(config.autostart){
  				thrownewError("Calledstart()outsideofatestcontextwhen"+"QUnit.config.autostartwastrue");
  			}elseif(!config.pageLoaded){

  				//Thepageisn'tcompletelyloadedyet,sowesetautostartandthen
  				//loadifwe'reinNodeorwaitforthebrowser'sloadevent.
  				config.autostart=true;

  				//StartsfromNodeevenif.loadwasnotpreviouslycalled.Westillreturn
  				//earlyotherwisewe'llwindup"beginning"twice.
  				if(!defined.document){
  					QUnit.load();
  				}

  				return;
  			}
  		}else{
  			thrownewError("QUnit.startcannotbecalledinsideatestcontext.");
  		}

  		scheduleBegin();
  	},

  	config:config,

  	is:is,

  	objectType:objectType,

  	extend:extend,

  	load:functionload(){
  		config.pageLoaded=true;

  		//Initializetheconfigurationoptions
  		extend(config,{
  			stats:{all:0,bad:0},
  			started:0,
  			updateRate:1000,
  			autostart:true,
  			filter:""
  		},true);

  		if(!runStarted){
  			config.blocking=false;

  			if(config.autostart){
  				scheduleBegin();
  			}
  		}
  	},

  	stack:functionstack(offset){
  		offset=(offset||0)+2;
  		returnsourceFromStacktrace(offset);
  	},

  	onError:onError,

  	onUnhandledRejection:onUnhandledRejection
  });

  QUnit.pushFailure=pushFailure;
  QUnit.assert=Assert.prototype;
  QUnit.equiv=equiv;
  QUnit.dump=dump;

  registerLoggingCallbacks(QUnit);

  functionscheduleBegin(){

  	runStarted=true;

  	//Addaslightdelaytoallowdefinitionofmoremodulesandtests.
  	if(defined.setTimeout){
  		setTimeout$1(function(){
  			begin();
  		});
  	}else{
  		begin();
  	}
  }

  functionunblockAndAdvanceQueue(){
  	config.blocking=false;
  	ProcessingQueue.advance();
  }

  functionbegin(){
  	vari,
  	   l,
  	   modulesLog=[];

  	//Ifthetestrunhasn'tofficiallybegunyet
  	if(!config.started){

  		//Recordthetimeofthetestrun'sbeginning
  		config.started=now();

  		//Deletethelooseunnamedmoduleifunused.
  		if(config.modules[0].name===""&&config.modules[0].tests.length===0){
  			config.modules.shift();
  		}

  		//Avoidunnecessaryinformationbynotloggingmodules'testenvironments
  		for(i=0,l=config.modules.length;i<l;i++){
  			modulesLog.push({
  				name:config.modules[i].name,
  				tests:config.modules[i].tests
  			});
  		}

  		//Thetestrunisofficiallybeginningnow
  		emit("runStart",globalSuite.start(true));
  		runLoggingCallbacks("begin",{
  			totalTests:Test.count,
  			modules:modulesLog
  		}).then(unblockAndAdvanceQueue);
  	}else{
  		unblockAndAdvanceQueue();
  	}
  }

  exportQUnit(QUnit);

  (function(){

  	if(typeofwindow$1==="undefined"||typeofdocument$1==="undefined"){
  		return;
  	}

  	varconfig=QUnit.config,
  	   hasOwn=Object.prototype.hasOwnProperty;

  	//StoresfixtureHTMLforresettinglater
  	functionstoreFixture(){

  		//Avoidoverwritinguser-definedvalues
  		if(hasOwn.call(config,"fixture")){
  			return;
  		}

  		varfixture=document$1.getElementById("qunit-fixture");
  		if(fixture){
  			config.fixture=fixture.cloneNode(true);
  		}
  	}

  	QUnit.begin(storeFixture);

  	//ResetsthefixtureDOMelementifavailable.
  	functionresetFixture(){
  		if(config.fixture==null){
  			return;
  		}

  		varfixture=document$1.getElementById("qunit-fixture");
  		varresetFixtureType=_typeof(config.fixture);
  		if(resetFixtureType==="string"){

  			//supportuserdefinedvaluesfor`config.fixture`
  			varnewFixture=document$1.createElement("div");
  			newFixture.setAttribute("id","qunit-fixture");
  			newFixture.innerHTML=config.fixture;
  			fixture.parentNode.replaceChild(newFixture,fixture);
  		}else{
  			varclonedFixture=config.fixture.cloneNode(true);
  			fixture.parentNode.replaceChild(clonedFixture,fixture);
  		}
  	}

  	QUnit.testStart(resetFixture);
  })();

  (function(){

  	//OnlyinteractwithURLsviawindow.location
  	varlocation=typeofwindow$1!=="undefined"&&window$1.location;
  	if(!location){
  		return;
  	}

  	varurlParams=getUrlParams();

  	QUnit.urlParams=urlParams;

  	//Matchmodule/testbyinclusioninanarray
  	QUnit.config.moduleId=[].concat(urlParams.moduleId||[]);
  	QUnit.config.testId=[].concat(urlParams.testId||[]);

  	//Exactcase-insensitivematchofthemodulename
  	QUnit.config.module=urlParams.module;

  	//Regularexpressionorcase-insenstivesubstringmatchagainst"moduleName:testName"
  	QUnit.config.filter=urlParams.filter;

  	//Testorderrandomization
  	if(urlParams.seed===true){

  		//Generatearandomseediftheoptionisspecifiedwithoutavalue
  		QUnit.config.seed=Math.random().toString(36).slice(2);
  	}elseif(urlParams.seed){
  		QUnit.config.seed=urlParams.seed;
  	}

  	//AddURL-parameter-mappedconfigvalueswithUIformrenderingdata
  	QUnit.config.urlConfig.push({
  		id:"hidepassed",
  		label:"Hidepassedtests",
  		tooltip:"Onlyshowtestsandassertionsthatfail.Storedasquery-strings."
  	},{
  		id:"noglobals",
  		label:"CheckforGlobals",
  		tooltip:"Enablingthiswilltestifanytestintroducesnewpropertiesonthe"+"globalobject(`window`inBrowsers).Storedasquery-strings."
  	},{
  		id:"notrycatch",
  		label:"Notry-catch",
  		tooltip:"Enablingthiswillruntestsoutsideofatry-catchblock.Makesdebugging"+"exceptionsinIEreasonable.Storedasquery-strings."
  	});

  	QUnit.begin(function(){
  		vari,
  		   option,
  		   urlConfig=QUnit.config.urlConfig;

  		for(i=0;i<urlConfig.length;i++){

  			//Optionscanbeeitherstringsorobjectswithnonempty"id"properties
  			option=QUnit.config.urlConfig[i];
  			if(typeofoption!=="string"){
  				option=option.id;
  			}

  			if(QUnit.config[option]===undefined){
  				QUnit.config[option]=urlParams[option];
  			}
  		}
  	});

  	functiongetUrlParams(){
  		vari,param,name,value;
  		varurlParams=Object.create(null);
  		varparams=location.search.slice(1).split("&");
  		varlength=params.length;

  		for(i=0;i<length;i++){
  			if(params[i]){
  				param=params[i].split("=");
  				name=decodeQueryParam(param[0]);

  				//Allowjustakeytoturnonaflag,e.g.,test.html?noglobals
  				value=param.length===1||decodeQueryParam(param.slice(1).join("="));
  				if(nameinurlParams){
  					urlParams[name]=[].concat(urlParams[name],value);
  				}else{
  					urlParams[name]=value;
  				}
  			}
  		}

  		returnurlParams;
  	}

  	functiondecodeQueryParam(param){
  		returndecodeURIComponent(param.replace(/\+/g,"%20"));
  	}
  })();

  varstats={
  	passedTests:0,
  	failedTests:0,
  	skippedTests:0,
  	todoTests:0
  };

  //Escapetextforattributeortextcontent.
  functionescapeText(s){
  	if(!s){
  		return"";
  	}
  	s=s+"";

  	//Bothsinglequotesanddoublequotes(forattributes)
  	returns.replace(/['"<>&]/g,function(s){
  		switch(s){
  			case"'":
  				return"&#039;";
  			case"\"":
  				return"&quot;";
  			case"<":
  				return"&lt;";
  			case">":
  				return"&gt;";
  			case"&":
  				return"&amp;";
  		}
  	});
  }

  (function(){

  	//Don'tloadtheHTMLReporteronnon-browserenvironments
  	if(typeofwindow$1==="undefined"||!window$1.document){
  		return;
  	}

  	varconfig=QUnit.config,
  	   hiddenTests=[],
  	   document=window$1.document,
  	   collapseNext=false,
  	   hasOwn=Object.prototype.hasOwnProperty,
  	   unfilteredUrl=setUrl({filter:undefined,module:undefined,
  		moduleId:undefined,testId:undefined}),
  	   modulesList=[];

  	functionaddEvent(elem,type,fn){
  		elem.addEventListener(type,fn,false);
  	}

  	functionremoveEvent(elem,type,fn){
  		elem.removeEventListener(type,fn,false);
  	}

  	functionaddEvents(elems,type,fn){
  		vari=elems.length;
  		while(i--){
  			addEvent(elems[i],type,fn);
  		}
  	}

  	functionhasClass(elem,name){
  		return(""+elem.className+"").indexOf(""+name+"")>=0;
  	}

  	functionaddClass(elem,name){
  		if(!hasClass(elem,name)){
  			elem.className+=(elem.className?"":"")+name;
  		}
  	}

  	functiontoggleClass(elem,name,force){
  		if(force||typeofforce==="undefined"&&!hasClass(elem,name)){
  			addClass(elem,name);
  		}else{
  			removeClass(elem,name);
  		}
  	}

  	functionremoveClass(elem,name){
  		varset=""+elem.className+"";

  		//Classnamemayappearmultipletimes
  		while(set.indexOf(""+name+"")>=0){
  			set=set.replace(""+name+"","");
  		}

  		//Trimforprettiness
  		elem.className=typeofset.trim==="function"?set.trim():set.replace(/^\s+|\s+$/g,"");
  	}

  	functionid(name){
  		returndocument.getElementById&&document.getElementById(name);
  	}

  	functionabortTests(){
  		varabortButton=id("qunit-abort-tests-button");
  		if(abortButton){
  			abortButton.disabled=true;
  			abortButton.innerHTML="Aborting...";
  		}
  		QUnit.config.queue.length=0;
  		returnfalse;
  	}

  	functioninterceptNavigation(ev){
  		applyUrlParams();

  		if(ev&&ev.preventDefault){
  			ev.preventDefault();
  		}

  		returnfalse;
  	}

  	functiongetUrlConfigHtml(){
  		vari,
  		   j,
  		   val,
  		   escaped,
  		   escapedTooltip,
  		   selection=false,
  		   urlConfig=config.urlConfig,
  		   urlConfigHtml="";

  		for(i=0;i<urlConfig.length;i++){

  			//Optionscanbeeitherstringsorobjectswithnonempty"id"properties
  			val=config.urlConfig[i];
  			if(typeofval==="string"){
  				val={
  					id:val,
  					label:val
  				};
  			}

  			escaped=escapeText(val.id);
  			escapedTooltip=escapeText(val.tooltip);

  			if(!val.value||typeofval.value==="string"){
  				urlConfigHtml+="<labelfor='qunit-urlconfig-"+escaped+"'title='"+escapedTooltip+"'><inputid='qunit-urlconfig-"+escaped+"'name='"+escaped+"'type='checkbox'"+(val.value?"value='"+escapeText(val.value)+"'":"")+(config[val.id]?"checked='checked'":"")+"title='"+escapedTooltip+"'/>"+escapeText(val.label)+"</label>";
  			}else{
  				urlConfigHtml+="<labelfor='qunit-urlconfig-"+escaped+"'title='"+escapedTooltip+"'>"+val.label+":</label><selectid='qunit-urlconfig-"+escaped+"'name='"+escaped+"'title='"+escapedTooltip+"'><option></option>";

  				if(QUnit.is("array",val.value)){
  					for(j=0;j<val.value.length;j++){
  						escaped=escapeText(val.value[j]);
  						urlConfigHtml+="<optionvalue='"+escaped+"'"+(config[val.id]===val.value[j]?(selection=true)&&"selected='selected'":"")+">"+escaped+"</option>";
  					}
  				}else{
  					for(jinval.value){
  						if(hasOwn.call(val.value,j)){
  							urlConfigHtml+="<optionvalue='"+escapeText(j)+"'"+(config[val.id]===j?(selection=true)&&"selected='selected'":"")+">"+escapeText(val.value[j])+"</option>";
  						}
  					}
  				}
  				if(config[val.id]&&!selection){
  					escaped=escapeText(config[val.id]);
  					urlConfigHtml+="<optionvalue='"+escaped+"'selected='selected'disabled='disabled'>"+escaped+"</option>";
  				}
  				urlConfigHtml+="</select>";
  			}
  		}

  		returnurlConfigHtml;
  	}

  	//Handle"click"eventsontoolbarcheckboxesand"change"forselectmenus.
  	//UpdatestheURLwiththenewstateof`config.urlConfig`values.
  	functiontoolbarChanged(){
  		varupdatedUrl,
  		   value,
  		   tests,
  		   field=this,
  		   params={};

  		//Detectiffieldisaselectmenuoracheckbox
  		if("selectedIndex"infield){
  			value=field.options[field.selectedIndex].value||undefined;
  		}else{
  			value=field.checked?field.defaultValue||true:undefined;
  		}

  		params[field.name]=value;
  		updatedUrl=setUrl(params);

  		//Checkifwecanapplythechangewithoutapagerefresh
  		if("hidepassed"===field.name&&"replaceState"inwindow$1.history){
  			QUnit.urlParams[field.name]=value;
  			config[field.name]=value||false;
  			tests=id("qunit-tests");
  			if(tests){
  				varlength=tests.children.length;
  				varchildren=tests.children;

  				if(field.checked){
  					for(vari=0;i<length;i++){
  						vartest=children[i];

  						if(test&&test.className.indexOf("pass")>-1){
  							hiddenTests.push(test);
  						}
  					}

  					var_iteratorNormalCompletion=true;
  					var_didIteratorError=false;
  					var_iteratorError=undefined;

  					try{
  						for(var_iterator=hiddenTests[Symbol.iterator](),_step;!(_iteratorNormalCompletion=(_step=_iterator.next()).done);_iteratorNormalCompletion=true){
  							varhiddenTest=_step.value;

  							tests.removeChild(hiddenTest);
  						}
  					}catch(err){
  						_didIteratorError=true;
  						_iteratorError=err;
  					}finally{
  						try{
  							if(!_iteratorNormalCompletion&&_iterator.return){
  								_iterator.return();
  							}
  						}finally{
  							if(_didIteratorError){
  								throw_iteratorError;
  							}
  						}
  					}
  				}else{
  					while((test=hiddenTests.pop())!=null){
  						tests.appendChild(test);
  					}
  				}
  			}
  			window$1.history.replaceState(null,"",updatedUrl);
  		}else{
  			window$1.location=updatedUrl;
  		}
  	}

  	functionsetUrl(params){
  		varkey,
  		   arrValue,
  		   i,
  		   querystring="?",
  		   location=window$1.location;

  		params=QUnit.extend(QUnit.extend({},QUnit.urlParams),params);

  		for(keyinparams){

  			//Skipinheritedorundefinedproperties
  			if(hasOwn.call(params,key)&&params[key]!==undefined){

  				//Outputaparameterforeachvalueofthiskey
  				//(butusuallyjustone)
  				arrValue=[].concat(params[key]);
  				for(i=0;i<arrValue.length;i++){
  					querystring+=encodeURIComponent(key);
  					if(arrValue[i]!==true){
  						querystring+="="+encodeURIComponent(arrValue[i]);
  					}
  					querystring+="&";
  				}
  			}
  		}
  		returnlocation.protocol+"//"+location.host+location.pathname+querystring.slice(0,-1);
  	}

  	functionapplyUrlParams(){
  		vari,
  		   selectedModules=[],
  		   modulesList=id("qunit-modulefilter-dropdown-list").getElementsByTagName("input"),
  		   filter=id("qunit-filter-input").value;

  		for(i=0;i<modulesList.length;i++){
  			if(modulesList[i].checked){
  				selectedModules.push(modulesList[i].value);
  			}
  		}

  		window$1.location=setUrl({
  			filter:filter===""?undefined:filter,
  			moduleId:selectedModules.length===0?undefined:selectedModules,

  			//RemovemoduleandtestIdfilter
  			module:undefined,
  			testId:undefined
  		});
  	}

  	functiontoolbarUrlConfigContainer(){
  		varurlConfigContainer=document.createElement("span");

  		urlConfigContainer.innerHTML=getUrlConfigHtml();
  		addClass(urlConfigContainer,"qunit-url-config");

  		addEvents(urlConfigContainer.getElementsByTagName("input"),"change",toolbarChanged);
  		addEvents(urlConfigContainer.getElementsByTagName("select"),"change",toolbarChanged);

  		returnurlConfigContainer;
  	}

  	functionabortTestsButton(){
  		varbutton=document.createElement("button");
  		button.id="qunit-abort-tests-button";
  		button.innerHTML="Abort";
  		addEvent(button,"click",abortTests);
  		returnbutton;
  	}

  	functiontoolbarLooseFilter(){
  		varfilter=document.createElement("form"),
  		   label=document.createElement("label"),
  		   input=document.createElement("input"),
  		   button=document.createElement("button");

  		addClass(filter,"qunit-filter");

  		label.innerHTML="Filter:";

  		input.type="text";
  		input.value=config.filter||"";
  		input.name="filter";
  		input.id="qunit-filter-input";

  		button.innerHTML="Go";

  		label.appendChild(input);

  		filter.appendChild(label);
  		filter.appendChild(document.createTextNode(""));
  		filter.appendChild(button);
  		addEvent(filter,"submit",interceptNavigation);

  		returnfilter;
  	}

  	functionmoduleListHtml(){
  		vari,
  		   checked,
  		   html="";

  		for(i=0;i<config.modules.length;i++){
  			if(config.modules[i].name!==""){
  				checked=config.moduleId.indexOf(config.modules[i].moduleId)>-1;
  				html+="<li><labelclass='clickable"+(checked?"checked":"")+"'><inputtype='checkbox'"+"value='"+config.modules[i].moduleId+"'"+(checked?"checked='checked'":"")+"/>"+escapeText(config.modules[i].name)+"</label></li>";
  			}
  		}

  		returnhtml;
  	}

  	functiontoolbarModuleFilter(){
  		varallCheckbox,
  		   commit,
  		   reset,
  		   moduleFilter=document.createElement("form"),
  		   label=document.createElement("label"),
  		   moduleSearch=document.createElement("input"),
  		   dropDown=document.createElement("div"),
  		   actions=document.createElement("span"),
  		   dropDownList=document.createElement("ul"),
  		   dirty=false;

  		moduleSearch.id="qunit-modulefilter-search";
  		moduleSearch.autocomplete="off";
  		addEvent(moduleSearch,"input",searchInput);
  		addEvent(moduleSearch,"input",searchFocus);
  		addEvent(moduleSearch,"focus",searchFocus);
  		addEvent(moduleSearch,"click",searchFocus);

  		label.id="qunit-modulefilter-search-container";
  		label.innerHTML="Module:";
  		label.appendChild(moduleSearch);

  		actions.id="qunit-modulefilter-actions";
  		actions.innerHTML="<buttonstyle='display:none'>Apply</button>"+"<buttontype='reset'style='display:none'>Reset</button>"+"<labelclass='clickable"+(config.moduleId.length?"":"checked")+"'><inputtype='checkbox'"+(config.moduleId.length?"":"checked='checked'")+"/>Allmodules</label>";
  		allCheckbox=actions.lastChild.firstChild;
  		commit=actions.firstChild;
  		reset=commit.nextSibling;
  		addEvent(commit,"click",applyUrlParams);

  		dropDownList.id="qunit-modulefilter-dropdown-list";
  		dropDownList.innerHTML=moduleListHtml();

  		dropDown.id="qunit-modulefilter-dropdown";
  		dropDown.style.display="none";
  		dropDown.appendChild(actions);
  		dropDown.appendChild(dropDownList);
  		addEvent(dropDown,"change",selectionChange);
  		selectionChange();

  		moduleFilter.id="qunit-modulefilter";
  		moduleFilter.appendChild(label);
  		moduleFilter.appendChild(dropDown);
  		addEvent(moduleFilter,"submit",interceptNavigation);
  		addEvent(moduleFilter,"reset",function(){

  			//Lettheresethappen,thenupdatestyles
  			window$1.setTimeout(selectionChange);
  		});

  		//Enablesshow/hideforthedropdown
  		functionsearchFocus(){
  			if(dropDown.style.display!=="none"){
  				return;
  			}

  			dropDown.style.display="block";
  			addEvent(document,"click",hideHandler);
  			addEvent(document,"keydown",hideHandler);

  			//HideonEscapekeydownoroutside-containerclick
  			functionhideHandler(e){
  				varinContainer=moduleFilter.contains(e.target);

  				if(e.keyCode===27||!inContainer){
  					if(e.keyCode===27&&inContainer){
  						moduleSearch.focus();
  					}
  					dropDown.style.display="none";
  					removeEvent(document,"click",hideHandler);
  					removeEvent(document,"keydown",hideHandler);
  					moduleSearch.value="";
  					searchInput();
  				}
  			}
  		}

  		//Processesmodulesearchboxinput
  		functionsearchInput(){
  			vari,
  			   item,
  			   searchText=moduleSearch.value.toLowerCase(),
  			   listItems=dropDownList.children;

  			for(i=0;i<listItems.length;i++){
  				item=listItems[i];
  				if(!searchText||item.textContent.toLowerCase().indexOf(searchText)>-1){
  					item.style.display="";
  				}else{
  					item.style.display="none";
  				}
  			}
  		}

  		//Processesselectionchanges
  		functionselectionChange(evt){
  			vari,
  			   item,
  			   checkbox=evt&&evt.target||allCheckbox,
  			   modulesList=dropDownList.getElementsByTagName("input"),
  			   selectedNames=[];

  			toggleClass(checkbox.parentNode,"checked",checkbox.checked);

  			dirty=false;
  			if(checkbox.checked&&checkbox!==allCheckbox){
  				allCheckbox.checked=false;
  				removeClass(allCheckbox.parentNode,"checked");
  			}
  			for(i=0;i<modulesList.length;i++){
  				item=modulesList[i];
  				if(!evt){
  					toggleClass(item.parentNode,"checked",item.checked);
  				}elseif(checkbox===allCheckbox&&checkbox.checked){
  					item.checked=false;
  					removeClass(item.parentNode,"checked");
  				}
  				dirty=dirty||item.checked!==item.defaultChecked;
  				if(item.checked){
  					selectedNames.push(item.parentNode.textContent);
  				}
  			}

  			commit.style.display=reset.style.display=dirty?"":"none";
  			moduleSearch.placeholder=selectedNames.join(",")||allCheckbox.parentNode.textContent;
  			moduleSearch.title="Typetofilterlist.Currentselection:\n"+(selectedNames.join("\n")||allCheckbox.parentNode.textContent);
  		}

  		returnmoduleFilter;
  	}

  	functionappendToolbar(){
  		vartoolbar=id("qunit-testrunner-toolbar");

  		if(toolbar){
  			toolbar.appendChild(toolbarUrlConfigContainer());
  			toolbar.appendChild(toolbarModuleFilter());
  			toolbar.appendChild(toolbarLooseFilter());
  			toolbar.appendChild(document.createElement("div")).className="clearfix";
  		}
  	}

  	functionappendHeader(){
  		varheader=id("qunit-header");

  		if(header){
  			header.innerHTML="<ahref='"+escapeText(unfilteredUrl)+"'>"+header.innerHTML+"</a>";
  		}
  	}

  	functionappendBanner(){
  		varbanner=id("qunit-banner");

  		if(banner){
  			banner.className="";
  		}
  	}

  	functionappendTestResults(){
  		vartests=id("qunit-tests"),
  		   result=id("qunit-testresult"),
  		   controls;

  		if(result){
  			result.parentNode.removeChild(result);
  		}

  		if(tests){
  			tests.innerHTML="";
  			result=document.createElement("p");
  			result.id="qunit-testresult";
  			result.className="result";
  			tests.parentNode.insertBefore(result,tests);
  			result.innerHTML="<divid=\"qunit-testresult-display\">Running...<br/>&#160;</div>"+"<divid=\"qunit-testresult-controls\"></div>"+"<divclass=\"clearfix\"></div>";
  			controls=id("qunit-testresult-controls");
  		}

  		if(controls){
  			controls.appendChild(abortTestsButton());
  		}
  	}

  	functionappendFilteredTest(){
  		vartestId=QUnit.config.testId;
  		if(!testId||testId.length<=0){
  			return"";
  		}
  		return"<divid='qunit-filteredTest'>Rerunningselectedtests:"+escapeText(testId.join(","))+"<aid='qunit-clearFilter'href='"+escapeText(unfilteredUrl)+"'>Runalltests</a></div>";
  	}

  	functionappendUserAgent(){
  		varuserAgent=id("qunit-userAgent");

  		if(userAgent){
  			userAgent.innerHTML="";
  			userAgent.appendChild(document.createTextNode("QUnit"+QUnit.version+";"+navigator.userAgent));
  		}
  	}

  	functionappendInterface(){
  		varqunit=id("qunit");

  		if(qunit){
  			qunit.innerHTML="<h1id='qunit-header'>"+escapeText(document.title)+"</h1>"+"<h2id='qunit-banner'></h2>"+"<divid='qunit-testrunner-toolbar'></div>"+appendFilteredTest()+"<h2id='qunit-userAgent'></h2>"+"<olid='qunit-tests'></ol>";
  		}

  		appendHeader();
  		appendBanner();
  		appendTestResults();
  		appendUserAgent();
  		appendToolbar();
  	}

  	functionappendTest(name,testId,moduleName){
  		vartitle,
  		   rerunTrigger,
  		   testBlock,
  		   assertList,
  		   tests=id("qunit-tests");

  		if(!tests){
  			return;
  		}

  		title=document.createElement("strong");
  		title.innerHTML=getNameHtml(name,moduleName);

  		rerunTrigger=document.createElement("a");
  		rerunTrigger.innerHTML="Rerun";
  		rerunTrigger.href=setUrl({testId:testId});

  		testBlock=document.createElement("li");
  		testBlock.appendChild(title);
  		testBlock.appendChild(rerunTrigger);
  		testBlock.id="qunit-test-output-"+testId;

  		assertList=document.createElement("ol");
  		assertList.className="qunit-assert-list";

  		testBlock.appendChild(assertList);

  		tests.appendChild(testBlock);
  	}

  	//HTMLReporterinitializationandload
  	QUnit.begin(function(details){
  		vari,moduleObj;

  		//Sortmodulesbynameforthepicker
  		for(i=0;i<details.modules.length;i++){
  			moduleObj=details.modules[i];
  			if(moduleObj.name){
  				modulesList.push(moduleObj.name);
  			}
  		}
  		modulesList.sort(function(a,b){
  			returna.localeCompare(b);
  		});

  		//InitializeQUnitelements
  		appendInterface();
  	});

  	QUnit.done(function(details){
  		varbanner=id("qunit-banner"),
  		   tests=id("qunit-tests"),
  		   abortButton=id("qunit-abort-tests-button"),
  		   totalTests=stats.passedTests+stats.skippedTests+stats.todoTests+stats.failedTests,
  		   html=[totalTests,"testscompletedin",details.runtime,"milliseconds,with",stats.failedTests,"failed,",stats.skippedTests,"skipped,and",stats.todoTests,"todo.<br/>","<spanclass='passed'>",details.passed,"</span>assertionsof<spanclass='total'>",details.total,"</span>passed,<spanclass='failed'>",details.failed,"</span>failed."].join(""),
  		   test,
  		   assertLi,
  		   assertList;

  		//Updateremaingteststoaborted
  		if(abortButton&&abortButton.disabled){
  			html="Testsabortedafter"+details.runtime+"milliseconds.";

  			for(vari=0;i<tests.children.length;i++){
  				test=tests.children[i];
  				if(test.className===""||test.className==="running"){
  					test.className="aborted";
  					assertList=test.getElementsByTagName("ol")[0];
  					assertLi=document.createElement("li");
  					assertLi.className="fail";
  					assertLi.innerHTML="Testaborted.";
  					assertList.appendChild(assertLi);
  				}
  			}
  		}

  		if(banner&&(!abortButton||abortButton.disabled===false)){
  			banner.className=stats.failedTests?"qunit-fail":"qunit-pass";
  		}

  		if(abortButton){
  			abortButton.parentNode.removeChild(abortButton);
  		}

  		if(tests){
  			id("qunit-testresult-display").innerHTML=html;
  		}

  		if(config.altertitle&&document.title){

  			//Show✖forgood,✔forbadsuiteresultintitle
  			//useescapesequencesincasefilegetsloadedwithnon-utf-8
  			//charset
  			document.title=[stats.failedTests?"\u2716":"\u2714",document.title.replace(/^[\u2714\u2716]/i,"")].join("");
  		}

  		//Scrollbacktotoptoshowresults
  		if(config.scrolltop&&window$1.scrollTo){
  			window$1.scrollTo(0,0);
  		}
  	});

  	functiongetNameHtml(name,module){
  		varnameHtml="";

  		if(module){
  			nameHtml="<spanclass='module-name'>"+escapeText(module)+"</span>:";
  		}

  		nameHtml+="<spanclass='test-name'>"+escapeText(name)+"</span>";

  		returnnameHtml;
  	}

  	QUnit.testStart(function(details){
  		varrunning,bad;

  		appendTest(details.name,details.testId,details.module);

  		running=id("qunit-testresult-display");

  		if(running){
  			addClass(running,"running");

  			bad=QUnit.config.reorder&&details.previousFailure;

  			running.innerHTML=[bad?"Rerunningpreviouslyfailedtest:<br/>":"Running:<br/>",getNameHtml(details.name,details.module)].join("");
  		}
  	});

  	functionstripHtml(string){

  		//Striptags,htmlentityandwhitespaces
  		returnstring.replace(/<\/?[^>]+(>|$)/g,"").replace(/&quot;/g,"").replace(/\s+/g,"");
  	}

  	QUnit.log(function(details){
  		varassertList,
  		   assertLi,
  		   message,
  		   expected,
  		   actual,
  		   diff,
  		   showDiff=false,
  		   testItem=id("qunit-test-output-"+details.testId);

  		if(!testItem){
  			return;
  		}

  		message=escapeText(details.message)||(details.result?"okay":"failed");
  		message="<spanclass='test-message'>"+message+"</span>";
  		message+="<spanclass='runtime'>@"+details.runtime+"ms</span>";

  		//ThepushFailuredoesn'tprovidedetails.expected
  		//whenitcalls,it'simplicittoalsonotshowexpectedanddiffstuff
  		//Also,weneedtocheckdetails.expectedexistence,asitcanexistandbeundefined
  		if(!details.result&&hasOwn.call(details,"expected")){
  			if(details.negative){
  				expected="NOT"+QUnit.dump.parse(details.expected);
  			}else{
  				expected=QUnit.dump.parse(details.expected);
  			}

  			actual=QUnit.dump.parse(details.actual);
  			message+="<table><trclass='test-expected'><th>Expected:</th><td><pre>"+escapeText(expected)+"</pre></td></tr>";

  			if(actual!==expected){

  				message+="<trclass='test-actual'><th>Result:</th><td><pre>"+escapeText(actual)+"</pre></td></tr>";

  				if(typeofdetails.actual==="number"&&typeofdetails.expected==="number"){
  					if(!isNaN(details.actual)&&!isNaN(details.expected)){
  						showDiff=true;
  						diff=details.actual-details.expected;
  						diff=(diff>0?"+":"")+diff;
  					}
  				}elseif(typeofdetails.actual!=="boolean"&&typeofdetails.expected!=="boolean"){
  					diff=QUnit.diff(expected,actual);

  					//don'tshowdiffifthereiszerooverlap
  					showDiff=stripHtml(diff).length!==stripHtml(expected).length+stripHtml(actual).length;
  				}

  				if(showDiff){
  					message+="<trclass='test-diff'><th>Diff:</th><td><pre>"+diff+"</pre></td></tr>";
  				}
  			}elseif(expected.indexOf("[objectArray]")!==-1||expected.indexOf("[objectObject]")!==-1){
  				message+="<trclass='test-message'><th>Message:</th><td>"+"Diffsuppressedasthedepthofobjectismorethancurrentmaxdepth("+QUnit.config.maxDepth+").<p>Hint:Use<code>QUnit.dump.maxDepth</code>to"+"runwithahighermaxdepthor<ahref='"+escapeText(setUrl({maxDepth:-1}))+"'>"+"Rerun</a>withoutmaxdepth.</p></td></tr>";
  			}else{
  				message+="<trclass='test-message'><th>Message:</th><td>"+"Diffsuppressedastheexpectedandactualresultshaveanequivalent"+"serialization</td></tr>";
  			}

  			if(details.source){
  				message+="<trclass='test-source'><th>Source:</th><td><pre>"+escapeText(details.source)+"</pre></td></tr>";
  			}

  			message+="</table>";

  			//ThisoccurswhenpushFailureissetandwehaveanextractedstacktrace
  		}elseif(!details.result&&details.source){
  			message+="<table>"+"<trclass='test-source'><th>Source:</th><td><pre>"+escapeText(details.source)+"</pre></td></tr>"+"</table>";
  		}

  		assertList=testItem.getElementsByTagName("ol")[0];

  		assertLi=document.createElement("li");
  		assertLi.className=details.result?"pass":"fail";
  		assertLi.innerHTML=message;
  		assertList.appendChild(assertLi);
  	});

  	QUnit.testDone(function(details){
  		vartestTitle,
  		   time,
  		   testItem,
  		   assertList,
  		   status,
  		   good,
  		   bad,
  		   testCounts,
  		   skipped,
  		   sourceName,
  		   tests=id("qunit-tests");

  		if(!tests){
  			return;
  		}

  		testItem=id("qunit-test-output-"+details.testId);

  		removeClass(testItem,"running");

  		if(details.failed>0){
  			status="failed";
  		}elseif(details.todo){
  			status="todo";
  		}else{
  			status=details.skipped?"skipped":"passed";
  		}

  		assertList=testItem.getElementsByTagName("ol")[0];

  		good=details.passed;
  		bad=details.failed;

  		//Thistestpassedifithasnounexpectedfailedassertions
  		vartestPassed=details.failed>0?details.todo:!details.todo;

  		if(testPassed){

  			//Collapsethepassingtests
  			addClass(assertList,"qunit-collapsed");
  		}elseif(config.collapse){
  			if(!collapseNext){

  				//Skipcollapsingthefirstfailingtest
  				collapseNext=true;
  			}else{

  				//Collapseremainingtests
  				addClass(assertList,"qunit-collapsed");
  			}
  		}

  		//ThetestItem.firstChildisthetestname
  		testTitle=testItem.firstChild;

  		testCounts=bad?"<bclass='failed'>"+bad+"</b>,"+"<bclass='passed'>"+good+"</b>,":"";

  		testTitle.innerHTML+="<bclass='counts'>("+testCounts+details.assertions.length+")</b>";

  		if(details.skipped){
  			stats.skippedTests++;

  			testItem.className="skipped";
  			skipped=document.createElement("em");
  			skipped.className="qunit-skipped-label";
  			skipped.innerHTML="skipped";
  			testItem.insertBefore(skipped,testTitle);
  		}else{
  			addEvent(testTitle,"click",function(){
  				toggleClass(assertList,"qunit-collapsed");
  			});

  			testItem.className=testPassed?"pass":"fail";

  			if(details.todo){
  				vartodoLabel=document.createElement("em");
  				todoLabel.className="qunit-todo-label";
  				todoLabel.innerHTML="todo";
  				testItem.className+="todo";
  				testItem.insertBefore(todoLabel,testTitle);
  			}

  			time=document.createElement("span");
  			time.className="runtime";
  			time.innerHTML=details.runtime+"ms";
  			testItem.insertBefore(time,assertList);

  			if(!testPassed){
  				stats.failedTests++;
  			}elseif(details.todo){
  				stats.todoTests++;
  			}else{
  				stats.passedTests++;
  			}
  		}

  		//Showthesourceofthetestwhenshowingassertions
  		if(details.source){
  			sourceName=document.createElement("p");
  			sourceName.innerHTML="<strong>Source:</strong>"+escapeText(details.source);
  			addClass(sourceName,"qunit-source");
  			if(testPassed){
  				addClass(sourceName,"qunit-collapsed");
  			}
  			addEvent(testTitle,"click",function(){
  				toggleClass(sourceName,"qunit-collapsed");
  			});
  			testItem.appendChild(sourceName);
  		}

  		if(config.hidepassed&&status==="passed"){

  			//useremoveChildinsteadofremovebecauseofsupport
  			hiddenTests.push(testItem);

  			tests.removeChild(testItem);
  		}
  	});

  	//AvoidreadyStateissuewithphantomjs
  	//Ref:#818
  	varnotPhantom=function(p){
  		return!(p&&p.version&&p.version.major>0);
  	}(window$1.phantom);

  	if(notPhantom&&document.readyState==="complete"){
  		QUnit.load();
  	}else{
  		addEvent(window$1,"load",QUnit.load);
  	}

  	//Wrapwindow.onerror.Wewillcalltheoriginalwindow.onerrortoseeif
  	//theexistinghandlerfullyhandlestheerror;ifnot,wewillcallthe
  	//QUnit.onErrorfunction.
  	varoriginalWindowOnError=window$1.onerror;

  	//Coveruncaughtexceptions
  	//Returningtruewillsuppressthedefaultbrowserhandler,
  	//returningfalsewillletitrun.
  	window$1.onerror=function(message,fileName,lineNumber,columnNumber,errorObj){
  		varret=false;
  		if(originalWindowOnError){
  			for(var_len=arguments.length,args=Array(_len>5?_len-5:0),_key=5;_key<_len;_key++){
  				args[_key-5]=arguments[_key];
  			}

  			ret=originalWindowOnError.call.apply(originalWindowOnError,[this,message,fileName,lineNumber,columnNumber,errorObj].concat(args));
  		}

  		//Treatreturnvalueaswindow.onerroritselfdoes,
  		//Onlydoourhandlingifnotsuppressed.
  		if(ret!==true){
  			varerror={
  				message:message,
  				fileName:fileName,
  				lineNumber:lineNumber
  			};

  			//Accordingto
  			//https://blog.sentry.io/2016/01/04/client-javascript-reporting-window-onerror,
  			//mostmodernbrowserssupportanerrorObjargument;usethatto
  			//getafullstacktraceifit'savailable.
  			if(errorObj&&errorObj.stack){
  				error.stacktrace=extractStacktrace(errorObj,0);
  			}

  			ret=QUnit.onError(error);
  		}

  		returnret;
  	};

  	//Listenforunhandledrejections,andcallQUnit.onUnhandledRejection
  	window$1.addEventListener("unhandledrejection",function(event){
  		QUnit.onUnhandledRejection(event.reason);
  	});
  })();

  /*
   *Thisfileisamodifiedversionofgoogle-diff-match-patch'sJavaScriptimplementation
   *(https://code.google.com/p/google-diff-match-patch/source/browse/trunk/javascript/diff_match_patch_uncompressed.js),
   *modificationsarelicensedasmorefullysetforthinLICENSE.txt.
   *
   *Theoriginalsourceofgoogle-diff-match-patchisattributableandlicensedasfollows:
   *
   *Copyright2006GoogleInc.
   *https://code.google.com/p/google-diff-match-patch/
   *
   *LicensedundertheApacheLicense,Version2.0(the"License");
   *youmaynotusethisfileexceptincompliancewiththeLicense.
   *YoumayobtainacopyoftheLicenseat
   *
   *https://www.apache.org/licenses/LICENSE-2.0
   *
   *Unlessrequiredbyapplicablelaworagreedtoinwriting,software
   *distributedundertheLicenseisdistributedonan"ASIS"BASIS,
   *WITHOUTWARRANTIESORCONDITIONSOFANYKIND,eitherexpressorimplied.
   *SeetheLicenseforthespecificlanguagegoverningpermissionsand
   *limitationsundertheLicense.
   *
   *MoreInfo:
   * https://code.google.com/p/google-diff-match-patch/
   *
   *Usage:QUnit.diff(expected,actual)
   *
   */
  QUnit.diff=function(){
  	functionDiffMatchPatch(){}

  	// DIFFFUNCTIONS

  	/**
    *Thedatastructurerepresentingadiffisanarrayoftuples:
    *[[DIFF_DELETE,'Hello'],[DIFF_INSERT,'Goodbye'],[DIFF_EQUAL,'world.']]
    *whichmeans:delete'Hello',add'Goodbye'andkeep'world.'
    */
  	varDIFF_DELETE=-1,
  	   DIFF_INSERT=1,
  	   DIFF_EQUAL=0;

  	/**
    *Findthedifferencesbetweentwotexts. Simplifiestheproblembystripping
    *anycommonprefixorsuffixoffthetextsbeforediffing.
    *@param{string}text1Oldstringtobediffed.
    *@param{string}text2Newstringtobediffed.
    *@param{boolean=}optChecklinesOptionalspeedupflag.Ifpresentandfalse,
    *    thendon'trunaline-leveldifffirsttoidentifythechangedareas.
    *    Defaultstotrue,whichdoesafaster,slightlylessoptimaldiff.
    *@return{!Array.<!DiffMatchPatch.Diff>}Arrayofdifftuples.
    */
  	DiffMatchPatch.prototype.DiffMain=function(text1,text2,optChecklines){
  		vardeadline,checklines,commonlength,commonprefix,commonsuffix,diffs;

  		//Thediffmustbecompleteinupto1second.
  		deadline=newDate().getTime()+1000;

  		//Checkfornullinputs.
  		if(text1===null||text2===null){
  			thrownewError("Nullinput.(DiffMain)");
  		}

  		//Checkforequality(speedup).
  		if(text1===text2){
  			if(text1){
  				return[[DIFF_EQUAL,text1]];
  			}
  			return[];
  		}

  		if(typeofoptChecklines==="undefined"){
  			optChecklines=true;
  		}

  		checklines=optChecklines;

  		//Trimoffcommonprefix(speedup).
  		commonlength=this.diffCommonPrefix(text1,text2);
  		commonprefix=text1.substring(0,commonlength);
  		text1=text1.substring(commonlength);
  		text2=text2.substring(commonlength);

  		//Trimoffcommonsuffix(speedup).
  		commonlength=this.diffCommonSuffix(text1,text2);
  		commonsuffix=text1.substring(text1.length-commonlength);
  		text1=text1.substring(0,text1.length-commonlength);
  		text2=text2.substring(0,text2.length-commonlength);

  		//Computethediffonthemiddleblock.
  		diffs=this.diffCompute(text1,text2,checklines,deadline);

  		//Restoretheprefixandsuffix.
  		if(commonprefix){
  			diffs.unshift([DIFF_EQUAL,commonprefix]);
  		}
  		if(commonsuffix){
  			diffs.push([DIFF_EQUAL,commonsuffix]);
  		}
  		this.diffCleanupMerge(diffs);
  		returndiffs;
  	};

  	/**
    *Reducethenumberofeditsbyeliminatingoperationallytrivialequalities.
    *@param{!Array.<!DiffMatchPatch.Diff>}diffsArrayofdifftuples.
    */
  	DiffMatchPatch.prototype.diffCleanupEfficiency=function(diffs){
  		varchanges,equalities,equalitiesLength,lastequality,pointer,preIns,preDel,postIns,postDel;
  		changes=false;
  		equalities=[];//Stackofindiceswhereequalitiesarefound.
  		equalitiesLength=0;//KeepingourownlengthvarisfasterinJS.
  		/**@type{?string}*/
  		lastequality=null;

  		//Alwaysequaltodiffs[equalities[equalitiesLength-1]][1]
  		pointer=0;//Indexofcurrentposition.

  		//Isthereaninsertionoperationbeforethelastequality.
  		preIns=false;

  		//Isthereadeletionoperationbeforethelastequality.
  		preDel=false;

  		//Isthereaninsertionoperationafterthelastequality.
  		postIns=false;

  		//Isthereadeletionoperationafterthelastequality.
  		postDel=false;
  		while(pointer<diffs.length){

  			//Equalityfound.
  			if(diffs[pointer][0]===DIFF_EQUAL){
  				if(diffs[pointer][1].length<4&&(postIns||postDel)){

  					//Candidatefound.
  					equalities[equalitiesLength++]=pointer;
  					preIns=postIns;
  					preDel=postDel;
  					lastequality=diffs[pointer][1];
  				}else{

  					//Notacandidate,andcanneverbecomeone.
  					equalitiesLength=0;
  					lastequality=null;
  				}
  				postIns=postDel=false;

  				//Aninsertionordeletion.
  			}else{

  				if(diffs[pointer][0]===DIFF_DELETE){
  					postDel=true;
  				}else{
  					postIns=true;
  				}

  				/*
       *Fivetypestobesplit:
       *<ins>A</ins><del>B</del>XY<ins>C</ins><del>D</del>
       *<ins>A</ins>X<ins>C</ins><del>D</del>
       *<ins>A</ins><del>B</del>X<ins>C</ins>
       *<ins>A</del>X<ins>C</ins><del>D</del>
       *<ins>A</ins><del>B</del>X<del>C</del>
       */
  				if(lastequality&&(preIns&&preDel&&postIns&&postDel||lastequality.length<2&&preIns+preDel+postIns+postDel===3)){

  					//Duplicaterecord.
  					diffs.splice(equalities[equalitiesLength-1],0,[DIFF_DELETE,lastequality]);

  					//Changesecondcopytoinsert.
  					diffs[equalities[equalitiesLength-1]+1][0]=DIFF_INSERT;
  					equalitiesLength--;//Throwawaytheequalitywejustdeleted;
  					lastequality=null;
  					if(preIns&&preDel){

  						//Nochangesmadewhichcouldaffectpreviousentry,keepgoing.
  						postIns=postDel=true;
  						equalitiesLength=0;
  					}else{
  						equalitiesLength--;//Throwawaythepreviousequality.
  						pointer=equalitiesLength>0?equalities[equalitiesLength-1]:-1;
  						postIns=postDel=false;
  					}
  					changes=true;
  				}
  			}
  			pointer++;
  		}

  		if(changes){
  			this.diffCleanupMerge(diffs);
  		}
  	};

  	/**
    *ConvertadiffarrayintoaprettyHTMLreport.
    *@param{!Array.<!DiffMatchPatch.Diff>}diffsArrayofdifftuples.
    *@param{integer}stringtobebeautified.
    *@return{string}HTMLrepresentation.
    */
  	DiffMatchPatch.prototype.diffPrettyHtml=function(diffs){
  		varop,
  		   data,
  		   x,
  		   html=[];
  		for(x=0;x<diffs.length;x++){
  			op=diffs[x][0];//Operation(insert,delete,equal)
  			data=diffs[x][1];//Textofchange.
  			switch(op){
  				caseDIFF_INSERT:
  					html[x]="<ins>"+escapeText(data)+"</ins>";
  					break;
  				caseDIFF_DELETE:
  					html[x]="<del>"+escapeText(data)+"</del>";
  					break;
  				caseDIFF_EQUAL:
  					html[x]="<span>"+escapeText(data)+"</span>";
  					break;
  			}
  		}
  		returnhtml.join("");
  	};

  	/**
    *Determinethecommonprefixoftwostrings.
    *@param{string}text1Firststring.
    *@param{string}text2Secondstring.
    *@return{number}Thenumberofcharacterscommontothestartofeach
    *    string.
    */
  	DiffMatchPatch.prototype.diffCommonPrefix=function(text1,text2){
  		varpointermid,pointermax,pointermin,pointerstart;

  		//Quickcheckforcommonnullcases.
  		if(!text1||!text2||text1.charAt(0)!==text2.charAt(0)){
  			return0;
  		}

  		//Binarysearch.
  		//Performanceanalysis:https://neil.fraser.name/news/2007/10/09/
  		pointermin=0;
  		pointermax=Math.min(text1.length,text2.length);
  		pointermid=pointermax;
  		pointerstart=0;
  		while(pointermin<pointermid){
  			if(text1.substring(pointerstart,pointermid)===text2.substring(pointerstart,pointermid)){
  				pointermin=pointermid;
  				pointerstart=pointermin;
  			}else{
  				pointermax=pointermid;
  			}
  			pointermid=Math.floor((pointermax-pointermin)/2+pointermin);
  		}
  		returnpointermid;
  	};

  	/**
    *Determinethecommonsuffixoftwostrings.
    *@param{string}text1Firststring.
    *@param{string}text2Secondstring.
    *@return{number}Thenumberofcharacterscommontotheendofeachstring.
    */
  	DiffMatchPatch.prototype.diffCommonSuffix=function(text1,text2){
  		varpointermid,pointermax,pointermin,pointerend;

  		//Quickcheckforcommonnullcases.
  		if(!text1||!text2||text1.charAt(text1.length-1)!==text2.charAt(text2.length-1)){
  			return0;
  		}

  		//Binarysearch.
  		//Performanceanalysis:https://neil.fraser.name/news/2007/10/09/
  		pointermin=0;
  		pointermax=Math.min(text1.length,text2.length);
  		pointermid=pointermax;
  		pointerend=0;
  		while(pointermin<pointermid){
  			if(text1.substring(text1.length-pointermid,text1.length-pointerend)===text2.substring(text2.length-pointermid,text2.length-pointerend)){
  				pointermin=pointermid;
  				pointerend=pointermin;
  			}else{
  				pointermax=pointermid;
  			}
  			pointermid=Math.floor((pointermax-pointermin)/2+pointermin);
  		}
  		returnpointermid;
  	};

  	/**
    *Findthedifferencesbetweentwotexts. Assumesthatthetextsdonot
    *haveanycommonprefixorsuffix.
    *@param{string}text1Oldstringtobediffed.
    *@param{string}text2Newstringtobediffed.
    *@param{boolean}checklinesSpeedupflag. Iffalse,thendon'truna
    *    line-leveldifffirsttoidentifythechangedareas.
    *    Iftrue,thenrunafaster,slightlylessoptimaldiff.
    *@param{number}deadlineTimewhenthediffshouldbecompleteby.
    *@return{!Array.<!DiffMatchPatch.Diff>}Arrayofdifftuples.
    *@private
    */
  	DiffMatchPatch.prototype.diffCompute=function(text1,text2,checklines,deadline){
  		vardiffs,longtext,shorttext,i,hm,text1A,text2A,text1B,text2B,midCommon,diffsA,diffsB;

  		if(!text1){

  			//Justaddsometext(speedup).
  			return[[DIFF_INSERT,text2]];
  		}

  		if(!text2){

  			//Justdeletesometext(speedup).
  			return[[DIFF_DELETE,text1]];
  		}

  		longtext=text1.length>text2.length?text1:text2;
  		shorttext=text1.length>text2.length?text2:text1;
  		i=longtext.indexOf(shorttext);
  		if(i!==-1){

  			//Shortertextisinsidethelongertext(speedup).
  			diffs=[[DIFF_INSERT,longtext.substring(0,i)],[DIFF_EQUAL,shorttext],[DIFF_INSERT,longtext.substring(i+shorttext.length)]];

  			//Swapinsertionsfordeletionsifdiffisreversed.
  			if(text1.length>text2.length){
  				diffs[0][0]=diffs[2][0]=DIFF_DELETE;
  			}
  			returndiffs;
  		}

  		if(shorttext.length===1){

  			//Singlecharacterstring.
  			//Afterthepreviousspeedup,thecharactercan'tbeanequality.
  			return[[DIFF_DELETE,text1],[DIFF_INSERT,text2]];
  		}

  		//Checktoseeiftheproblemcanbesplitintwo.
  		hm=this.diffHalfMatch(text1,text2);
  		if(hm){

  			//Ahalf-matchwasfound,sortoutthereturndata.
  			text1A=hm[0];
  			text1B=hm[1];
  			text2A=hm[2];
  			text2B=hm[3];
  			midCommon=hm[4];

  			//Sendbothpairsoffforseparateprocessing.
  			diffsA=this.DiffMain(text1A,text2A,checklines,deadline);
  			diffsB=this.DiffMain(text1B,text2B,checklines,deadline);

  			//Mergetheresults.
  			returndiffsA.concat([[DIFF_EQUAL,midCommon]],diffsB);
  		}

  		if(checklines&&text1.length>100&&text2.length>100){
  			returnthis.diffLineMode(text1,text2,deadline);
  		}

  		returnthis.diffBisect(text1,text2,deadline);
  	};

  	/**
    *Dothetwotextsshareasubstringwhichisatleasthalfthelengthofthe
    *longertext?
    *Thisspeedupcanproducenon-minimaldiffs.
    *@param{string}text1Firststring.
    *@param{string}text2Secondstring.
    *@return{Array.<string>}FiveelementArray,containingtheprefixof
    *    text1,thesuffixoftext1,theprefixoftext2,thesuffixof
    *    text2andthecommonmiddle. Ornulliftherewasnomatch.
    *@private
    */
  	DiffMatchPatch.prototype.diffHalfMatch=function(text1,text2){
  		varlongtext,shorttext,dmp,text1A,text2B,text2A,text1B,midCommon,hm1,hm2,hm;

  		longtext=text1.length>text2.length?text1:text2;
  		shorttext=text1.length>text2.length?text2:text1;
  		if(longtext.length<4||shorttext.length*2<longtext.length){
  			returnnull;//Pointless.
  		}
  		dmp=this;//'this'becomes'window'inaclosure.

  		/**
     *Doesasubstringofshorttextexistwithinlongtextsuchthatthesubstring
     *isatleasthalfthelengthoflongtext?
     *Closure,butdoesnotreferenceanyexternalvariables.
     *@param{string}longtextLongerstring.
     *@param{string}shorttextShorterstring.
     *@param{number}iStartindexofquarterlengthsubstringwithinlongtext.
     *@return{Array.<string>}FiveelementArray,containingtheprefixof
     *    longtext,thesuffixoflongtext,theprefixofshorttext,thesuffix
     *    ofshorttextandthecommonmiddle. Ornulliftherewasnomatch.
     *@private
     */
  		functiondiffHalfMatchI(longtext,shorttext,i){
  			varseed,j,bestCommon,prefixLength,suffixLength,bestLongtextA,bestLongtextB,bestShorttextA,bestShorttextB;

  			//Startwitha1/4lengthsubstringatpositioniasaseed.
  			seed=longtext.substring(i,i+Math.floor(longtext.length/4));
  			j=-1;
  			bestCommon="";
  			while((j=shorttext.indexOf(seed,j+1))!==-1){
  				prefixLength=dmp.diffCommonPrefix(longtext.substring(i),shorttext.substring(j));
  				suffixLength=dmp.diffCommonSuffix(longtext.substring(0,i),shorttext.substring(0,j));
  				if(bestCommon.length<suffixLength+prefixLength){
  					bestCommon=shorttext.substring(j-suffixLength,j)+shorttext.substring(j,j+prefixLength);
  					bestLongtextA=longtext.substring(0,i-suffixLength);
  					bestLongtextB=longtext.substring(i+prefixLength);
  					bestShorttextA=shorttext.substring(0,j-suffixLength);
  					bestShorttextB=shorttext.substring(j+prefixLength);
  				}
  			}
  			if(bestCommon.length*2>=longtext.length){
  				return[bestLongtextA,bestLongtextB,bestShorttextA,bestShorttextB,bestCommon];
  			}else{
  				returnnull;
  			}
  		}

  		//Firstcheckifthesecondquarteristheseedforahalf-match.
  		hm1=diffHalfMatchI(longtext,shorttext,Math.ceil(longtext.length/4));

  		//Checkagainbasedonthethirdquarter.
  		hm2=diffHalfMatchI(longtext,shorttext,Math.ceil(longtext.length/2));
  		if(!hm1&&!hm2){
  			returnnull;
  		}elseif(!hm2){
  			hm=hm1;
  		}elseif(!hm1){
  			hm=hm2;
  		}else{

  			//Bothmatched. Selectthelongest.
  			hm=hm1[4].length>hm2[4].length?hm1:hm2;
  		}

  		//Ahalf-matchwasfound,sortoutthereturndata.
  		if(text1.length>text2.length){
  			text1A=hm[0];
  			text1B=hm[1];
  			text2A=hm[2];
  			text2B=hm[3];
  		}else{
  			text2A=hm[0];
  			text2B=hm[1];
  			text1A=hm[2];
  			text1B=hm[3];
  		}
  		midCommon=hm[4];
  		return[text1A,text1B,text2A,text2B,midCommon];
  	};

  	/**
    *Doaquickline-leveldiffonbothstrings,thenrediffthepartsfor
    *greateraccuracy.
    *Thisspeedupcanproducenon-minimaldiffs.
    *@param{string}text1Oldstringtobediffed.
    *@param{string}text2Newstringtobediffed.
    *@param{number}deadlineTimewhenthediffshouldbecompleteby.
    *@return{!Array.<!DiffMatchPatch.Diff>}Arrayofdifftuples.
    *@private
    */
  	DiffMatchPatch.prototype.diffLineMode=function(text1,text2,deadline){
  		vara,diffs,linearray,pointer,countInsert,countDelete,textInsert,textDelete,j;

  		//Scanthetextonaline-by-linebasisfirst.
  		a=this.diffLinesToChars(text1,text2);
  		text1=a.chars1;
  		text2=a.chars2;
  		linearray=a.lineArray;

  		diffs=this.DiffMain(text1,text2,false,deadline);

  		//Convertthediffbacktooriginaltext.
  		this.diffCharsToLines(diffs,linearray);

  		//Eliminatefreakmatches(e.g.blanklines)
  		this.diffCleanupSemantic(diffs);

  		//Rediffanyreplacementblocks,thistimecharacter-by-character.
  		//Addadummyentryattheend.
  		diffs.push([DIFF_EQUAL,""]);
  		pointer=0;
  		countDelete=0;
  		countInsert=0;
  		textDelete="";
  		textInsert="";
  		while(pointer<diffs.length){
  			switch(diffs[pointer][0]){
  				caseDIFF_INSERT:
  					countInsert++;
  					textInsert+=diffs[pointer][1];
  					break;
  				caseDIFF_DELETE:
  					countDelete++;
  					textDelete+=diffs[pointer][1];
  					break;
  				caseDIFF_EQUAL:

  					//Uponreachinganequality,checkforpriorredundancies.
  					if(countDelete>=1&&countInsert>=1){

  						//Deletetheoffendingrecordsandaddthemergedones.
  						diffs.splice(pointer-countDelete-countInsert,countDelete+countInsert);
  						pointer=pointer-countDelete-countInsert;
  						a=this.DiffMain(textDelete,textInsert,false,deadline);
  						for(j=a.length-1;j>=0;j--){
  							diffs.splice(pointer,0,a[j]);
  						}
  						pointer=pointer+a.length;
  					}
  					countInsert=0;
  					countDelete=0;
  					textDelete="";
  					textInsert="";
  					break;
  			}
  			pointer++;
  		}
  		diffs.pop();//Removethedummyentryattheend.

  		returndiffs;
  	};

  	/**
    *Findthe'middlesnake'ofadiff,splittheproblemintwo
    *andreturntherecursivelyconstructeddiff.
    *SeeMyers1986paper:AnO(ND)DifferenceAlgorithmandItsVariations.
    *@param{string}text1Oldstringtobediffed.
    *@param{string}text2Newstringtobediffed.
    *@param{number}deadlineTimeatwhichtobailifnotyetcomplete.
    *@return{!Array.<!DiffMatchPatch.Diff>}Arrayofdifftuples.
    *@private
    */
  	DiffMatchPatch.prototype.diffBisect=function(text1,text2,deadline){
  		vartext1Length,text2Length,maxD,vOffset,vLength,v1,v2,x,delta,front,k1start,k1end,k2start,k2end,k2Offset,k1Offset,x1,x2,y1,y2,d,k1,k2;

  		//Cachethetextlengthstopreventmultiplecalls.
  		text1Length=text1.length;
  		text2Length=text2.length;
  		maxD=Math.ceil((text1Length+text2Length)/2);
  		vOffset=maxD;
  		vLength=2*maxD;
  		v1=newArray(vLength);
  		v2=newArray(vLength);

  		//Settingallelementsto-1isfasterinChrome&Firefoxthanmixing
  		//integersandundefined.
  		for(x=0;x<vLength;x++){
  			v1[x]=-1;
  			v2[x]=-1;
  		}
  		v1[vOffset+1]=0;
  		v2[vOffset+1]=0;
  		delta=text1Length-text2Length;

  		//Ifthetotalnumberofcharactersisodd,thenthefrontpathwillcollide
  		//withthereversepath.
  		front=delta%2!==0;

  		//Offsetsforstartandendofkloop.
  		//Preventsmappingofspacebeyondthegrid.
  		k1start=0;
  		k1end=0;
  		k2start=0;
  		k2end=0;
  		for(d=0;d<maxD;d++){

  			//Bailoutifdeadlineisreached.
  			if(newDate().getTime()>deadline){
  				break;
  			}

  			//Walkthefrontpathonestep.
  			for(k1=-d+k1start;k1<=d-k1end;k1+=2){
  				k1Offset=vOffset+k1;
  				if(k1===-d||k1!==d&&v1[k1Offset-1]<v1[k1Offset+1]){
  					x1=v1[k1Offset+1];
  				}else{
  					x1=v1[k1Offset-1]+1;
  				}
  				y1=x1-k1;
  				while(x1<text1Length&&y1<text2Length&&text1.charAt(x1)===text2.charAt(y1)){
  					x1++;
  					y1++;
  				}
  				v1[k1Offset]=x1;
  				if(x1>text1Length){

  					//Ranofftherightofthegraph.
  					k1end+=2;
  				}elseif(y1>text2Length){

  					//Ranoffthebottomofthegraph.
  					k1start+=2;
  				}elseif(front){
  					k2Offset=vOffset+delta-k1;
  					if(k2Offset>=0&&k2Offset<vLength&&v2[k2Offset]!==-1){

  						//Mirrorx2ontotop-leftcoordinatesystem.
  						x2=text1Length-v2[k2Offset];
  						if(x1>=x2){

  							//Overlapdetected.
  							returnthis.diffBisectSplit(text1,text2,x1,y1,deadline);
  						}
  					}
  				}
  			}

  			//Walkthereversepathonestep.
  			for(k2=-d+k2start;k2<=d-k2end;k2+=2){
  				k2Offset=vOffset+k2;
  				if(k2===-d||k2!==d&&v2[k2Offset-1]<v2[k2Offset+1]){
  					x2=v2[k2Offset+1];
  				}else{
  					x2=v2[k2Offset-1]+1;
  				}
  				y2=x2-k2;
  				while(x2<text1Length&&y2<text2Length&&text1.charAt(text1Length-x2-1)===text2.charAt(text2Length-y2-1)){
  					x2++;
  					y2++;
  				}
  				v2[k2Offset]=x2;
  				if(x2>text1Length){

  					//Ranofftheleftofthegraph.
  					k2end+=2;
  				}elseif(y2>text2Length){

  					//Ranoffthetopofthegraph.
  					k2start+=2;
  				}elseif(!front){
  					k1Offset=vOffset+delta-k2;
  					if(k1Offset>=0&&k1Offset<vLength&&v1[k1Offset]!==-1){
  						x1=v1[k1Offset];
  						y1=vOffset+x1-k1Offset;

  						//Mirrorx2ontotop-leftcoordinatesystem.
  						x2=text1Length-x2;
  						if(x1>=x2){

  							//Overlapdetected.
  							returnthis.diffBisectSplit(text1,text2,x1,y1,deadline);
  						}
  					}
  				}
  			}
  		}

  		//Difftooktoolongandhitthedeadlineor
  		//numberofdiffsequalsnumberofcharacters,nocommonalityatall.
  		return[[DIFF_DELETE,text1],[DIFF_INSERT,text2]];
  	};

  	/**
    *Giventhelocationofthe'middlesnake',splitthediffintwoparts
    *andrecurse.
    *@param{string}text1Oldstringtobediffed.
    *@param{string}text2Newstringtobediffed.
    *@param{number}xIndexofsplitpointintext1.
    *@param{number}yIndexofsplitpointintext2.
    *@param{number}deadlineTimeatwhichtobailifnotyetcomplete.
    *@return{!Array.<!DiffMatchPatch.Diff>}Arrayofdifftuples.
    *@private
    */
  	DiffMatchPatch.prototype.diffBisectSplit=function(text1,text2,x,y,deadline){
  		vartext1a,text1b,text2a,text2b,diffs,diffsb;
  		text1a=text1.substring(0,x);
  		text2a=text2.substring(0,y);
  		text1b=text1.substring(x);
  		text2b=text2.substring(y);

  		//Computebothdiffsserially.
  		diffs=this.DiffMain(text1a,text2a,false,deadline);
  		diffsb=this.DiffMain(text1b,text2b,false,deadline);

  		returndiffs.concat(diffsb);
  	};

  	/**
    *Reducethenumberofeditsbyeliminatingsemanticallytrivialequalities.
    *@param{!Array.<!DiffMatchPatch.Diff>}diffsArrayofdifftuples.
    */
  	DiffMatchPatch.prototype.diffCleanupSemantic=function(diffs){
  		varchanges,equalities,equalitiesLength,lastequality,pointer,lengthInsertions2,lengthDeletions2,lengthInsertions1,lengthDeletions1,deletion,insertion,overlapLength1,overlapLength2;
  		changes=false;
  		equalities=[];//Stackofindiceswhereequalitiesarefound.
  		equalitiesLength=0;//KeepingourownlengthvarisfasterinJS.
  		/**@type{?string}*/
  		lastequality=null;

  		//Alwaysequaltodiffs[equalities[equalitiesLength-1]][1]
  		pointer=0;//Indexofcurrentposition.

  		//Numberofcharactersthatchangedpriortotheequality.
  		lengthInsertions1=0;
  		lengthDeletions1=0;

  		//Numberofcharactersthatchangedaftertheequality.
  		lengthInsertions2=0;
  		lengthDeletions2=0;
  		while(pointer<diffs.length){
  			if(diffs[pointer][0]===DIFF_EQUAL){
  				//Equalityfound.
  				equalities[equalitiesLength++]=pointer;
  				lengthInsertions1=lengthInsertions2;
  				lengthDeletions1=lengthDeletions2;
  				lengthInsertions2=0;
  				lengthDeletions2=0;
  				lastequality=diffs[pointer][1];
  			}else{
  				//Aninsertionordeletion.
  				if(diffs[pointer][0]===DIFF_INSERT){
  					lengthInsertions2+=diffs[pointer][1].length;
  				}else{
  					lengthDeletions2+=diffs[pointer][1].length;
  				}

  				//Eliminateanequalitythatissmallerorequaltotheeditsonboth
  				//sidesofit.
  				if(lastequality&&lastequality.length<=Math.max(lengthInsertions1,lengthDeletions1)&&lastequality.length<=Math.max(lengthInsertions2,lengthDeletions2)){

  					//Duplicaterecord.
  					diffs.splice(equalities[equalitiesLength-1],0,[DIFF_DELETE,lastequality]);

  					//Changesecondcopytoinsert.
  					diffs[equalities[equalitiesLength-1]+1][0]=DIFF_INSERT;

  					//Throwawaytheequalitywejustdeleted.
  					equalitiesLength--;

  					//Throwawaythepreviousequality(itneedstobereevaluated).
  					equalitiesLength--;
  					pointer=equalitiesLength>0?equalities[equalitiesLength-1]:-1;

  					//Resetthecounters.
  					lengthInsertions1=0;
  					lengthDeletions1=0;
  					lengthInsertions2=0;
  					lengthDeletions2=0;
  					lastequality=null;
  					changes=true;
  				}
  			}
  			pointer++;
  		}

  		//Normalizethediff.
  		if(changes){
  			this.diffCleanupMerge(diffs);
  		}

  		//Findanyoverlapsbetweendeletionsandinsertions.
  		//e.g:<del>abcxxx</del><ins>xxxdef</ins>
  		//  -><del>abc</del>xxx<ins>def</ins>
  		//e.g:<del>xxxabc</del><ins>defxxx</ins>
  		//  -><ins>def</ins>xxx<del>abc</del>
  		//Onlyextractanoverlapifitisasbigastheeditaheadorbehindit.
  		pointer=1;
  		while(pointer<diffs.length){
  			if(diffs[pointer-1][0]===DIFF_DELETE&&diffs[pointer][0]===DIFF_INSERT){
  				deletion=diffs[pointer-1][1];
  				insertion=diffs[pointer][1];
  				overlapLength1=this.diffCommonOverlap(deletion,insertion);
  				overlapLength2=this.diffCommonOverlap(insertion,deletion);
  				if(overlapLength1>=overlapLength2){
  					if(overlapLength1>=deletion.length/2||overlapLength1>=insertion.length/2){

  						//Overlapfound. Insertanequalityandtrimthesurroundingedits.
  						diffs.splice(pointer,0,[DIFF_EQUAL,insertion.substring(0,overlapLength1)]);
  						diffs[pointer-1][1]=deletion.substring(0,deletion.length-overlapLength1);
  						diffs[pointer+1][1]=insertion.substring(overlapLength1);
  						pointer++;
  					}
  				}else{
  					if(overlapLength2>=deletion.length/2||overlapLength2>=insertion.length/2){

  						//Reverseoverlapfound.
  						//Insertanequalityandswapandtrimthesurroundingedits.
  						diffs.splice(pointer,0,[DIFF_EQUAL,deletion.substring(0,overlapLength2)]);

  						diffs[pointer-1][0]=DIFF_INSERT;
  						diffs[pointer-1][1]=insertion.substring(0,insertion.length-overlapLength2);
  						diffs[pointer+1][0]=DIFF_DELETE;
  						diffs[pointer+1][1]=deletion.substring(overlapLength2);
  						pointer++;
  					}
  				}
  				pointer++;
  			}
  			pointer++;
  		}
  	};

  	/**
    *Determineifthesuffixofonestringistheprefixofanother.
    *@param{string}text1Firststring.
    *@param{string}text2Secondstring.
    *@return{number}Thenumberofcharacterscommontotheendofthefirst
    *    stringandthestartofthesecondstring.
    *@private
    */
  	DiffMatchPatch.prototype.diffCommonOverlap=function(text1,text2){
  		vartext1Length,text2Length,textLength,best,length,pattern,found;

  		//Cachethetextlengthstopreventmultiplecalls.
  		text1Length=text1.length;
  		text2Length=text2.length;

  		//Eliminatethenullcase.
  		if(text1Length===0||text2Length===0){
  			return0;
  		}

  		//Truncatethelongerstring.
  		if(text1Length>text2Length){
  			text1=text1.substring(text1Length-text2Length);
  		}elseif(text1Length<text2Length){
  			text2=text2.substring(0,text1Length);
  		}
  		textLength=Math.min(text1Length,text2Length);

  		//Quickcheckfortheworstcase.
  		if(text1===text2){
  			returntextLength;
  		}

  		//Startbylookingforasinglecharactermatch
  		//andincreaselengthuntilnomatchisfound.
  		//Performanceanalysis:https://neil.fraser.name/news/2010/11/04/
  		best=0;
  		length=1;
  		while(true){
  			pattern=text1.substring(textLength-length);
  			found=text2.indexOf(pattern);
  			if(found===-1){
  				returnbest;
  			}
  			length+=found;
  			if(found===0||text1.substring(textLength-length)===text2.substring(0,length)){
  				best=length;
  				length++;
  			}
  		}
  	};

  	/**
    *Splittwotextsintoanarrayofstrings. Reducethetextstoastringof
    *hasheswhereeachUnicodecharacterrepresentsoneline.
    *@param{string}text1Firststring.
    *@param{string}text2Secondstring.
    *@return{{chars1:string,chars2:string,lineArray:!Array.<string>}}
    *    Anobjectcontainingtheencodedtext1,theencodedtext2and
    *    thearrayofuniquestrings.
    *    Thezerothelementofthearrayofuniquestringsisintentionallyblank.
    *@private
    */
  	DiffMatchPatch.prototype.diffLinesToChars=function(text1,text2){
  		varlineArray,lineHash,chars1,chars2;
  		lineArray=[];//E.g.lineArray[4]==='Hello\n'
  		lineHash={};//E.g.lineHash['Hello\n']===4

  		//'\x00'isavalidcharacter,butvariousdebuggersdon'tlikeit.
  		//Sowe'llinsertajunkentrytoavoidgeneratinganullcharacter.
  		lineArray[0]="";

  		/**
     *Splitatextintoanarrayofstrings. Reducethetextstoastringof
     *hasheswhereeachUnicodecharacterrepresentsoneline.
     *Modifieslinearrayandlinehashthroughbeingaclosure.
     *@param{string}textStringtoencode.
     *@return{string}Encodedstring.
     *@private
     */
  		functiondiffLinesToCharsMunge(text){
  			varchars,lineStart,lineEnd,lineArrayLength,line;
  			chars="";

  			//Walkthetext,pullingoutasubstringforeachline.
  			//text.split('\n')wouldwouldtemporarilydoubleourmemoryfootprint.
  			//Modifyingtextwouldcreatemanylargestringstogarbagecollect.
  			lineStart=0;
  			lineEnd=-1;

  			//Keepingourownlengthvariableisfasterthanlookingitup.
  			lineArrayLength=lineArray.length;
  			while(lineEnd<text.length-1){
  				lineEnd=text.indexOf("\n",lineStart);
  				if(lineEnd===-1){
  					lineEnd=text.length-1;
  				}
  				line=text.substring(lineStart,lineEnd+1);
  				lineStart=lineEnd+1;

  				varlineHashExists=lineHash.hasOwnProperty?lineHash.hasOwnProperty(line):lineHash[line]!==undefined;

  				if(lineHashExists){
  					chars+=String.fromCharCode(lineHash[line]);
  				}else{
  					chars+=String.fromCharCode(lineArrayLength);
  					lineHash[line]=lineArrayLength;
  					lineArray[lineArrayLength++]=line;
  				}
  			}
  			returnchars;
  		}

  		chars1=diffLinesToCharsMunge(text1);
  		chars2=diffLinesToCharsMunge(text2);
  		return{
  			chars1:chars1,
  			chars2:chars2,
  			lineArray:lineArray
  		};
  	};

  	/**
    *Rehydratethetextinadifffromastringoflinehashestoreallinesof
    *text.
    *@param{!Array.<!DiffMatchPatch.Diff>}diffsArrayofdifftuples.
    *@param{!Array.<string>}lineArrayArrayofuniquestrings.
    *@private
    */
  	DiffMatchPatch.prototype.diffCharsToLines=function(diffs,lineArray){
  		varx,chars,text,y;
  		for(x=0;x<diffs.length;x++){
  			chars=diffs[x][1];
  			text=[];
  			for(y=0;y<chars.length;y++){
  				text[y]=lineArray[chars.charCodeAt(y)];
  			}
  			diffs[x][1]=text.join("");
  		}
  	};

  	/**
    *Reorderandmergelikeeditsections. Mergeequalities.
    *Anyeditsectioncanmoveaslongasitdoesn'tcrossanequality.
    *@param{!Array.<!DiffMatchPatch.Diff>}diffsArrayofdifftuples.
    */
  	DiffMatchPatch.prototype.diffCleanupMerge=function(diffs){
  		varpointer,countDelete,countInsert,textInsert,textDelete,commonlength,changes,diffPointer,position;
  		diffs.push([DIFF_EQUAL,""]);//Addadummyentryattheend.
  		pointer=0;
  		countDelete=0;
  		countInsert=0;
  		textDelete="";
  		textInsert="";

  		while(pointer<diffs.length){
  			switch(diffs[pointer][0]){
  				caseDIFF_INSERT:
  					countInsert++;
  					textInsert+=diffs[pointer][1];
  					pointer++;
  					break;
  				caseDIFF_DELETE:
  					countDelete++;
  					textDelete+=diffs[pointer][1];
  					pointer++;
  					break;
  				caseDIFF_EQUAL:

  					//Uponreachinganequality,checkforpriorredundancies.
  					if(countDelete+countInsert>1){
  						if(countDelete!==0&&countInsert!==0){

  							//Factoroutanycommonprefixes.
  							commonlength=this.diffCommonPrefix(textInsert,textDelete);
  							if(commonlength!==0){
  								if(pointer-countDelete-countInsert>0&&diffs[pointer-countDelete-countInsert-1][0]===DIFF_EQUAL){
  									diffs[pointer-countDelete-countInsert-1][1]+=textInsert.substring(0,commonlength);
  								}else{
  									diffs.splice(0,0,[DIFF_EQUAL,textInsert.substring(0,commonlength)]);
  									pointer++;
  								}
  								textInsert=textInsert.substring(commonlength);
  								textDelete=textDelete.substring(commonlength);
  							}

  							//Factoroutanycommonsuffixies.
  							commonlength=this.diffCommonSuffix(textInsert,textDelete);
  							if(commonlength!==0){
  								diffs[pointer][1]=textInsert.substring(textInsert.length-commonlength)+diffs[pointer][1];
  								textInsert=textInsert.substring(0,textInsert.length-commonlength);
  								textDelete=textDelete.substring(0,textDelete.length-commonlength);
  							}
  						}

  						//Deletetheoffendingrecordsandaddthemergedones.
  						if(countDelete===0){
  							diffs.splice(pointer-countInsert,countDelete+countInsert,[DIFF_INSERT,textInsert]);
  						}elseif(countInsert===0){
  							diffs.splice(pointer-countDelete,countDelete+countInsert,[DIFF_DELETE,textDelete]);
  						}else{
  							diffs.splice(pointer-countDelete-countInsert,countDelete+countInsert,[DIFF_DELETE,textDelete],[DIFF_INSERT,textInsert]);
  						}
  						pointer=pointer-countDelete-countInsert+(countDelete?1:0)+(countInsert?1:0)+1;
  					}elseif(pointer!==0&&diffs[pointer-1][0]===DIFF_EQUAL){

  						//Mergethisequalitywiththepreviousone.
  						diffs[pointer-1][1]+=diffs[pointer][1];
  						diffs.splice(pointer,1);
  					}else{
  						pointer++;
  					}
  					countInsert=0;
  					countDelete=0;
  					textDelete="";
  					textInsert="";
  					break;
  			}
  		}
  		if(diffs[diffs.length-1][1]===""){
  			diffs.pop();//Removethedummyentryattheend.
  		}

  		//Secondpass:lookforsingleeditssurroundedonbothsidesbyequalities
  		//whichcanbeshiftedsidewaystoeliminateanequality.
  		//e.g:A<ins>BA</ins>C-><ins>AB</ins>AC
  		changes=false;
  		pointer=1;

  		//Intentionallyignorethefirstandlastelement(don'tneedchecking).
  		while(pointer<diffs.length-1){
  			if(diffs[pointer-1][0]===DIFF_EQUAL&&diffs[pointer+1][0]===DIFF_EQUAL){

  				diffPointer=diffs[pointer][1];
  				position=diffPointer.substring(diffPointer.length-diffs[pointer-1][1].length);

  				//Thisisasingleeditsurroundedbyequalities.
  				if(position===diffs[pointer-1][1]){

  					//Shifttheeditoverthepreviousequality.
  					diffs[pointer][1]=diffs[pointer-1][1]+diffs[pointer][1].substring(0,diffs[pointer][1].length-diffs[pointer-1][1].length);
  					diffs[pointer+1][1]=diffs[pointer-1][1]+diffs[pointer+1][1];
  					diffs.splice(pointer-1,1);
  					changes=true;
  				}elseif(diffPointer.substring(0,diffs[pointer+1][1].length)===diffs[pointer+1][1]){

  					//Shifttheeditoverthenextequality.
  					diffs[pointer-1][1]+=diffs[pointer+1][1];
  					diffs[pointer][1]=diffs[pointer][1].substring(diffs[pointer+1][1].length)+diffs[pointer+1][1];
  					diffs.splice(pointer+1,1);
  					changes=true;
  				}
  			}
  			pointer++;
  		}

  		//Ifshiftsweremade,thediffneedsreorderingandanothershiftsweep.
  		if(changes){
  			this.diffCleanupMerge(diffs);
  		}
  	};

  	returnfunction(o,n){
  		vardiff,output,text;
  		diff=newDiffMatchPatch();
  		output=diff.DiffMain(o,n);
  		diff.diffCleanupEfficiency(output);
  		text=diff.diffPrettyHtml(output);

  		returntext;
  	};
  }();

}((function(){returnthis;}())));
