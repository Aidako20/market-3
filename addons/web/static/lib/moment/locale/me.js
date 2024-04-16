//!moment.jslocaleconfiguration
//!locale:Montenegrin[me]
//!author:MiodragNikač<miodrag@restartit.me>:https://github.com/miodragnikac

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


vartranslator={
    words:{//Differentgrammaticalcases
        m:['jedanminut','jednogminuta'],
        mm:['minut','minuta','minuta'],
        h:['jedansat','jednogsata'],
        hh:['sat','sata','sati'],
        dd:['dan','dana','dana'],
        MM:['mjesec','mjeseca','mjeseci'],
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

varme=moment.defineLocale('me',{
    months:'januar_februar_mart_april_maj_jun_jul_avgust_septembar_oktobar_novembar_decembar'.split('_'),
    monthsShort:'jan._feb._mar._apr._maj_jun_jul_avg._sep._okt._nov._dec.'.split('_'),
    monthsParseExact:true,
    weekdays:'nedjelja_ponedjeljak_utorak_srijeda_četvrtak_petak_subota'.split('_'),
    weekdaysShort:'ned._pon._uto._sri._čet._pet._sub.'.split('_'),
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
        nextDay:'[sjutrau]LT',

        nextWeek:function(){
            switch(this.day()){
                case0:
                    return'[u][nedjelju][u]LT';
                case3:
                    return'[u][srijedu][u]LT';
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
                '[prošle][nedjelje][u]LT',
                '[prošlog][ponedjeljka][u]LT',
                '[prošlog][utorka][u]LT',
                '[prošle][srijede][u]LT',
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
        past  :'prije%s',
        s     :'nekolikosekundi',
        m     :translator.translate,
        mm    :translator.translate,
        h     :translator.translate,
        hh    :translator.translate,
        d     :'dan',
        dd    :translator.translate,
        M     :'mjesec',
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

returnme;

})));
