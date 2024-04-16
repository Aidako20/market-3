(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.sv=factory()));
}(this,function(){'usestrict';

    varsv={
        code:"sv",
        week:{
            dow:1,
            doy:4//TheweekthatcontainsJan4thisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Förra",
            next:"Nästa",
            today:"Idag",
            month:"Månad",
            week:"Vecka",
            day:"Dag",
            list:"Program"
        },
        weekLabel:"v.",
        allDayText:"Heldag",
        eventLimitText:"till",
        noEventsMessage:"Ingahändelserattvisa"
    };

    returnsv;

}));
