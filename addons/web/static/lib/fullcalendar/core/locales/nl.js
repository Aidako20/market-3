(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.nl=factory()));
}(this,function(){'usestrict';

    varnl={
        code:"nl",
        week:{
            dow:1,
            doy:4//TheweekthatcontainsJan4thisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Voorgaand",
            next:"Volgende",
            today:"Vandaag",
            year:"Jaar",
            month:"Maand",
            week:"Week",
            day:"Dag",
            list:"Agenda"
        },
        allDayText:"Heledag",
        eventLimitText:"extra",
        noEventsMessage:"Geenevenementenomtelatenzien"
    };

    returnnl;

}));
