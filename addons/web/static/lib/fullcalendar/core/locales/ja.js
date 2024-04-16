(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.ja=factory()));
}(this,function(){'usestrict';

    varja={
        code:"ja",
        buttonText:{
            prev:"前",
            next:"次",
            today:"今日",
            month:"月",
            week:"週",
            day:"日",
            list:"予定リスト"
        },
        weekLabel:"週",
        allDayText:"終日",
        eventLimitText:function(n){
            return"他"+n+"件";
        },
        noEventsMessage:"表示する予定はありません"
    };

    returnja;

}));
