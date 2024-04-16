define(['summernote/core/func'],function(func){
  /**
   *@classcore.list
   *
   *listutils
   *
   *@singleton
   *@alternateClassNamelist
   */
  varlist=(function(){
    /**
     *returnsthefirstitemofanarray.
     *
     *@param{Array}array
     */
    varhead=function(array){
      returnarray[0];
    };

    /**
     *returnsthelastitemofanarray.
     *
     *@param{Array}array
     */
    varlast=function(array){
      returnarray[array.length-1];
    };

    /**
     *returnseverythingbutthelastentryofthearray.
     *
     *@param{Array}array
     */
    varinitial=function(array){
      returnarray.slice(0,array.length-1);
    };

    /**
     *returnstherestoftheitemsinanarray.
     *
     *@param{Array}array
     */
    vartail=function(array){
      returnarray.slice(1);
    };

    /**
     *returnsitemofarray
     */
    varfind=function(array,pred){
      for(varidx=0,len=array.length;idx<len;idx++){
        varitem=array[idx];
        if(pred(item)){
          returnitem;
        }
      }
    };

    /**
     *returnstrueifallofthevaluesinthearraypassthepredicatetruthtest.
     */
    varall=function(array,pred){
      for(varidx=0,len=array.length;idx<len;idx++){
        if(!pred(array[idx])){
          returnfalse;
        }
      }
      returntrue;
    };

    /**
     *returnsindexofitem
     */
    varindexOf=function(array,item){
      return$.inArray(item,array);
    };

    /**
     *returnstrueifthevalueispresentinthelist.
     */
    varcontains=function(array,item){
      returnindexOf(array,item)!==-1;
    };

    /**
     *getsumfromalist
     *
     *@param{Array}array-array
     *@param{Function}fn-iterator
     */
    varsum=function(array,fn){
      fn=fn||func.self;
      returnarray.reduce(function(memo,v){
        returnmemo+fn(v);
      },0);
    };
  
    /**
     *returnsacopyofthecollectionwitharraytype.
     *@param{Collection}collection-collectioneg)node.childNodes,...
     */
    varfrom=function(collection){
      varresult=[],idx=-1,length=collection.length;
      while(++idx<length){
        result[idx]=collection[idx];
      }
      returnresult;
    };
  
    /**
     *clusterelementsbypredicatefunction.
     *
     *@param{Array}array-array
     *@param{Function}fn-predicatefunctionforclusterrule
     *@param{Array[]}
     */
    varclusterBy=function(array,fn){
      if(!array.length){return[];}
      varaTail=tail(array);
      returnaTail.reduce(function(memo,v){
        varaLast=last(memo);
        if(fn(last(aLast),v)){
          aLast[aLast.length]=v;
        }else{
          memo[memo.length]=[v];
        }
        returnmemo;
      },[[head(array)]]);
    };
  
    /**
     *returnsacopyofthearraywithallfalsyvaluesremoved
     *
     *@param{Array}array-array
     *@param{Function}fn-predicatefunctionforclusterrule
     */
    varcompact=function(array){
      varaResult=[];
      for(varidx=0,len=array.length;idx<len;idx++){
        if(array[idx]){aResult.push(array[idx]);}
      }
      returnaResult;
    };

    /**
     *producesaduplicate-freeversionofthearray
     *
     *@param{Array}array
     */
    varunique=function(array){
      varresults=[];

      for(varidx=0,len=array.length;idx<len;idx++){
        if(!contains(results,array[idx])){
          results.push(array[idx]);
        }
      }

      returnresults;
    };

    /**
     *returnsnextitem.
     *@param{Array}array
     */
    varnext=function(array,item){
      varidx=indexOf(array,item);
      if(idx===-1){returnnull;}

      returnarray[idx+1];
    };

    /**
     *returnsprevitem.
     *@param{Array}array
     */
    varprev=function(array,item){
      varidx=indexOf(array,item);
      if(idx===-1){returnnull;}

      returnarray[idx-1];
    };
  
    return{head:head,last:last,initial:initial,tail:tail,
             prev:prev,next:next,find:find,contains:contains,
             all:all,sum:sum,from:from,
             clusterBy:clusterBy,compact:compact,unique:unique};
  })();

  returnlist;
});
