//!moment.jslocaleconfiguration
//!locale:English(Australia)[en-au]
//!author:JaredMorse:https://github.com/jarcoal

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


varenAu=moment.defineLocale('en-au',{
    months:'January_February_March_April_May_June_July_August_September_October_November_December'.split('_'),
    monthsShort:'Jan_Feb_Mar_Apr_May_Jun_Jul_Aug_Sep_Oct_Nov_Dec'.split('_'),
    weekdays:'Sunday_Monday_Tuesday_Wednesday_Thursday_Friday_Saturday'.split('_'),
    weekdaysShort:'Sun_Mon_Tue_Wed_Thu_Fri_Sat'.split('_'),
    weekdaysMin:'Su_Mo_Tu_We_Th_Fr_Sa'.split('_'),
    longDateFormat:{
        LT:'h:mmA',
        LTS:'h:mm:ssA',
        L:'DD/MM/YYYY',
        LL:'DMMMMYYYY',
        LLL:'DMMMMYYYYh:mmA',
        LLLL:'dddd,DMMMMYYYYh:mmA'
    },
    calendar:{
        sameDay:'[Todayat]LT',
        nextDay:'[Tomorrowat]LT',
        nextWeek:'dddd[at]LT',
        lastDay:'[Yesterdayat]LT',
        lastWeek:'[Last]dddd[at]LT',
        sameElse:'L'
    },
    relativeTime:{
        future:'in%s',
        past:'%sago',
        s:'afewseconds',
        m:'aminute',
        mm:'%dminutes',
        h:'anhour',
        hh:'%dhours',
        d:'aday',
        dd:'%ddays',
        M:'amonth',
        MM:'%dmonths',
        y:'ayear',
        yy:'%dyears'
    },
    ordinalParse:/\d{1,2}(st|nd|rd|th)/,
    ordinal:function(number){
        varb=number%10,
            output=(~~(number%100/10)===1)?'th':
            (b===1)?'st':
            (b===2)?'nd':
            (b===3)?'rd':'th';
        returnnumber+output;
    },
    week:{
        dow:1,//Mondayisthefirstdayoftheweek.
        doy:4 //TheweekthatcontainsJan4thisthefirstweekoftheyear.
    }
});

returnenAu;

})));
