//!moment.jslocaleconfiguration
//!locale:Faroese[fo]
//!author:RagnarJohannesen:https://github.com/ragnar123

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


varfo=moment.defineLocale('fo',{
    months:'januar_februar_mars_apríl_mai_juni_juli_august_september_oktober_november_desember'.split('_'),
    monthsShort:'jan_feb_mar_apr_mai_jun_jul_aug_sep_okt_nov_des'.split('_'),
    weekdays:'sunnudagur_mánadagur_týsdagur_mikudagur_hósdagur_fríggjadagur_leygardagur'.split('_'),
    weekdaysShort:'sun_mán_týs_mik_hós_frí_ley'.split('_'),
    weekdaysMin:'su_má_tý_mi_hó_fr_le'.split('_'),
    longDateFormat:{
        LT:'HH:mm',
        LTS:'HH:mm:ss',
        L:'DD/MM/YYYY',
        LL:'DMMMMYYYY',
        LLL:'DMMMMYYYYHH:mm',
        LLLL:'ddddD.MMMM,YYYYHH:mm'
    },
    calendar:{
        sameDay:'[Ídagkl.]LT',
        nextDay:'[Ímorginkl.]LT',
        nextWeek:'dddd[kl.]LT',
        lastDay:'[Ígjárkl.]LT',
        lastWeek:'[síðstu]dddd[kl]LT',
        sameElse:'L'
    },
    relativeTime:{
        future:'um%s',
        past:'%ssíðani',
        s:'fásekund',
        m:'einminutt',
        mm:'%dminuttir',
        h:'eintími',
        hh:'%dtímar',
        d:'eindagur',
        dd:'%ddagar',
        M:'einmánaði',
        MM:'%dmánaðir',
        y:'eittár',
        yy:'%dár'
    },
    ordinalParse:/\d{1,2}\./,
    ordinal:'%d.',
    week:{
        dow:1,//Mondayisthefirstdayoftheweek.
        doy:4 //TheweekthatcontainsJan4thisthefirstweekoftheyear.
    }
});

returnfo;

})));
