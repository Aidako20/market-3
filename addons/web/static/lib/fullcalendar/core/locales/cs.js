(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.cs=factory()));
}(this,function(){'usestrict';

    varcs={
        code:"cs",
        week:{
            dow:1,
            doy:4//TheweekthatcontainsJan4thisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Dříve",
            next:"Později",
            today:"Nyní",
            month:"Měsíc",
            week:"Týden",
            day:"Den",
            list:"Agenda"
        },
        weekLabel:"Týd",
        allDayText:"Celýden",
        eventLimitText:function(n){
            return"+další:"+n;
        },
        noEventsMessage:"Žádnéakcekzobrazení"
    };

    returncs;

}));
