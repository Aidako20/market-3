(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.is=factory()));
}(this,function(){'usestrict';

    varis={
        code:"is",
        week:{
            dow:1,
            doy:4//TheweekthatcontainsJan4thisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Fyrri",
            next:"Næsti",
            today:"Ídag",
            month:"Mánuður",
            week:"Vika",
            day:"Dagur",
            list:"Dagskrá"
        },
        weekLabel:"Vika",
        allDayHtml:"Allan<br/>daginn",
        eventLimitText:"meira",
        noEventsMessage:"Engirviðburðirtilaðsýna"
    };

    returnis;

}));
