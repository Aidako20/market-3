//!moment.jslocaleconfiguration
//!locale:Tibetan[bo]
//!author:ThuptenN.Chakrishar:https://github.com/vajradog

;(function(global,factory){
   typeofexports==='object'&&typeofmodule!=='undefined'
       &&typeofrequire==='function'?factory(require('../moment')):
   typeofdefine==='function'&&define.amd?define(['../moment'],factory):
   factory(global.moment)
}(this,(function(moment){'usestrict';


varsymbolMap={
    '1':'༡',
    '2':'༢',
    '3':'༣',
    '4':'༤',
    '5':'༥',
    '6':'༦',
    '7':'༧',
    '8':'༨',
    '9':'༩',
    '0':'༠'
};
varnumberMap={
    '༡':'1',
    '༢':'2',
    '༣':'3',
    '༤':'4',
    '༥':'5',
    '༦':'6',
    '༧':'7',
    '༨':'8',
    '༩':'9',
    '༠':'0'
};

varbo=moment.defineLocale('bo',{
    months:'ཟླ་བ་དང་པོ_ཟླ་བ་གཉིས་པ_ཟླ་བ་གསུམ་པ_ཟླ་བ་བཞི་པ_ཟླ་བ་ལྔ་པ_ཟླ་བ་དྲུག་པ_ཟླ་བ་བདུན་པ_ཟླ་བ་བརྒྱད་པ_ཟླ་བ་དགུ་པ_ཟླ་བ་བཅུ་པ_ཟླ་བ་བཅུ་གཅིག་པ_ཟླ་བ་བཅུ་གཉིས་པ'.split('_'),
    monthsShort:'ཟླ་བ་དང་པོ_ཟླ་བ་གཉིས་པ_ཟླ་བ་གསུམ་པ_ཟླ་བ་བཞི་པ_ཟླ་བ་ལྔ་པ_ཟླ་བ་དྲུག་པ_ཟླ་བ་བདུན་པ_ཟླ་བ་བརྒྱད་པ_ཟླ་བ་དགུ་པ_ཟླ་བ་བཅུ་པ_ཟླ་བ་བཅུ་གཅིག་པ_ཟླ་བ་བཅུ་གཉིས་པ'.split('_'),
    weekdays:'གཟའ་ཉི་མ་_གཟའ་ཟླ་བ་_གཟའ་མིག་དམར་_གཟའ་ལྷག་པ་_གཟའ་ཕུར་བུ_གཟའ་པ་སངས་_གཟའ་སྤེན་པ་'.split('_'),
    weekdaysShort:'ཉི་མ་_ཟླ་བ་_མིག་དམར་_ལྷག་པ་_ཕུར་བུ_པ་སངས་_སྤེན་པ་'.split('_'),
    weekdaysMin:'ཉི་མ་_ཟླ་བ་_མིག་དམར་_ལྷག་པ་_ཕུར་བུ_པ་སངས་_སྤེན་པ་'.split('_'),
    longDateFormat:{
        LT:'Ah:mm',
        LTS:'Ah:mm:ss',
        L:'DD/MM/YYYY',
        LL:'DMMMMYYYY',
        LLL:'DMMMMYYYY,Ah:mm',
        LLLL:'dddd,DMMMMYYYY,Ah:mm'
    },
    calendar:{
        sameDay:'[དི་རིང]LT',
        nextDay:'[སང་ཉིན]LT',
        nextWeek:'[བདུན་ཕྲག་རྗེས་མ],LT',
        lastDay:'[ཁ་སང]LT',
        lastWeek:'[བདུན་ཕྲག་མཐའ་མ]dddd,LT',
        sameElse:'L'
    },
    relativeTime:{
        future:'%sལ་',
        past:'%sསྔན་ལ',
        s:'ལམ་སང',
        m:'སྐར་མ་གཅིག',
        mm:'%dསྐར་མ',
        h:'ཆུ་ཚོད་གཅིག',
        hh:'%dཆུ་ཚོད',
        d:'ཉིན་གཅིག',
        dd:'%dཉིན་',
        M:'ཟླ་བ་གཅིག',
        MM:'%dཟླ་བ',
        y:'ལོ་གཅིག',
        yy:'%dལོ'
    },
    preparse:function(string){
        returnstring.replace(/[༡༢༣༤༥༦༧༨༩༠]/g,function(match){
            returnnumberMap[match];
        });
    },
    postformat:function(string){
        returnstring.replace(/\d/g,function(match){
            returnsymbolMap[match];
        });
    },
    meridiemParse:/མཚན་མོ|ཞོགས་ཀས|ཉིན་གུང|དགོང་དག|མཚན་མོ/,
    meridiemHour:function(hour,meridiem){
        if(hour===12){
            hour=0;
        }
        if((meridiem==='མཚན་མོ'&&hour>=4)||
                (meridiem==='ཉིན་གུང'&&hour<5)||
                meridiem==='དགོང་དག'){
            returnhour+12;
        }else{
            returnhour;
        }
    },
    meridiem:function(hour,minute,isLower){
        if(hour<4){
            return'མཚན་མོ';
        }elseif(hour<10){
            return'ཞོགས་ཀས';
        }elseif(hour<17){
            return'ཉིན་གུང';
        }elseif(hour<20){
            return'དགོང་དག';
        }else{
            return'མཚན་མོ';
        }
    },
    week:{
        dow:0,//Sundayisthefirstdayoftheweek.
        doy:6 //TheweekthatcontainsJan1stisthefirstweekoftheyear.
    }
});

returnbo;

})));
