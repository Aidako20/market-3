//!moment.jslocaleconfiguration
//!locale:Bosnian[bs]
//!author:NedimCholich:https://github.com/frontyard
//!basedon(hr)translationbyBojanMarković

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


functiontranslate(number,withoutSuffix,key){
    varresult=number+'';
    switch(key){
        case'm':
            returnwithoutSuffix?'jednaminuta':'jedneminute';
        case'mm':
            if(number===1){
                result+='minuta';
            }elseif(number===2||number===3||number===4){
                result+='minute';
            }else{
                result+='minuta';
            }
            returnresult;
        case'h':
            returnwithoutSuffix?'jedansat':'jednogsata';
        case'hh':
            if(number===1){
                result+='sat';
            }elseif(number===2||number===3||number===4){
                result+='sata';
            }else{
                result+='sati';
            }
            returnresult;
        case'dd':
            if(number===1){
                result+='dan';
            }else{
                result+='dana';
            }
            returnresult;
        case'MM':
            if(number===1){
                result+='mjesec';
            }elseif(number===2||number===3||number===4){
                result+='mjeseca';
            }else{
                result+='mjeseci';
            }
            returnresult;
        case'yy':
            if(number===1){
                result+='godina';
            }elseif(number===2||number===3||number===4){
                result+='godine';
            }else{
                result+='godina';
            }
            returnresult;
    }
}

varbs=moment.defineLocale('bs',{
    months:'januar_februar_mart_april_maj_juni_juli_august_septembar_oktobar_novembar_decembar'.split('_'),
    monthsShort:'jan._feb._mar._apr._maj._jun._jul._aug._sep._okt._nov._dec.'.split('_'),
    monthsParseExact:true,
    weekdays:'nedjelja_ponedjeljak_utorak_srijeda_četvrtak_petak_subota'.split('_'),
    weekdaysShort:'ned._pon._uto._sri._čet._pet._sub.'.split('_'),
    weekdaysMin:'ne_po_ut_sr_če_pe_su'.split('_'),
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
        sameDay :'[danasu]LT',
        nextDay :'[sutrau]LT',
        nextWeek:function(){
            switch(this.day()){
                case0:
                    return'[u][nedjelju][u]LT';
                case3:
                    return'[u][srijedu][u]LT';
                case6:
                    return'[u][subotu][u]LT';
                case1:
                case2:
                case4:
                case5:
                    return'[u]dddd[u]LT';
            }
        },
        lastDay :'[jučeru]LT',
        lastWeek:function(){
            switch(this.day()){
                case0:
                case3:
                    return'[prošlu]dddd[u]LT';
                case6:
                    return'[prošle][subote][u]LT';
                case1:
                case2:
                case4:
                case5:
                    return'[prošli]dddd[u]LT';
            }
        },
        sameElse:'L'
    },
    relativeTime:{
        future:'za%s',
        past  :'prije%s',
        s     :'parsekundi',
        m     :translate,
        mm    :translate,
        h     :translate,
        hh    :translate,
        d     :'dan',
        dd    :translate,
        M     :'mjesec',
        MM    :translate,
        y     :'godinu',
        yy    :translate
    },
    ordinalParse:/\d{1,2}\./,
    ordinal:'%d.',
    week:{
        dow:1,//Mondayisthefirstdayoftheweek.
        doy:7 //TheweekthatcontainsJan1stisthefirstweekoftheyear.
    }
});

returnbs;

})));
