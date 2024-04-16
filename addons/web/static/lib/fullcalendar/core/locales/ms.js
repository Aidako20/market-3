(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.ms=factory()));
}(this,function(){'usestrict';

    varms={
        code:"ms",
        week:{
            dow:1,
            doy:7//TheweekthatcontainsJan1stisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Sebelum",
            next:"Selepas",
            today:"hariini",
            month:"Bulan",
            week:"Minggu",
            day:"Hari",
            list:"Agenda"
        },
        weekLabel:"Mg",
        allDayText:"Sepanjanghari",
        eventLimitText:function(n){
            return"masihada"+n+"acara";
        },
        noEventsMessage:"Tiadaperistiwauntukdipaparkan"
    };

    returnms;

}));
