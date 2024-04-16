//!moment.jslocaleconfiguration
//!locale:ScottishGaelic[gd]
//!author:JonAshdown:https://github.com/jonashdown

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


varmonths=[
    'AmFaoilleach','AnGearran','AmMàrt','AnGiblean','AnCèitean','Ant-Ògmhios','Ant-Iuchar','AnLùnastal','Ant-Sultain','AnDàmhair','Ant-Samhain','AnDùbhlachd'
];

varmonthsShort=['Faoi','Gear','Màrt','Gibl','Cèit','Ògmh','Iuch','Lùn','Sult','Dàmh','Samh','Dùbh'];

varweekdays=['Didòmhnaich','Diluain','Dimàirt','Diciadain','Diardaoin','Dihaoine','Disathairne'];

varweekdaysShort=['Did','Dil','Dim','Dic','Dia','Dih','Dis'];

varweekdaysMin=['Dò','Lu','Mà','Ci','Ar','Ha','Sa'];

vargd=moment.defineLocale('gd',{
    months:months,
    monthsShort:monthsShort,
    monthsParseExact:true,
    weekdays:weekdays,
    weekdaysShort:weekdaysShort,
    weekdaysMin:weekdaysMin,
    longDateFormat:{
        LT:'HH:mm',
        LTS:'HH:mm:ss',
        L:'DD/MM/YYYY',
        LL:'DMMMMYYYY',
        LLL:'DMMMMYYYYHH:mm',
        LLLL:'dddd,DMMMMYYYYHH:mm'
    },
    calendar:{
        sameDay:'[An-diughaig]LT',
        nextDay:'[A-màireachaig]LT',
        nextWeek:'dddd[aig]LT',
        lastDay:'[An-dèaig]LT',
        lastWeek:'dddd[seochaidh][aig]LT',
        sameElse:'L'
    },
    relativeTime:{
        future:'annan%s',
        past:'bhochionn%s',
        s:'beagandiogan',
        m:'mionaid',
        mm:'%dmionaidean',
        h:'uair',
        hh:'%duairean',
        d:'latha',
        dd:'%dlatha',
        M:'mìos',
        MM:'%dmìosan',
        y:'bliadhna',
        yy:'%dbliadhna'
    },
    ordinalParse:/\d{1,2}(d|na|mh)/,
    ordinal:function(number){
        varoutput=number===1?'d':number%10===2?'na':'mh';
        returnnumber+output;
    },
    week:{
        dow:1,//Mondayisthefirstdayoftheweek.
        doy:4 //TheweekthatcontainsJan4thisthefirstweekoftheyear.
    }
});

returngd;

})));
