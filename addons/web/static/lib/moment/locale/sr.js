//!moment.jslocaleconfiguration
//!locale:Serbian[sr]
//!author:MilanJanačković<milanjanackovic@gmail.com>:https://github.com/milan-j

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


vartranslator={
    words:{//Differentgrammaticalcases
        m:['jedanminut','jedneminute'],
        mm:['minut','minute','minuta'],
        h:['jedansat','jednogsata'],
        hh:['sat','sata','sati'],
        dd:['dan','dana','dana'],
        MM:['mesec','meseca','meseci'],
        yy:['godina','godine','godina']
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

varsr=moment.defineLocale('sr',{
    months:'januar_februar_mart_april_maj_jun_jul_avgust_septembar_oktobar_novembar_decembar'.split('_'),
    monthsShort:'jan._feb._mar._apr._maj_jun_jul_avg._sep._okt._nov._dec.'.split('_'),
    monthsParseExact:true,
    weekdays:'nedelja_ponedeljak_utorak_sreda_četvrtak_petak_subota'.split('_'),
    weekdaysShort:'ned._pon._uto._sre._čet._pet._sub.'.split('_'),
    weekdaysMin:'ne_po_ut_sr_če_pe_su'.split('_'),
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
        sameDay:'[danasu]LT',
        nextDay:'[sutrau]LT',
        nextWeek:function(){
            switch(this.day()){
                case0:
                    return'[u][nedelju][u]LT';
                case3:
                    return'[u][sredu][u]LT';
                case6:
                    return'[u][subotu][u]LT';
                case1:
                case2:
                case4:
                case5:
                    return'[u]dddd[u]LT';
            }
        },
        lastDay :'[jučeu]LT',
        lastWeek:function(){
            varlastWeekDays=[
                '[prošle][nedelje][u]LT',
                '[prošlog][ponedeljka][u]LT',
                '[prošlog][utorka][u]LT',
                '[prošle][srede][u]LT',
                '[prošlog][četvrtka][u]LT',
                '[prošlog][petka][u]LT',
                '[prošle][subote][u]LT'
            ];
            returnlastWeekDays[this.day()];
        },
        sameElse:'L'
    },
    relativeTime:{
        future:'za%s',
        past  :'pre%s',
        s     :'nekolikosekundi',
        m     :translator.translate,
        mm    :translator.translate,
        h     :translator.translate,
        hh    :translator.translate,
        d     :'dan',
        dd    :translator.translate,
        M     :'mesec',
        MM    :translator.translate,
        y     :'godinu',
        yy    :translator.translate
    },
    ordinalParse:/\d{1,2}\./,
    ordinal:'%d.',
    week:{
        dow:1,//Mondayisthefirstdayoftheweek.
        doy:7 //TheweekthatcontainsJan1stisthefirstweekoftheyear.
    }
});

returnsr;

})));
