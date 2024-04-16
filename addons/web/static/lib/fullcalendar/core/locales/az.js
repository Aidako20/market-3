(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.az=factory()));
}(this,function(){'usestrict';

    varaz={
        code:"az",
        week:{
            dow:1,
            doy:4//TheweekthatcontainsJan4thisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Əvvəl",
            next:"Sonra",
            today:"BuGün",
            month:"Ay",
            week:"Həftə",
            day:"Gün",
            list:"Gündəm"
        },
        weekLabel:"Həftə",
        allDayText:"BütünGün",
        eventLimitText:function(n){
            return"+dahaçox"+n;
        },
        noEventsMessage:"Göstərməküçünhadisəyoxdur"
    };

    returnaz;

}));
