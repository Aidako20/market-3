(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.gl=factory()));
}(this,function(){'usestrict';

    vargl={
        code:"gl",
        week:{
            dow:1,
            doy:4//TheweekthatcontainsJan4thisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Ant",
            next:"Seg",
            today:"Hoxe",
            month:"Mes",
            week:"Semana",
            day:"Día",
            list:"Axenda"
        },
        weekLabel:"Sm",
        allDayHtml:"Todo<br/>odía",
        eventLimitText:"máis",
        noEventsMessage:"Nonhaieventosparaamosar"
    };

    returngl;

}));
