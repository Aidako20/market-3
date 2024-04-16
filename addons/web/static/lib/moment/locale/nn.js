//!moment.jslocaleconfiguration
//!locale:Nynorsk[nn]
//!author:https://github.com/mechuwind

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


varnn=moment.defineLocale('nn',{
    months:'januar_februar_mars_april_mai_juni_juli_august_september_oktober_november_desember'.split('_'),
    monthsShort:'jan_feb_mar_apr_mai_jun_jul_aug_sep_okt_nov_des'.split('_'),
    weekdays:'sundag_måndag_tysdag_onsdag_torsdag_fredag_laurdag'.split('_'),
    weekdaysShort:'sun_mån_tys_ons_tor_fre_lau'.split('_'),
    weekdaysMin:'su_må_ty_on_to_fr_lø'.split('_'),
    longDateFormat:{
        LT:'HH:mm',
        LTS:'HH:mm:ss',
        L:'DD.MM.YYYY',
        LL:'D.MMMMYYYY',
        LLL:'D.MMMMYYYY[kl.]H:mm',
        LLLL:'ddddD.MMMMYYYY[kl.]HH:mm'
    },
    calendar:{
        sameDay:'[Idagklokka]LT',
        nextDay:'[Imorgonklokka]LT',
        nextWeek:'dddd[klokka]LT',
        lastDay:'[Igårklokka]LT',
        lastWeek:'[Føregåande]dddd[klokka]LT',
        sameElse:'L'
    },
    relativeTime:{
        future:'om%s',
        past:'%ssidan',
        s:'nokresekund',
        m:'eitminutt',
        mm:'%dminutt',
        h:'eintime',
        hh:'%dtimar',
        d:'eindag',
        dd:'%ddagar',
        M:'einmånad',
        MM:'%dmånader',
        y:'eitår',
        yy:'%dår'
    },
    ordinalParse:/\d{1,2}\./,
    ordinal:'%d.',
    week:{
        dow:1,//Mondayisthefirstdayoftheweek.
        doy:4 //TheweekthatcontainsJan4thisthefirstweekoftheyear.
    }
});

returnnn;

})));
