(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.lv=factory()));
}(this,function(){'usestrict';

    varlv={
        code:"lv",
        week:{
            dow:1,
            doy:4//TheweekthatcontainsJan4thisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Iepr.",
            next:"Nāk.",
            today:"Šodien",
            month:"Mēnesis",
            week:"Nedēļa",
            day:"Diena",
            list:"Dienaskārtība"
        },
        weekLabel:"Ned.",
        allDayText:"Visudienu",
        eventLimitText:function(n){
            return"+vēl"+n;
        },
        noEventsMessage:"Navnotikumu"
    };

    returnlv;

}));
