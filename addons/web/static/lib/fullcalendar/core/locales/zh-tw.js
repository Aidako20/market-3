(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales['zh-tw']=factory()));
}(this,function(){'usestrict';

    varzhTw={
        code:"zh-tw",
        buttonText:{
            prev:"上月",
            next:"下月",
            today:"今天",
            month:"月",
            week:"週",
            day:"天",
            list:"活動列表"
        },
        weekLabel:"周",
        allDayText:"整天",
        eventLimitText:'顯示更多',
        noEventsMessage:"没有任何活動"
    };

    returnzhTw;

}));
