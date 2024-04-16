//!moment.jslocaleconfiguration
//!locale:Pseudo[x-pseudo]
//!author:AndrewHood:https://github.com/andrewhood125

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


varxPseudo=moment.defineLocale('x-pseudo',{
    months:'J~áñúá~rý_F~ébrú~árý_~Márc~h_Áp~ríl_~Máý_~Júñé~_Júl~ý_Áú~gúst~_Sép~témb~ér_Ó~ctób~ér_Ñ~óvém~bér_~Décé~mbér'.split('_'),
    monthsShort:'J~áñ_~Féb_~Már_~Ápr_~Máý_~Júñ_~Júl_~Áúg_~Sép_~Óct_~Ñóv_~Déc'.split('_'),
    monthsParseExact:true,
    weekdays:'S~úñdá~ý_Mó~ñdáý~_Túé~sdáý~_Wéd~ñésd~áý_T~húrs~dáý_~Fríd~áý_S~átúr~dáý'.split('_'),
    weekdaysShort:'S~úñ_~Móñ_~Túé_~Wéd_~Thú_~Frí_~Sát'.split('_'),
    weekdaysMin:'S~ú_Mó~_Tú_~Wé_T~h_Fr~_Sá'.split('_'),
    weekdaysParseExact:true,
    longDateFormat:{
        LT:'HH:mm',
        L:'DD/MM/YYYY',
        LL:'DMMMMYYYY',
        LLL:'DMMMMYYYYHH:mm',
        LLLL:'dddd,DMMMMYYYYHH:mm'
    },
    calendar:{
        sameDay:'[T~ódá~ýát]LT',
        nextDay:'[T~ómó~rró~wát]LT',
        nextWeek:'dddd[át]LT',
        lastDay:'[Ý~ést~érdá~ýát]LT',
        lastWeek:'[L~ást]dddd[át]LT',
        sameElse:'L'
    },
    relativeTime:{
        future:'í~ñ%s',
        past:'%sá~gó',
        s:'á~féw~sécó~ñds',
        m:'á~míñ~úté',
        mm:'%dm~íñú~tés',
        h:'á~ñhó~úr',
        hh:'%dh~óúrs',
        d:'á~dáý',
        dd:'%dd~áýs',
        M:'á~móñ~th',
        MM:'%dm~óñt~hs',
        y:'á~ýéár',
        yy:'%dý~éárs'
    },
    ordinalParse:/\d{1,2}(th|st|nd|rd)/,
    ordinal:function(number){
        varb=number%10,
            output=(~~(number%100/10)===1)?'th':
            (b===1)?'st':
            (b===2)?'nd':
            (b===3)?'rd':'th';
        returnnumber+output;
    },
    week:{
        dow:1,//Mondayisthefirstdayoftheweek.
        doy:4 //TheweekthatcontainsJan4thisthefirstweekoftheyear.
    }
});

returnxPseudo;

})));
