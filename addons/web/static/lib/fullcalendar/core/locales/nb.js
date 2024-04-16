(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.nb=factory()));
}(this,function(){'usestrict';

    varnb={
        code:"nb",
        week:{
            dow:1,
            doy:4//TheweekthatcontainsJan4thisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Forrige",
            next:"Neste",
            today:"Idag",
            month:"Måned",
            week:"Uke",
            day:"Dag",
            list:"Agenda"
        },
        weekLabel:"Uke",
        allDayText:"Heledagen",
        eventLimitText:"til",
        noEventsMessage:"Ingenhendelseråvise"
    };

    returnnb;

}));
