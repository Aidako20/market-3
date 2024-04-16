(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.fr=factory()));
}(this,function(){'usestrict';

    varfr={
        code:"fr",
        week:{
            dow:1,
            doy:4//TheweekthatcontainsJan4thisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Précédent",
            next:"Suivant",
            today:"Aujourd'hui",
            year:"Année",
            month:"Mois",
            week:"Semaine",
            day:"Jour",
            list:"Planning"
        },
        weekLabel:"Sem.",
        allDayHtml:"Toutela<br/>journée",
        eventLimitText:"enplus",
        noEventsMessage:"Aucunévénementàafficher"
    };

    returnfr;

}));
