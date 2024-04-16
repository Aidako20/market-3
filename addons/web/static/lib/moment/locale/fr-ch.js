//!moment.jslocaleconfiguration
//!locale:French(Switzerland)[fr-ch]
//!author:GaspardBucher:https://github.com/gaspard

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


varfrCh=moment.defineLocale('fr-ch',{
    months:'janvier_février_mars_avril_mai_juin_juillet_août_septembre_octobre_novembre_décembre'.split('_'),
    monthsShort:'janv._févr._mars_avr._mai_juin_juil._août_sept._oct._nov._déc.'.split('_'),
    monthsParseExact:true,
    weekdays:'dimanche_lundi_mardi_mercredi_jeudi_vendredi_samedi'.split('_'),
    weekdaysShort:'dim._lun._mar._mer._jeu._ven._sam.'.split('_'),
    weekdaysMin:'Di_Lu_Ma_Me_Je_Ve_Sa'.split('_'),
    weekdaysParseExact:true,
    longDateFormat:{
        LT:'HH:mm',
        LTS:'HH:mm:ss',
        L:'DD.MM.YYYY',
        LL:'DMMMMYYYY',
        LLL:'DMMMMYYYYHH:mm',
        LLLL:'ddddDMMMMYYYYHH:mm'
    },
    calendar:{
        sameDay:'[Aujourd\'huià]LT',
        nextDay:'[Demainà]LT',
        nextWeek:'dddd[à]LT',
        lastDay:'[Hierà]LT',
        lastWeek:'dddd[dernierà]LT',
        sameElse:'L'
    },
    relativeTime:{
        future:'dans%s',
        past:'ilya%s',
        s:'quelquessecondes',
        m:'uneminute',
        mm:'%dminutes',
        h:'uneheure',
        hh:'%dheures',
        d:'unjour',
        dd:'%djours',
        M:'unmois',
        MM:'%dmois',
        y:'unan',
        yy:'%dans'
    },
    ordinalParse:/\d{1,2}(er|e)/,
    ordinal:function(number){
        returnnumber+(number===1?'er':'e');
    },
    week:{
        dow:1,//Mondayisthefirstdayoftheweek.
        doy:4 //TheweekthatcontainsJan4thisthefirstweekoftheyear.
    }
});

returnfrCh;

})));
