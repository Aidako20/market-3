/*!jQueryUI-v1.12.1-2019-01-18
*http://jqueryui.com
*Includes:widget.js,position.js,data.js,disable-selection.js,focusable.js,keycode.js,scroll-parent.js,unique-id.js,widgets/draggable.js,widgets/droppable.js,widgets/resizable.js,widgets/selectable.js,widgets/sortable.js,widgets/autocomplete.js,widgets/datepicker.js,widgets/menu.js,widgets/mouse.js,widgets/tooltip.js,effect.js,effects/effect-bounce.js
*CopyrightjQueryFoundationandothercontributors;LicensedMIT*/

(function(factory){
	if(typeofdefine==="function"&&define.amd){

		//AMD.Registerasananonymousmodule.
		define(["jquery"],factory);
	}else{

		//Browserglobals
		factory(jQuery);
	}
}(function($){

$.ui=$.ui||{};

varversion=$.ui.version="1.12.1";


/*!
 *jQueryUIWidget1.12.1
 *http://jqueryui.com
 *
 *CopyrightjQueryFoundationandothercontributors
 *ReleasedundertheMITlicense.
 *http://jquery.org/license
 */

//>>label:Widget
//>>group:Core
//>>description:ProvidesafactoryforcreatingstatefulwidgetswithacommonAPI.
//>>docs:http://api.jqueryui.com/jQuery.widget/
//>>demos:http://jqueryui.com/widget/



varwidgetUuid=0;
varwidgetSlice=Array.prototype.slice;

$.cleanData=(function(orig){
	returnfunction(elems){
		varevents,elem,i;
		for(i=0;(elem=elems[i])!=null;i++){
			try{

				//Onlytriggerremovewhennecessarytosavetime
				events=$._data(elem,"events");
				if(events&&events.remove){
					$(elem).triggerHandler("remove");
				}

			//Http://bugs.jquery.com/ticket/8235
			}catch(e){}
		}
		orig(elems);
	};
})($.cleanData);

$.widget=function(name,base,prototype){
	varexistingConstructor,constructor,basePrototype;

	//ProxiedPrototypeallowstheprovidedprototypetoremainunmodified
	//sothatitcanbeusedasamixinformultiplewidgets(#8876)
	varproxiedPrototype={};

	varnamespace=name.split(".")[0];
	name=name.split(".")[1];
	varfullName=namespace+"-"+name;

	if(!prototype){
		prototype=base;
		base=$.Widget;
	}

	if($.isArray(prototype)){
		prototype=$.extend.apply(null,[{}].concat(prototype));
	}

	//Createselectorforplugin
	$.expr[":"][fullName.toLowerCase()]=function(elem){
		return!!$.data(elem,fullName);
	};

	$[namespace]=$[namespace]||{};
	existingConstructor=$[namespace][name];
	constructor=$[namespace][name]=function(options,element){

		//Allowinstantiationwithout"new"keyword
		if(!this._createWidget){
			returnnewconstructor(options,element);
		}

		//Allowinstantiationwithoutinitializingforsimpleinheritance
		//mustuse"new"keyword(thecodeabovealwayspassesargs)
		if(arguments.length){
			this._createWidget(options,element);
		}
	};

	//Extendwiththeexistingconstructortocarryoveranystaticproperties
	$.extend(constructor,existingConstructor,{
		version:prototype.version,

		//Copytheobjectusedtocreatetheprototypeincaseweneedto
		//redefinethewidgetlater
		_proto:$.extend({},prototype),

		//Trackwidgetsthatinheritfromthiswidgetincasethiswidgetis
		//redefinedafterawidgetinheritsfromit
		_childConstructors:[]
	});

	basePrototype=newbase();

	//Weneedtomaketheoptionshashapropertydirectlyonthenewinstance
	//otherwisewe'llmodifytheoptionshashontheprototypethatwe're
	//inheritingfrom
	basePrototype.options=$.widget.extend({},basePrototype.options);
	$.each(prototype,function(prop,value){
		if(!$.isFunction(value)){
			proxiedPrototype[prop]=value;
			return;
		}
		proxiedPrototype[prop]=(function(){
			function_super(){
				returnbase.prototype[prop].apply(this,arguments);
			}

			function_superApply(args){
				returnbase.prototype[prop].apply(this,args);
			}

			returnfunction(){
				var__super=this._super;
				var__superApply=this._superApply;
				varreturnValue;

				this._super=_super;
				this._superApply=_superApply;

				returnValue=value.apply(this,arguments);

				this._super=__super;
				this._superApply=__superApply;

				returnreturnValue;
			};
		})();
	});
	constructor.prototype=$.widget.extend(basePrototype,{

		//TODO:removesupportforwidgetEventPrefix
		//alwaysusethename+acolonastheprefix,e.g.,draggable:start
		//don'tprefixforwidgetsthataren'tDOM-based
		widgetEventPrefix:existingConstructor?(basePrototype.widgetEventPrefix||name):name
	},proxiedPrototype,{
		constructor:constructor,
		namespace:namespace,
		widgetName:name,
		widgetFullName:fullName
	});

	//Ifthiswidgetisbeingredefinedthenweneedtofindallwidgetsthat
	//areinheritingfromitandredefineallofthemsothattheyinheritfrom
	//thenewversionofthiswidget.We'reessentiallytryingtoreplaceone
	//levelintheprototypechain.
	if(existingConstructor){
		$.each(existingConstructor._childConstructors,function(i,child){
			varchildPrototype=child.prototype;

			//Redefinethechildwidgetusingthesameprototypethatwas
			//originallyused,butinheritfromthenewversionofthebase
			$.widget(childPrototype.namespace+"."+childPrototype.widgetName,constructor,
				child._proto);
		});

		//Removethelistofexistingchildconstructorsfromtheoldconstructor
		//sotheoldchildconstructorscanbegarbagecollected
		deleteexistingConstructor._childConstructors;
	}else{
		base._childConstructors.push(constructor);
	}

	$.widget.bridge(name,constructor);

	returnconstructor;
};

$.widget.extend=function(target){
	varinput=widgetSlice.call(arguments,1);
	varinputIndex=0;
	varinputLength=input.length;
	varkey;
	varvalue;

	for(;inputIndex<inputLength;inputIndex++){
		for(keyininput[inputIndex]){
			value=input[inputIndex][key];
			if(input[inputIndex].hasOwnProperty(key)&&value!==undefined){

				//Cloneobjects
				if($.isPlainObject(value)){
					target[key]=$.isPlainObject(target[key])?
						$.widget.extend({},target[key],value):

						//Don'textendstrings,arrays,etc.withobjects
						$.widget.extend({},value);

				//Copyeverythingelsebyreference
				}else{
					target[key]=value;
				}
			}
		}
	}
	returntarget;
};

$.widget.bridge=function(name,object){
	varfullName=object.prototype.widgetFullName||name;
	$.fn[name]=function(options){
		varisMethodCall=typeofoptions==="string";
		varargs=widgetSlice.call(arguments,1);
		varreturnValue=this;

		if(isMethodCall){

			//Ifthisisanemptycollection,weneedtohavetheinstancemethod
			//returnundefinedinsteadofthejQueryinstance
			if(!this.length&&options==="instance"){
				returnValue=undefined;
			}else{
				this.each(function(){
					varmethodValue;
					varinstance=$.data(this,fullName);

					if(options==="instance"){
						returnValue=instance;
						returnfalse;
					}

					if(!instance){
						return$.error("cannotcallmethodson"+name+
							"priortoinitialization;"+
							"attemptedtocallmethod'"+options+"'");
					}

					if(!$.isFunction(instance[options])||options.charAt(0)==="_"){
						return$.error("nosuchmethod'"+options+"'for"+name+
							"widgetinstance");
					}

					methodValue=instance[options].apply(instance,args);

					if(methodValue!==instance&&methodValue!==undefined){
						returnValue=methodValue&&methodValue.jquery?
							returnValue.pushStack(methodValue.get()):
							methodValue;
						returnfalse;
					}
				});
			}
		}else{

			//Allowmultiplehashestobepassedoninit
			if(args.length){
				options=$.widget.extend.apply(null,[options].concat(args));
			}

			this.each(function(){
				varinstance=$.data(this,fullName);
				if(instance){
					instance.option(options||{});
					if(instance._init){
						instance._init();
					}
				}else{
					$.data(this,fullName,newobject(options,this));
				}
			});
		}

		returnreturnValue;
	};
};

$.Widget=function(/*options,element*/){};
$.Widget._childConstructors=[];

$.Widget.prototype={
	widgetName:"widget",
	widgetEventPrefix:"",
	defaultElement:"<div>",

	options:{
		classes:{},
		disabled:false,

		//Callbacks
		create:null
	},

	_createWidget:function(options,element){
		element=$(element||this.defaultElement||this)[0];
		this.element=$(element);
		this.uuid=widgetUuid++;
		this.eventNamespace="."+this.widgetName+this.uuid;

		this.bindings=$();
		this.hoverable=$();
		this.focusable=$();
		this.classesElementLookup={};

		if(element!==this){
			$.data(element,this.widgetFullName,this);
			this._on(true,this.element,{
				remove:function(event){
					if(event.target===element){
						this.destroy();
					}
				}
			});
			this.document=$(element.style?

				//Elementwithinthedocument
				element.ownerDocument:

				//Elementiswindowordocument
				element.document||element);
			this.window=$(this.document[0].defaultView||this.document[0].parentWindow);
		}

		this.options=$.widget.extend({},
			this.options,
			this._getCreateOptions(),
			options);

		this._create();

		if(this.options.disabled){
			this._setOptionDisabled(this.options.disabled);
		}

		this._trigger("create",null,this._getCreateEventData());
		this._init();
	},

	_getCreateOptions:function(){
		return{};
	},

	_getCreateEventData:$.noop,

	_create:$.noop,

	_init:$.noop,

	destroy:function(){
		varthat=this;

		this._destroy();
		$.each(this.classesElementLookup,function(key,value){
			that._removeClass(value,key);
		});

		//Wecanprobablyremovetheunbindcallsin2.0
		//alleventbindingsshouldgothroughthis._on()
		this.element
			.off(this.eventNamespace)
			.removeData(this.widgetFullName);
		this.widget()
			.off(this.eventNamespace)
			.removeAttr("aria-disabled");

		//Cleanupeventsandstates
		this.bindings.off(this.eventNamespace);
	},

	_destroy:$.noop,

	widget:function(){
		returnthis.element;
	},

	option:function(key,value){
		varoptions=key;
		varparts;
		varcurOption;
		vari;

		if(arguments.length===0){

			//Don'treturnareferencetotheinternalhash
			return$.widget.extend({},this.options);
		}

		if(typeofkey==="string"){

			//Handlenestedkeys,e.g.,"foo.bar"=>{foo:{bar:___}}
			options={};
			parts=key.split(".");
			key=parts.shift();
			if(parts.length){
				curOption=options[key]=$.widget.extend({},this.options[key]);
				for(i=0;i<parts.length-1;i++){
					curOption[parts[i]]=curOption[parts[i]]||{};
					curOption=curOption[parts[i]];
				}
				key=parts.pop();
				if(arguments.length===1){
					returncurOption[key]===undefined?null:curOption[key];
				}
				curOption[key]=value;
			}else{
				if(arguments.length===1){
					returnthis.options[key]===undefined?null:this.options[key];
				}
				options[key]=value;
			}
		}

		this._setOptions(options);

		returnthis;
	},

	_setOptions:function(options){
		varkey;

		for(keyinoptions){
			this._setOption(key,options[key]);
		}

		returnthis;
	},

	_setOption:function(key,value){
		if(key==="classes"){
			this._setOptionClasses(value);
		}

		this.options[key]=value;

		if(key==="disabled"){
			this._setOptionDisabled(value);
		}

		returnthis;
	},

	_setOptionClasses:function(value){
		varclassKey,elements,currentElements;

		for(classKeyinvalue){
			currentElements=this.classesElementLookup[classKey];
			if(value[classKey]===this.options.classes[classKey]||
					!currentElements||
					!currentElements.length){
				continue;
			}

			//WearedoingthistocreateanewjQueryobjectbecausethe_removeClass()call
			//onthenextlineisgoingtodestroythereferencetothecurrentelementsbeing
			//tracked.Weneedtosaveacopyofthiscollectionsothatwecanaddthenewclasses
			//below.
			elements=$(currentElements.get());
			this._removeClass(currentElements,classKey);

			//Wedon'tuse_addClass()here,becausethatusesthis.options.classes
			//forgeneratingthestringofclasses.Wewanttousethevaluepassedinfrom
			//_setOption(),thisisthenewvalueoftheclassesoptionwhichwaspassedto
			//_setOption().Wepassthisvaluedirectlyto_classes().
			elements.addClass(this._classes({
				element:elements,
				keys:classKey,
				classes:value,
				add:true
			}));
		}
	},

	_setOptionDisabled:function(value){
		this._toggleClass(this.widget(),this.widgetFullName+"-disabled",null,!!value);

		//Ifthewidgetisbecomingdisabled,thennothingisinteractive
		if(value){
			this._removeClass(this.hoverable,null,"ui-state-hover");
			this._removeClass(this.focusable,null,"ui-state-focus");
		}
	},

	enable:function(){
		returnthis._setOptions({disabled:false});
	},

	disable:function(){
		returnthis._setOptions({disabled:true});
	},

	_classes:function(options){
		varfull=[];
		varthat=this;

		options=$.extend({
			element:this.element,
			classes:this.options.classes||{}
		},options);

		functionprocessClassString(classes,checkOption){
			varcurrent,i;
			for(i=0;i<classes.length;i++){
				current=that.classesElementLookup[classes[i]]||$();
				if(options.add){
					current=$($.unique(current.get().concat(options.element.get())));
				}else{
					current=$(current.not(options.element).get());
				}
				that.classesElementLookup[classes[i]]=current;
				full.push(classes[i]);
				if(checkOption&&options.classes[classes[i]]){
					full.push(options.classes[classes[i]]);
				}
			}
		}

		this._on(options.element,{
			"remove":"_untrackClassesElement"
		});

		if(options.keys){
			processClassString(options.keys.match(/\S+/g)||[],true);
		}
		if(options.extra){
			processClassString(options.extra.match(/\S+/g)||[]);
		}

		returnfull.join("");
	},

	_untrackClassesElement:function(event){
		varthat=this;
		$.each(that.classesElementLookup,function(key,value){
			if($.inArray(event.target,value)!==-1){
				that.classesElementLookup[key]=$(value.not(event.target).get());
			}
		});
	},

	_removeClass:function(element,keys,extra){
		returnthis._toggleClass(element,keys,extra,false);
	},

	_addClass:function(element,keys,extra){
		returnthis._toggleClass(element,keys,extra,true);
	},

	_toggleClass:function(element,keys,extra,add){
		add=(typeofadd==="boolean")?add:extra;
		varshift=(typeofelement==="string"||element===null),
			options={
				extra:shift?keys:extra,
				keys:shift?element:keys,
				element:shift?this.element:element,
				add:add
			};
		options.element.toggleClass(this._classes(options),add);
		returnthis;
	},

	_on:function(suppressDisabledCheck,element,handlers){
		vardelegateElement;
		varinstance=this;

		//NosuppressDisabledCheckflag,shufflearguments
		if(typeofsuppressDisabledCheck!=="boolean"){
			handlers=element;
			element=suppressDisabledCheck;
			suppressDisabledCheck=false;
		}

		//Noelementargument,shuffleandusethis.element
		if(!handlers){
			handlers=element;
			element=this.element;
			delegateElement=this.widget();
		}else{
			element=delegateElement=$(element);
			this.bindings=this.bindings.add(element);
		}

		$.each(handlers,function(event,handler){
			functionhandlerProxy(){

				//Allowwidgetstocustomizethedisabledhandling
				//-disabledasanarrayinsteadofboolean
				//-disabledclassasmethodfordisablingindividualparts
				if(!suppressDisabledCheck&&
						(instance.options.disabled===true||
						$(this).hasClass("ui-state-disabled"))){
					return;
				}
				return(typeofhandler==="string"?instance[handler]:handler)
					.apply(instance,arguments);
			}

			//Copytheguidsodirectunbindingworks
			if(typeofhandler!=="string"){
				handlerProxy.guid=handler.guid=
					handler.guid||handlerProxy.guid||$.guid++;
			}

			varmatch=event.match(/^([\w:-]*)\s*(.*)$/);
			vareventName=match[1]+instance.eventNamespace;
			varselector=match[2];

			if(selector){
				delegateElement.on(eventName,selector,handlerProxy);
			}else{
				element.on(eventName,handlerProxy);
			}
		});
	},

	_off:function(element,eventName){
		eventName=(eventName||"").split("").join(this.eventNamespace+"")+
			this.eventNamespace;
		element.off(eventName).off(eventName);

		//Clearthestacktoavoidmemoryleaks(#10056)
		this.bindings=$(this.bindings.not(element).get());
		this.focusable=$(this.focusable.not(element).get());
		this.hoverable=$(this.hoverable.not(element).get());
	},

	_delay:function(handler,delay){
		functionhandlerProxy(){
			return(typeofhandler==="string"?instance[handler]:handler)
				.apply(instance,arguments);
		}
		varinstance=this;
		returnsetTimeout(handlerProxy,delay||0);
	},

	_hoverable:function(element){
		this.hoverable=this.hoverable.add(element);
		this._on(element,{
			mouseenter:function(event){
				this._addClass($(event.currentTarget),null,"ui-state-hover");
			},
			mouseleave:function(event){
				this._removeClass($(event.currentTarget),null,"ui-state-hover");
			}
		});
	},

	_focusable:function(element){
		this.focusable=this.focusable.add(element);
		this._on(element,{
			focusin:function(event){
				this._addClass($(event.currentTarget),null,"ui-state-focus");
			},
			focusout:function(event){
				this._removeClass($(event.currentTarget),null,"ui-state-focus");
			}
		});
	},

	_trigger:function(type,event,data){
		varprop,orig;
		varcallback=this.options[type];

		data=data||{};
		event=$.Event(event);
		event.type=(type===this.widgetEventPrefix?
			type:
			this.widgetEventPrefix+type).toLowerCase();

		//Theoriginaleventmaycomefromanyelement
		//soweneedtoresetthetargetonthenewevent
		event.target=this.element[0];

		//Copyoriginaleventpropertiesovertothenewevent
		orig=event.originalEvent;
		if(orig){
			for(propinorig){
				if(!(propinevent)){
					event[prop]=orig[prop];
				}
			}
		}

		this.element.trigger(event,data);
		return!($.isFunction(callback)&&
			callback.apply(this.element[0],[event].concat(data))===false||
			event.isDefaultPrevented());
	}
};

$.each({show:"fadeIn",hide:"fadeOut"},function(method,defaultEffect){
	$.Widget.prototype["_"+method]=function(element,options,callback){
		if(typeofoptions==="string"){
			options={effect:options};
		}

		varhasOptions;
		vareffectName=!options?
			method:
			options===true||typeofoptions==="number"?
				defaultEffect:
				options.effect||defaultEffect;

		options=options||{};
		if(typeofoptions==="number"){
			options={duration:options};
		}

		hasOptions=!$.isEmptyObject(options);
		options.complete=callback;

		if(options.delay){
			element.delay(options.delay);
		}

		if(hasOptions&&$.effects&&$.effects.effect[effectName]){
			element[method](options);
		}elseif(effectName!==method&&element[effectName]){
			element[effectName](options.duration,options.easing,callback);
		}else{
			element.queue(function(next){
				$(this)[method]();
				if(callback){
					callback.call(element[0]);
				}
				next();
			});
		}
	};
});

varwidget=$.widget;


/*!
 *jQueryUIPosition1.12.1
 *http://jqueryui.com
 *
 *CopyrightjQueryFoundationandothercontributors
 *ReleasedundertheMITlicense.
 *http://jquery.org/license
 *
 *http://api.jqueryui.com/position/
 */

//>>label:Position
//>>group:Core
//>>description:Positionselementsrelativetootherelements.
//>>docs:http://api.jqueryui.com/position/
//>>demos:http://jqueryui.com/position/


(function(){
varcachedScrollbarWidth,
	max=Math.max,
	abs=Math.abs,
	rhorizontal=/left|center|right/,
	rvertical=/top|center|bottom/,
	roffset=/[\+\-]\d+(\.[\d]+)?%?/,
	rposition=/^\w+/,
	rpercent=/%$/,
	_position=$.fn.position;

functiongetOffsets(offsets,width,height){
	return[
		parseFloat(offsets[0])*(rpercent.test(offsets[0])?width/100:1),
		parseFloat(offsets[1])*(rpercent.test(offsets[1])?height/100:1)
	];
}

functionparseCss(element,property){
	returnparseInt($.css(element,property),10)||0;
}

functiongetDimensions(elem){
	varraw=elem[0];
	if(raw.nodeType===9){
		return{
			width:elem.width(),
			height:elem.height(),
			offset:{top:0,left:0}
		};
	}
	if($.isWindow(raw)){
		return{
			width:elem.width(),
			height:elem.height(),
			offset:{top:elem.scrollTop(),left:elem.scrollLeft()}
		};
	}
	if(raw.preventDefault){
		return{
			width:0,
			height:0,
			offset:{top:raw.pageY,left:raw.pageX}
		};
	}
	return{
		width:elem.outerWidth(),
		height:elem.outerHeight(),
		offset:elem.offset()
	};
}

$.position={
	scrollbarWidth:function(){
		if(cachedScrollbarWidth!==undefined){
			returncachedScrollbarWidth;
		}
		varw1,w2,
			div=$("<div"+
				"style='display:block;position:absolute;width:50px;height:50px;overflow:hidden;'>"+
				"<divstyle='height:100px;width:auto;'></div></div>"),
			innerDiv=div.children()[0];

		$("body").append(div);
		w1=innerDiv.offsetWidth;
		div.css("overflow","scroll");

		w2=innerDiv.offsetWidth;

		if(w1===w2){
			w2=div[0].clientWidth;
		}

		div.remove();

		return(cachedScrollbarWidth=w1-w2);
	},
	getScrollInfo:function(within){
		varoverflowX=within.isWindow||within.isDocument?"":
				within.element.css("overflow-x"),
			overflowY=within.isWindow||within.isDocument?"":
				within.element.css("overflow-y"),
			hasOverflowX=overflowX==="scroll"||
				(overflowX==="auto"&&within.width<within.element[0].scrollWidth),
			hasOverflowY=overflowY==="scroll"||
				(overflowY==="auto"&&within.height<within.element[0].scrollHeight);
		return{
			width:hasOverflowY?$.position.scrollbarWidth():0,
			height:hasOverflowX?$.position.scrollbarWidth():0
		};
	},
	getWithinInfo:function(element){
		varwithinElement=$(element||window),
			isWindow=$.isWindow(withinElement[0]),
			isDocument=!!withinElement[0]&&withinElement[0].nodeType===9,
			hasOffset=!isWindow&&!isDocument;
		return{
			element:withinElement,
			isWindow:isWindow,
			isDocument:isDocument,
			offset:hasOffset?$(element).offset():{left:0,top:0},
			scrollLeft:withinElement.scrollLeft(),
			scrollTop:withinElement.scrollTop(),
			width:withinElement.outerWidth(),
			height:withinElement.outerHeight()
		};
	}
};

$.fn.position=function(options){
	if(!options||!options.of){
		return_position.apply(this,arguments);
	}

	//Makeacopy,wedon'twanttomodifyarguments
	options=$.extend({},options);

	varatOffset,targetWidth,targetHeight,targetOffset,basePosition,dimensions,
		target=$(options.of),
		within=$.position.getWithinInfo(options.within),
		scrollInfo=$.position.getScrollInfo(within),
		collision=(options.collision||"flip").split(""),
		offsets={};

	dimensions=getDimensions(target);
	if(target[0].preventDefault){

		//Forcelefttoptoallowflipping
		options.at="lefttop";
	}
	targetWidth=dimensions.width;
	targetHeight=dimensions.height;
	targetOffset=dimensions.offset;

	//ClonetoreuseoriginaltargetOffsetlater
	basePosition=$.extend({},targetOffset);

	//Forcemyandattohavevalidhorizontalandverticalpositions
	//ifavalueismissingorinvalid,itwillbeconvertedtocenter
	$.each(["my","at"],function(){
		varpos=(options[this]||"").split(""),
			horizontalOffset,
			verticalOffset;

		if(pos.length===1){
			pos=rhorizontal.test(pos[0])?
				pos.concat(["center"]):
				rvertical.test(pos[0])?
					["center"].concat(pos):
					["center","center"];
		}
		pos[0]=rhorizontal.test(pos[0])?pos[0]:"center";
		pos[1]=rvertical.test(pos[1])?pos[1]:"center";

		//Calculateoffsets
		horizontalOffset=roffset.exec(pos[0]);
		verticalOffset=roffset.exec(pos[1]);
		offsets[this]=[
			horizontalOffset?horizontalOffset[0]:0,
			verticalOffset?verticalOffset[0]:0
		];

		//Reducetojustthepositionswithouttheoffsets
		options[this]=[
			rposition.exec(pos[0])[0],
			rposition.exec(pos[1])[0]
		];
	});

	//Normalizecollisionoption
	if(collision.length===1){
		collision[1]=collision[0];
	}

	if(options.at[0]==="right"){
		basePosition.left+=targetWidth;
	}elseif(options.at[0]==="center"){
		basePosition.left+=targetWidth/2;
	}

	if(options.at[1]==="bottom"){
		basePosition.top+=targetHeight;
	}elseif(options.at[1]==="center"){
		basePosition.top+=targetHeight/2;
	}

	atOffset=getOffsets(offsets.at,targetWidth,targetHeight);
	basePosition.left+=atOffset[0];
	basePosition.top+=atOffset[1];

	returnthis.each(function(){
		varcollisionPosition,using,
			elem=$(this),
			elemWidth=elem.outerWidth(),
			elemHeight=elem.outerHeight(),
			marginLeft=parseCss(this,"marginLeft"),
			marginTop=parseCss(this,"marginTop"),
			collisionWidth=elemWidth+marginLeft+parseCss(this,"marginRight")+
				scrollInfo.width,
			collisionHeight=elemHeight+marginTop+parseCss(this,"marginBottom")+
				scrollInfo.height,
			position=$.extend({},basePosition),
			myOffset=getOffsets(offsets.my,elem.outerWidth(),elem.outerHeight());

		if(options.my[0]==="right"){
			position.left-=elemWidth;
		}elseif(options.my[0]==="center"){
			position.left-=elemWidth/2;
		}

		if(options.my[1]==="bottom"){
			position.top-=elemHeight;
		}elseif(options.my[1]==="center"){
			position.top-=elemHeight/2;
		}

		position.left+=myOffset[0];
		position.top+=myOffset[1];

		collisionPosition={
			marginLeft:marginLeft,
			marginTop:marginTop
		};

		$.each(["left","top"],function(i,dir){
			if($.ui.position[collision[i]]){
				$.ui.position[collision[i]][dir](position,{
					targetWidth:targetWidth,
					targetHeight:targetHeight,
					elemWidth:elemWidth,
					elemHeight:elemHeight,
					collisionPosition:collisionPosition,
					collisionWidth:collisionWidth,
					collisionHeight:collisionHeight,
					offset:[atOffset[0]+myOffset[0],atOffset[1]+myOffset[1]],
					my:options.my,
					at:options.at,
					within:within,
					elem:elem
				});
			}
		});

		if(options.using){

			//Addsfeedbackassecondargumenttousingcallback,ifpresent
			using=function(props){
				varleft=targetOffset.left-position.left,
					right=left+targetWidth-elemWidth,
					top=targetOffset.top-position.top,
					bottom=top+targetHeight-elemHeight,
					feedback={
						target:{
							element:target,
							left:targetOffset.left,
							top:targetOffset.top,
							width:targetWidth,
							height:targetHeight
						},
						element:{
							element:elem,
							left:position.left,
							top:position.top,
							width:elemWidth,
							height:elemHeight
						},
						horizontal:right<0?"left":left>0?"right":"center",
						vertical:bottom<0?"top":top>0?"bottom":"middle"
					};
				if(targetWidth<elemWidth&&abs(left+right)<targetWidth){
					feedback.horizontal="center";
				}
				if(targetHeight<elemHeight&&abs(top+bottom)<targetHeight){
					feedback.vertical="middle";
				}
				if(max(abs(left),abs(right))>max(abs(top),abs(bottom))){
					feedback.important="horizontal";
				}else{
					feedback.important="vertical";
				}
				options.using.call(this,props,feedback);
			};
		}

		elem.offset($.extend(position,{using:using}));
	});
};

$.ui.position={
	fit:{
		left:function(position,data){
			varwithin=data.within,
				withinOffset=within.isWindow?within.scrollLeft:within.offset.left,
				outerWidth=within.width,
				collisionPosLeft=position.left-data.collisionPosition.marginLeft,
				overLeft=withinOffset-collisionPosLeft,
				overRight=collisionPosLeft+data.collisionWidth-outerWidth-withinOffset,
				newOverRight;

			//Elementiswiderthanwithin
			if(data.collisionWidth>outerWidth){

				//Elementisinitiallyovertheleftsideofwithin
				if(overLeft>0&&overRight<=0){
					newOverRight=position.left+overLeft+data.collisionWidth-outerWidth-
						withinOffset;
					position.left+=overLeft-newOverRight;

				//Elementisinitiallyoverrightsideofwithin
				}elseif(overRight>0&&overLeft<=0){
					position.left=withinOffset;

				//Elementisinitiallyoverbothleftandrightsidesofwithin
				}else{
					if(overLeft>overRight){
						position.left=withinOffset+outerWidth-data.collisionWidth;
					}else{
						position.left=withinOffset;
					}
				}

			//Toofarleft->alignwithleftedge
			}elseif(overLeft>0){
				position.left+=overLeft;

			//Toofarright->alignwithrightedge
			}elseif(overRight>0){
				position.left-=overRight;

			//Adjustbasedonpositionandmargin
			}else{
				position.left=max(position.left-collisionPosLeft,position.left);
			}
		},
		top:function(position,data){
			varwithin=data.within,
				withinOffset=within.isWindow?within.scrollTop:within.offset.top,
				outerHeight=data.within.height,
				collisionPosTop=position.top-data.collisionPosition.marginTop,
				overTop=withinOffset-collisionPosTop,
				overBottom=collisionPosTop+data.collisionHeight-outerHeight-withinOffset,
				newOverBottom;

			//Elementistallerthanwithin
			if(data.collisionHeight>outerHeight){

				//Elementisinitiallyoverthetopofwithin
				if(overTop>0&&overBottom<=0){
					newOverBottom=position.top+overTop+data.collisionHeight-outerHeight-
						withinOffset;
					position.top+=overTop-newOverBottom;

				//Elementisinitiallyoverbottomofwithin
				}elseif(overBottom>0&&overTop<=0){
					position.top=withinOffset;

				//Elementisinitiallyoverbothtopandbottomofwithin
				}else{
					if(overTop>overBottom){
						position.top=withinOffset+outerHeight-data.collisionHeight;
					}else{
						position.top=withinOffset;
					}
				}

			//Toofarup->alignwithtop
			}elseif(overTop>0){
				position.top+=overTop;

			//Toofardown->alignwithbottomedge
			}elseif(overBottom>0){
				position.top-=overBottom;

			//Adjustbasedonpositionandmargin
			}else{
				position.top=max(position.top-collisionPosTop,position.top);
			}
		}
	},
	flip:{
		left:function(position,data){
			varwithin=data.within,
				withinOffset=within.offset.left+within.scrollLeft,
				outerWidth=within.width,
				offsetLeft=within.isWindow?within.scrollLeft:within.offset.left,
				collisionPosLeft=position.left-data.collisionPosition.marginLeft,
				overLeft=collisionPosLeft-offsetLeft,
				overRight=collisionPosLeft+data.collisionWidth-outerWidth-offsetLeft,
				myOffset=data.my[0]==="left"?
					-data.elemWidth:
					data.my[0]==="right"?
						data.elemWidth:
						0,
				atOffset=data.at[0]==="left"?
					data.targetWidth:
					data.at[0]==="right"?
						-data.targetWidth:
						0,
				offset=-2*data.offset[0],
				newOverRight,
				newOverLeft;

			if(overLeft<0){
				newOverRight=position.left+myOffset+atOffset+offset+data.collisionWidth-
					outerWidth-withinOffset;
				if(newOverRight<0||newOverRight<abs(overLeft)){
					position.left+=myOffset+atOffset+offset;
				}
			}elseif(overRight>0){
				newOverLeft=position.left-data.collisionPosition.marginLeft+myOffset+
					atOffset+offset-offsetLeft;
				if(newOverLeft>0||abs(newOverLeft)<overRight){
					position.left+=myOffset+atOffset+offset;
				}
			}
		},
		top:function(position,data){
			varwithin=data.within,
				withinOffset=within.offset.top+within.scrollTop,
				outerHeight=within.height,
				offsetTop=within.isWindow?within.scrollTop:within.offset.top,
				collisionPosTop=position.top-data.collisionPosition.marginTop,
				overTop=collisionPosTop-offsetTop,
				overBottom=collisionPosTop+data.collisionHeight-outerHeight-offsetTop,
				top=data.my[1]==="top",
				myOffset=top?
					-data.elemHeight:
					data.my[1]==="bottom"?
						data.elemHeight:
						0,
				atOffset=data.at[1]==="top"?
					data.targetHeight:
					data.at[1]==="bottom"?
						-data.targetHeight:
						0,
				offset=-2*data.offset[1],
				newOverTop,
				newOverBottom;
			if(overTop<0){
				newOverBottom=position.top+myOffset+atOffset+offset+data.collisionHeight-
					outerHeight-withinOffset;
				if(newOverBottom<0||newOverBottom<abs(overTop)){
					position.top+=myOffset+atOffset+offset;
				}
			}elseif(overBottom>0){
				newOverTop=position.top-data.collisionPosition.marginTop+myOffset+atOffset+
					offset-offsetTop;
				if(newOverTop>0||abs(newOverTop)<overBottom){
					position.top+=myOffset+atOffset+offset;
				}
			}
		}
	},
	flipfit:{
		left:function(){
			$.ui.position.flip.left.apply(this,arguments);
			$.ui.position.fit.left.apply(this,arguments);
		},
		top:function(){
			$.ui.position.flip.top.apply(this,arguments);
			$.ui.position.fit.top.apply(this,arguments);
		}
	}
};

})();

varposition=$.ui.position;


/*!
 *jQueryUI:data1.12.1
 *http://jqueryui.com
 *
 *CopyrightjQueryFoundationandothercontributors
 *ReleasedundertheMITlicense.
 *http://jquery.org/license
 */

//>>label::dataSelector
//>>group:Core
//>>description:Selectselementswhichhavedatastoredunderthespecifiedkey.
//>>docs:http://api.jqueryui.com/data-selector/


vardata=$.extend($.expr[":"],{
	data:$.expr.createPseudo?
		$.expr.createPseudo(function(dataName){
			returnfunction(elem){
				return!!$.data(elem,dataName);
			};
		}):

		//Support:jQuery<1.8
		function(elem,i,match){
			return!!$.data(elem,match[3]);
		}
});

/*!
 *jQueryUIDisableSelection1.12.1
 *http://jqueryui.com
 *
 *CopyrightjQueryFoundationandothercontributors
 *ReleasedundertheMITlicense.
 *http://jquery.org/license
 */

//>>label:disableSelection
//>>group:Core
//>>description:Disableselectionoftextcontentwithinthesetofmatchedelements.
//>>docs:http://api.jqueryui.com/disableSelection/

//Thisfileisdeprecated


vardisableSelection=$.fn.extend({
	disableSelection:(function(){
		vareventType="onselectstart"indocument.createElement("div")?
			"selectstart":
			"mousedown";

		returnfunction(){
			returnthis.on(eventType+".ui-disableSelection",function(event){
				event.preventDefault();
			});
		};
	})(),

	enableSelection:function(){
		returnthis.off(".ui-disableSelection");
	}
});


/*!
 *jQueryUIFocusable1.12.1
 *http://jqueryui.com
 *
 *CopyrightjQueryFoundationandothercontributors
 *ReleasedundertheMITlicense.
 *http://jquery.org/license
 */

//>>label::focusableSelector
//>>group:Core
//>>description:Selectselementswhichcanbefocused.
//>>docs:http://api.jqueryui.com/focusable-selector/



//Selectors
$.ui.focusable=function(element,hasTabindex){
	varmap,mapName,img,focusableIfVisible,fieldset,
		nodeName=element.nodeName.toLowerCase();

	if("area"===nodeName){
		map=element.parentNode;
		mapName=map.name;
		if(!element.href||!mapName||map.nodeName.toLowerCase()!=="map"){
			returnfalse;
		}
		img=$("img[usemap='#"+mapName+"']");
		returnimg.length>0&&img.is(":visible");
	}

	if(/^(input|select|textarea|button|object)$/.test(nodeName)){
		focusableIfVisible=!element.disabled;

		if(focusableIfVisible){

			//Formcontrolswithinadisabledfieldsetaredisabled.
			//However,controlswithinthefieldset'slegenddonotgetdisabled.
			//Sincecontrolsgenerallyaren'tplacedinsidelegends,weskip
			//thisportionofthecheck.
			fieldset=$(element).closest("fieldset")[0];
			if(fieldset){
				focusableIfVisible=!fieldset.disabled;
			}
		}
	}elseif("a"===nodeName){
		focusableIfVisible=element.href||hasTabindex;
	}else{
		focusableIfVisible=hasTabindex;
	}

	returnfocusableIfVisible&&$(element).is(":visible")&&visible($(element));
};

//Support:IE8only
//IE8doesn'tresolveinherittovisible/hiddenforcomputedvalues
functionvisible(element){
	varvisibility=element.css("visibility");
	while(visibility==="inherit"){
		element=element.parent();
		visibility=element.css("visibility");
	}
	returnvisibility!=="hidden";
}

$.extend($.expr[":"],{
	focusable:function(element){
		return$.ui.focusable(element,$.attr(element,"tabindex")!=null);
	}
});

varfocusable=$.ui.focusable;


/*!
 *jQueryUIKeycode1.12.1
 *http://jqueryui.com
 *
 *CopyrightjQueryFoundationandothercontributors
 *ReleasedundertheMITlicense.
 *http://jquery.org/license
 */

//>>label:Keycode
//>>group:Core
//>>description:Providekeycodesaskeynames
//>>docs:http://api.jqueryui.com/jQuery.ui.keyCode/


varkeycode=$.ui.keyCode={
	BACKSPACE:8,
	COMMA:188,
	DELETE:46,
	DOWN:40,
	END:35,
	ENTER:13,
	ESCAPE:27,
	HOME:36,
	LEFT:37,
	PAGE_DOWN:34,
	PAGE_UP:33,
	PERIOD:190,
	RIGHT:39,
	SPACE:32,
	TAB:9,
	UP:38
};


/*!
 *jQueryUIScrollParent1.12.1
 *http://jqueryui.com
 *
 *CopyrightjQueryFoundationandothercontributors
 *ReleasedundertheMITlicense.
 *http://jquery.org/license
 */

//>>label:scrollParent
//>>group:Core
//>>description:Gettheclosestancestorelementthatisscrollable.
//>>docs:http://api.jqueryui.com/scrollParent/



varscrollParent=$.fn.scrollParent=function(includeHidden){
	varposition=this.css("position"),
		excludeStaticParent=position==="absolute",
		overflowRegex=includeHidden?/(auto|scroll|hidden)/:/(auto|scroll)/,
		scrollParent=this.parents().filter(function(){
			varparent=$(this);
			if(excludeStaticParent&&parent.css("position")==="static"){
				returnfalse;
			}
			returnoverflowRegex.test(parent.css("overflow")+parent.css("overflow-y")+
				parent.css("overflow-x"));
		}).eq(0);

	returnposition==="fixed"||!scrollParent.length?
		$(this[0].ownerDocument||document):
		scrollParent;
};


/*!
 *jQueryUIUniqueID1.12.1
 *http://jqueryui.com
 *
 *CopyrightjQueryFoundationandothercontributors
 *ReleasedundertheMITlicense.
 *http://jquery.org/license
 */

//>>label:uniqueId
//>>group:Core
//>>description:FunctionstogenerateandremoveuniqueId's
//>>docs:http://api.jqueryui.com/uniqueId/



varuniqueId=$.fn.extend({
	uniqueId:(function(){
		varuuid=0;

		returnfunction(){
			returnthis.each(function(){
				if(!this.id){
					this.id="ui-id-"+(++uuid);
				}
			});
		};
	})(),

	removeUniqueId:function(){
		returnthis.each(function(){
			if(/^ui-id-\d+$/.test(this.id)){
				$(this).removeAttr("id");
			}
		});
	}
});




//Thisfileisdeprecated
varie=$.ui.ie=!!/msie[\w.]+/.exec(navigator.userAgent.toLowerCase());

/*!
 *jQueryUIMouse1.12.1
 *http://jqueryui.com
 *
 *CopyrightjQueryFoundationandothercontributors
 *ReleasedundertheMITlicense.
 *http://jquery.org/license
 */

//>>label:Mouse
//>>group:Widgets
//>>description:Abstractsmouse-basedinteractionstoassistincreatingcertainwidgets.
//>>docs:http://api.jqueryui.com/mouse/



varmouseHandled=false;
$(document).on("mouseup",function(){
	mouseHandled=false;
});

varwidgetsMouse=$.widget("ui.mouse",{
	version:"1.12.1",
	options:{
		cancel:"input,textarea,button,select,option",
		distance:1,
		delay:0
	},
	_mouseInit:function(){
		varthat=this;

		this.element
			.on("mousedown."+this.widgetName,function(event){
				returnthat._mouseDown(event);
			})
			.on("click."+this.widgetName,function(event){
				if(true===$.data(event.target,that.widgetName+".preventClickEvent")){
					$.removeData(event.target,that.widgetName+".preventClickEvent");
					event.stopImmediatePropagation();
					returnfalse;
				}
			});

		this.started=false;
	},

	//TODO:makesuredestroyingoneinstanceofmousedoesn'tmesswith
	//otherinstancesofmouse
	_mouseDestroy:function(){
		this.element.off("."+this.widgetName);
		if(this._mouseMoveDelegate){
			this.document
				.off("mousemove."+this.widgetName,this._mouseMoveDelegate)
				.off("mouseup."+this.widgetName,this._mouseUpDelegate);
		}
	},

	_mouseDown:function(event){

		//don'tletmorethanonewidgethandlemouseStart
		if(mouseHandled){
			return;
		}

		this._mouseMoved=false;

		//Wemayhavemissedmouseup(outofwindow)
		(this._mouseStarted&&this._mouseUp(event));

		this._mouseDownEvent=event;

		varthat=this,
			btnIsLeft=(event.which===1),

			//event.target.nodeNameworksaroundabuginIE8with
			//disabledinputs(#7620)
			elIsCancel=(typeofthis.options.cancel==="string"&&event.target.nodeName?
				$(event.target).closest(this.options.cancel).length:false);
		if(!btnIsLeft||elIsCancel||!this._mouseCapture(event)){
			returntrue;
		}

		this.mouseDelayMet=!this.options.delay;
		if(!this.mouseDelayMet){
			this._mouseDelayTimer=setTimeout(function(){
				that.mouseDelayMet=true;
			},this.options.delay);
		}

		if(this._mouseDistanceMet(event)&&this._mouseDelayMet(event)){
			this._mouseStarted=(this._mouseStart(event)!==false);
			if(!this._mouseStarted){
				event.preventDefault();
				returntrue;
			}
		}

		//Clickeventmayneverhavefired(Gecko&Opera)
		if(true===$.data(event.target,this.widgetName+".preventClickEvent")){
			$.removeData(event.target,this.widgetName+".preventClickEvent");
		}

		//Thesedelegatesarerequiredtokeepcontext
		this._mouseMoveDelegate=function(event){
			returnthat._mouseMove(event);
		};
		this._mouseUpDelegate=function(event){
			returnthat._mouseUp(event);
		};

		this.document
			.on("mousemove."+this.widgetName,this._mouseMoveDelegate)
			.on("mouseup."+this.widgetName,this._mouseUpDelegate);

		event.preventDefault();

		mouseHandled=true;
		returntrue;
	},

	_mouseMove:function(event){

		//Onlycheckformouseupsoutsidethedocumentifyou'vemovedinsidethedocument
		//atleastonce.ThispreventsthefiringofmouseupinthecaseofIE<9,whichwill
		//fireamousemoveeventifcontentisplacedunderthecursor.See#7778
		//Support:IE<9
		if(this._mouseMoved){

			//IEmouseupcheck-mouseuphappenedwhenmousewasoutofwindow
			if($.ui.ie&&(!document.documentMode||document.documentMode<9)&&
					!event.button){
				returnthis._mouseUp(event);

			//Iframemouseupcheck-mouseupoccurredinanotherdocument
			}elseif(!event.which){

				//Support:Safari<=8-9
				//Safarisetswhichto0ifyoupressanyofthefollowingkeys
				//duringadrag(#14461)
				if(event.originalEvent.altKey||event.originalEvent.ctrlKey||
						event.originalEvent.metaKey||event.originalEvent.shiftKey){
					this.ignoreMissingWhich=true;
				}elseif(!this.ignoreMissingWhich){
					returnthis._mouseUp(event);
				}
			}
		}

		if(event.which||event.button){
			this._mouseMoved=true;
		}

		if(this._mouseStarted){
			this._mouseDrag(event);
			returnevent.preventDefault();
		}

		if(this._mouseDistanceMet(event)&&this._mouseDelayMet(event)){
			this._mouseStarted=
				(this._mouseStart(this._mouseDownEvent,event)!==false);
			(this._mouseStarted?this._mouseDrag(event):this._mouseUp(event));
		}

		return!this._mouseStarted;
	},

	_mouseUp:function(event){
		this.document
			.off("mousemove."+this.widgetName,this._mouseMoveDelegate)
			.off("mouseup."+this.widgetName,this._mouseUpDelegate);

		if(this._mouseStarted){
			this._mouseStarted=false;

			if(event.target===this._mouseDownEvent.target){
				$.data(event.target,this.widgetName+".preventClickEvent",true);
			}

			this._mouseStop(event);
		}

		if(this._mouseDelayTimer){
			clearTimeout(this._mouseDelayTimer);
			deletethis._mouseDelayTimer;
		}

		this.ignoreMissingWhich=false;
		mouseHandled=false;
		event.preventDefault();
	},

	_mouseDistanceMet:function(event){
		return(Math.max(
				Math.abs(this._mouseDownEvent.pageX-event.pageX),
				Math.abs(this._mouseDownEvent.pageY-event.pageY)
			)>=this.options.distance
		);
	},

	_mouseDelayMet:function(/*event*/){
		returnthis.mouseDelayMet;
	},

	//Theseareplaceholdermethods,tobeoverriddenbyextendingplugin
	_mouseStart:function(/*event*/){},
	_mouseDrag:function(/*event*/){},
	_mouseStop:function(/*event*/){},
	_mouseCapture:function(/*event*/){returntrue;}
});




//$.ui.pluginisdeprecated.Use$.widget()extensionsinstead.
varplugin=$.ui.plugin={
	add:function(module,option,set){
		vari,
			proto=$.ui[module].prototype;
		for(iinset){
			proto.plugins[i]=proto.plugins[i]||[];
			proto.plugins[i].push([option,set[i]]);
		}
	},
	call:function(instance,name,args,allowDisconnected){
		vari,
			set=instance.plugins[name];

		if(!set){
			return;
		}

		if(!allowDisconnected&&(!instance.element[0].parentNode||
				instance.element[0].parentNode.nodeType===11)){
			return;
		}

		for(i=0;i<set.length;i++){
			if(instance.options[set[i][0]]){
				set[i][1].apply(instance.element,args);
			}
		}
	}
};



varsafeActiveElement=$.ui.safeActiveElement=function(document){
	varactiveElement;

	//Support:IE9only
	//IE9throwsan"Unspecifiederror"accessingdocument.activeElementfroman<iframe>
	try{
		activeElement=document.activeElement;
	}catch(error){
		activeElement=document.body;
	}

	//Support:IE9-11only
	//IEmayreturnnullinsteadofanelement
	//Interestingly,thisonlyseemstooccurwhenNOTinaniframe
	if(!activeElement){
		activeElement=document.body;
	}

	//Support:IE11only
	//IE11returnsaseeminglyemptyobjectinsomecaseswhenaccessing
	//document.activeElementfroman<iframe>
	if(!activeElement.nodeName){
		activeElement=document.body;
	}

	returnactiveElement;
};



varsafeBlur=$.ui.safeBlur=function(element){

	//Support:IE9-10only
	//Ifthe<body>isblurred,IEwillswitchwindows,see#9420
	if(element&&element.nodeName.toLowerCase()!=="body"){
		$(element).trigger("blur");
	}
};


/*!
 *jQueryUIDraggable1.12.1
 *http://jqueryui.com
 *
 *CopyrightjQueryFoundationandothercontributors
 *ReleasedundertheMITlicense.
 *http://jquery.org/license
 */

//>>label:Draggable
//>>group:Interactions
//>>description:Enablesdraggingfunctionalityforanyelement.
//>>docs:http://api.jqueryui.com/draggable/
//>>demos:http://jqueryui.com/draggable/
//>>css.structure:../../themes/base/draggable.css



$.widget("ui.draggable",$.ui.mouse,{
	version:"1.12.1",
	widgetEventPrefix:"drag",
	options:{
		addClasses:true,
		appendTo:"parent",
		axis:false,
		connectToSortable:false,
		containment:false,
		cursor:"auto",
		cursorAt:false,
		grid:false,
		handle:false,
		helper:"original",
		iframeFix:false,
		opacity:false,
		refreshPositions:false,
		revert:false,
		revertDuration:500,
		scope:"default",
		scroll:true,
		scrollSensitivity:20,
		scrollSpeed:20,
		snap:false,
		snapMode:"both",
		snapTolerance:20,
		stack:false,
		zIndex:false,

		//Callbacks
		drag:null,
		start:null,
		stop:null
	},
	_create:function(){

		if(this.options.helper==="original"){
			this._setPositionRelative();
		}
		if(this.options.addClasses){
			this._addClass("ui-draggable");
		}
		this._setHandleClassName();

		this._mouseInit();
	},

	_setOption:function(key,value){
		this._super(key,value);
		if(key==="handle"){
			this._removeHandleClassName();
			this._setHandleClassName();
		}
	},

	_destroy:function(){
		if((this.helper||this.element).is(".ui-draggable-dragging")){
			this.destroyOnClear=true;
			return;
		}
		this._removeHandleClassName();
		this._mouseDestroy();
	},

	_mouseCapture:function(event){
		varo=this.options;

		//Amongothers,preventadragonaresizable-handle
		if(this.helper||o.disabled||
				$(event.target).closest(".ui-resizable-handle").length>0){
			returnfalse;
		}

		//Quitifwe'renotonavalidhandle
		this.handle=this._getHandle(event);
		if(!this.handle){
			returnfalse;
		}

		this._blurActiveElement(event);

		this._blockFrames(o.iframeFix===true?"iframe":o.iframeFix);

		returntrue;

	},

	_blockFrames:function(selector){
		this.iframeBlocks=this.document.find(selector).map(function(){
			variframe=$(this);

			return$("<div>")
				.css("position","absolute")
				.appendTo(iframe.parent())
				.outerWidth(iframe.outerWidth())
				.outerHeight(iframe.outerHeight())
				.offset(iframe.offset())[0];
		});
	},

	_unblockFrames:function(){
		if(this.iframeBlocks){
			this.iframeBlocks.remove();
			deletethis.iframeBlocks;
		}
	},

	_blurActiveElement:function(event){
		varactiveElement=$.ui.safeActiveElement(this.document[0]),
			target=$(event.target);

		//Don'tbluriftheeventoccurredonanelementthatiswithin
		//thecurrentlyfocusedelement
		//See#10527,#12472
		if(target.closest(activeElement).length){
			return;
		}

		//Bluranyelementthatcurrentlyhasfocus,see#4261
		$.ui.safeBlur(activeElement);
	},

	_mouseStart:function(event){

		varo=this.options;

		//Createandappendthevisiblehelper
		this.helper=this._createHelper(event);

		this._addClass(this.helper,"ui-draggable-dragging");

		//Cachethehelpersize
		this._cacheHelperProportions();

		//Ifddmanagerisusedfordroppables,settheglobaldraggable
		if($.ui.ddmanager){
			$.ui.ddmanager.current=this;
		}

		/*
		*-Positiongeneration-
		*Thisblockgenerateseverythingpositionrelated-it'sthecoreofdraggables.
		*/

		//Cachethemarginsoftheoriginalelement
		this._cacheMargins();

		//Storethehelper'scssposition
		this.cssPosition=this.helper.css("position");
		this.scrollParent=this.helper.scrollParent(true);
		this.offsetParent=this.helper.offsetParent();
		this.hasFixedAncestor=this.helper.parents().filter(function(){
				return$(this).css("position")==="fixed";
			}).length>0;

		//Theelement'sabsolutepositiononthepageminusmargins
		this.positionAbs=this.element.offset();
		this._refreshOffsets(event);

		//Generatetheoriginalposition
		this.originalPosition=this.position=this._generatePosition(event,false);
		this.originalPageX=event.pageX;
		this.originalPageY=event.pageY;

		//Adjustthemouseoffsetrelativetothehelperif"cursorAt"issupplied
		(o.cursorAt&&this._adjustOffsetFromHelper(o.cursorAt));

		//Setacontainmentifgivenintheoptions
		this._setContainment();

		//Triggerevent+callbacks
		if(this._trigger("start",event)===false){
			this._clear();
			returnfalse;
		}

		//Recachethehelpersize
		this._cacheHelperProportions();

		//Preparethedroppableoffsets
		if($.ui.ddmanager&&!o.dropBehaviour){
			$.ui.ddmanager.prepareOffsets(this,event);
		}

		//Executethedragonce-thiscausesthehelpernottobevisiblebeforegettingits
		//correctposition
		this._mouseDrag(event,true);

		//Iftheddmanagerisusedfordroppables,informthemanagerthatdragginghasstarted
		//(see#5003)
		if($.ui.ddmanager){
			$.ui.ddmanager.dragStart(this,event);
		}

		returntrue;
	},

	_refreshOffsets:function(event){
		this.offset={
			top:this.positionAbs.top-this.margins.top,
			left:this.positionAbs.left-this.margins.left,
			scroll:false,
			parent:this._getParentOffset(),
			relative:this._getRelativeOffset()
		};

		this.offset.click={
			left:event.pageX-this.offset.left,
			top:event.pageY-this.offset.top
		};
	},

	_mouseDrag:function(event,noPropagation){

		//resetanynecessarycachedproperties(see#5009)
		if(this.hasFixedAncestor){
			this.offset.parent=this._getParentOffset();
		}

		//Computethehelpersposition
		this.position=this._generatePosition(event,true);
		this.positionAbs=this._convertPositionTo("absolute");

		//Callpluginsandcallbacksandusetheresultingpositionifsomethingisreturned
		if(!noPropagation){
			varui=this._uiHash();
			if(this._trigger("drag",event,ui)===false){
				this._mouseUp(new$.Event("mouseup",event));
				returnfalse;
			}
			this.position=ui.position;
		}

		this.helper[0].style.left=this.position.left+"px";
		this.helper[0].style.top=this.position.top+"px";

		if($.ui.ddmanager){
			$.ui.ddmanager.drag(this,event);
		}

		returnfalse;
	},

	_mouseStop:function(event){

		//Ifweareusingdroppables,informthemanageraboutthedrop
		varthat=this,
			dropped=false;
		if($.ui.ddmanager&&!this.options.dropBehaviour){
			dropped=$.ui.ddmanager.drop(this,event);
		}

		//ifadropcomesfromoutside(asortable)
		if(this.dropped){
			dropped=this.dropped;
			this.dropped=false;
		}

		if((this.options.revert==="invalid"&&!dropped)||
				(this.options.revert==="valid"&&dropped)||
				this.options.revert===true||($.isFunction(this.options.revert)&&
				this.options.revert.call(this.element,dropped))
		){
			$(this.helper).animate(
				this.originalPosition,
				parseInt(this.options.revertDuration,10),
				function(){
					if(that._trigger("stop",event)!==false){
						that._clear();
					}
				}
			);
		}else{
			if(this._trigger("stop",event)!==false){
				this._clear();
			}
		}

		returnfalse;
	},

	_mouseUp:function(event){
		this._unblockFrames();

		//Iftheddmanagerisusedfordroppables,informthemanagerthatdragginghasstopped
		//(see#5003)
		if($.ui.ddmanager){
			$.ui.ddmanager.dragStop(this,event);
		}

		//Onlyneedtofocusiftheeventoccurredonthedraggableitself,see#10527
		if(this.handleElement.is(event.target)){

			//Theinteractionisover;whetherornottheclickresultedinadrag,
			//focustheelement
			this.element.trigger("focus");
		}

		return$.ui.mouse.prototype._mouseUp.call(this,event);
	},

	cancel:function(){

		if(this.helper.is(".ui-draggable-dragging")){
			this._mouseUp(new$.Event("mouseup",{target:this.element[0]}));
		}else{
			this._clear();
		}

		returnthis;

	},

	_getHandle:function(event){
		returnthis.options.handle?
			!!$(event.target).closest(this.element.find(this.options.handle)).length:
			true;
	},

	_setHandleClassName:function(){
		this.handleElement=this.options.handle?
			this.element.find(this.options.handle):this.element;
		this._addClass(this.handleElement,"ui-draggable-handle");
	},

	_removeHandleClassName:function(){
		this._removeClass(this.handleElement,"ui-draggable-handle");
	},

	_createHelper:function(event){

		varo=this.options,
			helperIsFunction=$.isFunction(o.helper),
			helper=helperIsFunction?
				$(o.helper.apply(this.element[0],[event])):
				(o.helper==="clone"?
					this.element.clone().removeAttr("id"):
					this.element);

		if(!helper.parents("body").length){
			helper.appendTo((o.appendTo==="parent"?
				this.element[0].parentNode:
				o.appendTo));
		}

		//Http://bugs.jqueryui.com/ticket/9446
		//ahelperfunctioncanreturntheoriginalelement
		//whichwouldn'thavebeensettorelativein_create
		if(helperIsFunction&&helper[0]===this.element[0]){
			this._setPositionRelative();
		}

		if(helper[0]!==this.element[0]&&
				!(/(fixed|absolute)/).test(helper.css("position"))){
			helper.css("position","absolute");
		}

		returnhelper;

	},

	_setPositionRelative:function(){
		if(!(/^(?:r|a|f)/).test(this.element.css("position"))){
			this.element[0].style.position="relative";
		}
	},

	_adjustOffsetFromHelper:function(obj){
		if(typeofobj==="string"){
			obj=obj.split("");
		}
		if($.isArray(obj)){
			obj={left:+obj[0],top:+obj[1]||0};
		}
		if("left"inobj){
			this.offset.click.left=obj.left+this.margins.left;
		}
		if("right"inobj){
			this.offset.click.left=this.helperProportions.width-obj.right+this.margins.left;
		}
		if("top"inobj){
			this.offset.click.top=obj.top+this.margins.top;
		}
		if("bottom"inobj){
			this.offset.click.top=this.helperProportions.height-obj.bottom+this.margins.top;
		}
	},

	_isRootNode:function(element){
		return(/(html|body)/i).test(element.tagName)||element===this.document[0];
	},

	_getParentOffset:function(){

		//GettheoffsetParentandcacheitsposition
		varpo=this.offsetParent.offset(),
			document=this.document[0];

		//Thisisaspecialcasewhereweneedtomodifyaoffsetcalculatedonstart,sincethe
		//followinghappened:
		//1.Thepositionofthehelperisabsolute,soit'spositioniscalculatedbasedonthe
		//nextpositionedparent
		//2.Theactualoffsetparentisachildofthescrollparent,andthescrollparentisn't
		//thedocument,whichmeansthatthescrollisincludedintheinitialcalculationofthe
		//offsetoftheparent,andneverrecalculatedupondrag
		if(this.cssPosition==="absolute"&&this.scrollParent[0]!==document&&
				$.contains(this.scrollParent[0],this.offsetParent[0])){
			po.left+=this.scrollParent.scrollLeft();
			po.top+=this.scrollParent.scrollTop();
		}

		if(this._isRootNode(this.offsetParent[0])){
			po={top:0,left:0};
		}

		return{
			top:po.top+(parseInt(this.offsetParent.css("borderTopWidth"),10)||0),
			left:po.left+(parseInt(this.offsetParent.css("borderLeftWidth"),10)||0)
		};

	},

	_getRelativeOffset:function(){
		if(this.cssPosition!=="relative"){
			return{top:0,left:0};
		}

		varp=this.element.position(),
			scrollIsRootNode=this._isRootNode(this.scrollParent[0]);

		return{
			top:p.top-(parseInt(this.helper.css("top"),10)||0)+
				(!scrollIsRootNode?this.scrollParent.scrollTop():0),
			left:p.left-(parseInt(this.helper.css("left"),10)||0)+
				(!scrollIsRootNode?this.scrollParent.scrollLeft():0)
		};

	},

	_cacheMargins:function(){
		this.margins={
			left:(parseInt(this.element.css("marginLeft"),10)||0),
			top:(parseInt(this.element.css("marginTop"),10)||0),
			right:(parseInt(this.element.css("marginRight"),10)||0),
			bottom:(parseInt(this.element.css("marginBottom"),10)||0)
		};
	},

	_cacheHelperProportions:function(){
		this.helperProportions={
			width:this.helper.outerWidth(),
			height:this.helper.outerHeight()
		};
	},

	_setContainment:function(){

		varisUserScrollable,c,ce,
			o=this.options,
			document=this.document[0];

		this.relativeContainer=null;

		if(!o.containment){
			this.containment=null;
			return;
		}

		if(o.containment==="window"){
			this.containment=[
				$(window).scrollLeft()-this.offset.relative.left-this.offset.parent.left,
				$(window).scrollTop()-this.offset.relative.top-this.offset.parent.top,
				$(window).scrollLeft()+$(window).width()-
					this.helperProportions.width-this.margins.left,
				$(window).scrollTop()+
					($(window).height()||document.body.parentNode.scrollHeight)-
					this.helperProportions.height-this.margins.top
			];
			return;
		}

		if(o.containment==="document"){
			this.containment=[
				0,
				0,
				$(document).width()-this.helperProportions.width-this.margins.left,
				($(document).height()||document.body.parentNode.scrollHeight)-
					this.helperProportions.height-this.margins.top
			];
			return;
		}

		if(o.containment.constructor===Array){
			this.containment=o.containment;
			return;
		}

		if(o.containment==="parent"){
			o.containment=this.helper[0].parentNode;
		}

		c=$(o.containment);
		ce=c[0];

		if(!ce){
			return;
		}

		isUserScrollable=/(scroll|auto)/.test(c.css("overflow"));

		this.containment=[
			(parseInt(c.css("borderLeftWidth"),10)||0)+
				(parseInt(c.css("paddingLeft"),10)||0),
			(parseInt(c.css("borderTopWidth"),10)||0)+
				(parseInt(c.css("paddingTop"),10)||0),
			(isUserScrollable?Math.max(ce.scrollWidth,ce.offsetWidth):ce.offsetWidth)-
				(parseInt(c.css("borderRightWidth"),10)||0)-
				(parseInt(c.css("paddingRight"),10)||0)-
				this.helperProportions.width-
				this.margins.left-
				this.margins.right,
			(isUserScrollable?Math.max(ce.scrollHeight,ce.offsetHeight):ce.offsetHeight)-
				(parseInt(c.css("borderBottomWidth"),10)||0)-
				(parseInt(c.css("paddingBottom"),10)||0)-
				this.helperProportions.height-
				this.margins.top-
				this.margins.bottom
		];
		this.relativeContainer=c;
	},

	_convertPositionTo:function(d,pos){

		if(!pos){
			pos=this.position;
		}

		varmod=d==="absolute"?1:-1,
			scrollIsRootNode=this._isRootNode(this.scrollParent[0]);

		return{
			top:(

				//Theabsolutemouseposition
				pos.top	+

				//Onlyforrelativepositionednodes:Relativeoffsetfromelementtooffsetparent
				this.offset.relative.top*mod+

				//TheoffsetParent'soffsetwithoutborders(offset+border)
				this.offset.parent.top*mod-
				((this.cssPosition==="fixed"?
					-this.offset.scroll.top:
					(scrollIsRootNode?0:this.offset.scroll.top))*mod)
			),
			left:(

				//Theabsolutemouseposition
				pos.left+

				//Onlyforrelativepositionednodes:Relativeoffsetfromelementtooffsetparent
				this.offset.relative.left*mod+

				//TheoffsetParent'soffsetwithoutborders(offset+border)
				this.offset.parent.left*mod	-
				((this.cssPosition==="fixed"?
					-this.offset.scroll.left:
					(scrollIsRootNode?0:this.offset.scroll.left))*mod)
			)
		};

	},

	_generatePosition:function(event,constrainPosition){

		varcontainment,co,top,left,
			o=this.options,
			scrollIsRootNode=this._isRootNode(this.scrollParent[0]),
			pageX=event.pageX,
			pageY=event.pageY;

		//Cachethescroll
		if(!scrollIsRootNode||!this.offset.scroll){
			this.offset.scroll={
				top:this.scrollParent.scrollTop(),
				left:this.scrollParent.scrollLeft()
			};
		}

		/*
		*-Positionconstraining-
		*Constrainthepositiontoamixofgrid,containment.
		*/

		//Ifwearenotdraggingyet,wewon'tcheckforoptions
		if(constrainPosition){
			if(this.containment){
				if(this.relativeContainer){
					co=this.relativeContainer.offset();
					containment=[
						this.containment[0]+co.left,
						this.containment[1]+co.top,
						this.containment[2]+co.left,
						this.containment[3]+co.top
					];
				}else{
					containment=this.containment;
				}

				if(event.pageX-this.offset.click.left<containment[0]){
					pageX=containment[0]+this.offset.click.left;
				}
				if(event.pageY-this.offset.click.top<containment[1]){
					pageY=containment[1]+this.offset.click.top;
				}
				if(event.pageX-this.offset.click.left>containment[2]){
					pageX=containment[2]+this.offset.click.left;
				}
				if(event.pageY-this.offset.click.top>containment[3]){
					pageY=containment[3]+this.offset.click.top;
				}
			}

			if(o.grid){

				//Checkforgridelementssetto0topreventdivideby0errorcausinginvalid
				//argumenterrorsinIE(seeticket#6950)
				top=o.grid[1]?this.originalPageY+Math.round((pageY-
					this.originalPageY)/o.grid[1])*o.grid[1]:this.originalPageY;
				pageY=containment?((top-this.offset.click.top>=containment[1]||
					top-this.offset.click.top>containment[3])?
						top:
						((top-this.offset.click.top>=containment[1])?
							top-o.grid[1]:top+o.grid[1])):top;

				left=o.grid[0]?this.originalPageX+
					Math.round((pageX-this.originalPageX)/o.grid[0])*o.grid[0]:
					this.originalPageX;
				pageX=containment?((left-this.offset.click.left>=containment[0]||
					left-this.offset.click.left>containment[2])?
						left:
						((left-this.offset.click.left>=containment[0])?
							left-o.grid[0]:left+o.grid[0])):left;
			}

			if(o.axis==="y"){
				pageX=this.originalPageX;
			}

			if(o.axis==="x"){
				pageY=this.originalPageY;
			}
		}

		return{
			top:(

				//Theabsolutemouseposition
				pageY-

				//Clickoffset(relativetotheelement)
				this.offset.click.top-

				//Onlyforrelativepositionednodes:Relativeoffsetfromelementtooffsetparent
				this.offset.relative.top-

				//TheoffsetParent'soffsetwithoutborders(offset+border)
				this.offset.parent.top+
				(this.cssPosition==="fixed"?
					-this.offset.scroll.top:
					(scrollIsRootNode?0:this.offset.scroll.top))
			),
			left:(

				//Theabsolutemouseposition
				pageX-

				//Clickoffset(relativetotheelement)
				this.offset.click.left-

				//Onlyforrelativepositionednodes:Relativeoffsetfromelementtooffsetparent
				this.offset.relative.left-

				//TheoffsetParent'soffsetwithoutborders(offset+border)
				this.offset.parent.left+
				(this.cssPosition==="fixed"?
					-this.offset.scroll.left:
					(scrollIsRootNode?0:this.offset.scroll.left))
			)
		};

	},

	_clear:function(){
		this._removeClass(this.helper,"ui-draggable-dragging");
		if(this.helper[0]!==this.element[0]&&!this.cancelHelperRemoval){
			this.helper.remove();
		}
		this.helper=null;
		this.cancelHelperRemoval=false;
		if(this.destroyOnClear){
			this.destroy();
		}
	},

	//Fromnowonbulkstuff-mainlyhelpers

	_trigger:function(type,event,ui){
		ui=ui||this._uiHash();
		$.ui.plugin.call(this,type,[event,ui,this],true);

		//Absolutepositionandoffset(see#6884)havetoberecalculatedafterplugins
		if(/^(drag|start|stop)/.test(type)){
			this.positionAbs=this._convertPositionTo("absolute");
			ui.offset=this.positionAbs;
		}
		return$.Widget.prototype._trigger.call(this,type,event,ui);
	},

	plugins:{},

	_uiHash:function(){
		return{
			helper:this.helper,
			position:this.position,
			originalPosition:this.originalPosition,
			offset:this.positionAbs
		};
	}

});

$.ui.plugin.add("draggable","connectToSortable",{
	start:function(event,ui,draggable){
		varuiSortable=$.extend({},ui,{
			item:draggable.element
		});

		draggable.sortables=[];
		$(draggable.options.connectToSortable).each(function(){
			varsortable=$(this).sortable("instance");

			if(sortable&&!sortable.options.disabled){
				draggable.sortables.push(sortable);

				//RefreshPositionsiscalledatdragstarttorefreshthecontainerCache
				//whichisusedindrag.Thisensuresit'sinitializedandsynchronized
				//withanychangesthatmighthavehappenedonthepagesinceinitialization.
				sortable.refreshPositions();
				sortable._trigger("activate",event,uiSortable);
			}
		});
	},
	stop:function(event,ui,draggable){
		varuiSortable=$.extend({},ui,{
			item:draggable.element
		});

		draggable.cancelHelperRemoval=false;

		$.each(draggable.sortables,function(){
			varsortable=this;

			if(sortable.isOver){
				sortable.isOver=0;

				//Allowthissortabletohandleremovingthehelper
				draggable.cancelHelperRemoval=true;
				sortable.cancelHelperRemoval=false;

				//Use_storedCSSTorestorepropertiesinthesortable,
				//asthisalsohandlesrevert(#9675)sincethedraggable
				//mayhavemodifiedtheminunexpectedways(#8809)
				sortable._storedCSS={
					position:sortable.placeholder.css("position"),
					top:sortable.placeholder.css("top"),
					left:sortable.placeholder.css("left")
				};

				sortable._mouseStop(event);

				//Oncedraghasended,thesortableshouldreturntousing
				//itsoriginalhelper,notthesharedhelperfromdraggable
				sortable.options.helper=sortable.options._helper;
			}else{

				//PreventthisSortablefromremovingthehelper.
				//However,don'tsetthedraggabletoremovethehelper
				//eitherasanotherconnectedSortablemayyethandletheremoval.
				sortable.cancelHelperRemoval=true;

				sortable._trigger("deactivate",event,uiSortable);
			}
		});
	},
	drag:function(event,ui,draggable){
		$.each(draggable.sortables,function(){
			varinnermostIntersecting=false,
				sortable=this;

			//Copyovervariablesthatsortable's_intersectsWithuses
			sortable.positionAbs=draggable.positionAbs;
			sortable.helperProportions=draggable.helperProportions;
			sortable.offset.click=draggable.offset.click;

			if(sortable._intersectsWith(sortable.containerCache)){
				innermostIntersecting=true;

				$.each(draggable.sortables,function(){

					//Copyovervariablesthatsortable's_intersectsWithuses
					this.positionAbs=draggable.positionAbs;
					this.helperProportions=draggable.helperProportions;
					this.offset.click=draggable.offset.click;

					if(this!==sortable&&
							this._intersectsWith(this.containerCache)&&
							$.contains(sortable.element[0],this.element[0])){
						innermostIntersecting=false;
					}

					returninnermostIntersecting;
				});
			}

			if(innermostIntersecting){

				//Ifitintersects,weusealittleisOvervariableandsetitonce,
				//sothatthemove-instuffgetsfiredonlyonce.
				if(!sortable.isOver){
					sortable.isOver=1;

					//Storedraggable'sparentincaseweneedtoreappendtoitlater.
					draggable._parent=ui.helper.parent();

					sortable.currentItem=ui.helper
						.appendTo(sortable.element)
						.data("ui-sortable-item",true);

					//Storehelperoptiontolaterrestoreit
					sortable.options._helper=sortable.options.helper;

					sortable.options.helper=function(){
						returnui.helper[0];
					};

					//Firethestarteventsofthesortablewithourpassedbrowserevent,
					//andourownhelper(soitdoesn'tcreateanewone)
					event.target=sortable.currentItem[0];
					sortable._mouseCapture(event,true);
					sortable._mouseStart(event,true,true);

					//Becausethebrowsereventiswayoffthenewappendedportlet,
					//modifynecessaryvariablestoreflectthechanges
					sortable.offset.click.top=draggable.offset.click.top;
					sortable.offset.click.left=draggable.offset.click.left;
					sortable.offset.parent.left-=draggable.offset.parent.left-
						sortable.offset.parent.left;
					sortable.offset.parent.top-=draggable.offset.parent.top-
						sortable.offset.parent.top;

					draggable._trigger("toSortable",event);

					//Informdraggablethatthehelperisinavaliddropzone,
					//usedsolelyintherevertoptiontohandle"valid/invalid".
					draggable.dropped=sortable.element;

					//NeedtorefreshPositionsofallsortablesinthecasethat
					//addingtoonesortablechangesthelocationoftheothersortables(#9675)
					$.each(draggable.sortables,function(){
						this.refreshPositions();
					});

					//Hacksoreceive/updatecallbackswork(mostly)
					draggable.currentItem=draggable.element;
					sortable.fromOutside=draggable;
				}

				if(sortable.currentItem){
					sortable._mouseDrag(event);

					//Copythesortable'spositionbecausethedraggable'scanpotentiallyreflect
					//arelativeposition,whilesortableisalwaysabsolute,whichthedragged
					//elementhasnowbecome.(#8809)
					ui.position=sortable.position;
				}
			}else{

				//Ifitdoesn'tintersectwiththesortable,anditintersectedbefore,
				//wefakethedragstopofthesortable,butmakesureitdoesn'tremove
				//thehelperbyusingcancelHelperRemoval.
				if(sortable.isOver){

					sortable.isOver=0;
					sortable.cancelHelperRemoval=true;

					//Callingsortable'smouseStopwouldtriggerarevert,
					//sorevertmustbetemporarilyfalseuntilaftermouseStopiscalled.
					sortable.options._revert=sortable.options.revert;
					sortable.options.revert=false;

					sortable._trigger("out",event,sortable._uiHash(sortable));
					sortable._mouseStop(event,true);

					//Restoresortablebehaviorsthatweremodfied
					//whenthedraggableenteredthesortablearea(#9481)
					sortable.options.revert=sortable.options._revert;
					sortable.options.helper=sortable.options._helper;

					if(sortable.placeholder){
						sortable.placeholder.remove();
					}

					//Restoreandrecalculatethedraggable'soffsetconsideringthesortable
					//mayhavemodifiedtheminunexpectedways.(#8809,#10669)
					ui.helper.appendTo(draggable._parent);
					draggable._refreshOffsets(event);
					ui.position=draggable._generatePosition(event,true);

					draggable._trigger("fromSortable",event);

					//Informdraggablethatthehelperisnolongerinavaliddropzone
					draggable.dropped=false;

					//NeedtorefreshPositionsofallsortablesjustincaseremoving
					//fromonesortablechangesthelocationofothersortables(#9675)
					$.each(draggable.sortables,function(){
						this.refreshPositions();
					});
				}
			}
		});
	}
});

$.ui.plugin.add("draggable","cursor",{
	start:function(event,ui,instance){
		vart=$("body"),
			o=instance.options;

		if(t.css("cursor")){
			o._cursor=t.css("cursor");
		}
		t.css("cursor",o.cursor);
	},
	stop:function(event,ui,instance){
		varo=instance.options;
		if(o._cursor){
			$("body").css("cursor",o._cursor);
		}
	}
});

$.ui.plugin.add("draggable","opacity",{
	start:function(event,ui,instance){
		vart=$(ui.helper),
			o=instance.options;
		if(t.css("opacity")){
			o._opacity=t.css("opacity");
		}
		t.css("opacity",o.opacity);
	},
	stop:function(event,ui,instance){
		varo=instance.options;
		if(o._opacity){
			$(ui.helper).css("opacity",o._opacity);
		}
	}
});

$.ui.plugin.add("draggable","scroll",{
	start:function(event,ui,i){
		if(!i.scrollParentNotHidden){
			i.scrollParentNotHidden=i.helper.scrollParent(false);
		}

		if(i.scrollParentNotHidden[0]!==i.document[0]&&
				i.scrollParentNotHidden[0].tagName!=="HTML"){
			i.overflowOffset=i.scrollParentNotHidden.offset();
		}
	},
	drag:function(event,ui,i ){

		varo=i.options,
			scrolled=false,
			scrollParent=i.scrollParentNotHidden[0],
			document=i.document[0];

		if(scrollParent!==document&&scrollParent.tagName!=="HTML"){
			if(!o.axis||o.axis!=="x"){
				if((i.overflowOffset.top+scrollParent.offsetHeight)-event.pageY<
						o.scrollSensitivity){
					scrollParent.scrollTop=scrolled=scrollParent.scrollTop+o.scrollSpeed;
				}elseif(event.pageY-i.overflowOffset.top<o.scrollSensitivity){
					scrollParent.scrollTop=scrolled=scrollParent.scrollTop-o.scrollSpeed;
				}
			}

			if(!o.axis||o.axis!=="y"){
				if((i.overflowOffset.left+scrollParent.offsetWidth)-event.pageX<
						o.scrollSensitivity){
					scrollParent.scrollLeft=scrolled=scrollParent.scrollLeft+o.scrollSpeed;
				}elseif(event.pageX-i.overflowOffset.left<o.scrollSensitivity){
					scrollParent.scrollLeft=scrolled=scrollParent.scrollLeft-o.scrollSpeed;
				}
			}

		}else{

			if(!o.axis||o.axis!=="x"){
				if(event.pageY-$(document).scrollTop()<o.scrollSensitivity){
					scrolled=$(document).scrollTop($(document).scrollTop()-o.scrollSpeed);
				}elseif($(window).height()-(event.pageY-$(document).scrollTop())<
						o.scrollSensitivity){
					scrolled=$(document).scrollTop($(document).scrollTop()+o.scrollSpeed);
				}
			}

			if(!o.axis||o.axis!=="y"){
				if(event.pageX-$(document).scrollLeft()<o.scrollSensitivity){
					scrolled=$(document).scrollLeft(
						$(document).scrollLeft()-o.scrollSpeed
					);
				}elseif($(window).width()-(event.pageX-$(document).scrollLeft())<
						o.scrollSensitivity){
					scrolled=$(document).scrollLeft(
						$(document).scrollLeft()+o.scrollSpeed
					);
				}
			}

		}

		if(scrolled!==false&&$.ui.ddmanager&&!o.dropBehaviour){
			$.ui.ddmanager.prepareOffsets(i,event);
		}

	}
});

$.ui.plugin.add("draggable","snap",{
	start:function(event,ui,i){

		varo=i.options;

		i.snapElements=[];

		$(o.snap.constructor!==String?(o.snap.items||":data(ui-draggable)"):o.snap)
			.each(function(){
				var$t=$(this),
					$o=$t.offset();
				if(this!==i.element[0]){
					i.snapElements.push({
						item:this,
						width:$t.outerWidth(),height:$t.outerHeight(),
						top:$o.top,left:$o.left
					});
				}
			});

	},
	drag:function(event,ui,inst){

		varts,bs,ls,rs,l,r,t,b,i,first,
			o=inst.options,
			d=o.snapTolerance,
			x1=ui.offset.left,x2=x1+inst.helperProportions.width,
			y1=ui.offset.top,y2=y1+inst.helperProportions.height;

		for(i=inst.snapElements.length-1;i>=0;i--){

			l=inst.snapElements[i].left-inst.margins.left;
			r=l+inst.snapElements[i].width;
			t=inst.snapElements[i].top-inst.margins.top;
			b=t+inst.snapElements[i].height;

			if(x2<l-d||x1>r+d||y2<t-d||y1>b+d||
					!$.contains(inst.snapElements[i].item.ownerDocument,
					inst.snapElements[i].item)){
				if(inst.snapElements[i].snapping){
					(inst.options.snap.release&&
						inst.options.snap.release.call(
							inst.element,
							event,
							$.extend(inst._uiHash(),{snapItem:inst.snapElements[i].item})
						));
				}
				inst.snapElements[i].snapping=false;
				continue;
			}

			if(o.snapMode!=="inner"){
				ts=Math.abs(t-y2)<=d;
				bs=Math.abs(b-y1)<=d;
				ls=Math.abs(l-x2)<=d;
				rs=Math.abs(r-x1)<=d;
				if(ts){
					ui.position.top=inst._convertPositionTo("relative",{
						top:t-inst.helperProportions.height,
						left:0
					}).top;
				}
				if(bs){
					ui.position.top=inst._convertPositionTo("relative",{
						top:b,
						left:0
					}).top;
				}
				if(ls){
					ui.position.left=inst._convertPositionTo("relative",{
						top:0,
						left:l-inst.helperProportions.width
					}).left;
				}
				if(rs){
					ui.position.left=inst._convertPositionTo("relative",{
						top:0,
						left:r
					}).left;
				}
			}

			first=(ts||bs||ls||rs);

			if(o.snapMode!=="outer"){
				ts=Math.abs(t-y1)<=d;
				bs=Math.abs(b-y2)<=d;
				ls=Math.abs(l-x1)<=d;
				rs=Math.abs(r-x2)<=d;
				if(ts){
					ui.position.top=inst._convertPositionTo("relative",{
						top:t,
						left:0
					}).top;
				}
				if(bs){
					ui.position.top=inst._convertPositionTo("relative",{
						top:b-inst.helperProportions.height,
						left:0
					}).top;
				}
				if(ls){
					ui.position.left=inst._convertPositionTo("relative",{
						top:0,
						left:l
					}).left;
				}
				if(rs){
					ui.position.left=inst._convertPositionTo("relative",{
						top:0,
						left:r-inst.helperProportions.width
					}).left;
				}
			}

			if(!inst.snapElements[i].snapping&&(ts||bs||ls||rs||first)){
				(inst.options.snap.snap&&
					inst.options.snap.snap.call(
						inst.element,
						event,
						$.extend(inst._uiHash(),{
							snapItem:inst.snapElements[i].item
						})));
			}
			inst.snapElements[i].snapping=(ts||bs||ls||rs||first);

		}

	}
});

$.ui.plugin.add("draggable","stack",{
	start:function(event,ui,instance){
		varmin,
			o=instance.options,
			group=$.makeArray($(o.stack)).sort(function(a,b){
				return(parseInt($(a).css("zIndex"),10)||0)-
					(parseInt($(b).css("zIndex"),10)||0);
			});

		if(!group.length){return;}

		min=parseInt($(group[0]).css("zIndex"),10)||0;
		$(group).each(function(i){
			$(this).css("zIndex",min+i);
		});
		this.css("zIndex",(min+group.length));
	}
});

$.ui.plugin.add("draggable","zIndex",{
	start:function(event,ui,instance){
		vart=$(ui.helper),
			o=instance.options;

		if(t.css("zIndex")){
			o._zIndex=t.css("zIndex");
		}
		t.css("zIndex",o.zIndex);
	},
	stop:function(event,ui,instance){
		varo=instance.options;

		if(o._zIndex){
			$(ui.helper).css("zIndex",o._zIndex);
		}
	}
});

varwidgetsDraggable=$.ui.draggable;


/*!
 *jQueryUIDroppable1.12.1
 *http://jqueryui.com
 *
 *CopyrightjQueryFoundationandothercontributors
 *ReleasedundertheMITlicense.
 *http://jquery.org/license
 */

//>>label:Droppable
//>>group:Interactions
//>>description:Enablesdroptargetsfordraggableelements.
//>>docs:http://api.jqueryui.com/droppable/
//>>demos:http://jqueryui.com/droppable/



$.widget("ui.droppable",{
	version:"1.12.1",
	widgetEventPrefix:"drop",
	options:{
		accept:"*",
		addClasses:true,
		greedy:false,
		scope:"default",
		tolerance:"intersect",

		//Callbacks
		activate:null,
		deactivate:null,
		drop:null,
		out:null,
		over:null
	},
	_create:function(){

		varproportions,
			o=this.options,
			accept=o.accept;

		this.isover=false;
		this.isout=true;

		this.accept=$.isFunction(accept)?accept:function(d){
			returnd.is(accept);
		};

		this.proportions=function(/*valueToWrite*/){
			if(arguments.length){

				//Storethedroppable'sproportions
				proportions=arguments[0];
			}else{

				//Retrieveorderivethedroppable'sproportions
				returnproportions?
					proportions:
					proportions={
						width:this.element[0].offsetWidth,
						height:this.element[0].offsetHeight
					};
			}
		};

		this._addToManager(o.scope);

		o.addClasses&&this._addClass("ui-droppable");

	},

	_addToManager:function(scope){

		//Addthereferenceandpositionstothemanager
		$.ui.ddmanager.droppables[scope]=$.ui.ddmanager.droppables[scope]||[];
		$.ui.ddmanager.droppables[scope].push(this);
	},

	_splice:function(drop){
		vari=0;
		for(;i<drop.length;i++){
			if(drop[i]===this){
				drop.splice(i,1);
			}
		}
	},

	_destroy:function(){
		vardrop=$.ui.ddmanager.droppables[this.options.scope];

		this._splice(drop);
	},

	_setOption:function(key,value){

		if(key==="accept"){
			this.accept=$.isFunction(value)?value:function(d){
				returnd.is(value);
			};
		}elseif(key==="scope"){
			vardrop=$.ui.ddmanager.droppables[this.options.scope];

			this._splice(drop);
			this._addToManager(value);
		}

		this._super(key,value);
	},

	_activate:function(event){
		vardraggable=$.ui.ddmanager.current;

		this._addActiveClass();
		if(draggable){
			this._trigger("activate",event,this.ui(draggable));
		}
	},

	_deactivate:function(event){
		vardraggable=$.ui.ddmanager.current;

		this._removeActiveClass();
		if(draggable){
			this._trigger("deactivate",event,this.ui(draggable));
		}
	},

	_over:function(event){

		vardraggable=$.ui.ddmanager.current;

		//Bailifdraggableanddroppablearesameelement
		if(!draggable||(draggable.currentItem||
				draggable.element)[0]===this.element[0]){
			return;
		}

		if(this.accept.call(this.element[0],(draggable.currentItem||
				draggable.element))){
			this._addHoverClass();
			this._trigger("over",event,this.ui(draggable));
		}

	},

	_out:function(event){

		vardraggable=$.ui.ddmanager.current;

		//Bailifdraggableanddroppablearesameelement
		if(!draggable||(draggable.currentItem||
				draggable.element)[0]===this.element[0]){
			return;
		}

		if(this.accept.call(this.element[0],(draggable.currentItem||
				draggable.element))){
			this._removeHoverClass();
			this._trigger("out",event,this.ui(draggable));
		}

	},

	_drop:function(event,custom){

		vardraggable=custom||$.ui.ddmanager.current,
			childrenIntersection=false;

		//Bailifdraggableanddroppablearesameelement
		if(!draggable||(draggable.currentItem||
				draggable.element)[0]===this.element[0]){
			returnfalse;
		}

		this.element
			.find(":data(ui-droppable)")
			.not(".ui-draggable-dragging")
			.each(function(){
				varinst=$(this).droppable("instance");
				if(
					inst.options.greedy&&
					!inst.options.disabled&&
					inst.options.scope===draggable.options.scope&&
					inst.accept.call(
						inst.element[0],(draggable.currentItem||draggable.element)
					)&&
					intersect(
						draggable,
						$.extend(inst,{offset:inst.element.offset()}),
						inst.options.tolerance,event
					)
				){
					childrenIntersection=true;
					returnfalse;}
			});
		if(childrenIntersection){
			returnfalse;
		}

		if(this.accept.call(this.element[0],
				(draggable.currentItem||draggable.element))){
			this._removeActiveClass();
			this._removeHoverClass();

			this._trigger("drop",event,this.ui(draggable));
			returnthis.element;
		}

		returnfalse;

	},

	ui:function(c){
		return{
			draggable:(c.currentItem||c.element),
			helper:c.helper,
			position:c.position,
			offset:c.positionAbs
		};
	},

	//Extensionpointsjusttomakebackcompatsaneandavoidduplicatinglogic
	//TODO:Removein1.13alongwithcalltoitbelow
	_addHoverClass:function(){
		this._addClass("ui-droppable-hover");
	},

	_removeHoverClass:function(){
		this._removeClass("ui-droppable-hover");
	},

	_addActiveClass:function(){
		this._addClass("ui-droppable-active");
	},

	_removeActiveClass:function(){
		this._removeClass("ui-droppable-active");
	}
});

varintersect=$.ui.intersect=(function(){
	functionisOverAxis(x,reference,size){
		return(x>=reference)&&(x<(reference+size));
	}

	returnfunction(draggable,droppable,toleranceMode,event){

		if(!droppable.offset){
			returnfalse;
		}

		varx1=(draggable.positionAbs||
				draggable.position.absolute).left+draggable.margins.left,
			y1=(draggable.positionAbs||
				draggable.position.absolute).top+draggable.margins.top,
			x2=x1+draggable.helperProportions.width,
			y2=y1+draggable.helperProportions.height,
			l=droppable.offset.left,
			t=droppable.offset.top,
			r=l+droppable.proportions().width,
			b=t+droppable.proportions().height;

		switch(toleranceMode){
		case"fit":
			return(l<=x1&&x2<=r&&t<=y1&&y2<=b);
		case"intersect":
			return(l<x1+(draggable.helperProportions.width/2)&&//RightHalf
				x2-(draggable.helperProportions.width/2)<r&&//LeftHalf
				t<y1+(draggable.helperProportions.height/2)&&//BottomHalf
				y2-(draggable.helperProportions.height/2)<b);//TopHalf
		case"pointer":
			returnisOverAxis(event.pageY,t,droppable.proportions().height)&&
				isOverAxis(event.pageX,l,droppable.proportions().width);
		case"touch":
			return(
				(y1>=t&&y1<=b)||//Topedgetouching
				(y2>=t&&y2<=b)||//Bottomedgetouching
				(y1<t&&y2>b)//Surroundedvertically
			)&&(
				(x1>=l&&x1<=r)||//Leftedgetouching
				(x2>=l&&x2<=r)||//Rightedgetouching
				(x1<l&&x2>r)//Surroundedhorizontally
			);
		default:
			returnfalse;
		}
	};
})();

/*
	Thismanagertracksoffsetsofdraggablesanddroppables
*/
$.ui.ddmanager={
	current:null,
	droppables:{"default":[]},
	prepareOffsets:function(t,event){

		vari,j,
			m=$.ui.ddmanager.droppables[t.options.scope]||[],
			type=event?event.type:null,//workaroundfor#2317
			list=(t.currentItem||t.element).find(":data(ui-droppable)").addBack();

		droppablesLoop:for(i=0;i<m.length;i++){

			//Nodisabledandnon-accepted
			if(m[i].options.disabled||(t&&!m[i].accept.call(m[i].element[0],
					(t.currentItem||t.element)))){
				continue;
			}

			//Filteroutelementsinthecurrentdraggeditem
			for(j=0;j<list.length;j++){
				if(list[j]===m[i].element[0]){
					m[i].proportions().height=0;
					continuedroppablesLoop;
				}
			}

			m[i].visible=m[i].element.css("display")!=="none";
			if(!m[i].visible){
				continue;
			}

			//Activatethedroppableifuseddirectlyfromdraggables
			if(type==="mousedown"){
				m[i]._activate.call(m[i],event);
			}

			m[i].offset=m[i].element.offset();
			m[i].proportions({
				width:m[i].element[0].offsetWidth,
				height:m[i].element[0].offsetHeight
			});

		}

	},
	drop:function(draggable,event){

		vardropped=false;

		//Createacopyofthedroppablesincasethelistchangesduringthedrop(#9116)
		$.each(($.ui.ddmanager.droppables[draggable.options.scope]||[]).slice(),function(){

			if(!this.options){
				return;
			}
			if(!this.options.disabled&&this.visible&&
					intersect(draggable,this,this.options.tolerance,event)){
				dropped=this._drop.call(this,event)||dropped;
			}

			if(!this.options.disabled&&this.visible&&this.accept.call(this.element[0],
					(draggable.currentItem||draggable.element))){
				this.isout=true;
				this.isover=false;
				this._deactivate.call(this,event);
			}

		});
		returndropped;

	},
	dragStart:function(draggable,event){

		//Listenforscrollingsothatifthedraggingcausesscrollingthepositionofthe
		//droppablescanberecalculated(see#5003)
		draggable.element.parentsUntil("body").on("scroll.droppable",function(){
			if(!draggable.options.refreshPositions){
				$.ui.ddmanager.prepareOffsets(draggable,event);
			}
		});
	},
	drag:function(draggable,event){

		//Ifyouhaveahighlydynamicpage,youmighttrythisoption.Itrenderspositions
		//everytimeyoumovethemouse.
		if(draggable.options.refreshPositions){
			$.ui.ddmanager.prepareOffsets(draggable,event);
		}

		//Runthroughalldroppablesandchecktheirpositionsbasedonspecifictoleranceoptions
		$.each($.ui.ddmanager.droppables[draggable.options.scope]||[],function(){

			if(this.options.disabled||this.greedyChild||!this.visible){
				return;
			}

			varparentInstance,scope,parent,
				intersects=intersect(draggable,this,this.options.tolerance,event),
				c=!intersects&&this.isover?
					"isout":
					(intersects&&!this.isover?"isover":null);
			if(!c){
				return;
			}

			if(this.options.greedy){

				//finddroppableparentswithsamescope
				scope=this.options.scope;
				parent=this.element.parents(":data(ui-droppable)").filter(function(){
					return$(this).droppable("instance").options.scope===scope;
				});

				if(parent.length){
					parentInstance=$(parent[0]).droppable("instance");
					parentInstance.greedyChild=(c==="isover");
				}
			}

			//Wejustmovedintoagreedychild
			if(parentInstance&&c==="isover"){
				parentInstance.isover=false;
				parentInstance.isout=true;
				parentInstance._out.call(parentInstance,event);
			}

			this[c]=true;
			this[c==="isout"?"isover":"isout"]=false;
			this[c==="isover"?"_over":"_out"].call(this,event);

			//Wejustmovedoutofagreedychild
			if(parentInstance&&c==="isout"){
				parentInstance.isout=false;
				parentInstance.isover=true;
				parentInstance._over.call(parentInstance,event);
			}
		});

	},
	dragStop:function(draggable,event){
		draggable.element.parentsUntil("body").off("scroll.droppable");

		//CallprepareOffsetsonefinaltimesinceIEdoesnotfirereturnscrolleventswhen
		//overflowwascausedbydrag(see#5003)
		if(!draggable.options.refreshPositions){
			$.ui.ddmanager.prepareOffsets(draggable,event);
		}
	}
};

//DEPRECATED
//TODO:switchreturnbacktowidgetdeclarationattopoffilewhenthisisremoved
if($.uiBackCompat!==false){

	//BackcompatforactiveClassandhoverClassoptions
	$.widget("ui.droppable",$.ui.droppable,{
		options:{
			hoverClass:false,
			activeClass:false
		},
		_addActiveClass:function(){
			this._super();
			if(this.options.activeClass){
				this.element.addClass(this.options.activeClass);
			}
		},
		_removeActiveClass:function(){
			this._super();
			if(this.options.activeClass){
				this.element.removeClass(this.options.activeClass);
			}
		},
		_addHoverClass:function(){
			this._super();
			if(this.options.hoverClass){
				this.element.addClass(this.options.hoverClass);
			}
		},
		_removeHoverClass:function(){
			this._super();
			if(this.options.hoverClass){
				this.element.removeClass(this.options.hoverClass);
			}
		}
	});
}

varwidgetsDroppable=$.ui.droppable;


/*!
 *jQueryUIResizable1.12.1
 *http://jqueryui.com
 *
 *CopyrightjQueryFoundationandothercontributors
 *ReleasedundertheMITlicense.
 *http://jquery.org/license
 */

//>>label:Resizable
//>>group:Interactions
//>>description:Enablesresizefunctionalityforanyelement.
//>>docs:http://api.jqueryui.com/resizable/
//>>demos:http://jqueryui.com/resizable/
//>>css.structure:../../themes/base/core.css
//>>css.structure:../../themes/base/resizable.css
//>>css.theme:../../themes/base/theme.css



$.widget("ui.resizable",$.ui.mouse,{
	version:"1.12.1",
	widgetEventPrefix:"resize",
	options:{
		alsoResize:false,
		animate:false,
		animateDuration:"slow",
		animateEasing:"swing",
		aspectRatio:false,
		autoHide:false,
		classes:{
			"ui-resizable-se":"ui-iconui-icon-gripsmall-diagonal-se"
		},
		containment:false,
		ghost:false,
		grid:false,
		handles:"e,s,se",
		helper:false,
		maxHeight:null,
		maxWidth:null,
		minHeight:10,
		minWidth:10,

		//See#7960
		zIndex:90,

		flectra_isRTL:false,

		//Callbacks
		resize:null,
		start:null,
		stop:null
	},

	_num:function(value){
		returnparseFloat(value)||0;
	},

	_isNumber:function(value){
		return!isNaN(parseFloat(value));
	},

	_hasScroll:function(el,a){

		if($(el).css("overflow")==="hidden"){
			returnfalse;
		}

		varscroll=(a&&a==="left")?"scrollLeft":"scrollTop",
			has=false;

		if(el[scroll]>0){
			returntrue;
		}

		//TODO:determinewhichcasesactuallycausethistohappen
		//iftheelementdoesn'thavethescrollset,seeifit'spossibleto
		//setthescroll
		el[scroll]=1;
		has=(el[scroll]>0);
		el[scroll]=0;
		returnhas;
	},

	_create:function(){

		varmargins,
			o=this.options,
			that=this;
		this._addClass("ui-resizable");

		$.extend(this,{
			_aspectRatio:!!(o.aspectRatio),
			aspectRatio:o.aspectRatio,
			originalElement:this.element,
			_proportionallyResizeElements:[],
			_helper:o.helper||o.ghost||o.animate?o.helper||"ui-resizable-helper":null
		});

		//Wraptheelementifitcannotholdchildnodes
		if(this.element[0].nodeName.match(/^(canvas|textarea|input|select|button|img)$/i)){

			this.element.wrap(
				$("<divclass='ui-wrapper'style='overflow:hidden;'></div>").css({
					position:this.element.css("position"),
					width:this.element.outerWidth(),
					height:this.element.outerHeight(),
					top:this.element.css("top"),
					left:this.element.css("left")
				})
			);

			this.element=this.element.parent().data(
				"ui-resizable",this.element.resizable("instance")
			);

			this.elementIsWrapper=true;

			margins={
				marginTop:this.originalElement.css("marginTop"),
				marginRight:this.originalElement.css("marginRight"),
				marginBottom:this.originalElement.css("marginBottom"),
				marginLeft:this.originalElement.css("marginLeft")
			};

			this.element.css(margins);
			this.originalElement.css("margin",0);

			//support:Safari
			//PreventSafaritextarearesize
			this.originalResizeStyle=this.originalElement.css("resize");
			this.originalElement.css("resize","none");

			this._proportionallyResizeElements.push(this.originalElement.css({
				position:"static",
				zoom:1,
				display:"block"
			}));

			//Support:IE9
			//avoidIEjump(hardsetthemargin)
			this.originalElement.css(margins);

			this._proportionallyResize();
		}

		this._setupHandles();

		if(o.autoHide){
			$(this.element)
				.on("mouseenter",function(){
					if(o.disabled){
						return;
					}
					that._removeClass("ui-resizable-autohide");
					that._handles.show();
				})
				.on("mouseleave",function(){
					if(o.disabled){
						return;
					}
					if(!that.resizing){
						that._addClass("ui-resizable-autohide");
						that._handles.hide();
					}
				});
		}

		this._mouseInit();
	},

	_destroy:function(){

		this._mouseDestroy();

		varwrapper,
			_destroy=function(exp){
				$(exp)
					.removeData("resizable")
					.removeData("ui-resizable")
					.off(".resizable")
					.find(".ui-resizable-handle")
						.remove();
			};

		//TODO:UnwrapatsameDOMposition
		if(this.elementIsWrapper){
			_destroy(this.element);
			wrapper=this.element;
			this.originalElement.css({
				position:wrapper.css("position"),
				width:wrapper.outerWidth(),
				height:wrapper.outerHeight(),
				top:wrapper.css("top"),
				left:wrapper.css("left")
			}).insertAfter(wrapper);
			wrapper.remove();
		}

		this.originalElement.css("resize",this.originalResizeStyle);
		_destroy(this.originalElement);

		returnthis;
	},

	_setOption:function(key,value){
		this._super(key,value);

		switch(key){
		case"handles":
			this._removeHandles();
			this._setupHandles();
			break;
		default:
			break;
		}
	},

	_setupHandles:function(){
		varo=this.options,handle,i,n,hname,axis,that=this;
		this.handles=o.handles||
			(!$(".ui-resizable-handle",this.element).length?
				"e,s,se":{
					n:".ui-resizable-n",
					e:".ui-resizable-e",
					s:".ui-resizable-s",
					w:".ui-resizable-w",
					se:".ui-resizable-se",
					sw:".ui-resizable-sw",
					ne:".ui-resizable-ne",
					nw:".ui-resizable-nw"
				});

		this._handles=$();
		if(this.handles.constructor===String){

			if(this.handles==="all"){
				this.handles="n,e,s,w,se,sw,ne,nw";
			}

			n=this.handles.split(",");
			this.handles={};

			for(i=0;i<n.length;i++){

				handle=$.trim(n[i]);
				hname="ui-resizable-"+handle;
				axis=$("<div>");
				this._addClass(axis,"ui-resizable-handle"+hname);

				axis.css({zIndex:o.zIndex});

				this.handles[handle]=".ui-resizable-"+handle;
				this.element.append(axis);
			}

		}

		this._renderAxis=function(target){

			vari,axis,padPos,padWrapper;

			target=target||this.element;

			for(iinthis.handles){

				if(this.handles[i].constructor===String){
					this.handles[i]=this.element.children(this.handles[i]).first().show();
				}elseif(this.handles[i].jquery||this.handles[i].nodeType){
					this.handles[i]=$(this.handles[i]);
					this._on(this.handles[i],{"mousedown":that._mouseDown});
				}

				if(this.elementIsWrapper&&
						this.originalElement[0]
							.nodeName
							.match(/^(textarea|input|select|button)$/i)){
					axis=$(this.handles[i],this.element);

					padWrapper=/sw|ne|nw|se|n|s/.test(i)?
						axis.outerHeight():
						axis.outerWidth();

					padPos=["padding",
						/ne|nw|n/.test(i)?"Top":
						/se|sw|s/.test(i)?"Bottom":
						/^e$/.test(i)?"Right":"Left"].join("");

					target.css(padPos,padWrapper);

					this._proportionallyResize();
				}

				this._handles=this._handles.add(this.handles[i]);
			}
		};

		//TODO:makerenderAxisaprototypefunction
		this._renderAxis(this.element);

		this._handles=this._handles.add(this.element.find(".ui-resizable-handle"));
		this._handles.disableSelection();

		this._handles.on("mouseover",function(){
			if(!that.resizing){
				if(this.className){
					axis=this.className.match(/ui-resizable-(se|sw|ne|nw|n|e|s|w)/i);
				}
				that.axis=axis&&axis[1]?axis[1]:"se";
			}
		});

		if(o.autoHide){
			this._handles.hide();
			this._addClass("ui-resizable-autohide");
		}
	},

	_removeHandles:function(){
		this._handles.remove();
	},

	_mouseCapture:function(event){
		vari,handle,
			capture=false;

		for(iinthis.handles){
			handle=$(this.handles[i])[0];
			if(handle===event.target||$.contains(handle,event.target)){
				capture=true;
			}
		}

		return!this.options.disabled&&capture;
	},

	_mouseStart:function(event){

		varcurleft,curtop,cursor,
			o=this.options,
			el=this.element;

		this.resizing=true;

		this._renderProxy();

		curleft=this._num(this.helper.css("left"));
		curtop=this._num(this.helper.css("top"));

		if(o.containment){
			curleft+=$(o.containment).scrollLeft()||0;
			curtop+=$(o.containment).scrollTop()||0;
		}

		this.offset=this.helper.offset();
		this.position={left:curleft,top:curtop};

		this.size=this._helper?{
				width:this.helper.width(),
				height:this.helper.height()
			}:{
				width:el.width(),
				height:el.height()
			};

		this.originalSize=this._helper?{
				width:el.outerWidth(),
				height:el.outerHeight()
			}:{
				width:el.width(),
				height:el.height()
			};

		this.sizeDiff={
			width:el.outerWidth()-el.width(),
			height:el.outerHeight()-el.height()
		};

		this.originalPosition={left:curleft,top:curtop};
		this.originalMousePosition={left:event.pageX,top:event.pageY};

		this.aspectRatio=(typeofo.aspectRatio==="number")?
			o.aspectRatio:
			((this.originalSize.width/this.originalSize.height)||1);

		cursor=$(".ui-resizable-"+this.axis).css("cursor");
		$("body").css("cursor",cursor==="auto"?this.axis+"-resize":cursor);

		this._addClass("ui-resizable-resizing");
		this._propagate("start",event);
		returntrue;
	},

	_mouseDrag:function(event){

		vardata,props,
			smp=this.originalMousePosition,
			a=this.axis,
			dx=(event.pageX-smp.left)||0,
			dy=(event.pageY-smp.top)||0,
			trigger=this._change[a];
		dx=this.options.flectra_isRTL?-dx:dx;

		this._updatePrevProperties();

		if(!trigger){
			returnfalse;
		}

		data=trigger.apply(this,[event,dx,dy]);

		this._updateVirtualBoundaries(event.shiftKey);
		if(this._aspectRatio||event.shiftKey){
			data=this._updateRatio(data,event);
		}

		data=this._respectSize(data,event);

		this._updateCache(data);

		this._propagate("resize",event);

		props=this._applyChanges();

		if(!this._helper&&this._proportionallyResizeElements.length){
			this._proportionallyResize();
		}

		if(!$.isEmptyObject(props)){
			this._updatePrevProperties();
			this._trigger("resize",event,this.ui());
			this._applyChanges();
		}

		returnfalse;
	},

	_mouseStop:function(event){

		this.resizing=false;
		varpr,ista,soffseth,soffsetw,s,left,top,
			o=this.options,that=this;

		if(this._helper){

			pr=this._proportionallyResizeElements;
			ista=pr.length&&(/textarea/i).test(pr[0].nodeName);
			soffseth=ista&&this._hasScroll(pr[0],"left")?0:that.sizeDiff.height;
			soffsetw=ista?0:that.sizeDiff.width;

			s={
				width:(that.helper.width() -soffsetw),
				height:(that.helper.height()-soffseth)
			};
			left=(parseFloat(that.element.css("left"))+
				(that.position.left-that.originalPosition.left))||null;
			top=(parseFloat(that.element.css("top"))+
				(that.position.top-that.originalPosition.top))||null;

			if(!o.animate){
				this.element.css($.extend(s,{top:top,left:left}));
			}

			that.helper.height(that.size.height);
			that.helper.width(that.size.width);

			if(this._helper&&!o.animate){
				this._proportionallyResize();
			}
		}

		$("body").css("cursor","auto");

		this._removeClass("ui-resizable-resizing");

		this._propagate("stop",event);

		if(this._helper){
			this.helper.remove();
		}

		returnfalse;

	},

	_updatePrevProperties:function(){
		this.prevPosition={
			top:this.position.top,
			left:this.position.left
		};
		this.prevSize={
			width:this.size.width,
			height:this.size.height
		};
	},

	_applyChanges:function(){
		varprops={};

		if(this.position.top!==this.prevPosition.top){
			props.top=this.position.top+"px";
		}
		if(this.position.left!==this.prevPosition.left){
			props.left=this.position.left+"px";
		}
		if(this.size.width!==this.prevSize.width){
			props.width=this.size.width+"px";
		}
		if(this.size.height!==this.prevSize.height){
			props.height=this.size.height+"px";
		}

		this.helper.css(props);

		returnprops;
	},

	_updateVirtualBoundaries:function(forceAspectRatio){
		varpMinWidth,pMaxWidth,pMinHeight,pMaxHeight,b,
			o=this.options;

		b={
			minWidth:this._isNumber(o.minWidth)?o.minWidth:0,
			maxWidth:this._isNumber(o.maxWidth)?o.maxWidth:Infinity,
			minHeight:this._isNumber(o.minHeight)?o.minHeight:0,
			maxHeight:this._isNumber(o.maxHeight)?o.maxHeight:Infinity
		};

		if(this._aspectRatio||forceAspectRatio){
			pMinWidth=b.minHeight*this.aspectRatio;
			pMinHeight=b.minWidth/this.aspectRatio;
			pMaxWidth=b.maxHeight*this.aspectRatio;
			pMaxHeight=b.maxWidth/this.aspectRatio;

			if(pMinWidth>b.minWidth){
				b.minWidth=pMinWidth;
			}
			if(pMinHeight>b.minHeight){
				b.minHeight=pMinHeight;
			}
			if(pMaxWidth<b.maxWidth){
				b.maxWidth=pMaxWidth;
			}
			if(pMaxHeight<b.maxHeight){
				b.maxHeight=pMaxHeight;
			}
		}
		this._vBoundaries=b;
	},

	_updateCache:function(data){
		this.offset=this.helper.offset();
		if(this._isNumber(data.left)){
			this.position.left=data.left;
		}
		if(this._isNumber(data.top)){
			this.position.top=data.top;
		}
		if(this._isNumber(data.height)){
			this.size.height=data.height;
		}
		if(this._isNumber(data.width)){
			this.size.width=data.width;
		}
	},

	_updateRatio:function(data){

		varcpos=this.position,
			csize=this.size,
			a=this.axis;

		if(this._isNumber(data.height)){
			data.width=(data.height*this.aspectRatio);
		}elseif(this._isNumber(data.width)){
			data.height=(data.width/this.aspectRatio);
		}

		if(a==="sw"){
			data.left=cpos.left+(csize.width-data.width);
			data.top=null;
		}
		if(a==="nw"){
			data.top=cpos.top+(csize.height-data.height);
			data.left=cpos.left+(csize.width-data.width);
		}

		returndata;
	},

	_respectSize:function(data){

		varo=this._vBoundaries,
			a=this.axis,
			ismaxw=this._isNumber(data.width)&&o.maxWidth&&(o.maxWidth<data.width),
			ismaxh=this._isNumber(data.height)&&o.maxHeight&&(o.maxHeight<data.height),
			isminw=this._isNumber(data.width)&&o.minWidth&&(o.minWidth>data.width),
			isminh=this._isNumber(data.height)&&o.minHeight&&(o.minHeight>data.height),
			dw=this.originalPosition.left+this.originalSize.width,
			dh=this.originalPosition.top+this.originalSize.height,
			cw=/sw|nw|w/.test(a),ch=/nw|ne|n/.test(a);
		if(isminw){
			data.width=o.minWidth;
		}
		if(isminh){
			data.height=o.minHeight;
		}
		if(ismaxw){
			data.width=o.maxWidth;
		}
		if(ismaxh){
			data.height=o.maxHeight;
		}

		if(isminw&&cw){
			data.left=dw-o.minWidth;
		}
		if(ismaxw&&cw){
			data.left=dw-o.maxWidth;
		}
		if(isminh&&ch){
			data.top=dh-o.minHeight;
		}
		if(ismaxh&&ch){
			data.top=dh-o.maxHeight;
		}

		//Fixingjumperrorontop/left-bug#2330
		if(!data.width&&!data.height&&!data.left&&data.top){
			data.top=null;
		}elseif(!data.width&&!data.height&&!data.top&&data.left){
			data.left=null;
		}

		returndata;
	},

	_getPaddingPlusBorderDimensions:function(element){
		vari=0,
			widths=[],
			borders=[
				element.css("borderTopWidth"),
				element.css("borderRightWidth"),
				element.css("borderBottomWidth"),
				element.css("borderLeftWidth")
			],
			paddings=[
				element.css("paddingTop"),
				element.css("paddingRight"),
				element.css("paddingBottom"),
				element.css("paddingLeft")
			];

		for(;i<4;i++){
			widths[i]=(parseFloat(borders[i])||0);
			widths[i]+=(parseFloat(paddings[i])||0);
		}

		return{
			height:widths[0]+widths[2],
			width:widths[1]+widths[3]
		};
	},

	_proportionallyResize:function(){

		if(!this._proportionallyResizeElements.length){
			return;
		}

		varprel,
			i=0,
			element=this.helper||this.element;

		for(;i<this._proportionallyResizeElements.length;i++){

			prel=this._proportionallyResizeElements[i];

			//TODO:Seemslikeabugtocachethis.outerDimensions
			//consideringthatweareinaloop.
			if(!this.outerDimensions){
				this.outerDimensions=this._getPaddingPlusBorderDimensions(prel);
			}

			prel.css({
				height:(element.height()-this.outerDimensions.height)||0,
				width:(element.width()-this.outerDimensions.width)||0
			});

		}

	},

	_renderProxy:function(){

		varel=this.element,o=this.options;
		this.elementOffset=el.offset();

		if(this._helper){

			this.helper=this.helper||$("<divstyle='overflow:hidden;'></div>");

			this._addClass(this.helper,this._helper);
			this.helper.css({
				width:this.element.outerWidth(),
				height:this.element.outerHeight(),
				position:"absolute",
				left:this.elementOffset.left+"px",
				top:this.elementOffset.top+"px",
				zIndex:++o.zIndex//TODO:Don'tmodifyoption
			});

			this.helper
				.appendTo("body")
				.disableSelection();

		}else{
			this.helper=this.element;
		}

	},

	_change:{
		e:function(event,dx){
			return{width:this.originalSize.width+dx};
		},
		w:function(event,dx){
			varcs=this.originalSize,sp=this.originalPosition;
			return{left:sp.left+dx,width:cs.width-dx};
		},
		n:function(event,dx,dy){
			varcs=this.originalSize,sp=this.originalPosition;
			return{top:sp.top+dy,height:cs.height-dy};
		},
		s:function(event,dx,dy){
			return{height:this.originalSize.height+dy};
		},
		se:function(event,dx,dy){
			return$.extend(this._change.s.apply(this,arguments),
				this._change.e.apply(this,[event,dx,dy]));
		},
		sw:function(event,dx,dy){
			return$.extend(this._change.s.apply(this,arguments),
				this._change.w.apply(this,[event,dx,dy]));
		},
		ne:function(event,dx,dy){
			return$.extend(this._change.n.apply(this,arguments),
				this._change.e.apply(this,[event,dx,dy]));
		},
		nw:function(event,dx,dy){
			return$.extend(this._change.n.apply(this,arguments),
				this._change.w.apply(this,[event,dx,dy]));
		}
	},

	_propagate:function(n,event){
		$.ui.plugin.call(this,n,[event,this.ui()]);
		(n!=="resize"&&this._trigger(n,event,this.ui()));
	},

	plugins:{},

	ui:function(){
		return{
			originalElement:this.originalElement,
			element:this.element,
			helper:this.helper,
			position:this.position,
			size:this.size,
			originalSize:this.originalSize,
			originalPosition:this.originalPosition
		};
	}

});

/*
 *ResizableExtensions
 */

$.ui.plugin.add("resizable","animate",{

	stop:function(event){
		varthat=$(this).resizable("instance"),
			o=that.options,
			pr=that._proportionallyResizeElements,
			ista=pr.length&&(/textarea/i).test(pr[0].nodeName),
			soffseth=ista&&that._hasScroll(pr[0],"left")?0:that.sizeDiff.height,
			soffsetw=ista?0:that.sizeDiff.width,
			style={
				width:(that.size.width-soffsetw),
				height:(that.size.height-soffseth)
			},
			left=(parseFloat(that.element.css("left"))+
				(that.position.left-that.originalPosition.left))||null,
			top=(parseFloat(that.element.css("top"))+
				(that.position.top-that.originalPosition.top))||null;

		that.element.animate(
			$.extend(style,top&&left?{top:top,left:left}:{}),{
				duration:o.animateDuration,
				easing:o.animateEasing,
				step:function(){

					vardata={
						width:parseFloat(that.element.css("width")),
						height:parseFloat(that.element.css("height")),
						top:parseFloat(that.element.css("top")),
						left:parseFloat(that.element.css("left"))
					};

					if(pr&&pr.length){
						$(pr[0]).css({width:data.width,height:data.height});
					}

					//Propagatingresize,andupdatingvaluesforeachanimationstep
					that._updateCache(data);
					that._propagate("resize",event);

				}
			}
		);
	}

});

$.ui.plugin.add("resizable","containment",{

	start:function(){
		varelement,p,co,ch,cw,width,height,
			that=$(this).resizable("instance"),
			o=that.options,
			el=that.element,
			oc=o.containment,
			ce=(ocinstanceof$)?
				oc.get(0):
				(/parent/.test(oc))?el.parent().get(0):oc;

		if(!ce){
			return;
		}

		that.containerElement=$(ce);

		if(/document/.test(oc)||oc===document){
			that.containerOffset={
				left:0,
				top:0
			};
			that.containerPosition={
				left:0,
				top:0
			};

			that.parentData={
				element:$(document),
				left:0,
				top:0,
				width:$(document).width(),
				height:$(document).height()||document.body.parentNode.scrollHeight
			};
		}else{
			element=$(ce);
			p=[];
			$(["Top","Right","Left","Bottom"]).each(function(i,name){
				p[i]=that._num(element.css("padding"+name));
			});

			that.containerOffset=element.offset();
			that.containerPosition=element.position();
			that.containerSize={
				height:(element.innerHeight()-p[3]),
				width:(element.innerWidth()-p[1])
			};

			co=that.containerOffset;
			ch=that.containerSize.height;
			cw=that.containerSize.width;
			width=(that._hasScroll(ce,"left")?ce.scrollWidth:cw);
			height=(that._hasScroll(ce)?ce.scrollHeight:ch);

			that.parentData={
				element:ce,
				left:co.left,
				top:co.top,
				width:width,
				height:height
			};
		}
	},

	resize:function(event){
		varwoset,hoset,isParent,isOffsetRelative,
			that=$(this).resizable("instance"),
			o=that.options,
			co=that.containerOffset,
			cp=that.position,
			pRatio=that._aspectRatio||event.shiftKey,
			cop={
				top:0,
				left:0
			},
			ce=that.containerElement,
			continueResize=true;

		if(ce[0]!==document&&(/static/).test(ce.css("position"))){
			cop=co;
		}

		if(cp.left<(that._helper?co.left:0)){
			that.size.width=that.size.width+
				(that._helper?
					(that.position.left-co.left):
					(that.position.left-cop.left));

			if(pRatio){
				that.size.height=that.size.width/that.aspectRatio;
				continueResize=false;
			}
			that.position.left=o.helper?co.left:0;
		}

		if(cp.top<(that._helper?co.top:0)){
			that.size.height=that.size.height+
				(that._helper?
					(that.position.top-co.top):
					that.position.top);

			if(pRatio){
				that.size.width=that.size.height*that.aspectRatio;
				continueResize=false;
			}
			that.position.top=that._helper?co.top:0;
		}

		isParent=that.containerElement.get(0)===that.element.parent().get(0);
		isOffsetRelative=/relative|absolute/.test(that.containerElement.css("position"));

		if(isParent&&isOffsetRelative){
			that.offset.left=that.parentData.left+that.position.left;
			that.offset.top=that.parentData.top+that.position.top;
		}else{
			that.offset.left=that.element.offset().left;
			that.offset.top=that.element.offset().top;
		}

		woset=Math.abs(that.sizeDiff.width+
			(that._helper?
				that.offset.left-cop.left:
				(that.offset.left-co.left)));

		hoset=Math.abs(that.sizeDiff.height+
			(that._helper?
				that.offset.top-cop.top:
				(that.offset.top-co.top)));

		if(woset+that.size.width>=that.parentData.width){
			that.size.width=that.parentData.width-woset;
			if(pRatio){
				that.size.height=that.size.width/that.aspectRatio;
				continueResize=false;
			}
		}

		if(hoset+that.size.height>=that.parentData.height){
			that.size.height=that.parentData.height-hoset;
			if(pRatio){
				that.size.width=that.size.height*that.aspectRatio;
				continueResize=false;
			}
		}

		if(!continueResize){
			that.position.left=that.prevPosition.left;
			that.position.top=that.prevPosition.top;
			that.size.width=that.prevSize.width;
			that.size.height=that.prevSize.height;
		}
	},

	stop:function(){
		varthat=$(this).resizable("instance"),
			o=that.options,
			co=that.containerOffset,
			cop=that.containerPosition,
			ce=that.containerElement,
			helper=$(that.helper),
			ho=helper.offset(),
			w=helper.outerWidth()-that.sizeDiff.width,
			h=helper.outerHeight()-that.sizeDiff.height;

		if(that._helper&&!o.animate&&(/relative/).test(ce.css("position"))){
			$(this).css({
				left:ho.left-cop.left-co.left,
				width:w,
				height:h
			});
		}

		if(that._helper&&!o.animate&&(/static/).test(ce.css("position"))){
			$(this).css({
				left:ho.left-cop.left-co.left,
				width:w,
				height:h
			});
		}
	}
});

$.ui.plugin.add("resizable","alsoResize",{

	start:function(){
		varthat=$(this).resizable("instance"),
			o=that.options;

		$(o.alsoResize).each(function(){
			varel=$(this);
			el.data("ui-resizable-alsoresize",{
				width:parseFloat(el.width()),height:parseFloat(el.height()),
				left:parseFloat(el.css("left")),top:parseFloat(el.css("top"))
			});
		});
	},

	resize:function(event,ui){
		varthat=$(this).resizable("instance"),
			o=that.options,
			os=that.originalSize,
			op=that.originalPosition,
			delta={
				height:(that.size.height-os.height)||0,
				width:(that.size.width-os.width)||0,
				top:(that.position.top-op.top)||0,
				left:(that.position.left-op.left)||0
			};

			$(o.alsoResize).each(function(){
				varel=$(this),start=$(this).data("ui-resizable-alsoresize"),style={},
					css=el.parents(ui.originalElement[0]).length?
							["width","height"]:
							["width","height","top","left"];

				$.each(css,function(i,prop){
					varsum=(start[prop]||0)+(delta[prop]||0);
					if(sum&&sum>=0){
						style[prop]=sum||null;
					}
				});

				el.css(style);
			});
	},

	stop:function(){
		$(this).removeData("ui-resizable-alsoresize");
	}
});

$.ui.plugin.add("resizable","ghost",{

	start:function(){

		varthat=$(this).resizable("instance"),cs=that.size;

		that.ghost=that.originalElement.clone();
		that.ghost.css({
			opacity:0.25,
			display:"block",
			position:"relative",
			height:cs.height,
			width:cs.width,
			margin:0,
			left:0,
			top:0
		});

		that._addClass(that.ghost,"ui-resizable-ghost");

		//DEPRECATED
		//TODO:removeafter1.12
		if($.uiBackCompat!==false&&typeofthat.options.ghost==="string"){

			//Ghostoption
			that.ghost.addClass(this.options.ghost);
		}

		that.ghost.appendTo(that.helper);

	},

	resize:function(){
		varthat=$(this).resizable("instance");
		if(that.ghost){
			that.ghost.css({
				position:"relative",
				height:that.size.height,
				width:that.size.width
			});
		}
	},

	stop:function(){
		varthat=$(this).resizable("instance");
		if(that.ghost&&that.helper){
			that.helper.get(0).removeChild(that.ghost.get(0));
		}
	}

});

$.ui.plugin.add("resizable","grid",{

	resize:function(){
		varouterDimensions,
			that=$(this).resizable("instance"),
			o=that.options,
			cs=that.size,
			os=that.originalSize,
			op=that.originalPosition,
			a=that.axis,
			grid=typeofo.grid==="number"?[o.grid,o.grid]:o.grid,
			gridX=(grid[0]||1),
			gridY=(grid[1]||1),
			ox=Math.round((cs.width-os.width)/gridX)*gridX,
			oy=Math.round((cs.height-os.height)/gridY)*gridY,
			newWidth=os.width+ox,
			newHeight=os.height+oy,
			isMaxWidth=o.maxWidth&&(o.maxWidth<newWidth),
			isMaxHeight=o.maxHeight&&(o.maxHeight<newHeight),
			isMinWidth=o.minWidth&&(o.minWidth>newWidth),
			isMinHeight=o.minHeight&&(o.minHeight>newHeight);

		o.grid=grid;

		if(isMinWidth){
			newWidth+=gridX;
		}
		if(isMinHeight){
			newHeight+=gridY;
		}
		if(isMaxWidth){
			newWidth-=gridX;
		}
		if(isMaxHeight){
			newHeight-=gridY;
		}

		if(/^(se|s|e)$/.test(a)){
			that.size.width=newWidth;
			that.size.height=newHeight;
		}elseif(/^(ne)$/.test(a)){
			that.size.width=newWidth;
			that.size.height=newHeight;
			that.position.top=op.top-oy;
		}elseif(/^(sw)$/.test(a)){
			that.size.width=newWidth;
			that.size.height=newHeight;
			that.position.left=op.left-ox;
		}else{
			if(newHeight-gridY<=0||newWidth-gridX<=0){
				outerDimensions=that._getPaddingPlusBorderDimensions(this);
			}

			if(newHeight-gridY>0){
				that.size.height=newHeight;
				that.position.top=op.top-oy;
			}else{
				newHeight=gridY-outerDimensions.height;
				that.size.height=newHeight;
				that.position.top=op.top+os.height-newHeight;
			}
			if(newWidth-gridX>0){
				that.size.width=newWidth;
				if(that.options.flectra_isRTL){
					that.position.left=op.left+ox;
				}else{
					that.position.left=op.left-ox;
				}
			}else{
				newWidth=gridX-outerDimensions.width;
				that.size.width=newWidth;
				if(that.options.flectra_isRTL){
					that.position.left=op.left-os.width+newWidth;
				}else{
					that.position.left=op.left+os.width-newWidth;
				}
			}
		}
	}

});

varwidgetsResizable=$.ui.resizable;


/*!
 *jQueryUISelectable1.12.1
 *http://jqueryui.com
 *
 *CopyrightjQueryFoundationandothercontributors
 *ReleasedundertheMITlicense.
 *http://jquery.org/license
 */

//>>label:Selectable
//>>group:Interactions
//>>description:Allowsgroupsofelementstobeselectedwiththemouse.
//>>docs:http://api.jqueryui.com/selectable/
//>>demos:http://jqueryui.com/selectable/
//>>css.structure:../../themes/base/selectable.css



varwidgetsSelectable=$.widget("ui.selectable",$.ui.mouse,{
	version:"1.12.1",
	options:{
		appendTo:"body",
		autoRefresh:true,
		distance:0,
		filter:"*",
		tolerance:"touch",

		//Callbacks
		selected:null,
		selecting:null,
		start:null,
		stop:null,
		unselected:null,
		unselecting:null
	},
	_create:function(){
		varthat=this;

		this._addClass("ui-selectable");

		this.dragged=false;

		//Cacheselecteechildrenbasedonfilter
		this.refresh=function(){
			that.elementPos=$(that.element[0]).offset();
			that.selectees=$(that.options.filter,that.element[0]);
			that._addClass(that.selectees,"ui-selectee");
			that.selectees.each(function(){
				var$this=$(this),
					selecteeOffset=$this.offset(),
					pos={
						left:selecteeOffset.left-that.elementPos.left,
						top:selecteeOffset.top-that.elementPos.top
					};
				$.data(this,"selectable-item",{
					element:this,
					$element:$this,
					left:pos.left,
					top:pos.top,
					right:pos.left+$this.outerWidth(),
					bottom:pos.top+$this.outerHeight(),
					startselected:false,
					selected:$this.hasClass("ui-selected"),
					selecting:$this.hasClass("ui-selecting"),
					unselecting:$this.hasClass("ui-unselecting")
				});
			});
		};
		this.refresh();

		this._mouseInit();

		this.helper=$("<div>");
		this._addClass(this.helper,"ui-selectable-helper");
	},

	_destroy:function(){
		this.selectees.removeData("selectable-item");
		this._mouseDestroy();
	},

	_mouseStart:function(event){
		varthat=this,
			options=this.options;

		this.opos=[event.pageX,event.pageY];
		this.elementPos=$(this.element[0]).offset();

		if(this.options.disabled){
			return;
		}

		this.selectees=$(options.filter,this.element[0]);

		this._trigger("start",event);

		$(options.appendTo).append(this.helper);

		//positionhelper(lasso)
		this.helper.css({
			"left":event.pageX,
			"top":event.pageY,
			"width":0,
			"height":0
		});

		if(options.autoRefresh){
			this.refresh();
		}

		this.selectees.filter(".ui-selected").each(function(){
			varselectee=$.data(this,"selectable-item");
			selectee.startselected=true;
			if(!event.metaKey&&!event.ctrlKey){
				that._removeClass(selectee.$element,"ui-selected");
				selectee.selected=false;
				that._addClass(selectee.$element,"ui-unselecting");
				selectee.unselecting=true;

				//selectableUNSELECTINGcallback
				that._trigger("unselecting",event,{
					unselecting:selectee.element
				});
			}
		});

		$(event.target).parents().addBack().each(function(){
			vardoSelect,
				selectee=$.data(this,"selectable-item");
			if(selectee){
				doSelect=(!event.metaKey&&!event.ctrlKey)||
					!selectee.$element.hasClass("ui-selected");
				that._removeClass(selectee.$element,doSelect?"ui-unselecting":"ui-selected")
					._addClass(selectee.$element,doSelect?"ui-selecting":"ui-unselecting");
				selectee.unselecting=!doSelect;
				selectee.selecting=doSelect;
				selectee.selected=doSelect;

				//selectable(UN)SELECTINGcallback
				if(doSelect){
					that._trigger("selecting",event,{
						selecting:selectee.element
					});
				}else{
					that._trigger("unselecting",event,{
						unselecting:selectee.element
					});
				}
				returnfalse;
			}
		});

	},

	_mouseDrag:function(event){

		this.dragged=true;

		if(this.options.disabled){
			return;
		}

		vartmp,
			that=this,
			options=this.options,
			x1=this.opos[0],
			y1=this.opos[1],
			x2=event.pageX,
			y2=event.pageY;

		if(x1>x2){tmp=x2;x2=x1;x1=tmp;}
		if(y1>y2){tmp=y2;y2=y1;y1=tmp;}
		this.helper.css({left:x1,top:y1,width:x2-x1,height:y2-y1});

		this.selectees.each(function(){
			varselectee=$.data(this,"selectable-item"),
				hit=false,
				offset={};

			//preventhelperfrombeingselectedifappendTo:selectable
			if(!selectee||selectee.element===that.element[0]){
				return;
			}

			offset.left  =selectee.left  +that.elementPos.left;
			offset.right =selectee.right +that.elementPos.left;
			offset.top   =selectee.top   +that.elementPos.top;
			offset.bottom=selectee.bottom+that.elementPos.top;

			if(options.tolerance==="touch"){
				hit=(!(offset.left>x2||offset.right<x1||offset.top>y2||
                    offset.bottom<y1));
			}elseif(options.tolerance==="fit"){
				hit=(offset.left>x1&&offset.right<x2&&offset.top>y1&&
                    offset.bottom<y2);
			}

			if(hit){

				//SELECT
				if(selectee.selected){
					that._removeClass(selectee.$element,"ui-selected");
					selectee.selected=false;
				}
				if(selectee.unselecting){
					that._removeClass(selectee.$element,"ui-unselecting");
					selectee.unselecting=false;
				}
				if(!selectee.selecting){
					that._addClass(selectee.$element,"ui-selecting");
					selectee.selecting=true;

					//selectableSELECTINGcallback
					that._trigger("selecting",event,{
						selecting:selectee.element
					});
				}
			}else{

				//UNSELECT
				if(selectee.selecting){
					if((event.metaKey||event.ctrlKey)&&selectee.startselected){
						that._removeClass(selectee.$element,"ui-selecting");
						selectee.selecting=false;
						that._addClass(selectee.$element,"ui-selected");
						selectee.selected=true;
					}else{
						that._removeClass(selectee.$element,"ui-selecting");
						selectee.selecting=false;
						if(selectee.startselected){
							that._addClass(selectee.$element,"ui-unselecting");
							selectee.unselecting=true;
						}

						//selectableUNSELECTINGcallback
						that._trigger("unselecting",event,{
							unselecting:selectee.element
						});
					}
				}
				if(selectee.selected){
					if(!event.metaKey&&!event.ctrlKey&&!selectee.startselected){
						that._removeClass(selectee.$element,"ui-selected");
						selectee.selected=false;

						that._addClass(selectee.$element,"ui-unselecting");
						selectee.unselecting=true;

						//selectableUNSELECTINGcallback
						that._trigger("unselecting",event,{
							unselecting:selectee.element
						});
					}
				}
			}
		});

		returnfalse;
	},

	_mouseStop:function(event){
		varthat=this;

		this.dragged=false;

		$(".ui-unselecting",this.element[0]).each(function(){
			varselectee=$.data(this,"selectable-item");
			that._removeClass(selectee.$element,"ui-unselecting");
			selectee.unselecting=false;
			selectee.startselected=false;
			that._trigger("unselected",event,{
				unselected:selectee.element
			});
		});
		$(".ui-selecting",this.element[0]).each(function(){
			varselectee=$.data(this,"selectable-item");
			that._removeClass(selectee.$element,"ui-selecting")
				._addClass(selectee.$element,"ui-selected");
			selectee.selecting=false;
			selectee.selected=true;
			selectee.startselected=true;
			that._trigger("selected",event,{
				selected:selectee.element
			});
		});
		this._trigger("stop",event);

		this.helper.remove();

		returnfalse;
	}

});


/*!
 *jQueryUISortable1.12.1
 *http://jqueryui.com
 *
 *CopyrightjQueryFoundationandothercontributors
 *ReleasedundertheMITlicense.
 *http://jquery.org/license
 */

//>>label:Sortable
//>>group:Interactions
//>>description:Enablesitemsinalisttobesortedusingthemouse.
//>>docs:http://api.jqueryui.com/sortable/
//>>demos:http://jqueryui.com/sortable/
//>>css.structure:../../themes/base/sortable.css



varwidgetsSortable=$.widget("ui.sortable",$.ui.mouse,{
	version:"1.12.1",
	widgetEventPrefix:"sort",
	ready:false,
	options:{
		appendTo:"parent",
		axis:false,
		connectWith:false,
		containment:false,
		cursor:"auto",
		cursorAt:false,
		dropOnEmpty:true,
		forcePlaceholderSize:false,
		forceHelperSize:false,
		grid:false,
		handle:false,
		helper:"original",
		items:">*",
		opacity:false,
		placeholder:false,
		revert:false,
		scroll:true,
		scrollSensitivity:20,
		scrollSpeed:20,
		scope:"default",
		tolerance:"intersect",
		zIndex:1000,

		//Callbacks
		activate:null,
		beforeStop:null,
		change:null,
		deactivate:null,
		out:null,
		over:null,
		receive:null,
		remove:null,
		sort:null,
		start:null,
		stop:null,
		update:null
	},

	_isOverAxis:function(x,reference,size){
		return(x>=reference)&&(x<(reference+size));
	},

	_isFloating:function(item){
		return(/left|right/).test(item.css("float"))||
			(/inline|table-cell/).test(item.css("display"));
	},

	_create:function(){
		this.containerCache={};
		this._addClass("ui-sortable");

		//Gettheitems
		this.refresh();

		//Let'sdeterminetheparent'soffset
		this.offset=this.element.offset();

		//Initializemouseeventsforinteraction
		this._mouseInit();

		this._setHandleClassName();

		//We'rereadytogo
		this.ready=true;

	},

	_setOption:function(key,value){
		this._super(key,value);

		if(key==="handle"){
			this._setHandleClassName();
		}
	},

	_setHandleClassName:function(){
		varthat=this;
		this._removeClass(this.element.find(".ui-sortable-handle"),"ui-sortable-handle");
		$.each(this.items,function(){
			that._addClass(
				this.instance.options.handle?
					this.item.find(this.instance.options.handle):
					this.item,
				"ui-sortable-handle"
			);
		});
	},

	_destroy:function(){
		this._mouseDestroy();

		for(vari=this.items.length-1;i>=0;i--){
			this.items[i].item.removeData(this.widgetName+"-item");
		}

		returnthis;
	},

	_mouseCapture:function(event,overrideHandle){
		varcurrentItem=null,
			validHandle=false,
			that=this;

		if(this.reverting){
			returnfalse;
		}

		if(this.options.disabled||this.options.type==="static"){
			returnfalse;
		}

		//Wehavetorefreshtheitemsdataoncefirst
		this._refreshItems(event);

		//Findoutiftheclickednode(oroneofitsparents)isaactualiteminthis.items
		$(event.target).parents().each(function(){
			if($.data(this,that.widgetName+"-item")===that){
				currentItem=$(this);
				returnfalse;
			}
		});
		if($.data(event.target,that.widgetName+"-item")===that){
			currentItem=$(event.target);
		}

		if(!currentItem){
			returnfalse;
		}
		if(this.options.handle&&!overrideHandle){
			$(this.options.handle,currentItem).find("*").addBack().each(function(){
				if(this===event.target){
					validHandle=true;
				}
			});
			if(!validHandle){
				returnfalse;
			}
		}

		this.currentItem=currentItem;
		this._removeCurrentsFromItems();
		returntrue;

	},

	_mouseStart:function(event,overrideHandle,noActivation){

		vari,body,
			o=this.options;

		this.currentContainer=this;

		//WeonlyneedtocallrefreshPositions,becausetherefreshItemscallhasbeenmovedto
		//mouseCapture
		this.refreshPositions();

		//Createandappendthevisiblehelper
		this.helper=this._createHelper(event);

		//Cachethehelpersize
		this._cacheHelperProportions();

		/*
		*-Positiongeneration-
		*Thisblockgenerateseverythingpositionrelated-it'sthecoreofdraggables.
		*/

		//Cachethemarginsoftheoriginalelement
		this._cacheMargins();

		//Getthenextscrollingparent
		this.scrollParent=this.helper.scrollParent();

		//Theelement'sabsolutepositiononthepageminusmargins
		this.offset=this.currentItem.offset();
		this.offset={
			top:this.offset.top-this.margins.top,
			left:this.offset.left-this.margins.left
		};

		$.extend(this.offset,{
			click:{//Wheretheclickhappened,relativetotheelement
				left:event.pageX-this.offset.left,
				top:event.pageY-this.offset.top
			},
			parent:this._getParentOffset(),

			//Thisisarelativetoabsolutepositionminustheactualpositioncalculation-
			//onlyusedforrelativepositionedhelper
			relative:this._getRelativeOffset()
		});

		//Onlyafterwegottheoffset,wecanchangethehelper'spositiontoabsolute
		//TODO:Stillneedtofigureoutawaytomakerelativesortingpossible
		this.helper.css("position","absolute");
		this.cssPosition=this.helper.css("position");

		//Generatetheoriginalposition
		this.originalPosition=this._generatePosition(event);
		this.originalPageX=event.pageX;
		this.originalPageY=event.pageY;

		//Adjustthemouseoffsetrelativetothehelperif"cursorAt"issupplied
		(o.cursorAt&&this._adjustOffsetFromHelper(o.cursorAt));

		//CachetheformerDOMposition
		this.domPosition={
			prev:this.currentItem.prev()[0],
			parent:this.currentItem.parent()[0]
		};

		//Ifthehelperisnottheoriginal,hidetheoriginalsoit'snotplayinganyroleduring
		//thedrag,won'tcauseanythingbadthisway
		if(this.helper[0]!==this.currentItem[0]){
			this.currentItem.hide();
		}

		//Createtheplaceholder
		this._createPlaceholder();

		//Setacontainmentifgivenintheoptions
		if(o.containment){
			this._setContainment();
		}

		if(o.cursor&&o.cursor!=="auto"){//cursoroption
			body=this.document.find("body");

			//Support:IE
			this.storedCursor=body.css("cursor");
			body.css("cursor",o.cursor);

			this.storedStylesheet=
				$("<style>*{cursor:"+o.cursor+"!important;}</style>").appendTo(body);
		}

		if(o.opacity){//opacityoption
			if(this.helper.css("opacity")){
				this._storedOpacity=this.helper.css("opacity");
			}
			this.helper.css("opacity",o.opacity);
		}

		if(o.zIndex){//zIndexoption
			if(this.helper.css("zIndex")){
				this._storedZIndex=this.helper.css("zIndex");
			}
			this.helper.css("zIndex",o.zIndex);
		}

		//Preparescrolling
		if(this.scrollParent[0]!==this.document[0]&&
				this.scrollParent[0].tagName!=="HTML"){
			this.overflowOffset=this.scrollParent.offset();
		}

		//Callcallbacks
		this._trigger("start",event,this._uiHash());

		//Recachethehelpersize
		if(!this._preserveHelperProportions){
			this._cacheHelperProportions();
		}

		//Post"activate"eventstopossiblecontainers
		if(!noActivation){
			for(i=this.containers.length-1;i>=0;i--){
				this.containers[i]._trigger("activate",event,this._uiHash(this));
			}
		}

		//Preparepossibledroppables
		if($.ui.ddmanager){
			$.ui.ddmanager.current=this;
		}

		if($.ui.ddmanager&&!o.dropBehaviour){
			$.ui.ddmanager.prepareOffsets(this,event);
		}

		this.dragging=true;

		this._addClass(this.helper,"ui-sortable-helper");

		//Executethedragonce-thiscausesthehelpernottobevisiblebeforegettingits
		//correctposition
		this._mouseDrag(event);
		returntrue;

	},

	_mouseDrag:function(event){
		vari,item,itemElement,intersection,
			o=this.options,
			scrolled=false;

		//Computethehelpersposition
		this.position=this._generatePosition(event);
		this.positionAbs=this._convertPositionTo("absolute");

		if(!this.lastPositionAbs){
			this.lastPositionAbs=this.positionAbs;
		}

		//Doscrolling
		if(this.options.scroll){
			if(this.scrollParent[0]!==this.document[0]&&
					this.scrollParent[0].tagName!=="HTML"){

				if((this.overflowOffset.top+this.scrollParent[0].offsetHeight)-
						event.pageY<o.scrollSensitivity){
					this.scrollParent[0].scrollTop=
						scrolled=this.scrollParent[0].scrollTop+o.scrollSpeed;
				}elseif(event.pageY-this.overflowOffset.top<o.scrollSensitivity){
					this.scrollParent[0].scrollTop=
						scrolled=this.scrollParent[0].scrollTop-o.scrollSpeed;
				}

				if((this.overflowOffset.left+this.scrollParent[0].offsetWidth)-
						event.pageX<o.scrollSensitivity){
					this.scrollParent[0].scrollLeft=scrolled=
						this.scrollParent[0].scrollLeft+o.scrollSpeed;
				}elseif(event.pageX-this.overflowOffset.left<o.scrollSensitivity){
					this.scrollParent[0].scrollLeft=scrolled=
						this.scrollParent[0].scrollLeft-o.scrollSpeed;
				}

			}else{

				if(event.pageY-this.document.scrollTop()<o.scrollSensitivity){
					scrolled=this.document.scrollTop(this.document.scrollTop()-o.scrollSpeed);
				}elseif(this.window.height()-(event.pageY-this.document.scrollTop())<
						o.scrollSensitivity){
					scrolled=this.document.scrollTop(this.document.scrollTop()+o.scrollSpeed);
				}

				if(event.pageX-this.document.scrollLeft()<o.scrollSensitivity){
					scrolled=this.document.scrollLeft(
						this.document.scrollLeft()-o.scrollSpeed
					);
				}elseif(this.window.width()-(event.pageX-this.document.scrollLeft())<
						o.scrollSensitivity){
					scrolled=this.document.scrollLeft(
						this.document.scrollLeft()+o.scrollSpeed
					);
				}

			}

			if(scrolled!==false&&$.ui.ddmanager&&!o.dropBehaviour){
				$.ui.ddmanager.prepareOffsets(this,event);
			}
		}

		//Regeneratetheabsolutepositionusedforpositionchecks
		this.positionAbs=this._convertPositionTo("absolute");

		//Setthehelperposition
		if(!this.options.axis||this.options.axis!=="y"){
			this.helper[0].style.left=this.position.left+"px";
		}
		if(!this.options.axis||this.options.axis!=="x"){
			this.helper[0].style.top=this.position.top+"px";
		}

		//Rearrange
		for(i=this.items.length-1;i>=0;i--){

			//Cachevariablesandintersection,continueifnointersection
			item=this.items[i];
			itemElement=item.item[0];
			intersection=this._intersectsWithPointer(item);
			if(!intersection){
				continue;
			}

			//OnlyputtheplaceholderinsidethecurrentContainer,skipall
			//itemsfromothercontainers.Thisworksbecausewhenmoving
			//anitemfromonecontainertoanotherthe
			//currentContainerisswitchedbeforetheplaceholderismoved.
			//
			//Withoutthis,movingitemsin"sub-sortables"cancause
			//theplaceholdertojitterbetweentheouterandinnercontainer.
			if(item.instance!==this.currentContainer){
				continue;
			}

			//Cannotintersectwithitself
			//nouselessactionsthathavebeendonebefore
			//noactioniftheitemmovedistheparentoftheitemchecked
			if(itemElement!==this.currentItem[0]&&
				this.placeholder[intersection===1?"next":"prev"]()[0]!==itemElement&&
				!$.contains(this.placeholder[0],itemElement)&&
				(this.options.type==="semi-dynamic"?
					!$.contains(this.element[0],itemElement):
					true
				)
			){

				this.direction=intersection===1?"down":"up";

				if(this.options.tolerance==="pointer"||this._intersectsWithSides(item)){
					this._rearrange(event,item);
				}else{
					break;
				}

				this._trigger("change",event,this._uiHash());
				break;
			}
		}

		//Posteventstocontainers
		this._contactContainers(event);

		//Interconnectwithdroppables
		if($.ui.ddmanager){
			$.ui.ddmanager.drag(this,event);
		}

		//Callcallbacks
		this._trigger("sort",event,this._uiHash());

		this.lastPositionAbs=this.positionAbs;
		returnfalse;

	},

	_mouseStop:function(event,noPropagation){

		if(!event){
			return;
		}

		//Ifweareusingdroppables,informthemanageraboutthedrop
		if($.ui.ddmanager&&!this.options.dropBehaviour){
			$.ui.ddmanager.drop(this,event);
		}

		if(this.options.revert){
			varthat=this,
				cur=this.placeholder.offset(),
				axis=this.options.axis,
				animation={};

			if(!axis||axis==="x"){
				animation.left=cur.left-this.offset.parent.left-this.margins.left+
					(this.offsetParent[0]===this.document[0].body?
						0:
						this.offsetParent[0].scrollLeft
					);
			}
			if(!axis||axis==="y"){
				animation.top=cur.top-this.offset.parent.top-this.margins.top+
					(this.offsetParent[0]===this.document[0].body?
						0:
						this.offsetParent[0].scrollTop
					);
			}
			this.reverting=true;
			$(this.helper).animate(
				animation,
				parseInt(this.options.revert,10)||500,
				function(){
					that._clear(event);
				}
			);
		}else{
			this._clear(event,noPropagation);
		}

		returnfalse;

	},

	cancel:function(){

		if(this.dragging){

			this._mouseUp(new$.Event("mouseup",{target:null}));

			if(this.options.helper==="original"){
				this.currentItem.css(this._storedCSS);
				this._removeClass(this.currentItem,"ui-sortable-helper");
			}else{
				this.currentItem.show();
			}

			//Postdeactivatingeventstocontainers
			for(vari=this.containers.length-1;i>=0;i--){
				this.containers[i]._trigger("deactivate",null,this._uiHash(this));
				if(this.containers[i].containerCache.over){
					this.containers[i]._trigger("out",null,this._uiHash(this));
					this.containers[i].containerCache.over=0;
				}
			}

		}

		if(this.placeholder){

			//$(this.placeholder[0]).remove();wouldhavebeenthejQueryway-unfortunately,
			//itunbindsALLeventsfromtheoriginalnode!
			if(this.placeholder[0].parentNode){
				this.placeholder[0].parentNode.removeChild(this.placeholder[0]);
			}
			if(this.options.helper!=="original"&&this.helper&&
					this.helper[0].parentNode){
				this.helper.remove();
			}

			$.extend(this,{
				helper:null,
				dragging:false,
				reverting:false,
				_noFinalSort:null
			});

			if(this.domPosition.prev){
				$(this.domPosition.prev).after(this.currentItem);
			}else{
				$(this.domPosition.parent).prepend(this.currentItem);
			}
		}

		returnthis;

	},

	serialize:function(o){

		varitems=this._getItemsAsjQuery(o&&o.connected),
			str=[];
		o=o||{};

		$(items).each(function(){
			varres=($(o.item||this).attr(o.attribute||"id")||"")
				.match(o.expression||(/(.+)[\-=_](.+)/));
			if(res){
				str.push(
					(o.key||res[1]+"[]")+
					"="+(o.key&&o.expression?res[1]:res[2]));
			}
		});

		if(!str.length&&o.key){
			str.push(o.key+"=");
		}

		returnstr.join("&");

	},

	toArray:function(o){

		varitems=this._getItemsAsjQuery(o&&o.connected),
			ret=[];

		o=o||{};

		items.each(function(){
			ret.push($(o.item||this).attr(o.attribute||"id")||"");
		});
		returnret;

	},

	/*Becarefulwiththefollowingcorefunctions*/
	_intersectsWith:function(item){

		varx1=this.positionAbs.left,
			x2=x1+this.helperProportions.width,
			y1=this.positionAbs.top,
			y2=y1+this.helperProportions.height,
			l=item.left,
			r=l+item.width,
			t=item.top,
			b=t+item.height,
			dyClick=this.offset.click.top,
			dxClick=this.offset.click.left,
			isOverElementHeight=(this.options.axis==="x")||((y1+dyClick)>t&&
				(y1+dyClick)<b),
			isOverElementWidth=(this.options.axis==="y")||((x1+dxClick)>l&&
				(x1+dxClick)<r),
			isOverElement=isOverElementHeight&&isOverElementWidth;

		if(this.options.tolerance==="pointer"||
			this.options.forcePointerForContainers||
			(this.options.tolerance!=="pointer"&&
				this.helperProportions[this.floating?"width":"height"]>
				item[this.floating?"width":"height"])
		){
			returnisOverElement;
		}else{

			return(l<x1+(this.helperProportions.width/2)&&//RightHalf
				x2-(this.helperProportions.width/2)<r&&//LeftHalf
				t<y1+(this.helperProportions.height/2)&&//BottomHalf
				y2-(this.helperProportions.height/2)<b);//TopHalf

		}
	},

	_intersectsWithPointer:function(item){
		varverticalDirection,horizontalDirection,
			isOverElementHeight=(this.options.axis==="x")||
				this._isOverAxis(
					this.positionAbs.top+this.offset.click.top,item.top,item.height),
			isOverElementWidth=(this.options.axis==="y")||
				this._isOverAxis(
					this.positionAbs.left+this.offset.click.left,item.left,item.width),
			isOverElement=isOverElementHeight&&isOverElementWidth;

		if(!isOverElement){
			returnfalse;
		}

		verticalDirection=this._getDragVerticalDirection();
		horizontalDirection=this._getDragHorizontalDirection();

		returnthis.floating?
			((horizontalDirection==="right"||verticalDirection==="down")?2:1)
			:(verticalDirection&&(verticalDirection==="down"?2:1));

	},

	_intersectsWithSides:function(item){

		varisOverBottomHalf=this._isOverAxis(this.positionAbs.top+
				this.offset.click.top,item.top+(item.height/2),item.height),
			isOverRightHalf=this._isOverAxis(this.positionAbs.left+
				this.offset.click.left,item.left+(item.width/2),item.width),
			verticalDirection=this._getDragVerticalDirection(),
			horizontalDirection=this._getDragHorizontalDirection();

		if(this.floating&&horizontalDirection){
			return((horizontalDirection==="right"&&isOverRightHalf)||
				(horizontalDirection==="left"&&!isOverRightHalf));
		}else{
			returnverticalDirection&&((verticalDirection==="down"&&isOverBottomHalf)||
				(verticalDirection==="up"&&!isOverBottomHalf));
		}

	},

	_getDragVerticalDirection:function(){
		vardelta=this.positionAbs.top-this.lastPositionAbs.top;
		returndelta!==0&&(delta>0?"down":"up");
	},

	_getDragHorizontalDirection:function(){
		vardelta=this.positionAbs.left-this.lastPositionAbs.left;
		returndelta!==0&&(delta>0?"right":"left");
	},

	refresh:function(event){
		this._refreshItems(event);
		this._setHandleClassName();
		this.refreshPositions();
		returnthis;
	},

	_connectWith:function(){
		varoptions=this.options;
		returnoptions.connectWith.constructor===String?
			[options.connectWith]:
			options.connectWith;
	},

	_getItemsAsjQuery:function(connected){

		vari,j,cur,inst,
			items=[],
			queries=[],
			connectWith=this._connectWith();

		if(connectWith&&connected){
			for(i=connectWith.length-1;i>=0;i--){
				cur=$(connectWith[i],this.document[0]);
				for(j=cur.length-1;j>=0;j--){
					inst=$.data(cur[j],this.widgetFullName);
					if(inst&&inst!==this&&!inst.options.disabled){
						queries.push([$.isFunction(inst.options.items)?
							inst.options.items.call(inst.element):
							$(inst.options.items,inst.element)
								.not(".ui-sortable-helper")
								.not(".ui-sortable-placeholder"),inst]);
					}
				}
			}
		}

		queries.push([$.isFunction(this.options.items)?
			this.options.items
				.call(this.element,null,{options:this.options,item:this.currentItem}):
			$(this.options.items,this.element)
				.not(".ui-sortable-helper")
				.not(".ui-sortable-placeholder"),this]);

		functionaddItems(){
			items.push(this);
		}
		for(i=queries.length-1;i>=0;i--){
			queries[i][0].each(addItems);
		}

		return$(items);

	},

	_removeCurrentsFromItems:function(){

		varlist=this.currentItem.find(":data("+this.widgetName+"-item)");

		this.items=$.grep(this.items,function(item){
			for(varj=0;j<list.length;j++){
				if(list[j]===item.item[0]){
					returnfalse;
				}
			}
			returntrue;
		});

	},

	_refreshItems:function(event){

		this.items=[];
		this.containers=[this];

		vari,j,cur,inst,targetData,_queries,item,queriesLength,
			items=this.items,
			queries=[[$.isFunction(this.options.items)?
				this.options.items.call(this.element[0],event,{item:this.currentItem}):
				$(this.options.items,this.element),this]],
			connectWith=this._connectWith();

		//Shouldn'tberunthefirsttimethroughduetomassiveslow-down
		if(connectWith&&this.ready){
			for(i=connectWith.length-1;i>=0;i--){
				cur=$(connectWith[i],this.document[0]);
				for(j=cur.length-1;j>=0;j--){
					inst=$.data(cur[j],this.widgetFullName);
					if(inst&&inst!==this&&!inst.options.disabled){
						queries.push([$.isFunction(inst.options.items)?
							inst.options.items
								.call(inst.element[0],event,{item:this.currentItem}):
							$(inst.options.items,inst.element),inst]);
						this.containers.push(inst);
					}
				}
			}
		}

		for(i=queries.length-1;i>=0;i--){
			targetData=queries[i][1];
			_queries=queries[i][0];

			for(j=0,queriesLength=_queries.length;j<queriesLength;j++){
				item=$(_queries[j]);

				//Datafortargetchecking(mousemanager)
				item.data(this.widgetName+"-item",targetData);

				items.push({
					item:item,
					instance:targetData,
					width:0,height:0,
					left:0,top:0
				});
			}
		}

	},

	refreshPositions:function(fast){

		//Determinewhetheritemsarebeingdisplayedhorizontally
		this.floating=this.items.length?
			this.options.axis==="x"||this._isFloating(this.items[0].item):
			false;

		//Thishastoberedonebecauseduetotheitembeingmovedout/intotheoffsetParent,
		//theoffsetParent'spositionwillchange
		if(this.offsetParent&&this.helper){
			this.offset.parent=this._getParentOffset();
		}

		vari,item,t,p;

		for(i=this.items.length-1;i>=0;i--){
			item=this.items[i];

			//Weignorecalculatingpositionsofallconnectedcontainerswhenwe'renotoverthem
			if(item.instance!==this.currentContainer&&this.currentContainer&&
					item.item[0]!==this.currentItem[0]){
				continue;
			}

			t=this.options.toleranceElement?
				$(this.options.toleranceElement,item.item):
				item.item;

			if(!fast){
				item.width=t.outerWidth();
				item.height=t.outerHeight();
			}

			p=t.offset();
			item.left=p.left;
			item.top=p.top;
		}

		if(this.options.custom&&this.options.custom.refreshContainers){
			this.options.custom.refreshContainers.call(this);
		}else{
			for(i=this.containers.length-1;i>=0;i--){
				p=this.containers[i].element.offset();
				this.containers[i].containerCache.left=p.left;
				this.containers[i].containerCache.top=p.top;
				this.containers[i].containerCache.width=
					this.containers[i].element.outerWidth();
				this.containers[i].containerCache.height=
					this.containers[i].element.outerHeight();
			}
		}

		returnthis;
	},

	_createPlaceholder:function(that){
		that=that||this;
		varclassName,
			o=that.options;

		if(!o.placeholder||o.placeholder.constructor===String){
			className=o.placeholder;
			o.placeholder={
				element:function(){

					varnodeName=that.currentItem[0].nodeName.toLowerCase(),
						element=$("<"+nodeName+">",that.document[0]);

						that._addClass(element,"ui-sortable-placeholder",
								className||that.currentItem[0].className)
							._removeClass(element,"ui-sortable-helper");

					if(nodeName==="tbody"){
						that._createTrPlaceholder(
							that.currentItem.find("tr").eq(0),
							$("<tr>",that.document[0]).appendTo(element)
						);
					}elseif(nodeName==="tr"){
						that._createTrPlaceholder(that.currentItem,element);
					}elseif(nodeName==="img"){
						element.attr("src",that.currentItem.attr("src"));
					}

					if(!className){
						element.css("visibility","hidden");
					}

					returnelement;
				},
				update:function(container,p){

					//1.IfaclassNameissetas'placeholderoption,wedon'tforcesizes-
					//theclassisresponsibleforthat
					//2.Theoption'forcePlaceholderSizecanbeenabledtoforceitevenifa
					//classnameisspecified
					if(className&&!o.forcePlaceholderSize){
						return;
					}

					//Iftheelementdoesn'thaveaactualheightbyitself(withoutstylescoming
					//fromastylesheet),itreceivestheinlineheightfromthedraggeditem
					if(!p.height()){
						p.height(
							that.currentItem.innerHeight()-
							parseInt(that.currentItem.css("paddingTop")||0,10)-
							parseInt(that.currentItem.css("paddingBottom")||0,10));
					}
					if(!p.width()){
						p.width(
							that.currentItem.innerWidth()-
							parseInt(that.currentItem.css("paddingLeft")||0,10)-
							parseInt(that.currentItem.css("paddingRight")||0,10));
					}
				}
			};
		}

		//Createtheplaceholder
		that.placeholder=$(o.placeholder.element.call(that.element,that.currentItem));

		//Appenditaftertheactualcurrentitem
		that.currentItem.after(that.placeholder);

		//Updatethesizeoftheplaceholder(TODO:Logictofuzzy,seeline316/317)
		o.placeholder.update(that,that.placeholder);

	},

	_createTrPlaceholder:function(sourceTr,targetTr){
		varthat=this;

		sourceTr.children().each(function(){
			$("<td>&#160;</td>",that.document[0])
				.attr("colspan",$(this).attr("colspan")||1)
				.appendTo(targetTr);
		});
	},

	_contactContainers:function(event){
		vari,j,dist,itemWithLeastDistance,posProperty,sizeProperty,cur,nearBottom,
			floating,axis,
			innermostContainer=null,
			innermostIndex=null;

		//Getinnermostcontainerthatintersectswithitem
		for(i=this.containers.length-1;i>=0;i--){

			//Neverconsideracontainerthat'slocatedwithintheitemitself
			if($.contains(this.currentItem[0],this.containers[i].element[0])){
				continue;
			}

			if(this._intersectsWith(this.containers[i].containerCache)){

				//Ifwe'vealreadyfoundacontainerandit'smore"inner"thanthis,thencontinue
				if(innermostContainer&&
						$.contains(
							this.containers[i].element[0],
							innermostContainer.element[0])){
					continue;
				}

				innermostContainer=this.containers[i];
				innermostIndex=i;

			}else{

				//containerdoesn'tintersect.trigger"out"eventifnecessary
				if(this.containers[i].containerCache.over){
					this.containers[i]._trigger("out",event,this._uiHash(this));
					this.containers[i].containerCache.over=0;
				}
			}

		}

		//Ifnointersectingcontainersfound,return
		if(!innermostContainer){
			return;
		}

		//Movetheitemintothecontainerifit'snottherealready
		if(this.containers.length===1){
			if(!this.containers[innermostIndex].containerCache.over){
				this.containers[innermostIndex]._trigger("over",event,this._uiHash(this));
				this.containers[innermostIndex].containerCache.over=1;
			}
		}else{

			//Whenenteringanewcontainer,wewillfindtheitemwiththeleastdistanceand
			//appendouritemnearit
			dist=10000;
			itemWithLeastDistance=null;
			floating=innermostContainer.floating||this._isFloating(this.currentItem);
			posProperty=floating?"left":"top";
			sizeProperty=floating?"width":"height";
			axis=floating?"pageX":"pageY";

			for(j=this.items.length-1;j>=0;j--){
				if(!$.contains(
						this.containers[innermostIndex].element[0],this.items[j].item[0])
				){
					continue;
				}
				if(this.items[j].item[0]===this.currentItem[0]){
					continue;
				}

				cur=this.items[j].item.offset()[posProperty];
				nearBottom=false;
				if(event[axis]-cur>this.items[j][sizeProperty]/2){
					nearBottom=true;
				}

				if(Math.abs(event[axis]-cur)<dist){
					dist=Math.abs(event[axis]-cur);
					itemWithLeastDistance=this.items[j];
					this.direction=nearBottom?"up":"down";
				}
			}

			//CheckifdropOnEmptyisenabled
			if(!itemWithLeastDistance&&!this.options.dropOnEmpty){
				return;
			}

			if(this.currentContainer===this.containers[innermostIndex]){
				if(!this.currentContainer.containerCache.over){
					this.containers[innermostIndex]._trigger("over",event,this._uiHash());
					this.currentContainer.containerCache.over=1;
				}
				return;
			}

			itemWithLeastDistance?
				this._rearrange(event,itemWithLeastDistance,null,true):
				this._rearrange(event,null,this.containers[innermostIndex].element,true);
			this._trigger("change",event,this._uiHash());
			this.containers[innermostIndex]._trigger("change",event,this._uiHash(this));
			this.currentContainer=this.containers[innermostIndex];

			//Updatetheplaceholder
			this.options.placeholder.update(this.currentContainer,this.placeholder);

			this.containers[innermostIndex]._trigger("over",event,this._uiHash(this));
			this.containers[innermostIndex].containerCache.over=1;
		}

	},

	_createHelper:function(event){

		varo=this.options,
			helper=$.isFunction(o.helper)?
				$(o.helper.apply(this.element[0],[event,this.currentItem])):
				(o.helper==="clone"?this.currentItem.clone():this.currentItem);

		//AddthehelpertotheDOMifthatdidn'thappenalready
		if(!helper.parents("body").length){
			$(o.appendTo!=="parent"?
				o.appendTo:
				this.currentItem[0].parentNode)[0].appendChild(helper[0]);
		}

		if(helper[0]===this.currentItem[0]){
			this._storedCSS={
				width:this.currentItem[0].style.width,
				height:this.currentItem[0].style.height,
				position:this.currentItem.css("position"),
				top:this.currentItem.css("top"),
				left:this.currentItem.css("left")
			};
		}

		if(!helper[0].style.width||o.forceHelperSize){
			helper.width(this.currentItem.width());
		}
		if(!helper[0].style.height||o.forceHelperSize){
			helper.height(this.currentItem.height());
		}

		returnhelper;

	},

	_adjustOffsetFromHelper:function(obj){
		if(typeofobj==="string"){
			obj=obj.split("");
		}
		if($.isArray(obj)){
			obj={left:+obj[0],top:+obj[1]||0};
		}
		if("left"inobj){
			this.offset.click.left=obj.left+this.margins.left;
		}
		if("right"inobj){
			this.offset.click.left=this.helperProportions.width-obj.right+this.margins.left;
		}
		if("top"inobj){
			this.offset.click.top=obj.top+this.margins.top;
		}
		if("bottom"inobj){
			this.offset.click.top=this.helperProportions.height-obj.bottom+this.margins.top;
		}
	},

	_getParentOffset:function(){

		//GettheoffsetParentandcacheitsposition
		this.offsetParent=this.helper.offsetParent();
		varpo=this.offsetParent.offset();

		//Thisisaspecialcasewhereweneedtomodifyaoffsetcalculatedonstart,sincethe
		//followinghappened:
		//1.Thepositionofthehelperisabsolute,soit'spositioniscalculatedbasedonthe
		//nextpositionedparent
		//2.Theactualoffsetparentisachildofthescrollparent,andthescrollparentisn't
		//thedocument,whichmeansthatthescrollisincludedintheinitialcalculationofthe
		//offsetoftheparent,andneverrecalculatedupondrag
		if(this.cssPosition==="absolute"&&this.scrollParent[0]!==this.document[0]&&
				$.contains(this.scrollParent[0],this.offsetParent[0])){
			po.left+=this.scrollParent.scrollLeft();
			po.top+=this.scrollParent.scrollTop();
		}

		//Thisneedstobeactuallydoneforallbrowsers,sincepageX/pageYincludesthis
		//informationwithanuglyIEfix
		if(this.offsetParent[0]===this.document[0].body||
				(this.offsetParent[0].tagName&&
				this.offsetParent[0].tagName.toLowerCase()==="html"&&$.ui.ie)){
			po={top:0,left:0};
		}

		return{
			top:po.top+(parseInt(this.offsetParent.css("borderTopWidth"),10)||0),
			left:po.left+(parseInt(this.offsetParent.css("borderLeftWidth"),10)||0)
		};

	},

	_getRelativeOffset:function(){

		if(this.cssPosition==="relative"){
			varp=this.currentItem.position();
			return{
				top:p.top-(parseInt(this.helper.css("top"),10)||0)+
					this.scrollParent.scrollTop(),
				left:p.left-(parseInt(this.helper.css("left"),10)||0)+
					this.scrollParent.scrollLeft()
			};
		}else{
			return{top:0,left:0};
		}

	},

	_cacheMargins:function(){
		this.margins={
			left:(parseInt(this.currentItem.css("marginLeft"),10)||0),
			top:(parseInt(this.currentItem.css("marginTop"),10)||0)
		};
	},

	_cacheHelperProportions:function(){
		this.helperProportions={
			width:this.helper.outerWidth(),
			height:this.helper.outerHeight()
		};
	},

	_setContainment:function(){

		varce,co,over,
			o=this.options;
		if(o.containment==="parent"){
			o.containment=this.helper[0].parentNode;
		}
		if(o.containment==="document"||o.containment==="window"){
			this.containment=[
				0-this.offset.relative.left-this.offset.parent.left,
				0-this.offset.relative.top-this.offset.parent.top,
				o.containment==="document"?
					this.document.width():
					this.window.width()-this.helperProportions.width-this.margins.left,
				(o.containment==="document"?
					(this.document.height()||document.body.parentNode.scrollHeight):
					this.window.height()||this.document[0].body.parentNode.scrollHeight
				)-this.helperProportions.height-this.margins.top
			];
		}

		if(!(/^(document|window|parent)$/).test(o.containment)){
			ce=$(o.containment)[0];
			co=$(o.containment).offset();
			over=($(ce).css("overflow")!=="hidden");

			this.containment=[
				co.left+(parseInt($(ce).css("borderLeftWidth"),10)||0)+
					(parseInt($(ce).css("paddingLeft"),10)||0)-this.margins.left,
				co.top+(parseInt($(ce).css("borderTopWidth"),10)||0)+
					(parseInt($(ce).css("paddingTop"),10)||0)-this.margins.top,
				co.left+(over?Math.max(ce.scrollWidth,ce.offsetWidth):ce.offsetWidth)-
					(parseInt($(ce).css("borderLeftWidth"),10)||0)-
					(parseInt($(ce).css("paddingRight"),10)||0)-
					this.helperProportions.width-this.margins.left,
				co.top+(over?Math.max(ce.scrollHeight,ce.offsetHeight):ce.offsetHeight)-
					(parseInt($(ce).css("borderTopWidth"),10)||0)-
					(parseInt($(ce).css("paddingBottom"),10)||0)-
					this.helperProportions.height-this.margins.top
			];
		}

	},

	_convertPositionTo:function(d,pos){

		if(!pos){
			pos=this.position;
		}
		varmod=d==="absolute"?1:-1,
			scroll=this.cssPosition==="absolute"&&
				!(this.scrollParent[0]!==this.document[0]&&
				$.contains(this.scrollParent[0],this.offsetParent[0]))?
					this.offsetParent:
					this.scrollParent,
			scrollIsRootNode=(/(html|body)/i).test(scroll[0].tagName);

		return{
			top:(

				//Theabsolutemouseposition
				pos.top	+

				//Onlyforrelativepositionednodes:Relativeoffsetfromelementtooffsetparent
				this.offset.relative.top*mod+

				//TheoffsetParent'soffsetwithoutborders(offset+border)
				this.offset.parent.top*mod-
				((this.cssPosition==="fixed"?
					-this.scrollParent.scrollTop():
					(scrollIsRootNode?0:scroll.scrollTop()))*mod)
			),
			left:(

				//Theabsolutemouseposition
				pos.left+

				//Onlyforrelativepositionednodes:Relativeoffsetfromelementtooffsetparent
				this.offset.relative.left*mod+

				//TheoffsetParent'soffsetwithoutborders(offset+border)
				this.offset.parent.left*mod	-
				((this.cssPosition==="fixed"?
					-this.scrollParent.scrollLeft():scrollIsRootNode?0:
					scroll.scrollLeft())*mod)
			)
		};

	},

	_generatePosition:function(event){

		vartop,left,
			o=this.options,
			pageX=event.pageX,
			pageY=event.pageY,
			scroll=this.cssPosition==="absolute"&&
				!(this.scrollParent[0]!==this.document[0]&&
				$.contains(this.scrollParent[0],this.offsetParent[0]))?
					this.offsetParent:
					this.scrollParent,
				scrollIsRootNode=(/(html|body)/i).test(scroll[0].tagName);

		//Thisisanotherveryweirdspecialcasethatonlyhappensforrelativeelements:
		//1.Ifthecsspositionisrelative
		//2.andthescrollparentisthedocumentorsimilartotheoffsetparent
		//wehavetorefreshtherelativeoffsetduringthescrollsotherearenojumps
		if(this.cssPosition==="relative"&&!(this.scrollParent[0]!==this.document[0]&&
				this.scrollParent[0]!==this.offsetParent[0])){
			this.offset.relative=this._getRelativeOffset();
		}

		/*
		*-Positionconstraining-
		*Constrainthepositiontoamixofgrid,containment.
		*/

		if(this.originalPosition){//Ifwearenotdraggingyet,wewon'tcheckforoptions

			if(this.containment){
				if(event.pageX-this.offset.click.left<this.containment[0]){
					pageX=this.containment[0]+this.offset.click.left;
				}
				if(event.pageY-this.offset.click.top<this.containment[1]){
					pageY=this.containment[1]+this.offset.click.top;
				}
				if(event.pageX-this.offset.click.left>this.containment[2]){
					pageX=this.containment[2]+this.offset.click.left;
				}
				if(event.pageY-this.offset.click.top>this.containment[3]){
					pageY=this.containment[3]+this.offset.click.top;
				}
			}

			if(o.grid){
				top=this.originalPageY+Math.round((pageY-this.originalPageY)/
					o.grid[1])*o.grid[1];
				pageY=this.containment?
					((top-this.offset.click.top>=this.containment[1]&&
						top-this.offset.click.top<=this.containment[3])?
							top:
							((top-this.offset.click.top>=this.containment[1])?
								top-o.grid[1]:top+o.grid[1])):
								top;

				left=this.originalPageX+Math.round((pageX-this.originalPageX)/
					o.grid[0])*o.grid[0];
				pageX=this.containment?
					((left-this.offset.click.left>=this.containment[0]&&
						left-this.offset.click.left<=this.containment[2])?
							left:
							((left-this.offset.click.left>=this.containment[0])?
								left-o.grid[0]:left+o.grid[0])):
								left;
			}

		}

		return{
			top:(

				//Theabsolutemouseposition
				pageY-

				//Clickoffset(relativetotheelement)
				this.offset.click.top-

				//Onlyforrelativepositionednodes:Relativeoffsetfromelementtooffsetparent
				this.offset.relative.top-

				//TheoffsetParent'soffsetwithoutborders(offset+border)
				this.offset.parent.top+
				((this.cssPosition==="fixed"?
					-this.scrollParent.scrollTop():
					(scrollIsRootNode?0:scroll.scrollTop())))
			),
			left:(

				//Theabsolutemouseposition
				pageX-

				//Clickoffset(relativetotheelement)
				this.offset.click.left-

				//Onlyforrelativepositionednodes:Relativeoffsetfromelementtooffsetparent
				this.offset.relative.left-

				//TheoffsetParent'soffsetwithoutborders(offset+border)
				this.offset.parent.left+
				((this.cssPosition==="fixed"?
					-this.scrollParent.scrollLeft():
					scrollIsRootNode?0:scroll.scrollLeft()))
			)
		};

	},

	_rearrange:function(event,i,a,hardRefresh){

		a?a[0].appendChild(this.placeholder[0]):
			i.item[0].parentNode.insertBefore(this.placeholder[0],
				(this.direction==="down"?i.item[0]:i.item[0].nextSibling));

		//Variousthingsdoneheretoimprovetheperformance:
		//1.wecreateasetTimeout,thatcallsrefreshPositions
		//2.ontheinstance,wehaveacountervariable,thatget'shigheraftereveryappend
		//3.onthelocalscope,wecopythecountervariable,andcheckinthetimeout,
		//ifit'sstillthesame
		//4.thisletsonlythelastadditiontothetimeoutstackthrough
		this.counter=this.counter?++this.counter:1;
		varcounter=this.counter;

		this._delay(function(){
			if(counter===this.counter){

				//PrecomputeaftereachDOMinsertion,NOTonmousemove
				this.refreshPositions(!hardRefresh);
			}
		});

	},

	_clear:function(event,noPropagation){

		this.reverting=false;

		//Wedelayalleventsthathavetobetriggeredtoafterthepointwheretheplaceholder
		//hasbeenremovedandeverythingelsenormalizedagain
		vari,
			delayedTriggers=[];

		//WefirsthavetoupdatethedompositionoftheactualcurrentItem
		//Note:don'tdoitifthecurrentitemisalreadyremoved(byauser),oritgets
		//reappended(see#4088)
		if(!this._noFinalSort&&this.currentItem.parent().length){
			this.placeholder.before(this.currentItem);
		}
		this._noFinalSort=null;

		if(this.helper[0]===this.currentItem[0]){
			for(iinthis._storedCSS){
				if(this._storedCSS[i]==="auto"||this._storedCSS[i]==="static"){
					this._storedCSS[i]="";
				}
			}
			this.currentItem.css(this._storedCSS);
			this._removeClass(this.currentItem,"ui-sortable-helper");
		}else{
			this.currentItem.show();
		}

		if(this.fromOutside&&!noPropagation){
			delayedTriggers.push(function(event){
				this._trigger("receive",event,this._uiHash(this.fromOutside));
			});
		}
		if((this.fromOutside||
				this.domPosition.prev!==
				this.currentItem.prev().not(".ui-sortable-helper")[0]||
				this.domPosition.parent!==this.currentItem.parent()[0])&&!noPropagation){

			//TriggerupdatecallbackiftheDOMpositionhaschanged
			delayedTriggers.push(function(event){
				this._trigger("update",event,this._uiHash());
			});
		}

		//CheckiftheitemsContainerhasChangedandtriggerappropriate
		//events.
		if(this!==this.currentContainer){
			if(!noPropagation){
				delayedTriggers.push(function(event){
					this._trigger("remove",event,this._uiHash());
				});
				delayedTriggers.push((function(c){
					returnfunction(event){
						c._trigger("receive",event,this._uiHash(this));
					};
				}).call(this,this.currentContainer));
				delayedTriggers.push((function(c){
					returnfunction(event){
						c._trigger("update",event,this._uiHash(this));
					};
				}).call(this,this.currentContainer));
			}
		}

		//Posteventstocontainers
		functiondelayEvent(type,instance,container){
			returnfunction(event){
				container._trigger(type,event,instance._uiHash(instance));
			};
		}
		for(i=this.containers.length-1;i>=0;i--){
			if(!noPropagation){
				delayedTriggers.push(delayEvent("deactivate",this,this.containers[i]));
			}
			if(this.containers[i].containerCache.over){
				delayedTriggers.push(delayEvent("out",this,this.containers[i]));
				this.containers[i].containerCache.over=0;
			}
		}

		//Dowhatwasoriginallyinplugins
		if(this.storedCursor){
			this.document.find("body").css("cursor",this.storedCursor);
			this.storedStylesheet.remove();
		}
		if(this._storedOpacity){
			this.helper.css("opacity",this._storedOpacity);
		}
		if(this._storedZIndex){
			this.helper.css("zIndex",this._storedZIndex==="auto"?"":this._storedZIndex);
		}

		this.dragging=false;

		if(!noPropagation){
			this._trigger("beforeStop",event,this._uiHash());
		}

		//$(this.placeholder[0]).remove();wouldhavebeenthejQueryway-unfortunately,
		//itunbindsALLeventsfromtheoriginalnode!
		this.placeholder[0].parentNode.removeChild(this.placeholder[0]);

		if(!this.cancelHelperRemoval){
			if(this.helper[0]!==this.currentItem[0]){
				this.helper.remove();
			}
			this.helper=null;
		}

		if(!noPropagation){
			for(i=0;i<delayedTriggers.length;i++){

				//Triggeralldelayedevents
				delayedTriggers[i].call(this,event);
			}
			this._trigger("stop",event,this._uiHash());
		}

		this.fromOutside=false;
		return!this.cancelHelperRemoval;

	},

	_trigger:function(){
		if($.Widget.prototype._trigger.apply(this,arguments)===false){
			this.cancel();
		}
	},

	_uiHash:function(_inst){
		varinst=_inst||this;
		return{
			helper:inst.helper,
			placeholder:inst.placeholder||$([]),
			position:inst.position,
			originalPosition:inst.originalPosition,
			offset:inst.positionAbs,
			item:inst.currentItem,
			sender:_inst?_inst.element:null
		};
	}

});


/*!
 *jQueryUIMenu1.12.1
 *http://jqueryui.com
 *
 *CopyrightjQueryFoundationandothercontributors
 *ReleasedundertheMITlicense.
 *http://jquery.org/license
 */

//>>label:Menu
//>>group:Widgets
//>>description:Createsnestablemenus.
//>>docs:http://api.jqueryui.com/menu/
//>>demos:http://jqueryui.com/menu/
//>>css.structure:../../themes/base/core.css
//>>css.structure:../../themes/base/menu.css
//>>css.theme:../../themes/base/theme.css



varwidgetsMenu=$.widget("ui.menu",{
	version:"1.12.1",
	defaultElement:"<ul>",
	delay:300,
	options:{
		icons:{
			submenu:"ui-icon-caret-1-e"
		},
		items:">*",
		menus:"ul",
		position:{
			my:"lefttop",
			at:"righttop"
		},
		role:"menu",

		//Callbacks
		blur:null,
		focus:null,
		select:null
	},

	_create:function(){
		this.activeMenu=this.element;

		//Flagusedtopreventfiringoftheclickhandler
		//astheeventbubblesupthroughnestedmenus
		this.mouseHandled=false;
		this.element
			.uniqueId()
			.attr({
				role:this.options.role,
				tabIndex:0
			});

		this._addClass("ui-menu","ui-widgetui-widget-content");
		this._on({

			//Preventfocusfromstickingtolinksinsidemenuafterclicking
			//them(focusshouldalwaysstayonULduringnavigation).
			"mousedown.ui-menu-item":function(event){
				event.preventDefault();
			},
			"click.ui-menu-item":function(event){
				vartarget=$(event.target);
				varactive=$($.ui.safeActiveElement(this.document[0]));
				if(!this.mouseHandled&&target.not(".ui-state-disabled").length){
					this.select(event);

					//OnlysetthemouseHandledflagiftheeventwillbubble,see#9469.
					if(!event.isPropagationStopped()){
						this.mouseHandled=true;
					}

					//Opensubmenuonclick
					if(target.has(".ui-menu").length){
						this.expand(event);
					}elseif(!this.element.is(":focus")&&
							active.closest(".ui-menu").length){

						//Redirectfocustothemenu
						this.element.trigger("focus",[true]);

						//Iftheactiveitemisonthetoplevel,letitstayactive.
						//Otherwise,blurtheactiveitemsinceitisnolongervisible.
						if(this.active&&this.active.parents(".ui-menu").length===1){
							clearTimeout(this.timer);
						}
					}
				}
			},
			"mouseenter.ui-menu-item":function(event){

				//Ignoremouseeventswhiletypeaheadisactive,see#10458.
				//Preventsfocusingthewrongitemwhentypeaheadcausesascrollwhilethemouse
				//isoveraniteminthemenu
				if(this.previousFilter){
					return;
				}

				varactualTarget=$(event.target).closest(".ui-menu-item"),
					target=$(event.currentTarget);

				//Ignorebubbledeventsonparentitems,see#11641
				if(actualTarget[0]!==target[0]){
					return;
				}

				//Removeui-state-activeclassfromsiblingsofthenewlyfocusedmenuitem
				//toavoidajumpcausedbyadjacentelementsbothhavingaclasswithaborder
				this._removeClass(target.siblings().children(".ui-state-active"),
					null,"ui-state-active");
				this.focus(event,target);
			},
			mouseleave:"collapseAll",
			"mouseleave.ui-menu":"collapseAll",
			focus:function(event,keepActiveItem){

				//Ifthere'salreadyanactiveitem,keepitactive
				//Ifnot,activatethefirstitem
				varitem=this.active||this.element.find(this.options.items).eq(0);

				if(!keepActiveItem){
					this.focus(event,item);
				}
			},
			blur:function(event){
				this._delay(function(){
					varnotContained=!$.contains(
						this.element[0],
						$.ui.safeActiveElement(this.document[0])
					);
					if(notContained){
						this.collapseAll(event);
					}
				});
			},
			keydown:"_keydown"
		});

		this.refresh();

		//Clicksoutsideofamenucollapseanyopenmenus
		this._on(this.document,{
			click:function(event){
				if(this._closeOnDocumentClick(event)){
					this.collapseAll(event);
				}

				//ResetthemouseHandledflag
				this.mouseHandled=false;
			}
		});
	},

	_destroy:function(){
		varitems=this.element.find(".ui-menu-item")
				.removeAttr("rolearia-disabled"),
			submenus=items.children(".ui-menu-item-wrapper")
				.removeUniqueId()
				.removeAttr("tabIndexrolearia-haspopup");

		//Destroy(sub)menus
		this.element
			.removeAttr("aria-activedescendant")
			.find(".ui-menu").addBack()
				.removeAttr("rolearia-labelledbyaria-expandedaria-hiddenaria-disabled"+
					"tabIndex")
				.removeUniqueId()
				.show();

		submenus.children().each(function(){
			varelem=$(this);
			if(elem.data("ui-menu-submenu-caret")){
				elem.remove();
			}
		});
	},

	_keydown:function(event){
		varmatch,prev,character,skip,
			preventDefault=true;

		switch(event.keyCode){
		case$.ui.keyCode.PAGE_UP:
			this.previousPage(event);
			break;
		case$.ui.keyCode.PAGE_DOWN:
			this.nextPage(event);
			break;
		case$.ui.keyCode.HOME:
			this._move("first","first",event);
			break;
		case$.ui.keyCode.END:
			this._move("last","last",event);
			break;
		case$.ui.keyCode.UP:
			this.previous(event);
			break;
		case$.ui.keyCode.DOWN:
			this.next(event);
			break;
		case$.ui.keyCode.LEFT:
			this.collapse(event);
			break;
		case$.ui.keyCode.RIGHT:
			if(this.active&&!this.active.is(".ui-state-disabled")){
				this.expand(event);
			}
			break;
		case$.ui.keyCode.ENTER:
		case$.ui.keyCode.SPACE:
			this._activate(event);
			break;
		case$.ui.keyCode.ESCAPE:
			this.collapse(event);
			break;
		default:
			preventDefault=false;
			prev=this.previousFilter||"";
			skip=false;

			//Supportnumberpadvalues
			character=event.keyCode>=96&&event.keyCode<=105?
				(event.keyCode-96).toString():String.fromCharCode(event.keyCode);

			clearTimeout(this.filterTimer);

			if(character===prev){
				skip=true;
			}else{
				character=prev+character;
			}

			match=this._filterMenuItems(character);
			match=skip&&match.index(this.active.next())!==-1?
				this.active.nextAll(".ui-menu-item"):
				match;

			//Ifnomatchesonthecurrentfilter,resettothelastcharacterpressed
			//tomovedownthemenutothefirstitemthatstartswiththatcharacter
			if(!match.length){
				character=String.fromCharCode(event.keyCode);
				match=this._filterMenuItems(character);
			}

			if(match.length){
				this.focus(event,match);
				this.previousFilter=character;
				this.filterTimer=this._delay(function(){
					deletethis.previousFilter;
				},1000);
			}else{
				deletethis.previousFilter;
			}
		}

		if(preventDefault){
			event.preventDefault();
		}
	},

	_activate:function(event){
		if(this.active&&!this.active.is(".ui-state-disabled")){
			if(this.active.children("[aria-haspopup='true']").length){
				this.expand(event);
			}else{
				this.select(event);
			}
		}
	},

	refresh:function(){
		varmenus,items,newSubmenus,newItems,newWrappers,
			that=this,
			icon=this.options.icons.submenu,
			submenus=this.element.find(this.options.menus);

		this._toggleClass("ui-menu-icons",null,!!this.element.find(".ui-icon").length);

		//Initializenestedmenus
		newSubmenus=submenus.filter(":not(.ui-menu)")
			.hide()
			.attr({
				role:this.options.role,
				"aria-hidden":"true",
				"aria-expanded":"false"
			})
			.each(function(){
				varmenu=$(this),
					item=menu.prev(),
					submenuCaret=$("<span>").data("ui-menu-submenu-caret",true);

				that._addClass(submenuCaret,"ui-menu-icon","ui-icon"+icon);
				item
					.attr("aria-haspopup","true")
					.prepend(submenuCaret);
				menu.attr("aria-labelledby",item.attr("id"));
			});

		this._addClass(newSubmenus,"ui-menu","ui-widgetui-widget-contentui-front");

		menus=submenus.add(this.element);
		items=menus.find(this.options.items);

		//Initializemenu-itemscontainingspacesand/ordashesonlyasdividers
		items.not(".ui-menu-item").each(function(){
			varitem=$(this);
			if(that._isDivider(item)){
				that._addClass(item,"ui-menu-divider","ui-widget-content");
			}
		});

		//Don'trefreshlistitemsthatarealreadyadapted
		newItems=items.not(".ui-menu-item,.ui-menu-divider");
		newWrappers=newItems.children()
			.not(".ui-menu")
				.uniqueId()
				.attr({
					tabIndex:-1,
					role:this._itemRole()
				});
		this._addClass(newItems,"ui-menu-item")
			._addClass(newWrappers,"ui-menu-item-wrapper");

		//Addaria-disabledattributetoanydisabledmenuitem
		items.filter(".ui-state-disabled").attr("aria-disabled","true");

		//Iftheactiveitemhasbeenremoved,blurthemenu
		if(this.active&&!$.contains(this.element[0],this.active[0])){
			this.blur();
		}
	},

	_itemRole:function(){
		return{
			menu:"menuitem",
			listbox:"option"
		}[this.options.role];
	},

	_setOption:function(key,value){
		if(key==="icons"){
			varicons=this.element.find(".ui-menu-icon");
			this._removeClass(icons,null,this.options.icons.submenu)
				._addClass(icons,null,value.submenu);
		}
		this._super(key,value);
	},

	_setOptionDisabled:function(value){
		this._super(value);

		this.element.attr("aria-disabled",String(value));
		this._toggleClass(null,"ui-state-disabled",!!value);
	},

	focus:function(event,item){
		varnested,focused,activeParent;
		this.blur(event,event&&event.type==="focus");

		this._scrollIntoView(item);

		this.active=item.first();

		focused=this.active.children(".ui-menu-item-wrapper");
		this._addClass(focused,null,"ui-state-active");

		//Onlyupdatearia-activedescendantifthere'sarole
		//otherwiseweassumefocusismanagedelsewhere
		if(this.options.role){
			this.element.attr("aria-activedescendant",focused.attr("id"));
		}

		//Highlightactiveparentmenuitem,ifany
		activeParent=this.active
			.parent()
				.closest(".ui-menu-item")
					.children(".ui-menu-item-wrapper");
		this._addClass(activeParent,null,"ui-state-active");

		if(event&&event.type==="keydown"){
			this._close();
		}else{
			this.timer=this._delay(function(){
				this._close();
			},this.delay);
		}

		nested=item.children(".ui-menu");
		if(nested.length&&event&&(/^mouse/.test(event.type))){
			this._startOpening(nested);
		}
		this.activeMenu=item.parent();

		this._trigger("focus",event,{item:item});
	},

	_scrollIntoView:function(item){
		varborderTop,paddingTop,offset,scroll,elementHeight,itemHeight;
		if(this._hasScroll()){
			borderTop=parseFloat($.css(this.activeMenu[0],"borderTopWidth"))||0;
			paddingTop=parseFloat($.css(this.activeMenu[0],"paddingTop"))||0;
			offset=item.offset().top-this.activeMenu.offset().top-borderTop-paddingTop;
			scroll=this.activeMenu.scrollTop();
			elementHeight=this.activeMenu.height();
			itemHeight=item.outerHeight();

			if(offset<0){
				this.activeMenu.scrollTop(scroll+offset);
			}elseif(offset+itemHeight>elementHeight){
				this.activeMenu.scrollTop(scroll+offset-elementHeight+itemHeight);
			}
		}
	},

	blur:function(event,fromFocus){
		if(!fromFocus){
			clearTimeout(this.timer);
		}

		if(!this.active){
			return;
		}

		this._removeClass(this.active.children(".ui-menu-item-wrapper"),
			null,"ui-state-active");

		this._trigger("blur",event,{item:this.active});
		this.active=null;
	},

	_startOpening:function(submenu){
		clearTimeout(this.timer);

		//Don'topenifalreadyopenfixesaFirefoxbugthatcauseda.5pixel
		//shiftinthesubmenupositionwhenmousingoverthecareticon
		if(submenu.attr("aria-hidden")!=="true"){
			return;
		}

		this.timer=this._delay(function(){
			this._close();
			this._open(submenu);
		},this.delay);
	},

	_open:function(submenu){
		varposition=$.extend({
			of:this.active
		},this.options.position);

		clearTimeout(this.timer);
		this.element.find(".ui-menu").not(submenu.parents(".ui-menu"))
			.hide()
			.attr("aria-hidden","true");

		submenu
			.show()
			.removeAttr("aria-hidden")
			.attr("aria-expanded","true")
			.position(position);
	},

	collapseAll:function(event,all){
		clearTimeout(this.timer);
		this.timer=this._delay(function(){

			//Ifwewerepassedanevent,lookforthesubmenuthatcontainstheevent
			varcurrentMenu=all?this.element:
				$(event&&event.target).closest(this.element.find(".ui-menu"));

			//Ifwefoundnovalidsubmenuancestor,usethemainmenutocloseall
			//submenusanyway
			if(!currentMenu.length){
				currentMenu=this.element;
			}

			this._close(currentMenu);

			this.blur(event);

			//Workaroundactiveitemstayingactiveaftermenuisblurred
			this._removeClass(currentMenu.find(".ui-state-active"),null,"ui-state-active");

			this.activeMenu=currentMenu;
		},this.delay);
	},

	//Withnoarguments,closesthecurrentlyactivemenu-ifnothingisactive
	//itclosesallmenus. Ifpassedanargument,itwillsearchformenusBELOW
	_close:function(startMenu){
		if(!startMenu){
			startMenu=this.active?this.active.parent():this.element;
		}

		startMenu.find(".ui-menu")
			.hide()
			.attr("aria-hidden","true")
			.attr("aria-expanded","false");
	},

	_closeOnDocumentClick:function(event){
		return!$(event.target).closest(".ui-menu").length;
	},

	_isDivider:function(item){

		//Matchhyphen,emdash,endash
		return!/[^\-\u2014\u2013\s]/.test(item.text());
	},

	collapse:function(event){
		varnewItem=this.active&&
			this.active.parent().closest(".ui-menu-item",this.element);
		if(newItem&&newItem.length){
			this._close();
			this.focus(event,newItem);
		}
	},

	expand:function(event){
		varnewItem=this.active&&
			this.active
				.children(".ui-menu")
					.find(this.options.items)
						.first();

		if(newItem&&newItem.length){
			this._open(newItem.parent());

			//DelaysoFirefoxwillnothideactivedescendantchangeinexpandingsubmenufromAT
			this._delay(function(){
				this.focus(event,newItem);
			});
		}
	},

	next:function(event){
		this._move("next","first",event);
	},

	previous:function(event){
		this._move("prev","last",event);
	},

	isFirstItem:function(){
		returnthis.active&&!this.active.prevAll(".ui-menu-item").length;
	},

	isLastItem:function(){
		returnthis.active&&!this.active.nextAll(".ui-menu-item").length;
	},

	_move:function(direction,filter,event){
		varnext;
		if(this.active){
			if(direction==="first"||direction==="last"){
				next=this.active
					[direction==="first"?"prevAll":"nextAll"](".ui-menu-item")
					.eq(-1);
			}else{
				next=this.active
					[direction+"All"](".ui-menu-item")
					.eq(0);
			}
		}
		if(!next||!next.length||!this.active){
			next=this.activeMenu.find(this.options.items)[filter]();
		}

		this.focus(event,next);
	},

	nextPage:function(event){
		varitem,base,height;

		if(!this.active){
			this.next(event);
			return;
		}
		if(this.isLastItem()){
			return;
		}
		if(this._hasScroll()){
			base=this.active.offset().top;
			height=this.element.height();
			this.active.nextAll(".ui-menu-item").each(function(){
				item=$(this);
				returnitem.offset().top-base-height<0;
			});

			this.focus(event,item);
		}else{
			this.focus(event,this.activeMenu.find(this.options.items)
				[!this.active?"first":"last"]());
		}
	},

	previousPage:function(event){
		varitem,base,height;
		if(!this.active){
			this.next(event);
			return;
		}
		if(this.isFirstItem()){
			return;
		}
		if(this._hasScroll()){
			base=this.active.offset().top;
			height=this.element.height();
			this.active.prevAll(".ui-menu-item").each(function(){
				item=$(this);
				returnitem.offset().top-base+height>0;
			});

			this.focus(event,item);
		}else{
			this.focus(event,this.activeMenu.find(this.options.items).first());
		}
	},

	_hasScroll:function(){
		returnthis.element.outerHeight()<this.element.prop("scrollHeight");
	},

	select:function(event){

		//TODO:Itshouldneverbepossibletonothaveanactiveitematthis
		//point,butthetestsdon'ttriggermouseenterbeforeclick.
		this.active=this.active||$(event.target).closest(".ui-menu-item");
		varui={item:this.active};
		if(!this.active.has(".ui-menu").length){
			this.collapseAll(event,true);
		}
		this._trigger("select",event,ui);
	},

	_filterMenuItems:function(character){
		varescapedCharacter=character.replace(/[\-\[\]{}()*+?.,\\\^$|#\s]/g,"\\$&"),
			regex=newRegExp("^"+escapedCharacter,"i");

		returnthis.activeMenu
			.find(this.options.items)

				//Onlymatchonitems,notdividersorothercontent(#10571)
				.filter(".ui-menu-item")
					.filter(function(){
						returnregex.test(
							$.trim($(this).children(".ui-menu-item-wrapper").text()));
					});
	}
});


/*!
 *jQueryUIAutocomplete1.12.1
 *http://jqueryui.com
 *
 *CopyrightjQueryFoundationandothercontributors
 *ReleasedundertheMITlicense.
 *http://jquery.org/license
 */

//>>label:Autocomplete
//>>group:Widgets
//>>description:Listssuggestedwordsastheuseristyping.
//>>docs:http://api.jqueryui.com/autocomplete/
//>>demos:http://jqueryui.com/autocomplete/
//>>css.structure:../../themes/base/core.css
//>>css.structure:../../themes/base/autocomplete.css
//>>css.theme:../../themes/base/theme.css



$.widget("ui.autocomplete",{
	version:"1.12.1",
	defaultElement:"<input>",
	options:{
		appendTo:null,
		autoFocus:false,
		delay:300,
		minLength:1,
		position:{
			my:"lefttop",
			at:"leftbottom",
			collision:"none"
		},
		source:null,

		//Callbacks
		change:null,
		close:null,
		focus:null,
		open:null,
		response:null,
		search:null,
		select:null
	},

	requestIndex:0,
	pending:0,

	_create:function(){

		//Somebrowsersonlyrepeatkeydownevents,notkeypressevents,
		//soweusethesuppressKeyPressflagtodetermineifwe'vealready
		//handledthekeydownevent.#7269
		//Unfortunatelythecodefor&inkeypressisthesameastheuparrow,
		//soweusethesuppressKeyPressRepeatflagtoavoidhandlingkeypress
		//eventswhenweknowthekeydowneventwasusedtomodifythe
		//searchterm.#7799
		varsuppressKeyPress,suppressKeyPressRepeat,suppressInput,
			nodeName=this.element[0].nodeName.toLowerCase(),
			isTextarea=nodeName==="textarea",
			isInput=nodeName==="input";

		//Textareasarealwaysmulti-line
		//Inputsarealwayssingle-line,evenifinsideacontentEditableelement
		//IEalsotreatsinputsascontentEditable
		//Allotherelementtypesaredeterminedbywhetherornotthey'recontentEditable
		this.isMultiLine=isTextarea||!isInput&&this._isContentEditable(this.element);

		this.valueMethod=this.element[isTextarea||isInput?"val":"text"];
		this.isNewMenu=true;

		this._addClass("ui-autocomplete-input");
		this.element.attr("autocomplete","off");

		this._on(this.element,{
			keydown:function(event){
				if(this.element.prop("readOnly")){
					suppressKeyPress=true;
					suppressInput=true;
					suppressKeyPressRepeat=true;
					return;
				}

				suppressKeyPress=false;
				suppressInput=false;
				suppressKeyPressRepeat=false;
				varkeyCode=$.ui.keyCode;
				switch(event.keyCode){
				casekeyCode.PAGE_UP:
					suppressKeyPress=true;
					this._move("previousPage",event);
					break;
				casekeyCode.PAGE_DOWN:
					suppressKeyPress=true;
					this._move("nextPage",event);
					break;
				casekeyCode.UP:
					suppressKeyPress=true;
					this._keyEvent("previous",event);
					break;
				casekeyCode.DOWN:
					suppressKeyPress=true;
					this._keyEvent("next",event);
					break;
				casekeyCode.ENTER:

					//whenmenuisopenandhasfocus
					if(this.menu.active){

						//#6055-Operastillallowsthekeypresstooccur
						//whichcausesformstosubmit
						suppressKeyPress=true;
						event.preventDefault();
						this.menu.select(event);
					}
					break;
				casekeyCode.TAB:
					if(this.menu.active){
						this.menu.select(event);
					}
					break;
				casekeyCode.ESCAPE:
					if(this.menu.element.is(":visible")){
						if(!this.isMultiLine){
							this._value(this.term);
						}
						this.close(event);

						//Differentbrowsershavedifferentdefaultbehaviorforescape
						//Singlepresscanmeanundoorclear
						//DoublepressinIEmeansclearthewholeform
						event.preventDefault();
					}
					break;
				default:
					suppressKeyPressRepeat=true;

					//searchtimeoutshouldbetriggeredbeforetheinputvalueischanged
					this._searchTimeout(event);
					break;
				}
			},
			keypress:function(event){
				if(suppressKeyPress){
					suppressKeyPress=false;
					if(!this.isMultiLine||this.menu.element.is(":visible")){
						event.preventDefault();
					}
					return;
				}
				if(suppressKeyPressRepeat){
					return;
				}

				//ReplicatesomekeyhandlerstoallowthemtorepeatinFirefoxandOpera
				varkeyCode=$.ui.keyCode;
				switch(event.keyCode){
				casekeyCode.PAGE_UP:
					this._move("previousPage",event);
					break;
				casekeyCode.PAGE_DOWN:
					this._move("nextPage",event);
					break;
				casekeyCode.UP:
					this._keyEvent("previous",event);
					break;
				casekeyCode.DOWN:
					this._keyEvent("next",event);
					break;
				}
			},
			input:function(event){
				if(suppressInput){
					suppressInput=false;
					event.preventDefault();
					return;
				}
				this._searchTimeout(event);
			},
			focus:function(){
				this.selectedItem=null;
				this.previous=this._value();
			},
			blur:function(event){
				if(this.cancelBlur){
					deletethis.cancelBlur;
					return;
				}

				clearTimeout(this.searching);
				this.close(event);
				this._change(event);
			}
		});

		this._initSource();
		this.menu=$("<ul>")
			.appendTo(this._appendTo())
			.menu({

				//disableARIAsupport,theliveregiontakescareofthat
				role:null
			})
			.hide()
			.menu("instance");

		this._addClass(this.menu.element,"ui-autocomplete","ui-front");
		this._on(this.menu.element,{
			mousedown:function(event){

				//preventmovingfocusoutofthetextfield
				event.preventDefault();

				//IEdoesn'tpreventmovingfocusevenwithevent.preventDefault()
				//sowesetaflagtoknowwhenweshouldignoretheblurevent
				this.cancelBlur=true;
				this._delay(function(){
					deletethis.cancelBlur;

					//Support:IE8only
					//Rightclickingamenuitemorselectingtextfromthemenuitemswill
					//resultinfocusmovingoutoftheinput.However,we'vealreadyreceived
					//andignoredtheblureventbecauseofthecancelBlurflagsetabove.So
					//werestorefocustoensurethatthemenuclosesproperlybasedontheuser's
					//nextactions.
					if(this.element[0]!==$.ui.safeActiveElement(this.document[0])){
						this.element.trigger("focus");
					}
				});
			},
			menufocus:function(event,ui){
				varlabel,item;

				//support:Firefox
				//PreventaccidentalactivationofmenuitemsinFirefox(#7024#9118)
				if(this.isNewMenu){
					this.isNewMenu=false;
					if(event.originalEvent&&/^mouse/.test(event.originalEvent.type)){
						this.menu.blur();

						this.document.one("mousemove",function(){
							$(event.target).trigger(event.originalEvent);
						});

						return;
					}
				}

				item=ui.item.data("ui-autocomplete-item");
				if(false!==this._trigger("focus",event,{item:item})){

					//usevaluetomatchwhatwillendupintheinput,ifitwasakeyevent
					if(event.originalEvent&&/^key/.test(event.originalEvent.type)){
						this._value(item.value);
					}
				}

				//AnnouncethevalueintheliveRegion
				label=ui.item.attr("aria-label")||item.value;
				if(label&&$.trim(label).length){
					this.liveRegion.children().hide();
					$("<div>").text(label).appendTo(this.liveRegion);
				}
			},
			menuselect:function(event,ui){
				varitem=ui.item.data("ui-autocomplete-item"),
					previous=this.previous;

				//Onlytriggerwhenfocuswaslost(clickonmenu)
				if(this.element[0]!==$.ui.safeActiveElement(this.document[0])){
					this.element.trigger("focus");
					this.previous=previous;

					//#6109-IEtriggerstwofocuseventsandthesecond
					//isasynchronous,soweneedtoresettheprevious
					//termsynchronouslyandasynchronously:-(
					this._delay(function(){
						this.previous=previous;
						this.selectedItem=item;
					});
				}

				if(false!==this._trigger("select",event,{item:item})){
					this._value(item.value);
				}

				//resetthetermaftertheselectevent
				//thisallowscustomselecthandlingtoworkproperly
				this.term=this._value();

				this.close(event);
				this.selectedItem=item;
			}
		});

		this.liveRegion=$("<div>",{
			role:"status",
			"aria-live":"assertive",
			"aria-relevant":"additions"
		})
			.appendTo(this.document[0].body);

		this._addClass(this.liveRegion,null,"ui-helper-hidden-accessible");

		//Turningoffautocompletepreventsthebrowserfromrememberingthe
		//valuewhennavigatingthroughhistory,sowere-enableautocomplete
		//ifthepageisunloadedbeforethewidgetisdestroyed.#7790
		this._on(this.window,{
			beforeunload:function(){
				this.element.removeAttr("autocomplete");
			}
		});
	},

	_destroy:function(){
		clearTimeout(this.searching);
		this.element.removeAttr("autocomplete");
		this.menu.element.remove();
		this.liveRegion.remove();
	},

	_setOption:function(key,value){
		this._super(key,value);
		if(key==="source"){
			this._initSource();
		}
		if(key==="appendTo"){
			this.menu.element.appendTo(this._appendTo());
		}
		if(key==="disabled"&&value&&this.xhr){
			this.xhr.abort();
		}
	},

	_isEventTargetInWidget:function(event){
		varmenuElement=this.menu.element[0];

		returnevent.target===this.element[0]||
			event.target===menuElement||
			$.contains(menuElement,event.target);
	},

	_closeOnClickOutside:function(event){
		if(!this._isEventTargetInWidget(event)){
			this.close();
		}
	},

	_appendTo:function(){
		varelement=this.options.appendTo;

		if(element){
			element=element.jquery||element.nodeType?
				$(element):
				this.document.find(element).eq(0);
		}

		if(!element||!element[0]){
			element=this.element.closest(".ui-front,dialog");
		}

		if(!element.length){
			element=this.document[0].body;
		}

		returnelement;
	},

	_initSource:function(){
		vararray,url,
			that=this;
		if($.isArray(this.options.source)){
			array=this.options.source;
			this.source=function(request,response){
				response($.ui.autocomplete.filter(array,request.term));
			};
		}elseif(typeofthis.options.source==="string"){
			url=this.options.source;
			this.source=function(request,response){
				if(that.xhr){
					that.xhr.abort();
				}
				that.xhr=$.ajax({
					url:url,
					data:request,
					dataType:"json",
					success:function(data){
						response(data);
					},
					error:function(){
						response([]);
					}
				});
			};
		}else{
			this.source=this.options.source;
		}
	},

	_searchTimeout:function(event){
		clearTimeout(this.searching);
		this.searching=this._delay(function(){

			//Searchifthevaluehaschanged,oriftheuserretypesthesamevalue(see#7434)
			varequalValues=this.term===this._value(),
				menuVisible=this.menu.element.is(":visible"),
				modifierKey=event.altKey||event.ctrlKey||event.metaKey||event.shiftKey;

			if(!equalValues||(equalValues&&!menuVisible&&!modifierKey)){
				this.selectedItem=null;
				this.search(null,event);
			}
		},this.options.delay);
	},

	search:function(value,event){
		value=value!=null?value:this._value();

		//Alwayssavetheactualvalue,nottheonepassedasanargument
		this.term=this._value();

		if(value.length<this.options.minLength){
			returnthis.close(event);
		}

		if(this._trigger("search",event)===false){
			return;
		}

		returnthis._search(value);
	},

	_search:function(value){
		this.pending++;
		this._addClass("ui-autocomplete-loading");
		this.cancelSearch=false;

		this.source({term:value},this._response());
	},

	_response:function(){
		varindex=++this.requestIndex;

		return$.proxy(function(content){
			if(index===this.requestIndex){
				this.__response(content);
			}

			this.pending--;
			if(!this.pending){
				this._removeClass("ui-autocomplete-loading");
			}
		},this);
	},

	__response:function(content){
		if(content){
			content=this._normalize(content);
		}
		this._trigger("response",null,{content:content});
		if(!this.options.disabled&&content&&content.length&&!this.cancelSearch){
			this._suggest(content);
			this._trigger("open");
		}else{

			//use._close()insteadof.close()sowedon'tcancelfuturesearches
			this._close();
		}
	},

	close:function(event){
		this.cancelSearch=true;
		this._close(event);
	},

	_close:function(event){

		//Removethehandlerthatclosesthemenuonoutsideclicks
		this._off(this.document,"mousedown");

		if(this.menu.element.is(":visible")){
			this.menu.element.hide();
			this.menu.blur();
			this.isNewMenu=true;
			this._trigger("close",event);
		}
	},

	_change:function(event){
		if(this.previous!==this._value()){
			this._trigger("change",event,{item:this.selectedItem});
		}
	},

	_normalize:function(items){

		//assumeallitemshavetherightformatwhenthefirstitemiscomplete
		if(items.length&&items[0].label&&items[0].value){
			returnitems;
		}
		return$.map(items,function(item){
			if(typeofitem==="string"){
				return{
					label:item,
					value:item
				};
			}
			return$.extend({},item,{
				label:item.label||item.value,
				value:item.value||item.label
			});
		});
	},

	_suggest:function(items){
		varul=this.menu.element.empty();
		this._renderMenu(ul,items);
		this.isNewMenu=true;
		this.menu.refresh();

		//Sizeandpositionmenu
		ul.show();
		this._resizeMenu();
		ul.position($.extend({
			of:this.element
		},this.options.position));

		if(this.options.autoFocus){
			this.menu.next();
		}

		//Listenforinteractionsoutsideofthewidget(#6642)
		this._on(this.document,{
			mousedown:"_closeOnClickOutside"
		});
	},

	_resizeMenu:function(){
		varul=this.menu.element;
		ul.outerWidth(Math.max(

			//Firefoxwrapslongtext(possiblyaroundingbug)
			//soweadd1pxtoavoidthewrapping(#7513)
			ul.width("").outerWidth()+1,
			this.element.outerWidth()
		));
	},

	_renderMenu:function(ul,items){
		varthat=this;
		$.each(items,function(index,item){
			that._renderItemData(ul,item);
		});
	},

	_renderItemData:function(ul,item){
		returnthis._renderItem(ul,item).data("ui-autocomplete-item",item);
	},

	_renderItem:function(ul,item){
		return$("<li>")
			.append($("<div>").text(item.label))
			.appendTo(ul);
	},

	_move:function(direction,event){
		if(!this.menu.element.is(":visible")){
			this.search(null,event);
			return;
		}
		if(this.menu.isFirstItem()&&/^previous/.test(direction)||
				this.menu.isLastItem()&&/^next/.test(direction)){

			if(!this.isMultiLine){
				this._value(this.term);
			}

			this.menu.blur();
			return;
		}
		this.menu[direction](event);
	},

	widget:function(){
		returnthis.menu.element;
	},

	_value:function(){
		returnthis.valueMethod.apply(this.element,arguments);
	},

	_keyEvent:function(keyEvent,event){
		if(!this.isMultiLine||this.menu.element.is(":visible")){
			this._move(keyEvent,event);

			//Preventsmovingcursortobeginning/endofthetextfieldinsomebrowsers
			event.preventDefault();
		}
	},

	//Support:Chrome<=50
	//Weshouldbeabletojustusethis.element.prop("isContentEditable")
	//buthiddenelementsalwaysreportfalseinChrome.
	//https://code.google.com/p/chromium/issues/detail?id=313082
	_isContentEditable:function(element){
		if(!element.length){
			returnfalse;
		}

		vareditable=element.prop("contentEditable");

		if(editable==="inherit"){
		 returnthis._isContentEditable(element.parent());
		}

		returneditable==="true";
	}
});

$.extend($.ui.autocomplete,{
	escapeRegex:function(value){
		returnvalue.replace(/[\-\[\]{}()*+?.,\\\^$|#\s]/g,"\\$&");
	},
	filter:function(array,term){
		varmatcher=newRegExp($.ui.autocomplete.escapeRegex(term),"i");
		return$.grep(array,function(value){
			returnmatcher.test(value.label||value.value||value);
		});
	}
});

//Liveregionextension,addinga`messages`option
//NOTE:ThisisanexperimentalAPI.Wearestillinvestigating
//afullsolutionforstringmanipulationandinternationalization.
$.widget("ui.autocomplete",$.ui.autocomplete,{
	options:{
		messages:{
			noResults:"Nosearchresults.",
			results:function(amount){
				returnamount+(amount>1?"resultsare":"resultis")+
					"available,useupanddownarrowkeystonavigate.";
			}
		}
	},

	__response:function(content){
		varmessage;
		this._superApply(arguments);
		if(this.options.disabled||this.cancelSearch){
			return;
		}
		if(content&&content.length){
			message=this.options.messages.results(content.length);
		}else{
			message=this.options.messages.noResults;
		}
		this.liveRegion.children().hide();
		$("<div>").text(message).appendTo(this.liveRegion);
	}
});

varwidgetsAutocomplete=$.ui.autocomplete;


//jscs:disablemaximumLineLength
/*jscs:disablerequireCamelCaseOrUpperCaseIdentifiers*/
/*!
 *jQueryUIDatepicker1.12.1
 *http://jqueryui.com
 *
 *CopyrightjQueryFoundationandothercontributors
 *ReleasedundertheMITlicense.
 *http://jquery.org/license
 */

//>>label:Datepicker
//>>group:Widgets
//>>description:Displaysacalendarfromaninputorinlineforselectingdates.
//>>docs:http://api.jqueryui.com/datepicker/
//>>demos:http://jqueryui.com/datepicker/
//>>css.structure:../../themes/base/core.css
//>>css.structure:../../themes/base/datepicker.css
//>>css.theme:../../themes/base/theme.css



$.extend($.ui,{datepicker:{version:"1.12.1"}});

vardatepicker_instActive;

functiondatepicker_getZindex(elem){
	varposition,value;
	while(elem.length&&elem[0]!==document){

		//Ignorez-indexifpositionissettoavaluewherez-indexisignoredbythebrowser
		//Thismakesbehaviorofthisfunctionconsistentacrossbrowsers
		//WebKitalwaysreturnsautoiftheelementispositioned
		position=elem.css("position");
		if(position==="absolute"||position==="relative"||position==="fixed"){

			//IEreturns0whenzIndexisnotspecified
			//otherbrowsersreturnastring
			//weignorethecaseofnestedelementswithanexplicitvalueof0
			//<divstyle="z-index:-10;"><divstyle="z-index:0;"></div></div>
			value=parseInt(elem.css("zIndex"),10);
			if(!isNaN(value)&&value!==0){
				returnvalue;
			}
		}
		elem=elem.parent();
	}

	return0;
}
/*Datepickermanager.
   Usethesingletoninstanceofthisclass,$.datepicker,tointeractwiththedatepicker.
   Settingsfor(groupsof)datepickersaremaintainedinaninstanceobject,
   allowingmultipledifferentsettingsonthesamepage.*/

functionDatepicker(){
	this._curInst=null;//Thecurrentinstanceinuse
	this._keyEvent=false;//Ifthelasteventwasakeyevent
	this._disabledInputs=[];//Listofdatepickerinputsthathavebeendisabled
	this._datepickerShowing=false;//Trueifthepopuppickerisshowing,falseifnot
	this._inDialog=false;//Trueifshowingwithina"dialog",falseifnot
	this._mainDivId="ui-datepicker-div";//TheIDofthemaindatepickerdivision
	this._inlineClass="ui-datepicker-inline";//Thenameoftheinlinemarkerclass
	this._appendClass="ui-datepicker-append";//Thenameoftheappendmarkerclass
	this._triggerClass="ui-datepicker-trigger";//Thenameofthetriggermarkerclass
	this._dialogClass="ui-datepicker-dialog";//Thenameofthedialogmarkerclass
	this._disableClass="ui-datepicker-disabled";//Thenameofthedisabledcoveringmarkerclass
	this._unselectableClass="ui-datepicker-unselectable";//Thenameoftheunselectablecellmarkerclass
	this._currentClass="ui-datepicker-current-day";//Thenameofthecurrentdaymarkerclass
	this._dayOverClass="ui-datepicker-days-cell-over";//Thenameofthedayhovermarkerclass
	this.regional=[];//Availableregionalsettings,indexedbylanguagecode
	this.regional[""]={//Defaultregionalsettings
		closeText:"Done",//Displaytextforcloselink
		prevText:"Prev",//Displaytextforpreviousmonthlink
		nextText:"Next",//Displaytextfornextmonthlink
		currentText:"Today",//Displaytextforcurrentmonthlink
		monthNames:["January","February","March","April","May","June",
			"July","August","September","October","November","December"],//Namesofmonthsfordrop-downandformatting
		monthNamesShort:["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],//Forformatting
		dayNames:["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],//Forformatting
		dayNamesShort:["Sun","Mon","Tue","Wed","Thu","Fri","Sat"],//Forformatting
		dayNamesMin:["Su","Mo","Tu","We","Th","Fr","Sa"],//ColumnheadingsfordaysstartingatSunday
		weekHeader:"Wk",//Columnheaderforweekoftheyear
		dateFormat:"mm/dd/yy",//SeeformatoptionsonparseDate
		firstDay:0,//Thefirstdayoftheweek,Sun=0,Mon=1,...
		isRTL:false,//Trueifright-to-leftlanguage,falseifleft-to-right
		showMonthAfterYear:false,//Trueiftheyearselectprecedesmonth,falseformonththenyear
		yearSuffix:""//Additionaltexttoappendtotheyearinthemonthheaders
	};
	this._defaults={//Globaldefaultsforallthedatepickerinstances
		showOn:"focus",//"focus"forpopuponfocus,
			//"button"fortriggerbutton,or"both"foreither
		showAnim:"fadeIn",//NameofjQueryanimationforpopup
		showOptions:{},//Optionsforenhancedanimations
		defaultDate:null,//Usedwhenfieldisblank:actualdate,
			//+/-numberforoffsetfromtoday,nullfortoday
		appendText:"",//Displaytextfollowingtheinputbox,e.g.showingtheformat
		buttonText:"...",//Textfortriggerbutton
		buttonImage:"",//URLfortriggerbuttonimage
		buttonImageOnly:false,//Trueiftheimageappearsalone,falseifitappearsonabutton
		hideIfNoPrevNext:false,//Truetohidenext/previousmonthlinks
			//ifnotapplicable,falsetojustdisablethem
		navigationAsDateFormat:false,//Trueifdateformattingappliedtoprev/today/nextlinks
		gotoCurrent:false,//Trueiftodaylinkgoesbacktocurrentselectioninstead
		changeMonth:false,//Trueifmonthcanbeselecteddirectly,falseifonlyprev/next
		changeYear:false,//Trueifyearcanbeselecteddirectly,falseifonlyprev/next
		yearRange:"c-10:c+10",//Rangeofyearstodisplayindrop-down,
			//eitherrelativetotoday'syear(-nn:+nn),relativetocurrentlydisplayedyear
			//(c-nn:c+nn),absolute(nnnn:nnnn),oracombinationoftheabove(nnnn:-n)
		showOtherMonths:false,//Truetoshowdatesinothermonths,falsetoleaveblank
		selectOtherMonths:false,//Truetoallowselectionofdatesinothermonths,falseforunselectable
		showWeek:false,//Truetoshowweekoftheyear,falsetonotshowit
		calculateWeek:this.iso8601Week,//Howtocalculatetheweekoftheyear,
			//takesaDateandreturnsthenumberoftheweekforit
		shortYearCutoff:"+10",//Shortyearvalues<thisareinthecurrentcentury,
			//>thisareinthepreviouscentury,
			//stringvaluestartingwith"+"forcurrentyear+value
		minDate:null,//Theearliestselectabledate,ornullfornolimit
		maxDate:null,//Thelatestselectabledate,ornullfornolimit
		duration:"fast",//Durationofdisplay/closure
		beforeShowDay:null,//Functionthattakesadateandreturnsanarraywith
			//[0]=trueifselectable,falseifnot,[1]=customCSSclassname(s)or"",
			//[2]=celltitle(optional),e.g.$.datepicker.noWeekends
		beforeShow:null,//Functionthattakesaninputfieldand
			//returnsasetofcustomsettingsforthedatepicker
		onSelect:null,//Defineacallbackfunctionwhenadateisselected
		onChangeMonthYear:null,//Defineacallbackfunctionwhenthemonthoryearischanged
		onClose:null,//Defineacallbackfunctionwhenthedatepickerisclosed
		numberOfMonths:1,//Numberofmonthstoshowatatime
		showCurrentAtPos:0,//Thepositioninmultipemonthsatwhichtoshowthecurrentmonth(startingat0)
		stepMonths:1,//Numberofmonthstostepback/forward
		stepBigMonths:12,//Numberofmonthstostepback/forwardforthebiglinks
		altField:"",//Selectorforanalternatefieldtostoreselecteddatesinto
		altFormat:"",//Thedateformattouseforthealternatefield
		constrainInput:true,//Theinputisconstrainedbythecurrentdateformat
		showButtonPanel:false,//Truetoshowbuttonpanel,falsetonotshowit
		autoSize:false,//Truetosizetheinputforthedateformat,falsetoleaveasis
		disabled:false//Theinitialdisabledstate
	};
	$.extend(this._defaults,this.regional[""]);
	this.regional.en=$.extend(true,{},this.regional[""]);
	this.regional["en-US"]=$.extend(true,{},this.regional.en);
	this.dpDiv=datepicker_bindHover($("<divid='"+this._mainDivId+"'class='ui-datepickerui-widgetui-widget-contentui-helper-clearfixui-corner-all'></div>"));
}

$.extend(Datepicker.prototype,{
	/*Classnameaddedtoelementstoindicatealreadyconfiguredwithadatepicker.*/
	markerClassName:"hasDatepicker",

	//Keeptrackofthemaximumnumberofrowsdisplayed(see#7043)
	maxRows:4,

	//TODOrenameto"widget"whenswitchingtowidgetfactory
	_widgetDatepicker:function(){
		returnthis.dpDiv;
	},

	/*Overridethedefaultsettingsforallinstancesofthedatepicker.
	*@param settings object-thenewsettingstouseasdefaults(anonymousobject)
	*@returnthemanagerobject
	*/
	setDefaults:function(settings){
		datepicker_extendRemove(this._defaults,settings||{});
		returnthis;
	},

	/*AttachthedatepickertoajQueryselection.
	*@param target	element-thetargetinputfieldordivisionorspan
	*@param settings object-thenewsettingstouseforthisdatepickerinstance(anonymous)
	*/
	_attachDatepicker:function(target,settings){
		varnodeName,inline,inst;
		nodeName=target.nodeName.toLowerCase();
		inline=(nodeName==="div"||nodeName==="span");
		if(!target.id){
			this.uuid+=1;
			target.id="dp"+this.uuid;
		}
		inst=this._newInst($(target),inline);
		inst.settings=$.extend({},settings||{});
		if(nodeName==="input"){
			this._connectDatepicker(target,inst);
		}elseif(inline){
			this._inlineDatepicker(target,inst);
		}
	},

	/*Createanewinstanceobject.*/
	_newInst:function(target,inline){
		varid=target[0].id.replace(/([^A-Za-z0-9_\-])/g,"\\\\$1");//escapejQuerymetachars
		return{id:id,input:target,//associatedtarget
			selectedDay:0,selectedMonth:0,selectedYear:0,//currentselection
			drawMonth:0,drawYear:0,//monthbeingdrawn
			inline:inline,//isdatepickerinlineornot
			dpDiv:(!inline?this.dpDiv://presentationdiv
			datepicker_bindHover($("<divclass='"+this._inlineClass+"ui-datepickerui-widgetui-widget-contentui-helper-clearfixui-corner-all'></div>")))};
	},

	/*Attachthedatepickertoaninputfield.*/
	_connectDatepicker:function(target,inst){
		varinput=$(target);
		inst.append=$([]);
		inst.trigger=$([]);
		if(input.hasClass(this.markerClassName)){
			return;
		}
		this._attachments(input,inst);
		input.addClass(this.markerClassName).on("keydown",this._doKeyDown).
			on("keypress",this._doKeyPress).on("keyup",this._doKeyUp);
		this._autoSize(inst);
		$.data(target,"datepicker",inst);

		//Ifdisabledoptionistrue,disablethedatepickeronceithasbeenattachedtotheinput(seeticket#5665)
		if(inst.settings.disabled){
			this._disableDatepicker(target);
		}
	},

	/*Makeattachmentsbasedonsettings.*/
	_attachments:function(input,inst){
		varshowOn,buttonText,buttonImage,
			appendText=this._get(inst,"appendText"),
			isRTL=this._get(inst,"isRTL");

		if(inst.append){
			inst.append.remove();
		}
		if(appendText){
			inst.append=$("<spanclass='"+this._appendClass+"'>"+appendText+"</span>");
			input[isRTL?"before":"after"](inst.append);
		}

		input.off("focus",this._showDatepicker);

		if(inst.trigger){
			inst.trigger.remove();
		}

		showOn=this._get(inst,"showOn");
		if(showOn==="focus"||showOn==="both"){//pop-updatepickerwheninthemarkedfield
			input.on("focus",this._showDatepicker);
		}
		if(showOn==="button"||showOn==="both"){//pop-updatepickerwhenbuttonclicked
			buttonText=this._get(inst,"buttonText");
			buttonImage=this._get(inst,"buttonImage");
			inst.trigger=$(this._get(inst,"buttonImageOnly")?
				$("<img/>").addClass(this._triggerClass).
					attr({src:buttonImage,alt:buttonText,title:buttonText}):
				$("<buttontype='button'></button>").addClass(this._triggerClass).
					html(!buttonImage?buttonText:$("<img/>").attr(
					{src:buttonImage,alt:buttonText,title:buttonText})));
			input[isRTL?"before":"after"](inst.trigger);
			inst.trigger.on("click",function(){
				if($.datepicker._datepickerShowing&&$.datepicker._lastInput===input[0]){
					$.datepicker._hideDatepicker();
				}elseif($.datepicker._datepickerShowing&&$.datepicker._lastInput!==input[0]){
					$.datepicker._hideDatepicker();
					$.datepicker._showDatepicker(input[0]);
				}else{
					$.datepicker._showDatepicker(input[0]);
				}
				returnfalse;
			});
		}
	},

	/*Applythemaximumlengthforthedateformat.*/
	_autoSize:function(inst){
		if(this._get(inst,"autoSize")&&!inst.inline){
			varfindMax,max,maxI,i,
				date=newDate(2009,12-1,20),//Ensuredoubledigits
				dateFormat=this._get(inst,"dateFormat");

			if(dateFormat.match(/[DM]/)){
				findMax=function(names){
					max=0;
					maxI=0;
					for(i=0;i<names.length;i++){
						if(names[i].length>max){
							max=names[i].length;
							maxI=i;
						}
					}
					returnmaxI;
				};
				date.setMonth(findMax(this._get(inst,(dateFormat.match(/MM/)?
					"monthNames":"monthNamesShort"))));
				date.setDate(findMax(this._get(inst,(dateFormat.match(/DD/)?
					"dayNames":"dayNamesShort")))+20-date.getDay());
			}
			inst.input.attr("size",this._formatDate(inst,date).length);
		}
	},

	/*Attachaninlinedatepickertoadiv.*/
	_inlineDatepicker:function(target,inst){
		vardivSpan=$(target);
		if(divSpan.hasClass(this.markerClassName)){
			return;
		}
		divSpan.addClass(this.markerClassName).append(inst.dpDiv);
		$.data(target,"datepicker",inst);
		this._setDate(inst,this._getDefaultDate(inst),true);
		this._updateDatepicker(inst);
		this._updateAlternate(inst);

		//Ifdisabledoptionistrue,disablethedatepickerbeforeshowingit(seeticket#5665)
		if(inst.settings.disabled){
			this._disableDatepicker(target);
		}

		//Setdisplay:blockinplaceofinst.dpDiv.show()whichwon'tworkondisconnectedelements
		//http://bugs.jqueryui.com/ticket/7552-ADatepickercreatedonadetacheddivhaszeroheight
		inst.dpDiv.css("display","block");
	},

	/*Pop-upthedatepickerina"dialog"box.
	*@param inputelement-ignored
	*@param date	stringorDate-theinitialdatetodisplay
	*@param onSelect function-thefunctiontocallwhenadateisselected
	*@param settings object-updatethedialogdatepickerinstance'ssettings(anonymousobject)
	*@param posint[2]-coordinatesforthedialog'spositionwithinthescreenor
	*					event-withx/ycoordinatesor
	*					leaveemptyfordefault(screencentre)
	*@returnthemanagerobject
	*/
	_dialogDatepicker:function(input,date,onSelect,settings,pos){
		varid,browserWidth,browserHeight,scrollX,scrollY,
			inst=this._dialogInst;//internalinstance

		if(!inst){
			this.uuid+=1;
			id="dp"+this.uuid;
			this._dialogInput=$("<inputtype='text'id='"+id+
				"'style='position:absolute;top:-100px;width:0px;'/>");
			this._dialogInput.on("keydown",this._doKeyDown);
			$("body").append(this._dialogInput);
			inst=this._dialogInst=this._newInst(this._dialogInput,false);
			inst.settings={};
			$.data(this._dialogInput[0],"datepicker",inst);
		}
		datepicker_extendRemove(inst.settings,settings||{});
		date=(date&&date.constructor===Date?this._formatDate(inst,date):date);
		this._dialogInput.val(date);

		this._pos=(pos?(pos.length?pos:[pos.pageX,pos.pageY]):null);
		if(!this._pos){
			browserWidth=document.documentElement.clientWidth;
			browserHeight=document.documentElement.clientHeight;
			scrollX=document.documentElement.scrollLeft||document.body.scrollLeft;
			scrollY=document.documentElement.scrollTop||document.body.scrollTop;
			this._pos=//shoulduseactualwidth/heightbelow
				[(browserWidth/2)-100+scrollX,(browserHeight/2)-150+scrollY];
		}

		//Moveinputonscreenforfocus,buthiddenbehinddialog
		this._dialogInput.css("left",(this._pos[0]+20)+"px").css("top",this._pos[1]+"px");
		inst.settings.onSelect=onSelect;
		this._inDialog=true;
		this.dpDiv.addClass(this._dialogClass);
		this._showDatepicker(this._dialogInput[0]);
		if($.blockUI){
			$.blockUI(this.dpDiv);
		}
		$.data(this._dialogInput[0],"datepicker",inst);
		returnthis;
	},

	/*Detachadatepickerfromitscontrol.
	*@param target	element-thetargetinputfieldordivisionorspan
	*/
	_destroyDatepicker:function(target){
		varnodeName,
			$target=$(target),
			inst=$.data(target,"datepicker");

		if(!$target.hasClass(this.markerClassName)){
			return;
		}

		nodeName=target.nodeName.toLowerCase();
		$.removeData(target,"datepicker");
		if(nodeName==="input"){
			inst.append.remove();
			inst.trigger.remove();
			$target.removeClass(this.markerClassName).
				off("focus",this._showDatepicker).
				off("keydown",this._doKeyDown).
				off("keypress",this._doKeyPress).
				off("keyup",this._doKeyUp);
		}elseif(nodeName==="div"||nodeName==="span"){
			$target.removeClass(this.markerClassName).empty();
		}

		if(datepicker_instActive===inst){
			datepicker_instActive=null;
		}
	},

	/*EnablethedatepickertoajQueryselection.
	*@param target	element-thetargetinputfieldordivisionorspan
	*/
	_enableDatepicker:function(target){
		varnodeName,inline,
			$target=$(target),
			inst=$.data(target,"datepicker");

		if(!$target.hasClass(this.markerClassName)){
			return;
		}

		nodeName=target.nodeName.toLowerCase();
		if(nodeName==="input"){
			target.disabled=false;
			inst.trigger.filter("button").
				each(function(){this.disabled=false;}).end().
				filter("img").css({opacity:"1.0",cursor:""});
		}elseif(nodeName==="div"||nodeName==="span"){
			inline=$target.children("."+this._inlineClass);
			inline.children().removeClass("ui-state-disabled");
			inline.find("select.ui-datepicker-month,select.ui-datepicker-year").
				prop("disabled",false);
		}
		this._disabledInputs=$.map(this._disabledInputs,
			function(value){return(value===target?null:value);});//deleteentry
	},

	/*DisablethedatepickertoajQueryselection.
	*@param target	element-thetargetinputfieldordivisionorspan
	*/
	_disableDatepicker:function(target){
		varnodeName,inline,
			$target=$(target),
			inst=$.data(target,"datepicker");

		if(!$target.hasClass(this.markerClassName)){
			return;
		}

		nodeName=target.nodeName.toLowerCase();
		if(nodeName==="input"){
			target.disabled=true;
			inst.trigger.filter("button").
				each(function(){this.disabled=true;}).end().
				filter("img").css({opacity:"0.5",cursor:"default"});
		}elseif(nodeName==="div"||nodeName==="span"){
			inline=$target.children("."+this._inlineClass);
			inline.children().addClass("ui-state-disabled");
			inline.find("select.ui-datepicker-month,select.ui-datepicker-year").
				prop("disabled",true);
		}
		this._disabledInputs=$.map(this._disabledInputs,
			function(value){return(value===target?null:value);});//deleteentry
		this._disabledInputs[this._disabledInputs.length]=target;
	},

	/*IsthefirstfieldinajQuerycollectiondisabledasadatepicker?
	*@param target	element-thetargetinputfieldordivisionorspan
	*@returnboolean-trueifdisabled,falseifenabled
	*/
	_isDisabledDatepicker:function(target){
		if(!target){
			returnfalse;
		}
		for(vari=0;i<this._disabledInputs.length;i++){
			if(this._disabledInputs[i]===target){
				returntrue;
			}
		}
		returnfalse;
	},

	/*Retrievetheinstancedataforthetargetcontrol.
	*@param target element-thetargetinputfieldordivisionorspan
	*@return object-theassociatedinstancedata
	*@throws errorifajQueryproblemgettingdata
	*/
	_getInst:function(target){
		try{
			return$.data(target,"datepicker");
		}
		catch(err){
			throw"Missinginstancedataforthisdatepicker";
		}
	},

	/*Updateorretrievethesettingsforadatepickerattachedtoaninputfieldordivision.
	*@param target element-thetargetinputfieldordivisionorspan
	*@param name	object-thenewsettingstoupdateor
	*				string-thenameofthesettingtochangeorretrieve,
	*				whenretrievingalso"all"forallinstancesettingsor
	*				"defaults"forallglobaldefaults
	*@param value  any-thenewvalueforthesetting
	*				(omitifaboveisanobjectortoretrieveavalue)
	*/
	_optionDatepicker:function(target,name,value){
		varsettings,date,minDate,maxDate,
			inst=this._getInst(target);

		if(arguments.length===2&&typeofname==="string"){
			return(name==="defaults"?$.extend({},$.datepicker._defaults):
				(inst?(name==="all"?$.extend({},inst.settings):
				this._get(inst,name)):null));
		}

		settings=name||{};
		if(typeofname==="string"){
			settings={};
			settings[name]=value;
		}

		if(inst){
			if(this._curInst===inst){
				this._hideDatepicker();
			}

			date=this._getDateDatepicker(target,true);
			minDate=this._getMinMaxDate(inst,"min");
			maxDate=this._getMinMaxDate(inst,"max");
			datepicker_extendRemove(inst.settings,settings);

			//reformattheoldminDate/maxDatevaluesifdateFormatchangesandanewminDate/maxDateisn'tprovided
			if(minDate!==null&&settings.dateFormat!==undefined&&settings.minDate===undefined){
				inst.settings.minDate=this._formatDate(inst,minDate);
			}
			if(maxDate!==null&&settings.dateFormat!==undefined&&settings.maxDate===undefined){
				inst.settings.maxDate=this._formatDate(inst,maxDate);
			}
			if("disabled"insettings){
				if(settings.disabled){
					this._disableDatepicker(target);
				}else{
					this._enableDatepicker(target);
				}
			}
			this._attachments($(target),inst);
			this._autoSize(inst);
			this._setDate(inst,date);
			this._updateAlternate(inst);
			this._updateDatepicker(inst);
		}
	},

	//Changemethoddeprecated
	_changeDatepicker:function(target,name,value){
		this._optionDatepicker(target,name,value);
	},

	/*Redrawthedatepickerattachedtoaninputfieldordivision.
	*@param target element-thetargetinputfieldordivisionorspan
	*/
	_refreshDatepicker:function(target){
		varinst=this._getInst(target);
		if(inst){
			this._updateDatepicker(inst);
		}
	},

	/*SetthedatesforajQueryselection.
	*@param targetelement-thetargetinputfieldordivisionorspan
	*@param date	Date-thenewdate
	*/
	_setDateDatepicker:function(target,date){
		varinst=this._getInst(target);
		if(inst){
			this._setDate(inst,date);
			this._updateDatepicker(inst);
			this._updateAlternate(inst);
		}
	},

	/*Getthedate(s)forthefirstentryinajQueryselection.
	*@param targetelement-thetargetinputfieldordivisionorspan
	*@param noDefaultboolean-trueifnodefaultdateistobeused
	*@returnDate-thecurrentdate
	*/
	_getDateDatepicker:function(target,noDefault){
		varinst=this._getInst(target);
		if(inst&&!inst.inline){
			this._setDateFromField(inst,noDefault);
		}
		return(inst?this._getDate(inst):null);
	},

	/*Handlekeystrokes.*/
	_doKeyDown:function(event){
		varonSelect,dateStr,sel,
			inst=$.datepicker._getInst(event.target),
			handled=true,
			isRTL=inst.dpDiv.is(".ui-datepicker-rtl");

		inst._keyEvent=true;
		if($.datepicker._datepickerShowing){
			switch(event.keyCode){
				case9:$.datepicker._hideDatepicker();
						handled=false;
						break;//hideontabout
				case13:sel=$("td."+$.datepicker._dayOverClass+":not(."+
									$.datepicker._currentClass+")",inst.dpDiv);
						if(sel[0]){
							$.datepicker._selectDay(event.target,inst.selectedMonth,inst.selectedYear,sel[0]);
						}

						onSelect=$.datepicker._get(inst,"onSelect");
						if(onSelect){
							dateStr=$.datepicker._formatDate(inst);

							//Triggercustomcallback
							onSelect.apply((inst.input?inst.input[0]:null),[dateStr,inst]);
						}else{
							$.datepicker._hideDatepicker();
						}

						returnfalse;//don'tsubmittheform
				case27:$.datepicker._hideDatepicker();
						break;//hideonescape
				case33:$.datepicker._adjustDate(event.target,(event.ctrlKey?
							-$.datepicker._get(inst,"stepBigMonths"):
							-$.datepicker._get(inst,"stepMonths")),"M");
						break;//previousmonth/yearonpageup/+ctrl
				case34:$.datepicker._adjustDate(event.target,(event.ctrlKey?
							+$.datepicker._get(inst,"stepBigMonths"):
							+$.datepicker._get(inst,"stepMonths")),"M");
						break;//nextmonth/yearonpagedown/+ctrl
				case35:if(event.ctrlKey||event.metaKey){
							$.datepicker._clearDate(event.target);
						}
						handled=event.ctrlKey||event.metaKey;
						break;//clearonctrlorcommand+end
				case36:if(event.ctrlKey||event.metaKey){
							$.datepicker._gotoToday(event.target);
						}
						handled=event.ctrlKey||event.metaKey;
						break;//currentonctrlorcommand+home
				case37:if(event.ctrlKey||event.metaKey){
							$.datepicker._adjustDate(event.target,(isRTL?+1:-1),"D");
						}
						handled=event.ctrlKey||event.metaKey;

						//-1dayonctrlorcommand+left
						if(event.originalEvent.altKey){
							$.datepicker._adjustDate(event.target,(event.ctrlKey?
								-$.datepicker._get(inst,"stepBigMonths"):
								-$.datepicker._get(inst,"stepMonths")),"M");
						}

						//nextmonth/yearonalt+leftonMac
						break;
				case38:if(event.ctrlKey||event.metaKey){
							$.datepicker._adjustDate(event.target,-7,"D");
						}
						handled=event.ctrlKey||event.metaKey;
						break;//-1weekonctrlorcommand+up
				case39:if(event.ctrlKey||event.metaKey){
							$.datepicker._adjustDate(event.target,(isRTL?-1:+1),"D");
						}
						handled=event.ctrlKey||event.metaKey;

						//+1dayonctrlorcommand+right
						if(event.originalEvent.altKey){
							$.datepicker._adjustDate(event.target,(event.ctrlKey?
								+$.datepicker._get(inst,"stepBigMonths"):
								+$.datepicker._get(inst,"stepMonths")),"M");
						}

						//nextmonth/yearonalt+right
						break;
				case40:if(event.ctrlKey||event.metaKey){
							$.datepicker._adjustDate(event.target,+7,"D");
						}
						handled=event.ctrlKey||event.metaKey;
						break;//+1weekonctrlorcommand+down
				default:handled=false;
			}
		}elseif(event.keyCode===36&&event.ctrlKey){//displaythedatepickeronctrl+home
			$.datepicker._showDatepicker(this);
		}else{
			handled=false;
		}

		if(handled){
			event.preventDefault();
			event.stopPropagation();
		}
	},

	/*Filterenteredcharacters-basedondateformat.*/
	_doKeyPress:function(event){
		varchars,chr,
			inst=$.datepicker._getInst(event.target);

		if($.datepicker._get(inst,"constrainInput")){
			chars=$.datepicker._possibleChars($.datepicker._get(inst,"dateFormat"));
			chr=String.fromCharCode(event.charCode==null?event.keyCode:event.charCode);
			returnevent.ctrlKey||event.metaKey||(chr<""||!chars||chars.indexOf(chr)>-1);
		}
	},

	/*Synchronisemanualentryandfield/alternatefield.*/
	_doKeyUp:function(event){
		vardate,
			inst=$.datepicker._getInst(event.target);

		if(inst.input.val()!==inst.lastVal){
			try{
				date=$.datepicker.parseDate($.datepicker._get(inst,"dateFormat"),
					(inst.input?inst.input.val():null),
					$.datepicker._getFormatConfig(inst));

				if(date){//onlyifvalid
					$.datepicker._setDateFromField(inst);
					$.datepicker._updateAlternate(inst);
					$.datepicker._updateDatepicker(inst);
				}
			}
			catch(err){
			}
		}
		returntrue;
	},

	/*Pop-upthedatepickerforagiveninputfield.
	*IffalsereturnedfrombeforeShoweventhandlerdonotshow.
	*@param input element-theinputfieldattachedtothedatepickeror
	*					event-iftriggeredbyfocus
	*/
	_showDatepicker:function(input){
		input=input.target||input;
		if(input.nodeName.toLowerCase()!=="input"){//findfrombutton/imagetrigger
			input=$("input",input.parentNode)[0];
		}

		if($.datepicker._isDisabledDatepicker(input)||$.datepicker._lastInput===input){//alreadyhere
			return;
		}

		varinst,beforeShow,beforeShowSettings,isFixed,
			offset,showAnim,duration;

		inst=$.datepicker._getInst(input);
		if($.datepicker._curInst&&$.datepicker._curInst!==inst){
			$.datepicker._curInst.dpDiv.stop(true,true);
			if(inst&&$.datepicker._datepickerShowing){
				$.datepicker._hideDatepicker($.datepicker._curInst.input[0]);
			}
		}

		beforeShow=$.datepicker._get(inst,"beforeShow");
		beforeShowSettings=beforeShow?beforeShow.apply(input,[input,inst]):{};
		if(beforeShowSettings===false){
			return;
		}
		datepicker_extendRemove(inst.settings,beforeShowSettings);

		inst.lastVal=null;
		$.datepicker._lastInput=input;
		$.datepicker._setDateFromField(inst);

		if($.datepicker._inDialog){//hidecursor
			input.value="";
		}
		if(!$.datepicker._pos){//positionbelowinput
			$.datepicker._pos=$.datepicker._findPos(input);
			$.datepicker._pos[1]+=input.offsetHeight;//addtheheight
		}

		isFixed=false;
		$(input).parents().each(function(){
			isFixed|=$(this).css("position")==="fixed";
			return!isFixed;
		});

		offset={left:$.datepicker._pos[0],top:$.datepicker._pos[1]};
		$.datepicker._pos=null;

		//toavoidflashesonFirefox
		inst.dpDiv.empty();

		//determinesizingoffscreen
		inst.dpDiv.css({position:"absolute",display:"block",top:"-1000px"});
		$.datepicker._updateDatepicker(inst);

		//fixwidthfordynamicnumberofdatepickers
		//andadjustpositionbeforeshowing
		offset=$.datepicker._checkOffset(inst,offset,isFixed);
		inst.dpDiv.css({position:($.datepicker._inDialog&&$.blockUI?
			"static":(isFixed?"fixed":"absolute")),display:"none",
			left:offset.left+"px",top:offset.top+"px"});

		if(!inst.inline){
			showAnim=$.datepicker._get(inst,"showAnim");
			duration=$.datepicker._get(inst,"duration");
			inst.dpDiv.css("z-index",datepicker_getZindex($(input))+1);
			$.datepicker._datepickerShowing=true;

			if($.effects&&$.effects.effect[showAnim]){
				inst.dpDiv.show(showAnim,$.datepicker._get(inst,"showOptions"),duration);
			}else{
				inst.dpDiv[showAnim||"show"](showAnim?duration:null);
			}

			if($.datepicker._shouldFocusInput(inst)){
				inst.input.trigger("focus");
			}

			$.datepicker._curInst=inst;
		}
	},

	/*Generatethedatepickercontent.*/
	_updateDatepicker:function(inst){
		this.maxRows=4;//Resetthemaxnumberofrowsbeingdisplayed(see#7043)
		datepicker_instActive=inst;//fordelegatehoverevents
		inst.dpDiv.empty().append(this._generateHTML(inst));
		this._attachHandlers(inst);

		varorigyearshtml,
			numMonths=this._getNumberOfMonths(inst),
			cols=numMonths[1],
			width=17,
			activeCell=inst.dpDiv.find("."+this._dayOverClass+"a");

		if(activeCell.length>0){
			datepicker_handleMouseover.apply(activeCell.get(0));
		}

		inst.dpDiv.removeClass("ui-datepicker-multi-2ui-datepicker-multi-3ui-datepicker-multi-4").width("");
		if(cols>1){
			inst.dpDiv.addClass("ui-datepicker-multi-"+cols).css("width",(width*cols)+"em");
		}
		inst.dpDiv[(numMonths[0]!==1||numMonths[1]!==1?"add":"remove")+
			"Class"]("ui-datepicker-multi");
		inst.dpDiv[(this._get(inst,"isRTL")?"add":"remove")+
			"Class"]("ui-datepicker-rtl");

		if(inst===$.datepicker._curInst&&$.datepicker._datepickerShowing&&$.datepicker._shouldFocusInput(inst)){
			inst.input.trigger("focus");
		}

		//Defferedrenderoftheyearsselect(toavoidflashesonFirefox)
		if(inst.yearshtml){
			origyearshtml=inst.yearshtml;
			setTimeout(function(){

				//assurethatinst.yearshtmldidn'tchange.
				if(origyearshtml===inst.yearshtml&&inst.yearshtml){
					inst.dpDiv.find("select.ui-datepicker-year:first").replaceWith(inst.yearshtml);
				}
				origyearshtml=inst.yearshtml=null;
			},0);
		}
	},

	//#6694-don'tfocustheinputifit'salreadyfocused
	//thisbreaksthechangeeventinIE
	//Support:IEandjQuery<1.9
	_shouldFocusInput:function(inst){
		returninst.input&&inst.input.is(":visible")&&!inst.input.is(":disabled")&&!inst.input.is(":focus");
	},

	/*Checkpositioningtoremainonscreen.*/
	_checkOffset:function(inst,offset,isFixed){
		vardpWidth=inst.dpDiv.outerWidth(),
			dpHeight=inst.dpDiv.outerHeight(),
			inputWidth=inst.input?inst.input.outerWidth():0,
			inputHeight=inst.input?inst.input.outerHeight():0,
			viewWidth=document.documentElement.clientWidth+(isFixed?0:$(document).scrollLeft()),
			viewHeight=document.documentElement.clientHeight+(isFixed?0:$(document).scrollTop());

		offset.left-=(this._get(inst,"isRTL")?(dpWidth-inputWidth):0);
		offset.left-=(isFixed&&offset.left===inst.input.offset().left)?$(document).scrollLeft():0;
		offset.top-=(isFixed&&offset.top===(inst.input.offset().top+inputHeight))?$(document).scrollTop():0;

		//Nowcheckifdatepickerisshowingoutsidewindowviewport-movetoabetterplaceifso.
		offset.left-=Math.min(offset.left,(offset.left+dpWidth>viewWidth&&viewWidth>dpWidth)?
			Math.abs(offset.left+dpWidth-viewWidth):0);
		offset.top-=Math.min(offset.top,(offset.top+dpHeight>viewHeight&&viewHeight>dpHeight)?
			Math.abs(dpHeight+inputHeight):0);

		returnoffset;
	},

	/*Findanobject'spositiononthescreen.*/
	_findPos:function(obj){
		varposition,
			inst=this._getInst(obj),
			isRTL=this._get(inst,"isRTL");

		while(obj&&(obj.type==="hidden"||obj.nodeType!==1||$.expr.filters.hidden(obj))){
			obj=obj[isRTL?"previousSibling":"nextSibling"];
		}

		position=$(obj).offset();
		return[position.left,position.top];
	},

	/*Hidethedatepickerfromview.
	*@param input element-theinputfieldattachedtothedatepicker
	*/
	_hideDatepicker:function(input){
		varshowAnim,duration,postProcess,onClose,
			inst=this._curInst;

		if(!inst||(input&&inst!==$.data(input,"datepicker"))){
			return;
		}

		if(this._datepickerShowing){
			showAnim=this._get(inst,"showAnim");
			duration=this._get(inst,"duration");
			postProcess=function(){
				$.datepicker._tidyDialog(inst);
			};

			//DEPRECATED:afterBCfor1.8.x$.effects[showAnim]isnotneeded
			if($.effects&&($.effects.effect[showAnim]||$.effects[showAnim])){
				inst.dpDiv.hide(showAnim,$.datepicker._get(inst,"showOptions"),duration,postProcess);
			}else{
				inst.dpDiv[(showAnim==="slideDown"?"slideUp":
					(showAnim==="fadeIn"?"fadeOut":"hide"))]((showAnim?duration:null),postProcess);
			}

			if(!showAnim){
				postProcess();
			}
			this._datepickerShowing=false;

			onClose=this._get(inst,"onClose");
			if(onClose){
				onClose.apply((inst.input?inst.input[0]:null),[(inst.input?inst.input.val():""),inst]);
			}

			this._lastInput=null;
			if(this._inDialog){
				this._dialogInput.css({position:"absolute",left:"0",top:"-100px"});
				if($.blockUI){
					$.unblockUI();
					$("body").append(this.dpDiv);
				}
			}
			this._inDialog=false;
		}
	},

	/*Tidyupafteradialogdisplay.*/
	_tidyDialog:function(inst){
		inst.dpDiv.removeClass(this._dialogClass).off(".ui-datepicker-calendar");
	},

	/*Closedatepickerifclickedelsewhere.*/
	_checkExternalClick:function(event){
		if(!$.datepicker._curInst){
			return;
		}

		var$target=$(event.target),
			inst=$.datepicker._getInst($target[0]);

		if((($target[0].id!==$.datepicker._mainDivId&&
				$target.parents("#"+$.datepicker._mainDivId).length===0&&
				!$target.hasClass($.datepicker.markerClassName)&&
				!$target.closest("."+$.datepicker._triggerClass).length&&
				$.datepicker._datepickerShowing&&!($.datepicker._inDialog&&$.blockUI)))||
			($target.hasClass($.datepicker.markerClassName)&&$.datepicker._curInst!==inst)){
				$.datepicker._hideDatepicker();
		}
	},

	/*Adjustoneofthedatesub-fields.*/
	_adjustDate:function(id,offset,period){
		vartarget=$(id),
			inst=this._getInst(target[0]);

		if(this._isDisabledDatepicker(target[0])){
			return;
		}
		this._adjustInstDate(inst,offset+
			(period==="M"?this._get(inst,"showCurrentAtPos"):0),//undopositioning
			period);
		this._updateDatepicker(inst);
	},

	/*Actionforcurrentlink.*/
	_gotoToday:function(id){
		vardate,
			target=$(id),
			inst=this._getInst(target[0]);

		if(this._get(inst,"gotoCurrent")&&inst.currentDay){
			inst.selectedDay=inst.currentDay;
			inst.drawMonth=inst.selectedMonth=inst.currentMonth;
			inst.drawYear=inst.selectedYear=inst.currentYear;
		}else{
			date=newDate();
			inst.selectedDay=date.getDate();
			inst.drawMonth=inst.selectedMonth=date.getMonth();
			inst.drawYear=inst.selectedYear=date.getFullYear();
		}
		this._notifyChange(inst);
		this._adjustDate(target);
	},

	/*Actionforselectinganewmonth/year.*/
	_selectMonthYear:function(id,select,period){
		vartarget=$(id),
			inst=this._getInst(target[0]);

		inst["selected"+(period==="M"?"Month":"Year")]=
		inst["draw"+(period==="M"?"Month":"Year")]=
			parseInt(select.options[select.selectedIndex].value,10);

		this._notifyChange(inst);
		this._adjustDate(target);
	},

	/*Actionforselectingaday.*/
	_selectDay:function(id,month,year,td){
		varinst,
			target=$(id);

		if($(td).hasClass(this._unselectableClass)||this._isDisabledDatepicker(target[0])){
			return;
		}

		inst=this._getInst(target[0]);
		inst.selectedDay=inst.currentDay=$("a",td).html();
		inst.selectedMonth=inst.currentMonth=month;
		inst.selectedYear=inst.currentYear=year;
		this._selectDate(id,this._formatDate(inst,
			inst.currentDay,inst.currentMonth,inst.currentYear));
	},

	/*Erasetheinputfieldandhidethedatepicker.*/
	_clearDate:function(id){
		vartarget=$(id);
		this._selectDate(target,"");
	},

	/*Updatetheinputfieldwiththeselecteddate.*/
	_selectDate:function(id,dateStr){
		varonSelect,
			target=$(id),
			inst=this._getInst(target[0]);

		dateStr=(dateStr!=null?dateStr:this._formatDate(inst));
		if(inst.input){
			inst.input.val(dateStr);
		}
		this._updateAlternate(inst);

		onSelect=this._get(inst,"onSelect");
		if(onSelect){
			onSelect.apply((inst.input?inst.input[0]:null),[dateStr,inst]); //triggercustomcallback
		}elseif(inst.input){
			inst.input.trigger("change");//firethechangeevent
		}

		if(inst.inline){
			this._updateDatepicker(inst);
		}else{
			this._hideDatepicker();
			this._lastInput=inst.input[0];
			if(typeof(inst.input[0])!=="object"){
				inst.input.trigger("focus");//restorefocus
			}
			this._lastInput=null;
		}
	},

	/*Updateanyalternatefieldtosynchronisewiththemainfield.*/
	_updateAlternate:function(inst){
		varaltFormat,date,dateStr,
			altField=this._get(inst,"altField");

		if(altField){//updatealternatefieldtoo
			altFormat=this._get(inst,"altFormat")||this._get(inst,"dateFormat");
			date=this._getDate(inst);
			dateStr=this.formatDate(altFormat,date,this._getFormatConfig(inst));
			$(altField).val(dateStr);
		}
	},

	/*SetasbeforeShowDayfunctiontopreventselectionofweekends.
	*@param date Date-thedatetocustomise
	*@return[boolean,string]-isthisdateselectable?,whatisitsCSSclass?
	*/
	noWeekends:function(date){
		varday=date.getDay();
		return[(day>0&&day<6),""];
	},

	/*SetascalculateWeektodeterminetheweekoftheyearbasedontheISO8601definition.
	*@param date Date-thedatetogettheweekfor
	*@return number-thenumberoftheweekwithintheyearthatcontainsthisdate
	*/
	iso8601Week:function(date){
		vartime,
			checkDate=newDate(date.getTime());

		//FindThursdayofthisweekstartingonMonday
		checkDate.setDate(checkDate.getDate()+4-(checkDate.getDay()||7));

		time=checkDate.getTime();
		checkDate.setMonth(0);//ComparewithJan1
		checkDate.setDate(1);
		returnMath.floor(Math.round((time-checkDate)/86400000)/7)+1;
	},

	/*Parseastringvalueintoadateobject.
	*SeeformatDatebelowforthepossibleformats.
	*
	*@param formatstring-theexpectedformatofthedate
	*@param valuestring-thedateintheaboveformat
	*@param settingsObject-attributesinclude:
	*					shortYearCutoff number-thecutoffyearfordeterminingthecentury(optional)
	*					dayNamesShort	string[7]-abbreviatednamesofthedaysfromSunday(optional)
	*					dayNames		string[7]-namesofthedaysfromSunday(optional)
	*					monthNamesShortstring[12]-abbreviatednamesofthemonths(optional)
	*					monthNames		string[12]-namesofthemonths(optional)
	*@return Date-theextracteddatevalueornullifvalueisblank
	*/
	parseDate:function(format,value,settings){
		if(format==null||value==null){
			throw"Invalidarguments";
		}

		value=(typeofvalue==="object"?value.toString():value+"");
		if(value===""){
			returnnull;
		}

		variFormat,dim,extra,
			iValue=0,
			shortYearCutoffTemp=(settings?settings.shortYearCutoff:null)||this._defaults.shortYearCutoff,
			shortYearCutoff=(typeofshortYearCutoffTemp!=="string"?shortYearCutoffTemp:
				newDate().getFullYear()%100+parseInt(shortYearCutoffTemp,10)),
			dayNamesShort=(settings?settings.dayNamesShort:null)||this._defaults.dayNamesShort,
			dayNames=(settings?settings.dayNames:null)||this._defaults.dayNames,
			monthNamesShort=(settings?settings.monthNamesShort:null)||this._defaults.monthNamesShort,
			monthNames=(settings?settings.monthNames:null)||this._defaults.monthNames,
			year=-1,
			month=-1,
			day=-1,
			doy=-1,
			literal=false,
			date,

			//Checkwhetheraformatcharacterisdoubled
			lookAhead=function(match){
				varmatches=(iFormat+1<format.length&&format.charAt(iFormat+1)===match);
				if(matches){
					iFormat++;
				}
				returnmatches;
			},

			//Extractanumberfromthestringvalue
			getNumber=function(match){
				varisDoubled=lookAhead(match),
					size=(match==="@"?14:(match==="!"?20:
					(match==="y"&&isDoubled?4:(match==="o"?3:2)))),
					minSize=(match==="y"?size:1),
					digits=newRegExp("^\\d{"+minSize+","+size+"}"),
					num=value.substring(iValue).match(digits);
				if(!num){
					throw"Missingnumberatposition"+iValue;
				}
				iValue+=num[0].length;
				returnparseInt(num[0],10);
			},

			//Extractanamefromthestringvalueandconverttoanindex
			getName=function(match,shortNames,longNames){
				varindex=-1,
					names=$.map(lookAhead(match)?longNames:shortNames,function(v,k){
						return[[k,v]];
					}).sort(function(a,b){
						return-(a[1].length-b[1].length);
					});

				$.each(names,function(i,pair){
					varname=pair[1];
					if(value.substr(iValue,name.length).toLowerCase()===name.toLowerCase()){
						index=pair[0];
						iValue+=name.length;
						returnfalse;
					}
				});
				if(index!==-1){
					returnindex+1;
				}else{
					throw"Unknownnameatposition"+iValue;
				}
			},

			//Confirmthataliteralcharactermatchesthestringvalue
			checkLiteral=function(){
				if(value.charAt(iValue)!==format.charAt(iFormat)){
					throw"Unexpectedliteralatposition"+iValue;
				}
				iValue++;
			};

		for(iFormat=0;iFormat<format.length;iFormat++){
			if(literal){
				if(format.charAt(iFormat)==="'"&&!lookAhead("'")){
					literal=false;
				}else{
					checkLiteral();
				}
			}else{
				switch(format.charAt(iFormat)){
					case"d":
						day=getNumber("d");
						break;
					case"D":
						getName("D",dayNamesShort,dayNames);
						break;
					case"o":
						doy=getNumber("o");
						break;
					case"m":
						month=getNumber("m");
						break;
					case"M":
						month=getName("M",monthNamesShort,monthNames);
						break;
					case"y":
						year=getNumber("y");
						break;
					case"@":
						date=newDate(getNumber("@"));
						year=date.getFullYear();
						month=date.getMonth()+1;
						day=date.getDate();
						break;
					case"!":
						date=newDate((getNumber("!")-this._ticksTo1970)/10000);
						year=date.getFullYear();
						month=date.getMonth()+1;
						day=date.getDate();
						break;
					case"'":
						if(lookAhead("'")){
							checkLiteral();
						}else{
							literal=true;
						}
						break;
					default:
						checkLiteral();
				}
			}
		}

		if(iValue<value.length){
			extra=value.substr(iValue);
			if(!/^\s+/.test(extra)){
				throw"Extra/unparsedcharactersfoundindate:"+extra;
			}
		}

		if(year===-1){
			year=newDate().getFullYear();
		}elseif(year<100){
			year+=newDate().getFullYear()-newDate().getFullYear()%100+
				(year<=shortYearCutoff?0:-100);
		}

		if(doy>-1){
			month=1;
			day=doy;
			do{
				dim=this._getDaysInMonth(year,month-1);
				if(day<=dim){
					break;
				}
				month++;
				day-=dim;
			}while(true);
		}

		date=this._daylightSavingAdjust(newDate(year,month-1,day));
		if(date.getFullYear()!==year||date.getMonth()+1!==month||date.getDate()!==day){
			throw"Invaliddate";//E.g.31/02/00
		}
		returndate;
	},

	/*Standarddateformats.*/
	ATOM:"yy-mm-dd",//RFC3339(ISO8601)
	COOKIE:"D,ddMyy",
	ISO_8601:"yy-mm-dd",
	RFC_822:"D,dMy",
	RFC_850:"DD,dd-M-y",
	RFC_1036:"D,dMy",
	RFC_1123:"D,dMyy",
	RFC_2822:"D,dMyy",
	RSS:"D,dMy",//RFC822
	TICKS:"!",
	TIMESTAMP:"@",
	W3C:"yy-mm-dd",//ISO8601

	_ticksTo1970:(((1970-1)*365+Math.floor(1970/4)-Math.floor(1970/100)+
		Math.floor(1970/400))*24*60*60*10000000),

	/*Formatadateobjectintoastringvalue.
	*Theformatcanbecombinationsofthefollowing:
	*d -dayofmonth(noleadingzero)
	*dd-dayofmonth(twodigit)
	*o -dayofyear(noleadingzeros)
	*oo-dayofyear(threedigit)
	*D -daynameshort
	*DD-daynamelong
	*m -monthofyear(noleadingzero)
	*mm-monthofyear(twodigit)
	*M -monthnameshort
	*MM-monthnamelong
	*y -year(twodigit)
	*yy-year(fourdigit)
	*@-Unixtimestamp(mssince01/01/1970)
	*!-Windowsticks(100nssince01/01/0001)
	*"..."-literaltext
	*''-singlequote
	*
	*@param formatstring-thedesiredformatofthedate
	*@param dateDate-thedatevaluetoformat
	*@param settingsObject-attributesinclude:
	*					dayNamesShort	string[7]-abbreviatednamesofthedaysfromSunday(optional)
	*					dayNames		string[7]-namesofthedaysfromSunday(optional)
	*					monthNamesShortstring[12]-abbreviatednamesofthemonths(optional)
	*					monthNames		string[12]-namesofthemonths(optional)
	*@return string-thedateintheaboveformat
	*/
	formatDate:function(format,date,settings){
		if(!date){
			return"";
		}

		variFormat,
			dayNamesShort=(settings?settings.dayNamesShort:null)||this._defaults.dayNamesShort,
			dayNames=(settings?settings.dayNames:null)||this._defaults.dayNames,
			monthNamesShort=(settings?settings.monthNamesShort:null)||this._defaults.monthNamesShort,
			monthNames=(settings?settings.monthNames:null)||this._defaults.monthNames,

			//Checkwhetheraformatcharacterisdoubled
			lookAhead=function(match){
				varmatches=(iFormat+1<format.length&&format.charAt(iFormat+1)===match);
				if(matches){
					iFormat++;
				}
				returnmatches;
			},

			//Formatanumber,withleadingzeroifnecessary
			formatNumber=function(match,value,len){
				varnum=""+value;
				if(lookAhead(match)){
					while(num.length<len){
						num="0"+num;
					}
				}
				returnnum;
			},

			//Formataname,shortorlongasrequested
			formatName=function(match,value,shortNames,longNames){
				return(lookAhead(match)?longNames[value]:shortNames[value]);
			},
			output="",
			literal=false;

		if(date){
			for(iFormat=0;iFormat<format.length;iFormat++){
				if(literal){
					if(format.charAt(iFormat)==="'"&&!lookAhead("'")){
						literal=false;
					}else{
						output+=format.charAt(iFormat);
					}
				}else{
					switch(format.charAt(iFormat)){
						case"d":
							output+=formatNumber("d",date.getDate(),2);
							break;
						case"D":
							output+=formatName("D",date.getDay(),dayNamesShort,dayNames);
							break;
						case"o":
							output+=formatNumber("o",
								Math.round((newDate(date.getFullYear(),date.getMonth(),date.getDate()).getTime()-newDate(date.getFullYear(),0,0).getTime())/86400000),3);
							break;
						case"m":
							output+=formatNumber("m",date.getMonth()+1,2);
							break;
						case"M":
							output+=formatName("M",date.getMonth(),monthNamesShort,monthNames);
							break;
						case"y":
							output+=(lookAhead("y")?date.getFullYear():
								(date.getFullYear()%100<10?"0":"")+date.getFullYear()%100);
							break;
						case"@":
							output+=date.getTime();
							break;
						case"!":
							output+=date.getTime()*10000+this._ticksTo1970;
							break;
						case"'":
							if(lookAhead("'")){
								output+="'";
							}else{
								literal=true;
							}
							break;
						default:
							output+=format.charAt(iFormat);
					}
				}
			}
		}
		returnoutput;
	},

	/*Extractallpossiblecharactersfromthedateformat.*/
	_possibleChars:function(format){
		variFormat,
			chars="",
			literal=false,

			//Checkwhetheraformatcharacterisdoubled
			lookAhead=function(match){
				varmatches=(iFormat+1<format.length&&format.charAt(iFormat+1)===match);
				if(matches){
					iFormat++;
				}
				returnmatches;
			};

		for(iFormat=0;iFormat<format.length;iFormat++){
			if(literal){
				if(format.charAt(iFormat)==="'"&&!lookAhead("'")){
					literal=false;
				}else{
					chars+=format.charAt(iFormat);
				}
			}else{
				switch(format.charAt(iFormat)){
					case"d":case"m":case"y":case"@":
						chars+="0123456789";
						break;
					case"D":case"M":
						returnnull;//Acceptanything
					case"'":
						if(lookAhead("'")){
							chars+="'";
						}else{
							literal=true;
						}
						break;
					default:
						chars+=format.charAt(iFormat);
				}
			}
		}
		returnchars;
	},

	/*Getasettingvalue,defaultingifnecessary.*/
	_get:function(inst,name){
		returninst.settings[name]!==undefined?
			inst.settings[name]:this._defaults[name];
	},

	/*Parseexistingdateandinitialisedatepicker.*/
	_setDateFromField:function(inst,noDefault){
		if(inst.input.val()===inst.lastVal){
			return;
		}

		vardateFormat=this._get(inst,"dateFormat"),
			dates=inst.lastVal=inst.input?inst.input.val():null,
			defaultDate=this._getDefaultDate(inst),
			date=defaultDate,
			settings=this._getFormatConfig(inst);

		try{
			date=this.parseDate(dateFormat,dates,settings)||defaultDate;
		}catch(event){
			dates=(noDefault?"":dates);
		}
		inst.selectedDay=date.getDate();
		inst.drawMonth=inst.selectedMonth=date.getMonth();
		inst.drawYear=inst.selectedYear=date.getFullYear();
		inst.currentDay=(dates?date.getDate():0);
		inst.currentMonth=(dates?date.getMonth():0);
		inst.currentYear=(dates?date.getFullYear():0);
		this._adjustInstDate(inst);
	},

	/*Retrievethedefaultdateshownonopening.*/
	_getDefaultDate:function(inst){
		returnthis._restrictMinMax(inst,
			this._determineDate(inst,this._get(inst,"defaultDate"),newDate()));
	},

	/*Adatemaybespecifiedasanexactvalueorarelativeone.*/
	_determineDate:function(inst,date,defaultDate){
		varoffsetNumeric=function(offset){
				vardate=newDate();
				date.setDate(date.getDate()+offset);
				returndate;
			},
			offsetString=function(offset){
				try{
					return$.datepicker.parseDate($.datepicker._get(inst,"dateFormat"),
						offset,$.datepicker._getFormatConfig(inst));
				}
				catch(e){

					//Ignore
				}

				vardate=(offset.toLowerCase().match(/^c/)?
					$.datepicker._getDate(inst):null)||newDate(),
					year=date.getFullYear(),
					month=date.getMonth(),
					day=date.getDate(),
					pattern=/([+\-]?[0-9]+)\s*(d|D|w|W|m|M|y|Y)?/g,
					matches=pattern.exec(offset);

				while(matches){
					switch(matches[2]||"d"){
						case"d":case"D":
							day+=parseInt(matches[1],10);break;
						case"w":case"W":
							day+=parseInt(matches[1],10)*7;break;
						case"m":case"M":
							month+=parseInt(matches[1],10);
							day=Math.min(day,$.datepicker._getDaysInMonth(year,month));
							break;
						case"y":case"Y":
							year+=parseInt(matches[1],10);
							day=Math.min(day,$.datepicker._getDaysInMonth(year,month));
							break;
					}
					matches=pattern.exec(offset);
				}
				returnnewDate(year,month,day);
			},
			newDate=(date==null||date===""?defaultDate:(typeofdate==="string"?offsetString(date):
				(typeofdate==="number"?(isNaN(date)?defaultDate:offsetNumeric(date)):newDate(date.getTime()))));

		newDate=(newDate&&newDate.toString()==="InvalidDate"?defaultDate:newDate);
		if(newDate){
			newDate.setHours(0);
			newDate.setMinutes(0);
			newDate.setSeconds(0);
			newDate.setMilliseconds(0);
		}
		returnthis._daylightSavingAdjust(newDate);
	},

	/*Handleswitchto/fromdaylightsaving.
	*Hoursmaybenon-zeroondaylightsavingcut-over:
	*>12whenmidnightchangeover,butthencannotgenerate
	*midnightdatetime,sojumpto1AM,otherwisereset.
	*@param date (Date)thedatetocheck
	*@return (Date)thecorrecteddate
	*/
	_daylightSavingAdjust:function(date){
		if(!date){
			returnnull;
		}
		date.setHours(date.getHours()>12?date.getHours()+2:0);
		returndate;
	},

	/*Setthedate(s)directly.*/
	_setDate:function(inst,date,noChange){
		varclear=!date,
			origMonth=inst.selectedMonth,
			origYear=inst.selectedYear,
			newDate=this._restrictMinMax(inst,this._determineDate(inst,date,newDate()));

		inst.selectedDay=inst.currentDay=newDate.getDate();
		inst.drawMonth=inst.selectedMonth=inst.currentMonth=newDate.getMonth();
		inst.drawYear=inst.selectedYear=inst.currentYear=newDate.getFullYear();
		if((origMonth!==inst.selectedMonth||origYear!==inst.selectedYear)&&!noChange){
			this._notifyChange(inst);
		}
		this._adjustInstDate(inst);
		if(inst.input){
			inst.input.val(clear?"":this._formatDate(inst));
		}
	},

	/*Retrievethedate(s)directly.*/
	_getDate:function(inst){
		varstartDate=(!inst.currentYear||(inst.input&&inst.input.val()==="")?null:
			this._daylightSavingAdjust(newDate(
			inst.currentYear,inst.currentMonth,inst.currentDay)));
			returnstartDate;
	},

	/*Attachtheonxxxhandlers. Thesearedeclaredstaticallyso
	*theyworkwithstaticcodetransformerslikeCaja.
	*/
	_attachHandlers:function(inst){
		varstepMonths=this._get(inst,"stepMonths"),
			id="#"+inst.id.replace(/\\\\/g,"\\");
		inst.dpDiv.find("[data-handler]").map(function(){
			varhandler={
				prev:function(){
					$.datepicker._adjustDate(id,-stepMonths,"M");
				},
				next:function(){
					$.datepicker._adjustDate(id,+stepMonths,"M");
				},
				hide:function(){
					$.datepicker._hideDatepicker();
				},
				today:function(){
					$.datepicker._gotoToday(id);
				},
				selectDay:function(){
					$.datepicker._selectDay(id,+this.getAttribute("data-month"),+this.getAttribute("data-year"),this);
					returnfalse;
				},
				selectMonth:function(){
					$.datepicker._selectMonthYear(id,this,"M");
					returnfalse;
				},
				selectYear:function(){
					$.datepicker._selectMonthYear(id,this,"Y");
					returnfalse;
				}
			};
			$(this).on(this.getAttribute("data-event"),handler[this.getAttribute("data-handler")]);
		});
	},

	/*GeneratetheHTMLforthecurrentstateofthedatepicker.*/
	_generateHTML:function(inst){
		varmaxDraw,prevText,prev,nextText,next,currentText,gotoDate,
			controls,buttonPanel,firstDay,showWeek,dayNames,dayNamesMin,
			monthNames,monthNamesShort,beforeShowDay,showOtherMonths,
			selectOtherMonths,defaultDate,html,dow,row,group,col,selectedDate,
			cornerClass,calender,thead,day,daysInMonth,leadDays,curRows,numRows,
			printDate,dRow,tbody,daySettings,otherMonth,unselectable,
			tempDate=newDate(),
			today=this._daylightSavingAdjust(
				newDate(tempDate.getFullYear(),tempDate.getMonth(),tempDate.getDate())),//cleartime
			isRTL=this._get(inst,"isRTL"),
			showButtonPanel=this._get(inst,"showButtonPanel"),
			hideIfNoPrevNext=this._get(inst,"hideIfNoPrevNext"),
			navigationAsDateFormat=this._get(inst,"navigationAsDateFormat"),
			numMonths=this._getNumberOfMonths(inst),
			showCurrentAtPos=this._get(inst,"showCurrentAtPos"),
			stepMonths=this._get(inst,"stepMonths"),
			isMultiMonth=(numMonths[0]!==1||numMonths[1]!==1),
			currentDate=this._daylightSavingAdjust((!inst.currentDay?newDate(9999,9,9):
				newDate(inst.currentYear,inst.currentMonth,inst.currentDay))),
			minDate=this._getMinMaxDate(inst,"min"),
			maxDate=this._getMinMaxDate(inst,"max"),
			drawMonth=inst.drawMonth-showCurrentAtPos,
			drawYear=inst.drawYear;

		if(drawMonth<0){
			drawMonth+=12;
			drawYear--;
		}
		if(maxDate){
			maxDraw=this._daylightSavingAdjust(newDate(maxDate.getFullYear(),
				maxDate.getMonth()-(numMonths[0]*numMonths[1])+1,maxDate.getDate()));
			maxDraw=(minDate&&maxDraw<minDate?minDate:maxDraw);
			while(this._daylightSavingAdjust(newDate(drawYear,drawMonth,1))>maxDraw){
				drawMonth--;
				if(drawMonth<0){
					drawMonth=11;
					drawYear--;
				}
			}
		}
		inst.drawMonth=drawMonth;
		inst.drawYear=drawYear;

		prevText=this._get(inst,"prevText");
		prevText=(!navigationAsDateFormat?prevText:this.formatDate(prevText,
			this._daylightSavingAdjust(newDate(drawYear,drawMonth-stepMonths,1)),
			this._getFormatConfig(inst)));

		prev=(this._canAdjustMonth(inst,-1,drawYear,drawMonth)?
			"<aclass='ui-datepicker-prevui-corner-all'data-handler='prev'data-event='click'"+
			"title='"+prevText+"'><spanclass='ui-iconui-icon-circle-triangle-"+(isRTL?"e":"w")+"'>"+prevText+"</span></a>":
			(hideIfNoPrevNext?"":"<aclass='ui-datepicker-prevui-corner-allui-state-disabled'title='"+prevText+"'><spanclass='ui-iconui-icon-circle-triangle-"+(isRTL?"e":"w")+"'>"+prevText+"</span></a>"));

		nextText=this._get(inst,"nextText");
		nextText=(!navigationAsDateFormat?nextText:this.formatDate(nextText,
			this._daylightSavingAdjust(newDate(drawYear,drawMonth+stepMonths,1)),
			this._getFormatConfig(inst)));

		next=(this._canAdjustMonth(inst,+1,drawYear,drawMonth)?
			"<aclass='ui-datepicker-nextui-corner-all'data-handler='next'data-event='click'"+
			"title='"+nextText+"'><spanclass='ui-iconui-icon-circle-triangle-"+(isRTL?"w":"e")+"'>"+nextText+"</span></a>":
			(hideIfNoPrevNext?"":"<aclass='ui-datepicker-nextui-corner-allui-state-disabled'title='"+nextText+"'><spanclass='ui-iconui-icon-circle-triangle-"+(isRTL?"w":"e")+"'>"+nextText+"</span></a>"));

		currentText=this._get(inst,"currentText");
		gotoDate=(this._get(inst,"gotoCurrent")&&inst.currentDay?currentDate:today);
		currentText=(!navigationAsDateFormat?currentText:
			this.formatDate(currentText,gotoDate,this._getFormatConfig(inst)));

		controls=(!inst.inline?"<buttontype='button'class='ui-datepicker-closeui-state-defaultui-priority-primaryui-corner-all'data-handler='hide'data-event='click'>"+
			this._get(inst,"closeText")+"</button>":"");

		buttonPanel=(showButtonPanel)?"<divclass='ui-datepicker-buttonpaneui-widget-content'>"+(isRTL?controls:"")+
			(this._isInRange(inst,gotoDate)?"<buttontype='button'class='ui-datepicker-currentui-state-defaultui-priority-secondaryui-corner-all'data-handler='today'data-event='click'"+
			">"+currentText+"</button>":"")+(isRTL?"":controls)+"</div>":"";

		firstDay=parseInt(this._get(inst,"firstDay"),10);
		firstDay=(isNaN(firstDay)?0:firstDay);

		showWeek=this._get(inst,"showWeek");
		dayNames=this._get(inst,"dayNames");
		dayNamesMin=this._get(inst,"dayNamesMin");
		monthNames=this._get(inst,"monthNames");
		monthNamesShort=this._get(inst,"monthNamesShort");
		beforeShowDay=this._get(inst,"beforeShowDay");
		showOtherMonths=this._get(inst,"showOtherMonths");
		selectOtherMonths=this._get(inst,"selectOtherMonths");
		defaultDate=this._getDefaultDate(inst);
		html="";

		for(row=0;row<numMonths[0];row++){
			group="";
			this.maxRows=4;
			for(col=0;col<numMonths[1];col++){
				selectedDate=this._daylightSavingAdjust(newDate(drawYear,drawMonth,inst.selectedDay));
				cornerClass="ui-corner-all";
				calender="";
				if(isMultiMonth){
					calender+="<divclass='ui-datepicker-group";
					if(numMonths[1]>1){
						switch(col){
							case0:calender+="ui-datepicker-group-first";
								cornerClass="ui-corner-"+(isRTL?"right":"left");break;
							casenumMonths[1]-1:calender+="ui-datepicker-group-last";
								cornerClass="ui-corner-"+(isRTL?"left":"right");break;
							default:calender+="ui-datepicker-group-middle";cornerClass="";break;
						}
					}
					calender+="'>";
				}
				calender+="<divclass='ui-datepicker-headerui-widget-headerui-helper-clearfix"+cornerClass+"'>"+
					(/all|left/.test(cornerClass)&&row===0?(isRTL?next:prev):"")+
					(/all|right/.test(cornerClass)&&row===0?(isRTL?prev:next):"")+
					this._generateMonthYearHeader(inst,drawMonth,drawYear,minDate,maxDate,
					row>0||col>0,monthNames,monthNamesShort)+//drawmonthheaders
					"</div><tableclass='ui-datepicker-calendar'><thead>"+
					"<tr>";
				thead=(showWeek?"<thclass='ui-datepicker-week-col'>"+this._get(inst,"weekHeader")+"</th>":"");
				for(dow=0;dow<7;dow++){//daysoftheweek
					day=(dow+firstDay)%7;
					thead+="<thscope='col'"+((dow+firstDay+6)%7>=5?"class='ui-datepicker-week-end'":"")+">"+
						"<spantitle='"+dayNames[day]+"'>"+dayNamesMin[day]+"</span></th>";
				}
				calender+=thead+"</tr></thead><tbody>";
				daysInMonth=this._getDaysInMonth(drawYear,drawMonth);
				if(drawYear===inst.selectedYear&&drawMonth===inst.selectedMonth){
					inst.selectedDay=Math.min(inst.selectedDay,daysInMonth);
				}
				leadDays=(this._getFirstDayOfMonth(drawYear,drawMonth)-firstDay+7)%7;
				curRows=Math.ceil((leadDays+daysInMonth)/7);//calculatethenumberofrowstogenerate
				numRows=(isMultiMonth?this.maxRows>curRows?this.maxRows:curRows:curRows);//Ifmultiplemonths,usethehighernumberofrows(see#7043)
				this.maxRows=numRows;
				printDate=this._daylightSavingAdjust(newDate(drawYear,drawMonth,1-leadDays));
				for(dRow=0;dRow<numRows;dRow++){//createdatepickerrows
					calender+="<tr>";
					tbody=(!showWeek?"":"<tdclass='ui-datepicker-week-col'>"+
						this._get(inst,"calculateWeek")(printDate)+"</td>");
					for(dow=0;dow<7;dow++){//createdatepickerdays
						daySettings=(beforeShowDay?
							beforeShowDay.apply((inst.input?inst.input[0]:null),[printDate]):[true,""]);
						otherMonth=(printDate.getMonth()!==drawMonth);
						unselectable=(otherMonth&&!selectOtherMonths)||!daySettings[0]||
							(minDate&&printDate<minDate)||(maxDate&&printDate>maxDate);
						tbody+="<tdclass='"+
							((dow+firstDay+6)%7>=5?"ui-datepicker-week-end":"")+//highlightweekends
							(otherMonth?"ui-datepicker-other-month":"")+//highlightdaysfromothermonths
							((printDate.getTime()===selectedDate.getTime()&&drawMonth===inst.selectedMonth&&inst._keyEvent)||//userpressedkey
							(defaultDate.getTime()===printDate.getTime()&&defaultDate.getTime()===selectedDate.getTime())?

							//ordefaultDateiscurrentprintedDateanddefaultDateisselectedDate
							""+this._dayOverClass:"")+//highlightselectedday
							(unselectable?""+this._unselectableClass+"ui-state-disabled":"")+ //highlightunselectabledays
							(otherMonth&&!showOtherMonths?"":""+daySettings[1]+//highlightcustomdates
							(printDate.getTime()===currentDate.getTime()?""+this._currentClass:"")+//highlightselectedday
							(printDate.getTime()===today.getTime()?"ui-datepicker-today":""))+"'"+//highlighttoday(ifdifferent)
							((!otherMonth||showOtherMonths)&&daySettings[2]?"title='"+daySettings[2].replace(/'/g,"&#39;")+"'":"")+//celltitle
							(unselectable?"":"data-handler='selectDay'data-event='click'data-month='"+printDate.getMonth()+"'data-year='"+printDate.getFullYear()+"'")+">"+//actions
							(otherMonth&&!showOtherMonths?"&#xa0;"://displayforothermonths
							(unselectable?"<spanclass='ui-state-default'>"+printDate.getDate()+"</span>":"<aclass='ui-state-default"+
							(printDate.getTime()===today.getTime()?"ui-state-highlight":"")+
							(printDate.getTime()===currentDate.getTime()?"ui-state-active":"")+//highlightselectedday
							(otherMonth?"ui-priority-secondary":"")+//distinguishdatesfromothermonths
							"'href='#'>"+printDate.getDate()+"</a>"))+"</td>";//displayselectabledate
						printDate.setDate(printDate.getDate()+1);
						printDate=this._daylightSavingAdjust(printDate);
					}
					calender+=tbody+"</tr>";
				}
				drawMonth++;
				if(drawMonth>11){
					drawMonth=0;
					drawYear++;
				}
				calender+="</tbody></table>"+(isMultiMonth?"</div>"+
							((numMonths[0]>0&&col===numMonths[1]-1)?"<divclass='ui-datepicker-row-break'></div>":""):"");
				group+=calender;
			}
			html+=group;
		}
		html+=buttonPanel;
		inst._keyEvent=false;
		returnhtml;
	},

	/*Generatethemonthandyearheader.*/
	_generateMonthYearHeader:function(inst,drawMonth,drawYear,minDate,maxDate,
			secondary,monthNames,monthNamesShort){

		varinMinYear,inMaxYear,month,years,thisYear,determineYear,year,endYear,
			changeMonth=this._get(inst,"changeMonth"),
			changeYear=this._get(inst,"changeYear"),
			showMonthAfterYear=this._get(inst,"showMonthAfterYear"),
			html="<divclass='ui-datepicker-title'>",
			monthHtml="";

		//Monthselection
		if(secondary||!changeMonth){
			monthHtml+="<spanclass='ui-datepicker-month'>"+monthNames[drawMonth]+"</span>";
		}else{
			inMinYear=(minDate&&minDate.getFullYear()===drawYear);
			inMaxYear=(maxDate&&maxDate.getFullYear()===drawYear);
			monthHtml+="<selectclass='ui-datepicker-month'data-handler='selectMonth'data-event='change'>";
			for(month=0;month<12;month++){
				if((!inMinYear||month>=minDate.getMonth())&&(!inMaxYear||month<=maxDate.getMonth())){
					monthHtml+="<optionvalue='"+month+"'"+
						(month===drawMonth?"selected='selected'":"")+
						">"+monthNamesShort[month]+"</option>";
				}
			}
			monthHtml+="</select>";
		}

		if(!showMonthAfterYear){
			html+=monthHtml+(secondary||!(changeMonth&&changeYear)?"&#xa0;":"");
		}

		//Yearselection
		if(!inst.yearshtml){
			inst.yearshtml="";
			if(secondary||!changeYear){
				html+="<spanclass='ui-datepicker-year'>"+drawYear+"</span>";
			}else{

				//determinerangeofyearstodisplay
				years=this._get(inst,"yearRange").split(":");
				thisYear=newDate().getFullYear();
				determineYear=function(value){
					varyear=(value.match(/c[+\-].*/)?drawYear+parseInt(value.substring(1),10):
						(value.match(/[+\-].*/)?thisYear+parseInt(value,10):
						parseInt(value,10)));
					return(isNaN(year)?thisYear:year);
				};
				year=determineYear(years[0]);
				endYear=Math.max(year,determineYear(years[1]||""));
				year=(minDate?Math.max(year,minDate.getFullYear()):year);
				endYear=(maxDate?Math.min(endYear,maxDate.getFullYear()):endYear);
				inst.yearshtml+="<selectclass='ui-datepicker-year'data-handler='selectYear'data-event='change'>";
				for(;year<=endYear;year++){
					inst.yearshtml+="<optionvalue='"+year+"'"+
						(year===drawYear?"selected='selected'":"")+
						">"+year+"</option>";
				}
				inst.yearshtml+="</select>";

				html+=inst.yearshtml;
				inst.yearshtml=null;
			}
		}

		html+=this._get(inst,"yearSuffix");
		if(showMonthAfterYear){
			html+=(secondary||!(changeMonth&&changeYear)?"&#xa0;":"")+monthHtml;
		}
		html+="</div>";//Closedatepicker_header
		returnhtml;
	},

	/*Adjustoneofthedatesub-fields.*/
	_adjustInstDate:function(inst,offset,period){
		varyear=inst.selectedYear+(period==="Y"?offset:0),
			month=inst.selectedMonth+(period==="M"?offset:0),
			day=Math.min(inst.selectedDay,this._getDaysInMonth(year,month))+(period==="D"?offset:0),
			date=this._restrictMinMax(inst,this._daylightSavingAdjust(newDate(year,month,day)));

		inst.selectedDay=date.getDate();
		inst.drawMonth=inst.selectedMonth=date.getMonth();
		inst.drawYear=inst.selectedYear=date.getFullYear();
		if(period==="M"||period==="Y"){
			this._notifyChange(inst);
		}
	},

	/*Ensureadateiswithinanymin/maxbounds.*/
	_restrictMinMax:function(inst,date){
		varminDate=this._getMinMaxDate(inst,"min"),
			maxDate=this._getMinMaxDate(inst,"max"),
			newDate=(minDate&&date<minDate?minDate:date);
		return(maxDate&&newDate>maxDate?maxDate:newDate);
	},

	/*Notifychangeofmonth/year.*/
	_notifyChange:function(inst){
		varonChange=this._get(inst,"onChangeMonthYear");
		if(onChange){
			onChange.apply((inst.input?inst.input[0]:null),
				[inst.selectedYear,inst.selectedMonth+1,inst]);
		}
	},

	/*Determinethenumberofmonthstoshow.*/
	_getNumberOfMonths:function(inst){
		varnumMonths=this._get(inst,"numberOfMonths");
		return(numMonths==null?[1,1]:(typeofnumMonths==="number"?[1,numMonths]:numMonths));
	},

	/*Determinethecurrentmaximumdate-ensurenotimecomponentsareset.*/
	_getMinMaxDate:function(inst,minMax){
		returnthis._determineDate(inst,this._get(inst,minMax+"Date"),null);
	},

	/*Findthenumberofdaysinagivenmonth.*/
	_getDaysInMonth:function(year,month){
		return32-this._daylightSavingAdjust(newDate(year,month,32)).getDate();
	},

	/*Findthedayoftheweekofthefirstofamonth.*/
	_getFirstDayOfMonth:function(year,month){
		returnnewDate(year,month,1).getDay();
	},

	/*Determinesifweshouldallowa"next/prev"monthdisplaychange.*/
	_canAdjustMonth:function(inst,offset,curYear,curMonth){
		varnumMonths=this._getNumberOfMonths(inst),
			date=this._daylightSavingAdjust(newDate(curYear,
			curMonth+(offset<0?offset:numMonths[0]*numMonths[1]),1));

		if(offset<0){
			date.setDate(this._getDaysInMonth(date.getFullYear(),date.getMonth()));
		}
		returnthis._isInRange(inst,date);
	},

	/*Isthegivendateintheacceptedrange?*/
	_isInRange:function(inst,date){
		varyearSplit,currentYear,
			minDate=this._getMinMaxDate(inst,"min"),
			maxDate=this._getMinMaxDate(inst,"max"),
			minYear=null,
			maxYear=null,
			years=this._get(inst,"yearRange");
			if(years){
				yearSplit=years.split(":");
				currentYear=newDate().getFullYear();
				minYear=parseInt(yearSplit[0],10);
				maxYear=parseInt(yearSplit[1],10);
				if(yearSplit[0].match(/[+\-].*/)){
					minYear+=currentYear;
				}
				if(yearSplit[1].match(/[+\-].*/)){
					maxYear+=currentYear;
				}
			}

		return((!minDate||date.getTime()>=minDate.getTime())&&
			(!maxDate||date.getTime()<=maxDate.getTime())&&
			(!minYear||date.getFullYear()>=minYear)&&
			(!maxYear||date.getFullYear()<=maxYear));
	},

	/*Providetheconfigurationsettingsforformatting/parsing.*/
	_getFormatConfig:function(inst){
		varshortYearCutoff=this._get(inst,"shortYearCutoff");
		shortYearCutoff=(typeofshortYearCutoff!=="string"?shortYearCutoff:
			newDate().getFullYear()%100+parseInt(shortYearCutoff,10));
		return{shortYearCutoff:shortYearCutoff,
			dayNamesShort:this._get(inst,"dayNamesShort"),dayNames:this._get(inst,"dayNames"),
			monthNamesShort:this._get(inst,"monthNamesShort"),monthNames:this._get(inst,"monthNames")};
	},

	/*Formatthegivendatefordisplay.*/
	_formatDate:function(inst,day,month,year){
		if(!day){
			inst.currentDay=inst.selectedDay;
			inst.currentMonth=inst.selectedMonth;
			inst.currentYear=inst.selectedYear;
		}
		vardate=(day?(typeofday==="object"?day:
			this._daylightSavingAdjust(newDate(year,month,day))):
			this._daylightSavingAdjust(newDate(inst.currentYear,inst.currentMonth,inst.currentDay)));
		returnthis.formatDate(this._get(inst,"dateFormat"),date,this._getFormatConfig(inst));
	}
});

/*
 *Bindhovereventsfordatepickerelements.
 *Doneviadelegatesothebindingonlyoccursonceinthelifetimeoftheparentdiv.
 *Globaldatepicker_instActive,setby_updateDatepickerallowsthehandlerstofindtheirwaybacktotheactivepicker.
 */
functiondatepicker_bindHover(dpDiv){
	varselector="button,.ui-datepicker-prev,.ui-datepicker-next,.ui-datepicker-calendartda";
	returndpDiv.on("mouseout",selector,function(){
			$(this).removeClass("ui-state-hover");
			if(this.className.indexOf("ui-datepicker-prev")!==-1){
				$(this).removeClass("ui-datepicker-prev-hover");
			}
			if(this.className.indexOf("ui-datepicker-next")!==-1){
				$(this).removeClass("ui-datepicker-next-hover");
			}
		})
		.on("mouseover",selector,datepicker_handleMouseover);
}

functiondatepicker_handleMouseover(){
	if(!$.datepicker._isDisabledDatepicker(datepicker_instActive.inline?datepicker_instActive.dpDiv.parent()[0]:datepicker_instActive.input[0])){
		$(this).parents(".ui-datepicker-calendar").find("a").removeClass("ui-state-hover");
		$(this).addClass("ui-state-hover");
		if(this.className.indexOf("ui-datepicker-prev")!==-1){
			$(this).addClass("ui-datepicker-prev-hover");
		}
		if(this.className.indexOf("ui-datepicker-next")!==-1){
			$(this).addClass("ui-datepicker-next-hover");
		}
	}
}

/*jQueryextendnowignoresnulls!*/
functiondatepicker_extendRemove(target,props){
	$.extend(target,props);
	for(varnameinprops){
		if(props[name]==null){
			target[name]=props[name];
		}
	}
	returntarget;
}

/*Invokethedatepickerfunctionality.
   @param options string-acommand,optionallyfollowedbyadditionalparametersor
					Object-settingsforattachingnewdatepickerfunctionality
   @return jQueryobject*/
$.fn.datepicker=function(options){

	/*Verifyanemptycollectionwasn'tpassed-Fixes#6976*/
	if(!this.length){
		returnthis;
	}

	/*Initialisethedatepicker.*/
	if(!$.datepicker.initialized){
		$(document).on("mousedown",$.datepicker._checkExternalClick);
		$.datepicker.initialized=true;
	}

	/*Appenddatepickermaincontainertobodyifnotexist.*/
	if($("#"+$.datepicker._mainDivId).length===0){
		$("body").append($.datepicker.dpDiv);
	}

	varotherArgs=Array.prototype.slice.call(arguments,1);
	if(typeofoptions==="string"&&(options==="isDisabled"||options==="getDate"||options==="widget")){
		return$.datepicker["_"+options+"Datepicker"].
			apply($.datepicker,[this[0]].concat(otherArgs));
	}
	if(options==="option"&&arguments.length===2&&typeofarguments[1]==="string"){
		return$.datepicker["_"+options+"Datepicker"].
			apply($.datepicker,[this[0]].concat(otherArgs));
	}
	returnthis.each(function(){
		typeofoptions==="string"?
			$.datepicker["_"+options+"Datepicker"].
				apply($.datepicker,[this].concat(otherArgs)):
			$.datepicker._attachDatepicker(this,options);
	});
};

$.datepicker=newDatepicker();//singletoninstance
$.datepicker.initialized=false;
$.datepicker.uuid=newDate().getTime();
$.datepicker.version="1.12.1";

varwidgetsDatepicker=$.datepicker;


/*!
 *jQueryUITooltip1.12.1
 *http://jqueryui.com
 *
 *CopyrightjQueryFoundationandothercontributors
 *ReleasedundertheMITlicense.
 *http://jquery.org/license
 */

//>>label:Tooltip
//>>group:Widgets
//>>description:Showsadditionalinformationforanyelementonhoverorfocus.
//>>docs:http://api.jqueryui.com/tooltip/
//>>demos:http://jqueryui.com/tooltip/
//>>css.structure:../../themes/base/core.css
//>>css.structure:../../themes/base/tooltip.css
//>>css.theme:../../themes/base/theme.css



$.widget("ui.tooltip",{
	version:"1.12.1",
	options:{
		classes:{
			"ui-tooltip":"ui-corner-allui-widget-shadow"
		},
		content:function(){

			//support:IE<9,OperainjQuery<1.7
			//.text()can'tacceptundefined,socoercetoastring
			vartitle=$(this).attr("title")||"";

			//Escapetitle,sincewe'regoingfromanattributetorawHTML
			return$("<a>").text(title).html();
		},
		hide:true,

		//Disabledelementshaveinconsistentbehavioracrossbrowsers(#8661)
		items:"[title]:not([disabled])",
		position:{
			my:"lefttop+15",
			at:"leftbottom",
			collision:"flipfitflip"
		},
		show:true,
		track:false,

		//Callbacks
		close:null,
		open:null
	},

	_addDescribedBy:function(elem,id){
		vardescribedby=(elem.attr("aria-describedby")||"").split(/\s+/);
		describedby.push(id);
		elem
			.data("ui-tooltip-id",id)
			.attr("aria-describedby",$.trim(describedby.join("")));
	},

	_removeDescribedBy:function(elem){
		varid=elem.data("ui-tooltip-id"),
			describedby=(elem.attr("aria-describedby")||"").split(/\s+/),
			index=$.inArray(id,describedby);

		if(index!==-1){
			describedby.splice(index,1);
		}

		elem.removeData("ui-tooltip-id");
		describedby=$.trim(describedby.join(""));
		if(describedby){
			elem.attr("aria-describedby",describedby);
		}else{
			elem.removeAttr("aria-describedby");
		}
	},

	_create:function(){
		this._on({
			mouseover:"open",
			focusin:"open"
		});

		//IDsofgeneratedtooltips,neededfordestroy
		this.tooltips={};

		//IDsofparenttooltipswhereweremovedthetitleattribute
		this.parents={};

		//Appendthearia-liveregionsotooltipsannouncecorrectly
		this.liveRegion=$("<div>")
			.attr({
				role:"log",
				"aria-live":"assertive",
				"aria-relevant":"additions"
			})
			.appendTo(this.document[0].body);
		this._addClass(this.liveRegion,null,"ui-helper-hidden-accessible");

		this.disabledTitles=$([]);
	},

	_setOption:function(key,value){
		varthat=this;

		this._super(key,value);

		if(key==="content"){
			$.each(this.tooltips,function(id,tooltipData){
				that._updateContent(tooltipData.element);
			});
		}
	},

	_setOptionDisabled:function(value){
		this[value?"_disable":"_enable"]();
	},

	_disable:function(){
		varthat=this;

		//Closeopentooltips
		$.each(this.tooltips,function(id,tooltipData){
			varevent=$.Event("blur");
			event.target=event.currentTarget=tooltipData.element[0];
			that.close(event,true);
		});

		//Removetitleattributestopreventnativetooltips
		this.disabledTitles=this.disabledTitles.add(
			this.element.find(this.options.items).addBack()
				.filter(function(){
					varelement=$(this);
					if(element.is("[title]")){
						returnelement
							.data("ui-tooltip-title",element.attr("title"))
							.removeAttr("title");
					}
				})
		);
	},

	_enable:function(){

		//restoretitleattributes
		this.disabledTitles.each(function(){
			varelement=$(this);
			if(element.data("ui-tooltip-title")){
				element.attr("title",element.data("ui-tooltip-title"));
			}
		});
		this.disabledTitles=$([]);
	},

	open:function(event){
		varthat=this,
			target=$(event?event.target:this.element)

				//weneedclosesthereduetomouseoverbubbling,
				//butalwayspointingatthesameeventtarget
				.closest(this.options.items);

		//Noelementtoshowatooltipfororthetooltipisalreadyopen
		if(!target.length||target.data("ui-tooltip-id")){
			return;
		}

		if(target.attr("title")){
			target.data("ui-tooltip-title",target.attr("title"));
		}

		target.data("ui-tooltip-open",true);

		//Killparenttooltips,customornative,forhover
		if(event&&event.type==="mouseover"){
			target.parents().each(function(){
				varparent=$(this),
					blurEvent;
				if(parent.data("ui-tooltip-open")){
					blurEvent=$.Event("blur");
					blurEvent.target=blurEvent.currentTarget=this;
					that.close(blurEvent,true);
				}
				if(parent.attr("title")){
					parent.uniqueId();
					that.parents[this.id]={
						element:this,
						title:parent.attr("title")
					};
					parent.attr("title","");
				}
			});
		}

		this._registerCloseHandlers(event,target);
		this._updateContent(target,event);
	},

	_updateContent:function(target,event){
		varcontent,
			contentOption=this.options.content,
			that=this,
			eventType=event?event.type:null;

		if(typeofcontentOption==="string"||contentOption.nodeType||
				contentOption.jquery){
			returnthis._open(event,target,contentOption);
		}

		content=contentOption.call(target[0],function(response){

			//IEmayinstantlyserveacachedresponseforajaxrequests
			//delaythiscallto_opensotheothercallto_openrunsfirst
			that._delay(function(){

				//Ignoreasyncresponseiftooltipwasclosedalready
				if(!target.data("ui-tooltip-open")){
					return;
				}

				//JQuerycreatesaspecialeventforfocusinwhenitdoesn't
				//existnatively.Toimproveperformance,thenativeevent
				//objectisreusedandthetypeischanged.Therefore,wecan't
				//relyonthetypebeingcorrectaftertheeventfinished
				//bubbling,sowesetitbacktothepreviousvalue.(#8740)
				if(event){
					event.type=eventType;
				}
				this._open(event,target,response);
			});
		});
		if(content){
			this._open(event,target,content);
		}
	},

	_open:function(event,target,content){
		vartooltipData,tooltip,delayedShow,a11yContent,
			positionOption=$.extend({},this.options.position);

		if(!content){
			return;
		}

		//Contentcanbeupdatedmultipletimes.Ifthetooltipalready
		//exists,thenjustupdatethecontentandbail.
		tooltipData=this._find(target);
		if(tooltipData){
			tooltipData.tooltip.find(".ui-tooltip-content").html(content);
			return;
		}

		//Ifwehaveatitle,clearittopreventthenativetooltip
		//wehavetocheckfirsttoavoiddefiningatitleifnoneexists
		//(wedon'twanttocauseanelementtostartmatching[title])
		//
		//WeuseremoveAttronlyforkeyevents,toallowIEtoexportthecorrect
		//accessibleattributes.Formouseevents,settoemptystringtoavoid
		//nativetooltipshowingup(happensonlywhenremovinginsidemouseover).
		if(target.is("[title]")){
			if(event&&event.type==="mouseover"){
				target.attr("title","");
			}else{
				target.removeAttr("title");
			}
		}

		tooltipData=this._tooltip(target);
		tooltip=tooltipData.tooltip;
		this._addDescribedBy(target,tooltip.attr("id"));
		tooltip.find(".ui-tooltip-content").html(content);

		//Support:VoiceoveronOSX,JAWSonIE<=9
		//JAWSannouncesdeletionsevenwhenaria-relevant="additions"
		//Voiceoverwillsometimesre-readtheentirelogregion'scontentsfromthebeginning
		this.liveRegion.children().hide();
		a11yContent=$("<div>").html(tooltip.find(".ui-tooltip-content").html());
		a11yContent.removeAttr("name").find("[name]").removeAttr("name");
		a11yContent.removeAttr("id").find("[id]").removeAttr("id");
		a11yContent.appendTo(this.liveRegion);

		functionposition(event){
			positionOption.of=event;
			if(tooltip.is(":hidden")){
				return;
			}
			tooltip.position(positionOption);
		}
		if(this.options.track&&event&&/^mouse/.test(event.type)){
			this._on(this.document,{
				mousemove:position
			});

			//triggeroncetooverrideelement-relativepositioning
			position(event);
		}else{
			tooltip.position($.extend({
				of:target
			},this.options.position));
		}

		tooltip.hide();

		this._show(tooltip,this.options.show);

		//Handletrackingtooltipsthatareshownwithadelay(#8644).Assoon
		//asthetooltipisvisible,positionthetooltipusingthemostrecent
		//event.
		//Addsthechecktoaddthetimersonlywhenbothdelayandtrackoptionsareset(#14682)
		if(this.options.track&&this.options.show&&this.options.show.delay){
			delayedShow=this.delayedShow=setInterval(function(){
				if(tooltip.is(":visible")){
					position(positionOption.of);
					clearInterval(delayedShow);
				}
			},$.fx.interval);
		}

		this._trigger("open",event,{tooltip:tooltip});
	},

	_registerCloseHandlers:function(event,target){
		varevents={
			keyup:function(event){
				if(event.keyCode===$.ui.keyCode.ESCAPE){
					varfakeEvent=$.Event(event);
					fakeEvent.currentTarget=target[0];
					this.close(fakeEvent,true);
				}
			}
		};

		//Onlybindremovehandlerfordelegatedtargets.Non-delegated
		//tooltipswillhandlethisindestroy.
		if(target[0]!==this.element[0]){
			events.remove=function(){
				this._removeTooltip(this._find(target).tooltip);
			};
		}

		if(!event||event.type==="mouseover"){
			events.mouseleave="close";
		}
		if(!event||event.type==="focusin"){
			events.focusout="close";
		}
		this._on(true,target,events);
	},

	close:function(event){
		vartooltip,
			that=this,
			target=$(event?event.currentTarget:this.element),
			tooltipData=this._find(target);

		//Thetooltipmayalreadybeclosed
		if(!tooltipData){

			//Wesetui-tooltip-openimmediatelyuponopen(inopen()),butonlysetthe
			//additionaldataoncethere'sactuallycontenttoshow(in_open()).Soevenifthe
			//tooltipdoesn'thavefulldata,wealwaysremoveui-tooltip-openincasewe'rein
			//theperiodbetweenopen()and_open().
			target.removeData("ui-tooltip-open");
			return;
		}

		tooltip=tooltipData.tooltip;

		//Disablingclosesthetooltip,soweneedtotrackwhenwe'reclosing
		//toavoidaninfiniteloopincasethetooltipbecomesdisabledonclose
		if(tooltipData.closing){
			return;
		}

		//Cleartheintervalfordelayedtrackingtooltips
		clearInterval(this.delayedShow);

		//Onlysettitleifwehadonebefore(seecommentin_open())
		//Ifthetitleattributehaschangedsinceopen(),don'trestore
		if(target.data("ui-tooltip-title")&&!target.attr("title")){
			target.attr("title",target.data("ui-tooltip-title"));
		}

		this._removeDescribedBy(target);

		tooltipData.hiding=true;
		tooltip.stop(true);
		this._hide(tooltip,this.options.hide,function(){
			that._removeTooltip($(this));
		});

		target.removeData("ui-tooltip-open");
		this._off(target,"mouseleavefocusoutkeyup");

		//Remove'remove'bindingonlyondelegatedtargets
		if(target[0]!==this.element[0]){
			this._off(target,"remove");
		}
		this._off(this.document,"mousemove");

		if(event&&event.type==="mouseleave"){
			$.each(this.parents,function(id,parent){
				$(parent.element).attr("title",parent.title);
				deletethat.parents[id];
			});
		}

		tooltipData.closing=true;
		this._trigger("close",event,{tooltip:tooltip});
		if(!tooltipData.hiding){
			tooltipData.closing=false;
		}
	},

	_tooltip:function(element){
		vartooltip=$("<div>").attr("role","tooltip"),
			content=$("<div>").appendTo(tooltip),
			id=tooltip.uniqueId().attr("id");

		this._addClass(content,"ui-tooltip-content");
		this._addClass(tooltip,"ui-tooltip","ui-widgetui-widget-content");

		tooltip.appendTo(this._appendTo(element));

		returnthis.tooltips[id]={
			element:element,
			tooltip:tooltip
		};
	},

	_find:function(target){
		varid=target.data("ui-tooltip-id");
		returnid?this.tooltips[id]:null;
	},

	_removeTooltip:function(tooltip){
		tooltip.remove();
		deletethis.tooltips[tooltip.attr("id")];
	},

	_appendTo:function(target){
		varelement=target.closest(".ui-front,dialog");

		if(!element.length){
			element=this.document[0].body;
		}

		returnelement;
	},

	_destroy:function(){
		varthat=this;

		//Closeopentooltips
		$.each(this.tooltips,function(id,tooltipData){

			//Delegatetoclosemethodtohandlecommoncleanup
			varevent=$.Event("blur"),
				element=tooltipData.element;
			event.target=event.currentTarget=element[0];
			that.close(event,true);

			//Removeimmediately;destroyinganopentooltipdoesn'tusethe
			//hideanimation
			$("#"+id).remove();

			//Restorethetitle
			if(element.data("ui-tooltip-title")){

				//Ifthetitleattributehaschangedsinceopen(),don'trestore
				if(!element.attr("title")){
					element.attr("title",element.data("ui-tooltip-title"));
				}
				element.removeData("ui-tooltip-title");
			}
		});
		this.liveRegion.remove();
	}
});

//DEPRECATED
//TODO:Switchreturnbacktowidgetdeclarationattopoffilewhenthisisremoved
if($.uiBackCompat!==false){

	//BackcompatfortooltipClassoption
	$.widget("ui.tooltip",$.ui.tooltip,{
		options:{
			tooltipClass:null
		},
		_tooltip:function(){
			vartooltipData=this._superApply(arguments);
			if(this.options.tooltipClass){
				tooltipData.tooltip.addClass(this.options.tooltipClass);
			}
			returntooltipData;
		}
	});
}

varwidgetsTooltip=$.ui.tooltip;


/*!
 *jQueryUIEffects1.12.1
 *http://jqueryui.com
 *
 *CopyrightjQueryFoundationandothercontributors
 *ReleasedundertheMITlicense.
 *http://jquery.org/license
 */

//>>label:EffectsCore
//>>group:Effects
//jscs:disablemaximumLineLength
//>>description:ExtendstheinternaljQueryeffects.Includesmorphingandeasing.Requiredbyallothereffects.
//jscs:enablemaximumLineLength
//>>docs:http://api.jqueryui.com/category/effects-core/
//>>demos:http://jqueryui.com/effect/



vardataSpace="ui-effects-",
	dataSpaceStyle="ui-effects-style",
	dataSpaceAnimated="ui-effects-animated",

	//CreatealocaljQuerybecausejQueryColorreliesonitandthe
	//globalmaynotexistwithAMDandacustombuild(#10199)
	jQuery=$;

$.effects={
	effect:{}
};

/*!
 *jQueryColorAnimationsv2.1.2
 *https://github.com/jquery/jquery-color
 *
 *Copyright2014jQueryFoundationandothercontributors
 *ReleasedundertheMITlicense.
 *http://jquery.org/license
 *
 *Date:WedJan1608:47:092013-0600
 */
(function(jQuery,undefined){

	varstepHooks="backgroundColorborderBottomColorborderLeftColorborderRightColor"+
		"borderTopColorcolorcolumnRuleColoroutlineColortextDecorationColortextEmphasisColor",

	//Plusequalstestfor+=100-=100
	rplusequals=/^([\-+])=\s*(\d+\.?\d*)/,

	//AsetofRE'sthatcanmatchstringsandgeneratecolortuples.
	stringParsers=[{
			re:/rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*(?:,\s*(\d?(?:\.\d+)?)\s*)?\)/,
			parse:function(execResult){
				return[
					execResult[1],
					execResult[2],
					execResult[3],
					execResult[4]
				];
			}
		},{
			re:/rgba?\(\s*(\d+(?:\.\d+)?)\%\s*,\s*(\d+(?:\.\d+)?)\%\s*,\s*(\d+(?:\.\d+)?)\%\s*(?:,\s*(\d?(?:\.\d+)?)\s*)?\)/,
			parse:function(execResult){
				return[
					execResult[1]*2.55,
					execResult[2]*2.55,
					execResult[3]*2.55,
					execResult[4]
				];
			}
		},{

			//ThisregexignoresA-Fbecauseit'scomparedagainstanalreadylowercasedstring
			re:/#([a-f0-9]{2})([a-f0-9]{2})([a-f0-9]{2})/,
			parse:function(execResult){
				return[
					parseInt(execResult[1],16),
					parseInt(execResult[2],16),
					parseInt(execResult[3],16)
				];
			}
		},{

			//ThisregexignoresA-Fbecauseit'scomparedagainstanalreadylowercasedstring
			re:/#([a-f0-9])([a-f0-9])([a-f0-9])/,
			parse:function(execResult){
				return[
					parseInt(execResult[1]+execResult[1],16),
					parseInt(execResult[2]+execResult[2],16),
					parseInt(execResult[3]+execResult[3],16)
				];
			}
		},{
			re:/hsla?\(\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)\%\s*,\s*(\d+(?:\.\d+)?)\%\s*(?:,\s*(\d?(?:\.\d+)?)\s*)?\)/,
			space:"hsla",
			parse:function(execResult){
				return[
					execResult[1],
					execResult[2]/100,
					execResult[3]/100,
					execResult[4]
				];
			}
		}],

	//JQuery.Color()
	color=jQuery.Color=function(color,green,blue,alpha){
		returnnewjQuery.Color.fn.parse(color,green,blue,alpha);
	},
	spaces={
		rgba:{
			props:{
				red:{
					idx:0,
					type:"byte"
				},
				green:{
					idx:1,
					type:"byte"
				},
				blue:{
					idx:2,
					type:"byte"
				}
			}
		},

		hsla:{
			props:{
				hue:{
					idx:0,
					type:"degrees"
				},
				saturation:{
					idx:1,
					type:"percent"
				},
				lightness:{
					idx:2,
					type:"percent"
				}
			}
		}
	},
	propTypes={
		"byte":{
			floor:true,
			max:255
		},
		"percent":{
			max:1
		},
		"degrees":{
			mod:360,
			floor:true
		}
	},
	support=color.support={},

	//Elementforsupporttests
	supportElem=jQuery("<p>")[0],

	//Colors=jQuery.Color.names
	colors,

	//Localaliasesoffunctionscalledoften
	each=jQuery.each;

//Determinergbasupportimmediately
supportElem.style.cssText="background-color:rgba(1,1,1,.5)";
support.rgba=supportElem.style.backgroundColor.indexOf("rgba")>-1;

//Definecachenameandalphaproperties
//forrgbaandhslaspaces
each(spaces,function(spaceName,space){
	space.cache="_"+spaceName;
	space.props.alpha={
		idx:3,
		type:"percent",
		def:1
	};
});

functionclamp(value,prop,allowEmpty){
	vartype=propTypes[prop.type]||{};

	if(value==null){
		return(allowEmpty||!prop.def)?null:prop.def;
	}

	//~~isanshortwayofdoingfloorforpositivenumbers
	value=type.floor?~~value:parseFloat(value);

	//IEwillpassinemptystringsasvalueforalpha,
	//whichwillhitthiscase
	if(isNaN(value)){
		returnprop.def;
	}

	if(type.mod){

		//Weaddmodbeforemoddingtomakesurethatnegativesvalues
		//getconvertedproperly:-10->350
		return(value+type.mod)%type.mod;
	}

	//Fornowallpropertytypeswithoutmodhaveminandmax
	return0>value?0:type.max<value?type.max:value;
}

functionstringParse(string){
	varinst=color(),
		rgba=inst._rgba=[];

	string=string.toLowerCase();

	each(stringParsers,function(i,parser){
		varparsed,
			match=parser.re.exec(string),
			values=match&&parser.parse(match),
			spaceName=parser.space||"rgba";

		if(values){
			parsed=inst[spaceName](values);

			//Ifthiswasanrgbaparsetheassignmentmighthappentwice
			//ohwell....
			inst[spaces[spaceName].cache]=parsed[spaces[spaceName].cache];
			rgba=inst._rgba=parsed._rgba;

			//Exiteach(stringParsers)herebecausewematched
			returnfalse;
		}
	});

	//FoundastringParserthathandledit
	if(rgba.length){

		//Ifthiscamefromaparsedstring,force"transparent"whenalphais0
		//chrome,(andmaybeothers)return"transparent"asrgba(0,0,0,0)
		if(rgba.join()==="0,0,0,0"){
			jQuery.extend(rgba,colors.transparent);
		}
		returninst;
	}

	//Namedcolors
	returncolors[string];
}

color.fn=jQuery.extend(color.prototype,{
	parse:function(red,green,blue,alpha){
		if(red===undefined){
			this._rgba=[null,null,null,null];
			returnthis;
		}
		if(red.jquery||red.nodeType){
			red=jQuery(red).css(green);
			green=undefined;
		}

		varinst=this,
			type=jQuery.type(red),
			rgba=this._rgba=[];

		//Morethan1argumentspecified-assume(red,green,blue,alpha)
		if(green!==undefined){
			red=[red,green,blue,alpha];
			type="array";
		}

		if(type==="string"){
			returnthis.parse(stringParse(red)||colors._default);
		}

		if(type==="array"){
			each(spaces.rgba.props,function(key,prop){
				rgba[prop.idx]=clamp(red[prop.idx],prop);
			});
			returnthis;
		}

		if(type==="object"){
			if(redinstanceofcolor){
				each(spaces,function(spaceName,space){
					if(red[space.cache]){
						inst[space.cache]=red[space.cache].slice();
					}
				});
			}else{
				each(spaces,function(spaceName,space){
					varcache=space.cache;
					each(space.props,function(key,prop){

						//Ifthecachedoesn'texist,andweknowhowtoconvert
						if(!inst[cache]&&space.to){

							//Ifthevaluewasnull,wedon'tneedtocopyit
							//ifthekeywasalpha,wedon'tneedtocopyiteither
							if(key==="alpha"||red[key]==null){
								return;
							}
							inst[cache]=space.to(inst._rgba);
						}

						//ThisistheonlycasewhereweallownullsforALLproperties.
						//callclampwithalwaysAllowEmpty
						inst[cache][prop.idx]=clamp(red[key],prop,true);
					});

					//Everythingdefinedbutalpha?
					if(inst[cache]&&
							jQuery.inArray(null,inst[cache].slice(0,3))<0){

						//Usethedefaultof1
						inst[cache][3]=1;
						if(space.from){
							inst._rgba=space.from(inst[cache]);
						}
					}
				});
			}
			returnthis;
		}
	},
	is:function(compare){
		varis=color(compare),
			same=true,
			inst=this;

		each(spaces,function(_,space){
			varlocalCache,
				isCache=is[space.cache];
			if(isCache){
				localCache=inst[space.cache]||space.to&&space.to(inst._rgba)||[];
				each(space.props,function(_,prop){
					if(isCache[prop.idx]!=null){
						same=(isCache[prop.idx]===localCache[prop.idx]);
						returnsame;
					}
				});
			}
			returnsame;
		});
		returnsame;
	},
	_space:function(){
		varused=[],
			inst=this;
		each(spaces,function(spaceName,space){
			if(inst[space.cache]){
				used.push(spaceName);
			}
		});
		returnused.pop();
	},
	transition:function(other,distance){
		varend=color(other),
			spaceName=end._space(),
			space=spaces[spaceName],
			startColor=this.alpha()===0?color("transparent"):this,
			start=startColor[space.cache]||space.to(startColor._rgba),
			result=start.slice();

		end=end[space.cache];
		each(space.props,function(key,prop){
			varindex=prop.idx,
				startValue=start[index],
				endValue=end[index],
				type=propTypes[prop.type]||{};

			//Ifnull,don'toverridestartvalue
			if(endValue===null){
				return;
			}

			//Ifnull-useend
			if(startValue===null){
				result[index]=endValue;
			}else{
				if(type.mod){
					if(endValue-startValue>type.mod/2){
						startValue+=type.mod;
					}elseif(startValue-endValue>type.mod/2){
						startValue-=type.mod;
					}
				}
				result[index]=clamp((endValue-startValue)*distance+startValue,prop);
			}
		});
		returnthis[spaceName](result);
	},
	blend:function(opaque){

		//Ifwearealreadyopaque-returnourself
		if(this._rgba[3]===1){
			returnthis;
		}

		varrgb=this._rgba.slice(),
			a=rgb.pop(),
			blend=color(opaque)._rgba;

		returncolor(jQuery.map(rgb,function(v,i){
			return(1-a)*blend[i]+a*v;
		}));
	},
	toRgbaString:function(){
		varprefix="rgba(",
			rgba=jQuery.map(this._rgba,function(v,i){
				returnv==null?(i>2?1:0):v;
			});

		if(rgba[3]===1){
			rgba.pop();
			prefix="rgb(";
		}

		returnprefix+rgba.join()+")";
	},
	toHslaString:function(){
		varprefix="hsla(",
			hsla=jQuery.map(this.hsla(),function(v,i){
				if(v==null){
					v=i>2?1:0;
				}

				//Catch1and2
				if(i&&i<3){
					v=Math.round(v*100)+"%";
				}
				returnv;
			});

		if(hsla[3]===1){
			hsla.pop();
			prefix="hsl(";
		}
		returnprefix+hsla.join()+")";
	},
	toHexString:function(includeAlpha){
		varrgba=this._rgba.slice(),
			alpha=rgba.pop();

		if(includeAlpha){
			rgba.push(~~(alpha*255));
		}

		return"#"+jQuery.map(rgba,function(v){

			//Defaultto0whennullsexist
			v=(v||0).toString(16);
			returnv.length===1?"0"+v:v;
		}).join("");
	},
	toString:function(){
		returnthis._rgba[3]===0?"transparent":this.toRgbaString();
	}
});
color.fn.parse.prototype=color.fn;

//Hslaconversionsadaptedfrom:
//https://code.google.com/p/maashaack/source/browse/packages/graphics/trunk/src/graphics/colors/HUE2RGB.as?r=5021

functionhue2rgb(p,q,h){
	h=(h+1)%1;
	if(h*6<1){
		returnp+(q-p)*h*6;
	}
	if(h*2<1){
		returnq;
	}
	if(h*3<2){
		returnp+(q-p)*((2/3)-h)*6;
	}
	returnp;
}

spaces.hsla.to=function(rgba){
	if(rgba[0]==null||rgba[1]==null||rgba[2]==null){
		return[null,null,null,rgba[3]];
	}
	varr=rgba[0]/255,
		g=rgba[1]/255,
		b=rgba[2]/255,
		a=rgba[3],
		max=Math.max(r,g,b),
		min=Math.min(r,g,b),
		diff=max-min,
		add=max+min,
		l=add*0.5,
		h,s;

	if(min===max){
		h=0;
	}elseif(r===max){
		h=(60*(g-b)/diff)+360;
	}elseif(g===max){
		h=(60*(b-r)/diff)+120;
	}else{
		h=(60*(r-g)/diff)+240;
	}

	//Chroma(diff)==0meansgreyscalewhich,bydefinition,saturation=0%
	//otherwise,saturationisbasedontheratioofchroma(diff)tolightness(add)
	if(diff===0){
		s=0;
	}elseif(l<=0.5){
		s=diff/add;
	}else{
		s=diff/(2-add);
	}
	return[Math.round(h)%360,s,l,a==null?1:a];
};

spaces.hsla.from=function(hsla){
	if(hsla[0]==null||hsla[1]==null||hsla[2]==null){
		return[null,null,null,hsla[3]];
	}
	varh=hsla[0]/360,
		s=hsla[1],
		l=hsla[2],
		a=hsla[3],
		q=l<=0.5?l*(1+s):l+s-l*s,
		p=2*l-q;

	return[
		Math.round(hue2rgb(p,q,h+(1/3))*255),
		Math.round(hue2rgb(p,q,h)*255),
		Math.round(hue2rgb(p,q,h-(1/3))*255),
		a
	];
};

each(spaces,function(spaceName,space){
	varprops=space.props,
		cache=space.cache,
		to=space.to,
		from=space.from;

	//Makesrgba()andhsla()
	color.fn[spaceName]=function(value){

		//Generateacacheforthisspaceifitdoesn'texist
		if(to&&!this[cache]){
			this[cache]=to(this._rgba);
		}
		if(value===undefined){
			returnthis[cache].slice();
		}

		varret,
			type=jQuery.type(value),
			arr=(type==="array"||type==="object")?value:arguments,
			local=this[cache].slice();

		each(props,function(key,prop){
			varval=arr[type==="object"?key:prop.idx];
			if(val==null){
				val=local[prop.idx];
			}
			local[prop.idx]=clamp(val,prop);
		});

		if(from){
			ret=color(from(local));
			ret[cache]=local;
			returnret;
		}else{
			returncolor(local);
		}
	};

	//Makesred()green()blue()alpha()hue()saturation()lightness()
	each(props,function(key,prop){

		//Alphaisincludedinmorethanonespace
		if(color.fn[key]){
			return;
		}
		color.fn[key]=function(value){
			varvtype=jQuery.type(value),
				fn=(key==="alpha"?(this._hsla?"hsla":"rgba"):spaceName),
				local=this[fn](),
				cur=local[prop.idx],
				match;

			if(vtype==="undefined"){
				returncur;
			}

			if(vtype==="function"){
				value=value.call(this,cur);
				vtype=jQuery.type(value);
			}
			if(value==null&&prop.empty){
				returnthis;
			}
			if(vtype==="string"){
				match=rplusequals.exec(value);
				if(match){
					value=cur+parseFloat(match[2])*(match[1]==="+"?1:-1);
				}
			}
			local[prop.idx]=value;
			returnthis[fn](local);
		};
	});
});

//AddcssHookand.fx.stepfunctionforeachnamedhook.
//acceptaspaceseparatedstringofproperties
color.hook=function(hook){
	varhooks=hook.split("");
	each(hooks,function(i,hook){
		jQuery.cssHooks[hook]={
			set:function(elem,value){
				varparsed,curElem,
					backgroundColor="";

				if(value!=="transparent"&&(jQuery.type(value)!=="string"||
						(parsed=stringParse(value)))){
					value=color(parsed||value);
					if(!support.rgba&&value._rgba[3]!==1){
						curElem=hook==="backgroundColor"?elem.parentNode:elem;
						while(
							(backgroundColor===""||backgroundColor==="transparent")&&
							curElem&&curElem.style
						){
							try{
								backgroundColor=jQuery.css(curElem,"backgroundColor");
								curElem=curElem.parentNode;
							}catch(e){
							}
						}

						value=value.blend(backgroundColor&&backgroundColor!=="transparent"?
							backgroundColor:
							"_default");
					}

					value=value.toRgbaString();
				}
				try{
					elem.style[hook]=value;
				}catch(e){

					//WrappedtopreventIEfromthrowingerrorson"invalid"valueslike
					//'auto'or'inherit'
				}
			}
		};
		jQuery.fx.step[hook]=function(fx){
			if(!fx.colorInit){
				fx.start=color(fx.elem,hook);
				fx.end=color(fx.end);
				fx.colorInit=true;
			}
			jQuery.cssHooks[hook].set(fx.elem,fx.start.transition(fx.end,fx.pos));
		};
	});

};

color.hook(stepHooks);

jQuery.cssHooks.borderColor={
	expand:function(value){
		varexpanded={};

		each(["Top","Right","Bottom","Left"],function(i,part){
			expanded["border"+part+"Color"]=value;
		});
		returnexpanded;
	}
};

//Basiccolornamesonly.
//Usageofanyoftheothercolornamesrequiresaddingyourselforincluding
//jquery.color.svg-names.js.
colors=jQuery.Color.names={

	//4.1.Basiccolorkeywords
	aqua:"#00ffff",
	black:"#000000",
	blue:"#0000ff",
	fuchsia:"#ff00ff",
	gray:"#808080",
	green:"#008000",
	lime:"#00ff00",
	maroon:"#800000",
	navy:"#000080",
	olive:"#808000",
	purple:"#800080",
	red:"#ff0000",
	silver:"#c0c0c0",
	teal:"#008080",
	white:"#ffffff",
	yellow:"#ffff00",

	//4.2.3."transparent"colorkeyword
	transparent:[null,null,null,0],

	_default:"#ffffff"
};

})(jQuery);

/******************************************************************************/
/******************************CLASSANIMATIONS******************************/
/******************************************************************************/
(function(){

varclassAnimationActions=["add","remove","toggle"],
	shorthandStyles={
		border:1,
		borderBottom:1,
		borderColor:1,
		borderLeft:1,
		borderRight:1,
		borderTop:1,
		borderWidth:1,
		margin:1,
		padding:1
	};

$.each(
	["borderLeftStyle","borderRightStyle","borderBottomStyle","borderTopStyle"],
	function(_,prop){
		$.fx.step[prop]=function(fx){
			if(fx.end!=="none"&&!fx.setAttr||fx.pos===1&&!fx.setAttr){
				jQuery.style(fx.elem,prop,fx.end);
				fx.setAttr=true;
			}
		};
	}
);

functiongetElementStyles(elem){
	varkey,len,
		style=elem.ownerDocument.defaultView?
			elem.ownerDocument.defaultView.getComputedStyle(elem,null):
			elem.currentStyle,
		styles={};

	if(style&&style.length&&style[0]&&style[style[0]]){
		len=style.length;
		while(len--){
			key=style[len];
			if(typeofstyle[key]==="string"){
				styles[$.camelCase(key)]=style[key];
			}
		}

	//Support:Opera,IE<9
	}else{
		for(keyinstyle){
			if(typeofstyle[key]==="string"){
				styles[key]=style[key];
			}
		}
	}

	returnstyles;
}

functionstyleDifference(oldStyle,newStyle){
	vardiff={},
		name,value;

	for(nameinnewStyle){
		value=newStyle[name];
		if(oldStyle[name]!==value){
			if(!shorthandStyles[name]){
				if($.fx.step[name]||!isNaN(parseFloat(value))){
					diff[name]=value;
				}
			}
		}
	}

	returndiff;
}

//Support:jQuery<1.8
if(!$.fn.addBack){
	$.fn.addBack=function(selector){
		returnthis.add(selector==null?
			this.prevObject:this.prevObject.filter(selector)
		);
	};
}

$.effects.animateClass=function(value,duration,easing,callback){
	varo=$.speed(duration,easing,callback);

	returnthis.queue(function(){
		varanimated=$(this),
			baseClass=animated.attr("class")||"",
			applyClassChange,
			allAnimations=o.children?animated.find("*").addBack():animated;

		//Maptheanimatedobjectstostoretheoriginalstyles.
		allAnimations=allAnimations.map(function(){
			varel=$(this);
			return{
				el:el,
				start:getElementStyles(this)
			};
		});

		//Applyclasschange
		applyClassChange=function(){
			$.each(classAnimationActions,function(i,action){
				if(value[action]){
					animated[action+"Class"](value[action]);
				}
			});
		};
		applyClassChange();

		//Mapallanimatedobjectsagain-calculatenewstylesanddiff
		allAnimations=allAnimations.map(function(){
			this.end=getElementStyles(this.el[0]);
			this.diff=styleDifference(this.start,this.end);
			returnthis;
		});

		//Applyoriginalclass
		animated.attr("class",baseClass);

		//Mapallanimatedobjectsagain-thistimecollectingapromise
		allAnimations=allAnimations.map(function(){
			varstyleInfo=this,
				dfd=$.Deferred(),
				opts=$.extend({},o,{
					queue:false,
					complete:function(){
						dfd.resolve(styleInfo);
					}
				});

			this.el.animate(this.diff,opts);
			returndfd.promise();
		});

		//Onceallanimationshavecompleted:
		$.when.apply($,allAnimations.get()).done(function(){

			//Setthefinalclass
			applyClassChange();

			//Foreachanimatedelement,
			//clearallcsspropertiesthatwereanimated
			$.each(arguments,function(){
				varel=this.el;
				$.each(this.diff,function(key){
					el.css(key,"");
				});
			});

			//ThisisguarnteedtobethereifyouusejQuery.speed()
			//italsohandlesdequeuingthenextanim...
			o.complete.call(animated[0]);
		});
	});
};

$.fn.extend({
	addClass:(function(orig){
		returnfunction(classNames,speed,easing,callback){
			returnspeed?
				$.effects.animateClass.call(this,
					{add:classNames},speed,easing,callback):
				orig.apply(this,arguments);
		};
	})($.fn.addClass),

	removeClass:(function(orig){
		returnfunction(classNames,speed,easing,callback){
			returnarguments.length>1?
				$.effects.animateClass.call(this,
					{remove:classNames},speed,easing,callback):
				orig.apply(this,arguments);
		};
	})($.fn.removeClass),

	toggleClass:(function(orig){
		returnfunction(classNames,force,speed,easing,callback){
			if(typeofforce==="boolean"||force===undefined){
				if(!speed){

					//Withoutspeedparameter
					returnorig.apply(this,arguments);
				}else{
					return$.effects.animateClass.call(this,
						(force?{add:classNames}:{remove:classNames}),
						speed,easing,callback);
				}
			}else{

				//Withoutforceparameter
				return$.effects.animateClass.call(this,
					{toggle:classNames},force,speed,easing);
			}
		};
	})($.fn.toggleClass),

	switchClass:function(remove,add,speed,easing,callback){
		return$.effects.animateClass.call(this,{
			add:add,
			remove:remove
		},speed,easing,callback);
	}
});

})();

/******************************************************************************/
/***********************************EFFECTS**********************************/
/******************************************************************************/

(function(){

if($.expr&&$.expr.filters&&$.expr.filters.animated){
	$.expr.filters.animated=(function(orig){
		returnfunction(elem){
			return!!$(elem).data(dataSpaceAnimated)||orig(elem);
		};
	})($.expr.filters.animated);
}

if($.uiBackCompat!==false){
	$.extend($.effects,{

		//Savesasetofpropertiesinadatastorage
		save:function(element,set){
			vari=0,length=set.length;
			for(;i<length;i++){
				if(set[i]!==null){
					element.data(dataSpace+set[i],element[0].style[set[i]]);
				}
			}
		},

		//Restoresasetofpreviouslysavedpropertiesfromadatastorage
		restore:function(element,set){
			varval,i=0,length=set.length;
			for(;i<length;i++){
				if(set[i]!==null){
					val=element.data(dataSpace+set[i]);
					element.css(set[i],val);
				}
			}
		},

		setMode:function(el,mode){
			if(mode==="toggle"){
				mode=el.is(":hidden")?"show":"hide";
			}
			returnmode;
		},

		//Wrapstheelementaroundawrapperthatcopiespositionproperties
		createWrapper:function(element){

			//Iftheelementisalreadywrapped,returnit
			if(element.parent().is(".ui-effects-wrapper")){
				returnelement.parent();
			}

			//Wraptheelement
			varprops={
					width:element.outerWidth(true),
					height:element.outerHeight(true),
					"float":element.css("float")
				},
				wrapper=$("<div></div>")
					.addClass("ui-effects-wrapper")
					.css({
						fontSize:"100%",
						background:"transparent",
						border:"none",
						margin:0,
						padding:0
					}),

				//Storethesizeincasewidth/heightaredefinedin%-Fixes#5245
				size={
					width:element.width(),
					height:element.height()
				},
				active=document.activeElement;

			//Support:Firefox
			//Firefoxincorrectlyexposesanonymouscontent
			//https://bugzilla.mozilla.org/show_bug.cgi?id=561664
			try{
				active.id;
			}catch(e){
				active=document.body;
			}

			element.wrap(wrapper);

			//Fixes#7595-Elementslosefocuswhenwrapped.
			if(element[0]===active||$.contains(element[0],active)){
				$(active).trigger("focus");
			}

			//HotfixforjQuery1.4sincesomechangeinwrap()seemstoactually
			//losethereferencetothewrappedelement
			wrapper=element.parent();

			//Transferpositioningpropertiestothewrapper
			if(element.css("position")==="static"){
				wrapper.css({position:"relative"});
				element.css({position:"relative"});
			}else{
				$.extend(props,{
					position:element.css("position"),
					zIndex:element.css("z-index")
				});
				$.each(["top","left","bottom","right"],function(i,pos){
					props[pos]=element.css(pos);
					if(isNaN(parseInt(props[pos],10))){
						props[pos]="auto";
					}
				});
				element.css({
					position:"relative",
					top:0,
					left:0,
					right:"auto",
					bottom:"auto"
				});
			}
			element.css(size);

			returnwrapper.css(props).show();
		},

		removeWrapper:function(element){
			varactive=document.activeElement;

			if(element.parent().is(".ui-effects-wrapper")){
				element.parent().replaceWith(element);

				//Fixes#7595-Elementslosefocuswhenwrapped.
				if(element[0]===active||$.contains(element[0],active)){
					$(active).trigger("focus");
				}
			}

			returnelement;
		}
	});
}

$.extend($.effects,{
	version:"1.12.1",

	define:function(name,mode,effect){
		if(!effect){
			effect=mode;
			mode="effect";
		}

		$.effects.effect[name]=effect;
		$.effects.effect[name].mode=mode;

		returneffect;
	},

	scaledDimensions:function(element,percent,direction){
		if(percent===0){
			return{
				height:0,
				width:0,
				outerHeight:0,
				outerWidth:0
			};
		}

		varx=direction!=="horizontal"?((percent||100)/100):1,
			y=direction!=="vertical"?((percent||100)/100):1;

		return{
			height:element.height()*y,
			width:element.width()*x,
			outerHeight:element.outerHeight()*y,
			outerWidth:element.outerWidth()*x
		};

	},

	clipToBox:function(animation){
		return{
			width:animation.clip.right-animation.clip.left,
			height:animation.clip.bottom-animation.clip.top,
			left:animation.clip.left,
			top:animation.clip.top
		};
	},

	//Injectsrecentlyqueuedfunctionstobefirstinline(after"inprogress")
	unshift:function(element,queueLength,count){
		varqueue=element.queue();

		if(queueLength>1){
			queue.splice.apply(queue,
				[1,0].concat(queue.splice(queueLength,count)));
		}
		element.dequeue();
	},

	saveStyle:function(element){
		element.data(dataSpaceStyle,element[0].style.cssText);
	},

	restoreStyle:function(element){
		element[0].style.cssText=element.data(dataSpaceStyle)||"";
		element.removeData(dataSpaceStyle);
	},

	mode:function(element,mode){
		varhidden=element.is(":hidden");

		if(mode==="toggle"){
			mode=hidden?"show":"hide";
		}
		if(hidden?mode==="hide":mode==="show"){
			mode="none";
		}
		returnmode;
	},

	//Translatesa[top,left]arrayintoabaselinevalue
	getBaseline:function(origin,original){
		vary,x;

		switch(origin[0]){
		case"top":
			y=0;
			break;
		case"middle":
			y=0.5;
			break;
		case"bottom":
			y=1;
			break;
		default:
			y=origin[0]/original.height;
		}

		switch(origin[1]){
		case"left":
			x=0;
			break;
		case"center":
			x=0.5;
			break;
		case"right":
			x=1;
			break;
		default:
			x=origin[1]/original.width;
		}

		return{
			x:x,
			y:y
		};
	},

	//Createsaplaceholderelementsothattheoriginalelementcanbemadeabsolute
	createPlaceholder:function(element){
		varplaceholder,
			cssPosition=element.css("position"),
			position=element.position();

		//Lockinmarginsfirsttoaccountforformelements,which
		//willchangemarginifyouexplicitlysetheight
		//see:http://jsfiddle.net/JZSMt/3/https://bugs.webkit.org/show_bug.cgi?id=107380
		//Support:Safari
		element.css({
			marginTop:element.css("marginTop"),
			marginBottom:element.css("marginBottom"),
			marginLeft:element.css("marginLeft"),
			marginRight:element.css("marginRight")
		})
		.outerWidth(element.outerWidth())
		.outerHeight(element.outerHeight());

		if(/^(static|relative)/.test(cssPosition)){
			cssPosition="absolute";

			placeholder=$("<"+element[0].nodeName+">").insertAfter(element).css({

				//Convertinlinetoinlineblocktoaccountforinlineelements
				//thatturntoinlineblockbasedoncontent(likeimg)
				display:/^(inline|ruby)/.test(element.css("display"))?
					"inline-block":
					"block",
				visibility:"hidden",

				//Marginsneedtobesettoaccountformargincollapse
				marginTop:element.css("marginTop"),
				marginBottom:element.css("marginBottom"),
				marginLeft:element.css("marginLeft"),
				marginRight:element.css("marginRight"),
				"float":element.css("float")
			})
			.outerWidth(element.outerWidth())
			.outerHeight(element.outerHeight())
			.addClass("ui-effects-placeholder");

			element.data(dataSpace+"placeholder",placeholder);
		}

		element.css({
			position:cssPosition,
			left:position.left,
			top:position.top
		});

		returnplaceholder;
	},

	removePlaceholder:function(element){
		vardataKey=dataSpace+"placeholder",
				placeholder=element.data(dataKey);

		if(placeholder){
			placeholder.remove();
			element.removeData(dataKey);
		}
	},

	//Removesaplaceholderifitexistsandrestores
	//propertiesthatweremodifiedduringplaceholdercreation
	cleanUp:function(element){
		$.effects.restoreStyle(element);
		$.effects.removePlaceholder(element);
	},

	setTransition:function(element,list,factor,value){
		value=value||{};
		$.each(list,function(i,x){
			varunit=element.cssUnit(x);
			if(unit[0]>0){
				value[x]=unit[0]*factor+unit[1];
			}
		});
		returnvalue;
	}
});

//Returnaneffectoptionsobjectforthegivenparameters:
function_normalizeArguments(effect,options,speed,callback){

	//Allowpassingalloptionsasthefirstparameter
	if($.isPlainObject(effect)){
		options=effect;
		effect=effect.effect;
	}

	//Converttoanobject
	effect={effect:effect};

	//Catch(effect,null,...)
	if(options==null){
		options={};
	}

	//Catch(effect,callback)
	if($.isFunction(options)){
		callback=options;
		speed=null;
		options={};
	}

	//Catch(effect,speed,?)
	if(typeofoptions==="number"||$.fx.speeds[options]){
		callback=speed;
		speed=options;
		options={};
	}

	//Catch(effect,options,callback)
	if($.isFunction(speed)){
		callback=speed;
		speed=null;
	}

	//Addoptionstoeffect
	if(options){
		$.extend(effect,options);
	}

	speed=speed||options.duration;
	effect.duration=$.fx.off?0:
		typeofspeed==="number"?speed:
		speedin$.fx.speeds?$.fx.speeds[speed]:
		$.fx.speeds._default;

	effect.complete=callback||options.complete;

	returneffect;
}

functionstandardAnimationOption(option){

	//Validstandardspeeds(nothing,number,namedspeed)
	if(!option||typeofoption==="number"||$.fx.speeds[option]){
		returntrue;
	}

	//Invalidstrings-treatas"normal"speed
	if(typeofoption==="string"&&!$.effects.effect[option]){
		returntrue;
	}

	//Completecallback
	if($.isFunction(option)){
		returntrue;
	}

	//Optionshash(butnotnaminganeffect)
	if(typeofoption==="object"&&!option.effect){
		returntrue;
	}

	//Didn'tmatchanystandardAPI
	returnfalse;
}

$.fn.extend({
	effect:function(/*effect,options,speed,callback*/){
		varargs=_normalizeArguments.apply(this,arguments),
			effectMethod=$.effects.effect[args.effect],
			defaultMode=effectMethod.mode,
			queue=args.queue,
			queueName=queue||"fx",
			complete=args.complete,
			mode=args.mode,
			modes=[],
			prefilter=function(next){
				varel=$(this),
					normalizedMode=$.effects.mode(el,mode)||defaultMode;

				//Sentinelforduck-punchingthe:animatedpsuedo-selector
				el.data(dataSpaceAnimated,true);

				//Saveeffectmodeforlateruse,
				//wecan'tjustcall$.effects.modeagainlater,
				//asthe.show()belowdestroystheinitialstate
				modes.push(normalizedMode);

				//See$.uiBackCompatinsideofrun()forremovalofdefaultModein1.13
				if(defaultMode&&(normalizedMode==="show"||
						(normalizedMode===defaultMode&&normalizedMode==="hide"))){
					el.show();
				}

				if(!defaultMode||normalizedMode!=="none"){
					$.effects.saveStyle(el);
				}

				if($.isFunction(next)){
					next();
				}
			};

		if($.fx.off||!effectMethod){

			//Delegatetotheoriginalmethod(e.g.,.show())ifpossible
			if(mode){
				returnthis[mode](args.duration,complete);
			}else{
				returnthis.each(function(){
					if(complete){
						complete.call(this);
					}
				});
			}
		}

		functionrun(next){
			varelem=$(this);

			functioncleanup(){
				elem.removeData(dataSpaceAnimated);

				$.effects.cleanUp(elem);

				if(args.mode==="hide"){
					elem.hide();
				}

				done();
			}

			functiondone(){
				if($.isFunction(complete)){
					complete.call(elem[0]);
				}

				if($.isFunction(next)){
					next();
				}
			}

			//Overridemodeoptiononaperelementbasis,
			//astogglecanbeeithershoworhidedependingonelementstate
			args.mode=modes.shift();

			if($.uiBackCompat!==false&&!defaultMode){
				if(elem.is(":hidden")?mode==="hide":mode==="show"){

					//Callthecoremethodtotrack"olddisplay"properly
					elem[mode]();
					done();
				}else{
					effectMethod.call(elem[0],args,done);
				}
			}else{
				if(args.mode==="none"){

					//Callthecoremethodtotrack"olddisplay"properly
					elem[mode]();
					done();
				}else{
					effectMethod.call(elem[0],args,cleanup);
				}
			}
		}

		//Runprefilteronallelementsfirsttoensurethat
		//anyshowingorhidinghappensbeforeplaceholdercreation,
		//whichensuresthatanylayoutchangesarecorrectlycaptured.
		returnqueue===false?
			this.each(prefilter).each(run):
			this.queue(queueName,prefilter).queue(queueName,run);
	},

	show:(function(orig){
		returnfunction(option){
			if(standardAnimationOption(option)){
				returnorig.apply(this,arguments);
			}else{
				varargs=_normalizeArguments.apply(this,arguments);
				args.mode="show";
				returnthis.effect.call(this,args);
			}
		};
	})($.fn.show),

	hide:(function(orig){
		returnfunction(option){
			if(standardAnimationOption(option)){
				returnorig.apply(this,arguments);
			}else{
				varargs=_normalizeArguments.apply(this,arguments);
				args.mode="hide";
				returnthis.effect.call(this,args);
			}
		};
	})($.fn.hide),

	toggle:(function(orig){
		returnfunction(option){
			if(standardAnimationOption(option)||typeofoption==="boolean"){
				returnorig.apply(this,arguments);
			}else{
				varargs=_normalizeArguments.apply(this,arguments);
				args.mode="toggle";
				returnthis.effect.call(this,args);
			}
		};
	})($.fn.toggle),

	cssUnit:function(key){
		varstyle=this.css(key),
			val=[];

		$.each(["em","px","%","pt"],function(i,unit){
			if(style.indexOf(unit)>0){
				val=[parseFloat(style),unit];
			}
		});
		returnval;
	},

	cssClip:function(clipObj){
		if(clipObj){
			returnthis.css("clip","rect("+clipObj.top+"px"+clipObj.right+"px"+
				clipObj.bottom+"px"+clipObj.left+"px)");
		}
		returnparseClip(this.css("clip"),this);
	},

	transfer:function(options,done){
		varelement=$(this),
			target=$(options.to),
			targetFixed=target.css("position")==="fixed",
			body=$("body"),
			fixTop=targetFixed?body.scrollTop():0,
			fixLeft=targetFixed?body.scrollLeft():0,
			endPosition=target.offset(),
			animation={
				top:endPosition.top-fixTop,
				left:endPosition.left-fixLeft,
				height:target.innerHeight(),
				width:target.innerWidth()
			},
			startPosition=element.offset(),
			transfer=$("<divclass='ui-effects-transfer'></div>")
				.appendTo("body")
				.addClass(options.className)
				.css({
					top:startPosition.top-fixTop,
					left:startPosition.left-fixLeft,
					height:element.innerHeight(),
					width:element.innerWidth(),
					position:targetFixed?"fixed":"absolute"
				})
				.animate(animation,options.duration,options.easing,function(){
					transfer.remove();
					if($.isFunction(done)){
						done();
					}
				});
	}
});

functionparseClip(str,element){
		varouterWidth=element.outerWidth(),
			outerHeight=element.outerHeight(),
			clipRegex=/^rect\((-?\d*\.?\d*px|-?\d+%|auto),?\s*(-?\d*\.?\d*px|-?\d+%|auto),?\s*(-?\d*\.?\d*px|-?\d+%|auto),?\s*(-?\d*\.?\d*px|-?\d+%|auto)\)$/,
			values=clipRegex.exec(str)||["",0,outerWidth,outerHeight,0];

		return{
			top:parseFloat(values[1])||0,
			right:values[2]==="auto"?outerWidth:parseFloat(values[2]),
			bottom:values[3]==="auto"?outerHeight:parseFloat(values[3]),
			left:parseFloat(values[4])||0
		};
}

$.fx.step.clip=function(fx){
	if(!fx.clipInit){
		fx.start=$(fx.elem).cssClip();
		if(typeoffx.end==="string"){
			fx.end=parseClip(fx.end,fx.elem);
		}
		fx.clipInit=true;
	}

	$(fx.elem).cssClip({
		top:fx.pos*(fx.end.top-fx.start.top)+fx.start.top,
		right:fx.pos*(fx.end.right-fx.start.right)+fx.start.right,
		bottom:fx.pos*(fx.end.bottom-fx.start.bottom)+fx.start.bottom,
		left:fx.pos*(fx.end.left-fx.start.left)+fx.start.left
	});
};

})();

/******************************************************************************/
/***********************************EASING***********************************/
/******************************************************************************/

(function(){

//BasedoneasingequationsfromRobertPenner(http://www.robertpenner.com/easing)

varbaseEasings={};

$.each(["Quad","Cubic","Quart","Quint","Expo"],function(i,name){
	baseEasings[name]=function(p){
		returnMath.pow(p,i+2);
	};
});

$.extend(baseEasings,{
	Sine:function(p){
		return1-Math.cos(p*Math.PI/2);
	},
	Circ:function(p){
		return1-Math.sqrt(1-p*p);
	},
	Elastic:function(p){
		returnp===0||p===1?p:
			-Math.pow(2,8*(p-1))*Math.sin(((p-1)*80-7.5)*Math.PI/15);
	},
	Back:function(p){
		returnp*p*(3*p-2);
	},
	Bounce:function(p){
		varpow2,
			bounce=4;

		while(p<((pow2=Math.pow(2,--bounce))-1)/11){}
		return1/Math.pow(4,3-bounce)-7.5625*Math.pow((pow2*3-2)/22-p,2);
	}
});

$.each(baseEasings,function(name,easeIn){
	$.easing["easeIn"+name]=easeIn;
	$.easing["easeOut"+name]=function(p){
		return1-easeIn(1-p);
	};
	$.easing["easeInOut"+name]=function(p){
		returnp<0.5?
			easeIn(p*2)/2:
			1-easeIn(p*-2+2)/2;
	};
});

})();

vareffect=$.effects;


/*!
 *jQueryUIEffectsBounce1.12.1
 *http://jqueryui.com
 *
 *CopyrightjQueryFoundationandothercontributors
 *ReleasedundertheMITlicense.
 *http://jquery.org/license
 */

//>>label:BounceEffect
//>>group:Effects
//>>description:Bouncesanelementhorizontallyorverticallyntimes.
//>>docs:http://api.jqueryui.com/bounce-effect/
//>>demos:http://jqueryui.com/effect/



vareffectsEffectBounce=$.effects.define("bounce",function(options,done){
	varupAnim,downAnim,refValue,
		element=$(this),

		//Defaults:
		mode=options.mode,
		hide=mode==="hide",
		show=mode==="show",
		direction=options.direction||"up",
		distance=options.distance,
		times=options.times||5,

		//Numberofinternalanimations
		anims=times*2+(show||hide?1:0),
		speed=options.duration/anims,
		easing=options.easing,

		//Utility:
		ref=(direction==="up"||direction==="down")?"top":"left",
		motion=(direction==="up"||direction==="left"),
		i=0,

		queuelen=element.queue().length;

	$.effects.createPlaceholder(element);

	refValue=element.css(ref);

	//DefaultdistancefortheBIGGESTbounceistheouterDistance/3
	if(!distance){
		distance=element[ref==="top"?"outerHeight":"outerWidth"]()/3;
	}

	if(show){
		downAnim={opacity:1};
		downAnim[ref]=refValue;

		//Ifweareshowing,forceopacity0andsettheinitialposition
		//thendothe"first"animation
		element
			.css("opacity",0)
			.css(ref,motion?-distance*2:distance*2)
			.animate(downAnim,speed,easing);
	}

	//Startatthesmallestdistanceifwearehiding
	if(hide){
		distance=distance/Math.pow(2,times-1);
	}

	downAnim={};
	downAnim[ref]=refValue;

	//Bouncesup/down/left/rightthenbackto0--times*2animationshappenhere
	for(;i<times;i++){
		upAnim={};
		upAnim[ref]=(motion?"-=":"+=")+distance;

		element
			.animate(upAnim,speed,easing)
			.animate(downAnim,speed,easing);

		distance=hide?distance*2:distance/2;
	}

	//LastBouncewhenHiding
	if(hide){
		upAnim={opacity:0};
		upAnim[ref]=(motion?"-=":"+=")+distance;

		element.animate(upAnim,speed,easing);
	}

	element.queue(done);

	$.effects.unshift(element,queuelen,anims+1);
});




}));