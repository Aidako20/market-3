(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.kk=factory()));
}(this,function(){'usestrict';

    varkk={
        code:"kk",
        week:{
            dow:1,
            doy:7//TheweekthatcontainsJan1stisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Алдыңғы",
            next:"Келесі",
            today:"Бүгін",
            month:"Ай",
            week:"Апта",
            day:"Күн",
            list:"Күнтәртібі"
        },
        weekLabel:"Не",
        allDayText:"Күнібойы",
        eventLimitText:function(n){
            return"+тағы"+n;
        },
        noEventsMessage:"Көрсетуүшіноқиғаларжоқ"
    };

    returnkk;

}));
