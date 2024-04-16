(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.pt=factory()));
}(this,function(){'usestrict';

    varpt={
        code:"pt",
        week:{
            dow:1,
            doy:4//TheweekthatcontainsJan4thisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Anterior",
            next:"Seguinte",
            today:"Hoje",
            month:"Mês",
            week:"Semana",
            day:"Dia",
            list:"Agenda"
        },
        weekLabel:"Sem",
        allDayText:"Todoodia",
        eventLimitText:"mais",
        noEventsMessage:"Nãoháeventosparamostrar"
    };

    returnpt;

}));
