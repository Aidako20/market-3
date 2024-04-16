/*
 *Fuzzy
 *https://github.com/myork/fuzzy
 *
 *Copyright(c)2012MattYork
 *LicensedundertheMITlicense.
 */

(function(){

varroot=this;

varfuzzy={};

//Useinnodeorinbrowser
if(typeofexports!=='undefined'){
  module.exports=fuzzy;
}else{
  root.fuzzy=fuzzy;
}

//Returnallelementsof`array`thathaveafuzzy
//matchagainst`pattern`.
fuzzy.simpleFilter=function(pattern,array){
  returnarray.filter(function(string){
    returnfuzzy.test(pattern,string);
  });
};

//Does`pattern`fuzzymatch`string`?
fuzzy.test=function(pattern,string){
  returnfuzzy.match(pattern,string)!==null;
};

//If`pattern`matches`string`,wrapeachmatchingcharacter
//in`opts.pre`and`opts.post`.Ifnomatch,returnnull
fuzzy.match=function(pattern,string,opts){
  opts=opts||{};
  varpatternIdx=0
    ,result=[]
    ,len=string.length
    ,totalScore=0
    ,currScore=0
    //prefix
    ,pre=opts.pre||''
    //suffix
    ,post=opts.post||''
    //Stringtocompareagainst.Thismightbealowercaseversionofthe
    //rawstring
    ,compareString= opts.caseSensitive&&string||string.toLowerCase()
    ,ch,compareChar;

  pattern=opts.caseSensitive&&pattern||pattern.toLowerCase();

  //Foreachcharacterinthestring,eitheraddittotheresult
  //orwrapintemplateifit'sthenextstringinthepattern
  for(varidx=0;idx<len;idx++){
    ch=string[idx];
    if(compareString[idx]===pattern[patternIdx]){
      if(pattern[patternIdx]===''){
        //wedon'twantaspacecharactertoaccumulatealargerscore
        currScore=1-idx/200;
      }else{
        //consecutivecharactersshouldincreasethescoremorethanlinearly
        currScore+=1+currScore-idx/200;
      }

      ch=pre+ch+post;
      patternIdx+=1;
    }else{
      currScore=0;
    }
    totalScore+=currScore;
    if(compareString[idx]===''){
      //wedon'twantcharactersafteraspacetoaccumulatealargerscore
      currScore=0;
    }
    result[result.length]=ch;
  }

  //returnrenderedstringifwehaveamatchforeverychar
  if(patternIdx===pattern.length){
    return{rendered:result.join(''),score:totalScore};
  }

  returnnull;
};

//Thenormalentrypoint.Filters`arr`formatchesagainst`pattern`.
//Itreturnsanarraywithmatchingvaluesofthetype:
//
//    [{
//        string:  '<b>lah'//Therenderedstring
//      ,index:   2       //Theindexoftheelementin`arr`
//      ,original:'blah'  //Theoriginalelementin`arr`
//    }]
//
//`opts`isanoptionalargumentbag.Details:
//
//   opts={
//       //stringtoputbeforeamatchingcharacter
//       pre:    '<b>'
//
//       //stringtoputaftermatchingcharacter
//     ,post:   '</b>'
//
//       //Optionalfunction.Inputisanentryinthegivenarr`,
//       //outputshouldbethestringtotest`pattern`against.
//       //Inthisexample,if`arr=[{crying:'koala'}]`wewouldreturn
//       //'koala'.
//     ,extract:function(arg){returnarg.crying;}
//   }
fuzzy.filter=function(pattern,arr,opts){
  if(!arr||arr.length===0){
    return[]
  }
  if(typeofpattern!=='string'){
    returnarr
  }
  opts=opts||{};
  returnarr
    .reduce(function(prev,element,idx,arr){
      varstr=element;
      if(opts.extract){
        str=opts.extract(element);
      }
      varrendered=fuzzy.match(pattern,str,opts);
      if(rendered!=null){
        prev[prev.length]={
            string:rendered.rendered
          ,score:rendered.score
          ,index:idx
          ,original:element
        };
      }
      returnprev;
    },[])

    //Sortbyscore.Browsersareinconsistentwrtstable/unstable
    //sorting,soforcestablebyusingtheindexinthecaseoftie.
    //Seehttp://ofb.net/~sethml/is-sort-stable.html
    .sort(function(a,b){
      varcompare=b.score-a.score;
      if(compare)returncompare;
      returna.index-b.index;
    });
};


}());
