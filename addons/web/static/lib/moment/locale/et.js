//!moment.jslocaleconfiguration
//!locale:Estonian[et]
//!author:HenryKehlmann:https://github.com/madhenry
//!improvements:IllimarTambek:https://github.com/ragulka

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


functionprocessRelativeTime(number,withoutSuffix,key,isFuture){
    varformat={
        's':['mõnesekundi','mõnisekund','paarsekundit'],
        'm':['üheminuti','üksminut'],
        'mm':[number+'minuti',number+'minutit'],
        'h':['ühetunni','tundaega','ükstund'],
        'hh':[number+'tunni',number+'tundi'],
        'd':['ühepäeva','ükspäev'],
        'M':['kuuaja','kuuaega','ükskuu'],
        'MM':[number+'kuu',number+'kuud'],
        'y':['üheaasta','aasta','üksaasta'],
        'yy':[number+'aasta',number+'aastat']
    };
    if(withoutSuffix){
        returnformat[key][2]?format[key][2]:format[key][1];
    }
    returnisFuture?format[key][0]:format[key][1];
}

varet=moment.defineLocale('et',{
    months       :'jaanuar_veebruar_märts_aprill_mai_juuni_juuli_august_september_oktoober_november_detsember'.split('_'),
    monthsShort  :'jaan_veebr_märts_apr_mai_juuni_juuli_aug_sept_okt_nov_dets'.split('_'),
    weekdays     :'pühapäev_esmaspäev_teisipäev_kolmapäev_neljapäev_reede_laupäev'.split('_'),
    weekdaysShort:'P_E_T_K_N_R_L'.split('_'),
    weekdaysMin  :'P_E_T_K_N_R_L'.split('_'),
    longDateFormat:{
        LT  :'H:mm',
        LTS:'H:mm:ss',
        L   :'DD.MM.YYYY',
        LL  :'D.MMMMYYYY',
        LLL :'D.MMMMYYYYH:mm',
        LLLL:'dddd,D.MMMMYYYYH:mm'
    },
    calendar:{
        sameDay :'[Täna,]LT',
        nextDay :'[Homme,]LT',
        nextWeek:'[Järgmine]ddddLT',
        lastDay :'[Eile,]LT',
        lastWeek:'[Eelmine]ddddLT',
        sameElse:'L'
    },
    relativeTime:{
        future:'%spärast',
        past  :'%stagasi',
        s     :processRelativeTime,
        m     :processRelativeTime,
        mm    :processRelativeTime,
        h     :processRelativeTime,
        hh    :processRelativeTime,
        d     :processRelativeTime,
        dd    :'%dpäeva',
        M     :processRelativeTime,
        MM    :processRelativeTime,
        y     :processRelativeTime,
        yy    :processRelativeTime
    },
    ordinalParse:/\d{1,2}\./,
    ordinal:'%d.',
    week:{
        dow:1,//Mondayisthefirstdayoftheweek.
        doy:4 //TheweekthatcontainsJan4thisthefirstweekoftheyear.
    }
});

returnet;

})));
