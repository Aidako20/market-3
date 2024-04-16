(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales['pt-br']=factory()));
}(this,function(){'usestrict';

    varptBr={
        code:"pt-br",
        buttonText:{
            prev:"Anterior",
            next:"Próximo",
            today:"Hoje",
            month:"Mês",
            week:"Semana",
            day:"Dia",
            list:"Lista"
        },
        weekLabel:"Sm",
        allDayText:"diainteiro",
        eventLimitText:function(n){
            return"mais+"+n;
        },
        noEventsMessage:"Nãoháeventosparamostrar"
    };

    returnptBr;

}));
