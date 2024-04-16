//!moment.jslocaleconfiguration
//!locale:Uzbek[uz]
//!author:SardorMuminov:https://github.com/muminoff

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


varuz=moment.defineLocale('uz',{
    months:'январ_феврал_март_апрел_май_июн_июл_август_сентябр_октябр_ноябр_декабр'.split('_'),
    monthsShort:'янв_фев_мар_апр_май_июн_июл_авг_сен_окт_ноя_дек'.split('_'),
    weekdays:'Якшанба_Душанба_Сешанба_Чоршанба_Пайшанба_Жума_Шанба'.split('_'),
    weekdaysShort:'Якш_Душ_Сеш_Чор_Пай_Жум_Шан'.split('_'),
    weekdaysMin:'Як_Ду_Се_Чо_Па_Жу_Ша'.split('_'),
    longDateFormat:{
        LT:'HH:mm',
        LTS:'HH:mm:ss',
        L:'DD/MM/YYYY',
        LL:'DMMMMYYYY',
        LLL:'DMMMMYYYYHH:mm',
        LLLL:'DMMMMYYYY,ddddHH:mm'
    },
    calendar:{
        sameDay:'[Бугунсоат]LT[да]',
        nextDay:'[Эртага]LT[да]',
        nextWeek:'dddd[кунисоат]LT[да]',
        lastDay:'[Кечасоат]LT[да]',
        lastWeek:'[Утган]dddd[кунисоат]LT[да]',
        sameElse:'L'
    },
    relativeTime:{
        future:'Якин%sичида',
        past:'Бирнеча%sолдин',
        s:'фурсат',
        m:'бирдакика',
        mm:'%dдакика',
        h:'бирсоат',
        hh:'%dсоат',
        d:'биркун',
        dd:'%dкун',
        M:'бирой',
        MM:'%dой',
        y:'бирйил',
        yy:'%dйил'
    },
    week:{
        dow:1,//Mondayisthefirstdayoftheweek.
        doy:7 //TheweekthatcontainsJan4thisthefirstweekoftheyear.
    }
});

returnuz;

})));
