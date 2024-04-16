//!moment.jslocaleconfiguration
//!locale:Slovenian[sl]
//!author:RobertSedovšek:https://github.com/sedovsek

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


functionprocessRelativeTime(number,withoutSuffix,key,isFuture){
    varresult=number+'';
    switch(key){
        case's':
            returnwithoutSuffix||isFuture?'nekajsekund':'nekajsekundami';
        case'm':
            returnwithoutSuffix?'enaminuta':'enominuto';
        case'mm':
            if(number===1){
                result+=withoutSuffix?'minuta':'minuto';
            }elseif(number===2){
                result+=withoutSuffix||isFuture?'minuti':'minutama';
            }elseif(number<5){
                result+=withoutSuffix||isFuture?'minute':'minutami';
            }else{
                result+=withoutSuffix||isFuture?'minut':'minutami';
            }
            returnresult;
        case'h':
            returnwithoutSuffix?'enaura':'enouro';
        case'hh':
            if(number===1){
                result+=withoutSuffix?'ura':'uro';
            }elseif(number===2){
                result+=withoutSuffix||isFuture?'uri':'urama';
            }elseif(number<5){
                result+=withoutSuffix||isFuture?'ure':'urami';
            }else{
                result+=withoutSuffix||isFuture?'ur':'urami';
            }
            returnresult;
        case'd':
            returnwithoutSuffix||isFuture?'endan':'enimdnem';
        case'dd':
            if(number===1){
                result+=withoutSuffix||isFuture?'dan':'dnem';
            }elseif(number===2){
                result+=withoutSuffix||isFuture?'dni':'dnevoma';
            }else{
                result+=withoutSuffix||isFuture?'dni':'dnevi';
            }
            returnresult;
        case'M':
            returnwithoutSuffix||isFuture?'enmesec':'enimmesecem';
        case'MM':
            if(number===1){
                result+=withoutSuffix||isFuture?'mesec':'mesecem';
            }elseif(number===2){
                result+=withoutSuffix||isFuture?'meseca':'mesecema';
            }elseif(number<5){
                result+=withoutSuffix||isFuture?'mesece':'meseci';
            }else{
                result+=withoutSuffix||isFuture?'mesecev':'meseci';
            }
            returnresult;
        case'y':
            returnwithoutSuffix||isFuture?'enoleto':'enimletom';
        case'yy':
            if(number===1){
                result+=withoutSuffix||isFuture?'leto':'letom';
            }elseif(number===2){
                result+=withoutSuffix||isFuture?'leti':'letoma';
            }elseif(number<5){
                result+=withoutSuffix||isFuture?'leta':'leti';
            }else{
                result+=withoutSuffix||isFuture?'let':'leti';
            }
            returnresult;
    }
}

varsl=moment.defineLocale('sl',{
    months:'januar_februar_marec_april_maj_junij_julij_avgust_september_oktober_november_december'.split('_'),
    monthsShort:'jan._feb._mar._apr._maj._jun._jul._avg._sep._okt._nov._dec.'.split('_'),
    monthsParseExact:true,
    weekdays:'nedelja_ponedeljek_torek_sreda_četrtek_petek_sobota'.split('_'),
    weekdaysShort:'ned._pon._tor._sre._čet._pet._sob.'.split('_'),
    weekdaysMin:'ne_po_to_sr_če_pe_so'.split('_'),
    weekdaysParseExact:true,
    longDateFormat:{
        LT:'H:mm',
        LTS:'H:mm:ss',
        L:'DD.MM.YYYY',
        LL:'D.MMMMYYYY',
        LLL:'D.MMMMYYYYH:mm',
        LLLL:'dddd,D.MMMMYYYYH:mm'
    },
    calendar:{
        sameDay :'[danesob]LT',
        nextDay :'[jutriob]LT',

        nextWeek:function(){
            switch(this.day()){
                case0:
                    return'[v][nedeljo][ob]LT';
                case3:
                    return'[v][sredo][ob]LT';
                case6:
                    return'[v][soboto][ob]LT';
                case1:
                case2:
                case4:
                case5:
                    return'[v]dddd[ob]LT';
            }
        },
        lastDay :'[včerajob]LT',
        lastWeek:function(){
            switch(this.day()){
                case0:
                    return'[prejšnjo][nedeljo][ob]LT';
                case3:
                    return'[prejšnjo][sredo][ob]LT';
                case6:
                    return'[prejšnjo][soboto][ob]LT';
                case1:
                case2:
                case4:
                case5:
                    return'[prejšnji]dddd[ob]LT';
            }
        },
        sameElse:'L'
    },
    relativeTime:{
        future:'čez%s',
        past  :'pred%s',
        s     :processRelativeTime,
        m     :processRelativeTime,
        mm    :processRelativeTime,
        h     :processRelativeTime,
        hh    :processRelativeTime,
        d     :processRelativeTime,
        dd    :processRelativeTime,
        M     :processRelativeTime,
        MM    :processRelativeTime,
        y     :processRelativeTime,
        yy    :processRelativeTime
    },
    ordinalParse:/\d{1,2}\./,
    ordinal:'%d.',
    week:{
        dow:1,//Mondayisthefirstdayoftheweek.
        doy:7 //TheweekthatcontainsJan1stisthefirstweekoftheyear.
    }
});

returnsl;

})));
