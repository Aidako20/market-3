(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales['fr-ch']=factory()));
}(this,function(){'usestrict';

    varfrCh={
        code:"fr-ch",
        week:{
            dow:1,
            doy:4//TheweekthatcontainsJan4thisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Précédent",
            next:"Suivant",
            today:"Courant",
            year:"Année",
            month:"Mois",
            week:"Semaine",
            day:"Jour",
            list:"Monplanning"
        },
        weekLabel:"Sm",
        allDayHtml:"Toutela<br/>journée",
        eventLimitText:"enplus",
        noEventsMessage:"Aucunévénementàafficher"
    };

    returnfrCh;

}));
