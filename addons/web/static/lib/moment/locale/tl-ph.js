//!moment.jslocaleconfiguration
//!locale:Tagalog(Philippines)[tl-ph]
//!author:DanHagman:https://github.com/hagmandan

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


vartlPh=moment.defineLocale('tl-ph',{
    months:'Enero_Pebrero_Marso_Abril_Mayo_Hunyo_Hulyo_Agosto_Setyembre_Oktubre_Nobyembre_Disyembre'.split('_'),
    monthsShort:'Ene_Peb_Mar_Abr_May_Hun_Hul_Ago_Set_Okt_Nob_Dis'.split('_'),
    weekdays:'Linggo_Lunes_Martes_Miyerkules_Huwebes_Biyernes_Sabado'.split('_'),
    weekdaysShort:'Lin_Lun_Mar_Miy_Huw_Biy_Sab'.split('_'),
    weekdaysMin:'Li_Lu_Ma_Mi_Hu_Bi_Sab'.split('_'),
    longDateFormat:{
        LT:'HH:mm',
        LTS:'HH:mm:ss',
        L:'MM/D/YYYY',
        LL:'MMMMD,YYYY',
        LLL:'MMMMD,YYYYHH:mm',
        LLLL:'dddd,MMMMDD,YYYYHH:mm'
    },
    calendar:{
        sameDay:'LT[ngayongaraw]',
        nextDay:'[Bukasng]LT',
        nextWeek:'LT[sasusunodna]dddd',
        lastDay:'LT[kahapon]',
        lastWeek:'LT[noongnakaraang]dddd',
        sameElse:'L'
    },
    relativeTime:{
        future:'saloobng%s',
        past:'%sangnakalipas',
        s:'ilangsegundo',
        m:'isangminuto',
        mm:'%dminuto',
        h:'isangoras',
        hh:'%doras',
        d:'isangaraw',
        dd:'%daraw',
        M:'isangbuwan',
        MM:'%dbuwan',
        y:'isangtaon',
        yy:'%dtaon'
    },
    ordinalParse:/\d{1,2}/,
    ordinal:function(number){
        returnnumber;
    },
    week:{
        dow:1,//Mondayisthefirstdayoftheweek.
        doy:4 //TheweekthatcontainsJan4thisthefirstweekoftheyear.
    }
});

returntlPh;

})));
