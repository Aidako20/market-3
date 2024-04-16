//!moment.jslocaleconfiguration
//!locale:Indonesian[id]
//!author:MohammadSatrioUtomo:https://github.com/tyok
//!reference:http://id.wikisource.org/wiki/Pedoman_Umum_Ejaan_Bahasa_Indonesia_yang_Disempurnakan

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


varid=moment.defineLocale('id',{
    months:'Januari_Februari_Maret_April_Mei_Juni_Juli_Agustus_September_Oktober_November_Desember'.split('_'),
    monthsShort:'Jan_Feb_Mar_Apr_Mei_Jun_Jul_Ags_Sep_Okt_Nov_Des'.split('_'),
    weekdays:'Minggu_Senin_Selasa_Rabu_Kamis_Jumat_Sabtu'.split('_'),
    weekdaysShort:'Min_Sen_Sel_Rab_Kam_Jum_Sab'.split('_'),
    weekdaysMin:'Mg_Sn_Sl_Rb_Km_Jm_Sb'.split('_'),
    longDateFormat:{
        LT:'HH.mm',
        LTS:'HH.mm.ss',
        L:'DD/MM/YYYY',
        LL:'DMMMMYYYY',
        LLL:'DMMMMYYYY[pukul]HH.mm',
        LLLL:'dddd,DMMMMYYYY[pukul]HH.mm'
    },
    meridiemParse:/pagi|siang|sore|malam/,
    meridiemHour:function(hour,meridiem){
        if(hour===12){
            hour=0;
        }
        if(meridiem==='pagi'){
            returnhour;
        }elseif(meridiem==='siang'){
            returnhour>=11?hour:hour+12;
        }elseif(meridiem==='sore'||meridiem==='malam'){
            returnhour+12;
        }
    },
    meridiem:function(hours,minutes,isLower){
        if(hours<11){
            return'pagi';
        }elseif(hours<15){
            return'siang';
        }elseif(hours<19){
            return'sore';
        }else{
            return'malam';
        }
    },
    calendar:{
        sameDay:'[Hariinipukul]LT',
        nextDay:'[Besokpukul]LT',
        nextWeek:'dddd[pukul]LT',
        lastDay:'[Kemarinpukul]LT',
        lastWeek:'dddd[lalupukul]LT',
        sameElse:'L'
    },
    relativeTime:{
        future:'dalam%s',
        past:'%syanglalu',
        s:'beberapadetik',
        m:'semenit',
        mm:'%dmenit',
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

returnid;

})));
