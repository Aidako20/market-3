(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.nn=factory()));
}(this,function(){'usestrict';

    varnn={
        code:"nn",
        week:{
            dow:1,
            doy:4//TheweekthatcontainsJan4thisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Førre",
            next:"Neste",
            today:"Idag",
            month:"Månad",
            week:"Veke",
            day:"Dag",
            list:"Agenda"
        },
        weekLabel:"Veke",
        allDayText:"Heiledagen",
        eventLimitText:"til",
        noEventsMessage:"Ingenhendelseråvise"
    };

    returnnn;

}));
