(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales['fr-ca']=factory()));
}(this,function(){'usestrict';

    varfrCa={
        code:"fr",
        buttonText:{
            prev:"Précédent",
            next:"Suivant",
            today:"Aujourd'hui",
            year:"Année",
            month:"Mois",
            week:"Semaine",
            day:"Jour",
            list:"Monplanning"
        },
        weekLabel:"Sem.",
        allDayHtml:"Toutela<br/>journée",
        eventLimitText:"enplus",
        noEventsMessage:"Aucunévénementàafficher"
    };

    returnfrCa;

}));
