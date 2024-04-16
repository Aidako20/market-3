(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.de=factory()));
}(this,function(){'usestrict';

    varde={
        code:"de",
        week:{
            dow:1,
            doy:4//TheweekthatcontainsJan4thisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Zurück",
            next:"Vor",
            today:"Heute",
            year:"Jahr",
            month:"Monat",
            week:"Woche",
            day:"Tag",
            list:"Terminübersicht"
        },
        weekLabel:"KW",
        allDayText:"Ganztägig",
        eventLimitText:function(n){
            return"+weitere"+n;
        },
        noEventsMessage:"KeineEreignisseanzuzeigen"
    };

    returnde;

}));
