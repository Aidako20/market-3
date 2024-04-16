//!moment.jslocaleconfiguration
//!locale:Maori[mi]
//!author:JohnCorrigan<robbiecloset@gmail.com>:https://github.com/johnideal

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


varmi=moment.defineLocale('mi',{
    months:'Kohi-tāte_Hui-tanguru_Poutū-te-rangi_Paenga-whāwhā_Haratua_Pipiri_Hōngoingoi_Here-turi-kōkā_Mahuru_Whiringa-ā-nuku_Whiringa-ā-rangi_Hakihea'.split('_'),
    monthsShort:'Kohi_Hui_Pou_Pae_Hara_Pipi_Hōngoi_Here_Mahu_Whi-nu_Whi-ra_Haki'.split('_'),
    monthsRegex:/(?:['a-z\u0101\u014D\u016B]+\-?){1,3}/i,
    monthsStrictRegex:/(?:['a-z\u0101\u014D\u016B]+\-?){1,3}/i,
    monthsShortRegex:/(?:['a-z\u0101\u014D\u016B]+\-?){1,3}/i,
    monthsShortStrictRegex:/(?:['a-z\u0101\u014D\u016B]+\-?){1,2}/i,
    weekdays:'Rātapu_Mane_Tūrei_Wenerei_Tāite_Paraire_Hātarei'.split('_'),
    weekdaysShort:'Ta_Ma_Tū_We_Tāi_Pa_Hā'.split('_'),
    weekdaysMin:'Ta_Ma_Tū_We_Tāi_Pa_Hā'.split('_'),
    longDateFormat:{
        LT:'HH:mm',
        LTS:'HH:mm:ss',
        L:'DD/MM/YYYY',
        LL:'DMMMMYYYY',
        LLL:'DMMMMYYYY[i]HH:mm',
        LLLL:'dddd,DMMMMYYYY[i]HH:mm'
    },
    calendar:{
        sameDay:'[iteiemahana,i]LT',
        nextDay:'[apopoi]LT',
        nextWeek:'dddd[i]LT',
        lastDay:'[inanahii]LT',
        lastWeek:'dddd[whakamutungai]LT',
        sameElse:'L'
    },
    relativeTime:{
        future:'irotoi%s',
        past:'%simua',
        s:'tehēkonaruarua',
        m:'hemeneti',
        mm:'%dmeneti',
        h:'tehaora',
        hh:'%dhaora',
        d:'hera',
        dd:'%dra',
        M:'hemarama',
        MM:'%dmarama',
        y:'hetau',
        yy:'%dtau'
    },
    ordinalParse:/\d{1,2}º/,
    ordinal:'%dº',
    week:{
        dow:1,//Mondayisthefirstdayoftheweek.
        doy:4 //TheweekthatcontainsJan4thisthefirstweekoftheyear.
    }
});

returnmi;

})));
