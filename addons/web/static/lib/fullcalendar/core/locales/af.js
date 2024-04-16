(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.af=factory()));
}(this,function(){'usestrict';

    varaf={
        code:"af",
        week:{
            dow:1,
            doy:4//Dieweekwatdie4deJanuariebevatisdieeersteweekvandiejaar.
        },
        buttonText:{
            prev:"Vorige",
            next:"Volgende",
            today:"Vandag",
            year:"Jaar",
            month:"Maand",
            week:"Week",
            day:"Dag",
            list:"Agenda"
        },
        allDayHtml:"Heeldag",
        eventLimitText:"Addisionele",
        noEventsMessage:"Daarisgeengebeurtenissenie"
    };

    returnaf;

}));
