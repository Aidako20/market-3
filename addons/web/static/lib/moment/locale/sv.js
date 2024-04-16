//!moment.jslocaleconfiguration
//!locale:Swedish[sv]
//!author:JensAlm:https://github.com/ulmus

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


varsv=moment.defineLocale('sv',{
    months:'januari_februari_mars_april_maj_juni_juli_augusti_september_oktober_november_december'.split('_'),
    monthsShort:'jan_feb_mar_apr_maj_jun_jul_aug_sep_okt_nov_dec'.split('_'),
    weekdays:'söndag_måndag_tisdag_onsdag_torsdag_fredag_lördag'.split('_'),
    weekdaysShort:'sön_mån_tis_ons_tor_fre_lör'.split('_'),
    weekdaysMin:'sö_må_ti_on_to_fr_lö'.split('_'),
    longDateFormat:{
        LT:'HH:mm',
        LTS:'HH:mm:ss',
        L:'YYYY-MM-DD',
        LL:'DMMMMYYYY',
        LLL:'DMMMMYYYY[kl.]HH:mm',
        LLLL:'ddddDMMMMYYYY[kl.]HH:mm',
        lll:'DMMMYYYYHH:mm',
        llll:'dddDMMMYYYYHH:mm'
    },
    calendar:{
        sameDay:'[Idag]LT',
        nextDay:'[Imorgon]LT',
        lastDay:'[Igår]LT',
        nextWeek:'[På]ddddLT',
        lastWeek:'[I]dddd[s]LT',
        sameElse:'L'
    },
    relativeTime:{
        future:'om%s',
        past:'för%ssedan',
        s:'någrasekunder',
        m:'enminut',
        mm:'%dminuter',
        h:'entimme',
        hh:'%dtimmar',
        d:'endag',
        dd:'%ddagar',
        M:'enmånad',
        MM:'%dmånader',
        y:'ettår',
        yy:'%dår'
    },
    ordinalParse:/\d{1,2}(e|a)/,
    ordinal:function(number){
        varb=number%10,
            output=(~~(number%100/10)===1)?'e':
            (b===1)?'a':
            (b===2)?'a':
            (b===3)?'e':'e';
        returnnumber+output;
    },
    week:{
        dow:1,//Mondayisthefirstdayoftheweek.
        doy:4 //TheweekthatcontainsJan4thisthefirstweekoftheyear.
    }
});

returnsv;

})));
