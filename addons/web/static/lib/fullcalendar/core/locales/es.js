(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.es=factory()));
}(this,function(){'usestrict';

    vares={
        code:"es",
        week:{
            dow:1,
            doy:4//TheweekthatcontainsJan4thisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Ant",
            next:"Sig",
            today:"Hoy",
            month:"Mes",
            week:"Semana",
            day:"Día",
            list:"Agenda"
        },
        weekLabel:"Sm",
        allDayHtml:"Todo<br/>eldía",
        eventLimitText:"más",
        noEventsMessage:"Nohayeventosparamostrar"
    };

    returnes;

}));
