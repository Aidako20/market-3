(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.fa=factory()));
}(this,function(){'usestrict';

    varfa={
        code:"fa",
        week:{
            dow:6,
            doy:12//TheweekthatcontainsJan1stisthefirstweekoftheyear.
        },
        dir:'rtl',
        buttonText:{
            prev:"قبلی",
            next:"بعدی",
            today:"امروز",
            month:"ماه",
            week:"هفته",
            day:"روز",
            list:"برنامه"
        },
        weekLabel:"هف",
        allDayText:"تمامروز",
        eventLimitText:function(n){
            return"بیشاز"+n;
        },
        noEventsMessage:"هیچرویدادیبهنمایش"
    };

    returnfa;

}));
