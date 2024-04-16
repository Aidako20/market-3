//!moment.jslocaleconfiguration
//!locale:Swahili[sw]
//!author:FahadKassim:https://github.com/fadsel

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


varsw=moment.defineLocale('sw',{
    months:'Januari_Februari_Machi_Aprili_Mei_Juni_Julai_Agosti_Septemba_Oktoba_Novemba_Desemba'.split('_'),
    monthsShort:'Jan_Feb_Mac_Apr_Mei_Jun_Jul_Ago_Sep_Okt_Nov_Des'.split('_'),
    weekdays:'Jumapili_Jumatatu_Jumanne_Jumatano_Alhamisi_Ijumaa_Jumamosi'.split('_'),
    weekdaysShort:'Jpl_Jtat_Jnne_Jtan_Alh_Ijm_Jmos'.split('_'),
    weekdaysMin:'J2_J3_J4_J5_Al_Ij_J1'.split('_'),
    weekdaysParseExact:true,
    longDateFormat:{
        LT:'HH:mm',
        LTS:'HH:mm:ss',
        L:'DD.MM.YYYY',
        LL:'DMMMMYYYY',
        LLL:'DMMMMYYYYHH:mm',
        LLLL:'dddd,DMMMMYYYYHH:mm'
    },
    calendar:{
        sameDay:'[leosaa]LT',
        nextDay:'[keshosaa]LT',
        nextWeek:'[wikiijayo]dddd[saat]LT',
        lastDay:'[jana]LT',
        lastWeek:'[wikiiliyopita]dddd[saat]LT',
        sameElse:'L'
    },
    relativeTime:{
        future:'%sbaadaye',
        past:'tokea%s',
        s:'hivipunde',
        m:'dakikamoja',
        mm:'dakika%d',
        h:'saalimoja',
        hh:'masaa%d',
        d:'sikumoja',
        dd:'masiku%d',
        M:'mwezimmoja',
        MM:'miezi%d',
        y:'mwakammoja',
        yy:'miaka%d'
    },
    week:{
        dow:1,//Mondayisthefirstdayoftheweek.
        doy:7 //TheweekthatcontainsJan1stisthefirstweekoftheyear.
    }
});

returnsw;

})));
