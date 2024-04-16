define('summernote/core/func',function(){
  /**
   *@classcore.func
   *
   *funcutils(forhigh-orderfunc'sarg)
   *
   *@singleton
   *@alternateClassNamefunc
   */
  varfunc=(function(){
    vareq=function(itemA){
      returnfunction(itemB){
        returnitemA===itemB;
      };
    };

    vareq2=function(itemA,itemB){
      returnitemA===itemB;
    };

    varpeq2=function(propName){
      returnfunction(itemA,itemB){
        returnitemA[propName]===itemB[propName];
      };
    };

    varok=function(){
      returntrue;
    };

    varfail=function(){
      returnfalse;
    };

    varnot=function(f){
      returnfunction(){
        return!f.apply(f,arguments);
      };
    };

    varand=function(fA,fB){
      returnfunction(item){
        returnfA(item)&&fB(item);
      };
    };

    varself=function(a){
      returna;
    };

    varidCounter=0;

    /**
     *generateaglobally-uniqueid
     *
     *@param{String}[prefix]
     */
    varuniqueId=function(prefix){
      varid=++idCounter+'';
      returnprefix?prefix+id:id;
    };

    /**
     *returnsbnd(bounds)fromrect
     *
     *-IECompatabilityIssue:http://goo.gl/sRLOAo
     *-ScrollIssue:http://goo.gl/sNjUc
     *
     *@param{Rect}rect
     *@return{Object}bounds
     *@return{Number}bounds.top
     *@return{Number}bounds.left
     *@return{Number}bounds.width
     *@return{Number}bounds.height
     */
    varrect2bnd=function(rect){
      var$document=$(document);
      return{
        top:rect.top+$document.scrollTop(),
        left:rect.left+$document.scrollLeft(),
        width:rect.right-rect.left,
        height:rect.bottom-rect.top
      };
    };

    /**
     *returnsacopyoftheobjectwherethekeyshavebecomethevaluesandthevaluesthekeys.
     *@param{Object}obj
     *@return{Object}
     */
    varinvertObject=function(obj){
      varinverted={};
      for(varkeyinobj){
        if(obj.hasOwnProperty(key)){
          inverted[obj[key]]=key;
        }
      }
      returninverted;
    };

    /**
     *@param{String}namespace
     *@param{String}[prefix]
     *@return{String}
     */
    varnamespaceToCamel=function(namespace,prefix){
      prefix=prefix||'';
      returnprefix+namespace.split('.').map(function(name){
        returnname.substring(0,1).toUpperCase()+name.substring(1);
      }).join('');
    };

    return{
      eq:eq,
      eq2:eq2,
      peq2:peq2,
      ok:ok,
      fail:fail,
      self:self,
      not:not,
      and:and,
      uniqueId:uniqueId,
      rect2bnd:rect2bnd,
      invertObject:invertObject,
      namespaceToCamel:namespaceToCamel
    };
  })();

  returnfunc;
});
