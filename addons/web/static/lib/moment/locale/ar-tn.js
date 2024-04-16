//!moment.jslocaleconfiguration
//!locale : Arabic(Tunisia)[ar-tn]
//!author:NaderToukabri:https://github.com/naderio

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


vararTn=moment.defineLocale('ar-tn',{
    months:'جانفي_فيفري_مارس_أفريل_ماي_جوان_جويلية_أوت_سبتمبر_أكتوبر_نوفمبر_ديسمبر'.split('_'),
    monthsShort:'جانفي_فيفري_مارس_أفريل_ماي_جوان_جويلية_أوت_سبتمبر_أكتوبر_نوفمبر_ديسمبر'.split('_'),
    weekdays:'الأحد_الإثنين_الثلاثاء_الأربعاء_الخميس_الجمعة_السبت'.split('_'),
    weekdaysShort:'أحد_إثنين_ثلاثاء_أربعاء_خميس_جمعة_سبت'.split('_'),
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
        dow:1,//Mondayisthefirstdayoftheweek.
        doy:4//TheweekthatcontainsJan4thisthefirstweekoftheyear.
    }
});

returnarTn;

})));
