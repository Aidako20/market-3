//!moment.jslocaleconfiguration
//!locale:NorwegianBokmål[nb]
//!authors:EspenHovlandsdal:https://github.com/rexxars
//!          SigurdGartmann:https://github.com/sigurdga

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


varnb=moment.defineLocale('nb',{
    months:'januar_februar_mars_april_mai_juni_juli_august_september_oktober_november_desember'.split('_'),
    monthsShort:'jan._feb._mars_april_mai_juni_juli_aug._sep._okt._nov._des.'.split('_'),
    monthsParseExact:true,
    weekdays:'søndag_mandag_tirsdag_onsdag_torsdag_fredag_lørdag'.split('_'),
    weekdaysShort:'sø._ma._ti._on._to._fr._lø.'.split('_'),
    weekdaysMin:'sø_ma_ti_on_to_fr_lø'.split('_'),
    weekdaysParseExact:true,
    longDateFormat:{
        LT:'HH:mm',
        LTS:'HH:mm:ss',
        L:'DD.MM.YYYY',
        LL:'D.MMMMYYYY',
        LLL:'D.MMMMYYYY[kl.]HH:mm',
        LLLL:'ddddD.MMMMYYYY[kl.]HH:mm'
    },
    calendar:{
        sameDay:'[idagkl.]LT',
        nextDay:'[imorgenkl.]LT',
        nextWeek:'dddd[kl.]LT',
        lastDay:'[igårkl.]LT',
        lastWeek:'[forrige]dddd[kl.]LT',
        sameElse:'L'
    },
    relativeTime:{
        future:'om%s',
        past:'%ssiden',
        s:'noensekunder',
        m:'ettminutt',
        mm:'%dminutter',
        h:'entime',
        hh:'%dtimer',
        d:'endag',
        dd:'%ddager',
        M:'enmåned',
        MM:'%dmåneder',
        y:'ettår',
        yy:'%dår'
    },
    ordinalParse:/\d{1,2}\./,
    ordinal:'%d.',
    week:{
        dow:1,//Mondayisthefirstdayoftheweek.
        doy:4 //TheweekthatcontainsJan4thisthefirstweekoftheyear.
    }
});

returnnb;

})));
