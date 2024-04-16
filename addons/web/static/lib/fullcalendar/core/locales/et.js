(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.et=factory()));
}(this,function(){'usestrict';

    varet={
        code:"et",
        week:{
            dow:1,
            doy:4//TheweekthatcontainsJan4thisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Eelnev",
            next:"Järgnev",
            today:"Täna",
            month:"Kuu",
            week:"Nädal",
            day:"Päev",
            list:"Päevakord"
        },
        weekLabel:"näd",
        allDayText:"Kogupäev",
        eventLimitText:function(n){
            return"+veel"+n;
        },
        noEventsMessage:"Kuvamisekspuuduvadsündmused"
    };

    returnet;

}));
