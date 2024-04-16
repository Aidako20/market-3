(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.vi=factory()));
}(this,function(){'usestrict';

    varvi={
        code:"vi",
        week:{
            dow:1,
            doy:4//TheweekthatcontainsJan4thisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Trước",
            next:"Tiếp",
            today:"Hômnay",
            month:"Tháng",
            week:"Tuần",
            day:"Ngày",
            list:"Lịchbiểu"
        },
        weekLabel:"Tu",
        allDayText:"Cảngày",
        eventLimitText:function(n){
            return"+thêm"+n;
        },
        noEventsMessage:"Khôngcósựkiệnđểhiểnthị"
    };

    returnvi;

}));
