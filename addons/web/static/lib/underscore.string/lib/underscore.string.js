// Underscore.string
// (c)2010Esa-MattiSuuronen<esa-mattiaetsuuronendotorg>
// Underscore.stringisfreelydistributableunderthetermsoftheMITlicense.
// Documentation:https://github.com/epeli/underscore.string
// SomecodeisborrowedfromMooToolsandAlexandruMarasteanu.
// Version'2.3.2'

!function(root,String){
  'usestrict';

  //Defininghelperfunctions.

  varnativeTrim=String.prototype.trim;
  varnativeTrimRight=String.prototype.trimRight;
  varnativeTrimLeft=String.prototype.trimLeft;

  varparseNumber=function(source){returnsource*1||0;};

  varstrRepeat=function(str,qty){
    if(qty<1)return'';
    varresult='';
    while(qty>0){
      if(qty&1)result+=str;
      qty>>=1,str+=str;
    }
    returnresult;
  };

  varslice=[].slice;

  vardefaultToWhiteSpace=function(characters){
    if(characters==null)
      return'\\s';
    elseif(characters.source)
      returncharacters.source;
    else
      return'['+_s.escapeRegExp(characters)+']';
  };

  //HelperfortoBoolean
  functionboolMatch(s,matchers){
    vari,matcher,down=s.toLowerCase();
    matchers=[].concat(matchers);
    for(i=0;i<matchers.length;i+=1){
      matcher=matchers[i];
      if(!matcher)continue;
      if(matcher.test&&matcher.test(s))returntrue;
      if(matcher.toLowerCase()===down)returntrue;
    }
  }

  varescapeChars={
    lt:'<',
    gt:'>',
    quot:'"',
    amp:'&',
    apos:"'"
  };

  varreversedEscapeChars={};
  for(varkeyinescapeChars)reversedEscapeChars[escapeChars[key]]=key;
  reversedEscapeChars["'"]='#39';

  //sprintf()forJavaScript0.7-beta1
  //http://www.diveintojavascript.com/projects/javascript-sprintf
  //
  //Copyright(c)AlexandruMarasteanu<alexaholic[at)gmail(dot]com>
  //Allrightsreserved.

  varsprintf=(function(){
    functionget_type(variable){
      returnObject.prototype.toString.call(variable).slice(8,-1).toLowerCase();
    }

    varstr_repeat=strRepeat;

    varstr_format=function(){
      if(!str_format.cache.hasOwnProperty(arguments[0])){
        str_format.cache[arguments[0]]=str_format.parse(arguments[0]);
      }
      returnstr_format.format.call(null,str_format.cache[arguments[0]],arguments);
    };

    str_format.format=function(parse_tree,argv){
      varcursor=1,tree_length=parse_tree.length,node_type='',arg,output=[],i,k,match,pad,pad_character,pad_length;
      for(i=0;i<tree_length;i++){
        node_type=get_type(parse_tree[i]);
        if(node_type==='string'){
          output.push(parse_tree[i]);
        }
        elseif(node_type==='array'){
          match=parse_tree[i];//conveniencepurposesonly
          if(match[2]){//keywordargument
            arg=argv[cursor];
            for(k=0;k<match[2].length;k++){
              if(!arg.hasOwnProperty(match[2][k])){
                thrownewError(sprintf('[_.sprintf]property"%s"doesnotexist',match[2][k]));
              }
              arg=arg[match[2][k]];
            }
          }elseif(match[1]){//positionalargument(explicit)
            arg=argv[match[1]];
          }
          else{//positionalargument(implicit)
            arg=argv[cursor++];
          }

          if(/[^s]/.test(match[8])&&(get_type(arg)!='number')){
            thrownewError(sprintf('[_.sprintf]expectingnumberbutfound%s',get_type(arg)));
          }
          switch(match[8]){
            case'b':arg=arg.toString(2);break;
            case'c':arg=String.fromCharCode(arg);break;
            case'd':arg=parseInt(arg,10);break;
            case'e':arg=match[7]?arg.toExponential(match[7]):arg.toExponential();break;
            case'f':arg=match[7]?parseFloat(arg).toFixed(match[7]):parseFloat(arg);break;
            case'o':arg=arg.toString(8);break;
            case's':arg=((arg=String(arg))&&match[7]?arg.substring(0,match[7]):arg);break;
            case'u':arg=Math.abs(arg);break;
            case'x':arg=arg.toString(16);break;
            case'X':arg=arg.toString(16).toUpperCase();break;
          }
          arg=(/[def]/.test(match[8])&&match[3]&&arg>=0?'+'+arg:arg);
          pad_character=match[4]?match[4]=='0'?'0':match[4].charAt(1):'';
          pad_length=match[6]-String(arg).length;
          pad=match[6]?str_repeat(pad_character,pad_length):'';
          output.push(match[5]?arg+pad:pad+arg);
        }
      }
      returnoutput.join('');
    };

    str_format.cache={};

    str_format.parse=function(fmt){
      var_fmt=fmt,match=[],parse_tree=[],arg_names=0;
      while(_fmt){
        if((match=/^[^\x25]+/.exec(_fmt))!==null){
          parse_tree.push(match[0]);
        }
        elseif((match=/^\x25{2}/.exec(_fmt))!==null){
          parse_tree.push('%');
        }
        elseif((match=/^\x25(?:([1-9]\d*)\$|\(([^\)]+)\))?(\+)?(0|'[^$])?(-)?(\d+)?(?:\.(\d+))?([b-fosuxX])/.exec(_fmt))!==null){
          if(match[2]){
            arg_names|=1;
            varfield_list=[],replacement_field=match[2],field_match=[];
            if((field_match=/^([a-z_][a-z_\d]*)/i.exec(replacement_field))!==null){
              field_list.push(field_match[1]);
              while((replacement_field=replacement_field.substring(field_match[0].length))!==''){
                if((field_match=/^\.([a-z_][a-z_\d]*)/i.exec(replacement_field))!==null){
                  field_list.push(field_match[1]);
                }
                elseif((field_match=/^\[(\d+)\]/.exec(replacement_field))!==null){
                  field_list.push(field_match[1]);
                }
                else{
                  thrownewError('[_.sprintf]huh?');
                }
              }
            }
            else{
              thrownewError('[_.sprintf]huh?');
            }
            match[2]=field_list;
          }
          else{
            arg_names|=2;
          }
          if(arg_names===3){
            thrownewError('[_.sprintf]mixingpositionalandnamedplaceholdersisnot(yet)supported');
          }
          parse_tree.push(match);
        }
        else{
          thrownewError('[_.sprintf]huh?');
        }
        _fmt=_fmt.substring(match[0].length);
      }
      returnparse_tree;
    };

    returnstr_format;
  })();



  //Definingunderscore.string

  var_s={

    VERSION:'2.3.0',

    isBlank:function(str){
      if(str==null)str='';
      return(/^\s*$/).test(str);
    },

    stripTags:function(str){
      if(str==null)return'';
      returnString(str).replace(/<\/?[^>]+>/g,'');
    },

    capitalize:function(str){
      str=str==null?'':String(str);
      returnstr.charAt(0).toUpperCase()+str.slice(1);
    },

    chop:function(str,step){
      if(str==null)return[];
      str=String(str);
      step=~~step;
      returnstep>0?str.match(newRegExp('.{1,'+step+'}','g')):[str];
    },

    clean:function(str){
      return_s.strip(str).replace(/\s+/g,'');
    },

    count:function(str,substr){
      if(str==null||substr==null)return0;

      str=String(str);
      substr=String(substr);

      varcount=0,
        pos=0,
        length=substr.length;

      while(true){
        pos=str.indexOf(substr,pos);
        if(pos===-1)break;
        count++;
        pos+=length;
      }

      returncount;
    },

    chars:function(str){
      if(str==null)return[];
      returnString(str).split('');
    },

    swapCase:function(str){
      if(str==null)return'';
      returnString(str).replace(/\S/g,function(c){
        returnc===c.toUpperCase()?c.toLowerCase():c.toUpperCase();
      });
    },

    escapeHTML:function(str){
      if(str==null)return'';
      returnString(str).replace(/[&<>"']/g,function(m){return'&'+reversedEscapeChars[m]+';';});
    },

    unescapeHTML:function(str){
      if(str==null)return'';
      returnString(str).replace(/\&([^;]+);/g,function(entity,entityCode){
        varmatch;

        if(entityCodeinescapeChars){
          returnescapeChars[entityCode];
        }elseif(match=entityCode.match(/^#x([\da-fA-F]+)$/)){
          returnString.fromCharCode(parseInt(match[1],16));
        }elseif(match=entityCode.match(/^#(\d+)$/)){
          returnString.fromCharCode(~~match[1]);
        }else{
          returnentity;
        }
      });
    },

    escapeRegExp:function(str){
      if(str==null)return'';
      returnString(str).replace(/([.*+?^=!:${}()|[\]\/\\])/g,'\\$1');
    },

    splice:function(str,i,howmany,substr){
      vararr=_s.chars(str);
      arr.splice(~~i,~~howmany,substr);
      returnarr.join('');
    },

    insert:function(str,i,substr){
      return_s.splice(str,i,0,substr);
    },

    include:function(str,needle){
      if(needle==='')returntrue;
      if(str==null)returnfalse;
      returnString(str).indexOf(needle)!==-1;
    },

    join:function(){
      varargs=slice.call(arguments),
        separator=args.shift();

      if(separator==null)separator='';

      returnargs.join(separator);
    },

    lines:function(str){
      if(str==null)return[];
      returnString(str).split("\n");
    },

    reverse:function(str){
      return_s.chars(str).reverse().join('');
    },

    startsWith:function(str,starts){
      if(starts==='')returntrue;
      if(str==null||starts==null)returnfalse;
      str=String(str);starts=String(starts);
      returnstr.length>=starts.length&&str.slice(0,starts.length)===starts;
    },

    endsWith:function(str,ends){
      if(ends==='')returntrue;
      if(str==null||ends==null)returnfalse;
      str=String(str);ends=String(ends);
      returnstr.length>=ends.length&&str.slice(str.length-ends.length)===ends;
    },

    succ:function(str){
      if(str==null)return'';
      str=String(str);
      returnstr.slice(0,-1)+String.fromCharCode(str.charCodeAt(str.length-1)+1);
    },

    titleize:function(str){
      if(str==null)return'';
      str =String(str).toLowerCase();
      returnstr.replace(/(?:^|\s|-)\S/g,function(c){returnc.toUpperCase();});
    },

    camelize:function(str){
      return_s.trim(str).replace(/[-_\s]+(.)?/g,function(match,c){returnc?c.toUpperCase():"";});
    },

    underscored:function(str){
      return_s.trim(str).replace(/([a-z\d])([A-Z]+)/g,'$1_$2').replace(/[-\s]+/g,'_').toLowerCase();
    },

    dasherize:function(str){
      return_s.trim(str).replace(/([A-Z])/g,'-$1').replace(/[-_\s]+/g,'-').toLowerCase();
    },

    classify:function(str){
      return_s.titleize(String(str).replace(/[\W_]/g,'')).replace(/\s/g,'');
    },

    humanize:function(str){
      return_s.capitalize(_s.underscored(str).replace(/_id$/,'').replace(/_/g,''));
    },

    trim:function(str,characters){
      if(str==null)return'';
      if(!characters&&nativeTrim)returnnativeTrim.call(str);
      characters=defaultToWhiteSpace(characters);
      returnString(str).replace(newRegExp('\^'+characters+'+|'+characters+'+$','g'),'');
    },

    ltrim:function(str,characters){
      if(str==null)return'';
      if(!characters&&nativeTrimLeft)returnnativeTrimLeft.call(str);
      characters=defaultToWhiteSpace(characters);
      returnString(str).replace(newRegExp('^'+characters+'+'),'');
    },

    rtrim:function(str,characters){
      if(str==null)return'';
      if(!characters&&nativeTrimRight)returnnativeTrimRight.call(str);
      characters=defaultToWhiteSpace(characters);
      returnString(str).replace(newRegExp(characters+'+$'),'');
    },

    truncate:function(str,length,truncateStr){
      if(str==null)return'';
      str=String(str);truncateStr=truncateStr||'...';
      length=~~length;
      returnstr.length>length?str.slice(0,length)+truncateStr:str;
    },

    /**
     *_s.prune:amoreelegantversionoftruncate
     *pruneextrachars,neverleavingahalf-choppedword.
     *@authorgithub.com/rwz
     */
    prune:function(str,length,pruneStr){
      if(str==null)return'';

      str=String(str);length=~~length;
      pruneStr=pruneStr!=null?String(pruneStr):'...';

      if(str.length<=length)returnstr;

      vartmpl=function(c){returnc.toUpperCase()!==c.toLowerCase()?'A':'';},
        template=str.slice(0,length+1).replace(/.(?=\W*\w*$)/g,tmpl);//'Hello,world'->'HellAAAAAAA'

      if(template.slice(template.length-2).match(/\w\w/))
        template=template.replace(/\s*\S+$/,'');
      else
        template=_s.rtrim(template.slice(0,template.length-1));

      return(template+pruneStr).length>str.length?str:str.slice(0,template.length)+pruneStr;
    },

    words:function(str,delimiter){
      if(_s.isBlank(str))return[];
      return_s.trim(str,delimiter).split(delimiter||/\s+/);
    },

    pad:function(str,length,padStr,type){
      str=str==null?'':String(str);
      length=~~length;

      varpadlen =0;

      if(!padStr)
        padStr='';
      elseif(padStr.length>1)
        padStr=padStr.charAt(0);

      switch(type){
        case'right':
          padlen=length-str.length;
          returnstr+strRepeat(padStr,padlen);
        case'both':
          padlen=length-str.length;
          returnstrRepeat(padStr,Math.ceil(padlen/2))+str
                  +strRepeat(padStr,Math.floor(padlen/2));
        default://'left'
          padlen=length-str.length;
          returnstrRepeat(padStr,padlen)+str;
        }
    },

    lpad:function(str,length,padStr){
      return_s.pad(str,length,padStr);
    },

    rpad:function(str,length,padStr){
      return_s.pad(str,length,padStr,'right');
    },

    lrpad:function(str,length,padStr){
      return_s.pad(str,length,padStr,'both');
    },

    sprintf:sprintf,

    vsprintf:function(fmt,argv){
      argv.unshift(fmt);
      returnsprintf.apply(null,argv);
    },

    toNumber:function(str,decimals){
      if(!str)return0;
      str=_s.trim(str);
      if(!str.match(/^-?\d+(?:\.\d+)?$/))returnNaN;
      returnparseNumber(parseNumber(str).toFixed(~~decimals));
    },

    numberFormat:function(number,dec,dsep,tsep){
      if(isNaN(number)||number==null)return'';

      number=number.toFixed(~~dec);
      tsep=typeoftsep=='string'?tsep:',';

      varparts=number.split('.'),fnums=parts[0],
        decimals=parts[1]?(dsep||'.')+parts[1]:'';

      returnfnums.replace(/(\d)(?=(?:\d{3})+$)/g,'$1'+tsep)+decimals;
    },

    strRight:function(str,sep){
      if(str==null)return'';
      str=String(str);sep=sep!=null?String(sep):sep;
      varpos=!sep?-1:str.indexOf(sep);
      return~pos?str.slice(pos+sep.length,str.length):str;
    },

    strRightBack:function(str,sep){
      if(str==null)return'';
      str=String(str);sep=sep!=null?String(sep):sep;
      varpos=!sep?-1:str.lastIndexOf(sep);
      return~pos?str.slice(pos+sep.length,str.length):str;
    },

    strLeft:function(str,sep){
      if(str==null)return'';
      str=String(str);sep=sep!=null?String(sep):sep;
      varpos=!sep?-1:str.indexOf(sep);
      return~pos?str.slice(0,pos):str;
    },

    strLeftBack:function(str,sep){
      if(str==null)return'';
      str+='';sep=sep!=null?''+sep:sep;
      varpos=str.lastIndexOf(sep);
      return~pos?str.slice(0,pos):str;
    },

    toSentence:function(array,separator,lastSeparator,serial){
      separator=separator||',';
      lastSeparator=lastSeparator||'and';
      vara=array.slice(),lastMember=a.pop();

      if(array.length>2&&serial)lastSeparator=_s.rtrim(separator)+lastSeparator;

      returna.length?a.join(separator)+lastSeparator+lastMember:lastMember;
    },

    toSentenceSerial:function(){
      varargs=slice.call(arguments);
      args[3]=true;
      return_s.toSentence.apply(_s,args);
    },

    slugify:function(str){
      if(str==null)return'';

      varfrom ="ąàáäâãåæăćęèéëêìíïîłńòóöôõøśșțùúüûñçżź",
          to   ="aaaaaaaaaceeeeeiiiilnoooooosstuuuunczz",
          regex=newRegExp(defaultToWhiteSpace(from),'g');

      str=String(str).toLowerCase().replace(regex,function(c){
        varindex=from.indexOf(c);
        returnto.charAt(index)||'-';
      });

      return_s.dasherize(str.replace(/[^\w\s-]/g,''));
    },

    surround:function(str,wrapper){
      return[wrapper,str,wrapper].join('');
    },

    quote:function(str,quoteChar){
      return_s.surround(str,quoteChar||'"');
    },

    unquote:function(str,quoteChar){
      quoteChar=quoteChar||'"';
      if(str[0]===quoteChar&&str[str.length-1]===quoteChar)
        returnstr.slice(1,str.length-1);
      elsereturnstr;
    },

    exports:function(){
      varresult={};

      for(varpropinthis){
        if(!this.hasOwnProperty(prop)||prop.match(/^(?:include|contains|reverse)$/))continue;
        result[prop]=this[prop];
      }

      returnresult;
    },

    repeat:function(str,qty,separator){
      if(str==null)return'';

      qty=~~qty;

      //usingfasterimplementationifseparatorisnotneeded;
      if(separator==null)returnstrRepeat(String(str),qty);

      //thisoneisabout300xslowerinGoogleChrome
      for(varrepeat=[];qty>0;repeat[--qty]=str){}
      returnrepeat.join(separator);
    },

    naturalCmp:function(str1,str2){
      if(str1==str2)return0;
      if(!str1)return-1;
      if(!str2)return1;

      varcmpRegex=/(\.\d+)|(\d+)|(\D+)/g,
        tokens1=String(str1).toLowerCase().match(cmpRegex),
        tokens2=String(str2).toLowerCase().match(cmpRegex),
        count=Math.min(tokens1.length,tokens2.length);

      for(vari=0;i<count;i++){
        vara=tokens1[i],b=tokens2[i];

        if(a!==b){
          varnum1=parseInt(a,10);
          if(!isNaN(num1)){
            varnum2=parseInt(b,10);
            if(!isNaN(num2)&&num1-num2)
              returnnum1-num2;
          }
          returna<b?-1:1;
        }
      }

      if(tokens1.length===tokens2.length)
        returntokens1.length-tokens2.length;

      returnstr1<str2?-1:1;
    },

    levenshtein:function(str1,str2){
      if(str1==null&&str2==null)return0;
      if(str1==null)returnString(str2).length;
      if(str2==null)returnString(str1).length;

      str1=String(str1);str2=String(str2);

      varcurrent=[],prev,value;

      for(vari=0;i<=str2.length;i++)
        for(varj=0;j<=str1.length;j++){
          if(i&&j)
            if(str1.charAt(j-1)===str2.charAt(i-1))
              value=prev;
            else
              value=Math.min(current[j],current[j-1],prev)+1;
          else
            value=i+j;

          prev=current[j];
          current[j]=value;
        }

      returncurrent.pop();
    },

    toBoolean:function(str,trueValues,falseValues){
      if(typeofstr==="number")str=""+str;
      if(typeofstr!=="string")return!!str;
      str=_s.trim(str);
      if(boolMatch(str,trueValues||["true","1"]))returntrue;
      if(boolMatch(str,falseValues||["false","0"]))returnfalse;
    }
  };

  //Aliases

  _s.strip   =_s.trim;
  _s.lstrip  =_s.ltrim;
  _s.rstrip  =_s.rtrim;
  _s.center  =_s.lrpad;
  _s.rjust   =_s.lpad;
  _s.ljust   =_s.rpad;
  _s.contains=_s.include;
  _s.q       =_s.quote;
  _s.toBool  =_s.toBoolean;

  //Exporting

  //CommonJSmoduleisdefined
  if(typeofexports!=='undefined'){
    if(typeofmodule!=='undefined'&&module.exports)
      module.exports=_s;

    exports._s=_s;
  }

  //RegisterasanamedmodulewithAMD.
  if(typeofdefine==='function'&&define.amd)
    define('underscore.string',[],function(){return_s;});


  //IntegratewithUnderscore.jsifdefined
  //orcreateourownunderscoreobject.
  root._=root._||{};
  root._.string=root._.str=_s;
}(this,String);
