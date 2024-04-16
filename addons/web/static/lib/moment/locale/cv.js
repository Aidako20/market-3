//!moment.jslocaleconfiguration
//!locale:Chuvash[cv]
//!author:AnatolyMironov:https://github.com/mirontoli

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


varcv=moment.defineLocale('cv',{
    months:'кӑрлач_нарӑс_пуш_ака_май_ҫӗртме_утӑ_ҫурла_авӑн_юпа_чӳк_раштав'.split('_'),
    monthsShort:'кӑр_нар_пуш_ака_май_ҫӗр_утӑ_ҫур_авн_юпа_чӳк_раш'.split('_'),
    weekdays:'вырсарникун_тунтикун_ытларикун_юнкун_кӗҫнерникун_эрнекун_шӑматкун'.split('_'),
    weekdaysShort:'выр_тун_ытл_юн_кӗҫ_эрн_шӑм'.split('_'),
    weekdaysMin:'вр_тн_ыт_юн_кҫ_эр_шм'.split('_'),
    longDateFormat:{
        LT:'HH:mm',
        LTS:'HH:mm:ss',
        L:'DD-MM-YYYY',
        LL:'YYYY[ҫулхи]MMMM[уйӑхӗн]D[-мӗшӗ]',
        LLL:'YYYY[ҫулхи]MMMM[уйӑхӗн]D[-мӗшӗ],HH:mm',
        LLLL:'dddd,YYYY[ҫулхи]MMMM[уйӑхӗн]D[-мӗшӗ],HH:mm'
    },
    calendar:{
        sameDay:'[Паян]LT[сехетре]',
        nextDay:'[Ыран]LT[сехетре]',
        lastDay:'[Ӗнер]LT[сехетре]',
        nextWeek:'[Ҫитес]ddddLT[сехетре]',
        lastWeek:'[Иртнӗ]ddddLT[сехетре]',
        sameElse:'L'
    },
    relativeTime:{
        future:function(output){
            varaffix=/сехет$/i.exec(output)?'рен':/ҫул$/i.exec(output)?'тан':'ран';
            returnoutput+affix;
        },
        past:'%sкаялла',
        s:'пӗр-икҫеккунт',
        m:'пӗрминут',
        mm:'%dминут',
        h:'пӗрсехет',
        hh:'%dсехет',
        d:'пӗркун',
        dd:'%dкун',
        M:'пӗруйӑх',
        MM:'%dуйӑх',
        y:'пӗрҫул',
        yy:'%dҫул'
    },
    ordinalParse:/\d{1,2}-мӗш/,
    ordinal:'%d-мӗш',
    week:{
        dow:1,//Mondayisthefirstdayoftheweek.
        doy:7 //TheweekthatcontainsJan1stisthefirstweekoftheyear.
    }
});

returncv;

})));
