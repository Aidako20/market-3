//!moment.jslocaleconfiguration
//!locale:Frisian[fy]
//!author:RobinvanderVliet:https://github.com/robin0van0der0v

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


varmonthsShortWithDots='jan._feb._mrt._apr._mai_jun._jul._aug._sep._okt._nov._des.'.split('_');
varmonthsShortWithoutDots='jan_feb_mrt_apr_mai_jun_jul_aug_sep_okt_nov_des'.split('_');

varfy=moment.defineLocale('fy',{
    months:'jannewaris_febrewaris_maart_april_maaie_juny_july_augustus_septimber_oktober_novimber_desimber'.split('_'),
    monthsShort:function(m,format){
        if(/-MMM-/.test(format)){
            returnmonthsShortWithoutDots[m.month()];
        }else{
            returnmonthsShortWithDots[m.month()];
        }
    },
    monthsParseExact:true,
    weekdays:'snein_moandei_tiisdei_woansdei_tongersdei_freed_sneon'.split('_'),
    weekdaysShort:'si._mo._ti._wo._to._fr._so.'.split('_'),
    weekdaysMin:'Si_Mo_Ti_Wo_To_Fr_So'.split('_'),
    weekdaysParseExact:true,
    longDateFormat:{
        LT:'HH:mm',
        LTS:'HH:mm:ss',
        L:'DD-MM-YYYY',
        LL:'DMMMMYYYY',
        LLL:'DMMMMYYYYHH:mm',
        LLLL:'ddddDMMMMYYYYHH:mm'
    },
    calendar:{
        sameDay:'[hjoedom]LT',
        nextDay:'[moarnom]LT',
        nextWeek:'dddd[om]LT',
        lastDay:'[justerom]LT',
        lastWeek:'[ôfrûne]dddd[om]LT',
        sameElse:'L'
    },
    relativeTime:{
        future:'oer%s',
        past:'%slyn',
        s:'inpearsekonden',
        m:'ienminút',
        mm:'%dminuten',
        h:'ienoere',
        hh:'%doeren',
        d:'iendei',
        dd:'%ddagen',
        M:'ienmoanne',
        MM:'%dmoannen',
        y:'ienjier',
        yy:'%djierren'
    },
    ordinalParse:/\d{1,2}(ste|de)/,
    ordinal:function(number){
        returnnumber+((number===1||number===8||number>=20)?'ste':'de');
    },
    week:{
        dow:1,//Mondayisthefirstdayoftheweek.
        doy:4 //TheweekthatcontainsJan4thisthefirstweekoftheyear.
    }
});

returnfy;

})));
