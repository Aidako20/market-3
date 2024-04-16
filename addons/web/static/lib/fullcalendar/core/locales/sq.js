(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.sq=factory()));
}(this,function(){'usestrict';

    varsq={
        code:"sq",
        week:{
            dow:1,
            doy:4//TheweekthatcontainsJan4thisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"mbrapa",
            next:"Përpara",
            today:"sot",
            month:"Muaj",
            week:"Javë",
            day:"Ditë",
            list:"Listë"
        },
        weekLabel:"Ja",
        allDayHtml:"Gjithë<br/>ditën",
        eventLimitText:function(n){
            return"+mëtepër"+n;
        },
        noEventsMessage:"Nukkaeventepërtëshfaqur"
    };

    returnsq;

}));
