(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.ca=factory()));
}(this,function(){'usestrict';

    varca={
        code:"ca",
        week:{
            dow:1,
            doy:4//TheweekthatcontainsJan4thisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Anterior",
            next:"Següent",
            today:"Avui",
            month:"Mes",
            week:"Setmana",
            day:"Dia",
            list:"Agenda"
        },
        weekLabel:"Set",
        allDayText:"Toteldia",
        eventLimitText:"més",
        noEventsMessage:"Nohihaesdevenimentspermostrar"
    };

    returnca;

}));
