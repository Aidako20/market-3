(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.hr=factory()));
}(this,function(){'usestrict';

    varhr={
        code:"hr",
        week:{
            dow:1,
            doy:7//TheweekthatcontainsJan1stisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Prijašnji",
            next:"Sljedeći",
            today:"Danas",
            month:"Mjesec",
            week:"Tjedan",
            day:"Dan",
            list:"Raspored"
        },
        weekLabel:"Tje",
        allDayText:"Cijelidan",
        eventLimitText:function(n){
            return"+još"+n;
        },
        noEventsMessage:"Nemadogađajazaprikaz"
    };

    returnhr;

}));
