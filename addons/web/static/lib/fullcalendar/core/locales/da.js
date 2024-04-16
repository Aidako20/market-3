(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.da=factory()));
}(this,function(){'usestrict';

    varda={
        code:"da",
        week:{
            dow:1,
            doy:4//TheweekthatcontainsJan4thisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Forrige",
            next:"Næste",
            today:"Idag",
            month:"Måned",
            week:"Uge",
            day:"Dag",
            list:"Agenda"
        },
        weekLabel:"Uge",
        allDayText:"Heledagen",
        eventLimitText:"flere",
        noEventsMessage:"Ingenarrangementeratvise"
    };

    returnda;

}));
