/*
(TheMITLicense)

Copyright(c)2014-2017DouglasChristopherWilson

Permissionisherebygranted,freeofcharge,toanypersonobtaining
acopyofthissoftwareandassociateddocumentationfiles(the
'Software'),todealintheSoftwarewithoutrestriction,including
withoutlimitationtherightstouse,copy,modify,merge,publish,
distribute,sublicense,and/orsellcopiesoftheSoftware,andto
permitpersonstowhomtheSoftwareisfurnishedtodoso,subjectto
thefollowingconditions:

Theabovecopyrightnoticeandthispermissionnoticeshallbe
includedinallcopiesorsubstantialportionsoftheSoftware.

THESOFTWAREISPROVIDED'ASIS',WITHOUTWARRANTYOFANYKIND,
EXPRESSORIMPLIED,INCLUDINGBUTNOTLIMITEDTOTHEWARRANTIESOF
MERCHANTABILITY,FITNESSFORAPARTICULARPURPOSEANDNONINFRINGEMENT.
INNOEVENTSHALLTHEAUTHORSORCOPYRIGHTHOLDERSBELIABLEFORANY
CLAIM,DAMAGESOROTHERLIABILITY,WHETHERINANACTIONOFCONTRACT,
TORTOROTHERWISE,ARISINGFROM,OUTOFORINCONNECTIONWITHTHE
SOFTWAREORTHEUSEOROTHERDEALINGSINTHESOFTWARE.
 */

/**
 *Strippeddowntoonlyparsing/decoding.
 */
