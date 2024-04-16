//!moment.jslocaleconfiguration
//!locale:Malay[ms-my]
//!note:DEPRECATED,thecorrectoneis[ms]
//!author:WeldanJamili:https://github.com/weldan

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


varmsMy=moment.defineLocale('ms-my',{
    months:'Januari_Februari_Mac_April_Mei_Jun_Julai_Ogos_September_Oktober_November_Disember'.split('_'),
    monthsShort:'Jan_Feb_Mac_Apr_Mei_Jun_Jul_Ogs_Sep_Okt_Nov_Dis'.split('_'),
    weekdays:'Ahad_Isnin_Selasa_Rabu_Khamis_Jumaat_Sabtu'.split('_'),
    weekdaysShort:'Ahd_Isn_Sel_Rab_Kha_Jum_Sab'.split('_'),
    weekdaysMin:'Ah_Is_Sl_Rb_Km_Jm_Sb'.split('_'),
    longDateFormat:{
        LT:'HH.mm',
        LTS:'HH.mm.ss',
        L:'DD/MM/YYYY',
        LL:'DMMMMYYYY',
        LLL:'DMMMMYYYY[pukul]HH.mm',
        LLLL:'dddd,DMMMMYYYY[pukul]HH.mm'
    },
    meridiemParse:/pagi|tengahari|petang|malam/,
    meridiemHour:function(hour,meridiem){
        if(hour===12){
            hour=0;
        }
        if(meridiem==='pagi'){
            returnhour;
        }elseif(meridiem==='tengahari'){
            returnhour>=11?hour:hour+12;
        }elseif(meridiem==='petang'||meridiem==='malam'){
            returnhour+12;
        }
    },
    meridiem:function(hours,minutes,isLower){
        if(hours<11){
            return'pagi';
        }elseif(hours<15){
            return'tengahari';
        }elseif(hours<19){
            return'petang';
        }else{
            return'malam';
        }
    },
    calendar:{
        sameDay:'[Hariinipukul]LT',
        nextDay:'[Esokpukul]LT',
        nextWeek:'dddd[pukul]LT',
        lastDay:'[Kelmarinpukul]LT',
        lastWeek:'dddd[lepaspukul]LT',
        sameElse:'L'
    },
    relativeTime:{
        future:'dalam%s',
        past:'%syanglepas',
        s:'beberapasaat',
        m:'seminit',
        mm:'%dminit',
        h:'sejam',
        hh:'%djam',
        d:'sehari',
        dd:'%dhari',
        M:'sebulan',
        MM:'%dbulan',
        y:'setahun',
        yy:'%dtahun'
    },
    week:{
        dow:1,//Mondayisthefirstdayoftheweek.
        doy:7 //TheweekthatcontainsJan1stisthefirstweekoftheyear.
    }
});

returnmsMy;

})));
