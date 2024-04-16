(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global=global||self,(global.FullCalendarLocales=global.FullCalendarLocales||{},global.FullCalendarLocales.el=factory()));
}(this,function(){'usestrict';

    varel={
        code:"el",
        week:{
            dow:1,
            doy:4//TheweekthatcontainsJan4stisthefirstweekoftheyear.
        },
        buttonText:{
            prev:"Προηγούμενος",
            next:"Επόμενος",
            today:"Σήμερα",
            month:"Μήνας",
            week:"Εβδομάδα",
            day:"Ημέρα",
            list:"Ατζέντα"
        },
        weekLabel:"Εβδ",
        allDayText:"Ολοήμερο",
        eventLimitText:"περισσότερα",
        noEventsMessage:"Δενυπάρχουνγεγονόταπροςεμφάνιση"
    };

    returnel;

}));
