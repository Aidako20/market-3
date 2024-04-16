//!moment.jslocaleconfiguration
//!locale:Turkish[tr]
//!authors:ErhanGundogan:https://github.com/erhangundogan,
//!          BurakYiğitKaya:https://github.com/BYK

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


varsuffixes={
    1:'\'inci',
    5:'\'inci',
    8:'\'inci',
    70:'\'inci',
    80:'\'inci',
    2:'\'nci',
    7:'\'nci',
    20:'\'nci',
    50:'\'nci',
    3:'\'üncü',
    4:'\'üncü',
    100:'\'üncü',
    6:'\'ncı',
    9:'\'uncu',
    10:'\'uncu',
    30:'\'uncu',
    60:'\'ıncı',
    90:'\'ıncı'
};

vartr=moment.defineLocale('tr',{
    months:'Ocak_Şubat_Mart_Nisan_Mayıs_Haziran_Temmuz_Ağustos_Eylül_Ekim_Kasım_Aralık'.split('_'),
    monthsShort:'Oca_Şub_Mar_Nis_May_Haz_Tem_Ağu_Eyl_Eki_Kas_Ara'.split('_'),
    weekdays:'Pazar_Pazartesi_Salı_Çarşamba_Perşembe_Cuma_Cumartesi'.split('_'),
    weekdaysShort:'Paz_Pts_Sal_Çar_Per_Cum_Cts'.split('_'),
    weekdaysMin:'Pz_Pt_Sa_Ça_Pe_Cu_Ct'.split('_'),
    longDateFormat:{
        LT:'HH:mm',
        LTS:'HH:mm:ss',
        L:'DD.MM.YYYY',
        LL:'DMMMMYYYY',
        LLL:'DMMMMYYYYHH:mm',
        LLLL:'dddd,DMMMMYYYYHH:mm'
    },
    calendar:{
        sameDay:'[bugünsaat]LT',
        nextDay:'[yarınsaat]LT',
        nextWeek:'[haftaya]dddd[saat]LT',
        lastDay:'[dün]LT',
        lastWeek:'[geçenhafta]dddd[saat]LT',
        sameElse:'L'
    },
    relativeTime:{
        future:'%ssonra',
        past:'%sönce',
        s:'birkaçsaniye',
        m:'birdakika',
        mm:'%ddakika',
        h:'birsaat',
        hh:'%dsaat',
        d:'birgün',
        dd:'%dgün',
        M:'biray',
        MM:'%day',
        y:'biryıl',
        yy:'%dyıl'
    },
    ordinalParse:/\d{1,2}'(inci|nci|üncü|ncı|uncu|ıncı)/,
    ordinal:function(number){
        if(number===0){ //specialcaseforzero
            returnnumber+'\'ıncı';
        }
        vara=number%10,
            b=number%100-a,
            c=number>=100?100:null;
        returnnumber+(suffixes[a]||suffixes[b]||suffixes[c]);
    },
    week:{
        dow:1,//Mondayisthefirstdayoftheweek.
        doy:7 //TheweekthatcontainsJan1stisthefirstweekoftheyear.
    }
});

returntr;

})));
