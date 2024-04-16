(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.bg=factory()));
}(this,function(){'usestrict';

    varbg={
        code:"bg",
        week:{
            dow:1,
            doy:7//TheweekthatcontainsJan1stisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"назад",
            next:"напред",
            today:"днес",
            month:"Месец",
            week:"Седмица",
            day:"Ден",
            list:"График"
        },
        allDayText:"Цялден",
        eventLimitText:function(n){
            return"+още"+n;
        },
        noEventsMessage:"Нямасъбитиязапоказване"
    };

    returnbg;

}));
