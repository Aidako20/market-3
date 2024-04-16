(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.sk=factory()));
}(this,function(){'usestrict';

    varsk={
        code:"sk",
        week:{
            dow:1,
            doy:4//TheweekthatcontainsJan4thisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Predchádzajúci",
            next:"Nasledujúci",
            today:"Dnes",
            month:"Mesiac",
            week:"Týždeň",
            day:"Deň",
            list:"Rozvrh"
        },
        weekLabel:"Ty",
        allDayText:"Celýdeň",
        eventLimitText:function(n){
            return"+ďalšie:"+n;
        },
        noEventsMessage:"Žiadneakcienazobrazenie"
    };

    returnsk;

}));
