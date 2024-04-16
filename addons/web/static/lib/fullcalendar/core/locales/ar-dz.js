(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales['ar-dz']=factory()));
}(this,function(){'usestrict';

    vararDz={
        code:"ar-dz",
        week:{
            dow:0,
            doy:4//TheweekthatcontainsJan1stisthefirstweekoftheyear.
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

    returnarDz;

}));
