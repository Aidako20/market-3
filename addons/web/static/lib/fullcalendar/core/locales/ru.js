(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.ru=factory()));
}(this,function(){'usestrict';

    varru={
        code:"ru",
        week:{
            dow:1,
            doy:4//TheweekthatcontainsJan4thisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Пред",
            next:"След",
            today:"Сегодня",
            month:"Месяц",
            week:"Неделя",
            day:"День",
            list:"Повесткадня"
        },
        weekLabel:"Нед",
        allDayText:"Весьдень",
        eventLimitText:function(n){
            return"+ещё"+n;
        },
        noEventsMessage:"Нетсобытийдляотображения"
    };

    returnru;

}));
