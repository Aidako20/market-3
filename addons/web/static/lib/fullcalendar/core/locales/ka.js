(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.ka=factory()));
}(this,function(){'usestrict';

    varka={
        code:"ka",
        week:{
            dow:1,
            doy:7
        },
        buttonText:{
            prev:"წინა",
            next:"შემდეგი",
            today:"დღეს",
            month:"თვე",
            week:"კვირა",
            day:"დღე",
            list:"დღისწესრიგი"
        },
        weekLabel:"კვ",
        allDayText:"მთელიდღე",
        eventLimitText:function(n){
            return"+კიდევ"+n;
        },
        noEventsMessage:"ღონისძიებებიარარის"
    };

    returnka;

}));
