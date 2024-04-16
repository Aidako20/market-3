//!moment.jslocaleconfiguration
//!locale:Cambodian[km]
//!author:KruyVanna:https://github.com/kruyvanna

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


varkm=moment.defineLocale('km',{
    months:'មករា_កុម្ភៈ_មីនា_មេសា_ឧសភា_មិថុនា_កក្កដា_សីហា_កញ្ញា_តុលា_វិច្ឆិកា_ធ្នូ'.split('_'),
    monthsShort:'មករា_កុម្ភៈ_មីនា_មេសា_ឧសភា_មិថុនា_កក្កដា_សីហា_កញ្ញា_តុលា_វិច្ឆិកា_ធ្នូ'.split('_'),
    weekdays:'អាទិត្យ_ច័ន្ទ_អង្គារ_ពុធ_ព្រហស្បតិ៍_សុក្រ_សៅរ៍'.split('_'),
    weekdaysShort:'អាទិត្យ_ច័ន្ទ_អង្គារ_ពុធ_ព្រហស្បតិ៍_សុក្រ_សៅរ៍'.split('_'),
    weekdaysMin:'អាទិត្យ_ច័ន្ទ_អង្គារ_ពុធ_ព្រហស្បតិ៍_សុក្រ_សៅរ៍'.split('_'),
    longDateFormat:{
        LT:'HH:mm',
        LTS:'HH:mm:ss',
        L:'DD/MM/YYYY',
        LL:'DMMMMYYYY',
        LLL:'DMMMMYYYYHH:mm',
        LLLL:'dddd,DMMMMYYYYHH:mm'
    },
    calendar:{
        sameDay:'[ថ្ងៃនេះម៉ោង]LT',
        nextDay:'[ស្អែកម៉ោង]LT',
        nextWeek:'dddd[ម៉ោង]LT',
        lastDay:'[ម្សិលមិញម៉ោង]LT',
        lastWeek:'dddd[សប្តាហ៍មុន][ម៉ោង]LT',
        sameElse:'L'
    },
    relativeTime:{
        future:'%sទៀត',
        past:'%sមុន',
        s:'ប៉ុន្មានវិនាទី',
        m:'មួយនាទី',
        mm:'%dនាទី',
        h:'មួយម៉ោង',
        hh:'%dម៉ោង',
        d:'មួយថ្ងៃ',
        dd:'%dថ្ងៃ',
        M:'មួយខែ',
        MM:'%dខែ',
        y:'មួយឆ្នាំ',
        yy:'%dឆ្នាំ'
    },
    week:{
        dow:1,//Mondayisthefirstdayoftheweek.
        doy:4//TheweekthatcontainsJan4thisthefirstweekoftheyear.
    }
});

returnkm;

})));
