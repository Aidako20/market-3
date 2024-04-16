(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales['es-us']=factory()));
}(this,function(){'usestrict';

    varesUs={
        code:"es",
        week:{
            dow:0,
            doy:6//TheweekthatcontainsJan1stisthefirstweekoftheyear.
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

    returnesUs;

}));
