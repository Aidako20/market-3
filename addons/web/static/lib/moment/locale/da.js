//!moment.jslocaleconfiguration
//!locale:Danish[da]
//!author:UlrikNielsen:https://github.com/mrbase

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


varda=moment.defineLocale('da',{
    months:'januar_februar_marts_april_maj_juni_juli_august_september_oktober_november_december'.split('_'),
    monthsShort:'jan_feb_mar_apr_maj_jun_jul_aug_sep_okt_nov_dec'.split('_'),
    weekdays:'søndag_mandag_tirsdag_onsdag_torsdag_fredag_lørdag'.split('_'),
    weekdaysShort:'søn_man_tir_ons_tor_fre_lør'.split('_'),
    weekdaysMin:'sø_ma_ti_on_to_fr_lø'.split('_'),
    longDateFormat:{
        LT:'HH:mm',
        LTS:'HH:mm:ss',
        L:'DD/MM/YYYY',
        LL:'D.MMMMYYYY',
        LLL:'D.MMMMYYYYHH:mm',
        LLLL:'dddd[d.]D.MMMMYYYYHH:mm'
    },
    calendar:{
        sameDay:'[Idagkl.]LT',
        nextDay:'[Imorgenkl.]LT',
        nextWeek:'dddd[kl.]LT',
        lastDay:'[Igårkl.]LT',
        lastWeek:'[sidste]dddd[kl]LT',
        sameElse:'L'
    },
    relativeTime:{
        future:'om%s',
        past:'%ssiden',
        s:'fåsekunder',
        m:'etminut',
        mm:'%dminutter',
        h:'entime',
        hh:'%dtimer',
        d:'endag',
        dd:'%ddage',
        M:'enmåned',
        MM:'%dmåneder',
        y:'etår',
        yy:'%dår'
    },
    ordinalParse:/\d{1,2}\./,
    ordinal:'%d.',
    week:{
        dow:1,//Mondayisthefirstdayoftheweek.
        doy:4 //TheweekthatcontainsJan4thisthefirstweekoftheyear.
    }
});

returnda;

})));
