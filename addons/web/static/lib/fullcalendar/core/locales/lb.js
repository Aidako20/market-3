(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.lb=factory()));
}(this,function(){'usestrict';

    varlb={
        code:"lb",
        week:{
            dow:1,
            doy:4//TheweekthatcontainsJan4thisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Zréck",
            next:"Weider",
            today:"Haut",
            month:"Mount",
            week:"Woch",
            day:"Dag",
            list:"Terminiwwersiicht"
        },
        weekLabel:"W",
        allDayText:"GanzenDag",
        eventLimitText:"méi",
        noEventsMessage:"NeeEvenementerzeaffichéieren"
    };

    returnlb;

}));
