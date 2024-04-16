(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales['sr-cyrl']=factory()));
}(this,function(){'usestrict';

    varsrCyrl={
        code:"sr-cyrl",
        week:{
            dow:1,
            doy:7//TheweekthatcontainsJan1stisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Претходна",
            next:"следећи",
            today:"Данас",
            month:"Месец",
            week:"Недеља",
            day:"Дан",
            list:"Планер"
        },
        weekLabel:"Сед",
        allDayText:"Цеодан",
        eventLimitText:function(n){
            return"+још"+n;
        },
        noEventsMessage:"Немадогађајазаприказ"
    };

    returnsrCyrl;

}));
