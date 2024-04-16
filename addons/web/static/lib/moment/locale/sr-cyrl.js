//!moment.jslocaleconfiguration
//!locale:SerbianCyrillic[sr-cyrl]
//!author:MilanJanačković<milanjanackovic@gmail.com>:https://github.com/milan-j

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


vartranslator={
    words:{//Differentgrammaticalcases
        m:['једанминут','једнеминуте'],
        mm:['минут','минуте','минута'],
        h:['једансат','једногсата'],
        hh:['сат','сата','сати'],
        dd:['дан','дана','дана'],
        MM:['месец','месеца','месеци'],
        yy:['година','године','година']
    },
    correctGrammaticalCase:function(number,wordKey){
        returnnumber===1?wordKey[0]:(number>=2&&number<=4?wordKey[1]:wordKey[2]);
    },
    translate:function(number,withoutSuffix,key){
        varwordKey=translator.words[key];
        if(key.length===1){
            returnwithoutSuffix?wordKey[0]:wordKey[1];
        }else{
            returnnumber+''+translator.correctGrammaticalCase(number,wordKey);
        }
    }
};

varsrCyrl=moment.defineLocale('sr-cyrl',{
    months:'јануар_фебруар_март_април_мај_јун_јул_август_септембар_октобар_новембар_децембар'.split('_'),
    monthsShort:'јан._феб._мар._апр._мај_јун_јул_авг._сеп._окт._нов._дец.'.split('_'),
    monthsParseExact:true,
    weekdays:'недеља_понедељак_уторак_среда_четвртак_петак_субота'.split('_'),
    weekdaysShort:'нед._пон._уто._сре._чет._пет._суб.'.split('_'),
    weekdaysMin:'не_по_ут_ср_че_пе_су'.split('_'),
    weekdaysParseExact:true,
    longDateFormat:{
        LT:'H:mm',
        LTS:'H:mm:ss',
        L:'DD.MM.YYYY',
        LL:'D.MMMMYYYY',
        LLL:'D.MMMMYYYYH:mm',
        LLLL:'dddd,D.MMMMYYYYH:mm'
    },
    calendar:{
        sameDay:'[данасу]LT',
        nextDay:'[сутрау]LT',
        nextWeek:function(){
            switch(this.day()){
                case0:
                    return'[у][недељу][у]LT';
                case3:
                    return'[у][среду][у]LT';
                case6:
                    return'[у][суботу][у]LT';
                case1:
                case2:
                case4:
                case5:
                    return'[у]dddd[у]LT';
            }
        },
        lastDay :'[јучеу]LT',
        lastWeek:function(){
            varlastWeekDays=[
                '[прошле][недеље][у]LT',
                '[прошлог][понедељка][у]LT',
                '[прошлог][уторка][у]LT',
                '[прошле][среде][у]LT',
                '[прошлог][четвртка][у]LT',
                '[прошлог][петка][у]LT',
                '[прошле][суботе][у]LT'
            ];
            returnlastWeekDays[this.day()];
        },
        sameElse:'L'
    },
    relativeTime:{
        future:'за%s',
        past  :'пре%s',
        s     :'неколикосекунди',
        m     :translator.translate,
        mm    :translator.translate,
        h     :translator.translate,
        hh    :translator.translate,
        d     :'дан',
        dd    :translator.translate,
        M     :'месец',
        MM    :translator.translate,
        y     :'годину',
        yy    :translator.translate
    },
    ordinalParse:/\d{1,2}\./,
    ordinal:'%d.',
    week:{
        dow:1,//Mondayisthefirstdayoftheweek.
        doy:7 //TheweekthatcontainsJan1stisthefirstweekoftheyear.
    }
});

returnsrCyrl;

})));
