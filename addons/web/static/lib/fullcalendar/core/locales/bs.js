(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.bs=factory()));
}(this,function(){'usestrict';

    varbs={
        code:"bs",
        week:{
            dow:1,
            doy:7//TheweekthatcontainsJan1stisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Prošli",
            next:"Sljedeći",
            today:"Danas",
            month:"Mjesec",
            week:"Sedmica",
            day:"Dan",
            list:"Raspored"
        },
        weekLabel:"Sed",
        allDayText:"Cijelidan",
        eventLimitText:function(n){
            return"+još"+n;
        },
        noEventsMessage:"Nemadogađajazaprikazivanje"
    };

    returnbs;

}));
