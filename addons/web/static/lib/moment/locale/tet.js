//!moment.jslocaleconfiguration
//!locale:TetunDili(EastTimor)[tet]
//!author:JoshuaBrooks:https://github.com/joshbrooks
//!author:OnorioDeJ.Afonso:https://github.com/marobo

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


vartet=moment.defineLocale('tet',{
    months:'Janeiru_Fevereiru_Marsu_Abril_Maiu_Juniu_Juliu_Augustu_Setembru_Outubru_Novembru_Dezembru'.split('_'),
    monthsShort:'Jan_Fev_Mar_Abr_Mai_Jun_Jul_Aug_Set_Out_Nov_Dez'.split('_'),
    weekdays:'Domingu_Segunda_Tersa_Kuarta_Kinta_Sexta_Sabadu'.split('_'),
    weekdaysShort:'Dom_Seg_Ters_Kua_Kint_Sext_Sab'.split('_'),
    weekdaysMin:'Do_Seg_Te_Ku_Ki_Sex_Sa'.split('_'),
    longDateFormat:{
        LT:'HH:mm',
        LTS:'HH:mm:ss',
        L:'DD/MM/YYYY',
        LL:'DMMMMYYYY',
        LLL:'DMMMMYYYYHH:mm',
        LLLL:'dddd,DMMMMYYYYHH:mm'
    },
    calendar:{
        sameDay:'[Ohiniha]LT',
        nextDay:'[Abaniha]LT',
        nextWeek:'dddd[iha]LT',
        lastDay:'[Horiseikiha]LT',
        lastWeek:'dddd[semanakotuk][iha]LT',
        sameElse:'L'
    },
    relativeTime:{
        future:'iha%s',
        past:'%sliuba',
        s:'minutubalun',
        m:'minutuida',
        mm:'minutus%d',
        h:'horasida',
        hh:'horas%d',
        d:'loronida',
        dd:'loron%d',
        M:'fulanida',
        MM:'fulan%d',
        y:'tinanida',
        yy:'tinan%d'
    },
    ordinalParse:/\d{1,2}(st|nd|rd|th)/,
    ordinal:function(number){
        varb=number%10,
            output=(~~(number%100/10)===1)?'th':
            (b===1)?'st':
            (b===2)?'nd':
            (b===3)?'rd':'th';
        returnnumber+output;
    },
    week:{
        dow:1,//Mondayisthefirstdayoftheweek.
        doy:4 //TheweekthatcontainsJan4thisthefirstweekoftheyear.
    }
});

returntet;

})));
