//!moment.jslocaleconfiguration
//!locale:Arabic(Morocco)[ar-ma]
//!author:ElFadiliYassine:https://github.com/ElFadiliY
//!author:AbdelSaid:https://github.com/abdelsaid

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


vararMa=moment.defineLocale('ar-ma',{
    months:'يناير_فبراير_مارس_أبريل_ماي_يونيو_يوليوز_غشت_شتنبر_أكتوبر_نونبر_دجنبر'.split('_'),
    monthsShort:'يناير_فبراير_مارس_أبريل_ماي_يونيو_يوليوز_غشت_شتنبر_أكتوبر_نونبر_دجنبر'.split('_'),
    weekdays:'الأحد_الإتنين_الثلاثاء_الأربعاء_الخميس_الجمعة_السبت'.split('_'),
    weekdaysShort:'احد_اتنين_ثلاثاء_اربعاء_خميس_جمعة_سبت'.split('_'),
    weekdaysMin:'ح_ن_ث_ر_خ_ج_س'.split('_'),
    weekdaysParseExact:true,
    longDateFormat:{
        LT:'HH:mm',
        LTS:'HH:mm:ss',
        L:'DD/MM/YYYY',
        LL:'DMMMMYYYY',
        LLL:'DMMMMYYYYHH:mm',
        LLLL:'ddddDMMMMYYYYHH:mm'
    },
    calendar:{
        sameDay:'[اليومعلىالساعة]LT',
        nextDay:'[غداعلىالساعة]LT',
        nextWeek:'dddd[علىالساعة]LT',
        lastDay:'[أمسعلىالساعة]LT',
        lastWeek:'dddd[علىالساعة]LT',
        sameElse:'L'
    },
    relativeTime:{
        future:'في%s',
        past:'منذ%s',
        s:'ثوان',
        m:'دقيقة',
        mm:'%dدقائق',
        h:'ساعة',
        hh:'%dساعات',
        d:'يوم',
        dd:'%dأيام',
        M:'شهر',
        MM:'%dأشهر',
        y:'سنة',
        yy:'%dسنوات'
    },
    week:{
        dow:6,//Saturdayisthefirstdayoftheweek.
        doy:12 //TheweekthatcontainsJan1stisthefirstweekoftheyear.
    }
});

returnarMa;

})));
