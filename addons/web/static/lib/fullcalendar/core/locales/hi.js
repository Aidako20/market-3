(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.hi=factory()));
}(this,function(){'usestrict';

    varhi={
        code:"hi",
        week:{
            dow:0,
            doy:6//TheweekthatcontainsJan1stisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"पिछला",
            next:"अगला",
            today:"आज",
            month:"महीना",
            week:"सप्ताह",
            day:"दिन",
            list:"कार्यसूची"
        },
        weekLabel:"हफ्ता",
        allDayText:"सभीदिन",
        eventLimitText:function(n){
            return"+अधिक"+n;
        },
        noEventsMessage:"कोईघटनाओंकोप्रदर्शितकरनेकेलिए"
    };

    returnhi;

}));
