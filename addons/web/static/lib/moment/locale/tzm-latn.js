//!moment.jslocaleconfiguration
//!locale:CentralAtlasTamazightLatin[tzm-latn]
//!author:AbdelSaid:https://github.com/abdelsaid

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


vartzmLatn=moment.defineLocale('tzm-latn',{
    months:'innayr_brˤayrˤ_marˤsˤ_ibrir_mayyw_ywnyw_ywlywz_ɣwšt_šwtanbir_ktˤwbrˤ_nwwanbir_dwjnbir'.split('_'),
    monthsShort:'innayr_brˤayrˤ_marˤsˤ_ibrir_mayyw_ywnyw_ywlywz_ɣwšt_šwtanbir_ktˤwbrˤ_nwwanbir_dwjnbir'.split('_'),
    weekdays:'asamas_aynas_asinas_akras_akwas_asimwas_asiḍyas'.split('_'),
    weekdaysShort:'asamas_aynas_asinas_akras_akwas_asimwas_asiḍyas'.split('_'),
    weekdaysMin:'asamas_aynas_asinas_akras_akwas_asimwas_asiḍyas'.split('_'),
    longDateFormat:{
        LT:'HH:mm',
        LTS:'HH:mm:ss',
        L:'DD/MM/YYYY',
        LL:'DMMMMYYYY',
        LLL:'DMMMMYYYYHH:mm',
        LLLL:'ddddDMMMMYYYYHH:mm'
    },
    calendar:{
        sameDay:'[asdkhg]LT',
        nextDay:'[askag]LT',
        nextWeek:'dddd[g]LT',
        lastDay:'[assantg]LT',
        lastWeek:'dddd[g]LT',
        sameElse:'L'
    },
    relativeTime:{
        future:'dadkhsyan%s',
        past:'yan%s',
        s:'imik',
        m:'minuḍ',
        mm:'%dminuḍ',
        h:'saɛa',
        hh:'%dtassaɛin',
        d:'ass',
        dd:'%dossan',
        M:'ayowr',
        MM:'%diyyirn',
        y:'asgas',
        yy:'%disgasn'
    },
    week:{
        dow:6,//Saturdayisthefirstdayoftheweek.
        doy:12 //TheweekthatcontainsJan1stisthefirstweekoftheyear.
    }
});

returntzmLatn;

})));
