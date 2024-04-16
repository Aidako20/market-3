//!moment.jslocaleconfiguration
//!locale:CentralAtlasTamazight[tzm]
//!author:AbdelSaid:https://github.com/abdelsaid

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


vartzm=moment.defineLocale('tzm',{
    months:'ⵉⵏⵏⴰⵢⵔ_ⴱⵕⴰⵢⵕ_ⵎⴰⵕⵚ_ⵉⴱⵔⵉⵔ_ⵎⴰⵢⵢⵓ_ⵢⵓⵏⵢⵓ_ⵢⵓⵍⵢⵓⵣ_ⵖⵓⵛⵜ_ⵛⵓⵜⴰⵏⴱⵉⵔ_ⴽⵟⵓⴱⵕ_ⵏⵓⵡⴰⵏⴱⵉⵔ_ⴷⵓⵊⵏⴱⵉⵔ'.split('_'),
    monthsShort:'ⵉⵏⵏⴰⵢⵔ_ⴱⵕⴰⵢⵕ_ⵎⴰⵕⵚ_ⵉⴱⵔⵉⵔ_ⵎⴰⵢⵢⵓ_ⵢⵓⵏⵢⵓ_ⵢⵓⵍⵢⵓⵣ_ⵖⵓⵛⵜ_ⵛⵓⵜⴰⵏⴱⵉⵔ_ⴽⵟⵓⴱⵕ_ⵏⵓⵡⴰⵏⴱⵉⵔ_ⴷⵓⵊⵏⴱⵉⵔ'.split('_'),
    weekdays:'ⴰⵙⴰⵎⴰⵙ_ⴰⵢⵏⴰⵙ_ⴰⵙⵉⵏⴰⵙ_ⴰⴽⵔⴰⵙ_ⴰⴽⵡⴰⵙ_ⴰⵙⵉⵎⵡⴰⵙ_ⴰⵙⵉⴹⵢⴰⵙ'.split('_'),
    weekdaysShort:'ⴰⵙⴰⵎⴰⵙ_ⴰⵢⵏⴰⵙ_ⴰⵙⵉⵏⴰⵙ_ⴰⴽⵔⴰⵙ_ⴰⴽⵡⴰⵙ_ⴰⵙⵉⵎⵡⴰⵙ_ⴰⵙⵉⴹⵢⴰⵙ'.split('_'),
    weekdaysMin:'ⴰⵙⴰⵎⴰⵙ_ⴰⵢⵏⴰⵙ_ⴰⵙⵉⵏⴰⵙ_ⴰⴽⵔⴰⵙ_ⴰⴽⵡⴰⵙ_ⴰⵙⵉⵎⵡⴰⵙ_ⴰⵙⵉⴹⵢⴰⵙ'.split('_'),
    longDateFormat:{
        LT:'HH:mm',
        LTS:'HH:mm:ss',
        L:'DD/MM/YYYY',
        LL:'DMMMMYYYY',
        LLL:'DMMMMYYYYHH:mm',
        LLLL:'ddddDMMMMYYYYHH:mm'
    },
    calendar:{
        sameDay:'[ⴰⵙⴷⵅⴴ]LT',
        nextDay:'[ⴰⵙⴽⴰⴴ]LT',
        nextWeek:'dddd[ⴴ]LT',
        lastDay:'[ⴰⵚⴰⵏⵜⴴ]LT',
        lastWeek:'dddd[ⴴ]LT',
        sameElse:'L'
    },
    relativeTime:{
        future:'ⴷⴰⴷⵅⵙⵢⴰⵏ%s',
        past:'ⵢⴰⵏ%s',
        s:'ⵉⵎⵉⴽ',
        m:'ⵎⵉⵏⵓⴺ',
        mm:'%dⵎⵉⵏⵓⴺ',
        h:'ⵙⴰⵄⴰ',
        hh:'%dⵜⴰⵙⵙⴰⵄⵉⵏ',
        d:'ⴰⵙⵙ',
        dd:'%doⵙⵙⴰⵏ',
        M:'ⴰⵢoⵓⵔ',
        MM:'%dⵉⵢⵢⵉⵔⵏ',
        y:'ⴰⵙⴳⴰⵙ',
        yy:'%dⵉⵙⴳⴰⵙⵏ'
    },
    week:{
        dow:6,//Saturdayisthefirstdayoftheweek.
        doy:12 //TheweekthatcontainsJan1stisthefirstweekoftheyear.
    }
});

returntzm;

})));
