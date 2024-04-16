/*!
 *clipboard.jsv2.0.0
 *https://zenorocha.github.io/clipboard.js
 *
 *LicensedMIT©ZenoRocha
 */
(functionwebpackUniversalModuleDefinition(root,factory){
	if(typeofexports==='object'&&typeofmodule==='object')
		module.exports=factory();
	elseif(typeofdefine==='function'&&define.amd)
		define([],factory);
	elseif(typeofexports==='object')
		exports["ClipboardJS"]=factory();
	else
		root["ClipboardJS"]=factory();
})(this,function(){
return/******/(function(modules){//webpackBootstrap
/******/	//Themodulecache
/******/	varinstalledModules={};
/******/
/******/	//Therequirefunction
/******/	function__webpack_require__(moduleId){
/******/
/******/		//Checkifmoduleisincache
/******/		if(installedModules[moduleId]){
/******/			returninstalledModules[moduleId].exports;
/******/		}
/******/		//Createanewmodule(andputitintothecache)
/******/		varmodule=installedModules[moduleId]={
/******/			i:moduleId,
/******/			l:false,
/******/			exports:{}
/******/		};
/******/
/******/		//Executethemodulefunction
/******/		modules[moduleId].call(module.exports,module,module.exports,__webpack_require__);
/******/
/******/		//Flagthemoduleasloaded
/******/		module.l=true;
/******/
/******/		//Returntheexportsofthemodule
/******/		returnmodule.exports;
/******/	}
/******/
/******/
/******/	//exposethemodulesobject(__webpack_modules__)
/******/	__webpack_require__.m=modules;
/******/
/******/	//exposethemodulecache
/******/	__webpack_require__.c=installedModules;
/******/
/******/	//identityfunctionforcallingharmonyimportswiththecorrectcontext
/******/	__webpack_require__.i=function(value){returnvalue;};
/******/
/******/	//definegetterfunctionforharmonyexports
/******/	__webpack_require__.d=function(exports,name,getter){
/******/		if(!__webpack_require__.o(exports,name)){
/******/			Object.defineProperty(exports,name,{
/******/				configurable:false,
/******/				enumerable:true,
/******/				get:getter
/******/			});
/******/		}
/******/	};
/******/
/******/	//getDefaultExportfunctionforcompatibilitywithnon-harmonymodules
/******/	__webpack_require__.n=function(module){
/******/		vargetter=module&&module.__esModule?
/******/			functiongetDefault(){returnmodule['default'];}:
/******/			functiongetModuleExports(){returnmodule;};
/******/		__webpack_require__.d(getter,'a',getter);
/******/		returngetter;
/******/	};
/******/
/******/	//Object.prototype.hasOwnProperty.call
/******/	__webpack_require__.o=function(object,property){returnObject.prototype.hasOwnProperty.call(object,property);};
/******/
/******/	//__webpack_public_path__
/******/	__webpack_require__.p="";
/******/
/******/	//Loadentrymoduleandreturnexports
/******/	return__webpack_require__(__webpack_require__.s=3);
/******/})
/************************************************************************/
/******/([
/*0*/
/***/(function(module,exports,__webpack_require__){

var__WEBPACK_AMD_DEFINE_FACTORY__,__WEBPACK_AMD_DEFINE_ARRAY__,__WEBPACK_AMD_DEFINE_RESULT__;(function(global,factory){
    if(true){
        !(__WEBPACK_AMD_DEFINE_ARRAY__=[module,__webpack_require__(7)],__WEBPACK_AMD_DEFINE_FACTORY__=(factory),
				__WEBPACK_AMD_DEFINE_RESULT__=(typeof__WEBPACK_AMD_DEFINE_FACTORY__==='function'?
				(__WEBPACK_AMD_DEFINE_FACTORY__.apply(exports,__WEBPACK_AMD_DEFINE_ARRAY__)):__WEBPACK_AMD_DEFINE_FACTORY__),
				__WEBPACK_AMD_DEFINE_RESULT__!==undefined&&(module.exports=__WEBPACK_AMD_DEFINE_RESULT__));
    }elseif(typeofexports!=="undefined"){
        factory(module,require('select'));
    }else{
        varmod={
            exports:{}
        };
        factory(mod,global.select);
        global.clipboardAction=mod.exports;
    }
})(this,function(module,_select){
    'usestrict';

    var_select2=_interopRequireDefault(_select);

    function_interopRequireDefault(obj){
        returnobj&&obj.__esModule?obj:{
            default:obj
        };
    }

    var_typeof=typeofSymbol==="function"&&typeofSymbol.iterator==="symbol"?function(obj){
        returntypeofobj;
    }:function(obj){
        returnobj&&typeofSymbol==="function"&&obj.constructor===Symbol&&obj!==Symbol.prototype?"symbol":typeofobj;
    };

    function_classCallCheck(instance,Constructor){
        if(!(instanceinstanceofConstructor)){
            thrownewTypeError("Cannotcallaclassasafunction");
        }
    }

    var_createClass=function(){
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

    varClipboardAction=function(){
        /**
         *@param{Object}options
         */
        functionClipboardAction(options){
            _classCallCheck(this,ClipboardAction);

            this.resolveOptions(options);
            this.initSelection();
        }

        /**
         *Definesbasepropertiespassedfromconstructor.
         *@param{Object}options
         */


        _createClass(ClipboardAction,[{
            key:'resolveOptions',
            value:functionresolveOptions(){
                varoptions=arguments.length>0&&arguments[0]!==undefined?arguments[0]:{};

                this.action=options.action;
                this.container=options.container;
                this.emitter=options.emitter;
                this.target=options.target;
                this.text=options.text;
                this.trigger=options.trigger;

                this.selectedText='';
            }
        },{
            key:'initSelection',
            value:functioninitSelection(){
                if(this.text){
                    this.selectFake();
                }elseif(this.target){
                    this.selectTarget();
                }
            }
        },{
            key:'selectFake',
            value:functionselectFake(){
                var_this=this;

                varisRTL=document.documentElement.getAttribute('dir')=='rtl';

                this.removeFake();

                this.fakeHandlerCallback=function(){
                    return_this.removeFake();
                };
                this.fakeHandler=this.container.addEventListener('click',this.fakeHandlerCallback)||true;

                this.fakeElem=document.createElement('textarea');
                //PreventzoomingoniOS
                this.fakeElem.style.fontSize='12pt';
                //Resetboxmodel
                this.fakeElem.style.border='0';
                this.fakeElem.style.padding='0';
                this.fakeElem.style.margin='0';
                //Moveelementoutofscreenhorizontally
                this.fakeElem.style.position='absolute';
                this.fakeElem.style[isRTL?'right':'left']='-9999px';
                //Moveelementtothesamepositionvertically
                varyPosition=window.pageYOffset||document.documentElement.scrollTop;
                this.fakeElem.style.top=yPosition+'px';

                this.fakeElem.setAttribute('readonly','');
                this.fakeElem.value=this.text;

                this.container.appendChild(this.fakeElem);

                this.selectedText=(0,_select2.default)(this.fakeElem);
                this.copyText();
            }
        },{
            key:'removeFake',
            value:functionremoveFake(){
                if(this.fakeHandler){
                    this.container.removeEventListener('click',this.fakeHandlerCallback);
                    this.fakeHandler=null;
                    this.fakeHandlerCallback=null;
                }

                if(this.fakeElem){
                    this.container.removeChild(this.fakeElem);
                    this.fakeElem=null;
                }
            }
        },{
            key:'selectTarget',
            value:functionselectTarget(){
                this.selectedText=(0,_select2.default)(this.target);
                this.copyText();
            }
        },{
            key:'copyText',
            value:functioncopyText(){
                varsucceeded=void0;

                try{
                    succeeded=document.execCommand(this.action);
                }catch(err){
                    succeeded=false;
                }

                this.handleResult(succeeded);
            }
        },{
            key:'handleResult',
            value:functionhandleResult(succeeded){
                this.emitter.emit(succeeded?'success':'error',{
                    action:this.action,
                    text:this.selectedText,
                    trigger:this.trigger,
                    clearSelection:this.clearSelection.bind(this)
                });
            }
        },{
            key:'clearSelection',
            value:functionclearSelection(){
                if(this.trigger){
                    this.trigger.focus();
                }

                window.getSelection().removeAllRanges();
            }
        },{
            key:'destroy',
            value:functiondestroy(){
                this.removeFake();
            }
        },{
            key:'action',
            set:functionset(){
                varaction=arguments.length>0&&arguments[0]!==undefined?arguments[0]:'copy';

                this._action=action;

                if(this._action!=='copy'&&this._action!=='cut'){
                    thrownewError('Invalid"action"value,useeither"copy"or"cut"');
                }
            },
            get:functionget(){
                returnthis._action;
            }
        },{
            key:'target',
            set:functionset(target){
                if(target!==undefined){
                    if(target&&(typeoftarget==='undefined'?'undefined':_typeof(target))==='object'&&target.nodeType===1){
                        if(this.action==='copy'&&target.hasAttribute('disabled')){
                            thrownewError('Invalid"target"attribute.Pleaseuse"readonly"insteadof"disabled"attribute');
                        }

                        if(this.action==='cut'&&(target.hasAttribute('readonly')||target.hasAttribute('disabled'))){
                            thrownewError('Invalid"target"attribute.Youcan\'tcuttextfromelementswith"readonly"or"disabled"attributes');
                        }

                        this._target=target;
                    }else{
                        thrownewError('Invalid"target"value,useavalidElement');
                    }
                }
            },
            get:functionget(){
                returnthis._target;
            }
        }]);

        returnClipboardAction;
    }();

    module.exports=ClipboardAction;
});

/***/}),
/*1*/
/***/(function(module,exports,__webpack_require__){

varis=__webpack_require__(6);
vardelegate=__webpack_require__(5);

/**
 *Validatesallparamsandcallstheright
 *listenerfunctionbasedonitstargettype.
 *
 *@param{String|HTMLElement|HTMLCollection|NodeList}target
 *@param{String}type
 *@param{Function}callback
 *@return{Object}
 */
functionlisten(target,type,callback){
    if(!target&&!type&&!callback){
        thrownewError('Missingrequiredarguments');
    }

    if(!is.string(type)){
        thrownewTypeError('SecondargumentmustbeaString');
    }

    if(!is.fn(callback)){
        thrownewTypeError('ThirdargumentmustbeaFunction');
    }

    if(is.node(target)){
        returnlistenNode(target,type,callback);
    }
    elseif(is.nodeList(target)){
        returnlistenNodeList(target,type,callback);
    }
    elseif(is.string(target)){
        returnlistenSelector(target,type,callback);
    }
    else{
        thrownewTypeError('FirstargumentmustbeaString,HTMLElement,HTMLCollection,orNodeList');
    }
}

/**
 *AddsaneventlistenertoaHTMLelement
 *andreturnsaremovelistenerfunction.
 *
 *@param{HTMLElement}node
 *@param{String}type
 *@param{Function}callback
 *@return{Object}
 */
functionlistenNode(node,type,callback){
    node.addEventListener(type,callback);

    return{
        destroy:function(){
            node.removeEventListener(type,callback);
        }
    }
}

/**
 *AddaneventlistenertoalistofHTMLelements
 *andreturnsaremovelistenerfunction.
 *
 *@param{NodeList|HTMLCollection}nodeList
 *@param{String}type
 *@param{Function}callback
 *@return{Object}
 */
functionlistenNodeList(nodeList,type,callback){
    Array.prototype.forEach.call(nodeList,function(node){
        node.addEventListener(type,callback);
    });

    return{
        destroy:function(){
            Array.prototype.forEach.call(nodeList,function(node){
                node.removeEventListener(type,callback);
            });
        }
    }
}

/**
 *Addaneventlistenertoaselector
 *andreturnsaremovelistenerfunction.
 *
 *@param{String}selector
 *@param{String}type
 *@param{Function}callback
 *@return{Object}
 */
functionlistenSelector(selector,type,callback){
    returndelegate(document.body,selector,type,callback);
}

module.exports=listen;


/***/}),
/*2*/
/***/(function(module,exports){

functionE(){
  //Keepthisemptysoit'seasiertoinheritfrom
  //(viahttps://github.com/lipsmackfromhttps://github.com/scottcorgan/tiny-emitter/issues/3)
}

E.prototype={
  on:function(name,callback,ctx){
    vare=this.e||(this.e={});

    (e[name]||(e[name]=[])).push({
      fn:callback,
      ctx:ctx
    });

    returnthis;
  },

  once:function(name,callback,ctx){
    varself=this;
    functionlistener(){
      self.off(name,listener);
      callback.apply(ctx,arguments);
    };

    listener._=callback
    returnthis.on(name,listener,ctx);
  },

  emit:function(name){
    vardata=[].slice.call(arguments,1);
    varevtArr=((this.e||(this.e={}))[name]||[]).slice();
    vari=0;
    varlen=evtArr.length;

    for(i;i<len;i++){
      evtArr[i].fn.apply(evtArr[i].ctx,data);
    }

    returnthis;
  },

  off:function(name,callback){
    vare=this.e||(this.e={});
    varevts=e[name];
    varliveEvents=[];

    if(evts&&callback){
      for(vari=0,len=evts.length;i<len;i++){
        if(evts[i].fn!==callback&&evts[i].fn._!==callback)
          liveEvents.push(evts[i]);
      }
    }

    //Removeeventfromqueuetopreventmemoryleak
    //Suggestedbyhttps://github.com/lazd
    //Ref:https://github.com/scottcorgan/tiny-emitter/commit/c6ebfaa9bc973b33d110a84a307742b7cf94c953#commitcomment-5024910

    (liveEvents.length)
      ?e[name]=liveEvents
      :deletee[name];

    returnthis;
  }
};

module.exports=E;


/***/}),
/*3*/
/***/(function(module,exports,__webpack_require__){

var__WEBPACK_AMD_DEFINE_FACTORY__,__WEBPACK_AMD_DEFINE_ARRAY__,__WEBPACK_AMD_DEFINE_RESULT__;(function(global,factory){
    if(true){
        !(__WEBPACK_AMD_DEFINE_ARRAY__=[module,__webpack_require__(0),__webpack_require__(2),__webpack_require__(1)],__WEBPACK_AMD_DEFINE_FACTORY__=(factory),
				__WEBPACK_AMD_DEFINE_RESULT__=(typeof__WEBPACK_AMD_DEFINE_FACTORY__==='function'?
				(__WEBPACK_AMD_DEFINE_FACTORY__.apply(exports,__WEBPACK_AMD_DEFINE_ARRAY__)):__WEBPACK_AMD_DEFINE_FACTORY__),
				__WEBPACK_AMD_DEFINE_RESULT__!==undefined&&(module.exports=__WEBPACK_AMD_DEFINE_RESULT__));
    }elseif(typeofexports!=="undefined"){
        factory(module,require('./clipboard-action'),require('tiny-emitter'),require('good-listener'));
    }else{
        varmod={
            exports:{}
        };
        factory(mod,global.clipboardAction,global.tinyEmitter,global.goodListener);
        global.clipboard=mod.exports;
    }
})(this,function(module,_clipboardAction,_tinyEmitter,_goodListener){
    'usestrict';

    var_clipboardAction2=_interopRequireDefault(_clipboardAction);

    var_tinyEmitter2=_interopRequireDefault(_tinyEmitter);

    var_goodListener2=_interopRequireDefault(_goodListener);

    function_interopRequireDefault(obj){
        returnobj&&obj.__esModule?obj:{
            default:obj
        };
    }

    var_typeof=typeofSymbol==="function"&&typeofSymbol.iterator==="symbol"?function(obj){
        returntypeofobj;
    }:function(obj){
        returnobj&&typeofSymbol==="function"&&obj.constructor===Symbol&&obj!==Symbol.prototype?"symbol":typeofobj;
    };

    function_classCallCheck(instance,Constructor){
        if(!(instanceinstanceofConstructor)){
            thrownewTypeError("Cannotcallaclassasafunction");
        }
    }

    var_createClass=function(){
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

    function_possibleConstructorReturn(self,call){
        if(!self){
            thrownewReferenceError("thishasn'tbeeninitialised-super()hasn'tbeencalled");
        }

        returncall&&(typeofcall==="object"||typeofcall==="function")?call:self;
    }

    function_inherits(subClass,superClass){
        if(typeofsuperClass!=="function"&&superClass!==null){
            thrownewTypeError("Superexpressionmusteitherbenullorafunction,not"+typeofsuperClass);
        }

        subClass.prototype=Object.create(superClass&&superClass.prototype,{
            constructor:{
                value:subClass,
                enumerable:false,
                writable:true,
                configurable:true
            }
        });
        if(superClass)Object.setPrototypeOf?Object.setPrototypeOf(subClass,superClass):subClass.__proto__=superClass;
    }

    varClipboard=function(_Emitter){
        _inherits(Clipboard,_Emitter);

        /**
         *@param{String|HTMLElement|HTMLCollection|NodeList}trigger
         *@param{Object}options
         */
        functionClipboard(trigger,options){
            _classCallCheck(this,Clipboard);

            var_this=_possibleConstructorReturn(this,(Clipboard.__proto__||Object.getPrototypeOf(Clipboard)).call(this));

            _this.resolveOptions(options);
            _this.listenClick(trigger);
            return_this;
        }

        /**
         *Definesifattributeswouldberesolvedusinginternalsetterfunctions
         *orcustomfunctionsthatwerepassedintheconstructor.
         *@param{Object}options
         */


        _createClass(Clipboard,[{
            key:'resolveOptions',
            value:functionresolveOptions(){
                varoptions=arguments.length>0&&arguments[0]!==undefined?arguments[0]:{};

                this.action=typeofoptions.action==='function'?options.action:this.defaultAction;
                this.target=typeofoptions.target==='function'?options.target:this.defaultTarget;
                this.text=typeofoptions.text==='function'?options.text:this.defaultText;
                this.container=_typeof(options.container)==='object'?options.container:document.body;
            }
        },{
            key:'listenClick',
            value:functionlistenClick(trigger){
                var_this2=this;

                this.listener=(0,_goodListener2.default)(trigger,'click',function(e){
                    return_this2.onClick(e);
                });
            }
        },{
            key:'onClick',
            value:functiononClick(e){
                vartrigger=e.delegateTarget||e.currentTarget;

                if(this.clipboardAction){
                    this.clipboardAction=null;
                }

                this.clipboardAction=new_clipboardAction2.default({
                    action:this.action(trigger),
                    target:this.target(trigger),
                    text:this.text(trigger),
                    container:this.container,
                    trigger:trigger,
                    emitter:this
                });
            }
        },{
            key:'defaultAction',
            value:functiondefaultAction(trigger){
                returngetAttributeValue('action',trigger);
            }
        },{
            key:'defaultTarget',
            value:functiondefaultTarget(trigger){
                varselector=getAttributeValue('target',trigger);

                if(selector){
                    returndocument.querySelector(selector);
                }
            }
        },{
            key:'defaultText',
            value:functiondefaultText(trigger){
                returngetAttributeValue('text',trigger);
            }
        },{
            key:'destroy',
            value:functiondestroy(){
                this.listener.destroy();

                if(this.clipboardAction){
                    this.clipboardAction.destroy();
                    this.clipboardAction=null;
                }
            }
        }],[{
            key:'isSupported',
            value:functionisSupported(){
                varaction=arguments.length>0&&arguments[0]!==undefined?arguments[0]:['copy','cut'];

                varactions=typeofaction==='string'?[action]:action;
                varsupport=!!document.queryCommandSupported;

                actions.forEach(function(action){
                    support=support&&!!document.queryCommandSupported(action);
                });

                returnsupport;
            }
        }]);

        returnClipboard;
    }(_tinyEmitter2.default);

    /**
     *Helperfunctiontoretrieveattributevalue.
     *@param{String}suffix
     *@param{Element}element
     */
    functiongetAttributeValue(suffix,element){
        varattribute='data-clipboard-'+suffix;

        if(!element.hasAttribute(attribute)){
            return;
        }

        returnelement.getAttribute(attribute);
    }

    module.exports=Clipboard;
});

/***/}),
/*4*/
/***/(function(module,exports){

varDOCUMENT_NODE_TYPE=9;

/**
 *ApolyfillforElement.matches()
 */
if(typeofElement!=='undefined'&&!Element.prototype.matches){
    varproto=Element.prototype;

    proto.matches=proto.matchesSelector||
                    proto.mozMatchesSelector||
                    proto.msMatchesSelector||
                    proto.oMatchesSelector||
                    proto.webkitMatchesSelector;
}

/**
 *Findstheclosestparentthatmatchesaselector.
 *
 *@param{Element}element
 *@param{String}selector
 *@return{Function}
 */
functionclosest(element,selector){
    while(element&&element.nodeType!==DOCUMENT_NODE_TYPE){
        if(typeofelement.matches==='function'&&
            element.matches(selector)){
          returnelement;
        }
        element=element.parentNode;
    }
}

module.exports=closest;


/***/}),
/*5*/
/***/(function(module,exports,__webpack_require__){

varclosest=__webpack_require__(4);

/**
 *Delegateseventtoaselector.
 *
 *@param{Element}element
 *@param{String}selector
 *@param{String}type
 *@param{Function}callback
 *@param{Boolean}useCapture
 *@return{Object}
 */
function_delegate(element,selector,type,callback,useCapture){
    varlistenerFn=listener.apply(this,arguments);

    element.addEventListener(type,listenerFn,useCapture);

    return{
        destroy:function(){
            element.removeEventListener(type,listenerFn,useCapture);
        }
    }
}

/**
 *Delegateseventtoaselector.
 *
 *@param{Element|String|Array}[elements]
 *@param{String}selector
 *@param{String}type
 *@param{Function}callback
 *@param{Boolean}useCapture
 *@return{Object}
 */
functiondelegate(elements,selector,type,callback,useCapture){
    //HandletheregularElementusage
    if(typeofelements.addEventListener==='function'){
        return_delegate.apply(null,arguments);
    }

    //HandleElement-lessusage,itdefaultstoglobaldelegation
    if(typeoftype==='function'){
        //Use`document`asthefirstparameter,thenapplyarguments
        //Thisisashortwayto.unshift`arguments`withoutrunningintodeoptimizations
        return_delegate.bind(null,document).apply(null,arguments);
    }

    //HandleSelector-basedusage
    if(typeofelements==='string'){
        elements=document.querySelectorAll(elements);
    }

    //HandleArray-likebasedusage
    returnArray.prototype.map.call(elements,function(element){
        return_delegate(element,selector,type,callback,useCapture);
    });
}

/**
 *Findsclosestmatchandinvokescallback.
 *
 *@param{Element}element
 *@param{String}selector
 *@param{String}type
 *@param{Function}callback
 *@return{Function}
 */
functionlistener(element,selector,type,callback){
    returnfunction(e){
        e.delegateTarget=closest(e.target,selector);

        if(e.delegateTarget){
            callback.call(element,e);
        }
    }
}

module.exports=delegate;


/***/}),
/*6*/
/***/(function(module,exports){

/**
 *CheckifargumentisaHTMLelement.
 *
 *@param{Object}value
 *@return{Boolean}
 */
exports.node=function(value){
    returnvalue!==undefined
        &&valueinstanceofHTMLElement
        &&value.nodeType===1;
};

/**
 *CheckifargumentisalistofHTMLelements.
 *
 *@param{Object}value
 *@return{Boolean}
 */
exports.nodeList=function(value){
    vartype=Object.prototype.toString.call(value);

    returnvalue!==undefined
        &&(type==='[objectNodeList]'||type==='[objectHTMLCollection]')
        &&('length'invalue)
        &&(value.length===0||exports.node(value[0]));
};

/**
 *Checkifargumentisastring.
 *
 *@param{Object}value
 *@return{Boolean}
 */
exports.string=function(value){
    returntypeofvalue==='string'
        ||valueinstanceofString;
};

/**
 *Checkifargumentisafunction.
 *
 *@param{Object}value
 *@return{Boolean}
 */
exports.fn=function(value){
    vartype=Object.prototype.toString.call(value);

    returntype==='[objectFunction]';
};


/***/}),
/*7*/
/***/(function(module,exports){

functionselect(element){
    varselectedText;

    if(element.nodeName==='SELECT'){
        element.focus();

        selectedText=element.value;
    }
    elseif(element.nodeName==='INPUT'||element.nodeName==='TEXTAREA'){
        varisReadOnly=element.hasAttribute('readonly');

        if(!isReadOnly){
            element.setAttribute('readonly','');
        }

        element.select();
        element.setSelectionRange(0,element.value.length);

        if(!isReadOnly){
            element.removeAttribute('readonly');
        }

        selectedText=element.value;
    }
    else{
        if(element.hasAttribute('contenteditable')){
            element.focus();
        }

        varselection=window.getSelection();
        varrange=document.createRange();

        range.selectNodeContents(element);
        selection.removeAllRanges();
        selection.addRange(range);

        selectedText=selection.toString();
    }

    returnselectedText;
}

module.exports=select;


/***/})
/******/]);
});