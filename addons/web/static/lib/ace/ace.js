/******BEGINLICENSEBLOCK*****
 *DistributedundertheBSDlicense:
 *
 *Copyright(c)2010,Ajax.orgB.V.
 *Allrightsreserved.
 *
 *Redistributionanduseinsourceandbinaryforms,withorwithout
 *modification,arepermittedprovidedthatthefollowingconditionsaremet:
 *    *Redistributionsofsourcecodemustretaintheabovecopyright
 *      notice,thislistofconditionsandthefollowingdisclaimer.
 *    *Redistributionsinbinaryformmustreproducetheabovecopyright
 *      notice,thislistofconditionsandthefollowingdisclaimerinthe
 *      documentationand/orothermaterialsprovidedwiththedistribution.
 *    *NeitherthenameofAjax.orgB.V.northe
 *      namesofitscontributorsmaybeusedtoendorseorpromoteproducts
 *      derivedfromthissoftwarewithoutspecificpriorwrittenpermission.
 *
 *THISSOFTWAREISPROVIDEDBYTHECOPYRIGHTHOLDERSANDCONTRIBUTORS"ASIS"AND
 *ANYEXPRESSORIMPLIEDWARRANTIES,INCLUDING,BUTNOTLIMITEDTO,THEIMPLIED
 *WARRANTIESOFMERCHANTABILITYANDFITNESSFORAPARTICULARPURPOSEARE
 *DISCLAIMED.INNOEVENTSHALLAJAX.ORGB.V.BELIABLEFORANY
 *DIRECT,INDIRECT,INCIDENTAL,SPECIAL,EXEMPLARY,ORCONSEQUENTIALDAMAGES
 *(INCLUDING,BUTNOTLIMITEDTO,PROCUREMENTOFSUBSTITUTEGOODSORSERVICES;
 *LOSSOFUSE,DATA,ORPROFITS;ORBUSINESSINTERRUPTION)HOWEVERCAUSEDAND
 *ONANYTHEORYOFLIABILITY,WHETHERINCONTRACT,STRICTLIABILITY,ORTORT
 *(INCLUDINGNEGLIGENCEOROTHERWISE)ARISINGINANYWAYOUTOFTHEUSEOFTHIS
 *SOFTWARE,EVENIFADVISEDOFTHEPOSSIBILITYOFSUCHDAMAGE.
 *
 ******ENDLICENSEBLOCK******/

/**
 *Defineamodulealongwithapayload
 *@parammoduleanameforthepayload
 *@parampayloadafunctiontocallwith(require,exports,module)params
 */

(function(){

varACE_NAMESPACE="";

varglobal=(function(){returnthis;})();
if(!global&&typeofwindow!="undefined")global=window;//strictmode


if(!ACE_NAMESPACE&&typeofrequirejs!=="undefined")
    return;


vardefine=function(module,deps,payload){
    if(typeofmodule!=="string"){
        if(define.original)
            define.original.apply(this,arguments);
        else{
            console.error("droppingmodulebecausedefinewasn\'tastring.");
            console.trace();
        }
        return;
    }
    if(arguments.length==2)
        payload=deps;
    if(!define.modules[module]){
        define.payloads[module]=payload;
        define.modules[module]=null;
    }
};

define.modules={};
define.payloads={};

/**
 *Getatfunctionalitydefine()edusingthefunctionabove
 */
var_require=function(parentId,module,callback){
    if(typeofmodule==="string"){
        varpayload=lookup(parentId,module);
        if(payload!=undefined){
            callback&&callback();
            returnpayload;
        }
    }elseif(Object.prototype.toString.call(module)==="[objectArray]"){
        varparams=[];
        for(vari=0,l=module.length;i<l;++i){
            vardep=lookup(parentId,module[i]);
            if(dep==undefined&&require.original)
                return;
            params.push(dep);
        }
        returncallback&&callback.apply(null,params)||true;
    }
};

varrequire=function(module,callback){
    varpackagedModule=_require("",module,callback);
    if(packagedModule==undefined&&require.original)
        returnrequire.original.apply(this,arguments);
    returnpackagedModule;
};

varnormalizeModule=function(parentId,moduleName){
    //normalizepluginrequires
    if(moduleName.indexOf("!")!==-1){
        varchunks=moduleName.split("!");
        returnnormalizeModule(parentId,chunks[0])+"!"+normalizeModule(parentId,chunks[1]);
    }
    //normalizerelativerequires
    if(moduleName.charAt(0)=="."){
        varbase=parentId.split("/").slice(0,-1).join("/");
        moduleName=base+"/"+moduleName;

        while(moduleName.indexOf(".")!==-1&&previous!=moduleName){
            varprevious=moduleName;
            moduleName=moduleName.replace(/\/\.\//,"/").replace(/[^\/]+\/\.\.\//,"");
        }
    }
    returnmoduleName;
};

/**
 *InternalfunctiontolookupmoduleNamesandresolvethembycallingthe
 *definitionfunctionifneeded.
 */
varlookup=function(parentId,moduleName){
    moduleName=normalizeModule(parentId,moduleName);

    varmodule=define.modules[moduleName];
    if(!module){
        module=define.payloads[moduleName];
        if(typeofmodule==='function'){
            varexports={};
            varmod={
                id:moduleName,
                uri:'',
                exports:exports,
                packaged:true
            };

            varreq=function(module,callback){
                return_require(moduleName,module,callback);
            };

            varreturnValue=module(req,exports,mod);
            exports=returnValue||mod.exports;
            define.modules[moduleName]=exports;
            deletedefine.payloads[moduleName];
        }
        module=define.modules[moduleName]=exports||module;
    }
    returnmodule;
};

functionexportAce(ns){
    varroot=global;
    if(ns){
        if(!global[ns])
            global[ns]={};
        root=global[ns];
    }

    if(!root.define||!root.define.packaged){
        define.original=root.define;
        root.define=define;
        root.define.packaged=true;
    }

    if(!root.require||!root.require.packaged){
        require.original=root.require;
        root.require=require;
        root.require.packaged=true;
    }
}

exportAce(ACE_NAMESPACE);

})();

define("ace/lib/regexp",["require","exports","module"],function(require,exports,module){
"usestrict";

    varreal={
            exec:RegExp.prototype.exec,
            test:RegExp.prototype.test,
            match:String.prototype.match,
            replace:String.prototype.replace,
            split:String.prototype.split
        },
        compliantExecNpcg=real.exec.call(/()??/,"")[1]===undefined,//check`exec`handlingofnonparticipatingcapturinggroups
        compliantLastIndexIncrement=function(){
            varx=/^/g;
            real.test.call(x,"");
            return!x.lastIndex;
        }();

    if(compliantLastIndexIncrement&&compliantExecNpcg)
        return;
    RegExp.prototype.exec=function(str){
        varmatch=real.exec.apply(this,arguments),
            name,r2;
        if(typeof(str)=='string'&&match){
            if(!compliantExecNpcg&&match.length>1&&indexOf(match,"")>-1){
                r2=RegExp(this.source,real.replace.call(getNativeFlags(this),"g",""));
                real.replace.call(str.slice(match.index),r2,function(){
                    for(vari=1;i<arguments.length-2;i++){
                        if(arguments[i]===undefined)
                            match[i]=undefined;
                    }
                });
            }
            if(this._xregexp&&this._xregexp.captureNames){
                for(vari=1;i<match.length;i++){
                    name=this._xregexp.captureNames[i-1];
                    if(name)
                       match[name]=match[i];
                }
            }
            if(!compliantLastIndexIncrement&&this.global&&!match[0].length&&(this.lastIndex>match.index))
                this.lastIndex--;
        }
        returnmatch;
    };
    if(!compliantLastIndexIncrement){
        RegExp.prototype.test=function(str){
            varmatch=real.exec.call(this,str);
            if(match&&this.global&&!match[0].length&&(this.lastIndex>match.index))
                this.lastIndex--;
            return!!match;
        };
    }

    functiongetNativeFlags(regex){
        return(regex.global    ?"g":"")+
               (regex.ignoreCase?"i":"")+
               (regex.multiline ?"m":"")+
               (regex.extended  ?"x":"")+//ProposedforES4;includedinAS3
               (regex.sticky    ?"y":"");
    }

    functionindexOf(array,item,from){
        if(Array.prototype.indexOf)//Usethenativearraymethodifavailable
            returnarray.indexOf(item,from);
        for(vari=from||0;i<array.length;i++){
            if(array[i]===item)
                returni;
        }
        return-1;
    }

});

define("ace/lib/es5-shim",["require","exports","module"],function(require,exports,module){

functionEmpty(){}

if(!Function.prototype.bind){
    Function.prototype.bind=functionbind(that){//.lengthis1
        vartarget=this;
        if(typeoftarget!="function"){
            thrownewTypeError("Function.prototype.bindcalledonincompatible"+target);
        }
        varargs=slice.call(arguments,1);//fornormalcall
        varbound=function(){

            if(thisinstanceofbound){

                varresult=target.apply(
                    this,
                    args.concat(slice.call(arguments))
                );
                if(Object(result)===result){
                    returnresult;
                }
                returnthis;

            }else{
                returntarget.apply(
                    that,
                    args.concat(slice.call(arguments))
                );

            }

        };
        if(target.prototype){
            Empty.prototype=target.prototype;
            bound.prototype=newEmpty();
            Empty.prototype=null;
        }
        returnbound;
    };
}
varcall=Function.prototype.call;
varprototypeOfArray=Array.prototype;
varprototypeOfObject=Object.prototype;
varslice=prototypeOfArray.slice;
var_toString=call.bind(prototypeOfObject.toString);
varowns=call.bind(prototypeOfObject.hasOwnProperty);
vardefineGetter;
vardefineSetter;
varlookupGetter;
varlookupSetter;
varsupportsAccessors;
if((supportsAccessors=owns(prototypeOfObject,"__defineGetter__"))){
    defineGetter=call.bind(prototypeOfObject.__defineGetter__);
    defineSetter=call.bind(prototypeOfObject.__defineSetter__);
    lookupGetter=call.bind(prototypeOfObject.__lookupGetter__);
    lookupSetter=call.bind(prototypeOfObject.__lookupSetter__);
}
if([1,2].splice(0).length!=2){
    if(function(){//testIE<9tosplicebug-seeissue#138
        functionmakeArray(l){
            vara=newArray(l+2);
            a[0]=a[1]=0;
            returna;
        }
        vararray=[],lengthBefore;
        
        array.splice.apply(array,makeArray(20));
        array.splice.apply(array,makeArray(26));

        lengthBefore=array.length;//46
        array.splice(5,0,"XXX");//addoneelement

        lengthBefore+1==array.length

        if(lengthBefore+1==array.length){
            returntrue;//hasrightspliceimplementationwithoutbugs
        }
    }()){//IE6/7
        vararray_splice=Array.prototype.splice;
        Array.prototype.splice=function(start,deleteCount){
            if(!arguments.length){
                return[];
            }else{
                returnarray_splice.apply(this,[
                    start===void0?0:start,
                    deleteCount===void0?(this.length-start):deleteCount
                ].concat(slice.call(arguments,2)))
            }
        };
    }else{//IE8
        Array.prototype.splice=function(pos,removeCount){
            varlength=this.length;
            if(pos>0){
                if(pos>length)
                    pos=length;
            }elseif(pos==void0){
                pos=0;
            }elseif(pos<0){
                pos=Math.max(length+pos,0);
            }

            if(!(pos+removeCount<length))
                removeCount=length-pos;

            varremoved=this.slice(pos,pos+removeCount);
            varinsert=slice.call(arguments,2);
            varadd=insert.length;           
            if(pos===length){
                if(add){
                    this.push.apply(this,insert);
                }
            }else{
                varremove=Math.min(removeCount,length-pos);
                vartailOldPos=pos+remove;
                vartailNewPos=tailOldPos+add-remove;
                vartailCount=length-tailOldPos;
                varlengthAfterRemove=length-remove;

                if(tailNewPos<tailOldPos){//caseA
                    for(vari=0;i<tailCount;++i){
                        this[tailNewPos+i]=this[tailOldPos+i];
                    }
                }elseif(tailNewPos>tailOldPos){//caseB
                    for(i=tailCount;i--;){
                        this[tailNewPos+i]=this[tailOldPos+i];
                    }
                }//else,add==remove(nothingtodo)

                if(add&&pos===lengthAfterRemove){
                    this.length=lengthAfterRemove;//truncatearray
                    this.push.apply(this,insert);
                }else{
                    this.length=lengthAfterRemove+add;//reservesspace
                    for(i=0;i<add;++i){
                        this[pos+i]=insert[i];
                    }
                }
            }
            returnremoved;
        };
    }
}
if(!Array.isArray){
    Array.isArray=functionisArray(obj){
        return_toString(obj)=="[objectArray]";
    };
}
varboxedString=Object("a"),
    splitString=boxedString[0]!="a"||!(0inboxedString);

if(!Array.prototype.forEach){
    Array.prototype.forEach=functionforEach(fun/*,thisp*/){
        varobject=toObject(this),
            self=splitString&&_toString(this)=="[objectString]"?
                this.split(""):
                object,
            thisp=arguments[1],
            i=-1,
            length=self.length>>>0;
        if(_toString(fun)!="[objectFunction]"){
            thrownewTypeError();//TODOmessage
        }

        while(++i<length){
            if(iinself){
                fun.call(thisp,self[i],i,object);
            }
        }
    };
}
if(!Array.prototype.map){
    Array.prototype.map=functionmap(fun/*,thisp*/){
        varobject=toObject(this),
            self=splitString&&_toString(this)=="[objectString]"?
                this.split(""):
                object,
            length=self.length>>>0,
            result=Array(length),
            thisp=arguments[1];
        if(_toString(fun)!="[objectFunction]"){
            thrownewTypeError(fun+"isnotafunction");
        }

        for(vari=0;i<length;i++){
            if(iinself)
                result[i]=fun.call(thisp,self[i],i,object);
        }
        returnresult;
    };
}
if(!Array.prototype.filter){
    Array.prototype.filter=functionfilter(fun/*,thisp*/){
        varobject=toObject(this),
            self=splitString&&_toString(this)=="[objectString]"?
                this.split(""):
                    object,
            length=self.length>>>0,
            result=[],
            value,
            thisp=arguments[1];
        if(_toString(fun)!="[objectFunction]"){
            thrownewTypeError(fun+"isnotafunction");
        }

        for(vari=0;i<length;i++){
            if(iinself){
                value=self[i];
                if(fun.call(thisp,value,i,object)){
                    result.push(value);
                }
            }
        }
        returnresult;
    };
}
if(!Array.prototype.every){
    Array.prototype.every=functionevery(fun/*,thisp*/){
        varobject=toObject(this),
            self=splitString&&_toString(this)=="[objectString]"?
                this.split(""):
                object,
            length=self.length>>>0,
            thisp=arguments[1];
        if(_toString(fun)!="[objectFunction]"){
            thrownewTypeError(fun+"isnotafunction");
        }

        for(vari=0;i<length;i++){
            if(iinself&&!fun.call(thisp,self[i],i,object)){
                returnfalse;
            }
        }
        returntrue;
    };
}
if(!Array.prototype.some){
    Array.prototype.some=functionsome(fun/*,thisp*/){
        varobject=toObject(this),
            self=splitString&&_toString(this)=="[objectString]"?
                this.split(""):
                object,
            length=self.length>>>0,
            thisp=arguments[1];
        if(_toString(fun)!="[objectFunction]"){
            thrownewTypeError(fun+"isnotafunction");
        }

        for(vari=0;i<length;i++){
            if(iinself&&fun.call(thisp,self[i],i,object)){
                returntrue;
            }
        }
        returnfalse;
    };
}
if(!Array.prototype.reduce){
    Array.prototype.reduce=functionreduce(fun/*,initial*/){
        varobject=toObject(this),
            self=splitString&&_toString(this)=="[objectString]"?
                this.split(""):
                object,
            length=self.length>>>0;
        if(_toString(fun)!="[objectFunction]"){
            thrownewTypeError(fun+"isnotafunction");
        }
        if(!length&&arguments.length==1){
            thrownewTypeError("reduceofemptyarraywithnoinitialvalue");
        }

        vari=0;
        varresult;
        if(arguments.length>=2){
            result=arguments[1];
        }else{
            do{
                if(iinself){
                    result=self[i++];
                    break;
                }
                if(++i>=length){
                    thrownewTypeError("reduceofemptyarraywithnoinitialvalue");
                }
            }while(true);
        }

        for(;i<length;i++){
            if(iinself){
                result=fun.call(void0,result,self[i],i,object);
            }
        }

        returnresult;
    };
}
if(!Array.prototype.reduceRight){
    Array.prototype.reduceRight=functionreduceRight(fun/*,initial*/){
        varobject=toObject(this),
            self=splitString&&_toString(this)=="[objectString]"?
                this.split(""):
                object,
            length=self.length>>>0;
        if(_toString(fun)!="[objectFunction]"){
            thrownewTypeError(fun+"isnotafunction");
        }
        if(!length&&arguments.length==1){
            thrownewTypeError("reduceRightofemptyarraywithnoinitialvalue");
        }

        varresult,i=length-1;
        if(arguments.length>=2){
            result=arguments[1];
        }else{
            do{
                if(iinself){
                    result=self[i--];
                    break;
                }
                if(--i<0){
                    thrownewTypeError("reduceRightofemptyarraywithnoinitialvalue");
                }
            }while(true);
        }

        do{
            if(iinthis){
                result=fun.call(void0,result,self[i],i,object);
            }
        }while(i--);

        returnresult;
    };
}
if(!Array.prototype.indexOf||([0,1].indexOf(1,2)!=-1)){
    Array.prototype.indexOf=functionindexOf(sought/*,fromIndex*/){
        varself=splitString&&_toString(this)=="[objectString]"?
                this.split(""):
                toObject(this),
            length=self.length>>>0;

        if(!length){
            return-1;
        }

        vari=0;
        if(arguments.length>1){
            i=toInteger(arguments[1]);
        }
        i=i>=0?i:Math.max(0,length+i);
        for(;i<length;i++){
            if(iinself&&self[i]===sought){
                returni;
            }
        }
        return-1;
    };
}
if(!Array.prototype.lastIndexOf||([0,1].lastIndexOf(0,-3)!=-1)){
    Array.prototype.lastIndexOf=functionlastIndexOf(sought/*,fromIndex*/){
        varself=splitString&&_toString(this)=="[objectString]"?
                this.split(""):
                toObject(this),
            length=self.length>>>0;

        if(!length){
            return-1;
        }
        vari=length-1;
        if(arguments.length>1){
            i=Math.min(i,toInteger(arguments[1]));
        }
        i=i>=0?i:length-Math.abs(i);
        for(;i>=0;i--){
            if(iinself&&sought===self[i]){
                returni;
            }
        }
        return-1;
    };
}
if(!Object.getPrototypeOf){
    Object.getPrototypeOf=functiongetPrototypeOf(object){
        returnobject.__proto__||(
            object.constructor?
            object.constructor.prototype:
            prototypeOfObject
        );
    };
}
if(!Object.getOwnPropertyDescriptor){
    varERR_NON_OBJECT="Object.getOwnPropertyDescriptorcalledona"+
                         "non-object:";
    Object.getOwnPropertyDescriptor=functiongetOwnPropertyDescriptor(object,property){
        if((typeofobject!="object"&&typeofobject!="function")||object===null)
            thrownewTypeError(ERR_NON_OBJECT+object);
        if(!owns(object,property))
            return;

        vardescriptor,getter,setter;
        descriptor= {enumerable:true,configurable:true};
        if(supportsAccessors){
            varprototype=object.__proto__;
            object.__proto__=prototypeOfObject;

            vargetter=lookupGetter(object,property);
            varsetter=lookupSetter(object,property);
            object.__proto__=prototype;

            if(getter||setter){
                if(getter)descriptor.get=getter;
                if(setter)descriptor.set=setter;
                returndescriptor;
            }
        }
        descriptor.value=object[property];
        returndescriptor;
    };
}
if(!Object.getOwnPropertyNames){
    Object.getOwnPropertyNames=functiongetOwnPropertyNames(object){
        returnObject.keys(object);
    };
}
if(!Object.create){
    varcreateEmpty;
    if(Object.prototype.__proto__===null){
        createEmpty=function(){
            return{"__proto__":null};
        };
    }else{
        createEmpty=function(){
            varempty={};
            for(variinempty)
                empty[i]=null;
            empty.constructor=
            empty.hasOwnProperty=
            empty.propertyIsEnumerable=
            empty.isPrototypeOf=
            empty.toLocaleString=
            empty.toString=
            empty.valueOf=
            empty.__proto__=null;
            returnempty;
        }
    }

    Object.create=functioncreate(prototype,properties){
        varobject;
        if(prototype===null){
            object=createEmpty();
        }else{
            if(typeofprototype!="object")
                thrownewTypeError("typeofprototype["+(typeofprototype)+"]!='object'");
            varType=function(){};
            Type.prototype=prototype;
            object=newType();
            object.__proto__=prototype;
        }
        if(properties!==void0)
            Object.defineProperties(object,properties);
        returnobject;
    };
}

functiondoesDefinePropertyWork(object){
    try{
        Object.defineProperty(object,"sentinel",{});
        return"sentinel"inobject;
    }catch(exception){
    }
}
if(Object.defineProperty){
    vardefinePropertyWorksOnObject=doesDefinePropertyWork({});
    vardefinePropertyWorksOnDom=typeofdocument=="undefined"||
        doesDefinePropertyWork(document.createElement("div"));
    if(!definePropertyWorksOnObject||!definePropertyWorksOnDom){
        vardefinePropertyFallback=Object.defineProperty;
    }
}

if(!Object.defineProperty||definePropertyFallback){
    varERR_NON_OBJECT_DESCRIPTOR="Propertydescriptionmustbeanobject:";
    varERR_NON_OBJECT_TARGET="Object.definePropertycalledonnon-object:"
    varERR_ACCESSORS_NOT_SUPPORTED="getters&setterscannotbedefined"+
                                      "onthisjavascriptengine";

    Object.defineProperty=functiondefineProperty(object,property,descriptor){
        if((typeofobject!="object"&&typeofobject!="function")||object===null)
            thrownewTypeError(ERR_NON_OBJECT_TARGET+object);
        if((typeofdescriptor!="object"&&typeofdescriptor!="function")||descriptor===null)
            thrownewTypeError(ERR_NON_OBJECT_DESCRIPTOR+descriptor);
        if(definePropertyFallback){
            try{
                returndefinePropertyFallback.call(Object,object,property,descriptor);
            }catch(exception){
            }
        }
        if(owns(descriptor,"value")){

            if(supportsAccessors&&(lookupGetter(object,property)||
                                      lookupSetter(object,property)))
            {
                varprototype=object.__proto__;
                object.__proto__=prototypeOfObject;
                deleteobject[property];
                object[property]=descriptor.value;
                object.__proto__=prototype;
            }else{
                object[property]=descriptor.value;
            }
        }else{
            if(!supportsAccessors)
                thrownewTypeError(ERR_ACCESSORS_NOT_SUPPORTED);
            if(owns(descriptor,"get"))
                defineGetter(object,property,descriptor.get);
            if(owns(descriptor,"set"))
                defineSetter(object,property,descriptor.set);
        }

        returnobject;
    };
}
if(!Object.defineProperties){
    Object.defineProperties=functiondefineProperties(object,properties){
        for(varpropertyinproperties){
            if(owns(properties,property))
                Object.defineProperty(object,property,properties[property]);
        }
        returnobject;
    };
}
if(!Object.seal){
    Object.seal=functionseal(object){
        returnobject;
    };
}
if(!Object.freeze){
    Object.freeze=functionfreeze(object){
        returnobject;
    };
}
try{
    Object.freeze(function(){});
}catch(exception){
    Object.freeze=(functionfreeze(freezeObject){
        returnfunctionfreeze(object){
            if(typeofobject=="function"){
                returnobject;
            }else{
                returnfreezeObject(object);
            }
        };
    })(Object.freeze);
}
if(!Object.preventExtensions){
    Object.preventExtensions=functionpreventExtensions(object){
        returnobject;
    };
}
if(!Object.isSealed){
    Object.isSealed=functionisSealed(object){
        returnfalse;
    };
}
if(!Object.isFrozen){
    Object.isFrozen=functionisFrozen(object){
        returnfalse;
    };
}
if(!Object.isExtensible){
    Object.isExtensible=functionisExtensible(object){
        if(Object(object)===object){
            thrownewTypeError();//TODOmessage
        }
        varname='';
        while(owns(object,name)){
            name+='?';
        }
        object[name]=true;
        varreturnValue=owns(object,name);
        deleteobject[name];
        returnreturnValue;
    };
}
if(!Object.keys){
    varhasDontEnumBug=true,
        dontEnums=[
            "toString",
            "toLocaleString",
            "valueOf",
            "hasOwnProperty",
            "isPrototypeOf",
            "propertyIsEnumerable",
            "constructor"
        ],
        dontEnumsLength=dontEnums.length;

    for(varkeyin{"toString":null}){
        hasDontEnumBug=false;
    }

    Object.keys=functionkeys(object){

        if(
            (typeofobject!="object"&&typeofobject!="function")||
            object===null
        ){
            thrownewTypeError("Object.keyscalledonanon-object");
        }

        varkeys=[];
        for(varnameinobject){
            if(owns(object,name)){
                keys.push(name);
            }
        }

        if(hasDontEnumBug){
            for(vari=0,ii=dontEnumsLength;i<ii;i++){
                vardontEnum=dontEnums[i];
                if(owns(object,dontEnum)){
                    keys.push(dontEnum);
                }
            }
        }
        returnkeys;
    };

}
if(!Date.now){
    Date.now=functionnow(){
        returnnewDate().getTime();
    };
}
varws="\x09\x0A\x0B\x0C\x0D\x20\xA0\u1680\u180E\u2000\u2001\u2002\u2003"+
    "\u2004\u2005\u2006\u2007\u2008\u2009\u200A\u202F\u205F\u3000\u2028"+
    "\u2029\uFEFF";
if(!String.prototype.trim||ws.trim()){
    ws="["+ws+"]";
    vartrimBeginRegexp=newRegExp("^"+ws+ws+"*"),
        trimEndRegexp=newRegExp(ws+ws+"*$");
    String.prototype.trim=functiontrim(){
        returnString(this).replace(trimBeginRegexp,"").replace(trimEndRegexp,"");
    };
}

functiontoInteger(n){
    n=+n;
    if(n!==n){//isNaN
        n=0;
    }elseif(n!==0&&n!==(1/0)&&n!==-(1/0)){
        n=(n>0||-1)*Math.floor(Math.abs(n));
    }
    returnn;
}

functionisPrimitive(input){
    vartype=typeofinput;
    return(
        input===null||
        type==="undefined"||
        type==="boolean"||
        type==="number"||
        type==="string"
    );
}

functiontoPrimitive(input){
    varval,valueOf,toString;
    if(isPrimitive(input)){
        returninput;
    }
    valueOf=input.valueOf;
    if(typeofvalueOf==="function"){
        val=valueOf.call(input);
        if(isPrimitive(val)){
            returnval;
        }
    }
    toString=input.toString;
    if(typeoftoString==="function"){
        val=toString.call(input);
        if(isPrimitive(val)){
            returnval;
        }
    }
    thrownewTypeError();
}
vartoObject=function(o){
    if(o==null){//thismatchesbothnullandundefined
        thrownewTypeError("can'tconvert"+o+"toobject");
    }
    returnObject(o);
};

});

define("ace/lib/fixoldbrowsers",["require","exports","module","ace/lib/regexp","ace/lib/es5-shim"],function(require,exports,module){
"usestrict";

require("./regexp");
require("./es5-shim");

});

define("ace/lib/dom",["require","exports","module"],function(require,exports,module){
"usestrict";

varXHTML_NS="http://www.w3.org/1999/xhtml";

exports.buildDom=functionbuildDom(arr,parent,refs){
    if(typeofarr=="string"&&arr){
        vartxt=document.createTextNode(arr);
        if(parent)
            parent.appendChild(txt);
        returntxt;
    }
    
    if(!Array.isArray(arr))
        returnarr;
    if(typeofarr[0]!="string"||!arr[0]){
        varels=[];
        for(vari=0;i<arr.length;i++){
            varch=buildDom(arr[i],parent,refs);
            ch&&els.push(ch);
        }
        returnels;
    }
    
    varel=document.createElement(arr[0]);
    varoptions=arr[1];
    varchildIndex=1;
    if(options&&typeofoptions=="object"&&!Array.isArray(options))
        childIndex=2;
    for(vari=childIndex;i<arr.length;i++)
        buildDom(arr[i],el,refs);
    if(childIndex==2){
        Object.keys(options).forEach(function(n){
            varval=options[n];
            if(n==="class"){
                el.className=Array.isArray(val)?val.join(""):val;
            }elseif(typeofval=="function"||n=="value"){
                el[n]=val;
            }elseif(n==="ref"){
                if(refs)refs[val]=el;
            }elseif(val!=null){
                el.setAttribute(n,val);
            }
        });
    }
    if(parent)
        parent.appendChild(el);
    returnel;
};

exports.getDocumentHead=function(doc){
    if(!doc)
        doc=document;
    returndoc.head||doc.getElementsByTagName("head")[0]||doc.documentElement;
};

exports.createElement=function(tag,ns){
    returndocument.createElementNS?
           document.createElementNS(ns||XHTML_NS,tag):
           document.createElement(tag);
};

exports.hasCssClass=function(el,name){
    varclasses=(el.className+"").split(/\s+/g);
    returnclasses.indexOf(name)!==-1;
};
exports.addCssClass=function(el,name){
    if(!exports.hasCssClass(el,name)){
        el.className+=""+name;
    }
};
exports.removeCssClass=function(el,name){
    varclasses=el.className.split(/\s+/g);
    while(true){
        varindex=classes.indexOf(name);
        if(index==-1){
            break;
        }
        classes.splice(index,1);
    }
    el.className=classes.join("");
};

exports.toggleCssClass=function(el,name){
    varclasses=el.className.split(/\s+/g),add=true;
    while(true){
        varindex=classes.indexOf(name);
        if(index==-1){
            break;
        }
        add=false;
        classes.splice(index,1);
    }
    if(add)
        classes.push(name);

    el.className=classes.join("");
    returnadd;
};
exports.setCssClass=function(node,className,include){
    if(include){
        exports.addCssClass(node,className);
    }else{
        exports.removeCssClass(node,className);
    }
};

exports.hasCssString=function(id,doc){
    varindex=0,sheets;
    doc=doc||document;

    if(doc.createStyleSheet&&(sheets=doc.styleSheets)){
        while(index<sheets.length)
            if(sheets[index++].owningElement.id===id)returntrue;
    }elseif((sheets=doc.getElementsByTagName("style"))){
        while(index<sheets.length)
            if(sheets[index++].id===id)returntrue;
    }

    returnfalse;
};

exports.importCssString=functionimportCssString(cssText,id,doc){
    doc=doc||document;
    if(id&&exports.hasCssString(id,doc))
        returnnull;
    
    varstyle;
    
    if(id)
        cssText+="\n/*#sourceURL=ace/css/"+id+"*/";
    
    if(doc.createStyleSheet){
        style=doc.createStyleSheet();
        style.cssText=cssText;
        if(id)
            style.owningElement.id=id;
    }else{
        style=exports.createElement("style");
        style.appendChild(doc.createTextNode(cssText));
        if(id)
            style.id=id;

        exports.getDocumentHead(doc).appendChild(style);
    }
};

exports.importCssStylsheet=function(uri,doc){
    if(doc.createStyleSheet){
        doc.createStyleSheet(uri);
    }else{
        varlink=exports.createElement('link');
        link.rel='stylesheet';
        link.href=uri;

        exports.getDocumentHead(doc).appendChild(link);
    }
};

exports.getInnerWidth=function(element){
    return(
        parseInt(exports.computedStyle(element,"paddingLeft"),10)+
        parseInt(exports.computedStyle(element,"paddingRight"),10)+
        element.clientWidth
    );
};

exports.getInnerHeight=function(element){
    return(
        parseInt(exports.computedStyle(element,"paddingTop"),10)+
        parseInt(exports.computedStyle(element,"paddingBottom"),10)+
        element.clientHeight
    );
};

exports.scrollbarWidth=function(document){
    varinner=exports.createElement("ace_inner");
    inner.style.width="100%";
    inner.style.minWidth="0px";
    inner.style.height="200px";
    inner.style.display="block";

    varouter=exports.createElement("ace_outer");
    varstyle=outer.style;

    style.position="absolute";
    style.left="-10000px";
    style.overflow="hidden";
    style.width="200px";
    style.minWidth="0px";
    style.height="150px";
    style.display="block";

    outer.appendChild(inner);

    varbody=document.documentElement;
    body.appendChild(outer);

    varnoScrollbar=inner.offsetWidth;

    style.overflow="scroll";
    varwithScrollbar=inner.offsetWidth;

    if(noScrollbar==withScrollbar){
        withScrollbar=outer.clientWidth;
    }

    body.removeChild(outer);

    returnnoScrollbar-withScrollbar;
};

if(typeofdocument=="undefined"){
    exports.importCssString=function(){};
    return;
}

if(window.pageYOffset!==undefined){
    exports.getPageScrollTop=function(){
        returnwindow.pageYOffset;
    };

    exports.getPageScrollLeft=function(){
        returnwindow.pageXOffset;
    };
}
else{
    exports.getPageScrollTop=function(){
        returndocument.body.scrollTop;
    };

    exports.getPageScrollLeft=function(){
        returndocument.body.scrollLeft;
    };
}

if(window.getComputedStyle)
    exports.computedStyle=function(element,style){
        if(style)
            return(window.getComputedStyle(element,"")||{})[style]||"";
        returnwindow.getComputedStyle(element,"")||{};
    };
else
    exports.computedStyle=function(element,style){
        if(style)
            returnelement.currentStyle[style];
        returnelement.currentStyle;
    };
exports.setInnerHtml=function(el,innerHtml){
    varelement=el.cloneNode(false);//document.createElement("div");
    element.innerHTML=innerHtml;
    el.parentNode.replaceChild(element,el);
    returnelement;
};

if("textContent"indocument.documentElement){
    exports.setInnerText=function(el,innerText){
        el.textContent=innerText;
    };

    exports.getInnerText=function(el){
        returnel.textContent;
    };
}
else{
    exports.setInnerText=function(el,innerText){
        el.innerText=innerText;
    };

    exports.getInnerText=function(el){
        returnel.innerText;
    };
}

exports.getParentWindow=function(document){
    returndocument.defaultView||document.parentWindow;
};

});

define("ace/lib/oop",["require","exports","module"],function(require,exports,module){
"usestrict";

exports.inherits=function(ctor,superCtor){
    ctor.super_=superCtor;
    ctor.prototype=Object.create(superCtor.prototype,{
        constructor:{
            value:ctor,
            enumerable:false,
            writable:true,
            configurable:true
        }
    });
};

exports.mixin=function(obj,mixin){
    for(varkeyinmixin){
        obj[key]=mixin[key];
    }
    returnobj;
};

exports.implement=function(proto,mixin){
    exports.mixin(proto,mixin);
};

});

define("ace/lib/keys",["require","exports","module","ace/lib/fixoldbrowsers","ace/lib/oop"],function(require,exports,module){
"usestrict";

require("./fixoldbrowsers");

varoop=require("./oop");
varKeys=(function(){
    varret={
        MODIFIER_KEYS:{
            16:'Shift',17:'Ctrl',18:'Alt',224:'Meta'
        },

        KEY_MODS:{
            "ctrl":1,"alt":2,"option":2,"shift":4,
            "super":8,"meta":8,"command":8,"cmd":8
        },

        FUNCTION_KEYS:{
            8 :"Backspace",
            9 :"Tab",
            13:"Return",
            19:"Pause",
            27:"Esc",
            32:"Space",
            33:"PageUp",
            34:"PageDown",
            35:"End",
            36:"Home",
            37:"Left",
            38:"Up",
            39:"Right",
            40:"Down",
            44:"Print",
            45:"Insert",
            46:"Delete",
            96:"Numpad0",
            97:"Numpad1",
            98:"Numpad2",
            99:"Numpad3",
            100:"Numpad4",
            101:"Numpad5",
            102:"Numpad6",
            103:"Numpad7",
            104:"Numpad8",
            105:"Numpad9",
            '-13':"NumpadEnter",
            112:"F1",
            113:"F2",
            114:"F3",
            115:"F4",
            116:"F5",
            117:"F6",
            118:"F7",
            119:"F8",
            120:"F9",
            121:"F10",
            122:"F11",
            123:"F12",
            144:"Numlock",
            145:"Scrolllock"
        },

        PRINTABLE_KEYS:{
           32:'', 48:'0', 49:'1', 50:'2', 51:'3', 52:'4',53: '5',
           54:'6', 55:'7', 56:'8', 57:'9', 59:';', 61:'=',65: 'a',
           66:'b', 67:'c', 68:'d', 69:'e', 70:'f', 71:'g',72: 'h',
           73:'i', 74:'j', 75:'k', 76:'l', 77:'m', 78:'n',79: 'o',
           80:'p', 81:'q', 82:'r', 83:'s', 84:'t', 85:'u',86: 'v',
           87:'w', 88:'x', 89:'y', 90:'z',107:'+',109:'-',110:'.',
          186:';',187:'=',188:',',189:'-',190:'.',191:'/',192:'`',
          219:'[',220:'\\',221:']',222:"'",111:'/',106:'*'
        }
    };
    varname,i;
    for(iinret.FUNCTION_KEYS){
        name=ret.FUNCTION_KEYS[i].toLowerCase();
        ret[name]=parseInt(i,10);
    }
    for(iinret.PRINTABLE_KEYS){
        name=ret.PRINTABLE_KEYS[i].toLowerCase();
        ret[name]=parseInt(i,10);
    }
    oop.mixin(ret,ret.MODIFIER_KEYS);
    oop.mixin(ret,ret.PRINTABLE_KEYS);
    oop.mixin(ret,ret.FUNCTION_KEYS);
    ret.enter=ret["return"];
    ret.escape=ret.esc;
    ret.del=ret["delete"];
    ret[173]='-';
    
    (function(){
        varmods=["cmd","ctrl","alt","shift"];
        for(vari=Math.pow(2,mods.length);i--;){           
            ret.KEY_MODS[i]=mods.filter(function(x){
                returni&ret.KEY_MODS[x];
            }).join("-")+"-";
        }
    })();

    ret.KEY_MODS[0]="";
    ret.KEY_MODS[-1]="input-";

    returnret;
})();
oop.mixin(exports,Keys);

exports.keyCodeToString=function(keyCode){
    varkeyString=Keys[keyCode];
    if(typeofkeyString!="string")
        keyString=String.fromCharCode(keyCode);
    returnkeyString.toLowerCase();
};

});

define("ace/lib/useragent",["require","exports","module"],function(require,exports,module){
"usestrict";
exports.OS={
    LINUX:"LINUX",
    MAC:"MAC",
    WINDOWS:"WINDOWS"
};
exports.getOS=function(){
    if(exports.isMac){
        returnexports.OS.MAC;
    }elseif(exports.isLinux){
        returnexports.OS.LINUX;
    }else{
        returnexports.OS.WINDOWS;
    }
};
if(typeofnavigator!="object")
    return;

varos=(navigator.platform.match(/mac|win|linux/i)||["other"])[0].toLowerCase();
varua=navigator.userAgent;
exports.isWin=(os=="win");
exports.isMac=(os=="mac");
exports.isLinux=(os=="linux");
exports.isIE=
    (navigator.appName=="MicrosoftInternetExplorer"||navigator.appName.indexOf("MSAppHost")>=0)
    ?parseFloat((ua.match(/(?:MSIE|Trident\/[0-9]+[\.0-9]+;.*rv:)([0-9]+[\.0-9]+)/)||[])[1])
    :parseFloat((ua.match(/(?:Trident\/[0-9]+[\.0-9]+;.*rv:)([0-9]+[\.0-9]+)/)||[])[1]);//forie
    
exports.isOldIE=exports.isIE&&exports.isIE<9;
exports.isGecko=exports.isMozilla=ua.match(/Gecko\/\d+/);
exports.isOpera=window.opera&&Object.prototype.toString.call(window.opera)=="[objectOpera]";
exports.isWebKit=parseFloat(ua.split("WebKit/")[1])||undefined;

exports.isChrome=parseFloat(ua.split("Chrome/")[1])||undefined;

exports.isAIR=ua.indexOf("AdobeAIR")>=0;

exports.isIPad=ua.indexOf("iPad")>=0;

exports.isChromeOS=ua.indexOf("CrOS")>=0;

exports.isIOS=/iPad|iPhone|iPod/.test(ua)&&!window.MSStream;

if(exports.isIOS)exports.isMac=true;

});

define("ace/lib/event",["require","exports","module","ace/lib/keys","ace/lib/useragent"],function(require,exports,module){
"usestrict";

varkeys=require("./keys");
varuseragent=require("./useragent");

varpressedKeys=null;
varts=0;

exports.addListener=function(elem,type,callback){
    if(elem.addEventListener){
        returnelem.addEventListener(type,callback,false);
    }
    if(elem.attachEvent){
        varwrapper=function(){
            callback.call(elem,window.event);
        };
        callback._wrapper=wrapper;
        elem.attachEvent("on"+type,wrapper);
    }
};

exports.removeListener=function(elem,type,callback){
    if(elem.removeEventListener){
        returnelem.removeEventListener(type,callback,false);
    }
    if(elem.detachEvent){
        elem.detachEvent("on"+type,callback._wrapper||callback);
    }
};
exports.stopEvent=function(e){
    exports.stopPropagation(e);
    exports.preventDefault(e);
    returnfalse;
};

exports.stopPropagation=function(e){
    if(e.stopPropagation)
        e.stopPropagation();
    else
        e.cancelBubble=true;
};

exports.preventDefault=function(e){
    if(e.preventDefault)
        e.preventDefault();
    else
        e.returnValue=false;
};
exports.getButton=function(e){
    if(e.type=="dblclick")
        return0;
    if(e.type=="contextmenu"||(useragent.isMac&&(e.ctrlKey&&!e.altKey&&!e.shiftKey)))
        return2;
    if(e.preventDefault){
        returne.button;
    }
    else{
        return{1:0,2:2,4:1}[e.button];
    }
};

exports.capture=function(el,eventHandler,releaseCaptureHandler){
    functiononMouseUp(e){
        eventHandler&&eventHandler(e);
        releaseCaptureHandler&&releaseCaptureHandler(e);

        exports.removeListener(document,"mousemove",eventHandler,true);
        exports.removeListener(document,"mouseup",onMouseUp,true);
        exports.removeListener(document,"dragstart",onMouseUp,true);
    }

    exports.addListener(document,"mousemove",eventHandler,true);
    exports.addListener(document,"mouseup",onMouseUp,true);
    exports.addListener(document,"dragstart",onMouseUp,true);
    
    returnonMouseUp;
};

exports.addTouchMoveListener=function(el,callback){
    varstartx,starty;
    exports.addListener(el,"touchstart",function(e){
        vartouches=e.touches;
        vartouchObj=touches[0];
        startx=touchObj.clientX;
        starty=touchObj.clientY;
    });
    exports.addListener(el,"touchmove",function(e){
        vartouches=e.touches;
        if(touches.length>1)return;
        
        vartouchObj=touches[0];

        e.wheelX=startx-touchObj.clientX;
        e.wheelY=starty-touchObj.clientY;

        startx=touchObj.clientX;
        starty=touchObj.clientY;

        callback(e);
    });
};

exports.addMouseWheelListener=function(el,callback){
    if("onmousewheel"inel){
        exports.addListener(el,"mousewheel",function(e){
            varfactor=8;
            if(e.wheelDeltaX!==undefined){
                e.wheelX=-e.wheelDeltaX/factor;
                e.wheelY=-e.wheelDeltaY/factor;
            }else{
                e.wheelX=0;
                e.wheelY=-e.wheelDelta/factor;
            }
            callback(e);
        });
    }elseif("onwheel"inel){
        exports.addListener(el,"wheel", function(e){
            varfactor=0.35;
            switch(e.deltaMode){
                casee.DOM_DELTA_PIXEL:
                    e.wheelX=e.deltaX*factor||0;
                    e.wheelY=e.deltaY*factor||0;
                    break;
                casee.DOM_DELTA_LINE:
                casee.DOM_DELTA_PAGE:
                    e.wheelX=(e.deltaX||0)*5;
                    e.wheelY=(e.deltaY||0)*5;
                    break;
            }
            
            callback(e);
        });
    }else{
        exports.addListener(el,"DOMMouseScroll",function(e){
            if(e.axis&&e.axis==e.HORIZONTAL_AXIS){
                e.wheelX=(e.detail||0)*5;
                e.wheelY=0;
            }else{
                e.wheelX=0;
                e.wheelY=(e.detail||0)*5;
            }
            callback(e);
        });
    }
};

exports.addMultiMouseDownListener=function(elements,timeouts,eventHandler,callbackName){
    varclicks=0;
    varstartX,startY,timer;
    vareventNames={
        2:"dblclick",
        3:"tripleclick",
        4:"quadclick"
    };

    functiononMousedown(e){
        if(exports.getButton(e)!==0){
            clicks=0;
        }elseif(e.detail>1){
            clicks++;
            if(clicks>4)
                clicks=1;
        }else{
            clicks=1;
        }
        if(useragent.isIE){
            varisNewClick=Math.abs(e.clientX-startX)>5||Math.abs(e.clientY-startY)>5;
            if(!timer||isNewClick)
                clicks=1;
            if(timer)
                clearTimeout(timer);
            timer=setTimeout(function(){timer=null;},timeouts[clicks-1]||600);

            if(clicks==1){
                startX=e.clientX;
                startY=e.clientY;
            }
        }
        
        e._clicks=clicks;

        eventHandler[callbackName]("mousedown",e);

        if(clicks>4)
            clicks=0;
        elseif(clicks>1)
            returneventHandler[callbackName](eventNames[clicks],e);
    }
    functiononDblclick(e){
        clicks=2;
        if(timer)
            clearTimeout(timer);
        timer=setTimeout(function(){timer=null;},timeouts[clicks-1]||600);
        eventHandler[callbackName]("mousedown",e);
        eventHandler[callbackName](eventNames[clicks],e);
    }
    if(!Array.isArray(elements))
        elements=[elements];
    elements.forEach(function(el){
        exports.addListener(el,"mousedown",onMousedown);
        if(useragent.isOldIE)
            exports.addListener(el,"dblclick",onDblclick);
    });
};

vargetModifierHash=useragent.isMac&&useragent.isOpera&&!("KeyboardEvent"inwindow)
    ?function(e){
        return0|(e.metaKey?1:0)|(e.altKey?2:0)|(e.shiftKey?4:0)|(e.ctrlKey?8:0);
    }
    :function(e){
        return0|(e.ctrlKey?1:0)|(e.altKey?2:0)|(e.shiftKey?4:0)|(e.metaKey?8:0);
    };

exports.getModifierString=function(e){
    returnkeys.KEY_MODS[getModifierHash(e)];
};

functionnormalizeCommandKeys(callback,e,keyCode){
    varhashId=getModifierHash(e);

    if(!useragent.isMac&&pressedKeys){
        if(e.getModifierState&&(e.getModifierState("OS")||e.getModifierState("Win")))
            hashId|=8;
        if(pressedKeys.altGr){
            if((3&hashId)!=3)
                pressedKeys.altGr=0;
            else
                return;
        }
        if(keyCode===18||keyCode===17){
            varlocation="location"ine?e.location:e.keyLocation;
            if(keyCode===17&&location===1){
                if(pressedKeys[keyCode]==1)
                    ts=e.timeStamp;
            }elseif(keyCode===18&&hashId===3&&location===2){
                vardt=e.timeStamp-ts;
                if(dt<50)
                    pressedKeys.altGr=true;
            }
        }
    }
    
    if(keyCodeinkeys.MODIFIER_KEYS){
        keyCode=-1;
    }
    if(hashId&8&&(keyCode>=91&&keyCode<=93)){
        keyCode=-1;
    }
    
    if(!hashId&&keyCode===13){
        varlocation="location"ine?e.location:e.keyLocation;
        if(location===3){
            callback(e,hashId,-keyCode);
            if(e.defaultPrevented)
                return;
        }
    }
    
    if(useragent.isChromeOS&&hashId&8){
        callback(e,hashId,keyCode);
        if(e.defaultPrevented)
            return;
        else
            hashId&=~8;
    }
    if(!hashId&&!(keyCodeinkeys.FUNCTION_KEYS)&&!(keyCodeinkeys.PRINTABLE_KEYS)){
        returnfalse;
    }
    
    returncallback(e,hashId,keyCode);
}


exports.addCommandKeyListener=function(el,callback){
    varaddListener=exports.addListener;
    if(useragent.isOldGecko||(useragent.isOpera&&!("KeyboardEvent"inwindow))){
        varlastKeyDownKeyCode=null;
        addListener(el,"keydown",function(e){
            lastKeyDownKeyCode=e.keyCode;
        });
        addListener(el,"keypress",function(e){
            returnnormalizeCommandKeys(callback,e,lastKeyDownKeyCode);
        });
    }else{
        varlastDefaultPrevented=null;

        addListener(el,"keydown",function(e){
            pressedKeys[e.keyCode]=(pressedKeys[e.keyCode]||0)+1;
            varresult=normalizeCommandKeys(callback,e,e.keyCode);
            lastDefaultPrevented=e.defaultPrevented;
            returnresult;
        });

        addListener(el,"keypress",function(e){
            if(lastDefaultPrevented&&(e.ctrlKey||e.altKey||e.shiftKey||e.metaKey)){
                exports.stopEvent(e);
                lastDefaultPrevented=null;
            }
        });

        addListener(el,"keyup",function(e){
            pressedKeys[e.keyCode]=null;
        });

        if(!pressedKeys){
            resetPressedKeys();
            addListener(window,"focus",resetPressedKeys);
        }
    }
};
functionresetPressedKeys(){
    pressedKeys=Object.create(null);
}

if(typeofwindow=="object"&&window.postMessage&&!useragent.isOldIE){
    varpostMessageId=1;
    exports.nextTick=function(callback,win){
        win=win||window;
        varmessageName="zero-timeout-message-"+postMessageId;
        exports.addListener(win,"message",functionlistener(e){
            if(e.data==messageName){
                exports.stopPropagation(e);
                exports.removeListener(win,"message",listener);
                callback();
            }
        });
        win.postMessage(messageName,"*");
    };
}


exports.nextFrame=typeofwindow=="object"&&(window.requestAnimationFrame
    ||window.mozRequestAnimationFrame
    ||window.webkitRequestAnimationFrame
    ||window.msRequestAnimationFrame
    ||window.oRequestAnimationFrame);

if(exports.nextFrame)
    exports.nextFrame=exports.nextFrame.bind(window);
else
    exports.nextFrame=function(callback){
        setTimeout(callback,17);
    };
});

define("ace/range",["require","exports","module"],function(require,exports,module){
"usestrict";
varcomparePoints=function(p1,p2){
    returnp1.row-p2.row||p1.column-p2.column;
};
varRange=function(startRow,startColumn,endRow,endColumn){
    this.start={
        row:startRow,
        column:startColumn
    };

    this.end={
        row:endRow,
        column:endColumn
    };
};

(function(){
    this.isEqual=function(range){
        returnthis.start.row===range.start.row&&
            this.end.row===range.end.row&&
            this.start.column===range.start.column&&
            this.end.column===range.end.column;
    };
    this.toString=function(){
        return("Range:["+this.start.row+"/"+this.start.column+
            "]->["+this.end.row+"/"+this.end.column+"]");
    };

    this.contains=function(row,column){
        returnthis.compare(row,column)==0;
    };
    this.compareRange=function(range){
        varcmp,
            end=range.end,
            start=range.start;

        cmp=this.compare(end.row,end.column);
        if(cmp==1){
            cmp=this.compare(start.row,start.column);
            if(cmp==1){
                return2;
            }elseif(cmp==0){
                return1;
            }else{
                return0;
            }
        }elseif(cmp==-1){
            return-2;
        }else{
            cmp=this.compare(start.row,start.column);
            if(cmp==-1){
                return-1;
            }elseif(cmp==1){
                return42;
            }else{
                return0;
            }
        }
    };
    this.comparePoint=function(p){
        returnthis.compare(p.row,p.column);
    };
    this.containsRange=function(range){
        returnthis.comparePoint(range.start)==0&&this.comparePoint(range.end)==0;
    };
    this.intersects=function(range){
        varcmp=this.compareRange(range);
        return(cmp==-1||cmp==0||cmp==1);
    };
    this.isEnd=function(row,column){
        returnthis.end.row==row&&this.end.column==column;
    };
    this.isStart=function(row,column){
        returnthis.start.row==row&&this.start.column==column;
    };
    this.setStart=function(row,column){
        if(typeofrow=="object"){
            this.start.column=row.column;
            this.start.row=row.row;
        }else{
            this.start.row=row;
            this.start.column=column;
        }
    };
    this.setEnd=function(row,column){
        if(typeofrow=="object"){
            this.end.column=row.column;
            this.end.row=row.row;
        }else{
            this.end.row=row;
            this.end.column=column;
        }
    };
    this.inside=function(row,column){
        if(this.compare(row,column)==0){
            if(this.isEnd(row,column)||this.isStart(row,column)){
                returnfalse;
            }else{
                returntrue;
            }
        }
        returnfalse;
    };
    this.insideStart=function(row,column){
        if(this.compare(row,column)==0){
            if(this.isEnd(row,column)){
                returnfalse;
            }else{
                returntrue;
            }
        }
        returnfalse;
    };
    this.insideEnd=function(row,column){
        if(this.compare(row,column)==0){
            if(this.isStart(row,column)){
                returnfalse;
            }else{
                returntrue;
            }
        }
        returnfalse;
    };
    this.compare=function(row,column){
        if(!this.isMultiLine()){
            if(row===this.start.row){
                returncolumn<this.start.column?-1:(column>this.end.column?1:0);
            }
        }

        if(row<this.start.row)
            return-1;

        if(row>this.end.row)
            return1;

        if(this.start.row===row)
            returncolumn>=this.start.column?0:-1;

        if(this.end.row===row)
            returncolumn<=this.end.column?0:1;

        return0;
    };
    this.compareStart=function(row,column){
        if(this.start.row==row&&this.start.column==column){
            return-1;
        }else{
            returnthis.compare(row,column);
        }
    };
    this.compareEnd=function(row,column){
        if(this.end.row==row&&this.end.column==column){
            return1;
        }else{
            returnthis.compare(row,column);
        }
    };
    this.compareInside=function(row,column){
        if(this.end.row==row&&this.end.column==column){
            return1;
        }elseif(this.start.row==row&&this.start.column==column){
            return-1;
        }else{
            returnthis.compare(row,column);
        }
    };
    this.clipRows=function(firstRow,lastRow){
        if(this.end.row>lastRow)
            varend={row:lastRow+1,column:0};
        elseif(this.end.row<firstRow)
            varend={row:firstRow,column:0};

        if(this.start.row>lastRow)
            varstart={row:lastRow+1,column:0};
        elseif(this.start.row<firstRow)
            varstart={row:firstRow,column:0};

        returnRange.fromPoints(start||this.start,end||this.end);
    };
    this.extend=function(row,column){
        varcmp=this.compare(row,column);

        if(cmp==0)
            returnthis;
        elseif(cmp==-1)
            varstart={row:row,column:column};
        else
            varend={row:row,column:column};

        returnRange.fromPoints(start||this.start,end||this.end);
    };

    this.isEmpty=function(){
        return(this.start.row===this.end.row&&this.start.column===this.end.column);
    };
    this.isMultiLine=function(){
        return(this.start.row!==this.end.row);
    };
    this.clone=function(){
        returnRange.fromPoints(this.start,this.end);
    };
    this.collapseRows=function(){
        if(this.end.column==0)
            returnnewRange(this.start.row,0,Math.max(this.start.row,this.end.row-1),0);
        else
            returnnewRange(this.start.row,0,this.end.row,0);
    };
    this.toScreenRange=function(session){
        varscreenPosStart=session.documentToScreenPosition(this.start);
        varscreenPosEnd=session.documentToScreenPosition(this.end);

        returnnewRange(
            screenPosStart.row,screenPosStart.column,
            screenPosEnd.row,screenPosEnd.column
        );
    };
    this.moveBy=function(row,column){
        this.start.row+=row;
        this.start.column+=column;
        this.end.row+=row;
        this.end.column+=column;
    };

}).call(Range.prototype);
Range.fromPoints=function(start,end){
    returnnewRange(start.row,start.column,end.row,end.column);
};
Range.comparePoints=comparePoints;

Range.comparePoints=function(p1,p2){
    returnp1.row-p2.row||p1.column-p2.column;
};


exports.Range=Range;
});

define("ace/lib/lang",["require","exports","module"],function(require,exports,module){
"usestrict";

exports.last=function(a){
    returna[a.length-1];
};

exports.stringReverse=function(string){
    returnstring.split("").reverse().join("");
};

exports.stringRepeat=function(string,count){
    varresult='';
    while(count>0){
        if(count&1)
            result+=string;

        if(count>>=1)
            string+=string;
    }
    returnresult;
};

vartrimBeginRegexp=/^\s\s*/;
vartrimEndRegexp=/\s\s*$/;

exports.stringTrimLeft=function(string){
    returnstring.replace(trimBeginRegexp,'');
};

exports.stringTrimRight=function(string){
    returnstring.replace(trimEndRegexp,'');
};

exports.copyObject=function(obj){
    varcopy={};
    for(varkeyinobj){
        copy[key]=obj[key];
    }
    returncopy;
};

exports.copyArray=function(array){
    varcopy=[];
    for(vari=0,l=array.length;i<l;i++){
        if(array[i]&&typeofarray[i]=="object")
            copy[i]=this.copyObject(array[i]);
        else
            copy[i]=array[i];
    }
    returncopy;
};

exports.deepCopy=functiondeepCopy(obj){
    if(typeofobj!=="object"||!obj)
        returnobj;
    varcopy;
    if(Array.isArray(obj)){
        copy=[];
        for(varkey=0;key<obj.length;key++){
            copy[key]=deepCopy(obj[key]);
        }
        returncopy;
    }
    if(Object.prototype.toString.call(obj)!=="[objectObject]")
        returnobj;
    
    copy={};
    for(varkeyinobj)
        copy[key]=deepCopy(obj[key]);
    returncopy;
};

exports.arrayToMap=function(arr){
    varmap={};
    for(vari=0;i<arr.length;i++){
        map[arr[i]]=1;
    }
    returnmap;

};

exports.createMap=function(props){
    varmap=Object.create(null);
    for(variinprops){
        map[i]=props[i];
    }
    returnmap;
};
exports.arrayRemove=function(array,value){
  for(vari=0;i<=array.length;i++){
    if(value===array[i]){
      array.splice(i,1);
    }
  }
};

exports.escapeRegExp=function(str){
    returnstr.replace(/([.*+?^${}()|[\]\/\\])/g,'\\$1');
};

exports.escapeHTML=function(str){
    returnstr.replace(/&/g,"&#38;").replace(/"/g,"&#34;").replace(/'/g,"&#39;").replace(/</g,"&#60;");
};

exports.getMatchOffsets=function(string,regExp){
    varmatches=[];

    string.replace(regExp,function(str){
        matches.push({
            offset:arguments[arguments.length-2],
            length:str.length
        });
    });

    returnmatches;
};
exports.deferredCall=function(fcn){
    vartimer=null;
    varcallback=function(){
        timer=null;
        fcn();
    };

    vardeferred=function(timeout){
        deferred.cancel();
        timer=setTimeout(callback,timeout||0);
        returndeferred;
    };

    deferred.schedule=deferred;

    deferred.call=function(){
        this.cancel();
        fcn();
        returndeferred;
    };

    deferred.cancel=function(){
        clearTimeout(timer);
        timer=null;
        returndeferred;
    };
    
    deferred.isPending=function(){
        returntimer;
    };

    returndeferred;
};


exports.delayedCall=function(fcn,defaultTimeout){
    vartimer=null;
    varcallback=function(){
        timer=null;
        fcn();
    };

    var_self=function(timeout){
        if(timer==null)
            timer=setTimeout(callback,timeout||defaultTimeout);
    };

    _self.delay=function(timeout){
        timer&&clearTimeout(timer);
        timer=setTimeout(callback,timeout||defaultTimeout);
    };
    _self.schedule=_self;

    _self.call=function(){
        this.cancel();
        fcn();
    };

    _self.cancel=function(){
        timer&&clearTimeout(timer);
        timer=null;
    };

    _self.isPending=function(){
        returntimer;
    };

    return_self;
};
});

define("ace/keyboard/textinput_ios",["require","exports","module","ace/lib/event","ace/lib/useragent","ace/lib/dom","ace/lib/lang","ace/lib/keys"],function(require,exports,module){
"usestrict";

varevent=require("../lib/event");
varuseragent=require("../lib/useragent");
vardom=require("../lib/dom");
varlang=require("../lib/lang");
varKEYS=require("../lib/keys");
varMODS=KEYS.KEY_MODS;
varBROKEN_SETDATA=useragent.isChrome<18;
varUSE_IE_MIME_TYPE= useragent.isIE;

varTextInput=function(parentNode,host){
    varself=this;
    vartext=dom.createElement("textarea");
    text.className=useragent.isIOS?"ace_text-inputace_text-input-ios":"ace_text-input";

    if(useragent.isTouchPad)
        text.setAttribute("x-palm-disable-auto-cap",true);

    text.setAttribute("wrap","off");
    text.setAttribute("autocorrect","off");
    text.setAttribute("autocapitalize","off");
    text.setAttribute("spellcheck",false);

    text.style.opacity="0";
    parentNode.insertBefore(text,parentNode.firstChild);

    varPLACEHOLDER="\naaaaa\n";

    varcopied=false;
    varcut=false;
    varpasted=false;
    varinComposition=false;
    vartempStyle='';
    varisSelectionEmpty=true;
    try{varisFocused=document.activeElement===text;}catch(e){}
    
    event.addListener(text,"blur",function(e){
        host.onBlur(e);
        isFocused=false;
    });
    event.addListener(text,"focus",function(e){
        isFocused=true;
        host.onFocus(e);
        resetSelection();
    });
    this.focus=function(){
        if(tempStyle)returntext.focus();
        text.style.position="fixed";
        text.focus();
    };
    this.blur=function(){
        text.blur();
    };
    this.isFocused=function(){
        returnisFocused;
    };
    varsyncSelection=lang.delayedCall(function(){
        isFocused&&resetSelection(isSelectionEmpty);
    });
    varsyncValue=lang.delayedCall(function(){
         if(!inComposition){
            text.value=PLACEHOLDER;
            isFocused&&resetSelection();
         }
    });

    functionresetSelection(isEmpty){
        if(inComposition)
            return;
        inComposition=true;
        
        if(inputHandler){
            selectionStart=0;
            selectionEnd=isEmpty?0:text.value.length-1;
        }else{
            varselectionStart=4;
            varselectionEnd=5;
        }
        try{
            text.setSelectionRange(selectionStart,selectionEnd);
        }catch(e){}
        
        inComposition=false;
    }

    functionresetValue(){
        if(inComposition)
            return;
        text.value=PLACEHOLDER;
        if(useragent.isWebKit)
            syncValue.schedule();
    }

    useragent.isWebKit||host.addEventListener('changeSelection',function(){
        if(host.selection.isEmpty()!=isSelectionEmpty){
            isSelectionEmpty=!isSelectionEmpty;
            syncSelection.schedule();
        }
    });

    resetValue();
    if(isFocused)
        host.onFocus();


    varisAllSelected=function(text){
        returntext.selectionStart===0&&text.selectionEnd===text.value.length;
    };

    varonSelect=function(e){
        if(isAllSelected(text)){
            host.selectAll();
            resetSelection();
        }elseif(inputHandler){
            resetSelection(host.selection.isEmpty());
        }
    };

    varinputHandler=null;
    this.setInputHandler=function(cb){inputHandler=cb;};
    this.getInputHandler=function(){returninputHandler;};
    varafterContextMenu=false;
    
    varsendText=function(data){
        if(text.selectionStart===4&&text.selectionEnd===5){
          return;
        }
        if(inputHandler){
            data=inputHandler(data);
            inputHandler=null;
        }
        if(pasted){
            resetSelection();
            if(data)
                host.onPaste(data);
            pasted=false;
        }elseif(data==PLACEHOLDER.substr(0)&&text.selectionStart===4){
            if(afterContextMenu)
                host.execCommand("del",{source:"ace"});
            else//someversionsofandroiddonotfirekeydownwhenpressingbackspace
                host.execCommand("backspace",{source:"ace"});
        }elseif(!copied){
            if(data.substring(0,9)==PLACEHOLDER&&data.length>PLACEHOLDER.length)
                data=data.substr(9);
            elseif(data.substr(0,4)==PLACEHOLDER.substr(0,4))
                data=data.substr(4,data.length-PLACEHOLDER.length+1);
            elseif(data.charAt(data.length-1)==PLACEHOLDER.charAt(0))
                data=data.slice(0,-1);
            if(data==PLACEHOLDER.charAt(0)){
            }elseif(data.charAt(data.length-1)==PLACEHOLDER.charAt(0))
                data=data.slice(0,-1);
            
            if(data)
                host.onTextInput(data);
        }
        if(copied){
          copied=false;
        }
        if(afterContextMenu)
            afterContextMenu=false;
    };
    varonInput=function(e){
        if(inComposition)
            return;
        vardata=text.value;
        sendText(data);
        resetValue();
    };
    
    varhandleClipboardData=function(e,data,forceIEMime){
        varclipboardData=e.clipboardData||window.clipboardData;
        if(!clipboardData||BROKEN_SETDATA)
            return;
        varmime=USE_IE_MIME_TYPE||forceIEMime?"Text":"text/plain";
        try{
            if(data){
                returnclipboardData.setData(mime,data)!==false;
            }else{
                returnclipboardData.getData(mime);
            }
        }catch(e){
            if(!forceIEMime)
                returnhandleClipboardData(e,data,true);
        }
    };

    vardoCopy=function(e,isCut){
        vardata=host.getCopyText();
        if(!data)
            returnevent.preventDefault(e);

        if(handleClipboardData(e,data)){
            if(useragent.isIOS){
                cut=isCut;
                text.value="\naa"+data+"aa\n";
                text.setSelectionRange(4,4+data.length);
                copied={
                    value:data
                };
            }
            isCut?host.onCut():host.onCopy();
            if(!useragent.isIOS)event.preventDefault(e);
        }else{
            copied=true;
            text.value=data;
            text.select();
            setTimeout(function(){
                copied=false;
                resetValue();
                resetSelection();
                isCut?host.onCut():host.onCopy();
            });
        }
    };
    
    varonCut=function(e){
        doCopy(e,true);
    };
    
    varonCopy=function(e){
        doCopy(e,false);
    };
    
    varonPaste=function(e){
        vardata=handleClipboardData(e);
        if(typeofdata=="string"){
            if(data)
                host.onPaste(data,e);
            if(useragent.isIE)
                setTimeout(resetSelection);
            event.preventDefault(e);
        }
        else{
            text.value="";
            pasted=true;
        }
    };

    event.addCommandKeyListener(text,host.onCommandKey.bind(host));

    event.addListener(text,"select",onSelect);

    event.addListener(text,"input",onInput);

    event.addListener(text,"cut",onCut);
    event.addListener(text,"copy",onCopy);
    event.addListener(text,"paste",onPaste);
    varonCompositionStart=function(e){
        if(inComposition||!host.onCompositionStart||host.$readOnly)
            return;
        inComposition={};
        inComposition.canUndo=host.session.$undoManager;
        host.onCompositionStart();
        setTimeout(onCompositionUpdate,0);
        host.on("mousedown",onCompositionEnd);
        if(inComposition.canUndo&&!host.selection.isEmpty()){
            host.insert("");
            host.session.markUndoGroup();
            host.selection.clearSelection();
        }
        host.session.markUndoGroup();
    };

    varonCompositionUpdate=function(){
        if(!inComposition||!host.onCompositionUpdate||host.$readOnly)
            return;
        varval=text.value.replace(/\x01/g,"");
        if(inComposition.lastValue===val)return;
        
        host.onCompositionUpdate(val);
        if(inComposition.lastValue)
            host.undo();
        if(inComposition.canUndo)
            inComposition.lastValue=val;
        if(inComposition.lastValue){
            varr=host.selection.getRange();
            host.insert(inComposition.lastValue);
            host.session.markUndoGroup();
            inComposition.range=host.selection.getRange();
            host.selection.setRange(r);
            host.selection.clearSelection();
        }
    };

    varonCompositionEnd=function(e){
        if(!host.onCompositionEnd||host.$readOnly)return;
        varc=inComposition;
        inComposition=false;
        vartimer=setTimeout(function(){
            timer=null;
            varstr=text.value.replace(/\x01/g,"");
            if(inComposition)
                return;
            elseif(str==c.lastValue)
                resetValue();
            elseif(!c.lastValue&&str){
                resetValue();
                sendText(str);
            }
        });
        inputHandler=functioncompositionInputHandler(str){
            if(timer)
                clearTimeout(timer);
            str=str.replace(/\x01/g,"");
            if(str==c.lastValue)
                return"";
            if(c.lastValue&&timer)
                host.undo();
            returnstr;
        };
        host.onCompositionEnd();
        host.removeListener("mousedown",onCompositionEnd);
        if(e.type=="compositionend"&&c.range){
            host.selection.setRange(c.range);
        }
        varneedsOnInput=
            (!!useragent.isChrome&&useragent.isChrome>=53)||
            (!!useragent.isWebKit&&useragent.isWebKit>=603);

        if(needsOnInput){
          onInput();
        }
    };
    
    

    varsyncComposition=lang.delayedCall(onCompositionUpdate,50);

    event.addListener(text,"compositionstart",onCompositionStart);
    event.addListener(text,"compositionupdate",function(){syncComposition.schedule();});
    event.addListener(text,"keyup",function(){syncComposition.schedule();});
    event.addListener(text,"keydown",function(){syncComposition.schedule();});
    event.addListener(text,"compositionend",onCompositionEnd);

    this.getElement=function(){
        returntext;
    };

    this.setReadOnly=function(readOnly){
       text.readOnly=readOnly;
    };

    this.onContextMenu=function(e){
        afterContextMenu=true;
        resetSelection(host.selection.isEmpty());
        host._emit("nativecontextmenu",{target:host,domEvent:e});
        this.moveToMouse(e,true);
    };
    
    this.moveToMouse=function(e,bringToFront){
        if(!tempStyle)
            tempStyle=text.style.cssText;
        text.style.cssText=(bringToFront?"z-index:100000;":"")
            +"height:"+text.style.height+";"
            +(useragent.isIE?"opacity:0.1;":"");

        varrect=host.container.getBoundingClientRect();
        varstyle=dom.computedStyle(host.container);
        vartop=rect.top+(parseInt(style.borderTopWidth)||0);
        varleft=rect.left+(parseInt(rect.borderLeftWidth)||0);
        varmaxTop=rect.bottom-top-text.clientHeight-2;
        varmove=function(e){
            text.style.left=e.clientX-left-2+"px";
            text.style.top=Math.min(e.clientY-top-2,maxTop)+"px";
        };
        move(e);

        if(e.type!="mousedown")
            return;

        if(host.renderer.$keepTextAreaAtCursor)
            host.renderer.$keepTextAreaAtCursor=null;

        clearTimeout(closeTimeout);
        if(useragent.isWin)
            event.capture(host.container,move,onContextMenuClose);
    };

    this.onContextMenuClose=onContextMenuClose;
    varcloseTimeout;
    functiononContextMenuClose(){
        clearTimeout(closeTimeout);
        closeTimeout=setTimeout(function(){
            if(tempStyle){
                text.style.cssText=tempStyle;
                tempStyle='';
            }
            if(host.renderer.$keepTextAreaAtCursor==null){
                host.renderer.$keepTextAreaAtCursor=true;
                host.renderer.$moveTextAreaToCursor();
            }
        },0);
    }

    varonContextMenu=function(e){
        host.textInput.onContextMenu(e);
        onContextMenuClose();
    };
    event.addListener(text,"mouseup",onContextMenu);
    event.addListener(text,"mousedown",function(e){
        e.preventDefault();
        onContextMenuClose();
    });
    event.addListener(host.renderer.scroller,"contextmenu",onContextMenu);
    event.addListener(text,"contextmenu",onContextMenu);
    
    if(useragent.isIOS){
        vartypingResetTimeout=null;
        vartyping=false;

        parentNode.addEventListener("keydown",function(e){
            if(typingResetTimeout)clearTimeout(typingResetTimeout);
            typing=true;
        });

        parentNode.addEventListener("keyup",function(e){
            typingResetTimeout=setTimeout(function(){
                typing=false;
            },100);
        });
        vardetectArrowKeys=function(e){
            if(document.activeElement!==text)return;
            if(typing)return;
          
            if(cut){
                returnsetTimeout(function(){
                    cut=false;
                },100);
            }
            varselectionStart=text.selectionStart;
            varselectionEnd=text.selectionEnd;
            text.setSelectionRange(4,5);
            if(selectionStart==selectionEnd){
                switch(selectionStart){
                    case0:host.onCommandKey(null,0,KEYS.up);break;
                    case1:host.onCommandKey(null,0,KEYS.home);break;
                    case2:host.onCommandKey(null,MODS.option,KEYS.left);break;
                    case4:host.onCommandKey(null,0,KEYS.left);break;
                    case5:host.onCommandKey(null,0,KEYS.right);break;
                    case7:host.onCommandKey(null,MODS.option,KEYS.right);break;
                    case8:host.onCommandKey(null,0,KEYS.end);break;
                    case9:host.onCommandKey(null,0,KEYS.down);break;
                }
            }else{
                switch(selectionEnd){
                    case6:host.onCommandKey(null,MODS.shift,KEYS.right);break;
                    case7:host.onCommandKey(null,MODS.shift|MODS.option,KEYS.right);break;
                    case8:host.onCommandKey(null,MODS.shift,KEYS.end);break;
                    case9:host.onCommandKey(null,MODS.shift,KEYS.down);break;
                }
                switch(selectionStart){
                    case0:host.onCommandKey(null,MODS.shift,KEYS.up);break;
                    case1:host.onCommandKey(null,MODS.shift,KEYS.home);break;
                    case2:host.onCommandKey(null,MODS.shift|MODS.option,KEYS.left);break;
                    case3:host.onCommandKey(null,MODS.shift,KEYS.left);break;
                }
            }
        };
        document.addEventListener("selectionchange",detectArrowKeys);
        host.on("destroy",function(){
            document.removeEventListener("selectionchange",detectArrowKeys);
        });
    }
};

exports.TextInput=TextInput;
});

define("ace/keyboard/textinput",["require","exports","module","ace/lib/event","ace/lib/useragent","ace/lib/dom","ace/lib/lang","ace/keyboard/textinput_ios"],function(require,exports,module){
"usestrict";

varevent=require("../lib/event");
varuseragent=require("../lib/useragent");
vardom=require("../lib/dom");
varlang=require("../lib/lang");
varBROKEN_SETDATA=useragent.isChrome<18;
varUSE_IE_MIME_TYPE= useragent.isIE;
varHAS_FOCUS_ARGS=useragent.isChrome>63;

varTextInputIOS=require("./textinput_ios").TextInput;
varTextInput=function(parentNode,host){
    if(useragent.isIOS)
        returnTextInputIOS.call(this,parentNode,host);
    
    vartext=dom.createElement("textarea");
    text.className="ace_text-input";

    text.setAttribute("wrap","off");
    text.setAttribute("autocorrect","off");
    text.setAttribute("autocapitalize","off");
    text.setAttribute("spellcheck",false);

    text.style.opacity="0";
    parentNode.insertBefore(text,parentNode.firstChild);
    varPLACEHOLDER=useragent.isIE?"\x01\x01":"\u2028\u2028";
    varPLACEHOLDER_RE=useragent.isIE?/\x01/g:/\u2028/g;

    varcopied=false;
    varpasted=false;
    varinComposition=false;
    vartempStyle='';
    varisSelectionEmpty=true;
    varcopyWithEmptySelection=false;

    varcommandMode=false;
    try{varisFocused=document.activeElement===text;}catch(e){}
    
    event.addListener(text,"blur",function(e){
        host.onBlur(e);
        isFocused=false;
    });
    event.addListener(text,"focus",function(e){
        isFocused=true;
        host.onFocus(e);
        resetSelection();
    });
    this.$focusScroll=false;
    this.focus=function(){
        if(tempStyle||HAS_FOCUS_ARGS||this.$focusScroll=="browser")
            returntext.focus({preventScroll:true});
        vartop=text.style.top;
        text.style.position="fixed";
        text.style.top="0px";
        varisTransformed=text.getBoundingClientRect().top!=0;
        varancestors=[];
        if(isTransformed){
            vart=text.parentElement;
            while(t){
                ancestors.push(t);
                t.setAttribute("ace_nocontext",true);
                t=t.parentElement;
            }
        }
        text.focus({preventScroll:true});
        if(isTransformed){
            ancestors.forEach(function(p){
                p.removeAttribute("ace_nocontext");
            });
        }
        setTimeout(function(){
            text.style.position="";
            if(text.style.top=="0px")
                text.style.top=top;
        },0);
    };
    this.blur=function(){
        text.blur();
    };
    this.isFocused=function(){
        returnisFocused;
    };
    varsyncSelection=lang.delayedCall(function(){
        isFocused&&resetSelection(isSelectionEmpty);
    });
    varsyncValue=lang.delayedCall(function(){
         if(!inComposition){
            text.value=PLACEHOLDER;
            isFocused&&resetSelection();
         }
    });

    functionresetSelection(isEmpty){
        isEmpty=copyWithEmptySelection?false:isEmpty;
        if(inComposition)
            return;
        inComposition=true;
        
        if(inputHandler){
            varselectionStart=0;
            varselectionEnd=isEmpty?0:text.value.length-1;
        }else{
            varselectionStart=isEmpty?2:1;
            varselectionEnd=2;
        }
        try{
            text.setSelectionRange(selectionStart,selectionEnd);
        }catch(e){}
        
        inComposition=false;
    }

    functionresetValue(){
        if(inComposition)
            return;
        text.value=PLACEHOLDER;
        if(useragent.isWebKit)
            syncValue.schedule();
    }

    useragent.isWebKit||host.addEventListener('changeSelection',function(){
        if(host.selection.isEmpty()!=isSelectionEmpty){
            isSelectionEmpty=!isSelectionEmpty;
            syncSelection.schedule();
        }
    });

    resetValue();
    if(isFocused)
        host.onFocus();


    varisAllSelected=function(text){
        returntext.selectionStart===0&&text.selectionEnd===text.value.length;
    };

    varonSelect=function(e){
        if(copied){
            copied=false;
        }elseif(isAllSelected(text)){
            host.selectAll();
            resetSelection();
        }elseif(inputHandler){
            resetSelection(host.selection.isEmpty());
        }
    };

    varinputHandler=null;
    this.setInputHandler=function(cb){inputHandler=cb;};
    this.getInputHandler=function(){returninputHandler;};
    varafterContextMenu=false;
    
    varsendText=function(data){
        if(inputHandler){
            data=inputHandler(data);
            inputHandler=null;
        }
        if(pasted){
            resetSelection();
            if(data)
                host.onPaste(data);
            pasted=false;
        }elseif(data==PLACEHOLDER.charAt(0)){
            if(afterContextMenu)
                host.execCommand("del",{source:"ace"});
            else//someversionsofandroiddonotfirekeydownwhenpressingbackspace
                host.execCommand("backspace",{source:"ace"});
        }else{
            if(data.substring(0,2)==PLACEHOLDER)
                data=data.substr(2);
            elseif(data.charAt(0)==PLACEHOLDER.charAt(0))
                data=data.substr(1);
            elseif(data.charAt(data.length-1)==PLACEHOLDER.charAt(0))
                data=data.slice(0,-1);
            if(data.charAt(data.length-1)==PLACEHOLDER.charAt(0))
                data=data.slice(0,-1);
            
            if(data)
                host.onTextInput(data);
        }
        if(afterContextMenu)
            afterContextMenu=false;
    };
    varonInput=function(e){
        if(inComposition)
            return;
        vardata=text.value;
        sendText(data);
        resetValue();
    };
    
    varhandleClipboardData=function(e,data,forceIEMime){
        varclipboardData=e.clipboardData||window.clipboardData;
        if(!clipboardData||BROKEN_SETDATA)
            return;
        varmime=USE_IE_MIME_TYPE||forceIEMime?"Text":"text/plain";
        try{
            if(data){
                returnclipboardData.setData(mime,data)!==false;
            }else{
                returnclipboardData.getData(mime);
            }
        }catch(e){
            if(!forceIEMime)
                returnhandleClipboardData(e,data,true);
        }
    };

    vardoCopy=function(e,isCut){
        vardata=host.getCopyText();
        if(!data)
            returnevent.preventDefault(e);

        if(handleClipboardData(e,data)){
            isCut?host.onCut():host.onCopy();
            event.preventDefault(e);
        }else{
            copied=true;
            text.value=data;
            text.select();
            setTimeout(function(){
                copied=false;
                resetValue();
                resetSelection();
                isCut?host.onCut():host.onCopy();
            });
        }
    };
    
    varonCut=function(e){
        doCopy(e,true);
    };
    
    varonCopy=function(e){
        doCopy(e,false);
    };
    
    varonPaste=function(e){
        vardata=handleClipboardData(e);
        if(typeofdata=="string"){
            if(data)
                host.onPaste(data,e);
            if(useragent.isIE)
                setTimeout(resetSelection);
            event.preventDefault(e);
        }
        else{
            text.value="";
            pasted=true;
        }
    };

    event.addCommandKeyListener(text,host.onCommandKey.bind(host));

    event.addListener(text,"select",onSelect);

    event.addListener(text,"input",onInput);

    event.addListener(text,"cut",onCut);
    event.addListener(text,"copy",onCopy);
    event.addListener(text,"paste",onPaste);
    if(!('oncut'intext)||!('oncopy'intext)||!('onpaste'intext)){
        event.addListener(parentNode,"keydown",function(e){
            if((useragent.isMac&&!e.metaKey)||!e.ctrlKey)
                return;

            switch(e.keyCode){
                case67:
                    onCopy(e);
                    break;
                case86:
                    onPaste(e);
                    break;
                case88:
                    onCut(e);
                    break;
            }
        });
    }
    varonCompositionStart=function(e){
        if(inComposition||!host.onCompositionStart||host.$readOnly)
            return;
        inComposition={};
        inComposition.canUndo=host.session.$undoManager;
        host.onCompositionStart();
        setTimeout(onCompositionUpdate,0);
        host.on("mousedown",onCompositionEnd);
        if(inComposition.canUndo&&!host.selection.isEmpty()){
            host.insert("");
            host.session.markUndoGroup();
            host.selection.clearSelection();
        }
        host.session.markUndoGroup();
    };

    varonCompositionUpdate=function(){
        if(!inComposition||!host.onCompositionUpdate||host.$readOnly)
            return;
        varval=text.value.replace(PLACEHOLDER_RE,"");
        if(inComposition.lastValue===val)return;
        
        host.onCompositionUpdate(val);
        if(inComposition.lastValue)
            host.undo();
        if(inComposition.canUndo)
            inComposition.lastValue=val;
        if(inComposition.lastValue){
            varr=host.selection.getRange();
            host.insert(inComposition.lastValue);
            host.session.markUndoGroup();
            inComposition.range=host.selection.getRange();
            host.selection.setRange(r);
            host.selection.clearSelection();
        }
    };

    varonCompositionEnd=function(e){
        if(!host.onCompositionEnd||host.$readOnly)return;
        varc=inComposition;
        inComposition=false;
        vartimer=setTimeout(function(){
            timer=null;
            varstr=text.value.replace(PLACEHOLDER_RE,"");
            if(inComposition)
                return;
            elseif(str==c.lastValue)
                resetValue();
            elseif(!c.lastValue&&str){
                resetValue();
                sendText(str);
            }
        });
        inputHandler=functioncompositionInputHandler(str){
            if(timer)
                clearTimeout(timer);
            str=str.replace(PLACEHOLDER_RE,"");
            if(str==c.lastValue)
                return"";
            if(c.lastValue&&timer)
                host.undo();
            returnstr;
        };
        host.onCompositionEnd();
        host.removeListener("mousedown",onCompositionEnd);
        if(e.type=="compositionend"&&c.range){
            host.selection.setRange(c.range);
        }
        varneedsOnInput=useragent.isIE||
            (useragent.isChrome&&useragent.isChrome>=53)||
            (useragent.isWebKit&&useragent.isWebKit>=603);

        if(needsOnInput){
          onInput();
        }
    };
    
    

    varsyncComposition=lang.delayedCall(onCompositionUpdate,50);

    event.addListener(text,"compositionstart",onCompositionStart);
    event.addListener(text,"compositionupdate",function(){syncComposition.schedule();});
    event.addListener(text,"keyup",function(){syncComposition.schedule();});
    event.addListener(text,"keydown",function(){syncComposition.schedule();});
    event.addListener(text,"compositionend",onCompositionEnd);

    this.getElement=function(){
        returntext;
    };

    this.setCommandMode=function(value){
       commandMode=value;
       text.readOnly=false;
    };
    
    this.setReadOnly=function(readOnly){
        if(!commandMode)
            text.readOnly=readOnly;
    };

    this.setCopyWithEmptySelection=function(value){
        copyWithEmptySelection=value;
    };

    this.onContextMenu=function(e){
        afterContextMenu=true;
        resetSelection(host.selection.isEmpty());
        host._emit("nativecontextmenu",{target:host,domEvent:e});
        this.moveToMouse(e,true);
    };
    
    this.moveToMouse=function(e,bringToFront){
        if(!tempStyle)
            tempStyle=text.style.cssText;
        text.style.cssText=(bringToFront?"z-index:100000;":"")
            +"height:"+text.style.height+";"
            +(useragent.isIE?"opacity:0.1;":"");

        varrect=host.container.getBoundingClientRect();
        varstyle=dom.computedStyle(host.container);
        vartop=rect.top+(parseInt(style.borderTopWidth)||0);
        varleft=rect.left+(parseInt(rect.borderLeftWidth)||0);
        varmaxTop=rect.bottom-top-text.clientHeight-2;
        varmove=function(e){
            text.style.left=e.clientX-left-2+"px";
            text.style.top=Math.min(e.clientY-top-2,maxTop)+"px";
        };
        move(e);

        if(e.type!="mousedown")
            return;

        if(host.renderer.$keepTextAreaAtCursor)
            host.renderer.$keepTextAreaAtCursor=null;

        clearTimeout(closeTimeout);
        if(useragent.isWin)
            event.capture(host.container,move,onContextMenuClose);
    };

    this.onContextMenuClose=onContextMenuClose;
    varcloseTimeout;
    functiononContextMenuClose(){
        clearTimeout(closeTimeout);
        closeTimeout=setTimeout(function(){
            if(tempStyle){
                text.style.cssText=tempStyle;
                tempStyle='';
            }
            if(host.renderer.$keepTextAreaAtCursor==null){
                host.renderer.$keepTextAreaAtCursor=true;
                host.renderer.$moveTextAreaToCursor();
            }
        },0);
    }

    varonContextMenu=function(e){
        host.textInput.onContextMenu(e);
        onContextMenuClose();
    };
    event.addListener(text,"mouseup",onContextMenu);
    event.addListener(text,"mousedown",function(e){
        e.preventDefault();
        onContextMenuClose();
    });
    event.addListener(host.renderer.scroller,"contextmenu",onContextMenu);
    event.addListener(text,"contextmenu",onContextMenu);
};

exports.TextInput=TextInput;
});

define("ace/mouse/default_handlers",["require","exports","module","ace/lib/dom","ace/lib/event","ace/lib/useragent"],function(require,exports,module){
"usestrict";

vardom=require("../lib/dom");
varevent=require("../lib/event");
varuseragent=require("../lib/useragent");

varDRAG_OFFSET=0;//pixels
varSCROLL_COOLDOWN_T=250;//milliseconds

functionDefaultHandlers(mouseHandler){
    mouseHandler.$clickSelection=null;

    vareditor=mouseHandler.editor;
    editor.setDefaultHandler("mousedown",this.onMouseDown.bind(mouseHandler));
    editor.setDefaultHandler("dblclick",this.onDoubleClick.bind(mouseHandler));
    editor.setDefaultHandler("tripleclick",this.onTripleClick.bind(mouseHandler));
    editor.setDefaultHandler("quadclick",this.onQuadClick.bind(mouseHandler));
    editor.setDefaultHandler("mousewheel",this.onMouseWheel.bind(mouseHandler));
    editor.setDefaultHandler("touchmove",this.onTouchMove.bind(mouseHandler));

    varexports=["select","startSelect","selectEnd","selectAllEnd","selectByWordsEnd",
        "selectByLinesEnd","dragWait","dragWaitEnd","focusWait"];

    exports.forEach(function(x){
        mouseHandler[x]=this[x];
    },this);

    mouseHandler.selectByLines=this.extendSelectionBy.bind(mouseHandler,"getLineRange");
    mouseHandler.selectByWords=this.extendSelectionBy.bind(mouseHandler,"getWordRange");
}

(function(){

    this.onMouseDown=function(ev){
        varinSelection=ev.inSelection();
        varpos=ev.getDocumentPosition();
        this.mousedownEvent=ev;
        vareditor=this.editor;

        varbutton=ev.getButton();
        if(button!==0){
            varselectionRange=editor.getSelectionRange();
            varselectionEmpty=selectionRange.isEmpty();
            if(selectionEmpty||button==1)
                editor.selection.moveToPosition(pos);
            if(button==2){
                editor.textInput.onContextMenu(ev.domEvent);
                if(!useragent.isMozilla)
                    ev.preventDefault();
            }
            return;
        }

        this.mousedownEvent.time=Date.now();
        if(inSelection&&!editor.isFocused()){
            editor.focus();
            if(this.$focusTimeout&&!this.$clickSelection&&!editor.inMultiSelectMode){
                this.setState("focusWait");
                this.captureMouse(ev);
                return;
            }
        }

        this.captureMouse(ev);
        this.startSelect(pos,ev.domEvent._clicks>1);
        returnev.preventDefault();
    };

    this.startSelect=function(pos,waitForClickSelection){
        pos=pos||this.editor.renderer.screenToTextCoordinates(this.x,this.y);
        vareditor=this.editor;
        if(this.mousedownEvent.getShiftKey())
            editor.selection.selectToPosition(pos);
        elseif(!waitForClickSelection)
            editor.selection.moveToPosition(pos);
        if(!waitForClickSelection)
            this.select();
        if(editor.renderer.scroller.setCapture){
            editor.renderer.scroller.setCapture();
        }
        editor.setStyle("ace_selecting");
        this.setState("select");
    };

    this.select=function(){
        varanchor,editor=this.editor;
        varcursor=editor.renderer.screenToTextCoordinates(this.x,this.y);
        if(this.$clickSelection){
            varcmp=this.$clickSelection.comparePoint(cursor);

            if(cmp==-1){
                anchor=this.$clickSelection.end;
            }elseif(cmp==1){
                anchor=this.$clickSelection.start;
            }else{
                varorientedRange=calcRangeOrientation(this.$clickSelection,cursor);
                cursor=orientedRange.cursor;
                anchor=orientedRange.anchor;
            }
            editor.selection.setSelectionAnchor(anchor.row,anchor.column);
        }
        editor.selection.selectToPosition(cursor);
        editor.renderer.scrollCursorIntoView();
    };

    this.extendSelectionBy=function(unitName){
        varanchor,editor=this.editor;
        varcursor=editor.renderer.screenToTextCoordinates(this.x,this.y);
        varrange=editor.selection[unitName](cursor.row,cursor.column);
        if(this.$clickSelection){
            varcmpStart=this.$clickSelection.comparePoint(range.start);
            varcmpEnd=this.$clickSelection.comparePoint(range.end);

            if(cmpStart==-1&&cmpEnd<=0){
                anchor=this.$clickSelection.end;
                if(range.end.row!=cursor.row||range.end.column!=cursor.column)
                    cursor=range.start;
            }elseif(cmpEnd==1&&cmpStart>=0){
                anchor=this.$clickSelection.start;
                if(range.start.row!=cursor.row||range.start.column!=cursor.column)
                    cursor=range.end;
            }elseif(cmpStart==-1&&cmpEnd==1){
                cursor=range.end;
                anchor=range.start;
            }else{
                varorientedRange=calcRangeOrientation(this.$clickSelection,cursor);
                cursor=orientedRange.cursor;
                anchor=orientedRange.anchor;
            }
            editor.selection.setSelectionAnchor(anchor.row,anchor.column);
        }
        editor.selection.selectToPosition(cursor);
        editor.renderer.scrollCursorIntoView();
    };

    this.selectEnd=
    this.selectAllEnd=
    this.selectByWordsEnd=
    this.selectByLinesEnd=function(){
        this.$clickSelection=null;
        this.editor.unsetStyle("ace_selecting");
        if(this.editor.renderer.scroller.releaseCapture){
            this.editor.renderer.scroller.releaseCapture();
        }
    };

    this.focusWait=function(){
        vardistance=calcDistance(this.mousedownEvent.x,this.mousedownEvent.y,this.x,this.y);
        vartime=Date.now();

        if(distance>DRAG_OFFSET||time-this.mousedownEvent.time>this.$focusTimeout)
            this.startSelect(this.mousedownEvent.getDocumentPosition());
    };

    this.onDoubleClick=function(ev){
        varpos=ev.getDocumentPosition();
        vareditor=this.editor;
        varsession=editor.session;

        varrange=session.getBracketRange(pos);
        if(range){
            if(range.isEmpty()){
                range.start.column--;
                range.end.column++;
            }
            this.setState("select");
        }else{
            range=editor.selection.getWordRange(pos.row,pos.column);
            this.setState("selectByWords");
        }
        this.$clickSelection=range;
        this.select();
    };

    this.onTripleClick=function(ev){
        varpos=ev.getDocumentPosition();
        vareditor=this.editor;

        this.setState("selectByLines");
        varrange=editor.getSelectionRange();
        if(range.isMultiLine()&&range.contains(pos.row,pos.column)){
            this.$clickSelection=editor.selection.getLineRange(range.start.row);
            this.$clickSelection.end=editor.selection.getLineRange(range.end.row).end;
        }else{
            this.$clickSelection=editor.selection.getLineRange(pos.row);
        }
        this.select();
    };

    this.onQuadClick=function(ev){
        vareditor=this.editor;

        editor.selectAll();
        this.$clickSelection=editor.getSelectionRange();
        this.setState("selectAll");
    };

    this.onMouseWheel=function(ev){
        if(ev.getAccelKey())
            return;
        if(ev.getShiftKey()&&ev.wheelY&&!ev.wheelX){
            ev.wheelX=ev.wheelY;
            ev.wheelY=0;
        }
        
        vareditor=this.editor;
        
        if(!this.$lastScroll)
            this.$lastScroll={t:0,vx:0,vy:0,allowed:0};
        
        varprevScroll=this.$lastScroll;
        vart=ev.domEvent.timeStamp;
        vardt=t-prevScroll.t;
        varvx=dt?ev.wheelX/dt:prevScroll.vx;
        varvy=dt?ev.wheelY/dt:prevScroll.vy;
        if(dt<SCROLL_COOLDOWN_T){
            vx=(vx+prevScroll.vx)/2;
            vy=(vy+prevScroll.vy)/2;
        }
        
        vardirection=Math.abs(vx/vy);
        
        varcanScroll=false;
        if(direction>=1&&editor.renderer.isScrollableBy(ev.wheelX*ev.speed,0))
            canScroll=true;
        if(direction<=1&&editor.renderer.isScrollableBy(0,ev.wheelY*ev.speed))
            canScroll=true;
            
        if(canScroll){
            prevScroll.allowed=t;
        }elseif(t-prevScroll.allowed<SCROLL_COOLDOWN_T){
            varisSlower=Math.abs(vx)<=1.1*Math.abs(prevScroll.vx)
                &&Math.abs(vy)<=1.1*Math.abs(prevScroll.vy);
            if(isSlower){
                canScroll=true;
                prevScroll.allowed=t;
            }
            else{
                prevScroll.allowed=0;
            }
        }
        
        prevScroll.t=t;
        prevScroll.vx=vx;
        prevScroll.vy=vy;

        if(canScroll){
            editor.renderer.scrollBy(ev.wheelX*ev.speed,ev.wheelY*ev.speed);
            returnev.stop();
        }
    };
    
    this.onTouchMove=function(ev){
        this.editor._emit("mousewheel",ev);
    };

}).call(DefaultHandlers.prototype);

exports.DefaultHandlers=DefaultHandlers;

functioncalcDistance(ax,ay,bx,by){
    returnMath.sqrt(Math.pow(bx-ax,2)+Math.pow(by-ay,2));
}

functioncalcRangeOrientation(range,cursor){
    if(range.start.row==range.end.row)
        varcmp=2*cursor.column-range.start.column-range.end.column;
    elseif(range.start.row==range.end.row-1&&!range.start.column&&!range.end.column)
        varcmp=cursor.column-4;
    else
        varcmp=2*cursor.row-range.start.row-range.end.row;

    if(cmp<0)
        return{cursor:range.start,anchor:range.end};
    else
        return{cursor:range.end,anchor:range.start};
}

});

define("ace/tooltip",["require","exports","module","ace/lib/oop","ace/lib/dom"],function(require,exports,module){
"usestrict";

varoop=require("./lib/oop");
vardom=require("./lib/dom");
functionTooltip(parentNode){
    this.isOpen=false;
    this.$element=null;
    this.$parentNode=parentNode;
}

(function(){
    this.$init=function(){
        this.$element=dom.createElement("div");
        this.$element.className="ace_tooltip";
        this.$element.style.display="none";
        this.$parentNode.appendChild(this.$element);
        returnthis.$element;
    };
    this.getElement=function(){
        returnthis.$element||this.$init();
    };
    this.setText=function(text){
        dom.setInnerText(this.getElement(),text);
    };
    this.setHtml=function(html){
        this.getElement().innerHTML=html;
    };
    this.setPosition=function(x,y){
        this.getElement().style.left=x+"px";
        this.getElement().style.top=y+"px";
    };
    this.setClassName=function(className){
        dom.addCssClass(this.getElement(),className);
    };
    this.show=function(text,x,y){
        if(text!=null)
            this.setText(text);
        if(x!=null&&y!=null)
            this.setPosition(x,y);
        if(!this.isOpen){
            this.getElement().style.display="block";
            this.isOpen=true;
        }
    };

    this.hide=function(){
        if(this.isOpen){
            this.getElement().style.display="none";
            this.isOpen=false;
        }
    };
    this.getHeight=function(){
        returnthis.getElement().offsetHeight;
    };
    this.getWidth=function(){
        returnthis.getElement().offsetWidth;
    };
    
    this.destroy=function(){
        this.isOpen=false;
        if(this.$element&&this.$element.parentNode){
            this.$element.parentNode.removeChild(this.$element);
        }
    };

}).call(Tooltip.prototype);

exports.Tooltip=Tooltip;
});

define("ace/mouse/default_gutter_handler",["require","exports","module","ace/lib/dom","ace/lib/oop","ace/lib/event","ace/tooltip"],function(require,exports,module){
"usestrict";
vardom=require("../lib/dom");
varoop=require("../lib/oop");
varevent=require("../lib/event");
varTooltip=require("../tooltip").Tooltip;

functionGutterHandler(mouseHandler){
    vareditor=mouseHandler.editor;
    vargutter=editor.renderer.$gutterLayer;
    vartooltip=newGutterTooltip(editor.container);

    mouseHandler.editor.setDefaultHandler("guttermousedown",function(e){
        if(!editor.isFocused()||e.getButton()!=0)
            return;
        vargutterRegion=gutter.getRegion(e);

        if(gutterRegion=="foldWidgets")
            return;

        varrow=e.getDocumentPosition().row;
        varselection=editor.session.selection;

        if(e.getShiftKey())
            selection.selectTo(row,0);
        else{
            if(e.domEvent.detail==2){
                editor.selectAll();
                returne.preventDefault();
            }
            mouseHandler.$clickSelection=editor.selection.getLineRange(row);
        }
        mouseHandler.setState("selectByLines");
        mouseHandler.captureMouse(e);
        returne.preventDefault();
    });


    vartooltipTimeout,mouseEvent,tooltipAnnotation;

    functionshowTooltip(){
        varrow=mouseEvent.getDocumentPosition().row;
        varannotation=gutter.$annotations[row];
        if(!annotation)
            returnhideTooltip();

        varmaxRow=editor.session.getLength();
        if(row==maxRow){
            varscreenRow=editor.renderer.pixelToScreenCoordinates(0,mouseEvent.y).row;
            varpos=mouseEvent.$pos;
            if(screenRow>editor.session.documentToScreenRow(pos.row,pos.column))
                returnhideTooltip();
        }

        if(tooltipAnnotation==annotation)
            return;
        tooltipAnnotation=annotation.text.join("<br/>");

        tooltip.setHtml(tooltipAnnotation);
        tooltip.show();
        editor._signal("showGutterTooltip",tooltip);
        editor.on("mousewheel",hideTooltip);

        if(mouseHandler.$tooltipFollowsMouse){
            moveTooltip(mouseEvent);
        }else{
            vargutterElement=mouseEvent.domEvent.target;
            varrect=gutterElement.getBoundingClientRect();
            varstyle=tooltip.getElement().style;
            style.left=rect.right+"px";
            style.top=rect.bottom+"px";
        }
    }

    functionhideTooltip(){
        if(tooltipTimeout)
            tooltipTimeout=clearTimeout(tooltipTimeout);
        if(tooltipAnnotation){
            tooltip.hide();
            tooltipAnnotation=null;
            editor._signal("hideGutterTooltip",tooltip);
            editor.removeEventListener("mousewheel",hideTooltip);
        }
    }

    functionmoveTooltip(e){
        tooltip.setPosition(e.x,e.y);
    }

    mouseHandler.editor.setDefaultHandler("guttermousemove",function(e){
        vartarget=e.domEvent.target||e.domEvent.srcElement;
        if(dom.hasCssClass(target,"ace_fold-widget"))
            returnhideTooltip();

        if(tooltipAnnotation&&mouseHandler.$tooltipFollowsMouse)
            moveTooltip(e);

        mouseEvent=e;
        if(tooltipTimeout)
            return;
        tooltipTimeout=setTimeout(function(){
            tooltipTimeout=null;
            if(mouseEvent&&!mouseHandler.isMousePressed)
                showTooltip();
            else
                hideTooltip();
        },50);
    });

    event.addListener(editor.renderer.$gutter,"mouseout",function(e){
        mouseEvent=null;
        if(!tooltipAnnotation||tooltipTimeout)
            return;

        tooltipTimeout=setTimeout(function(){
            tooltipTimeout=null;
            hideTooltip();
        },50);
    });
    
    editor.on("changeSession",hideTooltip);
}

functionGutterTooltip(parentNode){
    Tooltip.call(this,parentNode);
}

oop.inherits(GutterTooltip,Tooltip);

(function(){
    this.setPosition=function(x,y){
        varwindowWidth=window.innerWidth||document.documentElement.clientWidth;
        varwindowHeight=window.innerHeight||document.documentElement.clientHeight;
        varwidth=this.getWidth();
        varheight=this.getHeight();
        x+=15;
        y+=15;
        if(x+width>windowWidth){
            x-=(x+width)-windowWidth;
        }
        if(y+height>windowHeight){
            y-=20+height;
        }
        Tooltip.prototype.setPosition.call(this,x,y);
    };

}).call(GutterTooltip.prototype);



exports.GutterHandler=GutterHandler;

});

define("ace/mouse/mouse_event",["require","exports","module","ace/lib/event","ace/lib/useragent"],function(require,exports,module){
"usestrict";

varevent=require("../lib/event");
varuseragent=require("../lib/useragent");
varMouseEvent=exports.MouseEvent=function(domEvent,editor){
    this.domEvent=domEvent;
    this.editor=editor;
    
    this.x=this.clientX=domEvent.clientX;
    this.y=this.clientY=domEvent.clientY;

    this.$pos=null;
    this.$inSelection=null;
    
    this.propagationStopped=false;
    this.defaultPrevented=false;
};

(function(){ 
    
    this.stopPropagation=function(){
        event.stopPropagation(this.domEvent);
        this.propagationStopped=true;
    };
    
    this.preventDefault=function(){
        event.preventDefault(this.domEvent);
        this.defaultPrevented=true;
    };
    
    this.stop=function(){
        this.stopPropagation();
        this.preventDefault();
    };
    this.getDocumentPosition=function(){
        if(this.$pos)
            returnthis.$pos;
        
        this.$pos=this.editor.renderer.screenToTextCoordinates(this.clientX,this.clientY);
        returnthis.$pos;
    };
    this.inSelection=function(){
        if(this.$inSelection!==null)
            returnthis.$inSelection;
            
        vareditor=this.editor;
        

        varselectionRange=editor.getSelectionRange();
        if(selectionRange.isEmpty())
            this.$inSelection=false;
        else{
            varpos=this.getDocumentPosition();
            this.$inSelection=selectionRange.contains(pos.row,pos.column);
        }

        returnthis.$inSelection;
    };
    this.getButton=function(){
        returnevent.getButton(this.domEvent);
    };
    this.getShiftKey=function(){
        returnthis.domEvent.shiftKey;
    };
    
    this.getAccelKey=useragent.isMac
        ?function(){returnthis.domEvent.metaKey;}
        :function(){returnthis.domEvent.ctrlKey;};
    
}).call(MouseEvent.prototype);

});

define("ace/mouse/dragdrop_handler",["require","exports","module","ace/lib/dom","ace/lib/event","ace/lib/useragent"],function(require,exports,module){
"usestrict";

vardom=require("../lib/dom");
varevent=require("../lib/event");
varuseragent=require("../lib/useragent");

varAUTOSCROLL_DELAY=200;
varSCROLL_CURSOR_DELAY=200;
varSCROLL_CURSOR_HYSTERESIS=5;

functionDragdropHandler(mouseHandler){

    vareditor=mouseHandler.editor;

    varblankImage=dom.createElement("img");
    blankImage.src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==";
    if(useragent.isOpera)
        blankImage.style.cssText="width:1px;height:1px;position:fixed;top:0;left:0;z-index:2147483647;opacity:0;";

    varexports=["dragWait","dragWaitEnd","startDrag","dragReadyEnd","onMouseDrag"];

     exports.forEach(function(x){
         mouseHandler[x]=this[x];
    },this);
    editor.addEventListener("mousedown",this.onMouseDown.bind(mouseHandler));


    varmouseTarget=editor.container;
    vardragSelectionMarker,x,y;
    vartimerId,range;
    vardragCursor,counter=0;
    vardragOperation;
    varisInternal;
    varautoScrollStartTime;
    varcursorMovedTime;
    varcursorPointOnCaretMoved;

    this.onDragStart=function(e){
        if(this.cancelDrag||!mouseTarget.draggable){
            varself=this;
            setTimeout(function(){
                self.startSelect();
                self.captureMouse(e);
            },0);
            returne.preventDefault();
        }
        range=editor.getSelectionRange();

        vardataTransfer=e.dataTransfer;
        dataTransfer.effectAllowed=editor.getReadOnly()?"copy":"copyMove";
        if(useragent.isOpera){
            editor.container.appendChild(blankImage);
            blankImage.scrollTop=0;
        }
        dataTransfer.setDragImage&&dataTransfer.setDragImage(blankImage,0,0);
        if(useragent.isOpera){
            editor.container.removeChild(blankImage);
        }
        dataTransfer.clearData();
        dataTransfer.setData("Text",editor.session.getTextRange());

        isInternal=true;
        this.setState("drag");
    };

    this.onDragEnd=function(e){
        mouseTarget.draggable=false;
        isInternal=false;
        this.setState(null);
        if(!editor.getReadOnly()){
            vardropEffect=e.dataTransfer.dropEffect;
            if(!dragOperation&&dropEffect=="move")
                editor.session.remove(editor.getSelectionRange());
            editor.renderer.$cursorLayer.setBlinking(true);
        }
        this.editor.unsetStyle("ace_dragging");
        this.editor.renderer.setCursorStyle("");
    };

    this.onDragEnter=function(e){
        if(editor.getReadOnly()||!canAccept(e.dataTransfer))
            return;
        x=e.clientX;
        y=e.clientY;
        if(!dragSelectionMarker)
            addDragMarker();
        counter++;
        e.dataTransfer.dropEffect=dragOperation=getDropEffect(e);
        returnevent.preventDefault(e);
    };

    this.onDragOver=function(e){
        if(editor.getReadOnly()||!canAccept(e.dataTransfer))
            return;
        x=e.clientX;
        y=e.clientY;
        if(!dragSelectionMarker){
            addDragMarker();
            counter++;
        }
        if(onMouseMoveTimer!==null)
            onMouseMoveTimer=null;

        e.dataTransfer.dropEffect=dragOperation=getDropEffect(e);
        returnevent.preventDefault(e);
    };

    this.onDragLeave=function(e){
        counter--;
        if(counter<=0&&dragSelectionMarker){
            clearDragMarker();
            dragOperation=null;
            returnevent.preventDefault(e);
        }
    };

    this.onDrop=function(e){
        if(!dragCursor)
            return;
        vardataTransfer=e.dataTransfer;
        if(isInternal){
            switch(dragOperation){
                case"move":
                    if(range.contains(dragCursor.row,dragCursor.column)){
                        range={
                            start:dragCursor,
                            end:dragCursor
                        };
                    }else{
                        range=editor.moveText(range,dragCursor);
                    }
                    break;
                case"copy":
                    range=editor.moveText(range,dragCursor,true);
                    break;
            }
        }else{
            vardropData=dataTransfer.getData('Text');
            range={
                start:dragCursor,
                end:editor.session.insert(dragCursor,dropData)
            };
            editor.focus();
            dragOperation=null;
        }
        clearDragMarker();
        returnevent.preventDefault(e);
    };

    event.addListener(mouseTarget,"dragstart",this.onDragStart.bind(mouseHandler));
    event.addListener(mouseTarget,"dragend",this.onDragEnd.bind(mouseHandler));
    event.addListener(mouseTarget,"dragenter",this.onDragEnter.bind(mouseHandler));
    event.addListener(mouseTarget,"dragover",this.onDragOver.bind(mouseHandler));
    event.addListener(mouseTarget,"dragleave",this.onDragLeave.bind(mouseHandler));
    event.addListener(mouseTarget,"drop",this.onDrop.bind(mouseHandler));

    functionscrollCursorIntoView(cursor,prevCursor){
        varnow=Date.now();
        varvMovement=!prevCursor||cursor.row!=prevCursor.row;
        varhMovement=!prevCursor||cursor.column!=prevCursor.column;
        if(!cursorMovedTime||vMovement||hMovement){
            editor.moveCursorToPosition(cursor);
            cursorMovedTime=now;
            cursorPointOnCaretMoved={x:x,y:y};
        }else{
            vardistance=calcDistance(cursorPointOnCaretMoved.x,cursorPointOnCaretMoved.y,x,y);
            if(distance>SCROLL_CURSOR_HYSTERESIS){
                cursorMovedTime=null;
            }elseif(now-cursorMovedTime>=SCROLL_CURSOR_DELAY){
                editor.renderer.scrollCursorIntoView();
                cursorMovedTime=null;
            }
        }
    }

    functionautoScroll(cursor,prevCursor){
        varnow=Date.now();
        varlineHeight=editor.renderer.layerConfig.lineHeight;
        varcharacterWidth=editor.renderer.layerConfig.characterWidth;
        vareditorRect=editor.renderer.scroller.getBoundingClientRect();
        varoffsets={
           x:{
               left:x-editorRect.left,
               right:editorRect.right-x
           },
           y:{
               top:y-editorRect.top,
               bottom:editorRect.bottom-y
           }
        };
        varnearestXOffset=Math.min(offsets.x.left,offsets.x.right);
        varnearestYOffset=Math.min(offsets.y.top,offsets.y.bottom);
        varscrollCursor={row:cursor.row,column:cursor.column};
        if(nearestXOffset/characterWidth<=2){
            scrollCursor.column+=(offsets.x.left<offsets.x.right?-3:+2);
        }
        if(nearestYOffset/lineHeight<=1){
            scrollCursor.row+=(offsets.y.top<offsets.y.bottom?-1:+1);
        }
        varvScroll=cursor.row!=scrollCursor.row;
        varhScroll=cursor.column!=scrollCursor.column;
        varvMovement=!prevCursor||cursor.row!=prevCursor.row;
        if(vScroll||(hScroll&&!vMovement)){
            if(!autoScrollStartTime)
                autoScrollStartTime=now;
            elseif(now-autoScrollStartTime>=AUTOSCROLL_DELAY)
                editor.renderer.scrollCursorIntoView(scrollCursor);
        }else{
            autoScrollStartTime=null;
        }
    }

    functiononDragInterval(){
        varprevCursor=dragCursor;
        dragCursor=editor.renderer.screenToTextCoordinates(x,y);
        scrollCursorIntoView(dragCursor,prevCursor);
        autoScroll(dragCursor,prevCursor);
    }

    functionaddDragMarker(){
        range=editor.selection.toOrientedRange();
        dragSelectionMarker=editor.session.addMarker(range,"ace_selection",editor.getSelectionStyle());
        editor.clearSelection();
        if(editor.isFocused())
            editor.renderer.$cursorLayer.setBlinking(false);
        clearInterval(timerId);
        onDragInterval();
        timerId=setInterval(onDragInterval,20);
        counter=0;
        event.addListener(document,"mousemove",onMouseMove);
    }

    functionclearDragMarker(){
        clearInterval(timerId);
        editor.session.removeMarker(dragSelectionMarker);
        dragSelectionMarker=null;
        editor.selection.fromOrientedRange(range);
        if(editor.isFocused()&&!isInternal)
            editor.renderer.$cursorLayer.setBlinking(!editor.getReadOnly());
        range=null;
        dragCursor=null;
        counter=0;
        autoScrollStartTime=null;
        cursorMovedTime=null;
        event.removeListener(document,"mousemove",onMouseMove);
    }
    varonMouseMoveTimer=null;
    functiononMouseMove(){
        if(onMouseMoveTimer==null){
            onMouseMoveTimer=setTimeout(function(){
                if(onMouseMoveTimer!=null&&dragSelectionMarker)
                    clearDragMarker();
            },20);
        }
    }

    functioncanAccept(dataTransfer){
        vartypes=dataTransfer.types;
        return!types||Array.prototype.some.call(types,function(type){
            returntype=='text/plain'||type=='Text';
        });
    }

    functiongetDropEffect(e){
        varcopyAllowed=['copy','copymove','all','uninitialized'];
        varmoveAllowed=['move','copymove','linkmove','all','uninitialized'];

        varcopyModifierState=useragent.isMac?e.altKey:e.ctrlKey;
        vareffectAllowed="uninitialized";
        try{
            effectAllowed=e.dataTransfer.effectAllowed.toLowerCase();
        }catch(e){}
        vardropEffect="none";

        if(copyModifierState&&copyAllowed.indexOf(effectAllowed)>=0)
            dropEffect="copy";
        elseif(moveAllowed.indexOf(effectAllowed)>=0)
            dropEffect="move";
        elseif(copyAllowed.indexOf(effectAllowed)>=0)
            dropEffect="copy";

        returndropEffect;
    }
}

(function(){

    this.dragWait=function(){
        varinterval=Date.now()-this.mousedownEvent.time;
        if(interval>this.editor.getDragDelay())
            this.startDrag();
    };

    this.dragWaitEnd=function(){
        vartarget=this.editor.container;
        target.draggable=false;
        this.startSelect(this.mousedownEvent.getDocumentPosition());
        this.selectEnd();
    };

    this.dragReadyEnd=function(e){
        this.editor.renderer.$cursorLayer.setBlinking(!this.editor.getReadOnly());
        this.editor.unsetStyle("ace_dragging");
        this.editor.renderer.setCursorStyle("");
        this.dragWaitEnd();
    };

    this.startDrag=function(){
        this.cancelDrag=false;
        vareditor=this.editor;
        vartarget=editor.container;
        target.draggable=true;
        editor.renderer.$cursorLayer.setBlinking(false);
        editor.setStyle("ace_dragging");
        varcursorStyle=useragent.isWin?"default":"move";
        editor.renderer.setCursorStyle(cursorStyle);
        this.setState("dragReady");
    };

    this.onMouseDrag=function(e){
        vartarget=this.editor.container;
        if(useragent.isIE&&this.state=="dragReady"){
            vardistance=calcDistance(this.mousedownEvent.x,this.mousedownEvent.y,this.x,this.y);
            if(distance>3)
                target.dragDrop();
        }
        if(this.state==="dragWait"){
            vardistance=calcDistance(this.mousedownEvent.x,this.mousedownEvent.y,this.x,this.y);
            if(distance>0){
                target.draggable=false;
                this.startSelect(this.mousedownEvent.getDocumentPosition());
            }
        }
    };

    this.onMouseDown=function(e){
        if(!this.$dragEnabled)
            return;
        this.mousedownEvent=e;
        vareditor=this.editor;

        varinSelection=e.inSelection();
        varbutton=e.getButton();
        varclickCount=e.domEvent.detail||1;
        if(clickCount===1&&button===0&&inSelection){
            if(e.editor.inMultiSelectMode&&(e.getAccelKey()||e.getShiftKey()))
                return;
            this.mousedownEvent.time=Date.now();
            vareventTarget=e.domEvent.target||e.domEvent.srcElement;
            if("unselectable"ineventTarget)
                eventTarget.unselectable="on";
            if(editor.getDragDelay()){
                if(useragent.isWebKit){
                    this.cancelDrag=true;
                    varmouseTarget=editor.container;
                    mouseTarget.draggable=true;
                }
                this.setState("dragWait");
            }else{
                this.startDrag();
            }
            this.captureMouse(e,this.onMouseDrag.bind(this));
            e.defaultPrevented=true;
        }
    };

}).call(DragdropHandler.prototype);


functioncalcDistance(ax,ay,bx,by){
    returnMath.sqrt(Math.pow(bx-ax,2)+Math.pow(by-ay,2));
}

exports.DragdropHandler=DragdropHandler;

});

define("ace/lib/net",["require","exports","module","ace/lib/dom"],function(require,exports,module){
"usestrict";
vardom=require("./dom");

exports.get=function(url,callback){
    varxhr=newXMLHttpRequest();
    xhr.open('GET',url,true);
    xhr.onreadystatechange=function(){
        if(xhr.readyState===4){
            callback(xhr.responseText);
        }
    };
    xhr.send(null);
};

exports.loadScript=function(path,callback){
    varhead=dom.getDocumentHead();
    vars=document.createElement('script');

    s.src=path;
    head.appendChild(s);

    s.onload=s.onreadystatechange=function(_,isAbort){
        if(isAbort||!s.readyState||s.readyState=="loaded"||s.readyState=="complete"){
            s=s.onload=s.onreadystatechange=null;
            if(!isAbort)
                callback();
        }
    };
};
exports.qualifyURL=function(url){
    vara=document.createElement('a');
    a.href=url;
    returna.href;
};

});

define("ace/lib/event_emitter",["require","exports","module"],function(require,exports,module){
"usestrict";

varEventEmitter={};
varstopPropagation=function(){this.propagationStopped=true;};
varpreventDefault=function(){this.defaultPrevented=true;};

EventEmitter._emit=
EventEmitter._dispatchEvent=function(eventName,e){
    this._eventRegistry||(this._eventRegistry={});
    this._defaultHandlers||(this._defaultHandlers={});

    varlisteners=this._eventRegistry[eventName]||[];
    vardefaultHandler=this._defaultHandlers[eventName];
    if(!listeners.length&&!defaultHandler)
        return;

    if(typeofe!="object"||!e)
        e={};

    if(!e.type)
        e.type=eventName;
    if(!e.stopPropagation)
        e.stopPropagation=stopPropagation;
    if(!e.preventDefault)
        e.preventDefault=preventDefault;

    listeners=listeners.slice();
    for(vari=0;i<listeners.length;i++){
        listeners[i](e,this);
        if(e.propagationStopped)
            break;
    }
    
    if(defaultHandler&&!e.defaultPrevented)
        returndefaultHandler(e,this);
};


EventEmitter._signal=function(eventName,e){
    varlisteners=(this._eventRegistry||{})[eventName];
    if(!listeners)
        return;
    listeners=listeners.slice();
    for(vari=0;i<listeners.length;i++)
        listeners[i](e,this);
};

EventEmitter.once=function(eventName,callback){
    var_self=this;
    callback&&this.addEventListener(eventName,functionnewCallback(){
        _self.removeEventListener(eventName,newCallback);
        callback.apply(null,arguments);
    });
};


EventEmitter.setDefaultHandler=function(eventName,callback){
    varhandlers=this._defaultHandlers;
    if(!handlers)
        handlers=this._defaultHandlers={_disabled_:{}};
    
    if(handlers[eventName]){
        varold=handlers[eventName];
        vardisabled=handlers._disabled_[eventName];
        if(!disabled)
            handlers._disabled_[eventName]=disabled=[];
        disabled.push(old);
        vari=disabled.indexOf(callback);
        if(i!=-1)
            disabled.splice(i,1);
    }
    handlers[eventName]=callback;
};
EventEmitter.removeDefaultHandler=function(eventName,callback){
    varhandlers=this._defaultHandlers;
    if(!handlers)
        return;
    vardisabled=handlers._disabled_[eventName];
    
    if(handlers[eventName]==callback){
        varold=handlers[eventName];
        if(disabled)
            this.setDefaultHandler(eventName,disabled.pop());
    }elseif(disabled){
        vari=disabled.indexOf(callback);
        if(i!=-1)
            disabled.splice(i,1);
    }
};

EventEmitter.on=
EventEmitter.addEventListener=function(eventName,callback,capturing){
    this._eventRegistry=this._eventRegistry||{};

    varlisteners=this._eventRegistry[eventName];
    if(!listeners)
        listeners=this._eventRegistry[eventName]=[];

    if(listeners.indexOf(callback)==-1)
        listeners[capturing?"unshift":"push"](callback);
    returncallback;
};

EventEmitter.off=
EventEmitter.removeListener=
EventEmitter.removeEventListener=function(eventName,callback){
    this._eventRegistry=this._eventRegistry||{};

    varlisteners=this._eventRegistry[eventName];
    if(!listeners)
        return;

    varindex=listeners.indexOf(callback);
    if(index!==-1)
        listeners.splice(index,1);
};

EventEmitter.removeAllListeners=function(eventName){
    if(this._eventRegistry)this._eventRegistry[eventName]=[];
};

exports.EventEmitter=EventEmitter;

});

define("ace/lib/app_config",["require","exports","module","ace/lib/oop","ace/lib/event_emitter"],function(require,exports,module){
"nousestrict";

varoop=require("./oop");
varEventEmitter=require("./event_emitter").EventEmitter;

varoptionsProvider={
    setOptions:function(optList){
        Object.keys(optList).forEach(function(key){
            this.setOption(key,optList[key]);
        },this);
    },
    getOptions:function(optionNames){
        varresult={};
        if(!optionNames){
            varoptions=this.$options;
            optionNames=Object.keys(options).filter(function(key){
                return!options[key].hidden;
            });
        }elseif(!Array.isArray(optionNames)){
            result=optionNames;
            optionNames=Object.keys(result);
        }
        optionNames.forEach(function(key){
            result[key]=this.getOption(key);
        },this);
        returnresult;
    },
    setOption:function(name,value){
        if(this["$"+name]===value)
            return;
        varopt=this.$options[name];
        if(!opt){
            returnwarn('misspelledoption"'+name+'"');
        }
        if(opt.forwardTo)
            returnthis[opt.forwardTo]&&this[opt.forwardTo].setOption(name,value);

        if(!opt.handlesSet)
            this["$"+name]=value;
        if(opt&&opt.set)
            opt.set.call(this,value);
    },
    getOption:function(name){
        varopt=this.$options[name];
        if(!opt){
            returnwarn('misspelledoption"'+name+'"');
        }
        if(opt.forwardTo)
            returnthis[opt.forwardTo]&&this[opt.forwardTo].getOption(name);
        returnopt&&opt.get?opt.get.call(this):this["$"+name];
    }
};

functionwarn(message){
    if(typeofconsole!="undefined"&&console.warn)
        console.warn.apply(console,arguments);
}

functionreportError(msg,data){
    vare=newError(msg);
    e.data=data;
    if(typeofconsole=="object"&&console.error)
        console.error(e);
    setTimeout(function(){throwe;});
}

varAppConfig=function(){
    this.$defaultOptions={};
};

(function(){
    oop.implement(this,EventEmitter);
    this.defineOptions=function(obj,path,options){
        if(!obj.$options)
            this.$defaultOptions[path]=obj.$options={};

        Object.keys(options).forEach(function(key){
            varopt=options[key];
            if(typeofopt=="string")
                opt={forwardTo:opt};

            opt.name||(opt.name=key);
            obj.$options[opt.name]=opt;
            if("initialValue"inopt)
                obj["$"+opt.name]=opt.initialValue;
        });
        oop.implement(obj,optionsProvider);

        returnthis;
    };

    this.resetOptions=function(obj){
        Object.keys(obj.$options).forEach(function(key){
            varopt=obj.$options[key];
            if("value"inopt)
                obj.setOption(key,opt.value);
        });
    };

    this.setDefaultValue=function(path,name,value){
        varopts=this.$defaultOptions[path]||(this.$defaultOptions[path]={});
        if(opts[name]){
            if(opts.forwardTo)
                this.setDefaultValue(opts.forwardTo,name,value);
            else
                opts[name].value=value;
        }
    };

    this.setDefaultValues=function(path,optionHash){
        Object.keys(optionHash).forEach(function(key){
            this.setDefaultValue(path,key,optionHash[key]);
        },this);
    };
    
    this.warn=warn;
    this.reportError=reportError;
    
}).call(AppConfig.prototype);

exports.AppConfig=AppConfig;

});

define("ace/config",["require","exports","module","ace/lib/lang","ace/lib/oop","ace/lib/net","ace/lib/app_config"],function(require,exports,module){
"nousestrict";

varlang=require("./lib/lang");
varoop=require("./lib/oop");
varnet=require("./lib/net");
varAppConfig=require("./lib/app_config").AppConfig;

module.exports=exports=newAppConfig();

varglobal=(function(){
    returnthis||typeofwindow!="undefined"&&window;
})();

varoptions={
    packaged:false,
    workerPath:null,
    modePath:null,
    themePath:null,
    basePath:"",
    suffix:".js",
    $moduleUrls:{}
};

exports.get=function(key){
    if(!options.hasOwnProperty(key))
        thrownewError("Unknownconfigkey:"+key);

    returnoptions[key];
};

exports.set=function(key,value){
    if(!options.hasOwnProperty(key))
        thrownewError("Unknownconfigkey:"+key);

    options[key]=value;
};

exports.all=function(){
    returnlang.copyObject(options);
};
exports.moduleUrl=function(name,component){
    if(options.$moduleUrls[name])
        returnoptions.$moduleUrls[name];

    varparts=name.split("/");
    component=component||parts[parts.length-2]||"";
    varsep=component=="snippets"?"/":"-";
    varbase=parts[parts.length-1];
    if(component=="worker"&&sep=="-"){
        varre=newRegExp("^"+component+"[\\-_]|[\\-_]"+component+"$","g");
        base=base.replace(re,"");
    }

    if((!base||base==component)&&parts.length>1)
        base=parts[parts.length-2];
    varpath=options[component+"Path"];
    if(path==null){
        path=options.basePath;
    }elseif(sep=="/"){
        component=sep="";
    }
    if(path&&path.slice(-1)!="/")
        path+="/";
    returnpath+component+sep+base+this.get("suffix");
};

exports.setModuleUrl=function(name,subst){
    returnoptions.$moduleUrls[name]=subst;
};

exports.$loading={};
exports.loadModule=function(moduleName,onLoad){
    varmodule,moduleType;
    if(Array.isArray(moduleName)){
        moduleType=moduleName[0];
        moduleName=moduleName[1];
    }

    try{
        module=require(moduleName);
    }catch(e){}
    if(module&&!exports.$loading[moduleName])
        returnonLoad&&onLoad(module);

    if(!exports.$loading[moduleName])
        exports.$loading[moduleName]=[];

    exports.$loading[moduleName].push(onLoad);

    if(exports.$loading[moduleName].length>1)
        return;

    varafterLoad=function(){
        require([moduleName],function(module){
            exports._emit("load.module",{name:moduleName,module:module});
            varlisteners=exports.$loading[moduleName];
            exports.$loading[moduleName]=null;
            listeners.forEach(function(onLoad){
                onLoad&&onLoad(module);
            });
        });
    };

    if(!exports.get("packaged"))
        returnafterLoad();
    net.loadScript(exports.moduleUrl(moduleName,moduleType),afterLoad);
};
init(true);functioninit(packaged){

    if(!global||!global.document)
        return;
    
    options.packaged=packaged||require.packaged||module.packaged||(global.define&&define.packaged);

    varscriptOptions={};
    varscriptUrl="";
    varcurrentScript=(document.currentScript||document._currentScript);//nativeorpolyfill
    varcurrentDocument=currentScript&&currentScript.ownerDocument||document;
    
    varscripts=currentDocument.getElementsByTagName("script");
    for(vari=0;i<scripts.length;i++){
        varscript=scripts[i];

        varsrc=script.src||script.getAttribute("src");
        if(!src)
            continue;

        varattributes=script.attributes;
        for(varj=0,l=attributes.length;j<l;j++){
            varattr=attributes[j];
            if(attr.name.indexOf("data-ace-")===0){
                scriptOptions[deHyphenate(attr.name.replace(/^data-ace-/,""))]=attr.value;
            }
        }

        varm=src.match(/^(.*)\/ace(\-\w+)?\.js(\?|$)/);
        if(m)
            scriptUrl=m[1];
    }

    if(scriptUrl){
        scriptOptions.base=scriptOptions.base||scriptUrl;
        scriptOptions.packaged=true;
    }

    scriptOptions.basePath=scriptOptions.base;
    scriptOptions.workerPath=scriptOptions.workerPath||scriptOptions.base;
    scriptOptions.modePath=scriptOptions.modePath||scriptOptions.base;
    scriptOptions.themePath=scriptOptions.themePath||scriptOptions.base;
    deletescriptOptions.base;

    for(varkeyinscriptOptions)
        if(typeofscriptOptions[key]!=="undefined")
            exports.set(key,scriptOptions[key]);
}

exports.init=init;

functiondeHyphenate(str){
    returnstr.replace(/-(.)/g,function(m,m1){returnm1.toUpperCase();});
}

});

define("ace/mouse/mouse_handler",["require","exports","module","ace/lib/event","ace/lib/useragent","ace/mouse/default_handlers","ace/mouse/default_gutter_handler","ace/mouse/mouse_event","ace/mouse/dragdrop_handler","ace/config"],function(require,exports,module){
"usestrict";

varevent=require("../lib/event");
varuseragent=require("../lib/useragent");
varDefaultHandlers=require("./default_handlers").DefaultHandlers;
varDefaultGutterHandler=require("./default_gutter_handler").GutterHandler;
varMouseEvent=require("./mouse_event").MouseEvent;
varDragdropHandler=require("./dragdrop_handler").DragdropHandler;
varconfig=require("../config");

varMouseHandler=function(editor){
    var_self=this;
    this.editor=editor;

    newDefaultHandlers(this);
    newDefaultGutterHandler(this);
    newDragdropHandler(this);

    varfocusEditor=function(e){
        varwindowBlurred=!document.hasFocus||!document.hasFocus()
            ||!editor.isFocused()&&document.activeElement==(editor.textInput&&editor.textInput.getElement());
        if(windowBlurred)
            window.focus();
        editor.focus();
    };

    varmouseTarget=editor.renderer.getMouseEventTarget();
    event.addListener(mouseTarget,"click",this.onMouseEvent.bind(this,"click"));
    event.addListener(mouseTarget,"mousemove",this.onMouseMove.bind(this,"mousemove"));
    event.addMultiMouseDownListener([
        mouseTarget,
        editor.renderer.scrollBarV&&editor.renderer.scrollBarV.inner,
        editor.renderer.scrollBarH&&editor.renderer.scrollBarH.inner,
        editor.textInput&&editor.textInput.getElement()
    ].filter(Boolean),[400,300,250],this,"onMouseEvent");
    event.addMouseWheelListener(editor.container,this.onMouseWheel.bind(this,"mousewheel"));
    event.addTouchMoveListener(editor.container,this.onTouchMove.bind(this,"touchmove"));

    vargutterEl=editor.renderer.$gutter;
    event.addListener(gutterEl,"mousedown",this.onMouseEvent.bind(this,"guttermousedown"));
    event.addListener(gutterEl,"click",this.onMouseEvent.bind(this,"gutterclick"));
    event.addListener(gutterEl,"dblclick",this.onMouseEvent.bind(this,"gutterdblclick"));
    event.addListener(gutterEl,"mousemove",this.onMouseEvent.bind(this,"guttermousemove"));

    event.addListener(mouseTarget,"mousedown",focusEditor);
    event.addListener(gutterEl,"mousedown",focusEditor);
    if(useragent.isIE&&editor.renderer.scrollBarV){
        event.addListener(editor.renderer.scrollBarV.element,"mousedown",focusEditor);
        event.addListener(editor.renderer.scrollBarH.element,"mousedown",focusEditor);
    }

    editor.on("mousemove",function(e){
        if(_self.state||_self.$dragDelay||!_self.$dragEnabled)
            return;

        varcharacter=editor.renderer.screenToTextCoordinates(e.x,e.y);
        varrange=editor.session.selection.getRange();
        varrenderer=editor.renderer;

        if(!range.isEmpty()&&range.insideStart(character.row,character.column)){
            renderer.setCursorStyle("default");
        }else{
            renderer.setCursorStyle("");
        }
    });
};

(function(){
    this.onMouseEvent=function(name,e){
        this.editor._emit(name,newMouseEvent(e,this.editor));
    };

    this.onMouseMove=function(name,e){
        varlisteners=this.editor._eventRegistry&&this.editor._eventRegistry.mousemove;
        if(!listeners||!listeners.length)
            return;

        this.editor._emit(name,newMouseEvent(e,this.editor));
    };

    this.onMouseWheel=function(name,e){
        varmouseEvent=newMouseEvent(e,this.editor);
        mouseEvent.speed=this.$scrollSpeed*2;
        mouseEvent.wheelX=e.wheelX;
        mouseEvent.wheelY=e.wheelY;

        this.editor._emit(name,mouseEvent);
    };
    
    this.onTouchMove=function(name,e){
        varmouseEvent=newMouseEvent(e,this.editor);
        mouseEvent.speed=1;//this.$scrollSpeed*2;
        mouseEvent.wheelX=e.wheelX;
        mouseEvent.wheelY=e.wheelY;
        this.editor._emit(name,mouseEvent);
    };

    this.setState=function(state){
        this.state=state;
    };

    this.captureMouse=function(ev,mouseMoveHandler){
        this.x=ev.x;
        this.y=ev.y;

        this.isMousePressed=true;
        vareditor=this.editor;
        varrenderer=this.editor.renderer;
        if(renderer.$keepTextAreaAtCursor)
            renderer.$keepTextAreaAtCursor=null;

        varself=this;
        varonMouseMove=function(e){
            if(!e)return;
            if(useragent.isWebKit&&!e.which&&self.releaseMouse)
                returnself.releaseMouse();

            self.x=e.clientX;
            self.y=e.clientY;
            mouseMoveHandler&&mouseMoveHandler(e);
            self.mouseEvent=newMouseEvent(e,self.editor);
            self.$mouseMoved=true;
        };

        varonCaptureEnd=function(e){
            editor.off("beforeEndOperation",onOperationEnd);
            clearInterval(timerId);
            onCaptureInterval();
            self[self.state+"End"]&&self[self.state+"End"](e);
            self.state="";
            if(renderer.$keepTextAreaAtCursor==null){
                renderer.$keepTextAreaAtCursor=true;
                renderer.$moveTextAreaToCursor();
            }
            self.isMousePressed=false;
            self.$onCaptureMouseMove=self.releaseMouse=null;
            e&&self.onMouseEvent("mouseup",e);
        };

        varonCaptureInterval=function(){
            self[self.state]&&self[self.state]();
            self.$mouseMoved=false;
        };

        if(useragent.isOldIE&&ev.domEvent.type=="dblclick"){
            returnsetTimeout(function(){onCaptureEnd(ev);});
        }

        varonOperationEnd=function(e){
            if(editor.curOp.command.name&&editor.curOp.selectionChanged){
                self[self.state+"End"]&&self[self.state+"End"]();
                self.state="";
                self.releaseMouse();
            }
        };

        editor.on("beforeEndOperation",onOperationEnd);

        self.$onCaptureMouseMove=onMouseMove;
        self.releaseMouse=event.capture(this.editor.container,onMouseMove,onCaptureEnd);
        vartimerId=setInterval(onCaptureInterval,20);
    };
    this.releaseMouse=null;
    this.cancelContextMenu=function(){
        varstop=function(e){
            if(e&&e.domEvent&&e.domEvent.type!="contextmenu")
                return;
            this.editor.off("nativecontextmenu",stop);
            if(e&&e.domEvent)
                event.stopEvent(e.domEvent);
        }.bind(this);
        setTimeout(stop,10);
        this.editor.on("nativecontextmenu",stop);
    };
}).call(MouseHandler.prototype);

config.defineOptions(MouseHandler.prototype,"mouseHandler",{
    scrollSpeed:{initialValue:2},
    dragDelay:{initialValue:(useragent.isMac?150:0)},
    dragEnabled:{initialValue:true},
    focusTimeout:{initialValue:0},
    tooltipFollowsMouse:{initialValue:true}
});


exports.MouseHandler=MouseHandler;
});

define("ace/mouse/fold_handler",["require","exports","module","ace/lib/dom"],function(require,exports,module){
"usestrict";
vardom=require("../lib/dom");

functionFoldHandler(editor){

    editor.on("click",function(e){
        varposition=e.getDocumentPosition();
        varsession=editor.session;
        varfold=session.getFoldAt(position.row,position.column,1);
        if(fold){
            if(e.getAccelKey())
                session.removeFold(fold);
            else
                session.expandFold(fold);

            e.stop();
        }
        
        vartarget=e.domEvent&&e.domEvent.target;
        if(target&&dom.hasCssClass(target,"ace_inline_button")){
            if(dom.hasCssClass(target,"ace_toggle_wrap")){
                session.setOption("wrap",true);
                editor.renderer.scrollCursorIntoView();
            }
        }
    });

    editor.on("gutterclick",function(e){
        vargutterRegion=editor.renderer.$gutterLayer.getRegion(e);

        if(gutterRegion=="foldWidgets"){
            varrow=e.getDocumentPosition().row;
            varsession=editor.session;
            if(session.foldWidgets&&session.foldWidgets[row])
                editor.session.onFoldWidgetClick(row,e);
            if(!editor.isFocused())
                editor.focus();
            e.stop();
        }
    });

    editor.on("gutterdblclick",function(e){
        vargutterRegion=editor.renderer.$gutterLayer.getRegion(e);

        if(gutterRegion=="foldWidgets"){
            varrow=e.getDocumentPosition().row;
            varsession=editor.session;
            vardata=session.getParentFoldRangeData(row,true);
            varrange=data.range||data.firstRange;

            if(range){
                row=range.start.row;
                varfold=session.getFoldAt(row,session.getLine(row).length,1);

                if(fold){
                    session.removeFold(fold);
                }else{
                    session.addFold("...",range);
                    editor.renderer.scrollCursorIntoView({row:range.start.row,column:0});
                }
            }
            e.stop();
        }
    });
}

exports.FoldHandler=FoldHandler;

});

define("ace/keyboard/keybinding",["require","exports","module","ace/lib/keys","ace/lib/event"],function(require,exports,module){
"usestrict";

varkeyUtil =require("../lib/keys");
varevent=require("../lib/event");

varKeyBinding=function(editor){
    this.$editor=editor;
    this.$data={editor:editor};
    this.$handlers=[];
    this.setDefaultHandler(editor.commands);
};

(function(){
    this.setDefaultHandler=function(kb){
        this.removeKeyboardHandler(this.$defaultHandler);
        this.$defaultHandler=kb;
        this.addKeyboardHandler(kb,0);
    };

    this.setKeyboardHandler=function(kb){
        varh=this.$handlers;
        if(h[h.length-1]==kb)
            return;

        while(h[h.length-1]&&h[h.length-1]!=this.$defaultHandler)
            this.removeKeyboardHandler(h[h.length-1]);

        this.addKeyboardHandler(kb,1);
    };

    this.addKeyboardHandler=function(kb,pos){
        if(!kb)
            return;
        if(typeofkb=="function"&&!kb.handleKeyboard)
            kb.handleKeyboard=kb;
        vari=this.$handlers.indexOf(kb);
        if(i!=-1)
            this.$handlers.splice(i,1);

        if(pos==undefined)
            this.$handlers.push(kb);
        else
            this.$handlers.splice(pos,0,kb);

        if(i==-1&&kb.attach)
            kb.attach(this.$editor);
    };

    this.removeKeyboardHandler=function(kb){
        vari=this.$handlers.indexOf(kb);
        if(i==-1)
            returnfalse;
        this.$handlers.splice(i,1);
        kb.detach&&kb.detach(this.$editor);
        returntrue;
    };

    this.getKeyboardHandler=function(){
        returnthis.$handlers[this.$handlers.length-1];
    };
    
    this.getStatusText=function(){
        vardata=this.$data;
        vareditor=data.editor;
        returnthis.$handlers.map(function(h){
            returnh.getStatusText&&h.getStatusText(editor,data)||"";
        }).filter(Boolean).join("");
    };

    this.$callKeyboardHandlers=function(hashId,keyString,keyCode,e){
        vartoExecute;
        varsuccess=false;
        varcommands=this.$editor.commands;

        for(vari=this.$handlers.length;i--;){
            toExecute=this.$handlers[i].handleKeyboard(
                this.$data,hashId,keyString,keyCode,e
            );
            if(!toExecute||!toExecute.command)
                continue;
            if(toExecute.command=="null"){
                success=true;
            }else{
                success=commands.exec(toExecute.command,this.$editor,toExecute.args,e);
            }
            if(success&&e&&hashId!=-1&&
                toExecute.passEvent!=true&&toExecute.command.passEvent!=true
            ){
                event.stopEvent(e);
            }
            if(success)
                break;
        }
        
        if(!success&&hashId==-1){
            toExecute={command:"insertstring"};
            success=commands.exec("insertstring",this.$editor,keyString);
        }
        
        if(success&&this.$editor._signal)
            this.$editor._signal("keyboardActivity",toExecute);
        
        returnsuccess;
    };

    this.onCommandKey=function(e,hashId,keyCode){
        varkeyString=keyUtil.keyCodeToString(keyCode);
        this.$callKeyboardHandlers(hashId,keyString,keyCode,e);
    };

    this.onTextInput=function(text){
        this.$callKeyboardHandlers(-1,text);
    };

}).call(KeyBinding.prototype);

exports.KeyBinding=KeyBinding;
});

define("ace/lib/bidiutil",["require","exports","module"],function(require,exports,module){
"usestrict";

varArabicAlefBetIntervalsBegine=['\u0621','\u0641'];
varArabicAlefBetIntervalsEnd=['\u063A','\u064a'];
vardir=0,hiLevel=0;
varlastArabic=false,hasUBAT_AL=false, hasUBAT_B=false, hasUBAT_S=false,hasBlockSep=false,hasSegSep=false;

varimpTab_LTR=[	[	0,		3,		0,		1,		0,		0,		0	],	[	0,		3,		0,		1,		2,		2,		0	],	[	0,		3,		0,		0x11,		2,		0,		1	],	[	0,		3,		5,		5,		4,		1,		0	],	[	0,		3,		0x15,		0x15,		4,		0,		1	],	[	0,		3,		5,		5,		4,		2,		0	]
];

varimpTab_RTL=[	[	2,		0,		1,		1,		0,		1,		0	],	[	2,		0,		1,		1,		0,		2,		0	],	[	2,		0,		2,		1,		3,		2,		0	],	[	2,		0,		2,		0x21,		3,		1,		1	]
];

varLTR=0,RTL=1;

varL=0;
varR=1;
varEN=2;
varAN=3;
varON=4;
varB=5;
varS=6;
varAL=7;
varWS=8;
varCS=9;
varES=10;
varET=11;
varNSM=12;
varLRE=13;
varRLE=14;
varPDF=15;
varLRO=16;
varRLO=17;
varBN=18;

varUnicodeTBL00=[
BN,BN,BN,BN,BN,BN,BN,BN,BN,S,B,S,WS,B,BN,BN,
BN,BN,BN,BN,BN,BN,BN,BN,BN,BN,BN,BN,B,B,B,S,
WS,ON,ON,ET,ET,ET,ON,ON,ON,ON,ON,ES,CS,ES,CS,CS,
EN,EN,EN,EN,EN,EN,EN,EN,EN,EN,CS,ON,ON,ON,ON,ON,
ON,L,L,L,L,L,L,L,L,L,L,L,L,L,L,L,
L,L,L,L,L,L,L,L,L,L,L,ON,ON,ON,ON,ON,
ON,L,L,L,L,L,L,L,L,L,L,L,L,L,L,L,
L,L,L,L,L,L,L,L,L,L,L,ON,ON,ON,ON,BN,
BN,BN,BN,BN,BN,B,BN,BN,BN,BN,BN,BN,BN,BN,BN,BN,
BN,BN,BN,BN,BN,BN,BN,BN,BN,BN,BN,BN,BN,BN,BN,BN,
CS,ON,ET,ET,ET,ET,ON,ON,ON,ON,L,ON,ON,BN,ON,ON,
ET,ET,EN,EN,ON,L,ON,ON,ON,EN,L,ON,ON,ON,ON,ON
];

varUnicodeTBL20=[
WS,WS,WS,WS,WS,WS,WS,WS,WS,WS,WS,BN,BN,BN,L,R	,
ON,ON,ON,ON,ON,ON,ON,ON,ON,ON,ON,ON,ON,ON,ON,ON,
ON,ON,ON,ON,ON,ON,ON,ON,WS,B,LRE,RLE,PDF,LRO,RLO,CS,
ET,ET,ET,ET,ET,ON,ON,ON,ON,ON,ON,ON,ON,ON,ON,ON,
ON,ON,ON,ON,CS,ON,ON,ON,ON,ON,ON,ON,ON,ON,ON,ON,
ON,ON,ON,ON,ON,ON,ON,ON,ON,ON,ON,ON,ON,ON,ON,WS
];

function_computeLevels(chars,levels,len,charTypes){
	varimpTab=dir?impTab_RTL:impTab_LTR
		,prevState=null,newClass=null,newLevel=null,newState=0
		,action=null,cond=null,condPos=-1,i=null,ix=null,classes=[];

	if(!charTypes){
		for(i=0,charTypes=[];i<len;i++){
			charTypes[i]=_getCharacterType(chars[i]);
		}
	}
	hiLevel=dir;
	lastArabic=false;
	hasUBAT_AL=false;
	hasUBAT_B=false;
	hasUBAT_S=false;
	for(ix=0;ix<len;ix++){
		prevState=newState;
		classes[ix]=newClass=_getCharClass(chars,charTypes,classes,ix);
		newState=impTab[prevState][newClass];
		action=newState&0xF0;
		newState&=0x0F;
		levels[ix]=newLevel=impTab[newState][5];
		if(action>0){
			if(action==0x10){
				for(i=condPos;i<ix;i++){
					levels[i]=1;
				}
				condPos=-1;
			}else{
				condPos=-1;
			}
		}
		cond=impTab[newState][6];
		if(cond){
			if(condPos==-1){
				condPos=ix;
			}
		}else{
			if(condPos>-1){
				for(i=condPos;i<ix;i++){
					levels[i]=newLevel;
				}
				condPos=-1;
			}
		}
		if(charTypes[ix]==B){
			levels[ix]=0;
		}
		hiLevel|=newLevel;
	}
	if(hasUBAT_S){
		for(i=0;i<len;i++){
			if(charTypes[i]==S){
				levels[i]=dir;
				for(varj=i-1;j>=0;j--){
					if(charTypes[j]==WS){
						levels[j]=dir;
					}else{
						break;
					}
				}
			}
		}
	}
}

function_invertLevel(lev,levels,_array){
	if(hiLevel<lev){
		return;
	}
	if(lev==1&&dir==RTL&&!hasUBAT_B){
		_array.reverse();
		return;
	}
	varlen=_array.length,start=0,end,lo,hi,tmp;
	while(start<len){
		if(levels[start]>=lev){
			end=start+1;
		while(end<len&&levels[end]>=lev){
			end++;
		}
		for(lo=start,hi=end-1;lo<hi;lo++,hi--){
			tmp=_array[lo];
			_array[lo]=_array[hi];
			_array[hi]=tmp;
		}
		start=end;
	}
	start++;
	}
}

function_getCharClass(chars,types,classes,ix){			
	varcType=types[ix],wType,nType,len,i;
	switch(cType){
		caseL:
		caseR:
			lastArabic=false;
		caseON:
		caseAN:
			returncType;
		caseEN:
			returnlastArabic?AN:EN;
		caseAL:
			lastArabic=true;
			hasUBAT_AL=true;
			returnR;
		caseWS:
			returnON;
		caseCS:
			if(ix<1||(ix+1)>=types.length||
				((wType=classes[ix-1])!=EN&&wType!=AN)||
				((nType=types[ix+1])!=EN&&nType!=AN)){
				returnON;
			}
			if(lastArabic){nType=AN;}
			returnnType==wType?nType:ON;
		caseES:
			wType=ix>0?classes[ix-1]:B;
			if(wType==EN&&(ix+1)<types.length&&types[ix+1]==EN){
				returnEN;
			}
			returnON;
		caseET:
			if(ix>0&&classes[ix-1]==EN){
				returnEN;
			}
			if(lastArabic){
				returnON;
			}
			i=ix+1;
			len=types.length;
			while(i<len&&types[i]==ET){
				i++;
			}
			if(i<len&&types[i]==EN){
				returnEN;
			}
			returnON;
		caseNSM:
			len=types.length;
			i=ix+1;
			while(i<len&&types[i]==NSM){
				i++;
			}
			if(i<len){
				varc=chars[ix],rtlCandidate=(c>=0x0591&&c<=0x08FF)||c==0xFB1E;
				
				wType=types[i];
				if(rtlCandidate&&(wType==R||wType==AL)){
					returnR;
				}
			}

			if(ix<1||(wType=types[ix-1])==B){
				returnON;
			}
			returnclasses[ix-1];
		caseB:
			lastArabic=false;
			hasUBAT_B=true;
			returndir;
		caseS:
			hasUBAT_S=true;
			returnON;
		caseLRE:
		caseRLE:
		caseLRO:
		caseRLO:
		casePDF:
			lastArabic=false;
		caseBN:
			returnON;
	}
}

function_getCharacterType(ch){		
	varuc=ch.charCodeAt(0),hi=uc>>8;
	
	if(hi==0){		
		return((uc>0x00BF)?L:UnicodeTBL00[uc]);
	}elseif(hi==5){
		return(/[\u0591-\u05f4]/.test(ch)?R:L);
	}elseif(hi==6){
		if(/[\u0610-\u061a\u064b-\u065f\u06d6-\u06e4\u06e7-\u06ed]/.test(ch))
			returnNSM;
		elseif(/[\u0660-\u0669\u066b-\u066c]/.test(ch))
			returnAN;
		elseif(uc==0x066A)
			returnET;
		elseif(/[\u06f0-\u06f9]/.test(ch))
			returnEN;			
		else
			returnAL;
	}elseif(hi==0x20&&uc<=0x205F){
		returnUnicodeTBL20[uc&0xFF];
	}elseif(hi==0xFE){
		return(uc>=0xFE70?AL:ON);
	}		
	returnON;	
}

function_isArabicDiacritics(ch){
	return(ch>='\u064b'&&ch<='\u0655');
}
exports.L=L;
exports.R=R;
exports.EN=EN;
exports.ON_R=3;
exports.AN=4;
exports.R_H=5;
exports.B=6;

exports.DOT="\xB7";
exports.doBidiReorder=function(text,textCharTypes,isRtl){
	if(text.length<2)
		return{};
		
	varchars=text.split(""),logicalFromVisual=newArray(chars.length),
		bidiLevels=newArray(chars.length),levels=[];

	dir=isRtl?RTL:LTR;

	_computeLevels(chars,levels,chars.length,textCharTypes);

	for(vari=0;i<logicalFromVisual.length;logicalFromVisual[i]=i,i++);

	_invertLevel(2,levels,logicalFromVisual);
	_invertLevel(1,levels,logicalFromVisual);

	for(vari=0;i<logicalFromVisual.length-1;i++){//fixlevelstoreflectcharacterwidth
		if(textCharTypes[i]===AN){
			levels[i]=exports.AN;
		}elseif(levels[i]===R&&((textCharTypes[i]>AL&&textCharTypes[i]<LRE)
			||textCharTypes[i]===ON||textCharTypes[i]===BN)){
			levels[i]=exports.ON_R;
		}elseif((i>0&&chars[i-1]==='\u0644')&&/\u0622|\u0623|\u0625|\u0627/.test(chars[i])){
			levels[i-1]=levels[i]=exports.R_H;
			i++;
		}
	}
	if(chars[chars.length-1]===exports.DOT)
		levels[chars.length-1]=exports.B;
				
	for(vari=0;i<logicalFromVisual.length;i++){
		bidiLevels[i]=levels[logicalFromVisual[i]];
	}

	return{'logicalFromVisual':logicalFromVisual,'bidiLevels':bidiLevels};
};
exports.hasBidiCharacters=function(text,textCharTypes){
	varret=false;
	for(vari=0;i<text.length;i++){
		textCharTypes[i]=_getCharacterType(text.charAt(i));
		if(!ret&&(textCharTypes[i]==R||textCharTypes[i]==AL))
			ret=true;
	}
	returnret;
};	
exports.getVisualFromLogicalIdx=function(logIdx,rowMap){
	for(vari=0;i<rowMap.logicalFromVisual.length;i++){
		if(rowMap.logicalFromVisual[i]==logIdx)
			returni;
	}
	return0;
};

});

define("ace/bidihandler",["require","exports","module","ace/lib/bidiutil","ace/lib/lang","ace/lib/useragent"],function(require,exports,module){
"usestrict";

varbidiUtil=require("./lib/bidiutil");
varlang=require("./lib/lang");
varuseragent=require("./lib/useragent");
varbidiRE=/[\u0590-\u05f4\u0600-\u06ff\u0700-\u08ac]/;
varBidiHandler=function(session){
    this.session=session;
    this.bidiMap={};
    this.currentRow=null;
    this.bidiUtil=bidiUtil;
    this.charWidths=[];
    this.EOL="\xAC";
    this.showInvisibles=true;
    this.isRtlDir=false;
    this.line="";
    this.wrapIndent=0;
    this.isLastRow=false;
    this.EOF="\xB6";
    this.seenBidi=false;
};

(function(){
    this.isBidiRow=function(screenRow,docRow,splitIndex){
        if(!this.seenBidi)
            returnfalse;
        if(screenRow!==this.currentRow){
            this.currentRow=screenRow;
            this.updateRowLine(docRow,splitIndex);
            this.updateBidiMap();
        }
        returnthis.bidiMap.bidiLevels;
    };

    this.onChange=function(delta){
        if(!this.seenBidi){
            if(delta.action=="insert"&&bidiRE.test(delta.lines.join("\n"))){
                this.seenBidi=true;
                this.currentRow=null;
            }
        }
        else{
            this.currentRow=null;
        }
    };

    this.getDocumentRow=function(){
        vardocRow=0;
        varrowCache=this.session.$screenRowCache;
        if(rowCache.length){
            varindex=this.session.$getRowCacheIndex(rowCache,this.currentRow);
            if(index>=0)
                docRow=this.session.$docRowCache[index];
        }

        returndocRow;
    };

    this.getSplitIndex=function(){
        varsplitIndex=0;
        varrowCache=this.session.$screenRowCache;
        if(rowCache.length){
            varcurrentIndex,prevIndex=this.session.$getRowCacheIndex(rowCache,this.currentRow);
            while(this.currentRow-splitIndex>0){
                currentIndex=this.session.$getRowCacheIndex(rowCache,this.currentRow-splitIndex-1);
                if(currentIndex!==prevIndex)
                    break;

                prevIndex=currentIndex;
                splitIndex++;
            }
        }

        returnsplitIndex;
    };

    this.updateRowLine=function(docRow,splitIndex){
        if(docRow===undefined)
            docRow=this.getDocumentRow();
            
        this.wrapIndent=0;
        this.isLastRow=(docRow===this.session.getLength()-1);
        this.line=this.session.getLine(docRow);
        if(this.session.$useWrapMode){
            varsplits=this.session.$wrapData[docRow];
            if(splits){
                if(splitIndex===undefined)
                    splitIndex=this.getSplitIndex();

                if(splitIndex>0&&splits.length){
                    this.wrapIndent=splits.indent;
                    this.line=(splitIndex<splits.length)?
                        this.line.substring(splits[splitIndex-1],splits[splits.length-1]):
                            this.line.substring(splits[splits.length-1]);
                }else{
                    this.line=this.line.substring(0,splits[splitIndex]);
                }
            }
        }
        varsession=this.session,shift=0,size;
        this.line=this.line.replace(/\t|[\u1100-\u2029,\u202F-\uFFE6]/g,function(ch,i){
            if(ch==='\t'||session.isFullWidth(ch.charCodeAt(0))){
                size=(ch==='\t')?session.getScreenTabSize(i+shift):2;
                shift+=size-1;
                returnlang.stringRepeat(bidiUtil.DOT,size);
            }
            returnch;
        });
    };
    
    this.updateBidiMap=function(){
        vartextCharTypes=[],endOfLine=this.isLastRow?this.EOF:this.EOL;
        varline=this.line+(this.showInvisibles?endOfLine:bidiUtil.DOT);
        if(bidiUtil.hasBidiCharacters(line,textCharTypes)){
            this.bidiMap=bidiUtil.doBidiReorder(line,textCharTypes,this.isRtlDir);
        }else{
            this.bidiMap={};
        }
    };
    this.markAsDirty=function(){
        this.currentRow=null;
    };
    this.updateCharacterWidths=function(fontMetrics){
        if(!this.seenBidi)
            return;
        if(this.characterWidth===fontMetrics.$characterSize.width)
            return;

        varcharacterWidth=this.characterWidth=fontMetrics.$characterSize.width;
        varbidiCharWidth=fontMetrics.$measureCharWidth("\u05d4");

        this.charWidths[bidiUtil.L]=this.charWidths[bidiUtil.EN]=this.charWidths[bidiUtil.ON_R]=characterWidth;
        this.charWidths[bidiUtil.R]=this.charWidths[bidiUtil.AN]=bidiCharWidth;
        this.charWidths[bidiUtil.R_H]=useragent.isChrome?bidiCharWidth:bidiCharWidth*0.45;
        this.charWidths[bidiUtil.B]=0;

        this.currentRow=null;
    };

    this.getShowInvisibles=function(){
        returnthis.showInvisibles;
    };

    this.setShowInvisibles=function(showInvisibles){
        this.showInvisibles=showInvisibles;
        this.currentRow=null;
    };

    this.setEolChar=function(eolChar){
        this.EOL=eolChar;
    };

    this.setTextDir=function(isRtlDir){
        this.isRtlDir=isRtlDir;
    };
    this.getPosLeft=function(col){
        col-=this.wrapIndent;
        varvisualIdx=bidiUtil.getVisualFromLogicalIdx(col>0?col-1:0,this.bidiMap),
            levels=this.bidiMap.bidiLevels,left=0;

        if(col===0&&levels[visualIdx]%2!==0)
            visualIdx++;

        for(vari=0;i<visualIdx;i++){
            left+=this.charWidths[levels[i]];
        }

        if(col!==0&&levels[visualIdx]%2===0)
            left+=this.charWidths[levels[visualIdx]];

        if(this.wrapIndent)
            left+=this.wrapIndent*this.charWidths[bidiUtil.L];

        returnleft;
    };
    this.getSelections=function(startCol,endCol){
        varmap=this.bidiMap,levels=map.bidiLevels,level,offset=this.wrapIndent*this.charWidths[bidiUtil.L],selections=[],
            selColMin=Math.min(startCol,endCol)-this.wrapIndent,selColMax=Math.max(startCol,endCol)-this.wrapIndent,
                isSelected=false,isSelectedPrev=false,selectionStart=0;

        for(varlogIdx,visIdx=0;visIdx<levels.length;visIdx++){
            logIdx=map.logicalFromVisual[visIdx];
            level=levels[visIdx];
            isSelected=(logIdx>=selColMin)&&(logIdx<selColMax);
            if(isSelected&&!isSelectedPrev){
                selectionStart=offset;
            }elseif(!isSelected&&isSelectedPrev){
                selections.push({left:selectionStart,width:offset-selectionStart});
            }
            offset+=this.charWidths[level];
            isSelectedPrev=isSelected;
        }

        if(isSelected&&(visIdx===levels.length)){
            selections.push({left:selectionStart,width:offset-selectionStart});
        }

        returnselections;
    };
    this.offsetToCol=function(posX){
        varlogicalIdx=0,posX=Math.max(posX,0),
            offset=0,visualIdx=0,levels=this.bidiMap.bidiLevels,
                charWidth=this.charWidths[levels[visualIdx]];

        if(this.wrapIndent){
            posX-=this.wrapIndent*this.charWidths[bidiUtil.L];
        }
    
        while(posX>offset+charWidth/2){
            offset+=charWidth;
            if(visualIdx===levels.length-1){
                charWidth=0;
                break;
            }
            charWidth=this.charWidths[levels[++visualIdx]];
        }
    
        if(visualIdx>0&&(levels[visualIdx-1]%2!==0)&&(levels[visualIdx]%2===0)){
            if(posX<offset)
                visualIdx--;
            logicalIdx=this.bidiMap.logicalFromVisual[visualIdx];

        }elseif(visualIdx>0&&(levels[visualIdx-1]%2===0)&&(levels[visualIdx]%2!==0)){
            logicalIdx=1+((posX>offset)?this.bidiMap.logicalFromVisual[visualIdx]
                    :this.bidiMap.logicalFromVisual[visualIdx-1]);

        }elseif((this.isRtlDir&&visualIdx===levels.length-1&&charWidth===0&&(levels[visualIdx-1]%2===0))
                ||(!this.isRtlDir&&visualIdx===0&&(levels[visualIdx]%2!==0))){
            logicalIdx=1+this.bidiMap.logicalFromVisual[visualIdx];
        }else{
            if(visualIdx>0&&(levels[visualIdx-1]%2!==0)&&charWidth!==0)
                visualIdx--;
            logicalIdx=this.bidiMap.logicalFromVisual[visualIdx];
        }

        return(logicalIdx+this.wrapIndent);
    };

}).call(BidiHandler.prototype);

exports.BidiHandler=BidiHandler;
});

define("ace/selection",["require","exports","module","ace/lib/oop","ace/lib/lang","ace/lib/event_emitter","ace/range"],function(require,exports,module){
"usestrict";

varoop=require("./lib/oop");
varlang=require("./lib/lang");
varEventEmitter=require("./lib/event_emitter").EventEmitter;
varRange=require("./range").Range;
varSelection=function(session){
    this.session=session;
    this.doc=session.getDocument();

    this.clearSelection();
    this.cursor=this.lead=this.doc.createAnchor(0,0);
    this.anchor=this.doc.createAnchor(0,0);
    this.$silent=false;

    varself=this;
    this.cursor.on("change",function(e){
        self.$cursorChanged=true;
        if(!self.$silent)
            self._emit("changeCursor");
        if(!self.$isEmpty&&!self.$silent)
            self._emit("changeSelection");
        if(!self.$keepDesiredColumnOnChange&&e.old.column!=e.value.column)
            self.$desiredColumn=null;
    });

    this.anchor.on("change",function(){
        self.$anchorChanged=true;
        if(!self.$isEmpty&&!self.$silent)
            self._emit("changeSelection");
    });
};

(function(){

    oop.implement(this,EventEmitter);
    this.isEmpty=function(){
        returnthis.$isEmpty||(
            this.anchor.row==this.lead.row&&
            this.anchor.column==this.lead.column
        );
    };
    this.isMultiLine=function(){
        return!this.$isEmpty&&this.anchor.row!=this.cursor.row;
    };
    this.getCursor=function(){
        returnthis.lead.getPosition();
    };
    this.setSelectionAnchor=function(row,column){
        this.$isEmpty=false;
        this.anchor.setPosition(row,column);
    };
    this.getAnchor=
    this.getSelectionAnchor=function(){
        if(this.$isEmpty)
            returnthis.getSelectionLead();
        
        returnthis.anchor.getPosition();
    };
    this.getSelectionLead=function(){
        returnthis.lead.getPosition();
    };
    this.isBackwards=function(){
        varanchor=this.anchor;
        varlead=this.lead;
        return(anchor.row>lead.row||(anchor.row==lead.row&&anchor.column>lead.column));
    };
    this.getRange=function(){
        varanchor=this.anchor;
        varlead=this.lead;

        if(this.$isEmpty)
            returnRange.fromPoints(lead,lead);

        returnthis.isBackwards()
            ?Range.fromPoints(lead,anchor)
            :Range.fromPoints(anchor,lead);
    };
    this.clearSelection=function(){
        if(!this.$isEmpty){
            this.$isEmpty=true;
            this._emit("changeSelection");
        }
    };
    this.selectAll=function(){
        this.$setSelection(0,0,Number.MAX_VALUE,Number.MAX_VALUE);
    };
    this.setRange=
    this.setSelectionRange=function(range,reverse){
        varstart=reverse?range.end:range.start;
        varend=reverse?range.start:range.end;
        this.$setSelection(start.row,start.column,end.row,end.column);
    };

    this.$setSelection=function(anchorRow,anchorColumn,cursorRow,cursorColumn){
        varwasEmpty=this.$isEmpty;
        this.$silent=true;
        this.$cursorChanged=this.$anchorChanged=false;
        this.anchor.setPosition(anchorRow,anchorColumn);
        this.cursor.setPosition(cursorRow,cursorColumn);
        this.$isEmpty=!Range.comparePoints(this.anchor,this.cursor);
        this.$silent=false;
        if(this.$cursorChanged)
            this._emit("changeCursor");
        if(this.$cursorChanged||this.$anchorChanged)
            this._emit("changeSelection");
    };

    this.$moveSelection=function(mover){
        varlead=this.lead;
        if(this.$isEmpty)
            this.setSelectionAnchor(lead.row,lead.column);

        mover.call(this);
    };
    this.selectTo=function(row,column){
        this.$moveSelection(function(){
            this.moveCursorTo(row,column);
        });
    };
    this.selectToPosition=function(pos){
        this.$moveSelection(function(){
            this.moveCursorToPosition(pos);
        });
    };
    this.moveTo=function(row,column){
        this.clearSelection();
        this.moveCursorTo(row,column);
    };
    this.moveToPosition=function(pos){
        this.clearSelection();
        this.moveCursorToPosition(pos);
    };
    this.selectUp=function(){
        this.$moveSelection(this.moveCursorUp);
    };
    this.selectDown=function(){
        this.$moveSelection(this.moveCursorDown);
    };
    this.selectRight=function(){
        this.$moveSelection(this.moveCursorRight);
    };
    this.selectLeft=function(){
        this.$moveSelection(this.moveCursorLeft);
    };
    this.selectLineStart=function(){
        this.$moveSelection(this.moveCursorLineStart);
    };
    this.selectLineEnd=function(){
        this.$moveSelection(this.moveCursorLineEnd);
    };
    this.selectFileEnd=function(){
        this.$moveSelection(this.moveCursorFileEnd);
    };
    this.selectFileStart=function(){
        this.$moveSelection(this.moveCursorFileStart);
    };
    this.selectWordRight=function(){
        this.$moveSelection(this.moveCursorWordRight);
    };
    this.selectWordLeft=function(){
        this.$moveSelection(this.moveCursorWordLeft);
    };
    this.getWordRange=function(row,column){
        if(typeofcolumn=="undefined"){
            varcursor=row||this.lead;
            row=cursor.row;
            column=cursor.column;
        }
        returnthis.session.getWordRange(row,column);
    };
    this.selectWord=function(){
        this.setSelectionRange(this.getWordRange());
    };
    this.selectAWord=function(){
        varcursor=this.getCursor();
        varrange=this.session.getAWordRange(cursor.row,cursor.column);
        this.setSelectionRange(range);
    };

    this.getLineRange=function(row,excludeLastChar){
        varrowStart=typeofrow=="number"?row:this.lead.row;
        varrowEnd;

        varfoldLine=this.session.getFoldLine(rowStart);
        if(foldLine){
            rowStart=foldLine.start.row;
            rowEnd=foldLine.end.row;
        }else{
            rowEnd=rowStart;
        }
        if(excludeLastChar===true)
            returnnewRange(rowStart,0,rowEnd,this.session.getLine(rowEnd).length);
        else
            returnnewRange(rowStart,0,rowEnd+1,0);
    };
    this.selectLine=function(){
        this.setSelectionRange(this.getLineRange());
    };
    this.moveCursorUp=function(){
        this.moveCursorBy(-1,0);
    };
    this.moveCursorDown=function(){
        this.moveCursorBy(1,0);
    };
    this.wouldMoveIntoSoftTab=function(cursor,tabSize,direction){
        varstart=cursor.column;
        varend=cursor.column+tabSize;

        if(direction<0){
            start=cursor.column-tabSize;
            end=cursor.column;
        }
        returnthis.session.isTabStop(cursor)&&this.doc.getLine(cursor.row).slice(start,end).split("").length-1==tabSize;
    };
    this.moveCursorLeft=function(){
        varcursor=this.lead.getPosition(),
            fold;

        if(fold=this.session.getFoldAt(cursor.row,cursor.column,-1)){
            this.moveCursorTo(fold.start.row,fold.start.column);
        }elseif(cursor.column===0){
            if(cursor.row>0){
                this.moveCursorTo(cursor.row-1,this.doc.getLine(cursor.row-1).length);
            }
        }
        else{
            vartabSize=this.session.getTabSize();
            if(this.wouldMoveIntoSoftTab(cursor,tabSize,-1)&&!this.session.getNavigateWithinSoftTabs()){
                this.moveCursorBy(0,-tabSize);
            }else{
                this.moveCursorBy(0,-1);
            }
        }
    };
    this.moveCursorRight=function(){
        varcursor=this.lead.getPosition(),
            fold;
        if(fold=this.session.getFoldAt(cursor.row,cursor.column,1)){
            this.moveCursorTo(fold.end.row,fold.end.column);
        }
        elseif(this.lead.column==this.doc.getLine(this.lead.row).length){
            if(this.lead.row<this.doc.getLength()-1){
                this.moveCursorTo(this.lead.row+1,0);
            }
        }
        else{
            vartabSize=this.session.getTabSize();
            varcursor=this.lead;
            if(this.wouldMoveIntoSoftTab(cursor,tabSize,1)&&!this.session.getNavigateWithinSoftTabs()){
                this.moveCursorBy(0,tabSize);
            }else{
                this.moveCursorBy(0,1);
            }
        }
    };
    this.moveCursorLineStart=function(){
        varrow=this.lead.row;
        varcolumn=this.lead.column;
        varscreenRow=this.session.documentToScreenRow(row,column);
        varfirstColumnPosition=this.session.screenToDocumentPosition(screenRow,0);
        varbeforeCursor=this.session.getDisplayLine(
            row,null,firstColumnPosition.row,
            firstColumnPosition.column
        );

        varleadingSpace=beforeCursor.match(/^\s*/);
        if(leadingSpace[0].length!=column&&!this.session.$useEmacsStyleLineStart)
            firstColumnPosition.column+=leadingSpace[0].length;
        this.moveCursorToPosition(firstColumnPosition);
    };
    this.moveCursorLineEnd=function(){
        varlead=this.lead;
        varlineEnd=this.session.getDocumentLastRowColumnPosition(lead.row,lead.column);
        if(this.lead.column==lineEnd.column){
            varline=this.session.getLine(lineEnd.row);
            if(lineEnd.column==line.length){
                vartextEnd=line.search(/\s+$/);
                if(textEnd>0)
                    lineEnd.column=textEnd;
            }
        }

        this.moveCursorTo(lineEnd.row,lineEnd.column);
    };
    this.moveCursorFileEnd=function(){
        varrow=this.doc.getLength()-1;
        varcolumn=this.doc.getLine(row).length;
        this.moveCursorTo(row,column);
    };
    this.moveCursorFileStart=function(){
        this.moveCursorTo(0,0);
    };
    this.moveCursorLongWordRight=function(){
        varrow=this.lead.row;
        varcolumn=this.lead.column;
        varline=this.doc.getLine(row);
        varrightOfCursor=line.substring(column);

        this.session.nonTokenRe.lastIndex=0;
        this.session.tokenRe.lastIndex=0;
        varfold=this.session.getFoldAt(row,column,1);
        if(fold){
            this.moveCursorTo(fold.end.row,fold.end.column);
            return;
        }
        if(this.session.nonTokenRe.exec(rightOfCursor)){
            column+=this.session.nonTokenRe.lastIndex;
            this.session.nonTokenRe.lastIndex=0;
            rightOfCursor=line.substring(column);
        }
        if(column>=line.length){
            this.moveCursorTo(row,line.length);
            this.moveCursorRight();
            if(row<this.doc.getLength()-1)
                this.moveCursorWordRight();
            return;
        }
        if(this.session.tokenRe.exec(rightOfCursor)){
            column+=this.session.tokenRe.lastIndex;
            this.session.tokenRe.lastIndex=0;
        }

        this.moveCursorTo(row,column);
    };
    this.moveCursorLongWordLeft=function(){
        varrow=this.lead.row;
        varcolumn=this.lead.column;
        varfold;
        if(fold=this.session.getFoldAt(row,column,-1)){
            this.moveCursorTo(fold.start.row,fold.start.column);
            return;
        }

        varstr=this.session.getFoldStringAt(row,column,-1);
        if(str==null){
            str=this.doc.getLine(row).substring(0,column);
        }

        varleftOfCursor=lang.stringReverse(str);
        this.session.nonTokenRe.lastIndex=0;
        this.session.tokenRe.lastIndex=0;
        if(this.session.nonTokenRe.exec(leftOfCursor)){
            column-=this.session.nonTokenRe.lastIndex;
            leftOfCursor=leftOfCursor.slice(this.session.nonTokenRe.lastIndex);
            this.session.nonTokenRe.lastIndex=0;
        }
        if(column<=0){
            this.moveCursorTo(row,0);
            this.moveCursorLeft();
            if(row>0)
                this.moveCursorWordLeft();
            return;
        }
        if(this.session.tokenRe.exec(leftOfCursor)){
            column-=this.session.tokenRe.lastIndex;
            this.session.tokenRe.lastIndex=0;
        }

        this.moveCursorTo(row,column);
    };

    this.$shortWordEndIndex=function(rightOfCursor){
        varindex=0,ch;
        varwhitespaceRe=/\s/;
        vartokenRe=this.session.tokenRe;

        tokenRe.lastIndex=0;
        if(this.session.tokenRe.exec(rightOfCursor)){
            index=this.session.tokenRe.lastIndex;
        }else{
            while((ch=rightOfCursor[index])&&whitespaceRe.test(ch))
                index++;

            if(index<1){
                tokenRe.lastIndex=0;
                 while((ch=rightOfCursor[index])&&!tokenRe.test(ch)){
                    tokenRe.lastIndex=0;
                    index++;
                    if(whitespaceRe.test(ch)){
                        if(index>2){
                            index--;
                            break;
                        }else{
                            while((ch=rightOfCursor[index])&&whitespaceRe.test(ch))
                                index++;
                            if(index>2)
                                break;
                        }
                    }
                }
            }
        }
        tokenRe.lastIndex=0;

        returnindex;
    };

    this.moveCursorShortWordRight=function(){
        varrow=this.lead.row;
        varcolumn=this.lead.column;
        varline=this.doc.getLine(row);
        varrightOfCursor=line.substring(column);

        varfold=this.session.getFoldAt(row,column,1);
        if(fold)
            returnthis.moveCursorTo(fold.end.row,fold.end.column);

        if(column==line.length){
            varl=this.doc.getLength();
            do{
                row++;
                rightOfCursor=this.doc.getLine(row);
            }while(row<l&&/^\s*$/.test(rightOfCursor));

            if(!/^\s+/.test(rightOfCursor))
                rightOfCursor="";
            column=0;
        }

        varindex=this.$shortWordEndIndex(rightOfCursor);

        this.moveCursorTo(row,column+index);
    };

    this.moveCursorShortWordLeft=function(){
        varrow=this.lead.row;
        varcolumn=this.lead.column;

        varfold;
        if(fold=this.session.getFoldAt(row,column,-1))
            returnthis.moveCursorTo(fold.start.row,fold.start.column);

        varline=this.session.getLine(row).substring(0,column);
        if(column===0){
            do{
                row--;
                line=this.doc.getLine(row);
            }while(row>0&&/^\s*$/.test(line));

            column=line.length;
            if(!/\s+$/.test(line))
                line="";
        }

        varleftOfCursor=lang.stringReverse(line);
        varindex=this.$shortWordEndIndex(leftOfCursor);

        returnthis.moveCursorTo(row,column-index);
    };

    this.moveCursorWordRight=function(){
        if(this.session.$selectLongWords)
            this.moveCursorLongWordRight();
        else
            this.moveCursorShortWordRight();
    };

    this.moveCursorWordLeft=function(){
        if(this.session.$selectLongWords)
            this.moveCursorLongWordLeft();
        else
            this.moveCursorShortWordLeft();
    };
    this.moveCursorBy=function(rows,chars){
        varscreenPos=this.session.documentToScreenPosition(
            this.lead.row,
            this.lead.column
        );

        varoffsetX;

        if(chars===0){
            if(rows!==0){
                if(this.session.$bidiHandler.isBidiRow(screenPos.row,this.lead.row)){
                    offsetX=this.session.$bidiHandler.getPosLeft(screenPos.column);
                    screenPos.column=Math.round(offsetX/this.session.$bidiHandler.charWidths[0]);
                }else{
                    offsetX=screenPos.column*this.session.$bidiHandler.charWidths[0];
                }
            }

            if(this.$desiredColumn)
                screenPos.column=this.$desiredColumn;
            else
                this.$desiredColumn=screenPos.column;
        }

        vardocPos=this.session.screenToDocumentPosition(screenPos.row+rows,screenPos.column,offsetX);
        
        if(rows!==0&&chars===0&&docPos.row===this.lead.row&&docPos.column===this.lead.column){
            if(this.session.lineWidgets&&this.session.lineWidgets[docPos.row]){
                if(docPos.row>0||rows>0)
                    docPos.row++;
            }
        }
        this.moveCursorTo(docPos.row,docPos.column+chars,chars===0);
    };
    this.moveCursorToPosition=function(position){
        this.moveCursorTo(position.row,position.column);
    };
    this.moveCursorTo=function(row,column,keepDesiredColumn){
        varfold=this.session.getFoldAt(row,column,1);
        if(fold){
            row=fold.start.row;
            column=fold.start.column;
        }

        this.$keepDesiredColumnOnChange=true;
        varline=this.session.getLine(row);
        if(/[\uDC00-\uDFFF]/.test(line.charAt(column))&&line.charAt(column-1)){
            if(this.lead.row==row&&this.lead.column==column+1)
                column=column-1;
            else
                column=column+1;
        }
        this.lead.setPosition(row,column);
        this.$keepDesiredColumnOnChange=false;

        if(!keepDesiredColumn)
            this.$desiredColumn=null;
    };
    this.moveCursorToScreen=function(row,column,keepDesiredColumn){
        varpos=this.session.screenToDocumentPosition(row,column);
        this.moveCursorTo(pos.row,pos.column,keepDesiredColumn);
    };
    this.detach=function(){
        this.lead.detach();
        this.anchor.detach();
        this.session=this.doc=null;
    };

    this.fromOrientedRange=function(range){
        this.setSelectionRange(range,range.cursor==range.start);
        this.$desiredColumn=range.desiredColumn||this.$desiredColumn;
    };

    this.toOrientedRange=function(range){
        varr=this.getRange();
        if(range){
            range.start.column=r.start.column;
            range.start.row=r.start.row;
            range.end.column=r.end.column;
            range.end.row=r.end.row;
        }else{
            range=r;
        }

        range.cursor=this.isBackwards()?range.start:range.end;
        range.desiredColumn=this.$desiredColumn;
        returnrange;
    };
    this.getRangeOfMovements=function(func){
        varstart=this.getCursor();
        try{
            func(this);
            varend=this.getCursor();
            returnRange.fromPoints(start,end);
        }catch(e){
            returnRange.fromPoints(start,start);
        }finally{
            this.moveCursorToPosition(start);
        }
    };

    this.toJSON=function(){
        if(this.rangeCount){
            vardata=this.ranges.map(function(r){
                varr1=r.clone();
                r1.isBackwards=r.cursor==r.start;
                returnr1;
            });
        }else{
            vardata=this.getRange();
            data.isBackwards=this.isBackwards();
        }
        returndata;
    };

    this.fromJSON=function(data){
        if(data.start==undefined){
            if(this.rangeList){
                this.toSingleRange(data[0]);
                for(vari=data.length;i--;){
                    varr=Range.fromPoints(data[i].start,data[i].end);
                    if(data[i].isBackwards)
                        r.cursor=r.start;
                    this.addRange(r,true);
                }
                return;
            }else{
                data=data[0];
            }
        }
        if(this.rangeList)
            this.toSingleRange(data);
        this.setSelectionRange(data,data.isBackwards);
    };

    this.isEqual=function(data){
        if((data.length||this.rangeCount)&&data.length!=this.rangeCount)
            returnfalse;
        if(!data.length||!this.ranges)
            returnthis.getRange().isEqual(data);

        for(vari=this.ranges.length;i--;){
            if(!this.ranges[i].isEqual(data[i]))
                returnfalse;
        }
        returntrue;
    };

}).call(Selection.prototype);

exports.Selection=Selection;
});

define("ace/tokenizer",["require","exports","module","ace/config"],function(require,exports,module){
"usestrict";

varconfig=require("./config");
varMAX_TOKEN_COUNT=2000;
varTokenizer=function(rules){
    this.states=rules;

    this.regExps={};
    this.matchMappings={};
    for(varkeyinthis.states){
        varstate=this.states[key];
        varruleRegExps=[];
        varmatchTotal=0;
        varmapping=this.matchMappings[key]={defaultToken:"text"};
        varflag="g";

        varsplitterRurles=[];
        for(vari=0;i<state.length;i++){
            varrule=state[i];
            if(rule.defaultToken)
                mapping.defaultToken=rule.defaultToken;
            if(rule.caseInsensitive)
                flag="gi";
            if(rule.regex==null)
                continue;

            if(rule.regexinstanceofRegExp)
                rule.regex=rule.regex.toString().slice(1,-1);
            varadjustedregex=rule.regex;
            varmatchcount=newRegExp("(?:("+adjustedregex+")|(.))").exec("a").length-2;
            if(Array.isArray(rule.token)){
                if(rule.token.length==1||matchcount==1){
                    rule.token=rule.token[0];
                }elseif(matchcount-1!=rule.token.length){
                    this.reportError("numberofclassesandregexpgroupsdoesn'tmatch",{
                        rule:rule,
                        groupCount:matchcount-1
                    });
                    rule.token=rule.token[0];
                }else{
                    rule.tokenArray=rule.token;
                    rule.token=null;
                    rule.onMatch=this.$arrayTokens;
                }
            }elseif(typeofrule.token=="function"&&!rule.onMatch){
                if(matchcount>1)
                    rule.onMatch=this.$applyToken;
                else
                    rule.onMatch=rule.token;
            }

            if(matchcount>1){
                if(/\\\d/.test(rule.regex)){
                    adjustedregex=rule.regex.replace(/\\([0-9]+)/g,function(match,digit){
                        return"\\"+(parseInt(digit,10)+matchTotal+1);
                    });
                }else{
                    matchcount=1;
                    adjustedregex=this.removeCapturingGroups(rule.regex);
                }
                if(!rule.splitRegex&&typeofrule.token!="string")
                    splitterRurles.push(rule);//flagwillbeknownonlyattheveryend
            }

            mapping[matchTotal]=i;
            matchTotal+=matchcount;

            ruleRegExps.push(adjustedregex);
            if(!rule.onMatch)
                rule.onMatch=null;
        }
        
        if(!ruleRegExps.length){
            mapping[0]=0;
            ruleRegExps.push("$");
        }
        
        splitterRurles.forEach(function(rule){
            rule.splitRegex=this.createSplitterRegexp(rule.regex,flag);
        },this);

        this.regExps[key]=newRegExp("("+ruleRegExps.join(")|(")+")|($)",flag);
    }
};

(function(){
    this.$setMaxTokenCount=function(m){
        MAX_TOKEN_COUNT=m|0;
    };
    
    this.$applyToken=function(str){
        varvalues=this.splitRegex.exec(str).slice(1);
        vartypes=this.token.apply(this,values);
        if(typeoftypes==="string")
            return[{type:types,value:str}];

        vartokens=[];
        for(vari=0,l=types.length;i<l;i++){
            if(values[i])
                tokens[tokens.length]={
                    type:types[i],
                    value:values[i]
                };
        }
        returntokens;
    };

    this.$arrayTokens=function(str){
        if(!str)
            return[];
        varvalues=this.splitRegex.exec(str);
        if(!values)
            return"text";
        vartokens=[];
        vartypes=this.tokenArray;
        for(vari=0,l=types.length;i<l;i++){
            if(values[i+1])
                tokens[tokens.length]={
                    type:types[i],
                    value:values[i+1]
                };
        }
        returntokens;
    };

    this.removeCapturingGroups=function(src){
        varr=src.replace(
            /\[(?:\\.|[^\]])*?\]|\\.|\(\?[:=!]|(\()/g,
            function(x,y){returny?"(?:":x;}
        );
        returnr;
    };

    this.createSplitterRegexp=function(src,flag){
        if(src.indexOf("(?=")!=-1){
            varstack=0;
            varinChClass=false;
            varlastCapture={};
            src.replace(/(\\.)|(\((?:\?[=!])?)|(\))|([\[\]])/g,function(
                m,esc,parenOpen,parenClose,square,index
            ){
                if(inChClass){
                    inChClass=square!="]";
                }elseif(square){
                    inChClass=true;
                }elseif(parenClose){
                    if(stack==lastCapture.stack){
                        lastCapture.end=index+1;
                        lastCapture.stack=-1;
                    }
                    stack--;
                }elseif(parenOpen){
                    stack++;
                    if(parenOpen.length!=1){
                        lastCapture.stack=stack;
                        lastCapture.start=index;
                    }
                }
                returnm;
            });

            if(lastCapture.end!=null&&/^\)*$/.test(src.substr(lastCapture.end)))
                src=src.substring(0,lastCapture.start)+src.substr(lastCapture.end);
        }
        if(src.charAt(0)!="^")src="^"+src;
        if(src.charAt(src.length-1)!="$")src+="$";
        
        returnnewRegExp(src,(flag||"").replace("g",""));
    };
    this.getLineTokens=function(line,startState){
        if(startState&&typeofstartState!="string"){
            varstack=startState.slice(0);
            startState=stack[0];
            if(startState==="#tmp"){
                stack.shift();
                startState=stack.shift();
            }
        }else
            varstack=[];

        varcurrentState=startState||"start";
        varstate=this.states[currentState];
        if(!state){
            currentState="start";
            state=this.states[currentState];
        }
        varmapping=this.matchMappings[currentState];
        varre=this.regExps[currentState];
        re.lastIndex=0;

        varmatch,tokens=[];
        varlastIndex=0;
        varmatchAttempts=0;

        vartoken={type:null,value:""};

        while(match=re.exec(line)){
            vartype=mapping.defaultToken;
            varrule=null;
            varvalue=match[0];
            varindex=re.lastIndex;

            if(index-value.length>lastIndex){
                varskipped=line.substring(lastIndex,index-value.length);
                if(token.type==type){
                    token.value+=skipped;
                }else{
                    if(token.type)
                        tokens.push(token);
                    token={type:type,value:skipped};
                }
            }

            for(vari=0;i<match.length-2;i++){
                if(match[i+1]===undefined)
                    continue;

                rule=state[mapping[i]];

                if(rule.onMatch)
                    type=rule.onMatch(value,currentState,stack,line);
                else
                    type=rule.token;

                if(rule.next){
                    if(typeofrule.next=="string"){
                        currentState=rule.next;
                    }else{
                        currentState=rule.next(currentState,stack);
                    }
                    
                    state=this.states[currentState];
                    if(!state){
                        this.reportError("statedoesn'texist",currentState);
                        currentState="start";
                        state=this.states[currentState];
                    }
                    mapping=this.matchMappings[currentState];
                    lastIndex=index;
                    re=this.regExps[currentState];
                    re.lastIndex=index;
                }
                if(rule.consumeLineEnd)
                    lastIndex=index;
                break;
            }

            if(value){
                if(typeoftype==="string"){
                    if((!rule||rule.merge!==false)&&token.type===type){
                        token.value+=value;
                    }else{
                        if(token.type)
                            tokens.push(token);
                        token={type:type,value:value};
                    }
                }elseif(type){
                    if(token.type)
                        tokens.push(token);
                    token={type:null,value:""};
                    for(vari=0;i<type.length;i++)
                        tokens.push(type[i]);
                }
            }

            if(lastIndex==line.length)
                break;

            lastIndex=index;

            if(matchAttempts++>MAX_TOKEN_COUNT){
                if(matchAttempts>2*line.length){
                    this.reportError("infiniteloopwithinacetokenizer",{
                        startState:startState,
                        line:line
                    });
                }
                while(lastIndex<line.length){
                    if(token.type)
                        tokens.push(token);
                    token={
                        value:line.substring(lastIndex,lastIndex+=2000),
                        type:"overflow"
                    };
                }
                currentState="start";
                stack=[];
                break;
            }
        }

        if(token.type)
            tokens.push(token);
        
        if(stack.length>1){
            if(stack[0]!==currentState)
                stack.unshift("#tmp",currentState);
        }
        return{
            tokens:tokens,
            state:stack.length?stack:currentState
        };
    };
    
    this.reportError=config.reportError;
    
}).call(Tokenizer.prototype);

exports.Tokenizer=Tokenizer;
});

define("ace/mode/text_highlight_rules",["require","exports","module","ace/lib/lang"],function(require,exports,module){
"usestrict";

varlang=require("../lib/lang");

varTextHighlightRules=function(){

    this.$rules={
        "start":[{
            token:"empty_line",
            regex:'^$'
        },{
            defaultToken:"text"
        }]
    };
};

(function(){

    this.addRules=function(rules,prefix){
        if(!prefix){
            for(varkeyinrules)
                this.$rules[key]=rules[key];
            return;
        }
        for(varkeyinrules){
            varstate=rules[key];
            for(vari=0;i<state.length;i++){
                varrule=state[i];
                if(rule.next||rule.onMatch){
                    if(typeofrule.next=="string"){
                        if(rule.next.indexOf(prefix)!==0)
                            rule.next=prefix+rule.next;
                    }
                    if(rule.nextState&&rule.nextState.indexOf(prefix)!==0)
                        rule.nextState=prefix+rule.nextState;
                }
            }
            this.$rules[prefix+key]=state;
        }
    };

    this.getRules=function(){
        returnthis.$rules;
    };

    this.embedRules=function(HighlightRules,prefix,escapeRules,states,append){
        varembedRules=typeofHighlightRules=="function"
            ?newHighlightRules().getRules()
            :HighlightRules;
        if(states){
            for(vari=0;i<states.length;i++)
                states[i]=prefix+states[i];
        }else{
            states=[];
            for(varkeyinembedRules)
                states.push(prefix+key);
        }

        this.addRules(embedRules,prefix);

        if(escapeRules){
            varaddRules=Array.prototype[append?"push":"unshift"];
            for(vari=0;i<states.length;i++)
                addRules.apply(this.$rules[states[i]],lang.deepCopy(escapeRules));
        }

        if(!this.$embeds)
            this.$embeds=[];
        this.$embeds.push(prefix);
    };

    this.getEmbeds=function(){
        returnthis.$embeds;
    };

    varpushState=function(currentState,stack){
        if(currentState!="start"||stack.length)
            stack.unshift(this.nextState,currentState);
        returnthis.nextState;
    };
    varpopState=function(currentState,stack){
        stack.shift();
        returnstack.shift()||"start";
    };

    this.normalizeRules=function(){
        varid=0;
        varrules=this.$rules;
        functionprocessState(key){
            varstate=rules[key];
            state.processed=true;
            for(vari=0;i<state.length;i++){
                varrule=state[i];
                vartoInsert=null;
                if(Array.isArray(rule)){
                    toInsert=rule;
                    rule={};
                }
                if(!rule.regex&&rule.start){
                    rule.regex=rule.start;
                    if(!rule.next)
                        rule.next=[];
                    rule.next.push({
                        defaultToken:rule.token
                    },{
                        token:rule.token+".end",
                        regex:rule.end||rule.start,
                        next:"pop"
                    });
                    rule.token=rule.token+".start";
                    rule.push=true;
                }
                varnext=rule.next||rule.push;
                if(next&&Array.isArray(next)){
                    varstateName=rule.stateName;
                    if(!stateName) {
                        stateName=rule.token;
                        if(typeofstateName!="string")
                            stateName=stateName[0]||"";
                        if(rules[stateName])
                            stateName+=id++;
                    }
                    rules[stateName]=next;
                    rule.next=stateName;
                    processState(stateName);
                }elseif(next=="pop"){
                    rule.next=popState;
                }

                if(rule.push){
                    rule.nextState=rule.next||rule.push;
                    rule.next=pushState;
                    deleterule.push;
                }

                if(rule.rules){
                    for(varrinrule.rules){
                        if(rules[r]){
                            if(rules[r].push)
                                rules[r].push.apply(rules[r],rule.rules[r]);
                        }else{
                            rules[r]=rule.rules[r];
                        }
                    }
                }
                varincludeName=typeofrule=="string"?rule:rule.include;
                if(includeName){
                    if(Array.isArray(includeName))
                        toInsert=includeName.map(function(x){returnrules[x];});
                    else
                        toInsert=rules[includeName];
                }

                if(toInsert){
                    varargs=[i,1].concat(toInsert);
                    if(rule.noEscape)
                        args=args.filter(function(x){return!x.next;});
                    state.splice.apply(state,args);
                    i--;
                }
                
                if(rule.keywordMap){
                    rule.token=this.createKeywordMapper(
                        rule.keywordMap,rule.defaultToken||"text",rule.caseInsensitive
                    );
                    deleterule.defaultToken;
                }
            }
        }
        Object.keys(rules).forEach(processState,this);
    };

    this.createKeywordMapper=function(map,defaultToken,ignoreCase,splitChar){
        varkeywords=Object.create(null);
        Object.keys(map).forEach(function(className){
            vara=map[className];
            if(ignoreCase)
                a=a.toLowerCase();
            varlist=a.split(splitChar||"|");
            for(vari=list.length;i--;)
                keywords[list[i]]=className;
        });
        if(Object.getPrototypeOf(keywords)){
            keywords.__proto__=null;
        }
        this.$keywordList=Object.keys(keywords);
        map=null;
        returnignoreCase
            ?function(value){returnkeywords[value.toLowerCase()]||defaultToken;}
            :function(value){returnkeywords[value]||defaultToken;};
    };

    this.getKeywords=function(){
        returnthis.$keywords;
    };

}).call(TextHighlightRules.prototype);

exports.TextHighlightRules=TextHighlightRules;
});

define("ace/mode/behaviour",["require","exports","module"],function(require,exports,module){
"usestrict";

varBehaviour=function(){
   this.$behaviours={};
};

(function(){

    this.add=function(name,action,callback){
        switch(undefined){
          casethis.$behaviours:
              this.$behaviours={};
          casethis.$behaviours[name]:
              this.$behaviours[name]={};
        }
        this.$behaviours[name][action]=callback;
    };
    
    this.addBehaviours=function(behaviours){
        for(varkeyinbehaviours){
            for(varactioninbehaviours[key]){
                this.add(key,action,behaviours[key][action]);
            }
        }
    };
    
    this.remove=function(name){
        if(this.$behaviours&&this.$behaviours[name]){
            deletethis.$behaviours[name];
        }
    };
    
    this.inherit=function(mode,filter){
        if(typeofmode==="function"){
            varbehaviours=newmode().getBehaviours(filter);
        }else{
            varbehaviours=mode.getBehaviours(filter);
        }
        this.addBehaviours(behaviours);
    };
    
    this.getBehaviours=function(filter){
        if(!filter){
            returnthis.$behaviours;
        }else{
            varret={};
            for(vari=0;i<filter.length;i++){
                if(this.$behaviours[filter[i]]){
                    ret[filter[i]]=this.$behaviours[filter[i]];
                }
            }
            returnret;
        }
    };

}).call(Behaviour.prototype);

exports.Behaviour=Behaviour;
});

define("ace/token_iterator",["require","exports","module","ace/range"],function(require,exports,module){
"usestrict";

varRange=require("./range").Range;
varTokenIterator=function(session,initialRow,initialColumn){
    this.$session=session;
    this.$row=initialRow;
    this.$rowTokens=session.getTokens(initialRow);

    vartoken=session.getTokenAt(initialRow,initialColumn);
    this.$tokenIndex=token?token.index:-1;
};

(function(){
    this.stepBackward=function(){
        this.$tokenIndex-=1;
        
        while(this.$tokenIndex<0){
            this.$row-=1;
            if(this.$row<0){
                this.$row=0;
                returnnull;
            }
                
            this.$rowTokens=this.$session.getTokens(this.$row);
            this.$tokenIndex=this.$rowTokens.length-1;
        }
            
        returnthis.$rowTokens[this.$tokenIndex];
    };  
    this.stepForward=function(){
        this.$tokenIndex+=1;
        varrowCount;
        while(this.$tokenIndex>=this.$rowTokens.length){
            this.$row+=1;
            if(!rowCount)
                rowCount=this.$session.getLength();
            if(this.$row>=rowCount){
                this.$row=rowCount-1;
                returnnull;
            }

            this.$rowTokens=this.$session.getTokens(this.$row);
            this.$tokenIndex=0;
        }
            
        returnthis.$rowTokens[this.$tokenIndex];
    };     
    this.getCurrentToken=function(){
        returnthis.$rowTokens[this.$tokenIndex];
    };     
    this.getCurrentTokenRow=function(){
        returnthis.$row;
    };    
    this.getCurrentTokenColumn=function(){
        varrowTokens=this.$rowTokens;
        vartokenIndex=this.$tokenIndex;
        varcolumn=rowTokens[tokenIndex].start;
        if(column!==undefined)
            returncolumn;
            
        column=0;
        while(tokenIndex>0){
            tokenIndex-=1;
            column+=rowTokens[tokenIndex].value.length;
        }
        
        returncolumn; 
    };
    this.getCurrentTokenPosition=function(){
        return{row:this.$row,column:this.getCurrentTokenColumn()};
    };
    this.getCurrentTokenRange=function(){
        vartoken=this.$rowTokens[this.$tokenIndex];
        varcolumn=this.getCurrentTokenColumn();
        returnnewRange(this.$row,column,this.$row,column+token.value.length);
    };
    
}).call(TokenIterator.prototype);

exports.TokenIterator=TokenIterator;
});

define("ace/mode/behaviour/cstyle",["require","exports","module","ace/lib/oop","ace/mode/behaviour","ace/token_iterator","ace/lib/lang"],function(require,exports,module){
"usestrict";

varoop=require("../../lib/oop");
varBehaviour=require("../behaviour").Behaviour;
varTokenIterator=require("../../token_iterator").TokenIterator;
varlang=require("../../lib/lang");

varSAFE_INSERT_IN_TOKENS=
    ["text","paren.rparen","punctuation.operator"];
varSAFE_INSERT_BEFORE_TOKENS=
    ["text","paren.rparen","punctuation.operator","comment"];

varcontext;
varcontextCache={};
vardefaultQuotes={'"':'"',"'":"'"};

varinitContext=function(editor){
    varid=-1;
    if(editor.multiSelect){
        id=editor.selection.index;
        if(contextCache.rangeCount!=editor.multiSelect.rangeCount)
            contextCache={rangeCount:editor.multiSelect.rangeCount};
    }
    if(contextCache[id])
        returncontext=contextCache[id];
    context=contextCache[id]={
        autoInsertedBrackets:0,
        autoInsertedRow:-1,
        autoInsertedLineEnd:"",
        maybeInsertedBrackets:0,
        maybeInsertedRow:-1,
        maybeInsertedLineStart:"",
        maybeInsertedLineEnd:""
    };
};

vargetWrapped=function(selection,selected,opening,closing){
    varrowDiff=selection.end.row-selection.start.row;
    return{
        text:opening+selected+closing,
        selection:[
                0,
                selection.start.column+1,
                rowDiff,
                selection.end.column+(rowDiff?0:1)
            ]
    };
};

varCstyleBehaviour=function(options){
    this.add("braces","insertion",function(state,action,editor,session,text){
        varcursor=editor.getCursorPosition();
        varline=session.doc.getLine(cursor.row);
        if(text=='{'){
            initContext(editor);
            varselection=editor.getSelectionRange();
            varselected=session.doc.getTextRange(selection);
            if(selected!==""&&selected!=="{"&&editor.getWrapBehavioursEnabled()){
                returngetWrapped(selection,selected,'{','}');
            }elseif(CstyleBehaviour.isSaneInsertion(editor,session)){
                if(/[\]\}\)]/.test(line[cursor.column])||editor.inMultiSelectMode||options&&options.braces){
                    CstyleBehaviour.recordAutoInsert(editor,session,"}");
                    return{
                        text:'{}',
                        selection:[1,1]
                    };
                }else{
                    CstyleBehaviour.recordMaybeInsert(editor,session,"{");
                    return{
                        text:'{',
                        selection:[1,1]
                    };
                }
            }
        }elseif(text=='}'){
            initContext(editor);
            varrightChar=line.substring(cursor.column,cursor.column+1);
            if(rightChar=='}'){
                varmatching=session.$findOpeningBracket('}',{column:cursor.column+1,row:cursor.row});
                if(matching!==null&&CstyleBehaviour.isAutoInsertedClosing(cursor,line,text)){
                    CstyleBehaviour.popAutoInsertedClosing();
                    return{
                        text:'',
                        selection:[1,1]
                    };
                }
            }
        }elseif(text=="\n"||text=="\r\n"){
            initContext(editor);
            varclosing="";
            if(CstyleBehaviour.isMaybeInsertedClosing(cursor,line)){
                closing=lang.stringRepeat("}",context.maybeInsertedBrackets);
                CstyleBehaviour.clearMaybeInsertedClosing();
            }
            varrightChar=line.substring(cursor.column,cursor.column+1);
            if(rightChar==='}'){
                varopenBracePos=session.findMatchingBracket({row:cursor.row,column:cursor.column+1},'}');
                if(!openBracePos)
                     returnnull;
                varnext_indent=this.$getIndent(session.getLine(openBracePos.row));
            }elseif(closing){
                varnext_indent=this.$getIndent(line);
            }else{
                CstyleBehaviour.clearMaybeInsertedClosing();
                return;
            }
            varindent=next_indent+session.getTabString();

            return{
                text:'\n'+indent+'\n'+next_indent+closing,
                selection:[1,indent.length,1,indent.length]
            };
        }else{
            CstyleBehaviour.clearMaybeInsertedClosing();
        }
    });

    this.add("braces","deletion",function(state,action,editor,session,range){
        varselected=session.doc.getTextRange(range);
        if(!range.isMultiLine()&&selected=='{'){
            initContext(editor);
            varline=session.doc.getLine(range.start.row);
            varrightChar=line.substring(range.end.column,range.end.column+1);
            if(rightChar=='}'){
                range.end.column++;
                returnrange;
            }else{
                context.maybeInsertedBrackets--;
            }
        }
    });

    this.add("parens","insertion",function(state,action,editor,session,text){
        if(text=='('){
            initContext(editor);
            varselection=editor.getSelectionRange();
            varselected=session.doc.getTextRange(selection);
            if(selected!==""&&editor.getWrapBehavioursEnabled()){
                returngetWrapped(selection,selected,'(',')');
            }elseif(CstyleBehaviour.isSaneInsertion(editor,session)){
                CstyleBehaviour.recordAutoInsert(editor,session,")");
                return{
                    text:'()',
                    selection:[1,1]
                };
            }
        }elseif(text==')'){
            initContext(editor);
            varcursor=editor.getCursorPosition();
            varline=session.doc.getLine(cursor.row);
            varrightChar=line.substring(cursor.column,cursor.column+1);
            if(rightChar==')'){
                varmatching=session.$findOpeningBracket(')',{column:cursor.column+1,row:cursor.row});
                if(matching!==null&&CstyleBehaviour.isAutoInsertedClosing(cursor,line,text)){
                    CstyleBehaviour.popAutoInsertedClosing();
                    return{
                        text:'',
                        selection:[1,1]
                    };
                }
            }
        }
    });

    this.add("parens","deletion",function(state,action,editor,session,range){
        varselected=session.doc.getTextRange(range);
        if(!range.isMultiLine()&&selected=='('){
            initContext(editor);
            varline=session.doc.getLine(range.start.row);
            varrightChar=line.substring(range.start.column+1,range.start.column+2);
            if(rightChar==')'){
                range.end.column++;
                returnrange;
            }
        }
    });

    this.add("brackets","insertion",function(state,action,editor,session,text){
        if(text=='['){
            initContext(editor);
            varselection=editor.getSelectionRange();
            varselected=session.doc.getTextRange(selection);
            if(selected!==""&&editor.getWrapBehavioursEnabled()){
                returngetWrapped(selection,selected,'[',']');
            }elseif(CstyleBehaviour.isSaneInsertion(editor,session)){
                CstyleBehaviour.recordAutoInsert(editor,session,"]");
                return{
                    text:'[]',
                    selection:[1,1]
                };
            }
        }elseif(text==']'){
            initContext(editor);
            varcursor=editor.getCursorPosition();
            varline=session.doc.getLine(cursor.row);
            varrightChar=line.substring(cursor.column,cursor.column+1);
            if(rightChar==']'){
                varmatching=session.$findOpeningBracket(']',{column:cursor.column+1,row:cursor.row});
                if(matching!==null&&CstyleBehaviour.isAutoInsertedClosing(cursor,line,text)){
                    CstyleBehaviour.popAutoInsertedClosing();
                    return{
                        text:'',
                        selection:[1,1]
                    };
                }
            }
        }
    });

    this.add("brackets","deletion",function(state,action,editor,session,range){
        varselected=session.doc.getTextRange(range);
        if(!range.isMultiLine()&&selected=='['){
            initContext(editor);
            varline=session.doc.getLine(range.start.row);
            varrightChar=line.substring(range.start.column+1,range.start.column+2);
            if(rightChar==']'){
                range.end.column++;
                returnrange;
            }
        }
    });

    this.add("string_dquotes","insertion",function(state,action,editor,session,text){
        varquotes=session.$mode.$quotes||defaultQuotes;
        if(text.length==1&&quotes[text]){
            if(this.lineCommentStart&&this.lineCommentStart.indexOf(text)!=-1)
                return;
            initContext(editor);
            varquote=text;
            varselection=editor.getSelectionRange();
            varselected=session.doc.getTextRange(selection);
            if(selected!==""&&(selected.length!=1||!quotes[selected])&&editor.getWrapBehavioursEnabled()){
                returngetWrapped(selection,selected,quote,quote);
            }elseif(!selected){
                varcursor=editor.getCursorPosition();
                varline=session.doc.getLine(cursor.row);
                varleftChar=line.substring(cursor.column-1,cursor.column);
                varrightChar=line.substring(cursor.column,cursor.column+1);
                
                vartoken=session.getTokenAt(cursor.row,cursor.column);
                varrightToken=session.getTokenAt(cursor.row,cursor.column+1);
                if(leftChar=="\\"&&token&&/escape/.test(token.type))
                    returnnull;
                
                varstringBefore=token&&/string|escape/.test(token.type);
                varstringAfter=!rightToken||/string|escape/.test(rightToken.type);
                
                varpair;
                if(rightChar==quote){
                    pair=stringBefore!==stringAfter;
                    if(pair&&/string\.end/.test(rightToken.type))
                        pair=false;
                }else{
                    if(stringBefore&&!stringAfter)
                        returnnull;//wrapstringwithdifferentquote
                    if(stringBefore&&stringAfter)
                        returnnull;//donotpairquotesinsidestrings
                    varwordRe=session.$mode.tokenRe;
                    wordRe.lastIndex=0;
                    varisWordBefore=wordRe.test(leftChar);
                    wordRe.lastIndex=0;
                    varisWordAfter=wordRe.test(leftChar);
                    if(isWordBefore||isWordAfter)
                        returnnull;//beforeorafteralphanumeric
                    if(rightChar&&!/[\s;,.})\]\\]/.test(rightChar))
                        returnnull;//thereisrightCharanditisn'tclosing
                    pair=true;
                }
                return{
                    text:pair?quote+quote:"",
                    selection:[1,1]
                };
            }
        }
    });

    this.add("string_dquotes","deletion",function(state,action,editor,session,range){
        varselected=session.doc.getTextRange(range);
        if(!range.isMultiLine()&&(selected=='"'||selected=="'")){
            initContext(editor);
            varline=session.doc.getLine(range.start.row);
            varrightChar=line.substring(range.start.column+1,range.start.column+2);
            if(rightChar==selected){
                range.end.column++;
                returnrange;
            }
        }
    });

};

    
CstyleBehaviour.isSaneInsertion=function(editor,session){
    varcursor=editor.getCursorPosition();
    variterator=newTokenIterator(session,cursor.row,cursor.column);
    if(!this.$matchTokenType(iterator.getCurrentToken()||"text",SAFE_INSERT_IN_TOKENS)){
        variterator2=newTokenIterator(session,cursor.row,cursor.column+1);
        if(!this.$matchTokenType(iterator2.getCurrentToken()||"text",SAFE_INSERT_IN_TOKENS))
            returnfalse;
    }
    iterator.stepForward();
    returniterator.getCurrentTokenRow()!==cursor.row||
        this.$matchTokenType(iterator.getCurrentToken()||"text",SAFE_INSERT_BEFORE_TOKENS);
};

CstyleBehaviour.$matchTokenType=function(token,types){
    returntypes.indexOf(token.type||token)>-1;
};

CstyleBehaviour.recordAutoInsert=function(editor,session,bracket){
    varcursor=editor.getCursorPosition();
    varline=session.doc.getLine(cursor.row);
    if(!this.isAutoInsertedClosing(cursor,line,context.autoInsertedLineEnd[0]))
        context.autoInsertedBrackets=0;
    context.autoInsertedRow=cursor.row;
    context.autoInsertedLineEnd=bracket+line.substr(cursor.column);
    context.autoInsertedBrackets++;
};

CstyleBehaviour.recordMaybeInsert=function(editor,session,bracket){
    varcursor=editor.getCursorPosition();
    varline=session.doc.getLine(cursor.row);
    if(!this.isMaybeInsertedClosing(cursor,line))
        context.maybeInsertedBrackets=0;
    context.maybeInsertedRow=cursor.row;
    context.maybeInsertedLineStart=line.substr(0,cursor.column)+bracket;
    context.maybeInsertedLineEnd=line.substr(cursor.column);
    context.maybeInsertedBrackets++;
};

CstyleBehaviour.isAutoInsertedClosing=function(cursor,line,bracket){
    returncontext.autoInsertedBrackets>0&&
        cursor.row===context.autoInsertedRow&&
        bracket===context.autoInsertedLineEnd[0]&&
        line.substr(cursor.column)===context.autoInsertedLineEnd;
};

CstyleBehaviour.isMaybeInsertedClosing=function(cursor,line){
    returncontext.maybeInsertedBrackets>0&&
        cursor.row===context.maybeInsertedRow&&
        line.substr(cursor.column)===context.maybeInsertedLineEnd&&
        line.substr(0,cursor.column)==context.maybeInsertedLineStart;
};

CstyleBehaviour.popAutoInsertedClosing=function(){
    context.autoInsertedLineEnd=context.autoInsertedLineEnd.substr(1);
    context.autoInsertedBrackets--;
};

CstyleBehaviour.clearMaybeInsertedClosing=function(){
    if(context){
        context.maybeInsertedBrackets=0;
        context.maybeInsertedRow=-1;
    }
};



oop.inherits(CstyleBehaviour,Behaviour);

exports.CstyleBehaviour=CstyleBehaviour;
});

define("ace/unicode",["require","exports","module"],function(require,exports,module){
"usestrict";
varwordChars=[48,9,8,25,5,0,2,25,48,0,11,0,5,0,6,22,2,30,2,457,5,11,15,4,8,0,2,0,18,116,2,1,3,3,9,0,2,2,2,0,2,19,2,82,2,138,2,4,3,155,12,37,3,0,8,38,10,44,2,0,2,1,2,1,2,0,9,26,6,2,30,10,7,61,2,9,5,101,2,7,3,9,2,18,3,0,17,58,3,100,15,53,5,0,6,45,211,57,3,18,2,5,3,11,3,9,2,1,7,6,2,2,2,7,3,1,3,21,2,6,2,0,4,3,3,8,3,1,3,3,9,0,5,1,2,4,3,11,16,2,2,5,5,1,3,21,2,6,2,1,2,1,2,1,3,0,2,4,5,1,3,2,4,0,8,3,2,0,8,15,12,2,2,8,2,2,2,21,2,6,2,1,2,4,3,9,2,2,2,2,3,0,16,3,3,9,18,2,2,7,3,1,3,21,2,6,2,1,2,4,3,8,3,1,3,2,9,1,5,1,2,4,3,9,2,0,17,1,2,5,4,2,2,3,4,1,2,0,2,1,4,1,4,2,4,11,5,4,4,2,2,3,3,0,7,0,15,9,18,2,2,7,2,2,2,22,2,9,2,4,4,7,2,2,2,3,8,1,2,1,7,3,3,9,19,1,2,7,2,2,2,22,2,9,2,4,3,8,2,2,2,3,8,1,8,0,2,3,3,9,19,1,2,7,2,2,2,22,2,15,4,7,2,2,2,3,10,0,9,3,3,9,11,5,3,1,2,17,4,23,2,8,2,0,3,6,4,0,5,5,2,0,2,7,19,1,14,57,6,14,2,9,40,1,2,0,3,1,2,0,3,0,7,3,2,6,2,2,2,0,2,0,3,1,2,12,2,2,3,4,2,0,2,5,3,9,3,1,35,0,24,1,7,9,12,0,2,0,2,0,5,9,2,35,5,19,2,5,5,7,2,35,10,0,58,73,7,77,3,37,11,42,2,0,4,328,2,3,3,6,2,0,2,3,3,40,2,3,3,32,2,3,3,6,2,0,2,3,3,14,2,56,2,3,3,66,5,0,33,15,17,84,13,619,3,16,2,25,6,74,22,12,2,6,12,20,12,19,13,12,2,2,2,1,13,51,3,29,4,0,5,1,3,9,34,2,3,9,7,87,9,42,6,69,11,28,4,11,5,11,11,39,3,4,12,43,5,25,7,10,38,27,5,62,2,28,3,10,7,9,14,0,89,75,5,9,18,8,13,42,4,11,71,55,9,9,4,48,83,2,2,30,14,230,23,280,3,5,3,37,3,5,3,7,2,0,2,0,2,0,2,30,3,52,2,6,2,0,4,2,2,6,4,3,3,5,5,12,6,2,2,6,67,1,20,0,29,0,14,0,17,4,60,12,5,0,4,11,18,0,5,0,3,9,2,0,4,4,7,0,2,0,2,0,2,3,2,10,3,3,6,4,5,0,53,1,2684,46,2,46,2,132,7,6,15,37,11,53,10,0,17,22,10,6,2,6,2,6,2,6,2,6,2,6,2,6,2,6,2,31,48,0,470,1,36,5,2,4,6,1,5,85,3,1,3,2,2,89,2,3,6,40,4,93,18,23,57,15,513,6581,75,20939,53,1164,68,45,3,268,4,27,21,31,3,13,13,1,2,24,9,69,11,1,38,8,3,102,3,1,111,44,25,51,13,68,12,9,7,23,4,0,5,45,3,35,13,28,4,64,15,10,39,54,10,13,3,9,7,22,4,1,5,66,25,2,227,42,2,1,3,9,7,11171,13,22,5,48,8453,301,3,61,3,105,39,6,13,4,6,11,2,12,2,4,2,0,2,1,2,1,2,107,34,362,19,63,3,53,41,11,5,15,17,6,13,1,25,2,33,4,2,134,20,9,8,25,5,0,2,25,12,88,4,5,3,5,3,5,3,2];

varcode=0;
varstr=[];
for(vari=0;i<wordChars.length;i+=2){
    str.push(code+=wordChars[i]);
    if(wordChars[i+1])
        str.push(45,code+=wordChars[i+1]);
}

exports.wordChars=String.fromCharCode.apply(null,str);

});

define("ace/mode/text",["require","exports","module","ace/tokenizer","ace/mode/text_highlight_rules","ace/mode/behaviour/cstyle","ace/unicode","ace/lib/lang","ace/token_iterator","ace/range"],function(require,exports,module){
"usestrict";

varTokenizer=require("../tokenizer").Tokenizer;
varTextHighlightRules=require("./text_highlight_rules").TextHighlightRules;
varCstyleBehaviour=require("./behaviour/cstyle").CstyleBehaviour;
varunicode=require("../unicode");
varlang=require("../lib/lang");
varTokenIterator=require("../token_iterator").TokenIterator;
varRange=require("../range").Range;

varMode=function(){
    this.HighlightRules=TextHighlightRules;
};

(function(){
    this.$defaultBehaviour=newCstyleBehaviour();

    this.tokenRe=newRegExp("^["+unicode.wordChars+"\\$_]+","g");

    this.nonTokenRe=newRegExp("^(?:[^"+unicode.wordChars+"\\$_]|\\s])+","g");

    this.getTokenizer=function(){
        if(!this.$tokenizer){
            this.$highlightRules=this.$highlightRules||newthis.HighlightRules(this.$highlightRuleConfig);
            this.$tokenizer=newTokenizer(this.$highlightRules.getRules());
        }
        returnthis.$tokenizer;
    };

    this.lineCommentStart="";
    this.blockComment="";

    this.toggleCommentLines=function(state,session,startRow,endRow){
        vardoc=session.doc;

        varignoreBlankLines=true;
        varshouldRemove=true;
        varminIndent=Infinity;
        vartabSize=session.getTabSize();
        varinsertAtTabStop=false;

        if(!this.lineCommentStart){
            if(!this.blockComment)
                returnfalse;
            varlineCommentStart=this.blockComment.start;
            varlineCommentEnd=this.blockComment.end;
            varregexpStart=newRegExp("^(\\s*)(?:"+lang.escapeRegExp(lineCommentStart)+")");
            varregexpEnd=newRegExp("(?:"+lang.escapeRegExp(lineCommentEnd)+")\\s*$");

            varcomment=function(line,i){
                if(testRemove(line,i))
                    return;
                if(!ignoreBlankLines||/\S/.test(line)){
                    doc.insertInLine({row:i,column:line.length},lineCommentEnd);
                    doc.insertInLine({row:i,column:minIndent},lineCommentStart);
                }
            };

            varuncomment=function(line,i){
                varm;
                if(m=line.match(regexpEnd))
                    doc.removeInLine(i,line.length-m[0].length,line.length);
                if(m=line.match(regexpStart))
                    doc.removeInLine(i,m[1].length,m[0].length);
            };

            vartestRemove=function(line,row){
                if(regexpStart.test(line))
                    returntrue;
                vartokens=session.getTokens(row);
                for(vari=0;i<tokens.length;i++){
                    if(tokens[i].type==="comment")
                        returntrue;
                }
            };
        }else{
            if(Array.isArray(this.lineCommentStart)){
                varregexpStart=this.lineCommentStart.map(lang.escapeRegExp).join("|");
                varlineCommentStart=this.lineCommentStart[0];
            }else{
                varregexpStart=lang.escapeRegExp(this.lineCommentStart);
                varlineCommentStart=this.lineCommentStart;
            }
            regexpStart=newRegExp("^(\\s*)(?:"+regexpStart+")?");
            
            insertAtTabStop=session.getUseSoftTabs();

            varuncomment=function(line,i){
                varm=line.match(regexpStart);
                if(!m)return;
                varstart=m[1].length,end=m[0].length;
                if(!shouldInsertSpace(line,start,end)&&m[0][end-1]=="")
                    end--;
                doc.removeInLine(i,start,end);
            };
            varcommentWithSpace=lineCommentStart+"";
            varcomment=function(line,i){
                if(!ignoreBlankLines||/\S/.test(line)){
                    if(shouldInsertSpace(line,minIndent,minIndent))
                        doc.insertInLine({row:i,column:minIndent},commentWithSpace);
                    else
                        doc.insertInLine({row:i,column:minIndent},lineCommentStart);
                }
            };
            vartestRemove=function(line,i){
                returnregexpStart.test(line);
            };
            
            varshouldInsertSpace=function(line,before,after){
                varspaces=0;
                while(before--&&line.charAt(before)=="")
                    spaces++;
                if(spaces%tabSize!=0)
                    returnfalse;
                varspaces=0;
                while(line.charAt(after++)=="")
                    spaces++;
                if(tabSize>2)
                    returnspaces%tabSize!=tabSize-1;
                else
                    returnspaces%tabSize==0;
            };
        }

        functioniter(fun){
            for(vari=startRow;i<=endRow;i++)
                fun(doc.getLine(i),i);
        }


        varminEmptyLength=Infinity;
        iter(function(line,i){
            varindent=line.search(/\S/);
            if(indent!==-1){
                if(indent<minIndent)
                    minIndent=indent;
                if(shouldRemove&&!testRemove(line,i))
                    shouldRemove=false;
            }elseif(minEmptyLength>line.length){
                minEmptyLength=line.length;
            }
        });

        if(minIndent==Infinity){
            minIndent=minEmptyLength;
            ignoreBlankLines=false;
            shouldRemove=false;
        }

        if(insertAtTabStop&&minIndent%tabSize!=0)
            minIndent=Math.floor(minIndent/tabSize)*tabSize;

        iter(shouldRemove?uncomment:comment);
    };

    this.toggleBlockComment=function(state,session,range,cursor){
        varcomment=this.blockComment;
        if(!comment)
            return;
        if(!comment.start&&comment[0])
            comment=comment[0];

        variterator=newTokenIterator(session,cursor.row,cursor.column);
        vartoken=iterator.getCurrentToken();

        varsel=session.selection;
        varinitialRange=session.selection.toOrientedRange();
        varstartRow,colDiff;

        if(token&&/comment/.test(token.type)){
            varstartRange,endRange;
            while(token&&/comment/.test(token.type)){
                vari=token.value.indexOf(comment.start);
                if(i!=-1){
                    varrow=iterator.getCurrentTokenRow();
                    varcolumn=iterator.getCurrentTokenColumn()+i;
                    startRange=newRange(row,column,row,column+comment.start.length);
                    break;
                }
                token=iterator.stepBackward();
            }

            variterator=newTokenIterator(session,cursor.row,cursor.column);
            vartoken=iterator.getCurrentToken();
            while(token&&/comment/.test(token.type)){
                vari=token.value.indexOf(comment.end);
                if(i!=-1){
                    varrow=iterator.getCurrentTokenRow();
                    varcolumn=iterator.getCurrentTokenColumn()+i;
                    endRange=newRange(row,column,row,column+comment.end.length);
                    break;
                }
                token=iterator.stepForward();
            }
            if(endRange)
                session.remove(endRange);
            if(startRange){
                session.remove(startRange);
                startRow=startRange.start.row;
                colDiff=-comment.start.length;
            }
        }else{
            colDiff=comment.start.length;
            startRow=range.start.row;
            session.insert(range.end,comment.end);
            session.insert(range.start,comment.start);
        }
        if(initialRange.start.row==startRow)
            initialRange.start.column+=colDiff;
        if(initialRange.end.row==startRow)
            initialRange.end.column+=colDiff;
        session.selection.fromOrientedRange(initialRange);
    };

    this.getNextLineIndent=function(state,line,tab){
        returnthis.$getIndent(line);
    };

    this.checkOutdent=function(state,line,input){
        returnfalse;
    };

    this.autoOutdent=function(state,doc,row){
    };

    this.$getIndent=function(line){
        returnline.match(/^\s*/)[0];
    };

    this.createWorker=function(session){
        returnnull;
    };

    this.createModeDelegates=function(mapping){
        this.$embeds=[];
        this.$modes={};
        for(variinmapping){
            if(mapping[i]){
                this.$embeds.push(i);
                this.$modes[i]=newmapping[i]();
            }
        }

        vardelegations=["toggleBlockComment","toggleCommentLines","getNextLineIndent",
            "checkOutdent","autoOutdent","transformAction","getCompletions"];

        for(vari=0;i<delegations.length;i++){
            (function(scope){
              varfunctionName=delegations[i];
              vardefaultHandler=scope[functionName];
              scope[delegations[i]]=function(){
                  returnthis.$delegator(functionName,arguments,defaultHandler);
              };
            }(this));
        }
    };

    this.$delegator=function(method,args,defaultHandler){
        varstate=args[0];
        if(typeofstate!="string")
            state=state[0];
        for(vari=0;i<this.$embeds.length;i++){
            if(!this.$modes[this.$embeds[i]])continue;

            varsplit=state.split(this.$embeds[i]);
            if(!split[0]&&split[1]){
                args[0]=split[1];
                varmode=this.$modes[this.$embeds[i]];
                returnmode[method].apply(mode,args);
            }
        }
        varret=defaultHandler.apply(this,args);
        returndefaultHandler?ret:undefined;
    };

    this.transformAction=function(state,action,editor,session,param){
        if(this.$behaviour){
            varbehaviours=this.$behaviour.getBehaviours();
            for(varkeyinbehaviours){
                if(behaviours[key][action]){
                    varret=behaviours[key][action].apply(this,arguments);
                    if(ret){
                        returnret;
                    }
                }
            }
        }
    };
    
    this.getKeywords=function(append){
        if(!this.completionKeywords){
            varrules=this.$tokenizer.rules;
            varcompletionKeywords=[];
            for(varruleinrules){
                varruleItr=rules[rule];
                for(varr=0,l=ruleItr.length;r<l;r++){
                    if(typeofruleItr[r].token==="string"){
                        if(/keyword|support|storage/.test(ruleItr[r].token))
                            completionKeywords.push(ruleItr[r].regex);
                    }
                    elseif(typeofruleItr[r].token==="object"){
                        for(vara=0,aLength=ruleItr[r].token.length;a<aLength;a++){   
                            if(/keyword|support|storage/.test(ruleItr[r].token[a])){
                                varrule=ruleItr[r].regex.match(/\(.+?\)/g)[a];
                                completionKeywords.push(rule.substr(1,rule.length-2));
                            }
                        }
                    }
                }
            }
            this.completionKeywords=completionKeywords;
        }
        if(!append)
            returnthis.$keywordList;
        returncompletionKeywords.concat(this.$keywordList||[]);
    };
    
    this.$createKeywordList=function(){
        if(!this.$highlightRules)
            this.getTokenizer();
        returnthis.$keywordList=this.$highlightRules.$keywordList||[];
    };

    this.getCompletions=function(state,session,pos,prefix){
        varkeywords=this.$keywordList||this.$createKeywordList();
        returnkeywords.map(function(word){
            return{
                name:word,
                value:word,
                score:0,
                meta:"keyword"
            };
        });
    };

    this.$id="ace/mode/text";
}).call(Mode.prototype);

exports.Mode=Mode;
});

define("ace/apply_delta",["require","exports","module"],function(require,exports,module){
"usestrict";

functionthrowDeltaError(delta,errorText){
    console.log("InvalidDelta:",delta);
    throw"InvalidDelta:"+errorText;
}

functionpositionInDocument(docLines,position){
    returnposition.row   >=0&&position.row   < docLines.length&&
           position.column>=0&&position.column<=docLines[position.row].length;
}

functionvalidateDelta(docLines,delta){
    if(delta.action!="insert"&&delta.action!="remove")
        throwDeltaError(delta,"delta.actionmustbe'insert'or'remove'");
    if(!(delta.linesinstanceofArray))
        throwDeltaError(delta,"delta.linesmustbeanArray");
    if(!delta.start||!delta.end)
       throwDeltaError(delta,"delta.start/endmustbeanpresent");
    varstart=delta.start;
    if(!positionInDocument(docLines,delta.start))
        throwDeltaError(delta,"delta.startmustbecontainedindocument");
    varend=delta.end;
    if(delta.action=="remove"&&!positionInDocument(docLines,end))
        throwDeltaError(delta,"delta.endmustcontainedindocumentfor'remove'actions");
    varnumRangeRows=end.row-start.row;
    varnumRangeLastLineChars=(end.column-(numRangeRows==0?start.column:0));
    if(numRangeRows!=delta.lines.length-1||delta.lines[numRangeRows].length!=numRangeLastLineChars)
        throwDeltaError(delta,"delta.rangemustmatchdeltalines");
}

exports.applyDelta=function(docLines,delta,doNotValidate){
    
    varrow=delta.start.row;
    varstartColumn=delta.start.column;
    varline=docLines[row]||"";
    switch(delta.action){
        case"insert":
            varlines=delta.lines;
            if(lines.length===1){
                docLines[row]=line.substring(0,startColumn)+delta.lines[0]+line.substring(startColumn);
            }else{
                varargs=[row,1].concat(delta.lines);
                docLines.splice.apply(docLines,args);
                docLines[row]=line.substring(0,startColumn)+docLines[row];
                docLines[row+delta.lines.length-1]+=line.substring(startColumn);
            }
            break;
        case"remove":
            varendColumn=delta.end.column;
            varendRow=delta.end.row;
            if(row===endRow){
                docLines[row]=line.substring(0,startColumn)+line.substring(endColumn);
            }else{
                docLines.splice(
                    row,endRow-row+1,
                    line.substring(0,startColumn)+docLines[endRow].substring(endColumn)
                );
            }
            break;
    }
};
});

define("ace/anchor",["require","exports","module","ace/lib/oop","ace/lib/event_emitter"],function(require,exports,module){
"usestrict";

varoop=require("./lib/oop");
varEventEmitter=require("./lib/event_emitter").EventEmitter;

varAnchor=exports.Anchor=function(doc,row,column){
    this.$onChange=this.onChange.bind(this);
    this.attach(doc);
    
    if(typeofcolumn=="undefined")
        this.setPosition(row.row,row.column);
    else
        this.setPosition(row,column);
};

(function(){

    oop.implement(this,EventEmitter);
    this.getPosition=function(){
        returnthis.$clipPositionToDocument(this.row,this.column);
    };
    this.getDocument=function(){
        returnthis.document;
    };
    this.$insertRight=false;
    this.onChange=function(delta){
        if(delta.start.row==delta.end.row&&delta.start.row!=this.row)
            return;

        if(delta.start.row>this.row)
            return;
            
        varpoint=$getTransformedPoint(delta,{row:this.row,column:this.column},this.$insertRight);
        this.setPosition(point.row,point.column,true);
    };
    
    function$pointsInOrder(point1,point2,equalPointsInOrder){
        varbColIsAfter=equalPointsInOrder?point1.column<=point2.column:point1.column<point2.column;
        return(point1.row<point2.row)||(point1.row==point2.row&&bColIsAfter);
    }
            
    function$getTransformedPoint(delta,point,moveIfEqual){
        vardeltaIsInsert=delta.action=="insert";
        vardeltaRowShift=(deltaIsInsert?1:-1)*(delta.end.row   -delta.start.row);
        vardeltaColShift=(deltaIsInsert?1:-1)*(delta.end.column-delta.start.column);
        vardeltaStart=delta.start;
        vardeltaEnd=deltaIsInsert?deltaStart:delta.end;//Collapseinsertrange.
        if($pointsInOrder(point,deltaStart,moveIfEqual)){
            return{
                row:point.row,
                column:point.column
            };
        }
        if($pointsInOrder(deltaEnd,point,!moveIfEqual)){
            return{
                row:point.row+deltaRowShift,
                column:point.column+(point.row==deltaEnd.row?deltaColShift:0)
            };
        }
        
        return{
            row:deltaStart.row,
            column:deltaStart.column
        };
    }
    this.setPosition=function(row,column,noClip){
        varpos;
        if(noClip){
            pos={
                row:row,
                column:column
            };
        }else{
            pos=this.$clipPositionToDocument(row,column);
        }

        if(this.row==pos.row&&this.column==pos.column)
            return;

        varold={
            row:this.row,
            column:this.column
        };

        this.row=pos.row;
        this.column=pos.column;
        this._signal("change",{
            old:old,
            value:pos
        });
    };
    this.detach=function(){
        this.document.removeEventListener("change",this.$onChange);
    };
    this.attach=function(doc){
        this.document=doc||this.document;
        this.document.on("change",this.$onChange);
    };
    this.$clipPositionToDocument=function(row,column){
        varpos={};

        if(row>=this.document.getLength()){
            pos.row=Math.max(0,this.document.getLength()-1);
            pos.column=this.document.getLine(pos.row).length;
        }
        elseif(row<0){
            pos.row=0;
            pos.column=0;
        }
        else{
            pos.row=row;
            pos.column=Math.min(this.document.getLine(pos.row).length,Math.max(0,column));
        }

        if(column<0)
            pos.column=0;

        returnpos;
    };

}).call(Anchor.prototype);

});

define("ace/document",["require","exports","module","ace/lib/oop","ace/apply_delta","ace/lib/event_emitter","ace/range","ace/anchor"],function(require,exports,module){
"usestrict";

varoop=require("./lib/oop");
varapplyDelta=require("./apply_delta").applyDelta;
varEventEmitter=require("./lib/event_emitter").EventEmitter;
varRange=require("./range").Range;
varAnchor=require("./anchor").Anchor;

varDocument=function(textOrLines){
    this.$lines=[""];
    if(textOrLines.length===0){
        this.$lines=[""];
    }elseif(Array.isArray(textOrLines)){
        this.insertMergedLines({row:0,column:0},textOrLines);
    }else{
        this.insert({row:0,column:0},textOrLines);
    }
};

(function(){

    oop.implement(this,EventEmitter);
    this.setValue=function(text){
        varlen=this.getLength()-1;
        this.remove(newRange(0,0,len,this.getLine(len).length));
        this.insert({row:0,column:0},text);
    };
    this.getValue=function(){
        returnthis.getAllLines().join(this.getNewLineCharacter());
    };
    this.createAnchor=function(row,column){
        returnnewAnchor(this,row,column);
    };
    if("aaa".split(/a/).length===0){
        this.$split=function(text){
            returntext.replace(/\r\n|\r/g,"\n").split("\n");
        };
    }else{
        this.$split=function(text){
            returntext.split(/\r\n|\r|\n/);
        };
    }


    this.$detectNewLine=function(text){
        varmatch=text.match(/^.*?(\r\n|\r|\n)/m);
        this.$autoNewLine=match?match[1]:"\n";
        this._signal("changeNewLineMode");
    };
    this.getNewLineCharacter=function(){
        switch(this.$newLineMode){
          case"windows":
            return"\r\n";
          case"unix":
            return"\n";
          default:
            returnthis.$autoNewLine||"\n";
        }
    };

    this.$autoNewLine="";
    this.$newLineMode="auto";
    this.setNewLineMode=function(newLineMode){
        if(this.$newLineMode===newLineMode)
            return;

        this.$newLineMode=newLineMode;
        this._signal("changeNewLineMode");
    };
    this.getNewLineMode=function(){
        returnthis.$newLineMode;
    };
    this.isNewLine=function(text){
        return(text=="\r\n"||text=="\r"||text=="\n");
    };
    this.getLine=function(row){
        returnthis.$lines[row]||"";
    };
    this.getLines=function(firstRow,lastRow){
        returnthis.$lines.slice(firstRow,lastRow+1);
    };
    this.getAllLines=function(){
        returnthis.getLines(0,this.getLength());
    };
    this.getLength=function(){
        returnthis.$lines.length;
    };
    this.getTextRange=function(range){
        returnthis.getLinesForRange(range).join(this.getNewLineCharacter());
    };
    this.getLinesForRange=function(range){
        varlines;
        if(range.start.row===range.end.row){
            lines=[this.getLine(range.start.row).substring(range.start.column,range.end.column)];
        }else{
            lines=this.getLines(range.start.row,range.end.row);
            lines[0]=(lines[0]||"").substring(range.start.column);
            varl=lines.length-1;
            if(range.end.row-range.start.row==l)
                lines[l]=lines[l].substring(0,range.end.column);
        }
        returnlines;
    };
    this.insertLines=function(row,lines){
        console.warn("Useofdocument.insertLinesisdeprecated.UsetheinsertFullLinesmethodinstead.");
        returnthis.insertFullLines(row,lines);
    };
    this.removeLines=function(firstRow,lastRow){
        console.warn("Useofdocument.removeLinesisdeprecated.UsetheremoveFullLinesmethodinstead.");
        returnthis.removeFullLines(firstRow,lastRow);
    };
    this.insertNewLine=function(position){
        console.warn("Useofdocument.insertNewLineisdeprecated.UseinsertMergedLines(position,['',''])instead.");
        returnthis.insertMergedLines(position,["",""]);
    };
    this.insert=function(position,text){
        if(this.getLength()<=1)
            this.$detectNewLine(text);
        
        returnthis.insertMergedLines(position,this.$split(text));
    };
    this.insertInLine=function(position,text){
        varstart=this.clippedPos(position.row,position.column);
        varend=this.pos(position.row,position.column+text.length);
        
        this.applyDelta({
            start:start,
            end:end,
            action:"insert",
            lines:[text]
        },true);
        
        returnthis.clonePos(end);
    };
    
    this.clippedPos=function(row,column){
        varlength=this.getLength();
        if(row===undefined){
            row=length;
        }elseif(row<0){
            row=0;
        }elseif(row>=length){
            row=length-1;
            column=undefined;
        }
        varline=this.getLine(row);
        if(column==undefined)
            column=line.length;
        column=Math.min(Math.max(column,0),line.length);
        return{row:row,column:column};
    };
    
    this.clonePos=function(pos){
        return{row:pos.row,column:pos.column};
    };
    
    this.pos=function(row,column){
        return{row:row,column:column};
    };
    
    this.$clipPosition=function(position){
        varlength=this.getLength();
        if(position.row>=length){
            position.row=Math.max(0,length-1);
            position.column=this.getLine(length-1).length;
        }else{
            position.row=Math.max(0,position.row);
            position.column=Math.min(Math.max(position.column,0),this.getLine(position.row).length);
        }
        returnposition;
    };
    this.insertFullLines=function(row,lines){
        row=Math.min(Math.max(row,0),this.getLength());
        varcolumn=0;
        if(row<this.getLength()){
            lines=lines.concat([""]);
            column=0;
        }else{
            lines=[""].concat(lines);
            row--;
            column=this.$lines[row].length;
        }
        this.insertMergedLines({row:row,column:column},lines);
    };   
    this.insertMergedLines=function(position,lines){
        varstart=this.clippedPos(position.row,position.column);
        varend={
            row:start.row+lines.length-1,
            column:(lines.length==1?start.column:0)+lines[lines.length-1].length
        };
        
        this.applyDelta({
            start:start,
            end:end,
            action:"insert",
            lines:lines
        });
        
        returnthis.clonePos(end);
    };
    this.remove=function(range){
        varstart=this.clippedPos(range.start.row,range.start.column);
        varend=this.clippedPos(range.end.row,range.end.column);
        this.applyDelta({
            start:start,
            end:end,
            action:"remove",
            lines:this.getLinesForRange({start:start,end:end})
        });
        returnthis.clonePos(start);
    };
    this.removeInLine=function(row,startColumn,endColumn){
        varstart=this.clippedPos(row,startColumn);
        varend=this.clippedPos(row,endColumn);
        
        this.applyDelta({
            start:start,
            end:end,
            action:"remove",
            lines:this.getLinesForRange({start:start,end:end})
        },true);
        
        returnthis.clonePos(start);
    };
    this.removeFullLines=function(firstRow,lastRow){
        firstRow=Math.min(Math.max(0,firstRow),this.getLength()-1);
        lastRow =Math.min(Math.max(0,lastRow),this.getLength()-1);
        vardeleteFirstNewLine=lastRow==this.getLength()-1&&firstRow>0;
        vardeleteLastNewLine =lastRow <this.getLength()-1;
        varstartRow=(deleteFirstNewLine?firstRow-1                 :firstRow                   );
        varstartCol=(deleteFirstNewLine?this.getLine(startRow).length:0                          );
        varendRow  =(deleteLastNewLine ?lastRow+1                  :lastRow                    );
        varendCol  =(deleteLastNewLine ?0                            :this.getLine(endRow).length);
        varrange=newRange(startRow,startCol,endRow,endCol);
        vardeletedLines=this.$lines.slice(firstRow,lastRow+1);
        
        this.applyDelta({
            start:range.start,
            end:range.end,
            action:"remove",
            lines:this.getLinesForRange(range)
        });
        returndeletedLines;
    };
    this.removeNewLine=function(row){
        if(row<this.getLength()-1&&row>=0){
            this.applyDelta({
                start:this.pos(row,this.getLine(row).length),
                end:this.pos(row+1,0),
                action:"remove",
                lines:["",""]
            });
        }
    };
    this.replace=function(range,text){
        if(!(rangeinstanceofRange))
            range=Range.fromPoints(range.start,range.end);
        if(text.length===0&&range.isEmpty())
            returnrange.start;
        if(text==this.getTextRange(range))
            returnrange.end;

        this.remove(range);
        varend;
        if(text){
            end=this.insert(range.start,text);
        }
        else{
            end=range.start;
        }
        
        returnend;
    };
    this.applyDeltas=function(deltas){
        for(vari=0;i<deltas.length;i++){
            this.applyDelta(deltas[i]);
        }
    };
    this.revertDeltas=function(deltas){
        for(vari=deltas.length-1;i>=0;i--){
            this.revertDelta(deltas[i]);
        }
    };
    this.applyDelta=function(delta,doNotValidate){
        varisInsert=delta.action=="insert";
        if(isInsert?delta.lines.length<=1&&!delta.lines[0]
            :!Range.comparePoints(delta.start,delta.end)){
            return;
        }
        
        if(isInsert&&delta.lines.length>20000)
            this.$splitAndapplyLargeDelta(delta,20000);
        applyDelta(this.$lines,delta,doNotValidate);
        this._signal("change",delta);
    };
    
    this.$splitAndapplyLargeDelta=function(delta,MAX){
        varlines=delta.lines;
        varl=lines.length;
        varrow=delta.start.row;
        varcolumn=delta.start.column;
        varfrom=0,to=0;
        do{
            from=to;
            to+=MAX-1;
            varchunk=lines.slice(from,to);
            if(to>l){
                delta.lines=chunk;
                delta.start.row=row+from;
                delta.start.column=column;
                break;
            }
            chunk.push("");
            this.applyDelta({
                start:this.pos(row+from,column),
                end:this.pos(row+to,column=0),
                action:delta.action,
                lines:chunk
            },true);
        }while(true);
    };
    this.revertDelta=function(delta){
        this.applyDelta({
            start:this.clonePos(delta.start),
            end:this.clonePos(delta.end),
            action:(delta.action=="insert"?"remove":"insert"),
            lines:delta.lines.slice()
        });
    };
    this.indexToPosition=function(index,startRow){
        varlines=this.$lines||this.getAllLines();
        varnewlineLength=this.getNewLineCharacter().length;
        for(vari=startRow||0,l=lines.length;i<l;i++){
            index-=lines[i].length+newlineLength;
            if(index<0)
                return{row:i,column:index+lines[i].length+newlineLength};
        }
        return{row:l-1,column:lines[l-1].length};
    };
    this.positionToIndex=function(pos,startRow){
        varlines=this.$lines||this.getAllLines();
        varnewlineLength=this.getNewLineCharacter().length;
        varindex=0;
        varrow=Math.min(pos.row,lines.length);
        for(vari=startRow||0;i<row;++i)
            index+=lines[i].length+newlineLength;

        returnindex+pos.column;
    };

}).call(Document.prototype);

exports.Document=Document;
});

define("ace/background_tokenizer",["require","exports","module","ace/lib/oop","ace/lib/event_emitter"],function(require,exports,module){
"usestrict";

varoop=require("./lib/oop");
varEventEmitter=require("./lib/event_emitter").EventEmitter;

varBackgroundTokenizer=function(tokenizer,editor){
    this.running=false;
    this.lines=[];
    this.states=[];
    this.currentLine=0;
    this.tokenizer=tokenizer;

    varself=this;

    this.$worker=function(){
        if(!self.running){return;}

        varworkerStart=newDate();
        varcurrentLine=self.currentLine;
        varendLine=-1;
        vardoc=self.doc;

        varstartLine=currentLine;
        while(self.lines[currentLine])
            currentLine++;
        
        varlen=doc.getLength();
        varprocessedLines=0;
        self.running=false;
        while(currentLine<len){
            self.$tokenizeRow(currentLine);
            endLine=currentLine;
            do{
                currentLine++;
            }while(self.lines[currentLine]);
            processedLines++;
            if((processedLines%5===0)&&(newDate()-workerStart)>20){               
                self.running=setTimeout(self.$worker,20);
                break;
            }
        }
        self.currentLine=currentLine;
        
        if(endLine==-1)
            endLine=currentLine;
        
        if(startLine<=endLine)
            self.fireUpdateEvent(startLine,endLine);
    };
};

(function(){

    oop.implement(this,EventEmitter);
    this.setTokenizer=function(tokenizer){
        this.tokenizer=tokenizer;
        this.lines=[];
        this.states=[];

        this.start(0);
    };
    this.setDocument=function(doc){
        this.doc=doc;
        this.lines=[];
        this.states=[];

        this.stop();
    };
    this.fireUpdateEvent=function(firstRow,lastRow){
        vardata={
            first:firstRow,
            last:lastRow
        };
        this._signal("update",{data:data});
    };
    this.start=function(startRow){
        this.currentLine=Math.min(startRow||0,this.currentLine,this.doc.getLength());
        this.lines.splice(this.currentLine,this.lines.length);
        this.states.splice(this.currentLine,this.states.length);

        this.stop();
        this.running=setTimeout(this.$worker,700);
    };
    
    this.scheduleStart=function(){
        if(!this.running)
            this.running=setTimeout(this.$worker,700);
    };

    this.$updateOnChange=function(delta){
        varstartRow=delta.start.row;
        varlen=delta.end.row-startRow;

        if(len===0){
            this.lines[startRow]=null;
        }elseif(delta.action=="remove"){
            this.lines.splice(startRow,len+1,null);
            this.states.splice(startRow,len+1,null);
        }else{
            varargs=Array(len+1);
            args.unshift(startRow,1);
            this.lines.splice.apply(this.lines,args);
            this.states.splice.apply(this.states,args);
        }

        this.currentLine=Math.min(startRow,this.currentLine,this.doc.getLength());

        this.stop();
    };
    this.stop=function(){
        if(this.running)
            clearTimeout(this.running);
        this.running=false;
    };
    this.getTokens=function(row){
        returnthis.lines[row]||this.$tokenizeRow(row);
    };
    this.getState=function(row){
        if(this.currentLine==row)
            this.$tokenizeRow(row);
        returnthis.states[row]||"start";
    };

    this.$tokenizeRow=function(row){
        varline=this.doc.getLine(row);
        varstate=this.states[row-1];

        vardata=this.tokenizer.getLineTokens(line,state,row);

        if(this.states[row]+""!==data.state+""){
            this.states[row]=data.state;
            this.lines[row+1]=null;
            if(this.currentLine>row+1)
                this.currentLine=row+1;
        }elseif(this.currentLine==row){
            this.currentLine=row+1;
        }

        returnthis.lines[row]=data.tokens;
    };

}).call(BackgroundTokenizer.prototype);

exports.BackgroundTokenizer=BackgroundTokenizer;
});

define("ace/search_highlight",["require","exports","module","ace/lib/lang","ace/lib/oop","ace/range"],function(require,exports,module){
"usestrict";

varlang=require("./lib/lang");
varoop=require("./lib/oop");
varRange=require("./range").Range;

varSearchHighlight=function(regExp,clazz,type){
    this.setRegexp(regExp);
    this.clazz=clazz;
    this.type=type||"text";
};

(function(){
    this.MAX_RANGES=500;
    
    this.setRegexp=function(regExp){
        if(this.regExp+""==regExp+"")
            return;
        this.regExp=regExp;
        this.cache=[];
    };

    this.update=function(html,markerLayer,session,config){
        if(!this.regExp)
            return;
        varstart=config.firstRow,end=config.lastRow;

        for(vari=start;i<=end;i++){
            varranges=this.cache[i];
            if(ranges==null){
                ranges=lang.getMatchOffsets(session.getLine(i),this.regExp);
                if(ranges.length>this.MAX_RANGES)
                    ranges=ranges.slice(0,this.MAX_RANGES);
                ranges=ranges.map(function(match){
                    returnnewRange(i,match.offset,i,match.offset+match.length);
                });
                this.cache[i]=ranges.length?ranges:"";
            }

            for(varj=ranges.length;j--;){
                markerLayer.drawSingleLineMarker(
                    html,ranges[j].toScreenRange(session),this.clazz,config);
            }
        }
    };

}).call(SearchHighlight.prototype);

exports.SearchHighlight=SearchHighlight;
});

define("ace/edit_session/fold_line",["require","exports","module","ace/range"],function(require,exports,module){
"usestrict";

varRange=require("../range").Range;
functionFoldLine(foldData,folds){
    this.foldData=foldData;
    if(Array.isArray(folds)){
        this.folds=folds;
    }else{
        folds=this.folds=[folds];
    }

    varlast=folds[folds.length-1];
    this.range=newRange(folds[0].start.row,folds[0].start.column,
                           last.end.row,last.end.column);
    this.start=this.range.start;
    this.end  =this.range.end;

    this.folds.forEach(function(fold){
        fold.setFoldLine(this);
    },this);
}

(function(){
    this.shiftRow=function(shift){
        this.start.row+=shift;
        this.end.row+=shift;
        this.folds.forEach(function(fold){
            fold.start.row+=shift;
            fold.end.row+=shift;
        });
    };

    this.addFold=function(fold){
        if(fold.sameRow){
            if(fold.start.row<this.startRow||fold.endRow>this.endRow){
                thrownewError("Can'taddafoldtothisFoldLineasithasnoconnection");
            }
            this.folds.push(fold);
            this.folds.sort(function(a,b){
                return-a.range.compareEnd(b.start.row,b.start.column);
            });
            if(this.range.compareEnd(fold.start.row,fold.start.column)>0){
                this.end.row=fold.end.row;
                this.end.column= fold.end.column;
            }elseif(this.range.compareStart(fold.end.row,fold.end.column)<0){
                this.start.row=fold.start.row;
                this.start.column=fold.start.column;
            }
        }elseif(fold.start.row==this.end.row){
            this.folds.push(fold);
            this.end.row=fold.end.row;
            this.end.column=fold.end.column;
        }elseif(fold.end.row==this.start.row){
            this.folds.unshift(fold);
            this.start.row=fold.start.row;
            this.start.column=fold.start.column;
        }else{
            thrownewError("TryingtoaddfoldtoFoldRowthatdoesn'thaveamatchingrow");
        }
        fold.foldLine=this;
    };

    this.containsRow=function(row){
        returnrow>=this.start.row&&row<=this.end.row;
    };

    this.walk=function(callback,endRow,endColumn){
        varlastEnd=0,
            folds=this.folds,
            fold,
            cmp,stop,isNewRow=true;

        if(endRow==null){
            endRow=this.end.row;
            endColumn=this.end.column;
        }

        for(vari=0;i<folds.length;i++){
            fold=folds[i];

            cmp=fold.range.compareStart(endRow,endColumn);
            if(cmp==-1){
                callback(null,endRow,endColumn,lastEnd,isNewRow);
                return;
            }

            stop=callback(null,fold.start.row,fold.start.column,lastEnd,isNewRow);
            stop=!stop&&callback(fold.placeholder,fold.start.row,fold.start.column,lastEnd);
            if(stop||cmp===0){
                return;
            }
            isNewRow=!fold.sameRow;
            lastEnd=fold.end.column;
        }
        callback(null,endRow,endColumn,lastEnd,isNewRow);
    };

    this.getNextFoldTo=function(row,column){
        varfold,cmp;
        for(vari=0;i<this.folds.length;i++){
            fold=this.folds[i];
            cmp=fold.range.compareEnd(row,column);
            if(cmp==-1){
                return{
                    fold:fold,
                    kind:"after"
                };
            }elseif(cmp===0){
                return{
                    fold:fold,
                    kind:"inside"
                };
            }
        }
        returnnull;
    };

    this.addRemoveChars=function(row,column,len){
        varret=this.getNextFoldTo(row,column),
            fold,folds;
        if(ret){
            fold=ret.fold;
            if(ret.kind=="inside"
                &&fold.start.column!=column
                &&fold.start.row!=row)
            {
                window.console&&window.console.log(row,column,fold);
            }elseif(fold.start.row==row){
                folds=this.folds;
                vari=folds.indexOf(fold);
                if(i===0){
                    this.start.column+=len;
                }
                for(i;i<folds.length;i++){
                    fold=folds[i];
                    fold.start.column+=len;
                    if(!fold.sameRow){
                        return;
                    }
                    fold.end.column+=len;
                }
                this.end.column+=len;
            }
        }
    };

    this.split=function(row,column){
        varpos=this.getNextFoldTo(row,column);
        
        if(!pos||pos.kind=="inside")
            returnnull;
            
        varfold=pos.fold;
        varfolds=this.folds;
        varfoldData=this.foldData;
        
        vari=folds.indexOf(fold);
        varfoldBefore=folds[i-1];
        this.end.row=foldBefore.end.row;
        this.end.column=foldBefore.end.column;
        folds=folds.splice(i,folds.length-i);

        varnewFoldLine=newFoldLine(foldData,folds);
        foldData.splice(foldData.indexOf(this)+1,0,newFoldLine);
        returnnewFoldLine;
    };

    this.merge=function(foldLineNext){
        varfolds=foldLineNext.folds;
        for(vari=0;i<folds.length;i++){
            this.addFold(folds[i]);
        }
        varfoldData=this.foldData;
        foldData.splice(foldData.indexOf(foldLineNext),1);
    };

    this.toString=function(){
        varret=[this.range.toString()+":["];

        this.folds.forEach(function(fold){
            ret.push(" "+fold.toString());
        });
        ret.push("]");
        returnret.join("\n");
    };

    this.idxToPosition=function(idx){
        varlastFoldEndColumn=0;

        for(vari=0;i<this.folds.length;i++){
            varfold=this.folds[i];

            idx-=fold.start.column-lastFoldEndColumn;
            if(idx<0){
                return{
                    row:fold.start.row,
                    column:fold.start.column+idx
                };
            }

            idx-=fold.placeholder.length;
            if(idx<0){
                returnfold.start;
            }

            lastFoldEndColumn=fold.end.column;
        }

        return{
            row:this.end.row,
            column:this.end.column+idx
        };
    };
}).call(FoldLine.prototype);

exports.FoldLine=FoldLine;
});

define("ace/range_list",["require","exports","module","ace/range"],function(require,exports,module){
"usestrict";
varRange=require("./range").Range;
varcomparePoints=Range.comparePoints;

varRangeList=function(){
    this.ranges=[];
};

(function(){
    this.comparePoints=comparePoints;

    this.pointIndex=function(pos,excludeEdges,startIndex){
        varlist=this.ranges;

        for(vari=startIndex||0;i<list.length;i++){
            varrange=list[i];
            varcmpEnd=comparePoints(pos,range.end);
            if(cmpEnd>0)
                continue;
            varcmpStart=comparePoints(pos,range.start);
            if(cmpEnd===0)
                returnexcludeEdges&&cmpStart!==0?-i-2:i;
            if(cmpStart>0||(cmpStart===0&&!excludeEdges))
                returni;

            return-i-1;
        }
        return-i-1;
    };

    this.add=function(range){
        varexcludeEdges=!range.isEmpty();
        varstartIndex=this.pointIndex(range.start,excludeEdges);
        if(startIndex<0)
            startIndex=-startIndex-1;

        varendIndex=this.pointIndex(range.end,excludeEdges,startIndex);

        if(endIndex<0)
            endIndex=-endIndex-1;
        else
            endIndex++;
        returnthis.ranges.splice(startIndex,endIndex-startIndex,range);
    };

    this.addList=function(list){
        varremoved=[];
        for(vari=list.length;i--;){
            removed.push.apply(removed,this.add(list[i]));
        }
        returnremoved;
    };

    this.substractPoint=function(pos){
        vari=this.pointIndex(pos);

        if(i>=0)
            returnthis.ranges.splice(i,1);
    };
    this.merge=function(){
        varremoved=[];
        varlist=this.ranges;
        
        list=list.sort(function(a,b){
            returncomparePoints(a.start,b.start);
        });
        
        varnext=list[0],range;
        for(vari=1;i<list.length;i++){
            range=next;
            next=list[i];
            varcmp=comparePoints(range.end,next.start);
            if(cmp<0)
                continue;

            if(cmp==0&&!range.isEmpty()&&!next.isEmpty())
                continue;

            if(comparePoints(range.end,next.end)<0){
                range.end.row=next.end.row;
                range.end.column=next.end.column;
            }

            list.splice(i,1);
            removed.push(next);
            next=range;
            i--;
        }
        
        this.ranges=list;

        returnremoved;
    };

    this.contains=function(row,column){
        returnthis.pointIndex({row:row,column:column})>=0;
    };

    this.containsPoint=function(pos){
        returnthis.pointIndex(pos)>=0;
    };

    this.rangeAtPoint=function(pos){
        vari=this.pointIndex(pos);
        if(i>=0)
            returnthis.ranges[i];
    };


    this.clipRows=function(startRow,endRow){
        varlist=this.ranges;
        if(list[0].start.row>endRow||list[list.length-1].start.row<startRow)
            return[];

        varstartIndex=this.pointIndex({row:startRow,column:0});
        if(startIndex<0)
            startIndex=-startIndex-1;
        varendIndex=this.pointIndex({row:endRow,column:0},startIndex);
        if(endIndex<0)
            endIndex=-endIndex-1;

        varclipped=[];
        for(vari=startIndex;i<endIndex;i++){
            clipped.push(list[i]);
        }
        returnclipped;
    };

    this.removeAll=function(){
        returnthis.ranges.splice(0,this.ranges.length);
    };

    this.attach=function(session){
        if(this.session)
            this.detach();

        this.session=session;
        this.onChange=this.$onChange.bind(this);

        this.session.on('change',this.onChange);
    };

    this.detach=function(){
        if(!this.session)
            return;
        this.session.removeListener('change',this.onChange);
        this.session=null;
    };

    this.$onChange=function(delta){
        if(delta.action=="insert"){
            varstart=delta.start;
            varend=delta.end;
        }else{
            varend=delta.start;
            varstart=delta.end;
        }
        varstartRow=start.row;
        varendRow=end.row;
        varlineDif=endRow-startRow;

        varcolDiff=-start.column+end.column;
        varranges=this.ranges;

        for(vari=0,n=ranges.length;i<n;i++){
            varr=ranges[i];
            if(r.end.row<startRow)
                continue;
            if(r.start.row>startRow)
                break;

            if(r.start.row==startRow&&r.start.column>=start.column){
                if(r.start.column==start.column&&this.$insertRight){
                }else{
                    r.start.column+=colDiff;
                    r.start.row+=lineDif;
                }
            }
            if(r.end.row==startRow&&r.end.column>=start.column){
                if(r.end.column==start.column&&this.$insertRight){
                    continue;
                }
                if(r.end.column==start.column&&colDiff>0&&i<n-1){               
                    if(r.end.column>r.start.column&&r.end.column==ranges[i+1].start.column)
                        r.end.column-=colDiff;
                }
                r.end.column+=colDiff;
                r.end.row+=lineDif;
            }
        }

        if(lineDif!=0&&i<n){
            for(;i<n;i++){
                varr=ranges[i];
                r.start.row+=lineDif;
                r.end.row+=lineDif;
            }
        }
    };

}).call(RangeList.prototype);

exports.RangeList=RangeList;
});

define("ace/edit_session/fold",["require","exports","module","ace/range","ace/range_list","ace/lib/oop"],function(require,exports,module){
"usestrict";

varRange=require("../range").Range;
varRangeList=require("../range_list").RangeList;
varoop=require("../lib/oop");
varFold=exports.Fold=function(range,placeholder){
    this.foldLine=null;
    this.placeholder=placeholder;
    this.range=range;
    this.start=range.start;
    this.end=range.end;

    this.sameRow=range.start.row==range.end.row;
    this.subFolds=this.ranges=[];
};

oop.inherits(Fold,RangeList);

(function(){

    this.toString=function(){
        return'"'+this.placeholder+'"'+this.range.toString();
    };

    this.setFoldLine=function(foldLine){
        this.foldLine=foldLine;
        this.subFolds.forEach(function(fold){
            fold.setFoldLine(foldLine);
        });
    };

    this.clone=function(){
        varrange=this.range.clone();
        varfold=newFold(range,this.placeholder);
        this.subFolds.forEach(function(subFold){
            fold.subFolds.push(subFold.clone());
        });
        fold.collapseChildren=this.collapseChildren;
        returnfold;
    };

    this.addSubFold=function(fold){
        if(this.range.isEqual(fold))
            return;

        if(!this.range.containsRange(fold))
            thrownewError("Afoldcan'tintersectalreadyexistingfold"+fold.range+this.range);
        consumeRange(fold,this.start);

        varrow=fold.start.row,column=fold.start.column;
        for(vari=0,cmp=-1;i<this.subFolds.length;i++){
            cmp=this.subFolds[i].range.compare(row,column);
            if(cmp!=1)
                break;
        }
        varafterStart=this.subFolds[i];

        if(cmp==0)
            returnafterStart.addSubFold(fold);
        varrow=fold.range.end.row,column=fold.range.end.column;
        for(varj=i,cmp=-1;j<this.subFolds.length;j++){
            cmp=this.subFolds[j].range.compare(row,column);
            if(cmp!=1)
                break;
        }
        varafterEnd=this.subFolds[j];

        if(cmp==0)
            thrownewError("Afoldcan'tintersectalreadyexistingfold"+fold.range+this.range);

        varconsumedFolds=this.subFolds.splice(i,j-i,fold);
        fold.setFoldLine(this.foldLine);

        returnfold;
    };
    
    this.restoreRange=function(range){
        returnrestoreRange(range,this.start);
    };

}).call(Fold.prototype);

functionconsumePoint(point,anchor){
    point.row-=anchor.row;
    if(point.row==0)
        point.column-=anchor.column;
}
functionconsumeRange(range,anchor){
    consumePoint(range.start,anchor);
    consumePoint(range.end,anchor);
}
functionrestorePoint(point,anchor){
    if(point.row==0)
        point.column+=anchor.column;
    point.row+=anchor.row;
}
functionrestoreRange(range,anchor){
    restorePoint(range.start,anchor);
    restorePoint(range.end,anchor);
}

});

define("ace/edit_session/folding",["require","exports","module","ace/range","ace/edit_session/fold_line","ace/edit_session/fold","ace/token_iterator"],function(require,exports,module){
"usestrict";

varRange=require("../range").Range;
varFoldLine=require("./fold_line").FoldLine;
varFold=require("./fold").Fold;
varTokenIterator=require("../token_iterator").TokenIterator;

functionFolding(){
    this.getFoldAt=function(row,column,side){
        varfoldLine=this.getFoldLine(row);
        if(!foldLine)
            returnnull;

        varfolds=foldLine.folds;
        for(vari=0;i<folds.length;i++){
            varfold=folds[i];
            if(fold.range.contains(row,column)){
                if(side==1&&fold.range.isEnd(row,column)){
                    continue;
                }elseif(side==-1&&fold.range.isStart(row,column)){
                    continue;
                }
                returnfold;
            }
        }
    };
    this.getFoldsInRange=function(range){
        varstart=range.start;
        varend=range.end;
        varfoldLines=this.$foldData;
        varfoundFolds=[];

        start.column+=1;
        end.column-=1;

        for(vari=0;i<foldLines.length;i++){
            varcmp=foldLines[i].range.compareRange(range);
            if(cmp==2){
                continue;
            }
            elseif(cmp==-2){
                break;
            }

            varfolds=foldLines[i].folds;
            for(varj=0;j<folds.length;j++){
                varfold=folds[j];
                cmp=fold.range.compareRange(range);
                if(cmp==-2){
                    break;
                }elseif(cmp==2){
                    continue;
                }else
                if(cmp==42){
                    break;
                }
                foundFolds.push(fold);
            }
        }
        start.column-=1;
        end.column+=1;

        returnfoundFolds;
    };

    this.getFoldsInRangeList=function(ranges){
        if(Array.isArray(ranges)){
            varfolds=[];
            ranges.forEach(function(range){
                folds=folds.concat(this.getFoldsInRange(range));
            },this);
        }else{
            varfolds=this.getFoldsInRange(ranges);
        }
        returnfolds;
    };
    this.getAllFolds=function(){
        varfolds=[];
        varfoldLines=this.$foldData;
        
        for(vari=0;i<foldLines.length;i++)
            for(varj=0;j<foldLines[i].folds.length;j++)
                folds.push(foldLines[i].folds[j]);

        returnfolds;
    };
    this.getFoldStringAt=function(row,column,trim,foldLine){
        foldLine=foldLine||this.getFoldLine(row);
        if(!foldLine)
            returnnull;

        varlastFold={
            end:{column:0}
        };
        varstr,fold;
        for(vari=0;i<foldLine.folds.length;i++){
            fold=foldLine.folds[i];
            varcmp=fold.range.compareEnd(row,column);
            if(cmp==-1){
                str=this
                    .getLine(fold.start.row)
                    .substring(lastFold.end.column,fold.start.column);
                break;
            }
            elseif(cmp===0){
                returnnull;
            }
            lastFold=fold;
        }
        if(!str)
            str=this.getLine(fold.start.row).substring(lastFold.end.column);

        if(trim==-1)
            returnstr.substring(0,column-lastFold.end.column);
        elseif(trim==1)
            returnstr.substring(column-lastFold.end.column);
        else
            returnstr;
    };

    this.getFoldLine=function(docRow,startFoldLine){
        varfoldData=this.$foldData;
        vari=0;
        if(startFoldLine)
            i=foldData.indexOf(startFoldLine);
        if(i==-1)
            i=0;
        for(i;i<foldData.length;i++){
            varfoldLine=foldData[i];
            if(foldLine.start.row<=docRow&&foldLine.end.row>=docRow){
                returnfoldLine;
            }elseif(foldLine.end.row>docRow){
                returnnull;
            }
        }
        returnnull;
    };
    this.getNextFoldLine=function(docRow,startFoldLine){
        varfoldData=this.$foldData;
        vari=0;
        if(startFoldLine)
            i=foldData.indexOf(startFoldLine);
        if(i==-1)
            i=0;
        for(i;i<foldData.length;i++){
            varfoldLine=foldData[i];
            if(foldLine.end.row>=docRow){
                returnfoldLine;
            }
        }
        returnnull;
    };

    this.getFoldedRowCount=function(first,last){
        varfoldData=this.$foldData,rowCount=last-first+1;
        for(vari=0;i<foldData.length;i++){
            varfoldLine=foldData[i],
                end=foldLine.end.row,
                start=foldLine.start.row;
            if(end>=last){
                if(start<last){
                    if(start>=first)
                        rowCount-=last-start;
                    else
                        rowCount=0;//inonefold
                }
                break;
            }elseif(end>=first){
                if(start>=first)//foldinsiderange
                    rowCount-= end-start;
                else
                    rowCount-= end-first+1;
            }
        }
        returnrowCount;
    };

    this.$addFoldLine=function(foldLine){
        this.$foldData.push(foldLine);
        this.$foldData.sort(function(a,b){
            returna.start.row-b.start.row;
        });
        returnfoldLine;
    };
    this.addFold=function(placeholder,range){
        varfoldData=this.$foldData;
        varadded=false;
        varfold;
        
        if(placeholderinstanceofFold)
            fold=placeholder;
        else{
            fold=newFold(range,placeholder);
            fold.collapseChildren=range.collapseChildren;
        }
        this.$clipRangeToDocument(fold.range);

        varstartRow=fold.start.row;
        varstartColumn=fold.start.column;
        varendRow=fold.end.row;
        varendColumn=fold.end.column;
        if(!(startRow<endRow||
            startRow==endRow&&startColumn<=endColumn-2))
            thrownewError("Therangehastobeatleast2characterswidth");

        varstartFold=this.getFoldAt(startRow,startColumn,1);
        varendFold=this.getFoldAt(endRow,endColumn,-1);
        if(startFold&&endFold==startFold)
            returnstartFold.addSubFold(fold);

        if(startFold&&!startFold.range.isStart(startRow,startColumn))
            this.removeFold(startFold);
        
        if(endFold&&!endFold.range.isEnd(endRow,endColumn))
            this.removeFold(endFold);
        varfolds=this.getFoldsInRange(fold.range);
        if(folds.length>0){
            this.removeFolds(folds);
            folds.forEach(function(subFold){
                fold.addSubFold(subFold);
            });
        }

        for(vari=0;i<foldData.length;i++){
            varfoldLine=foldData[i];
            if(endRow==foldLine.start.row){
                foldLine.addFold(fold);
                added=true;
                break;
            }elseif(startRow==foldLine.end.row){
                foldLine.addFold(fold);
                added=true;
                if(!fold.sameRow){
                    varfoldLineNext=foldData[i+1];
                    if(foldLineNext&&foldLineNext.start.row==endRow){
                        foldLine.merge(foldLineNext);
                        break;
                    }
                }
                break;
            }elseif(endRow<=foldLine.start.row){
                break;
            }
        }

        if(!added)
            foldLine=this.$addFoldLine(newFoldLine(this.$foldData,fold));

        if(this.$useWrapMode)
            this.$updateWrapData(foldLine.start.row,foldLine.start.row);
        else
            this.$updateRowLengthCache(foldLine.start.row,foldLine.start.row);
        this.$modified=true;
        this._signal("changeFold",{data:fold,action:"add"});

        returnfold;
    };

    this.addFolds=function(folds){
        folds.forEach(function(fold){
            this.addFold(fold);
        },this);
    };

    this.removeFold=function(fold){
        varfoldLine=fold.foldLine;
        varstartRow=foldLine.start.row;
        varendRow=foldLine.end.row;

        varfoldLines=this.$foldData;
        varfolds=foldLine.folds;
        if(folds.length==1){
            foldLines.splice(foldLines.indexOf(foldLine),1);
        }else
        if(foldLine.range.isEnd(fold.end.row,fold.end.column)){
            folds.pop();
            foldLine.end.row=folds[folds.length-1].end.row;
            foldLine.end.column=folds[folds.length-1].end.column;
        }else
        if(foldLine.range.isStart(fold.start.row,fold.start.column)){
            folds.shift();
            foldLine.start.row=folds[0].start.row;
            foldLine.start.column=folds[0].start.column;
        }else
        if(fold.sameRow){
            folds.splice(folds.indexOf(fold),1);
        }else
        {
            varnewFoldLine=foldLine.split(fold.start.row,fold.start.column);
            folds=newFoldLine.folds;
            folds.shift();
            newFoldLine.start.row=folds[0].start.row;
            newFoldLine.start.column=folds[0].start.column;
        }

        if(!this.$updating){
            if(this.$useWrapMode)
                this.$updateWrapData(startRow,endRow);
            else
                this.$updateRowLengthCache(startRow,endRow);
        }
        this.$modified=true;
        this._signal("changeFold",{data:fold,action:"remove"});
    };

    this.removeFolds=function(folds){
        varcloneFolds=[];
        for(vari=0;i<folds.length;i++){
            cloneFolds.push(folds[i]);
        }

        cloneFolds.forEach(function(fold){
            this.removeFold(fold);
        },this);
        this.$modified=true;
    };

    this.expandFold=function(fold){
        this.removeFold(fold);
        fold.subFolds.forEach(function(subFold){
            fold.restoreRange(subFold);
            this.addFold(subFold);
        },this);
        if(fold.collapseChildren>0){
            this.foldAll(fold.start.row+1,fold.end.row,fold.collapseChildren-1);
        }
        fold.subFolds=[];
    };

    this.expandFolds=function(folds){
        folds.forEach(function(fold){
            this.expandFold(fold);
        },this);
    };

    this.unfold=function(location,expandInner){
        varrange,folds;
        if(location==null){
            range=newRange(0,0,this.getLength(),0);
            expandInner=true;
        }elseif(typeoflocation=="number")
            range=newRange(location,0,location,this.getLine(location).length);
        elseif("row"inlocation)
            range=Range.fromPoints(location,location);
        else
            range=location;
        
        folds=this.getFoldsInRangeList(range);
        if(expandInner){
            this.removeFolds(folds);
        }else{
            varsubFolds=folds;
            while(subFolds.length){
                this.expandFolds(subFolds);
                subFolds=this.getFoldsInRangeList(range);
            }
        }
        if(folds.length)
            returnfolds;
    };
    this.isRowFolded=function(docRow,startFoldRow){
        return!!this.getFoldLine(docRow,startFoldRow);
    };

    this.getRowFoldEnd=function(docRow,startFoldRow){
        varfoldLine=this.getFoldLine(docRow,startFoldRow);
        returnfoldLine?foldLine.end.row:docRow;
    };

    this.getRowFoldStart=function(docRow,startFoldRow){
        varfoldLine=this.getFoldLine(docRow,startFoldRow);
        returnfoldLine?foldLine.start.row:docRow;
    };

    this.getFoldDisplayLine=function(foldLine,endRow,endColumn,startRow,startColumn){
        if(startRow==null)
            startRow=foldLine.start.row;
        if(startColumn==null)
            startColumn=0;
        if(endRow==null)
            endRow=foldLine.end.row;
        if(endColumn==null)
            endColumn=this.getLine(endRow).length;
        vardoc=this.doc;
        vartextLine="";

        foldLine.walk(function(placeholder,row,column,lastColumn){
            if(row<startRow)
                return;
            if(row==startRow){
                if(column<startColumn)
                    return;
                lastColumn=Math.max(startColumn,lastColumn);
            }

            if(placeholder!=null){
                textLine+=placeholder;
            }else{
                textLine+=doc.getLine(row).substring(lastColumn,column);
            }
        },endRow,endColumn);
        returntextLine;
    };

    this.getDisplayLine=function(row,endColumn,startRow,startColumn){
        varfoldLine=this.getFoldLine(row);

        if(!foldLine){
            varline;
            line=this.doc.getLine(row);
            returnline.substring(startColumn||0,endColumn||line.length);
        }else{
            returnthis.getFoldDisplayLine(
                foldLine,row,endColumn,startRow,startColumn);
        }
    };

    this.$cloneFoldData=function(){
        varfd=[];
        fd=this.$foldData.map(function(foldLine){
            varfolds=foldLine.folds.map(function(fold){
                returnfold.clone();
            });
            returnnewFoldLine(fd,folds);
        });

        returnfd;
    };

    this.toggleFold=function(tryToUnfold){
        varselection=this.selection;
        varrange=selection.getRange();
        varfold;
        varbracketPos;

        if(range.isEmpty()){
            varcursor=range.start;
            fold=this.getFoldAt(cursor.row,cursor.column);

            if(fold){
                this.expandFold(fold);
                return;
            }elseif(bracketPos=this.findMatchingBracket(cursor)){
                if(range.comparePoint(bracketPos)==1){
                    range.end=bracketPos;
                }else{
                    range.start=bracketPos;
                    range.start.column++;
                    range.end.column--;
                }
            }elseif(bracketPos=this.findMatchingBracket({row:cursor.row,column:cursor.column+1})){
                if(range.comparePoint(bracketPos)==1)
                    range.end=bracketPos;
                else
                    range.start=bracketPos;

                range.start.column++;
            }else{
                range=this.getCommentFoldRange(cursor.row,cursor.column)||range;
            }
        }else{
            varfolds=this.getFoldsInRange(range);
            if(tryToUnfold&&folds.length){
                this.expandFolds(folds);
                return;
            }elseif(folds.length==1){
                fold=folds[0];
            }
        }

        if(!fold)
            fold=this.getFoldAt(range.start.row,range.start.column);

        if(fold&&fold.range.toString()==range.toString()){
            this.expandFold(fold);
            return;
        }

        varplaceholder="...";
        if(!range.isMultiLine()){
            placeholder=this.getTextRange(range);
            if(placeholder.length<4)
                return;
            placeholder=placeholder.trim().substring(0,2)+"..";
        }

        this.addFold(placeholder,range);
    };

    this.getCommentFoldRange=function(row,column,dir){
        variterator=newTokenIterator(this,row,column);
        vartoken=iterator.getCurrentToken();
        vartype=token.type;
        if(token&&/^comment|string/.test(type)){
            type=type.match(/comment|string/)[0];
            if(type=="comment")
                type+="|doc-start";
            varre=newRegExp(type);
            varrange=newRange();
            if(dir!=1){
                do{
                    token=iterator.stepBackward();
                }while(token&&re.test(token.type));
                iterator.stepForward();
            }
            
            range.start.row=iterator.getCurrentTokenRow();
            range.start.column=iterator.getCurrentTokenColumn()+2;

            iterator=newTokenIterator(this,row,column);
            
            if(dir!=-1){
                varlastRow=-1;
                do{
                    token=iterator.stepForward();
                    if(lastRow==-1){
                        varstate=this.getState(iterator.$row);
                        if(!re.test(state))
                            lastRow=iterator.$row;
                    }elseif(iterator.$row>lastRow){
                        break;
                    }
                }while(token&&re.test(token.type));
                token=iterator.stepBackward();
            }else
                token=iterator.getCurrentToken();

            range.end.row=iterator.getCurrentTokenRow();
            range.end.column=iterator.getCurrentTokenColumn()+token.value.length-2;
            returnrange;
        }
    };

    this.foldAll=function(startRow,endRow,depth){
        if(depth==undefined)
            depth=100000;//JSON.stringifydoesn'thanleInfinity
        varfoldWidgets=this.foldWidgets;
        if(!foldWidgets)
            return;//modedoesn'tsupportfolding
        endRow=endRow||this.getLength();
        startRow=startRow||0;
        for(varrow=startRow;row<endRow;row++){
            if(foldWidgets[row]==null)
                foldWidgets[row]=this.getFoldWidget(row);
            if(foldWidgets[row]!="start")
                continue;

            varrange=this.getFoldWidgetRange(row);
            if(range&&range.isMultiLine()
                &&range.end.row<=endRow
                &&range.start.row>=startRow
            ){
                row=range.end.row;
                try{
                    varfold=this.addFold("...",range);
                    if(fold)
                        fold.collapseChildren=depth;
                }catch(e){}
            }
        }
    };
    this.$foldStyles={
        "manual":1,
        "markbegin":1,
        "markbeginend":1
    };
    this.$foldStyle="markbegin";
    this.setFoldStyle=function(style){
        if(!this.$foldStyles[style])
            thrownewError("invalidfoldstyle:"+style+"["+Object.keys(this.$foldStyles).join(",")+"]");
        
        if(this.$foldStyle==style)
            return;

        this.$foldStyle=style;
        
        if(style=="manual")
            this.unfold();
        varmode=this.$foldMode;
        this.$setFolding(null);
        this.$setFolding(mode);
    };

    this.$setFolding=function(foldMode){
        if(this.$foldMode==foldMode)
            return;
            
        this.$foldMode=foldMode;
        
        this.off('change',this.$updateFoldWidgets);
        this.off('tokenizerUpdate',this.$tokenizerUpdateFoldWidgets);
        this._signal("changeAnnotation");
        
        if(!foldMode||this.$foldStyle=="manual"){
            this.foldWidgets=null;
            return;
        }
        
        this.foldWidgets=[];
        this.getFoldWidget=foldMode.getFoldWidget.bind(foldMode,this,this.$foldStyle);
        this.getFoldWidgetRange=foldMode.getFoldWidgetRange.bind(foldMode,this,this.$foldStyle);
        
        this.$updateFoldWidgets=this.updateFoldWidgets.bind(this);
        this.$tokenizerUpdateFoldWidgets=this.tokenizerUpdateFoldWidgets.bind(this);
        this.on('change',this.$updateFoldWidgets);
        this.on('tokenizerUpdate',this.$tokenizerUpdateFoldWidgets);
    };

    this.getParentFoldRangeData=function(row,ignoreCurrent){
        varfw=this.foldWidgets;
        if(!fw||(ignoreCurrent&&fw[row]))
            return{};

        vari=row-1,firstRange;
        while(i>=0){
            varc=fw[i];
            if(c==null)
                c=fw[i]=this.getFoldWidget(i);

            if(c=="start"){
                varrange=this.getFoldWidgetRange(i);
                if(!firstRange)
                    firstRange=range;
                if(range&&range.end.row>=row)
                    break;
            }
            i--;
        }

        return{
            range:i!==-1&&range,
            firstRange:firstRange
        };
    };

    this.onFoldWidgetClick=function(row,e){
        e=e.domEvent;
        varoptions={
            children:e.shiftKey,
            all:e.ctrlKey||e.metaKey,
            siblings:e.altKey
        };
        
        varrange=this.$toggleFoldWidget(row,options);
        if(!range){
            varel=(e.target||e.srcElement);
            if(el&&/ace_fold-widget/.test(el.className))
                el.className+="ace_invalid";
        }
    };
    
    this.$toggleFoldWidget=function(row,options){
        if(!this.getFoldWidget)
            return;
        vartype=this.getFoldWidget(row);
        varline=this.getLine(row);

        vardir=type==="end"?-1:1;
        varfold=this.getFoldAt(row,dir===-1?0:line.length,dir);

        if(fold){
            if(options.children||options.all)
                this.removeFold(fold);
            else
                this.expandFold(fold);
            returnfold;
        }

        varrange=this.getFoldWidgetRange(row,true);
        if(range&&!range.isMultiLine()){
            fold=this.getFoldAt(range.start.row,range.start.column,1);
            if(fold&&range.isEqual(fold.range)){
                this.removeFold(fold);
                returnfold;
            }
        }
        
        if(options.siblings){
            vardata=this.getParentFoldRangeData(row);
            if(data.range){
                varstartRow=data.range.start.row+1;
                varendRow=data.range.end.row;
            }
            this.foldAll(startRow,endRow,options.all?10000:0);
        }elseif(options.children){
            endRow=range?range.end.row:this.getLength();
            this.foldAll(row+1,endRow,options.all?10000:0);
        }elseif(range){
            if(options.all)
                range.collapseChildren=10000;
            this.addFold("...",range);
        }
        
        returnrange;
    };
    
    
    
    this.toggleFoldWidget=function(toggleParent){
        varrow=this.selection.getCursor().row;
        row=this.getRowFoldStart(row);
        varrange=this.$toggleFoldWidget(row,{});
        
        if(range)
            return;
        vardata=this.getParentFoldRangeData(row,true);
        range=data.range||data.firstRange;
        
        if(range){
            row=range.start.row;
            varfold=this.getFoldAt(row,this.getLine(row).length,1);

            if(fold){
                this.removeFold(fold);
            }else{
                this.addFold("...",range);
            }
        }
    };

    this.updateFoldWidgets=function(delta){
        varfirstRow=delta.start.row;
        varlen=delta.end.row-firstRow;

        if(len===0){
            this.foldWidgets[firstRow]=null;
        }elseif(delta.action=='remove'){
            this.foldWidgets.splice(firstRow,len+1,null);
        }else{
            varargs=Array(len+1);
            args.unshift(firstRow,1);
            this.foldWidgets.splice.apply(this.foldWidgets,args);
        }
    };
    this.tokenizerUpdateFoldWidgets=function(e){
        varrows=e.data;
        if(rows.first!=rows.last){
            if(this.foldWidgets.length>rows.first)
                this.foldWidgets.splice(rows.first,this.foldWidgets.length);
        }
    };
}

exports.Folding=Folding;

});

define("ace/edit_session/bracket_match",["require","exports","module","ace/token_iterator","ace/range"],function(require,exports,module){
"usestrict";

varTokenIterator=require("../token_iterator").TokenIterator;
varRange=require("../range").Range;


functionBracketMatch(){

    this.findMatchingBracket=function(position,chr){
        if(position.column==0)returnnull;

        varcharBeforeCursor=chr||this.getLine(position.row).charAt(position.column-1);
        if(charBeforeCursor=="")returnnull;

        varmatch=charBeforeCursor.match(/([\(\[\{])|([\)\]\}])/);
        if(!match)
            returnnull;

        if(match[1])
            returnthis.$findClosingBracket(match[1],position);
        else
            returnthis.$findOpeningBracket(match[2],position);
    };
    
    this.getBracketRange=function(pos){
        varline=this.getLine(pos.row);
        varbefore=true,range;

        varchr=line.charAt(pos.column-1);
        varmatch=chr&&chr.match(/([\(\[\{])|([\)\]\}])/);
        if(!match){
            chr=line.charAt(pos.column);
            pos={row:pos.row,column:pos.column+1};
            match=chr&&chr.match(/([\(\[\{])|([\)\]\}])/);
            before=false;
        }
        if(!match)
            returnnull;

        if(match[1]){
            varbracketPos=this.$findClosingBracket(match[1],pos);
            if(!bracketPos)
                returnnull;
            range=Range.fromPoints(pos,bracketPos);
            if(!before){
                range.end.column++;
                range.start.column--;
            }
            range.cursor=range.end;
        }else{
            varbracketPos=this.$findOpeningBracket(match[2],pos);
            if(!bracketPos)
                returnnull;
            range=Range.fromPoints(bracketPos,pos);
            if(!before){
                range.start.column++;
                range.end.column--;
            }
            range.cursor=range.start;
        }
        
        returnrange;
    };

    this.$brackets={
        ")":"(",
        "(":")",
        "]":"[",
        "[":"]",
        "{":"}",
        "}":"{"
    };

    this.$findOpeningBracket=function(bracket,position,typeRe){
        varopenBracket=this.$brackets[bracket];
        vardepth=1;

        variterator=newTokenIterator(this,position.row,position.column);
        vartoken=iterator.getCurrentToken();
        if(!token)
            token=iterator.stepForward();
        if(!token)
            return;
        
         if(!typeRe){
            typeRe=newRegExp(
                "(\\.?"+
                token.type.replace(".","\\.").replace("rparen",".paren")
                    .replace(/\b(?:end)\b/,"(?:start|begin|end)")
                +")+"
            );
        }
        varvalueIndex=position.column-iterator.getCurrentTokenColumn()-2;
        varvalue=token.value;
        
        while(true){
        
            while(valueIndex>=0){
                varchr=value.charAt(valueIndex);
                if(chr==openBracket){
                    depth-=1;
                    if(depth==0){
                        return{row:iterator.getCurrentTokenRow(),
                            column:valueIndex+iterator.getCurrentTokenColumn()};
                    }
                }
                elseif(chr==bracket){
                    depth+=1;
                }
                valueIndex-=1;
            }
            do{
                token=iterator.stepBackward();
            }while(token&&!typeRe.test(token.type));

            if(token==null)
                break;
                
            value=token.value;
            valueIndex=value.length-1;
        }
        
        returnnull;
    };

    this.$findClosingBracket=function(bracket,position,typeRe){
        varclosingBracket=this.$brackets[bracket];
        vardepth=1;

        variterator=newTokenIterator(this,position.row,position.column);
        vartoken=iterator.getCurrentToken();
        if(!token)
            token=iterator.stepForward();
        if(!token)
            return;

        if(!typeRe){
            typeRe=newRegExp(
                "(\\.?"+
                token.type.replace(".","\\.").replace("lparen",".paren")
                    .replace(/\b(?:start|begin)\b/,"(?:start|begin|end)")
                +")+"
            );
        }
        varvalueIndex=position.column-iterator.getCurrentTokenColumn();

        while(true){

            varvalue=token.value;
            varvalueLength=value.length;
            while(valueIndex<valueLength){
                varchr=value.charAt(valueIndex);
                if(chr==closingBracket){
                    depth-=1;
                    if(depth==0){
                        return{row:iterator.getCurrentTokenRow(),
                            column:valueIndex+iterator.getCurrentTokenColumn()};
                    }
                }
                elseif(chr==bracket){
                    depth+=1;
                }
                valueIndex+=1;
            }
            do{
                token=iterator.stepForward();
            }while(token&&!typeRe.test(token.type));

            if(token==null)
                break;

            valueIndex=0;
        }
        
        returnnull;
    };
}
exports.BracketMatch=BracketMatch;

});

define("ace/edit_session",["require","exports","module","ace/lib/oop","ace/lib/lang","ace/bidihandler","ace/config","ace/lib/event_emitter","ace/selection","ace/mode/text","ace/range","ace/document","ace/background_tokenizer","ace/search_highlight","ace/edit_session/folding","ace/edit_session/bracket_match"],function(require,exports,module){
"usestrict";

varoop=require("./lib/oop");
varlang=require("./lib/lang");
varBidiHandler=require("./bidihandler").BidiHandler;
varconfig=require("./config");
varEventEmitter=require("./lib/event_emitter").EventEmitter;
varSelection=require("./selection").Selection;
varTextMode=require("./mode/text").Mode;
varRange=require("./range").Range;
varDocument=require("./document").Document;
varBackgroundTokenizer=require("./background_tokenizer").BackgroundTokenizer;
varSearchHighlight=require("./search_highlight").SearchHighlight;

varEditSession=function(text,mode){
    this.$breakpoints=[];
    this.$decorations=[];
    this.$frontMarkers={};
    this.$backMarkers={};
    this.$markerId=1;
    this.$undoSelect=true;

    this.$foldData=[];
    this.id="session"+(++EditSession.$uid);
    this.$foldData.toString=function(){
        returnthis.join("\n");
    };
    this.on("changeFold",this.onChangeFold.bind(this));
    this.$onChange=this.onChange.bind(this);

    if(typeoftext!="object"||!text.getLine)
        text=newDocument(text);

    this.$bidiHandler=newBidiHandler(this);
    this.setDocument(text);
    this.selection=newSelection(this);

    config.resetOptions(this);
    this.setMode(mode);
    config._signal("session",this);
};


EditSession.$uid=0;

(function(){

    oop.implement(this,EventEmitter);
    this.setDocument=function(doc){
        if(this.doc)
            this.doc.removeListener("change",this.$onChange);

        this.doc=doc;
        doc.on("change",this.$onChange);

        if(this.bgTokenizer)
            this.bgTokenizer.setDocument(this.getDocument());

        this.resetCaches();
    };
    this.getDocument=function(){
        returnthis.doc;
    };
    this.$resetRowCache=function(docRow){
        if(!docRow){
            this.$docRowCache=[];
            this.$screenRowCache=[];
            return;
        }
        varl=this.$docRowCache.length;
        vari=this.$getRowCacheIndex(this.$docRowCache,docRow)+1;
        if(l>i){
            this.$docRowCache.splice(i,l);
            this.$screenRowCache.splice(i,l);
        }
    };

    this.$getRowCacheIndex=function(cacheArray,val){
        varlow=0;
        varhi=cacheArray.length-1;

        while(low<=hi){
            varmid=(low+hi)>>1;
            varc=cacheArray[mid];

            if(val>c)
                low=mid+1;
            elseif(val<c)
                hi=mid-1;
            else
                returnmid;
        }

        returnlow-1;
    };

    this.resetCaches=function(){
        this.$modified=true;
        this.$wrapData=[];
        this.$rowLengthCache=[];
        this.$resetRowCache(0);
        if(this.bgTokenizer)
            this.bgTokenizer.start(0);
    };

    this.onChangeFold=function(e){
        varfold=e.data;
        this.$resetRowCache(fold.start.row);
    };

    this.onChange=function(delta){
        this.$modified=true;
        this.$bidiHandler.onChange(delta);
        this.$resetRowCache(delta.start.row);

        varremovedFolds=this.$updateInternalDataOnChange(delta);
        if(!this.$fromUndo&&this.$undoManager){
            if(removedFolds&&removedFolds.length){
                this.$undoManager.add({
                    action:"removeFolds",
                    folds: removedFolds
                },this.mergeUndoDeltas);
                this.mergeUndoDeltas=true;
            }
            this.$undoManager.add(delta,this.mergeUndoDeltas);
            this.mergeUndoDeltas=true;
            
            this.$informUndoManager.schedule();
        }

        this.bgTokenizer&&this.bgTokenizer.$updateOnChange(delta);
        this._signal("change",delta);
    };
    this.setValue=function(text){
        this.doc.setValue(text);
        this.selection.moveTo(0,0);

        this.$resetRowCache(0);
        this.setUndoManager(this.$undoManager);
        this.getUndoManager().reset();
    };
    this.getValue=
    this.toString=function(){
        returnthis.doc.getValue();
    };
    this.getSelection=function(){
        returnthis.selection;
    };
    this.getState=function(row){
        returnthis.bgTokenizer.getState(row);
    };
    this.getTokens=function(row){
        returnthis.bgTokenizer.getTokens(row);
    };
    this.getTokenAt=function(row,column){
        vartokens=this.bgTokenizer.getTokens(row);
        vartoken,c=0;
        if(column==null){
            vari=tokens.length-1;
            c=this.getLine(row).length;
        }else{
            for(vari=0;i<tokens.length;i++){
                c+=tokens[i].value.length;
                if(c>=column)
                    break;
            }
        }
        token=tokens[i];
        if(!token)
            returnnull;
        token.index=i;
        token.start=c-token.value.length;
        returntoken;
    };
    this.setUndoManager=function(undoManager){
        this.$undoManager=undoManager;
        
        if(this.$informUndoManager)
            this.$informUndoManager.cancel();
        
        if(undoManager){
            varself=this;
            undoManager.addSession(this);
            this.$syncInformUndoManager=function(){
                self.$informUndoManager.cancel();
                self.mergeUndoDeltas=false;
            };
            this.$informUndoManager=lang.delayedCall(this.$syncInformUndoManager);
        }else{
            this.$syncInformUndoManager=function(){};
        }
    };
    this.markUndoGroup=function(){
        if(this.$syncInformUndoManager)
            this.$syncInformUndoManager();
    };
    
    this.$defaultUndoManager={
        undo:function(){},
        redo:function(){},
        reset:function(){},
        add:function(){},
        addSelection:function(){},
        startNewGroup:function(){},
        addSession:function(){}
    };
    this.getUndoManager=function(){
        returnthis.$undoManager||this.$defaultUndoManager;
    };
    this.getTabString=function(){
        if(this.getUseSoftTabs()){
            returnlang.stringRepeat("",this.getTabSize());
        }else{
            return"\t";
        }
    };
    this.setUseSoftTabs=function(val){
        this.setOption("useSoftTabs",val);
    };
    this.getUseSoftTabs=function(){
        returnthis.$useSoftTabs&&!this.$mode.$indentWithTabs;
    };
    this.setTabSize=function(tabSize){
        this.setOption("tabSize",tabSize);
    };
    this.getTabSize=function(){
        returnthis.$tabSize;
    };
    this.isTabStop=function(position){
        returnthis.$useSoftTabs&&(position.column%this.$tabSize===0);
    };
    this.setNavigateWithinSoftTabs=function(navigateWithinSoftTabs){
        this.setOption("navigateWithinSoftTabs",navigateWithinSoftTabs);
    };
    this.getNavigateWithinSoftTabs=function(){
        returnthis.$navigateWithinSoftTabs;
    };

    this.$overwrite=false;
    this.setOverwrite=function(overwrite){
        this.setOption("overwrite",overwrite);
    };
    this.getOverwrite=function(){
        returnthis.$overwrite;
    };
    this.toggleOverwrite=function(){
        this.setOverwrite(!this.$overwrite);
    };
    this.addGutterDecoration=function(row,className){
        if(!this.$decorations[row])
            this.$decorations[row]="";
        this.$decorations[row]+=""+className;
        this._signal("changeBreakpoint",{});
    };
    this.removeGutterDecoration=function(row,className){
        this.$decorations[row]=(this.$decorations[row]||"").replace(""+className,"");
        this._signal("changeBreakpoint",{});
    };
    this.getBreakpoints=function(){
        returnthis.$breakpoints;
    };
    this.setBreakpoints=function(rows){
        this.$breakpoints=[];
        for(vari=0;i<rows.length;i++){
            this.$breakpoints[rows[i]]="ace_breakpoint";
        }
        this._signal("changeBreakpoint",{});
    };
    this.clearBreakpoints=function(){
        this.$breakpoints=[];
        this._signal("changeBreakpoint",{});
    };
    this.setBreakpoint=function(row,className){
        if(className===undefined)
            className="ace_breakpoint";
        if(className)
            this.$breakpoints[row]=className;
        else
            deletethis.$breakpoints[row];
        this._signal("changeBreakpoint",{});
    };
    this.clearBreakpoint=function(row){
        deletethis.$breakpoints[row];
        this._signal("changeBreakpoint",{});
    };
    this.addMarker=function(range,clazz,type,inFront){
        varid=this.$markerId++;

        varmarker={
            range:range,
            type:type||"line",
            renderer:typeoftype=="function"?type:null,
            clazz:clazz,
            inFront:!!inFront,
            id:id
        };

        if(inFront){
            this.$frontMarkers[id]=marker;
            this._signal("changeFrontMarker");
        }else{
            this.$backMarkers[id]=marker;
            this._signal("changeBackMarker");
        }

        returnid;
    };
    this.addDynamicMarker=function(marker,inFront){
        if(!marker.update)
            return;
        varid=this.$markerId++;
        marker.id=id;
        marker.inFront=!!inFront;

        if(inFront){
            this.$frontMarkers[id]=marker;
            this._signal("changeFrontMarker");
        }else{
            this.$backMarkers[id]=marker;
            this._signal("changeBackMarker");
        }

        returnmarker;
    };
    this.removeMarker=function(markerId){
        varmarker=this.$frontMarkers[markerId]||this.$backMarkers[markerId];
        if(!marker)
            return;

        varmarkers=marker.inFront?this.$frontMarkers:this.$backMarkers;
        delete(markers[markerId]);
        this._signal(marker.inFront?"changeFrontMarker":"changeBackMarker");
    };
    this.getMarkers=function(inFront){
        returninFront?this.$frontMarkers:this.$backMarkers;
    };

    this.highlight=function(re){
        if(!this.$searchHighlight){
            varhighlight=newSearchHighlight(null,"ace_selected-word","text");
            this.$searchHighlight=this.addDynamicMarker(highlight);
        }
        this.$searchHighlight.setRegexp(re);
    };
    this.highlightLines=function(startRow,endRow,clazz,inFront){
        if(typeofendRow!="number"){
            clazz=endRow;
            endRow=startRow;
        }
        if(!clazz)
            clazz="ace_step";

        varrange=newRange(startRow,0,endRow,Infinity);
        range.id=this.addMarker(range,clazz,"fullLine",inFront);
        returnrange;
    };
    this.setAnnotations=function(annotations){
        this.$annotations=annotations;
        this._signal("changeAnnotation",{});
    };
    this.getAnnotations=function(){
        returnthis.$annotations||[];
    };
    this.clearAnnotations=function(){
        this.setAnnotations([]);
    };
    this.$detectNewLine=function(text){
        varmatch=text.match(/^.*?(\r?\n)/m);
        if(match){
            this.$autoNewLine=match[1];
        }else{
            this.$autoNewLine="\n";
        }
    };
    this.getWordRange=function(row,column){
        varline=this.getLine(row);

        varinToken=false;
        if(column>0)
            inToken=!!line.charAt(column-1).match(this.tokenRe);

        if(!inToken)
            inToken=!!line.charAt(column).match(this.tokenRe);

        if(inToken)
            varre=this.tokenRe;
        elseif(/^\s+$/.test(line.slice(column-1,column+1)))
            varre=/\s/;
        else
            varre=this.nonTokenRe;

        varstart=column;
        if(start>0){
            do{
                start--;
            }
            while(start>=0&&line.charAt(start).match(re));
            start++;
        }

        varend=column;
        while(end<line.length&&line.charAt(end).match(re)){
            end++;
        }

        returnnewRange(row,start,row,end);
    };
    this.getAWordRange=function(row,column){
        varwordRange=this.getWordRange(row,column);
        varline=this.getLine(wordRange.end.row);

        while(line.charAt(wordRange.end.column).match(/[\t]/)){
            wordRange.end.column+=1;
        }
        returnwordRange;
    };
    this.setNewLineMode=function(newLineMode){
        this.doc.setNewLineMode(newLineMode);
    };
    this.getNewLineMode=function(){
        returnthis.doc.getNewLineMode();
    };
    this.setUseWorker=function(useWorker){this.setOption("useWorker",useWorker);};
    this.getUseWorker=function(){returnthis.$useWorker;};
    this.onReloadTokenizer=function(e){
        varrows=e.data;
        this.bgTokenizer.start(rows.first);
        this._signal("tokenizerUpdate",e);
    };

    this.$modes={};
    this.$mode=null;
    this.$modeId=null;
    this.setMode=function(mode,cb){
        if(mode&&typeofmode==="object"){
            if(mode.getTokenizer)
                returnthis.$onChangeMode(mode);
            varoptions=mode;
            varpath=options.path;
        }else{
            path=mode||"ace/mode/text";
        }
        if(!this.$modes["ace/mode/text"])
            this.$modes["ace/mode/text"]=newTextMode();

        if(this.$modes[path]&&!options){
            this.$onChangeMode(this.$modes[path]);
            cb&&cb();
            return;
        }
        this.$modeId=path;
        config.loadModule(["mode",path],function(m){
            if(this.$modeId!==path)
                returncb&&cb();
            if(this.$modes[path]&&!options){
                this.$onChangeMode(this.$modes[path]);
            }elseif(m&&m.Mode){
                m=newm.Mode(options);
                if(!options){
                    this.$modes[path]=m;
                    m.$id=path;
                }
                this.$onChangeMode(m);
            }
            cb&&cb();
        }.bind(this));
        if(!this.$mode)
            this.$onChangeMode(this.$modes["ace/mode/text"],true);
    };

    this.$onChangeMode=function(mode,$isPlaceholder){
        if(!$isPlaceholder)
            this.$modeId=mode.$id;
        if(this.$mode===mode)
            return;

        this.$mode=mode;

        this.$stopWorker();

        if(this.$useWorker)
            this.$startWorker();

        vartokenizer=mode.getTokenizer();

        if(tokenizer.addEventListener!==undefined){
            varonReloadTokenizer=this.onReloadTokenizer.bind(this);
            tokenizer.addEventListener("update",onReloadTokenizer);
        }

        if(!this.bgTokenizer){
            this.bgTokenizer=newBackgroundTokenizer(tokenizer);
            var_self=this;
            this.bgTokenizer.addEventListener("update",function(e){
                _self._signal("tokenizerUpdate",e);
            });
        }else{
            this.bgTokenizer.setTokenizer(tokenizer);
        }

        this.bgTokenizer.setDocument(this.getDocument());

        this.tokenRe=mode.tokenRe;
        this.nonTokenRe=mode.nonTokenRe;

        
        if(!$isPlaceholder){
            if(mode.attachToSession)
                mode.attachToSession(this);
            this.$options.wrapMethod.set.call(this,this.$wrapMethod);
            this.$setFolding(mode.foldingRules);
            this.bgTokenizer.start(0);
            this._emit("changeMode");
        }
    };

    this.$stopWorker=function(){
        if(this.$worker){
            this.$worker.terminate();
            this.$worker=null;
        }
    };

    this.$startWorker=function(){
        try{
            this.$worker=this.$mode.createWorker(this);
        }catch(e){
            config.warn("Couldnotloadworker",e);
            this.$worker=null;
        }
    };
    this.getMode=function(){
        returnthis.$mode;
    };

    this.$scrollTop=0;
    this.setScrollTop=function(scrollTop){
        if(this.$scrollTop===scrollTop||isNaN(scrollTop))
            return;

        this.$scrollTop=scrollTop;
        this._signal("changeScrollTop",scrollTop);
    };
    this.getScrollTop=function(){
        returnthis.$scrollTop;
    };

    this.$scrollLeft=0;
    this.setScrollLeft=function(scrollLeft){
        if(this.$scrollLeft===scrollLeft||isNaN(scrollLeft))
            return;

        this.$scrollLeft=scrollLeft;
        this._signal("changeScrollLeft",scrollLeft);
    };
    this.getScrollLeft=function(){
        returnthis.$scrollLeft;
    };
    this.getScreenWidth=function(){
        this.$computeWidth();
        if(this.lineWidgets)
            returnMath.max(this.getLineWidgetMaxWidth(),this.screenWidth);
        returnthis.screenWidth;
    };
    
    this.getLineWidgetMaxWidth=function(){
        if(this.lineWidgetsWidth!=null)returnthis.lineWidgetsWidth;
        varwidth=0;
        this.lineWidgets.forEach(function(w){
            if(w&&w.screenWidth>width)
                width=w.screenWidth;
        });
        returnthis.lineWidgetWidth=width;
    };

    this.$computeWidth=function(force){
        if(this.$modified||force){
            this.$modified=false;

            if(this.$useWrapMode)
                returnthis.screenWidth=this.$wrapLimit;

            varlines=this.doc.getAllLines();
            varcache=this.$rowLengthCache;
            varlongestScreenLine=0;
            varfoldIndex=0;
            varfoldLine=this.$foldData[foldIndex];
            varfoldStart=foldLine?foldLine.start.row:Infinity;
            varlen=lines.length;

            for(vari=0;i<len;i++){
                if(i>foldStart){
                    i=foldLine.end.row+1;
                    if(i>=len)
                        break;
                    foldLine=this.$foldData[foldIndex++];
                    foldStart=foldLine?foldLine.start.row:Infinity;
                }

                if(cache[i]==null)
                    cache[i]=this.$getStringScreenWidth(lines[i])[0];

                if(cache[i]>longestScreenLine)
                    longestScreenLine=cache[i];
            }
            this.screenWidth=longestScreenLine;
        }
    };
    this.getLine=function(row){
        returnthis.doc.getLine(row);
    };
    this.getLines=function(firstRow,lastRow){
        returnthis.doc.getLines(firstRow,lastRow);
    };
    this.getLength=function(){
        returnthis.doc.getLength();
    };
    this.getTextRange=function(range){
        returnthis.doc.getTextRange(range||this.selection.getRange());
    };
    this.insert=function(position,text){
        returnthis.doc.insert(position,text);
    };
    this.remove=function(range){
        returnthis.doc.remove(range);
    };
    this.removeFullLines=function(firstRow,lastRow){
        returnthis.doc.removeFullLines(firstRow,lastRow);
    };
    this.undoChanges=function(deltas,dontSelect){
        if(!deltas.length)
            return;

        this.$fromUndo=true;
        for(vari=deltas.length-1;i!=-1;i--){
            vardelta=deltas[i];
            if(delta.action=="insert"||delta.action=="remove"){
                this.doc.revertDelta(delta);
            }elseif(delta.folds){
                this.addFolds(delta.folds);
            }
        }
        if(!dontSelect&&this.$undoSelect){
            if(deltas.selectionBefore)
                this.selection.fromJSON(deltas.selectionBefore);
            else
                this.selection.setRange(this.$getUndoSelection(deltas,true));
        }
        this.$fromUndo=false;
    };
    this.redoChanges=function(deltas,dontSelect){
        if(!deltas.length)
            return;

        this.$fromUndo=true;
        for(vari=0;i<deltas.length;i++){
            vardelta=deltas[i];
            if(delta.action=="insert"||delta.action=="remove"){
                this.doc.applyDelta(delta);
            }
        }

        if(!dontSelect&&this.$undoSelect){
            if(deltas.selectionAfter)
                this.selection.fromJSON(deltas.selectionAfter);
            else
                this.selection.setRange(this.$getUndoSelection(deltas,false));
        }
        this.$fromUndo=false;
    };
    this.setUndoSelect=function(enable){
        this.$undoSelect=enable;
    };

    this.$getUndoSelection=function(deltas,isUndo){
        functionisInsert(delta){
            returnisUndo?delta.action!=="insert":delta.action==="insert";
        }

        varrange,point;
        varlastDeltaIsInsert;

        for(vari=0;i<deltas.length;i++){
            vardelta=deltas[i];
            if(!delta.start)continue;//skipfolds
            if(!range){
                if(isInsert(delta)){
                    range=Range.fromPoints(delta.start,delta.end);
                    lastDeltaIsInsert=true;
                }else{
                    range=Range.fromPoints(delta.start,delta.start);
                    lastDeltaIsInsert=false;
                }
                continue;
            }
            
            if(isInsert(delta)){
                point=delta.start;
                if(range.compare(point.row,point.column)==-1){
                    range.setStart(point);
                }
                point=delta.end;
                if(range.compare(point.row,point.column)==1){
                    range.setEnd(point);
                }
                lastDeltaIsInsert=true;
            }else{
                point=delta.start;
                if(range.compare(point.row,point.column)==-1){
                    range=Range.fromPoints(delta.start,delta.start);
                }
                lastDeltaIsInsert=false;
            }
        }
        returnrange;
    };
    this.replace=function(range,text){
        returnthis.doc.replace(range,text);
    };
    this.moveText=function(fromRange,toPosition,copy){
        vartext=this.getTextRange(fromRange);
        varfolds=this.getFoldsInRange(fromRange);

        vartoRange=Range.fromPoints(toPosition,toPosition);
        if(!copy){
            this.remove(fromRange);
            varrowDiff=fromRange.start.row-fromRange.end.row;
            varcollDiff=rowDiff?-fromRange.end.column:fromRange.start.column-fromRange.end.column;
            if(collDiff){
                if(toRange.start.row==fromRange.end.row&&toRange.start.column>fromRange.end.column)
                    toRange.start.column+=collDiff;
                if(toRange.end.row==fromRange.end.row&&toRange.end.column>fromRange.end.column)
                    toRange.end.column+=collDiff;
            }
            if(rowDiff&&toRange.start.row>=fromRange.end.row){
                toRange.start.row+=rowDiff;
                toRange.end.row+=rowDiff;
            }
        }

        toRange.end=this.insert(toRange.start,text);
        if(folds.length){
            varoldStart=fromRange.start;
            varnewStart=toRange.start;
            varrowDiff=newStart.row-oldStart.row;
            varcollDiff=newStart.column-oldStart.column;
            this.addFolds(folds.map(function(x){
                x=x.clone();
                if(x.start.row==oldStart.row)
                    x.start.column+=collDiff;
                if(x.end.row==oldStart.row)
                    x.end.column+=collDiff;
                x.start.row+=rowDiff;
                x.end.row+=rowDiff;
                returnx;
            }));
        }

        returntoRange;
    };
    this.indentRows=function(startRow,endRow,indentString){
        indentString=indentString.replace(/\t/g,this.getTabString());
        for(varrow=startRow;row<=endRow;row++)
            this.doc.insertInLine({row:row,column:0},indentString);
    };
    this.outdentRows=function(range){
        varrowRange=range.collapseRows();
        vardeleteRange=newRange(0,0,0,0);
        varsize=this.getTabSize();

        for(vari=rowRange.start.row;i<=rowRange.end.row;++i){
            varline=this.getLine(i);

            deleteRange.start.row=i;
            deleteRange.end.row=i;
            for(varj=0;j<size;++j)
                if(line.charAt(j)!='')
                    break;
            if(j<size&&line.charAt(j)=='\t'){
                deleteRange.start.column=j;
                deleteRange.end.column=j+1;
            }else{
                deleteRange.start.column=0;
                deleteRange.end.column=j;
            }
            this.remove(deleteRange);
        }
    };

    this.$moveLines=function(firstRow,lastRow,dir){
        firstRow=this.getRowFoldStart(firstRow);
        lastRow=this.getRowFoldEnd(lastRow);
        if(dir<0){
            varrow=this.getRowFoldStart(firstRow+dir);
            if(row<0)return0;
            vardiff=row-firstRow;
        }elseif(dir>0){
            varrow=this.getRowFoldEnd(lastRow+dir);
            if(row>this.doc.getLength()-1)return0;
            vardiff=row-lastRow;
        }else{
            firstRow=this.$clipRowToDocument(firstRow);
            lastRow=this.$clipRowToDocument(lastRow);
            vardiff=lastRow-firstRow+1;
        }

        varrange=newRange(firstRow,0,lastRow,Number.MAX_VALUE);
        varfolds=this.getFoldsInRange(range).map(function(x){
            x=x.clone();
            x.start.row+=diff;
            x.end.row+=diff;
            returnx;
        });
        
        varlines=dir==0
            ?this.doc.getLines(firstRow,lastRow)
            :this.doc.removeFullLines(firstRow,lastRow);
        this.doc.insertFullLines(firstRow+diff,lines);
        folds.length&&this.addFolds(folds);
        returndiff;
    };
    this.moveLinesUp=function(firstRow,lastRow){
        returnthis.$moveLines(firstRow,lastRow,-1);
    };
    this.moveLinesDown=function(firstRow,lastRow){
        returnthis.$moveLines(firstRow,lastRow,1);
    };
    this.duplicateLines=function(firstRow,lastRow){
        returnthis.$moveLines(firstRow,lastRow,0);
    };


    this.$clipRowToDocument=function(row){
        returnMath.max(0,Math.min(row,this.doc.getLength()-1));
    };

    this.$clipColumnToRow=function(row,column){
        if(column<0)
            return0;
        returnMath.min(this.doc.getLine(row).length,column);
    };


    this.$clipPositionToDocument=function(row,column){
        column=Math.max(0,column);

        if(row<0){
            row=0;
            column=0;
        }else{
            varlen=this.doc.getLength();
            if(row>=len){
                row=len-1;
                column=this.doc.getLine(len-1).length;
            }else{
                column=Math.min(this.doc.getLine(row).length,column);
            }
        }

        return{
            row:row,
            column:column
        };
    };

    this.$clipRangeToDocument=function(range){
        if(range.start.row<0){
            range.start.row=0;
            range.start.column=0;
        }else{
            range.start.column=this.$clipColumnToRow(
                range.start.row,
                range.start.column
            );
        }

        varlen=this.doc.getLength()-1;
        if(range.end.row>len){
            range.end.row=len;
            range.end.column=this.doc.getLine(len).length;
        }else{
            range.end.column=this.$clipColumnToRow(
                range.end.row,
                range.end.column
            );
        }
        returnrange;
    };
    this.$wrapLimit=80;
    this.$useWrapMode=false;
    this.$wrapLimitRange={
        min:null,
        max:null
    };
    this.setUseWrapMode=function(useWrapMode){
        if(useWrapMode!=this.$useWrapMode){
            this.$useWrapMode=useWrapMode;
            this.$modified=true;
            this.$resetRowCache(0);
            if(useWrapMode){
                varlen=this.getLength();
                this.$wrapData=Array(len);
                this.$updateWrapData(0,len-1);
            }

            this._signal("changeWrapMode");
        }
    };
    this.getUseWrapMode=function(){
        returnthis.$useWrapMode;
    };
    this.setWrapLimitRange=function(min,max){
        if(this.$wrapLimitRange.min!==min||this.$wrapLimitRange.max!==max){
            this.$wrapLimitRange={min:min,max:max};
            this.$modified=true;
            this.$bidiHandler.markAsDirty();
            if(this.$useWrapMode)
                this._signal("changeWrapMode");
        }
    };
    this.adjustWrapLimit=function(desiredLimit,$printMargin){
        varlimits=this.$wrapLimitRange;
        if(limits.max<0)
            limits={min:$printMargin,max:$printMargin};
        varwrapLimit=this.$constrainWrapLimit(desiredLimit,limits.min,limits.max);
        if(wrapLimit!=this.$wrapLimit&&wrapLimit>1){
            this.$wrapLimit=wrapLimit;
            this.$modified=true;
            if(this.$useWrapMode){
                this.$updateWrapData(0,this.getLength()-1);
                this.$resetRowCache(0);
                this._signal("changeWrapLimit");
            }
            returntrue;
        }
        returnfalse;
    };

    this.$constrainWrapLimit=function(wrapLimit,min,max){
        if(min)
            wrapLimit=Math.max(min,wrapLimit);

        if(max)
            wrapLimit=Math.min(max,wrapLimit);

        returnwrapLimit;
    };
    this.getWrapLimit=function(){
        returnthis.$wrapLimit;
    };
    this.setWrapLimit=function(limit){
        this.setWrapLimitRange(limit,limit);
    };
    this.getWrapLimitRange=function(){
        return{
            min:this.$wrapLimitRange.min,
            max:this.$wrapLimitRange.max
        };
    };

    this.$updateInternalDataOnChange=function(delta){
        varuseWrapMode=this.$useWrapMode;
        varaction=delta.action;
        varstart=delta.start;
        varend=delta.end;
        varfirstRow=start.row;
        varlastRow=end.row;
        varlen=lastRow-firstRow;
        varremovedFolds=null;
        
        this.$updating=true;
        if(len!=0){
            if(action==="remove"){
                this[useWrapMode?"$wrapData":"$rowLengthCache"].splice(firstRow,len);

                varfoldLines=this.$foldData;
                removedFolds=this.getFoldsInRange(delta);
                this.removeFolds(removedFolds);

                varfoldLine=this.getFoldLine(end.row);
                varidx=0;
                if(foldLine){
                    foldLine.addRemoveChars(end.row,end.column,start.column-end.column);
                    foldLine.shiftRow(-len);

                    varfoldLineBefore=this.getFoldLine(firstRow);
                    if(foldLineBefore&&foldLineBefore!==foldLine){
                        foldLineBefore.merge(foldLine);
                        foldLine=foldLineBefore;
                    }
                    idx=foldLines.indexOf(foldLine)+1;
                }

                for(idx;idx<foldLines.length;idx++){
                    varfoldLine=foldLines[idx];
                    if(foldLine.start.row>=end.row){
                        foldLine.shiftRow(-len);
                    }
                }

                lastRow=firstRow;
            }else{
                varargs=Array(len);
                args.unshift(firstRow,0);
                vararr=useWrapMode?this.$wrapData:this.$rowLengthCache;
                arr.splice.apply(arr,args);
                varfoldLines=this.$foldData;
                varfoldLine=this.getFoldLine(firstRow);
                varidx=0;
                if(foldLine){
                    varcmp=foldLine.range.compareInside(start.row,start.column);
                    if(cmp==0){
                        foldLine=foldLine.split(start.row,start.column);
                        if(foldLine){
                            foldLine.shiftRow(len);
                            foldLine.addRemoveChars(lastRow,0,end.column-start.column);
                        }
                    }else
                    if(cmp==-1){
                        foldLine.addRemoveChars(firstRow,0,end.column-start.column);
                        foldLine.shiftRow(len);
                    }
                    idx=foldLines.indexOf(foldLine)+1;
                }

                for(idx;idx<foldLines.length;idx++){
                    varfoldLine=foldLines[idx];
                    if(foldLine.start.row>=firstRow){
                        foldLine.shiftRow(len);
                    }
                }
            }
        }else{
            len=Math.abs(delta.start.column-delta.end.column);
            if(action==="remove"){
                removedFolds=this.getFoldsInRange(delta);
                this.removeFolds(removedFolds);

                len=-len;
            }
            varfoldLine=this.getFoldLine(firstRow);
            if(foldLine){
                foldLine.addRemoveChars(firstRow,start.column,len);
            }
        }

        if(useWrapMode&&this.$wrapData.length!=this.doc.getLength()){
            console.error("doc.getLength()and$wrapData.lengthhavetobethesame!");
        }
        this.$updating=false;

        if(useWrapMode)
            this.$updateWrapData(firstRow,lastRow);
        else
            this.$updateRowLengthCache(firstRow,lastRow);

        returnremovedFolds;
    };

    this.$updateRowLengthCache=function(firstRow,lastRow,b){
        this.$rowLengthCache[firstRow]=null;
        this.$rowLengthCache[lastRow]=null;
    };

    this.$updateWrapData=function(firstRow,lastRow){
        varlines=this.doc.getAllLines();
        vartabSize=this.getTabSize();
        varwrapData=this.$wrapData;
        varwrapLimit=this.$wrapLimit;
        vartokens;
        varfoldLine;

        varrow=firstRow;
        lastRow=Math.min(lastRow,lines.length-1);
        while(row<=lastRow){
            foldLine=this.getFoldLine(row,foldLine);
            if(!foldLine){
                tokens=this.$getDisplayTokens(lines[row]);
                wrapData[row]=this.$computeWrapSplits(tokens,wrapLimit,tabSize);
                row++;
            }else{
                tokens=[];
                foldLine.walk(function(placeholder,row,column,lastColumn){
                        varwalkTokens;
                        if(placeholder!=null){
                            walkTokens=this.$getDisplayTokens(
                                            placeholder,tokens.length);
                            walkTokens[0]=PLACEHOLDER_START;
                            for(vari=1;i<walkTokens.length;i++){
                                walkTokens[i]=PLACEHOLDER_BODY;
                            }
                        }else{
                            walkTokens=this.$getDisplayTokens(
                                lines[row].substring(lastColumn,column),
                                tokens.length);
                        }
                        tokens=tokens.concat(walkTokens);
                    }.bind(this),
                    foldLine.end.row,
                    lines[foldLine.end.row].length+1
                );

                wrapData[foldLine.start.row]=this.$computeWrapSplits(tokens,wrapLimit,tabSize);
                row=foldLine.end.row+1;
            }
        }
    };
    varCHAR=1,
        CHAR_EXT=2,
        PLACEHOLDER_START=3,
        PLACEHOLDER_BODY= 4,
        PUNCTUATION=9,
        SPACE=10,
        TAB=11,
        TAB_SPACE=12;


    this.$computeWrapSplits=function(tokens,wrapLimit,tabSize){
        if(tokens.length==0){
            return[];
        }

        varsplits=[];
        vardisplayLength=tokens.length;
        varlastSplit=0,lastDocSplit=0;

        varisCode=this.$wrapAsCode;

        varindentedSoftWrap=this.$indentedSoftWrap;
        varmaxIndent=wrapLimit<=Math.max(2*tabSize,8)
            ||indentedSoftWrap===false?0:Math.floor(wrapLimit/2);

        functiongetWrapIndent(){
            varindentation=0;
            if(maxIndent===0)
                returnindentation;
            if(indentedSoftWrap){
                for(vari=0;i<tokens.length;i++){
                    vartoken=tokens[i];
                    if(token==SPACE)
                        indentation+=1;
                    elseif(token==TAB)
                        indentation+=tabSize;
                    elseif(token==TAB_SPACE)
                        continue;
                    else
                        break;
                }
            }
            if(isCode&&indentedSoftWrap!==false)
                indentation+=tabSize;
            returnMath.min(indentation,maxIndent);
        }
        functionaddSplit(screenPos){
            vardisplayed=tokens.slice(lastSplit,screenPos);
            varlen=displayed.length;
            displayed.join("")
                .replace(/12/g,function(){
                    len-=1;
                })
                .replace(/2/g,function(){
                    len-=1;
                });

            if(!splits.length){
                indent=getWrapIndent();
                splits.indent=indent;
            }
            lastDocSplit+=len;
            splits.push(lastDocSplit);
            lastSplit=screenPos;
        }
        varindent=0;
        while(displayLength-lastSplit>wrapLimit-indent){
            varsplit=lastSplit+wrapLimit-indent;
            if(tokens[split-1]>=SPACE&&tokens[split]>=SPACE){
                addSplit(split);
                continue;
            }
            if(tokens[split]==PLACEHOLDER_START||tokens[split]==PLACEHOLDER_BODY){
                for(split;split!=lastSplit-1;split--){
                    if(tokens[split]==PLACEHOLDER_START){
                        break;
                    }
                }
                if(split>lastSplit){
                    addSplit(split);
                    continue;
                }
                split=lastSplit+wrapLimit;
                for(split;split<tokens.length;split++){
                    if(tokens[split]!=PLACEHOLDER_BODY){
                        break;
                    }
                }
                if(split==tokens.length){
                    break; //Breaksthewhile-loop.
                }
                addSplit(split);
                continue;
            }
            varminSplit=Math.max(split-(wrapLimit-(wrapLimit>>2)),lastSplit-1);
            while(split>minSplit&&tokens[split]<PLACEHOLDER_START){
                split--;
            }
            if(isCode){
                while(split>minSplit&&tokens[split]<PLACEHOLDER_START){
                    split--;
                }
                while(split>minSplit&&tokens[split]==PUNCTUATION){
                    split--;
                }
            }else{
                while(split>minSplit&&tokens[split]<SPACE){
                    split--;
                }
            }
            if(split>minSplit){
                addSplit(++split);
                continue;
            }
            split=lastSplit+wrapLimit;
            if(tokens[split]==CHAR_EXT)
                split--;
            addSplit(split-indent);
        }
        returnsplits;
    };
    this.$getDisplayTokens=function(str,offset){
        vararr=[];
        vartabSize;
        offset=offset||0;

        for(vari=0;i<str.length;i++){
            varc=str.charCodeAt(i);
            if(c==9){
                tabSize=this.getScreenTabSize(arr.length+offset);
                arr.push(TAB);
                for(varn=1;n<tabSize;n++){
                    arr.push(TAB_SPACE);
                }
            }
            elseif(c==32){
                arr.push(SPACE);
            }elseif((c>39&&c<48)||(c>57&&c<64)){
                arr.push(PUNCTUATION);
            }
            elseif(c>=0x1100&&isFullWidth(c)){
                arr.push(CHAR,CHAR_EXT);
            }else{
                arr.push(CHAR);
            }
        }
        returnarr;
    };
    this.$getStringScreenWidth=function(str,maxScreenColumn,screenColumn){
        if(maxScreenColumn==0)
            return[0,0];
        if(maxScreenColumn==null)
            maxScreenColumn=Infinity;
        screenColumn=screenColumn||0;

        varc,column;
        for(column=0;column<str.length;column++){
            c=str.charCodeAt(column);
            if(c==9){
                screenColumn+=this.getScreenTabSize(screenColumn);
            }
            elseif(c>=0x1100&&isFullWidth(c)){
                screenColumn+=2;
            }else{
                screenColumn+=1;
            }
            if(screenColumn>maxScreenColumn){
                break;
            }
        }

        return[screenColumn,column];
    };

    this.lineWidgets=null;
    this.getRowLength=function(row){
        if(this.lineWidgets)
            varh=this.lineWidgets[row]&&this.lineWidgets[row].rowCount||0;
        else
            h=0;
        if(!this.$useWrapMode||!this.$wrapData[row]){
            return1+h;
        }else{
            returnthis.$wrapData[row].length+1+h;
        }
    };
    this.getRowLineCount=function(row){
        if(!this.$useWrapMode||!this.$wrapData[row]){
            return1;
        }else{
            returnthis.$wrapData[row].length+1;
        }
    };

    this.getRowWrapIndent=function(screenRow){
        if(this.$useWrapMode){
            varpos=this.screenToDocumentPosition(screenRow,Number.MAX_VALUE);
            varsplits=this.$wrapData[pos.row];
            returnsplits.length&&splits[0]<pos.column?splits.indent:0;
        }else{
            return0;
        }
    };
    this.getScreenLastRowColumn=function(screenRow){
        varpos=this.screenToDocumentPosition(screenRow,Number.MAX_VALUE);
        returnthis.documentToScreenColumn(pos.row,pos.column);
    };
    this.getDocumentLastRowColumn=function(docRow,docColumn){
        varscreenRow=this.documentToScreenRow(docRow,docColumn);
        returnthis.getScreenLastRowColumn(screenRow);
    };
    this.getDocumentLastRowColumnPosition=function(docRow,docColumn){
        varscreenRow=this.documentToScreenRow(docRow,docColumn);
        returnthis.screenToDocumentPosition(screenRow,Number.MAX_VALUE/10);
    };
    this.getRowSplitData=function(row){
        if(!this.$useWrapMode){
            returnundefined;
        }else{
            returnthis.$wrapData[row];
        }
    };
    this.getScreenTabSize=function(screenColumn){
        returnthis.$tabSize-screenColumn%this.$tabSize;
    };


    this.screenToDocumentRow=function(screenRow,screenColumn){
        returnthis.screenToDocumentPosition(screenRow,screenColumn).row;
    };


    this.screenToDocumentColumn=function(screenRow,screenColumn){
        returnthis.screenToDocumentPosition(screenRow,screenColumn).column;
    };
    this.screenToDocumentPosition=function(screenRow,screenColumn,offsetX){
        if(screenRow<0)
            return{row:0,column:0};

        varline;
        vardocRow=0;
        vardocColumn=0;
        varcolumn;
        varrow=0;
        varrowLength=0;

        varrowCache=this.$screenRowCache;
        vari=this.$getRowCacheIndex(rowCache,screenRow);
        varl=rowCache.length;
        if(l&&i>=0){
            varrow=rowCache[i];
            vardocRow=this.$docRowCache[i];
            vardoCache=screenRow>rowCache[l-1];
        }else{
            vardoCache=!l;
        }

        varmaxRow=this.getLength()-1;
        varfoldLine=this.getNextFoldLine(docRow);
        varfoldStart=foldLine?foldLine.start.row:Infinity;

        while(row<=screenRow){
            rowLength=this.getRowLength(docRow);
            if(row+rowLength>screenRow||docRow>=maxRow){
                break;
            }else{
                row+=rowLength;
                docRow++;
                if(docRow>foldStart){
                    docRow=foldLine.end.row+1;
                    foldLine=this.getNextFoldLine(docRow,foldLine);
                    foldStart=foldLine?foldLine.start.row:Infinity;
                }
            }

            if(doCache){
                this.$docRowCache.push(docRow);
                this.$screenRowCache.push(row);
            }
        }

        if(foldLine&&foldLine.start.row<=docRow){
            line=this.getFoldDisplayLine(foldLine);
            docRow=foldLine.start.row;
        }elseif(row+rowLength<=screenRow||docRow>maxRow){
            return{
                row:maxRow,
                column:this.getLine(maxRow).length
            };
        }else{
            line=this.getLine(docRow);
            foldLine=null;
        }
        varwrapIndent=0,splitIndex=Math.floor(screenRow-row);
        if(this.$useWrapMode){
            varsplits=this.$wrapData[docRow];
            if(splits){
                column=splits[splitIndex];
                if(splitIndex>0&&splits.length){
                    wrapIndent=splits.indent;
                    docColumn=splits[splitIndex-1]||splits[splits.length-1];
                    line=line.substring(docColumn);
                }
            }
        }

        if(offsetX!==undefined&&this.$bidiHandler.isBidiRow(row+splitIndex,docRow,splitIndex))
            screenColumn=this.$bidiHandler.offsetToCol(offsetX);

        docColumn+=this.$getStringScreenWidth(line,screenColumn-wrapIndent)[1];
        if(this.$useWrapMode&&docColumn>=column)
            docColumn=column-1;

        if(foldLine)
            returnfoldLine.idxToPosition(docColumn);

        return{row:docRow,column:docColumn};
    };
    this.documentToScreenPosition=function(docRow,docColumn){
        if(typeofdocColumn==="undefined")
            varpos=this.$clipPositionToDocument(docRow.row,docRow.column);
        else
            pos=this.$clipPositionToDocument(docRow,docColumn);

        docRow=pos.row;
        docColumn=pos.column;

        varscreenRow=0;
        varfoldStartRow=null;
        varfold=null;
        fold=this.getFoldAt(docRow,docColumn,1);
        if(fold){
            docRow=fold.start.row;
            docColumn=fold.start.column;
        }

        varrowEnd,row=0;


        varrowCache=this.$docRowCache;
        vari=this.$getRowCacheIndex(rowCache,docRow);
        varl=rowCache.length;
        if(l&&i>=0){
            varrow=rowCache[i];
            varscreenRow=this.$screenRowCache[i];
            vardoCache=docRow>rowCache[l-1];
        }else{
            vardoCache=!l;
        }

        varfoldLine=this.getNextFoldLine(row);
        varfoldStart=foldLine?foldLine.start.row:Infinity;

        while(row<docRow){
            if(row>=foldStart){
                rowEnd=foldLine.end.row+1;
                if(rowEnd>docRow)
                    break;
                foldLine=this.getNextFoldLine(rowEnd,foldLine);
                foldStart=foldLine?foldLine.start.row:Infinity;
            }
            else{
                rowEnd=row+1;
            }

            screenRow+=this.getRowLength(row);
            row=rowEnd;

            if(doCache){
                this.$docRowCache.push(row);
                this.$screenRowCache.push(screenRow);
            }
        }
        vartextLine="";
        if(foldLine&&row>=foldStart){
            textLine=this.getFoldDisplayLine(foldLine,docRow,docColumn);
            foldStartRow=foldLine.start.row;
        }else{
            textLine=this.getLine(docRow).substring(0,docColumn);
            foldStartRow=docRow;
        }
        varwrapIndent=0;
        if(this.$useWrapMode){
            varwrapRow=this.$wrapData[foldStartRow];
            if(wrapRow){
                varscreenRowOffset=0;
                while(textLine.length>=wrapRow[screenRowOffset]){
                    screenRow++;
                    screenRowOffset++;
                }
                textLine=textLine.substring(
                    wrapRow[screenRowOffset-1]||0,textLine.length
                );
                wrapIndent=screenRowOffset>0?wrapRow.indent:0;
            }
        }

        return{
            row:screenRow,
            column:wrapIndent+this.$getStringScreenWidth(textLine)[0]
        };
    };
    this.documentToScreenColumn=function(row,docColumn){
        returnthis.documentToScreenPosition(row,docColumn).column;
    };
    this.documentToScreenRow=function(docRow,docColumn){
        returnthis.documentToScreenPosition(docRow,docColumn).row;
    };
    this.getScreenLength=function(){
        varscreenRows=0;
        varfold=null;
        if(!this.$useWrapMode){
            screenRows=this.getLength();
            varfoldData=this.$foldData;
            for(vari=0;i<foldData.length;i++){
                fold=foldData[i];
                screenRows-=fold.end.row-fold.start.row;
            }
        }else{
            varlastRow=this.$wrapData.length;
            varrow=0,i=0;
            varfold=this.$foldData[i++];
            varfoldStart=fold?fold.start.row:Infinity;

            while(row<lastRow){
                varsplits=this.$wrapData[row];
                screenRows+=splits?splits.length+1:1;
                row++;
                if(row>foldStart){
                    row=fold.end.row+1;
                    fold=this.$foldData[i++];
                    foldStart=fold?fold.start.row:Infinity;
                }
            }
        }
        if(this.lineWidgets)
            screenRows+=this.$getWidgetScreenLength();

        returnscreenRows;
    };
    this.$setFontMetrics=function(fm){
        if(!this.$enableVarChar)return;
        this.$getStringScreenWidth=function(str,maxScreenColumn,screenColumn){
            if(maxScreenColumn===0)
                return[0,0];
            if(!maxScreenColumn)
                maxScreenColumn=Infinity;
            screenColumn=screenColumn||0;
            
            varc,column;
            for(column=0;column<str.length;column++){
                c=str.charAt(column);
                if(c==="\t"){
                    screenColumn+=this.getScreenTabSize(screenColumn);
                }else{
                    screenColumn+=fm.getCharacterWidth(c);
                }
                if(screenColumn>maxScreenColumn){
                    break;
                }
            }
            
            return[screenColumn,column];
        };
    };
    
    this.destroy=function(){
        if(this.bgTokenizer){
            this.bgTokenizer.setDocument(null);
            this.bgTokenizer=null;
        }
        this.$stopWorker();
    };

    this.isFullWidth=isFullWidth;
    functionisFullWidth(c){
        if(c<0x1100)
            returnfalse;
        returnc>=0x1100&&c<=0x115F||
               c>=0x11A3&&c<=0x11A7||
               c>=0x11FA&&c<=0x11FF||
               c>=0x2329&&c<=0x232A||
               c>=0x2E80&&c<=0x2E99||
               c>=0x2E9B&&c<=0x2EF3||
               c>=0x2F00&&c<=0x2FD5||
               c>=0x2FF0&&c<=0x2FFB||
               c>=0x3000&&c<=0x303E||
               c>=0x3041&&c<=0x3096||
               c>=0x3099&&c<=0x30FF||
               c>=0x3105&&c<=0x312D||
               c>=0x3131&&c<=0x318E||
               c>=0x3190&&c<=0x31BA||
               c>=0x31C0&&c<=0x31E3||
               c>=0x31F0&&c<=0x321E||
               c>=0x3220&&c<=0x3247||
               c>=0x3250&&c<=0x32FE||
               c>=0x3300&&c<=0x4DBF||
               c>=0x4E00&&c<=0xA48C||
               c>=0xA490&&c<=0xA4C6||
               c>=0xA960&&c<=0xA97C||
               c>=0xAC00&&c<=0xD7A3||
               c>=0xD7B0&&c<=0xD7C6||
               c>=0xD7CB&&c<=0xD7FB||
               c>=0xF900&&c<=0xFAFF||
               c>=0xFE10&&c<=0xFE19||
               c>=0xFE30&&c<=0xFE52||
               c>=0xFE54&&c<=0xFE66||
               c>=0xFE68&&c<=0xFE6B||
               c>=0xFF01&&c<=0xFF60||
               c>=0xFFE0&&c<=0xFFE6;
    }

}).call(EditSession.prototype);

require("./edit_session/folding").Folding.call(EditSession.prototype);
require("./edit_session/bracket_match").BracketMatch.call(EditSession.prototype);


config.defineOptions(EditSession.prototype,"session",{
    wrap:{
        set:function(value){
            if(!value||value=="off")
                value=false;
            elseif(value=="free")
                value=true;
            elseif(value=="printMargin")
                value=-1;
            elseif(typeofvalue=="string")
                value=parseInt(value,10)||false;

            if(this.$wrap==value)
                return;
            this.$wrap=value;
            if(!value){
                this.setUseWrapMode(false);
            }else{
                varcol=typeofvalue=="number"?value:null;
                this.setWrapLimitRange(col,col);
                this.setUseWrapMode(true);
            }
        },
        get:function(){
            if(this.getUseWrapMode()){
                if(this.$wrap==-1)
                    return"printMargin";
                if(!this.getWrapLimitRange().min)
                    return"free";
                returnthis.$wrap;
            }
            return"off";
        },
        handlesSet:true
    },   
    wrapMethod:{
        set:function(val){
            val=val=="auto"
                ?this.$mode.type!="text"
                :val!="text";
            if(val!=this.$wrapAsCode){
                this.$wrapAsCode=val;
                if(this.$useWrapMode){
                    this.$modified=true;
                    this.$resetRowCache(0);
                    this.$updateWrapData(0,this.getLength()-1);
                }
            }
        },
        initialValue:"auto"
    },
    indentedSoftWrap:{initialValue:true},
    firstLineNumber:{
        set:function(){this._signal("changeBreakpoint");},
        initialValue:1
    },
    useWorker:{
        set:function(useWorker){
            this.$useWorker=useWorker;

            this.$stopWorker();
            if(useWorker)
                this.$startWorker();
        },
        initialValue:true
    },
    useSoftTabs:{initialValue:true},
    tabSize:{
        set:function(tabSize){
            if(isNaN(tabSize)||this.$tabSize===tabSize)return;

            this.$modified=true;
            this.$rowLengthCache=[];
            this.$tabSize=tabSize;
            this._signal("changeTabSize");
        },
        initialValue:4,
        handlesSet:true
    },
    navigateWithinSoftTabs:{initialValue:false},
    foldStyle:{
        set:function(val){this.setFoldStyle(val);},
        handlesSet:true
    },
    overwrite:{
        set:function(val){this._signal("changeOverwrite");},
        initialValue:false
    },
    newLineMode:{
        set:function(val){this.doc.setNewLineMode(val);},
        get:function(){returnthis.doc.getNewLineMode();},
        handlesSet:true
    },
    mode:{
        set:function(val){this.setMode(val);},
        get:function(){returnthis.$modeId;}
    }
});

exports.EditSession=EditSession;
});

define("ace/search",["require","exports","module","ace/lib/lang","ace/lib/oop","ace/range"],function(require,exports,module){
"usestrict";

varlang=require("./lib/lang");
varoop=require("./lib/oop");
varRange=require("./range").Range;

varSearch=function(){
    this.$options={};
};

(function(){
    this.set=function(options){
        oop.mixin(this.$options,options);
        returnthis;
    };
    this.getOptions=function(){
        returnlang.copyObject(this.$options);
    };
    this.setOptions=function(options){
        this.$options=options;
    };
    this.find=function(session){
        varoptions=this.$options;
        variterator=this.$matchIterator(session,options);
        if(!iterator)
            returnfalse;

        varfirstRange=null;
        iterator.forEach(function(sr,sc,er,ec){
            firstRange=newRange(sr,sc,er,ec);
            if(sc==ec&&options.start&&options.start.start
                &&options.skipCurrent!=false&&firstRange.isEqual(options.start)
            ){
                firstRange=null;
                returnfalse;
            }
            
            returntrue;
        });

        returnfirstRange;
    };
    this.findAll=function(session){
        varoptions=this.$options;
        if(!options.needle)
            return[];
        this.$assembleRegExp(options);

        varrange=options.range;
        varlines=range
            ?session.getLines(range.start.row,range.end.row)
            :session.doc.getAllLines();

        varranges=[];
        varre=options.re;
        if(options.$isMultiLine){
            varlen=re.length;
            varmaxRow=lines.length-len;
            varprevRange;
            outer:for(varrow=re.offset||0;row<=maxRow;row++){
                for(varj=0;j<len;j++)
                    if(lines[row+j].search(re[j])==-1)
                        continueouter;
                
                varstartLine=lines[row];
                varline=lines[row+len-1];
                varstartIndex=startLine.length-startLine.match(re[0])[0].length;
                varendIndex=line.match(re[len-1])[0].length;
                
                if(prevRange&&prevRange.end.row===row&&
                    prevRange.end.column>startIndex
                ){
                    continue;
                }
                ranges.push(prevRange=newRange(
                    row,startIndex,row+len-1,endIndex
                ));
                if(len>2)
                    row=row+len-2;
            }
        }else{
            for(vari=0;i<lines.length;i++){
                varmatches=lang.getMatchOffsets(lines[i],re);
                for(varj=0;j<matches.length;j++){
                    varmatch=matches[j];
                    ranges.push(newRange(i,match.offset,i,match.offset+match.length));
                }
            }
        }

        if(range){
            varstartColumn=range.start.column;
            varendColumn=range.start.column;
            vari=0,j=ranges.length-1;
            while(i<j&&ranges[i].start.column<startColumn&&ranges[i].start.row==range.start.row)
                i++;

            while(i<j&&ranges[j].end.column>endColumn&&ranges[j].end.row==range.end.row)
                j--;
            
            ranges=ranges.slice(i,j+1);
            for(i=0,j=ranges.length;i<j;i++){
                ranges[i].start.row+=range.start.row;
                ranges[i].end.row+=range.start.row;
            }
        }

        returnranges;
    };
    this.replace=function(input,replacement){
        varoptions=this.$options;

        varre=this.$assembleRegExp(options);
        if(options.$isMultiLine)
            returnreplacement;

        if(!re)
            return;

        varmatch=re.exec(input);
        if(!match||match[0].length!=input.length)
            returnnull;
        
        replacement=input.replace(re,replacement);
        if(options.preserveCase){
            replacement=replacement.split("");
            for(vari=Math.min(input.length,input.length);i--;){
                varch=input[i];
                if(ch&&ch.toLowerCase()!=ch)
                    replacement[i]=replacement[i].toUpperCase();
                else
                    replacement[i]=replacement[i].toLowerCase();
            }
            replacement=replacement.join("");
        }
        
        returnreplacement;
    };

    this.$assembleRegExp=function(options,$disableFakeMultiline){
        if(options.needleinstanceofRegExp)
            returnoptions.re=options.needle;

        varneedle=options.needle;

        if(!options.needle)
            returnoptions.re=false;

        if(!options.regExp)
            needle=lang.escapeRegExp(needle);

        if(options.wholeWord)
            needle=addWordBoundary(needle,options);

        varmodifier=options.caseSensitive?"gm":"gmi";

        options.$isMultiLine=!$disableFakeMultiline&&/[\n\r]/.test(needle);
        if(options.$isMultiLine)
            returnoptions.re=this.$assembleMultilineRegExp(needle,modifier);

        try{
            varre=newRegExp(needle,modifier);
        }catch(e){
            re=false;
        }
        returnoptions.re=re;
    };

    this.$assembleMultilineRegExp=function(needle,modifier){
        varparts=needle.replace(/\r\n|\r|\n/g,"$\n^").split("\n");
        varre=[];
        for(vari=0;i<parts.length;i++)try{
            re.push(newRegExp(parts[i],modifier));
        }catch(e){
            returnfalse;
        }
        returnre;
    };

    this.$matchIterator=function(session,options){
        varre=this.$assembleRegExp(options);
        if(!re)
            returnfalse;
        varbackwards=options.backwards==true;
        varskipCurrent=options.skipCurrent!=false;

        varrange=options.range;
        varstart=options.start;
        if(!start)
            start=range?range[backwards?"end":"start"]:session.selection.getRange();
         
        if(start.start)
            start=start[skipCurrent!=backwards?"end":"start"];

        varfirstRow=range?range.start.row:0;
        varlastRow=range?range.end.row:session.getLength()-1;
        
        if(backwards){
            varforEach=function(callback){
                varrow=start.row;
                if(forEachInLine(row,start.column,callback))
                    return;
                for(row--;row>=firstRow;row--)
                    if(forEachInLine(row,Number.MAX_VALUE,callback))
                        return;
                if(options.wrap==false)
                    return;
                for(row=lastRow,firstRow=start.row;row>=firstRow;row--)
                    if(forEachInLine(row,Number.MAX_VALUE,callback))
                        return;
            };
        }
        else{
            varforEach=function(callback){
                varrow=start.row;
                if(forEachInLine(row,start.column,callback))
                    return;
                for(row=row+1;row<=lastRow;row++)
                    if(forEachInLine(row,0,callback))
                        return;
                if(options.wrap==false)
                    return;
                for(row=firstRow,lastRow=start.row;row<=lastRow;row++)
                    if(forEachInLine(row,0,callback))
                        return;
            };
        }
        
        if(options.$isMultiLine){
            varlen=re.length;
            varforEachInLine=function(row,offset,callback){
                varstartRow=backwards?row-len+1:row;
                if(startRow<0)return;
                varline=session.getLine(startRow);
                varstartIndex=line.search(re[0]);
                if(!backwards&&startIndex<offset||startIndex===-1)return;
                for(vari=1;i<len;i++){
                    line=session.getLine(startRow+i);
                    if(line.search(re[i])==-1)
                        return;
                }
                varendIndex=line.match(re[len-1])[0].length;
                if(backwards&&endIndex>offset)return;
                if(callback(startRow,startIndex,startRow+len-1,endIndex))
                    returntrue;
            };
        }
        elseif(backwards){
            varforEachInLine=function(row,endIndex,callback){
                varline=session.getLine(row);
                varmatches=[];
                varm,last=0;
                re.lastIndex=0;
                while((m=re.exec(line))){
                    varlength=m[0].length;
                    last=m.index;
                    if(!length){
                        if(last>=line.length)break;
                        re.lastIndex=last+=1;
                    }
                    if(m.index+length>endIndex)
                        break;
                    matches.push(m.index,length);
                }
                for(vari=matches.length-1;i>=0;i-=2){
                    varcolumn=matches[i-1];
                    varlength=matches[i];
                    if(callback(row,column,row,column+length))
                        returntrue;
                }
            };
        }
        else{
            varforEachInLine=function(row,startIndex,callback){
                varline=session.getLine(row);
                varlast;
                varm;
                re.lastIndex=startIndex;
                while((m=re.exec(line))){
                    varlength=m[0].length;
                    last=m.index;
                    if(callback(row,last,row,last+length))
                        returntrue;
                    if(!length){
                        re.lastIndex=last+=1;
                        if(last>=line.length)returnfalse;
                    }
                }
            };
        }
        return{forEach:forEach};
    };

}).call(Search.prototype);

functionaddWordBoundary(needle,options){
    functionwordBoundary(c){
        if(/\w/.test(c)||options.regExp)return"\\b";
        return"";
    }
    returnwordBoundary(needle[0])+needle
        +wordBoundary(needle[needle.length-1]);
}

exports.Search=Search;
});

define("ace/keyboard/hash_handler",["require","exports","module","ace/lib/keys","ace/lib/useragent"],function(require,exports,module){
"usestrict";

varkeyUtil=require("../lib/keys");
varuseragent=require("../lib/useragent");
varKEY_MODS=keyUtil.KEY_MODS;

functionHashHandler(config,platform){
    this.platform=platform||(useragent.isMac?"mac":"win");
    this.commands={};
    this.commandKeyBinding={};
    this.addCommands(config);
    this.$singleCommand=true;
}

functionMultiHashHandler(config,platform){
    HashHandler.call(this,config,platform);
    this.$singleCommand=false;
}

MultiHashHandler.prototype=HashHandler.prototype;

(function(){
    

    this.addCommand=function(command){
        if(this.commands[command.name])
            this.removeCommand(command);

        this.commands[command.name]=command;

        if(command.bindKey)
            this._buildKeyHash(command);
    };

    this.removeCommand=function(command,keepCommand){
        varname=command&&(typeofcommand==='string'?command:command.name);
        command=this.commands[name];
        if(!keepCommand)
            deletethis.commands[name];
        varckb=this.commandKeyBinding;
        for(varkeyIdinckb){
            varcmdGroup=ckb[keyId];
            if(cmdGroup==command){
                deleteckb[keyId];
            }elseif(Array.isArray(cmdGroup)){
                vari=cmdGroup.indexOf(command);
                if(i!=-1){
                    cmdGroup.splice(i,1);
                    if(cmdGroup.length==1)
                        ckb[keyId]=cmdGroup[0];
                }
            }
        }
    };

    this.bindKey=function(key,command,position){
        if(typeofkey=="object"&&key){
            if(position==undefined)
                position=key.position;
            key=key[this.platform];
        }
        if(!key)
            return;
        if(typeofcommand=="function")
            returnthis.addCommand({exec:command,bindKey:key,name:command.name||key});
        
        key.split("|").forEach(function(keyPart){
            varchain="";
            if(keyPart.indexOf("")!=-1){
                varparts=keyPart.split(/\s+/);
                keyPart=parts.pop();
                parts.forEach(function(keyPart){
                    varbinding=this.parseKeys(keyPart);
                    varid=KEY_MODS[binding.hashId]+binding.key;
                    chain+=(chain?"":"")+id;
                    this._addCommandToBinding(chain,"chainKeys");
                },this);
                chain+="";
            }
            varbinding=this.parseKeys(keyPart);
            varid=KEY_MODS[binding.hashId]+binding.key;
            this._addCommandToBinding(chain+id,command,position);
        },this);
    };
    
    functiongetPosition(command){
        returntypeofcommand=="object"&&command.bindKey
            &&command.bindKey.position
            ||(command.isDefault?-100:0);
    }
    this._addCommandToBinding=function(keyId,command,position){
        varckb=this.commandKeyBinding,i;
        if(!command){
            deleteckb[keyId];
        }elseif(!ckb[keyId]||this.$singleCommand){
            ckb[keyId]=command;
        }else{
            if(!Array.isArray(ckb[keyId])){
                ckb[keyId]=[ckb[keyId]];
            }elseif((i=ckb[keyId].indexOf(command))!=-1){
                ckb[keyId].splice(i,1);
            }
            
            if(typeofposition!="number"){
                position=getPosition(command);
            }

            varcommands=ckb[keyId];
            for(i=0;i<commands.length;i++){
                varother=commands[i];
                varotherPos=getPosition(other);
                if(otherPos>position)
                    break;
            }
            commands.splice(i,0,command);
        }
    };

    this.addCommands=function(commands){
        commands&&Object.keys(commands).forEach(function(name){
            varcommand=commands[name];
            if(!command)
                return;
            
            if(typeofcommand==="string")
                returnthis.bindKey(command,name);

            if(typeofcommand==="function")
                command={exec:command};

            if(typeofcommand!=="object")
                return;

            if(!command.name)
                command.name=name;

            this.addCommand(command);
        },this);
    };

    this.removeCommands=function(commands){
        Object.keys(commands).forEach(function(name){
            this.removeCommand(commands[name]);
        },this);
    };

    this.bindKeys=function(keyList){
        Object.keys(keyList).forEach(function(key){
            this.bindKey(key,keyList[key]);
        },this);
    };

    this._buildKeyHash=function(command){
        this.bindKey(command.bindKey,command);
    };
    this.parseKeys=function(keys){
        varparts=keys.toLowerCase().split(/[\-\+]([\-\+])?/).filter(function(x){returnx;});
        varkey=parts.pop();

        varkeyCode=keyUtil[key];
        if(keyUtil.FUNCTION_KEYS[keyCode])
            key=keyUtil.FUNCTION_KEYS[keyCode].toLowerCase();
        elseif(!parts.length)
            return{key:key,hashId:-1};
        elseif(parts.length==1&&parts[0]=="shift")
            return{key:key.toUpperCase(),hashId:-1};

        varhashId=0;
        for(vari=parts.length;i--;){
            varmodifier=keyUtil.KEY_MODS[parts[i]];
            if(modifier==null){
                if(typeofconsole!="undefined")
                    console.error("invalidmodifier"+parts[i]+"in"+keys);
                returnfalse;
            }
            hashId|=modifier;
        }
        return{key:key,hashId:hashId};
    };

    this.findKeyCommand=functionfindKeyCommand(hashId,keyString){
        varkey=KEY_MODS[hashId]+keyString;
        returnthis.commandKeyBinding[key];
    };

    this.handleKeyboard=function(data,hashId,keyString,keyCode){
        if(keyCode<0)return;
        varkey=KEY_MODS[hashId]+keyString;
        varcommand=this.commandKeyBinding[key];
        if(data.$keyChain){
            data.$keyChain+=""+key;
            command=this.commandKeyBinding[data.$keyChain]||command;
        }
        
        if(command){
            if(command=="chainKeys"||command[command.length-1]=="chainKeys"){
                data.$keyChain=data.$keyChain||key;
                return{command:"null"};
            }
        }
        
        if(data.$keyChain){
            if((!hashId||hashId==4)&&keyString.length==1)
                data.$keyChain=data.$keyChain.slice(0,-key.length-1);//waitforinput
            elseif(hashId==-1||keyCode>0)
                data.$keyChain="";//resetkeyChain
        }
        return{command:command};
    };
    
    this.getStatusText=function(editor,data){
        returndata.$keyChain||"";
    };

}).call(HashHandler.prototype);

exports.HashHandler=HashHandler;
exports.MultiHashHandler=MultiHashHandler;
});

define("ace/commands/command_manager",["require","exports","module","ace/lib/oop","ace/keyboard/hash_handler","ace/lib/event_emitter"],function(require,exports,module){
"usestrict";

varoop=require("../lib/oop");
varMultiHashHandler=require("../keyboard/hash_handler").MultiHashHandler;
varEventEmitter=require("../lib/event_emitter").EventEmitter;

varCommandManager=function(platform,commands){
    MultiHashHandler.call(this,commands,platform);
    this.byName=this.commands;
    this.setDefaultHandler("exec",function(e){
        returne.command.exec(e.editor,e.args||{});
    });
};

oop.inherits(CommandManager,MultiHashHandler);

(function(){

    oop.implement(this,EventEmitter);

    this.exec=function(command,editor,args){
        if(Array.isArray(command)){
            for(vari=command.length;i--;){
                if(this.exec(command[i],editor,args))returntrue;
            }
            returnfalse;
        }

        if(typeofcommand==="string")
            command=this.commands[command];

        if(!command)
            returnfalse;

        if(editor&&editor.$readOnly&&!command.readOnly)
            returnfalse;

        if(command.isAvailable&&!command.isAvailable(editor))
            returnfalse;

        vare={editor:editor,command:command,args:args};
        e.returnValue=this._emit("exec",e);
        this._signal("afterExec",e);

        returne.returnValue===false?false:true;
    };

    this.toggleRecording=function(editor){
        if(this.$inReplay)
            return;

        editor&&editor._emit("changeStatus");
        if(this.recording){
            this.macro.pop();
            this.removeEventListener("exec",this.$addCommandToMacro);

            if(!this.macro.length)
                this.macro=this.oldMacro;

            returnthis.recording=false;
        }
        if(!this.$addCommandToMacro){
            this.$addCommandToMacro=function(e){
                this.macro.push([e.command,e.args]);
            }.bind(this);
        }

        this.oldMacro=this.macro;
        this.macro=[];
        this.on("exec",this.$addCommandToMacro);
        returnthis.recording=true;
    };

    this.replay=function(editor){
        if(this.$inReplay||!this.macro)
            return;

        if(this.recording)
            returnthis.toggleRecording(editor);

        try{
            this.$inReplay=true;
            this.macro.forEach(function(x){
                if(typeofx=="string")
                    this.exec(x,editor);
                else
                    this.exec(x[0],editor,x[1]);
            },this);
        }finally{
            this.$inReplay=false;
        }
    };

    this.trimMacro=function(m){
        returnm.map(function(x){
            if(typeofx[0]!="string")
                x[0]=x[0].name;
            if(!x[1])
                x=x[0];
            returnx;
        });
    };

}).call(CommandManager.prototype);

exports.CommandManager=CommandManager;

});

define("ace/commands/default_commands",["require","exports","module","ace/lib/lang","ace/config","ace/range"],function(require,exports,module){
"usestrict";

varlang=require("../lib/lang");
varconfig=require("../config");
varRange=require("../range").Range;

functionbindKey(win,mac){
    return{win:win,mac:mac};
}
exports.commands=[{
    name:"showSettingsMenu",
    bindKey:bindKey("Ctrl-,","Command-,"),
    exec:function(editor){
        config.loadModule("ace/ext/settings_menu",function(module){
            module.init(editor);
            editor.showSettingsMenu();
        });
    },
    readOnly:true
},{
    name:"goToNextError",
    bindKey:bindKey("Alt-E","F4"),
    exec:function(editor){
        config.loadModule("./ext/error_marker",function(module){
            module.showErrorMarker(editor,1);
        });
    },
    scrollIntoView:"animate",
    readOnly:true
},{
    name:"goToPreviousError",
    bindKey:bindKey("Alt-Shift-E","Shift-F4"),
    exec:function(editor){
        config.loadModule("./ext/error_marker",function(module){
            module.showErrorMarker(editor,-1);
        });
    },
    scrollIntoView:"animate",
    readOnly:true
},{
    name:"selectall",
    bindKey:bindKey("Ctrl-A","Command-A"),
    exec:function(editor){editor.selectAll();},
    readOnly:true
},{
    name:"centerselection",
    bindKey:bindKey(null,"Ctrl-L"),
    exec:function(editor){editor.centerSelection();},
    readOnly:true
},{
    name:"gotoline",
    bindKey:bindKey("Ctrl-L","Command-L"),
    exec:function(editor,line){
        if(typeofline!=="number")
            line=parseInt(prompt("Enterlinenumber:"),10);
        if(!isNaN(line)){
            editor.gotoLine(line);
        }
    },
    readOnly:true
},{
    name:"fold",
    bindKey:bindKey("Alt-L|Ctrl-F1","Command-Alt-L|Command-F1"),
    exec:function(editor){editor.session.toggleFold(false);},
    multiSelectAction:"forEach",
    scrollIntoView:"center",
    readOnly:true
},{
    name:"unfold",
    bindKey:bindKey("Alt-Shift-L|Ctrl-Shift-F1","Command-Alt-Shift-L|Command-Shift-F1"),
    exec:function(editor){editor.session.toggleFold(true);},
    multiSelectAction:"forEach",
    scrollIntoView:"center",
    readOnly:true
},{
    name:"toggleFoldWidget",
    bindKey:bindKey("F2","F2"),
    exec:function(editor){editor.session.toggleFoldWidget();},
    multiSelectAction:"forEach",
    scrollIntoView:"center",
    readOnly:true
},{
    name:"toggleParentFoldWidget",
    bindKey:bindKey("Alt-F2","Alt-F2"),
    exec:function(editor){editor.session.toggleFoldWidget(true);},
    multiSelectAction:"forEach",
    scrollIntoView:"center",
    readOnly:true
},{
    name:"foldall",
    bindKey:bindKey(null,"Ctrl-Command-Option-0"),
    exec:function(editor){editor.session.foldAll();},
    scrollIntoView:"center",
    readOnly:true
},{
    name:"foldOther",
    bindKey:bindKey("Alt-0","Command-Option-0"),
    exec:function(editor){
        editor.session.foldAll();
        editor.session.unfold(editor.selection.getAllRanges());
    },
    scrollIntoView:"center",
    readOnly:true
},{
    name:"unfoldall",
    bindKey:bindKey("Alt-Shift-0","Command-Option-Shift-0"),
    exec:function(editor){editor.session.unfold();},
    scrollIntoView:"center",
    readOnly:true
},{
    name:"findnext",
    bindKey:bindKey("Ctrl-K","Command-G"),
    exec:function(editor){editor.findNext();},
    multiSelectAction:"forEach",
    scrollIntoView:"center",
    readOnly:true
},{
    name:"findprevious",
    bindKey:bindKey("Ctrl-Shift-K","Command-Shift-G"),
    exec:function(editor){editor.findPrevious();},
    multiSelectAction:"forEach",
    scrollIntoView:"center",
    readOnly:true
},{
    name:"selectOrFindNext",
    bindKey:bindKey("Alt-K","Ctrl-G"),
    exec:function(editor){
        if(editor.selection.isEmpty())
            editor.selection.selectWord();
        else
            editor.findNext();
    },
    readOnly:true
},{
    name:"selectOrFindPrevious",
    bindKey:bindKey("Alt-Shift-K","Ctrl-Shift-G"),
    exec:function(editor){
        if(editor.selection.isEmpty())
            editor.selection.selectWord();
        else
            editor.findPrevious();
    },
    readOnly:true
},{
    name:"find",
    bindKey:bindKey("Ctrl-F","Command-F"),
    exec:function(editor){
        config.loadModule("ace/ext/searchbox",function(e){e.Search(editor);});
    },
    readOnly:true
},{
    name:"overwrite",
    bindKey:"Insert",
    exec:function(editor){editor.toggleOverwrite();},
    readOnly:true
},{
    name:"selecttostart",
    bindKey:bindKey("Ctrl-Shift-Home","Command-Shift-Home|Command-Shift-Up"),
    exec:function(editor){editor.getSelection().selectFileStart();},
    multiSelectAction:"forEach",
    readOnly:true,
    scrollIntoView:"animate",
    aceCommandGroup:"fileJump"
},{
    name:"gotostart",
    bindKey:bindKey("Ctrl-Home","Command-Home|Command-Up"),
    exec:function(editor){editor.navigateFileStart();},
    multiSelectAction:"forEach",
    readOnly:true,
    scrollIntoView:"animate",
    aceCommandGroup:"fileJump"
},{
    name:"selectup",
    bindKey:bindKey("Shift-Up","Shift-Up|Ctrl-Shift-P"),
    exec:function(editor){editor.getSelection().selectUp();},
    multiSelectAction:"forEach",
    scrollIntoView:"cursor",
    readOnly:true
},{
    name:"golineup",
    bindKey:bindKey("Up","Up|Ctrl-P"),
    exec:function(editor,args){editor.navigateUp(args.times);},
    multiSelectAction:"forEach",
    scrollIntoView:"cursor",
    readOnly:true
},{
    name:"selecttoend",
    bindKey:bindKey("Ctrl-Shift-End","Command-Shift-End|Command-Shift-Down"),
    exec:function(editor){editor.getSelection().selectFileEnd();},
    multiSelectAction:"forEach",
    readOnly:true,
    scrollIntoView:"animate",
    aceCommandGroup:"fileJump"
},{
    name:"gotoend",
    bindKey:bindKey("Ctrl-End","Command-End|Command-Down"),
    exec:function(editor){editor.navigateFileEnd();},
    multiSelectAction:"forEach",
    readOnly:true,
    scrollIntoView:"animate",
    aceCommandGroup:"fileJump"
},{
    name:"selectdown",
    bindKey:bindKey("Shift-Down","Shift-Down|Ctrl-Shift-N"),
    exec:function(editor){editor.getSelection().selectDown();},
    multiSelectAction:"forEach",
    scrollIntoView:"cursor",
    readOnly:true
},{
    name:"golinedown",
    bindKey:bindKey("Down","Down|Ctrl-N"),
    exec:function(editor,args){editor.navigateDown(args.times);},
    multiSelectAction:"forEach",
    scrollIntoView:"cursor",
    readOnly:true
},{
    name:"selectwordleft",
    bindKey:bindKey("Ctrl-Shift-Left","Option-Shift-Left"),
    exec:function(editor){editor.getSelection().selectWordLeft();},
    multiSelectAction:"forEach",
    scrollIntoView:"cursor",
    readOnly:true
},{
    name:"gotowordleft",
    bindKey:bindKey("Ctrl-Left","Option-Left"),
    exec:function(editor){editor.navigateWordLeft();},
    multiSelectAction:"forEach",
    scrollIntoView:"cursor",
    readOnly:true
},{
    name:"selecttolinestart",
    bindKey:bindKey("Alt-Shift-Left","Command-Shift-Left|Ctrl-Shift-A"),
    exec:function(editor){editor.getSelection().selectLineStart();},
    multiSelectAction:"forEach",
    scrollIntoView:"cursor",
    readOnly:true
},{
    name:"gotolinestart",
    bindKey:bindKey("Alt-Left|Home","Command-Left|Home|Ctrl-A"),
    exec:function(editor){editor.navigateLineStart();},
    multiSelectAction:"forEach",
    scrollIntoView:"cursor",
    readOnly:true
},{
    name:"selectleft",
    bindKey:bindKey("Shift-Left","Shift-Left|Ctrl-Shift-B"),
    exec:function(editor){editor.getSelection().selectLeft();},
    multiSelectAction:"forEach",
    scrollIntoView:"cursor",
    readOnly:true
},{
    name:"gotoleft",
    bindKey:bindKey("Left","Left|Ctrl-B"),
    exec:function(editor,args){editor.navigateLeft(args.times);},
    multiSelectAction:"forEach",
    scrollIntoView:"cursor",
    readOnly:true
},{
    name:"selectwordright",
    bindKey:bindKey("Ctrl-Shift-Right","Option-Shift-Right"),
    exec:function(editor){editor.getSelection().selectWordRight();},
    multiSelectAction:"forEach",
    scrollIntoView:"cursor",
    readOnly:true
},{
    name:"gotowordright",
    bindKey:bindKey("Ctrl-Right","Option-Right"),
    exec:function(editor){editor.navigateWordRight();},
    multiSelectAction:"forEach",
    scrollIntoView:"cursor",
    readOnly:true
},{
    name:"selecttolineend",
    bindKey:bindKey("Alt-Shift-Right","Command-Shift-Right|Shift-End|Ctrl-Shift-E"),
    exec:function(editor){editor.getSelection().selectLineEnd();},
    multiSelectAction:"forEach",
    scrollIntoView:"cursor",
    readOnly:true
},{
    name:"gotolineend",
    bindKey:bindKey("Alt-Right|End","Command-Right|End|Ctrl-E"),
    exec:function(editor){editor.navigateLineEnd();},
    multiSelectAction:"forEach",
    scrollIntoView:"cursor",
    readOnly:true
},{
    name:"selectright",
    bindKey:bindKey("Shift-Right","Shift-Right"),
    exec:function(editor){editor.getSelection().selectRight();},
    multiSelectAction:"forEach",
    scrollIntoView:"cursor",
    readOnly:true
},{
    name:"gotoright",
    bindKey:bindKey("Right","Right|Ctrl-F"),
    exec:function(editor,args){editor.navigateRight(args.times);},
    multiSelectAction:"forEach",
    scrollIntoView:"cursor",
    readOnly:true
},{
    name:"selectpagedown",
    bindKey:"Shift-PageDown",
    exec:function(editor){editor.selectPageDown();},
    readOnly:true
},{
    name:"pagedown",
    bindKey:bindKey(null,"Option-PageDown"),
    exec:function(editor){editor.scrollPageDown();},
    readOnly:true
},{
    name:"gotopagedown",
    bindKey:bindKey("PageDown","PageDown|Ctrl-V"),
    exec:function(editor){editor.gotoPageDown();},
    readOnly:true
},{
    name:"selectpageup",
    bindKey:"Shift-PageUp",
    exec:function(editor){editor.selectPageUp();},
    readOnly:true
},{
    name:"pageup",
    bindKey:bindKey(null,"Option-PageUp"),
    exec:function(editor){editor.scrollPageUp();},
    readOnly:true
},{
    name:"gotopageup",
    bindKey:"PageUp",
    exec:function(editor){editor.gotoPageUp();},
    readOnly:true
},{
    name:"scrollup",
    bindKey:bindKey("Ctrl-Up",null),
    exec:function(e){e.renderer.scrollBy(0,-2*e.renderer.layerConfig.lineHeight);},
    readOnly:true
},{
    name:"scrolldown",
    bindKey:bindKey("Ctrl-Down",null),
    exec:function(e){e.renderer.scrollBy(0,2*e.renderer.layerConfig.lineHeight);},
    readOnly:true
},{
    name:"selectlinestart",
    bindKey:"Shift-Home",
    exec:function(editor){editor.getSelection().selectLineStart();},
    multiSelectAction:"forEach",
    scrollIntoView:"cursor",
    readOnly:true
},{
    name:"selectlineend",
    bindKey:"Shift-End",
    exec:function(editor){editor.getSelection().selectLineEnd();},
    multiSelectAction:"forEach",
    scrollIntoView:"cursor",
    readOnly:true
},{
    name:"togglerecording",
    bindKey:bindKey("Ctrl-Alt-E","Command-Option-E"),
    exec:function(editor){editor.commands.toggleRecording(editor);},
    readOnly:true
},{
    name:"replaymacro",
    bindKey:bindKey("Ctrl-Shift-E","Command-Shift-E"),
    exec:function(editor){editor.commands.replay(editor);},
    readOnly:true
},{
    name:"jumptomatching",
    bindKey:bindKey("Ctrl-P","Ctrl-P"),
    exec:function(editor){editor.jumpToMatching();},
    multiSelectAction:"forEach",
    scrollIntoView:"animate",
    readOnly:true
},{
    name:"selecttomatching",
    bindKey:bindKey("Ctrl-Shift-P","Ctrl-Shift-P"),
    exec:function(editor){editor.jumpToMatching(true);},
    multiSelectAction:"forEach",
    scrollIntoView:"animate",
    readOnly:true
},{
    name:"expandToMatching",
    bindKey:bindKey("Ctrl-Shift-M","Ctrl-Shift-M"),
    exec:function(editor){editor.jumpToMatching(true,true);},
    multiSelectAction:"forEach",
    scrollIntoView:"animate",
    readOnly:true
},{
    name:"passKeysToBrowser",
    bindKey:bindKey(null,null),
    exec:function(){},
    passEvent:true,
    readOnly:true
},{
    name:"copy",
    exec:function(editor){
    },
    readOnly:true
},
{
    name:"cut",
    exec:function(editor){
        varcutLine=editor.$copyWithEmptySelection&&editor.selection.isEmpty();
        varrange=cutLine?editor.selection.getLineRange():editor.selection.getRange();
        editor._emit("cut",range);

        if(!range.isEmpty())
            editor.session.remove(range);
        editor.clearSelection();
    },
    scrollIntoView:"cursor",
    multiSelectAction:"forEach"
},{
    name:"paste",
    exec:function(editor,args){
        editor.$handlePaste(args);
    },
    scrollIntoView:"cursor"
},{
    name:"removeline",
    bindKey:bindKey("Ctrl-D","Command-D"),
    exec:function(editor){editor.removeLines();},
    scrollIntoView:"cursor",
    multiSelectAction:"forEachLine"
},{
    name:"duplicateSelection",
    bindKey:bindKey("Ctrl-Shift-D","Command-Shift-D"),
    exec:function(editor){editor.duplicateSelection();},
    scrollIntoView:"cursor",
    multiSelectAction:"forEach"
},{
    name:"sortlines",
    bindKey:bindKey("Ctrl-Alt-S","Command-Alt-S"),
    exec:function(editor){editor.sortLines();},
    scrollIntoView:"selection",
    multiSelectAction:"forEachLine"
},{
    name:"togglecomment",
    bindKey:bindKey("Ctrl-/","Command-/"),
    exec:function(editor){editor.toggleCommentLines();},
    multiSelectAction:"forEachLine",
    scrollIntoView:"selectionPart"
},{
    name:"toggleBlockComment",
    bindKey:bindKey("Ctrl-Shift-/","Command-Shift-/"),
    exec:function(editor){editor.toggleBlockComment();},
    multiSelectAction:"forEach",
    scrollIntoView:"selectionPart"
},{
    name:"modifyNumberUp",
    bindKey:bindKey("Ctrl-Shift-Up","Alt-Shift-Up"),
    exec:function(editor){editor.modifyNumber(1);},
    scrollIntoView:"cursor",
    multiSelectAction:"forEach"
},{
    name:"modifyNumberDown",
    bindKey:bindKey("Ctrl-Shift-Down","Alt-Shift-Down"),
    exec:function(editor){editor.modifyNumber(-1);},
    scrollIntoView:"cursor",
    multiSelectAction:"forEach"
},{
    name:"replace",
    bindKey:bindKey("Ctrl-H","Command-Option-F"),
    exec:function(editor){
        config.loadModule("ace/ext/searchbox",function(e){e.Search(editor,true);});
    }
},{
    name:"undo",
    bindKey:bindKey("Ctrl-Z","Command-Z"),
    exec:function(editor){editor.undo();}
},{
    name:"redo",
    bindKey:bindKey("Ctrl-Shift-Z|Ctrl-Y","Command-Shift-Z|Command-Y"),
    exec:function(editor){editor.redo();}
},{
    name:"copylinesup",
    bindKey:bindKey("Alt-Shift-Up","Command-Option-Up"),
    exec:function(editor){editor.copyLinesUp();},
    scrollIntoView:"cursor"
},{
    name:"movelinesup",
    bindKey:bindKey("Alt-Up","Option-Up"),
    exec:function(editor){editor.moveLinesUp();},
    scrollIntoView:"cursor"
},{
    name:"copylinesdown",
    bindKey:bindKey("Alt-Shift-Down","Command-Option-Down"),
    exec:function(editor){editor.copyLinesDown();},
    scrollIntoView:"cursor"
},{
    name:"movelinesdown",
    bindKey:bindKey("Alt-Down","Option-Down"),
    exec:function(editor){editor.moveLinesDown();},
    scrollIntoView:"cursor"
},{
    name:"del",
    bindKey:bindKey("Delete","Delete|Ctrl-D|Shift-Delete"),
    exec:function(editor){editor.remove("right");},
    multiSelectAction:"forEach",
    scrollIntoView:"cursor"
},{
    name:"backspace",
    bindKey:bindKey(
        "Shift-Backspace|Backspace",
        "Ctrl-Backspace|Shift-Backspace|Backspace|Ctrl-H"
    ),
    exec:function(editor){editor.remove("left");},
    multiSelectAction:"forEach",
    scrollIntoView:"cursor"
},{
    name:"cut_or_delete",
    bindKey:bindKey("Shift-Delete",null),
    exec:function(editor){
        if(editor.selection.isEmpty()){
            editor.remove("left");
        }else{
            returnfalse;
        }
    },
    multiSelectAction:"forEach",
    scrollIntoView:"cursor"
},{
    name:"removetolinestart",
    bindKey:bindKey("Alt-Backspace","Command-Backspace"),
    exec:function(editor){editor.removeToLineStart();},
    multiSelectAction:"forEach",
    scrollIntoView:"cursor"
},{
    name:"removetolineend",
    bindKey:bindKey("Alt-Delete","Ctrl-K|Command-Delete"),
    exec:function(editor){editor.removeToLineEnd();},
    multiSelectAction:"forEach",
    scrollIntoView:"cursor"
},{
    name:"removetolinestarthard",
    bindKey:bindKey("Ctrl-Shift-Backspace",null),
    exec:function(editor){
        varrange=editor.selection.getRange();
        range.start.column=0;
        editor.session.remove(range);
    },
    multiSelectAction:"forEach",
    scrollIntoView:"cursor"
},{
    name:"removetolineendhard",
    bindKey:bindKey("Ctrl-Shift-Delete",null),
    exec:function(editor){
        varrange=editor.selection.getRange();
        range.end.column=Number.MAX_VALUE;
        editor.session.remove(range);
    },
    multiSelectAction:"forEach",
    scrollIntoView:"cursor"
},{
    name:"removewordleft",
    bindKey:bindKey("Ctrl-Backspace","Alt-Backspace|Ctrl-Alt-Backspace"),
    exec:function(editor){editor.removeWordLeft();},
    multiSelectAction:"forEach",
    scrollIntoView:"cursor"
},{
    name:"removewordright",
    bindKey:bindKey("Ctrl-Delete","Alt-Delete"),
    exec:function(editor){editor.removeWordRight();},
    multiSelectAction:"forEach",
    scrollIntoView:"cursor"
},{
    name:"outdent",
    bindKey:bindKey("Shift-Tab","Shift-Tab"),
    exec:function(editor){editor.blockOutdent();},
    multiSelectAction:"forEach",
    scrollIntoView:"selectionPart"
},{
    name:"indent",
    bindKey:bindKey("Tab","Tab"),
    exec:function(editor){editor.indent();},
    multiSelectAction:"forEach",
    scrollIntoView:"selectionPart"
},{
    name:"blockoutdent",
    bindKey:bindKey("Ctrl-[","Ctrl-["),
    exec:function(editor){editor.blockOutdent();},
    multiSelectAction:"forEachLine",
    scrollIntoView:"selectionPart"
},{
    name:"blockindent",
    bindKey:bindKey("Ctrl-]","Ctrl-]"),
    exec:function(editor){editor.blockIndent();},
    multiSelectAction:"forEachLine",
    scrollIntoView:"selectionPart"
},{
    name:"insertstring",
    exec:function(editor,str){editor.insert(str);},
    multiSelectAction:"forEach",
    scrollIntoView:"cursor"
},{
    name:"inserttext",
    exec:function(editor,args){
        editor.insert(lang.stringRepeat(args.text ||"",args.times||1));
    },
    multiSelectAction:"forEach",
    scrollIntoView:"cursor"
},{
    name:"splitline",
    bindKey:bindKey(null,"Ctrl-O"),
    exec:function(editor){editor.splitLine();},
    multiSelectAction:"forEach",
    scrollIntoView:"cursor"
},{
    name:"transposeletters",
    bindKey:bindKey("Alt-Shift-X","Ctrl-T"),
    exec:function(editor){editor.transposeLetters();},
    multiSelectAction:function(editor){editor.transposeSelections(1);},
    scrollIntoView:"cursor"
},{
    name:"touppercase",
    bindKey:bindKey("Ctrl-U","Ctrl-U"),
    exec:function(editor){editor.toUpperCase();},
    multiSelectAction:"forEach",
    scrollIntoView:"cursor"
},{
    name:"tolowercase",
    bindKey:bindKey("Ctrl-Shift-U","Ctrl-Shift-U"),
    exec:function(editor){editor.toLowerCase();},
    multiSelectAction:"forEach",
    scrollIntoView:"cursor"
},{
    name:"expandtoline",
    bindKey:bindKey("Ctrl-Shift-L","Command-Shift-L"),
    exec:function(editor){
        varrange=editor.selection.getRange();

        range.start.column=range.end.column=0;
        range.end.row++;
        editor.selection.setRange(range,false);
    },
    multiSelectAction:"forEach",
    scrollIntoView:"cursor",
    readOnly:true
},{
    name:"joinlines",
    bindKey:bindKey(null,null),
    exec:function(editor){
        varisBackwards=editor.selection.isBackwards();
        varselectionStart=isBackwards?editor.selection.getSelectionLead():editor.selection.getSelectionAnchor();
        varselectionEnd=isBackwards?editor.selection.getSelectionAnchor():editor.selection.getSelectionLead();
        varfirstLineEndCol=editor.session.doc.getLine(selectionStart.row).length;
        varselectedText=editor.session.doc.getTextRange(editor.selection.getRange());
        varselectedCount=selectedText.replace(/\n\s*/,"").length;
        varinsertLine=editor.session.doc.getLine(selectionStart.row);

        for(vari=selectionStart.row+1;i<=selectionEnd.row+1;i++){
            varcurLine=lang.stringTrimLeft(lang.stringTrimRight(editor.session.doc.getLine(i)));
            if(curLine.length!==0){
                curLine=""+curLine;
            }
            insertLine+=curLine;
        }

        if(selectionEnd.row+1<(editor.session.doc.getLength()-1)){
            insertLine+=editor.session.doc.getNewLineCharacter();
        }

        editor.clearSelection();
        editor.session.doc.replace(newRange(selectionStart.row,0,selectionEnd.row+2,0),insertLine);

        if(selectedCount>0){
            editor.selection.moveCursorTo(selectionStart.row,selectionStart.column);
            editor.selection.selectTo(selectionStart.row,selectionStart.column+selectedCount);
        }else{
            firstLineEndCol=editor.session.doc.getLine(selectionStart.row).length>firstLineEndCol?(firstLineEndCol+1):firstLineEndCol;
            editor.selection.moveCursorTo(selectionStart.row,firstLineEndCol);
        }
    },
    multiSelectAction:"forEach",
    readOnly:true
},{
    name:"invertSelection",
    bindKey:bindKey(null,null),
    exec:function(editor){
        varendRow=editor.session.doc.getLength()-1;
        varendCol=editor.session.doc.getLine(endRow).length;
        varranges=editor.selection.rangeList.ranges;
        varnewRanges=[];
        if(ranges.length<1){
            ranges=[editor.selection.getRange()];
        }

        for(vari=0;i<ranges.length;i++){
            if(i==(ranges.length-1)){
                if(!(ranges[i].end.row===endRow&&ranges[i].end.column===endCol)){
                    newRanges.push(newRange(ranges[i].end.row,ranges[i].end.column,endRow,endCol));
                }
            }

            if(i===0){
                if(!(ranges[i].start.row===0&&ranges[i].start.column===0)){
                    newRanges.push(newRange(0,0,ranges[i].start.row,ranges[i].start.column));
                }
            }else{
                newRanges.push(newRange(ranges[i-1].end.row,ranges[i-1].end.column,ranges[i].start.row,ranges[i].start.column));
            }
        }

        editor.exitMultiSelectMode();
        editor.clearSelection();

        for(vari=0;i<newRanges.length;i++){
            editor.selection.addRange(newRanges[i],false);
        }
    },
    readOnly:true,
    scrollIntoView:"none"
}];

});

define("ace/clipboard",["require","exports","module"],function(require,exports,module){
"usestrict";

module.exports={lineMode:false};

});

define("ace/editor",["require","exports","module","ace/lib/fixoldbrowsers","ace/lib/oop","ace/lib/dom","ace/lib/lang","ace/lib/useragent","ace/keyboard/textinput","ace/mouse/mouse_handler","ace/mouse/fold_handler","ace/keyboard/keybinding","ace/edit_session","ace/search","ace/range","ace/lib/event_emitter","ace/commands/command_manager","ace/commands/default_commands","ace/config","ace/token_iterator","ace/clipboard"],function(require,exports,module){
"usestrict";

require("./lib/fixoldbrowsers");

varoop=require("./lib/oop");
vardom=require("./lib/dom");
varlang=require("./lib/lang");
varuseragent=require("./lib/useragent");
varTextInput=require("./keyboard/textinput").TextInput;
varMouseHandler=require("./mouse/mouse_handler").MouseHandler;
varFoldHandler=require("./mouse/fold_handler").FoldHandler;
varKeyBinding=require("./keyboard/keybinding").KeyBinding;
varEditSession=require("./edit_session").EditSession;
varSearch=require("./search").Search;
varRange=require("./range").Range;
varEventEmitter=require("./lib/event_emitter").EventEmitter;
varCommandManager=require("./commands/command_manager").CommandManager;
vardefaultCommands=require("./commands/default_commands").commands;
varconfig=require("./config");
varTokenIterator=require("./token_iterator").TokenIterator;

varclipboard=require("./clipboard");
varEditor=function(renderer,session,options){
    varcontainer=renderer.getContainerElement();
    this.container=container;
    this.renderer=renderer;
    this.id="editor"+(++Editor.$uid);

    this.commands=newCommandManager(useragent.isMac?"mac":"win",defaultCommands);
    if(typeofdocument=="object"){
        this.textInput=newTextInput(renderer.getTextAreaContainer(),this);
        this.renderer.textarea=this.textInput.getElement();
        this.$mouseHandler=newMouseHandler(this);
        newFoldHandler(this);
    }

    this.keyBinding=newKeyBinding(this);

    this.$search=newSearch().set({
        wrap:true
    });

    this.$historyTracker=this.$historyTracker.bind(this);
    this.commands.on("exec",this.$historyTracker);

    this.$initOperationListeners();
    
    this._$emitInputEvent=lang.delayedCall(function(){
        this._signal("input",{});
        if(this.session&&this.session.bgTokenizer)
            this.session.bgTokenizer.scheduleStart();
    }.bind(this));
    
    this.on("change",function(_,_self){
        _self._$emitInputEvent.schedule(31);
    });

    this.setSession(session||options&&options.session||newEditSession(""));
    config.resetOptions(this);
    if(options)
        this.setOptions(options);
    config._signal("editor",this);
};

Editor.$uid=0;

(function(){

    oop.implement(this,EventEmitter);

    this.$initOperationListeners=function(){
        this.commands.on("exec",this.startOperation.bind(this),true);
        this.commands.on("afterExec",this.endOperation.bind(this),true);

        this.$opResetTimer=lang.delayedCall(this.endOperation.bind(this));
        this.on("change",function(){
            if(!this.curOp){
                this.startOperation();
                this.curOp.selectionBefore=this.$lastSel;
            }
            this.curOp.docChanged=true;
        }.bind(this),true);
        
        this.on("changeSelection",function(){
            if(!this.curOp){
                this.startOperation();
                this.curOp.selectionBefore=this.$lastSel;
            }
            this.curOp.selectionChanged=true;
        }.bind(this),true);
    };

    this.curOp=null;
    this.prevOp={};
    this.startOperation=function(commadEvent){
        if(this.curOp){
            if(!commadEvent||this.curOp.command)
                return;
            this.prevOp=this.curOp;
        }
        if(!commadEvent){
            this.previousCommand=null;
            commadEvent={};
        }

        this.$opResetTimer.schedule();
        this.curOp=this.session.curOp={
            command:commadEvent.command||{},
            args:commadEvent.args,
            scrollTop:this.renderer.scrollTop
        };
        this.curOp.selectionBefore=this.selection.toJSON();
    };

    this.endOperation=function(e){
        if(this.curOp){
            if(e&&e.returnValue===false)
                return(this.curOp=null);
            this._signal("beforeEndOperation");
            varcommand=this.curOp.command;
            varscrollIntoView=command&&command.scrollIntoView;
            if(scrollIntoView){
                switch(scrollIntoView){
                    case"center-animate":
                        scrollIntoView="animate";
                    case"center":
                        this.renderer.scrollCursorIntoView(null,0.5);
                        break;
                    case"animate":
                    case"cursor":
                        this.renderer.scrollCursorIntoView();
                        break;
                    case"selectionPart":
                        varrange=this.selection.getRange();
                        varconfig=this.renderer.layerConfig;
                        if(range.start.row>=config.lastRow||range.end.row<=config.firstRow){
                            this.renderer.scrollSelectionIntoView(this.selection.anchor,this.selection.lead);
                        }
                        break;
                    default:
                        break;
                }
                if(scrollIntoView=="animate")
                    this.renderer.animateScrolling(this.curOp.scrollTop);
            }
            varsel=this.selection.toJSON();
            this.curOp.selectionAfter=sel;
            this.$lastSel=this.selection.toJSON();
            this.session.getUndoManager().addSelection(sel);
            this.prevOp=this.curOp;
            this.curOp=null;
        }
    };
    this.$mergeableCommands=["backspace","del","insertstring"];
    this.$historyTracker=function(e){
        if(!this.$mergeUndoDeltas)
            return;

        varprev=this.prevOp;
        varmergeableCommands=this.$mergeableCommands;
        varshouldMerge=prev.command&&(e.command.name==prev.command.name);
        if(e.command.name=="insertstring"){
            vartext=e.args;
            if(this.mergeNextCommand===undefined)
                this.mergeNextCommand=true;

            shouldMerge=shouldMerge
                &&this.mergeNextCommand//previouscommandallowstocoalescewith
                &&(!/\s/.test(text)||/\s/.test(prev.args));//previousinsertionwasofsametype

            this.mergeNextCommand=true;
        }else{
            shouldMerge=shouldMerge
                &&mergeableCommands.indexOf(e.command.name)!==-1;//thecommandismergeable
        }

        if(
            this.$mergeUndoDeltas!="always"
            &&Date.now()-this.sequenceStartTime>2000
        ){
            shouldMerge=false;//thesequenceistoolong
        }

        if(shouldMerge)
            this.session.mergeUndoDeltas=true;
        elseif(mergeableCommands.indexOf(e.command.name)!==-1)
            this.sequenceStartTime=Date.now();
    };
    this.setKeyboardHandler=function(keyboardHandler,cb){
        if(keyboardHandler&&typeofkeyboardHandler==="string"&&keyboardHandler!="ace"){
            this.$keybindingId=keyboardHandler;
            var_self=this;
            config.loadModule(["keybinding",keyboardHandler],function(module){
                if(_self.$keybindingId==keyboardHandler)
                    _self.keyBinding.setKeyboardHandler(module&&module.handler);
                cb&&cb();
            });
        }else{
            this.$keybindingId=null;
            this.keyBinding.setKeyboardHandler(keyboardHandler);
            cb&&cb();
        }
    };
    this.getKeyboardHandler=function(){
        returnthis.keyBinding.getKeyboardHandler();
    };
    this.setSession=function(session){
        if(this.session==session)
            return;
        if(this.curOp)this.endOperation();
        this.curOp={};

        varoldSession=this.session;
        if(oldSession){
            this.session.off("change",this.$onDocumentChange);
            this.session.off("changeMode",this.$onChangeMode);
            this.session.off("tokenizerUpdate",this.$onTokenizerUpdate);
            this.session.off("changeTabSize",this.$onChangeTabSize);
            this.session.off("changeWrapLimit",this.$onChangeWrapLimit);
            this.session.off("changeWrapMode",this.$onChangeWrapMode);
            this.session.off("changeFold",this.$onChangeFold);
            this.session.off("changeFrontMarker",this.$onChangeFrontMarker);
            this.session.off("changeBackMarker",this.$onChangeBackMarker);
            this.session.off("changeBreakpoint",this.$onChangeBreakpoint);
            this.session.off("changeAnnotation",this.$onChangeAnnotation);
            this.session.off("changeOverwrite",this.$onCursorChange);
            this.session.off("changeScrollTop",this.$onScrollTopChange);
            this.session.off("changeScrollLeft",this.$onScrollLeftChange);

            varselection=this.session.getSelection();
            selection.off("changeCursor",this.$onCursorChange);
            selection.off("changeSelection",this.$onSelectionChange);
        }

        this.session=session;
        if(session){
            this.$onDocumentChange=this.onDocumentChange.bind(this);
            session.on("change",this.$onDocumentChange);
            this.renderer.setSession(session);
    
            this.$onChangeMode=this.onChangeMode.bind(this);
            session.on("changeMode",this.$onChangeMode);
    
            this.$onTokenizerUpdate=this.onTokenizerUpdate.bind(this);
            session.on("tokenizerUpdate",this.$onTokenizerUpdate);
    
            this.$onChangeTabSize=this.renderer.onChangeTabSize.bind(this.renderer);
            session.on("changeTabSize",this.$onChangeTabSize);
    
            this.$onChangeWrapLimit=this.onChangeWrapLimit.bind(this);
            session.on("changeWrapLimit",this.$onChangeWrapLimit);
    
            this.$onChangeWrapMode=this.onChangeWrapMode.bind(this);
            session.on("changeWrapMode",this.$onChangeWrapMode);
    
            this.$onChangeFold=this.onChangeFold.bind(this);
            session.on("changeFold",this.$onChangeFold);
    
            this.$onChangeFrontMarker=this.onChangeFrontMarker.bind(this);
            this.session.on("changeFrontMarker",this.$onChangeFrontMarker);
    
            this.$onChangeBackMarker=this.onChangeBackMarker.bind(this);
            this.session.on("changeBackMarker",this.$onChangeBackMarker);
    
            this.$onChangeBreakpoint=this.onChangeBreakpoint.bind(this);
            this.session.on("changeBreakpoint",this.$onChangeBreakpoint);
    
            this.$onChangeAnnotation=this.onChangeAnnotation.bind(this);
            this.session.on("changeAnnotation",this.$onChangeAnnotation);
    
            this.$onCursorChange=this.onCursorChange.bind(this);
            this.session.on("changeOverwrite",this.$onCursorChange);
    
            this.$onScrollTopChange=this.onScrollTopChange.bind(this);
            this.session.on("changeScrollTop",this.$onScrollTopChange);
    
            this.$onScrollLeftChange=this.onScrollLeftChange.bind(this);
            this.session.on("changeScrollLeft",this.$onScrollLeftChange);
    
            this.selection=session.getSelection();
            this.selection.on("changeCursor",this.$onCursorChange);
    
            this.$onSelectionChange=this.onSelectionChange.bind(this);
            this.selection.on("changeSelection",this.$onSelectionChange);
    
            this.onChangeMode();
    
            this.onCursorChange();
    
            this.onScrollTopChange();
            this.onScrollLeftChange();
            this.onSelectionChange();
            this.onChangeFrontMarker();
            this.onChangeBackMarker();
            this.onChangeBreakpoint();
            this.onChangeAnnotation();
            this.session.getUseWrapMode()&&this.renderer.adjustWrapLimit();
            this.renderer.updateFull();
        }else{
            this.selection=null;
            this.renderer.setSession(session);
        }

        this._signal("changeSession",{
            session:session,
            oldSession:oldSession
        });
        
        this.curOp=null;
        
        oldSession&&oldSession._signal("changeEditor",{oldEditor:this});
        session&&session._signal("changeEditor",{editor:this});
        
        if(session&&session.bgTokenizer)
            session.bgTokenizer.scheduleStart();
    };
    this.getSession=function(){
        returnthis.session;
    };
    this.setValue=function(val,cursorPos){
        this.session.doc.setValue(val);

        if(!cursorPos)
            this.selectAll();
        elseif(cursorPos==1)
            this.navigateFileEnd();
        elseif(cursorPos==-1)
            this.navigateFileStart();

        returnval;
    };
    this.getValue=function(){
        returnthis.session.getValue();
    };
    this.getSelection=function(){
        returnthis.selection;
    };
    this.resize=function(force){
        this.renderer.onResize(force);
    };
    this.setTheme=function(theme,cb){
        this.renderer.setTheme(theme,cb);
    };
    this.getTheme=function(){
        returnthis.renderer.getTheme();
    };
    this.setStyle=function(style){
        this.renderer.setStyle(style);
    };
    this.unsetStyle=function(style){
        this.renderer.unsetStyle(style);
    };
    this.getFontSize=function(){
        returnthis.getOption("fontSize")||
           dom.computedStyle(this.container,"fontSize");
    };
    this.setFontSize=function(size){
        this.setOption("fontSize",size);
    };

    this.$highlightBrackets=function(){
        if(this.session.$bracketHighlight){
            this.session.removeMarker(this.session.$bracketHighlight);
            this.session.$bracketHighlight=null;
        }

        if(this.$highlightPending){
            return;
        }
        varself=this;
        this.$highlightPending=true;
        setTimeout(function(){
            self.$highlightPending=false;
            varsession=self.session;
            if(!session||!session.bgTokenizer)return;
            varpos=session.findMatchingBracket(self.getCursorPosition());
            if(pos){
                varrange=newRange(pos.row,pos.column,pos.row,pos.column+1);
            }elseif(session.$mode.getMatching){
                varrange=session.$mode.getMatching(self.session);
            }
            if(range)
                session.$bracketHighlight=session.addMarker(range,"ace_bracket","text");
        },50);
    };
    this.$highlightTags=function(){
        if(this.$highlightTagPending)
            return;
        varself=this;
        this.$highlightTagPending=true;
        setTimeout(function(){
            self.$highlightTagPending=false;
            
            varsession=self.session;
            if(!session||!session.bgTokenizer)return;
            
            varpos=self.getCursorPosition();
            variterator=newTokenIterator(self.session,pos.row,pos.column);
            vartoken=iterator.getCurrentToken();
            
            if(!token||!/\b(?:tag-open|tag-name)/.test(token.type)){
                session.removeMarker(session.$tagHighlight);
                session.$tagHighlight=null;
                return;
            }
            
            if(token.type.indexOf("tag-open")!=-1){
                token=iterator.stepForward();
                if(!token)
                    return;
            }
            
            vartag=token.value;
            vardepth=0;
            varprevToken=iterator.stepBackward();
            
            if(prevToken.value=='<'){
                do{
                    prevToken=token;
                    token=iterator.stepForward();
                    
                    if(token&&token.value===tag&&token.type.indexOf('tag-name')!==-1){
                        if(prevToken.value==='<'){
                            depth++;
                        }elseif(prevToken.value==='</'){
                            depth--;
                        }
                    }
                    
                }while(token&&depth>=0);
            }else{
                do{
                    token=prevToken;
                    prevToken=iterator.stepBackward();
                    
                    if(token&&token.value===tag&&token.type.indexOf('tag-name')!==-1){
                        if(prevToken.value==='<'){
                            depth++;
                        }elseif(prevToken.value==='</'){
                            depth--;
                        }
                    }
                }while(prevToken&&depth<=0);
                iterator.stepForward();
            }
            
            if(!token){
                session.removeMarker(session.$tagHighlight);
                session.$tagHighlight=null;
                return;
            }
            
            varrow=iterator.getCurrentTokenRow();
            varcolumn=iterator.getCurrentTokenColumn();
            varrange=newRange(row,column,row,column+token.value.length);
            varsbm=session.$backMarkers[session.$tagHighlight];
            if(session.$tagHighlight&&sbm!=undefined&&range.compareRange(sbm.range)!==0){
                session.removeMarker(session.$tagHighlight);
                session.$tagHighlight=null;
            }
            
            if(!session.$tagHighlight)
                session.$tagHighlight=session.addMarker(range,"ace_bracket","text");
        },50);
    };
    this.focus=function(){
        var_self=this;
        setTimeout(function(){
            if(!_self.isFocused())
                _self.textInput.focus();
        });
        this.textInput.focus();
    };
    this.isFocused=function(){
        returnthis.textInput.isFocused();
    };
    this.blur=function(){
        this.textInput.blur();
    };
    this.onFocus=function(e){
        if(this.$isFocused)
            return;
        this.$isFocused=true;
        this.renderer.showCursor();
        this.renderer.visualizeFocus();
        this._emit("focus",e);
    };
    this.onBlur=function(e){
        if(!this.$isFocused)
            return;
        this.$isFocused=false;
        this.renderer.hideCursor();
        this.renderer.visualizeBlur();
        this._emit("blur",e);
    };

    this.$cursorChange=function(){
        this.renderer.updateCursor();
    };
    this.onDocumentChange=function(delta){
        varwrap=this.session.$useWrapMode;
        varlastRow=(delta.start.row==delta.end.row?delta.end.row:Infinity);
        this.renderer.updateLines(delta.start.row,lastRow,wrap);

        this._signal("change",delta);
        this.$cursorChange();
        this.$updateHighlightActiveLine();
    };

    this.onTokenizerUpdate=function(e){
        varrows=e.data;
        this.renderer.updateLines(rows.first,rows.last);
    };


    this.onScrollTopChange=function(){
        this.renderer.scrollToY(this.session.getScrollTop());
    };

    this.onScrollLeftChange=function(){
        this.renderer.scrollToX(this.session.getScrollLeft());
    };
    this.onCursorChange=function(){
        this.$cursorChange();

        this.$highlightBrackets();
        this.$highlightTags();
        this.$updateHighlightActiveLine();
        this._signal("changeSelection");
    };

    this.$updateHighlightActiveLine=function(){
        varsession=this.getSession();

        varhighlight;
        if(this.$highlightActiveLine){
            if(this.$selectionStyle!="line"||!this.selection.isMultiLine())
                highlight=this.getCursorPosition();
            if(this.renderer.theme&&this.renderer.theme.$selectionColorConflict&&!this.selection.isEmpty())
                highlight=false;
            if(this.renderer.$maxLines&&this.session.getLength()===1&&!(this.renderer.$minLines>1))
                highlight=false;
        }

        if(session.$highlightLineMarker&&!highlight){
            session.removeMarker(session.$highlightLineMarker.id);
            session.$highlightLineMarker=null;
        }elseif(!session.$highlightLineMarker&&highlight){
            varrange=newRange(highlight.row,highlight.column,highlight.row,Infinity);
            range.id=session.addMarker(range,"ace_active-line","screenLine");
            session.$highlightLineMarker=range;
        }elseif(highlight){
            session.$highlightLineMarker.start.row=highlight.row;
            session.$highlightLineMarker.end.row=highlight.row;
            session.$highlightLineMarker.start.column=highlight.column;
            session._signal("changeBackMarker");
        }
    };

    this.onSelectionChange=function(e){
        varsession=this.session;

        if(session.$selectionMarker){
            session.removeMarker(session.$selectionMarker);
        }
        session.$selectionMarker=null;

        if(!this.selection.isEmpty()){
            varrange=this.selection.getRange();
            varstyle=this.getSelectionStyle();
            session.$selectionMarker=session.addMarker(range,"ace_selection",style);
        }else{
            this.$updateHighlightActiveLine();
        }

        varre=this.$highlightSelectedWord&&this.$getSelectionHighLightRegexp();
        this.session.highlight(re);

        this._signal("changeSelection");
    };

    this.$getSelectionHighLightRegexp=function(){
        varsession=this.session;

        varselection=this.getSelectionRange();
        if(selection.isEmpty()||selection.isMultiLine())
            return;

        varstartColumn=selection.start.column;
        varendColumn=selection.end.column;
        varline=session.getLine(selection.start.row);
        
        varneedle=line.substring(startColumn,endColumn);
        if(needle.length>5000||!/[\w\d]/.test(needle))
            return;

        varre=this.$search.$assembleRegExp({
            wholeWord:true,
            caseSensitive:true,
            needle:needle
        });
        
        varwordWithBoundary=line.substring(startColumn-1,endColumn+1);
        if(!re.test(wordWithBoundary))
            return;
        
        returnre;
    };


    this.onChangeFrontMarker=function(){
        this.renderer.updateFrontMarkers();
    };

    this.onChangeBackMarker=function(){
        this.renderer.updateBackMarkers();
    };


    this.onChangeBreakpoint=function(){
        this.renderer.updateBreakpoints();
    };

    this.onChangeAnnotation=function(){
        this.renderer.setAnnotations(this.session.getAnnotations());
    };


    this.onChangeMode=function(e){
        this.renderer.updateText();
        this._emit("changeMode",e);
    };


    this.onChangeWrapLimit=function(){
        this.renderer.updateFull();
    };

    this.onChangeWrapMode=function(){
        this.renderer.onResize(true);
    };


    this.onChangeFold=function(){
        this.$updateHighlightActiveLine();
        this.renderer.updateFull();
    };
    this.getSelectedText=function(){
        returnthis.session.getTextRange(this.getSelectionRange());
    };
    this.getCopyText=function(){
        vartext=this.getSelectedText();
        varnl=this.session.doc.getNewLineCharacter();
        varcopyLine=false;
        if(!text&&this.$copyWithEmptySelection){
            copyLine=true;
            varranges=this.selection.getAllRanges();
            for(vari=0;i<ranges.length;i++){
                varrange=ranges[i];
                if(i&&ranges[i-1].start.row==range.start.row)
                    continue;
                text+=this.session.getLine(range.start.row)+nl;
            }
        }
        vare={text:text};
        this._signal("copy",e);
        clipboard.lineMode=copyLine?e.text:"";
        returne.text;
    };
    this.onCopy=function(){
        this.commands.exec("copy",this);
    };
    this.onCut=function(){
        this.commands.exec("cut",this);
    };
    this.onPaste=function(text,event){
        vare={text:text,event:event};
        this.commands.exec("paste",this,e);
    };
    
    this.$handlePaste=function(e){
        if(typeofe=="string")
            e={text:e};
        this._signal("paste",e);
        vartext=e.text;

        varlineMode=text==clipboard.lineMode;
        varsession=this.session;
        if(!this.inMultiSelectMode||this.inVirtualSelectionMode){
            if(lineMode)
                session.insert({row:this.selection.lead.row,column:0},text);
            else
                this.insert(text);
        }elseif(lineMode){
            this.selection.rangeList.ranges.forEach(function(range){
                session.insert({row:range.start.row,column:0},text);
            });
        }else{
            varlines=text.split(/\r\n|\r|\n/);
            varranges=this.selection.rangeList.ranges;
    
            if(lines.length>ranges.length||lines.length<2||!lines[1])
                returnthis.commands.exec("insertstring",this,text);
    
            for(vari=ranges.length;i--;){
                varrange=ranges[i];
                if(!range.isEmpty())
                    session.remove(range);
    
                session.insert(range.start,lines[i]);
            }
        }
    };

    this.execCommand=function(command,args){
        returnthis.commands.exec(command,this,args);
    };
    this.insert=function(text,pasted){
        varsession=this.session;
        varmode=session.getMode();
        varcursor=this.getCursorPosition();

        if(this.getBehavioursEnabled()&&!pasted){
            vartransform=mode.transformAction(session.getState(cursor.row),'insertion',this,session,text);
            if(transform){
                if(text!==transform.text){
                    if(!this.inVirtualSelectionMode){
                        this.session.mergeUndoDeltas=false;
                        this.mergeNextCommand=false;
                    }
                }
                text=transform.text;

            }
        }
        
        if(text=="\t")
            text=this.session.getTabString();
        if(!this.selection.isEmpty()){
            varrange=this.getSelectionRange();
            cursor=this.session.remove(range);
            this.clearSelection();
        }
        elseif(this.session.getOverwrite()&&text.indexOf("\n")==-1){
            varrange=newRange.fromPoints(cursor,cursor);
            range.end.column+=text.length;
            this.session.remove(range);
        }

        if(text=="\n"||text=="\r\n"){
            varline=session.getLine(cursor.row);
            if(cursor.column>line.search(/\S|$/)){
                vard=line.substr(cursor.column).search(/\S|$/);
                session.doc.removeInLine(cursor.row,cursor.column,cursor.column+d);
            }
        }
        this.clearSelection();

        varstart=cursor.column;
        varlineState=session.getState(cursor.row);
        varline=session.getLine(cursor.row);
        varshouldOutdent=mode.checkOutdent(lineState,line,text);
        varend=session.insert(cursor,text);

        if(transform&&transform.selection){
            if(transform.selection.length==2){//Transformrelativetothecurrentcolumn
                this.selection.setSelectionRange(
                    newRange(cursor.row,start+transform.selection[0],
                              cursor.row,start+transform.selection[1]));
            }else{//Transformrelativetothecurrentrow.
                this.selection.setSelectionRange(
                    newRange(cursor.row+transform.selection[0],
                              transform.selection[1],
                              cursor.row+transform.selection[2],
                              transform.selection[3]));
            }
        }

        if(session.getDocument().isNewLine(text)){
            varlineIndent=mode.getNextLineIndent(lineState,line.slice(0,cursor.column),session.getTabString());

            session.insert({row:cursor.row+1,column:0},lineIndent);
        }
        if(shouldOutdent)
            mode.autoOutdent(lineState,session,cursor.row);
    };

    this.onTextInput=function(text){
        this.keyBinding.onTextInput(text);
    };

    this.onCommandKey=function(e,hashId,keyCode){
        this.keyBinding.onCommandKey(e,hashId,keyCode);
    };
    this.setOverwrite=function(overwrite){
        this.session.setOverwrite(overwrite);
    };
    this.getOverwrite=function(){
        returnthis.session.getOverwrite();
    };
    this.toggleOverwrite=function(){
        this.session.toggleOverwrite();
    };
    this.setScrollSpeed=function(speed){
        this.setOption("scrollSpeed",speed);
    };
    this.getScrollSpeed=function(){
        returnthis.getOption("scrollSpeed");
    };
    this.setDragDelay=function(dragDelay){
        this.setOption("dragDelay",dragDelay);
    };
    this.getDragDelay=function(){
        returnthis.getOption("dragDelay");
    };
    this.setSelectionStyle=function(val){
        this.setOption("selectionStyle",val);
    };
    this.getSelectionStyle=function(){
        returnthis.getOption("selectionStyle");
    };
    this.setHighlightActiveLine=function(shouldHighlight){
        this.setOption("highlightActiveLine",shouldHighlight);
    };
    this.getHighlightActiveLine=function(){
        returnthis.getOption("highlightActiveLine");
    };
    this.setHighlightGutterLine=function(shouldHighlight){
        this.setOption("highlightGutterLine",shouldHighlight);
    };

    this.getHighlightGutterLine=function(){
        returnthis.getOption("highlightGutterLine");
    };
    this.setHighlightSelectedWord=function(shouldHighlight){
        this.setOption("highlightSelectedWord",shouldHighlight);
    };
    this.getHighlightSelectedWord=function(){
        returnthis.$highlightSelectedWord;
    };

    this.setAnimatedScroll=function(shouldAnimate){
        this.renderer.setAnimatedScroll(shouldAnimate);
    };

    this.getAnimatedScroll=function(){
        returnthis.renderer.getAnimatedScroll();
    };
    this.setShowInvisibles=function(showInvisibles){
        this.renderer.setShowInvisibles(showInvisibles);
    };
    this.getShowInvisibles=function(){
        returnthis.renderer.getShowInvisibles();
    };

    this.setDisplayIndentGuides=function(display){
        this.renderer.setDisplayIndentGuides(display);
    };

    this.getDisplayIndentGuides=function(){
        returnthis.renderer.getDisplayIndentGuides();
    };
    this.setShowPrintMargin=function(showPrintMargin){
        this.renderer.setShowPrintMargin(showPrintMargin);
    };
    this.getShowPrintMargin=function(){
        returnthis.renderer.getShowPrintMargin();
    };
    this.setPrintMarginColumn=function(showPrintMargin){
        this.renderer.setPrintMarginColumn(showPrintMargin);
    };
    this.getPrintMarginColumn=function(){
        returnthis.renderer.getPrintMarginColumn();
    };
    this.setReadOnly=function(readOnly){
        this.setOption("readOnly",readOnly);
    };
    this.getReadOnly=function(){
        returnthis.getOption("readOnly");
    };
    this.setBehavioursEnabled=function(enabled){
        this.setOption("behavioursEnabled",enabled);
    };
    this.getBehavioursEnabled=function(){
        returnthis.getOption("behavioursEnabled");
    };
    this.setWrapBehavioursEnabled=function(enabled){
        this.setOption("wrapBehavioursEnabled",enabled);
    };
    this.getWrapBehavioursEnabled=function(){
        returnthis.getOption("wrapBehavioursEnabled");
    };
    this.setShowFoldWidgets=function(show){
        this.setOption("showFoldWidgets",show);

    };
    this.getShowFoldWidgets=function(){
        returnthis.getOption("showFoldWidgets");
    };

    this.setFadeFoldWidgets=function(fade){
        this.setOption("fadeFoldWidgets",fade);
    };

    this.getFadeFoldWidgets=function(){
        returnthis.getOption("fadeFoldWidgets");
    };
    this.remove=function(dir){
        if(this.selection.isEmpty()){
            if(dir=="left")
                this.selection.selectLeft();
            else
                this.selection.selectRight();
        }

        varrange=this.getSelectionRange();
        if(this.getBehavioursEnabled()){
            varsession=this.session;
            varstate=session.getState(range.start.row);
            varnew_range=session.getMode().transformAction(state,'deletion',this,session,range);

            if(range.end.column===0){
                vartext=session.getTextRange(range);
                if(text[text.length-1]=="\n"){
                    varline=session.getLine(range.end.row);
                    if(/^\s+$/.test(line)){
                        range.end.column=line.length;
                    }
                }
            }
            if(new_range)
                range=new_range;
        }

        this.session.remove(range);
        this.clearSelection();
    };
    this.removeWordRight=function(){
        if(this.selection.isEmpty())
            this.selection.selectWordRight();

        this.session.remove(this.getSelectionRange());
        this.clearSelection();
    };
    this.removeWordLeft=function(){
        if(this.selection.isEmpty())
            this.selection.selectWordLeft();

        this.session.remove(this.getSelectionRange());
        this.clearSelection();
    };
    this.removeToLineStart=function(){
        if(this.selection.isEmpty())
            this.selection.selectLineStart();

        this.session.remove(this.getSelectionRange());
        this.clearSelection();
    };
    this.removeToLineEnd=function(){
        if(this.selection.isEmpty())
            this.selection.selectLineEnd();

        varrange=this.getSelectionRange();
        if(range.start.column==range.end.column&&range.start.row==range.end.row){
            range.end.column=0;
            range.end.row++;
        }

        this.session.remove(range);
        this.clearSelection();
    };
    this.splitLine=function(){
        if(!this.selection.isEmpty()){
            this.session.remove(this.getSelectionRange());
            this.clearSelection();
        }

        varcursor=this.getCursorPosition();
        this.insert("\n");
        this.moveCursorToPosition(cursor);
    };
    this.transposeLetters=function(){
        if(!this.selection.isEmpty()){
            return;
        }

        varcursor=this.getCursorPosition();
        varcolumn=cursor.column;
        if(column===0)
            return;

        varline=this.session.getLine(cursor.row);
        varswap,range;
        if(column<line.length){
            swap=line.charAt(column)+line.charAt(column-1);
            range=newRange(cursor.row,column-1,cursor.row,column+1);
        }
        else{
            swap=line.charAt(column-1)+line.charAt(column-2);
            range=newRange(cursor.row,column-2,cursor.row,column);
        }
        this.session.replace(range,swap);
        this.session.selection.moveToPosition(range.end);
    };
    this.toLowerCase=function(){
        varoriginalRange=this.getSelectionRange();
        if(this.selection.isEmpty()){
            this.selection.selectWord();
        }

        varrange=this.getSelectionRange();
        vartext=this.session.getTextRange(range);
        this.session.replace(range,text.toLowerCase());
        this.selection.setSelectionRange(originalRange);
    };
    this.toUpperCase=function(){
        varoriginalRange=this.getSelectionRange();
        if(this.selection.isEmpty()){
            this.selection.selectWord();
        }

        varrange=this.getSelectionRange();
        vartext=this.session.getTextRange(range);
        this.session.replace(range,text.toUpperCase());
        this.selection.setSelectionRange(originalRange);
    };
    this.indent=function(){
        varsession=this.session;
        varrange=this.getSelectionRange();

        if(range.start.row<range.end.row){
            varrows=this.$getSelectedRows();
            session.indentRows(rows.first,rows.last,"\t");
            return;
        }elseif(range.start.column<range.end.column){
            vartext=session.getTextRange(range);
            if(!/^\s+$/.test(text)){
                varrows=this.$getSelectedRows();
                session.indentRows(rows.first,rows.last,"\t");
                return;
            }
        }
        
        varline=session.getLine(range.start.row);
        varposition=range.start;
        varsize=session.getTabSize();
        varcolumn=session.documentToScreenColumn(position.row,position.column);

        if(this.session.getUseSoftTabs()){
            varcount=(size-column%size);
            varindentString=lang.stringRepeat("",count);
        }else{
            varcount=column%size;
            while(line[range.start.column-1]==""&&count){
                range.start.column--;
                count--;
            }
            this.selection.setSelectionRange(range);
            indentString="\t";
        }
        returnthis.insert(indentString);
    };
    this.blockIndent=function(){
        varrows=this.$getSelectedRows();
        this.session.indentRows(rows.first,rows.last,"\t");
    };
    this.blockOutdent=function(){
        varselection=this.session.getSelection();
        this.session.outdentRows(selection.getRange());
    };
    this.sortLines=function(){
        varrows=this.$getSelectedRows();
        varsession=this.session;

        varlines=[];
        for(vari=rows.first;i<=rows.last;i++)
            lines.push(session.getLine(i));

        lines.sort(function(a,b){
            if(a.toLowerCase()<b.toLowerCase())return-1;
            if(a.toLowerCase()>b.toLowerCase())return1;
            return0;
        });

        vardeleteRange=newRange(0,0,0,0);
        for(vari=rows.first;i<=rows.last;i++){
            varline=session.getLine(i);
            deleteRange.start.row=i;
            deleteRange.end.row=i;
            deleteRange.end.column=line.length;
            session.replace(deleteRange,lines[i-rows.first]);
        }
    };
    this.toggleCommentLines=function(){
        varstate=this.session.getState(this.getCursorPosition().row);
        varrows=this.$getSelectedRows();
        this.session.getMode().toggleCommentLines(state,this.session,rows.first,rows.last);
    };

    this.toggleBlockComment=function(){
        varcursor=this.getCursorPosition();
        varstate=this.session.getState(cursor.row);
        varrange=this.getSelectionRange();
        this.session.getMode().toggleBlockComment(state,this.session,range,cursor);
    };
    this.getNumberAt=function(row,column){
        var_numberRx=/[\-]?[0-9]+(?:\.[0-9]+)?/g;
        _numberRx.lastIndex=0;

        vars=this.session.getLine(row);
        while(_numberRx.lastIndex<column){
            varm=_numberRx.exec(s);
            if(m.index<=column&&m.index+m[0].length>=column){
                varnumber={
                    value:m[0],
                    start:m.index,
                    end:m.index+m[0].length
                };
                returnnumber;
            }
        }
        returnnull;
    };
    this.modifyNumber=function(amount){
        varrow=this.selection.getCursor().row;
        varcolumn=this.selection.getCursor().column;
        varcharRange=newRange(row,column-1,row,column);

        varc=this.session.getTextRange(charRange);
        if(!isNaN(parseFloat(c))&&isFinite(c)){
            varnr=this.getNumberAt(row,column);
            if(nr){
                varfp=nr.value.indexOf(".")>=0?nr.start+nr.value.indexOf(".")+1:nr.end;
                vardecimals=nr.start+nr.value.length-fp;

                vart=parseFloat(nr.value);
                t*=Math.pow(10,decimals);


                if(fp!==nr.end&&column<fp){
                    amount*=Math.pow(10,nr.end-column-1);
                }else{
                    amount*=Math.pow(10,nr.end-column);
                }

                t+=amount;
                t/=Math.pow(10,decimals);
                varnnr=t.toFixed(decimals);
                varreplaceRange=newRange(row,nr.start,row,nr.end);
                this.session.replace(replaceRange,nnr);
                this.moveCursorTo(row,Math.max(nr.start+1,column+nnr.length-nr.value.length));

            }
        }
    };
    this.removeLines=function(){
        varrows=this.$getSelectedRows();
        this.session.removeFullLines(rows.first,rows.last);
        this.clearSelection();
    };

    this.duplicateSelection=function(){
        varsel=this.selection;
        vardoc=this.session;
        varrange=sel.getRange();
        varreverse=sel.isBackwards();
        if(range.isEmpty()){
            varrow=range.start.row;
            doc.duplicateLines(row,row);
        }else{
            varpoint=reverse?range.start:range.end;
            varendPoint=doc.insert(point,doc.getTextRange(range),false);
            range.start=point;
            range.end=endPoint;

            sel.setSelectionRange(range,reverse);
        }
    };
    this.moveLinesDown=function(){
        this.$moveLines(1,false);
    };
    this.moveLinesUp=function(){
        this.$moveLines(-1,false);
    };
    this.moveText=function(range,toPosition,copy){
        returnthis.session.moveText(range,toPosition,copy);
    };
    this.copyLinesUp=function(){
        this.$moveLines(-1,true);
    };
    this.copyLinesDown=function(){
        this.$moveLines(1,true);
    };
    this.$moveLines=function(dir,copy){
        varrows,moved;
        varselection=this.selection;
        if(!selection.inMultiSelectMode||this.inVirtualSelectionMode){
            varrange=selection.toOrientedRange();
            rows=this.$getSelectedRows(range);
            moved=this.session.$moveLines(rows.first,rows.last,copy?0:dir);
            if(copy&&dir==-1)moved=0;
            range.moveBy(moved,0);
            selection.fromOrientedRange(range);
        }else{
            varranges=selection.rangeList.ranges;
            selection.rangeList.detach(this.session);
            this.inVirtualSelectionMode=true;
            
            vardiff=0;
            vartotalDiff=0;
            varl=ranges.length;
            for(vari=0;i<l;i++){
                varrangeIndex=i;
                ranges[i].moveBy(diff,0);
                rows=this.$getSelectedRows(ranges[i]);
                varfirst=rows.first;
                varlast=rows.last;
                while(++i<l){
                    if(totalDiff)ranges[i].moveBy(totalDiff,0);
                    varsubRows=this.$getSelectedRows(ranges[i]);
                    if(copy&&subRows.first!=last)
                        break;
                    elseif(!copy&&subRows.first>last+1)
                        break;
                    last=subRows.last;
                }
                i--;
                diff=this.session.$moveLines(first,last,copy?0:dir);
                if(copy&&dir==-1)rangeIndex=i+1;
                while(rangeIndex<=i){
                    ranges[rangeIndex].moveBy(diff,0);
                    rangeIndex++;
                }
                if(!copy)diff=0;
                totalDiff+=diff;
            }
            
            selection.fromOrientedRange(selection.ranges[0]);
            selection.rangeList.attach(this.session);
            this.inVirtualSelectionMode=false;
        }
    };
    this.$getSelectedRows=function(range){
        range=(range||this.getSelectionRange()).collapseRows();

        return{
            first:this.session.getRowFoldStart(range.start.row),
            last:this.session.getRowFoldEnd(range.end.row)
        };
    };

    this.onCompositionStart=function(text){
        this.renderer.showComposition(this.getCursorPosition());
    };

    this.onCompositionUpdate=function(text){
        this.renderer.setCompositionText(text);
    };

    this.onCompositionEnd=function(){
        this.renderer.hideComposition();
    };
    this.getFirstVisibleRow=function(){
        returnthis.renderer.getFirstVisibleRow();
    };
    this.getLastVisibleRow=function(){
        returnthis.renderer.getLastVisibleRow();
    };
    this.isRowVisible=function(row){
        return(row>=this.getFirstVisibleRow()&&row<=this.getLastVisibleRow());
    };
    this.isRowFullyVisible=function(row){
        return(row>=this.renderer.getFirstFullyVisibleRow()&&row<=this.renderer.getLastFullyVisibleRow());
    };
    this.$getVisibleRowCount=function(){
        returnthis.renderer.getScrollBottomRow()-this.renderer.getScrollTopRow()+1;
    };

    this.$moveByPage=function(dir,select){
        varrenderer=this.renderer;
        varconfig=this.renderer.layerConfig;
        varrows=dir*Math.floor(config.height/config.lineHeight);

        if(select===true){
            this.selection.$moveSelection(function(){
                this.moveCursorBy(rows,0);
            });
        }elseif(select===false){
            this.selection.moveCursorBy(rows,0);
            this.selection.clearSelection();
        }

        varscrollTop=renderer.scrollTop;

        renderer.scrollBy(0,rows*config.lineHeight);
        if(select!=null)
            renderer.scrollCursorIntoView(null,0.5);

        renderer.animateScrolling(scrollTop);
    };
    this.selectPageDown=function(){
        this.$moveByPage(1,true);
    };
    this.selectPageUp=function(){
        this.$moveByPage(-1,true);
    };
    this.gotoPageDown=function(){
       this.$moveByPage(1,false);
    };
    this.gotoPageUp=function(){
        this.$moveByPage(-1,false);
    };
    this.scrollPageDown=function(){
        this.$moveByPage(1);
    };
    this.scrollPageUp=function(){
        this.$moveByPage(-1);
    };
    this.scrollToRow=function(row){
        this.renderer.scrollToRow(row);
    };
    this.scrollToLine=function(line,center,animate,callback){
        this.renderer.scrollToLine(line,center,animate,callback);
    };
    this.centerSelection=function(){
        varrange=this.getSelectionRange();
        varpos={
            row:Math.floor(range.start.row+(range.end.row-range.start.row)/2),
            column:Math.floor(range.start.column+(range.end.column-range.start.column)/2)
        };
        this.renderer.alignCursor(pos,0.5);
    };
    this.getCursorPosition=function(){
        returnthis.selection.getCursor();
    };
    this.getCursorPositionScreen=function(){
        returnthis.session.documentToScreenPosition(this.getCursorPosition());
    };
    this.getSelectionRange=function(){
        returnthis.selection.getRange();
    };
    this.selectAll=function(){
        this.selection.selectAll();
    };
    this.clearSelection=function(){
        this.selection.clearSelection();
    };
    this.moveCursorTo=function(row,column){
        this.selection.moveCursorTo(row,column);
    };
    this.moveCursorToPosition=function(pos){
        this.selection.moveCursorToPosition(pos);
    };
    this.jumpToMatching=function(select,expand){
        varcursor=this.getCursorPosition();
        variterator=newTokenIterator(this.session,cursor.row,cursor.column);
        varprevToken=iterator.getCurrentToken();
        vartoken=prevToken||iterator.stepForward();

        if(!token)return;
        varmatchType;
        varfound=false;
        vardepth={};
        vari=cursor.column-token.start;
        varbracketType;
        varbrackets={
            ")":"(",
            "(":"(",
            "]":"[",
            "[":"[",
            "{":"{",
            "}":"{"
        };
        
        do{
            if(token.value.match(/[{}()\[\]]/g)){
                for(;i<token.value.length&&!found;i++){
                    if(!brackets[token.value[i]]){
                        continue;
                    }

                    bracketType=brackets[token.value[i]]+'.'+token.type.replace("rparen","lparen");

                    if(isNaN(depth[bracketType])){
                        depth[bracketType]=0;
                    }

                    switch(token.value[i]){
                        case'(':
                        case'[':
                        case'{':
                            depth[bracketType]++;
                            break;
                        case')':
                        case']':
                        case'}':
                            depth[bracketType]--;

                            if(depth[bracketType]===-1){
                                matchType='bracket';
                                found=true;
                            }
                        break;
                    }
                }
            }
            elseif(token.type.indexOf('tag-name')!==-1){
                if(isNaN(depth[token.value])){
                    depth[token.value]=0;
                }
                
                if(prevToken.value==='<'){
                    depth[token.value]++;
                }
                elseif(prevToken.value==='</'){
                    depth[token.value]--;
                }
                
                if(depth[token.value]===-1){
                    matchType='tag';
                    found=true;
                }
            }

            if(!found){
                prevToken=token;
                token=iterator.stepForward();
                i=0;
            }
        }while(token&&!found);
        if(!matchType)
            return;

        varrange,pos;
        if(matchType==='bracket'){
            range=this.session.getBracketRange(cursor);
            if(!range){
                range=newRange(
                    iterator.getCurrentTokenRow(),
                    iterator.getCurrentTokenColumn()+i-1,
                    iterator.getCurrentTokenRow(),
                    iterator.getCurrentTokenColumn()+i-1
                );
                pos=range.start;
                if(expand||pos.row===cursor.row&&Math.abs(pos.column-cursor.column)<2)
                    range=this.session.getBracketRange(pos);
            }
        }
        elseif(matchType==='tag'){
            if(token&&token.type.indexOf('tag-name')!==-1)
                vartag=token.value;
            else
                return;

            range=newRange(
                iterator.getCurrentTokenRow(),
                iterator.getCurrentTokenColumn()-2,
                iterator.getCurrentTokenRow(),
                iterator.getCurrentTokenColumn()-2
            );
            if(range.compare(cursor.row,cursor.column)===0){
                found=false;
                do{
                    token=prevToken;
                    prevToken=iterator.stepBackward();
                    
                    if(prevToken){
                        if(prevToken.type.indexOf('tag-close')!==-1){
                            range.setEnd(iterator.getCurrentTokenRow(),iterator.getCurrentTokenColumn()+1);
                        }

                        if(token.value===tag&&token.type.indexOf('tag-name')!==-1){
                            if(prevToken.value==='<'){
                                depth[tag]++;
                            }
                            elseif(prevToken.value==='</'){
                                depth[tag]--;
                            }
                            
                            if(depth[tag]===0)
                                found=true;
                        }
                    }
                }while(prevToken&&!found);
            }
            if(token&&token.type.indexOf('tag-name')){
                pos=range.start;
                if(pos.row==cursor.row&&Math.abs(pos.column-cursor.column)<2)
                    pos=range.end;
            }
        }

        pos=range&&range.cursor||pos;
        if(pos){
            if(select){
                if(range&&expand){
                    this.selection.setRange(range);
                }elseif(range&&range.isEqual(this.getSelectionRange())){
                    this.clearSelection();
                }else{
                    this.selection.selectTo(pos.row,pos.column);
                }
            }else{
                this.selection.moveTo(pos.row,pos.column);
            }
        }
    };
    this.gotoLine=function(lineNumber,column,animate){
        this.selection.clearSelection();
        this.session.unfold({row:lineNumber-1,column:column||0});
        this.exitMultiSelectMode&&this.exitMultiSelectMode();
        this.moveCursorTo(lineNumber-1,column||0);

        if(!this.isRowFullyVisible(lineNumber-1))
            this.scrollToLine(lineNumber-1,true,animate);
    };
    this.navigateTo=function(row,column){
        this.selection.moveTo(row,column);
    };
    this.navigateUp=function(times){
        if(this.selection.isMultiLine()&&!this.selection.isBackwards()){
            varselectionStart=this.selection.anchor.getPosition();
            returnthis.moveCursorToPosition(selectionStart);
        }
        this.selection.clearSelection();
        this.selection.moveCursorBy(-times||-1,0);
    };
    this.navigateDown=function(times){
        if(this.selection.isMultiLine()&&this.selection.isBackwards()){
            varselectionEnd=this.selection.anchor.getPosition();
            returnthis.moveCursorToPosition(selectionEnd);
        }
        this.selection.clearSelection();
        this.selection.moveCursorBy(times||1,0);
    };
    this.navigateLeft=function(times){
        if(!this.selection.isEmpty()){
            varselectionStart=this.getSelectionRange().start;
            this.moveCursorToPosition(selectionStart);
        }
        else{
            times=times||1;
            while(times--){
                this.selection.moveCursorLeft();
            }
        }
        this.clearSelection();
    };
    this.navigateRight=function(times){
        if(!this.selection.isEmpty()){
            varselectionEnd=this.getSelectionRange().end;
            this.moveCursorToPosition(selectionEnd);
        }
        else{
            times=times||1;
            while(times--){
                this.selection.moveCursorRight();
            }
        }
        this.clearSelection();
    };
    this.navigateLineStart=function(){
        this.selection.moveCursorLineStart();
        this.clearSelection();
    };
    this.navigateLineEnd=function(){
        this.selection.moveCursorLineEnd();
        this.clearSelection();
    };
    this.navigateFileEnd=function(){
        this.selection.moveCursorFileEnd();
        this.clearSelection();
    };
    this.navigateFileStart=function(){
        this.selection.moveCursorFileStart();
        this.clearSelection();
    };
    this.navigateWordRight=function(){
        this.selection.moveCursorWordRight();
        this.clearSelection();
    };
    this.navigateWordLeft=function(){
        this.selection.moveCursorWordLeft();
        this.clearSelection();
    };
    this.replace=function(replacement,options){
        if(options)
            this.$search.set(options);

        varrange=this.$search.find(this.session);
        varreplaced=0;
        if(!range)
            returnreplaced;

        if(this.$tryReplace(range,replacement)){
            replaced=1;
        }

        this.selection.setSelectionRange(range);
        this.renderer.scrollSelectionIntoView(range.start,range.end);

        returnreplaced;
    };
    this.replaceAll=function(replacement,options){
        if(options){
            this.$search.set(options);
        }

        varranges=this.$search.findAll(this.session);
        varreplaced=0;
        if(!ranges.length)
            returnreplaced;

        varselection=this.getSelectionRange();
        this.selection.moveTo(0,0);

        for(vari=ranges.length-1;i>=0;--i){
            if(this.$tryReplace(ranges[i],replacement)){
                replaced++;
            }
        }

        this.selection.setSelectionRange(selection);

        returnreplaced;
    };

    this.$tryReplace=function(range,replacement){
        varinput=this.session.getTextRange(range);
        replacement=this.$search.replace(input,replacement);
        if(replacement!==null){
            range.end=this.session.replace(range,replacement);
            returnrange;
        }else{
            returnnull;
        }
    };
    this.getLastSearchOptions=function(){
        returnthis.$search.getOptions();
    };
    this.find=function(needle,options,animate){
        if(!options)
            options={};

        if(typeofneedle=="string"||needleinstanceofRegExp)
            options.needle=needle;
        elseif(typeofneedle=="object")
            oop.mixin(options,needle);

        varrange=this.selection.getRange();
        if(options.needle==null){
            needle=this.session.getTextRange(range)
                ||this.$search.$options.needle;
            if(!needle){
                range=this.session.getWordRange(range.start.row,range.start.column);
                needle=this.session.getTextRange(range);
            }
            this.$search.set({needle:needle});
        }

        this.$search.set(options);
        if(!options.start)
            this.$search.set({start:range});

        varnewRange=this.$search.find(this.session);
        if(options.preventScroll)
            returnnewRange;
        if(newRange){
            this.revealRange(newRange,animate);
            returnnewRange;
        }
        if(options.backwards)
            range.start=range.end;
        else
            range.end=range.start;
        this.selection.setRange(range);
    };
    this.findNext=function(options,animate){
        this.find({skipCurrent:true,backwards:false},options,animate);
    };
    this.findPrevious=function(options,animate){
        this.find(options,{skipCurrent:true,backwards:true},animate);
    };

    this.revealRange=function(range,animate){
        this.session.unfold(range);
        this.selection.setSelectionRange(range);

        varscrollTop=this.renderer.scrollTop;
        this.renderer.scrollSelectionIntoView(range.start,range.end,0.5);
        if(animate!==false)
            this.renderer.animateScrolling(scrollTop);
    };
    this.undo=function(){
        this.session.getUndoManager().undo(this.session);
        this.renderer.scrollCursorIntoView(null,0.5);
    };
    this.redo=function(){
        this.session.getUndoManager().redo(this.session);
        this.renderer.scrollCursorIntoView(null,0.5);
    };
    this.destroy=function(){
        this.renderer.destroy();
        this._signal("destroy",this);
        if(this.session){
            this.session.destroy();
        }
    };
    this.setAutoScrollEditorIntoView=function(enable){
        if(!enable)
            return;
        varrect;
        varself=this;
        varshouldScroll=false;
        if(!this.$scrollAnchor)
            this.$scrollAnchor=document.createElement("div");
        varscrollAnchor=this.$scrollAnchor;
        scrollAnchor.style.cssText="position:absolute";
        this.container.insertBefore(scrollAnchor,this.container.firstChild);
        varonChangeSelection=this.on("changeSelection",function(){
            shouldScroll=true;
        });
        varonBeforeRender=this.renderer.on("beforeRender",function(){
            if(shouldScroll)
                rect=self.renderer.container.getBoundingClientRect();
        });
        varonAfterRender=this.renderer.on("afterRender",function(){
            if(shouldScroll&&rect&&(self.isFocused()
                ||self.searchBox&&self.searchBox.isFocused())
            ){
                varrenderer=self.renderer;
                varpos=renderer.$cursorLayer.$pixelPos;
                varconfig=renderer.layerConfig;
                vartop=pos.top-config.offset;
                if(pos.top>=0&&top+rect.top<0){
                    shouldScroll=true;
                }elseif(pos.top<config.height&&
                    pos.top+rect.top+config.lineHeight>window.innerHeight){
                    shouldScroll=false;
                }else{
                    shouldScroll=null;
                }
                if(shouldScroll!=null){
                    scrollAnchor.style.top=top+"px";
                    scrollAnchor.style.left=pos.left+"px";
                    scrollAnchor.style.height=config.lineHeight+"px";
                    scrollAnchor.scrollIntoView(shouldScroll);
                }
                shouldScroll=rect=null;
            }
        });
        this.setAutoScrollEditorIntoView=function(enable){
            if(enable)
                return;
            deletethis.setAutoScrollEditorIntoView;
            this.off("changeSelection",onChangeSelection);
            this.renderer.off("afterRender",onAfterRender);
            this.renderer.off("beforeRender",onBeforeRender);
        };
    };


    this.$resetCursorStyle=function(){
        varstyle=this.$cursorStyle||"ace";
        varcursorLayer=this.renderer.$cursorLayer;
        if(!cursorLayer)
            return;
        cursorLayer.setSmoothBlinking(/smooth/.test(style));
        cursorLayer.isBlinking=!this.$readOnly&&style!="wide";
        dom.setCssClass(cursorLayer.element,"ace_slim-cursors",/slim/.test(style));
    };

}).call(Editor.prototype);



config.defineOptions(Editor.prototype,"editor",{
    selectionStyle:{
        set:function(style){
            this.onSelectionChange();
            this._signal("changeSelectionStyle",{data:style});
        },
        initialValue:"line"
    },
    highlightActiveLine:{
        set:function(){this.$updateHighlightActiveLine();},
        initialValue:true
    },
    highlightSelectedWord:{
        set:function(shouldHighlight){this.$onSelectionChange();},
        initialValue:true
    },
    readOnly:{
        set:function(readOnly){
            this.textInput.setReadOnly(readOnly);
            this.$resetCursorStyle();
        },
        initialValue:false
    },
    copyWithEmptySelection:{
        set:function(value){
            this.textInput.setCopyWithEmptySelection(value);
        },
        initialValue:false
    },
    cursorStyle:{
        set:function(val){this.$resetCursorStyle();},
        values:["ace","slim","smooth","wide"],
        initialValue:"ace"
    },
    mergeUndoDeltas:{
        values:[false,true,"always"],
        initialValue:true
    },
    behavioursEnabled:{initialValue:true},
    wrapBehavioursEnabled:{initialValue:true},
    autoScrollEditorIntoView:{
        set:function(val){this.setAutoScrollEditorIntoView(val);}
    },
    keyboardHandler:{
        set:function(val){this.setKeyboardHandler(val);},
        get:function(){returnthis.$keybindingId;},
        handlesSet:true
    },
    value:{
        set:function(val){this.session.setValue(val);},
        get:function(){returnthis.getValue();},
        handlesSet:true,
        hidden:true
    },
    session:{
        set:function(val){this.setSession(val);},
        get:function(){returnthis.session;},
        handlesSet:true,
        hidden:true
    },

    hScrollBarAlwaysVisible:"renderer",
    vScrollBarAlwaysVisible:"renderer",
    highlightGutterLine:"renderer",
    animatedScroll:"renderer",
    showInvisibles:"renderer",
    showPrintMargin:"renderer",
    printMarginColumn:"renderer",
    printMargin:"renderer",
    fadeFoldWidgets:"renderer",
    showFoldWidgets:"renderer",
    showLineNumbers:"renderer",
    showGutter:"renderer",
    displayIndentGuides:"renderer",
    fontSize:"renderer",
    fontFamily:"renderer",
    maxLines:"renderer",
    minLines:"renderer",
    scrollPastEnd:"renderer",
    fixedWidthGutter:"renderer",
    theme:"renderer",

    scrollSpeed:"$mouseHandler",
    dragDelay:"$mouseHandler",
    dragEnabled:"$mouseHandler",
    focusTimeout:"$mouseHandler",
    tooltipFollowsMouse:"$mouseHandler",

    firstLineNumber:"session",
    overwrite:"session",
    newLineMode:"session",
    useWorker:"session",
    useSoftTabs:"session",
    navigateWithinSoftTabs:"session",
    tabSize:"session",
    wrap:"session",
    indentedSoftWrap:"session",
    foldStyle:"session",
    mode:"session"
});

exports.Editor=Editor;
});

define("ace/undomanager",["require","exports","module","ace/range"],function(require,exports,module){
"usestrict";
varUndoManager=function(){
    this.$maxRev=0;
    this.$fromUndo=false;
    this.reset();
};

(function(){
    
    this.addSession=function(session){
        this.$session=session;
    };
    this.add=function(delta,allowMerge,session){
        if(this.$fromUndo)return;
        if(delta==this.$lastDelta)return;
        if(allowMerge===false||!this.lastDeltas){
            this.lastDeltas=[];
            this.$undoStack.push(this.lastDeltas);
            delta.id=this.$rev=++this.$maxRev;
        }
        if(delta.action=="remove"||delta.action=="insert")
            this.$lastDelta=delta;
        this.lastDeltas.push(delta);
    };
    
    this.addSelection=function(selection,rev){
        this.selections.push({
            value:selection,
            rev:rev||this.$rev
        });
    };
    
    this.startNewGroup=function(){
        this.lastDeltas=null;
        returnthis.$rev;
    };
    
    this.markIgnored=function(from,to){
        if(to==null)to=this.$rev+1;
        varstack=this.$undoStack;
        for(vari=stack.length;i--;){
            vardelta=stack[i][0];
            if(delta.id<=from)
                break;
            if(delta.id<to)
                delta.ignore=true;
        }
        this.lastDeltas=null;
    };
    
    this.getSelection=function(rev,after){
        varstack=this.selections;
        for(vari=stack.length;i--;){
            varselection=stack[i];
            if(selection.rev<rev){
                if(after)
                    selection=stack[i+1];
                returnselection;
            }
        }
    };
    
    this.getRevision=function(){
        returnthis.$rev;
    };
    
    this.getDeltas=function(from,to){
        if(to==null)to=this.$rev+1;
        varstack=this.$undoStack;
        varend=null,start=0;
        for(vari=stack.length;i--;){
            vardelta=stack[i][0];
            if(delta.id<to&&!end)
                end=i+1;
            if(delta.id<=from){
                start=i+1;
                break;
            }
        }
        returnstack.slice(start,end);
    };
    
    this.getChangedRanges=function(from,to){
        if(to==null)to=this.$rev+1;
        
    };
    
    this.getChangedLines=function(from,to){
        if(to==null)to=this.$rev+1;
        
    };
    this.undo=function(session,dontSelect){
        this.lastDeltas=null;
        varstack=this.$undoStack;
        
        if(!rearrangeUndoStack(stack,stack.length))
            return;
        
        if(!session)
            session=this.$session;
        
        if(this.$redoStackBaseRev!==this.$rev&&this.$redoStack.length)
            this.$redoStack=[];
        
        this.$fromUndo=true;
        
        vardeltaSet=stack.pop();
        varundoSelectionRange=null;
        if(deltaSet&&deltaSet.length){
            undoSelectionRange=session.undoChanges(deltaSet,dontSelect);
            this.$redoStack.push(deltaSet);
            this.$syncRev();
        }
        
        this.$fromUndo=false;

        returnundoSelectionRange;
    };
    this.redo=function(session,dontSelect){
        this.lastDeltas=null;
        
        if(!session)
            session=this.$session;
        
        this.$fromUndo=true;
        if(this.$redoStackBaseRev!=this.$rev){
            vardiff=this.getDeltas(this.$redoStackBaseRev,this.$rev+1);
            rebaseRedoStack(this.$redoStack,diff);
            this.$redoStackBaseRev=this.$rev;
            this.$redoStack.forEach(function(x){
                x[0].id=++this.$maxRev;
            },this);
        }
        vardeltaSet=this.$redoStack.pop();
        varredoSelectionRange=null;
        
        if(deltaSet){
            redoSelectionRange=session.redoChanges(deltaSet,dontSelect);
            this.$undoStack.push(deltaSet);
            this.$syncRev();
        }
        this.$fromUndo=false;
        
        returnredoSelectionRange;
    };
    
    this.$syncRev=function(){
        varstack=this.$undoStack;
        varnextDelta=stack[stack.length-1];
        varid=nextDelta&&nextDelta[0].id||0;
        this.$redoStackBaseRev=id;
        this.$rev=id;
    };
    this.reset=function(){
        this.lastDeltas=null;
        this.$lastDelta=null;
        this.$undoStack=[];
        this.$redoStack=[];
        this.$rev=0;
        this.mark=0;
        this.$redoStackBaseRev=this.$rev;
        this.selections=[];
    };
    this.canUndo=function(){
        returnthis.$undoStack.length>0;
    };
    this.canRedo=function(){
        returnthis.$redoStack.length>0;
    };
    this.bookmark=function(rev){
        if(rev==undefined)
            rev=this.$rev;
        this.mark=rev;
    };
    this.isAtBookmark=function(){
        returnthis.$rev===this.mark;
    };
    
    this.toJSON=function(){
        
    };
    
    this.fromJSON=function(){
        
    };
    
    this.hasUndo=this.canUndo;
    this.hasRedo=this.canRedo;
    this.isClean=this.isAtBookmark;
    this.markClean=this.bookmark;
    
}).call(UndoManager.prototype);

functionrearrangeUndoStack(stack,pos){
    for(vari=pos;i--;){
        vardeltaSet=stack[i];
        if(deltaSet&&!deltaSet[0].ignore){
            while(i<pos-1){
                varswapped=swapGroups(stack[i],stack[i+1]);
                stack[i]=swapped[0];
                stack[i+1]=swapped[1];
                i++;
            }
            returntrue;
        }
    }
}

varRange=require("./range").Range;
varcmp=Range.comparePoints;
varcomparePoints=Range.comparePoints;

function$updateMarkers(delta){
    varisInsert=delta.action=="insert";
    varstart=delta.start;
    varend=delta.end;
    varrowShift=(end.row-start.row)*(isInsert?1:-1);
    varcolShift=(end.column-start.column)*(isInsert?1:-1);
    if(isInsert)end=start;

    for(variinthis.marks){
        varpoint=this.marks[i];
        varcmp=comparePoints(point,start);
        if(cmp<0){
            continue;//deltastartsaftertherange
        }
        if(cmp===0){
            if(isInsert){
                if(point.bias==1){
                    cmp=1;
                }
                else{
                    point.bias==-1;
                    continue;
                }
            }
        }
        varcmp2=isInsert?cmp:comparePoints(point,end);
        if(cmp2>0){
            point.row+=rowShift;
            point.column+=point.row==end.row?colShift:0;
            continue;
        }
        if(!isInsert&&cmp2<=0){
            point.row=start.row;
            point.column=start.column;
            if(cmp2===0)
                point.bias=1;
        }
    }
}



functionclonePos(pos){
    return{row:pos.row,column:pos.column};
}
functioncloneDelta(d){
    return{
        start:clonePos(d.start),
        end:clonePos(d.end),
        action:d.action,
        lines:d.lines.slice()
    };
}
functionstringifyDelta(d){
    d=d||this;
    if(Array.isArray(d)){
        returnd.map(stringifyDelta).join("\n");
    }
    vartype="";
    if(d.action){
        type=d.action=="insert"?"+":"-";
        type+="["+d.lines+"]";
    }elseif(d.value){
        if(Array.isArray(d.value)){
            type=d.value.map(stringifyRange).join("\n");
        }else{
            type=stringifyRange(d.value);
        }
    }
    if(d.start){
        type+=stringifyRange(d);
    }
    if(d.id||d.rev){
        type+="\t("+(d.id||d.rev)+")";
    }
    returntype;
}
functionstringifyRange(r){
    returnr.start.row+":"+r.start.column
        +"=>"+r.end.row+":"+r.end.column;
}

functionswap(d1,d2){
    vari1=d1.action=="insert";
    vari2=d2.action=="insert";
    
    if(i1&&i2){
        if(cmp(d2.start,d1.end)>=0){
            shift(d2,d1,-1);
        }elseif(cmp(d2.start,d1.start)<=0){
            shift(d1,d2,+1);
        }else{
            returnnull;
        }
    }elseif(i1&&!i2){
        if(cmp(d2.start,d1.end)>=0){
            shift(d2,d1,-1);
        }elseif(cmp(d2.end,d1.start)<=0){
            shift(d1,d2,-1);
        }else{
            returnnull;
        }
    }elseif(!i1&&i2){
        if(cmp(d2.start,d1.start)>=0){
            shift(d2,d1,+1);
        }elseif(cmp(d2.start,d1.start)<=0){
            shift(d1,d2,+1);
        }else{
            returnnull;
        }
    }elseif(!i1&&!i2){
        if(cmp(d2.start,d1.start)>=0){
            shift(d2,d1,+1);
        }elseif(cmp(d2.end,d1.start)<=0){
            shift(d1,d2,-1);
        }else{
            returnnull;
        }
    }
    return[d2,d1];
}
functionswapGroups(ds1,ds2){
    for(vari=ds1.length;i--;){
        for(varj=0;j<ds2.length;j++){
            if(!swap(ds1[i],ds2[j])){
                while(i<ds1.length){
                    while(j--){
                        swap(ds2[j],ds1[i]);
                    }
                    j=ds2.length;
                    i++;
                }               
                return[ds1,ds2];
            }
        }
    }
    ds1.selectionBefore=ds2.selectionBefore=
    ds1.selectionAfter=ds2.selectionAfter=null;
    return[ds2,ds1];
}
functionxform(d1,c1){
    vari1=d1.action=="insert";
    vari2=c1.action=="insert";
    
    if(i1&&i2){
        if(cmp(d1.start,c1.start)<0){
            shift(c1,d1,1);
        }else{
            shift(d1,c1,1);
        }
    }elseif(i1&&!i2){
        if(cmp(d1.start,c1.end)>=0){
            shift(d1,c1,-1);
        }elseif(cmp(d1.start,c1.start)<=0){
            shift(c1,d1,+1);
        }else{
            shift(d1,Range.fromPoints(c1.start,d1.start),-1);
            shift(c1,d1,+1);
        }
    }elseif(!i1&&i2){
        if(cmp(c1.start,d1.end)>=0){
            shift(c1,d1,-1);
        }elseif(cmp(c1.start,d1.start)<=0){
            shift(d1,c1,+1);
        }else{
            shift(c1,Range.fromPoints(d1.start,c1.start),-1);
            shift(d1,c1,+1);
        }
    }elseif(!i1&&!i2){
        if(cmp(c1.start,d1.end)>=0){
            shift(c1,d1,-1);
        }elseif(cmp(c1.end,d1.start)<=0){
            shift(d1,c1,-1);
        }else{
            varbefore,after;
            if(cmp(d1.start,c1.start)<0){
                before=d1;
                d1=splitDelta(d1,c1.start);
            }
            if(cmp(d1.end,c1.end)>0){
                after=splitDelta(d1,c1.end);
            }

            shiftPos(c1.end,d1.start,d1.end,-1);
            if(after&&!before){
                d1.lines=after.lines;
                d1.start=after.start;
                d1.end=after.end;
                after=d1;
            }

            return[c1,before,after].filter(Boolean);
        }
    }
    return[c1,d1];
}
    
functionshift(d1,d2,dir){
    shiftPos(d1.start,d2.start,d2.end,dir);
    shiftPos(d1.end,d2.start,d2.end,dir);
}
functionshiftPos(pos,start,end,dir){
    if(pos.row==(dir==1?start:end).row){
        pos.column+=dir*(end.column-start.column);
    }
    pos.row+=dir*(end.row-start.row);
}
functionsplitDelta(c,pos){
    varlines=c.lines;
    varend=c.end;
    c.end=clonePos(pos);   
    varrowsBefore=c.end.row-c.start.row;
    varotherLines=lines.splice(rowsBefore,lines.length);
    
    varcol=rowsBefore?pos.column:pos.column-c.start.column;
    lines.push(otherLines[0].substring(0,col));
    otherLines[0]=otherLines[0].substr(col)  ;
    varrest={
        start:clonePos(pos),
        end:end,
        lines:otherLines,
        action:c.action
    };
    returnrest;
}

functionmoveDeltasByOne(redoStack,d){
    d=cloneDelta(d);
    for(varj=redoStack.length;j--;){
        vardeltaSet=redoStack[j];
        for(vari=deltaSet.length;i-->0;){
            varx=deltaSet[i];
            varxformed=xform(x,d);
            d=xformed[0];
            if(xformed.length!=2){
                if(xformed[2]){
                    redoStack.splice(i+1,1,xformed[1],xformed[2]);
                    i++;
                }elseif(!xformed[1]){
                    redoStack.splice(i,1);
                    i--;
                }
            }
        }
    }
    returnredoStack;
}
functionrebaseRedoStack(redoStack,deltaSets){
    for(vari=0;i<deltaSets.length;i++){
        vardeltas=deltaSets[i];
        for(varj=0;j<deltas.length;j++){
            moveDeltasByOne(redoStack,deltas[j]);
        }
    }
}

exports.UndoManager=UndoManager;

});

define("ace/layer/gutter",["require","exports","module","ace/lib/dom","ace/lib/oop","ace/lib/lang","ace/lib/event_emitter"],function(require,exports,module){
"usestrict";

vardom=require("../lib/dom");
varoop=require("../lib/oop");
varlang=require("../lib/lang");
varEventEmitter=require("../lib/event_emitter").EventEmitter;

varGutter=function(parentEl){
    this.element=dom.createElement("div");
    this.element.className="ace_layerace_gutter-layer";
    parentEl.appendChild(this.element);
    this.setShowFoldWidgets(this.$showFoldWidgets);
    
    this.gutterWidth=0;

    this.$annotations=[];
    this.$updateAnnotations=this.$updateAnnotations.bind(this);

    this.$cells=[];
};

(function(){

    oop.implement(this,EventEmitter);

    this.setSession=function(session){
        if(this.session)
            this.session.removeEventListener("change",this.$updateAnnotations);
        this.session=session;
        if(session)
            session.on("change",this.$updateAnnotations);
    };

    this.addGutterDecoration=function(row,className){
        if(window.console)
            console.warn&&console.warn("deprecatedusesession.addGutterDecoration");
        this.session.addGutterDecoration(row,className);
    };

    this.removeGutterDecoration=function(row,className){
        if(window.console)
            console.warn&&console.warn("deprecatedusesession.removeGutterDecoration");
        this.session.removeGutterDecoration(row,className);
    };

    this.setAnnotations=function(annotations){
        this.$annotations=[];
        for(vari=0;i<annotations.length;i++){
            varannotation=annotations[i];
            varrow=annotation.row;
            varrowInfo=this.$annotations[row];
            if(!rowInfo)
                rowInfo=this.$annotations[row]={text:[]};
           
            varannoText=annotation.text;
            annoText=annoText?lang.escapeHTML(annoText):annotation.html||"";

            if(rowInfo.text.indexOf(annoText)===-1)
                rowInfo.text.push(annoText);

            vartype=annotation.type;
            if(type=="error")
                rowInfo.className="ace_error";
            elseif(type=="warning"&&rowInfo.className!="ace_error")
                rowInfo.className="ace_warning";
            elseif(type=="info"&&(!rowInfo.className))
                rowInfo.className="ace_info";
        }
    };

    this.$updateAnnotations=function(delta){
        if(!this.$annotations.length)
            return;
        varfirstRow=delta.start.row;
        varlen=delta.end.row-firstRow;
        if(len===0){
        }elseif(delta.action=='remove'){
            this.$annotations.splice(firstRow,len+1,null);
        }else{
            varargs=newArray(len+1);
            args.unshift(firstRow,1);
            this.$annotations.splice.apply(this.$annotations,args);
        }
    };

    this.update=function(config){
        varsession=this.session;
        varfirstRow=config.firstRow;
        varlastRow=Math.min(config.lastRow+config.gutterOffset, //neededtocompensateforhorscollbar
            session.getLength()-1);
        varfold=session.getNextFoldLine(firstRow);
        varfoldStart=fold?fold.start.row:Infinity;
        varfoldWidgets=this.$showFoldWidgets&&session.foldWidgets;
        varbreakpoints=session.$breakpoints;
        vardecorations=session.$decorations;
        varfirstLineNumber=session.$firstLineNumber;
        varlastLineNumber=0;
        
        vargutterRenderer=session.gutterRenderer||this.$renderer;

        varcell=null;
        varindex=-1;
        varrow=firstRow;
        while(true){
            if(row>foldStart){
                row=fold.end.row+1;
                fold=session.getNextFoldLine(row,fold);
                foldStart=fold?fold.start.row:Infinity;
            }
            if(row>lastRow){
                while(this.$cells.length>index+1){
                    cell=this.$cells.pop();
                    this.element.removeChild(cell.element);
                }
                break;
            }

            cell=this.$cells[++index];
            if(!cell){
                cell={element:null,textNode:null,foldWidget:null};
                cell.element=dom.createElement("div");
                cell.textNode=document.createTextNode('');
                cell.element.appendChild(cell.textNode);
                this.element.appendChild(cell.element);
                this.$cells[index]=cell;
            }

            varclassName="ace_gutter-cell";
            if(breakpoints[row])
                className+=breakpoints[row];
            if(decorations[row])
                className+=decorations[row];
            if(this.$annotations[row])
                className+=this.$annotations[row].className;
            if(cell.element.className!=className)
                cell.element.className=className;

            varheight=session.getRowLength(row)*config.lineHeight+"px";
            if(height!=cell.element.style.height)
                cell.element.style.height=height;

            if(foldWidgets){
                varc=foldWidgets[row];
                if(c==null)
                    c=foldWidgets[row]=session.getFoldWidget(row);
            }

            if(c){
                if(!cell.foldWidget){
                    cell.foldWidget=dom.createElement("span");
                    cell.element.appendChild(cell.foldWidget);
                }
                varclassName="ace_fold-widgetace_"+c;
                if(c=="start"&&row==foldStart&&row<fold.end.row)
                    className+="ace_closed";
                else
                    className+="ace_open";
                if(cell.foldWidget.className!=className)
                    cell.foldWidget.className=className;

                varheight=config.lineHeight+"px";
                if(cell.foldWidget.style.height!=height)
                    cell.foldWidget.style.height=height;
            }else{
                if(cell.foldWidget){
                    cell.element.removeChild(cell.foldWidget);
                    cell.foldWidget=null;
                }
            }
            
            vartext=lastLineNumber=gutterRenderer
                ?gutterRenderer.getText(session,row)
                :row+firstLineNumber;
            if(text!==cell.textNode.data)
                cell.textNode.data=text;

            row++;
        }

        this.element.style.height=config.minHeight+"px";

        if(this.$fixedWidth||session.$useWrapMode)
            lastLineNumber=session.getLength()+firstLineNumber;

        vargutterWidth=gutterRenderer
            ?gutterRenderer.getWidth(session,lastLineNumber,config)
            :lastLineNumber.toString().length*config.characterWidth;
        
        varpadding=this.$padding||this.$computePadding();
        gutterWidth+=padding.left+padding.right;
        if(gutterWidth!==this.gutterWidth&&!isNaN(gutterWidth)){
            this.gutterWidth=gutterWidth;
            this.element.style.width=Math.ceil(this.gutterWidth)+"px";
            this._emit("changeGutterWidth",gutterWidth);
        }
    };

    this.$fixedWidth=false;
    
    this.$showLineNumbers=true;
    this.$renderer="";
    this.setShowLineNumbers=function(show){
        this.$renderer=!show&&{
            getWidth:function(){return"";},
            getText:function(){return"";}
        };
    };
    
    this.getShowLineNumbers=function(){
        returnthis.$showLineNumbers;
    };
    
    this.$showFoldWidgets=true;
    this.setShowFoldWidgets=function(show){
        if(show)
            dom.addCssClass(this.element,"ace_folding-enabled");
        else
            dom.removeCssClass(this.element,"ace_folding-enabled");

        this.$showFoldWidgets=show;
        this.$padding=null;
    };
    
    this.getShowFoldWidgets=function(){
        returnthis.$showFoldWidgets;
    };

    this.$computePadding=function(){
        if(!this.element.firstChild)
            return{left:0,right:0};
        varstyle=dom.computedStyle(this.element.firstChild);
        this.$padding={};
        this.$padding.left=parseInt(style.paddingLeft)+1||0;
        this.$padding.right=parseInt(style.paddingRight)||0;
        returnthis.$padding;
    };

    this.getRegion=function(point){
        varpadding=this.$padding||this.$computePadding();
        varrect=this.element.getBoundingClientRect();
        if(point.x<padding.left+rect.left)
            return"markers";
        if(this.$showFoldWidgets&&point.x>rect.right-padding.right)
            return"foldWidgets";
    };

}).call(Gutter.prototype);

exports.Gutter=Gutter;

});

define("ace/layer/marker",["require","exports","module","ace/range","ace/lib/dom"],function(require,exports,module){
"usestrict";

varRange=require("../range").Range;
vardom=require("../lib/dom");

varMarker=function(parentEl){
    this.element=dom.createElement("div");
    this.element.className="ace_layerace_marker-layer";
    parentEl.appendChild(this.element);
};

(function(){

    this.$padding=0;

    this.setPadding=function(padding){
        this.$padding=padding;
    };
    this.setSession=function(session){
        this.session=session;
    };
    
    this.setMarkers=function(markers){
        this.markers=markers;
    };

    this.update=function(config){
        if(!config)return;

        this.config=config;


        varhtml=[];
        for(varkeyinthis.markers){
            varmarker=this.markers[key];

            if(!marker.range){
                marker.update(html,this,this.session,config);
                continue;
            }

            varrange=marker.range.clipRows(config.firstRow,config.lastRow);
            if(range.isEmpty())continue;

            range=range.toScreenRange(this.session);
            if(marker.renderer){
                vartop=this.$getTop(range.start.row,config);
                varleft=this.$padding+(this.session.$bidiHandler.isBidiRow(range.start.row)
                    ?this.session.$bidiHandler.getPosLeft(range.start.column)
                    :range.start.column*config.characterWidth);
                marker.renderer(html,range,left,top,config);
            }elseif(marker.type=="fullLine"){
                this.drawFullLineMarker(html,range,marker.clazz,config);
            }elseif(marker.type=="screenLine"){
                this.drawScreenLineMarker(html,range,marker.clazz,config);
            }elseif(range.isMultiLine()){
                if(marker.type=="text")
                    this.drawTextMarker(html,range,marker.clazz,config);
                else
                    this.drawMultiLineMarker(html,range,marker.clazz,config);
            }else{
                if(this.session.$bidiHandler.isBidiRow(range.start.row)){
                    this.drawBidiSingleLineMarker(html,range,marker.clazz+"ace_start"+"ace_br15",config);
                }else{
                    this.drawSingleLineMarker(html,range,marker.clazz+"ace_start"+"ace_br15",config);
                }
            }
        }
        this.element.innerHTML=html.join("");
    };

    this.$getTop=function(row,layerConfig){
        return(row-layerConfig.firstRowScreen)*layerConfig.lineHeight;
    };

    functiongetBorderClass(tl,tr,br,bl){
        return(tl?1:0)|(tr?2:0)|(br?4:0)|(bl?8:0);
    }
    this.drawTextMarker=function(stringBuilder,range,clazz,layerConfig,extraStyle){
        varsession=this.session;
        varstart=range.start.row;
        varend=range.end.row;
        varrow=start;
        varprev=0;
        varcurr=0;
        varnext=session.getScreenLastRowColumn(row);
        varclazzModified=null;
        varlineRange=newRange(row,range.start.column,row,curr);
        for(;row<=end;row++){
            lineRange.start.row=lineRange.end.row=row;
            lineRange.start.column=row==start?range.start.column:session.getRowWrapIndent(row);
            lineRange.end.column=next;
            prev=curr;
            curr=next;
            next=row+1<end?session.getScreenLastRowColumn(row+1):row==end?0:range.end.column;
            clazzModified=clazz+(row==start ?"ace_start":"")+"ace_br"
                +getBorderClass(row==start||row==start+1&&range.start.column,prev<curr,curr>next,row==end);
            
            if(this.session.$bidiHandler.isBidiRow(row)){
                this.drawBidiSingleLineMarker(stringBuilder,lineRange,clazzModified,
                    layerConfig,row==end?0:1,extraStyle);
            }else{
                this.drawSingleLineMarker(stringBuilder,lineRange,clazzModified, 
                    layerConfig,row==end?0:1,extraStyle);
            }
        }
    };
    this.drawMultiLineMarker=function(stringBuilder,range,clazz,config,extraStyle){
        varpadding=this.$padding;
        varheight,top,left;
        extraStyle=extraStyle||"";
       if(this.session.$bidiHandler.isBidiRow(range.start.row)){
           varrange1=range.clone();
           range1.end.row=range1.start.row;
           range1.end.column=this.session.getLine(range1.start.row).length;
           this.drawBidiSingleLineMarker(stringBuilder,range1,clazz+"ace_br1ace_start",config,null,extraStyle);
        }else{
           height=config.lineHeight;
           top=this.$getTop(range.start.row,config);
           left=padding+range.start.column*config.characterWidth;
           stringBuilder.push(
               "<divclass='",clazz,"ace_br1ace_start'style='",
               "height:",height,"px;",
               "right:0;",
               "top:",top,"px;",
               "left:",left,"px;",extraStyle,"'></div>"
           );
        }
        if(this.session.$bidiHandler.isBidiRow(range.end.row)){
           varrange1=range.clone();
           range1.start.row=range1.end.row;
           range1.start.column=0;
           this.drawBidiSingleLineMarker(stringBuilder,range1,clazz+"ace_br12",config,null,extraStyle);
        }else{
           varwidth=range.end.column*config.characterWidth;
           height=config.lineHeight;
           top=this.$getTop(range.end.row,config);
           stringBuilder.push(
               "<divclass='",clazz,"ace_br12'style='",
               "height:",height,"px;",
               "width:",width,"px;",
               "top:",top,"px;",
               "left:",padding,"px;",extraStyle,"'></div>"
           );
        }
        height=(range.end.row-range.start.row-1)*config.lineHeight;
        if(height<=0)
            return;
        top=this.$getTop(range.start.row+1,config);
        
        varradiusClass=(range.start.column?1:0)|(range.end.column?0:8);

        stringBuilder.push(
            "<divclass='",clazz,(radiusClass?"ace_br"+radiusClass:""),"'style='",
            "height:",height,"px;",
            "right:0;",
            "top:",top,"px;",
            "left:",padding,"px;",extraStyle,"'></div>"
        );
    };
    this.drawSingleLineMarker=function(stringBuilder,range,clazz,config,extraLength,extraStyle){
        varheight=config.lineHeight;
        varwidth=(range.end.column+(extraLength||0)-range.start.column)*config.characterWidth;

        vartop=this.$getTop(range.start.row,config);
        varleft=this.$padding+range.start.column*config.characterWidth;

        stringBuilder.push(
            "<divclass='",clazz,"'style='",
            "height:",height,"px;",
            "width:",width,"px;",
            "top:",top,"px;",
            "left:",left,"px;",extraStyle||"","'></div>"
        );
    };
    this.drawBidiSingleLineMarker=function(stringBuilder,range,clazz,config,extraLength,extraStyle){
        varheight=config.lineHeight,top=this.$getTop(range.start.row,config),padding=this.$padding;
        varselections=this.session.$bidiHandler.getSelections(range.start.column,range.end.column);

        selections.forEach(function(selection){
            stringBuilder.push(
                "<divclass='",clazz,"'style='",
                "height:",height,"px;",
                "width:",selection.width+(extraLength||0),"px;",
                "top:",top,"px;",
                "left:",padding+selection.left,"px;",extraStyle||"","'></div>"
            );
        });
    };

    this.drawFullLineMarker=function(stringBuilder,range,clazz,config,extraStyle){
        vartop=this.$getTop(range.start.row,config);
        varheight=config.lineHeight;
        if(range.start.row!=range.end.row)
            height+=this.$getTop(range.end.row,config)-top;

        stringBuilder.push(
            "<divclass='",clazz,"'style='",
            "height:",height,"px;",
            "top:",top,"px;",
            "left:0;right:0;",extraStyle||"","'></div>"
        );
    };
    
    this.drawScreenLineMarker=function(stringBuilder,range,clazz,config,extraStyle){
        vartop=this.$getTop(range.start.row,config);
        varheight=config.lineHeight;

        stringBuilder.push(
            "<divclass='",clazz,"'style='",
            "height:",height,"px;",
            "top:",top,"px;",
            "left:0;right:0;",extraStyle||"","'></div>"
        );
    };

}).call(Marker.prototype);

exports.Marker=Marker;

});

define("ace/layer/text",["require","exports","module","ace/lib/oop","ace/lib/dom","ace/lib/lang","ace/lib/useragent","ace/lib/event_emitter"],function(require,exports,module){
"usestrict";

varoop=require("../lib/oop");
vardom=require("../lib/dom");
varlang=require("../lib/lang");
varuseragent=require("../lib/useragent");
varEventEmitter=require("../lib/event_emitter").EventEmitter;

varText=function(parentEl){
    this.element=dom.createElement("div");
    this.element.className="ace_layerace_text-layer";
    parentEl.appendChild(this.element);
    this.$updateEolChar=this.$updateEolChar.bind(this);
};

(function(){

    oop.implement(this,EventEmitter);

    this.EOF_CHAR="\xB6";
    this.EOL_CHAR_LF="\xAC";
    this.EOL_CHAR_CRLF="\xa4";
    this.EOL_CHAR=this.EOL_CHAR_LF;
    this.TAB_CHAR="\u2014";//"\u21E5";
    this.SPACE_CHAR="\xB7";
    this.$padding=0;
    this.MAX_LINE_LENGTH=10000;

    this.$updateEolChar=function(){
        varEOL_CHAR=this.session.doc.getNewLineCharacter()=="\n"
           ?this.EOL_CHAR_LF
           :this.EOL_CHAR_CRLF;
        if(this.EOL_CHAR!=EOL_CHAR){
            this.EOL_CHAR=EOL_CHAR;
            returntrue;
        }
    };

    this.setPadding=function(padding){
        this.$padding=padding;
        this.element.style.padding="0"+padding+"px";
    };

    this.getLineHeight=function(){
        returnthis.$fontMetrics.$characterSize.height||0;
    };

    this.getCharacterWidth=function(){
        returnthis.$fontMetrics.$characterSize.width||0;
    };
    
    this.$setFontMetrics=function(measure){
        this.$fontMetrics=measure;
        this.$fontMetrics.on("changeCharacterSize",function(e){
            this._signal("changeCharacterSize",e);
        }.bind(this));
        this.$pollSizeChanges();
    };

    this.checkForSizeChanges=function(){
        this.$fontMetrics.checkForSizeChanges();
    };
    this.$pollSizeChanges=function(){
        returnthis.$pollSizeChangesTimer=this.$fontMetrics.$pollSizeChanges();
    };
    this.setSession=function(session){
        this.session=session;
        if(session)
            this.$computeTabString();
    };

    this.showInvisibles=false;
    this.setShowInvisibles=function(showInvisibles){
        if(this.showInvisibles==showInvisibles)
            returnfalse;

        this.showInvisibles=showInvisibles;
        this.$computeTabString();
        returntrue;
    };

    this.displayIndentGuides=true;
    this.setDisplayIndentGuides=function(display){
        if(this.displayIndentGuides==display)
            returnfalse;

        this.displayIndentGuides=display;
        this.$computeTabString();
        returntrue;
    };

    this.$tabStrings=[];
    this.onChangeTabSize=
    this.$computeTabString=function(){
        vartabSize=this.session.getTabSize();
        this.tabSize=tabSize;
        vartabStr=this.$tabStrings=[0];
        for(vari=1;i<tabSize+1;i++){
            if(this.showInvisibles){
                tabStr.push("<spanclass='ace_invisibleace_invisible_tab'>"
                    +lang.stringRepeat(this.TAB_CHAR,i)
                    +"</span>");
            }else{
                tabStr.push(lang.stringRepeat("",i));
            }
        }
        if(this.displayIndentGuides){
            this.$indentGuideRe= /\s\S|\t|\t|\s$/;
            varclassName="ace_indent-guide";
            varspaceClass="";
            vartabClass="";
            if(this.showInvisibles){
                className+="ace_invisible";
                spaceClass="ace_invisible_space";
                tabClass="ace_invisible_tab";
                varspaceContent=lang.stringRepeat(this.SPACE_CHAR,this.tabSize);
                vartabContent=lang.stringRepeat(this.TAB_CHAR,this.tabSize);
            }else{
                varspaceContent=lang.stringRepeat("",this.tabSize);
                vartabContent=spaceContent;
            }

            this.$tabStrings[""]="<spanclass='"+className+spaceClass+"'>"+spaceContent+"</span>";
            this.$tabStrings["\t"]="<spanclass='"+className+tabClass+"'>"+tabContent+"</span>";
        }
    };

    this.updateLines=function(config,firstRow,lastRow){
        if(this.config.lastRow!=config.lastRow||
            this.config.firstRow!=config.firstRow){
            this.scrollLines(config);
        }
        this.config=config;

        varfirst=Math.max(firstRow,config.firstRow);
        varlast=Math.min(lastRow,config.lastRow);

        varlineElements=this.element.childNodes;
        varlineElementsIdx=0;

        for(varrow=config.firstRow;row<first;row++){
            varfoldLine=this.session.getFoldLine(row);
            if(foldLine){
                if(foldLine.containsRow(first)){
                    first=foldLine.start.row;
                    break;
                }else{
                    row=foldLine.end.row;
                }
            }
            lineElementsIdx++;
        }

        varrow=first;
        varfoldLine=this.session.getNextFoldLine(row);
        varfoldStart=foldLine?foldLine.start.row:Infinity;

        while(true){
            if(row>foldStart){
                row=foldLine.end.row+1;
                foldLine=this.session.getNextFoldLine(row,foldLine);
                foldStart=foldLine?foldLine.start.row:Infinity;
            }
            if(row>last)
                break;

            varlineElement=lineElements[lineElementsIdx++];
            if(lineElement){
                varhtml=[];
                this.$renderLine(
                    html,row,!this.$useLineGroups(),row==foldStart?foldLine:false
                );
                lineElement.style.height=config.lineHeight*this.session.getRowLength(row)+"px";
                lineElement.innerHTML=html.join("");
            }
            row++;
        }
    };

    this.scrollLines=function(config){
        varoldConfig=this.config;
        this.config=config;

        if(!oldConfig||oldConfig.lastRow<config.firstRow)
            returnthis.update(config);

        if(config.lastRow<oldConfig.firstRow)
            returnthis.update(config);

        varel=this.element;
        if(oldConfig.firstRow<config.firstRow)
            for(varrow=this.session.getFoldedRowCount(oldConfig.firstRow,config.firstRow-1);row>0;row--)
                el.removeChild(el.firstChild);

        if(oldConfig.lastRow>config.lastRow)
            for(varrow=this.session.getFoldedRowCount(config.lastRow+1,oldConfig.lastRow);row>0;row--)
                el.removeChild(el.lastChild);

        if(config.firstRow<oldConfig.firstRow){
            varfragment=this.$renderLinesFragment(config,config.firstRow,oldConfig.firstRow-1);
            if(el.firstChild)
                el.insertBefore(fragment,el.firstChild);
            else
                el.appendChild(fragment);
        }

        if(config.lastRow>oldConfig.lastRow){
            varfragment=this.$renderLinesFragment(config,oldConfig.lastRow+1,config.lastRow);
            el.appendChild(fragment);
        }
    };

    this.$renderLinesFragment=function(config,firstRow,lastRow){
        varfragment=this.element.ownerDocument.createDocumentFragment();
        varrow=firstRow;
        varfoldLine=this.session.getNextFoldLine(row);
        varfoldStart=foldLine?foldLine.start.row:Infinity;

        while(true){
            if(row>foldStart){
                row=foldLine.end.row+1;
                foldLine=this.session.getNextFoldLine(row,foldLine);
                foldStart=foldLine?foldLine.start.row:Infinity;
            }
            if(row>lastRow)
                break;

            varcontainer=dom.createElement("div");

            varhtml=[];
            this.$renderLine(html,row,false,row==foldStart?foldLine:false);
            container.innerHTML=html.join("");
            if(this.$useLineGroups()){
                container.className='ace_line_group';
                fragment.appendChild(container);
                container.style.height=config.lineHeight*this.session.getRowLength(row)+"px";

            }else{
                while(container.firstChild)
                    fragment.appendChild(container.firstChild);
            }

            row++;
        }
        returnfragment;
    };

    this.update=function(config){
        this.config=config;

        varhtml=[];
        varfirstRow=config.firstRow,lastRow=config.lastRow;

        varrow=firstRow;
        varfoldLine=this.session.getNextFoldLine(row);
        varfoldStart=foldLine?foldLine.start.row:Infinity;

        while(true){
            if(row>foldStart){
                row=foldLine.end.row+1;
                foldLine=this.session.getNextFoldLine(row,foldLine);
                foldStart=foldLine?foldLine.start.row:Infinity;
            }
            if(row>lastRow)
                break;

            if(this.$useLineGroups())
                html.push("<divclass='ace_line_group'style='height:",config.lineHeight*this.session.getRowLength(row),"px'>");

            this.$renderLine(html,row,false,row==foldStart?foldLine:false);

            if(this.$useLineGroups())
                html.push("</div>");//endthelinegroup

            row++;
        }
        this.element.innerHTML=html.join("");
    };

    this.$textToken={
        "text":true,
        "rparen":true,
        "lparen":true
    };

    this.$renderToken=function(stringBuilder,screenColumn,token,value){
        varself=this;
        varreplaceReg=/\t|&|<|>|(+)|([\x00-\x1f\x80-\xa0\xad\u1680\u180E\u2000-\u200f\u2028\u2029\u202F\u205F\u3000\uFEFF\uFFF9-\uFFFC])|[\u1100-\u115F\u11A3-\u11A7\u11FA-\u11FF\u2329-\u232A\u2E80-\u2E99\u2E9B-\u2EF3\u2F00-\u2FD5\u2FF0-\u2FFB\u3000-\u303E\u3041-\u3096\u3099-\u30FF\u3105-\u312D\u3131-\u318E\u3190-\u31BA\u31C0-\u31E3\u31F0-\u321E\u3220-\u3247\u3250-\u32FE\u3300-\u4DBF\u4E00-\uA48C\uA490-\uA4C6\uA960-\uA97C\uAC00-\uD7A3\uD7B0-\uD7C6\uD7CB-\uD7FB\uF900-\uFAFF\uFE10-\uFE19\uFE30-\uFE52\uFE54-\uFE66\uFE68-\uFE6B\uFF01-\uFF60\uFFE0-\uFFE6]|[\uD800-\uDBFF][\uDC00-\uDFFF]/g;
        varreplaceFunc=function(c,a,b,tabIdx,idx4){
            if(a){
                returnself.showInvisibles
                    ?"<spanclass='ace_invisibleace_invisible_space'>"+lang.stringRepeat(self.SPACE_CHAR,c.length)+"</span>"
                    :c;
            }elseif(c=="&"){
                return"&#38;";
            }elseif(c=="<"){
                return"&#60;";
            }elseif(c==">"){
                return"&#62;";
            }elseif(c=="\t"){
                vartabSize=self.session.getScreenTabSize(screenColumn+tabIdx);
                screenColumn+=tabSize-1;
                returnself.$tabStrings[tabSize];
            }elseif(c=="\u3000"){
                varclassToUse=self.showInvisibles?"ace_cjkace_invisibleace_invisible_space":"ace_cjk";
                varspace=self.showInvisibles?self.SPACE_CHAR:"";
                screenColumn+=1;
                return"<spanclass='"+classToUse+"'style='width:"+
                    (self.config.characterWidth*2)+
                    "px'>"+space+"</span>";
            }elseif(b){
                return"<spanclass='ace_invisibleace_invisible_spaceace_invalid'>"+self.SPACE_CHAR+"</span>";
            }else{
                screenColumn+=1;
                return"<spanclass='ace_cjk'style='width:"+
                    (self.config.characterWidth*2)+
                    "px'>"+c+"</span>";
            }
        };

        varoutput=value.replace(replaceReg,replaceFunc);

        if(!this.$textToken[token.type]){
            varclasses="ace_"+token.type.replace(/\./g,"ace_");
            varstyle="";
            if(token.type=="fold")
                style="style='width:"+(token.value.length*this.config.characterWidth)+"px;'";
            stringBuilder.push("<spanclass='",classes,"'",style,">",output,"</span>");
        }
        else{
            stringBuilder.push(output);
        }
        returnscreenColumn+value.length;
    };

    this.renderIndentGuide=function(stringBuilder,value,max){
        varcols=value.search(this.$indentGuideRe);
        if(cols<=0||cols>=max)
            returnvalue;
        if(value[0]==""){
            cols-=cols%this.tabSize;
            stringBuilder.push(lang.stringRepeat(this.$tabStrings[""],cols/this.tabSize));
            returnvalue.substr(cols);
        }elseif(value[0]=="\t"){
            stringBuilder.push(lang.stringRepeat(this.$tabStrings["\t"],cols));
            returnvalue.substr(cols);
        }
        returnvalue;
    };

    this.$renderWrappedLine=function(stringBuilder,tokens,splits,onlyContents){
        varchars=0;
        varsplit=0;
        varsplitChars=splits[0];
        varscreenColumn=0;

        for(vari=0;i<tokens.length;i++){
            vartoken=tokens[i];
            varvalue=token.value;
            if(i==0&&this.displayIndentGuides){
                chars=value.length;
                value=this.renderIndentGuide(stringBuilder,value,splitChars);
                if(!value)
                    continue;
                chars-=value.length;
            }

            if(chars+value.length<splitChars){
                screenColumn=this.$renderToken(stringBuilder,screenColumn,token,value);
                chars+=value.length;
            }else{
                while(chars+value.length>=splitChars){
                    screenColumn=this.$renderToken(
                        stringBuilder,screenColumn,
                        token,value.substring(0,splitChars-chars)
                    );
                    value=value.substring(splitChars-chars);
                    chars=splitChars;

                    if(!onlyContents){
                        stringBuilder.push("</div>",
                            "<divclass='ace_line'style='height:",
                            this.config.lineHeight,"px'>"
                        );
                    }

                    stringBuilder.push(lang.stringRepeat("\xa0",splits.indent));

                    split++;
                    screenColumn=0;
                    splitChars=splits[split]||Number.MAX_VALUE;
                }
                if(value.length!=0){
                    chars+=value.length;
                    screenColumn=this.$renderToken(
                        stringBuilder,screenColumn,token,value
                    );
                }
            }
        }
    };

    this.$renderSimpleLine=function(stringBuilder,tokens){
        varscreenColumn=0;
        vartoken=tokens[0];
        varvalue=token.value;
        if(this.displayIndentGuides)
            value=this.renderIndentGuide(stringBuilder,value);
        if(value)
            screenColumn=this.$renderToken(stringBuilder,screenColumn,token,value);
        for(vari=1;i<tokens.length;i++){
            token=tokens[i];
            value=token.value;
            if(screenColumn+value.length>this.MAX_LINE_LENGTH)
                returnthis.$renderOverflowMessage(stringBuilder,screenColumn,token,value);
            screenColumn=this.$renderToken(stringBuilder,screenColumn,token,value);
        }
    };
    
    this.$renderOverflowMessage=function(stringBuilder,screenColumn,token,value){
        this.$renderToken(stringBuilder,screenColumn,token,
            value.slice(0,this.MAX_LINE_LENGTH-screenColumn));
        stringBuilder.push(
            "<spanstyle='position:absolute;right:0'class='ace_inline_buttonace_keywordace_toggle_wrap'>&lt;clicktoseemore...&gt;</span>"
        );
    };
    this.$renderLine=function(stringBuilder,row,onlyContents,foldLine){
        if(!foldLine&&foldLine!=false)
            foldLine=this.session.getFoldLine(row);

        if(foldLine)
            vartokens=this.$getFoldLineTokens(row,foldLine);
        else
            vartokens=this.session.getTokens(row);


        if(!onlyContents){
            stringBuilder.push(
                "<divclass='ace_line'style='height:",
                    this.config.lineHeight*(
                        this.$useLineGroups()?1:this.session.getRowLength(row)
                    ),"px'>"
            );
        }

        if(tokens.length){
            varsplits=this.session.getRowSplitData(row);
            if(splits&&splits.length)
                this.$renderWrappedLine(stringBuilder,tokens,splits,onlyContents);
            else
                this.$renderSimpleLine(stringBuilder,tokens);
        }

        if(this.showInvisibles){
            if(foldLine)
                row=foldLine.end.row;

            stringBuilder.push(
                "<spanclass='ace_invisibleace_invisible_eol'>",
                row==this.session.getLength()-1?this.EOF_CHAR:this.EOL_CHAR,
                "</span>"
            );
        }
        if(!onlyContents)
            stringBuilder.push("</div>");
    };

    this.$getFoldLineTokens=function(row,foldLine){
        varsession=this.session;
        varrenderTokens=[];

        functionaddTokens(tokens,from,to){
            varidx=0,col=0;
            while((col+tokens[idx].value.length)<from){
                col+=tokens[idx].value.length;
                idx++;

                if(idx==tokens.length)
                    return;
            }
            if(col!=from){
                varvalue=tokens[idx].value.substring(from-col);
                if(value.length>(to-from))
                    value=value.substring(0,to-from);

                renderTokens.push({
                    type:tokens[idx].type,
                    value:value
                });

                col=from+value.length;
                idx+=1;
            }

            while(col<to&&idx<tokens.length){
                varvalue=tokens[idx].value;
                if(value.length+col>to){
                    renderTokens.push({
                        type:tokens[idx].type,
                        value:value.substring(0,to-col)
                    });
                }else
                    renderTokens.push(tokens[idx]);
                col+=value.length;
                idx+=1;
            }
        }

        vartokens=session.getTokens(row);
        foldLine.walk(function(placeholder,row,column,lastColumn,isNewRow){
            if(placeholder!=null){
                renderTokens.push({
                    type:"fold",
                    value:placeholder
                });
            }else{
                if(isNewRow)
                    tokens=session.getTokens(row);

                if(tokens.length)
                    addTokens(tokens,lastColumn,column);
            }
        },foldLine.end.row,this.session.getLine(foldLine.end.row).length);

        returnrenderTokens;
    };

    this.$useLineGroups=function(){
        returnthis.session.getUseWrapMode();
    };

    this.destroy=function(){
        clearInterval(this.$pollSizeChangesTimer);
        if(this.$measureNode)
            this.$measureNode.parentNode.removeChild(this.$measureNode);
        deletethis.$measureNode;
    };

}).call(Text.prototype);

exports.Text=Text;

});

define("ace/layer/cursor",["require","exports","module","ace/lib/dom"],function(require,exports,module){
"usestrict";

vardom=require("../lib/dom");
varisIE8;

varCursor=function(parentEl){
    this.element=dom.createElement("div");
    this.element.className="ace_layerace_cursor-layer";
    parentEl.appendChild(this.element);
    
    if(isIE8===undefined)
        isIE8=!("opacity"inthis.element.style);

    this.isVisible=false;
    this.isBlinking=true;
    this.blinkInterval=1000;
    this.smoothBlinking=false;

    this.cursors=[];
    this.cursor=this.addCursor();
    dom.addCssClass(this.element,"ace_hidden-cursors");
    this.$updateCursors=(isIE8
        ?this.$updateVisibility
        :this.$updateOpacity).bind(this);
};

(function(){
    
    this.$updateVisibility=function(val){
        varcursors=this.cursors;
        for(vari=cursors.length;i--;)
            cursors[i].style.visibility=val?"":"hidden";
    };
    this.$updateOpacity=function(val){
        varcursors=this.cursors;
        for(vari=cursors.length;i--;)
            cursors[i].style.opacity=val?"":"0";
    };
    

    this.$padding=0;
    this.setPadding=function(padding){
        this.$padding=padding;
    };

    this.setSession=function(session){
        this.session=session;
    };

    this.setBlinking=function(blinking){
        if(blinking!=this.isBlinking){
            this.isBlinking=blinking;
            this.restartTimer();
        }
    };

    this.setBlinkInterval=function(blinkInterval){
        if(blinkInterval!=this.blinkInterval){
            this.blinkInterval=blinkInterval;
            this.restartTimer();
        }
    };

    this.setSmoothBlinking=function(smoothBlinking){
        if(smoothBlinking!=this.smoothBlinking&&!isIE8){
            this.smoothBlinking=smoothBlinking;
            dom.setCssClass(this.element,"ace_smooth-blinking",smoothBlinking);
            this.$updateCursors(true);
            this.$updateCursors=(this.$updateOpacity).bind(this);
            this.restartTimer();
        }
    };

    this.addCursor=function(){
        varel=dom.createElement("div");
        el.className="ace_cursor";
        this.element.appendChild(el);
        this.cursors.push(el);
        returnel;
    };

    this.removeCursor=function(){
        if(this.cursors.length>1){
            varel=this.cursors.pop();
            el.parentNode.removeChild(el);
            returnel;
        }
    };

    this.hideCursor=function(){
        this.isVisible=false;
        dom.addCssClass(this.element,"ace_hidden-cursors");
        this.restartTimer();
    };

    this.showCursor=function(){
        this.isVisible=true;
        dom.removeCssClass(this.element,"ace_hidden-cursors");
        this.restartTimer();
    };

    this.restartTimer=function(){
        varupdate=this.$updateCursors;
        clearInterval(this.intervalId);
        clearTimeout(this.timeoutId);
        if(this.smoothBlinking){
            dom.removeCssClass(this.element,"ace_smooth-blinking");
        }
        
        update(true);

        if(!this.isBlinking||!this.blinkInterval||!this.isVisible)
            return;

        if(this.smoothBlinking){
            setTimeout(function(){
                dom.addCssClass(this.element,"ace_smooth-blinking");
            }.bind(this));
        }
        
        varblink=function(){
            this.timeoutId=setTimeout(function(){
                update(false);
            },0.6*this.blinkInterval);
        }.bind(this);

        this.intervalId=setInterval(function(){
            update(true);
            blink();
        },this.blinkInterval);

        blink();
    };

    this.getPixelPosition=function(position,onScreen){
        if(!this.config||!this.session)
            return{left:0,top:0};

        if(!position)
            position=this.session.selection.getCursor();
        varpos=this.session.documentToScreenPosition(position);
        varcursorLeft=this.$padding+(this.session.$bidiHandler.isBidiRow(pos.row,position.row)
            ?this.session.$bidiHandler.getPosLeft(pos.column)
            :pos.column*this.config.characterWidth);

        varcursorTop=(pos.row-(onScreen?this.config.firstRowScreen:0))*
            this.config.lineHeight;

        return{left:cursorLeft,top:cursorTop};
    };

    this.update=function(config){
        this.config=config;

        varselections=this.session.$selectionMarkers;
        vari=0,cursorIndex=0;

        if(selections===undefined||selections.length===0){
            selections=[{cursor:null}];
        }

        for(vari=0,n=selections.length;i<n;i++){
            varpixelPos=this.getPixelPosition(selections[i].cursor,true);
            if((pixelPos.top>config.height+config.offset||
                 pixelPos.top<0)&&i>1){
                continue;
            }

            varstyle=(this.cursors[cursorIndex++]||this.addCursor()).style;
            
            if(!this.drawCursor){
                style.left=pixelPos.left+"px";
                style.top=pixelPos.top+"px";
                style.width=config.characterWidth+"px";
                style.height=config.lineHeight+"px";
            }else{
                this.drawCursor(style,pixelPos,config,selections[i],this.session);
            }
        }
        while(this.cursors.length>cursorIndex)
            this.removeCursor();

        varoverwrite=this.session.getOverwrite();
        this.$setOverwrite(overwrite);
        this.$pixelPos=pixelPos;
        this.restartTimer();
    };
    
    this.drawCursor=null;

    this.$setOverwrite=function(overwrite){
        if(overwrite!=this.overwrite){
            this.overwrite=overwrite;
            if(overwrite)
                dom.addCssClass(this.element,"ace_overwrite-cursors");
            else
                dom.removeCssClass(this.element,"ace_overwrite-cursors");
        }
    };

    this.destroy=function(){
        clearInterval(this.intervalId);
        clearTimeout(this.timeoutId);
    };

}).call(Cursor.prototype);

exports.Cursor=Cursor;

});

define("ace/scrollbar",["require","exports","module","ace/lib/oop","ace/lib/dom","ace/lib/event","ace/lib/event_emitter"],function(require,exports,module){
"usestrict";

varoop=require("./lib/oop");
vardom=require("./lib/dom");
varevent=require("./lib/event");
varEventEmitter=require("./lib/event_emitter").EventEmitter;
varMAX_SCROLL_H=0x8000;
varScrollBar=function(parent){
    this.element=dom.createElement("div");
    this.element.className="ace_scrollbarace_scrollbar"+this.classSuffix;

    this.inner=dom.createElement("div");
    this.inner.className="ace_scrollbar-inner";
    this.element.appendChild(this.inner);

    parent.appendChild(this.element);

    this.setVisible(false);
    this.skipEvent=false;

    event.addListener(this.element,"scroll",this.onScroll.bind(this));
    event.addListener(this.element,"mousedown",event.preventDefault);
};

(function(){
    oop.implement(this,EventEmitter);

    this.setVisible=function(isVisible){
        this.element.style.display=isVisible?"":"none";
        this.isVisible=isVisible;
        this.coeff=1;
    };
}).call(ScrollBar.prototype);
varVScrollBar=function(parent,renderer){
    ScrollBar.call(this,parent);
    this.scrollTop=0;
    this.scrollHeight=0;
    renderer.$scrollbarWidth=
    this.width=dom.scrollbarWidth(parent.ownerDocument);
    this.inner.style.width=
    this.element.style.width=(this.width||15)+5+"px";
    this.$minWidth=0;
};

oop.inherits(VScrollBar,ScrollBar);

(function(){

    this.classSuffix='-v';
    this.onScroll=function(){
        if(!this.skipEvent){
            this.scrollTop=this.element.scrollTop;
            if(this.coeff!=1){
                varh=this.element.clientHeight/this.scrollHeight;
                this.scrollTop=this.scrollTop*(1-h)/(this.coeff-h);
            }
            this._emit("scroll",{data:this.scrollTop});
        }
        this.skipEvent=false;
    };
    this.getWidth=function(){
        returnMath.max(this.isVisible?this.width:0,this.$minWidth||0);
    };
    this.setHeight=function(height){
        this.element.style.height=height+"px";
    };
    this.setInnerHeight=
    this.setScrollHeight=function(height){
        this.scrollHeight=height;
        if(height>MAX_SCROLL_H){
            this.coeff=MAX_SCROLL_H/height;
            height=MAX_SCROLL_H;
        }elseif(this.coeff!=1){
            this.coeff=1;
        }
        this.inner.style.height=height+"px";
    };
    this.setScrollTop=function(scrollTop){
        if(this.scrollTop!=scrollTop){
            this.skipEvent=true;
            this.scrollTop=scrollTop;
            this.element.scrollTop=scrollTop*this.coeff;
        }
    };

}).call(VScrollBar.prototype);
varHScrollBar=function(parent,renderer){
    ScrollBar.call(this,parent);
    this.scrollLeft=0;
    this.height=renderer.$scrollbarWidth;
    this.inner.style.height=
    this.element.style.height=(this.height||15)+5+"px";
};

oop.inherits(HScrollBar,ScrollBar);

(function(){

    this.classSuffix='-h';
    this.onScroll=function(){
        if(!this.skipEvent){
            this.scrollLeft=this.element.scrollLeft;
            this._emit("scroll",{data:this.scrollLeft});
        }
        this.skipEvent=false;
    };
    this.getHeight=function(){
        returnthis.isVisible?this.height:0;
    };
    this.setWidth=function(width){
        this.element.style.width=width+"px";
    };
    this.setInnerWidth=function(width){
        this.inner.style.width=width+"px";
    };
    this.setScrollWidth=function(width){
        this.inner.style.width=width+"px";
    };
    this.setScrollLeft=function(scrollLeft){
        if(this.scrollLeft!=scrollLeft){
            this.skipEvent=true;
            this.scrollLeft=this.element.scrollLeft=scrollLeft;
        }
    };

}).call(HScrollBar.prototype);


exports.ScrollBar=VScrollBar;//backwardcompatibility
exports.ScrollBarV=VScrollBar;//backwardcompatibility
exports.ScrollBarH=HScrollBar;//backwardcompatibility

exports.VScrollBar=VScrollBar;
exports.HScrollBar=HScrollBar;
});

define("ace/renderloop",["require","exports","module","ace/lib/event"],function(require,exports,module){
"usestrict";

varevent=require("./lib/event");


varRenderLoop=function(onRender,win){
    this.onRender=onRender;
    this.pending=false;
    this.changes=0;
    this.window=win||window;
};

(function(){


    this.schedule=function(change){
        this.changes=this.changes|change;
        if(!this.pending&&this.changes){
            this.pending=true;
            var_self=this;
            event.nextFrame(function(){
                _self.pending=false;
                varchanges;
                while(changes=_self.changes){
                    _self.changes=0;
                    _self.onRender(changes);
                }
            },this.window);
        }
    };

}).call(RenderLoop.prototype);

exports.RenderLoop=RenderLoop;
});

define("ace/layer/font_metrics",["require","exports","module","ace/lib/oop","ace/lib/dom","ace/lib/lang","ace/lib/useragent","ace/lib/event_emitter"],function(require,exports,module){

varoop=require("../lib/oop");
vardom=require("../lib/dom");
varlang=require("../lib/lang");
varuseragent=require("../lib/useragent");
varEventEmitter=require("../lib/event_emitter").EventEmitter;

varCHAR_COUNT=256;
varUSE_OBSERVER=typeofResizeObserver=="function";

varFontMetrics=exports.FontMetrics=function(parentEl){
    this.el=dom.createElement("div");
    this.$setMeasureNodeStyles(this.el.style,true);
    
    this.$main=dom.createElement("div");
    this.$setMeasureNodeStyles(this.$main.style);
    
    this.$measureNode=dom.createElement("div");
    this.$setMeasureNodeStyles(this.$measureNode.style);
    
    
    this.el.appendChild(this.$main);
    this.el.appendChild(this.$measureNode);
    parentEl.appendChild(this.el);
    
    this.$measureNode.innerHTML=lang.stringRepeat("X",CHAR_COUNT);
    
    this.$characterSize={width:0,height:0};
    
    
    if(USE_OBSERVER)
        this.$addObserver();
    else
        this.checkForSizeChanges();
};

(function(){

    oop.implement(this,EventEmitter);
        
    this.$characterSize={width:0,height:0};
    
    this.$setMeasureNodeStyles=function(style,isRoot){
        style.width=style.height="auto";
        style.left=style.top="0px";
        style.visibility="hidden";
        style.position="absolute";
        style.whiteSpace="pre";

        if(useragent.isIE<8){
            style["font-family"]="inherit";
        }else{
            style.font="inherit";
        }
        style.overflow=isRoot?"hidden":"visible";
    };

    this.checkForSizeChanges=function(size){
        if(size===undefined)
            size=this.$measureSizes();
        if(size&&(this.$characterSize.width!==size.width||this.$characterSize.height!==size.height)){
            this.$measureNode.style.fontWeight="bold";
            varboldSize=this.$measureSizes();
            this.$measureNode.style.fontWeight="";
            this.$characterSize=size;
            this.charSizes=Object.create(null);
            this.allowBoldFonts=boldSize&&boldSize.width===size.width&&boldSize.height===size.height;
            this._emit("changeCharacterSize",{data:size});
        }
    };
    
    this.$addObserver=function(){
        varself=this;
        this.$observer=newwindow.ResizeObserver(function(e){
            varrect=e[0].contentRect;
            self.checkForSizeChanges({
                height:rect.height,
                width:rect.width/CHAR_COUNT
            });
        });
        this.$observer.observe(this.$measureNode);
    };

    this.$pollSizeChanges=function(){
        if(this.$pollSizeChangesTimer||this.$observer)
            returnthis.$pollSizeChangesTimer;
        varself=this;
        returnthis.$pollSizeChangesTimer=setInterval(function(){
            self.checkForSizeChanges();
        },500);
    };
    
    this.setPolling=function(val){
        if(val){
            this.$pollSizeChanges();
        }elseif(this.$pollSizeChangesTimer){
            clearInterval(this.$pollSizeChangesTimer);
            this.$pollSizeChangesTimer=0;
        }
    };

    this.$measureSizes=function(node){
        varsize={
            height:(node||this.$measureNode).clientHeight,
            width:(node||this.$measureNode).clientWidth/CHAR_COUNT
        };
        if(size.width===0||size.height===0)
            returnnull;
        returnsize;
    };

    this.$measureCharWidth=function(ch){
        this.$main.innerHTML=lang.stringRepeat(ch,CHAR_COUNT);
        varrect=this.$main.getBoundingClientRect();
        returnrect.width/CHAR_COUNT;
    };
    
    this.getCharacterWidth=function(ch){
        varw=this.charSizes[ch];
        if(w===undefined){
            w=this.charSizes[ch]=this.$measureCharWidth(ch)/this.$characterSize.width;
        }
        returnw;
    };

    this.destroy=function(){
        clearInterval(this.$pollSizeChangesTimer);
        if(this.el&&this.el.parentNode)
            this.el.parentNode.removeChild(this.el);
    };

}).call(FontMetrics.prototype);

});

define("ace/virtual_renderer",["require","exports","module","ace/lib/oop","ace/lib/dom","ace/config","ace/lib/useragent","ace/layer/gutter","ace/layer/marker","ace/layer/text","ace/layer/cursor","ace/scrollbar","ace/scrollbar","ace/renderloop","ace/layer/font_metrics","ace/lib/event_emitter"],function(require,exports,module){
"usestrict";

varoop=require("./lib/oop");
vardom=require("./lib/dom");
varconfig=require("./config");
varuseragent=require("./lib/useragent");
varGutterLayer=require("./layer/gutter").Gutter;
varMarkerLayer=require("./layer/marker").Marker;
varTextLayer=require("./layer/text").Text;
varCursorLayer=require("./layer/cursor").Cursor;
varHScrollBar=require("./scrollbar").HScrollBar;
varVScrollBar=require("./scrollbar").VScrollBar;
varRenderLoop=require("./renderloop").RenderLoop;
varFontMetrics=require("./layer/font_metrics").FontMetrics;
varEventEmitter=require("./lib/event_emitter").EventEmitter;
vareditorCss=".ace_editor{\
position:relative;\
overflow:hidden;\
font:12px/normal'Monaco','Menlo','UbuntuMono','Consolas','source-code-pro',monospace;\
direction:ltr;\
text-align:left;\
-webkit-tap-highlight-color:rgba(0,0,0,0);\
}\
.ace_scroller{\
position:absolute;\
overflow:hidden;\
top:0;\
bottom:0;\
background-color:inherit;\
-ms-user-select:none;\
-moz-user-select:none;\
-webkit-user-select:none;\
user-select:none;\
cursor:text;\
}\
.ace_content{\
position:absolute;\
box-sizing:border-box;\
min-width:100%;\
}\
.ace_dragging.ace_scroller:before{\
position:absolute;\
top:0;\
left:0;\
right:0;\
bottom:0;\
content:'';\
background:rgba(250,250,250,0.01);\
z-index:1000;\
}\
.ace_dragging.ace_dark.ace_scroller:before{\
background:rgba(0,0,0,0.01);\
}\
.ace_selecting,.ace_selecting*{\
cursor:text!important;\
}\
.ace_gutter{\
position:absolute;\
overflow:hidden;\
width:auto;\
top:0;\
bottom:0;\
left:0;\
cursor:default;\
z-index:4;\
-ms-user-select:none;\
-moz-user-select:none;\
-webkit-user-select:none;\
user-select:none;\
}\
.ace_gutter-active-line{\
position:absolute;\
left:0;\
right:0;\
}\
.ace_scroller.ace_scroll-left{\
box-shadow:17px016px-16pxrgba(0,0,0,0.4)inset;\
}\
.ace_gutter-cell{\
padding-left:19px;\
padding-right:6px;\
background-repeat:no-repeat;\
}\
.ace_gutter-cell.ace_error{\
background-image:url(\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAABOFBMVEX/////////QRswFAb/Ui4wFAYwFAYwFAaWGAfDRymzOSH/PxswFAb/SiUwFAYwFAbUPRvjQiDllog5HhHdRybsTi3/Tyv9Tir+Syj/UC3////XurebMBIwFAb/RSHbPx/gUzfdwL3kzMivKBAwFAbbvbnhPx66NhowFAYwFAaZJg8wFAaxKBDZurf/RB6mMxb/SCMwFAYwFAbxQB3+RB4wFAb/Qhy4Oh+4QifbNRcwFAYwFAYwFAb/QRzdNhgwFAYwFAbav7v/Uy7oaE68MBK5LxLewr/r2NXewLswFAaxJw4wFAbkPRy2PyYwFAaxKhLm1tMwFAazPiQwFAaUGAb/QBrfOx3bvrv/VC/maE4wFAbRPBq6MRO8Qynew8Dp2tjfwb0wFAbx6eju5+by6uns4uH9/f36+vr/GkHjAAAAYnRSTlMAGt+64rnWu/bo8eAA4InH3+DwoN7j4eLi4xP99Nfg4+b+/u9B/eDs1MD1mO7+4PHg2MXa347g7vDizMLN4eG+Pv7i5evs/v79yu7S3/DV7/498Yv24eH+4ufQ3Ozu/v7+y13sRqwAAADLSURBVHjaZc/XDsFgGIBhtDrshlitmk2IrbHFqL2pvXf/+78DPokj7+Fz9qpU/9UXJIlhmPaTaQ6QPaz0mm+5gwkgovcV6GZzd5JtCQwgsxoHOvJO15kleRLAnMgHFIESUEPmawB9ngmelTtipwwfASilxOLyiV5UVUyVAfbG0cCPHig+GBkzAENHS0AstVF6bacZIOzgLmxsHbt2OecNgJC83JERmePUYq8ARGkJx6XtFsdddBQgZE2nPR6CICZhawjA4Fb/chv+399kfR+MMMDGOQAAAABJRU5ErkJggg==\");\
background-repeat:no-repeat;\
background-position:2pxcenter;\
}\
.ace_gutter-cell.ace_warning{\
background-image:url(\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAAmVBMVEX///8AAAD///8AAAAAAABPSzb/5sAAAAB/blH/73z/ulkAAAAAAAD85pkAAAAAAAACAgP/vGz/rkDerGbGrV7/pkQICAf////e0IsAAAD/oED/qTvhrnUAAAD/yHD/njcAAADuv2r/nz//oTj/p064oGf/zHAAAAA9Nir/tFIAAAD/tlTiuWf/tkIAAACynXEAAAAAAAAtIRW7zBpBAAAAM3RSTlMAABR1m7RXO8Ln31Z36zT+neXe5OzooRDfn+TZ4p3h2hTf4t3k3ucyrN1K5+Xaks52Sfs9CXgrAAAAjklEQVR42o3PbQ+CIBQFYEwboPhSYgoYunIqqLn6/z8uYdH8Vmdnu9vz4WwXgN/xTPRD2+sgOcZjsge/whXZgUaYYvT8QnuJaUrjrHUQreGczuEafQCO/SJTufTbroWsPgsllVhq3wJEk2jUSzX3CUEDJC84707djRc5MTAQxoLgupWRwW6UB5fS++NV8AbOZgnsC7BpEAAAAABJRU5ErkJggg==\");\
background-position:2pxcenter;\
}\
.ace_gutter-cell.ace_info{\
background-image:url(\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAAAAAA6mKC9AAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAAJ0Uk5TAAB2k804AAAAPklEQVQY02NgIB68QuO3tiLznjAwpKTgNyDbMegwisCHZUETUZV0ZqOquBpXj2rtnpSJT1AEnnRmL2OgGgAAIKkRQap2htgAAAAASUVORK5CYII=\");\
background-position:2pxcenter;\
}\
.ace_dark.ace_gutter-cell.ace_info{\
background-image:url(\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQBAMAAADt3eJSAAAAJFBMVEUAAAChoaGAgIAqKiq+vr6tra1ZWVmUlJSbm5s8PDxubm56enrdgzg3AAAAAXRSTlMAQObYZgAAAClJREFUeNpjYMAPdsMYHegyJZFQBlsUlMFVCWUYKkAZMxZAGdxlDMQBAG+TBP4B6RyJAAAAAElFTkSuQmCC\");\
}\
.ace_scrollbar{\
position:absolute;\
right:0;\
bottom:0;\
z-index:6;\
}\
.ace_scrollbar-inner{\
position:absolute;\
cursor:text;\
left:0;\
top:0;\
}\
.ace_scrollbar-v{\
overflow-x:hidden;\
overflow-y:scroll;\
top:0;\
}\
.ace_scrollbar-h{\
overflow-x:scroll;\
overflow-y:hidden;\
left:0;\
}\
.ace_print-margin{\
position:absolute;\
height:100%;\
}\
.ace_text-input{\
position:absolute;\
z-index:0;\
width:0.5em;\
height:1em;\
opacity:0;\
background:transparent;\
-moz-appearance:none;\
appearance:none;\
border:none;\
resize:none;\
outline:none;\
overflow:hidden;\
font:inherit;\
padding:01px;\
margin:0-1px;\
text-indent:-1em;\
-ms-user-select:text;\
-moz-user-select:text;\
-webkit-user-select:text;\
user-select:text;\
white-space:pre!important;\
}\
.ace_text-input.ace_composition{\
background:inherit;\
color:inherit;\
z-index:1000;\
opacity:1;\
text-indent:0;\
}\
[ace_nocontext=true]{\
transform:none!important;\
filter:none!important;\
perspective:none!important;\
clip-path:none!important;\
mask:none!important;\
contain:none!important;\
perspective:none!important;\
mix-blend-mode:initial!important;\
z-index:auto;\
}\
.ace_layer{\
z-index:1;\
position:absolute;\
overflow:hidden;\
word-wrap:normal;\
white-space:pre;\
height:100%;\
width:100%;\
box-sizing:border-box;\
pointer-events:none;\
}\
.ace_gutter-layer{\
position:relative;\
width:auto;\
text-align:right;\
pointer-events:auto;\
}\
.ace_text-layer{\
font:inherit!important;\
}\
.ace_cjk{\
display:inline-block;\
text-align:center;\
}\
.ace_cursor-layer{\
z-index:4;\
}\
.ace_cursor{\
z-index:4;\
position:absolute;\
box-sizing:border-box;\
border-left:2pxsolid;\
transform:translatez(0);\
}\
.ace_multiselect.ace_cursor{\
border-left-width:1px;\
}\
.ace_slim-cursors.ace_cursor{\
border-left-width:1px;\
}\
.ace_overwrite-cursors.ace_cursor{\
border-left-width:0;\
border-bottom:1pxsolid;\
}\
.ace_hidden-cursors.ace_cursor{\
opacity:0.2;\
}\
.ace_smooth-blinking.ace_cursor{\
transition:opacity0.18s;\
}\
.ace_marker-layer.ace_step,.ace_marker-layer.ace_stack{\
position:absolute;\
z-index:3;\
}\
.ace_marker-layer.ace_selection{\
position:absolute;\
z-index:5;\
}\
.ace_marker-layer.ace_bracket{\
position:absolute;\
z-index:6;\
}\
.ace_marker-layer.ace_active-line{\
position:absolute;\
z-index:2;\
}\
.ace_marker-layer.ace_selected-word{\
position:absolute;\
z-index:4;\
box-sizing:border-box;\
}\
.ace_line.ace_fold{\
box-sizing:border-box;\
display:inline-block;\
height:11px;\
margin-top:-2px;\
vertical-align:middle;\
background-image:\
url(\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABEAAAAJCAYAAADU6McMAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAJpJREFUeNpi/P//PwOlgAXGYGRklAVSokD8GmjwY1wasKljQpYACtpCFeADcHVQfQyMQAwzwAZI3wJKvCLkfKBaMSClBlR7BOQikCFGQEErIH0VqkabiGCAqwUadAzZJRxQr/0gwiXIal8zQQPnNVTgJ1TdawL0T5gBIP1MUJNhBv2HKoQHHjqNrA4WO4zY0glyNKLT2KIfIMAAQsdgGiXvgnYAAAAASUVORK5CYII=\"),\
url(\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAA3CAYAAADNNiA5AAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAACJJREFUeNpi+P//fxgTAwPDBxDxD078RSX+YeEyDFMCIMAAI3INmXiwf2YAAAAASUVORK5CYII=\");\
background-repeat:no-repeat,repeat-x;\
background-position:centercenter,topleft;\
color:transparent;\
border:1pxsolidblack;\
border-radius:2px;\
cursor:pointer;\
pointer-events:auto;\
}\
.ace_dark.ace_fold{\
}\
.ace_fold:hover{\
background-image:\
url(\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABEAAAAJCAYAAADU6McMAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAJpJREFUeNpi/P//PwOlgAXGYGRklAVSokD8GmjwY1wasKljQpYACtpCFeADcHVQfQyMQAwzwAZI3wJKvCLkfKBaMSClBlR7BOQikCFGQEErIH0VqkabiGCAqwUadAzZJRxQr/0gwiXIal8zQQPnNVTgJ1TdawL0T5gBIP1MUJNhBv2HKoQHHjqNrA4WO4zY0glyNKLT2KIfIMAAQsdgGiXvgnYAAAAASUVORK5CYII=\"),\
url(\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAA3CAYAAADNNiA5AAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAACBJREFUeNpi+P//fz4TAwPDZxDxD5X4i5fLMEwJgAADAEPVDbjNw87ZAAAAAElFTkSuQmCC\");\
}\
.ace_tooltip{\
background-color:#FFF;\
background-image:linear-gradient(tobottom,transparent,rgba(0,0,0,0.1));\
border:1pxsolidgray;\
border-radius:1px;\
box-shadow:01px2pxrgba(0,0,0,0.3);\
color:black;\
max-width:100%;\
padding:3px4px;\
position:fixed;\
z-index:999999;\
box-sizing:border-box;\
cursor:default;\
white-space:pre;\
word-wrap:break-word;\
line-height:normal;\
font-style:normal;\
font-weight:normal;\
letter-spacing:normal;\
pointer-events:none;\
}\
.ace_folding-enabled>.ace_gutter-cell{\
padding-right:13px;\
}\
.ace_fold-widget{\
box-sizing:border-box;\
margin:0-12px01px;\
display:none;\
width:11px;\
vertical-align:top;\
background-image:url(\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAANElEQVR42mWKsQ0AMAzC8ixLlrzQjzmBiEjp0A6WwBCSPgKAXoLkqSot7nN3yMwR7pZ32NzpKkVoDBUxKAAAAABJRU5ErkJggg==\");\
background-repeat:no-repeat;\
background-position:center;\
border-radius:3px;\
border:1pxsolidtransparent;\
cursor:pointer;\
}\
.ace_folding-enabled.ace_fold-widget{\
display:inline-block;  \
}\
.ace_fold-widget.ace_end{\
background-image:url(\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAANElEQVR42m3HwQkAMAhD0YzsRchFKI7sAikeWkrxwScEB0nh5e7KTPWimZki4tYfVbX+MNl4pyZXejUO1QAAAABJRU5ErkJggg==\");\
}\
.ace_fold-widget.ace_closed{\
background-image:url(\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAMAAAAGCAYAAAAG5SQMAAAAOUlEQVR42jXKwQkAMAgDwKwqKD4EwQ26sSOkVWjgIIHAzPiCgaqiqnJHZnKICBERHN194O5b9vbLuAVRL+l0YWnZAAAAAElFTkSuQmCCXA==\");\
}\
.ace_fold-widget:hover{\
border:1pxsolidrgba(0,0,0,0.3);\
background-color:rgba(255,255,255,0.2);\
box-shadow:01px1pxrgba(255,255,255,0.7);\
}\
.ace_fold-widget:active{\
border:1pxsolidrgba(0,0,0,0.4);\
background-color:rgba(0,0,0,0.05);\
box-shadow:01px1pxrgba(255,255,255,0.8);\
}\
.ace_dark.ace_fold-widget{\
background-image:url(\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHklEQVQIW2P4//8/AzoGEQ7oGCaLLAhWiSwB146BAQCSTPYocqT0AAAAAElFTkSuQmCC\");\
}\
.ace_dark.ace_fold-widget.ace_end{\
background-image:url(\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAH0lEQVQIW2P4//8/AxQ7wNjIAjDMgC4AxjCVKBirIAAF0kz2rlhxpAAAAABJRU5ErkJggg==\");\
}\
.ace_dark.ace_fold-widget.ace_closed{\
background-image:url(\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAMAAAAFCAYAAACAcVaiAAAAHElEQVQIW2P4//+/AxAzgDADlOOAznHAKgPWAwARji8UIDTfQQAAAABJRU5ErkJggg==\");\
}\
.ace_dark.ace_fold-widget:hover{\
box-shadow:01px1pxrgba(255,255,255,0.2);\
background-color:rgba(255,255,255,0.1);\
}\
.ace_dark.ace_fold-widget:active{\
box-shadow:01px1pxrgba(255,255,255,0.2);\
}\
.ace_inline_button{\
border:1pxsolidlightgray;\
display:inline-block;\
margin:-1px8px;\
padding:05px;\
pointer-events:auto;\
cursor:pointer;\
}\
.ace_inline_button:hover{\
border-color:gray;\
background:rgba(200,200,200,0.2);\
display:inline-block;\
pointer-events:auto;\
}\
.ace_fold-widget.ace_invalid{\
background-color:#FFB4B4;\
border-color:#DE5555;\
}\
.ace_fade-fold-widgets.ace_fold-widget{\
transition:opacity0.4sease0.05s;\
opacity:0;\
}\
.ace_fade-fold-widgets:hover.ace_fold-widget{\
transition:opacity0.05sease0.05s;\
opacity:1;\
}\
.ace_underline{\
text-decoration:underline;\
}\
.ace_bold{\
font-weight:bold;\
}\
.ace_nobold.ace_bold{\
font-weight:normal;\
}\
.ace_italic{\
font-style:italic;\
}\
.ace_error-marker{\
background-color:rgba(255,0,0,0.2);\
position:absolute;\
z-index:9;\
}\
.ace_highlight-marker{\
background-color:rgba(255,255,0,0.2);\
position:absolute;\
z-index:8;\
}\
.ace_br1{border-top-left-radius   :3px;}\
.ace_br2{border-top-right-radius  :3px;}\
.ace_br3{border-top-left-radius   :3px;border-top-right-radius:   3px;}\
.ace_br4{border-bottom-right-radius:3px;}\
.ace_br5{border-top-left-radius   :3px;border-bottom-right-radius:3px;}\
.ace_br6{border-top-right-radius  :3px;border-bottom-right-radius:3px;}\
.ace_br7{border-top-left-radius   :3px;border-top-right-radius:   3px;border-bottom-right-radius:3px;}\
.ace_br8{border-bottom-left-radius:3px;}\
.ace_br9{border-top-left-radius   :3px;border-bottom-left-radius: 3px;}\
.ace_br10{border-top-right-radius  :3px;border-bottom-left-radius: 3px;}\
.ace_br11{border-top-left-radius   :3px;border-top-right-radius:   3px;border-bottom-left-radius: 3px;}\
.ace_br12{border-bottom-right-radius:3px;border-bottom-left-radius: 3px;}\
.ace_br13{border-top-left-radius   :3px;border-bottom-right-radius:3px;border-bottom-left-radius: 3px;}\
.ace_br14{border-top-right-radius  :3px;border-bottom-right-radius:3px;border-bottom-left-radius: 3px;}\
.ace_br15{border-top-left-radius   :3px;border-top-right-radius:   3px;border-bottom-right-radius:3px;border-bottom-left-radius:3px;}\
.ace_text-input-ios{\
position:absolute!important;\
top:-100000px!important;\
left:-100000px!important;\
}\
";

dom.importCssString(editorCss,"ace_editor.css");

varVirtualRenderer=function(container,theme){
    var_self=this;

    this.container=container||dom.createElement("div");

    dom.addCssClass(this.container,"ace_editor");

    this.setTheme(theme);

    this.$gutter=dom.createElement("div");
    this.$gutter.className="ace_gutter";
    this.container.appendChild(this.$gutter);
    this.$gutter.setAttribute("aria-hidden",true);

    this.scroller=dom.createElement("div");
    this.scroller.className="ace_scroller";
    this.container.appendChild(this.scroller);

    this.content=dom.createElement("div");
    this.content.className="ace_content";
    this.scroller.appendChild(this.content);

    this.$gutterLayer=newGutterLayer(this.$gutter);
    this.$gutterLayer.on("changeGutterWidth",this.onGutterResize.bind(this));

    this.$markerBack=newMarkerLayer(this.content);

    vartextLayer=this.$textLayer=newTextLayer(this.content);
    this.canvas=textLayer.element;

    this.$markerFront=newMarkerLayer(this.content);

    this.$cursorLayer=newCursorLayer(this.content);
    this.$horizScroll=false;
    this.$vScroll=false;

    this.scrollBar=
    this.scrollBarV=newVScrollBar(this.container,this);
    this.scrollBarH=newHScrollBar(this.container,this);
    this.scrollBarV.addEventListener("scroll",function(e){
        if(!_self.$scrollAnimation)
            _self.session.setScrollTop(e.data-_self.scrollMargin.top);
    });
    this.scrollBarH.addEventListener("scroll",function(e){
        if(!_self.$scrollAnimation)
            _self.session.setScrollLeft(e.data-_self.scrollMargin.left);
    });

    this.scrollTop=0;
    this.scrollLeft=0;

    this.cursorPos={
        row:0,
        column:0
    };

    this.$fontMetrics=newFontMetrics(this.container);
    this.$textLayer.$setFontMetrics(this.$fontMetrics);
    this.$textLayer.addEventListener("changeCharacterSize",function(e){
        _self.updateCharacterSize();
        _self.onResize(true,_self.gutterWidth,_self.$size.width,_self.$size.height);
        _self._signal("changeCharacterSize",e);
    });

    this.$size={
        width:0,
        height:0,
        scrollerHeight:0,
        scrollerWidth:0,
        $dirty:true
    };

    this.layerConfig={
        width:1,
        padding:0,
        firstRow:0,
        firstRowScreen:0,
        lastRow:0,
        lineHeight:0,
        characterWidth:0,
        minHeight:1,
        maxHeight:1,
        offset:0,
        height:1,
        gutterOffset:1
    };
    
    this.scrollMargin={
        left:0,
        right:0,
        top:0,
        bottom:0,
        v:0,
        h:0
    };

    this.$loop=newRenderLoop(
        this.$renderChanges.bind(this),
        this.container.ownerDocument.defaultView
    );
    this.$loop.schedule(this.CHANGE_FULL);

    this.updateCharacterSize();
    this.setPadding(4);
    config.resetOptions(this);
    config._emit("renderer",this);
};

(function(){

    this.CHANGE_CURSOR=1;
    this.CHANGE_MARKER=2;
    this.CHANGE_GUTTER=4;
    this.CHANGE_SCROLL=8;
    this.CHANGE_LINES=16;
    this.CHANGE_TEXT=32;
    this.CHANGE_SIZE=64;
    this.CHANGE_MARKER_BACK=128;
    this.CHANGE_MARKER_FRONT=256;
    this.CHANGE_FULL=512;
    this.CHANGE_H_SCROLL=1024;

    oop.implement(this,EventEmitter);

    this.updateCharacterSize=function(){
        if(this.$textLayer.allowBoldFonts!=this.$allowBoldFonts){
            this.$allowBoldFonts=this.$textLayer.allowBoldFonts;
            this.setStyle("ace_nobold",!this.$allowBoldFonts);
        }

        this.layerConfig.characterWidth=
        this.characterWidth=this.$textLayer.getCharacterWidth();
        this.layerConfig.lineHeight=
        this.lineHeight=this.$textLayer.getLineHeight();
        this.$updatePrintMargin();
    };
    this.setSession=function(session){
        if(this.session)
            this.session.doc.off("changeNewLineMode",this.onChangeNewLineMode);
            
        this.session=session;
        if(session&&this.scrollMargin.top&&session.getScrollTop()<=0)
            session.setScrollTop(-this.scrollMargin.top);

        this.$cursorLayer.setSession(session);
        this.$markerBack.setSession(session);
        this.$markerFront.setSession(session);
        this.$gutterLayer.setSession(session);
        this.$textLayer.setSession(session);
        if(!session)
            return;
        
        this.$loop.schedule(this.CHANGE_FULL);
        this.session.$setFontMetrics(this.$fontMetrics);
        this.scrollBarH.scrollLeft=this.scrollBarV.scrollTop=null;
        
        this.onChangeNewLineMode=this.onChangeNewLineMode.bind(this);
        this.onChangeNewLineMode();
        this.session.doc.on("changeNewLineMode",this.onChangeNewLineMode);
    };
    this.updateLines=function(firstRow,lastRow,force){
        if(lastRow===undefined)
            lastRow=Infinity;

        if(!this.$changedLines){
            this.$changedLines={
                firstRow:firstRow,
                lastRow:lastRow
            };
        }
        else{
            if(this.$changedLines.firstRow>firstRow)
                this.$changedLines.firstRow=firstRow;

            if(this.$changedLines.lastRow<lastRow)
                this.$changedLines.lastRow=lastRow;
        }
        if(this.$changedLines.lastRow<this.layerConfig.firstRow){
            if(force)
                this.$changedLines.lastRow=this.layerConfig.lastRow;
            else
                return;
        }
        if(this.$changedLines.firstRow>this.layerConfig.lastRow)
            return;
        this.$loop.schedule(this.CHANGE_LINES);
    };

    this.onChangeNewLineMode=function(){
        this.$loop.schedule(this.CHANGE_TEXT);
        this.$textLayer.$updateEolChar();
        this.session.$bidiHandler.setEolChar(this.$textLayer.EOL_CHAR);
    };
    
    this.onChangeTabSize=function(){
        this.$loop.schedule(this.CHANGE_TEXT|this.CHANGE_MARKER);
        this.$textLayer.onChangeTabSize();
    };
    this.updateText=function(){
        this.$loop.schedule(this.CHANGE_TEXT);
    };
    this.updateFull=function(force){
        if(force)
            this.$renderChanges(this.CHANGE_FULL,true);
        else
            this.$loop.schedule(this.CHANGE_FULL);
    };
    this.updateFontSize=function(){
        this.$textLayer.checkForSizeChanges();
    };

    this.$changes=0;
    this.$updateSizeAsync=function(){
        if(this.$loop.pending)
            this.$size.$dirty=true;
        else
            this.onResize();
    };
    this.onResize=function(force,gutterWidth,width,height){
        if(this.resizing>2)
            return;
        elseif(this.resizing>0)
            this.resizing++;
        else
            this.resizing=force?1:0;
        varel=this.container;
        if(!height)
            height=el.clientHeight||el.scrollHeight;
        if(!width)
            width=el.clientWidth||el.scrollWidth;
        varchanges=this.$updateCachedSize(force,gutterWidth,width,height);

        
        if(!this.$size.scrollerHeight||(!width&&!height))
            returnthis.resizing=0;

        if(force)
            this.$gutterLayer.$padding=null;

        if(force)
            this.$renderChanges(changes|this.$changes,true);
        else
            this.$loop.schedule(changes|this.$changes);

        if(this.resizing)
            this.resizing=0;
        this.scrollBarV.scrollLeft=this.scrollBarV.scrollTop=null;
    };
    
    this.$updateCachedSize=function(force,gutterWidth,width,height){
        height-=(this.$extraHeight||0);
        varchanges=0;
        varsize=this.$size;
        varoldSize={
            width:size.width,
            height:size.height,
            scrollerHeight:size.scrollerHeight,
            scrollerWidth:size.scrollerWidth
        };
        if(height&&(force||size.height!=height)){
            size.height=height;
            changes|=this.CHANGE_SIZE;

            size.scrollerHeight=size.height;
            if(this.$horizScroll)
                size.scrollerHeight-=this.scrollBarH.getHeight();
            this.scrollBarV.element.style.bottom=this.scrollBarH.getHeight()+"px";

            changes=changes|this.CHANGE_SCROLL;
        }

        if(width&&(force||size.width!=width)){
            changes|=this.CHANGE_SIZE;
            size.width=width;
            
            if(gutterWidth==null)
                gutterWidth=this.$showGutter?this.$gutter.offsetWidth:0;
            
            this.gutterWidth=gutterWidth;
            
            this.scrollBarH.element.style.left=
            this.scroller.style.left=gutterWidth+"px";
            size.scrollerWidth=Math.max(0,width-gutterWidth-this.scrollBarV.getWidth());          
            
            this.scrollBarH.element.style.right=
            this.scroller.style.right=this.scrollBarV.getWidth()+"px";
            this.scroller.style.bottom=this.scrollBarH.getHeight()+"px";

            if(this.session&&this.session.getUseWrapMode()&&this.adjustWrapLimit()||force)
                changes|=this.CHANGE_FULL;
        }
        
        size.$dirty=!width||!height;

        if(changes)
            this._signal("resize",oldSize);

        returnchanges;
    };

    this.onGutterResize=function(){
        vargutterWidth=this.$showGutter?this.$gutter.offsetWidth:0;
        if(gutterWidth!=this.gutterWidth)
            this.$changes|=this.$updateCachedSize(true,gutterWidth,this.$size.width,this.$size.height);

        if(this.session.getUseWrapMode()&&this.adjustWrapLimit()){
            this.$loop.schedule(this.CHANGE_FULL);
        }elseif(this.$size.$dirty){
            this.$loop.schedule(this.CHANGE_FULL);
        }else{
            this.$computeLayerConfig();
            this.$loop.schedule(this.CHANGE_MARKER);
        }
    };
    this.adjustWrapLimit=function(){
        varavailableWidth=this.$size.scrollerWidth-this.$padding*2;
        varlimit=Math.floor(availableWidth/this.characterWidth);
        returnthis.session.adjustWrapLimit(limit,this.$showPrintMargin&&this.$printMarginColumn);
    };
    this.setAnimatedScroll=function(shouldAnimate){
        this.setOption("animatedScroll",shouldAnimate);
    };
    this.getAnimatedScroll=function(){
        returnthis.$animatedScroll;
    };
    this.setShowInvisibles=function(showInvisibles){
        this.setOption("showInvisibles",showInvisibles);
        this.session.$bidiHandler.setShowInvisibles(showInvisibles);
    };
    this.getShowInvisibles=function(){
        returnthis.getOption("showInvisibles");
    };
    this.getDisplayIndentGuides=function(){
        returnthis.getOption("displayIndentGuides");
    };

    this.setDisplayIndentGuides=function(display){
        this.setOption("displayIndentGuides",display);
    };
    this.setShowPrintMargin=function(showPrintMargin){
        this.setOption("showPrintMargin",showPrintMargin);
    };
    this.getShowPrintMargin=function(){
        returnthis.getOption("showPrintMargin");
    };
    this.setPrintMarginColumn=function(showPrintMargin){
        this.setOption("printMarginColumn",showPrintMargin);
    };
    this.getPrintMarginColumn=function(){
        returnthis.getOption("printMarginColumn");
    };
    this.getShowGutter=function(){
        returnthis.getOption("showGutter");
    };
    this.setShowGutter=function(show){
        returnthis.setOption("showGutter",show);
    };

    this.getFadeFoldWidgets=function(){
        returnthis.getOption("fadeFoldWidgets");
    };

    this.setFadeFoldWidgets=function(show){
        this.setOption("fadeFoldWidgets",show);
    };

    this.setHighlightGutterLine=function(shouldHighlight){
        this.setOption("highlightGutterLine",shouldHighlight);
    };

    this.getHighlightGutterLine=function(){
        returnthis.getOption("highlightGutterLine");
    };

    this.$updateGutterLineHighlight=function(){
        varpos=this.$cursorLayer.$pixelPos;
        varheight=this.layerConfig.lineHeight;
        if(this.session.getUseWrapMode()){
            varcursor=this.session.selection.getCursor();
            cursor.column=0;
            pos=this.$cursorLayer.getPixelPosition(cursor,true);
            height*=this.session.getRowLength(cursor.row);
        }
        this.$gutterLineHighlight.style.top=pos.top-this.layerConfig.offset+"px";
        this.$gutterLineHighlight.style.height=height+"px";
    };

    this.$updatePrintMargin=function(){
        if(!this.$showPrintMargin&&!this.$printMarginEl)
            return;

        if(!this.$printMarginEl){
            varcontainerEl=dom.createElement("div");
            containerEl.className="ace_layerace_print-margin-layer";
            this.$printMarginEl=dom.createElement("div");
            this.$printMarginEl.className="ace_print-margin";
            containerEl.appendChild(this.$printMarginEl);
            this.content.insertBefore(containerEl,this.content.firstChild);
        }

        varstyle=this.$printMarginEl.style;
        style.left=Math.round(this.characterWidth*this.$printMarginColumn+this.$padding)+"px";
        style.visibility=this.$showPrintMargin?"visible":"hidden";
        
        if(this.session&&this.session.$wrap==-1)
            this.adjustWrapLimit();
    };
    this.getContainerElement=function(){
        returnthis.container;
    };
    this.getMouseEventTarget=function(){
        returnthis.scroller;
    };
    this.getTextAreaContainer=function(){
        returnthis.container;
    };
    this.$moveTextAreaToCursor=function(){
        varstyle=this.textarea.style;
        if(!this.$keepTextAreaAtCursor){
            style.left=-100+"px";
            return;
        }
        varconfig=this.layerConfig;
        varposTop=this.$cursorLayer.$pixelPos.top;
        varposLeft=this.$cursorLayer.$pixelPos.left;
        posTop-=config.offset;

        varh=this.lineHeight;
        if(posTop<0||posTop>config.height-h){
            style.top=style.left="0";
            return;
        }

        varw=this.characterWidth;
        if(this.$composition){
            varval=this.textarea.value.replace(/^\x01+/,"");
            w*=(this.session.$getStringScreenWidth(val)[0]+2);
            h+=2;
        }
        posLeft-=this.scrollLeft;
        if(posLeft>this.$size.scrollerWidth-w)
            posLeft=this.$size.scrollerWidth-w;

        posLeft+=this.gutterWidth;
        style.height=h+"px";
        style.width=w+"px";
        style.left=Math.min(posLeft,this.$size.scrollerWidth-w)+"px";
        style.top=Math.min(posTop,this.$size.height-h)+"px";
    };
    this.getFirstVisibleRow=function(){
        returnthis.layerConfig.firstRow;
    };
    this.getFirstFullyVisibleRow=function(){
        returnthis.layerConfig.firstRow+(this.layerConfig.offset===0?0:1);
    };
    this.getLastFullyVisibleRow=function(){
        varconfig=this.layerConfig;
        varlastRow=config.lastRow;
        vartop=this.session.documentToScreenRow(lastRow,0)*config.lineHeight;
        if(top-this.session.getScrollTop()>config.height-config.lineHeight)
            returnlastRow-1;
        returnlastRow;
    };
    this.getLastVisibleRow=function(){
        returnthis.layerConfig.lastRow;
    };

    this.$padding=null;
    this.setPadding=function(padding){
        this.$padding=padding;
        this.$textLayer.setPadding(padding);
        this.$cursorLayer.setPadding(padding);
        this.$markerFront.setPadding(padding);
        this.$markerBack.setPadding(padding);
        this.$loop.schedule(this.CHANGE_FULL);
        this.$updatePrintMargin();
    };
    
    this.setScrollMargin=function(top,bottom,left,right){
        varsm=this.scrollMargin;
        sm.top=top|0;
        sm.bottom=bottom|0;
        sm.right=right|0;
        sm.left=left|0;
        sm.v=sm.top+sm.bottom;
        sm.h=sm.left+sm.right;
        if(sm.top&&this.scrollTop<=0&&this.session)
            this.session.setScrollTop(-sm.top);
        this.updateFull();
    };
    this.getHScrollBarAlwaysVisible=function(){
        returnthis.$hScrollBarAlwaysVisible;
    };
    this.setHScrollBarAlwaysVisible=function(alwaysVisible){
        this.setOption("hScrollBarAlwaysVisible",alwaysVisible);
    };
    this.getVScrollBarAlwaysVisible=function(){
        returnthis.$vScrollBarAlwaysVisible;
    };
    this.setVScrollBarAlwaysVisible=function(alwaysVisible){
        this.setOption("vScrollBarAlwaysVisible",alwaysVisible);
    };

    this.$updateScrollBarV=function(){
        varscrollHeight=this.layerConfig.maxHeight;
        varscrollerHeight=this.$size.scrollerHeight;
        if(!this.$maxLines&&this.$scrollPastEnd){
            scrollHeight-=(scrollerHeight-this.lineHeight)*this.$scrollPastEnd;
            if(this.scrollTop>scrollHeight-scrollerHeight){
                scrollHeight=this.scrollTop+scrollerHeight;
                this.scrollBarV.scrollTop=null;
            }
        }
        this.scrollBarV.setScrollHeight(scrollHeight+this.scrollMargin.v);
        this.scrollBarV.setScrollTop(this.scrollTop+this.scrollMargin.top);
    };
    this.$updateScrollBarH=function(){
        this.scrollBarH.setScrollWidth(this.layerConfig.width+2*this.$padding+this.scrollMargin.h);
        this.scrollBarH.setScrollLeft(this.scrollLeft+this.scrollMargin.left);
    };
    
    this.$frozen=false;
    this.freeze=function(){
        this.$frozen=true;
    };
    
    this.unfreeze=function(){
        this.$frozen=false;
    };

    this.$renderChanges=function(changes,force){
        if(this.$changes){
            changes|=this.$changes;
            this.$changes=0;
        }
        if((!this.session||!this.container.offsetWidth||this.$frozen)||(!changes&&!force)){
            this.$changes|=changes;
            return;
        }
        if(this.$size.$dirty){
            this.$changes|=changes;
            returnthis.onResize(true);
        }
        if(!this.lineHeight){
            this.$textLayer.checkForSizeChanges();
        }
        
        this._signal("beforeRender");
        
        if(this.session&&this.session.$bidiHandler)
            this.session.$bidiHandler.updateCharacterWidths(this.$fontMetrics);

        varconfig=this.layerConfig;
        if(changes&this.CHANGE_FULL||
            changes&this.CHANGE_SIZE||
            changes&this.CHANGE_TEXT||
            changes&this.CHANGE_LINES||
            changes&this.CHANGE_SCROLL||
            changes&this.CHANGE_H_SCROLL
        ){
            changes|=this.$computeLayerConfig();
            if(config.firstRow!=this.layerConfig.firstRow&&config.firstRowScreen==this.layerConfig.firstRowScreen){
                varst=this.scrollTop+(config.firstRow-this.layerConfig.firstRow)*this.lineHeight;
                if(st>0){
                    this.scrollTop=st;
                    changes=changes|this.CHANGE_SCROLL;
                    changes|=this.$computeLayerConfig();
                }
            }
            config=this.layerConfig;
            this.$updateScrollBarV();
            if(changes&this.CHANGE_H_SCROLL)
                this.$updateScrollBarH();
            this.$gutterLayer.element.style.marginTop=(-config.offset)+"px";
            this.content.style.marginTop=(-config.offset)+"px";
            this.content.style.width=config.width+2*this.$padding+"px";
            this.content.style.height=config.minHeight+"px";
        }
        if(changes&this.CHANGE_H_SCROLL){
            this.content.style.marginLeft=-this.scrollLeft+"px";
            this.scroller.className=this.scrollLeft<=0?"ace_scroller":"ace_scrollerace_scroll-left";
        }
        if(changes&this.CHANGE_FULL){
            this.$textLayer.update(config);
            if(this.$showGutter)
                this.$gutterLayer.update(config);
            this.$markerBack.update(config);
            this.$markerFront.update(config);
            this.$cursorLayer.update(config);
            this.$moveTextAreaToCursor();
            this.$highlightGutterLine&&this.$updateGutterLineHighlight();
            this._signal("afterRender");
            return;
        }
        if(changes&this.CHANGE_SCROLL){
            if(changes&this.CHANGE_TEXT||changes&this.CHANGE_LINES)
                this.$textLayer.update(config);
            else
                this.$textLayer.scrollLines(config);

            if(this.$showGutter)
                this.$gutterLayer.update(config);
            this.$markerBack.update(config);
            this.$markerFront.update(config);
            this.$cursorLayer.update(config);
            this.$highlightGutterLine&&this.$updateGutterLineHighlight();
            this.$moveTextAreaToCursor();
            this._signal("afterRender");
            return;
        }

        if(changes&this.CHANGE_TEXT){
            this.$textLayer.update(config);
            if(this.$showGutter)
                this.$gutterLayer.update(config);
        }
        elseif(changes&this.CHANGE_LINES){
            if(this.$updateLines()||(changes&this.CHANGE_GUTTER)&&this.$showGutter)
                this.$gutterLayer.update(config);
        }
        elseif(changes&this.CHANGE_TEXT||changes&this.CHANGE_GUTTER){
            if(this.$showGutter)
                this.$gutterLayer.update(config);
        }

        if(changes&this.CHANGE_CURSOR){
            this.$cursorLayer.update(config);
            this.$moveTextAreaToCursor();
            this.$highlightGutterLine&&this.$updateGutterLineHighlight();
        }

        if(changes&(this.CHANGE_MARKER|this.CHANGE_MARKER_FRONT)){
            this.$markerFront.update(config);
        }

        if(changes&(this.CHANGE_MARKER|this.CHANGE_MARKER_BACK)){
            this.$markerBack.update(config);
        }

        this._signal("afterRender");
    };

    
    this.$autosize=function(){
        varheight=this.session.getScreenLength()*this.lineHeight;
        varmaxHeight=this.$maxLines*this.lineHeight;
        vardesiredHeight=Math.min(maxHeight,
            Math.max((this.$minLines||1)*this.lineHeight,height)
        )+this.scrollMargin.v+(this.$extraHeight||0);
        if(this.$horizScroll)
            desiredHeight+=this.scrollBarH.getHeight();
        if(this.$maxPixelHeight&&desiredHeight>this.$maxPixelHeight)
            desiredHeight=this.$maxPixelHeight;
        varvScroll=height>maxHeight;
        
        if(desiredHeight!=this.desiredHeight||
            this.$size.height!=this.desiredHeight||vScroll!=this.$vScroll){
            if(vScroll!=this.$vScroll){
                this.$vScroll=vScroll;
                this.scrollBarV.setVisible(vScroll);
            }
            
            varw=this.container.clientWidth;
            this.container.style.height=desiredHeight+"px";
            this.$updateCachedSize(true,this.$gutterWidth,w,desiredHeight);
            this.desiredHeight=desiredHeight;
            
            this._signal("autosize");
        }
    };
    
    this.$computeLayerConfig=function(){
        varsession=this.session;
        varsize=this.$size;
        
        varhideScrollbars=size.height<=2*this.lineHeight;
        varscreenLines=this.session.getScreenLength();
        varmaxHeight=screenLines*this.lineHeight;

        varlongestLine=this.$getLongestLine();
        
        varhorizScroll=!hideScrollbars&&(this.$hScrollBarAlwaysVisible||
            size.scrollerWidth-longestLine-2*this.$padding<0);

        varhScrollChanged=this.$horizScroll!==horizScroll;
        if(hScrollChanged){
            this.$horizScroll=horizScroll;
            this.scrollBarH.setVisible(horizScroll);
        }
        varvScrollBefore=this.$vScroll;//autosizecanchangevscrollvalueinwhichcaseweneedtoupdatelongestLine
        if(this.$maxLines&&this.lineHeight>1)
            this.$autosize();

        varoffset=this.scrollTop%this.lineHeight;
        varminHeight=size.scrollerHeight+this.lineHeight;
        
        varscrollPastEnd=!this.$maxLines&&this.$scrollPastEnd
            ?(size.scrollerHeight-this.lineHeight)*this.$scrollPastEnd
            :0;
        maxHeight+=scrollPastEnd;
        
        varsm=this.scrollMargin;
        this.session.setScrollTop(Math.max(-sm.top,
            Math.min(this.scrollTop,maxHeight-size.scrollerHeight+sm.bottom)));

        this.session.setScrollLeft(Math.max(-sm.left,Math.min(this.scrollLeft,
            longestLine+2*this.$padding-size.scrollerWidth+sm.right)));
        
        varvScroll=!hideScrollbars&&(this.$vScrollBarAlwaysVisible||
            size.scrollerHeight-maxHeight+scrollPastEnd<0||this.scrollTop>sm.top);
        varvScrollChanged=vScrollBefore!==vScroll;
        if(vScrollChanged){
            this.$vScroll=vScroll;
            this.scrollBarV.setVisible(vScroll);
        }

        varlineCount=Math.ceil(minHeight/this.lineHeight)-1;
        varfirstRow=Math.max(0,Math.round((this.scrollTop-offset)/this.lineHeight));
        varlastRow=firstRow+lineCount;
        varfirstRowScreen,firstRowHeight;
        varlineHeight=this.lineHeight;
        firstRow=session.screenToDocumentRow(firstRow,0);
        varfoldLine=session.getFoldLine(firstRow);
        if(foldLine){
            firstRow=foldLine.start.row;
        }

        firstRowScreen=session.documentToScreenRow(firstRow,0);
        firstRowHeight=session.getRowLength(firstRow)*lineHeight;

        lastRow=Math.min(session.screenToDocumentRow(lastRow,0),session.getLength()-1);
        minHeight=size.scrollerHeight+session.getRowLength(lastRow)*lineHeight+
                                                firstRowHeight;

        offset=this.scrollTop-firstRowScreen*lineHeight;

        varchanges=0;
        if(this.layerConfig.width!=longestLine||hScrollChanged)
            changes=this.CHANGE_H_SCROLL;
        if(hScrollChanged||vScrollChanged){
            changes=this.$updateCachedSize(true,this.gutterWidth,size.width,size.height);
            this._signal("scrollbarVisibilityChanged");
            if(vScrollChanged)
                longestLine=this.$getLongestLine();
        }
        
        this.layerConfig={
            width:longestLine,
            padding:this.$padding,
            firstRow:firstRow,
            firstRowScreen:firstRowScreen,
            lastRow:lastRow,
            lineHeight:lineHeight,
            characterWidth:this.characterWidth,
            minHeight:minHeight,
            maxHeight:maxHeight,
            offset:offset,
            gutterOffset:lineHeight?Math.max(0,Math.ceil((offset+size.height-size.scrollerHeight)/lineHeight)):0,
            height:this.$size.scrollerHeight
        };

        returnchanges;
    };

    this.$updateLines=function(){
        if(!this.$changedLines)return;
        varfirstRow=this.$changedLines.firstRow;
        varlastRow=this.$changedLines.lastRow;
        this.$changedLines=null;

        varlayerConfig=this.layerConfig;

        if(firstRow>layerConfig.lastRow+1){return;}
        if(lastRow<layerConfig.firstRow){return;}
        if(lastRow===Infinity){
            if(this.$showGutter)
                this.$gutterLayer.update(layerConfig);
            this.$textLayer.update(layerConfig);
            return;
        }
        this.$textLayer.updateLines(layerConfig,firstRow,lastRow);
        returntrue;
    };

    this.$getLongestLine=function(){
        varcharCount=this.session.getScreenWidth();
        if(this.showInvisibles&&!this.session.$useWrapMode)
            charCount+=1;
            
        if(this.$textLayer&&charCount>this.$textLayer.MAX_LINE_LENGTH)
            charCount=this.$textLayer.MAX_LINE_LENGTH+30;

        returnMath.max(this.$size.scrollerWidth-2*this.$padding,Math.round(charCount*this.characterWidth));
    };
    this.updateFrontMarkers=function(){
        this.$markerFront.setMarkers(this.session.getMarkers(true));
        this.$loop.schedule(this.CHANGE_MARKER_FRONT);
    };
    this.updateBackMarkers=function(){
        this.$markerBack.setMarkers(this.session.getMarkers());
        this.$loop.schedule(this.CHANGE_MARKER_BACK);
    };
    this.addGutterDecoration=function(row,className){
        this.$gutterLayer.addGutterDecoration(row,className);
    };
    this.removeGutterDecoration=function(row,className){
        this.$gutterLayer.removeGutterDecoration(row,className);
    };
    this.updateBreakpoints=function(rows){
        this.$loop.schedule(this.CHANGE_GUTTER);
    };
    this.setAnnotations=function(annotations){
        this.$gutterLayer.setAnnotations(annotations);
        this.$loop.schedule(this.CHANGE_GUTTER);
    };
    this.updateCursor=function(){
        this.$loop.schedule(this.CHANGE_CURSOR);
    };
    this.hideCursor=function(){
        this.$cursorLayer.hideCursor();
    };
    this.showCursor=function(){
        this.$cursorLayer.showCursor();
    };

    this.scrollSelectionIntoView=function(anchor,lead,offset){
        this.scrollCursorIntoView(anchor,offset);
        this.scrollCursorIntoView(lead,offset);
    };
    this.scrollCursorIntoView=function(cursor,offset,$viewMargin){
        if(this.$size.scrollerHeight===0)
            return;

        varpos=this.$cursorLayer.getPixelPosition(cursor);

        varleft=pos.left;
        vartop=pos.top;
        
        vartopMargin=$viewMargin&&$viewMargin.top||0;
        varbottomMargin=$viewMargin&&$viewMargin.bottom||0;
        
        varscrollTop=this.$scrollAnimation?this.session.getScrollTop():this.scrollTop;
        
        if(scrollTop+topMargin>top){
            if(offset&&scrollTop+topMargin>top+this.lineHeight)
                top-=offset*this.$size.scrollerHeight;
            if(top===0)
                top=-this.scrollMargin.top;
            this.session.setScrollTop(top);
        }elseif(scrollTop+this.$size.scrollerHeight-bottomMargin<top+this.lineHeight){
            if(offset&&scrollTop+this.$size.scrollerHeight-bottomMargin<top- this.lineHeight)
                top+=offset*this.$size.scrollerHeight;
            this.session.setScrollTop(top+this.lineHeight-this.$size.scrollerHeight);
        }

        varscrollLeft=this.scrollLeft;

        if(scrollLeft>left){
            if(left<this.$padding+2*this.layerConfig.characterWidth)
                left=-this.scrollMargin.left;
            this.session.setScrollLeft(left);
        }elseif(scrollLeft+this.$size.scrollerWidth<left+this.characterWidth){
            this.session.setScrollLeft(Math.round(left+this.characterWidth-this.$size.scrollerWidth));
        }elseif(scrollLeft<=this.$padding&&left-scrollLeft<this.characterWidth){
            this.session.setScrollLeft(0);
        }
    };
    this.getScrollTop=function(){
        returnthis.session.getScrollTop();
    };
    this.getScrollLeft=function(){
        returnthis.session.getScrollLeft();
    };
    this.getScrollTopRow=function(){
        returnthis.scrollTop/this.lineHeight;
    };
    this.getScrollBottomRow=function(){
        returnMath.max(0,Math.floor((this.scrollTop+this.$size.scrollerHeight)/this.lineHeight)-1);
    };
    this.scrollToRow=function(row){
        this.session.setScrollTop(row*this.lineHeight);
    };

    this.alignCursor=function(cursor,alignment){
        if(typeofcursor=="number")
            cursor={row:cursor,column:0};

        varpos=this.$cursorLayer.getPixelPosition(cursor);
        varh=this.$size.scrollerHeight-this.lineHeight;
        varoffset=pos.top-h*(alignment||0);

        this.session.setScrollTop(offset);
        returnoffset;
    };

    this.STEPS=8;
    this.$calcSteps=function(fromValue,toValue){
        vari=0;
        varl=this.STEPS;
        varsteps=[];

        varfunc =function(t,x_min,dx){
            returndx*(Math.pow(t-1,3)+1)+x_min;
        };

        for(i=0;i<l;++i)
            steps.push(func(i/this.STEPS,fromValue,toValue-fromValue));

        returnsteps;
    };
    this.scrollToLine=function(line,center,animate,callback){
        varpos=this.$cursorLayer.getPixelPosition({row:line,column:0});
        varoffset=pos.top;
        if(center)
            offset-=this.$size.scrollerHeight/2;

        varinitialScroll=this.scrollTop;
        this.session.setScrollTop(offset);
        if(animate!==false)
            this.animateScrolling(initialScroll,callback);
    };

    this.animateScrolling=function(fromValue,callback){
        vartoValue=this.scrollTop;
        if(!this.$animatedScroll)
            return;
        var_self=this;
        
        if(fromValue==toValue)
            return;
        
        if(this.$scrollAnimation){
            varoldSteps=this.$scrollAnimation.steps;
            if(oldSteps.length){
                fromValue=oldSteps[0];
                if(fromValue==toValue)
                    return;
            }
        }
        
        varsteps=_self.$calcSteps(fromValue,toValue);
        this.$scrollAnimation={from:fromValue,to:toValue,steps:steps};

        clearInterval(this.$timer);

        _self.session.setScrollTop(steps.shift());
        _self.session.$scrollTop=toValue;
        this.$timer=setInterval(function(){
            if(steps.length){
                _self.session.setScrollTop(steps.shift());
                _self.session.$scrollTop=toValue;
            }elseif(toValue!=null){
                _self.session.$scrollTop=-1;
                _self.session.setScrollTop(toValue);
                toValue=null;
            }else{
                _self.$timer=clearInterval(_self.$timer);
                _self.$scrollAnimation=null;
                callback&&callback();
            }
        },10);
    };
    this.scrollToY=function(scrollTop){
        if(this.scrollTop!==scrollTop){
            this.$loop.schedule(this.CHANGE_SCROLL);
            this.scrollTop=scrollTop;
        }
    };
    this.scrollToX=function(scrollLeft){
        if(this.scrollLeft!==scrollLeft)
            this.scrollLeft=scrollLeft;
        this.$loop.schedule(this.CHANGE_H_SCROLL);
    };
    this.scrollTo=function(x,y){
        this.session.setScrollTop(y);
        this.session.setScrollLeft(y);
    };
    this.scrollBy=function(deltaX,deltaY){
        deltaY&&this.session.setScrollTop(this.session.getScrollTop()+deltaY);
        deltaX&&this.session.setScrollLeft(this.session.getScrollLeft()+deltaX);
    };
    this.isScrollableBy=function(deltaX,deltaY){
        if(deltaY<0&&this.session.getScrollTop()>=1-this.scrollMargin.top)
           returntrue;
        if(deltaY>0&&this.session.getScrollTop()+this.$size.scrollerHeight
            -this.layerConfig.maxHeight<-1+this.scrollMargin.bottom)
           returntrue;
        if(deltaX<0&&this.session.getScrollLeft()>=1-this.scrollMargin.left)
            returntrue;
        if(deltaX>0&&this.session.getScrollLeft()+this.$size.scrollerWidth
            -this.layerConfig.width<-1+this.scrollMargin.right)
           returntrue;
    };

    this.pixelToScreenCoordinates=function(x,y){
        varcanvasPos=this.scroller.getBoundingClientRect();

        varoffsetX=x+this.scrollLeft-canvasPos.left-this.$padding;
        varoffset=offsetX/this.characterWidth;
        varrow=Math.floor((y+this.scrollTop-canvasPos.top)/this.lineHeight);
        varcol=Math.round(offset);

        return{row:row,column:col,side:offset-col>0?1:-1,offsetX: offsetX};
    };

    this.screenToTextCoordinates=function(x,y){
        varcanvasPos=this.scroller.getBoundingClientRect();
        varoffsetX=x+this.scrollLeft-canvasPos.left-this.$padding;
        
        varcol=Math.round(offsetX/this.characterWidth);

        varrow=(y+this.scrollTop-canvasPos.top)/this.lineHeight;

        returnthis.session.screenToDocumentPosition(row,Math.max(col,0),offsetX);
    };
    this.textToScreenCoordinates=function(row,column){
        varcanvasPos=this.scroller.getBoundingClientRect();
        varpos=this.session.documentToScreenPosition(row,column);

        varx=this.$padding+(this.session.$bidiHandler.isBidiRow(pos.row,row)
             ?this.session.$bidiHandler.getPosLeft(pos.column)
             :Math.round(pos.column*this.characterWidth));
        
        vary=pos.row*this.lineHeight;

        return{
            pageX:canvasPos.left+x-this.scrollLeft,
            pageY:canvasPos.top+y-this.scrollTop
        };
    };
    this.visualizeFocus=function(){
        dom.addCssClass(this.container,"ace_focus");
    };
    this.visualizeBlur=function(){
        dom.removeCssClass(this.container,"ace_focus");
    };
    this.showComposition=function(position){
        if(!this.$composition)
            this.$composition={
                keepTextAreaAtCursor:this.$keepTextAreaAtCursor,
                cssText:this.textarea.style.cssText
            };

        this.$keepTextAreaAtCursor=true;
        dom.addCssClass(this.textarea,"ace_composition");
        this.textarea.style.cssText="";
        this.$moveTextAreaToCursor();
    };
    this.setCompositionText=function(text){
        this.$moveTextAreaToCursor();
    };
    this.hideComposition=function(){
        if(!this.$composition)
            return;

        dom.removeCssClass(this.textarea,"ace_composition");
        this.$keepTextAreaAtCursor=this.$composition.keepTextAreaAtCursor;
        this.textarea.style.cssText=this.$composition.cssText;
        this.$composition=null;
    };
    this.setTheme=function(theme,cb){
        var_self=this;
        this.$themeId=theme;
        _self._dispatchEvent('themeChange',{theme:theme});

        if(!theme||typeoftheme=="string"){
            varmoduleName=theme||this.$options.theme.initialValue;
            config.loadModule(["theme",moduleName],afterLoad);
        }else{
            afterLoad(theme);
        }

        functionafterLoad(module){
            if(_self.$themeId!=theme)
                returncb&&cb();
            if(!module||!module.cssClass)
                thrownewError("couldn'tloadmodule"+theme+"oritdidn'tcalldefine");
            if(module.$id)
                _self.$themeId=module.$id;
            dom.importCssString(
                module.cssText,
                module.cssClass,
                _self.container.ownerDocument
            );

            if(_self.theme)
                dom.removeCssClass(_self.container,_self.theme.cssClass);

            varpadding="padding"inmodule?module.padding
                :"padding"in(_self.theme||{})?4:_self.$padding;
            if(_self.$padding&&padding!=_self.$padding)
                _self.setPadding(padding);
            _self.$theme=module.cssClass;

            _self.theme=module;
            dom.addCssClass(_self.container,module.cssClass);
            dom.setCssClass(_self.container,"ace_dark",module.isDark);
            if(_self.$size){
                _self.$size.width=0;
                _self.$updateSizeAsync();
            }

            _self._dispatchEvent('themeLoaded',{theme:module});
            cb&&cb();
        }
    };
    this.getTheme=function(){
        returnthis.$themeId;
    };
    this.setStyle=function(style,include){
        dom.setCssClass(this.container,style,include!==false);
    };
    this.unsetStyle=function(style){
        dom.removeCssClass(this.container,style);
    };
    
    this.setCursorStyle=function(style){
        if(this.scroller.style.cursor!=style)
            this.scroller.style.cursor=style;
    };
    this.setMouseCursor=function(cursorStyle){
        this.scroller.style.cursor=cursorStyle;
    };
    this.destroy=function(){
        this.$textLayer.destroy();
        this.$cursorLayer.destroy();
    };

}).call(VirtualRenderer.prototype);


config.defineOptions(VirtualRenderer.prototype,"renderer",{
    animatedScroll:{initialValue:false},
    showInvisibles:{
        set:function(value){
            if(this.$textLayer.setShowInvisibles(value))
                this.$loop.schedule(this.CHANGE_TEXT);
        },
        initialValue:false
    },
    showPrintMargin:{
        set:function(){this.$updatePrintMargin();},
        initialValue:true
    },
    printMarginColumn:{
        set:function(){this.$updatePrintMargin();},
        initialValue:80
    },
    printMargin:{
        set:function(val){
            if(typeofval=="number")
                this.$printMarginColumn=val;
            this.$showPrintMargin=!!val;
            this.$updatePrintMargin();
        },
        get:function(){
            returnthis.$showPrintMargin&&this.$printMarginColumn;
        }
    },
    showGutter:{
        set:function(show){
            this.$gutter.style.display=show?"block":"none";
            this.$loop.schedule(this.CHANGE_FULL);
            this.onGutterResize();
        },
        initialValue:true
    },
    fadeFoldWidgets:{
        set:function(show){
            dom.setCssClass(this.$gutter,"ace_fade-fold-widgets",show);
        },
        initialValue:false
    },
    showFoldWidgets:{
        set:function(show){this.$gutterLayer.setShowFoldWidgets(show);},
        initialValue:true
    },
    showLineNumbers:{
        set:function(show){
            this.$gutterLayer.setShowLineNumbers(show);
            this.$loop.schedule(this.CHANGE_GUTTER);
        },
        initialValue:true
    },
    displayIndentGuides:{
        set:function(show){
            if(this.$textLayer.setDisplayIndentGuides(show))
                this.$loop.schedule(this.CHANGE_TEXT);
        },
        initialValue:true
    },
    highlightGutterLine:{
        set:function(shouldHighlight){
            if(!this.$gutterLineHighlight){
                this.$gutterLineHighlight=dom.createElement("div");
                this.$gutterLineHighlight.className="ace_gutter-active-line";
                this.$gutter.appendChild(this.$gutterLineHighlight);
                return;
            }

            this.$gutterLineHighlight.style.display=shouldHighlight?"":"none";
            if(this.$cursorLayer.$pixelPos)
                this.$updateGutterLineHighlight();
        },
        initialValue:false,
        value:true
    },
    hScrollBarAlwaysVisible:{
        set:function(val){
            if(!this.$hScrollBarAlwaysVisible||!this.$horizScroll)
                this.$loop.schedule(this.CHANGE_SCROLL);
        },
        initialValue:false
    },
    vScrollBarAlwaysVisible:{
        set:function(val){
            if(!this.$vScrollBarAlwaysVisible||!this.$vScroll)
                this.$loop.schedule(this.CHANGE_SCROLL);
        },
        initialValue:false
    },
    fontSize: {
        set:function(size){
            if(typeofsize=="number")
                size=size+"px";
            this.container.style.fontSize=size;
            this.updateFontSize();
        },
        initialValue:12
    },
    fontFamily:{
        set:function(name){
            this.container.style.fontFamily=name;
            this.updateFontSize();
        }
    },
    maxLines:{
        set:function(val){
            this.updateFull();
        }
    },
    minLines:{
        set:function(val){
            this.updateFull();
        }
    },
    maxPixelHeight:{
        set:function(val){
            this.updateFull();
        },
        initialValue:0
    },
    scrollPastEnd:{
        set:function(val){
            val=+val||0;
            if(this.$scrollPastEnd==val)
                return;
            this.$scrollPastEnd=val;
            this.$loop.schedule(this.CHANGE_SCROLL);
        },
        initialValue:0,
        handlesSet:true
    },
    fixedWidthGutter:{
        set:function(val){
            this.$gutterLayer.$fixedWidth=!!val;
            this.$loop.schedule(this.CHANGE_GUTTER);
        }
    },
    theme:{
        set:function(val){this.setTheme(val);},
        get:function(){returnthis.$themeId||this.theme;},
        initialValue:"./theme/textmate",
        handlesSet:true
    }
});

exports.VirtualRenderer=VirtualRenderer;
});

define("ace/worker/worker_client",["require","exports","module","ace/lib/oop","ace/lib/net","ace/lib/event_emitter","ace/config"],function(require,exports,module){
"usestrict";

varoop=require("../lib/oop");
varnet=require("../lib/net");
varEventEmitter=require("../lib/event_emitter").EventEmitter;
varconfig=require("../config");

function$workerBlob(workerUrl){
    varscript="importScripts('"+net.qualifyURL(workerUrl)+"');";
    try{
        returnnewBlob([script],{"type":"application/javascript"});
    }catch(e){//Backwards-compatibility
        varBlobBuilder=window.BlobBuilder||window.WebKitBlobBuilder||window.MozBlobBuilder;
        varblobBuilder=newBlobBuilder();
        blobBuilder.append(script);
        returnblobBuilder.getBlob("application/javascript");
    }
}

functioncreateWorker(workerUrl){
    if(typeofWorker=="undefined")
        return{postMessage:function(){},terminate:function(){}};
    varblob=$workerBlob(workerUrl);
    varURL=window.URL||window.webkitURL;
    varblobURL=URL.createObjectURL(blob);
    returnnewWorker(blobURL);
}

varWorkerClient=function(topLevelNamespaces,mod,classname,workerUrl,importScripts){
    this.$sendDeltaQueue=this.$sendDeltaQueue.bind(this);
    this.changeListener=this.changeListener.bind(this);
    this.onMessage=this.onMessage.bind(this);
    if(require.nameToUrl&&!require.toUrl)
        require.toUrl=require.nameToUrl;
    
    if(config.get("packaged")||!require.toUrl){
        workerUrl=workerUrl||config.moduleUrl(mod,"worker");
    }else{
        varnormalizePath=this.$normalizePath;
        workerUrl=workerUrl||normalizePath(require.toUrl("ace/worker/worker.js",null,"_"));

        vartlns={};
        topLevelNamespaces.forEach(function(ns){
            tlns[ns]=normalizePath(require.toUrl(ns,null,"_").replace(/(\.js)?(\?.*)?$/,""));
        });
    }

    this.$worker=createWorker(workerUrl);
    if(importScripts){
        this.send("importScripts",importScripts);
    }
    this.$worker.postMessage({
        init:true,
        tlns:tlns,
        module:mod,
        classname:classname
    });

    this.callbackId=1;
    this.callbacks={};

    this.$worker.onmessage=this.onMessage;
};

(function(){

    oop.implement(this,EventEmitter);

    this.onMessage=function(e){
        varmsg=e.data;
        switch(msg.type){
            case"event":
                this._signal(msg.name,{data:msg.data});
                break;
            case"call":
                varcallback=this.callbacks[msg.id];
                if(callback){
                    callback(msg.data);
                    deletethis.callbacks[msg.id];
                }
                break;
            case"error":
                this.reportError(msg.data);
                break;
            case"log":
                window.console&&console.log&&console.log.apply(console,msg.data);
                break;
        }
    };
    
    this.reportError=function(err){
        window.console&&console.error&&console.error(err);
    };

    this.$normalizePath=function(path){
        returnnet.qualifyURL(path);
    };

    this.terminate=function(){
        this._signal("terminate",{});
        this.deltaQueue=null;
        this.$worker.terminate();
        this.$worker=null;
        if(this.$doc)
            this.$doc.off("change",this.changeListener);
        this.$doc=null;
    };

    this.send=function(cmd,args){
        this.$worker.postMessage({command:cmd,args:args});
    };

    this.call=function(cmd,args,callback){
        if(callback){
            varid=this.callbackId++;
            this.callbacks[id]=callback;
            args.push(id);
        }
        this.send(cmd,args);
    };

    this.emit=function(event,data){
        try{
            this.$worker.postMessage({event:event,data:{data:data.data}});
        }
        catch(ex){
            console.error(ex.stack);
        }
    };

    this.attachToDocument=function(doc){
        if(this.$doc)
            this.terminate();

        this.$doc=doc;
        this.call("setValue",[doc.getValue()]);
        doc.on("change",this.changeListener);
    };

    this.changeListener=function(delta){
        if(!this.deltaQueue){
            this.deltaQueue=[];
            setTimeout(this.$sendDeltaQueue,0);
        }
        if(delta.action=="insert")
            this.deltaQueue.push(delta.start,delta.lines);
        else
            this.deltaQueue.push(delta.start,delta.end);
    };

    this.$sendDeltaQueue=function(){
        varq=this.deltaQueue;
        if(!q)return;
        this.deltaQueue=null;
        if(q.length>50&&q.length>this.$doc.getLength()>>1){
            this.call("setValue",[this.$doc.getValue()]);
        }else
            this.emit("change",{data:q});
    };

}).call(WorkerClient.prototype);


varUIWorkerClient=function(topLevelNamespaces,mod,classname){
    this.$sendDeltaQueue=this.$sendDeltaQueue.bind(this);
    this.changeListener=this.changeListener.bind(this);
    this.callbackId=1;
    this.callbacks={};
    this.messageBuffer=[];

    varmain=null;
    varemitSync=false;
    varsender=Object.create(EventEmitter);
    var_self=this;

    this.$worker={};
    this.$worker.terminate=function(){};
    this.$worker.postMessage=function(e){
        _self.messageBuffer.push(e);
        if(main){
            if(emitSync)
                setTimeout(processNext);
            else
                processNext();
        }
    };
    this.setEmitSync=function(val){emitSync=val;};

    varprocessNext=function(){
        varmsg=_self.messageBuffer.shift();
        if(msg.command)
            main[msg.command].apply(main,msg.args);
        elseif(msg.event)
            sender._signal(msg.event,msg.data);
    };

    sender.postMessage=function(msg){
        _self.onMessage({data:msg});
    };
    sender.callback=function(data,callbackId){
        this.postMessage({type:"call",id:callbackId,data:data});
    };
    sender.emit=function(name,data){
        this.postMessage({type:"event",name:name,data:data});
    };

    config.loadModule(["worker",mod],function(Main){
        main=newMain[classname](sender);
        while(_self.messageBuffer.length)
            processNext();
    });
};

UIWorkerClient.prototype=WorkerClient.prototype;

exports.UIWorkerClient=UIWorkerClient;
exports.WorkerClient=WorkerClient;
exports.createWorker=createWorker;


});

define("ace/placeholder",["require","exports","module","ace/range","ace/lib/event_emitter","ace/lib/oop"],function(require,exports,module){
"usestrict";

varRange=require("./range").Range;
varEventEmitter=require("./lib/event_emitter").EventEmitter;
varoop=require("./lib/oop");

varPlaceHolder=function(session,length,pos,others,mainClass,othersClass){
    var_self=this;
    this.length=length;
    this.session=session;
    this.doc=session.getDocument();
    this.mainClass=mainClass;
    this.othersClass=othersClass;
    this.$onUpdate=this.onUpdate.bind(this);
    this.doc.on("change",this.$onUpdate);
    this.$others=others;
    
    this.$onCursorChange=function(){
        setTimeout(function(){
            _self.onCursorChange();
        });
    };
    
    this.$pos=pos;
    varundoStack=session.getUndoManager().$undoStack||session.getUndoManager().$undostack||{length:-1};
    this.$undoStackDepth=undoStack.length;
    this.setup();

    session.selection.on("changeCursor",this.$onCursorChange);
};

(function(){

    oop.implement(this,EventEmitter);
    this.setup=function(){
        var_self=this;
        vardoc=this.doc;
        varsession=this.session;
        
        this.selectionBefore=session.selection.toJSON();
        if(session.selection.inMultiSelectMode)
            session.selection.toSingleRange();

        this.pos=doc.createAnchor(this.$pos.row,this.$pos.column);
        varpos=this.pos;
        pos.$insertRight=true;
        pos.detach();
        pos.markerId=session.addMarker(newRange(pos.row,pos.column,pos.row,pos.column+this.length),this.mainClass,null,false);
        this.others=[];
        this.$others.forEach(function(other){
            varanchor=doc.createAnchor(other.row,other.column);
            anchor.$insertRight=true;
            anchor.detach();
            _self.others.push(anchor);
        });
        session.setUndoSelect(false);
    };
    this.showOtherMarkers=function(){
        if(this.othersActive)return;
        varsession=this.session;
        var_self=this;
        this.othersActive=true;
        this.others.forEach(function(anchor){
            anchor.markerId=session.addMarker(newRange(anchor.row,anchor.column,anchor.row,anchor.column+_self.length),_self.othersClass,null,false);
        });
    };
    this.hideOtherMarkers=function(){
        if(!this.othersActive)return;
        this.othersActive=false;
        for(vari=0;i<this.others.length;i++){
            this.session.removeMarker(this.others[i].markerId);
        }
    };
    this.onUpdate=function(delta){
        if(this.$updating)
            returnthis.updateAnchors(delta);
            
        varrange=delta;
        if(range.start.row!==range.end.row)return;
        if(range.start.row!==this.pos.row)return;
        this.$updating=true;
        varlengthDiff=delta.action==="insert"?range.end.column-range.start.column:range.start.column-range.end.column;
        varinMainRange=range.start.column>=this.pos.column&&range.start.column<=this.pos.column+this.length+1;
        vardistanceFromStart=range.start.column-this.pos.column;
        
        this.updateAnchors(delta);
        
        if(inMainRange)
            this.length+=lengthDiff;

        if(inMainRange&&!this.session.$fromUndo){
            if(delta.action==='insert'){
                for(vari=this.others.length-1;i>=0;i--){
                    varotherPos=this.others[i];
                    varnewPos={row:otherPos.row,column:otherPos.column+distanceFromStart};
                    this.doc.insertMergedLines(newPos,delta.lines);
                }
            }elseif(delta.action==='remove'){
                for(vari=this.others.length-1;i>=0;i--){
                    varotherPos=this.others[i];
                    varnewPos={row:otherPos.row,column:otherPos.column+distanceFromStart};
                    this.doc.remove(newRange(newPos.row,newPos.column,newPos.row,newPos.column-lengthDiff));
                }
            }
        }
        
        this.$updating=false;
        this.updateMarkers();
    };
    
    this.updateAnchors=function(delta){
        this.pos.onChange(delta);
        for(vari=this.others.length;i--;)
            this.others[i].onChange(delta);
        this.updateMarkers();
    };
    
    this.updateMarkers=function(){
        if(this.$updating)
            return;
        var_self=this;
        varsession=this.session;
        varupdateMarker=function(pos,className){
            session.removeMarker(pos.markerId);
            pos.markerId=session.addMarker(newRange(pos.row,pos.column,pos.row,pos.column+_self.length),className,null,false);
        };
        updateMarker(this.pos,this.mainClass);
        for(vari=this.others.length;i--;)
            updateMarker(this.others[i],this.othersClass);
    };

    this.onCursorChange=function(event){
        if(this.$updating||!this.session)return;
        varpos=this.session.selection.getCursor();
        if(pos.row===this.pos.row&&pos.column>=this.pos.column&&pos.column<=this.pos.column+this.length){
            this.showOtherMarkers();
            this._emit("cursorEnter",event);
        }else{
            this.hideOtherMarkers();
            this._emit("cursorLeave",event);
        }
    };   
    this.detach=function(){
        this.session.removeMarker(this.pos&&this.pos.markerId);
        this.hideOtherMarkers();
        this.doc.removeEventListener("change",this.$onUpdate);
        this.session.selection.removeEventListener("changeCursor",this.$onCursorChange);
        this.session.setUndoSelect(true);
        this.session=null;
    };
    this.cancel=function(){
        if(this.$undoStackDepth===-1)
            return;
        varundoManager=this.session.getUndoManager();
        varundosRequired=(undoManager.$undoStack||undoManager.$undostack).length-this.$undoStackDepth;
        for(vari=0;i<undosRequired;i++){
            undoManager.undo(this.session,true);
        }
        if(this.selectionBefore)
            this.session.selection.fromJSON(this.selectionBefore);
    };
}).call(PlaceHolder.prototype);


exports.PlaceHolder=PlaceHolder;
});

define("ace/mouse/multi_select_handler",["require","exports","module","ace/lib/event","ace/lib/useragent"],function(require,exports,module){

varevent=require("../lib/event");
varuseragent=require("../lib/useragent");
functionisSamePoint(p1,p2){
    returnp1.row==p2.row&&p1.column==p2.column;
}

functiononMouseDown(e){
    varev=e.domEvent;
    varalt=ev.altKey;
    varshift=ev.shiftKey;
    varctrl=ev.ctrlKey;
    varaccel=e.getAccelKey();
    varbutton=e.getButton();
    
    if(ctrl&&useragent.isMac)
        button=ev.button;

    if(e.editor.inMultiSelectMode&&button==2){
        e.editor.textInput.onContextMenu(e.domEvent);
        return;
    }
    
    if(!ctrl&&!alt&&!accel){
        if(button===0&&e.editor.inMultiSelectMode)
            e.editor.exitMultiSelectMode();
        return;
    }
    
    if(button!==0)
        return;

    vareditor=e.editor;
    varselection=editor.selection;
    varisMultiSelect=editor.inMultiSelectMode;
    varpos=e.getDocumentPosition();
    varcursor=selection.getCursor();
    varinSelection=e.inSelection()||(selection.isEmpty()&&isSamePoint(pos,cursor));

    varmouseX=e.x,mouseY=e.y;
    varonMouseSelection=function(e){
        mouseX=e.clientX;
        mouseY=e.clientY;
    };
    
    varsession=editor.session;
    varscreenAnchor=editor.renderer.pixelToScreenCoordinates(mouseX,mouseY);
    varscreenCursor=screenAnchor;
    
    varselectionMode;
    if(editor.$mouseHandler.$enableJumpToDef){
        if(ctrl&&alt||accel&&alt)
            selectionMode=shift?"block":"add";
        elseif(alt&&editor.$blockSelectEnabled)
            selectionMode="block";
    }else{
        if(accel&&!alt){
            selectionMode="add";
            if(!isMultiSelect&&shift)
                return;
        }elseif(alt&&editor.$blockSelectEnabled){
            selectionMode="block";
        }
    }
    
    if(selectionMode&&useragent.isMac&&ev.ctrlKey){
        editor.$mouseHandler.cancelContextMenu();
    }

    if(selectionMode=="add"){
        if(!isMultiSelect&&inSelection)
            return;//dragging

        if(!isMultiSelect){
            varrange=selection.toOrientedRange();
            editor.addSelectionMarker(range);
        }

        varoldRange=selection.rangeList.rangeAtPoint(pos);
        
        editor.inVirtualSelectionMode=true;
        
        if(shift){
            oldRange=null;
            range=selection.ranges[0]||range;
            editor.removeSelectionMarker(range);
        }
        editor.once("mouseup",function(){
            vartmpSel=selection.toOrientedRange();

            if(oldRange&&tmpSel.isEmpty()&&isSamePoint(oldRange.cursor,tmpSel.cursor))
                selection.substractPoint(tmpSel.cursor);
            else{
                if(shift){
                    selection.substractPoint(range.cursor);
                }elseif(range){
                    editor.removeSelectionMarker(range);
                    selection.addRange(range);
                }
                selection.addRange(tmpSel);
            }
            editor.inVirtualSelectionMode=false;
        });

    }elseif(selectionMode=="block"){
        e.stop();
        editor.inVirtualSelectionMode=true;       
        varinitialRange;
        varrectSel=[];
        varblockSelect=function(){
            varnewCursor=editor.renderer.pixelToScreenCoordinates(mouseX,mouseY);
            varcursor=session.screenToDocumentPosition(newCursor.row,newCursor.column,newCursor.offsetX);

            if(isSamePoint(screenCursor,newCursor)&&isSamePoint(cursor,selection.lead))
                return;
            screenCursor=newCursor;
            
            editor.selection.moveToPosition(cursor);
            editor.renderer.scrollCursorIntoView();

            editor.removeSelectionMarkers(rectSel);
            rectSel=selection.rectangularRangeBlock(screenCursor,screenAnchor);
            if(editor.$mouseHandler.$clickSelection&&rectSel.length==1&&rectSel[0].isEmpty())
                rectSel[0]=editor.$mouseHandler.$clickSelection.clone();
            rectSel.forEach(editor.addSelectionMarker,editor);
            editor.updateSelectionMarkers();
        };
        if(isMultiSelect&&!accel){
            selection.toSingleRange();
        }elseif(!isMultiSelect&&accel){
            initialRange=selection.toOrientedRange();
            editor.addSelectionMarker(initialRange);
        }
        
        if(shift)
            screenAnchor=session.documentToScreenPosition(selection.lead);           
        else
            selection.moveToPosition(pos);
        
        screenCursor={row:-1,column:-1};

        varonMouseSelectionEnd=function(e){
            clearInterval(timerId);
            editor.removeSelectionMarkers(rectSel);
            if(!rectSel.length)
                rectSel=[selection.toOrientedRange()];
            if(initialRange){
                editor.removeSelectionMarker(initialRange);
                selection.toSingleRange(initialRange);
            }
            for(vari=0;i<rectSel.length;i++)
                selection.addRange(rectSel[i]);
            editor.inVirtualSelectionMode=false;
            editor.$mouseHandler.$clickSelection=null;
        };

        varonSelectionInterval=blockSelect;

        event.capture(editor.container,onMouseSelection,onMouseSelectionEnd);
        vartimerId=setInterval(function(){onSelectionInterval();},20);

        returne.preventDefault();
    }
}


exports.onMouseDown=onMouseDown;

});

define("ace/commands/multi_select_commands",["require","exports","module","ace/keyboard/hash_handler"],function(require,exports,module){
exports.defaultCommands=[{
    name:"addCursorAbove",
    exec:function(editor){editor.selectMoreLines(-1);},
    bindKey:{win:"Ctrl-Alt-Up",mac:"Ctrl-Alt-Up"},
    scrollIntoView:"cursor",
    readOnly:true
},{
    name:"addCursorBelow",
    exec:function(editor){editor.selectMoreLines(1);},
    bindKey:{win:"Ctrl-Alt-Down",mac:"Ctrl-Alt-Down"},
    scrollIntoView:"cursor",
    readOnly:true
},{
    name:"addCursorAboveSkipCurrent",
    exec:function(editor){editor.selectMoreLines(-1,true);},
    bindKey:{win:"Ctrl-Alt-Shift-Up",mac:"Ctrl-Alt-Shift-Up"},
    scrollIntoView:"cursor",
    readOnly:true
},{
    name:"addCursorBelowSkipCurrent",
    exec:function(editor){editor.selectMoreLines(1,true);},
    bindKey:{win:"Ctrl-Alt-Shift-Down",mac:"Ctrl-Alt-Shift-Down"},
    scrollIntoView:"cursor",
    readOnly:true
},{
    name:"selectMoreBefore",
    exec:function(editor){editor.selectMore(-1);},
    bindKey:{win:"Ctrl-Alt-Left",mac:"Ctrl-Alt-Left"},
    scrollIntoView:"cursor",
    readOnly:true
},{
    name:"selectMoreAfter",
    exec:function(editor){editor.selectMore(1);},
    bindKey:{win:"Ctrl-Alt-Right",mac:"Ctrl-Alt-Right"},
    scrollIntoView:"cursor",
    readOnly:true
},{
    name:"selectNextBefore",
    exec:function(editor){editor.selectMore(-1,true);},
    bindKey:{win:"Ctrl-Alt-Shift-Left",mac:"Ctrl-Alt-Shift-Left"},
    scrollIntoView:"cursor",
    readOnly:true
},{
    name:"selectNextAfter",
    exec:function(editor){editor.selectMore(1,true);},
    bindKey:{win:"Ctrl-Alt-Shift-Right",mac:"Ctrl-Alt-Shift-Right"},
    scrollIntoView:"cursor",
    readOnly:true
},{
    name:"splitIntoLines",
    exec:function(editor){editor.multiSelect.splitIntoLines();},
    bindKey:{win:"Ctrl-Alt-L",mac:"Ctrl-Alt-L"},
    readOnly:true
},{
    name:"alignCursors",
    exec:function(editor){editor.alignCursors();},
    bindKey:{win:"Ctrl-Alt-A",mac:"Ctrl-Alt-A"},
    scrollIntoView:"cursor"
},{
    name:"findAll",
    exec:function(editor){editor.findAll();},
    bindKey:{win:"Ctrl-Alt-K",mac:"Ctrl-Alt-G"},
    scrollIntoView:"cursor",
    readOnly:true
}];
exports.multiSelectCommands=[{
    name:"singleSelection",
    bindKey:"esc",
    exec:function(editor){editor.exitMultiSelectMode();},
    scrollIntoView:"cursor",
    readOnly:true,
    isAvailable:function(editor){returneditor&&editor.inMultiSelectMode;}
}];

varHashHandler=require("../keyboard/hash_handler").HashHandler;
exports.keyboardHandler=newHashHandler(exports.multiSelectCommands);

});

define("ace/multi_select",["require","exports","module","ace/range_list","ace/range","ace/selection","ace/mouse/multi_select_handler","ace/lib/event","ace/lib/lang","ace/commands/multi_select_commands","ace/search","ace/edit_session","ace/editor","ace/config"],function(require,exports,module){

varRangeList=require("./range_list").RangeList;
varRange=require("./range").Range;
varSelection=require("./selection").Selection;
varonMouseDown=require("./mouse/multi_select_handler").onMouseDown;
varevent=require("./lib/event");
varlang=require("./lib/lang");
varcommands=require("./commands/multi_select_commands");
exports.commands=commands.defaultCommands.concat(commands.multiSelectCommands);
varSearch=require("./search").Search;
varsearch=newSearch();

functionfind(session,needle,dir){
    search.$options.wrap=true;
    search.$options.needle=needle;
    search.$options.backwards=dir==-1;
    returnsearch.find(session);
}
varEditSession=require("./edit_session").EditSession;
(function(){
    this.getSelectionMarkers=function(){
        returnthis.$selectionMarkers;
    };
}).call(EditSession.prototype);
(function(){
    this.ranges=null;
    this.rangeList=null;
    this.addRange=function(range,$blockChangeEvents){
        if(!range)
            return;

        if(!this.inMultiSelectMode&&this.rangeCount===0){
            varoldRange=this.toOrientedRange();
            this.rangeList.add(oldRange);
            this.rangeList.add(range);
            if(this.rangeList.ranges.length!=2){
                this.rangeList.removeAll();
                return$blockChangeEvents||this.fromOrientedRange(range);
            }
            this.rangeList.removeAll();
            this.rangeList.add(oldRange);
            this.$onAddRange(oldRange);
        }

        if(!range.cursor)
            range.cursor=range.end;

        varremoved=this.rangeList.add(range);

        this.$onAddRange(range);

        if(removed.length)
            this.$onRemoveRange(removed);

        if(this.rangeCount>1&&!this.inMultiSelectMode){
            this._signal("multiSelect");
            this.inMultiSelectMode=true;
            this.session.$undoSelect=false;
            this.rangeList.attach(this.session);
        }

        return$blockChangeEvents||this.fromOrientedRange(range);
    };

    this.toSingleRange=function(range){
        range=range||this.ranges[0];
        varremoved=this.rangeList.removeAll();
        if(removed.length)
            this.$onRemoveRange(removed);

        range&&this.fromOrientedRange(range);
    };
    this.substractPoint=function(pos){
        varremoved=this.rangeList.substractPoint(pos);
        if(removed){
            this.$onRemoveRange(removed);
            returnremoved[0];
        }
    };
    this.mergeOverlappingRanges=function(){
        varremoved=this.rangeList.merge();
        if(removed.length)
            this.$onRemoveRange(removed);
        elseif(this.ranges[0])
            this.fromOrientedRange(this.ranges[0]);
    };

    this.$onAddRange=function(range){
        this.rangeCount=this.rangeList.ranges.length;
        this.ranges.unshift(range);
        this._signal("addRange",{range:range});
    };

    this.$onRemoveRange=function(removed){
        this.rangeCount=this.rangeList.ranges.length;
        if(this.rangeCount==1&&this.inMultiSelectMode){
            varlastRange=this.rangeList.ranges.pop();
            removed.push(lastRange);
            this.rangeCount=0;
        }

        for(vari=removed.length;i--;){
            varindex=this.ranges.indexOf(removed[i]);
            this.ranges.splice(index,1);
        }

        this._signal("removeRange",{ranges:removed});

        if(this.rangeCount===0&&this.inMultiSelectMode){
            this.inMultiSelectMode=false;
            this._signal("singleSelect");
            this.session.$undoSelect=true;
            this.rangeList.detach(this.session);
        }

        lastRange=lastRange||this.ranges[0];
        if(lastRange&&!lastRange.isEqual(this.getRange()))
            this.fromOrientedRange(lastRange);
    };
    this.$initRangeList=function(){
        if(this.rangeList)
            return;

        this.rangeList=newRangeList();
        this.ranges=[];
        this.rangeCount=0;
    };
    this.getAllRanges=function(){
        returnthis.rangeCount?this.rangeList.ranges.concat():[this.getRange()];
    };

    this.splitIntoLines=function(){
        if(this.rangeCount>1){
            varranges=this.rangeList.ranges;
            varlastRange=ranges[ranges.length-1];
            varrange=Range.fromPoints(ranges[0].start,lastRange.end);

            this.toSingleRange();
            this.setSelectionRange(range,lastRange.cursor==lastRange.start);
        }else{
            varrange=this.getRange();
            varisBackwards=this.isBackwards();
            varstartRow=range.start.row;
            varendRow=range.end.row;
            if(startRow==endRow){
                if(isBackwards)
                    varstart=range.end,end=range.start;
                else
                    varstart=range.start,end=range.end;
                
                this.addRange(Range.fromPoints(end,end));
                this.addRange(Range.fromPoints(start,start));
                return;
            }

            varrectSel=[];
            varr=this.getLineRange(startRow,true);
            r.start.column=range.start.column;
            rectSel.push(r);

            for(vari=startRow+1;i<endRow;i++)
                rectSel.push(this.getLineRange(i,true));

            r=this.getLineRange(endRow,true);
            r.end.column=range.end.column;
            rectSel.push(r);

            rectSel.forEach(this.addRange,this);
        }
    };
    this.toggleBlockSelection=function(){
        if(this.rangeCount>1){
            varranges=this.rangeList.ranges;
            varlastRange=ranges[ranges.length-1];
            varrange=Range.fromPoints(ranges[0].start,lastRange.end);

            this.toSingleRange();
            this.setSelectionRange(range,lastRange.cursor==lastRange.start);
        }else{
            varcursor=this.session.documentToScreenPosition(this.cursor);
            varanchor=this.session.documentToScreenPosition(this.anchor);

            varrectSel=this.rectangularRangeBlock(cursor,anchor);
            rectSel.forEach(this.addRange,this);
        }
    };
    this.rectangularRangeBlock=function(screenCursor,screenAnchor,includeEmptyLines){
        varrectSel=[];

        varxBackwards=screenCursor.column<screenAnchor.column;
        if(xBackwards){
            varstartColumn=screenCursor.column;
            varendColumn=screenAnchor.column;
            varstartOffsetX=screenCursor.offsetX;
            varendOffsetX=screenAnchor.offsetX;
        }else{
            varstartColumn=screenAnchor.column;
            varendColumn=screenCursor.column;
            varstartOffsetX=screenAnchor.offsetX;
            varendOffsetX=screenCursor.offsetX;
        }

        varyBackwards=screenCursor.row<screenAnchor.row;
        if(yBackwards){
            varstartRow=screenCursor.row;
            varendRow=screenAnchor.row;
        }else{
            varstartRow=screenAnchor.row;
            varendRow=screenCursor.row;
        }

        if(startColumn<0)
            startColumn=0;
        if(startRow<0)
            startRow=0;

        if(startRow==endRow)
            includeEmptyLines=true;

        vardocEnd;
        for(varrow=startRow;row<=endRow;row++){
            varrange=Range.fromPoints(
                this.session.screenToDocumentPosition(row,startColumn,startOffsetX),
                this.session.screenToDocumentPosition(row,endColumn,endOffsetX)
            );
            if(range.isEmpty()){
                if(docEnd&&isSamePoint(range.end,docEnd))
                    break;
                docEnd=range.end;
            }
            range.cursor=xBackwards?range.start:range.end;
            rectSel.push(range);
        }

        if(yBackwards)
            rectSel.reverse();

        if(!includeEmptyLines){
            varend=rectSel.length-1;
            while(rectSel[end].isEmpty()&&end>0)
                end--;
            if(end>0){
                varstart=0;
                while(rectSel[start].isEmpty())
                    start++;
            }
            for(vari=end;i>=start;i--){
                if(rectSel[i].isEmpty())
                    rectSel.splice(i,1);
            }
        }

        returnrectSel;
    };
}).call(Selection.prototype);
varEditor=require("./editor").Editor;
(function(){
    this.updateSelectionMarkers=function(){
        this.renderer.updateCursor();
        this.renderer.updateBackMarkers();
    };
    this.addSelectionMarker=function(orientedRange){
        if(!orientedRange.cursor)
            orientedRange.cursor=orientedRange.end;

        varstyle=this.getSelectionStyle();
        orientedRange.marker=this.session.addMarker(orientedRange,"ace_selection",style);

        this.session.$selectionMarkers.push(orientedRange);
        this.session.selectionMarkerCount=this.session.$selectionMarkers.length;
        returnorientedRange;
    };
    this.removeSelectionMarker=function(range){
        if(!range.marker)
            return;
        this.session.removeMarker(range.marker);
        varindex=this.session.$selectionMarkers.indexOf(range);
        if(index!=-1)
            this.session.$selectionMarkers.splice(index,1);
        this.session.selectionMarkerCount=this.session.$selectionMarkers.length;
    };

    this.removeSelectionMarkers=function(ranges){
        varmarkerList=this.session.$selectionMarkers;
        for(vari=ranges.length;i--;){
            varrange=ranges[i];
            if(!range.marker)
                continue;
            this.session.removeMarker(range.marker);
            varindex=markerList.indexOf(range);
            if(index!=-1)
                markerList.splice(index,1);
        }
        this.session.selectionMarkerCount=markerList.length;
    };

    this.$onAddRange=function(e){
        this.addSelectionMarker(e.range);
        this.renderer.updateCursor();
        this.renderer.updateBackMarkers();
    };

    this.$onRemoveRange=function(e){
        this.removeSelectionMarkers(e.ranges);
        this.renderer.updateCursor();
        this.renderer.updateBackMarkers();
    };

    this.$onMultiSelect=function(e){
        if(this.inMultiSelectMode)
            return;
        this.inMultiSelectMode=true;

        this.setStyle("ace_multiselect");
        this.keyBinding.addKeyboardHandler(commands.keyboardHandler);
        this.commands.setDefaultHandler("exec",this.$onMultiSelectExec);

        this.renderer.updateCursor();
        this.renderer.updateBackMarkers();
    };

    this.$onSingleSelect=function(e){
        if(this.session.multiSelect.inVirtualMode)
            return;
        this.inMultiSelectMode=false;

        this.unsetStyle("ace_multiselect");
        this.keyBinding.removeKeyboardHandler(commands.keyboardHandler);

        this.commands.removeDefaultHandler("exec",this.$onMultiSelectExec);
        this.renderer.updateCursor();
        this.renderer.updateBackMarkers();
        this._emit("changeSelection");
    };

    this.$onMultiSelectExec=function(e){
        varcommand=e.command;
        vareditor=e.editor;
        if(!editor.multiSelect)
            return;
        if(!command.multiSelectAction){
            varresult=command.exec(editor,e.args||{});
            editor.multiSelect.addRange(editor.multiSelect.toOrientedRange());
            editor.multiSelect.mergeOverlappingRanges();
        }elseif(command.multiSelectAction=="forEach"){
            result=editor.forEachSelection(command,e.args);
        }elseif(command.multiSelectAction=="forEachLine"){
            result=editor.forEachSelection(command,e.args,true);
        }elseif(command.multiSelectAction=="single"){
            editor.exitMultiSelectMode();
            result=command.exec(editor,e.args||{});
        }else{
            result=command.multiSelectAction(editor,e.args||{});
        }
        returnresult;
    };
    this.forEachSelection=function(cmd,args,options){
        if(this.inVirtualSelectionMode)
            return;
        varkeepOrder=options&&options.keepOrder;
        var$byLines=options==true||options&&options.$byLines;
        varsession=this.session;
        varselection=this.selection;
        varrangeList=selection.rangeList;
        varranges=(keepOrder?selection:rangeList).ranges;
        varresult;
        
        if(!ranges.length)
            returncmd.exec?cmd.exec(this,args||{}):cmd(this,args||{});
        
        varreg=selection._eventRegistry;
        selection._eventRegistry={};

        vartmpSel=newSelection(session);
        this.inVirtualSelectionMode=true;
        for(vari=ranges.length;i--;){
            if($byLines){
                while(i>0&&ranges[i].start.row==ranges[i-1].end.row)
                    i--;
            }
            tmpSel.fromOrientedRange(ranges[i]);
            tmpSel.index=i;
            this.selection=session.selection=tmpSel;
            varcmdResult=cmd.exec?cmd.exec(this,args||{}):cmd(this,args||{});
            if(!result&&cmdResult!==undefined)
                result=cmdResult;
            tmpSel.toOrientedRange(ranges[i]);
        }
        tmpSel.detach();

        this.selection=session.selection=selection;
        this.inVirtualSelectionMode=false;
        selection._eventRegistry=reg;
        selection.mergeOverlappingRanges();
        
        varanim=this.renderer.$scrollAnimation;
        this.onCursorChange();
        this.onSelectionChange();
        if(anim&&anim.from==anim.to)
            this.renderer.animateScrolling(anim.from);
        
        returnresult;
    };
    this.exitMultiSelectMode=function(){
        if(!this.inMultiSelectMode||this.inVirtualSelectionMode)
            return;
        this.multiSelect.toSingleRange();
    };

    this.getSelectedText=function(){
        vartext="";
        if(this.inMultiSelectMode&&!this.inVirtualSelectionMode){
            varranges=this.multiSelect.rangeList.ranges;
            varbuf=[];
            for(vari=0;i<ranges.length;i++){
                buf.push(this.session.getTextRange(ranges[i]));
            }
            varnl=this.session.getDocument().getNewLineCharacter();
            text=buf.join(nl);
            if(text.length==(buf.length-1)*nl.length)
                text="";
        }elseif(!this.selection.isEmpty()){
            text=this.session.getTextRange(this.getSelectionRange());
        }
        returntext;
    };
    
    this.$checkMultiselectChange=function(e,anchor){
        if(this.inMultiSelectMode&&!this.inVirtualSelectionMode){
            varrange=this.multiSelect.ranges[0];
            if(this.multiSelect.isEmpty()&&anchor==this.multiSelect.anchor)
                return;
            varpos=anchor==this.multiSelect.anchor
                ?range.cursor==range.start?range.end:range.start
                :range.cursor;
            if(pos.row!=anchor.row
                ||this.session.$clipPositionToDocument(pos.row,pos.column).column!=anchor.column)
                this.multiSelect.toSingleRange(this.multiSelect.toOrientedRange());
        }
    };
    this.findAll=function(needle,options,additive){
        options=options||{};
        options.needle=needle||options.needle;
        if(options.needle==undefined){
            varrange=this.selection.isEmpty()
                ?this.selection.getWordRange()
                :this.selection.getRange();
            options.needle=this.session.getTextRange(range);
        }   
        this.$search.set(options);
        
        varranges=this.$search.findAll(this.session);
        if(!ranges.length)
            return0;

        varselection=this.multiSelect;

        if(!additive)
            selection.toSingleRange(ranges[0]);

        for(vari=ranges.length;i--;)
            selection.addRange(ranges[i],true);
        if(range&&selection.rangeList.rangeAtPoint(range.start))
            selection.addRange(range,true);
        
        returnranges.length;
    };
    this.selectMoreLines=function(dir,skip){
        varrange=this.selection.toOrientedRange();
        varisBackwards=range.cursor==range.end;

        varscreenLead=this.session.documentToScreenPosition(range.cursor);
        if(this.selection.$desiredColumn)
            screenLead.column=this.selection.$desiredColumn;

        varlead=this.session.screenToDocumentPosition(screenLead.row+dir,screenLead.column);

        if(!range.isEmpty()){
            varscreenAnchor=this.session.documentToScreenPosition(isBackwards?range.end:range.start);
            varanchor=this.session.screenToDocumentPosition(screenAnchor.row+dir,screenAnchor.column);
        }else{
            varanchor=lead;
        }

        if(isBackwards){
            varnewRange=Range.fromPoints(lead,anchor);
            newRange.cursor=newRange.start;
        }else{
            varnewRange=Range.fromPoints(anchor,lead);
            newRange.cursor=newRange.end;
        }

        newRange.desiredColumn=screenLead.column;
        if(!this.selection.inMultiSelectMode){
            this.selection.addRange(range);
        }else{
            if(skip)
                vartoRemove=range.cursor;
        }

        this.selection.addRange(newRange);
        if(toRemove)
            this.selection.substractPoint(toRemove);
    };
    this.transposeSelections=function(dir){
        varsession=this.session;
        varsel=session.multiSelect;
        varall=sel.ranges;

        for(vari=all.length;i--;){
            varrange=all[i];
            if(range.isEmpty()){
                vartmp=session.getWordRange(range.start.row,range.start.column);
                range.start.row=tmp.start.row;
                range.start.column=tmp.start.column;
                range.end.row=tmp.end.row;
                range.end.column=tmp.end.column;
            }
        }
        sel.mergeOverlappingRanges();

        varwords=[];
        for(vari=all.length;i--;){
            varrange=all[i];
            words.unshift(session.getTextRange(range));
        }

        if(dir<0)
            words.unshift(words.pop());
        else
            words.push(words.shift());

        for(vari=all.length;i--;){
            varrange=all[i];
            vartmp=range.clone();
            session.replace(range,words[i]);
            range.start.row=tmp.start.row;
            range.start.column=tmp.start.column;
        }
    };
    this.selectMore=function(dir,skip,stopAtFirst){
        varsession=this.session;
        varsel=session.multiSelect;

        varrange=sel.toOrientedRange();
        if(range.isEmpty()){
            range=session.getWordRange(range.start.row,range.start.column);
            range.cursor=dir==-1?range.start:range.end;
            this.multiSelect.addRange(range);
            if(stopAtFirst)
                return;
        }
        varneedle=session.getTextRange(range);

        varnewRange=find(session,needle,dir);
        if(newRange){
            newRange.cursor=dir==-1?newRange.start:newRange.end;
            this.session.unfold(newRange);
            this.multiSelect.addRange(newRange);
            this.renderer.scrollCursorIntoView(null,0.5);
        }
        if(skip)
            this.multiSelect.substractPoint(range.cursor);
    };
    this.alignCursors=function(){
        varsession=this.session;
        varsel=session.multiSelect;
        varranges=sel.ranges;
        varrow=-1;
        varsameRowRanges=ranges.filter(function(r){
            if(r.cursor.row==row)
                returntrue;
            row=r.cursor.row;
        });
        
        if(!ranges.length||sameRowRanges.length==ranges.length-1){
            varrange=this.selection.getRange();
            varfr=range.start.row,lr=range.end.row;
            varguessRange=fr==lr;
            if(guessRange){
                varmax=this.session.getLength();
                varline;
                do{
                    line=this.session.getLine(lr);
                }while(/[=:]/.test(line)&&++lr<max);
                do{
                    line=this.session.getLine(fr);
                }while(/[=:]/.test(line)&&--fr>0);
                
                if(fr<0)fr=0;
                if(lr>=max)lr=max-1;
            }
            varlines=this.session.removeFullLines(fr,lr);
            lines=this.$reAlignText(lines,guessRange);
            this.session.insert({row:fr,column:0},lines.join("\n")+"\n");
            if(!guessRange){
                range.start.column=0;
                range.end.column=lines[lines.length-1].length;
            }
            this.selection.setRange(range);
        }else{
            sameRowRanges.forEach(function(r){
                sel.substractPoint(r.cursor);
            });

            varmaxCol=0;
            varminSpace=Infinity;
            varspaceOffsets=ranges.map(function(r){
                varp=r.cursor;
                varline=session.getLine(p.row);
                varspaceOffset=line.substr(p.column).search(/\S/g);
                if(spaceOffset==-1)
                    spaceOffset=0;

                if(p.column>maxCol)
                    maxCol=p.column;
                if(spaceOffset<minSpace)
                    minSpace=spaceOffset;
                returnspaceOffset;
            });
            ranges.forEach(function(r,i){
                varp=r.cursor;
                varl=maxCol-p.column;
                vard=spaceOffsets[i]-minSpace;
                if(l>d)
                    session.insert(p,lang.stringRepeat("",l-d));
                else
                    session.remove(newRange(p.row,p.column,p.row,p.column-l+d));

                r.start.column=r.end.column=maxCol;
                r.start.row=r.end.row=p.row;
                r.cursor=r.end;
            });
            sel.fromOrientedRange(ranges[0]);
            this.renderer.updateCursor();
            this.renderer.updateBackMarkers();
        }
    };

    this.$reAlignText=function(lines,forceLeft){
        varisLeftAligned=true,isRightAligned=true;
        varstartW,textW,endW;

        returnlines.map(function(line){
            varm=line.match(/(\s*)(.*?)(\s*)([=:].*)/);
            if(!m)
                return[line];

            if(startW==null){
                startW=m[1].length;
                textW=m[2].length;
                endW=m[3].length;
                returnm;
            }

            if(startW+textW+endW!=m[1].length+m[2].length+m[3].length)
                isRightAligned=false;
            if(startW!=m[1].length)
                isLeftAligned=false;

            if(startW>m[1].length)
                startW=m[1].length;
            if(textW<m[2].length)
                textW=m[2].length;
            if(endW>m[3].length)
                endW=m[3].length;

            returnm;
        }).map(forceLeft?alignLeft:
            isLeftAligned?isRightAligned?alignRight:alignLeft:unAlign);

        functionspaces(n){
            returnlang.stringRepeat("",n);
        }

        functionalignLeft(m){
            return!m[2]?m[0]:spaces(startW)+m[2]
                +spaces(textW-m[2].length+endW)
                +m[4].replace(/^([=:])\s+/,"$1");
        }
        functionalignRight(m){
            return!m[2]?m[0]:spaces(startW+textW-m[2].length)+m[2]
                +spaces(endW)
                +m[4].replace(/^([=:])\s+/,"$1");
        }
        functionunAlign(m){
            return!m[2]?m[0]:spaces(startW)+m[2]
                +spaces(endW)
                +m[4].replace(/^([=:])\s+/,"$1");
        }
    };
}).call(Editor.prototype);


functionisSamePoint(p1,p2){
    returnp1.row==p2.row&&p1.column==p2.column;
}
exports.onSessionChange=function(e){
    varsession=e.session;
    if(session&&!session.multiSelect){
        session.$selectionMarkers=[];
        session.selection.$initRangeList();
        session.multiSelect=session.selection;
    }
    this.multiSelect=session&&session.multiSelect;

    varoldSession=e.oldSession;
    if(oldSession){
        oldSession.multiSelect.off("addRange",this.$onAddRange);
        oldSession.multiSelect.off("removeRange",this.$onRemoveRange);
        oldSession.multiSelect.off("multiSelect",this.$onMultiSelect);
        oldSession.multiSelect.off("singleSelect",this.$onSingleSelect);
        oldSession.multiSelect.lead.off("change",this.$checkMultiselectChange);
        oldSession.multiSelect.anchor.off("change",this.$checkMultiselectChange);
    }

    if(session){
        session.multiSelect.on("addRange",this.$onAddRange);
        session.multiSelect.on("removeRange",this.$onRemoveRange);
        session.multiSelect.on("multiSelect",this.$onMultiSelect);
        session.multiSelect.on("singleSelect",this.$onSingleSelect);
        session.multiSelect.lead.on("change",this.$checkMultiselectChange);
        session.multiSelect.anchor.on("change",this.$checkMultiselectChange);
    }

    if(session&&this.inMultiSelectMode!=session.selection.inMultiSelectMode){
        if(session.selection.inMultiSelectMode)
            this.$onMultiSelect();
        else
            this.$onSingleSelect();
    }
};
functionMultiSelect(editor){
    if(editor.$multiselectOnSessionChange)
        return;
    editor.$onAddRange=editor.$onAddRange.bind(editor);
    editor.$onRemoveRange=editor.$onRemoveRange.bind(editor);
    editor.$onMultiSelect=editor.$onMultiSelect.bind(editor);
    editor.$onSingleSelect=editor.$onSingleSelect.bind(editor);
    editor.$multiselectOnSessionChange=exports.onSessionChange.bind(editor);
    editor.$checkMultiselectChange=editor.$checkMultiselectChange.bind(editor);

    editor.$multiselectOnSessionChange(editor);
    editor.on("changeSession",editor.$multiselectOnSessionChange);

    editor.on("mousedown",onMouseDown);
    editor.commands.addCommands(commands.defaultCommands);

    addAltCursorListeners(editor);
}

functionaddAltCursorListeners(editor){
    varel=editor.textInput.getElement();
    varaltCursor=false;
    event.addListener(el,"keydown",function(e){
        varaltDown=e.keyCode==18&&!(e.ctrlKey||e.shiftKey||e.metaKey);
        if(editor.$blockSelectEnabled&&altDown){
            if(!altCursor){
                editor.renderer.setMouseCursor("crosshair");
                altCursor=true;
            }
        }elseif(altCursor){
            reset();
        }
    });

    event.addListener(el,"keyup",reset);
    event.addListener(el,"blur",reset);
    functionreset(e){
        if(altCursor){
            editor.renderer.setMouseCursor("");
            altCursor=false;
        }
    }
}

exports.MultiSelect=MultiSelect;


require("./config").defineOptions(Editor.prototype,"editor",{
    enableMultiselect:{
        set:function(val){
            MultiSelect(this);
            if(val){
                this.on("changeSession",this.$multiselectOnSessionChange);
                this.on("mousedown",onMouseDown);
            }else{
                this.off("changeSession",this.$multiselectOnSessionChange);
                this.off("mousedown",onMouseDown);
            }
        },
        value:true
    },
    enableBlockSelect:{
        set:function(val){
            this.$blockSelectEnabled=val;
        },
        value:true
    }
});



});

define("ace/mode/folding/fold_mode",["require","exports","module","ace/range"],function(require,exports,module){
"usestrict";

varRange=require("../../range").Range;

varFoldMode=exports.FoldMode=function(){};

(function(){

    this.foldingStartMarker=null;
    this.foldingStopMarker=null;
    this.getFoldWidget=function(session,foldStyle,row){
        varline=session.getLine(row);
        if(this.foldingStartMarker.test(line))
            return"start";
        if(foldStyle=="markbeginend"
                &&this.foldingStopMarker
                &&this.foldingStopMarker.test(line))
            return"end";
        return"";
    };

    this.getFoldWidgetRange=function(session,foldStyle,row){
        returnnull;
    };

    this.indentationBlock=function(session,row,column){
        varre=/\S/;
        varline=session.getLine(row);
        varstartLevel=line.search(re);
        if(startLevel==-1)
            return;

        varstartColumn=column||line.length;
        varmaxRow=session.getLength();
        varstartRow=row;
        varendRow=row;

        while(++row<maxRow){
            varlevel=session.getLine(row).search(re);

            if(level==-1)
                continue;

            if(level<=startLevel)
                break;

            endRow=row;
        }

        if(endRow>startRow){
            varendColumn=session.getLine(endRow).length;
            returnnewRange(startRow,startColumn,endRow,endColumn);
        }
    };

    this.openingBracketBlock=function(session,bracket,row,column,typeRe){
        varstart={row:row,column:column+1};
        varend=session.$findClosingBracket(bracket,start,typeRe);
        if(!end)
            return;

        varfw=session.foldWidgets[end.row];
        if(fw==null)
            fw=session.getFoldWidget(end.row);

        if(fw=="start"&&end.row>start.row){
            end.row--;
            end.column=session.getLine(end.row).length;
        }
        returnRange.fromPoints(start,end);
    };

    this.closingBracketBlock=function(session,bracket,row,column,typeRe){
        varend={row:row,column:column};
        varstart=session.$findOpeningBracket(bracket,end);

        if(!start)
            return;

        start.column++;
        end.column--;

        return Range.fromPoints(start,end);
    };
}).call(FoldMode.prototype);

});

define("ace/theme/textmate",["require","exports","module","ace/lib/dom"],function(require,exports,module){
"usestrict";

exports.isDark=false;
exports.cssClass="ace-tm";
exports.cssText=".ace-tm.ace_gutter{\
background:#f0f0f0;\
color:#333;\
}\
.ace-tm.ace_print-margin{\
width:1px;\
background:#e8e8e8;\
}\
.ace-tm.ace_fold{\
background-color:#6B72E6;\
}\
.ace-tm{\
background-color:#FFFFFF;\
color:black;\
}\
.ace-tm.ace_cursor{\
color:black;\
}\
.ace-tm.ace_invisible{\
color:rgb(191,191,191);\
}\
.ace-tm.ace_storage,\
.ace-tm.ace_keyword{\
color:blue;\
}\
.ace-tm.ace_constant{\
color:rgb(197,6,11);\
}\
.ace-tm.ace_constant.ace_buildin{\
color:rgb(88,72,246);\
}\
.ace-tm.ace_constant.ace_language{\
color:rgb(88,92,246);\
}\
.ace-tm.ace_constant.ace_library{\
color:rgb(6,150,14);\
}\
.ace-tm.ace_invalid{\
background-color:rgba(255,0,0,0.1);\
color:red;\
}\
.ace-tm.ace_support.ace_function{\
color:rgb(60,76,114);\
}\
.ace-tm.ace_support.ace_constant{\
color:rgb(6,150,14);\
}\
.ace-tm.ace_support.ace_type,\
.ace-tm.ace_support.ace_class{\
color:rgb(109,121,222);\
}\
.ace-tm.ace_keyword.ace_operator{\
color:rgb(104,118,135);\
}\
.ace-tm.ace_string{\
color:rgb(3,106,7);\
}\
.ace-tm.ace_comment{\
color:rgb(76,136,107);\
}\
.ace-tm.ace_comment.ace_doc{\
color:rgb(0,102,255);\
}\
.ace-tm.ace_comment.ace_doc.ace_tag{\
color:rgb(128,159,191);\
}\
.ace-tm.ace_constant.ace_numeric{\
color:rgb(0,0,205);\
}\
.ace-tm.ace_variable{\
color:rgb(49,132,149);\
}\
.ace-tm.ace_xml-pe{\
color:rgb(104,104,91);\
}\
.ace-tm.ace_entity.ace_name.ace_function{\
color:#0000A2;\
}\
.ace-tm.ace_heading{\
color:rgb(12,7,255);\
}\
.ace-tm.ace_list{\
color:rgb(185,6,144);\
}\
.ace-tm.ace_meta.ace_tag{\
color:rgb(0,22,142);\
}\
.ace-tm.ace_string.ace_regex{\
color:rgb(255,0,0)\
}\
.ace-tm.ace_marker-layer.ace_selection{\
background:rgb(181,213,255);\
}\
.ace-tm.ace_multiselect.ace_selection.ace_start{\
box-shadow:003px0pxwhite;\
}\
.ace-tm.ace_marker-layer.ace_step{\
background:rgb(252,255,0);\
}\
.ace-tm.ace_marker-layer.ace_stack{\
background:rgb(164,229,101);\
}\
.ace-tm.ace_marker-layer.ace_bracket{\
margin:-1px00-1px;\
border:1pxsolidrgb(192,192,192);\
}\
.ace-tm.ace_marker-layer.ace_active-line{\
background:rgba(0,0,0,0.07);\
}\
.ace-tm.ace_gutter-active-line{\
background-color:#dcdcdc;\
}\
.ace-tm.ace_marker-layer.ace_selected-word{\
background:rgb(250,250,255);\
border:1pxsolidrgb(200,200,250);\
}\
.ace-tm.ace_indent-guide{\
background:url(\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAACCAYAAACZgbYnAAAAE0lEQVQImWP4////f4bLly//BwAmVgd1/w11/gAAAABJRU5ErkJggg==\")rightrepeat-y;\
}\
";
exports.$id="ace/theme/textmate";

vardom=require("../lib/dom");
dom.importCssString(exports.cssText,exports.cssClass);
});

define("ace/line_widgets",["require","exports","module","ace/lib/oop","ace/lib/dom","ace/range"],function(require,exports,module){
"usestrict";

varoop=require("./lib/oop");
vardom=require("./lib/dom");
varRange=require("./range").Range;


functionLineWidgets(session){
    this.session=session;
    this.session.widgetManager=this;
    this.session.getRowLength=this.getRowLength;
    this.session.$getWidgetScreenLength=this.$getWidgetScreenLength;
    this.updateOnChange=this.updateOnChange.bind(this);
    this.renderWidgets=this.renderWidgets.bind(this);
    this.measureWidgets=this.measureWidgets.bind(this);
    this.session._changedWidgets=[];
    this.$onChangeEditor=this.$onChangeEditor.bind(this);
    
    this.session.on("change",this.updateOnChange);
    this.session.on("changeFold",this.updateOnFold);
    this.session.on("changeEditor",this.$onChangeEditor);
}

(function(){
    this.getRowLength=function(row){
        varh;
        if(this.lineWidgets)
            h=this.lineWidgets[row]&&this.lineWidgets[row].rowCount||0;
        else
            h=0;
        if(!this.$useWrapMode||!this.$wrapData[row]){
            return1+h;
        }else{
            returnthis.$wrapData[row].length+1+h;
        }
    };

    this.$getWidgetScreenLength=function(){
        varscreenRows=0;
        this.lineWidgets.forEach(function(w){
            if(w&&w.rowCount&&!w.hidden)
                screenRows+=w.rowCount;
        });
        returnscreenRows;
    };   
    
    this.$onChangeEditor=function(e){
        this.attach(e.editor);
    };
    
    this.attach=function(editor){
        if(editor &&editor.widgetManager&&editor.widgetManager!=this)
            editor.widgetManager.detach();

        if(this.editor==editor)
            return;

        this.detach();
        this.editor=editor;
        
        if(editor){
            editor.widgetManager=this;
            editor.renderer.on("beforeRender",this.measureWidgets);
            editor.renderer.on("afterRender",this.renderWidgets);
        }
    };
    this.detach=function(e){
        vareditor=this.editor;
        if(!editor)
            return;
        
        this.editor=null;
        editor.widgetManager=null;
        
        editor.renderer.off("beforeRender",this.measureWidgets);
        editor.renderer.off("afterRender",this.renderWidgets);
        varlineWidgets=this.session.lineWidgets;
        lineWidgets&&lineWidgets.forEach(function(w){
            if(w&&w.el&&w.el.parentNode){
                w._inDocument=false;
                w.el.parentNode.removeChild(w.el);
            }
        });
    };

    this.updateOnFold=function(e,session){
        varlineWidgets=session.lineWidgets;
        if(!lineWidgets||!e.action)
            return;
        varfold=e.data;
        varstart=fold.start.row;
        varend=fold.end.row;
        varhide=e.action=="add";
        for(vari=start+1;i<end;i++){
            if(lineWidgets[i])
                lineWidgets[i].hidden=hide;
        }
        if(lineWidgets[end]){
            if(hide){
                if(!lineWidgets[start])
                    lineWidgets[start]=lineWidgets[end];
                else
                    lineWidgets[end].hidden=hide;
            }else{
                if(lineWidgets[start]==lineWidgets[end])
                    lineWidgets[start]=undefined;
                lineWidgets[end].hidden=hide;
            }
        }
    };
    
    this.updateOnChange=function(delta){
        varlineWidgets=this.session.lineWidgets;
        if(!lineWidgets)return;
        
        varstartRow=delta.start.row;
        varlen=delta.end.row-startRow;

        if(len===0){
        }elseif(delta.action=='remove'){
            varremoved=lineWidgets.splice(startRow+1,len);
            removed.forEach(function(w){
                w&&this.removeLineWidget(w);
            },this);
            this.$updateRows();
        }else{
            varargs=newArray(len);
            args.unshift(startRow,0);
            lineWidgets.splice.apply(lineWidgets,args);
            this.$updateRows();
        }
    };
    
    this.$updateRows=function(){
        varlineWidgets=this.session.lineWidgets;
        if(!lineWidgets)return;
        varnoWidgets=true;
        lineWidgets.forEach(function(w,i){
            if(w){
                noWidgets=false;
                w.row=i;
                while(w.$oldWidget){
                    w.$oldWidget.row=i;
                    w=w.$oldWidget;
                }
            }
        });
        if(noWidgets)
            this.session.lineWidgets=null;
    };

    this.addLineWidget=function(w){
        if(!this.session.lineWidgets)
            this.session.lineWidgets=newArray(this.session.getLength());
        
        varold=this.session.lineWidgets[w.row];
        if(old){
            w.$oldWidget=old;
            if(old.el&&old.el.parentNode){
                old.el.parentNode.removeChild(old.el);
                old._inDocument=false;
            }
        }
            
        this.session.lineWidgets[w.row]=w;
        
        w.session=this.session;
        
        varrenderer=this.editor.renderer;
        if(w.html&&!w.el){
            w.el=dom.createElement("div");
            w.el.innerHTML=w.html;
        }
        if(w.el){
            dom.addCssClass(w.el,"ace_lineWidgetContainer");
            w.el.style.position="absolute";
            w.el.style.zIndex=5;
            renderer.container.appendChild(w.el);
            w._inDocument=true;
        }
        
        if(!w.coverGutter){
            w.el.style.zIndex=3;
        }
        if(w.pixelHeight==null){
            w.pixelHeight=w.el.offsetHeight;
        }
        if(w.rowCount==null){
            w.rowCount=w.pixelHeight/renderer.layerConfig.lineHeight;
        }
        
        varfold=this.session.getFoldAt(w.row,0);
        w.$fold=fold;
        if(fold){
            varlineWidgets=this.session.lineWidgets;
            if(w.row==fold.end.row&&!lineWidgets[fold.start.row])
                lineWidgets[fold.start.row]=w;
            else
                w.hidden=true;
        }
            
        this.session._emit("changeFold",{data:{start:{row:w.row}}});
        
        this.$updateRows();
        this.renderWidgets(null,renderer);
        this.onWidgetChanged(w);
        returnw;
    };
    
    this.removeLineWidget=function(w){
        w._inDocument=false;
        w.session=null;
        if(w.el&&w.el.parentNode)
            w.el.parentNode.removeChild(w.el);
        if(w.editor&&w.editor.destroy)try{
            w.editor.destroy();
        }catch(e){}
        if(this.session.lineWidgets){
            varw1=this.session.lineWidgets[w.row];
            if(w1==w){
                this.session.lineWidgets[w.row]=w.$oldWidget;
                if(w.$oldWidget)
                    this.onWidgetChanged(w.$oldWidget);
            }else{
                while(w1){
                    if(w1.$oldWidget==w){
                        w1.$oldWidget=w.$oldWidget;
                        break;
                    }
                    w1=w1.$oldWidget;
                }
            }
        }
        this.session._emit("changeFold",{data:{start:{row:w.row}}});
        this.$updateRows();
    };
    
    this.getWidgetsAtRow=function(row){
        varlineWidgets=this.session.lineWidgets;
        varw=lineWidgets&&lineWidgets[row];
        varlist=[];
        while(w){
            list.push(w);
            w=w.$oldWidget;
        }
        returnlist;
    };
    
    this.onWidgetChanged=function(w){
        this.session._changedWidgets.push(w);
        this.editor&&this.editor.renderer.updateFull();
    };
    
    this.measureWidgets=function(e,renderer){
        varchangedWidgets=this.session._changedWidgets;
        varconfig=renderer.layerConfig;
        
        if(!changedWidgets||!changedWidgets.length)return;
        varmin=Infinity;
        for(vari=0;i<changedWidgets.length;i++){
            varw=changedWidgets[i];
            if(!w||!w.el)continue;
            if(w.session!=this.session)continue;
            if(!w._inDocument){
                if(this.session.lineWidgets[w.row]!=w)
                    continue;
                w._inDocument=true;
                renderer.container.appendChild(w.el);
            }
            
            w.h=w.el.offsetHeight;
            
            if(!w.fixedWidth){
                w.w=w.el.offsetWidth;
                w.screenWidth=Math.ceil(w.w/config.characterWidth);
            }
            
            varrowCount=w.h/config.lineHeight;
            if(w.coverLine){
                rowCount-=this.session.getRowLineCount(w.row);
                if(rowCount<0)
                    rowCount=0;
            }
            if(w.rowCount!=rowCount){
                w.rowCount=rowCount;
                if(w.row<min)
                    min=w.row;
            }
        }
        if(min!=Infinity){
            this.session._emit("changeFold",{data:{start:{row:min}}});
            this.session.lineWidgetWidth=null;
        }
        this.session._changedWidgets=[];
    };
    
    this.renderWidgets=function(e,renderer){
        varconfig=renderer.layerConfig;
        varlineWidgets=this.session.lineWidgets;
        if(!lineWidgets)
            return;
        varfirst=Math.min(this.firstRow,config.firstRow);
        varlast=Math.max(this.lastRow,config.lastRow,lineWidgets.length);
        
        while(first>0&&!lineWidgets[first])
            first--;
        
        this.firstRow=config.firstRow;
        this.lastRow=config.lastRow;

        renderer.$cursorLayer.config=config;
        for(vari=first;i<=last;i++){
            varw=lineWidgets[i];
            if(!w||!w.el)continue;
            if(w.hidden){
                w.el.style.top=-100-(w.pixelHeight||0)+"px";
                continue;
            }
            if(!w._inDocument){
                w._inDocument=true;
                renderer.container.appendChild(w.el);
            }
            vartop=renderer.$cursorLayer.getPixelPosition({row:i,column:0},true).top;
            if(!w.coverLine)
                top+=config.lineHeight*this.session.getRowLineCount(w.row);
            w.el.style.top=top-config.offset+"px";
            
            varleft=w.coverGutter?0:renderer.gutterWidth;
            if(!w.fixedWidth)
                left-=renderer.scrollLeft;
            w.el.style.left=left+"px";
            
            if(w.fullWidth&&w.screenWidth){
                w.el.style.minWidth=config.width+2*config.padding+"px";
            }
            
            if(w.fixedWidth){
                w.el.style.right=renderer.scrollBar.getWidth()+"px";
            }else{
                w.el.style.right="";
            }
        }
    };
    
}).call(LineWidgets.prototype);


exports.LineWidgets=LineWidgets;

});

define("ace/ext/error_marker",["require","exports","module","ace/line_widgets","ace/lib/dom","ace/range"],function(require,exports,module){
"usestrict";
varLineWidgets=require("../line_widgets").LineWidgets;
vardom=require("../lib/dom");
varRange=require("../range").Range;

functionbinarySearch(array,needle,comparator){
    varfirst=0;
    varlast=array.length-1;

    while(first<=last){
        varmid=(first+last)>>1;
        varc=comparator(needle,array[mid]);
        if(c>0)
            first=mid+1;
        elseif(c<0)
            last=mid-1;
        else
            returnmid;
    }
    return-(first+1);
}

functionfindAnnotations(session,row,dir){
    varannotations=session.getAnnotations().sort(Range.comparePoints);
    if(!annotations.length)
        return;
    
    vari=binarySearch(annotations,{row:row,column:-1},Range.comparePoints);
    if(i<0)
        i=-i-1;
    
    if(i>=annotations.length)
        i=dir>0?0:annotations.length-1;
    elseif(i===0&&dir<0)
        i=annotations.length-1;
    
    varannotation=annotations[i];
    if(!annotation||!dir)
        return;

    if(annotation.row===row){
        do{
            annotation=annotations[i+=dir];
        }while(annotation&&annotation.row===row);
        if(!annotation)
            returnannotations.slice();
    }
    
    
    varmatched=[];
    row=annotation.row;
    do{
        matched[dir<0?"unshift":"push"](annotation);
        annotation=annotations[i+=dir];
    }while(annotation&&annotation.row==row);
    returnmatched.length&&matched;
}

exports.showErrorMarker=function(editor,dir){
    varsession=editor.session;
    if(!session.widgetManager){
        session.widgetManager=newLineWidgets(session);
        session.widgetManager.attach(editor);
    }
    
    varpos=editor.getCursorPosition();
    varrow=pos.row;
    varoldWidget=session.widgetManager.getWidgetsAtRow(row).filter(function(w){
        returnw.type=="errorMarker";
    })[0];
    if(oldWidget){
        oldWidget.destroy();
    }else{
        row-=dir;
    }
    varannotations=findAnnotations(session,row,dir);
    vargutterAnno;
    if(annotations){
        varannotation=annotations[0];
        pos.column=(annotation.pos&&typeofannotation.column!="number"
            ?annotation.pos.sc
            :annotation.column)||0;
        pos.row=annotation.row;
        gutterAnno=editor.renderer.$gutterLayer.$annotations[pos.row];
    }elseif(oldWidget){
        return;
    }else{
        gutterAnno={
            text:["Looksgood!"],
            className:"ace_ok"
        };
    }
    editor.session.unfold(pos.row);
    editor.selection.moveToPosition(pos);
    
    varw={
        row:pos.row,
        fixedWidth:true,
        coverGutter:true,
        el:dom.createElement("div"),
        type:"errorMarker"
    };
    varel=w.el.appendChild(dom.createElement("div"));
    vararrow=w.el.appendChild(dom.createElement("div"));
    arrow.className="error_widget_arrow"+gutterAnno.className;
    
    varleft=editor.renderer.$cursorLayer
        .getPixelPosition(pos).left;
    arrow.style.left=left+editor.renderer.gutterWidth-5+"px";
    
    w.el.className="error_widget_wrapper";
    el.className="error_widget"+gutterAnno.className;
    el.innerHTML=gutterAnno.text.join("<br>");
    
    el.appendChild(dom.createElement("div"));
    
    varkb=function(_,hashId,keyString){
        if(hashId===0&&(keyString==="esc"||keyString==="return")){
            w.destroy();
            return{command:"null"};
        }
    };
    
    w.destroy=function(){
        if(editor.$mouseHandler.isMousePressed)
            return;
        editor.keyBinding.removeKeyboardHandler(kb);
        session.widgetManager.removeLineWidget(w);
        editor.off("changeSelection",w.destroy);
        editor.off("changeSession",w.destroy);
        editor.off("mouseup",w.destroy);
        editor.off("change",w.destroy);
    };
    
    editor.keyBinding.addKeyboardHandler(kb);
    editor.on("changeSelection",w.destroy);
    editor.on("changeSession",w.destroy);
    editor.on("mouseup",w.destroy);
    editor.on("change",w.destroy);
    
    editor.session.widgetManager.addLineWidget(w);
    
    w.el.onmousedown=editor.focus.bind(editor);
    
    editor.renderer.scrollCursorIntoView(null,0.5,{bottom:w.el.offsetHeight});
};


dom.importCssString("\
    .error_widget_wrapper{\
        background:inherit;\
        color:inherit;\
        border:none\
    }\
    .error_widget{\
        border-top:solid2px;\
        border-bottom:solid2px;\
        margin:5px0;\
        padding:10px40px;\
        white-space:pre-wrap;\
    }\
    .error_widget.ace_error,.error_widget_arrow.ace_error{\
        border-color:#ff5a5a\
    }\
    .error_widget.ace_warning,.error_widget_arrow.ace_warning{\
        border-color:#F1D817\
    }\
    .error_widget.ace_info,.error_widget_arrow.ace_info{\
        border-color:#5a5a5a\
    }\
    .error_widget.ace_ok,.error_widget_arrow.ace_ok{\
        border-color:#5aaa5a\
    }\
    .error_widget_arrow{\
        position:absolute;\
        border:solid5px;\
        border-top-color:transparent!important;\
        border-right-color:transparent!important;\
        border-left-color:transparent!important;\
        top:-5px;\
    }\
","");

});

define("ace/ace",["require","exports","module","ace/lib/fixoldbrowsers","ace/lib/dom","ace/lib/event","ace/range","ace/editor","ace/edit_session","ace/undomanager","ace/virtual_renderer","ace/worker/worker_client","ace/keyboard/hash_handler","ace/placeholder","ace/multi_select","ace/mode/folding/fold_mode","ace/theme/textmate","ace/ext/error_marker","ace/config"],function(require,exports,module){
"usestrict";

require("./lib/fixoldbrowsers");

vardom=require("./lib/dom");
varevent=require("./lib/event");

varRange=require("./range").Range;
varEditor=require("./editor").Editor;
varEditSession=require("./edit_session").EditSession;
varUndoManager=require("./undomanager").UndoManager;
varRenderer=require("./virtual_renderer").VirtualRenderer;
require("./worker/worker_client");
require("./keyboard/hash_handler");
require("./placeholder");
require("./multi_select");
require("./mode/folding/fold_mode");
require("./theme/textmate");
require("./ext/error_marker");

exports.config=require("./config");
exports.require=require;

if(typeofdefine==="function")
    exports.define=define;
exports.edit=function(el,options){
    if(typeofel=="string"){
        var_id=el;
        el=document.getElementById(_id);
        if(!el)
            thrownewError("ace.editcan'tfinddiv#"+_id);
    }

    if(el&&el.env&&el.env.editorinstanceofEditor)
        returnel.env.editor;

    varvalue="";
    if(el&&/input|textarea/i.test(el.tagName)){
        varoldNode=el;
        value=oldNode.value;
        el=dom.createElement("pre");
        oldNode.parentNode.replaceChild(el,oldNode);
    }elseif(el){
        value=el.textContent;
        el.innerHTML="";
    }

    vardoc=exports.createEditSession(value);

    vareditor=newEditor(newRenderer(el),doc,options);

    varenv={
        document:doc,
        editor:editor,
        onResize:editor.resize.bind(editor,null)
    };
    if(oldNode)env.textarea=oldNode;
    event.addListener(window,"resize",env.onResize);
    editor.on("destroy",function(){
        event.removeListener(window,"resize",env.onResize);
        env.editor.container.env=null;//preventmemoryleakonoldie
    });
    editor.container.env=editor.env=env;
    returneditor;
};
exports.createEditSession=function(text,mode){
    vardoc=newEditSession(text,mode);
    doc.setUndoManager(newUndoManager());
    returndoc;
};
exports.Range=Range;
exports.EditSession=EditSession;
exports.UndoManager=UndoManager;
exports.VirtualRenderer=Renderer;
exports.version="1.3.1";
});
            (function(){
                window.require(["ace/ace"],function(a){
                    if(a){
                        a.config.init(true);
                        a.define=window.define;
                    }
                    if(!window.ace)
                        window.ace=a;
                    for(varkeyina)if(a.hasOwnProperty(key))
                        window.ace[key]=a[key];
                });
            })();
         