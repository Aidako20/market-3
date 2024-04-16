/*
Copyright2012IgorVaynberg

Version:3.5.4Timestamp:SunAug3013:30:32EDT2015

ThissoftwareislicensedundertheApacheLicense,Version2.0(the"ApacheLicense")ortheGNU
GeneralPublicLicenseversion2(the"GPLLicense").Youmaychooseeitherlicensetogovernyour
useofthissoftwareonlyupontheconditionthatyouacceptallofthetermsofeithertheApache
LicenseortheGPLLicense.

YoumayobtainacopyoftheApacheLicenseandtheGPLLicenseat:

    http://www.apache.org/licenses/LICENSE-2.0
    http://www.gnu.org/licenses/gpl-2.0.html

Unlessrequiredbyapplicablelaworagreedtoinwriting,softwaredistributedunderthe
ApacheLicenseortheGPLLicenseisdistributedonan"ASIS"BASIS,WITHOUTWARRANTIESOR
CONDITIONSOFANYKIND,eitherexpressorimplied.SeetheApacheLicenseandtheGPLLicensefor
thespecificlanguagegoverningpermissionsandlimitationsundertheApacheLicenseandtheGPLLicense.
*/
(function($){
    if(typeof$.fn.each2=="undefined"){
        $.extend($.fn,{
            /*
            *4-10timesfaster.eachreplacement
            *useitcarefully,asitoverridesjQuerycontextofelementoneachiteration
            */
            each2:function(c){
                varj=$([0]),i=-1,l=this.length;
                while(
                    ++i<l
                    &&(j.context=j[0]=this[i])
                    &&c.call(j[0],i,j)!==false//"this"=DOM,i=index,j=jQueryobject
                );
                returnthis;
            }
        });
    }
})(jQuery);

