flectra.define('web.field_utils',function(require){
"usestrict";

/**
 *FieldUtils
 *
 *Thisfilecontainstwotypesoffunctions:formattingfunctionsandparsing
 *functions.
 *
 *Eachfieldtypehastodisplayinstringformatsomepoint,butitshouldbe
 *storedinmemorywiththeactualvalue. Forexample,afloatvalueof0.5is
 *representedasthestring"0.5"butiskeptinmemoryasafloat. Adate
 *(ordatetime)valueisalwaysstoredasaMoment.jsobject,butdisplayedas
 *astring. Thisfilecontainsallsortoffunctionsnecessarytoperformthe
 *conversions.
 */

varcore=require('web.core');
vardom=require('web.dom');
varsession=require('web.session');
vartime=require('web.time');
varutils=require('web.utils');

var_t=core._t;

constNBSP="\u00a0";

//------------------------------------------------------------------------------
//Formatting
//------------------------------------------------------------------------------

/**
 *Convertbinarytobin_size
 *
 *@param{string}[value]base64representationofthebinary(mightbealreadyabin_size!)
 *@param{Object}[field]
 *       adescriptionofthefield(note:thisparameterisignored)
 *@param{Object}[options]additionaloptions(note:thisparameterisignored)
 *
 *@returns{string}bin_size(whichishuman-readable)
 */
functionformatBinary(value,field,options){
    if(!value){
        return'';
    }
    returnutils.binaryToBinsize(value);
}

/**
 *@todoReally?itreturnsajQueryelement... Weshouldtrytoavoidthisand
 *letDOMutilityfunctionshandlethisdirectly.Andreplacethiswitha
 *functionthatreturnsastringsowecangetridoftheforceString.
 *
 *@param{boolean}value
 *@param{Object}[field]
 *       adescriptionofthefield(note:thisparameterisignored)
 *@param{Object}[options]additionaloptions
 *@param{boolean}[options.forceString=false]iftrue,returnsastring
*   representationofthebooleanratherthanajQueryElement
 *@returns{jQuery|string}
 */
functionformatBoolean(value,field,options){
    if(options&&options.forceString){
        returnvalue?_t('True'):_t('False');
    }
    returndom.renderCheckbox({
        prop:{
            checked:value,
            disabled:true,
        },
    });
}

/**
 *Returnsastringrepresentingachar. Ifthevalueisfalse,thenwereturn
 *anemptystring.
 *
 *@param{string|false}value
 *@param{Object}[field]
 *       adescriptionofthefield(note:thisparameterisignored)
 *@param{Object}[options]additionaloptions
 *@param{boolean}[options.escape=false]iftrue,escapestheformattedvalue
 *@param{boolean}[options.isPassword=false]iftrue,returns'********'
 *  insteadoftheformattedvalue
 *@returns{string}
 */
functionformatChar(value,field,options){
    value=typeofvalue==='string'?value:'';
    if(options&&options.isPassword){
        return_.str.repeat('*',value?value.length:0);
    }
    if(options&&options.escape){
        value=_.escape(value);
    }
    returnvalue;
}

/**
 *Returnsastringrepresentingadate. Ifthevalueisfalse,thenwereturn
 *anemptystring.Notethatthisisdependantonthelocalizationsettings
 *
 *@param{Moment|false}value
 *@param{Object}[field]
 *       adescriptionofthefield(note:thisparameterisignored)
 *@param{Object}[options]additionaloptions
 *@param{boolean}[options.timezone=true]usetheusertimezonewhenformatingthe
 *       date
 *@returns{string}
 */
functionformatDate(value,field,options){
    if(value===false||isNaN(value)){
        return"";
    }
    if(field&&field.type==='datetime'){
        if(!options||!('timezone'inoptions)||options.timezone){
            value=value.clone().add(session.getTZOffset(value),'minutes');
        }
    }
    vardate_format=time.getLangDateFormat();
    returnvalue.format(date_format);
}

/**
 *Returnsastringrepresentingadatetime. Ifthevalueisfalse,thenwe
 *returnanemptystring. Notethatthisisdependantonthelocalization
 *settings
 *
 *@params{Moment|false}
 *@param{Object}[field]
 *       adescriptionofthefield(note:thisparameterisignored)
 *@param{Object}[options]additionaloptions
 *@param{boolean}[options.timezone=true]usetheusertimezonewhenformatingthe
 *       date
 *@returns{string}
 */
functionformatDateTime(value,field,options){
    if(value===false){
        return"";
    }
    if(!options||!('timezone'inoptions)||options.timezone){
        value=value.clone().add(session.getTZOffset(value),'minutes');
    }
    returnvalue.format(time.getLangDatetimeFormat());
}

/**
 *Returnsastringrepresentingafloat. Theresulttakesintoaccountthe
 *usersettings(todisplaythecorrectdecimalseparator).
 *
 *@param{float|false}valuethevaluethatshouldbeformatted
 *@param{Object}[field]adescriptionofthefield(returnedbyfields_get
 *  forexample). Itmaycontainadescriptionofthenumberofdigitsthat
 *  shouldbeused.
 *@param{Object}[options]additionaloptionstooverridethevaluesinthe
 *  pythondescriptionofthefield.
 *@param{integer[]}[options.digits]thenumberofdigitsthatshouldbeused,
 *  insteadofthedefaultdigitsprecisioninthefield.
 *@param{function}[options.humanReadable]ifreturnstrue,
 *  formatFloatactslikeutils.human_number
 *@returns{string}
 */
functionformatFloat(value,field,options){
    options=options||{};
    if(value===false){
        return"";
    }
    if(options.humanReadable&&options.humanReadable(value)){
        returnutils.human_number(value,options.decimals,options.minDigits,options.formatterCallback);
    }
    varl10n=core._t.database.parameters;
    varprecision;
    if(options.digits){
        precision=options.digits[1];
    }elseif(field&&field.digits){
        precision=field.digits[1];
    }else{
        precision=2;
    }
    varformatted=_.str.sprintf('%.'+precision+'f',value||0).split('.');
    formatted[0]=utils.insert_thousand_seps(formatted[0]);
    returnformatted.join(l10n.decimal_point);
}


/**
 *Returnsastringrepresentingafloatvalue,fromafloatconvertedwitha
 *factor.
 *
 *@param{number}value
 *@param{number}[options.factor]
 *         Conversionfactor,defaultvalueis1.0
 *@returns{string}
 */
functionformatFloatFactor(value,field,options){
    varfactor=options.factor||1;
    returnformatFloat(value*factor,field,options);
}

/**
 *Returnsastringrepresentingatimevalue,fromafloat. Theideaisthat
 *wesometimeswanttodisplaysomethinglike1:45insteadof1.75,or0:15
 *insteadof0.25.
 *
 *@param{float}value
 *@param{Object}[field]
 *       adescriptionofthefield(note:thisparameterisignored)
 *@param{Object}[options]
 *@param{boolean}[options.noLeadingZeroHour]iftrue,formatlike1:30
 *       otherwise,formatlike01:30
 *@returns{string}
 */
functionformatFloatTime(value,field,options){
    options=options||{};
    varpattern=options.noLeadingZeroHour?'%1d:%02d':'%02d:%02d';
    if(value<0){
        value=Math.abs(value);
        pattern='-'+pattern;
    }
    varhour=Math.floor(value);
    varmin=Math.round((value%1)*60);
    if(min===60){
        min=0;
        hour=hour+1;
    }
    return_.str.sprintf(pattern,hour,min);
}

/**
 *Returnsastringrepresentinganinteger. Ifthevalueisfalse,thenwe
 *returnanemptystring.
 *
 *@param{integer|false}value
 *@param{Object}[field]
 *       adescriptionofthefield(note:thisparameterisignored)
 *@param{Object}[options]additionaloptions
 *@param{boolean}[options.isPassword=false]iftrue,returns'********'
 *@param{function}[options.humanReadable]ifreturnstrue,
 *  formatFloatactslikeutils.human_number
 *@returns{string}
 */
functionformatInteger(value,field,options){
    options=options||{};
    if(options.isPassword){
        return_.str.repeat('*',String(value).length);
    }
    if(!value&&value!==0){
        //previously,itreturned'false'.Idon'tknowwhy. ButforthePivot
        //view,Iwanttodisplaytheconceptof'novalue'withanempty
        //string.
        return"";
    }
    if(options.humanReadable&&options.humanReadable(value)){
        returnutils.human_number(value,options.decimals,options.minDigits,options.formatterCallback);
    }
    returnutils.insert_thousand_seps(_.str.sprintf('%d',value));
}

/**
 *Returnsastringrepresentinganmany2one. Ifthevalueisfalse,thenwe
 *returnanemptystring. Notethatitacceptstwotypesofinputparameters:
 *anarray,inthatcaseweassumethatthemany2onevalueisoftheform
 *[id,nameget],andwereturnthenameget,oritcanbeanobject,andinthat
 *case,weassumethatitisarecorddatapointfromaBasicModel.
 *
 *@param{Array|Object|false}value
 *@param{Object}[field]
 *       adescriptionofthefield(note:thisparameterisignored)
 *@param{Object}[options]additionaloptions
 *@param{boolean}[options.escape=false]iftrue,escapestheformattedvalue
 *@returns{string}
 */
functionformatMany2one(value,field,options){
    if(!value){
        value='';
    }elseif(_.isArray(value)){
        //valueisapair[id,nameget]
        value=value[1];
    }else{
        //valueisadatapoint,sowereaditsdisplay_namefield,which
        //mayinturnbeadatapoint(ifthenamefieldisamany2one)
        while(value.data){
            value=value.data.display_name||'';
        }
    }
    if(options&&options.escape){
        value=_.escape(value);
    }
    returnvalue;
}

/**
 *Returnsastringindicatingthenumberofrecordsintherelation.
 *
 *@param{Object}valueavalidelementfromaBasicModel,thatrepresentsa
 *  listofvalues
 *@returns{string}
 */
functionformatX2Many(value){
    if(value.data.length===0){
        return_t('Norecords');
    }elseif(value.data.length===1){
        return_t('1record');
    }else{
        returnvalue.data.length+_t('records');
    }
}

/**
 *Returnsastringrepresentingamonetaryvalue.Theresulttakesintoaccount
 *theusersettings(todisplaythecorrectdecimalseparator,currency,...).
 *
 *@param{float|false}valuethevaluethatshouldbeformatted
 *@param{Object}[field]
 *       adescriptionofthefield(returnedbyfields_getforexample).It
 *       maycontainadescriptionofthenumberofdigitsthatshouldbeused.
 *@param{Object}[options]
 *       additionaloptionstooverridethevaluesinthepythondescriptionof
 *       thefield.
 *@param{Object}[options.currency]thedescriptionofthecurrencytouse
 *@param{integer}[options.currency_id]
 *       theidofthe'res.currency'touse(ignoredifoptions.currency)
 *@param{string}[options.currency_field]
 *       thenameofthefieldwhosevalueisthecurrencyid
 *       (ignoreifoptions.currencyoroptions.currency_id)
 *       Note:ifnotgivenitwilldefaulttothefieldcurrency_fieldvalue
 *       orto'currency_id'.
 *@param{Object}[options.data]
 *       amappingoffieldnametofieldvalue,requiredwith
 *       options.currency_field
 *@param{integer[]}[options.digits]
 *       thenumberofdigitsthatshouldbeused,insteadofthedefault
 *       digitsprecisioninthefield.Note:ifthecurrencydefinesa
 *       precision,thecurrency'soneisused.
 *@param{boolean}[options.forceString=false]
 *       iftrue,returnsastringwithregularwhitespace.Otherwiseituses
 *       non-breakingwhitespaceunicodecharacter.Theoptionispresentedfor
 *       historicalreasonandwillberemovedinmaster.Previous
 *       implementationusedhtmlentity`&nbsp;`,whichdoesn'tworkinhtml
 *       attributes.Withnewimplementationwecanalwaysusetheunicode
 *       characterandtheoptionisnotneededanymore.
 *@returns{string}
 */
functionformatMonetary(value,field,options){
    if(value===false){
        return"";
    }
    options=Object.assign({forceString:false},options);

    varcurrency=options.currency;
    if(!currency){
        varcurrency_id=options.currency_id;
        if(!currency_id&&options.data){
            varcurrency_field=options.currency_field||field.currency_field||'currency_id';
            currency_id=options.data[currency_field]&&options.data[currency_field].res_id;
        }
        currency=session.get_currency(currency_id);
    }

    vardigits=(currency&&currency.digits)||options.digits;
    if(options.field_digits===true){
        digits=field.digits||digits;
    }
    varformatted_value=formatFloat(value,field,
        _.extend({},options,{digits:digits})
    );

    if(!currency||options.noSymbol){
        returnformatted_value;
    }
    constws=options.forceString?'':NBSP;
    if(currency.position==="after"){
        returnformatted_value+ws+currency.symbol;
    }else{
        returncurrency.symbol+ws+formatted_value;
    }
}
/**
 *Returnsastringrepresentingthegivenvalue(multipliedby100)
 *concatenatedwith'%'.
 *
 *@param{number|false}value
 *@param{Object}[field]
 *@param{Object}[options]
 *@param{function}[options.humanReadable]ifreturnstrue,parsingisavoided
 *@returns{string}
 */
functionformatPercentage(value,field,options){
    options=options||{};
    letresult=formatFloat(value*100,field,options)||'0';
    if(!options.humanReadable||!options.humanReadable(value*100)){
        result=parseFloat(result).toString().replace('.',_t.database.parameters.decimal_point);
    }
    returnresult+(options.noSymbol?'':'%');
}
/**
 *Returnsastringrepresentingthevalueoftheselection.
 *
 *@param{string|false}value
 *@param{Object}[field]
 *       adescriptionofthefield(note:thisparameterisignored)
 *@param{Object}[options]additionaloptions
 *@param{boolean}[options.escape=false]iftrue,escapestheformattedvalue
 */
functionformatSelection(value,field,options){
    varval=_.find(field.selection,function(option){
        returnoption[0]===value;
    });
    if(!val){
        return'';
    }
    value=val[1];
    if(options&&options.escape){
        value=_.escape(value);
    }
    returnvalue;
}

////////////////////////////////////////////////////////////////////////////////
//Parse
////////////////////////////////////////////////////////////////////////////////

/**
 *Smartdateinputsareshortcutstowritedatesquicker.
 *Theseshortcutsshouldrespecttheformat^[+-]\d+[dmwy]?$
 *
 *e.g.
 *  "+1d"or"+1"willreturnnow+1day
 *  "-2w"willreturnnow-2weeks
 *  "+3m"willreturnnow+3months
 *  "-4y"willreturnnow+4years
 *
 *@param{string}value
 *@returns{Moment|false}Momentdateobject
 */
functionparseSmartDateInput(value){
    constunits={
        d:'days',
        m:'months',
        w:'weeks',
        y:'years',
    };
    constre=newRegExp(`^([+-])(\\d+)([${Object.keys(units).join('')}]?)$`);
    constmatch=re.exec(value);
    if(match){
        letdate=moment();
        constoffset=parseInt(match[2],10);
        constunit=units[match[3]||'d'];
        if(match[1]==='+'){
            date.add(offset,unit);
        }else{
            date.subtract(offset,unit);
        }
        returndate;
    }
    returnfalse;
}

/**
 *CreateanDateobject
 *ThemethodtoJSONreturntheformatedvaluetosendvalueserverside
 *
 *@param{string}value
 *@param{Object}[field]
 *       adescriptionofthefield(note:thisparameterisignored)
 *@param{Object}[options]additionaloptions
 *@param{boolean}[options.isUTC]theformatteddateisutc
 *@param{boolean}[options.timezone=false]formatthedateafterapplythetimezone
 *       offset
 *@returns{Moment|false}Momentdateobject
 */
functionparseDate(value,field,options){
    if(!value){
        returnfalse;
    }
    vardatePattern=time.getLangDateFormat();
    vardatePatternWoZero=time.getLangDateFormatWoZero();
    vardate;
    constsmartDate=parseSmartDateInput(value);
    if(smartDate){
        date=smartDate;
    }else{
        if(options&&options.isUTC){
            value=value.padStart(10,"0");//servermaysend"932-10-10"for"0932-10-10"onsomeOS
            date=moment.utc(value);
        }else{
            date=moment.utc(value,[datePattern,datePatternWoZero,moment.ISO_8601]);
        }
    }
    if(date.isValid()){
        if(date.year()===0){
            date.year(moment.utc().year());
        }
        if(date.year()>=1000){
            date.toJSON=function(){
                returnthis.clone().locale('en').format('YYYY-MM-DD');
            };
            returndate;
        }
    }
    thrownewError(_.str.sprintf(core._t("'%s'isnotacorrectdate"),value));
}

/**
 *CreateanDateobject
 *ThemethodtoJSONreturntheformatedvaluetosendvalueserverside
 *
 *@param{string}value
 *@param{Object}[field]
 *       adescriptionofthefield(note:thisparameterisignored)
 *@param{Object}[options]additionaloptions
 *@param{boolean}[options.isUTC]theformatteddateisutc
 *@param{boolean}[options.timezone=false]formatthedateafterapplythetimezone
 *       offset
 *@returns{Moment|false}Momentdateobject
 */
functionparseDateTime(value,field,options){
    if(!value){
        returnfalse;
    }
    constdatePattern=time.getLangDateFormat();
    consttimePattern=time.getLangTimeFormat();
    constdatePatternWoZero=time.getLangDateFormatWoZero();
    consttimePatternWoZero=time.getLangTimeFormatWoZero();
    varpattern1=datePattern+''+timePattern;
    varpattern2=datePatternWoZero+''+timePatternWoZero;
    vardatetime;
    constsmartDate=parseSmartDateInput(value);
    if(smartDate){
        datetime=smartDate;
    }else{
        if(options&&options.isUTC){
            value=value.padStart(19,"0");//servermaysend"932-10-10"for"0932-10-10"onsomeOS
            //phatomjscrashifwedon'tusethisformat
            datetime=moment.utc(value.replace('','T')+'Z');
        }else{
            datetime=moment.utc(value,[pattern1,pattern2,moment.ISO_8601]);
            if(options&&options.timezone){
                datetime.add(-session.getTZOffset(datetime),'minutes');
            }
        }
    }
    if(datetime.isValid()){
        if(datetime.year()===0){
            datetime.year(moment.utc().year());
        }
        if(datetime.year()>=1000){
            datetime.toJSON=function(){
                returnthis.clone().locale('en').format('YYYY-MM-DDHH:mm:ss');
            };
            returndatetime;
        }
    }
    thrownewError(_.str.sprintf(core._t("'%s'isnotacorrectdatetime"),value));
}

/**
 *ParseaStringcontainingnumberinlanguageformating
 *
 *@param{string}value
 *               Thestringtobeparsedwiththesettingofthousandsand
 *               decimalseparator
 *@returns{float|NaN}thenumbervaluecontainedinthestringrepresentation
 */
functionparseNumber(value){
    if(core._t.database.parameters.thousands_sep){
        varescapedSep=_.str.escapeRegExp(core._t.database.parameters.thousands_sep);
        value=value.replace(newRegExp(escapedSep,'g'),'');
    }
    if(core._t.database.parameters.decimal_point){
        value=value.replace(core._t.database.parameters.decimal_point,'.');
    }
    returnNumber(value);
}

/**
 *ParseaStringcontainingfloatinlanguageformating
 *
 *@param{string}value
 *               Thestringtobeparsedwiththesettingofthousandsand
 *               decimalseparator
 *@returns{float}
 *@throws{Error}ifnofloatisfoundrespectingthelanguageconfiguration
 */
functionparseFloat(value){
    varparsed=parseNumber(value);
    if(isNaN(parsed)){
        thrownewError(_.str.sprintf(core._t("'%s'isnotacorrectfloat"),value));
    }
    returnparsed;
}

/**
 *ParseaStringcontainingcurrencysymbolandreturnsamount
 *
 *@param{string}value
 *               Thestringtobeparsed
 *               Weassumethatamonetaryisalwaysapair(symbol,amount)separated
 *               byanonbreakingspace.Asimplefloatcanalsobeacceptedasvalue
 *@param{Object}[field]
 *       adescriptionofthefield(returnedbyfields_getforexample).
 *@param{Object}[options]additionaloptions.
 *@param{Object}[options.currency]-thedescriptionofthecurrencytouse
 *@param{integer}[options.currency_id]
 *       theidofthe'res.currency'touse(ignoredifoptions.currency)
 *@param{string}[options.currency_field]
 *       thenameofthefieldwhosevalueisthecurrencyid
 *       (ignoreifoptions.currencyoroptions.currency_id)
 *       Note:ifnotgivenitwilldefaulttothefieldcurrency_fieldvalue
 *       orto'currency_id'.
 *@param{Object}[options.data]
 *       amappingoffieldnametofieldvalue,requiredwith
 *       options.currency_field
 *
 *@returns{float}thefloatvaluecontainedinthestringrepresentation
 *@throws{Error}ifnofloatisfoundorifparameterdoesnotrespectmonetarycondition
 */
functionparseMonetary(value,field,options){
    if(!value.includes(NBSP)&&!value.includes('&nbsp;')){
        returnparseFloat(value);
    }
    options=options||{};
    varcurrency=options.currency;
    if(!currency){
        varcurrency_id=options.currency_id;
        if(!currency_id&&options.data){
            varcurrency_field=options.currency_field||field.currency_field||'currency_id';
            currency_id=options.data[currency_field]&&options.data[currency_field].res_id;
        }
        currency=session.get_currency(currency_id);
    }
    if(!currency){
        returnparseFloat(value);
    }
    if(!value.includes(currency.symbol)){
        thrownewError(_.str.sprintf(core._t("'%s'isnotacorrectmonetaryfield"),value));
    }
    if(currency.position==='after'){
        returnparseFloat(value
            .replace(`${NBSP}${currency.symbol}`,'')
            .replace(`&nbsp;${currency.symbol}`,''));
    }else{
        returnparseFloat(value
            .replace(`${currency.symbol}${NBSP}`,'')
            .replace(`${currency.symbol}&nbsp;`,''));
    }
}

/**
 *ParseaStringcontainingfloatandunconvertitwithaconversionfactor
 *
 *@param{number}[options.factor]
 *         Conversionfactor,defaultvalueis1.0
 */
functionparseFloatFactor(value,field,options){
    varparsed=parseFloat(value);
    varfactor=options.factor||1.0;
    returnparsed/factor;
}

functionparseFloatTime(value){
    varfactor=1;
    if(value[0]==='-'){
        value=value.slice(1);
        factor=-1;
    }
    varfloat_time_pair=value.split(":");
    if(float_time_pair.length!==2)
        returnfactor*parseFloat(value);
    varhours=parseInteger(float_time_pair[0]);
    varminutes=parseInteger(float_time_pair[1]);
    returnfactor*(hours+(minutes/60));
}

/**
 *ParseaStringcontainingfloatandunconvertitwithaconversionfactor
 *of100.Thepercentagecanbearegularxx.xxfloatoraxx%.
 *
 *@param{string}value
 *               Thestringtobeparsed
 *@returns{float}
 *@throws{Error}ifthevaluecouldn'tbeconvertedtofloat
 */
functionparsePercentage(value){
    returnparseFloat(value)/100;
}

/**
 *ParseaStringcontainingintegerwithlanguageformating
 *
 *@param{string}value
 *               Thestringtobeparsedwiththesettingofthousandsand
 *               decimalseparator
 *@returns{integer}
 *@throws{Error}ifnointegerisfoundrespectingthelanguageconfiguration
 */
functionparseInteger(value){
    varparsed=parseNumber(value);
    //donotacceptnotnumbersorfloatvalues
    if(isNaN(parsed)||parsed%1||parsed<-2147483648||parsed>2147483647){
        thrownewError(_.str.sprintf(core._t("'%s'isnotacorrectinteger"),value));
    }
    returnparsed;
}

/**
 *Createsanobjectwithidanddisplay_name.
 *
 *@param{Array|number|string|Object}value
 *       Thegivenvaluecanbe:
 *       -anarraywithidasfirstelementanddisplay_nameassecondelement
 *       -anumberorastringrepresentingtheid(thedisplay_namewillbe
 *         returnedasundefined)
 *       -anobject,simplyreturneduntouched
 *@returns{Object}(containstheidanddisplay_name)
 *                  Note:ifthegivenvalueisnotanarray,astringora
 *                  number,thevalueisreturneduntouched.
 */
functionparseMany2one(value){
    if(_.isArray(value)){
        return{
            id:value[0],
            display_name:value[1],
        };
    }
    if(_.isNumber(value)||_.isString(value)){
        return{
            id:parseInt(value,10),
        };
    }
    returnvalue;
}

return{
    format:{
        binary:formatBinary,
        boolean:formatBoolean,
        char:formatChar,
        date:formatDate,
        datetime:formatDateTime,
        float:formatFloat,
        float_factor:formatFloatFactor,
        float_time:formatFloatTime,
        html:_.identity,//todo
        integer:formatInteger,
        many2many:formatX2Many,
        many2one:formatMany2one,
        many2one_reference:formatInteger,
        monetary:formatMonetary,
        one2many:formatX2Many,
        percentage:formatPercentage,
        reference:formatMany2one,
        selection:formatSelection,
        text:formatChar,
    },
    parse:{
        binary:_.identity,
        boolean:_.identity,//todo
        char:_.identity,//todo
        date:parseDate,//todo
        datetime:parseDateTime,//todo
        float:parseFloat,
        float_factor:parseFloatFactor,
        float_time:parseFloatTime,
        html:_.identity,//todo
        integer:parseInteger,
        many2many:_.identity,//todo
        many2one:parseMany2one,
        many2one_reference:parseInteger,
        monetary:parseMonetary,
        one2many:_.identity,
        percentage:parsePercentage,
        reference:parseMany2one,
        selection:_.identity,//todo
        text:_.identity,//todo
    },
};

});
