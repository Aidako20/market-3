/*!
 *jQueryJavaScriptLibraryv3.3.1
 *https://jquery.com/
 *
 *IncludesSizzle.js
 *https://sizzlejs.com/
 *
 *CopyrightJSFoundationandothercontributors
 *ReleasedundertheMITlicense
 *https://jquery.org/license
 *
 *Date:2018-01-20T17:24Z
 */
(function(global,factory){

	"usestrict";

	if(typeofmodule==="object"&&typeofmodule.exports==="object"){

		//ForCommonJSandCommonJS-likeenvironmentswhereaproper`window`
		//ispresent,executethefactoryandgetjQuery.
		//Forenvironmentsthatdonothavea`window`witha`document`
		//(suchasNode.js),exposeafactoryasmodule.exports.
		//Thisaccentuatestheneedforthecreationofareal`window`.
		//e.g.varjQuery=require("jquery")(window);
		//Seeticket#14549formoreinfo.
		module.exports=global.document?
			factory(global,true):
			function(w){
				if(!w.document){
					thrownewError("jQueryrequiresawindowwithadocument");
				}
				returnfactory(w);
			};
	}else{
		factory(global);
	}

//Passthisifwindowisnotdefinedyet
})(typeofwindow!=="undefined"?window:this,function(window,noGlobal){

//Edge<=12-13+,Firefox<=18-45+,IE10-11,Safari5.1-9+,iOS6-9.1
//throwexceptionswhennon-strictcode(e.g.,ASP.NET4.5)accessesstrictmode
//arguments.callee.caller(trac-13335).ButasofjQuery3.0(2016),strictmodeshouldbecommon
//enoughthatallsuchattemptsareguardedinatryblock.
"usestrict";

vararr=[];

vardocument=window.document;

vargetProto=Object.getPrototypeOf;

varslice=arr.slice;

varconcat=arr.concat;

varpush=arr.push;

varindexOf=arr.indexOf;

varclass2type={};

vartoString=class2type.toString;

varhasOwn=class2type.hasOwnProperty;

varfnToString=hasOwn.toString;

varObjectFunctionString=fnToString.call(Object);

varsupport={};

varisFunction=functionisFunction(obj){

      //Support:Chrome<=57,Firefox<=52
      //Insomebrowsers,typeofreturns"function"forHTML<object>elements
      //(i.e.,`typeofdocument.createElement("object")==="function"`).
      //Wedon'twanttoclassify*any*DOMnodeasafunction.
      returntypeofobj==="function"&&typeofobj.nodeType!=="number";
  };


varisWindow=functionisWindow(obj){
		returnobj!=null&&obj===obj.window;
	};




	varpreservedScriptAttributes={
		type:true,
		src:true,
		noModule:true
	};

	functionDOMEval(code,doc,node){
		doc=doc||document;

		vari,
			script=doc.createElement("script");

		script.text=code;
		if(node){
			for(iinpreservedScriptAttributes){
				if(node[i]){
					script[i]=node[i];
				}
			}
		}
		doc.head.appendChild(script).parentNode.removeChild(script);
	}


functiontoType(obj){
	if(obj==null){
		returnobj+"";
	}

	//Support:Android<=2.3only(functionishRegExp)
	returntypeofobj==="object"||typeofobj==="function"?
		class2type[toString.call(obj)]||"object":
		typeofobj;
}
/*globalSymbol*/
//Definingthisglobalin.eslintrc.jsonwouldcreateadangerofusingtheglobal
//unguardedinanotherplace,itseemssafertodefineglobalonlyforthismodule



var
	version="3.3.1",

	//DefinealocalcopyofjQuery
	jQuery=function(selector,context){

		//ThejQueryobjectisactuallyjusttheinitconstructor'enhanced'
		//NeedinitifjQueryiscalled(justallowerrortobethrownifnotincluded)
		returnnewjQuery.fn.init(selector,context);
	},

	//Support:Android<=4.0only
	//MakesurewetrimBOMandNBSP
	rtrim=/^[\s\uFEFF\xA0]+|[\s\uFEFF\xA0]+$/g;

jQuery.fn=jQuery.prototype={

	//ThecurrentversionofjQuerybeingused
	jquery:version,

	constructor:jQuery,

	//ThedefaultlengthofajQueryobjectis0
	length:0,

	toArray:function(){
		returnslice.call(this);
	},

	//GettheNthelementinthematchedelementsetOR
	//Getthewholematchedelementsetasacleanarray
	get:function(num){

		//Returnalltheelementsinacleanarray
		if(num==null){
			returnslice.call(this);
		}

		//Returnjusttheoneelementfromtheset
		returnnum<0?this[num+this.length]:this[num];
	},

	//Takeanarrayofelementsandpushitontothestack
	//(returningthenewmatchedelementset)
	pushStack:function(elems){

		//BuildanewjQuerymatchedelementset
		varret=jQuery.merge(this.constructor(),elems);

		//Addtheoldobjectontothestack(asareference)
		ret.prevObject=this;

		//Returnthenewly-formedelementset
		returnret;
	},

	//Executeacallbackforeveryelementinthematchedset.
	each:function(callback){
		returnjQuery.each(this,callback);
	},

	map:function(callback){
		returnthis.pushStack(jQuery.map(this,function(elem,i){
			returncallback.call(elem,i,elem);
		}));
	},

	slice:function(){
		returnthis.pushStack(slice.apply(this,arguments));
	},

	first:function(){
		returnthis.eq(0);
	},

	last:function(){
		returnthis.eq(-1);
	},

	eq:function(i){
		varlen=this.length,
			j=+i+(i<0?len:0);
		returnthis.pushStack(j>=0&&j<len?[this[j]]:[]);
	},

	end:function(){
		returnthis.prevObject||this.constructor();
	},

	//Forinternaluseonly.
	//BehaveslikeanArray'smethod,notlikeajQuerymethod.
	push:push,
	sort:arr.sort,
	splice:arr.splice
};

jQuery.extend=jQuery.fn.extend=function(){
	varoptions,name,src,copy,copyIsArray,clone,
		target=arguments[0]||{},
		i=1,
		length=arguments.length,
		deep=false;

	//Handleadeepcopysituation
	if(typeoftarget==="boolean"){
		deep=target;

		//Skipthebooleanandthetarget
		target=arguments[i]||{};
		i++;
	}

	//Handlecasewhentargetisastringorsomething(possibleindeepcopy)
	if(typeoftarget!=="object"&&!isFunction(target)){
		target={};
	}

	//ExtendjQueryitselfifonlyoneargumentispassed
	if(i===length){
		target=this;
		i--;
	}

	for(;i<length;i++){

		//Onlydealwithnon-null/undefinedvalues
		if((options=arguments[i])!=null){

			//Extendthebaseobject
			for(nameinoptions){
				src=target[name];
				copy=options[name];

				//Preventnever-endingloop
				if(name==='__proto__'||target===copy){
					continue;
				}

				//Recurseifwe'remergingplainobjectsorarrays
				if(deep&&copy&&(jQuery.isPlainObject(copy)||
					(copyIsArray=Array.isArray(copy)))){

					if(copyIsArray){
						copyIsArray=false;
						clone=src&&Array.isArray(src)?src:[];

					}else{
						clone=src&&jQuery.isPlainObject(src)?src:{};
					}

					//Nevermoveoriginalobjects,clonethem
					target[name]=jQuery.extend(deep,clone,copy);

				//Don'tbringinundefinedvalues
				}elseif(copy!==undefined){
					target[name]=copy;
				}
			}
		}
	}

	//Returnthemodifiedobject
	returntarget;
};

jQuery.extend({

	//UniqueforeachcopyofjQueryonthepage
	expando:"jQuery"+(version+Math.random()).replace(/\D/g,""),

	//AssumejQueryisreadywithoutthereadymodule
	isReady:true,

	error:function(msg){
		thrownewError(msg);
	},

	noop:function(){},

	isPlainObject:function(obj){
		varproto,Ctor;

		//Detectobviousnegatives
		//UsetoStringinsteadofjQuery.typetocatchhostobjects
		if(!obj||toString.call(obj)!=="[objectObject]"){
			returnfalse;
		}

		proto=getProto(obj);

		//Objectswithnoprototype(e.g.,`Object.create(null)`)areplain
		if(!proto){
			returntrue;
		}

		//ObjectswithprototypeareplainifftheywereconstructedbyaglobalObjectfunction
		Ctor=hasOwn.call(proto,"constructor")&&proto.constructor;
		returntypeofCtor==="function"&&fnToString.call(Ctor)===ObjectFunctionString;
	},

	isEmptyObject:function(obj){

		/*eslint-disableno-unused-vars*/
		//Seehttps://github.com/eslint/eslint/issues/6125
		varname;

		for(nameinobj){
			returnfalse;
		}
		returntrue;
	},

	//Evaluatesascriptinaglobalcontext
	globalEval:function(code){
		DOMEval(code);
	},

	each:function(obj,callback){
		varlength,i=0;

		if(isArrayLike(obj)){
			length=obj.length;
			for(;i<length;i++){
				if(callback.call(obj[i],i,obj[i])===false){
					break;
				}
			}
		}else{
			for(iinobj){
				if(callback.call(obj[i],i,obj[i])===false){
					break;
				}
			}
		}

		returnobj;
	},

	//Support:Android<=4.0only
	trim:function(text){
		returntext==null?
			"":
			(text+"").replace(rtrim,"");
	},

	//resultsisforinternalusageonly
	makeArray:function(arr,results){
		varret=results||[];

		if(arr!=null){
			if(isArrayLike(Object(arr))){
				jQuery.merge(ret,
					typeofarr==="string"?
					[arr]:arr
				);
			}else{
				push.call(ret,arr);
			}
		}

		returnret;
	},

	inArray:function(elem,arr,i){
		returnarr==null?-1:indexOf.call(arr,elem,i);
	},

	//Support:Android<=4.0only,PhantomJS1only
	//push.apply(_,arraylike)throwsonancientWebKit
	merge:function(first,second){
		varlen=+second.length,
			j=0,
			i=first.length;

		for(;j<len;j++){
			first[i++]=second[j];
		}

		first.length=i;

		returnfirst;
	},

	grep:function(elems,callback,invert){
		varcallbackInverse,
			matches=[],
			i=0,
			length=elems.length,
			callbackExpect=!invert;

		//Gothroughthearray,onlysavingtheitems
		//thatpassthevalidatorfunction
		for(;i<length;i++){
			callbackInverse=!callback(elems[i],i);
			if(callbackInverse!==callbackExpect){
				matches.push(elems[i]);
			}
		}

		returnmatches;
	},

	//argisforinternalusageonly
	map:function(elems,callback,arg){
		varlength,value,
			i=0,
			ret=[];

		//Gothroughthearray,translatingeachoftheitemstotheirnewvalues
		if(isArrayLike(elems)){
			length=elems.length;
			for(;i<length;i++){
				value=callback(elems[i],i,arg);

				if(value!=null){
					ret.push(value);
				}
			}

		//Gothrougheverykeyontheobject,
		}else{
			for(iinelems){
				value=callback(elems[i],i,arg);

				if(value!=null){
					ret.push(value);
				}
			}
		}

		//Flattenanynestedarrays
		returnconcat.apply([],ret);
	},

	//AglobalGUIDcounterforobjects
	guid:1,

	//jQuery.supportisnotusedinCorebutotherprojectsattachtheir
	//propertiestoitsoitneedstoexist.
	support:support
});

if(typeofSymbol==="function"){
	jQuery.fn[Symbol.iterator]=arr[Symbol.iterator];
}

//Populatetheclass2typemap
jQuery.each("BooleanNumberStringFunctionArrayDateRegExpObjectErrorSymbol".split(""),
function(i,name){
	class2type["[object"+name+"]"]=name.toLowerCase();
});

functionisArrayLike(obj){

	//Support:realiOS8.2only(notreproducibleinsimulator)
	//`in`checkusedtopreventJITerror(gh-2145)
	//hasOwnisn'tusedhereduetofalsenegatives
	//regardingNodelistlengthinIE
	varlength=!!obj&&"length"inobj&&obj.length,
		type=toType(obj);

	if(isFunction(obj)||isWindow(obj)){
		returnfalse;
	}

	returntype==="array"||length===0||
		typeoflength==="number"&&length>0&&(length-1)inobj;
}
varSizzle=
/*!
 *SizzleCSSSelectorEnginev2.3.3
 *https://sizzlejs.com/
 *
 *CopyrightjQueryFoundationandothercontributors
 *ReleasedundertheMITlicense
 *http://jquery.org/license
 *
 *Date:2016-08-08
 */
(function(window){

vari,
	support,
	Expr,
	getText,
	isXML,
	tokenize,
	compile,
	select,
	outermostContext,
	sortInput,
	hasDuplicate,

	//Localdocumentvars
	setDocument,
	document,
	docElem,
	documentIsHTML,
	rbuggyQSA,
	rbuggyMatches,
	matches,
	contains,

	//Instance-specificdata
	expando="sizzle"+1*newDate(),
	preferredDoc=window.document,
	dirruns=0,
	done=0,
	classCache=createCache(),
	tokenCache=createCache(),
	compilerCache=createCache(),
	sortOrder=function(a,b){
		if(a===b){
			hasDuplicate=true;
		}
		return0;
	},

	//Instancemethods
	hasOwn=({}).hasOwnProperty,
	arr=[],
	pop=arr.pop,
	push_native=arr.push,
	push=arr.push,
	slice=arr.slice,
	//Useastripped-downindexOfasit'sfasterthannative
	//https://jsperf.com/thor-indexof-vs-for/5
	indexOf=function(list,elem){
		vari=0,
			len=list.length;
		for(;i<len;i++){
			if(list[i]===elem){
				returni;
			}
		}
		return-1;
	},

	booleans="checked|selected|async|autofocus|autoplay|controls|defer|disabled|hidden|ismap|loop|multiple|open|readonly|required|scoped",

	//Regularexpressions

	//http://www.w3.org/TR/css3-selectors/#whitespace
	whitespace="[\\x20\\t\\r\\n\\f]",

	//http://www.w3.org/TR/CSS21/syndata.html#value-def-identifier
	identifier="(?:\\\\.|[\\w-]|[^\0-\\xa0])+",

	//Attributeselectors:http://www.w3.org/TR/selectors/#attribute-selectors
	attributes="\\["+whitespace+"*("+identifier+")(?:"+whitespace+
		//Operator(capture2)
		"*([*^$|!~]?=)"+whitespace+
		//"AttributevaluesmustbeCSSidentifiers[capture5]orstrings[capture3orcapture4]"
		"*(?:'((?:\\\\.|[^\\\\'])*)'|\"((?:\\\\.|[^\\\\\"])*)\"|("+identifier+"))|)"+whitespace+
		"*\\]",

	pseudos=":("+identifier+")(?:\\(("+
		//ToreducethenumberofselectorsneedingtokenizeinthepreFilter,preferarguments:
		//1.quoted(capture3;capture4orcapture5)
		"('((?:\\\\.|[^\\\\'])*)'|\"((?:\\\\.|[^\\\\\"])*)\")|"+
		//2.simple(capture6)
		"((?:\\\\.|[^\\\\()[\\]]|"+attributes+")*)|"+
		//3.anythingelse(capture2)
		".*"+
		")\\)|)",

	//Leadingandnon-escapedtrailingwhitespace,capturingsomenon-whitespacecharactersprecedingthelatter
	rwhitespace=newRegExp(whitespace+"+","g"),
	rtrim=newRegExp("^"+whitespace+"+|((?:^|[^\\\\])(?:\\\\.)*)"+whitespace+"+$","g"),

	rcomma=newRegExp("^"+whitespace+"*,"+whitespace+"*"),
	rcombinators=newRegExp("^"+whitespace+"*([>+~]|"+whitespace+")"+whitespace+"*"),

	rattributeQuotes=newRegExp("="+whitespace+"*([^\\]'\"]*?)"+whitespace+"*\\]","g"),

	rpseudo=newRegExp(pseudos),
	ridentifier=newRegExp("^"+identifier+"$"),

	matchExpr={
		"ID":newRegExp("^#("+identifier+")"),
		"CLASS":newRegExp("^\\.("+identifier+")"),
		"TAG":newRegExp("^("+identifier+"|[*])"),
		"ATTR":newRegExp("^"+attributes),
		"PSEUDO":newRegExp("^"+pseudos),
		"CHILD":newRegExp("^:(only|first|last|nth|nth-last)-(child|of-type)(?:\\("+whitespace+
			"*(even|odd|(([+-]|)(\\d*)n|)"+whitespace+"*(?:([+-]|)"+whitespace+
			"*(\\d+)|))"+whitespace+"*\\)|)","i"),
		"bool":newRegExp("^(?:"+booleans+")$","i"),
		//Foruseinlibrariesimplementing.is()
		//WeusethisforPOSmatchingin`select`
		"needsContext":newRegExp("^"+whitespace+"*[>+~]|:(even|odd|eq|gt|lt|nth|first|last)(?:\\("+
			whitespace+"*((?:-\\d)?\\d*)"+whitespace+"*\\)|)(?=[^-]|$)","i")
	},

	rinputs=/^(?:input|select|textarea|button)$/i,
	rheader=/^h\d$/i,

	rnative=/^[^{]+\{\s*\[native\w/,

	//Easily-parseable/retrievableIDorTAGorCLASSselectors
	rquickExpr=/^(?:#([\w-]+)|(\w+)|\.([\w-]+))$/,

	rsibling=/[+~]/,

	//CSSescapes
	//http://www.w3.org/TR/CSS21/syndata.html#escaped-characters
	runescape=newRegExp("\\\\([\\da-f]{1,6}"+whitespace+"?|("+whitespace+")|.)","ig"),
	funescape=function(_,escaped,escapedWhitespace){
		varhigh="0x"+escaped-0x10000;
		//NaNmeansnon-codepoint
		//Support:Firefox<24
		//Workarounderroneousnumericinterpretationof+"0x"
		returnhigh!==high||escapedWhitespace?
			escaped:
			high<0?
				//BMPcodepoint
				String.fromCharCode(high+0x10000):
				//SupplementalPlanecodepoint(surrogatepair)
				String.fromCharCode(high>>10|0xD800,high&0x3FF|0xDC00);
	},

	//CSSstring/identifierserialization
	//https://drafts.csswg.org/cssom/#common-serializing-idioms
	rcssescape=/([\0-\x1f\x7f]|^-?\d)|^-$|[^\0-\x1f\x7f-\uFFFF\w-]/g,
	fcssescape=function(ch,asCodePoint){
		if(asCodePoint){

			//U+0000NULLbecomesU+FFFDREPLACEMENTCHARACTER
			if(ch==="\0"){
				return"\uFFFD";
			}

			//Controlcharactersand(dependentuponposition)numbersgetescapedascodepoints
			returnch.slice(0,-1)+"\\"+ch.charCodeAt(ch.length-1).toString(16)+"";
		}

		//Otherpotentially-specialASCIIcharactersgetbackslash-escaped
		return"\\"+ch;
	},

	//Usedforiframes
	//SeesetDocument()
	//Removingthefunctionwrappercausesa"PermissionDenied"
	//errorinIE
	unloadHandler=function(){
		setDocument();
	},

	disabledAncestor=addCombinator(
		function(elem){
			returnelem.disabled===true&&("form"inelem||"label"inelem);
		},
		{dir:"parentNode",next:"legend"}
	);

//Optimizeforpush.apply(_,NodeList)
try{
	push.apply(
		(arr=slice.call(preferredDoc.childNodes)),
		preferredDoc.childNodes
	);
	//Support:Android<4.0
	//Detectsilentlyfailingpush.apply
	arr[preferredDoc.childNodes.length].nodeType;
}catch(e){
	push={apply:arr.length?

		//Leveragesliceifpossible
		function(target,els){
			push_native.apply(target,slice.call(els));
		}:

		//Support:IE<9
		//Otherwiseappenddirectly
		function(target,els){
			varj=target.length,
				i=0;
			//Can'ttrustNodeList.length
			while((target[j++]=els[i++])){}
			target.length=j-1;
		}
	};
}

functionSizzle(selector,context,results,seed){
	varm,i,elem,nid,match,groups,newSelector,
		newContext=context&&context.ownerDocument,

		//nodeTypedefaultsto9,sincecontextdefaultstodocument
		nodeType=context?context.nodeType:9;

	results=results||[];

	//Returnearlyfromcallswithinvalidselectororcontext
	if(typeofselector!=="string"||!selector||
		nodeType!==1&&nodeType!==9&&nodeType!==11){

		returnresults;
	}

	//Trytoshortcutfindoperations(asopposedtofilters)inHTMLdocuments
	if(!seed){

		if((context?context.ownerDocument||context:preferredDoc)!==document){
			setDocument(context);
		}
		context=context||document;

		if(documentIsHTML){

			//Iftheselectorissufficientlysimple,tryusinga"get*By*"DOMmethod
			//(exceptingDocumentFragmentcontext,wherethemethodsdon'texist)
			if(nodeType!==11&&(match=rquickExpr.exec(selector))){

				//IDselector
				if((m=match[1])){

					//Documentcontext
					if(nodeType===9){
						if((elem=context.getElementById(m))){

							//Support:IE,Opera,Webkit
							//TODO:identifyversions
							//getElementByIdcanmatchelementsbynameinsteadofID
							if(elem.id===m){
								results.push(elem);
								returnresults;
							}
						}else{
							returnresults;
						}

					//Elementcontext
					}else{

						//Support:IE,Opera,Webkit
						//TODO:identifyversions
						//getElementByIdcanmatchelementsbynameinsteadofID
						if(newContext&&(elem=newContext.getElementById(m))&&
							contains(context,elem)&&
							elem.id===m){

							results.push(elem);
							returnresults;
						}
					}

				//Typeselector
				}elseif(match[2]){
					push.apply(results,context.getElementsByTagName(selector));
					returnresults;

				//Classselector
				}elseif((m=match[3])&&support.getElementsByClassName&&
					context.getElementsByClassName){

					push.apply(results,context.getElementsByClassName(m));
					returnresults;
				}
			}

			//TakeadvantageofquerySelectorAll
			if(support.qsa&&
				!compilerCache[selector+""]&&
				(!rbuggyQSA||!rbuggyQSA.test(selector))){

				if(nodeType!==1){
					newContext=context;
					newSelector=selector;

				//qSAlooksoutsideElementcontext,whichisnotwhatwewant
				//ThankstoAndrewDupontforthisworkaroundtechnique
				//Support:IE<=8
				//Excludeobjectelements
				}elseif(context.nodeName.toLowerCase()!=="object"){

					//CapturethecontextID,settingitfirstifnecessary
					if((nid=context.getAttribute("id"))){
						nid=nid.replace(rcssescape,fcssescape);
					}else{
						context.setAttribute("id",(nid=expando));
					}

					//Prefixeveryselectorinthelist
					groups=tokenize(selector);
					i=groups.length;
					while(i--){
						groups[i]="#"+nid+""+toSelector(groups[i]);
					}
					newSelector=groups.join(",");

					//Expandcontextforsiblingselectors
					newContext=rsibling.test(selector)&&testContext(context.parentNode)||
						context;
				}

				if(newSelector){
					try{
						push.apply(results,
							newContext.querySelectorAll(newSelector)
						);
						returnresults;
					}catch(qsaError){
					}finally{
						if(nid===expando){
							context.removeAttribute("id");
						}
					}
				}
			}
		}
	}

	//Allothers
	returnselect(selector.replace(rtrim,"$1"),context,results,seed);
}

/**
 *Createkey-valuecachesoflimitedsize
 *@returns{function(string,object)}ReturnstheObjectdataafterstoringitonitselfwith
 *	propertynamethe(space-suffixed)stringand(ifthecacheislargerthanExpr.cacheLength)
 *	deletingtheoldestentry
 */
functioncreateCache(){
	varkeys=[];

	functioncache(key,value){
		//Use(key+"")toavoidcollisionwithnativeprototypeproperties(seeIssue#157)
		if(keys.push(key+"")>Expr.cacheLength){
			//Onlykeepthemostrecententries
			deletecache[keys.shift()];
		}
		return(cache[key+""]=value);
	}
	returncache;
}

/**
 *MarkafunctionforspecialusebySizzle
 *@param{Function}fnThefunctiontomark
 */
functionmarkFunction(fn){
	fn[expando]=true;
	returnfn;
}

/**
 *Supporttestingusinganelement
 *@param{Function}fnPassedthecreatedelementandreturnsabooleanresult
 */
functionassert(fn){
	varel=document.createElement("fieldset");

	try{
		return!!fn(el);
	}catch(e){
		returnfalse;
	}finally{
		//Removefromitsparentbydefault
		if(el.parentNode){
			el.parentNode.removeChild(el);
		}
		//releasememoryinIE
		el=null;
	}
}

/**
 *Addsthesamehandlerforallofthespecifiedattrs
 *@param{String}attrsPipe-separatedlistofattributes
 *@param{Function}handlerThemethodthatwillbeapplied
 */
functionaddHandle(attrs,handler){
	vararr=attrs.split("|"),
		i=arr.length;

	while(i--){
		Expr.attrHandle[arr[i]]=handler;
	}
}

/**
 *Checksdocumentorderoftwosiblings
 *@param{Element}a
 *@param{Element}b
 *@returns{Number}Returnslessthan0ifaprecedesb,greaterthan0ifafollowsb
 */
functionsiblingCheck(a,b){
	varcur=b&&a,
		diff=cur&&a.nodeType===1&&b.nodeType===1&&
			a.sourceIndex-b.sourceIndex;

	//UseIEsourceIndexifavailableonbothnodes
	if(diff){
		returndiff;
	}

	//Checkifbfollowsa
	if(cur){
		while((cur=cur.nextSibling)){
			if(cur===b){
				return-1;
			}
		}
	}

	returna?1:-1;
}

/**
 *Returnsafunctiontouseinpseudosforinputtypes
 *@param{String}type
 */
functioncreateInputPseudo(type){
	returnfunction(elem){
		varname=elem.nodeName.toLowerCase();
		returnname==="input"&&elem.type===type;
	};
}

/**
 *Returnsafunctiontouseinpseudosforbuttons
 *@param{String}type
 */
functioncreateButtonPseudo(type){
	returnfunction(elem){
		varname=elem.nodeName.toLowerCase();
		return(name==="input"||name==="button")&&elem.type===type;
	};
}

/**
 *Returnsafunctiontouseinpseudosfor:enabled/:disabled
 *@param{Boolean}disabledtruefor:disabled;falsefor:enabled
 */
functioncreateDisabledPseudo(disabled){

	//Known:disabledfalsepositives:fieldset[disabled]>legend:nth-of-type(n+2):can-disable
	returnfunction(elem){

		//Onlycertainelementscanmatch:enabledor:disabled
		//https://html.spec.whatwg.org/multipage/scripting.html#selector-enabled
		//https://html.spec.whatwg.org/multipage/scripting.html#selector-disabled
		if("form"inelem){

			//Checkforinheriteddisablednessonrelevantnon-disabledelements:
			//*listedform-associatedelementsinadisabledfieldset
			//  https://html.spec.whatwg.org/multipage/forms.html#category-listed
			//  https://html.spec.whatwg.org/multipage/forms.html#concept-fe-disabled
			//*optionelementsinadisabledoptgroup
			//  https://html.spec.whatwg.org/multipage/forms.html#concept-option-disabled
			//Allsuchelementshavea"form"property.
			if(elem.parentNode&&elem.disabled===false){

				//Optionelementsdefertoaparentoptgroupifpresent
				if("label"inelem){
					if("label"inelem.parentNode){
						returnelem.parentNode.disabled===disabled;
					}else{
						returnelem.disabled===disabled;
					}
				}

				//Support:IE6-11
				//UsetheisDisabledshortcutpropertytocheckfordisabledfieldsetancestors
				returnelem.isDisabled===disabled||

					//WherethereisnoisDisabled,checkmanually
					/*jshint-W018*/
					elem.isDisabled!==!disabled&&
						disabledAncestor(elem)===disabled;
			}

			returnelem.disabled===disabled;

		//Trytowinnowoutelementsthatcan'tbedisabledbeforetrustingthedisabledproperty.
		//Somevictimsgetcaughtinournet(label,legend,menu,track),butitshouldn't
		//evenexistonthem,letalonehaveabooleanvalue.
		}elseif("label"inelem){
			returnelem.disabled===disabled;
		}

		//Remainingelementsareneither:enablednor:disabled
		returnfalse;
	};
}

/**
 *Returnsafunctiontouseinpseudosforpositionals
 *@param{Function}fn
 */
functioncreatePositionalPseudo(fn){
	returnmarkFunction(function(argument){
		argument=+argument;
		returnmarkFunction(function(seed,matches){
			varj,
				matchIndexes=fn([],seed.length,argument),
				i=matchIndexes.length;

			//Matchelementsfoundatthespecifiedindexes
			while(i--){
				if(seed[(j=matchIndexes[i])]){
					seed[j]=!(matches[j]=seed[j]);
				}
			}
		});
	});
}

/**
 *ChecksanodeforvalidityasaSizzlecontext
 *@param{Element|Object=}context
 *@returns{Element|Object|Boolean}Theinputnodeifacceptable,otherwiseafalsyvalue
 */
functiontestContext(context){
	returncontext&&typeofcontext.getElementsByTagName!=="undefined"&&context;
}

//Exposesupportvarsforconvenience
support=Sizzle.support={};

/**
 *DetectsXMLnodes
 *@param{Element|Object}elemAnelementoradocument
 *@returns{Boolean}Trueiffelemisanon-HTMLXMLnode
 */
isXML=Sizzle.isXML=function(elem){
	//documentElementisverifiedforcaseswhereitdoesn'tyetexist
	//(suchasloadingiframesinIE-#4833)
	vardocumentElement=elem&&(elem.ownerDocument||elem).documentElement;
	returndocumentElement?documentElement.nodeName!=="HTML":false;
};

/**
 *Setsdocument-relatedvariablesoncebasedonthecurrentdocument
 *@param{Element|Object}[doc]Anelementordocumentobjecttousetosetthedocument
 *@returns{Object}Returnsthecurrentdocument
 */
setDocument=Sizzle.setDocument=function(node){
	varhasCompare,subWindow,
		doc=node?node.ownerDocument||node:preferredDoc;

	//Returnearlyifdocisinvalidoralreadyselected
	if(doc===document||doc.nodeType!==9||!doc.documentElement){
		returndocument;
	}

	//Updateglobalvariables
	document=doc;
	docElem=document.documentElement;
	documentIsHTML=!isXML(document);

	//Support:IE9-11,Edge
	//Accessingiframedocumentsafterunloadthrows"permissiondenied"errors(jQuery#13936)
	if(preferredDoc!==document&&
		(subWindow=document.defaultView)&&subWindow.top!==subWindow){

		//Support:IE11,Edge
		if(subWindow.addEventListener){
			subWindow.addEventListener("unload",unloadHandler,false);

		//Support:IE9-10only
		}elseif(subWindow.attachEvent){
			subWindow.attachEvent("onunload",unloadHandler);
		}
	}

	/*Attributes
	----------------------------------------------------------------------*/

	//Support:IE<8
	//VerifythatgetAttributereallyreturnsattributesandnotproperties
	//(exceptingIE8booleans)
	support.attributes=assert(function(el){
		el.className="i";
		return!el.getAttribute("className");
	});

	/*getElement(s)By*
	----------------------------------------------------------------------*/

	//CheckifgetElementsByTagName("*")returnsonlyelements
	support.getElementsByTagName=assert(function(el){
		el.appendChild(document.createComment(""));
		return!el.getElementsByTagName("*").length;
	});

	//Support:IE<9
	support.getElementsByClassName=rnative.test(document.getElementsByClassName);

	//Support:IE<10
	//CheckifgetElementByIdreturnselementsbyname
	//ThebrokengetElementByIdmethodsdon'tpickupprogrammatically-setnames,
	//sousearoundaboutgetElementsByNametest
	support.getById=assert(function(el){
		docElem.appendChild(el).id=expando;
		return!document.getElementsByName||!document.getElementsByName(expando).length;
	});

	//IDfilterandfind
	if(support.getById){
		Expr.filter["ID"]=function(id){
			varattrId=id.replace(runescape,funescape);
			returnfunction(elem){
				returnelem.getAttribute("id")===attrId;
			};
		};
		Expr.find["ID"]=function(id,context){
			if(typeofcontext.getElementById!=="undefined"&&documentIsHTML){
				varelem=context.getElementById(id);
				returnelem?[elem]:[];
			}
		};
	}else{
		Expr.filter["ID"]= function(id){
			varattrId=id.replace(runescape,funescape);
			returnfunction(elem){
				varnode=typeofelem.getAttributeNode!=="undefined"&&
					elem.getAttributeNode("id");
				returnnode&&node.value===attrId;
			};
		};

		//Support:IE6-7only
		//getElementByIdisnotreliableasafindshortcut
		Expr.find["ID"]=function(id,context){
			if(typeofcontext.getElementById!=="undefined"&&documentIsHTML){
				varnode,i,elems,
					elem=context.getElementById(id);

				if(elem){

					//Verifytheidattribute
					node=elem.getAttributeNode("id");
					if(node&&node.value===id){
						return[elem];
					}

					//FallbackongetElementsByName
					elems=context.getElementsByName(id);
					i=0;
					while((elem=elems[i++])){
						node=elem.getAttributeNode("id");
						if(node&&node.value===id){
							return[elem];
						}
					}
				}

				return[];
			}
		};
	}

	//Tag
	Expr.find["TAG"]=support.getElementsByTagName?
		function(tag,context){
			if(typeofcontext.getElementsByTagName!=="undefined"){
				returncontext.getElementsByTagName(tag);

			//DocumentFragmentnodesdon'thavegEBTN
			}elseif(support.qsa){
				returncontext.querySelectorAll(tag);
			}
		}:

		function(tag,context){
			varelem,
				tmp=[],
				i=0,
				//Byhappycoincidence,a(broken)gEBTNappearsonDocumentFragmentnodestoo
				results=context.getElementsByTagName(tag);

			//Filteroutpossiblecomments
			if(tag==="*"){
				while((elem=results[i++])){
					if(elem.nodeType===1){
						tmp.push(elem);
					}
				}

				returntmp;
			}
			returnresults;
		};

	//Class
	Expr.find["CLASS"]=support.getElementsByClassName&&function(className,context){
		if(typeofcontext.getElementsByClassName!=="undefined"&&documentIsHTML){
			returncontext.getElementsByClassName(className);
		}
	};

	/*QSA/matchesSelector
	----------------------------------------------------------------------*/

	//QSAandmatchesSelectorsupport

	//matchesSelector(:active)reportsfalsewhentrue(IE9/Opera11.5)
	rbuggyMatches=[];

	//qSa(:focus)reportsfalsewhentrue(Chrome21)
	//WeallowthisbecauseofabuginIE8/9thatthrowsanerror
	//whenever`document.activeElement`isaccessedonaniframe
	//So,weallow:focustopassthroughQSAallthetimetoavoidtheIEerror
	//Seehttps://bugs.jquery.com/ticket/13378
	rbuggyQSA=[];

	if((support.qsa=rnative.test(document.querySelectorAll))){
		//BuildQSAregex
		//RegexstrategyadoptedfromDiegoPerini
		assert(function(el){
			//Selectissettoemptystringonpurpose
			//ThisistotestIE'streatmentofnotexplicitly
			//settingabooleancontentattribute,
			//sinceitspresenceshouldbeenough
			//https://bugs.jquery.com/ticket/12359
			docElem.appendChild(el).innerHTML="<aid='"+expando+"'></a>"+
				"<selectid='"+expando+"-\r\\'msallowcapture=''>"+
				"<optionselected=''></option></select>";

			//Support:IE8,Opera11-12.16
			//Nothingshouldbeselectedwhenemptystringsfollow^=or$=or*=
			//ThetestattributemustbeunknowninOperabut"safe"forWinRT
			//https://msdn.microsoft.com/en-us/library/ie/hh465388.aspx#attribute_section
			if(el.querySelectorAll("[msallowcapture^='']").length){
				rbuggyQSA.push("[*^$]="+whitespace+"*(?:''|\"\")");
			}

			//Support:IE8
			//Booleanattributesand"value"arenottreatedcorrectly
			if(!el.querySelectorAll("[selected]").length){
				rbuggyQSA.push("\\["+whitespace+"*(?:value|"+booleans+")");
			}

			//Support:Chrome<29,Android<4.4,Safari<7.0+,iOS<7.0+,PhantomJS<1.9.8+
			if(!el.querySelectorAll("[id~="+expando+"-]").length){
				rbuggyQSA.push("~=");
			}

			//Webkit/Opera-:checkedshouldreturnselectedoptionelements
			//http://www.w3.org/TR/2011/REC-css3-selectors-20110929/#checked
			//IE8throwserrorhereandwillnotseelatertests
			if(!el.querySelectorAll(":checked").length){
				rbuggyQSA.push(":checked");
			}

			//Support:Safari8+,iOS8+
			//https://bugs.webkit.org/show_bug.cgi?id=136851
			//In-page`selector#idsibling-combinatorselector`fails
			if(!el.querySelectorAll("a#"+expando+"+*").length){
				rbuggyQSA.push(".#.+[+~]");
			}
		});

		assert(function(el){
			el.innerHTML="<ahref=''disabled='disabled'></a>"+
				"<selectdisabled='disabled'><option/></select>";

			//Support:Windows8NativeApps
			//Thetypeandnameattributesarerestrictedduring.innerHTMLassignment
			varinput=document.createElement("input");
			input.setAttribute("type","hidden");
			el.appendChild(input).setAttribute("name","D");

			//Support:IE8
			//Enforcecase-sensitivityofnameattribute
			if(el.querySelectorAll("[name=d]").length){
				rbuggyQSA.push("name"+whitespace+"*[*^$|!~]?=");
			}

			//FF3.5-:enabled/:disabledandhiddenelements(hiddenelementsarestillenabled)
			//IE8throwserrorhereandwillnotseelatertests
			if(el.querySelectorAll(":enabled").length!==2){
				rbuggyQSA.push(":enabled",":disabled");
			}

			//Support:IE9-11+
			//IE's:disabledselectordoesnotpickupthechildrenofdisabledfieldsets
			docElem.appendChild(el).disabled=true;
			if(el.querySelectorAll(":disabled").length!==2){
				rbuggyQSA.push(":enabled",":disabled");
			}

			//Opera10-11doesnotthrowonpost-commainvalidpseudos
			el.querySelectorAll("*,:x");
			rbuggyQSA.push(",.*:");
		});
	}

	if((support.matchesSelector=rnative.test((matches=docElem.matches||
		docElem.webkitMatchesSelector||
		docElem.mozMatchesSelector||
		docElem.oMatchesSelector||
		docElem.msMatchesSelector)))){

		assert(function(el){
			//Checktoseeifit'spossibletodomatchesSelector
			//onadisconnectednode(IE9)
			support.disconnectedMatch=matches.call(el,"*");

			//Thisshouldfailwithanexception
			//Geckodoesnoterror,returnsfalseinstead
			matches.call(el,"[s!='']:x");
			rbuggyMatches.push("!=",pseudos);
		});
	}

	rbuggyQSA=rbuggyQSA.length&&newRegExp(rbuggyQSA.join("|"));
	rbuggyMatches=rbuggyMatches.length&&newRegExp(rbuggyMatches.join("|"));

	/*Contains
	----------------------------------------------------------------------*/
	hasCompare=rnative.test(docElem.compareDocumentPosition);

	//Elementcontainsanother
	//Purposefullyself-exclusive
	//Asin,anelementdoesnotcontainitself
	contains=hasCompare||rnative.test(docElem.contains)?
		function(a,b){
			varadown=a.nodeType===9?a.documentElement:a,
				bup=b&&b.parentNode;
			returna===bup||!!(bup&&bup.nodeType===1&&(
				adown.contains?
					adown.contains(bup):
					a.compareDocumentPosition&&a.compareDocumentPosition(bup)&16
			));
		}:
		function(a,b){
			if(b){
				while((b=b.parentNode)){
					if(b===a){
						returntrue;
					}
				}
			}
			returnfalse;
		};

	/*Sorting
	----------------------------------------------------------------------*/

	//Documentordersorting
	sortOrder=hasCompare?
	function(a,b){

		//Flagforduplicateremoval
		if(a===b){
			hasDuplicate=true;
			return0;
		}

		//SortonmethodexistenceifonlyoneinputhascompareDocumentPosition
		varcompare=!a.compareDocumentPosition-!b.compareDocumentPosition;
		if(compare){
			returncompare;
		}

		//Calculatepositionifbothinputsbelongtothesamedocument
		compare=(a.ownerDocument||a)===(b.ownerDocument||b)?
			a.compareDocumentPosition(b):

			//Otherwiseweknowtheyaredisconnected
			1;

		//Disconnectednodes
		if(compare&1||
			(!support.sortDetached&&b.compareDocumentPosition(a)===compare)){

			//Choosethefirstelementthatisrelatedtoourpreferreddocument
			if(a===document||a.ownerDocument===preferredDoc&&contains(preferredDoc,a)){
				return-1;
			}
			if(b===document||b.ownerDocument===preferredDoc&&contains(preferredDoc,b)){
				return1;
			}

			//Maintainoriginalorder
			returnsortInput?
				(indexOf(sortInput,a)-indexOf(sortInput,b)):
				0;
		}

		returncompare&4?-1:1;
	}:
	function(a,b){
		//Exitearlyifthenodesareidentical
		if(a===b){
			hasDuplicate=true;
			return0;
		}

		varcur,
			i=0,
			aup=a.parentNode,
			bup=b.parentNode,
			ap=[a],
			bp=[b];

		//Parentlessnodesareeitherdocumentsordisconnected
		if(!aup||!bup){
			returna===document?-1:
				b===document?1:
				aup?-1:
				bup?1:
				sortInput?
				(indexOf(sortInput,a)-indexOf(sortInput,b)):
				0;

		//Ifthenodesaresiblings,wecandoaquickcheck
		}elseif(aup===bup){
			returnsiblingCheck(a,b);
		}

		//Otherwiseweneedfulllistsoftheirancestorsforcomparison
		cur=a;
		while((cur=cur.parentNode)){
			ap.unshift(cur);
		}
		cur=b;
		while((cur=cur.parentNode)){
			bp.unshift(cur);
		}

		//Walkdownthetreelookingforadiscrepancy
		while(ap[i]===bp[i]){
			i++;
		}

		returni?
			//Doasiblingcheckifthenodeshaveacommonancestor
			siblingCheck(ap[i],bp[i]):

			//Otherwisenodesinourdocumentsortfirst
			ap[i]===preferredDoc?-1:
			bp[i]===preferredDoc?1:
			0;
	};

	returndocument;
};

Sizzle.matches=function(expr,elements){
	returnSizzle(expr,null,null,elements);
};

Sizzle.matchesSelector=function(elem,expr){
	//Setdocumentvarsifneeded
	if((elem.ownerDocument||elem)!==document){
		setDocument(elem);
	}

	//Makesurethatattributeselectorsarequoted
	expr=expr.replace(rattributeQuotes,"='$1']");

	if(support.matchesSelector&&documentIsHTML&&
		!compilerCache[expr+""]&&
		(!rbuggyMatches||!rbuggyMatches.test(expr))&&
		(!rbuggyQSA    ||!rbuggyQSA.test(expr))){

		try{
			varret=matches.call(elem,expr);

			//IE9'smatchesSelectorreturnsfalseondisconnectednodes
			if(ret||support.disconnectedMatch||
					//Aswell,disconnectednodesaresaidtobeinadocument
					//fragmentinIE9
					elem.document&&elem.document.nodeType!==11){
				returnret;
			}
		}catch(e){}
	}

	returnSizzle(expr,document,null,[elem]).length>0;
};

Sizzle.contains=function(context,elem){
	//Setdocumentvarsifneeded
	if((context.ownerDocument||context)!==document){
		setDocument(context);
	}
	returncontains(context,elem);
};

Sizzle.attr=function(elem,name){
	//Setdocumentvarsifneeded
	if((elem.ownerDocument||elem)!==document){
		setDocument(elem);
	}

	varfn=Expr.attrHandle[name.toLowerCase()],
		//Don'tgetfooledbyObject.prototypeproperties(jQuery#13807)
		val=fn&&hasOwn.call(Expr.attrHandle,name.toLowerCase())?
			fn(elem,name,!documentIsHTML):
			undefined;

	returnval!==undefined?
		val:
		support.attributes||!documentIsHTML?
			elem.getAttribute(name):
			(val=elem.getAttributeNode(name))&&val.specified?
				val.value:
				null;
};

Sizzle.escape=function(sel){
	return(sel+"").replace(rcssescape,fcssescape);
};

Sizzle.error=function(msg){
	thrownewError("Syntaxerror,unrecognizedexpression:"+msg);
};

/**
 *Documentsortingandremovingduplicates
 *@param{ArrayLike}results
 */
Sizzle.uniqueSort=function(results){
	varelem,
		duplicates=[],
		j=0,
		i=0;

	//Unlesswe*know*wecandetectduplicates,assumetheirpresence
	hasDuplicate=!support.detectDuplicates;
	sortInput=!support.sortStable&&results.slice(0);
	results.sort(sortOrder);

	if(hasDuplicate){
		while((elem=results[i++])){
			if(elem===results[i]){
				j=duplicates.push(i);
			}
		}
		while(j--){
			results.splice(duplicates[j],1);
		}
	}

	//Clearinputaftersortingtoreleaseobjects
	//Seehttps://github.com/jquery/sizzle/pull/225
	sortInput=null;

	returnresults;
};

/**
 *UtilityfunctionforretrievingthetextvalueofanarrayofDOMnodes
 *@param{Array|Element}elem
 */
getText=Sizzle.getText=function(elem){
	varnode,
		ret="",
		i=0,
		nodeType=elem.nodeType;

	if(!nodeType){
		//IfnonodeType,thisisexpectedtobeanarray
		while((node=elem[i++])){
			//Donottraversecommentnodes
			ret+=getText(node);
		}
	}elseif(nodeType===1||nodeType===9||nodeType===11){
		//UsetextContentforelements
		//innerTextusageremovedforconsistencyofnewlines(jQuery#11153)
		if(typeofelem.textContent==="string"){
			returnelem.textContent;
		}else{
			//Traverseitschildren
			for(elem=elem.firstChild;elem;elem=elem.nextSibling){
				ret+=getText(elem);
			}
		}
	}elseif(nodeType===3||nodeType===4){
		returnelem.nodeValue;
	}
	//Donotincludecommentorprocessinginstructionnodes

	returnret;
};

Expr=Sizzle.selectors={

	//Canbeadjustedbytheuser
	cacheLength:50,

	createPseudo:markFunction,

	match:matchExpr,

	attrHandle:{},

	find:{},

	relative:{
		">":{dir:"parentNode",first:true},
		"":{dir:"parentNode"},
		"+":{dir:"previousSibling",first:true},
		"~":{dir:"previousSibling"}
	},

	preFilter:{
		"ATTR":function(match){
			match[1]=match[1].replace(runescape,funescape);

			//Movethegivenvaluetomatch[3]whetherquotedorunquoted
			match[3]=(match[3]||match[4]||match[5]||"").replace(runescape,funescape);

			if(match[2]==="~="){
				match[3]=""+match[3]+"";
			}

			returnmatch.slice(0,4);
		},

		"CHILD":function(match){
			/*matchesfrommatchExpr["CHILD"]
				1type(only|nth|...)
				2what(child|of-type)
				3argument(even|odd|\d*|\d*n([+-]\d+)?|...)
				4xn-componentofxn+yargument([+-]?\d*n|)
				5signofxn-component
				6xofxn-component
				7signofy-component
				8yofy-component
			*/
			match[1]=match[1].toLowerCase();

			if(match[1].slice(0,3)==="nth"){
				//nth-*requiresargument
				if(!match[3]){
					Sizzle.error(match[0]);
				}

				//numericxandyparametersforExpr.filter.CHILD
				//rememberthatfalse/truecastrespectivelyto0/1
				match[4]=+(match[4]?match[5]+(match[6]||1):2*(match[3]==="even"||match[3]==="odd"));
				match[5]=+((match[7]+match[8])||match[3]==="odd");

			//othertypesprohibitarguments
			}elseif(match[3]){
				Sizzle.error(match[0]);
			}

			returnmatch;
		},

		"PSEUDO":function(match){
			varexcess,
				unquoted=!match[6]&&match[2];

			if(matchExpr["CHILD"].test(match[0])){
				returnnull;
			}

			//Acceptquotedargumentsas-is
			if(match[3]){
				match[2]=match[4]||match[5]||"";

			//Stripexcesscharactersfromunquotedarguments
			}elseif(unquoted&&rpseudo.test(unquoted)&&
				//Getexcessfromtokenize(recursively)
				(excess=tokenize(unquoted,true))&&
				//advancetothenextclosingparenthesis
				(excess=unquoted.indexOf(")",unquoted.length-excess)-unquoted.length)){

				//excessisanegativeindex
				match[0]=match[0].slice(0,excess);
				match[2]=unquoted.slice(0,excess);
			}

			//Returnonlycapturesneededbythepseudofiltermethod(typeandargument)
			returnmatch.slice(0,3);
		}
	},

	filter:{

		"TAG":function(nodeNameSelector){
			varnodeName=nodeNameSelector.replace(runescape,funescape).toLowerCase();
			returnnodeNameSelector==="*"?
				function(){returntrue;}:
				function(elem){
					returnelem.nodeName&&elem.nodeName.toLowerCase()===nodeName;
				};
		},

		"CLASS":function(className){
			varpattern=classCache[className+""];

			returnpattern||
				(pattern=newRegExp("(^|"+whitespace+")"+className+"("+whitespace+"|$)"))&&
				classCache(className,function(elem){
					returnpattern.test(typeofelem.className==="string"&&elem.className||typeofelem.getAttribute!=="undefined"&&elem.getAttribute("class")||"");
				});
		},

		"ATTR":function(name,operator,check){
			returnfunction(elem){
				varresult=Sizzle.attr(elem,name);

				if(result==null){
					returnoperator==="!=";
				}
				if(!operator){
					returntrue;
				}

				result+="";

				returnoperator==="="?result===check:
					operator==="!="?result!==check:
					operator==="^="?check&&result.indexOf(check)===0:
					operator==="*="?check&&result.indexOf(check)>-1:
					operator==="$="?check&&result.slice(-check.length)===check:
					operator==="~="?(""+result.replace(rwhitespace,"")+"").indexOf(check)>-1:
					operator==="|="?result===check||result.slice(0,check.length+1)===check+"-":
					false;
			};
		},

		"CHILD":function(type,what,argument,first,last){
			varsimple=type.slice(0,3)!=="nth",
				forward=type.slice(-4)!=="last",
				ofType=what==="of-type";

			returnfirst===1&&last===0?

				//Shortcutfor:nth-*(n)
				function(elem){
					return!!elem.parentNode;
				}:

				function(elem,context,xml){
					varcache,uniqueCache,outerCache,node,nodeIndex,start,
						dir=simple!==forward?"nextSibling":"previousSibling",
						parent=elem.parentNode,
						name=ofType&&elem.nodeName.toLowerCase(),
						useCache=!xml&&!ofType,
						diff=false;

					if(parent){

						//:(first|last|only)-(child|of-type)
						if(simple){
							while(dir){
								node=elem;
								while((node=node[dir])){
									if(ofType?
										node.nodeName.toLowerCase()===name:
										node.nodeType===1){

										returnfalse;
									}
								}
								//Reversedirectionfor:only-*(ifwehaven'tyetdoneso)
								start=dir=type==="only"&&!start&&"nextSibling";
							}
							returntrue;
						}

						start=[forward?parent.firstChild:parent.lastChild];

						//non-xml:nth-child(...)storescachedataon`parent`
						if(forward&&useCache){

							//Seek`elem`fromapreviously-cachedindex

							//...inagzip-friendlyway
							node=parent;
							outerCache=node[expando]||(node[expando]={});

							//Support:IE<9only
							//Defendagainstclonedattroperties(jQuerygh-1709)
							uniqueCache=outerCache[node.uniqueID]||
								(outerCache[node.uniqueID]={});

							cache=uniqueCache[type]||[];
							nodeIndex=cache[0]===dirruns&&cache[1];
							diff=nodeIndex&&cache[2];
							node=nodeIndex&&parent.childNodes[nodeIndex];

							while((node=++nodeIndex&&node&&node[dir]||

								//Fallbacktoseeking`elem`fromthestart
								(diff=nodeIndex=0)||start.pop())){

								//Whenfound,cacheindexeson`parent`andbreak
								if(node.nodeType===1&&++diff&&node===elem){
									uniqueCache[type]=[dirruns,nodeIndex,diff];
									break;
								}
							}

						}else{
							//Usepreviously-cachedelementindexifavailable
							if(useCache){
								//...inagzip-friendlyway
								node=elem;
								outerCache=node[expando]||(node[expando]={});

								//Support:IE<9only
								//Defendagainstclonedattroperties(jQuerygh-1709)
								uniqueCache=outerCache[node.uniqueID]||
									(outerCache[node.uniqueID]={});

								cache=uniqueCache[type]||[];
								nodeIndex=cache[0]===dirruns&&cache[1];
								diff=nodeIndex;
							}

							//xml:nth-child(...)
							//or:nth-last-child(...)or:nth(-last)?-of-type(...)
							if(diff===false){
								//Usethesameloopasabovetoseek`elem`fromthestart
								while((node=++nodeIndex&&node&&node[dir]||
									(diff=nodeIndex=0)||start.pop())){

									if((ofType?
										node.nodeName.toLowerCase()===name:
										node.nodeType===1)&&
										++diff){

										//Cachetheindexofeachencounteredelement
										if(useCache){
											outerCache=node[expando]||(node[expando]={});

											//Support:IE<9only
											//Defendagainstclonedattroperties(jQuerygh-1709)
											uniqueCache=outerCache[node.uniqueID]||
												(outerCache[node.uniqueID]={});

											uniqueCache[type]=[dirruns,diff];
										}

										if(node===elem){
											break;
										}
									}
								}
							}
						}

						//Incorporatetheoffset,thencheckagainstcyclesize
						diff-=last;
						returndiff===first||(diff%first===0&&diff/first>=0);
					}
				};
		},

		"PSEUDO":function(pseudo,argument){
			//pseudo-classnamesarecase-insensitive
			//http://www.w3.org/TR/selectors/#pseudo-classes
			//Prioritizebycasesensitivityincasecustompseudosareaddedwithuppercaseletters
			//RememberthatsetFiltersinheritsfrompseudos
			varargs,
				fn=Expr.pseudos[pseudo]||Expr.setFilters[pseudo.toLowerCase()]||
					Sizzle.error("unsupportedpseudo:"+pseudo);

			//TheusermayusecreatePseudotoindicatethat
			//argumentsareneededtocreatethefilterfunction
			//justasSizzledoes
			if(fn[expando]){
				returnfn(argument);
			}

			//Butmaintainsupportforoldsignatures
			if(fn.length>1){
				args=[pseudo,pseudo,"",argument];
				returnExpr.setFilters.hasOwnProperty(pseudo.toLowerCase())?
					markFunction(function(seed,matches){
						varidx,
							matched=fn(seed,argument),
							i=matched.length;
						while(i--){
							idx=indexOf(seed,matched[i]);
							seed[idx]=!(matches[idx]=matched[i]);
						}
					}):
					function(elem){
						returnfn(elem,0,args);
					};
			}

			returnfn;
		}
	},

	pseudos:{
		//Potentiallycomplexpseudos
		"not":markFunction(function(selector){
			//Trimtheselectorpassedtocompile
			//toavoidtreatingleadingandtrailing
			//spacesascombinators
			varinput=[],
				results=[],
				matcher=compile(selector.replace(rtrim,"$1"));

			returnmatcher[expando]?
				markFunction(function(seed,matches,context,xml){
					varelem,
						unmatched=matcher(seed,null,xml,[]),
						i=seed.length;

					//Matchelementsunmatchedby`matcher`
					while(i--){
						if((elem=unmatched[i])){
							seed[i]=!(matches[i]=elem);
						}
					}
				}):
				function(elem,context,xml){
					input[0]=elem;
					matcher(input,null,xml,results);
					//Don'tkeeptheelement(issue#299)
					input[0]=null;
					return!results.pop();
				};
		}),

		"has":markFunction(function(selector){
			returnfunction(elem){
				returnSizzle(selector,elem).length>0;
			};
		}),

		"contains":markFunction(function(text){
			text=text.replace(runescape,funescape);
			returnfunction(elem){
				return(elem.textContent||elem.innerText||getText(elem)).indexOf(text)>-1;
			};
		}),

		//"Whetheranelementisrepresentedbya:lang()selector
		//isbasedsolelyontheelement'slanguagevalue
		//beingequaltotheidentifierC,
		//orbeginningwiththeidentifierCimmediatelyfollowedby"-".
		//ThematchingofCagainsttheelement'slanguagevalueisperformedcase-insensitively.
		//TheidentifierCdoesnothavetobeavalidlanguagename."
		//http://www.w3.org/TR/selectors/#lang-pseudo
		"lang":markFunction(function(lang){
			//langvaluemustbeavalididentifier
			if(!ridentifier.test(lang||"")){
				Sizzle.error("unsupportedlang:"+lang);
			}
			lang=lang.replace(runescape,funescape).toLowerCase();
			returnfunction(elem){
				varelemLang;
				do{
					if((elemLang=documentIsHTML?
						elem.lang:
						elem.getAttribute("xml:lang")||elem.getAttribute("lang"))){

						elemLang=elemLang.toLowerCase();
						returnelemLang===lang||elemLang.indexOf(lang+"-")===0;
					}
				}while((elem=elem.parentNode)&&elem.nodeType===1);
				returnfalse;
			};
		}),

		//Miscellaneous
		"target":function(elem){
			varhash=window.location&&window.location.hash;
			returnhash&&hash.slice(1)===elem.id;
		},

		"root":function(elem){
			returnelem===docElem;
		},

		"focus":function(elem){
			returnelem===document.activeElement&&(!document.hasFocus||document.hasFocus())&&!!(elem.type||elem.href||~elem.tabIndex);
		},

		//Booleanproperties
		"enabled":createDisabledPseudo(false),
		"disabled":createDisabledPseudo(true),

		"checked":function(elem){
			//InCSS3,:checkedshouldreturnbothcheckedandselectedelements
			//http://www.w3.org/TR/2011/REC-css3-selectors-20110929/#checked
			varnodeName=elem.nodeName.toLowerCase();
			return(nodeName==="input"&&!!elem.checked)||(nodeName==="option"&&!!elem.selected);
		},

		"selected":function(elem){
			//Accessingthispropertymakesselected-by-default
			//optionsinSafariworkproperly
			if(elem.parentNode){
				elem.parentNode.selectedIndex;
			}

			returnelem.selected===true;
		},

		//Contents
		"empty":function(elem){
			//http://www.w3.org/TR/selectors/#empty-pseudo
			//:emptyisnegatedbyelement(1)orcontentnodes(text:3;cdata:4;entityref:5),
			//  butnotbyothers(comment:8;processinginstruction:7;etc.)
			//nodeType<6worksbecauseattributes(2)donotappearaschildren
			for(elem=elem.firstChild;elem;elem=elem.nextSibling){
				if(elem.nodeType<6){
					returnfalse;
				}
			}
			returntrue;
		},

		"parent":function(elem){
			return!Expr.pseudos["empty"](elem);
		},

		//Element/inputtypes
		"header":function(elem){
			returnrheader.test(elem.nodeName);
		},

		"input":function(elem){
			returnrinputs.test(elem.nodeName);
		},

		"button":function(elem){
			varname=elem.nodeName.toLowerCase();
			returnname==="input"&&elem.type==="button"||name==="button";
		},

		"text":function(elem){
			varattr;
			returnelem.nodeName.toLowerCase()==="input"&&
				elem.type==="text"&&

				//Support:IE<8
				//NewHTML5attributevalues(e.g.,"search")appearwithelem.type==="text"
				((attr=elem.getAttribute("type"))==null||attr.toLowerCase()==="text");
		},

		//Position-in-collection
		"first":createPositionalPseudo(function(){
			return[0];
		}),

		"last":createPositionalPseudo(function(matchIndexes,length){
			return[length-1];
		}),

		"eq":createPositionalPseudo(function(matchIndexes,length,argument){
			return[argument<0?argument+length:argument];
		}),

		"even":createPositionalPseudo(function(matchIndexes,length){
			vari=0;
			for(;i<length;i+=2){
				matchIndexes.push(i);
			}
			returnmatchIndexes;
		}),

		"odd":createPositionalPseudo(function(matchIndexes,length){
			vari=1;
			for(;i<length;i+=2){
				matchIndexes.push(i);
			}
			returnmatchIndexes;
		}),

		"lt":createPositionalPseudo(function(matchIndexes,length,argument){
			vari=argument<0?argument+length:argument;
			for(;--i>=0;){
				matchIndexes.push(i);
			}
			returnmatchIndexes;
		}),

		"gt":createPositionalPseudo(function(matchIndexes,length,argument){
			vari=argument<0?argument+length:argument;
			for(;++i<length;){
				matchIndexes.push(i);
			}
			returnmatchIndexes;
		})
	}
};

Expr.pseudos["nth"]=Expr.pseudos["eq"];

//Addbutton/inputtypepseudos
for(iin{radio:true,checkbox:true,file:true,password:true,image:true}){
	Expr.pseudos[i]=createInputPseudo(i);
}
for(iin{submit:true,reset:true}){
	Expr.pseudos[i]=createButtonPseudo(i);
}

//EasyAPIforcreatingnewsetFilters
functionsetFilters(){}
setFilters.prototype=Expr.filters=Expr.pseudos;
Expr.setFilters=newsetFilters();

tokenize=Sizzle.tokenize=function(selector,parseOnly){
	varmatched,match,tokens,type,
		soFar,groups,preFilters,
		cached=tokenCache[selector+""];

	if(cached){
		returnparseOnly?0:cached.slice(0);
	}

	soFar=selector;
	groups=[];
	preFilters=Expr.preFilter;

	while(soFar){

		//Commaandfirstrun
		if(!matched||(match=rcomma.exec(soFar))){
			if(match){
				//Don'tconsumetrailingcommasasvalid
				soFar=soFar.slice(match[0].length)||soFar;
			}
			groups.push((tokens=[]));
		}

		matched=false;

		//Combinators
		if((match=rcombinators.exec(soFar))){
			matched=match.shift();
			tokens.push({
				value:matched,
				//Castdescendantcombinatorstospace
				type:match[0].replace(rtrim,"")
			});
			soFar=soFar.slice(matched.length);
		}

		//Filters
		for(typeinExpr.filter){
			if((match=matchExpr[type].exec(soFar))&&(!preFilters[type]||
				(match=preFilters[type](match)))){
				matched=match.shift();
				tokens.push({
					value:matched,
					type:type,
					matches:match
				});
				soFar=soFar.slice(matched.length);
			}
		}

		if(!matched){
			break;
		}
	}

	//Returnthelengthoftheinvalidexcess
	//ifwe'rejustparsing
	//Otherwise,throwanerrororreturntokens
	returnparseOnly?
		soFar.length:
		soFar?
			Sizzle.error(selector):
			//Cachethetokens
			tokenCache(selector,groups).slice(0);
};

functiontoSelector(tokens){
	vari=0,
		len=tokens.length,
		selector="";
	for(;i<len;i++){
		selector+=tokens[i].value;
	}
	returnselector;
}

functionaddCombinator(matcher,combinator,base){
	vardir=combinator.dir,
		skip=combinator.next,
		key=skip||dir,
		checkNonElements=base&&key==="parentNode",
		doneName=done++;

	returncombinator.first?
		//Checkagainstclosestancestor/precedingelement
		function(elem,context,xml){
			while((elem=elem[dir])){
				if(elem.nodeType===1||checkNonElements){
					returnmatcher(elem,context,xml);
				}
			}
			returnfalse;
		}:

		//Checkagainstallancestor/precedingelements
		function(elem,context,xml){
			varoldCache,uniqueCache,outerCache,
				newCache=[dirruns,doneName];

			//Wecan'tsetarbitrarydataonXMLnodes,sotheydon'tbenefitfromcombinatorcaching
			if(xml){
				while((elem=elem[dir])){
					if(elem.nodeType===1||checkNonElements){
						if(matcher(elem,context,xml)){
							returntrue;
						}
					}
				}
			}else{
				while((elem=elem[dir])){
					if(elem.nodeType===1||checkNonElements){
						outerCache=elem[expando]||(elem[expando]={});

						//Support:IE<9only
						//Defendagainstclonedattroperties(jQuerygh-1709)
						uniqueCache=outerCache[elem.uniqueID]||(outerCache[elem.uniqueID]={});

						if(skip&&skip===elem.nodeName.toLowerCase()){
							elem=elem[dir]||elem;
						}elseif((oldCache=uniqueCache[key])&&
							oldCache[0]===dirruns&&oldCache[1]===doneName){

							//AssigntonewCachesoresultsback-propagatetopreviouselements
							return(newCache[2]=oldCache[2]);
						}else{
							//Reusenewcachesoresultsback-propagatetopreviouselements
							uniqueCache[key]=newCache;

							//Amatchmeanswe'redone;afailmeanswehavetokeepchecking
							if((newCache[2]=matcher(elem,context,xml))){
								returntrue;
							}
						}
					}
				}
			}
			returnfalse;
		};
}

functionelementMatcher(matchers){
	returnmatchers.length>1?
		function(elem,context,xml){
			vari=matchers.length;
			while(i--){
				if(!matchers[i](elem,context,xml)){
					returnfalse;
				}
			}
			returntrue;
		}:
		matchers[0];
}

functionmultipleContexts(selector,contexts,results){
	vari=0,
		len=contexts.length;
	for(;i<len;i++){
		Sizzle(selector,contexts[i],results);
	}
	returnresults;
}

functioncondense(unmatched,map,filter,context,xml){
	varelem,
		newUnmatched=[],
		i=0,
		len=unmatched.length,
		mapped=map!=null;

	for(;i<len;i++){
		if((elem=unmatched[i])){
			if(!filter||filter(elem,context,xml)){
				newUnmatched.push(elem);
				if(mapped){
					map.push(i);
				}
			}
		}
	}

	returnnewUnmatched;
}

functionsetMatcher(preFilter,selector,matcher,postFilter,postFinder,postSelector){
	if(postFilter&&!postFilter[expando]){
		postFilter=setMatcher(postFilter);
	}
	if(postFinder&&!postFinder[expando]){
		postFinder=setMatcher(postFinder,postSelector);
	}
	returnmarkFunction(function(seed,results,context,xml){
		vartemp,i,elem,
			preMap=[],
			postMap=[],
			preexisting=results.length,

			//Getinitialelementsfromseedorcontext
			elems=seed||multipleContexts(selector||"*",context.nodeType?[context]:context,[]),

			//Prefiltertogetmatcherinput,preservingamapforseed-resultssynchronization
			matcherIn=preFilter&&(seed||!selector)?
				condense(elems,preMap,preFilter,context,xml):
				elems,

			matcherOut=matcher?
				//IfwehaveapostFinder,orfilteredseed,ornon-seedpostFilterorpreexistingresults,
				postFinder||(seed?preFilter:preexisting||postFilter)?

					//...intermediateprocessingisnecessary
					[]:

					//...otherwiseuseresultsdirectly
					results:
				matcherIn;

		//Findprimarymatches
		if(matcher){
			matcher(matcherIn,matcherOut,context,xml);
		}

		//ApplypostFilter
		if(postFilter){
			temp=condense(matcherOut,postMap);
			postFilter(temp,[],context,xml);

			//Un-matchfailingelementsbymovingthembacktomatcherIn
			i=temp.length;
			while(i--){
				if((elem=temp[i])){
					matcherOut[postMap[i]]=!(matcherIn[postMap[i]]=elem);
				}
			}
		}

		if(seed){
			if(postFinder||preFilter){
				if(postFinder){
					//GetthefinalmatcherOutbycondensingthisintermediateintopostFindercontexts
					temp=[];
					i=matcherOut.length;
					while(i--){
						if((elem=matcherOut[i])){
							//RestorematcherInsinceelemisnotyetafinalmatch
							temp.push((matcherIn[i]=elem));
						}
					}
					postFinder(null,(matcherOut=[]),temp,xml);
				}

				//Movematchedelementsfromseedtoresultstokeepthemsynchronized
				i=matcherOut.length;
				while(i--){
					if((elem=matcherOut[i])&&
						(temp=postFinder?indexOf(seed,elem):preMap[i])>-1){

						seed[temp]=!(results[temp]=elem);
					}
				}
			}

		//Addelementstoresults,throughpostFinderifdefined
		}else{
			matcherOut=condense(
				matcherOut===results?
					matcherOut.splice(preexisting,matcherOut.length):
					matcherOut
			);
			if(postFinder){
				postFinder(null,results,matcherOut,xml);
			}else{
				push.apply(results,matcherOut);
			}
		}
	});
}

functionmatcherFromTokens(tokens){
	varcheckContext,matcher,j,
		len=tokens.length,
		leadingRelative=Expr.relative[tokens[0].type],
		implicitRelative=leadingRelative||Expr.relative[""],
		i=leadingRelative?1:0,

		//Thefoundationalmatcherensuresthatelementsarereachablefromtop-levelcontext(s)
		matchContext=addCombinator(function(elem){
			returnelem===checkContext;
		},implicitRelative,true),
		matchAnyContext=addCombinator(function(elem){
			returnindexOf(checkContext,elem)>-1;
		},implicitRelative,true),
		matchers=[function(elem,context,xml){
			varret=(!leadingRelative&&(xml||context!==outermostContext))||(
				(checkContext=context).nodeType?
					matchContext(elem,context,xml):
					matchAnyContext(elem,context,xml));
			//Avoidhangingontoelement(issue#299)
			checkContext=null;
			returnret;
		}];

	for(;i<len;i++){
		if((matcher=Expr.relative[tokens[i].type])){
			matchers=[addCombinator(elementMatcher(matchers),matcher)];
		}else{
			matcher=Expr.filter[tokens[i].type].apply(null,tokens[i].matches);

			//Returnspecialuponseeingapositionalmatcher
			if(matcher[expando]){
				//Findthenextrelativeoperator(ifany)forproperhandling
				j=++i;
				for(;j<len;j++){
					if(Expr.relative[tokens[j].type]){
						break;
					}
				}
				returnsetMatcher(
					i>1&&elementMatcher(matchers),
					i>1&&toSelector(
						//Iftheprecedingtokenwasadescendantcombinator,insertanimplicitany-element`*`
						tokens.slice(0,i-1).concat({value:tokens[i-2].type===""?"*":""})
					).replace(rtrim,"$1"),
					matcher,
					i<j&&matcherFromTokens(tokens.slice(i,j)),
					j<len&&matcherFromTokens((tokens=tokens.slice(j))),
					j<len&&toSelector(tokens)
				);
			}
			matchers.push(matcher);
		}
	}

	returnelementMatcher(matchers);
}

functionmatcherFromGroupMatchers(elementMatchers,setMatchers){
	varbySet=setMatchers.length>0,
		byElement=elementMatchers.length>0,
		superMatcher=function(seed,context,xml,results,outermost){
			varelem,j,matcher,
				matchedCount=0,
				i="0",
				unmatched=seed&&[],
				setMatched=[],
				contextBackup=outermostContext,
				//Wemustalwayshaveeitherseedelementsoroutermostcontext
				elems=seed||byElement&&Expr.find["TAG"]("*",outermost),
				//Useintegerdirrunsiffthisistheoutermostmatcher
				dirrunsUnique=(dirruns+=contextBackup==null?1:Math.random()||0.1),
				len=elems.length;

			if(outermost){
				outermostContext=context===document||context||outermost;
			}

			//AddelementspassingelementMatchersdirectlytoresults
			//Support:IE<9,Safari
			//TolerateNodeListproperties(IE:"length";Safari:<number>)matchingelementsbyid
			for(;i!==len&&(elem=elems[i])!=null;i++){
				if(byElement&&elem){
					j=0;
					if(!context&&elem.ownerDocument!==document){
						setDocument(elem);
						xml=!documentIsHTML;
					}
					while((matcher=elementMatchers[j++])){
						if(matcher(elem,context||document,xml)){
							results.push(elem);
							break;
						}
					}
					if(outermost){
						dirruns=dirrunsUnique;
					}
				}

				//Trackunmatchedelementsforsetfilters
				if(bySet){
					//Theywillhavegonethroughallpossiblematchers
					if((elem=!matcher&&elem)){
						matchedCount--;
					}

					//Lengthenthearrayforeveryelement,matchedornot
					if(seed){
						unmatched.push(elem);
					}
				}
			}

			//`i`isnowthecountofelementsvisitedabove,andaddingitto`matchedCount`
			//makesthelatternonnegative.
			matchedCount+=i;

			//Applysetfilterstounmatchedelements
			//NOTE:Thiscanbeskippediftherearenounmatchedelements(i.e.,`matchedCount`
			//equals`i`),unlesswedidn'tvisit_any_elementsintheaboveloopbecausewehave
			//noelementmatchersandnoseed.
			//Incrementinganinitially-string"0"`i`allows`i`toremainastringonlyinthat
			//case,whichwillresultina"00"`matchedCount`thatdiffersfrom`i`butisalso
			//numericallyzero.
			if(bySet&&i!==matchedCount){
				j=0;
				while((matcher=setMatchers[j++])){
					matcher(unmatched,setMatched,context,xml);
				}

				if(seed){
					//Reintegrateelementmatchestoeliminatetheneedforsorting
					if(matchedCount>0){
						while(i--){
							if(!(unmatched[i]||setMatched[i])){
								setMatched[i]=pop.call(results);
							}
						}
					}

					//Discardindexplaceholdervaluestogetonlyactualmatches
					setMatched=condense(setMatched);
				}

				//Addmatchestoresults
				push.apply(results,setMatched);

				//Seedlesssetmatchessucceedingmultiplesuccessfulmatchersstipulatesorting
				if(outermost&&!seed&&setMatched.length>0&&
					(matchedCount+setMatchers.length)>1){

					Sizzle.uniqueSort(results);
				}
			}

			//Overridemanipulationofglobalsbynestedmatchers
			if(outermost){
				dirruns=dirrunsUnique;
				outermostContext=contextBackup;
			}

			returnunmatched;
		};

	returnbySet?
		markFunction(superMatcher):
		superMatcher;
}

compile=Sizzle.compile=function(selector,match/*InternalUseOnly*/){
	vari,
		setMatchers=[],
		elementMatchers=[],
		cached=compilerCache[selector+""];

	if(!cached){
		//Generateafunctionofrecursivefunctionsthatcanbeusedtocheckeachelement
		if(!match){
			match=tokenize(selector);
		}
		i=match.length;
		while(i--){
			cached=matcherFromTokens(match[i]);
			if(cached[expando]){
				setMatchers.push(cached);
			}else{
				elementMatchers.push(cached);
			}
		}

		//Cachethecompiledfunction
		cached=compilerCache(selector,matcherFromGroupMatchers(elementMatchers,setMatchers));

		//Saveselectorandtokenization
		cached.selector=selector;
	}
	returncached;
};

/**
 *Alow-levelselectionfunctionthatworkswithSizzle'scompiled
 * selectorfunctions
 *@param{String|Function}selectorAselectororapre-compiled
 * selectorfunctionbuiltwithSizzle.compile
 *@param{Element}context
 *@param{Array}[results]
 *@param{Array}[seed]Asetofelementstomatchagainst
 */
select=Sizzle.select=function(selector,context,results,seed){
	vari,tokens,token,type,find,
		compiled=typeofselector==="function"&&selector,
		match=!seed&&tokenize((selector=compiled.selector||selector));

	results=results||[];

	//Trytominimizeoperationsifthereisonlyoneselectorinthelistandnoseed
	//(thelatterofwhichguaranteesuscontext)
	if(match.length===1){

		//ReducecontextiftheleadingcompoundselectorisanID
		tokens=match[0]=match[0].slice(0);
		if(tokens.length>2&&(token=tokens[0]).type==="ID"&&
				context.nodeType===9&&documentIsHTML&&Expr.relative[tokens[1].type]){

			context=(Expr.find["ID"](token.matches[0].replace(runescape,funescape),context)||[])[0];
			if(!context){
				returnresults;

			//Precompiledmatcherswillstillverifyancestry,sostepupalevel
			}elseif(compiled){
				context=context.parentNode;
			}

			selector=selector.slice(tokens.shift().value.length);
		}

		//Fetchaseedsetforright-to-leftmatching
		i=matchExpr["needsContext"].test(selector)?0:tokens.length;
		while(i--){
			token=tokens[i];

			//Abortifwehitacombinator
			if(Expr.relative[(type=token.type)]){
				break;
			}
			if((find=Expr.find[type])){
				//Search,expandingcontextforleadingsiblingcombinators
				if((seed=find(
					token.matches[0].replace(runescape,funescape),
					rsibling.test(tokens[0].type)&&testContext(context.parentNode)||context
				))){

					//Ifseedisemptyornotokensremain,wecanreturnearly
					tokens.splice(i,1);
					selector=seed.length&&toSelector(tokens);
					if(!selector){
						push.apply(results,seed);
						returnresults;
					}

					break;
				}
			}
		}
	}

	//Compileandexecuteafilteringfunctionifoneisnotprovided
	//Provide`match`toavoidretokenizationifwemodifiedtheselectorabove
	(compiled||compile(selector,match))(
		seed,
		context,
		!documentIsHTML,
		results,
		!context||rsibling.test(selector)&&testContext(context.parentNode)||context
	);
	returnresults;
};

//One-timeassignments

//Sortstability
support.sortStable=expando.split("").sort(sortOrder).join("")===expando;

//Support:Chrome14-35+
//Alwaysassumeduplicatesiftheyaren'tpassedtothecomparisonfunction
support.detectDuplicates=!!hasDuplicate;

//Initializeagainstthedefaultdocument
setDocument();

//Support:Webkit<537.32-Safari6.0.3/Chrome25(fixedinChrome27)
//Detachednodesconfoundinglyfollow*eachother*
support.sortDetached=assert(function(el){
	//Shouldreturn1,butreturns4(following)
	returnel.compareDocumentPosition(document.createElement("fieldset"))&1;
});

//Support:IE<8
//Preventattribute/property"interpolation"
//https://msdn.microsoft.com/en-us/library/ms536429%28VS.85%29.aspx
if(!assert(function(el){
	el.innerHTML="<ahref='#'></a>";
	returnel.firstChild.getAttribute("href")==="#";
})){
	addHandle("type|href|height|width",function(elem,name,isXML){
		if(!isXML){
			returnelem.getAttribute(name,name.toLowerCase()==="type"?1:2);
		}
	});
}

//Support:IE<9
//UsedefaultValueinplaceofgetAttribute("value")
if(!support.attributes||!assert(function(el){
	el.innerHTML="<input/>";
	el.firstChild.setAttribute("value","");
	returnel.firstChild.getAttribute("value")==="";
})){
	addHandle("value",function(elem,name,isXML){
		if(!isXML&&elem.nodeName.toLowerCase()==="input"){
			returnelem.defaultValue;
		}
	});
}

//Support:IE<9
//UsegetAttributeNodetofetchbooleanswhengetAttributelies
if(!assert(function(el){
	returnel.getAttribute("disabled")==null;
})){
	addHandle(booleans,function(elem,name,isXML){
		varval;
		if(!isXML){
			returnelem[name]===true?name.toLowerCase():
					(val=elem.getAttributeNode(name))&&val.specified?
					val.value:
				null;
		}
	});
}

returnSizzle;

})(window);



jQuery.find=Sizzle;
jQuery.expr=Sizzle.selectors;

//Deprecated
jQuery.expr[":"]=jQuery.expr.pseudos;
jQuery.uniqueSort=jQuery.unique=Sizzle.uniqueSort;
jQuery.text=Sizzle.getText;
jQuery.isXMLDoc=Sizzle.isXML;
jQuery.contains=Sizzle.contains;
jQuery.escapeSelector=Sizzle.escape;




vardir=function(elem,dir,until){
	varmatched=[],
		truncate=until!==undefined;

	while((elem=elem[dir])&&elem.nodeType!==9){
		if(elem.nodeType===1){
			if(truncate&&jQuery(elem).is(until)){
				break;
			}
			matched.push(elem);
		}
	}
	returnmatched;
};


varsiblings=function(n,elem){
	varmatched=[];

	for(;n;n=n.nextSibling){
		if(n.nodeType===1&&n!==elem){
			matched.push(n);
		}
	}

	returnmatched;
};


varrneedsContext=jQuery.expr.match.needsContext;



functionnodeName(elem,name){

  returnelem.nodeName&&elem.nodeName.toLowerCase()===name.toLowerCase();

};
varrsingleTag=(/^<([a-z][^\/\0>:\x20\t\r\n\f]*)[\x20\t\r\n\f]*\/?>(?:<\/\1>|)$/i);



//Implementtheidenticalfunctionalityforfilterandnot
functionwinnow(elements,qualifier,not){
	if(isFunction(qualifier)){
		returnjQuery.grep(elements,function(elem,i){
			return!!qualifier.call(elem,i,elem)!==not;
		});
	}

	//Singleelement
	if(qualifier.nodeType){
		returnjQuery.grep(elements,function(elem){
			return(elem===qualifier)!==not;
		});
	}

	//Arraylikeofelements(jQuery,arguments,Array)
	if(typeofqualifier!=="string"){
		returnjQuery.grep(elements,function(elem){
			return(indexOf.call(qualifier,elem)>-1)!==not;
		});
	}

	//Filtereddirectlyforbothsimpleandcomplexselectors
	returnjQuery.filter(qualifier,elements,not);
}

jQuery.filter=function(expr,elems,not){
	varelem=elems[0];

	if(not){
		expr=":not("+expr+")";
	}

	if(elems.length===1&&elem.nodeType===1){
		returnjQuery.find.matchesSelector(elem,expr)?[elem]:[];
	}

	returnjQuery.find.matches(expr,jQuery.grep(elems,function(elem){
		returnelem.nodeType===1;
	}));
};

jQuery.fn.extend({
	find:function(selector){
		vari,ret,
			len=this.length,
			self=this;

		if(typeofselector!=="string"){
			returnthis.pushStack(jQuery(selector).filter(function(){
				for(i=0;i<len;i++){
					if(jQuery.contains(self[i],this)){
						returntrue;
					}
				}
			}));
		}

		ret=this.pushStack([]);

		for(i=0;i<len;i++){
			jQuery.find(selector,self[i],ret);
		}

		returnlen>1?jQuery.uniqueSort(ret):ret;
	},
	filter:function(selector){
		returnthis.pushStack(winnow(this,selector||[],false));
	},
	not:function(selector){
		returnthis.pushStack(winnow(this,selector||[],true));
	},
	is:function(selector){
		return!!winnow(
			this,

			//Ifthisisapositional/relativeselector,checkmembershipinthereturnedset
			//so$("p:first").is("p:last")won'treturntrueforadocwithtwo"p".
			typeofselector==="string"&&rneedsContext.test(selector)?
				jQuery(selector):
				selector||[],
			false
		).length;
	}
});


//InitializeajQueryobject


//AcentralreferencetotherootjQuery(document)
varrootjQuery,

	//AsimplewaytocheckforHTMLstrings
	//Prioritize#idover<tag>toavoidXSSvialocation.hash(#9521)
	//StrictHTMLrecognition(#11290:muststartwith<)
	//Shortcutsimple#idcaseforspeed
	rquickExpr=/^(?:\s*(<[\w\W]+>)[^>]*|#([\w-]+))$/,

	init=jQuery.fn.init=function(selector,context,root){
		varmatch,elem;

		//HANDLE:$(""),$(null),$(undefined),$(false)
		if(!selector){
			returnthis;
		}

		//Methodinit()acceptsanalternaterootjQuery
		//somigratecansupportjQuery.sub(gh-2101)
		root=root||rootjQuery;

		//HandleHTMLstrings
		if(typeofselector==="string"){
			if(selector[0]==="<"&&
				selector[selector.length-1]===">"&&
				selector.length>=3){

				//Assumethatstringsthatstartandendwith<>areHTMLandskiptheregexcheck
				match=[null,selector,null];

			}else{
				match=rquickExpr.exec(selector);
			}

			//Matchhtmlormakesurenocontextisspecifiedfor#id
			if(match&&(match[1]||!context)){

				//HANDLE:$(html)->$(array)
				if(match[1]){
					context=contextinstanceofjQuery?context[0]:context;

					//Optiontorunscriptsistrueforback-compat
					//IntentionallylettheerrorbethrownifparseHTMLisnotpresent
					jQuery.merge(this,jQuery.parseHTML(
						match[1],
						context&&context.nodeType?context.ownerDocument||context:document,
						true
					));

					//HANDLE:$(html,props)
					if(rsingleTag.test(match[1])&&jQuery.isPlainObject(context)){
						for(matchincontext){

							//Propertiesofcontextarecalledasmethodsifpossible
							if(isFunction(this[match])){
								this[match](context[match]);

							//...andotherwisesetasattributes
							}else{
								this.attr(match,context[match]);
							}
						}
					}

					returnthis;

				//HANDLE:$(#id)
				}else{
					elem=document.getElementById(match[2]);

					if(elem){

						//InjecttheelementdirectlyintothejQueryobject
						this[0]=elem;
						this.length=1;
					}
					returnthis;
				}

			//HANDLE:$(expr,$(...))
			}elseif(!context||context.jquery){
				return(context||root).find(selector);

			//HANDLE:$(expr,context)
			//(whichisjustequivalentto:$(context).find(expr)
			}else{
				returnthis.constructor(context).find(selector);
			}

		//HANDLE:$(DOMElement)
		}elseif(selector.nodeType){
			this[0]=selector;
			this.length=1;
			returnthis;

		//HANDLE:$(function)
		//Shortcutfordocumentready
		}elseif(isFunction(selector)){
			returnroot.ready!==undefined?
				root.ready(selector):

				//Executeimmediatelyifreadyisnotpresent
				selector(jQuery);
		}

		returnjQuery.makeArray(selector,this);
	};

//GivetheinitfunctionthejQueryprototypeforlaterinstantiation
init.prototype=jQuery.fn;

//Initializecentralreference
rootjQuery=jQuery(document);


varrparentsprev=/^(?:parents|prev(?:Until|All))/,

	//Methodsguaranteedtoproduceauniquesetwhenstartingfromauniqueset
	guaranteedUnique={
		children:true,
		contents:true,
		next:true,
		prev:true
	};

jQuery.fn.extend({
	has:function(target){
		vartargets=jQuery(target,this),
			l=targets.length;

		returnthis.filter(function(){
			vari=0;
			for(;i<l;i++){
				if(jQuery.contains(this,targets[i])){
					returntrue;
				}
			}
		});
	},

	closest:function(selectors,context){
		varcur,
			i=0,
			l=this.length,
			matched=[],
			targets=typeofselectors!=="string"&&jQuery(selectors);

		//Positionalselectorsnevermatch,sincethere'sno_selection_context
		if(!rneedsContext.test(selectors)){
			for(;i<l;i++){
				for(cur=this[i];cur&&cur!==context;cur=cur.parentNode){

					//Alwaysskipdocumentfragments
					if(cur.nodeType<11&&(targets?
						targets.index(cur)>-1:

						//Don'tpassnon-elementstoSizzle
						cur.nodeType===1&&
							jQuery.find.matchesSelector(cur,selectors))){

						matched.push(cur);
						break;
					}
				}
			}
		}

		returnthis.pushStack(matched.length>1?jQuery.uniqueSort(matched):matched);
	},

	//Determinethepositionofanelementwithintheset
	index:function(elem){

		//Noargument,returnindexinparent
		if(!elem){
			return(this[0]&&this[0].parentNode)?this.first().prevAll().length:-1;
		}

		//Indexinselector
		if(typeofelem==="string"){
			returnindexOf.call(jQuery(elem),this[0]);
		}

		//Locatethepositionofthedesiredelement
		returnindexOf.call(this,

			//IfitreceivesajQueryobject,thefirstelementisused
			elem.jquery?elem[0]:elem
		);
	},

	add:function(selector,context){
		returnthis.pushStack(
			jQuery.uniqueSort(
				jQuery.merge(this.get(),jQuery(selector,context))
			)
		);
	},

	addBack:function(selector){
		returnthis.add(selector==null?
			this.prevObject:this.prevObject.filter(selector)
		);
	}
});

functionsibling(cur,dir){
	while((cur=cur[dir])&&cur.nodeType!==1){}
	returncur;
}

jQuery.each({
	parent:function(elem){
		varparent=elem.parentNode;
		returnparent&&parent.nodeType!==11?parent:null;
	},
	parents:function(elem){
		returndir(elem,"parentNode");
	},
	parentsUntil:function(elem,i,until){
		returndir(elem,"parentNode",until);
	},
	next:function(elem){
		returnsibling(elem,"nextSibling");
	},
	prev:function(elem){
		returnsibling(elem,"previousSibling");
	},
	nextAll:function(elem){
		returndir(elem,"nextSibling");
	},
	prevAll:function(elem){
		returndir(elem,"previousSibling");
	},
	nextUntil:function(elem,i,until){
		returndir(elem,"nextSibling",until);
	},
	prevUntil:function(elem,i,until){
		returndir(elem,"previousSibling",until);
	},
	siblings:function(elem){
		returnsiblings((elem.parentNode||{}).firstChild,elem);
	},
	children:function(elem){
		returnsiblings(elem.firstChild);
	},
	contents:function(elem){
        if(nodeName(elem,"iframe")){
            returnelem.contentDocument;
        }

        //Support:IE9-11only,iOS7only,AndroidBrowser<=4.3only
        //Treatthetemplateelementasaregularoneinbrowsersthat
        //don'tsupportit.
        if(nodeName(elem,"template")){
            elem=elem.content||elem;
        }

        returnjQuery.merge([],elem.childNodes);
	}
},function(name,fn){
	jQuery.fn[name]=function(until,selector){
		varmatched=jQuery.map(this,fn,until);

		if(name.slice(-5)!=="Until"){
			selector=until;
		}

		if(selector&&typeofselector==="string"){
			matched=jQuery.filter(selector,matched);
		}

		if(this.length>1){

			//Removeduplicates
			if(!guaranteedUnique[name]){
				jQuery.uniqueSort(matched);
			}

			//Reverseorderforparents*andprev-derivatives
			if(rparentsprev.test(name)){
				matched.reverse();
			}
		}

		returnthis.pushStack(matched);
	};
});
varrnothtmlwhite=(/[^\x20\t\r\n\f]+/g);



//ConvertString-formattedoptionsintoObject-formattedones
functioncreateOptions(options){
	varobject={};
	jQuery.each(options.match(rnothtmlwhite)||[],function(_,flag){
		object[flag]=true;
	});
	returnobject;
}

/*
 *Createacallbacklistusingthefollowingparameters:
 *
 *	options:anoptionallistofspace-separatedoptionsthatwillchangehow
 *			thecallbacklistbehavesoramoretraditionaloptionobject
 *
 *Bydefaultacallbacklistwillactlikeaneventcallbacklistandcanbe
 *"fired"multipletimes.
 *
 *Possibleoptions:
 *
 *	once:			willensurethecallbacklistcanonlybefiredonce(likeaDeferred)
 *
 *	memory:			willkeeptrackofpreviousvaluesandwillcallanycallbackadded
 *					afterthelisthasbeenfiredrightawaywiththelatest"memorized"
 *					values(likeaDeferred)
 *
 *	unique:			willensureacallbackcanonlybeaddedonce(noduplicateinthelist)
 *
 *	stopOnFalse:	interruptcallingswhenacallbackreturnsfalse
 *
 */
jQuery.Callbacks=function(options){

	//ConvertoptionsfromString-formattedtoObject-formattedifneeded
	//(wecheckincachefirst)
	options=typeofoptions==="string"?
		createOptions(options):
		jQuery.extend({},options);

	var//Flagtoknowiflistiscurrentlyfiring
		firing,

		//Lastfirevaluefornon-forgettablelists
		memory,

		//Flagtoknowiflistwasalreadyfired
		fired,

		//Flagtopreventfiring
		locked,

		//Actualcallbacklist
		list=[],

		//Queueofexecutiondataforrepeatablelists
		queue=[],

		//Indexofcurrentlyfiringcallback(modifiedbyadd/removeasneeded)
		firingIndex=-1,

		//Firecallbacks
		fire=function(){

			//Enforcesingle-firing
			locked=locked||options.once;

			//Executecallbacksforallpendingexecutions,
			//respectingfiringIndexoverridesandruntimechanges
			fired=firing=true;
			for(;queue.length;firingIndex=-1){
				memory=queue.shift();
				while(++firingIndex<list.length){

					//Runcallbackandcheckforearlytermination
					if(list[firingIndex].apply(memory[0],memory[1])===false&&
						options.stopOnFalse){

						//Jumptoendandforgetthedataso.adddoesn'tre-fire
						firingIndex=list.length;
						memory=false;
					}
				}
			}

			//Forgetthedataifwe'redonewithit
			if(!options.memory){
				memory=false;
			}

			firing=false;

			//Cleanupifwe'redonefiringforgood
			if(locked){

				//Keepanemptylistifwehavedataforfutureaddcalls
				if(memory){
					list=[];

				//Otherwise,thisobjectisspent
				}else{
					list="";
				}
			}
		},

		//ActualCallbacksobject
		self={

			//Addacallbackoracollectionofcallbackstothelist
			add:function(){
				if(list){

					//Ifwehavememoryfromapastrun,weshouldfireafteradding
					if(memory&&!firing){
						firingIndex=list.length-1;
						queue.push(memory);
					}

					(functionadd(args){
						jQuery.each(args,function(_,arg){
							if(isFunction(arg)){
								if(!options.unique||!self.has(arg)){
									list.push(arg);
								}
							}elseif(arg&&arg.length&&toType(arg)!=="string"){

								//Inspectrecursively
								add(arg);
							}
						});
					})(arguments);

					if(memory&&!firing){
						fire();
					}
				}
				returnthis;
			},

			//Removeacallbackfromthelist
			remove:function(){
				jQuery.each(arguments,function(_,arg){
					varindex;
					while((index=jQuery.inArray(arg,list,index))>-1){
						list.splice(index,1);

						//Handlefiringindexes
						if(index<=firingIndex){
							firingIndex--;
						}
					}
				});
				returnthis;
			},

			//Checkifagivencallbackisinthelist.
			//Ifnoargumentisgiven,returnwhetherornotlisthascallbacksattached.
			has:function(fn){
				returnfn?
					jQuery.inArray(fn,list)>-1:
					list.length>0;
			},

			//Removeallcallbacksfromthelist
			empty:function(){
				if(list){
					list=[];
				}
				returnthis;
			},

			//Disable.fireand.add
			//Abortanycurrent/pendingexecutions
			//Clearallcallbacksandvalues
			disable:function(){
				locked=queue=[];
				list=memory="";
				returnthis;
			},
			disabled:function(){
				return!list;
			},

			//Disable.fire
			//Alsodisable.addunlesswehavememory(sinceitwouldhavenoeffect)
			//Abortanypendingexecutions
			lock:function(){
				locked=queue=[];
				if(!memory&&!firing){
					list=memory="";
				}
				returnthis;
			},
			locked:function(){
				return!!locked;
			},

			//Callallcallbackswiththegivencontextandarguments
			fireWith:function(context,args){
				if(!locked){
					args=args||[];
					args=[context,args.slice?args.slice():args];
					queue.push(args);
					if(!firing){
						fire();
					}
				}
				returnthis;
			},

			//Callallthecallbackswiththegivenarguments
			fire:function(){
				self.fireWith(this,arguments);
				returnthis;
			},

			//Toknowifthecallbackshavealreadybeencalledatleastonce
			fired:function(){
				return!!fired;
			}
		};

	returnself;
};


functionIdentity(v){
	returnv;
}
functionThrower(ex){
	throwex;
}

functionadoptValue(value,resolve,reject,noValue){
	varmethod;

	try{

		//Checkforpromiseaspectfirsttoprivilegesynchronousbehavior
		if(value&&isFunction((method=value.promise))){
			method.call(value).done(resolve).fail(reject);

		//Otherthenables
		}elseif(value&&isFunction((method=value.then))){
			method.call(value,resolve,reject);

		//Othernon-thenables
		}else{

			//Control`resolve`argumentsbylettingArray#slicecastboolean`noValue`tointeger:
			//*false:[value].slice(0)=>resolve(value)
			//*true:[value].slice(1)=>resolve()
			resolve.apply(undefined,[value].slice(noValue));
		}

	//ForPromises/A+,convertexceptionsintorejections
	//SincejQuery.whendoesn'tunwrapthenables,wecanskiptheextrachecksappearingin
	//Deferred#thentoconditionallysuppressrejection.
	}catch(value){

		//Support:Android4.0only
		//Strictmodefunctionsinvokedwithout.call/.applygetglobal-objectcontext
		reject.apply(undefined,[value]);
	}
}

jQuery.extend({

	Deferred:function(func){
		vartuples=[

				//action,addlistener,callbacks,
				//....thenhandlers,argumentindex,[finalstate]
				["notify","progress",jQuery.Callbacks("memory"),
					jQuery.Callbacks("memory"),2],
				["resolve","done",jQuery.Callbacks("oncememory"),
					jQuery.Callbacks("oncememory"),0,"resolved"],
				["reject","fail",jQuery.Callbacks("oncememory"),
					jQuery.Callbacks("oncememory"),1,"rejected"]
			],
			state="pending",
			promise={
				state:function(){
					returnstate;
				},
				always:function(){
					deferred.done(arguments).fail(arguments);
					returnthis;
				},
				"catch":function(fn){
					returnpromise.then(null,fn);
				},

				//Keeppipeforback-compat
				pipe:function(/*fnDone,fnFail,fnProgress*/){
					varfns=arguments;

					returnjQuery.Deferred(function(newDefer){
						jQuery.each(tuples,function(i,tuple){

							//Maptuples(progress,done,fail)toarguments(done,fail,progress)
							varfn=isFunction(fns[tuple[4]])&&fns[tuple[4]];

							//deferred.progress(function(){bindtonewDeferornewDefer.notify})
							//deferred.done(function(){bindtonewDeferornewDefer.resolve})
							//deferred.fail(function(){bindtonewDeferornewDefer.reject})
							deferred[tuple[1]](function(){
								varreturned=fn&&fn.apply(this,arguments);
								if(returned&&isFunction(returned.promise)){
									returned.promise()
										.progress(newDefer.notify)
										.done(newDefer.resolve)
										.fail(newDefer.reject);
								}else{
									newDefer[tuple[0]+"With"](
										this,
										fn?[returned]:arguments
									);
								}
							});
						});
						fns=null;
					}).promise();
				},
				then:function(onFulfilled,onRejected,onProgress){
					varmaxDepth=0;
					functionresolve(depth,deferred,handler,special){
						returnfunction(){
							varthat=this,
								args=arguments,
								mightThrow=function(){
									varreturned,then;

									//Support:Promises/A+section2.3.3.3.3
									//https://promisesaplus.com/#point-59
									//Ignoredouble-resolutionattempts
									if(depth<maxDepth){
										return;
									}

									returned=handler.apply(that,args);

									//Support:Promises/A+section2.3.1
									//https://promisesaplus.com/#point-48
									if(returned===deferred.promise()){
										thrownewTypeError("Thenableself-resolution");
									}

									//Support:Promises/A+sections2.3.3.1,3.5
									//https://promisesaplus.com/#point-54
									//https://promisesaplus.com/#point-75
									//Retrieve`then`onlyonce
									then=returned&&

										//Support:Promises/A+section2.3.4
										//https://promisesaplus.com/#point-64
										//Onlycheckobjectsandfunctionsforthenability
										(typeofreturned==="object"||
											typeofreturned==="function")&&
										returned.then;

									//Handleareturnedthenable
									if(isFunction(then)){

										//Specialprocessors(notify)justwaitforresolution
										if(special){
											then.call(
												returned,
												resolve(maxDepth,deferred,Identity,special),
												resolve(maxDepth,deferred,Thrower,special)
											);

										//Normalprocessors(resolve)alsohookintoprogress
										}else{

											//...anddisregardolderresolutionvalues
											maxDepth++;

											then.call(
												returned,
												resolve(maxDepth,deferred,Identity,special),
												resolve(maxDepth,deferred,Thrower,special),
												resolve(maxDepth,deferred,Identity,
													deferred.notifyWith)
											);
										}

									//Handleallotherreturnedvalues
									}else{

										//Onlysubstitutehandlerspassoncontext
										//andmultiplevalues(non-specbehavior)
										if(handler!==Identity){
											that=undefined;
											args=[returned];
										}

										//Processthevalue(s)
										//Defaultprocessisresolve
										(special||deferred.resolveWith)(that,args);
									}
								},

								//Onlynormalprocessors(resolve)catchandrejectexceptions
								process=special?
									mightThrow:
									function(){
										try{
											mightThrow();
										}catch(e){

											if(jQuery.Deferred.exceptionHook){
												jQuery.Deferred.exceptionHook(e,
													process.stackTrace);
											}

											//Support:Promises/A+section2.3.3.3.4.1
											//https://promisesaplus.com/#point-61
											//Ignorepost-resolutionexceptions
											if(depth+1>=maxDepth){

												//Onlysubstitutehandlerspassoncontext
												//andmultiplevalues(non-specbehavior)
												if(handler!==Thrower){
													that=undefined;
													args=[e];
												}

												deferred.rejectWith(that,args);
											}
										}
									};

							//Support:Promises/A+section2.3.3.3.1
							//https://promisesaplus.com/#point-57
							//Re-resolvepromisesimmediatelytododgefalserejectionfrom
							//subsequenterrors
							if(depth){
								process();
							}else{

								//Callanoptionalhooktorecordthestack,incaseofexception
								//sinceit'sotherwiselostwhenexecutiongoesasync
								if(jQuery.Deferred.getStackHook){
									process.stackTrace=jQuery.Deferred.getStackHook();
								}
								window.setTimeout(process);
							}
						};
					}

					returnjQuery.Deferred(function(newDefer){

						//progress_handlers.add(...)
						tuples[0][3].add(
							resolve(
								0,
								newDefer,
								isFunction(onProgress)?
									onProgress:
									Identity,
								newDefer.notifyWith
							)
						);

						//fulfilled_handlers.add(...)
						tuples[1][3].add(
							resolve(
								0,
								newDefer,
								isFunction(onFulfilled)?
									onFulfilled:
									Identity
							)
						);

						//rejected_handlers.add(...)
						tuples[2][3].add(
							resolve(
								0,
								newDefer,
								isFunction(onRejected)?
									onRejected:
									Thrower
							)
						);
					}).promise();
				},

				//Getapromiseforthisdeferred
				//Ifobjisprovided,thepromiseaspectisaddedtotheobject
				promise:function(obj){
					returnobj!=null?jQuery.extend(obj,promise):promise;
				}
			},
			deferred={};

		//Addlist-specificmethods
		jQuery.each(tuples,function(i,tuple){
			varlist=tuple[2],
				stateString=tuple[5];

			//promise.progress=list.add
			//promise.done=list.add
			//promise.fail=list.add
			promise[tuple[1]]=list.add;

			//Handlestate
			if(stateString){
				list.add(
					function(){

						//state="resolved"(i.e.,fulfilled)
						//state="rejected"
						state=stateString;
					},

					//rejected_callbacks.disable
					//fulfilled_callbacks.disable
					tuples[3-i][2].disable,

					//rejected_handlers.disable
					//fulfilled_handlers.disable
					tuples[3-i][3].disable,

					//progress_callbacks.lock
					tuples[0][2].lock,

					//progress_handlers.lock
					tuples[0][3].lock
				);
			}

			//progress_handlers.fire
			//fulfilled_handlers.fire
			//rejected_handlers.fire
			list.add(tuple[3].fire);

			//deferred.notify=function(){deferred.notifyWith(...)}
			//deferred.resolve=function(){deferred.resolveWith(...)}
			//deferred.reject=function(){deferred.rejectWith(...)}
			deferred[tuple[0]]=function(){
				deferred[tuple[0]+"With"](this===deferred?undefined:this,arguments);
				returnthis;
			};

			//deferred.notifyWith=list.fireWith
			//deferred.resolveWith=list.fireWith
			//deferred.rejectWith=list.fireWith
			deferred[tuple[0]+"With"]=list.fireWith;
		});

		//Makethedeferredapromise
		promise.promise(deferred);

		//Callgivenfuncifany
		if(func){
			func.call(deferred,deferred);
		}

		//Alldone!
		returndeferred;
	},

	//Deferredhelper
	when:function(singleValue){
		var

			//countofuncompletedsubordinates
			remaining=arguments.length,

			//countofunprocessedarguments
			i=remaining,

			//subordinatefulfillmentdata
			resolveContexts=Array(i),
			resolveValues=slice.call(arguments),

			//themasterDeferred
			master=jQuery.Deferred(),

			//subordinatecallbackfactory
			updateFunc=function(i){
				returnfunction(value){
					resolveContexts[i]=this;
					resolveValues[i]=arguments.length>1?slice.call(arguments):value;
					if(!(--remaining)){
						master.resolveWith(resolveContexts,resolveValues);
					}
				};
			};

		//Single-andemptyargumentsareadoptedlikePromise.resolve
		if(remaining<=1){
			adoptValue(singleValue,master.done(updateFunc(i)).resolve,master.reject,
				!remaining);

			//Use.then()tounwrapsecondarythenables(cf.gh-3000)
			if(master.state()==="pending"||
				isFunction(resolveValues[i]&&resolveValues[i].then)){

				returnmaster.then();
			}
		}

		//MultipleargumentsareaggregatedlikePromise.allarrayelements
		while(i--){
			adoptValue(resolveValues[i],updateFunc(i),master.reject);
		}

		returnmaster.promise();
	}
});


//Theseusuallyindicateaprogrammermistakeduringdevelopment,
//warnaboutthemASAPratherthanswallowingthembydefault.
varrerrorNames=/^(Eval|Internal|Range|Reference|Syntax|Type|URI)Error$/;

jQuery.Deferred.exceptionHook=function(error,stack){

	//Support:IE8-9only
	//Consoleexistswhendevtoolsareopen,whichcanhappenatanytime
	if(window.console&&window.console.warn&&error&&rerrorNames.test(error.name)){
		window.console.warn("jQuery.Deferredexception:"+error.message,error.stack,stack);
	}
};




jQuery.readyException=function(error){
	window.setTimeout(function(){
		throwerror;
	});
};




//ThedeferredusedonDOMready
varreadyList=jQuery.Deferred();

jQuery.fn.ready=function(fn){

	readyList
		.then(fn)

		//WrapjQuery.readyExceptioninafunctionsothatthelookup
		//happensatthetimeoferrorhandlinginsteadofcallback
		//registration.
		.catch(function(error){
			jQuery.readyException(error);
		});

	returnthis;
};

jQuery.extend({

	//IstheDOMreadytobeused?Settotrueonceitoccurs.
	isReady:false,

	//Acountertotrackhowmanyitemstowaitforbefore
	//thereadyeventfires.See#6781
	readyWait:1,

	//HandlewhentheDOMisready
	ready:function(wait){

		//Abortiftherearependingholdsorwe'realreadyready
		if(wait===true?--jQuery.readyWait:jQuery.isReady){
			return;
		}

		//RememberthattheDOMisready
		jQuery.isReady=true;

		//IfanormalDOMReadyeventfired,decrement,andwaitifneedbe
		if(wait!==true&&--jQuery.readyWait>0){
			return;
		}

		//Iftherearefunctionsbound,toexecute
		readyList.resolveWith(document,[jQuery]);
	}
});

jQuery.ready.then=readyList.then;

//Thereadyeventhandlerandselfcleanupmethod
functioncompleted(){
	document.removeEventListener("DOMContentLoaded",completed);
	window.removeEventListener("load",completed);
	jQuery.ready();
}

//Catchcaseswhere$(document).ready()iscalled
//afterthebrowsereventhasalreadyoccurred.
//Support:IE<=9-10only
//OlderIEsometimessignals"interactive"toosoon
if(document.readyState==="complete"||
	(document.readyState!=="loading"&&!document.documentElement.doScroll)){

	//Handleitasynchronouslytoallowscriptstheopportunitytodelayready
	window.setTimeout(jQuery.ready);

}else{

	//Usethehandyeventcallback
	document.addEventListener("DOMContentLoaded",completed);

	//Afallbacktowindow.onload,thatwillalwayswork
	window.addEventListener("load",completed);
}




//Multifunctionalmethodtogetandsetvaluesofacollection
//Thevalue/scanoptionallybeexecutedifit'safunction
varaccess=function(elems,fn,key,value,chainable,emptyGet,raw){
	vari=0,
		len=elems.length,
		bulk=key==null;

	//Setsmanyvalues
	if(toType(key)==="object"){
		chainable=true;
		for(iinkey){
			access(elems,fn,i,key[i],true,emptyGet,raw);
		}

	//Setsonevalue
	}elseif(value!==undefined){
		chainable=true;

		if(!isFunction(value)){
			raw=true;
		}

		if(bulk){

			//Bulkoperationsrunagainsttheentireset
			if(raw){
				fn.call(elems,value);
				fn=null;

			//...exceptwhenexecutingfunctionvalues
			}else{
				bulk=fn;
				fn=function(elem,key,value){
					returnbulk.call(jQuery(elem),value);
				};
			}
		}

		if(fn){
			for(;i<len;i++){
				fn(
					elems[i],key,raw?
					value:
					value.call(elems[i],i,fn(elems[i],key))
				);
			}
		}
	}

	if(chainable){
		returnelems;
	}

	//Gets
	if(bulk){
		returnfn.call(elems);
	}

	returnlen?fn(elems[0],key):emptyGet;
};


//Matchesdashedstringforcamelizing
varrmsPrefix=/^-ms-/,
	rdashAlpha=/-([a-z])/g;

//UsedbycamelCaseascallbacktoreplace()
functionfcamelCase(all,letter){
	returnletter.toUpperCase();
}

//ConvertdashedtocamelCase;usedbythecssanddatamodules
//Support:IE<=9-11,Edge12-15
//Microsoftforgottohumptheirvendorprefix(#9572)
functioncamelCase(string){
	returnstring.replace(rmsPrefix,"ms-").replace(rdashAlpha,fcamelCase);
}
varacceptData=function(owner){

	//Acceptsonly:
	// -Node
	//   -Node.ELEMENT_NODE
	//   -Node.DOCUMENT_NODE
	// -Object
	//   -Any
	returnowner.nodeType===1||owner.nodeType===9||!(+owner.nodeType);
};




functionData(){
	this.expando=jQuery.expando+Data.uid++;
}

Data.uid=1;

Data.prototype={

	cache:function(owner){

		//Checkiftheownerobjectalreadyhasacache
		varvalue=owner[this.expando];

		//Ifnot,createone
		if(!value){
			value={};

			//Wecanacceptdatafornon-elementnodesinmodernbrowsers,
			//butweshouldnot,see#8335.
			//Alwaysreturnanemptyobject.
			if(acceptData(owner)){

				//Ifitisanodeunlikelytobestringify-edorloopedover
				//useplainassignment
				if(owner.nodeType){
					owner[this.expando]=value;

				//Otherwisesecureitinanon-enumerableproperty
				//configurablemustbetruetoallowthepropertytobe
				//deletedwhendataisremoved
				}else{
					Object.defineProperty(owner,this.expando,{
						value:value,
						configurable:true
					});
				}
			}
		}

		returnvalue;
	},
	set:function(owner,data,value){
		varprop,
			cache=this.cache(owner);

		//Handle:[owner,key,value]args
		//AlwaysusecamelCasekey(gh-2257)
		if(typeofdata==="string"){
			cache[camelCase(data)]=value;

		//Handle:[owner,{properties}]args
		}else{

			//Copythepropertiesone-by-onetothecacheobject
			for(propindata){
				cache[camelCase(prop)]=data[prop];
			}
		}
		returncache;
	},
	get:function(owner,key){
		returnkey===undefined?
			this.cache(owner):

			//AlwaysusecamelCasekey(gh-2257)
			owner[this.expando]&&owner[this.expando][camelCase(key)];
	},
	access:function(owner,key,value){

		//Incaseswhereeither:
		//
		//  1.Nokeywasspecified
		//  2.Astringkeywasspecified,butnovalueprovided
		//
		//Takethe"read"pathandallowthegetmethodtodetermine
		//whichvaluetoreturn,respectivelyeither:
		//
		//  1.Theentirecacheobject
		//  2.Thedatastoredatthekey
		//
		if(key===undefined||
				((key&&typeofkey==="string")&&value===undefined)){

			returnthis.get(owner,key);
		}

		//Whenthekeyisnotastring,orbothakeyandvalue
		//arespecified,setorextend(existingobjects)witheither:
		//
		//  1.Anobjectofproperties
		//  2.Akeyandvalue
		//
		this.set(owner,key,value);

		//Sincethe"set"pathcanhavetwopossibleentrypoints
		//returntheexpecteddatabasedonwhichpathwastaken[*]
		returnvalue!==undefined?value:key;
	},
	remove:function(owner,key){
		vari,
			cache=owner[this.expando];

		if(cache===undefined){
			return;
		}

		if(key!==undefined){

			//Supportarrayorspaceseparatedstringofkeys
			if(Array.isArray(key)){

				//Ifkeyisanarrayofkeys...
				//WealwayssetcamelCasekeys,soremovethat.
				key=key.map(camelCase);
			}else{
				key=camelCase(key);

				//Ifakeywiththespacesexists,useit.
				//Otherwise,createanarraybymatchingnon-whitespace
				key=keyincache?
					[key]:
					(key.match(rnothtmlwhite)||[]);
			}

			i=key.length;

			while(i--){
				deletecache[key[i]];
			}
		}

		//Removetheexpandoifthere'snomoredata
		if(key===undefined||jQuery.isEmptyObject(cache)){

			//Support:Chrome<=35-45
			//Webkit&Blinkperformancesufferswhendeletingproperties
			//fromDOMnodes,sosettoundefinedinstead
			//https://bugs.chromium.org/p/chromium/issues/detail?id=378607(bugrestricted)
			if(owner.nodeType){
				owner[this.expando]=undefined;
			}else{
				deleteowner[this.expando];
			}
		}
	},
	hasData:function(owner){
		varcache=owner[this.expando];
		returncache!==undefined&&!jQuery.isEmptyObject(cache);
	}
};
vardataPriv=newData();

vardataUser=newData();



//	ImplementationSummary
//
//	1.EnforceAPIsurfaceandsemanticcompatibilitywith1.9.xbranch
//	2.Improvethemodule'smaintainabilitybyreducingthestorage
//		pathstoasinglemechanism.
//	3.Usethesamesinglemechanismtosupport"private"and"user"data.
//	4._Never_expose"private"datatousercode(TODO:Drop_data,_removeData)
//	5.Avoidexposingimplementationdetailsonuserobjects(eg.expandoproperties)
//	6.ProvideaclearpathforimplementationupgradetoWeakMapin2014

varrbrace=/^(?:\{[\w\W]*\}|\[[\w\W]*\])$/,
	rmultiDash=/[A-Z]/g;

functiongetData(data){
	if(data==="true"){
		returntrue;
	}

	if(data==="false"){
		returnfalse;
	}

	if(data==="null"){
		returnnull;
	}

	//Onlyconverttoanumberifitdoesn'tchangethestring
	if(data===+data+""){
		return+data;
	}

	if(rbrace.test(data)){
		returnJSON.parse(data);
	}

	returndata;
}

functiondataAttr(elem,key,data){
	varname;

	//Ifnothingwasfoundinternally,trytofetchany
	//datafromtheHTML5data-*attribute
	if(data===undefined&&elem.nodeType===1){
		name="data-"+key.replace(rmultiDash,"-$&").toLowerCase();
		data=elem.getAttribute(name);

		if(typeofdata==="string"){
			try{
				data=getData(data);
			}catch(e){}

			//Makesurewesetthedatasoitisn'tchangedlater
			dataUser.set(elem,key,data);
		}else{
			data=undefined;
		}
	}
	returndata;
}

jQuery.extend({
	hasData:function(elem){
		returndataUser.hasData(elem)||dataPriv.hasData(elem);
	},

	data:function(elem,name,data){
		returndataUser.access(elem,name,data);
	},

	removeData:function(elem,name){
		dataUser.remove(elem,name);
	},

	//TODO:Nowthatallcallsto_dataand_removeDatahavebeenreplaced
	//withdirectcallstodataPrivmethods,thesecanbedeprecated.
	_data:function(elem,name,data){
		returndataPriv.access(elem,name,data);
	},

	_removeData:function(elem,name){
		dataPriv.remove(elem,name);
	}
});

jQuery.fn.extend({
	data:function(key,value){
		vari,name,data,
			elem=this[0],
			attrs=elem&&elem.attributes;

		//Getsallvalues
		if(key===undefined){
			if(this.length){
				data=dataUser.get(elem);

				if(elem.nodeType===1&&!dataPriv.get(elem,"hasDataAttrs")){
					i=attrs.length;
					while(i--){

						//Support:IE11only
						//Theattrselementscanbenull(#14894)
						if(attrs[i]){
							name=attrs[i].name;
							if(name.indexOf("data-")===0){
								name=camelCase(name.slice(5));
								dataAttr(elem,name,data[name]);
							}
						}
					}
					dataPriv.set(elem,"hasDataAttrs",true);
				}
			}

			returndata;
		}

		//Setsmultiplevalues
		if(typeofkey==="object"){
			returnthis.each(function(){
				dataUser.set(this,key);
			});
		}

		returnaccess(this,function(value){
			vardata;

			//ThecallingjQueryobject(elementmatches)isnotempty
			//(andthereforehasanelementappearsatthis[0])andthe
			//`value`parameterwasnotundefined.AnemptyjQueryobject
			//willresultin`undefined`forelem=this[0]whichwill
			//throwanexceptionifanattempttoreadadatacacheismade.
			if(elem&&value===undefined){

				//Attempttogetdatafromthecache
				//ThekeywillalwaysbecamelCasedinData
				data=dataUser.get(elem,key);
				if(data!==undefined){
					returndata;
				}

				//Attemptto"discover"thedatain
				//HTML5customdata-*attrs
				data=dataAttr(elem,key);
				if(data!==undefined){
					returndata;
				}

				//Wetriedreallyhard,butthedatadoesn'texist.
				return;
			}

			//Setthedata...
			this.each(function(){

				//WealwaysstorethecamelCasedkey
				dataUser.set(this,key,value);
			});
		},null,value,arguments.length>1,null,true);
	},

	removeData:function(key){
		returnthis.each(function(){
			dataUser.remove(this,key);
		});
	}
});


jQuery.extend({
	queue:function(elem,type,data){
		varqueue;

		if(elem){
			type=(type||"fx")+"queue";
			queue=dataPriv.get(elem,type);

			//Speedupdequeuebygettingoutquicklyifthisisjustalookup
			if(data){
				if(!queue||Array.isArray(data)){
					queue=dataPriv.access(elem,type,jQuery.makeArray(data));
				}else{
					queue.push(data);
				}
			}
			returnqueue||[];
		}
	},

	dequeue:function(elem,type){
		type=type||"fx";

		varqueue=jQuery.queue(elem,type),
			startLength=queue.length,
			fn=queue.shift(),
			hooks=jQuery._queueHooks(elem,type),
			next=function(){
				jQuery.dequeue(elem,type);
			};

		//Ifthefxqueueisdequeued,alwaysremovetheprogresssentinel
		if(fn==="inprogress"){
			fn=queue.shift();
			startLength--;
		}

		if(fn){

			//Addaprogresssentineltopreventthefxqueuefrombeing
			//automaticallydequeued
			if(type==="fx"){
				queue.unshift("inprogress");
			}

			//Clearupthelastqueuestopfunction
			deletehooks.stop;
			fn.call(elem,next,hooks);
		}

		if(!startLength&&hooks){
			hooks.empty.fire();
		}
	},

	//Notpublic-generateaqueueHooksobject,orreturnthecurrentone
	_queueHooks:function(elem,type){
		varkey=type+"queueHooks";
		returndataPriv.get(elem,key)||dataPriv.access(elem,key,{
			empty:jQuery.Callbacks("oncememory").add(function(){
				dataPriv.remove(elem,[type+"queue",key]);
			})
		});
	}
});

jQuery.fn.extend({
	queue:function(type,data){
		varsetter=2;

		if(typeoftype!=="string"){
			data=type;
			type="fx";
			setter--;
		}

		if(arguments.length<setter){
			returnjQuery.queue(this[0],type);
		}

		returndata===undefined?
			this:
			this.each(function(){
				varqueue=jQuery.queue(this,type,data);

				//Ensureahooksforthisqueue
				jQuery._queueHooks(this,type);

				if(type==="fx"&&queue[0]!=="inprogress"){
					jQuery.dequeue(this,type);
				}
			});
	},
	dequeue:function(type){
		returnthis.each(function(){
			jQuery.dequeue(this,type);
		});
	},
	clearQueue:function(type){
		returnthis.queue(type||"fx",[]);
	},

	//Getapromiseresolvedwhenqueuesofacertaintype
	//areemptied(fxisthetypebydefault)
	promise:function(type,obj){
		vartmp,
			count=1,
			defer=jQuery.Deferred(),
			elements=this,
			i=this.length,
			resolve=function(){
				if(!(--count)){
					defer.resolveWith(elements,[elements]);
				}
			};

		if(typeoftype!=="string"){
			obj=type;
			type=undefined;
		}
		type=type||"fx";

		while(i--){
			tmp=dataPriv.get(elements[i],type+"queueHooks");
			if(tmp&&tmp.empty){
				count++;
				tmp.empty.add(resolve);
			}
		}
		resolve();
		returndefer.promise(obj);
	}
});
varpnum=(/[+-]?(?:\d*\.|)\d+(?:[eE][+-]?\d+|)/).source;

varrcssNum=newRegExp("^(?:([+-])=|)("+pnum+")([a-z%]*)$","i");


varcssExpand=["Top","Right","Bottom","Left"];

varisHiddenWithinTree=function(elem,el){

		//isHiddenWithinTreemightbecalledfromjQuery#filterfunction;
		//inthatcase,elementwillbesecondargument
		elem=el||elem;

		//Inlinestyletrumpsall
		returnelem.style.display==="none"||
			elem.style.display===""&&

			//Otherwise,checkcomputedstyle
			//Support:Firefox<=43-45
			//Disconnectedelementscanhavecomputeddisplay:none,sofirstconfirmthatelemis
			//inthedocument.
			jQuery.contains(elem.ownerDocument,elem)&&

			jQuery.css(elem,"display")==="none";
	};

varswap=function(elem,options,callback,args){
	varret,name,
		old={};

	//Remembertheoldvalues,andinsertthenewones
	for(nameinoptions){
		old[name]=elem.style[name];
		elem.style[name]=options[name];
	}

	ret=callback.apply(elem,args||[]);

	//Reverttheoldvalues
	for(nameinoptions){
		elem.style[name]=old[name];
	}

	returnret;
};




functionadjustCSS(elem,prop,valueParts,tween){
	varadjusted,scale,
		maxIterations=20,
		currentValue=tween?
			function(){
				returntween.cur();
			}:
			function(){
				returnjQuery.css(elem,prop,"");
			},
		initial=currentValue(),
		unit=valueParts&&valueParts[3]||(jQuery.cssNumber[prop]?"":"px"),

		//Startingvaluecomputationisrequiredforpotentialunitmismatches
		initialInUnit=(jQuery.cssNumber[prop]||unit!=="px"&&+initial)&&
			rcssNum.exec(jQuery.css(elem,prop));

	if(initialInUnit&&initialInUnit[3]!==unit){

		//Support:Firefox<=54
		//HalvetheiterationtargetvaluetopreventinterferencefromCSSupperbounds(gh-2144)
		initial=initial/2;

		//TrustunitsreportedbyjQuery.css
		unit=unit||initialInUnit[3];

		//Iterativelyapproximatefromanonzerostartingpoint
		initialInUnit=+initial||1;

		while(maxIterations--){

			//Evaluateandupdateourbestguess(doublingguessesthatzeroout).
			//Finishifthescaleequalsorcrosses1(makingtheold*newproductnon-positive).
			jQuery.style(elem,prop,initialInUnit+unit);
			if((1-scale)*(1-(scale=currentValue()/initial||0.5))<=0){
				maxIterations=0;
			}
			initialInUnit=initialInUnit/scale;

		}

		initialInUnit=initialInUnit*2;
		jQuery.style(elem,prop,initialInUnit+unit);

		//Makesureweupdatethetweenpropertieslateron
		valueParts=valueParts||[];
	}

	if(valueParts){
		initialInUnit=+initialInUnit||+initial||0;

		//Applyrelativeoffset(+=/-=)ifspecified
		adjusted=valueParts[1]?
			initialInUnit+(valueParts[1]+1)*valueParts[2]:
			+valueParts[2];
		if(tween){
			tween.unit=unit;
			tween.start=initialInUnit;
			tween.end=adjusted;
		}
	}
	returnadjusted;
}


vardefaultDisplayMap={};

functiongetDefaultDisplay(elem){
	vartemp,
		doc=elem.ownerDocument,
		nodeName=elem.nodeName,
		display=defaultDisplayMap[nodeName];

	if(display){
		returndisplay;
	}

	temp=doc.body.appendChild(doc.createElement(nodeName));
	display=jQuery.css(temp,"display");

	temp.parentNode.removeChild(temp);

	if(display==="none"){
		display="block";
	}
	defaultDisplayMap[nodeName]=display;

	returndisplay;
}

functionshowHide(elements,show){
	vardisplay,elem,
		values=[],
		index=0,
		length=elements.length;

	//Determinenewdisplayvalueforelementsthatneedtochange
	for(;index<length;index++){
		elem=elements[index];
		if(!elem.style){
			continue;
		}

		display=elem.style.display;
		if(show){

			//Sinceweforcevisibilityuponcascade-hiddenelements,animmediate(andslow)
			//checkisrequiredinthisfirstloopunlesswehaveanonemptydisplayvalue(either
			//inlineorabout-to-be-restored)
			if(display==="none"){
				values[index]=dataPriv.get(elem,"display")||null;
				if(!values[index]){
					elem.style.display="";
				}
			}
			if(elem.style.display===""&&isHiddenWithinTree(elem)){
				values[index]=getDefaultDisplay(elem);
			}
		}else{
			if(display!=="none"){
				values[index]="none";

				//Rememberwhatwe'reoverwriting
				dataPriv.set(elem,"display",display);
			}
		}
	}

	//Setthedisplayoftheelementsinasecondlooptoavoidconstantreflow
	for(index=0;index<length;index++){
		if(values[index]!=null){
			elements[index].style.display=values[index];
		}
	}

	returnelements;
}

jQuery.fn.extend({
	show:function(){
		returnshowHide(this,true);
	},
	hide:function(){
		returnshowHide(this);
	},
	toggle:function(state){
		if(typeofstate==="boolean"){
			returnstate?this.show():this.hide();
		}

		returnthis.each(function(){
			if(isHiddenWithinTree(this)){
				jQuery(this).show();
			}else{
				jQuery(this).hide();
			}
		});
	}
});
varrcheckableType=(/^(?:checkbox|radio)$/i);

varrtagName=(/<([a-z][^\/\0>\x20\t\r\n\f]+)/i);

varrscriptType=(/^$|^module$|\/(?:java|ecma)script/i);



//WehavetoclosethesetagstosupportXHTML(#13200)
varwrapMap={

	//Support:IE<=9only
	option:[1,"<selectmultiple='multiple'>","</select>"],

	//XHTMLparsersdonotmagicallyinsertelementsinthe
	//samewaythattagsoupparsersdo.Sowecannotshorten
	//thisbyomitting<tbody>orotherrequiredelements.
	thead:[1,"<table>","</table>"],
	col:[2,"<table><colgroup>","</colgroup></table>"],
	tr:[2,"<table><tbody>","</tbody></table>"],
	td:[3,"<table><tbody><tr>","</tr></tbody></table>"],

	_default:[0,"",""]
};

//Support:IE<=9only
wrapMap.optgroup=wrapMap.option;

wrapMap.tbody=wrapMap.tfoot=wrapMap.colgroup=wrapMap.caption=wrapMap.thead;
wrapMap.th=wrapMap.td;


functiongetAll(context,tag){

	//Support:IE<=9-11only
	//Usetypeoftoavoidzero-argumentmethodinvocationonhostobjects(#15151)
	varret;

	if(typeofcontext.getElementsByTagName!=="undefined"){
		ret=context.getElementsByTagName(tag||"*");

	}elseif(typeofcontext.querySelectorAll!=="undefined"){
		ret=context.querySelectorAll(tag||"*");

	}else{
		ret=[];
	}

	if(tag===undefined||tag&&nodeName(context,tag)){
		returnjQuery.merge([context],ret);
	}

	returnret;
}


//Markscriptsashavingalreadybeenevaluated
functionsetGlobalEval(elems,refElements){
	vari=0,
		l=elems.length;

	for(;i<l;i++){
		dataPriv.set(
			elems[i],
			"globalEval",
			!refElements||dataPriv.get(refElements[i],"globalEval")
		);
	}
}


varrhtml=/<|&#?\w+;/;

functionbuildFragment(elems,context,scripts,selection,ignored){
	varelem,tmp,tag,wrap,contains,j,
		fragment=context.createDocumentFragment(),
		nodes=[],
		i=0,
		l=elems.length;

	for(;i<l;i++){
		elem=elems[i];

		if(elem||elem===0){

			//Addnodesdirectly
			if(toType(elem)==="object"){

				//Support:Android<=4.0only,PhantomJS1only
				//push.apply(_,arraylike)throwsonancientWebKit
				jQuery.merge(nodes,elem.nodeType?[elem]:elem);

			//Convertnon-htmlintoatextnode
			}elseif(!rhtml.test(elem)){
				nodes.push(context.createTextNode(elem));

			//ConverthtmlintoDOMnodes
			}else{
				tmp=tmp||fragment.appendChild(context.createElement("div"));

				//Deserializeastandardrepresentation
				tag=(rtagName.exec(elem)||["",""])[1].toLowerCase();
				wrap=wrapMap[tag]||wrapMap._default;
				tmp.innerHTML=wrap[1]+jQuery.htmlPrefilter(elem)+wrap[2];

				//Descendthroughwrapperstotherightcontent
				j=wrap[0];
				while(j--){
					tmp=tmp.lastChild;
				}

				//Support:Android<=4.0only,PhantomJS1only
				//push.apply(_,arraylike)throwsonancientWebKit
				jQuery.merge(nodes,tmp.childNodes);

				//Rememberthetop-levelcontainer
				tmp=fragment.firstChild;

				//Ensurethecreatednodesareorphaned(#12392)
				tmp.textContent="";
			}
		}
	}

	//Removewrapperfromfragment
	fragment.textContent="";

	i=0;
	while((elem=nodes[i++])){

		//Skipelementsalreadyinthecontextcollection(trac-4087)
		if(selection&&jQuery.inArray(elem,selection)>-1){
			if(ignored){
				ignored.push(elem);
			}
			continue;
		}

		contains=jQuery.contains(elem.ownerDocument,elem);

		//Appendtofragment
		tmp=getAll(fragment.appendChild(elem),"script");

		//Preservescriptevaluationhistory
		if(contains){
			setGlobalEval(tmp);
		}

		//Captureexecutables
		if(scripts){
			j=0;
			while((elem=tmp[j++])){
				if(rscriptType.test(elem.type||"")){
					scripts.push(elem);
				}
			}
		}
	}

	returnfragment;
}


(function(){
	varfragment=document.createDocumentFragment(),
		div=fragment.appendChild(document.createElement("div")),
		input=document.createElement("input");

	//Support:Android4.0-4.3only
	//Checkstatelostifthenameisset(#11217)
	//Support:WindowsWebApps(WWA)
	//`name`and`type`mustuse.setAttributeforWWA(#14901)
	input.setAttribute("type","radio");
	input.setAttribute("checked","checked");
	input.setAttribute("name","t");

	div.appendChild(input);

	//Support:Android<=4.1only
	//OlderWebKitdoesn'tclonecheckedstatecorrectlyinfragments
	support.checkClone=div.cloneNode(true).cloneNode(true).lastChild.checked;

	//Support:IE<=11only
	//Makesuretextarea(andcheckbox)defaultValueisproperlycloned
	div.innerHTML="<textarea>x</textarea>";
	support.noCloneChecked=!!div.cloneNode(true).lastChild.defaultValue;
})();
vardocumentElement=document.documentElement;



var
	rkeyEvent=/^key/,
	rmouseEvent=/^(?:mouse|pointer|contextmenu|drag|drop)|click/,
	rtypenamespace=/^([^.]*)(?:\.(.+)|)/;

functionreturnTrue(){
	returntrue;
}

functionreturnFalse(){
	returnfalse;
}

//Support:IE<=9only
//See#13393formoreinfo
functionsafeActiveElement(){
	try{
		returndocument.activeElement;
	}catch(err){}
}

functionon(elem,types,selector,data,fn,one){
	varorigFn,type;

	//Typescanbeamapoftypes/handlers
	if(typeoftypes==="object"){

		//(types-Object,selector,data)
		if(typeofselector!=="string"){

			//(types-Object,data)
			data=data||selector;
			selector=undefined;
		}
		for(typeintypes){
			on(elem,type,selector,data,types[type],one);
		}
		returnelem;
	}

	if(data==null&&fn==null){

		//(types,fn)
		fn=selector;
		data=selector=undefined;
	}elseif(fn==null){
		if(typeofselector==="string"){

			//(types,selector,fn)
			fn=data;
			data=undefined;
		}else{

			//(types,data,fn)
			fn=data;
			data=selector;
			selector=undefined;
		}
	}
	if(fn===false){
		fn=returnFalse;
	}elseif(!fn){
		returnelem;
	}

	if(one===1){
		origFn=fn;
		fn=function(event){

			//Canuseanemptyset,sinceeventcontainstheinfo
			jQuery().off(event);
			returnorigFn.apply(this,arguments);
		};

		//UsesameguidsocallercanremoveusingorigFn
		fn.guid=origFn.guid||(origFn.guid=jQuery.guid++);
	}
	returnelem.each(function(){
		jQuery.event.add(this,types,fn,data,selector);
	});
}

/*
 *Helperfunctionsformanagingevents--notpartofthepublicinterface.
 *PropstoDeanEdwards'addEventlibraryformanyoftheideas.
 */
jQuery.event={

	global:{},

	add:function(elem,types,handler,data,selector){

		varhandleObjIn,eventHandle,tmp,
			events,t,handleObj,
			special,handlers,type,namespaces,origType,
			elemData=dataPriv.get(elem);

		//Don'tattacheventstonoDataortext/commentnodes(butallowplainobjects)
		if(!elemData){
			return;
		}

		//Callercanpassinanobjectofcustomdatainlieuofthehandler
		if(handler.handler){
			handleObjIn=handler;
			handler=handleObjIn.handler;
			selector=handleObjIn.selector;
		}

		//Ensurethatinvalidselectorsthrowexceptionsatattachtime
		//EvaluateagainstdocumentElementincaseelemisanon-elementnode(e.g.,document)
		if(selector){
			jQuery.find.matchesSelector(documentElement,selector);
		}

		//MakesurethatthehandlerhasauniqueID,usedtofind/removeitlater
		if(!handler.guid){
			handler.guid=jQuery.guid++;
		}

		//Inittheelement'seventstructureandmainhandler,ifthisisthefirst
		if(!(events=elemData.events)){
			events=elemData.events={};
		}
		if(!(eventHandle=elemData.handle)){
			eventHandle=elemData.handle=function(e){

				//DiscardthesecondeventofajQuery.event.trigger()and
				//whenaneventiscalledafterapagehasunloaded
				returntypeofjQuery!=="undefined"&&jQuery.event.triggered!==e.type?
					jQuery.event.dispatch.apply(elem,arguments):undefined;
			};
		}

		//Handlemultipleeventsseparatedbyaspace
		types=(types||"").match(rnothtmlwhite)||[""];
		t=types.length;
		while(t--){
			tmp=rtypenamespace.exec(types[t])||[];
			type=origType=tmp[1];
			namespaces=(tmp[2]||"").split(".").sort();

			//There*must*beatype,noattachingnamespace-onlyhandlers
			if(!type){
				continue;
			}

			//Ifeventchangesitstype,usethespecialeventhandlersforthechangedtype
			special=jQuery.event.special[type]||{};

			//Ifselectordefined,determinespecialeventapitype,otherwisegiventype
			type=(selector?special.delegateType:special.bindType)||type;

			//Updatespecialbasedonnewlyresettype
			special=jQuery.event.special[type]||{};

			//handleObjispassedtoalleventhandlers
			handleObj=jQuery.extend({
				type:type,
				origType:origType,
				data:data,
				handler:handler,
				guid:handler.guid,
				selector:selector,
				needsContext:selector&&jQuery.expr.match.needsContext.test(selector),
				namespace:namespaces.join(".")
			},handleObjIn);

			//Inittheeventhandlerqueueifwe'rethefirst
			if(!(handlers=events[type])){
				handlers=events[type]=[];
				handlers.delegateCount=0;

				//OnlyuseaddEventListenerifthespecialeventshandlerreturnsfalse
				if(!special.setup||
					special.setup.call(elem,data,namespaces,eventHandle)===false){

					if(elem.addEventListener){
						elem.addEventListener(type,eventHandle);
					}
				}
			}

			if(special.add){
				special.add.call(elem,handleObj);

				if(!handleObj.handler.guid){
					handleObj.handler.guid=handler.guid;
				}
			}

			//Addtotheelement'shandlerlist,delegatesinfront
			if(selector){
				handlers.splice(handlers.delegateCount++,0,handleObj);
			}else{
				handlers.push(handleObj);
			}

			//Keeptrackofwhicheventshaveeverbeenused,foreventoptimization
			jQuery.event.global[type]=true;
		}

	},

	//Detachaneventorsetofeventsfromanelement
	remove:function(elem,types,handler,selector,mappedTypes){

		varj,origCount,tmp,
			events,t,handleObj,
			special,handlers,type,namespaces,origType,
			elemData=dataPriv.hasData(elem)&&dataPriv.get(elem);

		if(!elemData||!(events=elemData.events)){
			return;
		}

		//Onceforeachtype.namespaceintypes;typemaybeomitted
		types=(types||"").match(rnothtmlwhite)||[""];
		t=types.length;
		while(t--){
			tmp=rtypenamespace.exec(types[t])||[];
			type=origType=tmp[1];
			namespaces=(tmp[2]||"").split(".").sort();

			//Unbindallevents(onthisnamespace,ifprovided)fortheelement
			if(!type){
				for(typeinevents){
					jQuery.event.remove(elem,type+types[t],handler,selector,true);
				}
				continue;
			}

			special=jQuery.event.special[type]||{};
			type=(selector?special.delegateType:special.bindType)||type;
			handlers=events[type]||[];
			tmp=tmp[2]&&
				newRegExp("(^|\\.)"+namespaces.join("\\.(?:.*\\.|)")+"(\\.|$)");

			//Removematchingevents
			origCount=j=handlers.length;
			while(j--){
				handleObj=handlers[j];

				if((mappedTypes||origType===handleObj.origType)&&
					(!handler||handler.guid===handleObj.guid)&&
					(!tmp||tmp.test(handleObj.namespace))&&
					(!selector||selector===handleObj.selector||
						selector==="**"&&handleObj.selector)){
					handlers.splice(j,1);

					if(handleObj.selector){
						handlers.delegateCount--;
					}
					if(special.remove){
						special.remove.call(elem,handleObj);
					}
				}
			}

			//Removegenericeventhandlerifweremovedsomethingandnomorehandlersexist
			//(avoidspotentialforendlessrecursionduringremovalofspecialeventhandlers)
			if(origCount&&!handlers.length){
				if(!special.teardown||
					special.teardown.call(elem,namespaces,elemData.handle)===false){

					jQuery.removeEvent(elem,type,elemData.handle);
				}

				deleteevents[type];
			}
		}

		//Removedataandtheexpandoifit'snolongerused
		if(jQuery.isEmptyObject(events)){
			dataPriv.remove(elem,"handleevents");
		}
	},

	dispatch:function(nativeEvent){

		//MakeawritablejQuery.Eventfromthenativeeventobject
		varevent=jQuery.event.fix(nativeEvent);

		vari,j,ret,matched,handleObj,handlerQueue,
			args=newArray(arguments.length),
			handlers=(dataPriv.get(this,"events")||{})[event.type]||[],
			special=jQuery.event.special[event.type]||{};

		//Usethefix-edjQuery.Eventratherthanthe(read-only)nativeevent
		args[0]=event;

		for(i=1;i<arguments.length;i++){
			args[i]=arguments[i];
		}

		event.delegateTarget=this;

		//CallthepreDispatchhookforthemappedtype,andletitbailifdesired
		if(special.preDispatch&&special.preDispatch.call(this,event)===false){
			return;
		}

		//Determinehandlers
		handlerQueue=jQuery.event.handlers.call(this,event,handlers);

		//Rundelegatesfirst;theymaywanttostoppropagationbeneathus
		i=0;
		while((matched=handlerQueue[i++])&&!event.isPropagationStopped()){
			event.currentTarget=matched.elem;

			j=0;
			while((handleObj=matched.handlers[j++])&&
				!event.isImmediatePropagationStopped()){

				//Triggeredeventmusteither1)havenonamespace,or2)havenamespace(s)
				//asubsetorequaltothoseintheboundevent(bothcanhavenonamespace).
				if(!event.rnamespace||event.rnamespace.test(handleObj.namespace)){

					event.handleObj=handleObj;
					event.data=handleObj.data;

					ret=((jQuery.event.special[handleObj.origType]||{}).handle||
						handleObj.handler).apply(matched.elem,args);

					if(ret!==undefined){
						if((event.result=ret)===false){
							event.preventDefault();
							event.stopPropagation();
						}
					}
				}
			}
		}

		//CallthepostDispatchhookforthemappedtype
		if(special.postDispatch){
			special.postDispatch.call(this,event);
		}

		returnevent.result;
	},

	handlers:function(event,handlers){
		vari,handleObj,sel,matchedHandlers,matchedSelectors,
			handlerQueue=[],
			delegateCount=handlers.delegateCount,
			cur=event.target;

		//Finddelegatehandlers
		if(delegateCount&&

			//Support:IE<=9
			//Black-holeSVG<use>instancetrees(trac-13180)
			cur.nodeType&&

			//Support:Firefox<=42
			//Suppressspec-violatingclicksindicatinganon-primarypointerbutton(trac-3861)
			//https://www.w3.org/TR/DOM-Level-3-Events/#event-type-click
			//Support:IE11only
			//...butnotarrowkey"clicks"ofradioinputs,whichcanhave`button`-1(gh-2343)
			!(event.type==="click"&&event.button>=1)){

			for(;cur!==this;cur=cur.parentNode||this){

				//Don'tchecknon-elements(#13208)
				//Don'tprocessclicksondisabledelements(#6911,#8165,#11382,#11764)
				if(cur.nodeType===1&&!(event.type==="click"&&cur.disabled===true)){
					matchedHandlers=[];
					matchedSelectors={};
					for(i=0;i<delegateCount;i++){
						handleObj=handlers[i];

						//Don'tconflictwithObject.prototypeproperties(#13203)
						sel=handleObj.selector+"";

						if(matchedSelectors[sel]===undefined){
							matchedSelectors[sel]=handleObj.needsContext?
								jQuery(sel,this).index(cur)>-1:
								jQuery.find(sel,this,null,[cur]).length;
						}
						if(matchedSelectors[sel]){
							matchedHandlers.push(handleObj);
						}
					}
					if(matchedHandlers.length){
						handlerQueue.push({elem:cur,handlers:matchedHandlers});
					}
				}
			}
		}

		//Addtheremaining(directly-bound)handlers
		cur=this;
		if(delegateCount<handlers.length){
			handlerQueue.push({elem:cur,handlers:handlers.slice(delegateCount)});
		}

		returnhandlerQueue;
	},

	addProp:function(name,hook){
		Object.defineProperty(jQuery.Event.prototype,name,{
			enumerable:true,
			configurable:true,

			get:isFunction(hook)?
				function(){
					if(this.originalEvent){
							returnhook(this.originalEvent);
					}
				}:
				function(){
					if(this.originalEvent){
							returnthis.originalEvent[name];
					}
				},

			set:function(value){
				Object.defineProperty(this,name,{
					enumerable:true,
					configurable:true,
					writable:true,
					value:value
				});
			}
		});
	},

	fix:function(originalEvent){
		returnoriginalEvent[jQuery.expando]?
			originalEvent:
			newjQuery.Event(originalEvent);
	},

	special:{
		load:{

			//Preventtriggeredimage.loadeventsfrombubblingtowindow.load
			noBubble:true
		},
		focus:{

			//Firenativeeventifpossiblesoblur/focussequenceiscorrect
			trigger:function(){
				if(this!==safeActiveElement()&&this.focus){
					this.focus();
					returnfalse;
				}
			},
			delegateType:"focusin"
		},
		blur:{
			trigger:function(){
				if(this===safeActiveElement()&&this.blur){
					this.blur();
					returnfalse;
				}
			},
			delegateType:"focusout"
		},
		click:{

			//Forcheckbox,firenativeeventsocheckedstatewillberight
			trigger:function(){
				if(this.type==="checkbox"&&this.click&&nodeName(this,"input")){
					this.click();
					returnfalse;
				}
			},

			//Forcross-browserconsistency,don'tfirenative.click()onlinks
			_default:function(event){
				returnnodeName(event.target,"a");
			}
		},

		beforeunload:{
			postDispatch:function(event){

				//Support:Firefox20+
				//Firefoxdoesn'talertifthereturnValuefieldisnotset.
				if(event.result!==undefined&&event.originalEvent){
					event.originalEvent.returnValue=event.result;
				}
			}
		}
	}
};

jQuery.removeEvent=function(elem,type,handle){

	//This"if"isneededforplainobjects
	if(elem.removeEventListener){
		elem.removeEventListener(type,handle);
	}
};

jQuery.Event=function(src,props){

	//Allowinstantiationwithoutthe'new'keyword
	if(!(thisinstanceofjQuery.Event)){
		returnnewjQuery.Event(src,props);
	}

	//Eventobject
	if(src&&src.type){
		this.originalEvent=src;
		this.type=src.type;

		//Eventsbubblingupthedocumentmayhavebeenmarkedasprevented
		//byahandlerlowerdownthetree;reflectthecorrectvalue.
		this.isDefaultPrevented=src.defaultPrevented||
				src.defaultPrevented===undefined&&

				//Support:Android<=2.3only
				src.returnValue===false?
			returnTrue:
			returnFalse;

		//Createtargetproperties
		//Support:Safari<=6-7only
		//Targetshouldnotbeatextnode(#504,#13143)
		this.target=(src.target&&src.target.nodeType===3)?
			src.target.parentNode:
			src.target;

		this.currentTarget=src.currentTarget;
		this.relatedTarget=src.relatedTarget;

	//Eventtype
	}else{
		this.type=src;
	}

	//Putexplicitlyprovidedpropertiesontotheeventobject
	if(props){
		jQuery.extend(this,props);
	}

	//Createatimestampifincomingeventdoesn'thaveone
	this.timeStamp=src&&src.timeStamp||Date.now();

	//Markitasfixed
	this[jQuery.expando]=true;
};

//jQuery.EventisbasedonDOM3EventsasspecifiedbytheECMAScriptLanguageBinding
//https://www.w3.org/TR/2003/WD-DOM-Level-3-Events-20030331/ecma-script-binding.html
jQuery.Event.prototype={
	constructor:jQuery.Event,
	isDefaultPrevented:returnFalse,
	isPropagationStopped:returnFalse,
	isImmediatePropagationStopped:returnFalse,
	isSimulated:false,

	preventDefault:function(){
		vare=this.originalEvent;

		this.isDefaultPrevented=returnTrue;

		if(e&&!this.isSimulated){
			e.preventDefault();
		}
	},
	stopPropagation:function(){
		vare=this.originalEvent;

		this.isPropagationStopped=returnTrue;

		if(e&&!this.isSimulated){
			e.stopPropagation();
		}
	},
	stopImmediatePropagation:function(){
		vare=this.originalEvent;

		this.isImmediatePropagationStopped=returnTrue;

		if(e&&!this.isSimulated){
			e.stopImmediatePropagation();
		}

		this.stopPropagation();
	}
};

//IncludesallcommoneventpropsincludingKeyEventandMouseEventspecificprops
jQuery.each({
	altKey:true,
	bubbles:true,
	cancelable:true,
	changedTouches:true,
	ctrlKey:true,
	detail:true,
	eventPhase:true,
	metaKey:true,
	pageX:true,
	pageY:true,
	shiftKey:true,
	view:true,
	"char":true,
	charCode:true,
	key:true,
	keyCode:true,
	button:true,
	buttons:true,
	clientX:true,
	clientY:true,
	offsetX:true,
	offsetY:true,
	pointerId:true,
	pointerType:true,
	screenX:true,
	screenY:true,
	targetTouches:true,
	toElement:true,
	touches:true,

	which:function(event){
		varbutton=event.button;

		//Addwhichforkeyevents
		if(event.which==null&&rkeyEvent.test(event.type)){
			returnevent.charCode!=null?event.charCode:event.keyCode;
		}

		//Addwhichforclick:1===left;2===middle;3===right
		if(!event.which&&button!==undefined&&rmouseEvent.test(event.type)){
			if(button&1){
				return1;
			}

			if(button&2){
				return3;
			}

			if(button&4){
				return2;
			}

			return0;
		}

		returnevent.which;
	}
},jQuery.event.addProp);

//Createmouseenter/leaveeventsusingmouseover/outandevent-timechecks
//sothateventdelegationworksinjQuery.
//Dothesameforpointerenter/pointerleaveandpointerover/pointerout
//
//Support:Safari7only
//Safarisendsmouseentertoooften;see:
//https://bugs.chromium.org/p/chromium/issues/detail?id=470258
//forthedescriptionofthebug(itexistedinolderChromeversionsaswell).
jQuery.each({
	mouseenter:"mouseover",
	mouseleave:"mouseout",
	pointerenter:"pointerover",
	pointerleave:"pointerout"
},function(orig,fix){
	jQuery.event.special[orig]={
		delegateType:fix,
		bindType:fix,

		handle:function(event){
			varret,
				target=this,
				related=event.relatedTarget,
				handleObj=event.handleObj;

			//Formouseenter/leavecallthehandlerifrelatedisoutsidethetarget.
			//NB:NorelatedTargetifthemouseleft/enteredthebrowserwindow
			if(!related||(related!==target&&!jQuery.contains(target,related))){
				event.type=handleObj.origType;
				ret=handleObj.handler.apply(this,arguments);
				event.type=fix;
			}
			returnret;
		}
	};
});

jQuery.fn.extend({

	on:function(types,selector,data,fn){
		returnon(this,types,selector,data,fn);
	},
	one:function(types,selector,data,fn){
		returnon(this,types,selector,data,fn,1);
	},
	off:function(types,selector,fn){
		varhandleObj,type;
		if(types&&types.preventDefault&&types.handleObj){

			//(event) dispatchedjQuery.Event
			handleObj=types.handleObj;
			jQuery(types.delegateTarget).off(
				handleObj.namespace?
					handleObj.origType+"."+handleObj.namespace:
					handleObj.origType,
				handleObj.selector,
				handleObj.handler
			);
			returnthis;
		}
		if(typeoftypes==="object"){

			//(types-object[,selector])
			for(typeintypes){
				this.off(type,selector,types[type]);
			}
			returnthis;
		}
		if(selector===false||typeofselector==="function"){

			//(types[,fn])
			fn=selector;
			selector=undefined;
		}
		if(fn===false){
			fn=returnFalse;
		}
		returnthis.each(function(){
			jQuery.event.remove(this,types,fn,selector);
		});
	}
});


var

	/*eslint-disablemax-len*/

	//Seehttps://github.com/eslint/eslint/issues/3229
	rxhtmlTag=/<(?!area|br|col|embed|hr|img|input|link|meta|param)(([a-z][^\/\0>\x20\t\r\n\f]*)[^>]*)\/>/gi,

	/*eslint-enable*/

	//Support:IE<=10-11,Edge12-13only
	//InIE/Edgeusingregexgroupsherecausessevereslowdowns.
	//Seehttps://connect.microsoft.com/IE/feedback/details/1736512/
	rnoInnerhtml=/<script|<style|<link/i,

	//checked="checked"orchecked
	rchecked=/checked\s*(?:[^=]|=\s*.checked.)/i,
	rcleanScript=/^\s*<!(?:\[CDATA\[|--)|(?:\]\]|--)>\s*$/g;

//Preferatbodyoveritsparenttableforcontainingnewrows
functionmanipulationTarget(elem,content){
	if(nodeName(elem,"table")&&
		nodeName(content.nodeType!==11?content:content.firstChild,"tr")){

		returnjQuery(elem).children("tbody")[0]||elem;
	}

	returnelem;
}

//Replace/restorethetypeattributeofscriptelementsforsafeDOMmanipulation
functiondisableScript(elem){
	elem.type=(elem.getAttribute("type")!==null)+"/"+elem.type;
	returnelem;
}
functionrestoreScript(elem){
	if((elem.type||"").slice(0,5)==="true/"){
		elem.type=elem.type.slice(5);
	}else{
		elem.removeAttribute("type");
	}

	returnelem;
}

functioncloneCopyEvent(src,dest){
	vari,l,type,pdataOld,pdataCur,udataOld,udataCur,events;

	if(dest.nodeType!==1){
		return;
	}

	//1.Copyprivatedata:events,handlers,etc.
	if(dataPriv.hasData(src)){
		pdataOld=dataPriv.access(src);
		pdataCur=dataPriv.set(dest,pdataOld);
		events=pdataOld.events;

		if(events){
			deletepdataCur.handle;
			pdataCur.events={};

			for(typeinevents){
				for(i=0,l=events[type].length;i<l;i++){
					jQuery.event.add(dest,type,events[type][i]);
				}
			}
		}
	}

	//2.Copyuserdata
	if(dataUser.hasData(src)){
		udataOld=dataUser.access(src);
		udataCur=jQuery.extend({},udataOld);

		dataUser.set(dest,udataCur);
	}
}

//FixIEbugs,seesupporttests
functionfixInput(src,dest){
	varnodeName=dest.nodeName.toLowerCase();

	//Failstopersistthecheckedstateofaclonedcheckboxorradiobutton.
	if(nodeName==="input"&&rcheckableType.test(src.type)){
		dest.checked=src.checked;

	//Failstoreturntheselectedoptiontothedefaultselectedstatewhencloningoptions
	}elseif(nodeName==="input"||nodeName==="textarea"){
		dest.defaultValue=src.defaultValue;
	}
}

functiondomManip(collection,args,callback,ignored){

	//Flattenanynestedarrays
	args=concat.apply([],args);

	varfragment,first,scripts,hasScripts,node,doc,
		i=0,
		l=collection.length,
		iNoClone=l-1,
		value=args[0],
		valueIsFunction=isFunction(value);

	//Wecan'tcloneNodefragmentsthatcontainchecked,inWebKit
	if(valueIsFunction||
			(l>1&&typeofvalue==="string"&&
				!support.checkClone&&rchecked.test(value))){
		returncollection.each(function(index){
			varself=collection.eq(index);
			if(valueIsFunction){
				args[0]=value.call(this,index,self.html());
			}
			domManip(self,args,callback,ignored);
		});
	}

	if(l){
		fragment=buildFragment(args,collection[0].ownerDocument,false,collection,ignored);
		first=fragment.firstChild;

		if(fragment.childNodes.length===1){
			fragment=first;
		}

		//Requireeithernewcontentoraninterestinignoredelementstoinvokethecallback
		if(first||ignored){
			scripts=jQuery.map(getAll(fragment,"script"),disableScript);
			hasScripts=scripts.length;

			//Usetheoriginalfragmentforthelastitem
			//insteadofthefirstbecauseitcanendup
			//beingemptiedincorrectlyincertainsituations(#8070).
			for(;i<l;i++){
				node=fragment;

				if(i!==iNoClone){
					node=jQuery.clone(node,true,true);

					//Keepreferencestoclonedscriptsforlaterrestoration
					if(hasScripts){

						//Support:Android<=4.0only,PhantomJS1only
						//push.apply(_,arraylike)throwsonancientWebKit
						jQuery.merge(scripts,getAll(node,"script"));
					}
				}

				callback.call(collection[i],node,i);
			}

			if(hasScripts){
				doc=scripts[scripts.length-1].ownerDocument;

				//Reenablescripts
				jQuery.map(scripts,restoreScript);

				//Evaluateexecutablescriptsonfirstdocumentinsertion
				for(i=0;i<hasScripts;i++){
					node=scripts[i];
					if(rscriptType.test(node.type||"")&&
						!dataPriv.access(node,"globalEval")&&
						jQuery.contains(doc,node)){

						if(node.src&&(node.type||"").toLowerCase() !=="module"){

							//OptionalAJAXdependency,butwon'trunscriptsifnotpresent
							if(jQuery._evalUrl){
								jQuery._evalUrl(node.src);
							}
						}else{
							DOMEval(node.textContent.replace(rcleanScript,""),doc,node);
						}
					}
				}
			}
		}
	}

	returncollection;
}

functionremove(elem,selector,keepData){
	varnode,
		nodes=selector?jQuery.filter(selector,elem):elem,
		i=0;

	for(;(node=nodes[i])!=null;i++){
		if(!keepData&&node.nodeType===1){
			jQuery.cleanData(getAll(node));
		}

		if(node.parentNode){
			if(keepData&&jQuery.contains(node.ownerDocument,node)){
				setGlobalEval(getAll(node,"script"));
			}
			node.parentNode.removeChild(node);
		}
	}

	returnelem;
}

jQuery.extend({
	htmlPrefilter:function(html){
		returnhtml.replace(rxhtmlTag,"<$1></$2>");
	},

	clone:function(elem,dataAndEvents,deepDataAndEvents){
		vari,l,srcElements,destElements,
			clone=elem.cloneNode(true),
			inPage=jQuery.contains(elem.ownerDocument,elem);

		//FixIEcloningissues
		if(!support.noCloneChecked&&(elem.nodeType===1||elem.nodeType===11)&&
				!jQuery.isXMLDoc(elem)){

			//WeeschewSizzlehereforperformancereasons:https://jsperf.com/getall-vs-sizzle/2
			destElements=getAll(clone);
			srcElements=getAll(elem);

			for(i=0,l=srcElements.length;i<l;i++){
				fixInput(srcElements[i],destElements[i]);
			}
		}

		//Copytheeventsfromtheoriginaltotheclone
		if(dataAndEvents){
			if(deepDataAndEvents){
				srcElements=srcElements||getAll(elem);
				destElements=destElements||getAll(clone);

				for(i=0,l=srcElements.length;i<l;i++){
					cloneCopyEvent(srcElements[i],destElements[i]);
				}
			}else{
				cloneCopyEvent(elem,clone);
			}
		}

		//Preservescriptevaluationhistory
		destElements=getAll(clone,"script");
		if(destElements.length>0){
			setGlobalEval(destElements,!inPage&&getAll(elem,"script"));
		}

		//Returntheclonedset
		returnclone;
	},

	cleanData:function(elems){
		vardata,elem,type,
			special=jQuery.event.special,
			i=0;

		for(;(elem=elems[i])!==undefined;i++){
			if(acceptData(elem)){
				if((data=elem[dataPriv.expando])){
					if(data.events){
						for(typeindata.events){
							if(special[type]){
								jQuery.event.remove(elem,type);

							//ThisisashortcuttoavoidjQuery.event.remove'soverhead
							}else{
								jQuery.removeEvent(elem,type,data.handle);
							}
						}
					}

					//Support:Chrome<=35-45+
					//Assignundefinedinsteadofusingdelete,seeData#remove
					elem[dataPriv.expando]=undefined;
				}
				if(elem[dataUser.expando]){

					//Support:Chrome<=35-45+
					//Assignundefinedinsteadofusingdelete,seeData#remove
					elem[dataUser.expando]=undefined;
				}
			}
		}
	}
});

jQuery.fn.extend({
	detach:function(selector){
		returnremove(this,selector,true);
	},

	remove:function(selector){
		returnremove(this,selector);
	},

	text:function(value){
		returnaccess(this,function(value){
			returnvalue===undefined?
				jQuery.text(this):
				this.empty().each(function(){
					if(this.nodeType===1||this.nodeType===11||this.nodeType===9){
						this.textContent=value;
					}
				});
		},null,value,arguments.length);
	},

	append:function(){
		returndomManip(this,arguments,function(elem){
			if(this.nodeType===1||this.nodeType===11||this.nodeType===9){
				vartarget=manipulationTarget(this,elem);
				target.appendChild(elem);
			}
		});
	},

	prepend:function(){
		returndomManip(this,arguments,function(elem){
			if(this.nodeType===1||this.nodeType===11||this.nodeType===9){
				vartarget=manipulationTarget(this,elem);
				target.insertBefore(elem,target.firstChild);
			}
		});
	},

	before:function(){
		returndomManip(this,arguments,function(elem){
			if(this.parentNode){
				this.parentNode.insertBefore(elem,this);
			}
		});
	},

	after:function(){
		returndomManip(this,arguments,function(elem){
			if(this.parentNode){
				this.parentNode.insertBefore(elem,this.nextSibling);
			}
		});
	},

	empty:function(){
		varelem,
			i=0;

		for(;(elem=this[i])!=null;i++){
			if(elem.nodeType===1){

				//Preventmemoryleaks
				jQuery.cleanData(getAll(elem,false));

				//Removeanyremainingnodes
				elem.textContent="";
			}
		}

		returnthis;
	},

	clone:function(dataAndEvents,deepDataAndEvents){
		dataAndEvents=dataAndEvents==null?false:dataAndEvents;
		deepDataAndEvents=deepDataAndEvents==null?dataAndEvents:deepDataAndEvents;

		returnthis.map(function(){
			returnjQuery.clone(this,dataAndEvents,deepDataAndEvents);
		});
	},

	html:function(value){
		returnaccess(this,function(value){
			varelem=this[0]||{},
				i=0,
				l=this.length;

			if(value===undefined&&elem.nodeType===1){
				returnelem.innerHTML;
			}

			//SeeifwecantakeashortcutandjustuseinnerHTML
			if(typeofvalue==="string"&&!rnoInnerhtml.test(value)&&
				!wrapMap[(rtagName.exec(value)||["",""])[1].toLowerCase()]){

				value=jQuery.htmlPrefilter(value);

				try{
					for(;i<l;i++){
						elem=this[i]||{};

						//Removeelementnodesandpreventmemoryleaks
						if(elem.nodeType===1){
							jQuery.cleanData(getAll(elem,false));
							elem.innerHTML=value;
						}
					}

					elem=0;

				//IfusinginnerHTMLthrowsanexception,usethefallbackmethod
				}catch(e){}
			}

			if(elem){
				this.empty().append(value);
			}
		},null,value,arguments.length);
	},

	replaceWith:function(){
		varignored=[];

		//Makethechanges,replacingeachnon-ignoredcontextelementwiththenewcontent
		returndomManip(this,arguments,function(elem){
			varparent=this.parentNode;

			if(jQuery.inArray(this,ignored)<0){
				jQuery.cleanData(getAll(this));
				if(parent){
					parent.replaceChild(elem,this);
				}
			}

		//Forcecallbackinvocation
		},ignored);
	}
});

jQuery.each({
	appendTo:"append",
	prependTo:"prepend",
	insertBefore:"before",
	insertAfter:"after",
	replaceAll:"replaceWith"
},function(name,original){
	jQuery.fn[name]=function(selector){
		varelems,
			ret=[],
			insert=jQuery(selector),
			last=insert.length-1,
			i=0;

		for(;i<=last;i++){
			elems=i===last?this:this.clone(true);
			jQuery(insert[i])[original](elems);

			//Support:Android<=4.0only,PhantomJS1only
			//.get()becausepush.apply(_,arraylike)throwsonancientWebKit
			push.apply(ret,elems.get());
		}

		returnthis.pushStack(ret);
	};
});
varrnumnonpx=newRegExp("^("+pnum+")(?!px)[a-z%]+$","i");

vargetStyles=function(elem){

		//Support:IE<=11only,Firefox<=30(#15098,#14150)
		//IEthrowsonelementscreatedinpopups
		//FFmeanwhilethrowsonframeelementsthrough"defaultView.getComputedStyle"
		varview=elem.ownerDocument.defaultView;

		if(!view||!view.opener){
			view=window;
		}

		returnview.getComputedStyle(elem);
	};

varrboxStyle=newRegExp(cssExpand.join("|"),"i");



(function(){

	//ExecutingbothpixelPosition&boxSizingReliabletestsrequireonlyonelayout
	//sothey'reexecutedatthesametimetosavethesecondcomputation.
	functioncomputeStyleTests(){

		//Thisisasingleton,weneedtoexecuteitonlyonce
		if(!div){
			return;
		}

		container.style.cssText="position:absolute;left:-11111px;width:60px;"+
			"margin-top:1px;padding:0;border:0";
		div.style.cssText=
			"position:relative;display:block;box-sizing:border-box;overflow:scroll;"+
			"margin:auto;border:1px;padding:1px;"+
			"width:60%;top:1%";
		documentElement.appendChild(container).appendChild(div);

		vardivStyle=window.getComputedStyle(div);
		pixelPositionVal=divStyle.top!=="1%";

		//Support:Android4.0-4.3only,Firefox<=3-44
		reliableMarginLeftVal=roundPixelMeasures(divStyle.marginLeft)===12;

		//Support:Android4.0-4.3only,Safari<=9.1-10.1,iOS<=7.0-9.3
		//Somestylescomebackwithpercentagevalues,eventhoughtheyshouldn't
		div.style.right="60%";
		pixelBoxStylesVal=roundPixelMeasures(divStyle.right)===36;

		//Support:IE9-11only
		//Detectmisreportingofcontentdimensionsforbox-sizing:border-boxelements
		boxSizingReliableVal=roundPixelMeasures(divStyle.width)===36;

		//Support:IE9only
		//Detectoverflow:scrollscrewiness(gh-3699)
		div.style.position="absolute";
		scrollboxSizeVal=div.offsetWidth===36||"absolute";

		documentElement.removeChild(container);

		//Nullifythedivsoitwouldn'tbestoredinthememoryand
		//itwillalsobeasignthatchecksalreadyperformed
		div=null;
	}

	functionroundPixelMeasures(measure){
		returnMath.round(parseFloat(measure));
	}

	varpixelPositionVal,boxSizingReliableVal,scrollboxSizeVal,pixelBoxStylesVal,
		reliableMarginLeftVal,
		container=document.createElement("div"),
		div=document.createElement("div");

	//Finishearlyinlimited(non-browser)environments
	if(!div.style){
		return;
	}

	//Support:IE<=9-11only
	//Styleofclonedelementaffectssourceelementcloned(#8908)
	div.style.backgroundClip="content-box";
	div.cloneNode(true).style.backgroundClip="";
	support.clearCloneStyle=div.style.backgroundClip==="content-box";

	jQuery.extend(support,{
		boxSizingReliable:function(){
			computeStyleTests();
			returnboxSizingReliableVal;
		},
		pixelBoxStyles:function(){
			computeStyleTests();
			returnpixelBoxStylesVal;
		},
		pixelPosition:function(){
			computeStyleTests();
			returnpixelPositionVal;
		},
		reliableMarginLeft:function(){
			computeStyleTests();
			returnreliableMarginLeftVal;
		},
		scrollboxSize:function(){
			computeStyleTests();
			returnscrollboxSizeVal;
		}
	});
})();


functioncurCSS(elem,name,computed){
	varwidth,minWidth,maxWidth,ret,

		//Support:Firefox51+
		//Retrievingstylebeforecomputedsomehow
		//fixesanissuewithgettingwrongvalues
		//ondetachedelements
		style=elem.style;

	computed=computed||getStyles(elem);

	//getPropertyValueisneededfor:
	//  .css('filter')(IE9only,#12537)
	//  .css('--customProperty)(#3144)
	if(computed){
		ret=computed.getPropertyValue(name)||computed[name];

		if(ret===""&&!jQuery.contains(elem.ownerDocument,elem)){
			ret=jQuery.style(elem,name);
		}

		//Atributetothe"awesomehackbyDeanEdwards"
		//AndroidBrowserreturnspercentageforsomevalues,
		//butwidthseemstobereliablypixels.
		//ThisisagainsttheCSSOMdraftspec:
		//https://drafts.csswg.org/cssom/#resolved-values
		if(!support.pixelBoxStyles()&&rnumnonpx.test(ret)&&rboxStyle.test(name)){

			//Remembertheoriginalvalues
			width=style.width;
			minWidth=style.minWidth;
			maxWidth=style.maxWidth;

			//Putinthenewvaluestogetacomputedvalueout
			style.minWidth=style.maxWidth=style.width=ret;
			ret=computed.width;

			//Revertthechangedvalues
			style.width=width;
			style.minWidth=minWidth;
			style.maxWidth=maxWidth;
		}
	}

	returnret!==undefined?

		//Support:IE<=9-11only
		//IEreturnszIndexvalueasaninteger.
		ret+"":
		ret;
}


functionaddGetHookIf(conditionFn,hookFn){

	//Definethehook,we'llcheckonthefirstrunifit'sreallyneeded.
	return{
		get:function(){
			if(conditionFn()){

				//Hooknotneeded(orit'snotpossibletouseitdue
				//tomissingdependency),removeit.
				deletethis.get;
				return;
			}

			//Hookneeded;redefineitsothatthesupporttestisnotexecutedagain.
			return(this.get=hookFn).apply(this,arguments);
		}
	};
}


var

	//Swappableifdisplayisnoneorstartswithtable
	//except"table","table-cell",or"table-caption"
	//Seeherefordisplayvalues:https://developer.mozilla.org/en-US/docs/CSS/display
	rdisplayswap=/^(none|table(?!-c[ea]).+)/,
	rcustomProp=/^--/,
	cssShow={position:"absolute",visibility:"hidden",display:"block"},
	cssNormalTransform={
		letterSpacing:"0",
		fontWeight:"400"
	},

	cssPrefixes=["Webkit","Moz","ms"],
	emptyStyle=document.createElement("div").style;

//Returnacsspropertymappedtoapotentiallyvendorprefixedproperty
functionvendorPropName(name){

	//Shortcutfornamesthatarenotvendorprefixed
	if(nameinemptyStyle){
		returnname;
	}

	//Checkforvendorprefixednames
	varcapName=name[0].toUpperCase()+name.slice(1),
		i=cssPrefixes.length;

	while(i--){
		name=cssPrefixes[i]+capName;
		if(nameinemptyStyle){
			returnname;
		}
	}
}

//ReturnapropertymappedalongwhatjQuery.cssPropssuggestsorto
//avendorprefixedproperty.
functionfinalPropName(name){
	varret=jQuery.cssProps[name];
	if(!ret){
		ret=jQuery.cssProps[name]=vendorPropName(name)||name;
	}
	returnret;
}

functionsetPositiveNumber(elem,value,subtract){

	//Anyrelative(+/-)valueshavealreadybeen
	//normalizedatthispoint
	varmatches=rcssNum.exec(value);
	returnmatches?

		//Guardagainstundefined"subtract",e.g.,whenusedasincssHooks
		Math.max(0,matches[2]-(subtract||0))+(matches[3]||"px"):
		value;
}

functionboxModelAdjustment(elem,dimension,box,isBorderBox,styles,computedVal){
	vari=dimension==="width"?1:0,
		extra=0,
		delta=0;

	//Adjustmentmaynotbenecessary
	if(box===(isBorderBox?"border":"content")){
		return0;
	}

	for(;i<4;i+=2){

		//Bothboxmodelsexcludemargin
		if(box==="margin"){
			delta+=jQuery.css(elem,box+cssExpand[i],true,styles);
		}

		//Ifwegetherewithacontent-box,we'reseeking"padding"or"border"or"margin"
		if(!isBorderBox){

			//Addpadding
			delta+=jQuery.css(elem,"padding"+cssExpand[i],true,styles);

			//For"border"or"margin",addborder
			if(box!=="padding"){
				delta+=jQuery.css(elem,"border"+cssExpand[i]+"Width",true,styles);

			//Butstillkeeptrackofitotherwise
			}else{
				extra+=jQuery.css(elem,"border"+cssExpand[i]+"Width",true,styles);
			}

		//Ifwegetherewithaborder-box(content+padding+border),we'reseeking"content"or
		//"padding"or"margin"
		}else{

			//For"content",subtractpadding
			if(box==="content"){
				delta-=jQuery.css(elem,"padding"+cssExpand[i],true,styles);
			}

			//For"content"or"padding",subtractborder
			if(box!=="margin"){
				delta-=jQuery.css(elem,"border"+cssExpand[i]+"Width",true,styles);
			}
		}
	}

	//Accountforpositivecontent-boxscrollgutterwhenrequestedbyprovidingcomputedVal
	if(!isBorderBox&&computedVal>=0){

		//offsetWidth/offsetHeightisaroundedsumofcontent,padding,scrollgutter,andborder
		//Assumingintegerscrollgutter,subtracttherestandrounddown
		delta+=Math.max(0,Math.ceil(
			elem["offset"+dimension[0].toUpperCase()+dimension.slice(1)]-
			computedVal-
			delta-
			extra-
			0.5
		));
	}

	returndelta;
}

functiongetWidthOrHeight(elem,dimension,extra){

	//Startwithcomputedstyle
	varstyles=getStyles(elem),
		val=curCSS(elem,dimension,styles),
		isBorderBox=jQuery.css(elem,"boxSizing",false,styles)==="border-box",
		valueIsBorderBox=isBorderBox;

	//Support:Firefox<=54
	//Returnaconfoundingnon-pixelvalueorfeignignorance,asappropriate.
	if(rnumnonpx.test(val)){
		if(!extra){
			returnval;
		}
		val="auto";
	}

	//Checkforstyleincaseabrowserwhichreturnsunreliablevalues
	//forgetComputedStylesilentlyfallsbacktothereliableelem.style
	valueIsBorderBox=valueIsBorderBox&&
		(support.boxSizingReliable()||val===elem.style[dimension]);

	//FallbacktooffsetWidth/offsetHeightwhenvalueis"auto"
	//Thishappensforinlineelementswithnoexplicitsetting(gh-3571)
	//Support:Android<=4.1-4.3only
	//AlsouseoffsetWidth/offsetHeightformisreportedinlinedimensions(gh-3602)
	if(val==="auto"||
		!parseFloat(val)&&jQuery.css(elem,"display",false,styles)==="inline"){

		val=elem["offset"+dimension[0].toUpperCase()+dimension.slice(1)];

		//offsetWidth/offsetHeightprovideborder-boxvalues
		valueIsBorderBox=true;
	}

	//Normalize""andauto
	val=parseFloat(val)||0;

	//Adjustfortheelement'sboxmodel
	return(val+
		boxModelAdjustment(
			elem,
			dimension,
			extra||(isBorderBox?"border":"content"),
			valueIsBorderBox,
			styles,

			//Providethecurrentcomputedsizetorequestscrollguttercalculation(gh-3589)
			val
		)
	)+"px";
}

jQuery.extend({

	//Addinstylepropertyhooksforoverridingthedefault
	//behaviorofgettingandsettingastyleproperty
	cssHooks:{
		opacity:{
			get:function(elem,computed){
				if(computed){

					//Weshouldalwaysgetanumberbackfromopacity
					varret=curCSS(elem,"opacity");
					returnret===""?"1":ret;
				}
			}
		}
	},

	//Don'tautomaticallyadd"px"tothesepossibly-unitlessproperties
	cssNumber:{
		"animationIterationCount":true,
		"columnCount":true,
		"fillOpacity":true,
		"flexGrow":true,
		"flexShrink":true,
		"fontWeight":true,
		"lineHeight":true,
		"opacity":true,
		"order":true,
		"orphans":true,
		"widows":true,
		"zIndex":true,
		"zoom":true
	},

	//Addinpropertieswhosenamesyouwishtofixbefore
	//settingorgettingthevalue
	cssProps:{},

	//GetandsetthestylepropertyonaDOMNode
	style:function(elem,name,value,extra){

		//Don'tsetstylesontextandcommentnodes
		if(!elem||elem.nodeType===3||elem.nodeType===8||!elem.style){
			return;
		}

		//Makesurethatwe'reworkingwiththerightname
		varret,type,hooks,
			origName=camelCase(name),
			isCustomProp=rcustomProp.test(name),
			style=elem.style;

		//Makesurethatwe'reworkingwiththerightname.Wedon't
		//wanttoquerythevalueifitisaCSScustomproperty
		//sincetheyareuser-defined.
		if(!isCustomProp){
			name=finalPropName(origName);
		}

		//Getshookfortheprefixedversion,thenunprefixedversion
		hooks=jQuery.cssHooks[name]||jQuery.cssHooks[origName];

		//Checkifwe'resettingavalue
		if(value!==undefined){
			type=typeofvalue;

			//Convert"+="or"-="torelativenumbers(#7345)
			if(type==="string"&&(ret=rcssNum.exec(value))&&ret[1]){
				value=adjustCSS(elem,name,ret);

				//Fixesbug#9237
				type="number";
			}

			//MakesurethatnullandNaNvaluesaren'tset(#7116)
			if(value==null||value!==value){
				return;
			}

			//Ifanumberwaspassedin,addtheunit(exceptforcertainCSSproperties)
			if(type==="number"){
				value+=ret&&ret[3]||(jQuery.cssNumber[origName]?"":"px");
			}

			//background-*propsaffectoriginalclone'svalues
			if(!support.clearCloneStyle&&value===""&&name.indexOf("background")===0){
				style[name]="inherit";
			}

			//Ifahookwasprovided,usethatvalue,otherwisejustsetthespecifiedvalue
			if(!hooks||!("set"inhooks)||
				(value=hooks.set(elem,value,extra))!==undefined){

				if(isCustomProp){
					style.setProperty(name,value);
				}else{
					style[name]=value;
				}
			}

		}else{

			//Ifahookwasprovidedgetthenon-computedvaluefromthere
			if(hooks&&"get"inhooks&&
				(ret=hooks.get(elem,false,extra))!==undefined){

				returnret;
			}

			//Otherwisejustgetthevaluefromthestyleobject
			returnstyle[name];
		}
	},

	css:function(elem,name,extra,styles){
		varval,num,hooks,
			origName=camelCase(name),
			isCustomProp=rcustomProp.test(name);

		//Makesurethatwe'reworkingwiththerightname.Wedon't
		//wanttomodifythevalueifitisaCSScustomproperty
		//sincetheyareuser-defined.
		if(!isCustomProp){
			name=finalPropName(origName);
		}

		//Tryprefixednamefollowedbytheunprefixedname
		hooks=jQuery.cssHooks[name]||jQuery.cssHooks[origName];

		//Ifahookwasprovidedgetthecomputedvaluefromthere
		if(hooks&&"get"inhooks){
			val=hooks.get(elem,true,extra);
		}

		//Otherwise,ifawaytogetthecomputedvalueexists,usethat
		if(val===undefined){
			val=curCSS(elem,name,styles);
		}

		//Convert"normal"tocomputedvalue
		if(val==="normal"&&nameincssNormalTransform){
			val=cssNormalTransform[name];
		}

		//Makenumericifforcedoraqualifierwasprovidedandvallooksnumeric
		if(extra===""||extra){
			num=parseFloat(val);
			returnextra===true||isFinite(num)?num||0:val;
		}

		returnval;
	}
});

jQuery.each(["height","width"],function(i,dimension){
	jQuery.cssHooks[dimension]={
		get:function(elem,computed,extra){
			if(computed){

				//Certainelementscanhavedimensioninfoifweinvisiblyshowthem
				//butitmusthaveacurrentdisplaystylethatwouldbenefit
				returnrdisplayswap.test(jQuery.css(elem,"display"))&&

					//Support:Safari8+
					//TablecolumnsinSafarihavenon-zerooffsetWidth&zero
					//getBoundingClientRect().widthunlessdisplayischanged.
					//Support:IE<=11only
					//RunninggetBoundingClientRectonadisconnectednode
					//inIEthrowsanerror.
					(!elem.getClientRects().length||!elem.getBoundingClientRect().width)?
						swap(elem,cssShow,function(){
							returngetWidthOrHeight(elem,dimension,extra);
						}):
						getWidthOrHeight(elem,dimension,extra);
			}
		},

		set:function(elem,value,extra){
			varmatches,
				styles=getStyles(elem),
				isBorderBox=jQuery.css(elem,"boxSizing",false,styles)==="border-box",
				subtract=extra&&boxModelAdjustment(
					elem,
					dimension,
					extra,
					isBorderBox,
					styles
				);

			//Accountforunreliableborder-boxdimensionsbycomparingoffset*tocomputedand
			//fakingacontent-boxtogetborderandpadding(gh-3699)
			if(isBorderBox&&support.scrollboxSize()===styles.position){
				subtract-=Math.ceil(
					elem["offset"+dimension[0].toUpperCase()+dimension.slice(1)]-
					parseFloat(styles[dimension])-
					boxModelAdjustment(elem,dimension,"border",false,styles)-
					0.5
				);
			}

			//Converttopixelsifvalueadjustmentisneeded
			if(subtract&&(matches=rcssNum.exec(value))&&
				(matches[3]||"px")!=="px"){

				elem.style[dimension]=value;
				value=jQuery.css(elem,dimension);
			}

			returnsetPositiveNumber(elem,value,subtract);
		}
	};
});

jQuery.cssHooks.marginLeft=addGetHookIf(support.reliableMarginLeft,
	function(elem,computed){
		if(computed){
			return(parseFloat(curCSS(elem,"marginLeft"))||
				elem.getBoundingClientRect().left-
					swap(elem,{marginLeft:0},function(){
						returnelem.getBoundingClientRect().left;
					})
				)+"px";
		}
	}
);

//Thesehooksareusedbyanimatetoexpandproperties
jQuery.each({
	margin:"",
	padding:"",
	border:"Width"
},function(prefix,suffix){
	jQuery.cssHooks[prefix+suffix]={
		expand:function(value){
			vari=0,
				expanded={},

				//Assumesasinglenumberifnotastring
				parts=typeofvalue==="string"?value.split(""):[value];

			for(;i<4;i++){
				expanded[prefix+cssExpand[i]+suffix]=
					parts[i]||parts[i-2]||parts[0];
			}

			returnexpanded;
		}
	};

	if(prefix!=="margin"){
		jQuery.cssHooks[prefix+suffix].set=setPositiveNumber;
	}
});

jQuery.fn.extend({
	css:function(name,value){
		returnaccess(this,function(elem,name,value){
			varstyles,len,
				map={},
				i=0;

			if(Array.isArray(name)){
				styles=getStyles(elem);
				len=name.length;

				for(;i<len;i++){
					map[name[i]]=jQuery.css(elem,name[i],false,styles);
				}

				returnmap;
			}

			returnvalue!==undefined?
				jQuery.style(elem,name,value):
				jQuery.css(elem,name);
		},name,value,arguments.length>1);
	}
});


functionTween(elem,options,prop,end,easing){
	returnnewTween.prototype.init(elem,options,prop,end,easing);
}
jQuery.Tween=Tween;

Tween.prototype={
	constructor:Tween,
	init:function(elem,options,prop,end,easing,unit){
		this.elem=elem;
		this.prop=prop;
		this.easing=easing||jQuery.easing._default;
		this.options=options;
		this.start=this.now=this.cur();
		this.end=end;
		this.unit=unit||(jQuery.cssNumber[prop]?"":"px");
	},
	cur:function(){
		varhooks=Tween.propHooks[this.prop];

		returnhooks&&hooks.get?
			hooks.get(this):
			Tween.propHooks._default.get(this);
	},
	run:function(percent){
		vareased,
			hooks=Tween.propHooks[this.prop];

		if(this.options.duration){
			this.pos=eased=jQuery.easing[this.easing](
				percent,this.options.duration*percent,0,1,this.options.duration
			);
		}else{
			this.pos=eased=percent;
		}
		this.now=(this.end-this.start)*eased+this.start;

		if(this.options.step){
			this.options.step.call(this.elem,this.now,this);
		}

		if(hooks&&hooks.set){
			hooks.set(this);
		}else{
			Tween.propHooks._default.set(this);
		}
		returnthis;
	}
};

Tween.prototype.init.prototype=Tween.prototype;

Tween.propHooks={
	_default:{
		get:function(tween){
			varresult;

			//UseapropertyontheelementdirectlywhenitisnotaDOMelement,
			//orwhenthereisnomatchingstylepropertythatexists.
			if(tween.elem.nodeType!==1||
				tween.elem[tween.prop]!=null&&tween.elem.style[tween.prop]==null){
				returntween.elem[tween.prop];
			}

			//Passinganemptystringasa3rdparameterto.csswillautomatically
			//attemptaparseFloatandfallbacktoastringiftheparsefails.
			//Simplevaluessuchas"10px"areparsedtoFloat;
			//complexvaluessuchas"rotate(1rad)"arereturnedas-is.
			result=jQuery.css(tween.elem,tween.prop,"");

			//Emptystrings,null,undefinedand"auto"areconvertedto0.
			return!result||result==="auto"?0:result;
		},
		set:function(tween){

			//Usestephookforbackcompat.
			//UsecssHookifitsthere.
			//Use.styleifavailableanduseplainpropertieswhereavailable.
			if(jQuery.fx.step[tween.prop]){
				jQuery.fx.step[tween.prop](tween);
			}elseif(tween.elem.nodeType===1&&
				(tween.elem.style[jQuery.cssProps[tween.prop]]!=null||
					jQuery.cssHooks[tween.prop])){
				jQuery.style(tween.elem,tween.prop,tween.now+tween.unit);
			}else{
				tween.elem[tween.prop]=tween.now;
			}
		}
	}
};

//Support:IE<=9only
//Panicbasedapproachtosettingthingsondisconnectednodes
Tween.propHooks.scrollTop=Tween.propHooks.scrollLeft={
	set:function(tween){
		if(tween.elem.nodeType&&tween.elem.parentNode){
			tween.elem[tween.prop]=tween.now;
		}
	}
};

jQuery.easing={
	linear:function(p){
		returnp;
	},
	swing:function(p){
		return0.5-Math.cos(p*Math.PI)/2;
	},
	_default:"swing"
};

jQuery.fx=Tween.prototype.init;

//Backcompat<1.8extensionpoint
jQuery.fx.step={};




var
	fxNow,inProgress,
	rfxtypes=/^(?:toggle|show|hide)$/,
	rrun=/queueHooks$/;

functionschedule(){
	if(inProgress){
		if(document.hidden===false&&window.requestAnimationFrame){
			window.requestAnimationFrame(schedule);
		}else{
			window.setTimeout(schedule,jQuery.fx.interval);
		}

		jQuery.fx.tick();
	}
}

//Animationscreatedsynchronouslywillrunsynchronously
functioncreateFxNow(){
	window.setTimeout(function(){
		fxNow=undefined;
	});
	return(fxNow=Date.now());
}

//Generateparameterstocreateastandardanimation
functiongenFx(type,includeWidth){
	varwhich,
		i=0,
		attrs={height:type};

	//Ifweincludewidth,stepvalueis1todoallcssExpandvalues,
	//otherwisestepvalueis2toskipoverLeftandRight
	includeWidth=includeWidth?1:0;
	for(;i<4;i+=2-includeWidth){
		which=cssExpand[i];
		attrs["margin"+which]=attrs["padding"+which]=type;
	}

	if(includeWidth){
		attrs.opacity=attrs.width=type;
	}

	returnattrs;
}

functioncreateTween(value,prop,animation){
	vartween,
		collection=(Animation.tweeners[prop]||[]).concat(Animation.tweeners["*"]),
		index=0,
		length=collection.length;
	for(;index<length;index++){
		if((tween=collection[index].call(animation,prop,value))){

			//We'redonewiththisproperty
			returntween;
		}
	}
}

functiondefaultPrefilter(elem,props,opts){
	varprop,value,toggle,hooks,oldfire,propTween,restoreDisplay,display,
		isBox="width"inprops||"height"inprops,
		anim=this,
		orig={},
		style=elem.style,
		hidden=elem.nodeType&&isHiddenWithinTree(elem),
		dataShow=dataPriv.get(elem,"fxshow");

	//Queue-skippinganimationshijackthefxhooks
	if(!opts.queue){
		hooks=jQuery._queueHooks(elem,"fx");
		if(hooks.unqueued==null){
			hooks.unqueued=0;
			oldfire=hooks.empty.fire;
			hooks.empty.fire=function(){
				if(!hooks.unqueued){
					oldfire();
				}
			};
		}
		hooks.unqueued++;

		anim.always(function(){

			//Ensurethecompletehandleriscalledbeforethiscompletes
			anim.always(function(){
				hooks.unqueued--;
				if(!jQuery.queue(elem,"fx").length){
					hooks.empty.fire();
				}
			});
		});
	}

	//Detectshow/hideanimations
	for(propinprops){
		value=props[prop];
		if(rfxtypes.test(value)){
			deleteprops[prop];
			toggle=toggle||value==="toggle";
			if(value===(hidden?"hide":"show")){

				//Pretendtobehiddenifthisisa"show"and
				//thereisstilldatafromastoppedshow/hide
				if(value==="show"&&dataShow&&dataShow[prop]!==undefined){
					hidden=true;

				//Ignoreallotherno-opshow/hidedata
				}else{
					continue;
				}
			}
			orig[prop]=dataShow&&dataShow[prop]||jQuery.style(elem,prop);
		}
	}

	//Bailoutifthisisano-oplike.hide().hide()
	propTween=!jQuery.isEmptyObject(props);
	if(!propTween&&jQuery.isEmptyObject(orig)){
		return;
	}

	//Restrict"overflow"and"display"stylesduringboxanimations
	if(isBox&&elem.nodeType===1){

		//Support:IE<=9-11,Edge12-15
		//Recordall3overflowattributesbecauseIEdoesnotinfertheshorthand
		//fromidentically-valuedoverflowXandoverflowYandEdgejustmirrors
		//theoverflowXvaluethere.
		opts.overflow=[style.overflow,style.overflowX,style.overflowY];

		//Identifyadisplaytype,preferringoldshow/hidedataovertheCSScascade
		restoreDisplay=dataShow&&dataShow.display;
		if(restoreDisplay==null){
			restoreDisplay=dataPriv.get(elem,"display");
		}
		display=jQuery.css(elem,"display");
		if(display==="none"){
			if(restoreDisplay){
				display=restoreDisplay;
			}else{

				//Getnonemptyvalue(s)bytemporarilyforcingvisibility
				showHide([elem],true);
				restoreDisplay=elem.style.display||restoreDisplay;
				display=jQuery.css(elem,"display");
				showHide([elem]);
			}
		}

		//Animateinlineelementsasinline-block
		if(display==="inline"||display==="inline-block"&&restoreDisplay!=null){
			if(jQuery.css(elem,"float")==="none"){

				//Restoretheoriginaldisplayvalueattheendofpureshow/hideanimations
				if(!propTween){
					anim.done(function(){
						style.display=restoreDisplay;
					});
					if(restoreDisplay==null){
						display=style.display;
						restoreDisplay=display==="none"?"":display;
					}
				}
				style.display="inline-block";
			}
		}
	}

	if(opts.overflow){
		style.overflow="hidden";
		anim.always(function(){
			style.overflow=opts.overflow[0];
			style.overflowX=opts.overflow[1];
			style.overflowY=opts.overflow[2];
		});
	}

	//Implementshow/hideanimations
	propTween=false;
	for(propinorig){

		//Generalshow/hidesetupforthiselementanimation
		if(!propTween){
			if(dataShow){
				if("hidden"indataShow){
					hidden=dataShow.hidden;
				}
			}else{
				dataShow=dataPriv.access(elem,"fxshow",{display:restoreDisplay});
			}

			//Storehidden/visiblefortoggleso`.stop().toggle()`"reverses"
			if(toggle){
				dataShow.hidden=!hidden;
			}

			//Showelementsbeforeanimatingthem
			if(hidden){
				showHide([elem],true);
			}

			/*eslint-disableno-loop-func*/

			anim.done(function(){

			/*eslint-enableno-loop-func*/

				//Thefinalstepofa"hide"animationisactuallyhidingtheelement
				if(!hidden){
					showHide([elem]);
				}
				dataPriv.remove(elem,"fxshow");
				for(propinorig){
					jQuery.style(elem,prop,orig[prop]);
				}
			});
		}

		//Per-propertysetup
		propTween=createTween(hidden?dataShow[prop]:0,prop,anim);
		if(!(propindataShow)){
			dataShow[prop]=propTween.start;
			if(hidden){
				propTween.end=propTween.start;
				propTween.start=0;
			}
		}
	}
}

functionpropFilter(props,specialEasing){
	varindex,name,easing,value,hooks;

	//camelCase,specialEasingandexpandcssHookpass
	for(indexinprops){
		name=camelCase(index);
		easing=specialEasing[name];
		value=props[index];
		if(Array.isArray(value)){
			easing=value[1];
			value=props[index]=value[0];
		}

		if(index!==name){
			props[name]=value;
			deleteprops[index];
		}

		hooks=jQuery.cssHooks[name];
		if(hooks&&"expand"inhooks){
			value=hooks.expand(value);
			deleteprops[name];

			//Notquite$.extend,thiswon'toverwriteexistingkeys.
			//Reusing'index'becausewehavethecorrect"name"
			for(indexinvalue){
				if(!(indexinprops)){
					props[index]=value[index];
					specialEasing[index]=easing;
				}
			}
		}else{
			specialEasing[name]=easing;
		}
	}
}

functionAnimation(elem,properties,options){
	varresult,
		stopped,
		index=0,
		length=Animation.prefilters.length,
		deferred=jQuery.Deferred().always(function(){

			//Don'tmatcheleminthe:animatedselector
			deletetick.elem;
		}),
		tick=function(){
			if(stopped){
				returnfalse;
			}
			varcurrentTime=fxNow||createFxNow(),
				remaining=Math.max(0,animation.startTime+animation.duration-currentTime),

				//Support:Android2.3only
				//Archaiccrashbugwon'tallowustouse`1-(0.5||0)`(#12497)
				temp=remaining/animation.duration||0,
				percent=1-temp,
				index=0,
				length=animation.tweens.length;

			for(;index<length;index++){
				animation.tweens[index].run(percent);
			}

			deferred.notifyWith(elem,[animation,percent,remaining]);

			//Ifthere'smoretodo,yield
			if(percent<1&&length){
				returnremaining;
			}

			//Ifthiswasanemptyanimation,synthesizeafinalprogressnotification
			if(!length){
				deferred.notifyWith(elem,[animation,1,0]);
			}

			//Resolvetheanimationandreportitsconclusion
			deferred.resolveWith(elem,[animation]);
			returnfalse;
		},
		animation=deferred.promise({
			elem:elem,
			props:jQuery.extend({},properties),
			opts:jQuery.extend(true,{
				specialEasing:{},
				easing:jQuery.easing._default
			},options),
			originalProperties:properties,
			originalOptions:options,
			startTime:fxNow||createFxNow(),
			duration:options.duration,
			tweens:[],
			createTween:function(prop,end){
				vartween=jQuery.Tween(elem,animation.opts,prop,end,
						animation.opts.specialEasing[prop]||animation.opts.easing);
				animation.tweens.push(tween);
				returntween;
			},
			stop:function(gotoEnd){
				varindex=0,

					//Ifwearegoingtotheend,wewanttorunallthetweens
					//otherwiseweskipthispart
					length=gotoEnd?animation.tweens.length:0;
				if(stopped){
					returnthis;
				}
				stopped=true;
				for(;index<length;index++){
					animation.tweens[index].run(1);
				}

				//Resolvewhenweplayedthelastframe;otherwise,reject
				if(gotoEnd){
					deferred.notifyWith(elem,[animation,1,0]);
					deferred.resolveWith(elem,[animation,gotoEnd]);
				}else{
					deferred.rejectWith(elem,[animation,gotoEnd]);
				}
				returnthis;
			}
		}),
		props=animation.props;

	propFilter(props,animation.opts.specialEasing);

	for(;index<length;index++){
		result=Animation.prefilters[index].call(animation,elem,props,animation.opts);
		if(result){
			if(isFunction(result.stop)){
				jQuery._queueHooks(animation.elem,animation.opts.queue).stop=
					result.stop.bind(result);
			}
			returnresult;
		}
	}

	jQuery.map(props,createTween,animation);

	if(isFunction(animation.opts.start)){
		animation.opts.start.call(elem,animation);
	}

	//Attachcallbacksfromoptions
	animation
		.progress(animation.opts.progress)
		.done(animation.opts.done,animation.opts.complete)
		.fail(animation.opts.fail)
		.always(animation.opts.always);

	jQuery.fx.timer(
		jQuery.extend(tick,{
			elem:elem,
			anim:animation,
			queue:animation.opts.queue
		})
	);

	returnanimation;
}

jQuery.Animation=jQuery.extend(Animation,{

	tweeners:{
		"*":[function(prop,value){
			vartween=this.createTween(prop,value);
			adjustCSS(tween.elem,prop,rcssNum.exec(value),tween);
			returntween;
		}]
	},

	tweener:function(props,callback){
		if(isFunction(props)){
			callback=props;
			props=["*"];
		}else{
			props=props.match(rnothtmlwhite);
		}

		varprop,
			index=0,
			length=props.length;

		for(;index<length;index++){
			prop=props[index];
			Animation.tweeners[prop]=Animation.tweeners[prop]||[];
			Animation.tweeners[prop].unshift(callback);
		}
	},

	prefilters:[defaultPrefilter],

	prefilter:function(callback,prepend){
		if(prepend){
			Animation.prefilters.unshift(callback);
		}else{
			Animation.prefilters.push(callback);
		}
	}
});

jQuery.speed=function(speed,easing,fn){
	varopt=speed&&typeofspeed==="object"?jQuery.extend({},speed):{
		complete:fn||!fn&&easing||
			isFunction(speed)&&speed,
		duration:speed,
		easing:fn&&easing||easing&&!isFunction(easing)&&easing
	};

	//Gototheendstateiffxareoff
	if(jQuery.fx.off){
		opt.duration=0;

	}else{
		if(typeofopt.duration!=="number"){
			if(opt.durationinjQuery.fx.speeds){
				opt.duration=jQuery.fx.speeds[opt.duration];

			}else{
				opt.duration=jQuery.fx.speeds._default;
			}
		}
	}

	//Normalizeopt.queue-true/undefined/null->"fx"
	if(opt.queue==null||opt.queue===true){
		opt.queue="fx";
	}

	//Queueing
	opt.old=opt.complete;

	opt.complete=function(){
		if(isFunction(opt.old)){
			opt.old.call(this);
		}

		if(opt.queue){
			jQuery.dequeue(this,opt.queue);
		}
	};

	returnopt;
};

jQuery.fn.extend({
	fadeTo:function(speed,to,easing,callback){

		//Showanyhiddenelementsaftersettingopacityto0
		returnthis.filter(isHiddenWithinTree).css("opacity",0).show()

			//Animatetothevaluespecified
			.end().animate({opacity:to},speed,easing,callback);
	},
	animate:function(prop,speed,easing,callback){
		varempty=jQuery.isEmptyObject(prop),
			optall=jQuery.speed(speed,easing,callback),
			doAnimation=function(){

				//Operateonacopyofpropsoper-propertyeasingwon'tbelost
				varanim=Animation(this,jQuery.extend({},prop),optall);

				//Emptyanimations,orfinishingresolvesimmediately
				if(empty||dataPriv.get(this,"finish")){
					anim.stop(true);
				}
			};
			doAnimation.finish=doAnimation;

		returnempty||optall.queue===false?
			this.each(doAnimation):
			this.queue(optall.queue,doAnimation);
	},
	stop:function(type,clearQueue,gotoEnd){
		varstopQueue=function(hooks){
			varstop=hooks.stop;
			deletehooks.stop;
			stop(gotoEnd);
		};

		if(typeoftype!=="string"){
			gotoEnd=clearQueue;
			clearQueue=type;
			type=undefined;
		}
		if(clearQueue&&type!==false){
			this.queue(type||"fx",[]);
		}

		returnthis.each(function(){
			vardequeue=true,
				index=type!=null&&type+"queueHooks",
				timers=jQuery.timers,
				data=dataPriv.get(this);

			if(index){
				if(data[index]&&data[index].stop){
					stopQueue(data[index]);
				}
			}else{
				for(indexindata){
					if(data[index]&&data[index].stop&&rrun.test(index)){
						stopQueue(data[index]);
					}
				}
			}

			for(index=timers.length;index--;){
				if(timers[index].elem===this&&
					(type==null||timers[index].queue===type)){

					timers[index].anim.stop(gotoEnd);
					dequeue=false;
					timers.splice(index,1);
				}
			}

			//Startthenextinthequeueifthelaststepwasn'tforced.
			//Timerscurrentlywillcalltheircompletecallbacks,which
			//willdequeuebutonlyiftheyweregotoEnd.
			if(dequeue||!gotoEnd){
				jQuery.dequeue(this,type);
			}
		});
	},
	finish:function(type){
		if(type!==false){
			type=type||"fx";
		}
		returnthis.each(function(){
			varindex,
				data=dataPriv.get(this),
				queue=data[type+"queue"],
				hooks=data[type+"queueHooks"],
				timers=jQuery.timers,
				length=queue?queue.length:0;

			//Enablefinishingflagonprivatedata
			data.finish=true;

			//Emptythequeuefirst
			jQuery.queue(this,type,[]);

			if(hooks&&hooks.stop){
				hooks.stop.call(this,true);
			}

			//Lookforanyactiveanimations,andfinishthem
			for(index=timers.length;index--;){
				if(timers[index].elem===this&&timers[index].queue===type){
					timers[index].anim.stop(true);
					timers.splice(index,1);
				}
			}

			//Lookforanyanimationsintheoldqueueandfinishthem
			for(index=0;index<length;index++){
				if(queue[index]&&queue[index].finish){
					queue[index].finish.call(this);
				}
			}

			//Turnofffinishingflag
			deletedata.finish;
		});
	}
});

jQuery.each(["toggle","show","hide"],function(i,name){
	varcssFn=jQuery.fn[name];
	jQuery.fn[name]=function(speed,easing,callback){
		returnspeed==null||typeofspeed==="boolean"?
			cssFn.apply(this,arguments):
			this.animate(genFx(name,true),speed,easing,callback);
	};
});

//Generateshortcutsforcustomanimations
jQuery.each({
	slideDown:genFx("show"),
	slideUp:genFx("hide"),
	slideToggle:genFx("toggle"),
	fadeIn:{opacity:"show"},
	fadeOut:{opacity:"hide"},
	fadeToggle:{opacity:"toggle"}
},function(name,props){
	jQuery.fn[name]=function(speed,easing,callback){
		returnthis.animate(props,speed,easing,callback);
	};
});

jQuery.timers=[];
jQuery.fx.tick=function(){
	vartimer,
		i=0,
		timers=jQuery.timers;

	fxNow=Date.now();

	for(;i<timers.length;i++){
		timer=timers[i];

		//Runthetimerandsafelyremoveitwhendone(allowingforexternalremoval)
		if(!timer()&&timers[i]===timer){
			timers.splice(i--,1);
		}
	}

	if(!timers.length){
		jQuery.fx.stop();
	}
	fxNow=undefined;
};

jQuery.fx.timer=function(timer){
	jQuery.timers.push(timer);
	jQuery.fx.start();
};

jQuery.fx.interval=13;
jQuery.fx.start=function(){
	if(inProgress){
		return;
	}

	inProgress=true;
	schedule();
};

jQuery.fx.stop=function(){
	inProgress=null;
};

jQuery.fx.speeds={
	slow:600,
	fast:200,

	//Defaultspeed
	_default:400
};


//BasedoffofthepluginbyClintHelfers,withpermission.
//https://web.archive.org/web/20100324014747/http://blindsignals.com/index.php/2009/07/jquery-delay/
jQuery.fn.delay=function(time,type){
	time=jQuery.fx?jQuery.fx.speeds[time]||time:time;
	type=type||"fx";

	returnthis.queue(type,function(next,hooks){
		vartimeout=window.setTimeout(next,time);
		hooks.stop=function(){
			window.clearTimeout(timeout);
		};
	});
};


(function(){
	varinput=document.createElement("input"),
		select=document.createElement("select"),
		opt=select.appendChild(document.createElement("option"));

	input.type="checkbox";

	//Support:Android<=4.3only
	//Defaultvalueforacheckboxshouldbe"on"
	support.checkOn=input.value!=="";

	//Support:IE<=11only
	//MustaccessselectedIndextomakedefaultoptionsselect
	support.optSelected=opt.selected;

	//Support:IE<=11only
	//Aninputlosesitsvalueafterbecomingaradio
	input=document.createElement("input");
	input.value="t";
	input.type="radio";
	support.radioValue=input.value==="t";
})();


varboolHook,
	attrHandle=jQuery.expr.attrHandle;

jQuery.fn.extend({
	attr:function(name,value){
		returnaccess(this,jQuery.attr,name,value,arguments.length>1);
	},

	removeAttr:function(name){
		returnthis.each(function(){
			jQuery.removeAttr(this,name);
		});
	}
});

jQuery.extend({
	attr:function(elem,name,value){
		varret,hooks,
			nType=elem.nodeType;

		//Don'tget/setattributesontext,commentandattributenodes
		if(nType===3||nType===8||nType===2){
			return;
		}

		//Fallbacktopropwhenattributesarenotsupported
		if(typeofelem.getAttribute==="undefined"){
			returnjQuery.prop(elem,name,value);
		}

		//Attributehooksaredeterminedbythelowercaseversion
		//Grabnecessaryhookifoneisdefined
		if(nType!==1||!jQuery.isXMLDoc(elem)){
			hooks=jQuery.attrHooks[name.toLowerCase()]||
				(jQuery.expr.match.bool.test(name)?boolHook:undefined);
		}

		if(value!==undefined){
			if(value===null){
				jQuery.removeAttr(elem,name);
				return;
			}

			if(hooks&&"set"inhooks&&
				(ret=hooks.set(elem,value,name))!==undefined){
				returnret;
			}

			elem.setAttribute(name,value+"");
			returnvalue;
		}

		if(hooks&&"get"inhooks&&(ret=hooks.get(elem,name))!==null){
			returnret;
		}

		ret=jQuery.find.attr(elem,name);

		//Non-existentattributesreturnnull,wenormalizetoundefined
		returnret==null?undefined:ret;
	},

	attrHooks:{
		type:{
			set:function(elem,value){
				if(!support.radioValue&&value==="radio"&&
					nodeName(elem,"input")){
					varval=elem.value;
					elem.setAttribute("type",value);
					if(val){
						elem.value=val;
					}
					returnvalue;
				}
			}
		}
	},

	removeAttr:function(elem,value){
		varname,
			i=0,

			//Attributenamescancontainnon-HTMLwhitespacecharacters
			//https://html.spec.whatwg.org/multipage/syntax.html#attributes-2
			attrNames=value&&value.match(rnothtmlwhite);

		if(attrNames&&elem.nodeType===1){
			while((name=attrNames[i++])){
				elem.removeAttribute(name);
			}
		}
	}
});

//Hooksforbooleanattributes
boolHook={
	set:function(elem,value,name){
		if(value===false){

			//Removebooleanattributeswhensettofalse
			jQuery.removeAttr(elem,name);
		}else{
			elem.setAttribute(name,name);
		}
		returnname;
	}
};

jQuery.each(jQuery.expr.match.bool.source.match(/\w+/g),function(i,name){
	vargetter=attrHandle[name]||jQuery.find.attr;

	attrHandle[name]=function(elem,name,isXML){
		varret,handle,
			lowercaseName=name.toLowerCase();

		if(!isXML){

			//Avoidaninfiniteloopbytemporarilyremovingthisfunctionfromthegetter
			handle=attrHandle[lowercaseName];
			attrHandle[lowercaseName]=ret;
			ret=getter(elem,name,isXML)!=null?
				lowercaseName:
				null;
			attrHandle[lowercaseName]=handle;
		}
		returnret;
	};
});




varrfocusable=/^(?:input|select|textarea|button)$/i,
	rclickable=/^(?:a|area)$/i;

jQuery.fn.extend({
	prop:function(name,value){
		returnaccess(this,jQuery.prop,name,value,arguments.length>1);
	},

	removeProp:function(name){
		returnthis.each(function(){
			deletethis[jQuery.propFix[name]||name];
		});
	}
});

jQuery.extend({
	prop:function(elem,name,value){
		varret,hooks,
			nType=elem.nodeType;

		//Don'tget/setpropertiesontext,commentandattributenodes
		if(nType===3||nType===8||nType===2){
			return;
		}

		if(nType!==1||!jQuery.isXMLDoc(elem)){

			//Fixnameandattachhooks
			name=jQuery.propFix[name]||name;
			hooks=jQuery.propHooks[name];
		}

		if(value!==undefined){
			if(hooks&&"set"inhooks&&
				(ret=hooks.set(elem,value,name))!==undefined){
				returnret;
			}

			return(elem[name]=value);
		}

		if(hooks&&"get"inhooks&&(ret=hooks.get(elem,name))!==null){
			returnret;
		}

		returnelem[name];
	},

	propHooks:{
		tabIndex:{
			get:function(elem){

				//Support:IE<=9-11only
				//elem.tabIndexdoesn'talwaysreturnthe
				//correctvaluewhenithasn'tbeenexplicitlyset
				//https://web.archive.org/web/20141116233347/http://fluidproject.org/blog/2008/01/09/getting-setting-and-removing-tabindex-values-with-javascript/
				//Useproperattributeretrieval(#12072)
				vartabindex=jQuery.find.attr(elem,"tabindex");

				if(tabindex){
					returnparseInt(tabindex,10);
				}

				if(
					rfocusable.test(elem.nodeName)||
					rclickable.test(elem.nodeName)&&
					elem.href
				){
					return0;
				}

				return-1;
			}
		}
	},

	propFix:{
		"for":"htmlFor",
		"class":"className"
	}
});

//Support:IE<=11only
//AccessingtheselectedIndexproperty
//forcesthebrowsertorespectsettingselected
//ontheoption
//Thegetterensuresadefaultoptionisselected
//wheninanoptgroup
//eslintrule"no-unused-expressions"isdisabledforthiscode
//sinceitconsiderssuchaccessionsnoop
if(!support.optSelected){
	jQuery.propHooks.selected={
		get:function(elem){

			/*eslintno-unused-expressions:"off"*/

			varparent=elem.parentNode;
			if(parent&&parent.parentNode){
				parent.parentNode.selectedIndex;
			}
			returnnull;
		},
		set:function(elem){

			/*eslintno-unused-expressions:"off"*/

			varparent=elem.parentNode;
			if(parent){
				parent.selectedIndex;

				if(parent.parentNode){
					parent.parentNode.selectedIndex;
				}
			}
		}
	};
}

jQuery.each([
	"tabIndex",
	"readOnly",
	"maxLength",
	"cellSpacing",
	"cellPadding",
	"rowSpan",
	"colSpan",
	"useMap",
	"frameBorder",
	"contentEditable"
],function(){
	jQuery.propFix[this.toLowerCase()]=this;
});




	//StripandcollapsewhitespaceaccordingtoHTMLspec
	//https://infra.spec.whatwg.org/#strip-and-collapse-ascii-whitespace
	functionstripAndCollapse(value){
		vartokens=value.match(rnothtmlwhite)||[];
		returntokens.join("");
	}


functiongetClass(elem){
	returnelem.getAttribute&&elem.getAttribute("class")||"";
}

functionclassesToArray(value){
	if(Array.isArray(value)){
		returnvalue;
	}
	if(typeofvalue==="string"){
		returnvalue.match(rnothtmlwhite)||[];
	}
	return[];
}

jQuery.fn.extend({
	addClass:function(value){
		varclasses,elem,cur,curValue,clazz,j,finalValue,
			i=0;

		if(isFunction(value)){
			returnthis.each(function(j){
				jQuery(this).addClass(value.call(this,j,getClass(this)));
			});
		}

		classes=classesToArray(value);

		if(classes.length){
			while((elem=this[i++])){
				curValue=getClass(elem);
				cur=elem.nodeType===1&&(""+stripAndCollapse(curValue)+"");

				if(cur){
					j=0;
					while((clazz=classes[j++])){
						if(cur.indexOf(""+clazz+"")<0){
							cur+=clazz+"";
						}
					}

					//Onlyassignifdifferenttoavoidunneededrendering.
					finalValue=stripAndCollapse(cur);
					if(curValue!==finalValue){
						elem.setAttribute("class",finalValue);
					}
				}
			}
		}

		returnthis;
	},

	removeClass:function(value){
		varclasses,elem,cur,curValue,clazz,j,finalValue,
			i=0;

		if(isFunction(value)){
			returnthis.each(function(j){
				jQuery(this).removeClass(value.call(this,j,getClass(this)));
			});
		}

		if(!arguments.length){
			returnthis.attr("class","");
		}

		classes=classesToArray(value);

		if(classes.length){
			while((elem=this[i++])){
				curValue=getClass(elem);

				//Thisexpressionishereforbettercompressibility(seeaddClass)
				cur=elem.nodeType===1&&(""+stripAndCollapse(curValue)+"");

				if(cur){
					j=0;
					while((clazz=classes[j++])){

						//Remove*all*instances
						while(cur.indexOf(""+clazz+"")>-1){
							cur=cur.replace(""+clazz+"","");
						}
					}

					//Onlyassignifdifferenttoavoidunneededrendering.
					finalValue=stripAndCollapse(cur);
					if(curValue!==finalValue){
						elem.setAttribute("class",finalValue);
					}
				}
			}
		}

		returnthis;
	},

	toggleClass:function(value,stateVal){
		vartype=typeofvalue,
			isValidValue=type==="string"||Array.isArray(value);

		if(typeofstateVal==="boolean"&&isValidValue){
			returnstateVal?this.addClass(value):this.removeClass(value);
		}

		if(isFunction(value)){
			returnthis.each(function(i){
				jQuery(this).toggleClass(
					value.call(this,i,getClass(this),stateVal),
					stateVal
				);
			});
		}

		returnthis.each(function(){
			varclassName,i,self,classNames;

			if(isValidValue){

				//Toggleindividualclassnames
				i=0;
				self=jQuery(this);
				classNames=classesToArray(value);

				while((className=classNames[i++])){

					//CheckeachclassNamegiven,spaceseparatedlist
					if(self.hasClass(className)){
						self.removeClass(className);
					}else{
						self.addClass(className);
					}
				}

			//Togglewholeclassname
			}elseif(value===undefined||type==="boolean"){
				className=getClass(this);
				if(className){

					//StoreclassNameifset
					dataPriv.set(this,"__className__",className);
				}

				//Iftheelementhasaclassnameorifwe'repassed`false`,
				//thenremovethewholeclassname(iftherewasone,theabovesavedit).
				//Otherwisebringbackwhateverwaspreviouslysaved(ifanything),
				//fallingbacktotheemptystringifnothingwasstored.
				if(this.setAttribute){
					this.setAttribute("class",
						className||value===false?
						"":
						dataPriv.get(this,"__className__")||""
					);
				}
			}
		});
	},

	hasClass:function(selector){
		varclassName,elem,
			i=0;

		className=""+selector+"";
		while((elem=this[i++])){
			if(elem.nodeType===1&&
				(""+stripAndCollapse(getClass(elem))+"").indexOf(className)>-1){
					returntrue;
			}
		}

		returnfalse;
	}
});




varrreturn=/\r/g;

jQuery.fn.extend({
	val:function(value){
		varhooks,ret,valueIsFunction,
			elem=this[0];

		if(!arguments.length){
			if(elem){
				hooks=jQuery.valHooks[elem.type]||
					jQuery.valHooks[elem.nodeName.toLowerCase()];

				if(hooks&&
					"get"inhooks&&
					(ret=hooks.get(elem,"value"))!==undefined
				){
					returnret;
				}

				ret=elem.value;

				//Handlemostcommonstringcases
				if(typeofret==="string"){
					returnret.replace(rreturn,"");
				}

				//Handlecaseswherevalueisnull/undefornumber
				returnret==null?"":ret;
			}

			return;
		}

		valueIsFunction=isFunction(value);

		returnthis.each(function(i){
			varval;

			if(this.nodeType!==1){
				return;
			}

			if(valueIsFunction){
				val=value.call(this,i,jQuery(this).val());
			}else{
				val=value;
			}

			//Treatnull/undefinedas"";convertnumberstostring
			if(val==null){
				val="";

			}elseif(typeofval==="number"){
				val+="";

			}elseif(Array.isArray(val)){
				val=jQuery.map(val,function(value){
					returnvalue==null?"":value+"";
				});
			}

			hooks=jQuery.valHooks[this.type]||jQuery.valHooks[this.nodeName.toLowerCase()];

			//Ifsetreturnsundefined,fallbacktonormalsetting
			if(!hooks||!("set"inhooks)||hooks.set(this,val,"value")===undefined){
				this.value=val;
			}
		});
	}
});

jQuery.extend({
	valHooks:{
		option:{
			get:function(elem){

				varval=jQuery.find.attr(elem,"value");
				returnval!=null?
					val:

					//Support:IE<=10-11only
					//option.textthrowsexceptions(#14686,#14858)
					//Stripandcollapsewhitespace
					//https://html.spec.whatwg.org/#strip-and-collapse-whitespace
					stripAndCollapse(jQuery.text(elem));
			}
		},
		select:{
			get:function(elem){
				varvalue,option,i,
					options=elem.options,
					index=elem.selectedIndex,
					one=elem.type==="select-one",
					values=one?null:[],
					max=one?index+1:options.length;

				if(index<0){
					i=max;

				}else{
					i=one?index:0;
				}

				//Loopthroughalltheselectedoptions
				for(;i<max;i++){
					option=options[i];

					//Support:IE<=9only
					//IE8-9doesn'tupdateselectedafterformreset(#2551)
					if((option.selected||i===index)&&

							//Don'treturnoptionsthataredisabledorinadisabledoptgroup
							!option.disabled&&
							(!option.parentNode.disabled||
								!nodeName(option.parentNode,"optgroup"))){

						//Getthespecificvaluefortheoption
						value=jQuery(option).val();

						//Wedon'tneedanarrayforoneselects
						if(one){
							returnvalue;
						}

						//Multi-Selectsreturnanarray
						values.push(value);
					}
				}

				returnvalues;
			},

			set:function(elem,value){
				varoptionSet,option,
					options=elem.options,
					values=jQuery.makeArray(value),
					i=options.length;

				while(i--){
					option=options[i];

					/*eslint-disableno-cond-assign*/

					if(option.selected=
						jQuery.inArray(jQuery.valHooks.option.get(option),values)>-1
					){
						optionSet=true;
					}

					/*eslint-enableno-cond-assign*/
				}

				//Forcebrowserstobehaveconsistentlywhennon-matchingvalueisset
				if(!optionSet){
					elem.selectedIndex=-1;
				}
				returnvalues;
			}
		}
	}
});

//Radiosandcheckboxesgetter/setter
jQuery.each(["radio","checkbox"],function(){
	jQuery.valHooks[this]={
		set:function(elem,value){
			if(Array.isArray(value)){
				return(elem.checked=jQuery.inArray(jQuery(elem).val(),value)>-1);
			}
		}
	};
	if(!support.checkOn){
		jQuery.valHooks[this].get=function(elem){
			returnelem.getAttribute("value")===null?"on":elem.value;
		};
	}
});




//ReturnjQueryforattributes-onlyinclusion


support.focusin="onfocusin"inwindow;


varrfocusMorph=/^(?:focusinfocus|focusoutblur)$/,
	stopPropagationCallback=function(e){
		e.stopPropagation();
	};

jQuery.extend(jQuery.event,{

	trigger:function(event,data,elem,onlyHandlers){

		vari,cur,tmp,bubbleType,ontype,handle,special,lastElement,
			eventPath=[elem||document],
			type=hasOwn.call(event,"type")?event.type:event,
			namespaces=hasOwn.call(event,"namespace")?event.namespace.split("."):[];

		cur=lastElement=tmp=elem=elem||document;

		//Don'tdoeventsontextandcommentnodes
		if(elem.nodeType===3||elem.nodeType===8){
			return;
		}

		//focus/blurmorphstofocusin/out;ensurewe'renotfiringthemrightnow
		if(rfocusMorph.test(type+jQuery.event.triggered)){
			return;
		}

		if(type.indexOf(".")>-1){

			//Namespacedtrigger;createaregexptomatcheventtypeinhandle()
			namespaces=type.split(".");
			type=namespaces.shift();
			namespaces.sort();
		}
		ontype=type.indexOf(":")<0&&"on"+type;

		//CallercanpassinajQuery.Eventobject,Object,orjustaneventtypestring
		event=event[jQuery.expando]?
			event:
			newjQuery.Event(type,typeofevent==="object"&&event);

		//Triggerbitmask:&1fornativehandlers;&2forjQuery(alwaystrue)
		event.isTrigger=onlyHandlers?2:3;
		event.namespace=namespaces.join(".");
		event.rnamespace=event.namespace?
			newRegExp("(^|\\.)"+namespaces.join("\\.(?:.*\\.|)")+"(\\.|$)"):
			null;

		//Cleanuptheeventincaseitisbeingreused
		event.result=undefined;
		if(!event.target){
			event.target=elem;
		}

		//Cloneanyincomingdataandprependtheevent,creatingthehandlerarglist
		data=data==null?
			[event]:
			jQuery.makeArray(data,[event]);

		//Allowspecialeventstodrawoutsidethelines
		special=jQuery.event.special[type]||{};
		if(!onlyHandlers&&special.trigger&&special.trigger.apply(elem,data)===false){
			return;
		}

		//Determineeventpropagationpathinadvance,perW3Ceventsspec(#9951)
		//Bubbleuptodocument,thentowindow;watchforaglobalownerDocumentvar(#9724)
		if(!onlyHandlers&&!special.noBubble&&!isWindow(elem)){

			bubbleType=special.delegateType||type;
			if(!rfocusMorph.test(bubbleType+type)){
				cur=cur.parentNode;
			}
			for(;cur;cur=cur.parentNode){
				eventPath.push(cur);
				tmp=cur;
			}

			//Onlyaddwindowifwegottodocument(e.g.,notplainobjordetachedDOM)
			if(tmp===(elem.ownerDocument||document)){
				eventPath.push(tmp.defaultView||tmp.parentWindow||window);
			}
		}

		//Firehandlersontheeventpath
		i=0;
		while((cur=eventPath[i++])&&!event.isPropagationStopped()){
			lastElement=cur;
			event.type=i>1?
				bubbleType:
				special.bindType||type;

			//jQueryhandler
			handle=(dataPriv.get(cur,"events")||{})[event.type]&&
				dataPriv.get(cur,"handle");
			if(handle){
				handle.apply(cur,data);
			}

			//Nativehandler
			handle=ontype&&cur[ontype];
			if(handle&&handle.apply&&acceptData(cur)){
				event.result=handle.apply(cur,data);
				if(event.result===false){
					event.preventDefault();
				}
			}
		}
		event.type=type;

		//Ifnobodypreventedthedefaultaction,doitnow
		if(!onlyHandlers&&!event.isDefaultPrevented()){

			if((!special._default||
				special._default.apply(eventPath.pop(),data)===false)&&
				acceptData(elem)){

				//CallanativeDOMmethodonthetargetwiththesamenameastheevent.
				//Don'tdodefaultactionsonwindow,that'swhereglobalvariablesbe(#6170)
				if(ontype&&isFunction(elem[type])&&!isWindow(elem)){

					//Don'tre-triggeranonFOOeventwhenwecallitsFOO()method
					tmp=elem[ontype];

					if(tmp){
						elem[ontype]=null;
					}

					//Preventre-triggeringofthesameevent,sincewealreadybubbleditabove
					jQuery.event.triggered=type;

					if(event.isPropagationStopped()){
						lastElement.addEventListener(type,stopPropagationCallback);
					}

					elem[type]();

					if(event.isPropagationStopped()){
						lastElement.removeEventListener(type,stopPropagationCallback);
					}

					jQuery.event.triggered=undefined;

					if(tmp){
						elem[ontype]=tmp;
					}
				}
			}
		}

		returnevent.result;
	},

	//Piggybackonadonoreventtosimulateadifferentone
	//Usedonlyfor`focus(in|out)`events
	simulate:function(type,elem,event){
		vare=jQuery.extend(
			newjQuery.Event(),
			event,
			{
				type:type,
				isSimulated:true
			}
		);

		jQuery.event.trigger(e,null,elem);
	}

});

jQuery.fn.extend({

	trigger:function(type,data){
		returnthis.each(function(){
			jQuery.event.trigger(type,data,this);
		});
	},
	triggerHandler:function(type,data){
		varelem=this[0];
		if(elem){
			returnjQuery.event.trigger(type,data,elem,true);
		}
	}
});


//Support:Firefox<=44
//Firefoxdoesn'thavefocus(in|out)events
//Relatedticket-https://bugzilla.mozilla.org/show_bug.cgi?id=687787
//
//Support:Chrome<=48-49,Safari<=9.0-9.1
//focus(in|out)eventsfireafterfocus&blurevents,
//whichisspecviolation-http://www.w3.org/TR/DOM-Level-3-Events/#events-focusevent-event-order
//Relatedticket-https://bugs.chromium.org/p/chromium/issues/detail?id=449857
if(!support.focusin){
	jQuery.each({focus:"focusin",blur:"focusout"},function(orig,fix){

		//Attachasinglecapturinghandleronthedocumentwhilesomeonewantsfocusin/focusout
		varhandler=function(event){
			jQuery.event.simulate(fix,event.target,jQuery.event.fix(event));
		};

		jQuery.event.special[fix]={
			setup:function(){
				vardoc=this.ownerDocument||this,
					attaches=dataPriv.access(doc,fix);

				if(!attaches){
					doc.addEventListener(orig,handler,true);
				}
				dataPriv.access(doc,fix,(attaches||0)+1);
			},
			teardown:function(){
				vardoc=this.ownerDocument||this,
					attaches=dataPriv.access(doc,fix)-1;

				if(!attaches){
					doc.removeEventListener(orig,handler,true);
					dataPriv.remove(doc,fix);

				}else{
					dataPriv.access(doc,fix,attaches);
				}
			}
		};
	});
}
varlocation=window.location;

varnonce=Date.now();

varrquery=(/\?/);



//Cross-browserxmlparsing
jQuery.parseXML=function(data){
	varxml;
	if(!data||typeofdata!=="string"){
		returnnull;
	}

	//Support:IE9-11only
	//IEthrowsonparseFromStringwithinvalidinput.
	try{
		xml=(newwindow.DOMParser()).parseFromString(data,"text/xml");
	}catch(e){
		xml=undefined;
	}

	if(!xml||xml.getElementsByTagName("parsererror").length){
		jQuery.error("InvalidXML:"+data);
	}
	returnxml;
};


var
	rbracket=/\[\]$/,
	rCRLF=/\r?\n/g,
	rsubmitterTypes=/^(?:submit|button|image|reset|file)$/i,
	rsubmittable=/^(?:input|select|textarea|keygen)/i;

functionbuildParams(prefix,obj,traditional,add){
	varname;

	if(Array.isArray(obj)){

		//Serializearrayitem.
		jQuery.each(obj,function(i,v){
			if(traditional||rbracket.test(prefix)){

				//Treateacharrayitemasascalar.
				add(prefix,v);

			}else{

				//Itemisnon-scalar(arrayorobject),encodeitsnumericindex.
				buildParams(
					prefix+"["+(typeofv==="object"&&v!=null?i:"")+"]",
					v,
					traditional,
					add
				);
			}
		});

	}elseif(!traditional&&toType(obj)==="object"){

		//Serializeobjectitem.
		for(nameinobj){
			buildParams(prefix+"["+name+"]",obj[name],traditional,add);
		}

	}else{

		//Serializescalaritem.
		add(prefix,obj);
	}
}

//Serializeanarrayofformelementsorasetof
//key/valuesintoaquerystring
jQuery.param=function(a,traditional){
	varprefix,
		s=[],
		add=function(key,valueOrFunction){

			//Ifvalueisafunction,invokeitanduseitsreturnvalue
			varvalue=isFunction(valueOrFunction)?
				valueOrFunction():
				valueOrFunction;

			s[s.length]=encodeURIComponent(key)+"="+
				encodeURIComponent(value==null?"":value);
		};

	//Ifanarraywaspassedin,assumethatitisanarrayofformelements.
	if(Array.isArray(a)||(a.jquery&&!jQuery.isPlainObject(a))){

		//Serializetheformelements
		jQuery.each(a,function(){
			add(this.name,this.value);
		});

	}else{

		//Iftraditional,encodethe"old"way(theway1.3.2orolder
		//didit),otherwiseencodeparamsrecursively.
		for(prefixina){
			buildParams(prefix,a[prefix],traditional,add);
		}
	}

	//Returntheresultingserialization
	returns.join("&");
};

jQuery.fn.extend({
	serialize:function(){
		returnjQuery.param(this.serializeArray());
	},
	serializeArray:function(){
		returnthis.map(function(){

			//CanaddpropHookfor"elements"tofilteroraddformelements
			varelements=jQuery.prop(this,"elements");
			returnelements?jQuery.makeArray(elements):this;
		})
		.filter(function(){
			vartype=this.type;

			//Use.is(":disabled")sothatfieldset[disabled]works
			returnthis.name&&!jQuery(this).is(":disabled")&&
				rsubmittable.test(this.nodeName)&&!rsubmitterTypes.test(type)&&
				(this.checked||!rcheckableType.test(type));
		})
		.map(function(i,elem){
			varval=jQuery(this).val();

			if(val==null){
				returnnull;
			}

			if(Array.isArray(val)){
				returnjQuery.map(val,function(val){
					return{name:elem.name,value:val.replace(rCRLF,"\r\n")};
				});
			}

			return{name:elem.name,value:val.replace(rCRLF,"\r\n")};
		}).get();
	}
});


var
	r20=/%20/g,
	rhash=/#.*$/,
	rantiCache=/([?&])_=[^&]*/,
	rheaders=/^(.*?):[\t]*([^\r\n]*)$/mg,

	//#7653,#8125,#8152:localprotocoldetection
	rlocalProtocol=/^(?:about|app|app-storage|.+-extension|file|res|widget):$/,
	rnoContent=/^(?:GET|HEAD)$/,
	rprotocol=/^\/\//,

	/*Prefilters
	*1)TheyareusefultointroducecustomdataTypes(seeajax/jsonp.jsforanexample)
	*2)Thesearecalled:
	*   -BEFOREaskingforatransport
	*   -AFTERparamserialization(s.dataisastringifs.processDataistrue)
	*3)keyisthedataType
	*4)thecatchallsymbol"*"canbeused
	*5)executionwillstartwithtransportdataTypeandTHENcontinuedownto"*"ifneeded
	*/
	prefilters={},

	/*Transportsbindings
	*1)keyisthedataType
	*2)thecatchallsymbol"*"canbeused
	*3)selectionwillstartwithtransportdataTypeandTHENgoto"*"ifneeded
	*/
	transports={},

	//Avoidcomment-prologcharsequence(#10098);mustappeaselintandevadecompression
	allTypes="*/".concat("*"),

	//Anchortagforparsingthedocumentorigin
	originAnchor=document.createElement("a");
	originAnchor.href=location.href;

//Base"constructor"forjQuery.ajaxPrefilterandjQuery.ajaxTransport
functionaddToPrefiltersOrTransports(structure){

	//dataTypeExpressionisoptionalanddefaultsto"*"
	returnfunction(dataTypeExpression,func){

		if(typeofdataTypeExpression!=="string"){
			func=dataTypeExpression;
			dataTypeExpression="*";
		}

		vardataType,
			i=0,
			dataTypes=dataTypeExpression.toLowerCase().match(rnothtmlwhite)||[];

		if(isFunction(func)){

			//ForeachdataTypeinthedataTypeExpression
			while((dataType=dataTypes[i++])){

				//Prependifrequested
				if(dataType[0]==="+"){
					dataType=dataType.slice(1)||"*";
					(structure[dataType]=structure[dataType]||[]).unshift(func);

				//Otherwiseappend
				}else{
					(structure[dataType]=structure[dataType]||[]).push(func);
				}
			}
		}
	};
}

//Baseinspectionfunctionforprefiltersandtransports
functioninspectPrefiltersOrTransports(structure,options,originalOptions,jqXHR){

	varinspected={},
		seekingTransport=(structure===transports);

	functioninspect(dataType){
		varselected;
		inspected[dataType]=true;
		jQuery.each(structure[dataType]||[],function(_,prefilterOrFactory){
			vardataTypeOrTransport=prefilterOrFactory(options,originalOptions,jqXHR);
			if(typeofdataTypeOrTransport==="string"&&
				!seekingTransport&&!inspected[dataTypeOrTransport]){

				options.dataTypes.unshift(dataTypeOrTransport);
				inspect(dataTypeOrTransport);
				returnfalse;
			}elseif(seekingTransport){
				return!(selected=dataTypeOrTransport);
			}
		});
		returnselected;
	}

	returninspect(options.dataTypes[0])||!inspected["*"]&&inspect("*");
}

//Aspecialextendforajaxoptions
//thattakes"flat"options(nottobedeepextended)
//Fixes#9887
functionajaxExtend(target,src){
	varkey,deep,
		flatOptions=jQuery.ajaxSettings.flatOptions||{};

	for(keyinsrc){
		if(src[key]!==undefined){
			(flatOptions[key]?target:(deep||(deep={})))[key]=src[key];
		}
	}
	if(deep){
		jQuery.extend(true,target,deep);
	}

	returntarget;
}

/*Handlesresponsestoanajaxrequest:
 *-findstherightdataType(mediatesbetweencontent-typeandexpecteddataType)
 *-returnsthecorrespondingresponse
 */
functionajaxHandleResponses(s,jqXHR,responses){

	varct,type,finalDataType,firstDataType,
		contents=s.contents,
		dataTypes=s.dataTypes;

	//RemoveautodataTypeandgetcontent-typeintheprocess
	while(dataTypes[0]==="*"){
		dataTypes.shift();
		if(ct===undefined){
			ct=s.mimeType||jqXHR.getResponseHeader("Content-Type");
		}
	}

	//Checkifwe'redealingwithaknowncontent-type
	if(ct){
		for(typeincontents){
			if(contents[type]&&contents[type].test(ct)){
				dataTypes.unshift(type);
				break;
			}
		}
	}

	//ChecktoseeifwehavearesponsefortheexpecteddataType
	if(dataTypes[0]inresponses){
		finalDataType=dataTypes[0];
	}else{

		//TryconvertibledataTypes
		for(typeinresponses){
			if(!dataTypes[0]||s.converters[type+""+dataTypes[0]]){
				finalDataType=type;
				break;
			}
			if(!firstDataType){
				firstDataType=type;
			}
		}

		//Orjustusefirstone
		finalDataType=finalDataType||firstDataType;
	}

	//IfwefoundadataType
	//WeaddthedataTypetothelistifneeded
	//andreturnthecorrespondingresponse
	if(finalDataType){
		if(finalDataType!==dataTypes[0]){
			dataTypes.unshift(finalDataType);
		}
		returnresponses[finalDataType];
	}
}

/*Chainconversionsgiventherequestandtheoriginalresponse
 *AlsosetstheresponseXXXfieldsonthejqXHRinstance
 */
functionajaxConvert(s,response,jqXHR,isSuccess){
	varconv2,current,conv,tmp,prev,
		converters={},

		//WorkwithacopyofdataTypesincaseweneedtomodifyitforconversion
		dataTypes=s.dataTypes.slice();

	//Createconvertersmapwithlowercasedkeys
	if(dataTypes[1]){
		for(convins.converters){
			converters[conv.toLowerCase()]=s.converters[conv];
		}
	}

	current=dataTypes.shift();

	//ConverttoeachsequentialdataType
	while(current){

		if(s.responseFields[current]){
			jqXHR[s.responseFields[current]]=response;
		}

		//ApplythedataFilterifprovided
		if(!prev&&isSuccess&&s.dataFilter){
			response=s.dataFilter(response,s.dataType);
		}

		prev=current;
		current=dataTypes.shift();

		if(current){

			//There'sonlyworktodoifcurrentdataTypeisnon-auto
			if(current==="*"){

				current=prev;

			//ConvertresponseifprevdataTypeisnon-autoanddiffersfromcurrent
			}elseif(prev!=="*"&&prev!==current){

				//Seekadirectconverter
				conv=converters[prev+""+current]||converters["*"+current];

				//Ifnonefound,seekapair
				if(!conv){
					for(conv2inconverters){

						//Ifconv2outputscurrent
						tmp=conv2.split("");
						if(tmp[1]===current){

							//Ifprevcanbeconvertedtoacceptedinput
							conv=converters[prev+""+tmp[0]]||
								converters["*"+tmp[0]];
							if(conv){

								//Condenseequivalenceconverters
								if(conv===true){
									conv=converters[conv2];

								//Otherwise,inserttheintermediatedataType
								}elseif(converters[conv2]!==true){
									current=tmp[0];
									dataTypes.unshift(tmp[1]);
								}
								break;
							}
						}
					}
				}

				//Applyconverter(ifnotanequivalence)
				if(conv!==true){

					//Unlesserrorsareallowedtobubble,catchandreturnthem
					if(conv&&s.throws){
						response=conv(response);
					}else{
						try{
							response=conv(response);
						}catch(e){
							return{
								state:"parsererror",
								error:conv?e:"Noconversionfrom"+prev+"to"+current
							};
						}
					}
				}
			}
		}
	}

	return{state:"success",data:response};
}

jQuery.extend({

	//Counterforholdingthenumberofactivequeries
	active:0,

	//Last-Modifiedheadercachefornextrequest
	lastModified:{},
	etag:{},

	ajaxSettings:{
		url:location.href,
		type:"GET",
		isLocal:rlocalProtocol.test(location.protocol),
		global:true,
		processData:true,
		async:true,
		contentType:"application/x-www-form-urlencoded;charset=UTF-8",

		/*
		timeout:0,
		data:null,
		dataType:null,
		username:null,
		password:null,
		cache:null,
		throws:false,
		traditional:false,
		headers:{},
		*/

		accepts:{
			"*":allTypes,
			text:"text/plain",
			html:"text/html",
			xml:"application/xml,text/xml",
			json:"application/json,text/javascript"
		},

		contents:{
			xml:/\bxml\b/,
			html:/\bhtml/,
			json:/\bjson\b/
		},

		responseFields:{
			xml:"responseXML",
			text:"responseText",
			json:"responseJSON"
		},

		//Dataconverters
		//Keysseparatesource(orcatchall"*")anddestinationtypeswithasinglespace
		converters:{

			//Convertanythingtotext
			"*text":String,

			//Texttohtml(true=notransformation)
			"texthtml":true,

			//Evaluatetextasajsonexpression
			"textjson":JSON.parse,

			//Parsetextasxml
			"textxml":jQuery.parseXML
		},

		//Foroptionsthatshouldn'tbedeepextended:
		//youcanaddyourowncustomoptionshereif
		//andwhenyoucreateonethatshouldn'tbe
		//deepextended(seeajaxExtend)
		flatOptions:{
			url:true,
			context:true
		}
	},

	//Createsafullfledgedsettingsobjectintotarget
	//withbothajaxSettingsandsettingsfields.
	//Iftargetisomitted,writesintoajaxSettings.
	ajaxSetup:function(target,settings){
		returnsettings?

			//Buildingasettingsobject
			ajaxExtend(ajaxExtend(target,jQuery.ajaxSettings),settings):

			//ExtendingajaxSettings
			ajaxExtend(jQuery.ajaxSettings,target);
	},

	ajaxPrefilter:addToPrefiltersOrTransports(prefilters),
	ajaxTransport:addToPrefiltersOrTransports(transports),

	//Mainmethod
	ajax:function(url,options){

		//Ifurlisanobject,simulatepre-1.5signature
		if(typeofurl==="object"){
			options=url;
			url=undefined;
		}

		//Forceoptionstobeanobject
		options=options||{};

		vartransport,

			//URLwithoutanti-cacheparam
			cacheURL,

			//Responseheaders
			responseHeadersString,
			responseHeaders,

			//timeouthandle
			timeoutTimer,

			//Urlcleanupvar
			urlAnchor,

			//Requeststate(becomesfalseuponsendandtrueuponcompletion)
			completed,

			//Toknowifglobaleventsaretobedispatched
			fireGlobals,

			//Loopvariable
			i,

			//uncachedpartoftheurl
			uncached,

			//Createthefinaloptionsobject
			s=jQuery.ajaxSetup({},options),

			//Callbackscontext
			callbackContext=s.context||s,

			//ContextforglobaleventsiscallbackContextifitisaDOMnodeorjQuerycollection
			globalEventContext=s.context&&
				(callbackContext.nodeType||callbackContext.jquery)?
					jQuery(callbackContext):
					jQuery.event,

			//Deferreds
			deferred=jQuery.Deferred(),
			completeDeferred=jQuery.Callbacks("oncememory"),

			//Status-dependentcallbacks
			statusCode=s.statusCode||{},

			//Headers(theyaresentallatonce)
			requestHeaders={},
			requestHeadersNames={},

			//Defaultabortmessage
			strAbort="canceled",

			//Fakexhr
			jqXHR={
				readyState:0,

				//Buildsheadershashtableifneeded
				getResponseHeader:function(key){
					varmatch;
					if(completed){
						if(!responseHeaders){
							responseHeaders={};
							while((match=rheaders.exec(responseHeadersString))){
								responseHeaders[match[1].toLowerCase()]=match[2];
							}
						}
						match=responseHeaders[key.toLowerCase()];
					}
					returnmatch==null?null:match;
				},

				//Rawstring
				getAllResponseHeaders:function(){
					returncompleted?responseHeadersString:null;
				},

				//Cachestheheader
				setRequestHeader:function(name,value){
					if(completed==null){
						name=requestHeadersNames[name.toLowerCase()]=
							requestHeadersNames[name.toLowerCase()]||name;
						requestHeaders[name]=value;
					}
					returnthis;
				},

				//Overridesresponsecontent-typeheader
				overrideMimeType:function(type){
					if(completed==null){
						s.mimeType=type;
					}
					returnthis;
				},

				//Status-dependentcallbacks
				statusCode:function(map){
					varcode;
					if(map){
						if(completed){

							//Executetheappropriatecallbacks
							jqXHR.always(map[jqXHR.status]);
						}else{

							//Lazy-addthenewcallbacksinawaythatpreservesoldones
							for(codeinmap){
								statusCode[code]=[statusCode[code],map[code]];
							}
						}
					}
					returnthis;
				},

				//Canceltherequest
				abort:function(statusText){
					varfinalText=statusText||strAbort;
					if(transport){
						transport.abort(finalText);
					}
					done(0,finalText);
					returnthis;
				}
			};

		//Attachdeferreds
		deferred.promise(jqXHR);

		//Addprotocolifnotprovided(prefiltersmightexpectit)
		//Handlefalsyurlinthesettingsobject(#10093:consistencywitholdsignature)
		//Wealsousetheurlparameterifavailable
		s.url=((url||s.url||location.href)+"")
			.replace(rprotocol,location.protocol+"//");

		//Aliasmethodoptiontotypeasperticket#12004
		s.type=options.method||options.type||s.method||s.type;

		//ExtractdataTypeslist
		s.dataTypes=(s.dataType||"*").toLowerCase().match(rnothtmlwhite)||[""];

		//Across-domainrequestisinorderwhentheorigindoesn'tmatchthecurrentorigin.
		if(s.crossDomain==null){
			urlAnchor=document.createElement("a");

			//Support:IE<=8-11,Edge12-15
			//IEthrowsexceptiononaccessingthehrefpropertyifurlismalformed,
			//e.g.http://example.com:80x/
			try{
				urlAnchor.href=s.url;

				//Support:IE<=8-11only
				//Anchor'shostpropertyisn'tcorrectlysetwhens.urlisrelative
				urlAnchor.href=urlAnchor.href;
				s.crossDomain=originAnchor.protocol+"//"+originAnchor.host!==
					urlAnchor.protocol+"//"+urlAnchor.host;
			}catch(e){

				//IfthereisanerrorparsingtheURL,assumeitiscrossDomain,
				//itcanberejectedbythetransportifitisinvalid
				s.crossDomain=true;
			}
		}

		//Convertdataifnotalreadyastring
		if(s.data&&s.processData&&typeofs.data!=="string"){
			s.data=jQuery.param(s.data,s.traditional);
		}

		//Applyprefilters
		inspectPrefiltersOrTransports(prefilters,s,options,jqXHR);

		//Ifrequestwasabortedinsideaprefilter,stopthere
		if(completed){
			returnjqXHR;
		}

		//Wecanfireglobaleventsasofnowifaskedto
		//Don'tfireeventsifjQuery.eventisundefinedinanAMD-usagescenario(#15118)
		fireGlobals=jQuery.event&&s.global;

		//Watchforanewsetofrequests
		if(fireGlobals&&jQuery.active++===0){
			jQuery.event.trigger("ajaxStart");
		}

		//Uppercasethetype
		s.type=s.type.toUpperCase();

		//Determineifrequesthascontent
		s.hasContent=!rnoContent.test(s.type);

		//SavetheURLincasewe'retoyingwiththeIf-Modified-Since
		//and/orIf-None-Matchheaderlateron
		//Removehashtosimplifyurlmanipulation
		cacheURL=s.url.replace(rhash,"");

		//Moreoptionshandlingforrequestswithnocontent
		if(!s.hasContent){

			//Rememberthehashsowecanputitback
			uncached=s.url.slice(cacheURL.length);

			//Ifdataisavailableandshouldbeprocessed,appenddatatourl
			if(s.data&&(s.processData||typeofs.data==="string")){
				cacheURL+=(rquery.test(cacheURL)?"&":"?")+s.data;

				//#9682:removedatasothatit'snotusedinaneventualretry
				deletes.data;
			}

			//Addorupdateanti-cacheparamifneeded
			if(s.cache===false){
				cacheURL=cacheURL.replace(rantiCache,"$1");
				uncached=(rquery.test(cacheURL)?"&":"?")+"_="+(nonce++)+uncached;
			}

			//Puthashandanti-cacheontheURLthatwillberequested(gh-1732)
			s.url=cacheURL+uncached;

		//Change'%20'to'+'ifthisisencodedformbodycontent(gh-2658)
		}elseif(s.data&&s.processData&&
			(s.contentType||"").indexOf("application/x-www-form-urlencoded")===0){
			s.data=s.data.replace(r20,"+");
		}

		//SettheIf-Modified-Sinceand/orIf-None-Matchheader,ifinifModifiedmode.
		if(s.ifModified){
			if(jQuery.lastModified[cacheURL]){
				jqXHR.setRequestHeader("If-Modified-Since",jQuery.lastModified[cacheURL]);
			}
			if(jQuery.etag[cacheURL]){
				jqXHR.setRequestHeader("If-None-Match",jQuery.etag[cacheURL]);
			}
		}

		//Setthecorrectheader,ifdataisbeingsent
		if(s.data&&s.hasContent&&s.contentType!==false||options.contentType){
			jqXHR.setRequestHeader("Content-Type",s.contentType);
		}

		//SettheAcceptsheaderfortheserver,dependingonthedataType
		jqXHR.setRequestHeader(
			"Accept",
			s.dataTypes[0]&&s.accepts[s.dataTypes[0]]?
				s.accepts[s.dataTypes[0]]+
					(s.dataTypes[0]!=="*"?","+allTypes+";q=0.01":""):
				s.accepts["*"]
		);

		//Checkforheadersoption
		for(iins.headers){
			jqXHR.setRequestHeader(i,s.headers[i]);
		}

		//Allowcustomheaders/mimetypesandearlyabort
		if(s.beforeSend&&
			(s.beforeSend.call(callbackContext,jqXHR,s)===false||completed)){

			//Abortifnotdonealreadyandreturn
			returnjqXHR.abort();
		}

		//Abortingisnolongeracancellation
		strAbort="abort";

		//Installcallbacksondeferreds
		completeDeferred.add(s.complete);
		jqXHR.done(s.success);
		jqXHR.fail(s.error);

		//Gettransport
		transport=inspectPrefiltersOrTransports(transports,s,options,jqXHR);

		//Ifnotransport,weauto-abort
		if(!transport){
			done(-1,"NoTransport");
		}else{
			jqXHR.readyState=1;

			//Sendglobalevent
			if(fireGlobals){
				globalEventContext.trigger("ajaxSend",[jqXHR,s]);
			}

			//IfrequestwasabortedinsideajaxSend,stopthere
			if(completed){
				returnjqXHR;
			}

			//Timeout
			if(s.async&&s.timeout>0){
				timeoutTimer=window.setTimeout(function(){
					jqXHR.abort("timeout");
				},s.timeout);
			}

			try{
				completed=false;
				transport.send(requestHeaders,done);
			}catch(e){

				//Rethrowpost-completionexceptions
				if(completed){
					throwe;
				}

				//Propagateothersasresults
				done(-1,e);
			}
		}

		//Callbackforwheneverythingisdone
		functiondone(status,nativeStatusText,responses,headers){
			varisSuccess,success,error,response,modified,
				statusText=nativeStatusText;

			//Ignorerepeatinvocations
			if(completed){
				return;
			}

			completed=true;

			//Cleartimeoutifitexists
			if(timeoutTimer){
				window.clearTimeout(timeoutTimer);
			}

			//Dereferencetransportforearlygarbagecollection
			//(nomatterhowlongthejqXHRobjectwillbeused)
			transport=undefined;

			//Cacheresponseheaders
			responseHeadersString=headers||"";

			//SetreadyState
			jqXHR.readyState=status>0?4:0;

			//Determineifsuccessful
			isSuccess=status>=200&&status<300||status===304;

			//Getresponsedata
			if(responses){
				response=ajaxHandleResponses(s,jqXHR,responses);
			}

			//Convertnomatterwhat(thatwayresponseXXXfieldsarealwaysset)
			response=ajaxConvert(s,response,jqXHR,isSuccess);

			//Ifsuccessful,handletypechaining
			if(isSuccess){

				//SettheIf-Modified-Sinceand/orIf-None-Matchheader,ifinifModifiedmode.
				if(s.ifModified){
					modified=jqXHR.getResponseHeader("Last-Modified");
					if(modified){
						jQuery.lastModified[cacheURL]=modified;
					}
					modified=jqXHR.getResponseHeader("etag");
					if(modified){
						jQuery.etag[cacheURL]=modified;
					}
				}

				//ifnocontent
				if(status===204||s.type==="HEAD"){
					statusText="nocontent";

				//ifnotmodified
				}elseif(status===304){
					statusText="notmodified";

				//Ifwehavedata,let'sconvertit
				}else{
					statusText=response.state;
					success=response.data;
					error=response.error;
					isSuccess=!error;
				}
			}else{

				//ExtracterrorfromstatusTextandnormalizefornon-aborts
				error=statusText;
				if(status||!statusText){
					statusText="error";
					if(status<0){
						status=0;
					}
				}
			}

			//Setdataforthefakexhrobject
			jqXHR.status=status;
			jqXHR.statusText=(nativeStatusText||statusText)+"";

			//Success/Error
			if(isSuccess){
				deferred.resolveWith(callbackContext,[success,statusText,jqXHR]);
			}else{
				deferred.rejectWith(callbackContext,[jqXHR,statusText,error]);
			}

			//Status-dependentcallbacks
			jqXHR.statusCode(statusCode);
			statusCode=undefined;

			if(fireGlobals){
				globalEventContext.trigger(isSuccess?"ajaxSuccess":"ajaxError",
					[jqXHR,s,isSuccess?success:error]);
			}

			//Complete
			completeDeferred.fireWith(callbackContext,[jqXHR,statusText]);

			if(fireGlobals){
				globalEventContext.trigger("ajaxComplete",[jqXHR,s]);

				//HandletheglobalAJAXcounter
				if(!(--jQuery.active)){
					jQuery.event.trigger("ajaxStop");
				}
			}
		}

		returnjqXHR;
	},

	getJSON:function(url,data,callback){
		returnjQuery.get(url,data,callback,"json");
	},

	getScript:function(url,callback){
		returnjQuery.get(url,undefined,callback,"script");
	}
});

jQuery.each(["get","post"],function(i,method){
	jQuery[method]=function(url,data,callback,type){

		//Shiftargumentsifdataargumentwasomitted
		if(isFunction(data)){
			type=type||callback;
			callback=data;
			data=undefined;
		}

		//Theurlcanbeanoptionsobject(whichthenmusthave.url)
		returnjQuery.ajax(jQuery.extend({
			url:url,
			type:method,
			dataType:type,
			data:data,
			success:callback
		},jQuery.isPlainObject(url)&&url));
	};
});


jQuery._evalUrl=function(url){
	returnjQuery.ajax({
		url:url,

		//Makethisexplicit,sinceusercanoverridethisthroughajaxSetup(#11264)
		type:"GET",
		dataType:"script",
		cache:true,
		async:false,
		global:false,
		"throws":true
	});
};


jQuery.fn.extend({
	wrapAll:function(html){
		varwrap;

		if(this[0]){
			if(isFunction(html)){
				html=html.call(this[0]);
			}

			//Theelementstowrapthetargetaround
			wrap=jQuery(html,this[0].ownerDocument).eq(0).clone(true);

			if(this[0].parentNode){
				wrap.insertBefore(this[0]);
			}

			wrap.map(function(){
				varelem=this;

				while(elem.firstElementChild){
					elem=elem.firstElementChild;
				}

				returnelem;
			}).append(this);
		}

		returnthis;
	},

	wrapInner:function(html){
		if(isFunction(html)){
			returnthis.each(function(i){
				jQuery(this).wrapInner(html.call(this,i));
			});
		}

		returnthis.each(function(){
			varself=jQuery(this),
				contents=self.contents();

			if(contents.length){
				contents.wrapAll(html);

			}else{
				self.append(html);
			}
		});
	},

	wrap:function(html){
		varhtmlIsFunction=isFunction(html);

		returnthis.each(function(i){
			jQuery(this).wrapAll(htmlIsFunction?html.call(this,i):html);
		});
	},

	unwrap:function(selector){
		this.parent(selector).not("body").each(function(){
			jQuery(this).replaceWith(this.childNodes);
		});
		returnthis;
	}
});


jQuery.expr.pseudos.hidden=function(elem){
	return!jQuery.expr.pseudos.visible(elem);
};
jQuery.expr.pseudos.visible=function(elem){
	return!!(elem.offsetWidth||elem.offsetHeight||elem.getClientRects().length);
};




jQuery.ajaxSettings.xhr=function(){
	try{
		returnnewwindow.XMLHttpRequest();
	}catch(e){}
};

varxhrSuccessStatus={

		//Fileprotocolalwaysyieldsstatuscode0,assume200
		0:200,

		//Support:IE<=9only
		//#1450:sometimesIEreturns1223whenitshouldbe204
		1223:204
	},
	xhrSupported=jQuery.ajaxSettings.xhr();

support.cors=!!xhrSupported&&("withCredentials"inxhrSupported);
support.ajax=xhrSupported=!!xhrSupported;

jQuery.ajaxTransport(function(options){
	varcallback,errorCallback;

	//CrossdomainonlyallowedifsupportedthroughXMLHttpRequest
	if(support.cors||xhrSupported&&!options.crossDomain){
		return{
			send:function(headers,complete){
				vari,
					xhr=options.xhr();

				xhr.open(
					options.type,
					options.url,
					options.async,
					options.username,
					options.password
				);

				//Applycustomfieldsifprovided
				if(options.xhrFields){
					for(iinoptions.xhrFields){
						xhr[i]=options.xhrFields[i];
					}
				}

				//Overridemimetypeifneeded
				if(options.mimeType&&xhr.overrideMimeType){
					xhr.overrideMimeType(options.mimeType);
				}

				//X-Requested-Withheader
				//Forcross-domainrequests,seeingasconditionsforapreflightare
				//akintoajigsawpuzzle,wesimplyneversetittobesure.
				//(itcanalwaysbesetonaper-requestbasisorevenusingajaxSetup)
				//Forsame-domainrequests,won'tchangeheaderifalreadyprovided.
				if(!options.crossDomain&&!headers["X-Requested-With"]){
					headers["X-Requested-With"]="XMLHttpRequest";
				}

				//Setheaders
				for(iinheaders){
					xhr.setRequestHeader(i,headers[i]);
				}

				//Callback
				callback=function(type){
					returnfunction(){
						if(callback){
							callback=errorCallback=xhr.onload=
								xhr.onerror=xhr.onabort=xhr.ontimeout=
									xhr.onreadystatechange=null;

							if(type==="abort"){
								xhr.abort();
							}elseif(type==="error"){

								//Support:IE<=9only
								//Onamanualnativeabort,IE9throws
								//errorsonanypropertyaccessthatisnotreadyState
								if(typeofxhr.status!=="number"){
									complete(0,"error");
								}else{
									complete(

										//File:protocolalwaysyieldsstatus0;see#8605,#14207
										xhr.status,
										xhr.statusText
									);
								}
							}else{
								complete(
									xhrSuccessStatus[xhr.status]||xhr.status,
									xhr.statusText,

									//Support:IE<=9only
									//IE9hasnoXHR2butthrowsonbinary(trac-11426)
									//ForXHR2non-text,letthecallerhandleit(gh-2498)
									(xhr.responseType||"text")!=="text" ||
									typeofxhr.responseText!=="string"?
										{binary:xhr.response}:
										{text:xhr.responseText},
									xhr.getAllResponseHeaders()
								);
							}
						}
					};
				};

				//Listentoevents
				xhr.onload=callback();
				errorCallback=xhr.onerror=xhr.ontimeout=callback("error");

				//Support:IE9only
				//Useonreadystatechangetoreplaceonabort
				//tohandleuncaughtaborts
				if(xhr.onabort!==undefined){
					xhr.onabort=errorCallback;
				}else{
					xhr.onreadystatechange=function(){

						//CheckreadyStatebeforetimeoutasitchanges
						if(xhr.readyState===4){

							//Allowonerrortobecalledfirst,
							//butthatwillnothandleanativeabort
							//Also,saveerrorCallbacktoavariable
							//asxhr.onerrorcannotbeaccessed
							window.setTimeout(function(){
								if(callback){
									errorCallback();
								}
							});
						}
					};
				}

				//Createtheabortcallback
				callback=callback("abort");

				try{

					//Dosendtherequest(thismayraiseanexception)
					xhr.send(options.hasContent&&options.data||null);
				}catch(e){

					//#14683:Onlyrethrowifthishasn'tbeennotifiedasanerroryet
					if(callback){
						throwe;
					}
				}
			},

			abort:function(){
				if(callback){
					callback();
				}
			}
		};
	}
});




//Preventauto-executionofscriptswhennoexplicitdataTypewasprovided(Seegh-2432)
jQuery.ajaxPrefilter(function(s){
	if(s.crossDomain){
		s.contents.script=false;
	}
});

//InstallscriptdataType
jQuery.ajaxSetup({
	accepts:{
		script:"text/javascript,application/javascript,"+
			"application/ecmascript,application/x-ecmascript"
	},
	contents:{
		script:/\b(?:java|ecma)script\b/
	},
	converters:{
		"textscript":function(text){
			jQuery.globalEval(text);
			returntext;
		}
	}
});

//Handlecache'sspecialcaseandcrossDomain
jQuery.ajaxPrefilter("script",function(s){
	if(s.cache===undefined){
		s.cache=false;
	}
	if(s.crossDomain){
		s.type="GET";
	}
});

//Bindscripttaghacktransport
jQuery.ajaxTransport("script",function(s){

	//Thistransportonlydealswithcrossdomainrequests
	if(s.crossDomain){
		varscript,callback;
		return{
			send:function(_,complete){
				script=jQuery("<script>").prop({
					charset:s.scriptCharset,
					src:s.url
				}).on(
					"loaderror",
					callback=function(evt){
						script.remove();
						callback=null;
						if(evt){
							complete(evt.type==="error"?404:200,evt.type);
						}
					}
				);

				//UsenativeDOMmanipulationtoavoidourdomManipAJAXtrickery
				document.head.appendChild(script[0]);
			},
			abort:function(){
				if(callback){
					callback();
				}
			}
		};
	}
});




varoldCallbacks=[],
	rjsonp=/(=)\?(?=&|$)|\?\?/;

//Defaultjsonpsettings
jQuery.ajaxSetup({
	jsonp:"callback",
	jsonpCallback:function(){
		varcallback=oldCallbacks.pop()||(jQuery.expando+"_"+(nonce++));
		this[callback]=true;
		returncallback;
	}
});

//Detect,normalizeoptionsandinstallcallbacksforjsonprequests
jQuery.ajaxPrefilter("jsonjsonp",function(s,originalSettings,jqXHR){

	varcallbackName,overwritten,responseContainer,
		jsonProp=s.jsonp!==false&&(rjsonp.test(s.url)?
			"url":
			typeofs.data==="string"&&
				(s.contentType||"")
					.indexOf("application/x-www-form-urlencoded")===0&&
				rjsonp.test(s.data)&&"data"
		);

	//Handleifftheexpecteddatatypeis"jsonp"orwehaveaparametertoset
	if(jsonProp||s.dataTypes[0]==="jsonp"){

		//Getcallbackname,rememberingpreexistingvalueassociatedwithit
		callbackName=s.jsonpCallback=isFunction(s.jsonpCallback)?
			s.jsonpCallback():
			s.jsonpCallback;

		//Insertcallbackintourlorformdata
		if(jsonProp){
			s[jsonProp]=s[jsonProp].replace(rjsonp,"$1"+callbackName);
		}elseif(s.jsonp!==false){
			s.url+=(rquery.test(s.url)?"&":"?")+s.jsonp+"="+callbackName;
		}

		//Usedataconvertertoretrievejsonafterscriptexecution
		s.converters["scriptjson"]=function(){
			if(!responseContainer){
				jQuery.error(callbackName+"wasnotcalled");
			}
			returnresponseContainer[0];
		};

		//ForcejsondataType
		s.dataTypes[0]="json";

		//Installcallback
		overwritten=window[callbackName];
		window[callbackName]=function(){
			responseContainer=arguments;
		};

		//Clean-upfunction(firesafterconverters)
		jqXHR.always(function(){

			//Ifpreviousvaluedidn'texist-removeit
			if(overwritten===undefined){
				jQuery(window).removeProp(callbackName);

			//Otherwiserestorepreexistingvalue
			}else{
				window[callbackName]=overwritten;
			}

			//Savebackasfree
			if(s[callbackName]){

				//Makesurethatre-usingtheoptionsdoesn'tscrewthingsaround
				s.jsonpCallback=originalSettings.jsonpCallback;

				//Savethecallbacknameforfutureuse
				oldCallbacks.push(callbackName);
			}

			//Callifitwasafunctionandwehavearesponse
			if(responseContainer&&isFunction(overwritten)){
				overwritten(responseContainer[0]);
			}

			responseContainer=overwritten=undefined;
		});

		//Delegatetoscript
		return"script";
	}
});




//Support:Safari8only
//InSafari8documentscreatedviadocument.implementation.createHTMLDocument
//collapsesiblingforms:thesecondonebecomesachildofthefirstone.
//Becauseofthat,thissecuritymeasurehastobedisabledinSafari8.
//https://bugs.webkit.org/show_bug.cgi?id=137337
support.createHTMLDocument=(function(){
	varbody=document.implementation.createHTMLDocument("").body;
	body.innerHTML="<form></form><form></form>";
	returnbody.childNodes.length===2;
})();


//Argument"data"shouldbestringofhtml
//context(optional):Ifspecified,thefragmentwillbecreatedinthiscontext,
//defaultstodocument
//keepScripts(optional):Iftrue,willincludescriptspassedinthehtmlstring
jQuery.parseHTML=function(data,context,keepScripts){
	if(typeofdata!=="string"){
		return[];
	}
	if(typeofcontext==="boolean"){
		keepScripts=context;
		context=false;
	}

	varbase,parsed,scripts;

	if(!context){

		//Stopscriptsorinlineeventhandlersfrombeingexecutedimmediately
		//byusingdocument.implementation
		if(support.createHTMLDocument){
			context=document.implementation.createHTMLDocument("");

			//Setthebasehrefforthecreateddocument
			//soanyparsedelementswithURLs
			//arebasedonthedocument'sURL(gh-2965)
			base=context.createElement("base");
			base.href=document.location.href;
			context.head.appendChild(base);
		}else{
			context=document;
		}
	}

	parsed=rsingleTag.exec(data);
	scripts=!keepScripts&&[];

	//Singletag
	if(parsed){
		return[context.createElement(parsed[1])];
	}

	parsed=buildFragment([data],context,scripts);

	if(scripts&&scripts.length){
		jQuery(scripts).remove();
	}

	returnjQuery.merge([],parsed.childNodes);
};


/**
 *Loadaurlintoapage
 */
jQuery.fn.load=function(url,params,callback){
	varselector,type,response,
		self=this,
		off=url.indexOf("");

	if(off>-1){
		selector=stripAndCollapse(url.slice(off));
		url=url.slice(0,off);
	}

	//Ifit'safunction
	if(isFunction(params)){

		//Weassumethatit'sthecallback
		callback=params;
		params=undefined;

	//Otherwise,buildaparamstring
	}elseif(params&&typeofparams==="object"){
		type="POST";
	}

	//Ifwehaveelementstomodify,maketherequest
	if(self.length>0){
		jQuery.ajax({
			url:url,

			//If"type"variableisundefined,then"GET"methodwillbeused.
			//Makevalueofthisfieldexplicitsince
			//usercanoverrideitthroughajaxSetupmethod
			type:type||"GET",
			dataType:"html",
			data:params
		}).done(function(responseText){

			//Saveresponseforuseincompletecallback
			response=arguments;

			self.html(selector?

				//Ifaselectorwasspecified,locatetherightelementsinadummydiv
				//ExcludescriptstoavoidIE'PermissionDenied'errors
				jQuery("<div>").append(jQuery.parseHTML(responseText)).find(selector):

				//Otherwiseusethefullresult
				responseText);

		//Iftherequestsucceeds,thisfunctiongets"data","status","jqXHR"
		//buttheyareignoredbecauseresponsewassetabove.
		//Ifitfails,thisfunctiongets"jqXHR","status","error"
		}).always(callback&&function(jqXHR,status){
			self.each(function(){
				callback.apply(this,response||[jqXHR.responseText,status,jqXHR]);
			});
		});
	}

	returnthis;
};




//AttachabunchoffunctionsforhandlingcommonAJAXevents
jQuery.each([
	"ajaxStart",
	"ajaxStop",
	"ajaxComplete",
	"ajaxError",
	"ajaxSuccess",
	"ajaxSend"
],function(i,type){
	jQuery.fn[type]=function(fn){
		returnthis.on(type,fn);
	};
});




jQuery.expr.pseudos.animated=function(elem){
	returnjQuery.grep(jQuery.timers,function(fn){
		returnelem===fn.elem;
	}).length;
};




jQuery.offset={
	setOffset:function(elem,options,i){
		varcurPosition,curLeft,curCSSTop,curTop,curOffset,curCSSLeft,calculatePosition,
			position=jQuery.css(elem,"position"),
			curElem=jQuery(elem),
			props={};

		//Setpositionfirst,in-casetop/leftaresetevenonstaticelem
		if(position==="static"){
			elem.style.position="relative";
		}

		curOffset=curElem.offset();
		curCSSTop=jQuery.css(elem,"top");
		curCSSLeft=jQuery.css(elem,"left");
		calculatePosition=(position==="absolute"||position==="fixed")&&
			(curCSSTop+curCSSLeft).indexOf("auto")>-1;

		//Needtobeabletocalculatepositionifeither
		//toporleftisautoandpositioniseitherabsoluteorfixed
		if(calculatePosition){
			curPosition=curElem.position();
			curTop=curPosition.top;
			curLeft=curPosition.left;

		}else{
			curTop=parseFloat(curCSSTop)||0;
			curLeft=parseFloat(curCSSLeft)||0;
		}

		if(isFunction(options)){

			//UsejQuery.extendheretoallowmodificationofcoordinatesargument(gh-1848)
			options=options.call(elem,i,jQuery.extend({},curOffset));
		}

		if(options.top!=null){
			props.top=(options.top-curOffset.top)+curTop;
		}
		if(options.left!=null){
			props.left=(options.left-curOffset.left)+curLeft;
		}

		if("using"inoptions){
			options.using.call(elem,props);

		}else{
			curElem.css(props);
		}
	}
};

jQuery.fn.extend({

	//offset()relatesanelement'sborderboxtothedocumentorigin
	offset:function(options){

		//Preservechainingforsetter
		if(arguments.length){
			returnoptions===undefined?
				this:
				this.each(function(i){
					jQuery.offset.setOffset(this,options,i);
				});
		}

		varrect,win,
			elem=this[0];

		if(!elem){
			return;
		}

		//Returnzerosfordisconnectedandhidden(display:none)elements(gh-2310)
		//Support:IE<=11only
		//RunninggetBoundingClientRectona
		//disconnectednodeinIEthrowsanerror
		if(!elem.getClientRects().length){
			return{top:0,left:0};
		}

		//Getdocument-relativepositionbyaddingviewportscrolltoviewport-relativegBCR
		rect=elem.getBoundingClientRect();
		win=elem.ownerDocument.defaultView;
		return{
			top:rect.top+win.pageYOffset,
			left:rect.left+win.pageXOffset
		};
	},

	//position()relatesanelement'smarginboxtoitsoffsetparent'spaddingbox
	//ThiscorrespondstothebehaviorofCSSabsolutepositioning
	position:function(){
		if(!this[0]){
			return;
		}

		varoffsetParent,offset,doc,
			elem=this[0],
			parentOffset={top:0,left:0};

		//position:fixedelementsareoffsetfromtheviewport,whichitselfalwayshaszerooffset
		if(jQuery.css(elem,"position")==="fixed"){

			//Assumeposition:fixedimpliesavailabilityofgetBoundingClientRect
			offset=elem.getBoundingClientRect();

		}else{
			offset=this.offset();

			//Accountforthe*real*offsetparent,whichcanbethedocumentoritsrootelement
			//whenastaticallypositionedelementisidentified
			doc=elem.ownerDocument;
			offsetParent=elem.offsetParent||doc.documentElement;
			while(offsetParent&&
				(offsetParent===doc.body||offsetParent===doc.documentElement)&&
				jQuery.css(offsetParent,"position")==="static"){

				offsetParent=offsetParent.parentNode;
			}
			if(offsetParent&&offsetParent!==elem&&offsetParent.nodeType===1){

				//Incorporatebordersintoitsoffset,sincetheyareoutsideitscontentorigin
				parentOffset=jQuery(offsetParent).offset();
				parentOffset.top+=jQuery.css(offsetParent,"borderTopWidth",true);
				parentOffset.left+=jQuery.css(offsetParent,"borderLeftWidth",true);
			}
		}

		//Subtractparentoffsetsandelementmargins
		return{
			top:offset.top-parentOffset.top-jQuery.css(elem,"marginTop",true),
			left:offset.left-parentOffset.left-jQuery.css(elem,"marginLeft",true)
		};
	},

	//ThismethodwillreturndocumentElementinthefollowingcases:
	//1)FortheelementinsidetheiframewithoutoffsetParent,thismethodwillreturn
	//   documentElementoftheparentwindow
	//2)Forthehiddenordetachedelement
	//3)Forbodyorhtmlelement,i.e.incaseofthehtmlnode-itwillreturnitself
	//
	//butthoseexceptionswereneverpresentedasareallifeuse-cases
	//andmightbeconsideredasmorepreferableresults.
	//
	//Thislogic,however,isnotguaranteedandcanchangeatanypointinthefuture
	offsetParent:function(){
		returnthis.map(function(){
			varoffsetParent=this.offsetParent;

			while(offsetParent&&jQuery.css(offsetParent,"position")==="static"){
				offsetParent=offsetParent.offsetParent;
			}

			returnoffsetParent||documentElement;
		});
	}
});

//CreatescrollLeftandscrollTopmethods
jQuery.each({scrollLeft:"pageXOffset",scrollTop:"pageYOffset"},function(method,prop){
	vartop="pageYOffset"===prop;

	jQuery.fn[method]=function(val){
		returnaccess(this,function(elem,method,val){

			//Coalescedocumentsandwindows
			varwin;
			if(isWindow(elem)){
				win=elem;
			}elseif(elem.nodeType===9){
				win=elem.defaultView;
			}

			if(val===undefined){
				returnwin?win[prop]:elem[method];
			}

			if(win){
				win.scrollTo(
					!top?val:win.pageXOffset,
					top?val:win.pageYOffset
				);

			}else{
				elem[method]=val;
			}
		},method,val,arguments.length);
	};
});

//Support:Safari<=7-9.1,Chrome<=37-49
//Addthetop/leftcssHooksusingjQuery.fn.position
//Webkitbug:https://bugs.webkit.org/show_bug.cgi?id=29084
//Blinkbug:https://bugs.chromium.org/p/chromium/issues/detail?id=589347
//getComputedStylereturnspercentwhenspecifiedfortop/left/bottom/right;
//ratherthanmakethecssmoduledependontheoffsetmodule,justcheckforithere
jQuery.each(["top","left"],function(i,prop){
	jQuery.cssHooks[prop]=addGetHookIf(support.pixelPosition,
		function(elem,computed){
			if(computed){
				computed=curCSS(elem,prop);

				//IfcurCSSreturnspercentage,fallbacktooffset
				returnrnumnonpx.test(computed)?
					jQuery(elem).position()[prop]+"px":
					computed;
			}
		}
	);
});


//CreateinnerHeight,innerWidth,height,width,outerHeightandouterWidthmethods
jQuery.each({Height:"height",Width:"width"},function(name,type){
	jQuery.each({padding:"inner"+name,content:type,"":"outer"+name},
		function(defaultExtra,funcName){

		//MarginisonlyforouterHeight,outerWidth
		jQuery.fn[funcName]=function(margin,value){
			varchainable=arguments.length&&(defaultExtra||typeofmargin!=="boolean"),
				extra=defaultExtra||(margin===true||value===true?"margin":"border");

			returnaccess(this,function(elem,type,value){
				vardoc;

				if(isWindow(elem)){

					//$(window).outerWidth/Heightreturnw/hincludingscrollbars(gh-1729)
					returnfuncName.indexOf("outer")===0?
						elem["inner"+name]:
						elem.document.documentElement["client"+name];
				}

				//Getdocumentwidthorheight
				if(elem.nodeType===9){
					doc=elem.documentElement;

					//Eitherscroll[Width/Height]oroffset[Width/Height]orclient[Width/Height],
					//whicheverisgreatest
					returnMath.max(
						elem.body["scroll"+name],doc["scroll"+name],
						elem.body["offset"+name],doc["offset"+name],
						doc["client"+name]
					);
				}

				returnvalue===undefined?

					//Getwidthorheightontheelement,requestingbutnotforcingparseFloat
					jQuery.css(elem,type,extra):

					//Setwidthorheightontheelement
					jQuery.style(elem,type,value,extra);
			},type,chainable?margin:undefined,chainable);
		};
	});
});


jQuery.each(("blurfocusfocusinfocusoutresizescrollclickdblclick"+
	"mousedownmouseupmousemovemouseovermouseoutmouseentermouseleave"+
	"changeselectsubmitkeydownkeypresskeyupcontextmenu").split(""),
	function(i,name){

	//Handleeventbinding
	jQuery.fn[name]=function(data,fn){
		returnarguments.length>0?
			this.on(name,null,data,fn):
			this.trigger(name);
	};
});

jQuery.fn.extend({
	hover:function(fnOver,fnOut){
		returnthis.mouseenter(fnOver).mouseleave(fnOut||fnOver);
	}
});




jQuery.fn.extend({

	bind:function(types,data,fn){
		returnthis.on(types,null,data,fn);
	},
	unbind:function(types,fn){
		returnthis.off(types,null,fn);
	},

	delegate:function(selector,types,data,fn){
		returnthis.on(types,selector,data,fn);
	},
	undelegate:function(selector,types,fn){

		//(namespace)or(selector,types[,fn])
		returnarguments.length===1?
			this.off(selector,"**"):
			this.off(types,selector||"**",fn);
	}
});

//Bindafunctiontoacontext,optionallypartiallyapplyingany
//arguments.
//jQuery.proxyisdeprecatedtopromotestandards(specificallyFunction#bind)
//However,itisnotslatedforremovalanytimesoon
jQuery.proxy=function(fn,context){
	vartmp,args,proxy;

	if(typeofcontext==="string"){
		tmp=fn[context];
		context=fn;
		fn=tmp;
	}

	//Quickchecktodetermineiftargetiscallable,inthespec
	//thisthrowsaTypeError,butwewilljustreturnundefined.
	if(!isFunction(fn)){
		returnundefined;
	}

	//Simulatedbind
	args=slice.call(arguments,2);
	proxy=function(){
		returnfn.apply(context||this,args.concat(slice.call(arguments)));
	};

	//Settheguidofuniquehandlertothesameoforiginalhandler,soitcanberemoved
	proxy.guid=fn.guid=fn.guid||jQuery.guid++;

	returnproxy;
};

jQuery.holdReady=function(hold){
	if(hold){
		jQuery.readyWait++;
	}else{
		jQuery.ready(true);
	}
};
jQuery.isArray=Array.isArray;
jQuery.parseJSON=JSON.parse;
jQuery.nodeName=nodeName;
jQuery.isFunction=isFunction;
jQuery.isWindow=isWindow;
jQuery.camelCase=camelCase;
jQuery.type=toType;

jQuery.now=Date.now;

jQuery.isNumeric=function(obj){

	//AsofjQuery3.0,isNumericislimitedto
	//stringsandnumbers(primitivesorobjects)
	//thatcanbecoercedtofinitenumbers(gh-2662)
	vartype=jQuery.type(obj);
	return(type==="number"||type==="string")&&

		//parseFloatNaNsnumeric-castfalsepositives("")
		//...butmisinterpretsleading-numberstrings,particularlyhexliterals("0x...")
		//subtractionforcesinfinitiestoNaN
		!isNaN(obj-parseFloat(obj));
};




//RegisterasanamedAMDmodule,sincejQuerycanbeconcatenatedwithother
//filesthatmayusedefine,butnotviaaproperconcatenationscriptthat
//understandsanonymousAMDmodules.AnamedAMDissafestandmostrobust
//waytoregister.LowercasejqueryisusedbecauseAMDmodulenamesare
//derivedfromfilenames,andjQueryisnormallydeliveredinalowercase
//filename.DothisaftercreatingtheglobalsothatifanAMDmodulewants
//tocallnoConflicttohidethisversionofjQuery,itwillwork.

//Notethatformaximumportability,librariesthatarenotjQueryshould
//declarethemselvesasanonymousmodules,andavoidsettingaglobalifan
//AMDloaderispresent.jQueryisaspecialcase.Formoreinformation,see
//https://github.com/jrburke/requirejs/wiki/Updating-existing-libraries#wiki-anon

if(typeofdefine==="function"&&define.amd){
	define("jquery",[],function(){
		returnjQuery;
	});
}




var

	//MapoverjQueryincaseofoverwrite
	_jQuery=window.jQuery,

	//Mapoverthe$incaseofoverwrite
	_$=window.$;

jQuery.noConflict=function(deep){
	if(window.$===jQuery){
		window.$=_$;
	}

	if(deep&&window.jQuery===jQuery){
		window.jQuery=_jQuery;
	}

	returnjQuery;
};

//ExposejQueryand$identifiers,eveninAMD
//(#7102#comment:10,https://github.com/jquery/jquery/pull/557)
//andCommonJSforbrowseremulators(#13566)
if(!noGlobal){
	window.jQuery=window.$=jQuery;
}




returnjQuery;
});