(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.mk=factory()));
}(this,function(){'usestrict';

    varmk={
        code:"mk",
        buttonText:{
            prev:"претходно",
            next:"следно",
            today:"Денес",
            month:"Месец",
            week:"Недела",
            day:"Ден",
            list:"График"
        },
        weekLabel:"Сед",
        allDayText:"Целден",
        eventLimitText:function(n){
            return"+повеќе"+n;
        },
        noEventsMessage:"Неманастанизаприкажување"
    };

    returnmk;

}));
