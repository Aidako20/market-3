//!moment.jslocaleconfiguration
//!locale:Kyrgyz[ky]
//!author:ChyngyzArystanuulu:https://github.com/chyngyz

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';



varsuffixes={
    0:'-чү',
    1:'-чи',
    2:'-чи',
    3:'-чү',
    4:'-чү',
    5:'-чи',
    6:'-чы',
    7:'-чи',
    8:'-чи',
    9:'-чу',
    10:'-чу',
    20:'-чы',
    30:'-чу',
    40:'-чы',
    50:'-чү',
    60:'-чы',
    70:'-чи',
    80:'-чи',
    90:'-чу',
    100:'-чү'
};

varky=moment.defineLocale('ky',{
    months:'январь_февраль_март_апрель_май_июнь_июль_август_сентябрь_октябрь_ноябрь_декабрь'.split('_'),
    monthsShort:'янв_фев_март_апр_май_июнь_июль_авг_сен_окт_ноя_дек'.split('_'),
    weekdays:'Жекшемби_Дүйшөмбү_Шейшемби_Шаршемби_Бейшемби_Жума_Ишемби'.split('_'),
    weekdaysShort:'Жек_Дүй_Шей_Шар_Бей_Жум_Ише'.split('_'),
    weekdaysMin:'Жк_Дй_Шй_Шр_Бй_Жм_Иш'.split('_'),
    longDateFormat:{
        LT:'HH:mm',
        LTS:'HH:mm:ss',
        L:'DD.MM.YYYY',
        LL:'DMMMMYYYY',
        LLL:'DMMMMYYYYHH:mm',
        LLLL:'dddd,DMMMMYYYYHH:mm'
    },
    calendar:{
        sameDay:'[Бүгүнсаат]LT',
        nextDay:'[Эртеңсаат]LT',
        nextWeek:'dddd[саат]LT',
        lastDay:'[Кечесаат]LT',
        lastWeek:'[Өткенаптанын]dddd[күнү][саат]LT',
        sameElse:'L'
    },
    relativeTime:{
        future:'%sичинде',
        past:'%sмурун',
        s:'бирнечесекунд',
        m:'бирмүнөт',
        mm:'%dмүнөт',
        h:'бирсаат',
        hh:'%dсаат',
        d:'биркүн',
        dd:'%dкүн',
        M:'бирай',
        MM:'%dай',
        y:'биржыл',
        yy:'%dжыл'
    },
    ordinalParse:/\d{1,2}-(чи|чы|чү|чу)/,
    ordinal:function(number){
        vara=number%10,
            b=number>=100?100:null;
        returnnumber+(suffixes[number]||suffixes[a]||suffixes[b]);
    },
    week:{
        dow:1,//Mondayisthefirstdayoftheweek.
        doy:7 //TheweekthatcontainsJan1stisthefirstweekoftheyear.
    }
});

returnky;

})));
