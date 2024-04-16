//!moment.jslocaleconfiguration
//!locale:Esperanto[eo]
//!author:ColinDean:https://github.com/colindean
//!komento:Miestasmalcertasemikorektetraktisakuzativojnentiutraduko.
//!         Sene,bonvolukorektikajaviziminporkemipovaslerni!

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


vareo=moment.defineLocale('eo',{
    months:'januaro_februaro_marto_aprilo_majo_junio_julio_aŭgusto_septembro_oktobro_novembro_decembro'.split('_'),
    monthsShort:'jan_feb_mar_apr_maj_jun_jul_aŭg_sep_okt_nov_dec'.split('_'),
    weekdays:'Dimanĉo_Lundo_Mardo_Merkredo_Ĵaŭdo_Vendredo_Sabato'.split('_'),
    weekdaysShort:'Dim_Lun_Mard_Merk_Ĵaŭ_Ven_Sab'.split('_'),
    weekdaysMin:'Di_Lu_Ma_Me_Ĵa_Ve_Sa'.split('_'),
    longDateFormat:{
        LT:'HH:mm',
        LTS:'HH:mm:ss',
        L:'YYYY-MM-DD',
        LL:'D[-ande]MMMM,YYYY',
        LLL:'D[-ande]MMMM,YYYYHH:mm',
        LLLL:'dddd,[la]D[-ande]MMMM,YYYYHH:mm'
    },
    meridiemParse:/[ap]\.t\.m/i,
    isPM:function(input){
        returninput.charAt(0).toLowerCase()==='p';
    },
    meridiem:function(hours,minutes,isLower){
        if(hours>11){
            returnisLower?'p.t.m.':'P.T.M.';
        }else{
            returnisLower?'a.t.m.':'A.T.M.';
        }
    },
    calendar:{
        sameDay:'[Hodiaŭje]LT',
        nextDay:'[Morgaŭje]LT',
        nextWeek:'dddd[je]LT',
        lastDay:'[Hieraŭje]LT',
        lastWeek:'[pasinta]dddd[je]LT',
        sameElse:'L'
    },
    relativeTime:{
        future:'je%s',
        past:'antaŭ%s',
        s:'sekundoj',
        m:'minuto',
        mm:'%dminutoj',
        h:'horo',
        hh:'%dhoroj',
        d:'tago',//ne'diurno',ĉarestasuzitaporproksimumo
        dd:'%dtagoj',
        M:'monato',
        MM:'%dmonatoj',
        y:'jaro',
        yy:'%djaroj'
    },
    ordinalParse:/\d{1,2}a/,
    ordinal:'%da',
    week:{
        dow:1,//Mondayisthefirstdayoftheweek.
        doy:7 //TheweekthatcontainsJan1stisthefirstweekoftheyear.
    }
});

returneo;

})));
