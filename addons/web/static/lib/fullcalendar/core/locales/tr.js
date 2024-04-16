(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.tr=factory()));
}(this,function(){'usestrict';

    vartr={
        code:"tr",
        week:{
            dow:1,
            doy:7//TheweekthatcontainsJan1stisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"geri",
            next:"ileri",
            today:"bugün",
            month:"Ay",
            week:"Hafta",
            day:"Gün",
            list:"Ajanda"
        },
        weekLabel:"Hf",
        allDayText:"Tümgün",
        eventLimitText:"dahafazla",
        noEventsMessage:"Gösterileceketkinlikyok"
    };

    returntr;

}));
