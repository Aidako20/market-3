(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.fi=factory()));
}(this,function(){'usestrict';

    varfi={
        code:"fi",
        week:{
            dow:1,
            doy:4//TheweekthatcontainsJan4thisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Edellinen",
            next:"Seuraava",
            today:"Tänään",
            month:"Kuukausi",
            week:"Viikko",
            day:"Päivä",
            list:"Tapahtumat"
        },
        weekLabel:"Vk",
        allDayText:"Kokopäivä",
        eventLimitText:"lisää",
        noEventsMessage:"Einäytettäviätapahtumia"
    };

    returnfi;

}));
