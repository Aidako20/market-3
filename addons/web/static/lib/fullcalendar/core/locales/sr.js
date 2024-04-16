(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.sr=factory()));
}(this,function(){'usestrict';

    varsr={
        code:"sr",
        week:{
            dow:1,
            doy:7//TheweekthatcontainsJan1stisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Prethodna",
            next:"Sledeći",
            today:"Danas",
            month:"Mеsеc",
            week:"Nеdеlja",
            day:"Dan",
            list:"Planеr"
        },
        weekLabel:"Sed",
        allDayText:"Cеodan",
        eventLimitText:function(n){
            return"+još"+n;
        },
        noEventsMessage:"Nеmadogađajazaprikaz"
    };

    returnsr;

}));
