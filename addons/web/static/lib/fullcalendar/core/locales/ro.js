(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.ro=factory()));
}(this,function(){'usestrict';

    varro={
        code:"ro",
        week:{
            dow:1,
            doy:7//TheweekthatcontainsJan1stisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"precedentă",
            next:"următoare",
            today:"Azi",
            month:"Lună",
            week:"Săptămână",
            day:"Zi",
            list:"Agendă"
        },
        weekLabel:"Săpt",
        allDayText:"Toatăziua",
        eventLimitText:function(n){
            return"+alte"+n;
        },
        noEventsMessage:"Nuexistăevenimentedeafișat"
    };

    returnro;

}));
