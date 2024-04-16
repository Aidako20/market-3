(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.eu=factory()));
}(this,function(){'usestrict';

    vareu={
        code:"eu",
        week:{
            dow:1,
            doy:7//TheweekthatcontainsJan1stisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Aur",
            next:"Hur",
            today:"Gaur",
            month:"Hilabetea",
            week:"Astea",
            day:"Eguna",
            list:"Agenda"
        },
        weekLabel:"As",
        allDayHtml:"Egun<br/>osoa",
        eventLimitText:"gehiago",
        noEventsMessage:"Ezdagoekitaldirikerakusteko"
    };

    returneu;

}));
