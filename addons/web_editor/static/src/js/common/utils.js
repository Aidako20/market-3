flectra.define('web_editor.utils',function(require){
'usestrict';

const{ColorpickerWidget}=require('web.Colorpicker');

/**
 *window.getComputedStylecannotworkproperlywithCSSshortcuts(like
 *'border-width'whichisashortcutforthetop+right+bottom+leftborder
 *widths.Ifanoptionwantstocustomizesuchashortcut,itshouldbelisted
 *herewiththenon-shortcutspropertyitstandsfor,inorder.
 *
 *@type{Object<string[]>}
 */
constCSS_SHORTHANDS={
    'border-width':['border-top-width','border-right-width','border-bottom-width','border-left-width'],
    'border-radius':['border-top-left-radius','border-top-right-radius','border-bottom-right-radius','border-bottom-left-radius'],
    'border-color':['border-top-color','border-right-color','border-bottom-color','border-left-color'],
    'border-style':['border-top-style','border-right-style','border-bottom-style','border-left-style'],
};
/**
 *Key-valuemappingtolistconvertersfromanunitAtoanunitB.
 *-Thekeyisastringintheformat'$1-$2'where$1istheCSSsymbolof
 *  unitAand$2istheCSSsymbolofunitB.
 *-Thevalueisafunctionthatconvertsthereceivedvalue(expressedin
 *  unitA)toanothervalueexpressedinunitB.Twootherparametersis
 *  received:thecsspropertyonwhichtheunitappliesandthejQueryelement
 *  onwhichthatcsspropertymaychange.
 */
constCSS_UNITS_CONVERSION={
    's-ms':()=>1000,
    'ms-s':()=>0.001,
    'rem-px':()=>_computePxByRem(),
    'px-rem':()=>_computePxByRem(true),
};
/**
 *Colorsofthedefaultpalette,usedforsubstitutioninshapes/illustrations.
 *key:numberofthecolorinthepalette(ie,o-color-<1-5>)
 *value:colorhexcode
 */
constDEFAULT_PALETTE={
    '1':'#3AADAA',
    '2':'#7C6576',
    '3':'#F6F6F6',
    '4':'#FFFFFF',
    '5':'#383E45',
};
/**
 *Setofallthedataattributesrelativetothebackgroundimages.
 */
constBACKGROUND_IMAGE_ATTRIBUTES=newSet([
    "originalId","originalSrc","mimetype","resizeWidth","glFilter","quality","bgSrc",
    "filterOptions",
]);

/**
 *Computesthenumberof"px"neededtomakea"rem"unit.Subsequentcalls
 *returnsthecachedcomputedvalue.
 *
 *@param{boolean}[toRem=false]
 *@returns{float}-numberofpxbyremif'toRem'isfalse
 *                 -theinverseotherwise
 */
function_computePxByRem(toRem){
    if(_computePxByRem.PX_BY_REM===undefined){
        consthtmlStyle=window.getComputedStyle(document.documentElement);
        _computePxByRem.PX_BY_REM=parseFloat(htmlStyle['font-size']);
    }
    returntoRem?(1/_computePxByRem.PX_BY_REM):_computePxByRem.PX_BY_REM;
}
/**
 *Convertsthegiven(value+unit)stringtoanumericvalueexpressedin
 *theothergivencssunit.
 *
 *e.g.fct('400ms','s')->0.4
 *
 *@param{string}value
 *@param{string}unitTo
 *@param{string}[cssProp]-thecsspropertyonwhichtheunitapplies
 *@param{jQuery}[$target]-thejQueryelementonwhichthatcssproperty
 *                            maychange
 *@returns{number}
 */
function_convertValueToUnit(value,unitTo,cssProp,$target){
    constm=_getNumericAndUnit(value);
    if(!m){
        returnNaN;
    }
    constnumValue=parseFloat(m[0]);
    constvalueUnit=m[1];
    return_convertNumericToUnit(numValue,valueUnit,unitTo,cssProp,$target);
}
/**
 *Convertsthegivennumericvalueexpressedinthegivencssunitinto
 *thecorrespondingnumericvalueexpressedintheothergivencssunit.
 *
 *e.g.fct(400,'ms','s')->0.4
 *
 *@param{number}value
 *@param{string}unitFrom
 *@param{string}unitTo
 *@param{string}[cssProp]-thecsspropertyonwhichtheunitapplies
 *@param{jQuery}[$target]-thejQueryelementonwhichthatcssproperty
 *                            maychange
 *@returns{number}
 */
function_convertNumericToUnit(value,unitFrom,unitTo,cssProp,$target){
    if(Math.abs(value)<Number.EPSILON||unitFrom===unitTo){
        returnvalue;
    }
    constconverter=CSS_UNITS_CONVERSION[`${unitFrom}-${unitTo}`];
    if(converter===undefined){
        thrownewError(`Cannotconvert'${unitFrom}'unitsinto'${unitTo}'units!`);
    }
    returnvalue*converter(cssProp,$target);
}
/**
 *Returnsthenumericvalueandunitofacssvalue.
 *
 *e.g.fct('400ms')->[400,'ms']
 *
 *@param{string}value
 *@returns{Array|null}
 */
function_getNumericAndUnit(value){
    constm=value.trim().match(/^(-?[0-9.]+)([A-Za-z%-]*)$/);
    if(!m){
        returnnull;
    }
    return[m[1].trim(),m[2].trim()];
}
/**
 *Checksiftwocssvaluesareequal.
 *
 *@param{string}value1
 *@param{string}value2
 *@param{string}[cssProp]-thecsspropertyonwhichtheunitapplies
 *@param{jQuery}[$target]-thejQueryelementonwhichthatcssproperty
 *                            maychange
 *@returns{boolean}
 */
function_areCssValuesEqual(value1,value2,cssProp,$target){
    //Stringcomparisonfirst
    if(value1===value2){
        returntrue;
    }

    //ItcouldbeaCSSvariable,inthatcasetheactualvaluehastobe
    //retrievedbeforecomparing.
    if(value1.startsWith('var(--')){
        value1=_getCSSVariableValue(value1.substring(6,value1.length-1));
    }
    if(value2.startsWith('var(--')){
        value2=_getCSSVariableValue(value2.substring(6,value2.length-1));
    }
    if(value1===value2){
        returntrue;
    }

    //Theymaybecolors,normalizethenre-comparetheresultingstring
    constcolor1=ColorpickerWidget.normalizeCSSColor(value1);
    constcolor2=ColorpickerWidget.normalizeCSSColor(value2);
    if(color1===color2){
        returntrue;
    }

    //Incasethevaluesaremeantasbox-shadow,thisisdifficulttocompare.
    //Inthiscaseweusethekindahackyandprobablyinneficientbutprobably
    //easiestway:applyingthevalueasbox-shadowoftwofakeselementsand
    //comparetheircomputedvalue.
    if(cssProp==='box-shadow'){
        consttemp1El=document.createElement('div');
        temp1El.style.boxShadow=value1;
        document.body.appendChild(temp1El);
        value1=getComputedStyle(temp1El).boxShadow;
        document.body.removeChild(temp1El);

        consttemp2El=document.createElement('div');
        temp2El.style.boxShadow=value2;
        document.body.appendChild(temp2El);
        value2=getComputedStyle(temp2El).boxShadow;
        document.body.removeChild(temp2El);

        returnvalue1===value2;
    }

    //Convertthesecondvalueintheunitofthefirstoneandcompare
    //floatingvalues
    constdata=_getNumericAndUnit(value1);
    if(!data){
        returnfalse;
    }
    constnumValue1=data[0];
    constnumValue2=_convertValueToUnit(value2,data[1],cssProp,$target);
    return(Math.abs(numValue1-numValue2)<Number.EPSILON);
}
/**
 *@param{string|number}name
 *@returns{boolean}
 */
function_isColorCombinationName(name){
    constnumber=parseInt(name);
    return(!isNaN(number)&&number%100!==0);
}
/**
 *@param{string[]}colorNames
 *@param{string}[prefix='bg-']
 *@returns{string[]}
 */
function_computeColorClasses(colorNames,prefix='bg-'){
    lethasCCClasses=false;
    constisBgPrefix=(prefix==='bg-');
    constclasses=colorNames.map(c=>{
        if(isBgPrefix&&_isColorCombinationName(c)){
            hasCCClasses=true;
            return`o_cc${c}`;
        }
        return(prefix+c);
    });
    if(hasCCClasses){
        classes.push('o_cc');
    }
    returnclasses;
}
/**
 *@param{string}key
 *@param{CSSStyleDeclaration}[htmlStyle]ifnotprovided,itiscomputed
 *@returns{string}
 */
function_getCSSVariableValue(key,htmlStyle){
    if(htmlStyle===undefined){
        htmlStyle=window.getComputedStyle(document.documentElement);
    }
    //GettrimmedvaluefromtheHTMLelement
    letvalue=htmlStyle.getPropertyValue(`--${key}`).trim();
    //Ifitisacolorvalue,itneedstobenormalized
    value=ColorpickerWidget.normalizeCSSColor(value);
    //Normallyscss-stringvaluesare"printed"single-quoted.Thatwayno
    //magicconversationisneededwhencustomizingavariable:eithersaveit
    //quotedforstringsornonquotedforcolors,numbers,etc.However,
    //Chromehastheannoyingbehaviorofchangingthesingle-quotesto
    //double-quoteswhenreadingthemthroughgetPropertyValue...
    returnvalue.replace(/"/g,"'");
}
/**
 *Normalizeacolorincaseitisavariablenamesoitcanbeusedoutsideof
 *css.
 *
 *@param{string}colorthecolortonormalizeintoacssvalue
 *@returns{string}thenormalizedcolor
 */
function_normalizeColor(color){
    if(ColorpickerWidget.isCSSColor(color)){
        returncolor;
    }
    return_getCSSVariableValue(color);
}
/**
 *Parseanelement'sbackground-image'surl.
 *
 *@param{string}stringacssvalueintheform'url("...")'
 *@returns{string|false}thesrcoftheimageorfalseifnotparsable
 */
function_getBgImageURL(el){
    conststring=$(el).css('background-image');
    constmatch=string.match(/^url\((['"])(.*?)\1\)$/);
    if(!match){
        return'';
    }
    constmatchedURL=match[2];
    //MakeURLrelativeifpossible
    constfullURL=newURL(matchedURL,window.location.origin);
    if(fullURL.origin===window.location.origin){
        returnfullURL.href.slice(fullURL.origin.length);
    }
    returnmatchedURL;
}
/**
 *Addoneormorenewattributesrelatedtobackgroundimagesinthe
 *BACKGROUND_IMAGE_ATTRIBUTESset.
 *
 *@param{...string}newAttributesThenewattributestoaddinthe
 *BACKGROUND_IMAGE_ATTRIBUTESset.
 */
function_addBackgroundImageAttributes(...newAttributes){
    BACKGROUND_IMAGE_ATTRIBUTES.add(...newAttributes);
}
/**
 *CheckifanattributeisintheBACKGROUND_IMAGE_ATTRIBUTESset.
 *
 *@param{string}attributeTheattributethathastobechecked.
 */
function_isBackgroundImageAttribute(attribute){
    returnBACKGROUND_IMAGE_ATTRIBUTES.has(attribute);
}

return{
    CSS_SHORTHANDS:CSS_SHORTHANDS,
    CSS_UNITS_CONVERSION:CSS_UNITS_CONVERSION,
    DEFAULT_PALETTE:DEFAULT_PALETTE,
    computePxByRem:_computePxByRem,
    convertValueToUnit:_convertValueToUnit,
    convertNumericToUnit:_convertNumericToUnit,
    getNumericAndUnit:_getNumericAndUnit,
    areCssValuesEqual:_areCssValuesEqual,
    isColorCombinationName:_isColorCombinationName,
    computeColorClasses:_computeColorClasses,
    getCSSVariableValue:_getCSSVariableValue,
    normalizeColor:_normalizeColor,
    getBgImageURL:_getBgImageURL,
    addBackgroundImageAttributes:_addBackgroundImageAttributes,
    isBackgroundImageAttribute:_isBackgroundImageAttribute,
};
});
