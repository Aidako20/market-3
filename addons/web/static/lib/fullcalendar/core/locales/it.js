(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.it=factory()));
}(this,function(){'usestrict';

    varit={
        code:"it",
        week:{
            dow:1,
            doy:4//TheweekthatcontainsJan4thisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Prec",
            next:"Succ",
            today:"Oggi",
            month:"Mese",
            week:"Settimana",
            day:"Giorno",
            list:"Agenda"
        },
        weekLabel:"Sm",
        allDayHtml:"Tuttoil<br/>giorno",
        eventLimitText:function(n){
            return"+altri"+n;
        },
        noEventsMessage:"Noncisonoeventidavisualizzare"
    };

    returnit;

}));
