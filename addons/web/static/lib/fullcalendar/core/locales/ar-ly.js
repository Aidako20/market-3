(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales['ar-ly']=factory()));
}(this,function(){'usestrict';

    vararLy={
        code:"ar-ly",
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

    returnarLy;

}));
