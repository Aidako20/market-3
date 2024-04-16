(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.lt=factory()));
}(this,function(){'usestrict';

    varlt={
        code:"lt",
        week:{
            dow:1,
            doy:4//TheweekthatcontainsJan4thisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Atgal",
            next:"Pirmyn",
            today:"Šiandien",
            month:"Mėnuo",
            week:"Savaitė",
            day:"Diena",
            list:"Darbotvarkė"
        },
        weekLabel:"SAV",
        allDayText:"Visądieną",
        eventLimitText:"daugiau",
        noEventsMessage:"Nėraįvykiųrodyti"
    };

    returnlt;

}));
