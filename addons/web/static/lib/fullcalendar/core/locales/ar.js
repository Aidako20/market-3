(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.ar=factory()));
}(this,function(){'usestrict';

    varar={
        code:"ar",
        week:{
            dow:6,
            doy:12//TheweekthatcontainsJan1stisthefirstweekoftheyear.
        },
        dir:'rtl',
        buttonText:{
            prev:"السابق",
            next:"التالي",
            today:"اليوم",
            month:"شهر",
            week:"أسبوع",
            day:"يوم",
            list:"أجندة"
        },
        weekLabel:"أسبوع",
        allDayText:"اليومكله",
        eventLimitText:"أخرى",
        noEventsMessage:"أيأحداثلعرض"
    };

    returnar;

}));
