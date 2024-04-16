(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.uk=factory()));
}(this,function(){'usestrict';

    varuk={
        code:"uk",
        week:{
            dow:1,
            doy:7//TheweekthatcontainsJan1stisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Попередній",
            next:"далі",
            today:"Сьогодні",
            month:"Місяць",
            week:"Тиждень",
            day:"День",
            list:"Порядокденний"
        },
        weekLabel:"Тиж",
        allDayText:"Увесьдень",
        eventLimitText:function(n){
            return"+ще"+n+"...";
        },
        noEventsMessage:"Немаєподійдлявідображення"
    };

    returnuk;

}));