(function($,undefined){
    "usestrict";
    /*globaldocument,window,jQuery,console*/

    if(window.Select2!==undefined){
        return;
    }

    varAbstractSelect2,SingleSelect2,MultiSelect2,nextUid,sizer,
        lastMousePosition={x:0,y:0},$document,scrollBarDimensions,

    KEY={
        TAB:9,
        ENTER:13,
        ESC:27,
        SPACE:32,
        LEFT:37,
        UP:38,
        RIGHT:39,
        DOWN:40,
        SHIFT:16,
        CTRL:17,
        ALT:18,
        PAGE_UP:33,
        PAGE_DOWN:34,
        HOME:36,
        END:35,
        BACKSPACE:8,
        DELETE:46,
        isArrow:function(k){
            k=k.which?k.which:k;
            switch(k){
            caseKEY.LEFT:
            caseKEY.RIGHT:
            caseKEY.UP:
            caseKEY.DOWN:
                returntrue;
            }
            returnfalse;
        },
        isControl:function(e){
            vark=e.which;
            switch(k){
            caseKEY.SHIFT:
            caseKEY.CTRL:
            caseKEY.ALT:
                returntrue;
            }

            if(e.metaKey)returntrue;

            returnfalse;
        },
        isFunctionKey:function(k){
            k=k.which?k.which:k;
            returnk>=112&&k<=123;
        }
    },
    MEASURE_SCROLLBAR_TEMPLATE="<divclass='select2-measure-scrollbar'></div>",

    DIACRITICS={"\u24B6":"A","\uFF21":"A","\u00C0":"A","\u00C1":"A","\u00C2":"A","\u1EA6":"A","\u1EA4":"A","\u1EAA":"A","\u1EA8":"A","\u00C3":"A","\u0100":"A","\u0102":"A","\u1EB0":"A","\u1EAE":"A","\u1EB4":"A","\u1EB2":"A","\u0226":"A","\u01E0":"A","\u00C4":"A","\u01DE":"A","\u1EA2":"A","\u00C5":"A","\u01FA":"A","\u01CD":"A","\u0200":"A","\u0202":"A","\u1EA0":"A","\u1EAC":"A","\u1EB6":"A","\u1E00":"A","\u0104":"A","\u023A":"A","\u2C6F":"A","\uA732":"AA","\u00C6":"AE","\u01FC":"AE","\u01E2":"AE","\uA734":"AO","\uA736":"AU","\uA738":"AV","\uA73A":"AV","\uA73C":"AY","\u24B7":"B","\uFF22":"B","\u1E02":"B","\u1E04":"B","\u1E06":"B","\u0243":"B","\u0182":"B","\u0181":"B","\u24B8":"C","\uFF23":"C","\u0106":"C","\u0108":"C","\u010A":"C","\u010C":"C","\u00C7":"C","\u1E08":"C","\u0187":"C","\u023B":"C","\uA73E":"C","\u24B9":"D","\uFF24":"D","\u1E0A":"D","\u010E":"D","\u1E0C":"D","\u1E10":"D","\u1E12":"D","\u1E0E":"D","\u0110":"D","\u018B":"D","\u018A":"D","\u0189":"D","\uA779":"D","\u01F1":"DZ","\u01C4":"DZ","\u01F2":"Dz","\u01C5":"Dz","\u24BA":"E","\uFF25":"E","\u00C8":"E","\u00C9":"E","\u00CA":"E","\u1EC0":"E","\u1EBE":"E","\u1EC4":"E","\u1EC2":"E","\u1EBC":"E","\u0112":"E","\u1E14":"E","\u1E16":"E","\u0114":"E","\u0116":"E","\u00CB":"E","\u1EBA":"E","\u011A":"E","\u0204":"E","\u0206":"E","\u1EB8":"E","\u1EC6":"E","\u0228":"E","\u1E1C":"E","\u0118":"E","\u1E18":"E","\u1E1A":"E","\u0190":"E","\u018E":"E","\u24BB":"F","\uFF26":"F","\u1E1E":"F","\u0191":"F","\uA77B":"F","\u24BC":"G","\uFF27":"G","\u01F4":"G","\u011C":"G","\u1E20":"G","\u011E":"G","\u0120":"G","\u01E6":"G","\u0122":"G","\u01E4":"G","\u0193":"G","\uA7A0":"G","\uA77D":"G","\uA77E":"G","\u24BD":"H","\uFF28":"H","\u0124":"H","\u1E22":"H","\u1E26":"H","\u021E":"H","\u1E24":"H","\u1E28":"H","\u1E2A":"H","\u0126":"H","\u2C67":"H","\u2C75":"H","\uA78D":"H","\u24BE":"I","\uFF29":"I","\u00CC":"I","\u00CD":"I","\u00CE":"I","\u0128":"I","\u012A":"I","\u012C":"I","\u0130":"I","\u00CF":"I","\u1E2E":"I","\u1EC8":"I","\u01CF":"I","\u0208":"I","\u020A":"I","\u1ECA":"I","\u012E":"I","\u1E2C":"I","\u0197":"I","\u24BF":"J","\uFF2A":"J","\u0134":"J","\u0248":"J","\u24C0":"K","\uFF2B":"K","\u1E30":"K","\u01E8":"K","\u1E32":"K","\u0136":"K","\u1E34":"K","\u0198":"K","\u2C69":"K","\uA740":"K","\uA742":"K","\uA744":"K","\uA7A2":"K","\u24C1":"L","\uFF2C":"L","\u013F":"L","\u0139":"L","\u013D":"L","\u1E36":"L","\u1E38":"L","\u013B":"L","\u1E3C":"L","\u1E3A":"L","\u0141":"L","\u023D":"L","\u2C62":"L","\u2C60":"L","\uA748":"L","\uA746":"L","\uA780":"L","\u01C7":"LJ","\u01C8":"Lj","\u24C2":"M","\uFF2D":"M","\u1E3E":"M","\u1E40":"M","\u1E42":"M","\u2C6E":"M","\u019C":"M","\u24C3":"N","\uFF2E":"N","\u01F8":"N","\u0143":"N","\u00D1":"N","\u1E44":"N","\u0147":"N","\u1E46":"N","\u0145":"N","\u1E4A":"N","\u1E48":"N","\u0220":"N","\u019D":"N","\uA790":"N","\uA7A4":"N","\u01CA":"NJ","\u01CB":"Nj","\u24C4":"O","\uFF2F":"O","\u00D2":"O","\u00D3":"O","\u00D4":"O","\u1ED2":"O","\u1ED0":"O","\u1ED6":"O","\u1ED4":"O","\u00D5":"O","\u1E4C":"O","\u022C":"O","\u1E4E":"O","\u014C":"O","\u1E50":"O","\u1E52":"O","\u014E":"O","\u022E":"O","\u0230":"O","\u00D6":"O","\u022A":"O","\u1ECE":"O","\u0150":"O","\u01D1":"O","\u020C":"O","\u020E":"O","\u01A0":"O","\u1EDC":"O","\u1EDA":"O","\u1EE0":"O","\u1EDE":"O","\u1EE2":"O","\u1ECC":"O","\u1ED8":"O","\u01EA":"O","\u01EC":"O","\u00D8":"O","\u01FE":"O","\u0186":"O","\u019F":"O","\uA74A":"O","\uA74C":"O","\u01A2":"OI","\uA74E":"OO","\u0222":"OU","\u24C5":"P","\uFF30":"P","\u1E54":"P","\u1E56":"P","\u01A4":"P","\u2C63":"P","\uA750":"P","\uA752":"P","\uA754":"P","\u24C6":"Q","\uFF31":"Q","\uA756":"Q","\uA758":"Q","\u024A":"Q","\u24C7":"R","\uFF32":"R","\u0154":"R","\u1E58":"R","\u0158":"R","\u0210":"R","\u0212":"R","\u1E5A":"R","\u1E5C":"R","\u0156":"R","\u1E5E":"R","\u024C":"R","\u2C64":"R","\uA75A":"R","\uA7A6":"R","\uA782":"R","\u24C8":"S","\uFF33":"S","\u1E9E":"S","\u015A":"S","\u1E64":"S","\u015C":"S","\u1E60":"S","\u0160":"S","\u1E66":"S","\u1E62":"S","\u1E68":"S","\u0218":"S","\u015E":"S","\u2C7E":"S","\uA7A8":"S","\uA784":"S","\u24C9":"T","\uFF34":"T","\u1E6A":"T","\u0164":"T","\u1E6C":"T","\u021A":"T","\u0162":"T","\u1E70":"T","\u1E6E":"T","\u0166":"T","\u01AC":"T","\u01AE":"T","\u023E":"T","\uA786":"T","\uA728":"TZ","\u24CA":"U","\uFF35":"U","\u00D9":"U","\u00DA":"U","\u00DB":"U","\u0168":"U","\u1E78":"U","\u016A":"U","\u1E7A":"U","\u016C":"U","\u00DC":"U","\u01DB":"U","\u01D7":"U","\u01D5":"U","\u01D9":"U","\u1EE6":"U","\u016E":"U","\u0170":"U","\u01D3":"U","\u0214":"U","\u0216":"U","\u01AF":"U","\u1EEA":"U","\u1EE8":"U","\u1EEE":"U","\u1EEC":"U","\u1EF0":"U","\u1EE4":"U","\u1E72":"U","\u0172":"U","\u1E76":"U","\u1E74":"U","\u0244":"U","\u24CB":"V","\uFF36":"V","\u1E7C":"V","\u1E7E":"V","\u01B2":"V","\uA75E":"V","\u0245":"V","\uA760":"VY","\u24CC":"W","\uFF37":"W","\u1E80":"W","\u1E82":"W","\u0174":"W","\u1E86":"W","\u1E84":"W","\u1E88":"W","\u2C72":"W","\u24CD":"X","\uFF38":"X","\u1E8A":"X","\u1E8C":"X","\u24CE":"Y","\uFF39":"Y","\u1EF2":"Y","\u00DD":"Y","\u0176":"Y","\u1EF8":"Y","\u0232":"Y","\u1E8E":"Y","\u0178":"Y","\u1EF6":"Y","\u1EF4":"Y","\u01B3":"Y","\u024E":"Y","\u1EFE":"Y","\u24CF":"Z","\uFF3A":"Z","\u0179":"Z","\u1E90":"Z","\u017B":"Z","\u017D":"Z","\u1E92":"Z","\u1E94":"Z","\u01B5":"Z","\u0224":"Z","\u2C7F":"Z","\u2C6B":"Z","\uA762":"Z","\u24D0":"a","\uFF41":"a","\u1E9A":"a","\u00E0":"a","\u00E1":"a","\u00E2":"a","\u1EA7":"a","\u1EA5":"a","\u1EAB":"a","\u1EA9":"a","\u00E3":"a","\u0101":"a","\u0103":"a","\u1EB1":"a","\u1EAF":"a","\u1EB5":"a","\u1EB3":"a","\u0227":"a","\u01E1":"a","\u00E4":"a","\u01DF":"a","\u1EA3":"a","\u00E5":"a","\u01FB":"a","\u01CE":"a","\u0201":"a","\u0203":"a","\u1EA1":"a","\u1EAD":"a","\u1EB7":"a","\u1E01":"a","\u0105":"a","\u2C65":"a","\u0250":"a","\uA733":"aa","\u00E6":"ae","\u01FD":"ae","\u01E3":"ae","\uA735":"ao","\uA737":"au","\uA739":"av","\uA73B":"av","\uA73D":"ay","\u24D1":"b","\uFF42":"b","\u1E03":"b","\u1E05":"b","\u1E07":"b","\u0180":"b","\u0183":"b","\u0253":"b","\u24D2":"c","\uFF43":"c","\u0107":"c","\u0109":"c","\u010B":"c","\u010D":"c","\u00E7":"c","\u1E09":"c","\u0188":"c","\u023C":"c","\uA73F":"c","\u2184":"c","\u24D3":"d","\uFF44":"d","\u1E0B":"d","\u010F":"d","\u1E0D":"d","\u1E11":"d","\u1E13":"d","\u1E0F":"d","\u0111":"d","\u018C":"d","\u0256":"d","\u0257":"d","\uA77A":"d","\u01F3":"dz","\u01C6":"dz","\u24D4":"e","\uFF45":"e","\u00E8":"e","\u00E9":"e","\u00EA":"e","\u1EC1":"e","\u1EBF":"e","\u1EC5":"e","\u1EC3":"e","\u1EBD":"e","\u0113":"e","\u1E15":"e","\u1E17":"e","\u0115":"e","\u0117":"e","\u00EB":"e","\u1EBB":"e","\u011B":"e","\u0205":"e","\u0207":"e","\u1EB9":"e","\u1EC7":"e","\u0229":"e","\u1E1D":"e","\u0119":"e","\u1E19":"e","\u1E1B":"e","\u0247":"e","\u025B":"e","\u01DD":"e","\u24D5":"f","\uFF46":"f","\u1E1F":"f","\u0192":"f","\uA77C":"f","\u24D6":"g","\uFF47":"g","\u01F5":"g","\u011D":"g","\u1E21":"g","\u011F":"g","\u0121":"g","\u01E7":"g","\u0123":"g","\u01E5":"g","\u0260":"g","\uA7A1":"g","\u1D79":"g","\uA77F":"g","\u24D7":"h","\uFF48":"h","\u0125":"h","\u1E23":"h","\u1E27":"h","\u021F":"h","\u1E25":"h","\u1E29":"h","\u1E2B":"h","\u1E96":"h","\u0127":"h","\u2C68":"h","\u2C76":"h","\u0265":"h","\u0195":"hv","\u24D8":"i","\uFF49":"i","\u00EC":"i","\u00ED":"i","\u00EE":"i","\u0129":"i","\u012B":"i","\u012D":"i","\u00EF":"i","\u1E2F":"i","\u1EC9":"i","\u01D0":"i","\u0209":"i","\u020B":"i","\u1ECB":"i","\u012F":"i","\u1E2D":"i","\u0268":"i","\u0131":"i","\u24D9":"j","\uFF4A":"j","\u0135":"j","\u01F0":"j","\u0249":"j","\u24DA":"k","\uFF4B":"k","\u1E31":"k","\u01E9":"k","\u1E33":"k","\u0137":"k","\u1E35":"k","\u0199":"k","\u2C6A":"k","\uA741":"k","\uA743":"k","\uA745":"k","\uA7A3":"k","\u24DB":"l","\uFF4C":"l","\u0140":"l","\u013A":"l","\u013E":"l","\u1E37":"l","\u1E39":"l","\u013C":"l","\u1E3D":"l","\u1E3B":"l","\u017F":"l","\u0142":"l","\u019A":"l","\u026B":"l","\u2C61":"l","\uA749":"l","\uA781":"l","\uA747":"l","\u01C9":"lj","\u24DC":"m","\uFF4D":"m","\u1E3F":"m","\u1E41":"m","\u1E43":"m","\u0271":"m","\u026F":"m","\u24DD":"n","\uFF4E":"n","\u01F9":"n","\u0144":"n","\u00F1":"n","\u1E45":"n","\u0148":"n","\u1E47":"n","\u0146":"n","\u1E4B":"n","\u1E49":"n","\u019E":"n","\u0272":"n","\u0149":"n","\uA791":"n","\uA7A5":"n","\u01CC":"nj","\u24DE":"o","\uFF4F":"o","\u00F2":"o","\u00F3":"o","\u00F4":"o","\u1ED3":"o","\u1ED1":"o","\u1ED7":"o","\u1ED5":"o","\u00F5":"o","\u1E4D":"o","\u022D":"o","\u1E4F":"o","\u014D":"o","\u1E51":"o","\u1E53":"o","\u014F":"o","\u022F":"o","\u0231":"o","\u00F6":"o","\u022B":"o","\u1ECF":"o","\u0151":"o","\u01D2":"o","\u020D":"o","\u020F":"o","\u01A1":"o","\u1EDD":"o","\u1EDB":"o","\u1EE1":"o","\u1EDF":"o","\u1EE3":"o","\u1ECD":"o","\u1ED9":"o","\u01EB":"o","\u01ED":"o","\u00F8":"o","\u01FF":"o","\u0254":"o","\uA74B":"o","\uA74D":"o","\u0275":"o","\u01A3":"oi","\u0223":"ou","\uA74F":"oo","\u24DF":"p","\uFF50":"p","\u1E55":"p","\u1E57":"p","\u01A5":"p","\u1D7D":"p","\uA751":"p","\uA753":"p","\uA755":"p","\u24E0":"q","\uFF51":"q","\u024B":"q","\uA757":"q","\uA759":"q","\u24E1":"r","\uFF52":"r","\u0155":"r","\u1E59":"r","\u0159":"r","\u0211":"r","\u0213":"r","\u1E5B":"r","\u1E5D":"r","\u0157":"r","\u1E5F":"r","\u024D":"r","\u027D":"r","\uA75B":"r","\uA7A7":"r","\uA783":"r","\u24E2":"s","\uFF53":"s","\u00DF":"s","\u015B":"s","\u1E65":"s","\u015D":"s","\u1E61":"s","\u0161":"s","\u1E67":"s","\u1E63":"s","\u1E69":"s","\u0219":"s","\u015F":"s","\u023F":"s","\uA7A9":"s","\uA785":"s","\u1E9B":"s","\u24E3":"t","\uFF54":"t","\u1E6B":"t","\u1E97":"t","\u0165":"t","\u1E6D":"t","\u021B":"t","\u0163":"t","\u1E71":"t","\u1E6F":"t","\u0167":"t","\u01AD":"t","\u0288":"t","\u2C66":"t","\uA787":"t","\uA729":"tz","\u24E4":"u","\uFF55":"u","\u00F9":"u","\u00FA":"u","\u00FB":"u","\u0169":"u","\u1E79":"u","\u016B":"u","\u1E7B":"u","\u016D":"u","\u00FC":"u","\u01DC":"u","\u01D8":"u","\u01D6":"u","\u01DA":"u","\u1EE7":"u","\u016F":"u","\u0171":"u","\u01D4":"u","\u0215":"u","\u0217":"u","\u01B0":"u","\u1EEB":"u","\u1EE9":"u","\u1EEF":"u","\u1EED":"u","\u1EF1":"u","\u1EE5":"u","\u1E73":"u","\u0173":"u","\u1E77":"u","\u1E75":"u","\u0289":"u","\u24E5":"v","\uFF56":"v","\u1E7D":"v","\u1E7F":"v","\u028B":"v","\uA75F":"v","\u028C":"v","\uA761":"vy","\u24E6":"w","\uFF57":"w","\u1E81":"w","\u1E83":"w","\u0175":"w","\u1E87":"w","\u1E85":"w","\u1E98":"w","\u1E89":"w","\u2C73":"w","\u24E7":"x","\uFF58":"x","\u1E8B":"x","\u1E8D":"x","\u24E8":"y","\uFF59":"y","\u1EF3":"y","\u00FD":"y","\u0177":"y","\u1EF9":"y","\u0233":"y","\u1E8F":"y","\u00FF":"y","\u1EF7":"y","\u1E99":"y","\u1EF5":"y","\u01B4":"y","\u024F":"y","\u1EFF":"y","\u24E9":"z","\uFF5A":"z","\u017A":"z","\u1E91":"z","\u017C":"z","\u017E":"z","\u1E93":"z","\u1E95":"z","\u01B6":"z","\u0225":"z","\u0240":"z","\u2C6C":"z","\uA763":"z","\u0386":"\u0391","\u0388":"\u0395","\u0389":"\u0397","\u038A":"\u0399","\u03AA":"\u0399","\u038C":"\u039F","\u038E":"\u03A5","\u03AB":"\u03A5","\u038F":"\u03A9","\u03AC":"\u03B1","\u03AD":"\u03B5","\u03AE":"\u03B7","\u03AF":"\u03B9","\u03CA":"\u03B9","\u0390":"\u03B9","\u03CC":"\u03BF","\u03CD":"\u03C5","\u03CB":"\u03C5","\u03B0":"\u03C5","\u03C9":"\u03C9","\u03C2":"\u03C3"};

    $document=$(document);

    nextUid=(function(){varcounter=1;returnfunction(){returncounter++;};}());


    functionreinsertElement(element){
        varplaceholder=$(document.createTextNode(''));

        element.before(placeholder);
        placeholder.before(element);
        placeholder.remove();
    }

    functionstripDiacritics(str){
        //Used'unirange+namedfunction'fromhttp://jsperf.com/diacritics/18
        functionmatch(a){
            returnDIACRITICS[a]||a;
        }

        returnstr.replace(/[^\u0000-\u007E]/g,match);
    }

    functionindexOf(value,array){
        vari=0,l=array.length;
        for(;i<l;i=i+1){
            if(equal(value,array[i]))returni;
        }
        return-1;
    }

    functionmeasureScrollbar(){
        var$template=$(MEASURE_SCROLLBAR_TEMPLATE);
        $template.appendTo(document.body);

        vardim={
            width:$template.width()-$template[0].clientWidth,
            height:$template.height()-$template[0].clientHeight
        };
        $template.remove();

        returndim;
    }

    /**
     *Comparesequalityofaandb
     *@parama
     *@paramb
     */
    functionequal(a,b){
        if(a===b)returntrue;
        if(a===undefined||b===undefined)returnfalse;
        if(a===null||b===null)returnfalse;
        //Checkwhether'a'or'b'isastring(primitiveorobject).
        //Theconcatenationofanemptystring(+'')convertsitsargumenttoastring'sprimitive.
        if(a.constructor===String)returna+''===b+'';//a+''-incase'a'isaStringobject
        if(b.constructor===String)returnb+''===a+'';//b+''-incase'b'isaStringobject
        returnfalse;
    }

    /**
     *Splitsthestringintoanarrayofvalues,transformingeachvalue.Anemptyarrayisreturnedfornullsorempty
     *strings
     *@paramstring
     *@paramseparator
     */
    functionsplitVal(string,separator,transform){
        varval,i,l;
        if(string===null||string.length<1)return[];
        val=string.split(separator);
        for(i=0,l=val.length;i<l;i=i+1)val[i]=transform(val[i]);
        returnval;
    }

    functiongetSideBorderPadding(element){
        returnelement.outerWidth(false)-element.width();
    }

    functioninstallKeyUpChangeEvent(element){
        varkey="keyup-change-value";
        element.on("keydown",function(){
            if($.data(element,key)===undefined){
                $.data(element,key,element.val());
            }
        });
        element.on("keyup",function(){
            varval=$.data(element,key);
            if(val!==undefined&&element.val()!==val){
                $.removeData(element,key);
                element.trigger("keyup-change");
            }
        });
    }


    /**
     *filtersmouseeventssoaneventisfiredonlyifthemousemoved.
     *
     *filtersoutmouseeventsthatoccurwhenmouseisstationarybut
     *theelementsunderthepointerarescrolled.
     */
    functioninstallFilteredMouseMove(element){
        element.on("mousemove",function(e){
            varlastpos=lastMousePosition;
            if(lastpos===undefined||lastpos.x!==e.pageX||lastpos.y!==e.pageY){
                $(e.target).trigger("mousemove-filtered",e);
            }
        });
    }

    /**
     *Debouncesafunction.Returnsafunctionthatcallstheoriginalfnfunctiononlyifnoinvocationshavebeenmade
     *withinthelastquietMillismilliseconds.
     *
     *@paramquietMillisnumberofmillisecondstowaitbeforeinvokingfn
     *@paramfnfunctiontobedebounced
     *@paramctxobjecttobeusedasthisreferencewithinfn
     *@returndebouncedversionoffn
     */
    functiondebounce(quietMillis,fn,ctx){
        ctx=ctx||undefined;
        vartimeout;
        returnfunction(){
            varargs=arguments;
            window.clearTimeout(timeout);
            timeout=window.setTimeout(function(){
                fn.apply(ctx,args);
            },quietMillis);
        };
    }

    functioninstallDebouncedScroll(threshold,element){
        varnotify=debounce(threshold,function(e){element.trigger("scroll-debounced",e);});
        element.on("scroll",function(e){
            if(indexOf(e.target,element.get())>=0)notify(e);
        });
    }

    functionfocus($el){
        if($el[0]===document.activeElement)return;

        /*setthefocusina0timeout-thatwaythefocusissetaftertheprocessing
            ofthecurrenteventhasfinished-whichseemsliketheonlyreliableway
            tosetfocus*/
        window.setTimeout(function(){
            varel=$el[0],pos=$el.val().length,range;

            $el.focus();

            /*makesureelreceivedfocussowedonoterroroutwhentryingtomanipulatethecaret.
                sometimesmodalsorotherslistenersmaystealitafteritsset*/
            varisVisible=(el.offsetWidth>0||el.offsetHeight>0);
            if(isVisible&&el===document.activeElement){

                /*afterthefocusissetmovethecarettotheend,necessarywhenweval()
                    justbeforesettingfocus*/
                if(el.setSelectionRange)
                {
                    el.setSelectionRange(pos,pos);
                }
                elseif(el.createTextRange){
                    range=el.createTextRange();
                    range.collapse(false);
                    range.select();
                }
            }
        },0);
    }

    functiongetCursorInfo(el){
        el=$(el)[0];
        varoffset=0;
        varlength=0;
        if('selectionStart'inel){
            offset=el.selectionStart;
            length=el.selectionEnd-offset;
        }elseif('selection'indocument){
            el.focus();
            varsel=document.selection.createRange();
            length=document.selection.createRange().text.length;
            sel.moveStart('character',-el.value.length);
            offset=sel.text.length-length;
        }
        return{offset:offset,length:length};
    }

    functionkillEvent(event){
        event.preventDefault();
        event.stopPropagation();
    }
    functionkillEventImmediately(event){
        event.preventDefault();
        event.stopImmediatePropagation();
    }

    functionmeasureTextWidth(e){
        if(!sizer){
            varstyle=e[0].currentStyle||window.getComputedStyle(e[0],null);
            sizer=$(document.createElement("div")).css({
                position:"absolute",
                left:"-10000px",
                top:"-10000px",
                display:"none",
                fontSize:style.fontSize,
                fontFamily:style.fontFamily,
                fontStyle:style.fontStyle,
                fontWeight:style.fontWeight,
                letterSpacing:style.letterSpacing,
                textTransform:style.textTransform,
                whiteSpace:"nowrap"
            });
            sizer.attr("class","select2-sizer");
            $(document.body).append(sizer);
        }
        sizer.text(e.val());
        returnsizer.width();
    }

    functionsyncCssClasses(dest,src,adapter){
        varclasses,replacements=[],adapted;

        classes=$.trim(dest.attr("class"));

        if(classes){
            classes=''+classes;//forIEwhichreturnsobject

            $(classes.split(/\s+/)).each2(function(){
                if(this.indexOf("select2-")===0){
                    replacements.push(this);
                }
            });
        }

        classes=$.trim(src.attr("class"));

        if(classes){
            classes=''+classes;//forIEwhichreturnsobject

            $(classes.split(/\s+/)).each2(function(){
                if(this.indexOf("select2-")!==0){
                    adapted=adapter(this);

                    if(adapted){
                        replacements.push(adapted);
                    }
                }
            });
        }

        dest.attr("class",replacements.join(""));
    }


    functionmarkMatch(text,term,markup,escapeMarkup){
        varmatch=stripDiacritics(text.toUpperCase()).indexOf(stripDiacritics(term.toUpperCase())),
            tl=term.length;

        if(match<0){
            markup.push(escapeMarkup(text));
            return;
        }

        markup.push(escapeMarkup(text.substring(0,match)));
        markup.push("<spanclass='select2-match'>");
        markup.push(escapeMarkup(text.substring(match,match+tl)));
        markup.push("</span>");
        markup.push(escapeMarkup(text.substring(match+tl,text.length)));
    }

    functiondefaultEscapeMarkup(markup){
        varreplace_map={
            '\\':'&#92;',
            '&':'&amp;',
            '<':'&lt;',
            '>':'&gt;',
            '"':'&quot;',
            "'":'&#39;',
            "/":'&#47;'
        };

        returnString(markup).replace(/[&<>"'\/\\]/g,function(match){
            returnreplace_map[match];
        });
    }

    /**
     *Producesanajax-basedqueryfunction
     *
     *@paramoptionsobjectcontainingconfigurationparameters
     *@paramoptions.paramsparametermapforthetransportajaxcall,cancontainsuchoptionsascache,jsonpCallback,etc.see$.ajax
     *@paramoptions.transportfunctionthatwillbeusedtoexecutetheajaxrequest.mustbecompatiblewithparameterssupportedby$.ajax
     *@paramoptions.urlurlforthedata
     *@paramoptions.dataafunction(searchTerm,pageNumber,context)thatshouldreturnanobjectcontainingquerystringparametersfortheaboveurl.
     *@paramoptions.dataTyperequestdatatype:ajax,jsonp,otherdatatypessupportedbyjQuery's$.ajaxfunctionorthetransportfunctionifspecified
     *@paramoptions.quietMillis(optional)millisecondstowaitbeforemakingtheajaxRequest,helpsdebouncetheajaxfunctionifinvokedtoooften
     *@paramoptions.resultsafunction(remoteData,pageNumber,query)thatconvertsdatareturnedformtheremoterequesttotheformatexpectedbySelect2.
     *     Theexpectedformatisanobjectcontainingthefollowingkeys:
     *     resultsarrayofobjectsthatwillbeusedaschoices
     *     more(optional)booleanindicatingwhethertherearemoreresultsavailable
     *     Example:{results:[{id:1,text:'Red'},{id:2,text:'Blue'}],more:true}
     */
    functionajax(options){
        vartimeout,//currentscheduledbutnotyetexecutedrequest
            handler=null,
            quietMillis=options.quietMillis||100,
            ajaxUrl=options.url,
            self=this;

        returnfunction(query){
            window.clearTimeout(timeout);
            timeout=window.setTimeout(function(){
                vardata=options.data,//ajaxdatafunction
                    url=ajaxUrl,//ajaxurlstringorfunction
                    transport=options.transport||$.fn.select2.ajaxDefaults.transport,
                    //deprecated-toberemovedin4.0 -useparamsinstead
                    deprecated={
                        type:options.type||'GET',//settypeofrequest(GETorPOST)
                        cache:options.cache||false,
                        jsonpCallback:options.jsonpCallback||undefined,
                        dataType:options.dataType||"json"
                    },
                    params=$.extend({},$.fn.select2.ajaxDefaults.params,deprecated);

                data=data?data.call(self,query.term,query.page,query.context):null;
                url=(typeofurl==='function')?url.call(self,query.term,query.page,query.context):url;

                if(handler&&typeofhandler.abort==="function"){handler.abort();}

                if(options.params){
                    if($.isFunction(options.params)){
                        $.extend(params,options.params.call(self));
                    }else{
                        $.extend(params,options.params);
                    }
                }

                $.extend(params,{
                    url:url,
                    dataType:options.dataType,
                    data:data,
                    success:function(data){
                        //TODO-replacequery.pagewithquerysousershaveaccesstoterm,page,etc.
                        //addedqueryasthirdparamtertokeepbackwardscompatibility
                        varresults=options.results(data,query.page,query);
                        query.callback(results);
                    },
                    error:function(jqXHR,textStatus,errorThrown){
                        varresults={
                            hasError:true,
                            jqXHR:jqXHR,
                            textStatus:textStatus,
                            errorThrown:errorThrown
                        };

                        query.callback(results);
                    }
                });
                handler=transport.call(self,params);
            },quietMillis);
        };
    }

    /**
     *Producesaqueryfunctionthatworkswithalocalarray
     *
     *@paramoptionsobjectcontainingconfigurationparameters.Theoptionsparametercaneitherbeanarrayoran
     *object.
     *
     *Ifthearrayformisuseditisassumedthatitcontainsobjectswith'id'and'text'keys.
     *
     *Iftheobjectformisuseditisassumedthatitcontains'data'and'text'keys.The'data'keyshouldcontain
     *anarrayofobjectsthatwillbeusedaschoices.Theseobjectsmustcontainatleastan'id'key.The'text'
     *keycaneitherbeaStringinwhichcaseitisexpectedthateachelementinthe'data'arrayhasakeywiththe
     *valueof'text'whichwillbeusedtomatchchoices.Alternatively,textcanbeafunction(item)thatcanextract
     *thetext.
     */
    functionlocal(options){
        vardata=options,//dataelements
            dataText,
            tmp,
            text=function(item){return""+item.text;};//functionusedtoretrievethetextportionofadataitemthatismatchedagainstthesearch

         if($.isArray(data)){
            tmp=data;
            data={results:tmp};
        }

         if($.isFunction(data)===false){
            tmp=data;
            data=function(){returntmp;};
        }

        vardataItem=data();
        if(dataItem.text){
            text=dataItem.text;
            //iftextisnotafunctionweassumeittobeakeyname
            if(!$.isFunction(text)){
                dataText=dataItem.text;//weneedtostorethisinaseparatevariablebecauseinthenextstepdatagetsresetanddata.textisnolongeravailable
                text=function(item){returnitem[dataText];};
            }
        }

        returnfunction(query){
            vart=query.term,filtered={results:[]},process;
            if(t===""){
                query.callback(data());
                return;
            }

            process=function(datum,collection){
                vargroup,attr;
                datum=datum[0];
                if(datum.children){
                    group={};
                    for(attrindatum){
                        if(datum.hasOwnProperty(attr))group[attr]=datum[attr];
                    }
                    group.children=[];
                    $(datum.children).each2(function(i,childDatum){process(childDatum,group.children);});
                    if(group.children.length||query.matcher(t,text(group),datum)){
                        collection.push(group);
                    }
                }else{
                    if(query.matcher(t,text(datum),datum)){
                        collection.push(datum);
                    }
                }
            };

            $(data().results).each2(function(i,datum){process(datum,filtered.results);});
            query.callback(filtered);
        };
    }

    //TODOjavadoc
    functiontags(data){
        varisFunc=$.isFunction(data);
        returnfunction(query){
            vart=query.term,filtered={results:[]};
            varresult=isFunc?data(query):data;
            if($.isArray(result)){
                $(result).each(function(){
                    varisObject=this.text!==undefined,
                        text=isObject?this.text:this;
                    if(t===""||query.matcher(t,text)){
                        filtered.results.push(isObject?this:{id:this,text:this});
                    }
                });
                query.callback(filtered);
            }
        };
    }

    /**
     *Checksiftheformatterfunctionshouldbeused.
     *
     *Throwsanerrorifitisnotafunction.Returnstrueifitshouldbeused,
     *falseifnoformattingshouldbeperformed.
     *
     *@paramformatter
     */
    functioncheckFormatter(formatter,formatterName){
        if($.isFunction(formatter))returntrue;
        if(!formatter)returnfalse;
        if(typeof(formatter)==='string')returntrue;
        thrownewError(formatterName+"mustbeastring,function,orfalsyvalue");
    }

  /**
   *Returnsagivenvalue
   *Ifgivenafunction,returnsitsoutput
   *
   *@paramvalstring|function
   *@paramcontextvalueof"this"tobepassedtofunction
   *@returns{*}
   */
    functionevaluate(val,context){
        if($.isFunction(val)){
            varargs=Array.prototype.slice.call(arguments,2);
            returnval.apply(context,args);
        }
        returnval;
    }

    functioncountResults(results){
        varcount=0;
        $.each(results,function(i,item){
            if(item.children){
                count+=countResults(item.children);
            }else{
                count++;
            }
        });
        returncount;
    }

    /**
     *Defaulttokenizer.Thisfunctionusesbreakstheinputonsubstringmatchofanystringfromthe
     *opts.tokenSeparatorsarrayandusesopts.createSearchChoicetocreatethechoiceobject.Bothofthose
     *twooptionshavetobedefinedinorderforthetokenizertowork.
     *
     *@paraminputtextuserhastypedsofarorpastedintothesearchfield
     *@paramselectioncurrentlyselectedchoices
     *@paramselectCallbackfunction(choice)callbackthoaddthechoicetoselection
     *@paramoptsselect2'sopts
     *@returnundefined/nulltoleavethecurrentinputunchanged,orastringtochangetheinputtothereturnedvalue
     */
    functiondefaultTokenizer(input,selection,selectCallback,opts){
        varoriginal=input,//storetheoriginalsowecancompareandknowifweneedtotellthesearchtoupdateitstext
            dupe=false,//checkforwhetheratokenweextractedrepresentsaduplicateselectedchoice
            token,//token
            index,//positionatwhichtheseparatorwasfound
            i,l,//loopingvariables
            separator;//thematchedseparator

        if(!opts.createSearchChoice||!opts.tokenSeparators||opts.tokenSeparators.length<1)returnundefined;

        while(true){
            index=-1;

            for(i=0,l=opts.tokenSeparators.length;i<l;i++){
                separator=opts.tokenSeparators[i];
                index=input.indexOf(separator);
                if(index>=0)break;
            }

            if(index<0)break;//didnotfindanytokenseparatorintheinputstring,bail

            token=input.substring(0,index);
            input=input.substring(index+separator.length);

            if(token.length>0){
                token=opts.createSearchChoice.call(this,token,selection);
                if(token!==undefined&&token!==null&&opts.id(token)!==undefined&&opts.id(token)!==null){
                    dupe=false;
                    for(i=0,l=selection.length;i<l;i++){
                        if(equal(opts.id(token),opts.id(selection[i]))){
                            dupe=true;break;
                        }
                    }

                    if(!dupe)selectCallback(token);
                }
            }
        }

        if(original!==input)returninput;
    }

    functioncleanupJQueryElements(){
        varself=this;

        $.each(arguments,function(i,element){
            self[element].remove();
            self[element]=null;
        });
    }

    /**
     *Createsanewclass
     *
     *@paramsuperClass
     *@parammethods
     */
    functionclazz(SuperClass,methods){
        varconstructor=function(){};
        constructor.prototype=newSuperClass;
        constructor.prototype.constructor=constructor;
        constructor.prototype.parent=SuperClass.prototype;
        constructor.prototype=$.extend(constructor.prototype,methods);
        returnconstructor;
    }

    AbstractSelect2=clazz(Object,{

        //abstract
        bind:function(func){
            varself=this;
            returnfunction(){
                func.apply(self,arguments);
            };
        },

        //abstract
        init:function(opts){
            varresults,search,resultsSelector=".select2-results";

            //prepareoptions
            this.opts=opts=this.prepareOpts(opts);

            this.id=opts.id;

            //destroyifcalledonanexistingcomponent
            if(opts.element.data("select2")!==undefined&&
                opts.element.data("select2")!==null){
                opts.element.data("select2").destroy();
            }

            this.container=this.createContainer();

            this.liveRegion=$('.select2-hidden-accessible');
            if(this.liveRegion.length==0){
                this.liveRegion=$("<span>",{
                        role:"status",
                        "aria-live":"polite"
                    })
                    .addClass("select2-hidden-accessible")
                    .appendTo(document.body);
            }

            this.containerId="s2id_"+(opts.element.attr("id")||"autogen"+nextUid());
            this.containerEventName=this.containerId
                .replace(/([.])/g,'_')
                .replace(/([;&,\-\.\+\*\~':"\!\^#$%@\[\]\(\)=>\|])/g,'\\$1');
            this.container.attr("id",this.containerId);

            this.container.attr("title",opts.element.attr("title"));

            this.body=$(document.body);

            syncCssClasses(this.container,this.opts.element,this.opts.adaptContainerCssClass);

            this.container.attr("style",opts.element.attr("style"));
            this.container.css(evaluate(opts.containerCss,this.opts.element));
            this.container.addClass(evaluate(opts.containerCssClass,this.opts.element));

            this.elementTabIndex=this.opts.element.attr("tabindex");

            //swapcontainerfortheelement
            this.opts.element
                .data("select2",this)
                .attr("tabindex","-1")
                .before(this.container)
                .on("click.select2",killEvent);//donotleakclickevents

            this.container.data("select2",this);

            this.dropdown=this.container.find(".select2-drop");

            syncCssClasses(this.dropdown,this.opts.element,this.opts.adaptDropdownCssClass);

            this.dropdown.addClass(evaluate(opts.dropdownCssClass,this.opts.element));
            this.dropdown.data("select2",this);
            this.dropdown.on("click",killEvent);

            this.results=results=this.container.find(resultsSelector);
            this.search=search=this.container.find("input.select2-input");

            this.queryCount=0;
            this.resultsPage=0;
            this.context=null;

            //initializethecontainer
            this.initContainer();

            this.container.on("click",killEvent);

            installFilteredMouseMove(this.results);

            this.dropdown.on("mousemove-filtered",resultsSelector,this.bind(this.highlightUnderEvent));
            this.dropdown.on("touchstarttouchmovetouchend",resultsSelector,this.bind(function(event){
                this._touchEvent=true;
                this.highlightUnderEvent(event);
            }));
            this.dropdown.on("touchmove",resultsSelector,this.bind(this.touchMoved));
            this.dropdown.on("touchstarttouchend",resultsSelector,this.bind(this.clearTouchMoved));

            //Waitingforaclickeventontouchdevicestoselectoptionandhidedropdown
            //otherwiseclickwillbetriggeredonanunderlyingelement
            this.dropdown.on('click',this.bind(function(event){
                if(this._touchEvent){
                    this._touchEvent=false;
                    this.selectHighlighted();
                }
            }));

            installDebouncedScroll(80,this.results);
            this.dropdown.on("scroll-debounced",resultsSelector,this.bind(this.loadMoreIfNeeded));

            //donotpropagatechangeeventfromthesearchfieldoutofthecomponent
            $(this.container).on("change",".select2-input",function(e){e.stopPropagation();});
            $(this.dropdown).on("change",".select2-input",function(e){e.stopPropagation();});

            //ifjquery.mousewheelpluginisinstalledwecanpreventout-of-boundsscrollingofresultsviamousewheel
            if($.fn.mousewheel){
                results.mousewheel(function(e,delta,deltaX,deltaY){
                    vartop=results.scrollTop();
                    if(deltaY>0&&top-deltaY<=0){
                        results.scrollTop(0);
                        killEvent(e);
                    }elseif(deltaY<0&&results.get(0).scrollHeight-results.scrollTop()+deltaY<=results.height()){
                        results.scrollTop(results.get(0).scrollHeight-results.height());
                        killEvent(e);
                    }
                });
            }

            installKeyUpChangeEvent(search);
            search.on("keyup-changeinputpaste",this.bind(this.updateResults));
            search.on("focus",function(){search.addClass("select2-focused");});
            search.on("blur",function(){search.removeClass("select2-focused");});

            this.dropdown.on("mouseup",resultsSelector,this.bind(function(e){
                if($(e.target).closest(".select2-result-selectable").length>0){
                    this.highlightUnderEvent(e);
                    this.selectHighlighted(e);
                }
            }));

            //trapallmouseeventsfromleavingthedropdown.sometimestheremaybeamodalthatislistening
            //formouseeventsoutsideofitselfsoitcancloseitself.sincethedropdownisnowoutsidetheselect2's
            //domitwilltriggerthepopupclose,whichisnotwhatwewant
            //focusincancausefocuswarsbetweenmodalsandselect2sincethedropdownisoutsidethemodal.
            this.dropdown.on("clickmouseupmousedowntouchstarttouchendfocusin",function(e){e.stopPropagation();});

            this.lastSearchTerm=undefined;

            if($.isFunction(this.opts.initSelection)){
                //initializeselectionbasedonthecurrentvalueofthesourceelement
                this.initSelection();

                //iftheuserhasprovidedafunctionthatcansetselectionbasedonthevalueofthesourceelement
                //wemonitorthechangeeventontheelementandtriggerit,allowingfortwowaysynchronization
                this.monitorSource();
            }

            if(opts.maximumInputLength!==null){
                this.search.attr("maxlength",opts.maximumInputLength);
            }

            vardisabled=opts.element.prop("disabled");
            if(disabled===undefined)disabled=false;
            this.enable(!disabled);

            varreadonly=opts.element.prop("readonly");
            if(readonly===undefined)readonly=false;
            this.readonly(readonly);

            //Calculatesizeofscrollbar
            scrollBarDimensions=scrollBarDimensions||measureScrollbar();

            this.autofocus=opts.element.prop("autofocus");
            opts.element.prop("autofocus",false);
            if(this.autofocus)this.focus();

            this.search.attr("placeholder",opts.searchInputPlaceholder);
        },

        //abstract
        destroy:function(){
            varelement=this.opts.element,select2=element.data("select2"),self=this;

            this.close();

            if(element.length&&element[0].detachEvent&&self._sync){
                element.each(function(){
                    if(self._sync){
                        this.detachEvent("onpropertychange",self._sync);
                    }
                });
            }
            if(this.propertyObserver){
                this.propertyObserver.disconnect();
                this.propertyObserver=null;
            }
            this._sync=null;

            if(select2!==undefined){
                select2.container.remove();
                select2.liveRegion.remove();
                select2.dropdown.remove();
                element.removeData("select2")
                    .off(".select2");
                if(!element.is("input[type='hidden']")){
                    element
                        .show()
                        .prop("autofocus",this.autofocus||false);
                    if(this.elementTabIndex){
                        element.attr({tabindex:this.elementTabIndex});
                    }else{
                        element.removeAttr("tabindex");
                    }
                    element.show();
                }else{
                    element.css("display","");
                }
            }

            cleanupJQueryElements.call(this,
                "container",
                "liveRegion",
                "dropdown",
                "results",
                "search"
            );
        },

        //abstract
        optionToData:function(element){
            if(element.is("option")){
                return{
                    id:element.prop("value"),
                    text:element.text(),
                    element:element.get(),
                    css:element.attr("class"),
                    disabled:element.prop("disabled"),
                    locked:equal(element.attr("locked"),"locked")||equal(element.data("locked"),true)
                };
            }elseif(element.is("optgroup")){
                return{
                    text:element.attr("label"),
                    children:[],
                    element:element.get(),
                    css:element.attr("class")
                };
            }
        },

        //abstract
        prepareOpts:function(opts){
            varelement,select,idKey,ajaxUrl,self=this;

            element=opts.element;

            if(element.get(0).tagName.toLowerCase()==="select"){
                this.select=select=opts.element;
            }

            if(select){
                //theseoptionsarenotallowedwhenattachedtoaselectbecausetheyarepickedupofftheelementitself
                $.each(["id","multiple","ajax","query","createSearchChoice","initSelection","data","tags"],function(){
                    if(thisinopts){
                        thrownewError("Option'"+this+"'isnotallowedforSelect2whenattachedtoa<select>element.");
                    }
                });
            }

            opts.debug=opts.debug||$.fn.select2.defaults.debug;

            //Warningsforoptionsrenamed/removedinSelect24.0.0
            //Onlywhenit'senabledthroughdebugmode
            if(opts.debug&&console&&console.warn){
                //idwasremoved
                if(opts.id!=null){
                    console.warn(
                        'Select2:The`id`optionhasbeenremovedinSelect24.0.0,'+
                        'considerrenamingyour`id`propertyormappingthepropertybeforeyourdatamakesittoSelect2.'+
                        'Youcanreadmoreathttps://select2.github.io/announcements-4.0.html#changed-id'
                    );
                }

                //textwasremoved
                if(opts.text!=null){
                    console.warn(
                        'Select2:The`text`optionhasbeenremovedinSelect24.0.0,'+
                        'considerrenamingyour`text`propertyormappingthepropertybeforeyourdatamakesittoSelect2.'+
                        'Youcanreadmoreathttps://select2.github.io/announcements-4.0.html#changed-id'
                    );
                }

                //sortResultswasrenamedtoresults
                if(opts.sortResults!=null){
                    console.warn(
                        'Select2:the`sortResults`optionhasbeenrenamedto`sorter`inSelect24.0.0.'
                    );
                }

                //selectOnBlurwasrenamedtoselectOnClose
                if(opts.selectOnBlur!=null){
                    console.warn(
                        'Select2:The`selectOnBlur`optionhasbeenrenamedto`selectOnClose`inSelect24.0.0.'
                    );
                }

                //ajax.resultswasrenamedtoajax.processResults
                if(opts.ajax!=null&&opts.ajax.results!=null){
                    console.warn(
                        'Select2:The`ajax.results`optionhasbeenrenamedto`ajax.processResults`inSelect24.0.0.'
                    );
                }

                //format*optionswererenamedtolanguage.*
                if(opts.formatNoResults!=null){
                    console.warn(
                        'Select2:The`formatNoResults`optionhasbeenrenamedto`language.noResults`inSelect24.0.0.'
                    );
                }
                if(opts.formatSearching!=null){
                    console.warn(
                        'Select2:The`formatSearching`optionhasbeenrenamedto`language.searching`inSelect24.0.0.'
                    );
                }
                if(opts.formatInputTooShort!=null){
                    console.warn(
                        'Select2:The`formatInputTooShort`optionhasbeenrenamedto`language.inputTooShort`inSelect24.0.0.'
                    );
                }
                if(opts.formatInputTooLong!=null){
                    console.warn(
                        'Select2:The`formatInputTooLong`optionhasbeenrenamedto`language.inputTooLong`inSelect24.0.0.'
                    );
                }
                if(opts.formatLoading!=null){
                    console.warn(
                        'Select2:The`formatLoading`optionhasbeenrenamedto`language.loadingMore`inSelect24.0.0.'
                    );
                }
                if(opts.formatSelectionTooBig!=null){
                    console.warn(
                        'Select2:The`formatSelectionTooBig`optionhasbeenrenamedto`language.maximumSelected`inSelect24.0.0.'
                    );
                }

                if(opts.element.data('select2Tags')){
                    console.warn(
                        'Select2:The`data-select2-tags`attributehasbeenrenamedto`data-tags`inSelect24.0.0.'
                    );
                }
            }

            //AliasingoptionsrenamedinSelect24.0.0

            //data-select2-tags->data-tags
            if(opts.element.data('tags')!=null){
                varelemTags=opts.element.data('tags');

                //data-tagsshouldactuallybeaboolean
                if(!$.isArray(elemTags)){
                    elemTags=[];
                }

                opts.element.data('select2Tags',elemTags);
            }

            //sortResults->sorter
            if(opts.sorter!=null){
                opts.sortResults=opts.sorter;
            }

            //selectOnBlur->selectOnClose
            if(opts.selectOnClose!=null){
                opts.selectOnBlur=opts.selectOnClose;
            }

            //ajax.results->ajax.processResults
            if(opts.ajax!=null){
                if($.isFunction(opts.ajax.processResults)){
                    opts.ajax.results=opts.ajax.processResults;
                }
            }

            //Formatters/languageoptions
            if(opts.language!=null){
                varlang=opts.language;

                //formatNoMatches->language.noMatches
                if($.isFunction(lang.noMatches)){
                    opts.formatNoMatches=lang.noMatches;
                }

                //formatSearching->language.searching
                if($.isFunction(lang.searching)){
                    opts.formatSearching=lang.searching;
                }

                //formatInputTooShort->language.inputTooShort
                if($.isFunction(lang.inputTooShort)){
                    opts.formatInputTooShort=lang.inputTooShort;
                }

                //formatInputTooLong->language.inputTooLong
                if($.isFunction(lang.inputTooLong)){
                    opts.formatInputTooLong=lang.inputTooLong;
                }

                //formatLoading->language.loadingMore
                if($.isFunction(lang.loadingMore)){
                    opts.formatLoading=lang.loadingMore;
                }

                //formatSelectionTooBig->language.maximumSelected
                if($.isFunction(lang.maximumSelected)){
                    opts.formatSelectionTooBig=lang.maximumSelected;
                }
            }

            opts=$.extend({},{
                populateResults:function(container,results,query){
                    varpopulate,id=this.opts.id,liveRegion=this.liveRegion;

                    populate=function(results,container,depth){

                        vari,l,result,selectable,disabled,compound,node,label,innerContainer,formatted;

                        results=opts.sortResults(results,container,query);

                        //collectthecreatednodesforbulkappend
                        varnodes=[];
                        for(i=0,l=results.length;i<l;i=i+1){

                            result=results[i];

                            disabled=(result.disabled===true);
                            selectable=(!disabled)&&(id(result)!==undefined);

                            compound=result.children&&result.children.length>0;

                            node=$("<li></li>");
                            node.addClass("select2-results-dept-"+depth);
                            node.addClass("select2-result");
                            node.addClass(selectable?"select2-result-selectable":"select2-result-unselectable");
                            if(disabled){node.addClass("select2-disabled");}
                            if(compound){node.addClass("select2-result-with-children");}
                            node.addClass(self.opts.formatResultCssClass(result));
                            node.attr("role","presentation");

                            label=$(document.createElement("div"));
                            label.addClass("select2-result-label");
                            label.attr("id","select2-result-label-"+nextUid());
                            label.attr("role","option");

                            formatted=opts.formatResult(result,label,query,self.opts.escapeMarkup);
                            if(formatted!==undefined){
                                label.html(formatted);
                                node.append(label);
                            }


                            if(compound){
                                innerContainer=$("<ul></ul>");
                                innerContainer.addClass("select2-result-sub");
                                populate(result.children,innerContainer,depth+1);
                                node.append(innerContainer);
                            }

                            node.data("select2-data",result);
                            nodes.push(node[0]);
                        }

                        //bulkappendthecreatednodes
                        container.append(nodes);
                        liveRegion.text(opts.formatMatches(results.length));
                    };

                    populate(results,container,0);
                }
            },$.fn.select2.defaults,opts);

            if(typeof(opts.id)!=="function"){
                idKey=opts.id;
                opts.id=function(e){returne[idKey];};
            }

            if($.isArray(opts.element.data("select2Tags"))){
                if("tags"inopts){
                    throw"tagsspecifiedasbothanattribute'data-select2-tags'andinoptionsofSelect2"+opts.element.attr("id");
                }
                opts.tags=opts.element.data("select2Tags");
            }

            if(select){
                opts.query=this.bind(function(query){
                    vardata={results:[],more:false},
                        term=query.term,
                        children,placeholderOption,process;

                    process=function(element,collection){
                        vargroup;
                        if(element.is("option")){
                            if(query.matcher(term,element.text(),element)){
                                collection.push(self.optionToData(element));
                            }
                        }elseif(element.is("optgroup")){
                            group=self.optionToData(element);
                            element.children().each2(function(i,elm){process(elm,group.children);});
                            if(group.children.length>0){
                                collection.push(group);
                            }
                        }
                    };

                    children=element.children();

                    //ignoretheplaceholderoptionifthereisone
                    if(this.getPlaceholder()!==undefined&&children.length>0){
                        placeholderOption=this.getPlaceholderOption();
                        if(placeholderOption){
                            children=children.not(placeholderOption);
                        }
                    }

                    children.each2(function(i,elm){process(elm,data.results);});

                    query.callback(data);
                });
                //thisisneededbecauseinsideval()weconstructchoicesfromoptionsandtheiridishardcoded
                opts.id=function(e){returne.id;};
            }else{
                if(!("query"inopts)){
                    if("ajax"inopts){
                        ajaxUrl=opts.element.data("ajax-url");
                        if(ajaxUrl&&ajaxUrl.length>0){
                            opts.ajax.url=ajaxUrl;
                        }
                        opts.query=ajax.call(opts.element,opts.ajax);
                    }elseif("data"inopts){
                        opts.query=local(opts.data);
                    }elseif("tags"inopts){
                        opts.query=tags(opts.tags);
                        if(opts.createSearchChoice===undefined){
                            opts.createSearchChoice=function(term){return{id:$.trim(term),text:$.trim(term)};};
                        }
                        if(opts.initSelection===undefined){
                            opts.initSelection=function(element,callback){
                                vardata=[];
                                $(splitVal(element.val(),opts.separator,opts.transformVal)).each(function(){
                                    varobj={id:this,text:this},
                                        tags=opts.tags;
                                    if($.isFunction(tags))tags=tags();
                                    $(tags).each(function(){if(equal(this.id,obj.id)){obj=this;returnfalse;}});
                                    data.push(obj);
                                });

                                callback(data);
                            };
                        }
                    }
                }
            }
            if(typeof(opts.query)!=="function"){
                throw"queryfunctionnotdefinedforSelect2"+opts.element.attr("id");
            }

            if(opts.createSearchChoicePosition==='top'){
                opts.createSearchChoicePosition=function(list,item){list.unshift(item);};
            }
            elseif(opts.createSearchChoicePosition==='bottom'){
                opts.createSearchChoicePosition=function(list,item){list.push(item);};
            }
            elseif(typeof(opts.createSearchChoicePosition)!=="function") {
                throw"invalidcreateSearchChoicePositionoptionmustbe'top','bottom'oracustomfunction";
            }

            returnopts;
        },

        /**
         *Monitortheoriginalelementforchangesandupdateselect2accordingly
         */
        //abstract
        monitorSource:function(){
            varel=this.opts.element,observer,self=this;

            el.on("change.select2",this.bind(function(e){
                if(this.opts.element.data("select2-change-triggered")!==true){
                    this.initSelection();
                }
            }));

            this._sync=this.bind(function(){

                //syncenabledstate
                vardisabled=el.prop("disabled");
                if(disabled===undefined)disabled=false;
                this.enable(!disabled);

                varreadonly=el.prop("readonly");
                if(readonly===undefined)readonly=false;
                this.readonly(readonly);

                if(this.container){
                    syncCssClasses(this.container,this.opts.element,this.opts.adaptContainerCssClass);
                    this.container.addClass(evaluate(this.opts.containerCssClass,this.opts.element));
                }

                if(this.dropdown){
                    syncCssClasses(this.dropdown,this.opts.element,this.opts.adaptDropdownCssClass);
                    this.dropdown.addClass(evaluate(this.opts.dropdownCssClass,this.opts.element));
                }

            });

            //IE8-10(IE9/10won'tfirepropertyChangeviaattachEventListener)
            if(el.length&&el[0].attachEvent){
                el.each(function(){
                    this.attachEvent("onpropertychange",self._sync);
                });
            }

            //safari,chrome,firefox,IE11
            observer=window.MutationObserver||window.WebKitMutationObserver||window.MozMutationObserver;
            if(observer!==undefined){
                if(this.propertyObserver){deletethis.propertyObserver;this.propertyObserver=null;}
                this.propertyObserver=newobserver(function(mutations){
                    $.each(mutations,self._sync);
                });
                this.propertyObserver.observe(el.get(0),{attributes:true,subtree:false});
            }
        },

        //abstract
        triggerSelect:function(data){
            varevt=$.Event("select2-selecting",{val:this.id(data),object:data,choice:data});
            this.opts.element.trigger(evt);
            return!evt.isDefaultPrevented();
        },

        /**
         *Triggersthechangeeventonthesourceelement
         */
        //abstract
        triggerChange:function(details){

            details=details||{};
            details=$.extend({},details,{type:"change",val:this.val()});
            //preventsrecursivetriggering
            this.opts.element.data("select2-change-triggered",true);
            this.opts.element.trigger(details);
            this.opts.element.data("select2-change-triggered",false);

            //somevalidationframeworksignorethechangeeventandlisteninsteadtokeyup,clickforselects
            //soherewetriggertheclickeventmanually
            this.opts.element.click();

            //ValidationEngineignoresthechangeeventandlistensinsteadtoblur
            //soherewetriggertheblureventmanuallyifsodesired
            if(this.opts.blurOnChange)
                this.opts.element.blur();
        },

        //abstract
        isInterfaceEnabled:function()
        {
            returnthis.enabledInterface===true;
        },

        //abstract
        enableInterface:function(){
            varenabled=this._enabled&&!this._readonly,
                disabled=!enabled;

            if(enabled===this.enabledInterface)returnfalse;

            this.container.toggleClass("select2-container-disabled",disabled);
            this.close();
            this.enabledInterface=enabled;

            returntrue;
        },

        //abstract
        enable:function(enabled){
            if(enabled===undefined)enabled=true;
            if(this._enabled===enabled)return;
            this._enabled=enabled;

            this.opts.element.prop("disabled",!enabled);
            this.enableInterface();
        },

        //abstract
        disable:function(){
            this.enable(false);
        },

        //abstract
        readonly:function(enabled){
            if(enabled===undefined)enabled=false;
            if(this._readonly===enabled)return;
            this._readonly=enabled;

            this.opts.element.prop("readonly",enabled);
            this.enableInterface();
        },

        //abstract
        opened:function(){
            return(this.container)?this.container.hasClass("select2-dropdown-open"):false;
        },

        //abstract
        positionDropdown:function(){
            var$dropdown=this.dropdown,
                container=this.container,
                offset=container.offset(),
                height=container.outerHeight(false),
                width=container.outerWidth(false),
                dropHeight=$dropdown.outerHeight(false),
                $window=$(window),
                windowWidth=$window.width(),
                windowHeight=$window.height(),
                viewPortRight=$window.scrollLeft()+windowWidth,
                viewportBottom=$window.scrollTop()+windowHeight,
                dropTop=offset.top+height,
                dropLeft=offset.left,
                enoughRoomBelow=dropTop+dropHeight<=viewportBottom,
                enoughRoomAbove=(offset.top-dropHeight)>=$window.scrollTop(),
                dropWidth=$dropdown.outerWidth(false),
                enoughRoomOnRight=function(){
                    returndropLeft+dropWidth<=viewPortRight;
                },
                enoughRoomOnLeft=function(){
                    returnoffset.left+viewPortRight+container.outerWidth(false) >dropWidth;
                },
                aboveNow=$dropdown.hasClass("select2-drop-above"),
                bodyOffset,
                above,
                changeDirection,
                css,
                resultsListNode;

            //alwayspreferthecurrentabove/belowalignment,unlessthereisnotenoughroom
            if(aboveNow){
                above=true;
                if(!enoughRoomAbove&&enoughRoomBelow){
                    changeDirection=true;
                    above=false;
                }
            }else{
                above=false;
                if(!enoughRoomBelow&&enoughRoomAbove){
                    changeDirection=true;
                    above=true;
                }
            }

            //ifwearechangingdirectionweneedtogetpositionswhendropdownishidden;
            if(changeDirection){
                $dropdown.hide();
                offset=this.container.offset();
                height=this.container.outerHeight(false);
                width=this.container.outerWidth(false);
                dropHeight=$dropdown.outerHeight(false);
                viewPortRight=$window.scrollLeft()+windowWidth;
                viewportBottom=$window.scrollTop()+windowHeight;
                dropTop=offset.top+height;
                dropLeft=offset.left;
                dropWidth=$dropdown.outerWidth(false);
                $dropdown.show();

                //fixsothecursordoesnotmovetotheleftwithinthesearch-textboxinIE
                this.focusSearch();
            }

            if(this.opts.dropdownAutoWidth){
                resultsListNode=$('.select2-results',$dropdown)[0];
                $dropdown.addClass('select2-drop-auto-width');
                $dropdown.css('width','');
                //Addscrollbarwidthtodropdownifverticalscrollbarispresent
                dropWidth=$dropdown.outerWidth(false)+(resultsListNode.scrollHeight===resultsListNode.clientHeight?0:scrollBarDimensions.width);
                dropWidth>width?width=dropWidth:dropWidth=width;
                dropHeight=$dropdown.outerHeight(false);
            }
            else{
                this.container.removeClass('select2-drop-auto-width');
            }

            //console.log("below/droptop:",dropTop,"dropHeight",dropHeight,"sum",(dropTop+dropHeight)+"viewportbottom",viewportBottom,"enough?",enoughRoomBelow);
            //console.log("above/offset.top",offset.top,"dropHeight",dropHeight,"top",(offset.top-dropHeight),"scrollTop",this.body.scrollTop(),"enough?",enoughRoomAbove);

            //fixpositioningwhenbodyhasanoffsetandisnotposition:static
            if(this.body.css('position')!=='static'){
                bodyOffset=this.body.offset();
                dropTop-=bodyOffset.top;
                dropLeft-=bodyOffset.left;
            }

            if(!enoughRoomOnRight()&&enoughRoomOnLeft()){
                dropLeft=offset.left+this.container.outerWidth(false)-dropWidth;
            }

            css= {
                left:dropLeft,
                width:width
            };

            if(above){
                this.container.addClass("select2-drop-above");
                $dropdown.addClass("select2-drop-above");
                dropHeight=$dropdown.outerHeight(false);
                css.top=offset.top-dropHeight;
                css.bottom='auto';
            }
            else{
                css.top=dropTop;
                css.bottom='auto';
                this.container.removeClass("select2-drop-above");
                $dropdown.removeClass("select2-drop-above");
            }
            css=$.extend(css,evaluate(this.opts.dropdownCss,this.opts.element));

            $dropdown.css(css);
        },

        //abstract
        shouldOpen:function(){
            varevent;

            if(this.opened())returnfalse;

            if(this._enabled===false||this._readonly===true)returnfalse;

            event=$.Event("select2-opening");
            this.opts.element.trigger(event);
            return!event.isDefaultPrevented();
        },

        //abstract
        clearDropdownAlignmentPreference:function(){
            //cleartheclassesusedtofigureoutthepreferenceofwherethedropdownshouldbeopened
            this.container.removeClass("select2-drop-above");
            this.dropdown.removeClass("select2-drop-above");
        },

        /**
         *Opensthedropdown
         *
         *@return{Boolean}whetherornotdropdownwasopened.Thismethodwillreturnfalseif,forexample,
         *thedropdownisalreadyopen,orifthe'open'eventlistenerontheelementcalledpreventDefault().
         */
        //abstract
        open:function(){

            if(!this.shouldOpen())returnfalse;

            this.opening();

            //Onlybindthedocumentmousemovewhenthedropdownisvisible
            $document.on("mousemove.select2Event",function(e){
                lastMousePosition.x=e.pageX;
                lastMousePosition.y=e.pageY;
            });

            returntrue;
        },

        /**
         *Performstheopeningofthedropdown
         */
        //abstract
        opening:function(){
            varcid=this.containerEventName,
                scroll="scroll."+cid,
                resize="resize."+cid,
                orient="orientationchange."+cid,
                mask;

            this.container.addClass("select2-dropdown-open").addClass("select2-container-active");

            this.clearDropdownAlignmentPreference();

            if(this.dropdown[0]!==this.body.children().last()[0]){
                this.dropdown.detach().appendTo(this.body);
            }

            //createthedropdownmaskifdoesn'talreadyexist
            mask=$("#select2-drop-mask");
            if(mask.length===0){
                mask=$(document.createElement("div"));
                mask.attr("id","select2-drop-mask").attr("class","select2-drop-mask");
                mask.hide();
                mask.appendTo(this.body);
                mask.on("mousedowntouchstartclick",function(e){
                    //PreventIEfromgeneratingaclickeventonthebody
                    reinsertElement(mask);

                    vardropdown=$("#select2-drop"),self;
                    if(dropdown.length>0){
                        self=dropdown.data("select2");
                        if(self.opts.selectOnBlur){
                            self.selectHighlighted({noFocus:true});
                        }
                        self.close();
                        e.preventDefault();
                        e.stopPropagation();
                    }
                });
            }

            //ensurethemaskisalwaysrightbeforethedropdown
            if(this.dropdown.prev()[0]!==mask[0]){
                this.dropdown.before(mask);
            }

            //movetheglobalidtothecorrectdropdown
            $("#select2-drop").removeAttr("id");
            this.dropdown.attr("id","select2-drop");

            //showtheelements
            mask.show();

            this.positionDropdown();
            this.dropdown.show();
            this.positionDropdown();

            this.dropdown.addClass("select2-drop-active");

            //attachlistenerstoeventsthatcanchangethepositionofthecontainerandthusrequire
            //thepositionofthedropdowntobeupdatedaswellsoitdoesnotcomeungluedfromthecontainer
            varthat=this;
            this.container.parents().add(window).each(function(){
                $(this).on(resize+""+scroll+""+orient,function(e){
                    if(that.opened())that.positionDropdown();
                });
            });


        },

        //abstract
        close:function(){
            if(!this.opened())return;

            varcid=this.containerEventName,
                scroll="scroll."+cid,
                resize="resize."+cid,
                orient="orientationchange."+cid;

            //unbindeventlisteners
            this.container.parents().add(window).each(function(){$(this).off(scroll).off(resize).off(orient);});

            this.clearDropdownAlignmentPreference();

            $("#select2-drop-mask").hide();
            this.dropdown.removeAttr("id");//onlytheactivedropdownhastheselect2-dropid
            this.dropdown.hide();
            this.container.removeClass("select2-dropdown-open").removeClass("select2-container-active");
            this.results.empty();

            //Nowthatthedropdownisclosed,unbindtheglobaldocumentmousemoveevent
            $document.off("mousemove.select2Event");

            this.clearSearch();
            this.search.removeClass("select2-active");

            //Removetheariaactivedescendantforhighlightedelement
            this.search.removeAttr("aria-activedescendant");
            this.opts.element.trigger($.Event("select2-close"));
        },

        /**
         *Openscontrol,setsinputvalue,andupdatesresults.
         */
        //abstract
        externalSearch:function(term){
            this.open();
            this.search.val(term);
            this.updateResults(false);
        },

        //abstract
        clearSearch:function(){

        },

        /**
         *@return{Boolean}Whetherornotsearchvaluewaschanged.
         *@private
         */
        prefillNextSearchTerm:function(){
            //initializessearch'svaluewithnextSearchTerm(ifdefinedbyuser)
            //ignorenextSearchTermifthedropdownisopenedbytheuserpressingaletter
            if(this.search.val()!==""){
                returnfalse;
            }

            varnextSearchTerm=this.opts.nextSearchTerm(this.data(),this.lastSearchTerm);
            if(nextSearchTerm!==undefined){
                this.search.val(nextSearchTerm);
                this.search.select();
                returntrue;
            }

            returnfalse;
        },

        //abstract
        getMaximumSelectionSize:function(){
            returnevaluate(this.opts.maximumSelectionSize,this.opts.element);
        },

        //abstract
        ensureHighlightVisible:function(){
            varresults=this.results,children,index,child,hb,rb,y,more,topOffset;

            index=this.highlight();

            if(index<0)return;

            if(index==0){

                //ifthefirstelementishighlightedscrollallthewaytothetop,
                //thatwayanyunselectableheadersaboveitwillalsobescrolled
                //intoview

                results.scrollTop(0);
                return;
            }

            children=this.findHighlightableChoices().find('.select2-result-label');

            child=$(children[index]);

            topOffset=(child.offset()||{}).top||0;

            hb=topOffset+child.outerHeight(true);

            //ifthisisthelastchildletsalsomakesureselect2-more-resultsisvisible
            if(index===children.length-1){
                more=results.find("li.select2-more-results");
                if(more.length>0){
                    hb=more.offset().top+more.outerHeight(true);
                }
            }

            rb=results.offset().top+results.outerHeight(false);
            if(hb>rb){
                results.scrollTop(results.scrollTop()+(hb-rb));
            }
            y=topOffset-results.offset().top;

            //makesurethetopoftheelementisvisible
            if(y<0&&child.css('display')!='none'){
                results.scrollTop(results.scrollTop()+y);//yisnegative
            }
        },

        //abstract
        findHighlightableChoices:function(){
            returnthis.results.find(".select2-result-selectable:not(.select2-disabled):not(.select2-selected)");
        },

        //abstract
        moveHighlight:function(delta){
            varchoices=this.findHighlightableChoices(),
                index=this.highlight();

            while(index>-1&&index<choices.length){
                index+=delta;
                varchoice=$(choices[index]);
                if(choice.hasClass("select2-result-selectable")&&!choice.hasClass("select2-disabled")&&!choice.hasClass("select2-selected")){
                    this.highlight(index);
                    break;
                }
            }
        },

        //abstract
        highlight:function(index){
            varchoices=this.findHighlightableChoices(),
                choice,
                data;

            if(arguments.length===0){
                returnindexOf(choices.filter(".select2-highlighted")[0],choices.get());
            }

            if(index>=choices.length)index=choices.length-1;
            if(index<0)index=0;

            this.removeHighlight();

            choice=$(choices[index]);
            choice.addClass("select2-highlighted");

            //ensureassistivetechnologycandeterminetheactivechoice
            this.search.attr("aria-activedescendant",choice.find(".select2-result-label").attr("id"));

            this.ensureHighlightVisible();

            this.liveRegion.text(choice.text());

            data=choice.data("select2-data");
            if(data){
                this.opts.element.trigger({type:"select2-highlight",val:this.id(data),choice:data});
            }
        },

        removeHighlight:function(){
            this.results.find(".select2-highlighted").removeClass("select2-highlighted");
        },

        touchMoved:function(){
            this._touchMoved=true;
        },

        clearTouchMoved:function(){
          this._touchMoved=false;
        },

        //abstract
        countSelectableResults:function(){
            returnthis.findHighlightableChoices().length;
        },

        //abstract
        highlightUnderEvent:function(event){
            varel=$(event.target).closest(".select2-result-selectable");
            if(el.length>0&&!el.is(".select2-highlighted")){
                varchoices=this.findHighlightableChoices();
                this.highlight(choices.index(el));
            }elseif(el.length==0){
                //ifweareoveranunselectableitemremoveallhighlights
                this.removeHighlight();
            }
        },

        //abstract
        loadMoreIfNeeded:function(){
            varresults=this.results,
                more=results.find("li.select2-more-results"),
                below,//pixelstheelementisbelowthescrollfold,below==0iswhentheelementisstartingtobevisible
                page=this.resultsPage+1,
                self=this,
                term=this.search.val(),
                context=this.context;

            if(more.length===0)return;
            below=more.offset().top-results.offset().top-results.height();

            if(below<=this.opts.loadMorePadding){
                more.addClass("select2-active");
                this.opts.query({
                        element:this.opts.element,
                        term:term,
                        page:page,
                        context:context,
                        matcher:this.opts.matcher,
                        callback:this.bind(function(data){

                    //ignorearesponseiftheselect2hasbeenclosedbeforeitwasreceived
                    if(!self.opened())return;


                    self.opts.populateResults.call(this,results,data.results,{term:term,page:page,context:context});
                    self.postprocessResults(data,false,false);

                    if(data.more===true){
                        more.detach().appendTo(results).html(self.opts.escapeMarkup(evaluate(self.opts.formatLoadMore,self.opts.element,page+1)));
                        window.setTimeout(function(){self.loadMoreIfNeeded();},10);
                    }else{
                        more.remove();
                    }
                    self.positionDropdown();
                    self.resultsPage=page;
                    self.context=data.context;
                    this.opts.element.trigger({type:"select2-loaded",items:data});
                })});
            }
        },

        /**
         *Defaulttokenizerfunctionwhichdoesnothing
         */
        tokenize:function(){

        },

        /**
         *@paraminitialwhetherornotthisisthecalltothismethodrightafterthedropdownhasbeenopened
         */
        //abstract
        updateResults:function(initial){
            varsearch=this.search,
                results=this.results,
                opts=this.opts,
                data,
                self=this,
                input,
                term=search.val(),
                lastTerm=$.data(this.container,"select2-last-term"),
                //sequencenumberusedtodropout-of-orderresponses
                queryNumber;

            //preventduplicatequeriesagainstthesameterm
            if(initial!==true&&lastTerm&&equal(term,lastTerm))return;

            $.data(this.container,"select2-last-term",term);

            //ifthesearchiscurrentlyhiddenwedonotaltertheresults
            if(initial!==true&&(this.showSearchInput===false||!this.opened())){
                return;
            }

            functionpostRender(){
                search.removeClass("select2-active");
                self.positionDropdown();
                if(results.find('.select2-no-results,.select2-selection-limit,.select2-searching').length){
                    self.liveRegion.text(results.text());
                }
                else{
                    self.liveRegion.text(self.opts.formatMatches(results.find('.select2-result-selectable:not(".select2-selected")').length));
                }
            }

            functionrender(html){
                results.html(html);
                postRender();
            }

            queryNumber=++this.queryCount;

            varmaxSelSize=this.getMaximumSelectionSize();
            if(maxSelSize>=1){
                data=this.data();
                if($.isArray(data)&&data.length>=maxSelSize&&checkFormatter(opts.formatSelectionTooBig,"formatSelectionTooBig")){
                    render("<liclass='select2-selection-limit'>"+evaluate(opts.formatSelectionTooBig,opts.element,maxSelSize)+"</li>");
                    return;
                }
            }

            if(search.val().length<opts.minimumInputLength){
                if(checkFormatter(opts.formatInputTooShort,"formatInputTooShort")){
                    render("<liclass='select2-no-results'>"+evaluate(opts.formatInputTooShort,opts.element,search.val(),opts.minimumInputLength)+"</li>");
                }else{
                    render("");
                }
                if(initial&&this.showSearch)this.showSearch(true);
                return;
            }

            if(opts.maximumInputLength&&search.val().length>opts.maximumInputLength){
                if(checkFormatter(opts.formatInputTooLong,"formatInputTooLong")){
                    render("<liclass='select2-no-results'>"+evaluate(opts.formatInputTooLong,opts.element,search.val(),opts.maximumInputLength)+"</li>");
                }else{
                    render("");
                }
                return;
            }

            if(opts.formatSearching&&this.findHighlightableChoices().length===0){
                render("<liclass='select2-searching'>"+evaluate(opts.formatSearching,opts.element)+"</li>");
            }

            search.addClass("select2-active");

            this.removeHighlight();

            //givethetokenizerachancetopre-processtheinput
            input=this.tokenize();
            if(input!=undefined&&input!=null){
                search.val(input);
            }

            this.resultsPage=1;

            opts.query({
                element:opts.element,
                    term:search.val(),
                    page:this.resultsPage,
                    context:null,
                    matcher:opts.matcher,
                    callback:this.bind(function(data){
                vardef;//defaultchoice

                //ignoreoldresponses
                if(queryNumber!=this.queryCount){
                  return;
                }

                //ignorearesponseiftheselect2hasbeenclosedbeforeitwasreceived
                if(!this.opened()){
                    this.search.removeClass("select2-active");
                    return;
                }

                //handleajaxerror
                if(data.hasError!==undefined&&checkFormatter(opts.formatAjaxError,"formatAjaxError")){
                    render("<liclass='select2-ajax-error'>"+evaluate(opts.formatAjaxError,opts.element,data.jqXHR,data.textStatus,data.errorThrown)+"</li>");
                    return;
                }

                //savecontext,ifany
                this.context=(data.context===undefined)?null:data.context;
                //createadefaultchoiceandprependittothelist
                if(this.opts.createSearchChoice&&search.val()!==""){
                    def=this.opts.createSearchChoice.call(self,search.val(),data.results);
                    if(def!==undefined&&def!==null&&self.id(def)!==undefined&&self.id(def)!==null){
                        if($(data.results).filter(
                            function(){
                                returnequal(self.id(this),self.id(def));
                            }).length===0){
                            this.opts.createSearchChoicePosition(data.results,def);
                        }
                    }
                }

                if(data.results.length===0&&checkFormatter(opts.formatNoMatches,"formatNoMatches")){
                    render("<liclass='select2-no-results'>"+evaluate(opts.formatNoMatches,opts.element,search.val())+"</li>");
                    if(this.showSearch){
                        this.showSearch(search.val());
                    }
                    return;
                }

                results.empty();
                self.opts.populateResults.call(this,results,data.results,{term:search.val(),page:this.resultsPage,context:null});

                if(data.more===true&&checkFormatter(opts.formatLoadMore,"formatLoadMore")){
                    results.append("<liclass='select2-more-results'>"+opts.escapeMarkup(evaluate(opts.formatLoadMore,opts.element,this.resultsPage))+"</li>");
                    window.setTimeout(function(){self.loadMoreIfNeeded();},10);
                }

                this.postprocessResults(data,initial);

                postRender();

                this.opts.element.trigger({type:"select2-loaded",items:data});
            })});
        },

        //abstract
        cancel:function(){
            this.close();
        },

        //abstract
        blur:function(){
            //ifselectOnBlur==true,selectthecurrentlyhighlightedoption
            if(this.opts.selectOnBlur)
                this.selectHighlighted({noFocus:true});

            this.close();
            this.container.removeClass("select2-container-active");
            //synonymousto.is(':focus'),whichisavailableinjquery>=1.6
            if(this.search[0]===document.activeElement){this.search.blur();}
            this.clearSearch();
            this.selection.find(".select2-search-choice-focus").removeClass("select2-search-choice-focus");
        },

        //abstract
        focusSearch:function(){
            focus(this.search);
        },

        //abstract
        selectHighlighted:function(options){
            if(this._touchMoved){
              this.clearTouchMoved();
              return;
            }
            varindex=this.highlight(),
                highlighted=this.results.find(".select2-highlighted"),
                data=highlighted.closest('.select2-result').data("select2-data");

            if(data){
                this.highlight(index);
                this.onSelect(data,options);
            }elseif(options&&options.noFocus){
                this.close();
            }
        },

        //abstract
        getPlaceholder:function(){
            varplaceholderOption;
            returnthis.opts.element.attr("placeholder")||
                this.opts.element.attr("data-placeholder")||//jquery1.4compat
                this.opts.element.data("placeholder")||
                this.opts.placeholder||
                ((placeholderOption=this.getPlaceholderOption())!==undefined?placeholderOption.text():undefined);
        },

        //abstract
        getPlaceholderOption:function(){
            if(this.select){
                varfirstOption=this.select.children('option').first();
                if(this.opts.placeholderOption!==undefined){
                    //DeterminetheplaceholderoptionbasedonthespecifiedplaceholderOptionsetting
                    return(this.opts.placeholderOption==="first"&&firstOption)||
                           (typeofthis.opts.placeholderOption==="function"&&this.opts.placeholderOption(this.select));
                }elseif($.trim(firstOption.text())===""&&firstOption.val()===""){
                    //Noexplicitplaceholderoptionspecified,usethefirstifit'sblank
                    returnfirstOption;
                }
            }
        },

        /**
         *Getthedesiredwidthforthecontainerelement. Thisis
         *derivedfirstfromoption`width`passedtoselect2,then
         *theinline'style'ontheoriginalelement,andfinally
         *fallsbacktothejQuerycalculatedelementwidth.
         */
        //abstract
        initContainerWidth:function(){
            functionresolveContainerWidth(){
                varstyle,attrs,matches,i,l,attr;

                if(this.opts.width==="off"){
                    returnnull;
                }elseif(this.opts.width==="element"){
                    returnthis.opts.element.outerWidth(false)===0?'auto':this.opts.element.outerWidth(false)+'px';
                }elseif(this.opts.width==="copy"||this.opts.width==="resolve"){
                    //checkifthereisinlinestyleontheelementthatcontainswidth
                    style=this.opts.element.attr('style');
                    if(typeof(style)==="string"){
                        attrs=style.split(';');
                        for(i=0,l=attrs.length;i<l;i=i+1){
                            attr=attrs[i].replace(/\s/g,'');
                            matches=attr.match(/^width:(([-+]?([0-9]*\.)?[0-9]+)(px|em|ex|%|in|cm|mm|pt|pc))/i);
                            if(matches!==null&&matches.length>=1)
                                returnmatches[1];
                        }
                    }

                    if(this.opts.width==="resolve"){
                        //nextcheckifcss('width')canresolveawidththatispercentbased,thisissometimespossible
                        //whenattachedtoinputtype=hiddenorelementshiddenviacss
                        style=this.opts.element.css('width');
                        if(style.indexOf("%")>0)returnstyle;

                        //finally,fallbackonthecalculatedwidthoftheelement
                        return(this.opts.element.outerWidth(false)===0?'auto':this.opts.element.outerWidth(false)+'px');
                    }

                    returnnull;
                }elseif($.isFunction(this.opts.width)){
                    returnthis.opts.width();
                }else{
                    returnthis.opts.width;
               }
            };

            varwidth=resolveContainerWidth.call(this);
            if(width!==null){
                this.container.css("width",width);
            }
        }
    });

    SingleSelect2=clazz(AbstractSelect2,{

        //single

        createContainer:function(){
            varcontainer=$(document.createElement("div")).attr({
                "class":"select2-container"
            }).html([
                "<ahref='javascript:void(0)'class='select2-choice'tabindex='-1'>",
                "  <spanclass='select2-chosen'>&#160;</span><abbrclass='select2-search-choice-close'></abbr>",
                "  <spanclass='select2-arrow'role='presentation'><brole='presentation'></b></span>",
                "</a>",
                "<labelfor=''class='select2-offscreen'></label>",
                "<inputclass='select2-focusserselect2-offscreen'type='text'aria-haspopup='true'role='button'/>",
                "<divclass='select2-dropselect2-display-none'>",
                "  <divclass='select2-search'>",
                "      <labelfor=''class='select2-offscreen'></label>",
                "      <inputtype='text'autocomplete='off'autocorrect='off'autocapitalize='off'spellcheck='false'class='select2-input'role='combobox'aria-expanded='true'",
                "      aria-autocomplete='list'/>",
                "  </div>",
                "  <ulclass='select2-results'role='listbox'>",
                "  </ul>",
                "</div>"].join(""));
            returncontainer;
        },

        //single
        enableInterface:function(){
            if(this.parent.enableInterface.apply(this,arguments)){
                this.focusser.prop("disabled",!this.isInterfaceEnabled());
            }
        },

        //single
        opening:function(){
            varel,range,len;

            if(this.opts.minimumResultsForSearch>=0){
                this.showSearch(true);
            }

            this.parent.opening.apply(this,arguments);

            if(this.showSearchInput!==false){
                //IEappendsfocusser.val()attheendoffield:/sowemanuallyinsertitatthebeginningusingarange
                //allotherbrowsershandlethisjustfine

                this.search.val(this.focusser.val());
            }
            if(this.opts.shouldFocusInput(this)){
                this.search.focus();
                //movethecursortotheendafterfocussing,otherwiseitwillbeatthebeginningand
                //newtextwillappear*before*focusser.val()
                el=this.search.get(0);
                if(el.createTextRange){
                    range=el.createTextRange();
                    range.collapse(false);
                    range.select();
                }elseif(el.setSelectionRange){
                    len=this.search.val().length;
                    el.setSelectionRange(len,len);
                }
            }

            this.prefillNextSearchTerm();

            this.focusser.prop("disabled",true).val("");
            this.updateResults(true);
            this.opts.element.trigger($.Event("select2-open"));
        },

        //single
        close:function(){
            if(!this.opened())return;
            this.parent.close.apply(this,arguments);

            this.focusser.prop("disabled",false);

            if(this.opts.shouldFocusInput(this)){
                this.focusser.focus();
            }
        },

        //single
        focus:function(){
            if(this.opened()){
                this.close();
            }else{
                this.focusser.prop("disabled",false);
                if(this.opts.shouldFocusInput(this)){
                    this.focusser.focus();
                }
            }
        },

        //single
        isFocused:function(){
            returnthis.container.hasClass("select2-container-active");
        },

        //single
        cancel:function(){
            this.parent.cancel.apply(this,arguments);
            this.focusser.prop("disabled",false);

            if(this.opts.shouldFocusInput(this)){
                this.focusser.focus();
            }
        },

        //single
        destroy:function(){
            $("label[for='"+this.focusser.attr('id')+"']")
                .attr('for',this.opts.element.attr("id"));
            this.parent.destroy.apply(this,arguments);

            cleanupJQueryElements.call(this,
                "selection",
                "focusser"
            );
        },

        //single
        initContainer:function(){

            varselection,
                container=this.container,
                dropdown=this.dropdown,
                idSuffix=nextUid(),
                elementLabel;

            if(this.opts.minimumResultsForSearch<0){
                this.showSearch(false);
            }else{
                this.showSearch(true);
            }

            this.selection=selection=container.find(".select2-choice");

            this.focusser=container.find(".select2-focusser");

            //addariaassociations
            selection.find(".select2-chosen").attr("id","select2-chosen-"+idSuffix);
            this.focusser.attr("aria-labelledby","select2-chosen-"+idSuffix);
            this.results.attr("id","select2-results-"+idSuffix);
            this.search.attr("aria-owns","select2-results-"+idSuffix);

            //rewritelabelsfromoriginalelementtofocusser
            this.focusser.attr("id","s2id_autogen"+idSuffix);

            elementLabel=$("label[for='"+this.opts.element.attr("id")+"']");
            this.opts.element.on('focus.select2',this.bind(function(){this.focus();}));

            this.focusser.prev()
                .text(elementLabel.text())
                .attr('for',this.focusser.attr('id'));

            //Ensuretheoriginalelementretainsanaccessiblename
            varoriginalTitle=this.opts.element.attr("title");
            this.opts.element.attr("title",(originalTitle||elementLabel.text()));

            this.focusser.attr("tabindex",this.elementTabIndex);

            //writelabelforsearchfieldusingthelabelfromthefocusserelement
            this.search.attr("id",this.focusser.attr('id')+'_search');

            this.search.prev()
                .text($("label[for='"+this.focusser.attr('id')+"']").text())
                .attr('for',this.search.attr('id'));

            this.search.on("keydown",this.bind(function(e){
                if(!this.isInterfaceEnabled())return;

                //filter229keyCodes(inputmethodeditorisprocessingkeyinput)
                if(229==e.keyCode)return;

                if(e.which===KEY.PAGE_UP||e.which===KEY.PAGE_DOWN){
                    //preventthepagefromscrolling
                    killEvent(e);
                    return;
                }

                switch(e.which){
                    caseKEY.UP:
                    caseKEY.DOWN:
                        this.moveHighlight((e.which===KEY.UP)?-1:1);
                        killEvent(e);
                        return;
                    caseKEY.ENTER:
                        this.selectHighlighted();
                        killEvent(e);
                        return;
                    caseKEY.TAB:
                        this.selectHighlighted({noFocus:true});
                        return;
                    caseKEY.ESC:
                        this.cancel(e);
                        killEvent(e);
                        return;
                }
            }));

            this.search.on("blur",this.bind(function(e){
                //aworkaroundforchrometokeepthesearchfieldfocussedwhenthescrollbarisusedtoscrollthedropdown.
                //withoutthisthesearchfieldlosesfocuswhichisannoying
                if(document.activeElement===this.body.get(0)){
                    window.setTimeout(this.bind(function(){
                        if(this.opened()&&this.results&&this.results.length>1){
                            this.search.focus();
                        }
                    }),0);
                }
            }));

            this.focusser.on("keydown",this.bind(function(e){
                if(!this.isInterfaceEnabled())return;

                if(e.which===KEY.TAB||KEY.isControl(e)||KEY.isFunctionKey(e)||e.which===KEY.ESC){
                    return;
                }

                if(this.opts.openOnEnter===false&&e.which===KEY.ENTER){
                    killEvent(e);
                    return;
                }

                if(e.which==KEY.DOWN||e.which==KEY.UP
                    ||(e.which==KEY.ENTER&&this.opts.openOnEnter)){

                    if(e.altKey||e.ctrlKey||e.shiftKey||e.metaKey)return;

                    this.open();
                    killEvent(e);
                    return;
                }

                if(e.which==KEY.DELETE||e.which==KEY.BACKSPACE){
                    if(this.opts.allowClear){
                        this.clear();
                    }
                    killEvent(e);
                    return;
                }
            }));


            installKeyUpChangeEvent(this.focusser);
            this.focusser.on("keyup-changeinput",this.bind(function(e){
                if(this.opts.minimumResultsForSearch>=0){
                    e.stopPropagation();
                    if(this.opened())return;
                    this.open();
                }
            }));

            selection.on("mousedowntouchstart","abbr",this.bind(function(e){
                if(!this.isInterfaceEnabled()){
                    return;
                }

                this.clear();
                killEventImmediately(e);
                this.close();

                if(this.selection){
                    this.selection.focus();
                }
            }));

            selection.on("mousedowntouchstart",this.bind(function(e){
                //PreventIEfromgeneratingaclickeventonthebody
                reinsertElement(selection);

                if(!this.container.hasClass("select2-container-active")){
                    this.opts.element.trigger($.Event("select2-focus"));
                }

                if(this.opened()){
                    this.close();
                }elseif(this.isInterfaceEnabled()){
                    this.open();
                }

                killEvent(e);
            }));

            dropdown.on("mousedowntouchstart",this.bind(function(){
                if(this.opts.shouldFocusInput(this)){
                    this.search.focus();
                }
            }));

            selection.on("focus",this.bind(function(e){
                killEvent(e);
            }));

            this.focusser.on("focus",this.bind(function(){
                if(!this.container.hasClass("select2-container-active")){
                    this.opts.element.trigger($.Event("select2-focus"));
                }
                this.container.addClass("select2-container-active");
            })).on("blur",this.bind(function(){
                if(!this.opened()){
                    this.container.removeClass("select2-container-active");
                    this.opts.element.trigger($.Event("select2-blur"));
                }
            }));
            this.search.on("focus",this.bind(function(){
                if(!this.container.hasClass("select2-container-active")){
                    this.opts.element.trigger($.Event("select2-focus"));
                }
                this.container.addClass("select2-container-active");
            }));

            this.initContainerWidth();
            this.opts.element.hide();
            this.setPlaceholder();

        },

        //single
        clear:function(triggerChange){
            vardata=this.selection.data("select2-data");
            if(data){//guardagainstqueuedquickconsecutiveclicks
                varevt=$.Event("select2-clearing");
                this.opts.element.trigger(evt);
                if(evt.isDefaultPrevented()){
                    return;
                }
                varplaceholderOption=this.getPlaceholderOption();
                this.opts.element.val(placeholderOption?placeholderOption.val():"");
                this.selection.find(".select2-chosen").empty();
                this.selection.removeData("select2-data");
                this.setPlaceholder();

                if(triggerChange!==false){
                    this.opts.element.trigger({type:"select2-removed",val:this.id(data),choice:data});
                    this.triggerChange({removed:data});
                }
            }
        },

        /**
         *Setsselectionbasedonsourceelement'svalue
         */
        //single
        initSelection:function(){
            varselected;
            if(this.isPlaceholderOptionSelected()){
                this.updateSelection(null);
                this.close();
                this.setPlaceholder();
            }else{
                varself=this;
                this.opts.initSelection.call(null,this.opts.element,function(selected){
                    if(selected!==undefined&&selected!==null){
                        self.updateSelection(selected);
                        self.close();
                        self.setPlaceholder();
                        self.lastSearchTerm=self.search.val();
                    }
                });
            }
        },

        isPlaceholderOptionSelected:function(){
            varplaceholderOption;
            if(this.getPlaceholder()===undefined)returnfalse;//noplaceholderspecifiedsonooptionshouldbeconsidered
            return((placeholderOption=this.getPlaceholderOption())!==undefined&&placeholderOption.prop("selected"))
                ||(this.opts.element.val()==="")
                ||(this.opts.element.val()===undefined)
                ||(this.opts.element.val()===null);
        },

        //single
        prepareOpts:function(){
            varopts=this.parent.prepareOpts.apply(this,arguments),
                self=this;

            if(opts.element.get(0).tagName.toLowerCase()==="select"){
                //installtheselectioninitializer
                opts.initSelection=function(element,callback){
                    varselected=element.find("option").filter(function(){returnthis.selected&&!this.disabled});
                    //asingleselectboxalwayshasavalue,noneedtonullcheck'selected'
                    callback(self.optionToData(selected));
                };
            }elseif("data"inopts){
                //installdefaultinitSelectionwhenappliedtohiddeninputanddataislocal
                opts.initSelection=opts.initSelection||function(element,callback){
                    varid=element.val();
                    //searchindatabyid,storingtheactualmatchingitem
                    varmatch=null;
                    opts.query({
                        matcher:function(term,text,el){
                            varis_match=equal(id,opts.id(el));
                            if(is_match){
                                match=el;
                            }
                            returnis_match;
                        },
                        callback:!$.isFunction(callback)?$.noop:function(){
                            callback(match);
                        }
                    });
                };
            }

            returnopts;
        },

        //single
        getPlaceholder:function(){
            //ifaplaceholderisspecifiedonasingleselectwithoutavalidplaceholderoptionignoreit
            if(this.select){
                if(this.getPlaceholderOption()===undefined){
                    returnundefined;
                }
            }

            returnthis.parent.getPlaceholder.apply(this,arguments);
        },

        //single
        setPlaceholder:function(){
            varplaceholder=this.getPlaceholder();

            if(this.isPlaceholderOptionSelected()&&placeholder!==undefined){

                //checkforaplaceholderoptionifattachedtoaselect
                if(this.select&&this.getPlaceholderOption()===undefined)return;

                this.selection.find(".select2-chosen").html(this.opts.escapeMarkup(placeholder));

                this.selection.addClass("select2-default");

                this.container.removeClass("select2-allowclear");
            }
        },

        //single
        postprocessResults:function(data,initial,noHighlightUpdate){
            varselected=0,self=this,showSearchInput=true;

            //findtheselectedelementintheresultlist

            this.findHighlightableChoices().each2(function(i,elm){
                if(equal(self.id(elm.data("select2-data")),self.opts.element.val())){
                    selected=i;
                    returnfalse;
                }
            });

            //andhighlightit
            if(noHighlightUpdate!==false){
                if(initial===true&&selected>=0){
                    this.highlight(selected);
                }else{
                    this.highlight(0);
                }
            }

            //hidethesearchboxifthisisthefirstwegottheresultsandthereareenoughofthemforsearch

            if(initial===true){
                varmin=this.opts.minimumResultsForSearch;
                if(min>=0){
                    this.showSearch(countResults(data.results)>=min);
                }
            }
        },

        //single
        showSearch:function(showSearchInput){
            if(this.showSearchInput===showSearchInput)return;

            this.showSearchInput=showSearchInput;

            this.dropdown.find(".select2-search").toggleClass("select2-search-hidden",!showSearchInput);
            this.dropdown.find(".select2-search").toggleClass("select2-offscreen",!showSearchInput);
            //add"select2-with-searchbox"tothecontainerifsearchboxisshown
            $(this.dropdown,this.container).toggleClass("select2-with-searchbox",showSearchInput);
        },

        //single
        onSelect:function(data,options){

            if(!this.triggerSelect(data)){return;}

            varold=this.opts.element.val(),
                oldData=this.data();

            this.opts.element.val(this.id(data));
            this.updateSelection(data);

            this.opts.element.trigger({type:"select2-selected",val:this.id(data),choice:data});

            this.lastSearchTerm=this.search.val();
            this.close();

            if((!options||!options.noFocus)&&this.opts.shouldFocusInput(this)){
                this.focusser.focus();
            }

            if(!equal(old,this.id(data))){
                this.triggerChange({added:data,removed:oldData});
            }
        },

        //single
        updateSelection:function(data){

            varcontainer=this.selection.find(".select2-chosen"),formatted,cssClass;

            this.selection.data("select2-data",data);

            container.empty();
            if(data!==null){
                formatted=this.opts.formatSelection(data,container,this.opts.escapeMarkup);
            }
            if(formatted!==undefined){
                container.append(formatted);
            }
            cssClass=this.opts.formatSelectionCssClass(data,container);
            if(cssClass!==undefined){
                container.addClass(cssClass);
            }

            this.selection.removeClass("select2-default");

            if(this.opts.allowClear&&this.getPlaceholder()!==undefined){
                this.container.addClass("select2-allowclear");
            }
        },

        //single
        val:function(){
            varval,
                triggerChange=false,
                data=null,
                self=this,
                oldData=this.data();

            if(arguments.length===0){
                returnthis.opts.element.val();
            }

            val=arguments[0];

            if(arguments.length>1){
                triggerChange=arguments[1];

                if(this.opts.debug&&console&&console.warn){
                    console.warn(
                        'Select2:Thesecondoptionto`select2("val")`isnotsupportedinSelect24.0.0.'+
                        'The`change`eventwillalwaysbetriggeredin4.0.0.'
                    );
                }
            }

            if(this.select){
                if(this.opts.debug&&console&&console.warn){
                    console.warn(
                        'Select2:Settingthevalueona<select>using`select2("val")`isnolongersupportedin4.0.0.'+
                        'Youcanusethe`.val(newValue).trigger("change")`methodprovidedbyjQueryinstead.'
                    );
                }

                this.select
                    .val(val)
                    .find("option").filter(function(){returnthis.selected}).each2(function(i,elm){
                        data=self.optionToData(elm);
                        returnfalse;
                    });
                this.updateSelection(data);
                this.setPlaceholder();
                if(triggerChange){
                    this.triggerChange({added:data,removed:oldData});
                }
            }else{
                //valisanid.!valistruefor[undefined,null,'',0]-0islegal
                if(!val&&val!==0){
                    this.clear(triggerChange);
                    return;
                }
                if(this.opts.initSelection===undefined){
                    thrownewError("cannotcallval()ifinitSelection()isnotdefined");
                }
                this.opts.element.val(val);
                this.opts.initSelection(this.opts.element,function(data){
                    self.opts.element.val(!data?"":self.id(data));
                    self.updateSelection(data);
                    self.setPlaceholder();
                    if(triggerChange){
                        self.triggerChange({added:data,removed:oldData});
                    }
                });
            }
        },

        //single
        clearSearch:function(){
            this.search.val("");
            this.focusser.val("");
        },

        //single
        data:function(value){
            vardata,
                triggerChange=false;

            if(arguments.length===0){
                data=this.selection.data("select2-data");
                if(data==undefined)data=null;
                returndata;
            }else{
                if(this.opts.debug&&console&&console.warn){
                    console.warn(
                        'Select2:The`select2("data")`methodcannolongersetselectedvaluesin4.0.0,'+
                        'considerusingthe`.val()`methodinstead.'
                    );
                }

                if(arguments.length>1){
                    triggerChange=arguments[1];
                }
                if(!value){
                    this.clear(triggerChange);
                }else{
                    data=this.data();
                    this.opts.element.val(!value?"":this.id(value));
                    this.updateSelection(value);
                    if(triggerChange){
                        this.triggerChange({added:value,removed:data});
                    }
                }
            }
        }
    });

    MultiSelect2=clazz(AbstractSelect2,{

        //multi
        createContainer:function(){
            varcontainer=$(document.createElement("div")).attr({
                "class":"select2-containerselect2-container-multi"
            }).html([
                "<ulclass='select2-choices'>",
                " <liclass='select2-search-field'>",
                "   <labelfor=''class='select2-offscreen'></label>",
                "   <inputtype='text'autocomplete='off'autocorrect='off'autocapitalize='off'spellcheck='false'class='select2-input'>",
                " </li>",
                "</ul>",
                "<divclass='select2-dropselect2-drop-multiselect2-display-none'>",
                "  <ulclass='select2-results'>",
                "  </ul>",
                "</div>"].join(""));
            returncontainer;
        },

        //multi
        prepareOpts:function(){
            varopts=this.parent.prepareOpts.apply(this,arguments),
                self=this;

            //TODOvalidateplaceholderisastringifspecified
            if(opts.element.get(0).tagName.toLowerCase()==="select"){
                //installtheselectioninitializer
                opts.initSelection=function(element,callback){

                    vardata=[];

                    element.find("option").filter(function(){returnthis.selected&&!this.disabled}).each2(function(i,elm){
                        data.push(self.optionToData(elm));
                    });
                    callback(data);
                };
            }elseif("data"inopts){
                //installdefaultinitSelectionwhenappliedtohiddeninputanddataislocal
                opts.initSelection=opts.initSelection||function(element,callback){
                    varids=splitVal(element.val(),opts.separator,opts.transformVal);
                    //searchindatabyarrayofids,storingmatchingitemsinalist
                    varmatches=[];
                    opts.query({
                        matcher:function(term,text,el){
                            varis_match=$.grep(ids,function(id){
                                returnequal(id,opts.id(el));
                            }).length;
                            if(is_match){
                                matches.push(el);
                            }
                            returnis_match;
                        },
                        callback:!$.isFunction(callback)?$.noop:function(){
                            //reordermatchesbasedontheordertheyappearintheidsarraybecauserightnow
                            //theyareintheorderinwhichtheyappearindataarray
                            varordered=[];
                            for(vari=0;i<ids.length;i++){
                                varid=ids[i];
                                for(varj=0;j<matches.length;j++){
                                    varmatch=matches[j];
                                    if(equal(id,opts.id(match))){
                                        ordered.push(match);
                                        matches.splice(j,1);
                                        break;
                                    }
                                }
                            }
                            callback(ordered);
                        }
                    });
                };
            }

            returnopts;
        },

        //multi
        selectChoice:function(choice){

            varselected=this.container.find(".select2-search-choice-focus");
            if(selected.length&&choice&&choice[0]==selected[0]){

            }else{
                if(selected.length){
                    this.opts.element.trigger("choice-deselected",selected);
                }
                selected.removeClass("select2-search-choice-focus");
                if(choice&&choice.length){
                    this.close();
                    choice.addClass("select2-search-choice-focus");
                    this.opts.element.trigger("choice-selected",choice);
                }
            }
        },

        //multi
        destroy:function(){
            $("label[for='"+this.search.attr('id')+"']")
                .attr('for',this.opts.element.attr("id"));
            this.parent.destroy.apply(this,arguments);

            cleanupJQueryElements.call(this,
                "searchContainer",
                "selection"
            );
        },

        //multi
        initContainer:function(){

            varselector=".select2-choices",selection;

            this.searchContainer=this.container.find(".select2-search-field");
            this.selection=selection=this.container.find(selector);

            var_this=this;
            this.selection.on("click",".select2-container:not(.select2-container-disabled).select2-search-choice:not(.select2-locked)",function(e){
                _this.search[0].focus();
                _this.selectChoice($(this));
            });

            //rewritelabelsfromoriginalelementtofocusser
            this.search.attr("id","s2id_autogen"+nextUid());

            this.search.prev()
                .text($("label[for='"+this.opts.element.attr("id")+"']").text())
                .attr('for',this.search.attr('id'));
            this.opts.element.on('focus.select2',this.bind(function(){this.focus();}));

            this.search.on("inputpaste",this.bind(function(){
                if(this.search.attr('placeholder')&&this.search.val().length==0)return;
                if(!this.isInterfaceEnabled())return;
                if(!this.opened()){
                    this.open();
                }
            }));

            this.search.attr("tabindex",this.elementTabIndex);

            this.keydowns=0;
            this.search.on("keydown",this.bind(function(e){
                if(!this.isInterfaceEnabled())return;

                ++this.keydowns;
                varselected=selection.find(".select2-search-choice-focus");
                varprev=selected.prev(".select2-search-choice:not(.select2-locked)");
                varnext=selected.next(".select2-search-choice:not(.select2-locked)");
                varpos=getCursorInfo(this.search);

                if(selected.length&&
                    (e.which==KEY.LEFT||e.which==KEY.RIGHT||e.which==KEY.BACKSPACE||e.which==KEY.DELETE||e.which==KEY.ENTER)){
                    varselectedChoice=selected;
                    if(e.which==KEY.LEFT&&prev.length){
                        selectedChoice=prev;
                    }
                    elseif(e.which==KEY.RIGHT){
                        selectedChoice=next.length?next:null;
                    }
                    elseif(e.which===KEY.BACKSPACE){
                        if(this.unselect(selected.first())){
                            this.search.width(10);
                            selectedChoice=prev.length?prev:next;
                        }
                    }elseif(e.which==KEY.DELETE){
                        if(this.unselect(selected.first())){
                            this.search.width(10);
                            selectedChoice=next.length?next:null;
                        }
                    }elseif(e.which==KEY.ENTER){
                        selectedChoice=null;
                    }

                    this.selectChoice(selectedChoice);
                    killEvent(e);
                    if(!selectedChoice||!selectedChoice.length){
                        this.open();
                    }
                    return;
                }elseif(((e.which===KEY.BACKSPACE&&this.keydowns==1)
                    ||e.which==KEY.LEFT)&&(pos.offset==0&&!pos.length)){

                    this.selectChoice(selection.find(".select2-search-choice:not(.select2-locked)").last());
                    killEvent(e);
                    return;
                }else{
                    this.selectChoice(null);
                }

                if(this.opened()){
                    switch(e.which){
                    caseKEY.UP:
                    caseKEY.DOWN:
                        this.moveHighlight((e.which===KEY.UP)?-1:1);
                        killEvent(e);
                        return;
                    caseKEY.ENTER:
                        this.selectHighlighted();
                        killEvent(e);
                        return;
                    caseKEY.TAB:
                        this.selectHighlighted({noFocus:true});
                        this.close();
                        return;
                    caseKEY.ESC:
                        this.cancel(e);
                        killEvent(e);
                        return;
                    }
                }

                if(e.which===KEY.TAB||KEY.isControl(e)||KEY.isFunctionKey(e)
                 ||e.which===KEY.BACKSPACE||e.which===KEY.ESC){
                    return;
                }

                if(e.which===KEY.ENTER){
                    if(this.opts.openOnEnter===false){
                        return;
                    }elseif(e.altKey||e.ctrlKey||e.shiftKey||e.metaKey){
                        return;
                    }
                }

                this.open();

                if(e.which===KEY.PAGE_UP||e.which===KEY.PAGE_DOWN){
                    //preventthepagefromscrolling
                    killEvent(e);
                }

                if(e.which===KEY.ENTER){
                    //preventformfrombeingsubmitted
                    killEvent(e);
                }

            }));

            this.search.on("keyup",this.bind(function(e){
                this.keydowns=0;
                this.resizeSearch();
            })
            );

            this.search.on("blur",this.bind(function(e){
                this.container.removeClass("select2-container-active");
                this.search.removeClass("select2-focused");
                this.selectChoice(null);
                if(!this.opened())this.clearSearch();
                e.stopImmediatePropagation();
                this.opts.element.trigger($.Event("select2-blur"));
            }));

            this.container.on("click",selector,this.bind(function(e){
                if(!this.isInterfaceEnabled())return;
                if($(e.target).closest(".select2-search-choice").length>0){
                    //clickedinsideaselect2searchchoice,donotopen
                    return;
                }
                this.selectChoice(null);
                this.clearPlaceholder();
                if(!this.container.hasClass("select2-container-active")){
                    this.opts.element.trigger($.Event("select2-focus"));
                }
                this.open();
                this.focusSearch();
                e.preventDefault();
            }));

            this.container.on("focus",selector,this.bind(function(){
                if(!this.isInterfaceEnabled())return;
                if(!this.container.hasClass("select2-container-active")){
                    this.opts.element.trigger($.Event("select2-focus"));
                }
                this.container.addClass("select2-container-active");
                this.dropdown.addClass("select2-drop-active");
                this.clearPlaceholder();
            }));

            this.initContainerWidth();
            this.opts.element.hide();

            //settheplaceholderifnecessary
            this.clearSearch();
        },

        //multi
        enableInterface:function(){
            if(this.parent.enableInterface.apply(this,arguments)){
                this.search.prop("disabled",!this.isInterfaceEnabled());
            }
        },

        //multi
        initSelection:function(){
            vardata;
            if(this.opts.element.val()===""&&this.opts.element.text()===""){
                this.updateSelection([]);
                this.close();
                //settheplaceholderifnecessary
                this.clearSearch();
            }
            if(this.select||this.opts.element.val()!==""){
                varself=this;
                this.opts.initSelection.call(null,this.opts.element,function(data){
                    if(data!==undefined&&data!==null){
                        self.updateSelection(data);
                        self.close();
                        //settheplaceholderifnecessary
                        self.clearSearch();
                    }
                });
            }
        },

        //multi
        clearSearch:function(){
            varplaceholder=this.getPlaceholder(),
                maxWidth=this.getMaxSearchWidth();

            if(placeholder!==undefined &&this.getVal().length===0&&this.search.hasClass("select2-focused")===false){
                this.search.val(placeholder).addClass("select2-default");
                //stretchthesearchboxtofullwidthofthecontainersoasmuchoftheplaceholderisvisibleaspossible
                //wecouldcallthis.resizeSearch(),butwedonotbecausethatrequiresasizerandwedonotwanttocreateonesoearlybecauseofafirefoxbug,see#944
                this.search.width(maxWidth>0?maxWidth:this.container.css("width"));
            }else{
                this.search.val("").width(10);
            }
        },

        //multi
        clearPlaceholder:function(){
            if(this.search.hasClass("select2-default")){
                this.search.val("").removeClass("select2-default");
            }
        },

        //multi
        opening:function(){
            this.clearPlaceholder();//shouldbedonebeforesupersoplaceholderisnotusedtosearch
            this.resizeSearch();

            this.parent.opening.apply(this,arguments);

            this.focusSearch();

            this.prefillNextSearchTerm();
            this.updateResults(true);

            if(this.opts.shouldFocusInput(this)){
                this.search.focus();
            }
            this.opts.element.trigger($.Event("select2-open"));
        },

        //multi
        close:function(){
            if(!this.opened())return;
            this.parent.close.apply(this,arguments);
        },

        //multi
        focus:function(){
            this.close();
            this.search.focus();
        },

        //multi
        isFocused:function(){
            returnthis.search.hasClass("select2-focused");
        },

        //multi
        updateSelection:function(data){
            varids={},filtered=[],self=this;

            //filteroutduplicates
            $(data).each(function(){
                if(!(self.id(this)inids)){
                    ids[self.id(this)]=0;
                    filtered.push(this);
                }
            });

            this.selection.find(".select2-search-choice").remove();
            this.addSelectedChoice(filtered);
            self.postprocessResults();
        },

        //multi
        tokenize:function(){
            varinput=this.search.val();
            input=this.opts.tokenizer.call(this,input,this.data(),this.bind(this.onSelect),this.opts);
            if(input!=null&&input!=undefined){
                this.search.val(input);
                if(input.length>0){
                    this.open();
                }
            }

        },

        //multi
        onSelect:function(data,options){

            if(!this.triggerSelect(data)||data.text===""){return;}

            this.addSelectedChoice(data);

            this.opts.element.trigger({type:"selected",val:this.id(data),choice:data});

            //keeptrackofthesearch'svaluebeforeitgetscleared
            this.lastSearchTerm=this.search.val();

            this.clearSearch();
            this.updateResults();

            if(this.select||!this.opts.closeOnSelect)this.postprocessResults(data,false,this.opts.closeOnSelect===true);

            if(this.opts.closeOnSelect){
                this.close();
                this.search.width(10);
            }else{
                if(this.countSelectableResults()>0){
                    this.search.width(10);
                    this.resizeSearch();
                    if(this.getMaximumSelectionSize()>0&&this.val().length>=this.getMaximumSelectionSize()){
                        //ifwereachedmaxselectionsizerepainttheresultssochoices
                        //arereplacedwiththemaxselectionreachedmessage
                        this.updateResults(true);
                    }else{
                        //initializessearch'svaluewithnextSearchTermandupdatesearchresult
                        if(this.prefillNextSearchTerm()){
                            this.updateResults();
                        }
                    }
                    this.positionDropdown();
                }else{
                    //ifnothinglefttoselectclose
                    this.close();
                    this.search.width(10);
                }
            }

            //sinceitsnotpossibletoselectanelementthathasalreadybeen
            //addedwedonotneedtocheckifthisisanewelementbeforefiringchange
            this.triggerChange({added:data});

            if(!options||!options.noFocus)
                this.focusSearch();
        },

        //multi
        cancel:function(){
            this.close();
            this.focusSearch();
        },

        addSelectedChoice:function(data){
            varval=this.getVal(),self=this;
            $(data).each(function(){
                val.push(self.createChoice(this));
            });
            this.setVal(val);
        },

        createChoice:function(data){
            varenableChoice=!data.locked,
                enabledItem=$(
                    "<liclass='select2-search-choice'>"+
                    "   <div></div>"+
                    "   <ahref='#'class='select2-search-choice-close'tabindex='-1'></a>"+
                    "</li>"),
                disabledItem=$(
                    "<liclass='select2-search-choiceselect2-locked'>"+
                    "<div></div>"+
                    "</li>");
            varchoice=enableChoice?enabledItem:disabledItem,
                id=this.id(data),
                formatted,
                cssClass;

            formatted=this.opts.formatSelection(data,choice.find("div"),this.opts.escapeMarkup);
            if(formatted!=undefined){
                choice.find("div").replaceWith($("<div></div>").html(formatted));
            }
            cssClass=this.opts.formatSelectionCssClass(data,choice.find("div"));
            if(cssClass!=undefined){
                choice.addClass(cssClass);
            }

            if(enableChoice){
              choice.find(".select2-search-choice-close")
                  .on("mousedown",killEvent)
                  .on("clickdblclick",this.bind(function(e){
                  if(!this.isInterfaceEnabled())return;

                  this.unselect($(e.target));
                  this.selection.find(".select2-search-choice-focus").removeClass("select2-search-choice-focus");
                  killEvent(e);
                  this.close();
                  this.focusSearch();
              })).on("focus",this.bind(function(){
                  if(!this.isInterfaceEnabled())return;
                  this.container.addClass("select2-container-active");
                  this.dropdown.addClass("select2-drop-active");
              }));
            }

            choice.data("select2-data",data);
            choice.insertBefore(this.searchContainer);

            returnid;
        },

        //multi
        unselect:function(selected){
            varval=this.getVal(),
                data,
                index;
            selected=selected.closest(".select2-search-choice");

            if(selected.length===0){
                throw"Invalidargument:"+selected+".Mustbe.select2-search-choice";
            }

            data=selected.data("select2-data");

            if(!data){
                //preventaraceconditionwhenthe'x'isclickedreallyfastrepeatedlytheeventcanbequeued
                //andinvokedonanelementalreadyremoved
                return;
            }

            varevt=$.Event("select2-removing");
            evt.val=this.id(data);
            evt.choice=data;
            this.opts.element.trigger(evt);

            if(evt.isDefaultPrevented()){
                returnfalse;
            }

            while((index=indexOf(this.id(data),val))>=0){
                val.splice(index,1);
                this.setVal(val);
                if(this.select)this.postprocessResults();
            }

            selected.remove();

            this.opts.element.trigger({type:"select2-removed",val:this.id(data),choice:data});
            this.triggerChange({removed:data});

            returntrue;
        },

        //multi
        postprocessResults:function(data,initial,noHighlightUpdate){
            varval=this.getVal(),
                choices=this.results.find(".select2-result"),
                compound=this.results.find(".select2-result-with-children"),
                self=this;

            choices.each2(function(i,choice){
                varid=self.id(choice.data("select2-data"));
                if(indexOf(id,val)>=0){
                    choice.addClass("select2-selected");
                    //markallchildrenoftheselectedparentasselected
                    choice.find(".select2-result-selectable").addClass("select2-selected");
                }
            });

            compound.each2(function(i,choice){
                //hideanoptgroupifitdoesn'thaveanyselectablechildren
                if(!choice.is('.select2-result-selectable')
                    &&choice.find(".select2-result-selectable:not(.select2-selected)").length===0){
                    choice.addClass("select2-selected");
                }
            });

            if(this.highlight()==-1&&noHighlightUpdate!==false&&this.opts.closeOnSelect===true){
                self.highlight(0);
            }

            //IfallresultsarechosenrenderformatNoMatches
            if(!this.opts.createSearchChoice&&!choices.filter('.select2-result:not(.select2-selected)').length>0){
                if(!data||data&&!data.more&&this.results.find(".select2-no-results").length===0){
                    if(checkFormatter(self.opts.formatNoMatches,"formatNoMatches")){
                        this.results.append("<liclass='select2-no-results'>"+evaluate(self.opts.formatNoMatches,self.opts.element,self.search.val())+"</li>");
                    }
                }
            }

        },

        //multi
        getMaxSearchWidth:function(){
            returnthis.selection.width()-getSideBorderPadding(this.search);
        },

        //multi
        resizeSearch:function(){
            varminimumWidth,left,maxWidth,containerLeft,searchWidth,
                sideBorderPadding=getSideBorderPadding(this.search);

            minimumWidth=measureTextWidth(this.search)+10;

            left=this.search.offset().left;

            maxWidth=this.selection.width();
            containerLeft=this.selection.offset().left;

            searchWidth=maxWidth-(left-containerLeft)-sideBorderPadding;

            if(searchWidth<minimumWidth){
                searchWidth=maxWidth-sideBorderPadding;
            }

            if(searchWidth<40){
                searchWidth=maxWidth-sideBorderPadding;
            }

            if(searchWidth<=0){
              searchWidth=minimumWidth;
            }

            this.search.width(Math.floor(searchWidth));
        },

        //multi
        getVal:function(){
            varval;
            if(this.select){
                val=this.select.val();
                returnval===null?[]:val;
            }else{
                val=this.opts.element.val();
                returnsplitVal(val,this.opts.separator,this.opts.transformVal);
            }
        },

        //multi
        setVal:function(val){
            if(this.select){
                this.select.val(val);
            }else{
                varunique=[],valMap={};
                //filteroutduplicates
                $(val).each(function(){
                    if(!(thisinvalMap)){
                        unique.push(this);
                        valMap[this]=0;
                    }
                });
                this.opts.element.val(unique.length===0?"":unique.join(this.opts.separator));
            }
        },

        //multi
        buildChangeDetails:function(old,current){
            varcurrent=current.slice(0),
                old=old.slice(0);

            //removeintersectionfromeacharray
            for(vari=0;i<current.length;i++){
                for(varj=0;j<old.length;j++){
                    if(equal(this.opts.id(current[i]),this.opts.id(old[j]))){
                        current.splice(i,1);
                        i--;
                        old.splice(j,1);
                        break;
                    }
                }
            }

            return{added:current,removed:old};
        },


        //multi
        val:function(val,triggerChange){
            varoldData,self=this;

            if(arguments.length===0){
                returnthis.getVal();
            }

            oldData=this.data();
            if(!oldData.length)oldData=[];

            //valisanid.!valistruefor[undefined,null,'',0]-0islegal
            if(!val&&val!==0){
                this.opts.element.val("");
                this.updateSelection([]);
                this.clearSearch();
                if(triggerChange){
                    this.triggerChange({added:this.data(),removed:oldData});
                }
                return;
            }

            //valisalistofids
            this.setVal(val);

            if(this.select){
                this.opts.initSelection(this.select,this.bind(this.updateSelection));
                if(triggerChange){
                    this.triggerChange(this.buildChangeDetails(oldData,this.data()));
                }
            }else{
                if(this.opts.initSelection===undefined){
                    thrownewError("val()cannotbecalledifinitSelection()isnotdefined");
                }

                this.opts.initSelection(this.opts.element,function(data){
                    varids=$.map(data,self.id);
                    self.setVal(ids);
                    self.updateSelection(data);
                    self.clearSearch();
                    if(triggerChange){
                        self.triggerChange(self.buildChangeDetails(oldData,self.data()));
                    }
                });
            }
            this.clearSearch();
        },

        //multi
        onSortStart:function(){
            if(this.select){
                thrownewError("Sortingofelementsisnotsupportedwhenattachedto<select>.Attachto<inputtype='hidden'/>instead.");
            }

            //collapsesearchfieldinto0widthsoitscontainercanbecollapsedaswell
            this.search.width(0);
            //hidethecontainer
            this.searchContainer.hide();
        },

        //multi
        onSortEnd:function(){

            varval=[],self=this;

            //showsearchandmoveittotheendofthelist
            this.searchContainer.show();
            //makesurethesearchcontaineristhelastiteminthelist
            this.searchContainer.appendTo(this.searchContainer.parent());
            //sincewecollapsedthewidthindragStarted,weresizeithere
            this.resizeSearch();

            //updateselection
            this.selection.find(".select2-search-choice").each(function(){
                val.push(self.opts.id($(this).data("select2-data")));
            });
            this.setVal(val);
            this.triggerChange();
        },

        //multi
        data:function(values,triggerChange){
            varself=this,ids,old;
            if(arguments.length===0){
                 returnthis.selection
                     .children(".select2-search-choice")
                     .map(function(){return$(this).data("select2-data");})
                     .get();
            }else{
                old=this.data();
                if(!values){values=[];}
                ids=$.map(values,function(e){returnself.opts.id(e);});
                this.setVal(ids);
                this.updateSelection(values);
                this.clearSearch();
                if(triggerChange){
                    this.triggerChange(this.buildChangeDetails(old,this.data()));
                }
            }
        }
    });

    $.fn.select2=function(){

        varargs=Array.prototype.slice.call(arguments,0),
            opts,
            select2,
            method,value,multiple,
            allowedMethods=["val","destroy","opened","open","close","focus","isFocused","container","dropdown","onSortStart","onSortEnd","enable","disable","readonly","positionDropdown","data","search"],
            valueMethods=["opened","isFocused","container","dropdown"],
            propertyMethods=["val","data"],
            methodsMap={search:"externalSearch"};

        this.each(function(){
            if(args.length===0||typeof(args[0])==="object"){
                opts=args.length===0?{}:$.extend({},args[0]);
                opts.element=$(this);

                if(opts.element.get(0).tagName.toLowerCase()==="select"){
                    multiple=opts.element.prop("multiple");
                }else{
                    multiple=opts.multiple||false;
                    if("tags"inopts){opts.multiple=multiple=true;}
                }

                select2=multiple?newwindow.Select2["class"].multi():newwindow.Select2["class"].single();
                select2.init(opts);
            }elseif(typeof(args[0])==="string"){

                if(indexOf(args[0],allowedMethods)<0){
                    throw"Unknownmethod:"+args[0];
                }

                value=undefined;
                select2=$(this).data("select2");
                if(select2===undefined)return;

                method=args[0];

                if(method==="container"){
                    value=select2.container;
                }elseif(method==="dropdown"){
                    value=select2.dropdown;
                }else{
                    if(methodsMap[method])method=methodsMap[method];

                    value=select2[method].apply(select2,args.slice(1));
                }
                if(indexOf(args[0],valueMethods)>=0
                    ||(indexOf(args[0],propertyMethods)>=0&&args.length==1)){
                    returnfalse;//aborttheiteration,readytoreturnfirstmatchedvalue
                }
            }else{
                throw"Invalidargumentstoselect2plugin:"+args;
            }
        });
        return(value===undefined)?this:value;
    };

    //plugindefaults,accessibletousers
    $.fn.select2.defaults={
        debug:false,
        width:"copy",
        loadMorePadding:0,
        closeOnSelect:true,
        openOnEnter:true,
        containerCss:{},
        dropdownCss:{},
        containerCssClass:"",
        dropdownCssClass:"",
        formatResult:function(result,container,query,escapeMarkup){
            varmarkup=[];
            markMatch(this.text(result),query.term,markup,escapeMarkup);
            returnmarkup.join("");
        },
        transformVal:function(val){
            return$.trim(val);
        },
        formatSelection:function(data,container,escapeMarkup){
            returndata?escapeMarkup(this.text(data)):undefined;
        },
        sortResults:function(results,container,query){
            returnresults;
        },
        formatResultCssClass:function(data){returndata.css;},
        formatSelectionCssClass:function(data,container){returnundefined;},
        minimumResultsForSearch:0,
        minimumInputLength:0,
        maximumInputLength:null,
        maximumSelectionSize:0,
        id:function(e){returne==undefined?null:e.id;},
        text:function(e){
          if(e&&this.data&&this.data.text){
            if($.isFunction(this.data.text)){
              returnthis.data.text(e);
            }else{
              returne[this.data.text];
            }
          }else{
            returne.text;
          }
        },
        matcher:function(term,text){
            returnstripDiacritics(''+text).toUpperCase().indexOf(stripDiacritics(''+term).toUpperCase())>=0;
        },
        separator:",",
        tokenSeparators:[],
        tokenizer:defaultTokenizer,
        escapeMarkup:defaultEscapeMarkup,
        blurOnChange:false,
        selectOnBlur:false,
        adaptContainerCssClass:function(c){returnc;},
        adaptDropdownCssClass:function(c){returnnull;},
        nextSearchTerm:function(selectedObject,currentSearchTerm){returnundefined;},
        searchInputPlaceholder:'',
        createSearchChoicePosition:'top',
        shouldFocusInput:function(instance){
            //Attempttodetecttouchdevices
            varsupportsTouchEvents=(('ontouchstart'inwindow)||
                                       (navigator.msMaxTouchPoints>0));

            //Onlydeviceswhichsupporttoucheventsshouldbespecialcased
            if(!supportsTouchEvents){
                returntrue;
            }

            //Neverfocustheinputifsearchisdisabled
            if(instance.opts.minimumResultsForSearch<0){
                returnfalse;
            }

            returntrue;
        }
    };

    $.fn.select2.locales=[];

    $.fn.select2.locales['en']={
         formatMatches:function(matches){if(matches===1){return"Oneresultisavailable,pressentertoselectit.";}returnmatches+"resultsareavailable,useupanddownarrowkeystonavigate.";},
         formatNoMatches:function(){return"Nomatchesfound";},
         formatAjaxError:function(jqXHR,textStatus,errorThrown){return"Loadingfailed";},
         formatInputTooShort:function(input,min){varn=min-input.length;return"Pleaseenter"+n+"ormorecharacter"+(n==1?"":"s");},
         formatInputTooLong:function(input,max){varn=input.length-max;return"Pleasedelete"+n+"character"+(n==1?"":"s");},
         formatSelectionTooBig:function(limit){return"Youcanonlyselect"+limit+"item"+(limit==1?"":"s");},
         formatLoadMore:function(pageNumber){return"Loadingmoreresults…";},
         formatSearching:function(){return"Searching…";}
    };

    $.extend($.fn.select2.defaults,$.fn.select2.locales['en']);

    $.fn.select2.ajaxDefaults={
        transport:$.ajax,
        params:{
            type:"GET",
            cache:false,
            dataType:"json"
        }
    };

    //exports
    window.Select2={
        query:{
            ajax:ajax,
            local:local,
            tags:tags
        },util:{
            debounce:debounce,
            markMatch:markMatch,
            escapeMarkup:defaultEscapeMarkup,
            stripDiacritics:stripDiacritics
        },"class":{
            "abstract":AbstractSelect2,
            "single":SingleSelect2,
            "multi":MultiSelect2
        }
    };

}(jQuery));
