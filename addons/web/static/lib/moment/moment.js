//!moment.js
//!version:2.17.1
//!authors:TimWood,IskrenChernev,Moment.jscontributors
//!license:MIT
//!momentjs.com

;(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    global.moment=factory()
}(this,(function(){'usestrict';

varhookCallback;

functionhooks(){
    returnhookCallback.apply(null,arguments);
}

//Thisisdonetoregisterthemethodcalledwithmoment()
//withoutcreatingcirculardependencies.
functionsetHookCallback(callback){
    hookCallback=callback;
}

functionisArray(input){
    returninputinstanceofArray||Object.prototype.toString.call(input)==='[objectArray]';
}

functionisObject(input){
    //IE8willtreatundefinedandnullasobjectifitwasn'tfor
    //input!=null
    returninput!=null&&Object.prototype.toString.call(input)==='[objectObject]';
}

functionisObjectEmpty(obj){
    vark;
    for(kinobj){
        //evenifitsnotownpropertyI'dstillcallitnon-empty
        returnfalse;
    }
    returntrue;
}

functionisNumber(input){
    returntypeofinput==='number'||Object.prototype.toString.call(input)==='[objectNumber]';
}

functionisDate(input){
    returninputinstanceofDate||Object.prototype.toString.call(input)==='[objectDate]';
}

functionmap(arr,fn){
    varres=[],i;
    for(i=0;i<arr.length;++i){
        res.push(fn(arr[i],i));
    }
    returnres;
}

functionhasOwnProp(a,b){
    returnObject.prototype.hasOwnProperty.call(a,b);
}

functionextend(a,b){
    for(variinb){
        if(hasOwnProp(b,i)){
            a[i]=b[i];
        }
    }

    if(hasOwnProp(b,'toString')){
        a.toString=b.toString;
    }

    if(hasOwnProp(b,'valueOf')){
        a.valueOf=b.valueOf;
    }

    returna;
}

functioncreateUTC(input,format,locale,strict){
    returncreateLocalOrUTC(input,format,locale,strict,true).utc();
}

functiondefaultParsingFlags(){
    //Weneedtodeepclonethisobject.
    return{
        empty          :false,
        unusedTokens   :[],
        unusedInput    :[],
        overflow       :-2,
        charsLeftOver  :0,
        nullInput      :false,
        invalidMonth   :null,
        invalidFormat  :false,
        userInvalidated:false,
        iso            :false,
        parsedDateParts:[],
        meridiem       :null
    };
}

functiongetParsingFlags(m){
    if(m._pf==null){
        m._pf=defaultParsingFlags();
    }
    returnm._pf;
}

varsome;
if(Array.prototype.some){
    some=Array.prototype.some;
}else{
    some=function(fun){
        vart=Object(this);
        varlen=t.length>>>0;

        for(vari=0;i<len;i++){
            if(iint&&fun.call(this,t[i],i,t)){
                returntrue;
            }
        }

        returnfalse;
    };
}

varsome$1=some;

functionisValid(m){
    if(m._isValid==null){
        varflags=getParsingFlags(m);
        varparsedParts=some$1.call(flags.parsedDateParts,function(i){
            returni!=null;
        });
        varisNowValid=!isNaN(m._d.getTime())&&
            flags.overflow<0&&
            !flags.empty&&
            !flags.invalidMonth&&
            !flags.invalidWeekday&&
            !flags.nullInput&&
            !flags.invalidFormat&&
            !flags.userInvalidated&&
            (!flags.meridiem||(flags.meridiem&&parsedParts));

        if(m._strict){
            isNowValid=isNowValid&&
                flags.charsLeftOver===0&&
                flags.unusedTokens.length===0&&
                flags.bigHour===undefined;
        }

        if(Object.isFrozen==null||!Object.isFrozen(m)){
            m._isValid=isNowValid;
        }
        else{
            returnisNowValid;
        }
    }
    returnm._isValid;
}

functioncreateInvalid(flags){
    varm=createUTC(NaN);
    if(flags!=null){
        extend(getParsingFlags(m),flags);
    }
    else{
        getParsingFlags(m).userInvalidated=true;
    }

    returnm;
}

functionisUndefined(input){
    returninput===void0;
}

//Pluginsthataddpropertiesshouldalsoaddthekeyhere(nullvalue),
//sowecanproperlycloneourselves.
varmomentProperties=hooks.momentProperties=[];

functioncopyConfig(to,from){
    vari,prop,val;

    if(!isUndefined(from._isAMomentObject)){
        to._isAMomentObject=from._isAMomentObject;
    }
    if(!isUndefined(from._i)){
        to._i=from._i;
    }
    if(!isUndefined(from._f)){
        to._f=from._f;
    }
    if(!isUndefined(from._l)){
        to._l=from._l;
    }
    if(!isUndefined(from._strict)){
        to._strict=from._strict;
    }
    if(!isUndefined(from._tzm)){
        to._tzm=from._tzm;
    }
    if(!isUndefined(from._isUTC)){
        to._isUTC=from._isUTC;
    }
    if(!isUndefined(from._offset)){
        to._offset=from._offset;
    }
    if(!isUndefined(from._pf)){
        to._pf=getParsingFlags(from);
    }
    if(!isUndefined(from._locale)){
        to._locale=from._locale;
    }

    if(momentProperties.length>0){
        for(iinmomentProperties){
            prop=momentProperties[i];
            val=from[prop];
            if(!isUndefined(val)){
                to[prop]=val;
            }
        }
    }

    returnto;
}

varupdateInProgress=false;

//Momentprototypeobject
functionMoment(config){
    copyConfig(this,config);
    this._d=newDate(config._d!=null?config._d.getTime():NaN);
    if(!this.isValid()){
        this._d=newDate(NaN);
    }
    //PreventinfiniteloopincaseupdateOffsetcreatesnewmoment
    //objects.
    if(updateInProgress===false){
        updateInProgress=true;
        hooks.updateOffset(this);
        updateInProgress=false;
    }
}

functionisMoment(obj){
    returnobjinstanceofMoment||(obj!=null&&obj._isAMomentObject!=null);
}

functionabsFloor(number){
    if(number<0){
        //-0->0
        returnMath.ceil(number)||0;
    }else{
        returnMath.floor(number);
    }
}

functiontoInt(argumentForCoercion){
    varcoercedNumber=+argumentForCoercion,
        value=0;

    if(coercedNumber!==0&&isFinite(coercedNumber)){
        value=absFloor(coercedNumber);
    }

    returnvalue;
}

//comparetwoarrays,returnthenumberofdifferences
functioncompareArrays(array1,array2,dontConvert){
    varlen=Math.min(array1.length,array2.length),
        lengthDiff=Math.abs(array1.length-array2.length),
        diffs=0,
        i;
    for(i=0;i<len;i++){
        if((dontConvert&&array1[i]!==array2[i])||
            (!dontConvert&&toInt(array1[i])!==toInt(array2[i]))){
            diffs++;
        }
    }
    returndiffs+lengthDiff;
}

functionwarn(msg){
    if(hooks.suppressDeprecationWarnings===false&&
            (typeofconsole!== 'undefined')&&console.warn){
        console.warn('Deprecationwarning:'+msg);
    }
}

functiondeprecate(msg,fn){
    varfirstTime=true;

    returnextend(function(){
        if(hooks.deprecationHandler!=null){
            hooks.deprecationHandler(null,msg);
        }
        if(firstTime){
            varargs=[];
            vararg;
            for(vari=0;i<arguments.length;i++){
                arg='';
                if(typeofarguments[i]==='object'){
                    arg+='\n['+i+']';
                    for(varkeyinarguments[0]){
                        arg+=key+':'+arguments[0][key]+',';
                    }
                    arg=arg.slice(0,-2);//Removetrailingcommaandspace
                }else{
                    arg=arguments[i];
                }
                args.push(arg);
            }
            warn(msg+'\nArguments:'+Array.prototype.slice.call(args).join('')+'\n'+(newError()).stack);
            firstTime=false;
        }
        returnfn.apply(this,arguments);
    },fn);
}

vardeprecations={};

functiondeprecateSimple(name,msg){
    if(hooks.deprecationHandler!=null){
        hooks.deprecationHandler(name,msg);
    }
    if(!deprecations[name]){
        warn(msg);
        deprecations[name]=true;
    }
}

hooks.suppressDeprecationWarnings=false;
hooks.deprecationHandler=null;

functionisFunction(input){
    returninputinstanceofFunction||Object.prototype.toString.call(input)==='[objectFunction]';
}

functionset(config){
    varprop,i;
    for(iinconfig){
        prop=config[i];
        if(isFunction(prop)){
            this[i]=prop;
        }else{
            this['_'+i]=prop;
        }
    }
    this._config=config;
    //Lenientordinalparsingacceptsjustanumberinadditionto
    //number+(possibly)stuffcomingfrom_ordinalParseLenient.
    this._ordinalParseLenient=newRegExp(this._ordinalParse.source+'|'+(/\d{1,2}/).source);
}

functionmergeConfigs(parentConfig,childConfig){
    varres=extend({},parentConfig),prop;
    for(propinchildConfig){
        if(hasOwnProp(childConfig,prop)){
            if(isObject(parentConfig[prop])&&isObject(childConfig[prop])){
                res[prop]={};
                extend(res[prop],parentConfig[prop]);
                extend(res[prop],childConfig[prop]);
            }elseif(childConfig[prop]!=null){
                res[prop]=childConfig[prop];
            }else{
                deleteres[prop];
            }
        }
    }
    for(propinparentConfig){
        if(hasOwnProp(parentConfig,prop)&&
                !hasOwnProp(childConfig,prop)&&
                isObject(parentConfig[prop])){
            //makesurechangestopropertiesdon'tmodifyparentconfig
            res[prop]=extend({},res[prop]);
        }
    }
    returnres;
}

functionLocale(config){
    if(config!=null){
        this.set(config);
    }
}

varkeys;

if(Object.keys){
    keys=Object.keys;
}else{
    keys=function(obj){
        vari,res=[];
        for(iinobj){
            if(hasOwnProp(obj,i)){
                res.push(i);
            }
        }
        returnres;
    };
}

varkeys$1=keys;

vardefaultCalendar={
    sameDay:'[Todayat]LT',
    nextDay:'[Tomorrowat]LT',
    nextWeek:'dddd[at]LT',
    lastDay:'[Yesterdayat]LT',
    lastWeek:'[Last]dddd[at]LT',
    sameElse:'L'
};

functioncalendar(key,mom,now){
    varoutput=this._calendar[key]||this._calendar['sameElse'];
    returnisFunction(output)?output.call(mom,now):output;
}

vardefaultLongDateFormat={
    LTS :'h:mm:ssA',
    LT  :'h:mmA',
    L   :'MM/DD/YYYY',
    LL  :'MMMMD,YYYY',
    LLL :'MMMMD,YYYYh:mmA',
    LLLL:'dddd,MMMMD,YYYYh:mmA'
};

functionlongDateFormat(key){
    varformat=this._longDateFormat[key],
        formatUpper=this._longDateFormat[key.toUpperCase()];

    if(format||!formatUpper){
        returnformat;
    }

    this._longDateFormat[key]=formatUpper.replace(/MMMM|MM|DD|dddd/g,function(val){
        returnval.slice(1);
    });

    returnthis._longDateFormat[key];
}

vardefaultInvalidDate='Invaliddate';

functioninvalidDate(){
    returnthis._invalidDate;
}

vardefaultOrdinal='%d';
vardefaultOrdinalParse=/\d{1,2}/;

functionordinal(number){
    returnthis._ordinal.replace('%d',number);
}

vardefaultRelativeTime={
    future:'in%s',
    past  :'%sago',
    s :'afewseconds',
    m :'aminute',
    mm:'%dminutes',
    h :'anhour',
    hh:'%dhours',
    d :'aday',
    dd:'%ddays',
    M :'amonth',
    MM:'%dmonths',
    y :'ayear',
    yy:'%dyears'
};

functionrelativeTime(number,withoutSuffix,string,isFuture){
    varoutput=this._relativeTime[string];
    return(isFunction(output))?
        output(number,withoutSuffix,string,isFuture):
        output.replace(/%d/i,number);
}

functionpastFuture(diff,output){
    varformat=this._relativeTime[diff>0?'future':'past'];
    returnisFunction(format)?format(output):format.replace(/%s/i,output);
}

varaliases={};

functionaddUnitAlias(unit,shorthand){
    varlowerCase=unit.toLowerCase();
    aliases[lowerCase]=aliases[lowerCase+'s']=aliases[shorthand]=unit;
}

functionnormalizeUnits(units){
    returntypeofunits==='string'?aliases[units]||aliases[units.toLowerCase()]:undefined;
}

functionnormalizeObjectUnits(inputObject){
    varnormalizedInput={},
        normalizedProp,
        prop;

    for(propininputObject){
        if(hasOwnProp(inputObject,prop)){
            normalizedProp=normalizeUnits(prop);
            if(normalizedProp){
                normalizedInput[normalizedProp]=inputObject[prop];
            }
        }
    }

    returnnormalizedInput;
}

varpriorities={};

functionaddUnitPriority(unit,priority){
    priorities[unit]=priority;
}

functiongetPrioritizedUnits(unitsObj){
    varunits=[];
    for(varuinunitsObj){
        units.push({unit:u,priority:priorities[u]});
    }
    units.sort(function(a,b){
        returna.priority-b.priority;
    });
    returnunits;
}

functionmakeGetSet(unit,keepTime){
    returnfunction(value){
        if(value!=null){
            set$1(this,unit,value);
            hooks.updateOffset(this,keepTime);
            returnthis;
        }else{
            returnget(this,unit);
        }
    };
}

functionget(mom,unit){
    returnmom.isValid()?
        mom._d['get'+(mom._isUTC?'UTC':'')+unit]():NaN;
}

functionset$1(mom,unit,value){
    if(mom.isValid()){
        mom._d['set'+(mom._isUTC?'UTC':'')+unit](value);
    }
}

//MOMENTS

functionstringGet(units){
    units=normalizeUnits(units);
    if(isFunction(this[units])){
        returnthis[units]();
    }
    returnthis;
}


functionstringSet(units,value){
    if(typeofunits==='object'){
        units=normalizeObjectUnits(units);
        varprioritized=getPrioritizedUnits(units);
        for(vari=0;i<prioritized.length;i++){
            this[prioritized[i].unit](units[prioritized[i].unit]);
        }
    }else{
        units=normalizeUnits(units);
        if(isFunction(this[units])){
            returnthis[units](value);
        }
    }
    returnthis;
}

functionzeroFill(number,targetLength,forceSign){
    varabsNumber=''+Math.abs(number),
        zerosToFill=targetLength-absNumber.length,
        sign=number>=0;
    return(sign?(forceSign?'+':''):'-')+
        Math.pow(10,Math.max(0,zerosToFill)).toString().substr(1)+absNumber;
}

varformattingTokens=/(\[[^\[]*\])|(\\)?([Hh]mm(ss)?|Mo|MM?M?M?|Do|DDDo|DD?D?D?|ddd?d?|do?|w[o|w]?|W[o|W]?|Qo?|YYYYYY|YYYYY|YYYY|YY|gg(ggg?)?|GG(GGG?)?|e|E|a|A|hh?|HH?|kk?|mm?|ss?|S{1,9}|x|X|zz?|ZZ?|.)/g;

varlocalFormattingTokens=/(\[[^\[]*\])|(\\)?(LTS|LT|LL?L?L?|l{1,4})/g;

varformatFunctions={};

varformatTokenFunctions={};

//token:   'M'
//padded:  ['MM',2]
//ordinal: 'Mo'
//callback:function(){this.month()+1}
functionaddFormatToken(token,padded,ordinal,callback){
    varfunc=callback;
    if(typeofcallback==='string'){
        func=function(){
            returnthis[callback]();
        };
    }
    if(token){
        formatTokenFunctions[token]=func;
    }
    if(padded){
        formatTokenFunctions[padded[0]]=function(){
            returnzeroFill(func.apply(this,arguments),padded[1],padded[2]);
        };
    }
    if(ordinal){
        formatTokenFunctions[ordinal]=function(){
            returnthis.localeData().ordinal(func.apply(this,arguments),token);
        };
    }
}

functionremoveFormattingTokens(input){
    if(input.match(/\[[\s\S]/)){
        returninput.replace(/^\[|\]$/g,'');
    }
    returninput.replace(/\\/g,'');
}

functionmakeFormatFunction(format){
    vararray=format.match(formattingTokens),i,length;

    for(i=0,length=array.length;i<length;i++){
        if(formatTokenFunctions[array[i]]){
            array[i]=formatTokenFunctions[array[i]];
        }else{
            array[i]=removeFormattingTokens(array[i]);
        }
    }

    returnfunction(mom){
        varoutput='',i;
        for(i=0;i<length;i++){
            output+=array[i]instanceofFunction?array[i].call(mom,format):array[i];
        }
        returnoutput;
    };
}

//formatdateusingnativedateobject
functionformatMoment(m,format){
    if(!m.isValid()){
        returnm.localeData().invalidDate();
    }

    format=expandFormat(format,m.localeData());
    formatFunctions[format]=formatFunctions[format]||makeFormatFunction(format);

    returnformatFunctions[format](m);
}

functionexpandFormat(format,locale){
    vari=5;

    functionreplaceLongDateFormatTokens(input){
        returnlocale.longDateFormat(input)||input;
    }

    localFormattingTokens.lastIndex=0;
    while(i>=0&&localFormattingTokens.test(format)){
        format=format.replace(localFormattingTokens,replaceLongDateFormatTokens);
        localFormattingTokens.lastIndex=0;
        i-=1;
    }

    returnformat;
}

varmatch1        =/\d/;           //      0-9
varmatch2        =/\d\d/;         //     00-99
varmatch3        =/\d{3}/;        //    000-999
varmatch4        =/\d{4}/;        //   0000-9999
varmatch6        =/[+-]?\d{6}/;   //-999999-999999
varmatch1to2     =/\d\d?/;        //      0-99
varmatch3to4     =/\d\d\d\d?/;    //    999-9999
varmatch5to6     =/\d\d\d\d\d\d?/;//  99999-999999
varmatch1to3     =/\d{1,3}/;      //      0-999
varmatch1to4     =/\d{1,4}/;      //      0-9999
varmatch1to6     =/[+-]?\d{1,6}/; //-999999-999999

varmatchUnsigned =/\d+/;          //      0-inf
varmatchSigned   =/[+-]?\d+/;     //   -inf-inf

varmatchOffset   =/Z|[+-]\d\d:?\d\d/gi;//+00:00-00:00+0000-0000orZ
varmatchShortOffset=/Z|[+-]\d\d(?::?\d\d)?/gi;//+00-00+00:00-00:00+0000-0000orZ

varmatchTimestamp=/[+-]?\d+(\.\d{1,3})?/;//123456789123456789.123

//anyword(ortwo)charactersornumbersincludingtwo/threewordmonthinarabic.
//includesscottishgaelictwowordandhyphenatedmonths
varmatchWord=/[0-9]*['a-z\u00A0-\u05FF\u0700-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]+|[\u0600-\u06FF\/]+(\s*?[\u0600-\u06FF]+){1,2}/i;


varregexes={};

functionaddRegexToken(token,regex,strictRegex){
    regexes[token]=isFunction(regex)?regex:function(isStrict,localeData){
        return(isStrict&&strictRegex)?strictRegex:regex;
    };
}

functiongetParseRegexForToken(token,config){
    if(!hasOwnProp(regexes,token)){
        returnnewRegExp(unescapeFormat(token));
    }

    returnregexes[token](config._strict,config._locale);
}

//Codefromhttp://stackoverflow.com/questions/3561493/is-there-a-regexp-escape-function-in-javascript
functionunescapeFormat(s){
    returnregexEscape(s.replace('\\','').replace(/\\(\[)|\\(\])|\[([^\]\[]*)\]|\\(.)/g,function(matched,p1,p2,p3,p4){
        returnp1||p2||p3||p4;
    }));
}

functionregexEscape(s){
    returns.replace(/[-\/\\^$*+?.()|[\]{}]/g,'\\$&');
}

vartokens={};

functionaddParseToken(token,callback){
    vari,func=callback;
    if(typeoftoken==='string'){
        token=[token];
    }
    if(isNumber(callback)){
        func=function(input,array){
            array[callback]=toInt(input);
        };
    }
    for(i=0;i<token.length;i++){
        tokens[token[i]]=func;
    }
}

functionaddWeekParseToken(token,callback){
    addParseToken(token,function(input,array,config,token){
        config._w=config._w||{};
        callback(input,config._w,config,token);
    });
}

functionaddTimeToArrayFromToken(token,input,config){
    if(input!=null&&hasOwnProp(tokens,token)){
        tokens[token](input,config._a,config,token);
    }
}

varYEAR=0;
varMONTH=1;
varDATE=2;
varHOUR=3;
varMINUTE=4;
varSECOND=5;
varMILLISECOND=6;
varWEEK=7;
varWEEKDAY=8;

varindexOf;

if(Array.prototype.indexOf){
    indexOf=Array.prototype.indexOf;
}else{
    indexOf=function(o){
        //Iknow
        vari;
        for(i=0;i<this.length;++i){
            if(this[i]===o){
                returni;
            }
        }
        return-1;
    };
}

varindexOf$1=indexOf;

functiondaysInMonth(year,month){
    returnnewDate(Date.UTC(year,month+1,0)).getUTCDate();
}

//FORMATTING

addFormatToken('M',['MM',2],'Mo',function(){
    returnthis.month()+1;
});

addFormatToken('MMM',0,0,function(format){
    returnthis.localeData().monthsShort(this,format);
});

addFormatToken('MMMM',0,0,function(format){
    returnthis.localeData().months(this,format);
});

//ALIASES

addUnitAlias('month','M');

//PRIORITY

addUnitPriority('month',8);

//PARSING

addRegexToken('M',   match1to2);
addRegexToken('MM',  match1to2,match2);
addRegexToken('MMM', function(isStrict,locale){
    returnlocale.monthsShortRegex(isStrict);
});
addRegexToken('MMMM',function(isStrict,locale){
    returnlocale.monthsRegex(isStrict);
});

addParseToken(['M','MM'],function(input,array){
    array[MONTH]=toInt(input)-1;
});

addParseToken(['MMM','MMMM'],function(input,array,config,token){
    varmonth=config._locale.monthsParse(input,token,config._strict);
    //ifwedidn'tfindamonthname,markthedateasinvalid.
    if(month!=null){
        array[MONTH]=month;
    }else{
        getParsingFlags(config).invalidMonth=input;
    }
});

//LOCALES

varMONTHS_IN_FORMAT=/D[oD]?(\[[^\[\]]*\]|\s)+MMMM?/;
vardefaultLocaleMonths='January_February_March_April_May_June_July_August_September_October_November_December'.split('_');
functionlocaleMonths(m,format){
    if(!m){
        returnthis._months;
    }
    returnisArray(this._months)?this._months[m.month()]:
        this._months[(this._months.isFormat||MONTHS_IN_FORMAT).test(format)?'format':'standalone'][m.month()];
}

vardefaultLocaleMonthsShort='Jan_Feb_Mar_Apr_May_Jun_Jul_Aug_Sep_Oct_Nov_Dec'.split('_');
functionlocaleMonthsShort(m,format){
    if(!m){
        returnthis._monthsShort;
    }
    returnisArray(this._monthsShort)?this._monthsShort[m.month()]:
        this._monthsShort[MONTHS_IN_FORMAT.test(format)?'format':'standalone'][m.month()];
}

functionhandleStrictParse(monthName,format,strict){
    vari,ii,mom,llc=monthName.toLocaleLowerCase();
    if(!this._monthsParse){
        //thisisnotused
        this._monthsParse=[];
        this._longMonthsParse=[];
        this._shortMonthsParse=[];
        for(i=0;i<12;++i){
            mom=createUTC([2000,i]);
            this._shortMonthsParse[i]=this.monthsShort(mom,'').toLocaleLowerCase();
            this._longMonthsParse[i]=this.months(mom,'').toLocaleLowerCase();
        }
    }

    if(strict){
        if(format==='MMM'){
            ii=indexOf$1.call(this._shortMonthsParse,llc);
            returnii!==-1?ii:null;
        }else{
            ii=indexOf$1.call(this._longMonthsParse,llc);
            returnii!==-1?ii:null;
        }
    }else{
        if(format==='MMM'){
            ii=indexOf$1.call(this._shortMonthsParse,llc);
            if(ii!==-1){
                returnii;
            }
            ii=indexOf$1.call(this._longMonthsParse,llc);
            returnii!==-1?ii:null;
        }else{
            ii=indexOf$1.call(this._longMonthsParse,llc);
            if(ii!==-1){
                returnii;
            }
            ii=indexOf$1.call(this._shortMonthsParse,llc);
            returnii!==-1?ii:null;
        }
    }
}

functionlocaleMonthsParse(monthName,format,strict){
    vari,mom,regex;

    if(this._monthsParseExact){
        returnhandleStrictParse.call(this,monthName,format,strict);
    }

    if(!this._monthsParse){
        this._monthsParse=[];
        this._longMonthsParse=[];
        this._shortMonthsParse=[];
    }

    //TODO:addsorting
    //Sortingmakessureifonemonth(orabbr)isaprefixofanother
    //seesortingincomputeMonthsParse
    for(i=0;i<12;i++){
        //maketheregexifwedon'thaveitalready
        mom=createUTC([2000,i]);
        if(strict&&!this._longMonthsParse[i]){
            this._longMonthsParse[i]=newRegExp('^'+this.months(mom,'').replace('.','')+'$','i');
            this._shortMonthsParse[i]=newRegExp('^'+this.monthsShort(mom,'').replace('.','')+'$','i');
        }
        if(!strict&&!this._monthsParse[i]){
            regex='^'+this.months(mom,'')+'|^'+this.monthsShort(mom,'');
            this._monthsParse[i]=newRegExp(regex.replace('.',''),'i');
        }
        //testtheregex
        if(strict&&format==='MMMM'&&this._longMonthsParse[i].test(monthName)){
            returni;
        }elseif(strict&&format==='MMM'&&this._shortMonthsParse[i].test(monthName)){
            returni;
        }elseif(!strict&&this._monthsParse[i].test(monthName)){
            returni;
        }
    }
}

//MOMENTS

functionsetMonth(mom,value){
    vardayOfMonth;

    if(!mom.isValid()){
        //Noop
        returnmom;
    }

    if(typeofvalue==='string'){
        if(/^\d+$/.test(value)){
            value=toInt(value);
        }else{
            value=mom.localeData().monthsParse(value);
            //TODO:Anothersilentfailure?
            if(!isNumber(value)){
                returnmom;
            }
        }
    }

    dayOfMonth=Math.min(mom.date(),daysInMonth(mom.year(),value));
    mom._d['set'+(mom._isUTC?'UTC':'')+'Month'](value,dayOfMonth);
    returnmom;
}

functiongetSetMonth(value){
    if(value!=null){
        setMonth(this,value);
        hooks.updateOffset(this,true);
        returnthis;
    }else{
        returnget(this,'Month');
    }
}

functiongetDaysInMonth(){
    returndaysInMonth(this.year(),this.month());
}

vardefaultMonthsShortRegex=matchWord;
functionmonthsShortRegex(isStrict){
    if(this._monthsParseExact){
        if(!hasOwnProp(this,'_monthsRegex')){
            computeMonthsParse.call(this);
        }
        if(isStrict){
            returnthis._monthsShortStrictRegex;
        }else{
            returnthis._monthsShortRegex;
        }
    }else{
        if(!hasOwnProp(this,'_monthsShortRegex')){
            this._monthsShortRegex=defaultMonthsShortRegex;
        }
        returnthis._monthsShortStrictRegex&&isStrict?
            this._monthsShortStrictRegex:this._monthsShortRegex;
    }
}

vardefaultMonthsRegex=matchWord;
functionmonthsRegex(isStrict){
    if(this._monthsParseExact){
        if(!hasOwnProp(this,'_monthsRegex')){
            computeMonthsParse.call(this);
        }
        if(isStrict){
            returnthis._monthsStrictRegex;
        }else{
            returnthis._monthsRegex;
        }
    }else{
        if(!hasOwnProp(this,'_monthsRegex')){
            this._monthsRegex=defaultMonthsRegex;
        }
        returnthis._monthsStrictRegex&&isStrict?
            this._monthsStrictRegex:this._monthsRegex;
    }
}

functioncomputeMonthsParse(){
    functioncmpLenRev(a,b){
        returnb.length-a.length;
    }

    varshortPieces=[],longPieces=[],mixedPieces=[],
        i,mom;
    for(i=0;i<12;i++){
        //maketheregexifwedon'thaveitalready
        mom=createUTC([2000,i]);
        shortPieces.push(this.monthsShort(mom,''));
        longPieces.push(this.months(mom,''));
        mixedPieces.push(this.months(mom,''));
        mixedPieces.push(this.monthsShort(mom,''));
    }
    //Sortingmakessureifonemonth(orabbr)isaprefixofanotherit
    //willmatchthelongerpiece.
    shortPieces.sort(cmpLenRev);
    longPieces.sort(cmpLenRev);
    mixedPieces.sort(cmpLenRev);
    for(i=0;i<12;i++){
        shortPieces[i]=regexEscape(shortPieces[i]);
        longPieces[i]=regexEscape(longPieces[i]);
    }
    for(i=0;i<24;i++){
        mixedPieces[i]=regexEscape(mixedPieces[i]);
    }

    this._monthsRegex=newRegExp('^('+mixedPieces.join('|')+')','i');
    this._monthsShortRegex=this._monthsRegex;
    this._monthsStrictRegex=newRegExp('^('+longPieces.join('|')+')','i');
    this._monthsShortStrictRegex=newRegExp('^('+shortPieces.join('|')+')','i');
}

//FORMATTING

addFormatToken('Y',0,0,function(){
    vary=this.year();
    returny<=9999?''+y:'+'+y;
});

addFormatToken(0,['YY',2],0,function(){
    returnthis.year()%100;
});

addFormatToken(0,['YYYY',  4],      0,'year');
addFormatToken(0,['YYYYY', 5],      0,'year');
addFormatToken(0,['YYYYYY',6,true],0,'year');

//ALIASES

addUnitAlias('year','y');

//PRIORITIES

addUnitPriority('year',1);

//PARSING

addRegexToken('Y',     matchSigned);
addRegexToken('YY',    match1to2,match2);
addRegexToken('YYYY',  match1to4,match4);
addRegexToken('YYYYY', match1to6,match6);
addRegexToken('YYYYYY',match1to6,match6);

addParseToken(['YYYYY','YYYYYY'],YEAR);
addParseToken('YYYY',function(input,array){
    array[YEAR]=input.length===2?hooks.parseTwoDigitYear(input):toInt(input);
});
addParseToken('YY',function(input,array){
    array[YEAR]=hooks.parseTwoDigitYear(input);
});
addParseToken('Y',function(input,array){
    array[YEAR]=parseInt(input,10);
});

//HELPERS

functiondaysInYear(year){
    returnisLeapYear(year)?366:365;
}

functionisLeapYear(year){
    return(year%4===0&&year%100!==0)||year%400===0;
}

//HOOKS

hooks.parseTwoDigitYear=function(input){
    returntoInt(input)+(toInt(input)>68?1900:2000);
};

//MOMENTS

vargetSetYear=makeGetSet('FullYear',true);

functiongetIsLeapYear(){
    returnisLeapYear(this.year());
}

functioncreateDate(y,m,d,h,M,s,ms){
    //can'tjustapply()tocreateadate:
    //http://stackoverflow.com/questions/181348/instantiating-a-javascript-object-by-calling-prototype-constructor-apply
    vardate=newDate(y,m,d,h,M,s,ms);

    //thedateconstructorremapsyears0-99to1900-1999
    if(y<100&&y>=0&&isFinite(date.getFullYear())){
        date.setFullYear(y);
    }
    returndate;
}

functioncreateUTCDate(y){
    vardate=newDate(Date.UTC.apply(null,arguments));

    //theDate.UTCfunctionremapsyears0-99to1900-1999
    if(y<100&&y>=0&&isFinite(date.getUTCFullYear())){
        date.setUTCFullYear(y);
    }
    returndate;
}

//start-of-first-week-start-of-year
functionfirstWeekOffset(year,dow,doy){
    var//first-weekday--whichjanuaryisalwaysinthefirstweek(4foriso,1forother)
        fwd=7+dow-doy,
        //first-weekdaylocalweekday--whichlocalweekdayisfwd
        fwdlw=(7+createUTCDate(year,0,fwd).getUTCDay()-dow)%7;

    return-fwdlw+fwd-1;
}

//http://en.wikipedia.org/wiki/ISO_week_date#Calculating_a_date_given_the_year.2C_week_number_and_weekday
functiondayOfYearFromWeeks(year,week,weekday,dow,doy){
    varlocalWeekday=(7+weekday-dow)%7,
        weekOffset=firstWeekOffset(year,dow,doy),
        dayOfYear=1+7*(week-1)+localWeekday+weekOffset,
        resYear,resDayOfYear;

    if(dayOfYear<=0){
        resYear=year-1;
        resDayOfYear=daysInYear(resYear)+dayOfYear;
    }elseif(dayOfYear>daysInYear(year)){
        resYear=year+1;
        resDayOfYear=dayOfYear-daysInYear(year);
    }else{
        resYear=year;
        resDayOfYear=dayOfYear;
    }

    return{
        year:resYear,
        dayOfYear:resDayOfYear
    };
}

functionweekOfYear(mom,dow,doy){
    varweekOffset=firstWeekOffset(mom.year(),dow,doy),
        week=Math.floor((mom.dayOfYear()-weekOffset-1)/7)+1,
        resWeek,resYear;

    if(week<1){
        resYear=mom.year()-1;
        resWeek=week+weeksInYear(resYear,dow,doy);
    }elseif(week>weeksInYear(mom.year(),dow,doy)){
        resWeek=week-weeksInYear(mom.year(),dow,doy);
        resYear=mom.year()+1;
    }else{
        resYear=mom.year();
        resWeek=week;
    }

    return{
        week:resWeek,
        year:resYear
    };
}

functionweeksInYear(year,dow,doy){
    varweekOffset=firstWeekOffset(year,dow,doy),
        weekOffsetNext=firstWeekOffset(year+1,dow,doy);
    return(daysInYear(year)-weekOffset+weekOffsetNext)/7;
}

//FORMATTING

addFormatToken('w',['ww',2],'wo','week');
addFormatToken('W',['WW',2],'Wo','isoWeek');

//ALIASES

addUnitAlias('week','w');
addUnitAlias('isoWeek','W');

//PRIORITIES

addUnitPriority('week',5);
addUnitPriority('isoWeek',5);

//PARSING

addRegexToken('w', match1to2);
addRegexToken('ww',match1to2,match2);
addRegexToken('W', match1to2);
addRegexToken('WW',match1to2,match2);

addWeekParseToken(['w','ww','W','WW'],function(input,week,config,token){
    week[token.substr(0,1)]=toInt(input);
});

//HELPERS

//LOCALES

functionlocaleWeek(mom){
    returnweekOfYear(mom,this._week.dow,this._week.doy).week;
}

vardefaultLocaleWeek={
    dow:0,//Sundayisthefirstdayoftheweek.
    doy:6 //TheweekthatcontainsJan1stisthefirstweekoftheyear.
};

functionlocaleFirstDayOfWeek(){
    returnthis._week.dow;
}

functionlocaleFirstDayOfYear(){
    returnthis._week.doy;
}

//MOMENTS

functiongetSetWeek(input){
    varweek=this.localeData().week(this);
    returninput==null?week:this.add((input-week)*7,'d');
}

functiongetSetISOWeek(input){
    varweek=weekOfYear(this,1,4).week;
    returninput==null?week:this.add((input-week)*7,'d');
}

//FORMATTING

addFormatToken('d',0,'do','day');

addFormatToken('dd',0,0,function(format){
    returnthis.localeData().weekdaysMin(this,format);
});

addFormatToken('ddd',0,0,function(format){
    returnthis.localeData().weekdaysShort(this,format);
});

addFormatToken('dddd',0,0,function(format){
    returnthis.localeData().weekdays(this,format);
});

addFormatToken('e',0,0,'weekday');
addFormatToken('E',0,0,'isoWeekday');

//ALIASES

addUnitAlias('day','d');
addUnitAlias('weekday','e');
addUnitAlias('isoWeekday','E');

//PRIORITY
addUnitPriority('day',11);
addUnitPriority('weekday',11);
addUnitPriority('isoWeekday',11);

//PARSING

addRegexToken('d',   match1to2);
addRegexToken('e',   match1to2);
addRegexToken('E',   match1to2);
addRegexToken('dd',  function(isStrict,locale){
    returnlocale.weekdaysMinRegex(isStrict);
});
addRegexToken('ddd',  function(isStrict,locale){
    returnlocale.weekdaysShortRegex(isStrict);
});
addRegexToken('dddd',  function(isStrict,locale){
    returnlocale.weekdaysRegex(isStrict);
});

addWeekParseToken(['dd','ddd','dddd'],function(input,week,config,token){
    varweekday=config._locale.weekdaysParse(input,token,config._strict);
    //ifwedidn'tgetaweekdayname,markthedateasinvalid
    if(weekday!=null){
        week.d=weekday;
    }else{
        getParsingFlags(config).invalidWeekday=input;
    }
});

addWeekParseToken(['d','e','E'],function(input,week,config,token){
    week[token]=toInt(input);
});

//HELPERS

functionparseWeekday(input,locale){
    if(typeofinput!=='string'){
        returninput;
    }

    if(!isNaN(input)){
        returnparseInt(input,10);
    }

    input=locale.weekdaysParse(input);
    if(typeofinput==='number'){
        returninput;
    }

    returnnull;
}

functionparseIsoWeekday(input,locale){
    if(typeofinput==='string'){
        returnlocale.weekdaysParse(input)%7||7;
    }
    returnisNaN(input)?null:input;
}

//LOCALES

vardefaultLocaleWeekdays='Sunday_Monday_Tuesday_Wednesday_Thursday_Friday_Saturday'.split('_');
functionlocaleWeekdays(m,format){
    if(!m){
        returnthis._weekdays;
    }
    returnisArray(this._weekdays)?this._weekdays[m.day()]:
        this._weekdays[this._weekdays.isFormat.test(format)?'format':'standalone'][m.day()];
}

vardefaultLocaleWeekdaysShort='Sun_Mon_Tue_Wed_Thu_Fri_Sat'.split('_');
functionlocaleWeekdaysShort(m){
    return(m)?this._weekdaysShort[m.day()]:this._weekdaysShort;
}

vardefaultLocaleWeekdaysMin='Su_Mo_Tu_We_Th_Fr_Sa'.split('_');
functionlocaleWeekdaysMin(m){
    return(m)?this._weekdaysMin[m.day()]:this._weekdaysMin;
}

functionhandleStrictParse$1(weekdayName,format,strict){
    vari,ii,mom,llc=weekdayName.toLocaleLowerCase();
    if(!this._weekdaysParse){
        this._weekdaysParse=[];
        this._shortWeekdaysParse=[];
        this._minWeekdaysParse=[];

        for(i=0;i<7;++i){
            mom=createUTC([2000,1]).day(i);
            this._minWeekdaysParse[i]=this.weekdaysMin(mom,'').toLocaleLowerCase();
            this._shortWeekdaysParse[i]=this.weekdaysShort(mom,'').toLocaleLowerCase();
            this._weekdaysParse[i]=this.weekdays(mom,'').toLocaleLowerCase();
        }
    }

    if(strict){
        if(format==='dddd'){
            ii=indexOf$1.call(this._weekdaysParse,llc);
            returnii!==-1?ii:null;
        }elseif(format==='ddd'){
            ii=indexOf$1.call(this._shortWeekdaysParse,llc);
            returnii!==-1?ii:null;
        }else{
            ii=indexOf$1.call(this._minWeekdaysParse,llc);
            returnii!==-1?ii:null;
        }
    }else{
        if(format==='dddd'){
            ii=indexOf$1.call(this._weekdaysParse,llc);
            if(ii!==-1){
                returnii;
            }
            ii=indexOf$1.call(this._shortWeekdaysParse,llc);
            if(ii!==-1){
                returnii;
            }
            ii=indexOf$1.call(this._minWeekdaysParse,llc);
            returnii!==-1?ii:null;
        }elseif(format==='ddd'){
            ii=indexOf$1.call(this._shortWeekdaysParse,llc);
            if(ii!==-1){
                returnii;
            }
            ii=indexOf$1.call(this._weekdaysParse,llc);
            if(ii!==-1){
                returnii;
            }
            ii=indexOf$1.call(this._minWeekdaysParse,llc);
            returnii!==-1?ii:null;
        }else{
            ii=indexOf$1.call(this._minWeekdaysParse,llc);
            if(ii!==-1){
                returnii;
            }
            ii=indexOf$1.call(this._weekdaysParse,llc);
            if(ii!==-1){
                returnii;
            }
            ii=indexOf$1.call(this._shortWeekdaysParse,llc);
            returnii!==-1?ii:null;
        }
    }
}

functionlocaleWeekdaysParse(weekdayName,format,strict){
    vari,mom,regex;

    if(this._weekdaysParseExact){
        returnhandleStrictParse$1.call(this,weekdayName,format,strict);
    }

    if(!this._weekdaysParse){
        this._weekdaysParse=[];
        this._minWeekdaysParse=[];
        this._shortWeekdaysParse=[];
        this._fullWeekdaysParse=[];
    }

    for(i=0;i<7;i++){
        //maketheregexifwedon'thaveitalready

        mom=createUTC([2000,1]).day(i);
        if(strict&&!this._fullWeekdaysParse[i]){
            this._fullWeekdaysParse[i]=newRegExp('^'+this.weekdays(mom,'').replace('.','\.?')+'$','i');
            this._shortWeekdaysParse[i]=newRegExp('^'+this.weekdaysShort(mom,'').replace('.','\.?')+'$','i');
            this._minWeekdaysParse[i]=newRegExp('^'+this.weekdaysMin(mom,'').replace('.','\.?')+'$','i');
        }
        if(!this._weekdaysParse[i]){
            regex='^'+this.weekdays(mom,'')+'|^'+this.weekdaysShort(mom,'')+'|^'+this.weekdaysMin(mom,'');
            this._weekdaysParse[i]=newRegExp(regex.replace('.',''),'i');
        }
        //testtheregex
        if(strict&&format==='dddd'&&this._fullWeekdaysParse[i].test(weekdayName)){
            returni;
        }elseif(strict&&format==='ddd'&&this._shortWeekdaysParse[i].test(weekdayName)){
            returni;
        }elseif(strict&&format==='dd'&&this._minWeekdaysParse[i].test(weekdayName)){
            returni;
        }elseif(!strict&&this._weekdaysParse[i].test(weekdayName)){
            returni;
        }
    }
}

//MOMENTS

functiongetSetDayOfWeek(input){
    if(!this.isValid()){
        returninput!=null?this:NaN;
    }
    varday=this._isUTC?this._d.getUTCDay():this._d.getDay();
    if(input!=null){
        input=parseWeekday(input,this.localeData());
        returnthis.add(input-day,'d');
    }else{
        returnday;
    }
}

functiongetSetLocaleDayOfWeek(input){
    if(!this.isValid()){
        returninput!=null?this:NaN;
    }
    varweekday=(this.day()+7-this.localeData()._week.dow)%7;
    returninput==null?weekday:this.add(input-weekday,'d');
}

functiongetSetISODayOfWeek(input){
    if(!this.isValid()){
        returninput!=null?this:NaN;
    }

    //behavesthesameasmoment#dayexcept
    //asagetter,returns7insteadof0(1-7rangeinsteadof0-6)
    //asasetter,sundayshouldbelongtothepreviousweek.

    if(input!=null){
        varweekday=parseIsoWeekday(input,this.localeData());
        returnthis.day(this.day()%7?weekday:weekday-7);
    }else{
        returnthis.day()||7;
    }
}

vardefaultWeekdaysRegex=matchWord;
functionweekdaysRegex(isStrict){
    if(this._weekdaysParseExact){
        if(!hasOwnProp(this,'_weekdaysRegex')){
            computeWeekdaysParse.call(this);
        }
        if(isStrict){
            returnthis._weekdaysStrictRegex;
        }else{
            returnthis._weekdaysRegex;
        }
    }else{
        if(!hasOwnProp(this,'_weekdaysRegex')){
            this._weekdaysRegex=defaultWeekdaysRegex;
        }
        returnthis._weekdaysStrictRegex&&isStrict?
            this._weekdaysStrictRegex:this._weekdaysRegex;
    }
}

vardefaultWeekdaysShortRegex=matchWord;
functionweekdaysShortRegex(isStrict){
    if(this._weekdaysParseExact){
        if(!hasOwnProp(this,'_weekdaysRegex')){
            computeWeekdaysParse.call(this);
        }
        if(isStrict){
            returnthis._weekdaysShortStrictRegex;
        }else{
            returnthis._weekdaysShortRegex;
        }
    }else{
        if(!hasOwnProp(this,'_weekdaysShortRegex')){
            this._weekdaysShortRegex=defaultWeekdaysShortRegex;
        }
        returnthis._weekdaysShortStrictRegex&&isStrict?
            this._weekdaysShortStrictRegex:this._weekdaysShortRegex;
    }
}

vardefaultWeekdaysMinRegex=matchWord;
functionweekdaysMinRegex(isStrict){
    if(this._weekdaysParseExact){
        if(!hasOwnProp(this,'_weekdaysRegex')){
            computeWeekdaysParse.call(this);
        }
        if(isStrict){
            returnthis._weekdaysMinStrictRegex;
        }else{
            returnthis._weekdaysMinRegex;
        }
    }else{
        if(!hasOwnProp(this,'_weekdaysMinRegex')){
            this._weekdaysMinRegex=defaultWeekdaysMinRegex;
        }
        returnthis._weekdaysMinStrictRegex&&isStrict?
            this._weekdaysMinStrictRegex:this._weekdaysMinRegex;
    }
}


functioncomputeWeekdaysParse(){
    functioncmpLenRev(a,b){
        returnb.length-a.length;
    }

    varminPieces=[],shortPieces=[],longPieces=[],mixedPieces=[],
        i,mom,minp,shortp,longp;
    for(i=0;i<7;i++){
        //maketheregexifwedon'thaveitalready
        mom=createUTC([2000,1]).day(i);
        minp=this.weekdaysMin(mom,'');
        shortp=this.weekdaysShort(mom,'');
        longp=this.weekdays(mom,'');
        minPieces.push(minp);
        shortPieces.push(shortp);
        longPieces.push(longp);
        mixedPieces.push(minp);
        mixedPieces.push(shortp);
        mixedPieces.push(longp);
    }
    //Sortingmakessureifoneweekday(orabbr)isaprefixofanotherit
    //willmatchthelongerpiece.
    minPieces.sort(cmpLenRev);
    shortPieces.sort(cmpLenRev);
    longPieces.sort(cmpLenRev);
    mixedPieces.sort(cmpLenRev);
    for(i=0;i<7;i++){
        shortPieces[i]=regexEscape(shortPieces[i]);
        longPieces[i]=regexEscape(longPieces[i]);
        mixedPieces[i]=regexEscape(mixedPieces[i]);
    }

    this._weekdaysRegex=newRegExp('^('+mixedPieces.join('|')+')','i');
    this._weekdaysShortRegex=this._weekdaysRegex;
    this._weekdaysMinRegex=this._weekdaysRegex;

    this._weekdaysStrictRegex=newRegExp('^('+longPieces.join('|')+')','i');
    this._weekdaysShortStrictRegex=newRegExp('^('+shortPieces.join('|')+')','i');
    this._weekdaysMinStrictRegex=newRegExp('^('+minPieces.join('|')+')','i');
}

//FORMATTING

functionhFormat(){
    returnthis.hours()%12||12;
}

functionkFormat(){
    returnthis.hours()||24;
}

addFormatToken('H',['HH',2],0,'hour');
addFormatToken('h',['hh',2],0,hFormat);
addFormatToken('k',['kk',2],0,kFormat);

addFormatToken('hmm',0,0,function(){
    return''+hFormat.apply(this)+zeroFill(this.minutes(),2);
});

addFormatToken('hmmss',0,0,function(){
    return''+hFormat.apply(this)+zeroFill(this.minutes(),2)+
        zeroFill(this.seconds(),2);
});

addFormatToken('Hmm',0,0,function(){
    return''+this.hours()+zeroFill(this.minutes(),2);
});

addFormatToken('Hmmss',0,0,function(){
    return''+this.hours()+zeroFill(this.minutes(),2)+
        zeroFill(this.seconds(),2);
});

functionmeridiem(token,lowercase){
    addFormatToken(token,0,0,function(){
        returnthis.localeData().meridiem(this.hours(),this.minutes(),lowercase);
    });
}

meridiem('a',true);
meridiem('A',false);

//ALIASES

addUnitAlias('hour','h');

//PRIORITY
addUnitPriority('hour',13);

//PARSING

functionmatchMeridiem(isStrict,locale){
    returnlocale._meridiemParse;
}

addRegexToken('a', matchMeridiem);
addRegexToken('A', matchMeridiem);
addRegexToken('H', match1to2);
addRegexToken('h', match1to2);
addRegexToken('HH',match1to2,match2);
addRegexToken('hh',match1to2,match2);

addRegexToken('hmm',match3to4);
addRegexToken('hmmss',match5to6);
addRegexToken('Hmm',match3to4);
addRegexToken('Hmmss',match5to6);

addParseToken(['H','HH'],HOUR);
addParseToken(['a','A'],function(input,array,config){
    config._isPm=config._locale.isPM(input);
    config._meridiem=input;
});
addParseToken(['h','hh'],function(input,array,config){
    array[HOUR]=toInt(input);
    getParsingFlags(config).bigHour=true;
});
addParseToken('hmm',function(input,array,config){
    varpos=input.length-2;
    array[HOUR]=toInt(input.substr(0,pos));
    array[MINUTE]=toInt(input.substr(pos));
    getParsingFlags(config).bigHour=true;
});
addParseToken('hmmss',function(input,array,config){
    varpos1=input.length-4;
    varpos2=input.length-2;
    array[HOUR]=toInt(input.substr(0,pos1));
    array[MINUTE]=toInt(input.substr(pos1,2));
    array[SECOND]=toInt(input.substr(pos2));
    getParsingFlags(config).bigHour=true;
});
addParseToken('Hmm',function(input,array,config){
    varpos=input.length-2;
    array[HOUR]=toInt(input.substr(0,pos));
    array[MINUTE]=toInt(input.substr(pos));
});
addParseToken('Hmmss',function(input,array,config){
    varpos1=input.length-4;
    varpos2=input.length-2;
    array[HOUR]=toInt(input.substr(0,pos1));
    array[MINUTE]=toInt(input.substr(pos1,2));
    array[SECOND]=toInt(input.substr(pos2));
});

//LOCALES

functionlocaleIsPM(input){
    //IE8QuirksMode&IE7StandardsModedonotallowaccessingstringslikearrays
    //UsingcharAtshouldbemorecompatible.
    return((input+'').toLowerCase().charAt(0)==='p');
}

vardefaultLocaleMeridiemParse=/[ap]\.?m?\.?/i;
functionlocaleMeridiem(hours,minutes,isLower){
    if(hours>11){
        returnisLower?'pm':'PM';
    }else{
        returnisLower?'am':'AM';
    }
}


//MOMENTS

//Settingthehourshouldkeepthetime,becausetheuserexplicitly
//specifiedwhichhourhewants.Sotryingtomaintainthesamehour(in
//anewtimezone)makessense.Adding/subtractinghoursdoesnotfollow
//thisrule.
vargetSetHour=makeGetSet('Hours',true);

//months
//week
//weekdays
//meridiem
varbaseConfig={
    calendar:defaultCalendar,
    longDateFormat:defaultLongDateFormat,
    invalidDate:defaultInvalidDate,
    ordinal:defaultOrdinal,
    ordinalParse:defaultOrdinalParse,
    relativeTime:defaultRelativeTime,

    months:defaultLocaleMonths,
    monthsShort:defaultLocaleMonthsShort,

    week:defaultLocaleWeek,

    weekdays:defaultLocaleWeekdays,
    weekdaysMin:defaultLocaleWeekdaysMin,
    weekdaysShort:defaultLocaleWeekdaysShort,

    meridiemParse:defaultLocaleMeridiemParse
};

//internalstorageforlocaleconfigfiles
varlocales={};
varlocaleFamilies={};
varglobalLocale;

functionnormalizeLocale(key){
    returnkey?key.toLowerCase().replace('_','-'):key;
}

//pickthelocalefromthearray
//try['en-au','en-gb']as'en-au','en-gb','en',asinmovethroughthelisttryingeach
//substringfrommostspecifictoleast,butmovetothenextarrayitemifit'samorespecificvariantthanthecurrentroot
functionchooseLocale(names){
    vari=0,j,next,locale,split;

    while(i<names.length){
        split=normalizeLocale(names[i]).split('-');
        j=split.length;
        next=normalizeLocale(names[i+1]);
        next=next?next.split('-'):null;
        while(j>0){
            locale=loadLocale(split.slice(0,j).join('-'));
            if(locale){
                returnlocale;
            }
            if(next&&next.length>=j&&compareArrays(split,next,true)>=j-1){
                //thenextarrayitemisbetterthanashallowersubstringofthisone
                break;
            }
            j--;
        }
        i++;
    }
    returnnull;
}

functionloadLocale(name){
    varoldLocale=null;
    //TODO:FindabetterwaytoregisterandloadallthelocalesinNode
    if(!locales[name]&&(typeofmodule!=='undefined')&&
            module&&module.exports){
        try{
            oldLocale=globalLocale._abbr;
            require('./locale/'+name);
            //becausedefineLocalecurrentlyalsosetsthegloballocale,we
            //wanttoundothatforlazyloadedlocales
            getSetGlobalLocale(oldLocale);
        }catch(e){}
    }
    returnlocales[name];
}

//Thisfunctionwillloadlocaleandthensetthegloballocale. If
//noargumentsarepassedin,itwillsimplyreturnthecurrentglobal
//localekey.
functiongetSetGlobalLocale(key,values){
    vardata;
    if(key){
        if(isUndefined(values)){
            data=getLocale(key);
        }
        else{
            data=defineLocale(key,values);
        }

        if(data){
            //moment.duration._locale=moment._locale=data;
            globalLocale=data;
        }
    }

    returnglobalLocale._abbr;
}

functiondefineLocale(name,config){
    if(config!==null){
        varparentConfig=baseConfig;
        config.abbr=name;
        if(locales[name]!=null){
            deprecateSimple('defineLocaleOverride',
                    'usemoment.updateLocale(localeName,config)tochange'+
                    'anexistinglocale.moment.defineLocale(localeName,'+
                    'config)shouldonlybeusedforcreatinganewlocale'+
                    'Seehttp://momentjs.com/guides/#/warnings/define-locale/formoreinfo.');
            parentConfig=locales[name]._config;
        }elseif(config.parentLocale!=null){
            if(locales[config.parentLocale]!=null){
                parentConfig=locales[config.parentLocale]._config;
            }else{
                if(!localeFamilies[config.parentLocale]){
                    localeFamilies[config.parentLocale]=[];
                }
                localeFamilies[config.parentLocale].push({
                    name:name,
                    config:config
                });
                returnnull;
            }
        }
        locales[name]=newLocale(mergeConfigs(parentConfig,config));

        if(localeFamilies[name]){
            localeFamilies[name].forEach(function(x){
                defineLocale(x.name,x.config);
            });
        }

        //backwardscompatfornow:alsosetthelocale
        //makesurewesetthelocaleAFTERallchildlocaleshavebeen
        //created,sowewon'tendupwiththechildlocaleset.
        getSetGlobalLocale(name);


        returnlocales[name];
    }else{
        //usefulfortesting
        deletelocales[name];
        returnnull;
    }
}

functionupdateLocale(name,config){
    if(config!=null){
        varlocale,parentConfig=baseConfig;
        //MERGE
        if(locales[name]!=null){
            parentConfig=locales[name]._config;
        }
        config=mergeConfigs(parentConfig,config);
        locale=newLocale(config);
        locale.parentLocale=locales[name];
        locales[name]=locale;

        //backwardscompatfornow:alsosetthelocale
        getSetGlobalLocale(name);
    }else{
        //passnullforconfigtounupdate,usefulfortests
        if(locales[name]!=null){
            if(locales[name].parentLocale!=null){
                locales[name]=locales[name].parentLocale;
            }elseif(locales[name]!=null){
                deletelocales[name];
            }
        }
    }
    returnlocales[name];
}

//returnslocaledata
functiongetLocale(key){
    varlocale;

    if(key&&key._locale&&key._locale._abbr){
        key=key._locale._abbr;
    }

    if(!key){
        returnglobalLocale;
    }

    if(!isArray(key)){
        //short-circuiteverythingelse
        locale=loadLocale(key);
        if(locale){
            returnlocale;
        }
        key=[key];
    }

    returnchooseLocale(key);
}

functionlistLocales(){
    returnkeys$1(locales);
}

functioncheckOverflow(m){
    varoverflow;
    vara=m._a;

    if(a&&getParsingFlags(m).overflow===-2){
        overflow=
            a[MONTH]      <0||a[MONTH]      >11 ?MONTH:
            a[DATE]       <1||a[DATE]       >daysInMonth(a[YEAR],a[MONTH])?DATE:
            a[HOUR]       <0||a[HOUR]       >24||(a[HOUR]===24&&(a[MINUTE]!==0||a[SECOND]!==0||a[MILLISECOND]!==0))?HOUR:
            a[MINUTE]     <0||a[MINUTE]     >59 ?MINUTE:
            a[SECOND]     <0||a[SECOND]     >59 ?SECOND:
            a[MILLISECOND]<0||a[MILLISECOND]>999?MILLISECOND:
            -1;

        if(getParsingFlags(m)._overflowDayOfYear&&(overflow<YEAR||overflow>DATE)){
            overflow=DATE;
        }
        if(getParsingFlags(m)._overflowWeeks&&overflow===-1){
            overflow=WEEK;
        }
        if(getParsingFlags(m)._overflowWeekday&&overflow===-1){
            overflow=WEEKDAY;
        }

        getParsingFlags(m).overflow=overflow;
    }

    returnm;
}

//iso8601regex
//0000-00-000000-W00or0000-W00-0+T+00or00:00or00:00:00or00:00:00.000++00:00or+0000or+00)
varextendedIsoRegex=/^\s*((?:[+-]\d{6}|\d{4})-(?:\d\d-\d\d|W\d\d-\d|W\d\d|\d\d\d|\d\d))(?:(T|)(\d\d(?::\d\d(?::\d\d(?:[.,]\d+)?)?)?)([\+\-]\d\d(?::?\d\d)?|\s*Z)?)?$/;
varbasicIsoRegex=/^\s*((?:[+-]\d{6}|\d{4})(?:\d\d\d\d|W\d\d\d|W\d\d|\d\d\d|\d\d))(?:(T|)(\d\d(?:\d\d(?:\d\d(?:[.,]\d+)?)?)?)([\+\-]\d\d(?::?\d\d)?|\s*Z)?)?$/;

vartzRegex=/Z|[+-]\d\d(?::?\d\d)?/;

varisoDates=[
    ['YYYYYY-MM-DD',/[+-]\d{6}-\d\d-\d\d/],
    ['YYYY-MM-DD',/\d{4}-\d\d-\d\d/],
    ['GGGG-[W]WW-E',/\d{4}-W\d\d-\d/],
    ['GGGG-[W]WW',/\d{4}-W\d\d/,false],
    ['YYYY-DDD',/\d{4}-\d{3}/],
    ['YYYY-MM',/\d{4}-\d\d/,false],
    ['YYYYYYMMDD',/[+-]\d{10}/],
    ['YYYYMMDD',/\d{8}/],
    //YYYYMMisNOTallowedbythestandard
    ['GGGG[W]WWE',/\d{4}W\d{3}/],
    ['GGGG[W]WW',/\d{4}W\d{2}/,false],
    ['YYYYDDD',/\d{7}/]
];

//isotimeformatsandregexes
varisoTimes=[
    ['HH:mm:ss.SSSS',/\d\d:\d\d:\d\d\.\d+/],
    ['HH:mm:ss,SSSS',/\d\d:\d\d:\d\d,\d+/],
    ['HH:mm:ss',/\d\d:\d\d:\d\d/],
    ['HH:mm',/\d\d:\d\d/],
    ['HHmmss.SSSS',/\d\d\d\d\d\d\.\d+/],
    ['HHmmss,SSSS',/\d\d\d\d\d\d,\d+/],
    ['HHmmss',/\d\d\d\d\d\d/],
    ['HHmm',/\d\d\d\d/],
    ['HH',/\d\d/]
];

varaspNetJsonRegex=/^\/?Date\((\-?\d+)/i;

//datefromisoformat
functionconfigFromISO(config){
    vari,l,
        string=config._i,
        match=extendedIsoRegex.exec(string)||basicIsoRegex.exec(string),
        allowTime,dateFormat,timeFormat,tzFormat;

    if(match){
        getParsingFlags(config).iso=true;

        for(i=0,l=isoDates.length;i<l;i++){
            if(isoDates[i][1].exec(match[1])){
                dateFormat=isoDates[i][0];
                allowTime=isoDates[i][2]!==false;
                break;
            }
        }
        if(dateFormat==null){
            config._isValid=false;
            return;
        }
        if(match[3]){
            for(i=0,l=isoTimes.length;i<l;i++){
                if(isoTimes[i][1].exec(match[3])){
                    //match[2]shouldbe'T'orspace
                    timeFormat=(match[2]||'')+isoTimes[i][0];
                    break;
                }
            }
            if(timeFormat==null){
                config._isValid=false;
                return;
            }
        }
        if(!allowTime&&timeFormat!=null){
            config._isValid=false;
            return;
        }
        if(match[4]){
            if(tzRegex.exec(match[4])){
                tzFormat='Z';
            }else{
                config._isValid=false;
                return;
            }
        }
        config._f=dateFormat+(timeFormat||'')+(tzFormat||'');
        configFromStringAndFormat(config);
    }else{
        config._isValid=false;
    }
}

//datefromisoformatorfallback
functionconfigFromString(config){
    varmatched=aspNetJsonRegex.exec(config._i);

    if(matched!==null){
        config._d=newDate(+matched[1]);
        return;
    }

    configFromISO(config);
    if(config._isValid===false){
        deleteconfig._isValid;
        hooks.createFromInputFallback(config);
    }
}

hooks.createFromInputFallback=deprecate(
    'valueprovidedisnotinarecognizedISOformat.momentconstructionfallsbacktojsDate(),'+
    'whichisnotreliableacrossallbrowsersandversions.NonISOdateformatsare'+
    'discouragedandwillberemovedinanupcomingmajorrelease.Pleasereferto'+
    'http://momentjs.com/guides/#/warnings/js-date/formoreinfo.',
    function(config){
        config._d=newDate(config._i+(config._useUTC?'UTC':''));
    }
);

//Pickthefirstdefinedoftwoorthreearguments.
functiondefaults(a,b,c){
    if(a!=null){
        returna;
    }
    if(b!=null){
        returnb;
    }
    returnc;
}

functioncurrentDateArray(config){
    //hooksisactuallytheexportedmomentobject
    varnowValue=newDate(hooks.now());
    if(config._useUTC){
        return[nowValue.getUTCFullYear(),nowValue.getUTCMonth(),nowValue.getUTCDate()];
    }
    return[nowValue.getFullYear(),nowValue.getMonth(),nowValue.getDate()];
}

//convertanarraytoadate.
//thearrayshouldmirrortheparametersbelow
//note:allvaluespasttheyearareoptionalandwilldefaulttothelowestpossiblevalue.
//[year,month,day,hour,minute,second,millisecond]
functionconfigFromArray(config){
    vari,date,input=[],currentDate,yearToUse;

    if(config._d){
        return;
    }

    currentDate=currentDateArray(config);

    //computedayoftheyearfromweeksandweekdays
    if(config._w&&config._a[DATE]==null&&config._a[MONTH]==null){
        dayOfYearFromWeekInfo(config);
    }

    //ifthedayoftheyearisset,figureoutwhatitis
    if(config._dayOfYear){
        yearToUse=defaults(config._a[YEAR],currentDate[YEAR]);

        if(config._dayOfYear>daysInYear(yearToUse)){
            getParsingFlags(config)._overflowDayOfYear=true;
        }

        date=createUTCDate(yearToUse,0,config._dayOfYear);
        config._a[MONTH]=date.getUTCMonth();
        config._a[DATE]=date.getUTCDate();
    }

    //Defaulttocurrentdate.
    //*ifnoyear,month,dayofmontharegiven,defaulttotoday
    //*ifdayofmonthisgiven,defaultmonthandyear
    //*ifmonthisgiven,defaultonlyyear
    //*ifyearisgiven,don'tdefaultanything
    for(i=0;i<3&&config._a[i]==null;++i){
        config._a[i]=input[i]=currentDate[i];
    }

    //Zerooutwhateverwasnotdefaulted,includingtime
    for(;i<7;i++){
        config._a[i]=input[i]=(config._a[i]==null)?(i===2?1:0):config._a[i];
    }

    //Checkfor24:00:00.000
    if(config._a[HOUR]===24&&
            config._a[MINUTE]===0&&
            config._a[SECOND]===0&&
            config._a[MILLISECOND]===0){
        config._nextDay=true;
        config._a[HOUR]=0;
    }

    config._d=(config._useUTC?createUTCDate:createDate).apply(null,input);
    //Applytimezoneoffsetfrominput.TheactualutcOffsetcanbechanged
    //withparseZone.
    if(config._tzm!=null){
        config._d.setUTCMinutes(config._d.getUTCMinutes()-config._tzm);
    }

    if(config._nextDay){
        config._a[HOUR]=24;
    }
}

functiondayOfYearFromWeekInfo(config){
    varw,weekYear,week,weekday,dow,doy,temp,weekdayOverflow;

    w=config._w;
    if(w.GG!=null||w.W!=null||w.E!=null){
        dow=1;
        doy=4;

        //TODO:WeneedtotakethecurrentisoWeekYear,butthatdependson
        //howweinterpretnow(local,utc,fixedoffset).Socreate
        //anowversionofcurrentconfig(takelocal/utc/offsetflags,and
        //createnow).
        weekYear=defaults(w.GG,config._a[YEAR],weekOfYear(createLocal(),1,4).year);
        week=defaults(w.W,1);
        weekday=defaults(w.E,1);
        if(weekday<1||weekday>7){
            weekdayOverflow=true;
        }
    }else{
        dow=config._locale._week.dow;
        doy=config._locale._week.doy;

        varcurWeek=weekOfYear(createLocal(),dow,doy);

        weekYear=defaults(w.gg,config._a[YEAR],curWeek.year);

        //Defaulttocurrentweek.
        week=defaults(w.w,curWeek.week);

        if(w.d!=null){
            //weekday--lowdaynumbersareconsiderednextweek
            weekday=w.d;
            if(weekday<0||weekday>6){
                weekdayOverflow=true;
            }
        }elseif(w.e!=null){
            //localweekday--countingstartsfrombeginningofweek
            weekday=w.e+dow;
            if(w.e<0||w.e>6){
                weekdayOverflow=true;
            }
        }else{
            //defaulttobeginningofweek
            weekday=dow;
        }
    }
    if(week<1||week>weeksInYear(weekYear,dow,doy)){
        getParsingFlags(config)._overflowWeeks=true;
    }elseif(weekdayOverflow!=null){
        getParsingFlags(config)._overflowWeekday=true;
    }else{
        temp=dayOfYearFromWeeks(weekYear,week,weekday,dow,doy);
        config._a[YEAR]=temp.year;
        config._dayOfYear=temp.dayOfYear;
    }
}

//constantthatreferstotheISOstandard
hooks.ISO_8601=function(){};

//datefromstringandformatstring
functionconfigFromStringAndFormat(config){
    //TODO:Movethistoanotherpartofthecreationflowtopreventcirculardeps
    if(config._f===hooks.ISO_8601){
        configFromISO(config);
        return;
    }

    config._a=[];
    getParsingFlags(config).empty=true;

    //ThisarrayisusedtomakeaDate,eitherwith`newDate`or`Date.UTC`
    varstring=''+config._i,
        i,parsedInput,tokens,token,skipped,
        stringLength=string.length,
        totalParsedInputLength=0;

    tokens=expandFormat(config._f,config._locale).match(formattingTokens)||[];

    for(i=0;i<tokens.length;i++){
        token=tokens[i];
        parsedInput=(string.match(getParseRegexForToken(token,config))||[])[0];
        //console.log('token',token,'parsedInput',parsedInput,
        //        'regex',getParseRegexForToken(token,config));
        if(parsedInput){
            skipped=string.substr(0,string.indexOf(parsedInput));
            if(skipped.length>0){
                getParsingFlags(config).unusedInput.push(skipped);
            }
            string=string.slice(string.indexOf(parsedInput)+parsedInput.length);
            totalParsedInputLength+=parsedInput.length;
        }
        //don'tparseifit'snotaknowntoken
        if(formatTokenFunctions[token]){
            if(parsedInput){
                getParsingFlags(config).empty=false;
            }
            else{
                getParsingFlags(config).unusedTokens.push(token);
            }
            addTimeToArrayFromToken(token,parsedInput,config);
        }
        elseif(config._strict&&!parsedInput){
            getParsingFlags(config).unusedTokens.push(token);
        }
    }

    //addremainingunparsedinputlengthtothestring
    getParsingFlags(config).charsLeftOver=stringLength-totalParsedInputLength;
    if(string.length>0){
        getParsingFlags(config).unusedInput.push(string);
    }

    //clear_12hflagifhouris<=12
    if(config._a[HOUR]<=12&&
        getParsingFlags(config).bigHour===true&&
        config._a[HOUR]>0){
        getParsingFlags(config).bigHour=undefined;
    }

    getParsingFlags(config).parsedDateParts=config._a.slice(0);
    getParsingFlags(config).meridiem=config._meridiem;
    //handlemeridiem
    config._a[HOUR]=meridiemFixWrap(config._locale,config._a[HOUR],config._meridiem);

    configFromArray(config);
    checkOverflow(config);
}


functionmeridiemFixWrap(locale,hour,meridiem){
    varisPm;

    if(meridiem==null){
        //nothingtodo
        returnhour;
    }
    if(locale.meridiemHour!=null){
        returnlocale.meridiemHour(hour,meridiem);
    }elseif(locale.isPM!=null){
        //Fallback
        isPm=locale.isPM(meridiem);
        if(isPm&&hour<12){
            hour+=12;
        }
        if(!isPm&&hour===12){
            hour=0;
        }
        returnhour;
    }else{
        //thisisnotsupposedtohappen
        returnhour;
    }
}

//datefromstringandarrayofformatstrings
functionconfigFromStringAndArray(config){
    vartempConfig,
        bestMoment,

        scoreToBeat,
        i,
        currentScore;

    if(config._f.length===0){
        getParsingFlags(config).invalidFormat=true;
        config._d=newDate(NaN);
        return;
    }

    for(i=0;i<config._f.length;i++){
        currentScore=0;
        tempConfig=copyConfig({},config);
        if(config._useUTC!=null){
            tempConfig._useUTC=config._useUTC;
        }
        tempConfig._f=config._f[i];
        configFromStringAndFormat(tempConfig);

        if(!isValid(tempConfig)){
            continue;
        }

        //ifthereisanyinputthatwasnotparsedaddapenaltyforthatformat
        currentScore+=getParsingFlags(tempConfig).charsLeftOver;

        //ortokens
        currentScore+=getParsingFlags(tempConfig).unusedTokens.length*10;

        getParsingFlags(tempConfig).score=currentScore;

        if(scoreToBeat==null||currentScore<scoreToBeat){
            scoreToBeat=currentScore;
            bestMoment=tempConfig;
        }
    }

    extend(config,bestMoment||tempConfig);
}

functionconfigFromObject(config){
    if(config._d){
        return;
    }

    vari=normalizeObjectUnits(config._i);
    config._a=map([i.year,i.month,i.day||i.date,i.hour,i.minute,i.second,i.millisecond],function(obj){
        returnobj&&parseInt(obj,10);
    });

    configFromArray(config);
}

functioncreateFromConfig(config){
    varres=newMoment(checkOverflow(prepareConfig(config)));
    if(res._nextDay){
        //AddingissmartenougharoundDST
        res.add(1,'d');
        res._nextDay=undefined;
    }

    returnres;
}

functionprepareConfig(config){
    varinput=config._i,
        format=config._f;

    config._locale=config._locale||getLocale(config._l);

    if(input===null||(format===undefined&&input==='')){
        returncreateInvalid({nullInput:true});
    }

    if(typeofinput==='string'){
        config._i=input=config._locale.preparse(input);
    }

    if(isMoment(input)){
        returnnewMoment(checkOverflow(input));
    }elseif(isDate(input)){
        config._d=input;
    }elseif(isArray(format)){
        configFromStringAndArray(config);
    }elseif(format){
        configFromStringAndFormat(config);
    } else{
        configFromInput(config);
    }

    if(!isValid(config)){
        config._d=null;
    }

    returnconfig;
}

functionconfigFromInput(config){
    varinput=config._i;
    if(input===undefined){
        config._d=newDate(hooks.now());
    }elseif(isDate(input)){
        config._d=newDate(input.valueOf());
    }elseif(typeofinput==='string'){
        configFromString(config);
    }elseif(isArray(input)){
        config._a=map(input.slice(0),function(obj){
            returnparseInt(obj,10);
        });
        configFromArray(config);
    }elseif(typeof(input)==='object'){
        configFromObject(config);
    }elseif(isNumber(input)){
        //frommilliseconds
        config._d=newDate(input);
    }else{
        hooks.createFromInputFallback(config);
    }
}

functioncreateLocalOrUTC(input,format,locale,strict,isUTC){
    varc={};

    if(locale===true||locale===false){
        strict=locale;
        locale=undefined;
    }

    if((isObject(input)&&isObjectEmpty(input))||
            (isArray(input)&&input.length===0)){
        input=undefined;
    }
    //objectconstructionmustbedonethisway.
    //https://github.com/moment/moment/issues/1423
    c._isAMomentObject=true;
    c._useUTC=c._isUTC=isUTC;
    c._l=locale;
    c._i=input;
    c._f=format;
    c._strict=strict;

    returncreateFromConfig(c);
}

functioncreateLocal(input,format,locale,strict){
    returncreateLocalOrUTC(input,format,locale,strict,false);
}

varprototypeMin=deprecate(
    'moment().minisdeprecated,usemoment.maxinstead.http://momentjs.com/guides/#/warnings/min-max/',
    function(){
        varother=createLocal.apply(null,arguments);
        if(this.isValid()&&other.isValid()){
            returnother<this?this:other;
        }else{
            returncreateInvalid();
        }
    }
);

varprototypeMax=deprecate(
    'moment().maxisdeprecated,usemoment.mininstead.http://momentjs.com/guides/#/warnings/min-max/',
    function(){
        varother=createLocal.apply(null,arguments);
        if(this.isValid()&&other.isValid()){
            returnother>this?this:other;
        }else{
            returncreateInvalid();
        }
    }
);

//Pickamomentmfrommomentssothatm[fn](other)istrueforall
//other.Thisreliesonthefunctionfntobetransitive.
//
//momentsshouldeitherbeanarrayofmomentobjectsoranarray,whose
//firstelementisanarrayofmomentobjects.
functionpickBy(fn,moments){
    varres,i;
    if(moments.length===1&&isArray(moments[0])){
        moments=moments[0];
    }
    if(!moments.length){
        returncreateLocal();
    }
    res=moments[0];
    for(i=1;i<moments.length;++i){
        if(!moments[i].isValid()||moments[i][fn](res)){
            res=moments[i];
        }
    }
    returnres;
}

//TODO:Use[].sortinstead?
functionmin(){
    varargs=[].slice.call(arguments,0);

    returnpickBy('isBefore',args);
}

functionmax(){
    varargs=[].slice.call(arguments,0);

    returnpickBy('isAfter',args);
}

varnow=function(){
    returnDate.now?Date.now():+(newDate());
};

functionDuration(duration){
    varnormalizedInput=normalizeObjectUnits(duration),
        years=normalizedInput.year||0,
        quarters=normalizedInput.quarter||0,
        months=normalizedInput.month||0,
        weeks=normalizedInput.week||0,
        days=normalizedInput.day||0,
        hours=normalizedInput.hour||0,
        minutes=normalizedInput.minute||0,
        seconds=normalizedInput.second||0,
        milliseconds=normalizedInput.millisecond||0;

    //representationfordateAddRemove
    this._milliseconds=+milliseconds+
        seconds*1e3+//1000
        minutes*6e4+//1000*60
        hours*1000*60*60;//using1000*60*60insteadof36e5toavoidfloatingpointroundingerrorshttps://github.com/moment/moment/issues/2978
    //BecauseofdateAddRemovetreats24hoursasdifferentfroma
    //daywhenworkingaroundDST,weneedtostorethemseparately
    this._days=+days+
        weeks*7;
    //Itisimpossibletranslatemonthsintodayswithoutknowing
    //whichmonthsyouarearetalkingabout,sowehavetostore
    //itseparately.
    this._months=+months+
        quarters*3+
        years*12;

    this._data={};

    this._locale=getLocale();

    this._bubble();
}

functionisDuration(obj){
    returnobjinstanceofDuration;
}

functionabsRound(number){
    if(number<0){
        returnMath.round(-1*number)*-1;
    }else{
        returnMath.round(number);
    }
}

//FORMATTING

functionoffset(token,separator){
    addFormatToken(token,0,0,function(){
        varoffset=this.utcOffset();
        varsign='+';
        if(offset<0){
            offset=-offset;
            sign='-';
        }
        returnsign+zeroFill(~~(offset/60),2)+separator+zeroFill(~~(offset)%60,2);
    });
}

offset('Z',':');
offset('ZZ','');

//PARSING

addRegexToken('Z', matchShortOffset);
addRegexToken('ZZ',matchShortOffset);
addParseToken(['Z','ZZ'],function(input,array,config){
    config._useUTC=true;
    config._tzm=offsetFromString(matchShortOffset,input);
});

//HELPERS

//timezonechunker
//'+10:00'>['10', '00']
//'-1530' >['-15','30']
varchunkOffset=/([\+\-]|\d\d)/gi;

functionoffsetFromString(matcher,string){
    varmatches=(string||'').match(matcher);

    if(matches===null){
        returnnull;
    }

    varchunk  =matches[matches.length-1]||[];
    varparts  =(chunk+'').match(chunkOffset)||['-',0,0];
    varminutes=+(parts[1]*60)+toInt(parts[2]);

    returnminutes===0?
      0:
      parts[0]==='+'?minutes:-minutes;
}

//Returnamomentfrominput,thatislocal/utc/zoneequivalenttomodel.
functioncloneWithOffset(input,model){
    varres,diff;
    if(model._isUTC){
        res=model.clone();
        diff=(isMoment(input)||isDate(input)?input.valueOf():createLocal(input).valueOf())-res.valueOf();
        //Uselow-levelapi,becausethisfnislow-levelapi.
        res._d.setTime(res._d.valueOf()+diff);
        hooks.updateOffset(res,false);
        returnres;
    }else{
        returncreateLocal(input).local();
    }
}

functiongetDateOffset(m){
    //OnFirefox.24Date#getTimezoneOffsetreturnsafloatingpoint.
    //https://github.com/moment/moment/pull/1871
    return-Math.round(m._d.getTimezoneOffset()/15)*15;
}

//HOOKS

//Thisfunctionwillbecalledwheneveramomentismutated.
//Itisintendedtokeeptheoffsetinsyncwiththetimezone.
hooks.updateOffset=function(){};

//MOMENTS

//keepLocalTime=truemeansonlychangethetimezone,without
//affectingthelocalhour.So5:31:26+0300--[utcOffset(2,true)]-->
//5:31:26+0200Itispossiblethat5:31:26doesn'texistwithoffset
//+0200,soweadjustthetimeasneeded,tobevalid.
//
//Keepingthetimeactuallyadds/subtracts(onehour)
//fromtheactualrepresentedtime.ThatiswhywecallupdateOffset
//asecondtime.Incaseitwantsustochangetheoffsetagain
//_changeInProgress==truecase,thenwehavetoadjust,because
//thereisnosuchtimeinthegiventimezone.
functiongetSetOffset(input,keepLocalTime){
    varoffset=this._offset||0,
        localAdjust;
    if(!this.isValid()){
        returninput!=null?this:NaN;
    }
    if(input!=null){
        if(typeofinput==='string'){
            input=offsetFromString(matchShortOffset,input);
            if(input===null){
                returnthis;
            }
        }elseif(Math.abs(input)<16){
            input=input*60;
        }
        if(!this._isUTC&&keepLocalTime){
            localAdjust=getDateOffset(this);
        }
        this._offset=input;
        this._isUTC=true;
        if(localAdjust!=null){
            this.add(localAdjust,'m');
        }
        if(offset!==input){
            if(!keepLocalTime||this._changeInProgress){
                addSubtract(this,createDuration(input-offset,'m'),1,false);
            }elseif(!this._changeInProgress){
                this._changeInProgress=true;
                hooks.updateOffset(this,true);
                this._changeInProgress=null;
            }
        }
        returnthis;
    }else{
        returnthis._isUTC?offset:getDateOffset(this);
    }
}

functiongetSetZone(input,keepLocalTime){
    if(input!=null){
        if(typeofinput!=='string'){
            input=-input;
        }

        this.utcOffset(input,keepLocalTime);

        returnthis;
    }else{
        return-this.utcOffset();
    }
}

functionsetOffsetToUTC(keepLocalTime){
    returnthis.utcOffset(0,keepLocalTime);
}

functionsetOffsetToLocal(keepLocalTime){
    if(this._isUTC){
        this.utcOffset(0,keepLocalTime);
        this._isUTC=false;

        if(keepLocalTime){
            this.subtract(getDateOffset(this),'m');
        }
    }
    returnthis;
}

functionsetOffsetToParsedOffset(){
    if(this._tzm!=null){
        this.utcOffset(this._tzm);
    }elseif(typeofthis._i==='string'){
        vartZone=offsetFromString(matchOffset,this._i);
        if(tZone!=null){
            this.utcOffset(tZone);
        }
        else{
            this.utcOffset(0,true);
        }
    }
    returnthis;
}

functionhasAlignedHourOffset(input){
    if(!this.isValid()){
        returnfalse;
    }
    input=input?createLocal(input).utcOffset():0;

    return(this.utcOffset()-input)%60===0;
}

functionisDaylightSavingTime(){
    return(
        this.utcOffset()>this.clone().month(0).utcOffset()||
        this.utcOffset()>this.clone().month(5).utcOffset()
    );
}

functionisDaylightSavingTimeShifted(){
    if(!isUndefined(this._isDSTShifted)){
        returnthis._isDSTShifted;
    }

    varc={};

    copyConfig(c,this);
    c=prepareConfig(c);

    if(c._a){
        varother=c._isUTC?createUTC(c._a):createLocal(c._a);
        this._isDSTShifted=this.isValid()&&
            compareArrays(c._a,other.toArray())>0;
    }else{
        this._isDSTShifted=false;
    }

    returnthis._isDSTShifted;
}

functionisLocal(){
    returnthis.isValid()?!this._isUTC:false;
}

functionisUtcOffset(){
    returnthis.isValid()?this._isUTC:false;
}

functionisUtc(){
    returnthis.isValid()?this._isUTC&&this._offset===0:false;
}

//ASP.NETjsondateformatregex
varaspNetRegex=/^(\-)?(?:(\d*)[.])?(\d+)\:(\d+)(?:\:(\d+)(\.\d*)?)?$/;

//fromhttp://docs.closure-library.googlecode.com/git/closure_goog_date_date.js.source.html
//somewhatmoreinlinewith4.4.3.22004spec,butallowsdecimalanywhere
//andfurthermodifiedtoallowforstringscontainingbothweekandday
varisoRegex=/^(-)?P(?:(-?[0-9,.]*)Y)?(?:(-?[0-9,.]*)M)?(?:(-?[0-9,.]*)W)?(?:(-?[0-9,.]*)D)?(?:T(?:(-?[0-9,.]*)H)?(?:(-?[0-9,.]*)M)?(?:(-?[0-9,.]*)S)?)?$/;

functioncreateDuration(input,key){
    varduration=input,
        //matchingagainstregexpisexpensive,doitondemand
        match=null,
        sign,
        ret,
        diffRes;

    if(isDuration(input)){
        duration={
            ms:input._milliseconds,
            d :input._days,
            M :input._months
        };
    }elseif(isNumber(input)){
        duration={};
        if(key){
            duration[key]=input;
        }else{
            duration.milliseconds=input;
        }
    }elseif(!!(match=aspNetRegex.exec(input))){
        sign=(match[1]==='-')?-1:1;
        duration={
            y :0,
            d :toInt(match[DATE])                        *sign,
            h :toInt(match[HOUR])                        *sign,
            m :toInt(match[MINUTE])                      *sign,
            s :toInt(match[SECOND])                      *sign,
            ms:toInt(absRound(match[MILLISECOND]*1000))*sign//themilliseconddecimalpointisincludedinthematch
        };
    }elseif(!!(match=isoRegex.exec(input))){
        sign=(match[1]==='-')?-1:1;
        duration={
            y:parseIso(match[2],sign),
            M:parseIso(match[3],sign),
            w:parseIso(match[4],sign),
            d:parseIso(match[5],sign),
            h:parseIso(match[6],sign),
            m:parseIso(match[7],sign),
            s:parseIso(match[8],sign)
        };
    }elseif(duration==null){//checksfornullorundefined
        duration={};
    }elseif(typeofduration==='object'&&('from'induration||'to'induration)){
        diffRes=momentsDifference(createLocal(duration.from),createLocal(duration.to));

        duration={};
        duration.ms=diffRes.milliseconds;
        duration.M=diffRes.months;
    }

    ret=newDuration(duration);

    if(isDuration(input)&&hasOwnProp(input,'_locale')){
        ret._locale=input._locale;
    }

    returnret;
}

createDuration.fn=Duration.prototype;

functionparseIso(inp,sign){
    //We'dnormallyuse~~inpforthis,butunfortunatelyitalso
    //convertsfloatstoints.
    //inpmaybeundefined,socarefulcallingreplaceonit.
    varres=inp&&parseFloat(inp.replace(',','.'));
    //applysignwhilewe'reatit
    return(isNaN(res)?0:res)*sign;
}

functionpositiveMomentsDifference(base,other){
    varres={milliseconds:0,months:0};

    res.months=other.month()-base.month()+
        (other.year()-base.year())*12;
    if(base.clone().add(res.months,'M').isAfter(other)){
        --res.months;
    }

    res.milliseconds=+other-+(base.clone().add(res.months,'M'));

    returnres;
}

functionmomentsDifference(base,other){
    varres;
    if(!(base.isValid()&&other.isValid())){
        return{milliseconds:0,months:0};
    }

    other=cloneWithOffset(other,base);
    if(base.isBefore(other)){
        res=positiveMomentsDifference(base,other);
    }else{
        res=positiveMomentsDifference(other,base);
        res.milliseconds=-res.milliseconds;
        res.months=-res.months;
    }

    returnres;
}

//TODO:remove'name'argafterdeprecationisremoved
functioncreateAdder(direction,name){
    returnfunction(val,period){
        vardur,tmp;
        //invertthearguments,butcomplainaboutit
        if(period!==null&&!isNaN(+period)){
            deprecateSimple(name,'moment().'+name +'(period,number)isdeprecated.Pleaseusemoment().'+name+'(number,period).'+
            'Seehttp://momentjs.com/guides/#/warnings/add-inverted-param/formoreinfo.');
            tmp=val;val=period;period=tmp;
        }

        val=typeofval==='string'?+val:val;
        dur=createDuration(val,period);
        addSubtract(this,dur,direction);
        returnthis;
    };
}

functionaddSubtract(mom,duration,isAdding,updateOffset){
    varmilliseconds=duration._milliseconds,
        days=absRound(duration._days),
        months=absRound(duration._months);

    if(!mom.isValid()){
        //Noop
        return;
    }

    updateOffset=updateOffset==null?true:updateOffset;

    if(milliseconds){
        mom._d.setTime(mom._d.valueOf()+milliseconds*isAdding);
    }
    if(days){
        set$1(mom,'Date',get(mom,'Date')+days*isAdding);
    }
    if(months){
        setMonth(mom,get(mom,'Month')+months*isAdding);
    }
    if(updateOffset){
        hooks.updateOffset(mom,days||months);
    }
}

varadd     =createAdder(1,'add');
varsubtract=createAdder(-1,'subtract');

functiongetCalendarFormat(myMoment,now){
    vardiff=myMoment.diff(now,'days',true);
    returndiff<-6?'sameElse':
            diff<-1?'lastWeek':
            diff<0?'lastDay':
            diff<1?'sameDay':
            diff<2?'nextDay':
            diff<7?'nextWeek':'sameElse';
}

functioncalendar$1(time,formats){
    //Wewanttocomparethestartoftoday,vsthis.
    //Gettingstart-of-todaydependsonwhetherwe'relocal/utc/offsetornot.
    varnow=time||createLocal(),
        sod=cloneWithOffset(now,this).startOf('day'),
        format=hooks.calendarFormat(this,sod)||'sameElse';

    varoutput=formats&&(isFunction(formats[format])?formats[format].call(this,now):formats[format]);

    returnthis.format(output||this.localeData().calendar(format,this,createLocal(now)));
}

functionclone(){
    returnnewMoment(this);
}

functionisAfter(input,units){
    varlocalInput=isMoment(input)?input:createLocal(input);
    if(!(this.isValid()&&localInput.isValid())){
        returnfalse;
    }
    units=normalizeUnits(!isUndefined(units)?units:'millisecond');
    if(units==='millisecond'){
        returnthis.valueOf()>localInput.valueOf();
    }else{
        returnlocalInput.valueOf()<this.clone().startOf(units).valueOf();
    }
}

functionisBefore(input,units){
    varlocalInput=isMoment(input)?input:createLocal(input);
    if(!(this.isValid()&&localInput.isValid())){
        returnfalse;
    }
    units=normalizeUnits(!isUndefined(units)?units:'millisecond');
    if(units==='millisecond'){
        returnthis.valueOf()<localInput.valueOf();
    }else{
        returnthis.clone().endOf(units).valueOf()<localInput.valueOf();
    }
}

functionisBetween(from,to,units,inclusivity){
    inclusivity=inclusivity||'()';
    return(inclusivity[0]==='('?this.isAfter(from,units):!this.isBefore(from,units))&&
        (inclusivity[1]===')'?this.isBefore(to,units):!this.isAfter(to,units));
}

functionisSame(input,units){
    varlocalInput=isMoment(input)?input:createLocal(input),
        inputMs;
    if(!(this.isValid()&&localInput.isValid())){
        returnfalse;
    }
    units=normalizeUnits(units||'millisecond');
    if(units==='millisecond'){
        returnthis.valueOf()===localInput.valueOf();
    }else{
        inputMs=localInput.valueOf();
        returnthis.clone().startOf(units).valueOf()<=inputMs&&inputMs<=this.clone().endOf(units).valueOf();
    }
}

functionisSameOrAfter(input,units){
    returnthis.isSame(input,units)||this.isAfter(input,units);
}

functionisSameOrBefore(input,units){
    returnthis.isSame(input,units)||this.isBefore(input,units);
}

functiondiff(input,units,asFloat){
    varthat,
        zoneDelta,
        delta,output;

    if(!this.isValid()){
        returnNaN;
    }

    that=cloneWithOffset(input,this);

    if(!that.isValid()){
        returnNaN;
    }

    zoneDelta=(that.utcOffset()-this.utcOffset())*6e4;

    units=normalizeUnits(units);

    if(units==='year'||units==='month'||units==='quarter'){
        output=monthDiff(this,that);
        if(units==='quarter'){
            output=output/3;
        }elseif(units==='year'){
            output=output/12;
        }
    }else{
        delta=this-that;
        output=units==='second'?delta/1e3://1000
            units==='minute'?delta/6e4://1000*60
            units==='hour'?delta/36e5://1000*60*60
            units==='day'?(delta-zoneDelta)/864e5://1000*60*60*24,negatedst
            units==='week'?(delta-zoneDelta)/6048e5://1000*60*60*24*7,negatedst
            delta;
    }
    returnasFloat?output:absFloor(output);
}

functionmonthDiff(a,b){
    //differenceinmonths
    varwholeMonthDiff=((b.year()-a.year())*12)+(b.month()-a.month()),
        //bisin(anchor-1month,anchor+1month)
        anchor=a.clone().add(wholeMonthDiff,'months'),
        anchor2,adjust;

    if(b-anchor<0){
        anchor2=a.clone().add(wholeMonthDiff-1,'months');
        //linearacrossthemonth
        adjust=(b-anchor)/(anchor-anchor2);
    }else{
        anchor2=a.clone().add(wholeMonthDiff+1,'months');
        //linearacrossthemonth
        adjust=(b-anchor)/(anchor2-anchor);
    }

    //checkfornegativezero,returnzeroifnegativezero
    return-(wholeMonthDiff+adjust)||0;
}

hooks.defaultFormat='YYYY-MM-DDTHH:mm:ssZ';
hooks.defaultFormatUtc='YYYY-MM-DDTHH:mm:ss[Z]';

functiontoString(){
    returnthis.clone().locale('en').format('dddMMMDDYYYYHH:mm:ss[GMT]ZZ');
}

functiontoISOString(){
    varm=this.clone().utc();
    if(0<m.year()&&m.year()<=9999){
        if(isFunction(Date.prototype.toISOString)){
            //nativeimplementationis~50xfaster,useitwhenwecan
            returnthis.toDate().toISOString();
        }else{
            returnformatMoment(m,'YYYY-MM-DD[T]HH:mm:ss.SSS[Z]');
        }
    }else{
        returnformatMoment(m,'YYYYYY-MM-DD[T]HH:mm:ss.SSS[Z]');
    }
}

/**
 *Returnahumanreadablerepresentationofamomentthatcan
 *alsobeevaluatedtogetanewmomentwhichisthesame
 *
 *@linkhttps://nodejs.org/dist/latest/docs/api/util.html#util_custom_inspect_function_on_objects
 */
functioninspect(){
    if(!this.isValid()){
        return'moment.invalid(/*'+this._i+'*/)';
    }
    varfunc='moment';
    varzone='';
    if(!this.isLocal()){
        func=this.utcOffset()===0?'moment.utc':'moment.parseZone';
        zone='Z';
    }
    varprefix='['+func+'("]';
    varyear=(0<this.year()&&this.year()<=9999)?'YYYY':'YYYYYY';
    vardatetime='-MM-DD[T]HH:mm:ss.SSS';
    varsuffix=zone+'[")]';

    returnthis.format(prefix+year+datetime+suffix);
}

functionformat(inputString){
    if(!inputString){
        inputString=this.isUtc()?hooks.defaultFormatUtc:hooks.defaultFormat;
    }
    varoutput=formatMoment(this,inputString);
    returnthis.localeData().postformat(output);
}

functionfrom(time,withoutSuffix){
    if(this.isValid()&&
            ((isMoment(time)&&time.isValid())||
             createLocal(time).isValid())){
        returncreateDuration({to:this,from:time}).locale(this.locale()).humanize(!withoutSuffix);
    }else{
        returnthis.localeData().invalidDate();
    }
}

functionfromNow(withoutSuffix){
    returnthis.from(createLocal(),withoutSuffix);
}

functionto(time,withoutSuffix){
    if(this.isValid()&&
            ((isMoment(time)&&time.isValid())||
             createLocal(time).isValid())){
        returncreateDuration({from:this,to:time}).locale(this.locale()).humanize(!withoutSuffix);
    }else{
        returnthis.localeData().invalidDate();
    }
}

functiontoNow(withoutSuffix){
    returnthis.to(createLocal(),withoutSuffix);
}

//Ifpassedalocalekey,itwillsetthelocaleforthis
//instance. Otherwise,itwillreturnthelocaleconfiguration
//variablesforthisinstance.
functionlocale(key){
    varnewLocaleData;

    if(key===undefined){
        returnthis._locale._abbr;
    }else{
        newLocaleData=getLocale(key);
        if(newLocaleData!=null){
            this._locale=newLocaleData;
        }
        returnthis;
    }
}

varlang=deprecate(
    'moment().lang()isdeprecated.Instead,usemoment().localeData()togetthelanguageconfiguration.Usemoment().locale()tochangelanguages.',
    function(key){
        if(key===undefined){
            returnthis.localeData();
        }else{
            returnthis.locale(key);
        }
    }
);

functionlocaleData(){
    returnthis._locale;
}

functionstartOf(units){
    units=normalizeUnits(units);
    //thefollowingswitchintentionallyomitsbreakkeywords
    //toutilizefallingthroughthecases.
    switch(units){
        case'year':
            this.month(0);
            /*fallsthrough*/
        case'quarter':
        case'month':
            this.date(1);
            /*fallsthrough*/
        case'week':
        case'isoWeek':
        case'day':
        case'date':
            this.hours(0);
            /*fallsthrough*/
        case'hour':
            this.minutes(0);
            /*fallsthrough*/
        case'minute':
            this.seconds(0);
            /*fallsthrough*/
        case'second':
            this.milliseconds(0);
    }

    //weeksareaspecialcase
    if(units==='week'){
        this.weekday(0);
    }
    if(units==='isoWeek'){
        this.isoWeekday(1);
    }

    //quartersarealsospecial
    if(units==='quarter'){
        this.month(Math.floor(this.month()/3)*3);
    }

    returnthis;
}

functionendOf(units){
    units=normalizeUnits(units);
    if(units===undefined||units==='millisecond'){
        returnthis;
    }

    //'date'isanaliasfor'day',soitshouldbeconsideredassuch.
    if(units==='date'){
        units='day';
    }

    returnthis.startOf(units).add(1,(units==='isoWeek'?'week':units)).subtract(1,'ms');
}

functionvalueOf(){
    returnthis._d.valueOf()-((this._offset||0)*60000);
}

functionunix(){
    returnMath.floor(this.valueOf()/1000);
}

functiontoDate(){
    returnnewDate(this.valueOf());
}

functiontoArray(){
    varm=this;
    return[m.year(),m.month(),m.date(),m.hour(),m.minute(),m.second(),m.millisecond()];
}

functiontoObject(){
    varm=this;
    return{
        years:m.year(),
        months:m.month(),
        date:m.date(),
        hours:m.hours(),
        minutes:m.minutes(),
        seconds:m.seconds(),
        milliseconds:m.milliseconds()
    };
}

functiontoJSON(){
    //newDate(NaN).toJSON()===null
    returnthis.isValid()?this.toISOString():null;
}

functionisValid$1(){
    returnisValid(this);
}

functionparsingFlags(){
    returnextend({},getParsingFlags(this));
}

functioninvalidAt(){
    returngetParsingFlags(this).overflow;
}

functioncreationData(){
    return{
        input:this._i,
        format:this._f,
        locale:this._locale,
        isUTC:this._isUTC,
        strict:this._strict
    };
}

//FORMATTING

addFormatToken(0,['gg',2],0,function(){
    returnthis.weekYear()%100;
});

addFormatToken(0,['GG',2],0,function(){
    returnthis.isoWeekYear()%100;
});

functionaddWeekYearFormatToken(token,getter){
    addFormatToken(0,[token,token.length],0,getter);
}

addWeekYearFormatToken('gggg',    'weekYear');
addWeekYearFormatToken('ggggg',   'weekYear');
addWeekYearFormatToken('GGGG', 'isoWeekYear');
addWeekYearFormatToken('GGGGG','isoWeekYear');

//ALIASES

addUnitAlias('weekYear','gg');
addUnitAlias('isoWeekYear','GG');

//PRIORITY

addUnitPriority('weekYear',1);
addUnitPriority('isoWeekYear',1);


//PARSING

addRegexToken('G',     matchSigned);
addRegexToken('g',     matchSigned);
addRegexToken('GG',    match1to2,match2);
addRegexToken('gg',    match1to2,match2);
addRegexToken('GGGG',  match1to4,match4);
addRegexToken('gggg',  match1to4,match4);
addRegexToken('GGGGG', match1to6,match6);
addRegexToken('ggggg', match1to6,match6);

addWeekParseToken(['gggg','ggggg','GGGG','GGGGG'],function(input,week,config,token){
    week[token.substr(0,2)]=toInt(input);
});

addWeekParseToken(['gg','GG'],function(input,week,config,token){
    week[token]=hooks.parseTwoDigitYear(input);
});

//MOMENTS

functiongetSetWeekYear(input){
    returngetSetWeekYearHelper.call(this,
            input,
            this.week(),
            this.weekday(),
            this.localeData()._week.dow,
            this.localeData()._week.doy);
}

functiongetSetISOWeekYear(input){
    returngetSetWeekYearHelper.call(this,
            input,this.isoWeek(),this.isoWeekday(),1,4);
}

functiongetISOWeeksInYear(){
    returnweeksInYear(this.year(),1,4);
}

functiongetWeeksInYear(){
    varweekInfo=this.localeData()._week;
    returnweeksInYear(this.year(),weekInfo.dow,weekInfo.doy);
}

functiongetSetWeekYearHelper(input,week,weekday,dow,doy){
    varweeksTarget;
    if(input==null){
        returnweekOfYear(this,dow,doy).year;
    }else{
        weeksTarget=weeksInYear(input,dow,doy);
        if(week>weeksTarget){
            week=weeksTarget;
        }
        returnsetWeekAll.call(this,input,week,weekday,dow,doy);
    }
}

functionsetWeekAll(weekYear,week,weekday,dow,doy){
    vardayOfYearData=dayOfYearFromWeeks(weekYear,week,weekday,dow,doy),
        date=createUTCDate(dayOfYearData.year,0,dayOfYearData.dayOfYear);

    this.year(date.getUTCFullYear());
    this.month(date.getUTCMonth());
    this.date(date.getUTCDate());
    returnthis;
}

//FORMATTING

addFormatToken('Q',0,'Qo','quarter');

//ALIASES

addUnitAlias('quarter','Q');

//PRIORITY

addUnitPriority('quarter',7);

//PARSING

addRegexToken('Q',match1);
addParseToken('Q',function(input,array){
    array[MONTH]=(toInt(input)-1)*3;
});

//MOMENTS

functiongetSetQuarter(input){
    returninput==null?Math.ceil((this.month()+1)/3):this.month((input-1)*3+this.month()%3);
}

//FORMATTING

addFormatToken('D',['DD',2],'Do','date');

//ALIASES

addUnitAlias('date','D');

//PRIOROITY
addUnitPriority('date',9);

//PARSING

addRegexToken('D', match1to2);
addRegexToken('DD',match1to2,match2);
addRegexToken('Do',function(isStrict,locale){
    returnisStrict?locale._ordinalParse:locale._ordinalParseLenient;
});

addParseToken(['D','DD'],DATE);
addParseToken('Do',function(input,array){
    array[DATE]=toInt(input.match(match1to2)[0],10);
});

//MOMENTS

vargetSetDayOfMonth=makeGetSet('Date',true);

//FORMATTING

addFormatToken('DDD',['DDDD',3],'DDDo','dayOfYear');

//ALIASES

addUnitAlias('dayOfYear','DDD');

//PRIORITY
addUnitPriority('dayOfYear',4);

//PARSING

addRegexToken('DDD', match1to3);
addRegexToken('DDDD',match3);
addParseToken(['DDD','DDDD'],function(input,array,config){
    config._dayOfYear=toInt(input);
});

//HELPERS

//MOMENTS

functiongetSetDayOfYear(input){
    vardayOfYear=Math.round((this.clone().startOf('day')-this.clone().startOf('year'))/864e5)+1;
    returninput==null?dayOfYear:this.add((input-dayOfYear),'d');
}

//FORMATTING

addFormatToken('m',['mm',2],0,'minute');

//ALIASES

addUnitAlias('minute','m');

//PRIORITY

addUnitPriority('minute',14);

//PARSING

addRegexToken('m', match1to2);
addRegexToken('mm',match1to2,match2);
addParseToken(['m','mm'],MINUTE);

//MOMENTS

vargetSetMinute=makeGetSet('Minutes',false);

//FORMATTING

addFormatToken('s',['ss',2],0,'second');

//ALIASES

addUnitAlias('second','s');

//PRIORITY

addUnitPriority('second',15);

//PARSING

addRegexToken('s', match1to2);
addRegexToken('ss',match1to2,match2);
addParseToken(['s','ss'],SECOND);

//MOMENTS

vargetSetSecond=makeGetSet('Seconds',false);

//FORMATTING

addFormatToken('S',0,0,function(){
    return~~(this.millisecond()/100);
});

addFormatToken(0,['SS',2],0,function(){
    return~~(this.millisecond()/10);
});

addFormatToken(0,['SSS',3],0,'millisecond');
addFormatToken(0,['SSSS',4],0,function(){
    returnthis.millisecond()*10;
});
addFormatToken(0,['SSSSS',5],0,function(){
    returnthis.millisecond()*100;
});
addFormatToken(0,['SSSSSS',6],0,function(){
    returnthis.millisecond()*1000;
});
addFormatToken(0,['SSSSSSS',7],0,function(){
    returnthis.millisecond()*10000;
});
addFormatToken(0,['SSSSSSSS',8],0,function(){
    returnthis.millisecond()*100000;
});
addFormatToken(0,['SSSSSSSSS',9],0,function(){
    returnthis.millisecond()*1000000;
});


//ALIASES

addUnitAlias('millisecond','ms');

//PRIORITY

addUnitPriority('millisecond',16);

//PARSING

addRegexToken('S',   match1to3,match1);
addRegexToken('SS',  match1to3,match2);
addRegexToken('SSS', match1to3,match3);

vartoken;
for(token='SSSS';token.length<=9;token+='S'){
    addRegexToken(token,matchUnsigned);
}

functionparseMs(input,array){
    array[MILLISECOND]=toInt(('0.'+input)*1000);
}

for(token='S';token.length<=9;token+='S'){
    addParseToken(token,parseMs);
}
//MOMENTS

vargetSetMillisecond=makeGetSet('Milliseconds',false);

//FORMATTING

addFormatToken('z', 0,0,'zoneAbbr');
addFormatToken('zz',0,0,'zoneName');

//MOMENTS

functiongetZoneAbbr(){
    returnthis._isUTC?'UTC':'';
}

functiongetZoneName(){
    returnthis._isUTC?'CoordinatedUniversalTime':'';
}

varproto=Moment.prototype;

proto.add              =add;
proto.calendar         =calendar$1;
proto.clone            =clone;
proto.diff             =diff;
proto.endOf            =endOf;
proto.format           =format;
proto.from             =from;
proto.fromNow          =fromNow;
proto.to               =to;
proto.toNow            =toNow;
proto.get              =stringGet;
proto.invalidAt        =invalidAt;
proto.isAfter          =isAfter;
proto.isBefore         =isBefore;
proto.isBetween        =isBetween;
proto.isSame           =isSame;
proto.isSameOrAfter    =isSameOrAfter;
proto.isSameOrBefore   =isSameOrBefore;
proto.isValid          =isValid$1;
proto.lang             =lang;
proto.locale           =locale;
proto.localeData       =localeData;
proto.max              =prototypeMax;
proto.min              =prototypeMin;
proto.parsingFlags     =parsingFlags;
proto.set              =stringSet;
proto.startOf          =startOf;
proto.subtract         =subtract;
proto.toArray          =toArray;
proto.toObject         =toObject;
proto.toDate           =toDate;
proto.toISOString      =toISOString;
proto.inspect          =inspect;
proto.toJSON           =toJSON;
proto.toString         =toString;
proto.unix             =unix;
proto.valueOf          =valueOf;
proto.creationData     =creationData;

//Year
proto.year      =getSetYear;
proto.isLeapYear=getIsLeapYear;

//WeekYear
proto.weekYear   =getSetWeekYear;
proto.isoWeekYear=getSetISOWeekYear;

//Quarter
proto.quarter=proto.quarters=getSetQuarter;

//Month
proto.month      =getSetMonth;
proto.daysInMonth=getDaysInMonth;

//Week
proto.week          =proto.weeks       =getSetWeek;
proto.isoWeek       =proto.isoWeeks    =getSetISOWeek;
proto.weeksInYear   =getWeeksInYear;
proto.isoWeeksInYear=getISOWeeksInYear;

//Day
proto.date      =getSetDayOfMonth;
proto.day       =proto.days            =getSetDayOfWeek;
proto.weekday   =getSetLocaleDayOfWeek;
proto.isoWeekday=getSetISODayOfWeek;
proto.dayOfYear =getSetDayOfYear;

//Hour
proto.hour=proto.hours=getSetHour;

//Minute
proto.minute=proto.minutes=getSetMinute;

//Second
proto.second=proto.seconds=getSetSecond;

//Millisecond
proto.millisecond=proto.milliseconds=getSetMillisecond;

//Offset
proto.utcOffset           =getSetOffset;
proto.utc                 =setOffsetToUTC;
proto.local               =setOffsetToLocal;
proto.parseZone           =setOffsetToParsedOffset;
proto.hasAlignedHourOffset=hasAlignedHourOffset;
proto.isDST               =isDaylightSavingTime;
proto.isLocal             =isLocal;
proto.isUtcOffset         =isUtcOffset;
proto.isUtc               =isUtc;
proto.isUTC               =isUtc;

//Timezone
proto.zoneAbbr=getZoneAbbr;
proto.zoneName=getZoneName;

//Deprecations
proto.dates =deprecate('datesaccessorisdeprecated.Usedateinstead.',getSetDayOfMonth);
proto.months=deprecate('monthsaccessorisdeprecated.Usemonthinstead',getSetMonth);
proto.years =deprecate('yearsaccessorisdeprecated.Useyearinstead',getSetYear);
proto.zone  =deprecate('moment().zoneisdeprecated,usemoment().utcOffsetinstead.http://momentjs.com/guides/#/warnings/zone/',getSetZone);
proto.isDSTShifted=deprecate('isDSTShiftedisdeprecated.Seehttp://momentjs.com/guides/#/warnings/dst-shifted/formoreinformation',isDaylightSavingTimeShifted);

functioncreateUnix(input){
    returncreateLocal(input*1000);
}

functioncreateInZone(){
    returncreateLocal.apply(null,arguments).parseZone();
}

functionpreParsePostFormat(string){
    returnstring;
}

varproto$1=Locale.prototype;

proto$1.calendar       =calendar;
proto$1.longDateFormat =longDateFormat;
proto$1.invalidDate    =invalidDate;
proto$1.ordinal        =ordinal;
proto$1.preparse       =preParsePostFormat;
proto$1.postformat     =preParsePostFormat;
proto$1.relativeTime   =relativeTime;
proto$1.pastFuture     =pastFuture;
proto$1.set            =set;

//Month
proto$1.months           =       localeMonths;
proto$1.monthsShort      =       localeMonthsShort;
proto$1.monthsParse      =       localeMonthsParse;
proto$1.monthsRegex      =monthsRegex;
proto$1.monthsShortRegex =monthsShortRegex;

//Week
proto$1.week=localeWeek;
proto$1.firstDayOfYear=localeFirstDayOfYear;
proto$1.firstDayOfWeek=localeFirstDayOfWeek;

//DayofWeek
proto$1.weekdays      =       localeWeekdays;
proto$1.weekdaysMin   =       localeWeekdaysMin;
proto$1.weekdaysShort =       localeWeekdaysShort;
proto$1.weekdaysParse =       localeWeekdaysParse;

proto$1.weekdaysRegex      =       weekdaysRegex;
proto$1.weekdaysShortRegex =       weekdaysShortRegex;
proto$1.weekdaysMinRegex   =       weekdaysMinRegex;

//Hours
proto$1.isPM=localeIsPM;
proto$1.meridiem=localeMeridiem;

functionget$1(format,index,field,setter){
    varlocale=getLocale();
    varutc=createUTC().set(setter,index);
    returnlocale[field](utc,format);
}

functionlistMonthsImpl(format,index,field){
    if(isNumber(format)){
        index=format;
        format=undefined;
    }

    format=format||'';

    if(index!=null){
        returnget$1(format,index,field,'month');
    }

    vari;
    varout=[];
    for(i=0;i<12;i++){
        out[i]=get$1(format,i,field,'month');
    }
    returnout;
}

//()
//(5)
//(fmt,5)
//(fmt)
//(true)
//(true,5)
//(true,fmt,5)
//(true,fmt)
functionlistWeekdaysImpl(localeSorted,format,index,field){
    if(typeoflocaleSorted==='boolean'){
        if(isNumber(format)){
            index=format;
            format=undefined;
        }

        format=format||'';
    }else{
        format=localeSorted;
        index=format;
        localeSorted=false;

        if(isNumber(format)){
            index=format;
            format=undefined;
        }

        format=format||'';
    }

    varlocale=getLocale(),
        shift=localeSorted?locale._week.dow:0;

    if(index!=null){
        returnget$1(format,(index+shift)%7,field,'day');
    }

    vari;
    varout=[];
    for(i=0;i<7;i++){
        out[i]=get$1(format,(i+shift)%7,field,'day');
    }
    returnout;
}

functionlistMonths(format,index){
    returnlistMonthsImpl(format,index,'months');
}

functionlistMonthsShort(format,index){
    returnlistMonthsImpl(format,index,'monthsShort');
}

functionlistWeekdays(localeSorted,format,index){
    returnlistWeekdaysImpl(localeSorted,format,index,'weekdays');
}

functionlistWeekdaysShort(localeSorted,format,index){
    returnlistWeekdaysImpl(localeSorted,format,index,'weekdaysShort');
}

functionlistWeekdaysMin(localeSorted,format,index){
    returnlistWeekdaysImpl(localeSorted,format,index,'weekdaysMin');
}

getSetGlobalLocale('en',{
    ordinalParse:/\d{1,2}(th|st|nd|rd)/,
    ordinal:function(number){
        varb=number%10,
            output=(toInt(number%100/10)===1)?'th':
            (b===1)?'st':
            (b===2)?'nd':
            (b===3)?'rd':'th';
        returnnumber+output;
    }
});

//Sideeffectimports
hooks.lang=deprecate('moment.langisdeprecated.Usemoment.localeinstead.',getSetGlobalLocale);
hooks.langData=deprecate('moment.langDataisdeprecated.Usemoment.localeDatainstead.',getLocale);

varmathAbs=Math.abs;

functionabs(){
    vardata          =this._data;

    this._milliseconds=mathAbs(this._milliseconds);
    this._days        =mathAbs(this._days);
    this._months      =mathAbs(this._months);

    data.milliseconds =mathAbs(data.milliseconds);
    data.seconds      =mathAbs(data.seconds);
    data.minutes      =mathAbs(data.minutes);
    data.hours        =mathAbs(data.hours);
    data.months       =mathAbs(data.months);
    data.years        =mathAbs(data.years);

    returnthis;
}

functionaddSubtract$1(duration,input,value,direction){
    varother=createDuration(input,value);

    duration._milliseconds+=direction*other._milliseconds;
    duration._days        +=direction*other._days;
    duration._months      +=direction*other._months;

    returnduration._bubble();
}

//supportsonly2.0-styleadd(1,'s')oradd(duration)
functionadd$1(input,value){
    returnaddSubtract$1(this,input,value,1);
}

//supportsonly2.0-stylesubtract(1,'s')orsubtract(duration)
functionsubtract$1(input,value){
    returnaddSubtract$1(this,input,value,-1);
}

functionabsCeil(number){
    if(number<0){
        returnMath.floor(number);
    }else{
        returnMath.ceil(number);
    }
}

functionbubble(){
    varmilliseconds=this._milliseconds;
    vardays        =this._days;
    varmonths      =this._months;
    vardata        =this._data;
    varseconds,minutes,hours,years,monthsFromDays;

    //ifwehaveamixofpositiveandnegativevalues,bubbledownfirst
    //check:https://github.com/moment/moment/issues/2166
    if(!((milliseconds>=0&&days>=0&&months>=0)||
            (milliseconds<=0&&days<=0&&months<=0))){
        milliseconds+=absCeil(monthsToDays(months)+days)*864e5;
        days=0;
        months=0;
    }

    //Thefollowingcodebubblesupvalues,seethetestsfor
    //examplesofwhatthatmeans.
    data.milliseconds=milliseconds%1000;

    seconds          =absFloor(milliseconds/1000);
    data.seconds     =seconds%60;

    minutes          =absFloor(seconds/60);
    data.minutes     =minutes%60;

    hours            =absFloor(minutes/60);
    data.hours       =hours%24;

    days+=absFloor(hours/24);

    //convertdaystomonths
    monthsFromDays=absFloor(daysToMonths(days));
    months+=monthsFromDays;
    days-=absCeil(monthsToDays(monthsFromDays));

    //12months->1year
    years=absFloor(months/12);
    months%=12;

    data.days  =days;
    data.months=months;
    data.years =years;

    returnthis;
}

functiondaysToMonths(days){
    //400yearshave146097days(takingintoaccountleapyearrules)
    //400yearshave12months===4800
    returndays*4800/146097;
}

functionmonthsToDays(months){
    //thereverseofdaysToMonths
    returnmonths*146097/4800;
}

functionas(units){
    vardays;
    varmonths;
    varmilliseconds=this._milliseconds;

    units=normalizeUnits(units);

    if(units==='month'||units==='year'){
        days  =this._days  +milliseconds/864e5;
        months=this._months+daysToMonths(days);
        returnunits==='month'?months:months/12;
    }else{
        //handlemillisecondsseparatelybecauseoffloatingpointmatherrors(issue#1867)
        days=this._days+Math.round(monthsToDays(this._months));
        switch(units){
            case'week'  :returndays/7    +milliseconds/6048e5;
            case'day'   :returndays        +milliseconds/864e5;
            case'hour'  :returndays*24   +milliseconds/36e5;
            case'minute':returndays*1440 +milliseconds/6e4;
            case'second':returndays*86400+milliseconds/1000;
            //Math.floorpreventsfloatingpointmatherrorshere
            case'millisecond':returnMath.floor(days*864e5)+milliseconds;
            default:thrownewError('Unknownunit'+units);
        }
    }
}

//TODO:Usethis.as('ms')?
functionvalueOf$1(){
    return(
        this._milliseconds+
        this._days*864e5+
        (this._months%12)*2592e6+
        toInt(this._months/12)*31536e6
    );
}

functionmakeAs(alias){
    returnfunction(){
        returnthis.as(alias);
    };
}

varasMilliseconds=makeAs('ms');
varasSeconds     =makeAs('s');
varasMinutes     =makeAs('m');
varasHours       =makeAs('h');
varasDays        =makeAs('d');
varasWeeks       =makeAs('w');
varasMonths      =makeAs('M');
varasYears       =makeAs('y');

functionget$2(units){
    units=normalizeUnits(units);
    returnthis[units+'s']();
}

functionmakeGetter(name){
    returnfunction(){
        returnthis._data[name];
    };
}

varmilliseconds=makeGetter('milliseconds');
varseconds     =makeGetter('seconds');
varminutes     =makeGetter('minutes');
varhours       =makeGetter('hours');
vardays        =makeGetter('days');
varmonths      =makeGetter('months');
varyears       =makeGetter('years');

functionweeks(){
    returnabsFloor(this.days()/7);
}

varround=Math.round;
varthresholds={
    s:45, //secondstominute
    m:45, //minutestohour
    h:22, //hourstoday
    d:26, //daystomonth
    M:11  //monthstoyear
};

//helperfunctionformoment.fn.from,moment.fn.fromNow,andmoment.duration.fn.humanize
functionsubstituteTimeAgo(string,number,withoutSuffix,isFuture,locale){
    returnlocale.relativeTime(number||1,!!withoutSuffix,string,isFuture);
}

functionrelativeTime$1(posNegDuration,withoutSuffix,locale){
    varduration=createDuration(posNegDuration).abs();
    varseconds =round(duration.as('s'));
    varminutes =round(duration.as('m'));
    varhours   =round(duration.as('h'));
    vardays    =round(duration.as('d'));
    varmonths  =round(duration.as('M'));
    varyears   =round(duration.as('y'));

    vara=seconds<thresholds.s&&['s',seconds] ||
            minutes<=1          &&['m']          ||
            minutes<thresholds.m&&['mm',minutes]||
            hours  <=1          &&['h']          ||
            hours  <thresholds.h&&['hh',hours]  ||
            days   <=1          &&['d']          ||
            days   <thresholds.d&&['dd',days]   ||
            months <=1          &&['M']          ||
            months <thresholds.M&&['MM',months] ||
            years  <=1          &&['y']          ||['yy',years];

    a[2]=withoutSuffix;
    a[3]=+posNegDuration>0;
    a[4]=locale;
    returnsubstituteTimeAgo.apply(null,a);
}

//Thisfunctionallowsyoutosettheroundingfunctionforrelativetimestrings
functiongetSetRelativeTimeRounding(roundingFunction){
    if(roundingFunction===undefined){
        returnround;
    }
    if(typeof(roundingFunction)==='function'){
        round=roundingFunction;
        returntrue;
    }
    returnfalse;
}

//Thisfunctionallowsyoutosetathresholdforrelativetimestrings
functiongetSetRelativeTimeThreshold(threshold,limit){
    if(thresholds[threshold]===undefined){
        returnfalse;
    }
    if(limit===undefined){
        returnthresholds[threshold];
    }
    thresholds[threshold]=limit;
    returntrue;
}

functionhumanize(withSuffix){
    varlocale=this.localeData();
    varoutput=relativeTime$1(this,!withSuffix,locale);

    if(withSuffix){
        output=locale.pastFuture(+this,output);
    }

    returnlocale.postformat(output);
}

varabs$1=Math.abs;

functiontoISOString$1(){
    //forISOstringswedonotusethenormalbubblingrules:
    // *millisecondsbubbleupuntiltheybecomehours
    // *daysdonotbubbleatall
    // *monthsbubbleupuntiltheybecomeyears
    //Thisisbecausethereisnocontext-freeconversionbetweenhoursanddays
    //(thinkofclockchanges)
    //andalsonotbetweendaysandmonths(28-31dayspermonth)
    varseconds=abs$1(this._milliseconds)/1000;
    vardays        =abs$1(this._days);
    varmonths      =abs$1(this._months);
    varminutes,hours,years;

    //3600seconds->60minutes->1hour
    minutes          =absFloor(seconds/60);
    hours            =absFloor(minutes/60);
    seconds%=60;
    minutes%=60;

    //12months->1year
    years =absFloor(months/12);
    months%=12;


    //inspiredbyhttps://github.com/dordille/moment-isoduration/blob/master/moment.isoduration.js
    varY=years;
    varM=months;
    varD=days;
    varh=hours;
    varm=minutes;
    vars=seconds;
    vartotal=this.asSeconds();

    if(!total){
        //thisisthesameasC#'s(Noda)andpython(isodate)...
        //butnototherJS(goog.date)
        return'P0D';
    }

    return(total<0?'-':'')+
        'P'+
        (Y?Y+'Y':'')+
        (M?M+'M':'')+
        (D?D+'D':'')+
        ((h||m||s)?'T':'')+
        (h?h+'H':'')+
        (m?m+'M':'')+
        (s?s+'S':'');
}

varproto$2=Duration.prototype;

proto$2.abs           =abs;
proto$2.add           =add$1;
proto$2.subtract      =subtract$1;
proto$2.as            =as;
proto$2.asMilliseconds=asMilliseconds;
proto$2.asSeconds     =asSeconds;
proto$2.asMinutes     =asMinutes;
proto$2.asHours       =asHours;
proto$2.asDays        =asDays;
proto$2.asWeeks       =asWeeks;
proto$2.asMonths      =asMonths;
proto$2.asYears       =asYears;
proto$2.valueOf       =valueOf$1;
proto$2._bubble       =bubble;
proto$2.get           =get$2;
proto$2.milliseconds  =milliseconds;
proto$2.seconds       =seconds;
proto$2.minutes       =minutes;
proto$2.hours         =hours;
proto$2.days          =days;
proto$2.weeks         =weeks;
proto$2.months        =months;
proto$2.years         =years;
proto$2.humanize      =humanize;
proto$2.toISOString   =toISOString$1;
proto$2.toString      =toISOString$1;
proto$2.toJSON        =toISOString$1;
proto$2.locale        =locale;
proto$2.localeData    =localeData;

//Deprecations
proto$2.toIsoString=deprecate('toIsoString()isdeprecated.PleaseusetoISOString()instead(noticethecapitals)',toISOString$1);
proto$2.lang=lang;

//Sideeffectimports

//FORMATTING

addFormatToken('X',0,0,'unix');
addFormatToken('x',0,0,'valueOf');

//PARSING

addRegexToken('x',matchSigned);
addRegexToken('X',matchTimestamp);
addParseToken('X',function(input,array,config){
    config._d=newDate(parseFloat(input,10)*1000);
});
addParseToken('x',function(input,array,config){
    config._d=newDate(toInt(input));
});

//Sideeffectimports


hooks.version='2.17.1';

setHookCallback(createLocal);

hooks.fn                   =proto;
hooks.min                  =min;
hooks.max                  =max;
hooks.now                  =now;
hooks.utc                  =createUTC;
hooks.unix                 =createUnix;
hooks.months               =listMonths;
hooks.isDate               =isDate;
hooks.locale               =getSetGlobalLocale;
hooks.invalid              =createInvalid;
hooks.duration             =createDuration;
hooks.isMoment             =isMoment;
hooks.weekdays             =listWeekdays;
hooks.parseZone            =createInZone;
hooks.localeData           =getLocale;
hooks.isDuration           =isDuration;
hooks.monthsShort          =listMonthsShort;
hooks.weekdaysMin          =listWeekdaysMin;
hooks.defineLocale         =defineLocale;
hooks.updateLocale         =updateLocale;
hooks.locales              =listLocales;
hooks.weekdaysShort        =listWeekdaysShort;
hooks.normalizeUnits       =normalizeUnits;
hooks.relativeTimeRounding=getSetRelativeTimeRounding;
hooks.relativeTimeThreshold=getSetRelativeTimeThreshold;
hooks.calendarFormat       =getCalendarFormat;
hooks.prototype            =proto;

returnhooks;

})));
