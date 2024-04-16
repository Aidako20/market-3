(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.id=factory()));
}(this,function(){'usestrict';

    varid={
        code:"id",
        week:{
            dow:1,
            doy:7//TheweekthatcontainsJan1stisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"mundur",
            next:"maju",
            today:"hariini",
            month:"Bulan",
            week:"Minggu",
            day:"Hari",
            list:"Agenda"
        },
        weekLabel:"Mg",
        allDayHtml:"Sehari<br/>penuh",
        eventLimitText:"lebih",
        noEventsMessage:"Tidakadaacarauntukditampilkan"
    };

    returnid;

}));
