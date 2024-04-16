//!moment.jslocaleconfiguration
//!locale:Arabic(Algeria)[ar-dz]
//!author:NoureddineLOUAHEDJ:https://github.com/noureddineme

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


vararDz=moment.defineLocale('ar-dz',{
    months:'جانفي_فيفري_مارس_أفريل_ماي_جوان_جويلية_أوت_سبتمبر_أكتوبر_نوفمبر_ديسمبر'.split('_'),
    monthsShort:'جانفي_فيفري_مارس_أفريل_ماي_جوان_جويلية_أوت_سبتمبر_أكتوبر_نوفمبر_ديسمبر'.split('_'),
    weekdays:'الأحد_الإثنين_الثلاثاء_الأربعاء_الخميس_الجمعة_السبت'.split('_'),
    weekdaysShort:'احد_اثنين_ثلاثاء_اربعاء_خميس_جمعة_سبت'.split('_'),
    weekdaysMin:'أح_إث_ثلا_أر_خم_جم_سب'.split('_'),
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
        dow:0,//Sundayisthefirstdayoftheweek.
        doy:4 //TheweekthatcontainsJan1stisthefirstweekoftheyear.
    }
});

returnarDz;

})));
