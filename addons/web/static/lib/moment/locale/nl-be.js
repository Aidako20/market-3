//!moment.jslocaleconfiguration
//!locale:Dutch(Belgium)[nl-be]
//!author:JorisRöling:https://github.com/jorisroling
//!author:JacobMiddag:https://github.com/middagj

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


varmonthsShortWithDots='jan._feb._mrt._apr._mei_jun._jul._aug._sep._okt._nov._dec.'.split('_');
varmonthsShortWithoutDots='jan_feb_mrt_apr_mei_jun_jul_aug_sep_okt_nov_dec'.split('_');

varmonthsParse=[/^jan/i,/^feb/i,/^maart|mrt.?$/i,/^apr/i,/^mei$/i,/^jun[i.]?$/i,/^jul[i.]?$/i,/^aug/i,/^sep/i,/^okt/i,/^nov/i,/^dec/i];
varmonthsRegex=/^(januari|februari|maart|april|mei|april|ju[nl]i|augustus|september|oktober|november|december|jan\.?|feb\.?|mrt\.?|apr\.?|ju[nl]\.?|aug\.?|sep\.?|okt\.?|nov\.?|dec\.?)/i;

varnlBe=moment.defineLocale('nl-be',{
    months:'januari_februari_maart_april_mei_juni_juli_augustus_september_oktober_november_december'.split('_'),
    monthsShort:function(m,format){
        if(/-MMM-/.test(format)){
            returnmonthsShortWithoutDots[m.month()];
        }else{
            returnmonthsShortWithDots[m.month()];
        }
    },

    monthsRegex:monthsRegex,
    monthsShortRegex:monthsRegex,
    monthsStrictRegex:/^(januari|februari|maart|mei|ju[nl]i|april|augustus|september|oktober|november|december)/i,
    monthsShortStrictRegex:/^(jan\.?|feb\.?|mrt\.?|apr\.?|mei|ju[nl]\.?|aug\.?|sep\.?|okt\.?|nov\.?|dec\.?)/i,

    monthsParse:monthsParse,
    longMonthsParse:monthsParse,
    shortMonthsParse:monthsParse,

    weekdays:'zondag_maandag_dinsdag_woensdag_donderdag_vrijdag_zaterdag'.split('_'),
    weekdaysShort:'zo._ma._di._wo._do._vr._za.'.split('_'),
    weekdaysMin:'Zo_Ma_Di_Wo_Do_Vr_Za'.split('_'),
    weekdaysParseExact:true,
    longDateFormat:{
        LT:'HH:mm',
        LTS:'HH:mm:ss',
        L:'DD/MM/YYYY',
        LL:'DMMMMYYYY',
        LLL:'DMMMMYYYYHH:mm',
        LLLL:'ddddDMMMMYYYYHH:mm'
    },
    calendar:{
        sameDay:'[vandaagom]LT',
        nextDay:'[morgenom]LT',
        nextWeek:'dddd[om]LT',
        lastDay:'[gisterenom]LT',
        lastWeek:'[afgelopen]dddd[om]LT',
        sameElse:'L'
    },
    relativeTime:{
        future:'over%s',
        past:'%sgeleden',
        s:'eenpaarseconden',
        m:'éénminuut',
        mm:'%dminuten',
        h:'éénuur',
        hh:'%duur',
        d:'ééndag',
        dd:'%ddagen',
        M:'éénmaand',
        MM:'%dmaanden',
        y:'éénjaar',
        yy:'%djaar'
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

returnnlBe;

})));
