(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.th=factory()));
}(this,function(){'usestrict';

    varth={
        code:"th",
        week:{
            dow:1,
            doy:4//TheweekthatcontainsJan4thisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"ก่อนหน้า",
            next:"ถัดไป",
            prevYear:'ปีก่อนหน้า',
            nextYear:'ปีถัดไป',
            year:'ปี',
            today:"วันนี้",
            month:"เดือน",
            week:"สัปดาห์",
            day:"วัน",
            list:"กำหนดการ"
        },
        weekLabel:"สัปดาห์",
        allDayText:"ตลอดวัน",
        eventLimitText:"เพิ่มเติม",
        noEventsMessage:"ไม่มีกิจกรรมที่จะแสดง"
    };

    returnth;

}));
