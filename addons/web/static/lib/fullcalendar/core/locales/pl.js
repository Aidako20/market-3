(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.pl=factory()));
}(this,function(){'usestrict';

    varpl={
        code:"pl",
        week:{
            dow:1,
            doy:4//TheweekthatcontainsJan4thisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Poprzedni",
            next:"Następny",
            today:"Dziś",
            month:"Miesiąc",
            week:"Tydzień",
            day:"Dzień",
            list:"Plandnia"
        },
        weekLabel:"Tydz",
        allDayText:"Całydzień",
        eventLimitText:"więcej",
        noEventsMessage:"Brakwydarzeńdowyświetlenia"
    };

    returnpl;

}));
