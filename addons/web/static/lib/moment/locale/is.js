//!moment.jslocaleconfiguration
//!locale:Icelandic[is]
//!author:HinrikÖrnSigurðsson:https://github.com/hinrik

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


functionplural(n){
    if(n%100===11){
        returntrue;
    }elseif(n%10===1){
        returnfalse;
    }
    returntrue;
}
functiontranslate(number,withoutSuffix,key,isFuture){
    varresult=number+'';
    switch(key){
        case's':
            returnwithoutSuffix||isFuture?'nokkrarsekúndur':'nokkrumsekúndum';
        case'm':
            returnwithoutSuffix?'mínúta':'mínútu';
        case'mm':
            if(plural(number)){
                returnresult+(withoutSuffix||isFuture?'mínútur':'mínútum');
            }elseif(withoutSuffix){
                returnresult+'mínúta';
            }
            returnresult+'mínútu';
        case'hh':
            if(plural(number)){
                returnresult+(withoutSuffix||isFuture?'klukkustundir':'klukkustundum');
            }
            returnresult+'klukkustund';
        case'd':
            if(withoutSuffix){
                return'dagur';
            }
            returnisFuture?'dag':'degi';
        case'dd':
            if(plural(number)){
                if(withoutSuffix){
                    returnresult+'dagar';
                }
                returnresult+(isFuture?'daga':'dögum');
            }elseif(withoutSuffix){
                returnresult+'dagur';
            }
            returnresult+(isFuture?'dag':'degi');
        case'M':
            if(withoutSuffix){
                return'mánuður';
            }
            returnisFuture?'mánuð':'mánuði';
        case'MM':
            if(plural(number)){
                if(withoutSuffix){
                    returnresult+'mánuðir';
                }
                returnresult+(isFuture?'mánuði':'mánuðum');
            }elseif(withoutSuffix){
                returnresult+'mánuður';
            }
            returnresult+(isFuture?'mánuð':'mánuði');
        case'y':
            returnwithoutSuffix||isFuture?'ár':'ári';
        case'yy':
            if(plural(number)){
                returnresult+(withoutSuffix||isFuture?'ár':'árum');
            }
            returnresult+(withoutSuffix||isFuture?'ár':'ári');
    }
}

varis=moment.defineLocale('is',{
    months:'janúar_febrúar_mars_apríl_maí_júní_júlí_ágúst_september_október_nóvember_desember'.split('_'),
    monthsShort:'jan_feb_mar_apr_maí_jún_júl_ágú_sep_okt_nóv_des'.split('_'),
    weekdays:'sunnudagur_mánudagur_þriðjudagur_miðvikudagur_fimmtudagur_föstudagur_laugardagur'.split('_'),
    weekdaysShort:'sun_mán_þri_mið_fim_fös_lau'.split('_'),
    weekdaysMin:'Su_Má_Þr_Mi_Fi_Fö_La'.split('_'),
    longDateFormat:{
        LT:'H:mm',
        LTS:'H:mm:ss',
        L:'DD.MM.YYYY',
        LL:'D.MMMMYYYY',
        LLL:'D.MMMMYYYY[kl.]H:mm',
        LLLL:'dddd,D.MMMMYYYY[kl.]H:mm'
    },
    calendar:{
        sameDay:'[ídagkl.]LT',
        nextDay:'[ámorgunkl.]LT',
        nextWeek:'dddd[kl.]LT',
        lastDay:'[ígærkl.]LT',
        lastWeek:'[síðasta]dddd[kl.]LT',
        sameElse:'L'
    },
    relativeTime:{
        future:'eftir%s',
        past:'fyrir%ssíðan',
        s:translate,
        m:translate,
        mm:translate,
        h:'klukkustund',
        hh:translate,
        d:translate,
        dd:translate,
        M:translate,
        MM:translate,
        y:translate,
        yy:translate
    },
    ordinalParse:/\d{1,2}\./,
    ordinal:'%d.',
    week:{
        dow:1,//Mondayisthefirstdayoftheweek.
        doy:4 //TheweekthatcontainsJan4thisthefirstweekoftheyear.
    }
});

returnis;

})));
