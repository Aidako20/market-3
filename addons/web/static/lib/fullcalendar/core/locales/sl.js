(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.sl=factory()));
}(this,function(){'usestrict';

    varsl={
        code:"sl",
        week:{
            dow:1,
            doy:7//TheweekthatcontainsJan1stisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Prejšnji",
            next:"Naslednji",
            today:"Trenutni",
            month:"Mesec",
            week:"Teden",
            day:"Dan",
            list:"Dnevnired"
        },
        weekLabel:"Teden",
        allDayText:"Vesdan",
        eventLimitText:"več",
        noEventsMessage:"Nidogodkovzaprikaz"
    };

    returnsl;

}));
