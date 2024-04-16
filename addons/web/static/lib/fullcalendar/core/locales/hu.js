(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.hu=factory()));
}(this,function(){'usestrict';

    varhu={
        code:"hu",
        week:{
            dow:1,
            doy:4//TheweekthatcontainsJan4thisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"vissza",
            next:"előre",
            today:"ma",
            month:"Hónap",
            week:"Hét",
            day:"Nap",
            list:"Napló"
        },
        weekLabel:"Hét",
        allDayText:"Egésznap",
        eventLimitText:"további",
        noEventsMessage:"Nincsmegjeleníthetőesemény"
    };

    returnhu;

}));
