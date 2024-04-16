//!moment.jslocaleconfiguration
//!locale:Basque[eu]
//!author:EnekoIllarramendi:https://github.com/eillarra

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


vareu=moment.defineLocale('eu',{
    months:'urtarrila_otsaila_martxoa_apirila_maiatza_ekaina_uztaila_abuztua_iraila_urria_azaroa_abendua'.split('_'),
    monthsShort:'urt._ots._mar._api._mai._eka._uzt._abu._ira._urr._aza._abe.'.split('_'),
    monthsParseExact:true,
    weekdays:'igandea_astelehena_asteartea_asteazkena_osteguna_ostirala_larunbata'.split('_'),
    weekdaysShort:'ig._al._ar._az._og._ol._lr.'.split('_'),
    weekdaysMin:'ig_al_ar_az_og_ol_lr'.split('_'),
    weekdaysParseExact:true,
    longDateFormat:{
        LT:'HH:mm',
        LTS:'HH:mm:ss',
        L:'YYYY-MM-DD',
        LL:'YYYY[ko]MMMM[ren]D[a]',
        LLL:'YYYY[ko]MMMM[ren]D[a]HH:mm',
        LLLL:'dddd,YYYY[ko]MMMM[ren]D[a]HH:mm',
        l:'YYYY-M-D',
        ll:'YYYY[ko]MMMD[a]',
        lll:'YYYY[ko]MMMD[a]HH:mm',
        llll:'ddd,YYYY[ko]MMMD[a]HH:mm'
    },
    calendar:{
        sameDay:'[gaur]LT[etan]',
        nextDay:'[bihar]LT[etan]',
        nextWeek:'ddddLT[etan]',
        lastDay:'[atzo]LT[etan]',
        lastWeek:'[aurreko]ddddLT[etan]',
        sameElse:'L'
    },
    relativeTime:{
        future:'%sbarru',
        past:'duela%s',
        s:'segundobatzuk',
        m:'minutubat',
        mm:'%dminutu',
        h:'ordubat',
        hh:'%dordu',
        d:'egunbat',
        dd:'%degun',
        M:'hilabetebat',
        MM:'%dhilabete',
        y:'urtebat',
        yy:'%durte'
    },
    ordinalParse:/\d{1,2}\./,
    ordinal:'%d.',
    week:{
        dow:1,//Mondayisthefirstdayoftheweek.
        doy:7 //TheweekthatcontainsJan1stisthefirstweekoftheyear.
    }
});

returneu;

})));
