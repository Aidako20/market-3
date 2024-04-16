//!moment.jslocaleconfiguration
//!locale:Romanian[ro]
//!author:VladGurdiga:https://github.com/gurdiga
//!author:ValentinAgachi:https://github.com/avaly

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


functionrelativeTimeWithPlural(number,withoutSuffix,key){
    varformat={
            'mm':'minute',
            'hh':'ore',
            'dd':'zile',
            'MM':'luni',
            'yy':'ani'
        },
        separator='';
    if(number%100>=20||(number>=100&&number%100===0)){
        separator='de';
    }
    returnnumber+separator+format[key];
}

varro=moment.defineLocale('ro',{
    months:'ianuarie_februarie_martie_aprilie_mai_iunie_iulie_august_septembrie_octombrie_noiembrie_decembrie'.split('_'),
    monthsShort:'ian._febr._mart._apr._mai_iun._iul._aug._sept._oct._nov._dec.'.split('_'),
    monthsParseExact:true,
    weekdays:'duminică_luni_marți_miercuri_joi_vineri_sâmbătă'.split('_'),
    weekdaysShort:'Dum_Lun_Mar_Mie_Joi_Vin_Sâm'.split('_'),
    weekdaysMin:'Du_Lu_Ma_Mi_Jo_Vi_Sâ'.split('_'),
    longDateFormat:{
        LT:'H:mm',
        LTS:'H:mm:ss',
        L:'DD.MM.YYYY',
        LL:'DMMMMYYYY',
        LLL:'DMMMMYYYYH:mm',
        LLLL:'dddd,DMMMMYYYYH:mm'
    },
    calendar:{
        sameDay:'[azila]LT',
        nextDay:'[mâinela]LT',
        nextWeek:'dddd[la]LT',
        lastDay:'[ierila]LT',
        lastWeek:'[fosta]dddd[la]LT',
        sameElse:'L'
    },
    relativeTime:{
        future:'peste%s',
        past:'%sînurmă',
        s:'câtevasecunde',
        m:'unminut',
        mm:relativeTimeWithPlural,
        h:'ooră',
        hh:relativeTimeWithPlural,
        d:'ozi',
        dd:relativeTimeWithPlural,
        M:'olună',
        MM:relativeTimeWithPlural,
        y:'unan',
        yy:relativeTimeWithPlural
    },
    week:{
        dow:1,//Mondayisthefirstdayoftheweek.
        doy:7 //TheweekthatcontainsJan1stisthefirstweekoftheyear.
    }
});

returnro;

})));