flectra.define('web.contentdisposition',function(){
'usestrict';

/**
 *RegExptomatchpercentencodingescape.
 *@private
 */
varHEX_ESCAPE_REPLACE_REGEXP=/%([0-9A-Fa-f]{2})/g;

/**
 *RegExptomatchnon-latin1characters.
 *@private
 */
varNON_LATIN1_REGEXP=/[^\x20-\x7e\xa0-\xff]/g;

/**
 *RegExptomatchquoted-pairinRFC2616
 *
 *quoted-pair="\"CHAR
 *CHAR       =<anyUS-ASCIIcharacter(octets0-127)>
 *@private
 */
varQESC_REGEXP=/\\([\u0000-\u007f])/g;

/**
 *RegExpforvariousRFC2616grammar
 *
 *parameter    =token"="(token|quoted-string)
 *token        =1*<anyCHARexceptCTLsorseparators>
 *separators   ="("|")"|"<"|">"|"@"
 *              |","|";"|":"|"\"|<">
 *              |"/"|"["|"]"|"?"|"="
 *              |"{"|"}"|SP|HT
 *quoted-string=(<">*(qdtext|quoted-pair)<">)
 *qdtext       =<anyTEXTexcept<">>
 *quoted-pair  ="\"CHAR
 *CHAR         =<anyUS-ASCIIcharacter(octets0-127)>
 *TEXT         =<anyOCTETexceptCTLs,butincludingLWS>
 *LWS          =[CRLF]1*(SP|HT)
 *CRLF         =CRLF
 *CR           =<US-ASCIICR,carriagereturn(13)>
 *LF           =<US-ASCIILF,linefeed(10)>
 *SP           =<US-ASCIISP,space(32)>
 *HT           =<US-ASCIIHT,horizontal-tab(9)>
 *CTL          =<anyUS-ASCIIcontrolcharacter(octets0-31)andDEL(127)>
 *OCTET        =<any8-bitsequenceofdata>
 *@private
 */
varPARAM_REGEXP=/;[\x09\x20]*([!#$%&'*+.0-9A-Z^_`a-z|~-]+)[\x09\x20]*=[\x09\x20]*("(?:[\x20!\x23-\x5b\x5d-\x7e\x80-\xff]|\\[\x20-\x7e])*"|[!#$%&'*+.0-9A-Z^_`a-z|~-]+)[\x09\x20]*/g;

/**
 *RegExpforvariousRFC5987grammar
 *
 *ext-value    =charset "'"[language]"'"value-chars
 *charset      ="UTF-8"/"ISO-8859-1"/mime-charset
 *mime-charset =1*mime-charsetc
 *mime-charsetc=ALPHA/DIGIT
 *              /"!"/"#"/"$"/"%"/"&"
 *              /"+"/"-"/"^"/"_"/"`"
 *              /"{"/"}"/"~"
 *language     =(2*3ALPHA[extlang])
 *              /4ALPHA
 *              /5*8ALPHA
 *extlang      =*3("-"3ALPHA)
 *value-chars  =*(pct-encoded/attr-char)
 *pct-encoded  ="%"HEXDIGHEXDIG
 *attr-char    =ALPHA/DIGIT
 *              /"!"/"#"/"$"/"&"/"+"/"-"/"."
 *              /"^"/"_"/"`"/"|"/"~"
 *@private
 */
varEXT_VALUE_REGEXP=/^([A-Za-z0-9!#$%&+\-^_`{}~]+)'(?:[A-Za-z]{2,3}(?:-[A-Za-z]{3}){0,3}|[A-Za-z]{4,8}|)'((?:%[0-9A-Fa-f]{2}|[A-Za-z0-9!#$&+.^_`|~-])+)$/;

/**
 *RegExpforvariousRFC6266grammar
 *
 *disposition-type="inline"|"attachment"|disp-ext-type
 *disp-ext-type   =token
 *disposition-parm=filename-parm|disp-ext-parm
 *filename-parm   ="filename""="value
 *                 |"filename*""="ext-value
 *disp-ext-parm   =token"="value
 *                 |ext-token"="ext-value
 *ext-token       =<thecharactersintoken,followedby"*">
 *@private
 */
varDISPOSITION_TYPE_REGEXP=/^([!#$%&'*+.0-9A-Z^_`a-z|~-]+)[\x09\x20]*(?:$|;)/;

/**
 *DecodeaRFC6987fieldvalue(gracefully).
 *
 *@param{string}str
 *@return{string}
 *@private
 */
functiondecodefield(str){
    varmatch=EXT_VALUE_REGEXP.exec(str);

    if(!match){
        thrownewTypeError('invalidextendedfieldvalue')
    }

    varcharset=match[1].toLowerCase();
    varencoded=match[2];

    switch(charset){
    case'iso-8859-1':
        returnencoded.replace(HEX_ESCAPE_REPLACE_REGEXP,pdecode).replace(NON_LATIN1_REGEXP,'?');
    case'utf-8':
        returndecodeURIComponent(encoded);
    default:
        thrownewTypeError('unsupportedcharsetinextendedfield')
    }
}

/**
 *ParseContent-Dispositionheaderstring.
 *
 *@param{string}string
 *@return{ContentDisposition}
 *@public
 */
functionparse(string){
    if(!string||typeofstring!=='string'){
        thrownewTypeError('argumentstringisrequired')
    }

    varmatch=DISPOSITION_TYPE_REGEXP.exec(string);

    if(!match){
        thrownewTypeError('invalidtypeformat')
    }

    //normalizetype
    varindex=match[0].length;
    vartype=match[1].toLowerCase();

    varkey;
    varnames=[];
    varparams={};
    varvalue;

    //calculateindextostartat
    index=PARAM_REGEXP.lastIndex=match[0].substr(-1)===';'?index-1:index;

    //matchparameters
    while((match=PARAM_REGEXP.exec(string))){
        if(match.index!==index){
            thrownewTypeError('invalidparameterformat')
        }

        index+=match[0].length;
        key=match[1].toLowerCase();
        value=match[2];

        if(names.indexOf(key)!==-1){
            thrownewTypeError('invalidduplicateparameter')
        }

        names.push(key);

        if(key.indexOf('*')+1===key.length){
            //decodeextendedvalue
            key=key.slice(0,-1);
            value=decodefield(value);

            //overwriteexistingvalue
            params[key]=value;
            continue
        }

        if(typeofparams[key]==='string'){
            continue
        }

        if(value[0]==='"'){
            //removequotesandescapes
            value=value
                    .substr(1,value.length-2)
                    .replace(QESC_REGEXP,'$1')
        }

        params[key]=value
    }

    if(index!==-1&&index!==string.length){
        thrownewTypeError('invalidparameterformat')
    }

    returnnewContentDisposition(type,params)
}

/**
 *Percentdecodeasinglecharacter.
 *
 *@param{string}str
 *@param{string}hex
 *@return{string}
 *@private
 */
functionpdecode(str,hex){
    returnString.fromCharCode(parseInt(hex,16))
}

/**
 *ClassforparsedContent-Dispositionheaderforv8optimization
 *
 *@public
 *@param{string}type
 *@param{object}parameters
 *@constructor
 */
functionContentDisposition(type,parameters){
    this.type=type;
    this.parameters=parameters
}

return{
    parse:parse,
};
});
