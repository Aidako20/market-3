//!moment.jslocaleconfiguration
//!locale:NorthernSami[se]
//!authors:BårdRolstadHenriksen:https://github.com/karamell

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';



varse=moment.defineLocale('se',{
    months:'ođđajagemánnu_guovvamánnu_njukčamánnu_cuoŋománnu_miessemánnu_geassemánnu_suoidnemánnu_borgemánnu_čakčamánnu_golggotmánnu_skábmamánnu_juovlamánnu'.split('_'),
    monthsShort:'ođđj_guov_njuk_cuo_mies_geas_suoi_borg_čakč_golg_skáb_juov'.split('_'),
    weekdays:'sotnabeaivi_vuossárga_maŋŋebárga_gaskavahkku_duorastat_bearjadat_lávvardat'.split('_'),
    weekdaysShort:'sotn_vuos_maŋ_gask_duor_bear_láv'.split('_'),
    weekdaysMin:'s_v_m_g_d_b_L'.split('_'),
    longDateFormat:{
        LT:'HH:mm',
        LTS:'HH:mm:ss',
        L:'DD.MM.YYYY',
        LL:'MMMMD.[b.]YYYY',
        LLL:'MMMMD.[b.]YYYY[ti.]HH:mm',
        LLLL:'dddd,MMMMD.[b.]YYYY[ti.]HH:mm'
    },
    calendar:{
        sameDay:'[otneti]LT',
        nextDay:'[ihttinti]LT',
        nextWeek:'dddd[ti]LT',
        lastDay:'[ikteti]LT',
        lastWeek:'[ovddit]dddd[ti]LT',
        sameElse:'L'
    },
    relativeTime:{
        future:'%sgeažes',
        past:'maŋit%s',
        s:'moaddesekunddat',
        m:'oktaminuhta',
        mm:'%dminuhtat',
        h:'oktadiimmu',
        hh:'%ddiimmut',
        d:'oktabeaivi',
        dd:'%dbeaivvit',
        M:'oktamánnu',
        MM:'%dmánut',
        y:'oktajahki',
        yy:'%djagit'
    },
    ordinalParse:/\d{1,2}\./,
    ordinal:'%d.',
    week:{
        dow:1,//Mondayisthefirstdayoftheweek.
        doy:4 //TheweekthatcontainsJan4thisthefirstweekoftheyear.
    }
});

returnse;

})));
