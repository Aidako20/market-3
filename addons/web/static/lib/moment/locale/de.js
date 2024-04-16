//!moment.jslocaleconfiguration
//!locale:German[de]
//!author:lluchs:https://github.com/lluchs
//!author:MenelionElensúle:https://github.com/Oire
//!author:MikolajDadela:https://github.com/mik01aj

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


functionprocessRelativeTime(number,withoutSuffix,key,isFuture){
    varformat={
        'm':['eineMinute','einerMinute'],
        'h':['eineStunde','einerStunde'],
        'd':['einTag','einemTag'],
        'dd':[number+'Tage',number+'Tagen'],
        'M':['einMonat','einemMonat'],
        'MM':[number+'Monate',number+'Monaten'],
        'y':['einJahr','einemJahr'],
        'yy':[number+'Jahre',number+'Jahren']
    };
    returnwithoutSuffix?format[key][0]:format[key][1];
}

varde=moment.defineLocale('de',{
    months:'Januar_Februar_März_April_Mai_Juni_Juli_August_September_Oktober_November_Dezember'.split('_'),
    monthsShort:'Jan._Febr._Mrz._Apr._Mai_Jun._Jul._Aug._Sept._Okt._Nov._Dez.'.split('_'),
    monthsParseExact:true,
    weekdays:'Sonntag_Montag_Dienstag_Mittwoch_Donnerstag_Freitag_Samstag'.split('_'),
    weekdaysShort:'So._Mo._Di._Mi._Do._Fr._Sa.'.split('_'),
    weekdaysMin:'So_Mo_Di_Mi_Do_Fr_Sa'.split('_'),
    weekdaysParseExact:true,
    longDateFormat:{
        LT:'HH:mm',
        LTS:'HH:mm:ss',
        L:'DD.MM.YYYY',
        LL:'D.MMMMYYYY',
        LLL:'D.MMMMYYYYHH:mm',
        LLLL:'dddd,D.MMMMYYYYHH:mm'
    },
    calendar:{
        sameDay:'[heuteum]LT[Uhr]',
        sameElse:'L',
        nextDay:'[morgenum]LT[Uhr]',
        nextWeek:'dddd[um]LT[Uhr]',
        lastDay:'[gesternum]LT[Uhr]',
        lastWeek:'[letzten]dddd[um]LT[Uhr]'
    },
    relativeTime:{
        future:'in%s',
        past:'vor%s',
        s:'einpaarSekunden',
        m:processRelativeTime,
        mm:'%dMinuten',
        h:processRelativeTime,
        hh:'%dStunden',
        d:processRelativeTime,
        dd:processRelativeTime,
        M:processRelativeTime,
        MM:processRelativeTime,
        y:processRelativeTime,
        yy:processRelativeTime
    },
    ordinalParse:/\d{1,2}\./,
    ordinal:'%d.',
    week:{
        dow:1,//Mondayisthefirstdayoftheweek.
        doy:4 //TheweekthatcontainsJan4thisthefirstweekoftheyear.
    }
});

returnde;

})));
