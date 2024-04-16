/*!
 *jQueryBBQ:BackButton&QueryLibrary-v1.3pre-8/26/2010
 *http://benalman.com/projects/jquery-bbq-plugin/
 *
 *Copyright(c)2010"Cowboy"BenAlman
 *DuallicensedundertheMITandGPLlicenses.
 *http://benalman.com/about/license/
 */

//Script:jQueryBBQ:BackButton&QueryLibrary
//
//*Version:1.3pre,Lastupdated:8/26/2010*
//
//ProjectHome-http://benalman.com/projects/jquery-bbq-plugin/
//GitHub      -http://github.com/cowboy/jquery-bbq/
//Source      -http://github.com/cowboy/jquery-bbq/raw/master/jquery.ba-bbq.js
//(Minified)  -http://github.com/cowboy/jquery-bbq/raw/master/jquery.ba-bbq.min.js(2.2kbgzipped)
//
//About:License
//
//Copyright(c)2010"Cowboy"BenAlman,
//DuallicensedundertheMITandGPLlicenses.
//http://benalman.com/about/license/
//
//About:Examples
//
//Theseworkingexamples,completewithfullycommentedcode,illustrateafew
//waysinwhichthisplugincanbeused.
//
//BasicAJAX    -http://benalman.com/code/projects/jquery-bbq/examples/fragment-basic/
//AdvancedAJAX -http://benalman.com/code/projects/jquery-bbq/examples/fragment-advanced/
//jQueryUITabs-http://benalman.com/code/projects/jquery-bbq/examples/fragment-jquery-ui-tabs/
//Deparam       -http://benalman.com/code/projects/jquery-bbq/examples/deparam/
//
//About:SupportandTesting
//
//InformationaboutwhatversionorversionsofjQuerythispluginhasbeen
//testedwith,whatbrowsersithasbeentestedin,andwheretheunittests
//reside(soyoucantestityourself).
//
//jQueryVersions-1.2.6,1.3.2,1.4.1,1.4.2
//BrowsersTested-InternetExplorer6-8,Firefox2-4,Chrome5-6,Safari3.2-5,
//                  Opera9.6-10.60,iPhone3.1,Android1.6-2.2,BlackBerry4.6-5.
//UnitTests     -http://benalman.com/code/projects/jquery-bbq/unit/
//
//About:ReleaseHistory
//
//1.3pre-(8/26/2010)Integrated<jQueryhashchangeevent>v1.3,whichadds
//        document.titleanddocument.domainsupportinIE6/7,BlackBerry
//        support,betterIframehidingforaccessibilityreasons,andthenew
//        <jQuery.fn.hashchange>"shortcut"method.Addedthe
//        <jQuery.param.sorted>methodwhichreducesthepossibilityof
//        extraneoushashchangeeventtriggering.Addedthe
//        <jQuery.param.fragment.ajaxCrawlable>methodwhichcanbeusedto
//        enableGoogle"AJAXCrawlablemode."
//1.2.1-(2/17/2010)Actuallyfixedthestalewindow.locationSafaribugfrom
//        <jQueryhashchangeevent>inBBQ,whichwasthemainreasonforthe
//        previousrelease!
//1.2  -(2/16/2010)Integrated<jQueryhashchangeevent>v1.2,whichfixesa
//        Safaribug,theeventcannowbeboundbeforeDOMready,andIE6/7
//        pageshouldnolongerscrollwhentheeventisfirstbound.Also
//        addedthe<jQuery.param.fragment.noEscape>method,andreworkedthe
//        <hashchangeevent(BBQ)>internal"add"methodtobecompatiblewith
//        changesmadetothejQuery1.4.2specialeventsAPI.
//1.1.1-(1/22/2010)Integrated<jQueryhashchangeevent>v1.1,whichfixesan
//        obscureIE8EmulateIE7metatagcompatibilitymodebug.
//1.1  -(1/9/2010)BrokeoutthejQueryBBQevent.special<hashchangeevent>
//        functionalityintoaseparatepluginforuserswhowantjustthe
//        basicevent&backbuttonsupport,withoutalltheextraawesomeness
//        thatBBQprovides.ThispluginwillbeincludedaspartofjQueryBBQ,
//        butalsobeavailableseparately.See<jQueryhashchangeevent>
//        pluginformoreinformation.Alsoaddedthe<jQuery.bbq.removeState>
//        methodandaddedadditional<jQuery.deparam>examples.
//1.0.3-(12/2/2009)FixedanissueinIE6wherelocation.searchand
//        location.hashwouldreportincorrectlyifthehashcontainedthe?
//        character.Also<jQuery.param.querystring>and<jQuery.param.fragment>
//        willnolongerparseparamsoutofaURLthatdoesn'tcontain?or#,
//        respectively.
//1.0.2-(10/10/2009)FixedanissueinIE6/7wherethehiddenIFRAMEcaused
//        a"Thispagecontainsbothsecureandnonsecureitems."warningwhen
//        usedonanhttps://page.
//1.0.1-(10/7/2009)FixedanissueinIE8.Sinceboth"IE7"and"IE8
//        CompatibilityView"modeserroneouslyreportthatthebrowser
//        supportsthenativewindow.onhashchangeevent,aslightlymore
//        robusttestneededtobeadded.
//1.0  -(10/2/2009)Initialrelease

(function($,window){
  '$:nomunge';//UsedbyYUIcompressor.
  
  //Someconvenientshortcuts.
  varundefined,
    aps=Array.prototype.slice,
    decode=decodeURIComponent,
    
    //Method/objectreferences.
    jq_param=$.param,
    jq_param_sorted,
    jq_param_fragment,
    jq_deparam,
    jq_deparam_fragment,
    jq_bbq=$.bbq=$.bbq||{},
    jq_bbq_pushState,
    jq_bbq_getState,
    jq_elemUrlAttr,
    special=$.event.special,
    
    //Reusedstrings.
    str_hashchange='hashchange',
    str_querystring='querystring',
    str_fragment='fragment',
    str_elemUrlAttr='elemUrlAttr',
    str_href='href',
    str_src='src',
    
    //ReusedRegExp.
    re_params_querystring=/^.*\?|#.*$/g,
    re_params_fragment,
    re_fragment,
    re_no_escape,
    
    ajax_crawlable,
    fragment_prefix,
    
    //UsedbyjQuery.elemUrlAttr.
    elemUrlAttr_cache={};
  
  //Afewcommonlyusedbits,brokenouttohelpreduceminifiedfilesize.
  
  functionis_string(arg){
    returntypeofarg==='string';
  };
  
  //Whywritethesamefunctiontwice?Let'scurry!Mmmm,curry..
  
  functioncurry(func){
    varargs=aps.call(arguments,1);
    
    returnfunction(){
      returnfunc.apply(this,args.concat(aps.call(arguments)));
    };
  };
  
  //Getlocation.hash(orwhatyou'dexpectlocation.hashtobe)sansany
  //leading#.Thanksformakingthisnecessary,Firefox!
  functionget_fragment(url){
    returnurl.replace(re_fragment,'$2');
  };
  
  //Getlocation.search(orwhatyou'dexpectlocation.searchtobe)sansany
  //leading#.Thanksformakingthisnecessary,IE6!
  functionget_querystring(url){
    returnurl.replace(/(?:^[^?#]*\?([^#]*).*$)?.*/,'$1');
  };
  
  //Section:Param(tostring)
  //
  //Method:jQuery.param.querystring
  //
  //RetrievethequerystringfromaURLorifnoargumentsarepassed,the
  //currentwindow.location.href.
  //
  //Usage:
  //
  //>jQuery.param.querystring([url]);
  //
  //Arguments:
  //
  // url-(String)AURLcontainingquerystringparamstobeparsed.Ifurl
  //   isnotpassed,thecurrentwindow.location.hrefisused.
  //
  //Returns:
  //
  // (String)Theparsedquerystring,withanyleading"?"removed.
  //
  
  //Method:jQuery.param.querystring(buildurl)
  //
  //MergeaURL,withorwithoutpre-existingquerystringparams,plusany
  //object,paramsstringorURLcontainingquerystringparamsintoanewURL.
  //
  //Usage:
  //
  //>jQuery.param.querystring(url,params[,merge_mode]);
  //
  //Arguments:
  //
  // url-(String)AvalidURLforparamstobemergedinto.ThisURLmay
  //   containaquerystringand/orfragment(hash).
  // params-(String)AparamsstringorURLcontainingquerystringparamsto
  //   bemergedintourl.
  // params-(Object)Aparamsobjecttobemergedintourl.
  // merge_mode-(Number)Mergebehaviordefaultsto0ifmerge_modeisnot
  //   specified,andisas-follows:
  //
  //   *0:paramsintheparamsargumentwilloverrideanyquerystring
  //        paramsinurl.
  //   *1:anyquerystringparamsinurlwilloverrideparamsintheparams
  //        argument.
  //   *2:paramsargumentwillcompletelyreplaceanyquerystringinurl.
  //
  //Returns:
  //
  // (String)AURLwithaurlencodedquerystringintheformat'?a=b&c=d&e=f'.
  
  //Method:jQuery.param.fragment
  //
  //Retrievethefragment(hash)fromaURLorifnoargumentsarepassed,the
  //currentwindow.location.href.
  //
  //Usage:
  //
  //>jQuery.param.fragment([url]);
  //
  //Arguments:
  //
  // url-(String)AURLcontainingfragment(hash)paramstobeparsed.If
  //   urlisnotpassed,thecurrentwindow.location.hrefisused.
  //
  //Returns:
  //
  // (String)Theparsedfragment(hash)string,withanyleading"#"removed.
  
  //Method:jQuery.param.fragment(buildurl)
  //
  //MergeaURL,withorwithoutpre-existingfragment(hash)params,plusany
  //object,paramsstringorURLcontainingfragment(hash)paramsintoanew
  //URL.
  //
  //Usage:
  //
  //>jQuery.param.fragment(url,params[,merge_mode]);
  //
  //Arguments:
  //
  // url-(String)AvalidURLforparamstobemergedinto.ThisURLmay
  //   containaquerystringand/orfragment(hash).
  // params-(String)AparamsstringorURLcontainingfragment(hash)params
  //   tobemergedintourl.
  // params-(Object)Aparamsobjecttobemergedintourl.
  // merge_mode-(Number)Mergebehaviordefaultsto0ifmerge_modeisnot
  //   specified,andisas-follows:
  //
  //   *0:paramsintheparamsargumentwilloverrideanyfragment(hash)
  //        paramsinurl.
  //   *1:anyfragment(hash)paramsinurlwilloverrideparamsinthe
  //        paramsargument.
  //   *2:paramsargumentwillcompletelyreplaceanyquerystringinurl.
  //
  //Returns:
  //
  // (String)AURLwithaurlencodedfragment(hash)intheformat'#a=b&c=d&e=f'.
  
  functionjq_param_sub(is_fragment,get_func,url,params,merge_mode){
    varresult,
      qs,
      matches,
      url_params,
      hash;
    
    if(params!==undefined){
      //BuildURLbymergingparamsintourlstring.
      
      //matches[1]=urlpartthatprecedesparams,notincludingtrailing?/#
      //matches[2]=params,notincludingleading?/#
      //matches[3]=ifin'querystring'mode,hashincludingleading#,otherwise''
      matches=url.match(is_fragment?re_fragment:/^([^#?]*)\??([^#]*)(#?.*)/);
      
      //Getthehashifin'querystring'mode,anditexists.
      hash=matches[3]||'';
      
      if(merge_mode===2&&is_string(params)){
        //Ifmerge_modeis2andparamsisastring,mergethefragment/query
        //stringintotheURLwholesale,withoutconvertingitintoanobject.
        qs=params.replace(is_fragment?re_params_fragment:re_params_querystring,'');
        
      }else{
        //Convertrelevantparamsinurltoobject.
        url_params=jq_deparam(matches[2]);
        
        params=is_string(params)
          
          //Convertpassedparamsstringintoobject.
          ?jq_deparam[is_fragment?str_fragment:str_querystring](params)
          
          //Passedparamsobject.
          :params;
        
        qs=merge_mode===2?params                             //passedparamsreplaceurlparams
          :merge_mode===1 ?$.extend({},params,url_params) //urlparamsoverridepassedparams
          :$.extend({},url_params,params);                    //passedparamsoverrideurlparams
        
        //Convertparamsobjectintoasortedparamsstring.
        qs=jq_param_sorted(qs);
        
        //Unescapecharactersspecifiedvia$.param.noEscape.Sinceonlyhash-
        //historyusershaverequestedthisfeature,it'sonlyenabledfor
        //fragment-relatedparamsstrings.
        if(is_fragment){
          qs=qs.replace(re_no_escape,decode);
        }
      }
      
      //BuildURLfromthebaseurl,querystringandhash.In'querystring'
      //mode,?isonlyaddedifaquerystringexists.In'fragment'mode,#
      //isalwaysadded.
      result=matches[1]+(is_fragment?fragment_prefix:qs||!matches[1]?'?':'')+qs+hash;
      
    }else{
      //IfURLwaspassedin,parseparamsfromURLstring,otherwiseparse
      //paramsfromwindow.location.href.
      result=get_func(url!==undefined?url:location.href);
    }
    
    returnresult;
  };
  
  jq_param[str_querystring]                 =curry(jq_param_sub,0,get_querystring);
  jq_param[str_fragment]=jq_param_fragment=curry(jq_param_sub,1,get_fragment);
  
  //Method:jQuery.param.sorted
  //
  //Returnsaparamsstringequivalenttothatreturnedbytheinternal
  //jQuery.parammethod,butsorted,whichmakesitsuitableforuseasa
  //cachekey.
  //
  //Forexample,inmostbrowsersjQuery.param({z:1,a:2})returns"z=1&a=2"
  //andjQuery.param({a:2,z:1})returns"a=2&z=1".Eventhoughboththe
  //objectsbeingserializedandtheresultingparamsstringsareequivalent,
  //iftheseparamsstringsweresetintothelocation.hashfragment
  //sequentially,thehashchangeeventwouldbetriggeredunnecessarily,since
  //thestringsaredifferent(eventhoughthedatadescribedbythemisthe
  //same).Bysortingtheparamsstring,unecessaryhashchangeeventtriggering
  //canbeavoided.
  //
  //Usage:
  //
  //>jQuery.param.sorted(obj[,traditional]);
  //
  //Arguments:
  //
  // obj-(Object)Anobjecttobeserialized.
  // traditional-(Boolean)Paramsdeep/shallowserializationmode.Seethe
  //   documentationathttp://api.jquery.com/jQuery.param/formoredetail.
  //
  //Returns:
  //
  // (String)Asortedparamsstring.
  
  jq_param.sorted=jq_param_sorted=function(a,traditional){
    vararr=[],
      obj={};
    
    $.each(jq_param(a,traditional).split('&'),function(i,v){
      varkey=v.replace(/(?:%5B|=).*$/,''),
        key_obj=obj[key];
      
      if(!key_obj){
        key_obj=obj[key]=[];
        arr.push(key);
      }
      
      key_obj.push(v);
    });
    
    return$.map(arr.sort(),function(v){
      returnobj[v];
    }).join('&');
  };
  
  //Method:jQuery.param.fragment.noEscape
  //
  //Specifycharactersthatwillbeleftunescapedwhenfragmentsarecreated
  //ormergedusing<jQuery.param.fragment>,orwhenthefragmentismodified
  //using<jQuery.bbq.pushState>.Thisoptiononlyappliestoserializeddata
  //objectfragments,andnotset-as-stringfragments.Doesnotaffectthe
  //querystring.Defaultsto",/"(comma,forwardslash).
  //
  //Notethatthisisconsideredapurelyaestheticoption,andwillhelpto
  //createURLsthat"lookpretty"intheaddressbarorbookmarks,without
  //affectingfunctionalityinanyway.Thatbeingsaid,becarefultonot
  //unescapecharactersthatareusedasdelimitersorserveaspecial
  //purpose,suchasthe"#?&=+"(octothorpe,questionmark,ampersand,
  //equals,plus)characters.
  //
  //Usage:
  //
  //>jQuery.param.fragment.noEscape([chars]);
  //
  //Arguments:
  //
  // chars-(String)Thecharacterstonotescapeinthefragment.If
  //   unspecified,defaultstoemptystring(escapeallcharacters).
  //
  //Returns:
  //
  // Nothing.
  
  jq_param_fragment.noEscape=function(chars){
    chars=chars||'';
    vararr=$.map(chars.split(''),encodeURIComponent);
    re_no_escape=newRegExp(arr.join('|'),'g');
  };
  
  //Asensibledefault.Thesearethecharacterspeopleseemtocomplainabout
  //"uglifyinguptheURL"themost.
  jq_param_fragment.noEscape(',/');
  
  //Method:jQuery.param.fragment.ajaxCrawlable
  //
  //TODO:DESCRIBE
  //
  //Usage:
  //
  //>jQuery.param.fragment.ajaxCrawlable([state]);
  //
  //Arguments:
  //
  // state-(Boolean)TODO:DESCRIBE
  //
  //Returns:
  //
  // (Boolean)ThecurrentajaxCrawlablestate.
  
  jq_param_fragment.ajaxCrawlable=function(state){
    if(state!==undefined){
      if(state){
        re_params_fragment=/^.*(?:#!|#)/;
        re_fragment=/^([^#]*)(?:#!|#)?(.*)$/;
        fragment_prefix='#!';
      }else{
        re_params_fragment=/^.*#/;
        re_fragment=/^([^#]*)#?(.*)$/;
        fragment_prefix='#';
      }
      ajax_crawlable=!!state;
    }
    
    returnajax_crawlable;
  };
  
  jq_param_fragment.ajaxCrawlable(0);
  
  //Section:Deparam(fromstring)
  //
  //Method:jQuery.deparam
  //
  //Deserializeaparamsstringintoanobject,optionallycoercingnumbers,
  //booleans,nullandundefinedvalues;thismethodisthecounterparttothe
  //internaljQuery.parammethod.
  //
  //Usage:
  //
  //>jQuery.deparam(params[,coerce]);
  //
  //Arguments:
  //
  // params-(String)Aparamsstringtobeparsed.
  // coerce-(Boolean)Iftrue,coercesanynumbersortrue,false,null,and
  //   undefinedtotheiractualvalue.Defaultstofalseifomitted.
  //
  //Returns:
  //
  // (Object)Anobjectrepresentingthedeserializedparamsstring.
  
  $.deparam=jq_deparam=function(params,coerce){
    varobj={},
      coerce_types={'true':!0,'false':!1,'null':null};
    
    //Iterateoverallname=valuepairs.
    $.each(params.replace(/\+/g,'').split('&'),function(j,v){
      varparam=v.split('='),
        key=decode(param[0]),
        val,
        cur=obj,
        i=0,
        
        //Ifkeyismorecomplexthan'foo',like'a[]'or'a[b][c]',splitit
        //intoitscomponentparts.
        keys=key.split(']['),
        keys_last=keys.length-1;
      
      //Ifthefirstkeyspartcontains[andthelastendswith],then[]
      //arecorrectlybalanced.
      if(/\[/.test(keys[0])&&/\]$/.test(keys[keys_last])){
        //Removethetrailing]fromthelastkeyspart.
        keys[keys_last]=keys[keys_last].replace(/\]$/,'');
        
        //Splitfirstkeyspartintotwopartsonthe[andaddthembackonto
        //thebeginningofthekeysarray.
        keys=keys.shift().split('[').concat(keys);
        
        keys_last=keys.length-1;
      }else{
        //Basic'foo'stylekey.
        keys_last=0;
      }
      
      //Arewedealingwithaname=valuepair,orjustaname?
      if(param.length===2){
        val=decode(param[1]);
        
        //Coercevalues.
        if(coerce){
          val=val&&!isNaN(val)           ?+val             //number
            :val==='undefined'            ?undefined        //undefined
            :coerce_types[val]!==undefined?coerce_types[val]//true,false,null
            :val;                                               //string
        }
        
        if(keys_last){
          //Complexkey,builddeepobjectstructurebasedonafewrules:
          //*The'cur'pointerstartsattheobjecttop-level.
          //*[]=arraypush(nissettoarraylength),[n]=arrayifnis
          //  numeric,otherwiseobject.
          //*Ifatthelastkeyspart,setthevalue.
          //*Foreachkeyspart,ifthecurrentlevelisundefinedcreatean
          //  objectorarraybasedonthetypeofthenextkeyspart.
          //*Movethe'cur'pointertothenextlevel.
          //*Rinse&repeat.
          for(;i<=keys_last;i++){
            key=keys[i]===''?cur.length:keys[i];
            if(key==="__proto__"||key==="prototype"||key==="constructor")break;
            cur=cur[key]=i<keys_last
              ?cur[key]||(keys[i+1]&&isNaN(keys[i+1])?{}:[])
              :val;
          }
          
        }else{
          //Simplekey,evensimplerrules,sinceonlyscalarsandshallow
          //arraysareallowed.
          
          if($.isArray(obj[key])){
            //valisalreadyanarray,sopushonthenextvalue.
            obj[key].push(val);
            
          }elseif(obj[key]!==undefined){
            //valisn'tanarray,butsinceasecondvaluehasbeenspecified,
            //convertvalintoanarray.
            obj[key]=[obj[key],val];
            
          }else{
            //valisascalar.
            obj[key]=val;
          }
        }
        
      }elseif(key){
        //Novaluewasdefined,sosetsomethingmeaningful.
        obj[key]=coerce
          ?undefined
          :'';
      }
    });
    
    returnobj;
  };
  
  //Method:jQuery.deparam.querystring
  //
  //ParsethequerystringfromaURLorthecurrentwindow.location.href,
  //deserializingitintoanobject,optionallycoercingnumbers,booleans,
  //nullandundefinedvalues.
  //
  //Usage:
  //
  //>jQuery.deparam.querystring([url][,coerce]);
  //
  //Arguments:
  //
  // url-(String)AnoptionalparamsstringorURLcontainingquerystring
  //   paramstobeparsed.Ifurlisomitted,thecurrent
  //   window.location.hrefisused.
  // coerce-(Boolean)Iftrue,coercesanynumbersortrue,false,null,and
  //   undefinedtotheiractualvalue.Defaultstofalseifomitted.
  //
  //Returns:
  //
  // (Object)Anobjectrepresentingthedeserializedparamsstring.
  
  //Method:jQuery.deparam.fragment
  //
  //Parsethefragment(hash)fromaURLorthecurrentwindow.location.href,
  //deserializingitintoanobject,optionallycoercingnumbers,booleans,
  //nullandundefinedvalues.
  //
  //Usage:
  //
  //>jQuery.deparam.fragment([url][,coerce]);
  //
  //Arguments:
  //
  // url-(String)AnoptionalparamsstringorURLcontainingfragment(hash)
  //   paramstobeparsed.Ifurlisomitted,thecurrentwindow.location.href
  //   isused.
  // coerce-(Boolean)Iftrue,coercesanynumbersortrue,false,null,and
  //   undefinedtotheiractualvalue.Defaultstofalseifomitted.
  //
  //Returns:
  //
  // (Object)Anobjectrepresentingthedeserializedparamsstring.
  
  functionjq_deparam_sub(is_fragment,url_or_params,coerce){
    if(url_or_params===undefined||typeofurl_or_params==='boolean'){
      //url_or_paramsnotspecified.
      coerce=url_or_params;
      url_or_params=jq_param[is_fragment?str_fragment:str_querystring]();
    }else{
      url_or_params=is_string(url_or_params)
        ?url_or_params.replace(is_fragment?re_params_fragment:re_params_querystring,'')
        :url_or_params;
    }
    
    returnjq_deparam(url_or_params,coerce);
  };
  
  jq_deparam[str_querystring]                   =curry(jq_deparam_sub,0);
  jq_deparam[str_fragment]=jq_deparam_fragment=curry(jq_deparam_sub,1);
  
  //Section:Elementmanipulation
  //
  //Method:jQuery.elemUrlAttr
  //
  //Gettheinternal"DefaultURLattributepertag"list,oraugmentthelist
  //withadditionaltag-attributepairs,incasethedefaultsareinsufficient.
  //
  //Inthe<jQuery.fn.querystring>and<jQuery.fn.fragment>methods,thislist
  //isusedtodeterminewhichattributecontainstheURLtobemodified,if
  //an"attr"paramisnotspecified.
  //
  //DefaultTag-AttributeList:
  //
  // a     -href
  // base  -href
  // iframe-src
  // img   -src
  // input -src
  // form  -action
  // link  -href
  // script-src
  //
  //Usage:
  //
  //>jQuery.elemUrlAttr([tag_attr]);
  //
  //Arguments:
  //
  // tag_attr-(Object)Anobjectcontainingalistoftagnamesandtheir
  //   associateddefaultattributenamesintheformat{tag:'attr',...}to
  //   bemergedintotheinternaltag-attributelist.
  //
  //Returns:
  //
  // (Object)Anobjectcontainingallstoredtag-attributevalues.
  
  //Onlydefinefunctionandsetdefaultsiffunctiondoesn'talreadyexist,as
  //theurlInternalpluginwillprovidethismethodaswell.
  $[str_elemUrlAttr]||($[str_elemUrlAttr]=function(obj){
    return$.extend(elemUrlAttr_cache,obj);
  })({
    a:str_href,
    base:str_href,
    iframe:str_src,
    img:str_src,
    input:str_src,
    form:'action',
    link:str_href,
    script:str_src
  });
  
  jq_elemUrlAttr=$[str_elemUrlAttr];
  
  //Method:jQuery.fn.querystring
  //
  //UpdateURLattributeinoneormoreelements,mergingthecurrentURL(with
  //orwithoutpre-existingquerystringparams)plusanyparamsobjector
  //stringintoanewURL,whichisthensetintothatattribute.Like
  //<jQuery.param.querystring(buildurl)>,butforallelementsinajQuery
  //collection.
  //
  //Usage:
  //
  //>jQuery('selector').querystring([attr,]params[,merge_mode]);
  //
  //Arguments:
  //
  // attr-(String)OptionalnameofanattributethatwillcontainaURLto
  //   mergeparamsorurlinto.See<jQuery.elemUrlAttr>foralistofdefault
  //   attributes.
  // params-(Object)AparamsobjecttobemergedintotheURLattribute.
  // params-(String)AURLcontainingquerystringparams,orparamsstring
  //   tobemergedintotheURLattribute.
  // merge_mode-(Number)Mergebehaviordefaultsto0ifmerge_modeisnot
  //   specified,andisas-follows:
  //   
  //   *0:paramsintheparamsargumentwilloverrideanyparamsinattrURL.
  //   *1:anyparamsinattrURLwilloverrideparamsintheparamsargument.
  //   *2:paramsargumentwillcompletelyreplaceanyquerystringinattr
  //        URL.
  //
  //Returns:
  //
  // (jQuery)TheinitialjQuerycollectionofelements,butwithmodifiedURL
  // attributevalues.
  
  //Method:jQuery.fn.fragment
  //
  //UpdateURLattributeinoneormoreelements,mergingthecurrentURL(with
  //orwithoutpre-existingfragment/hashparams)plusanyparamsobjector
  //stringintoanewURL,whichisthensetintothatattribute.Like
  //<jQuery.param.fragment(buildurl)>,butforallelementsinajQuery
  //collection.
  //
  //Usage:
  //
  //>jQuery('selector').fragment([attr,]params[,merge_mode]);
  //
  //Arguments:
  //
  // attr-(String)OptionalnameofanattributethatwillcontainaURLto
  //   mergeparamsinto.See<jQuery.elemUrlAttr>foralistofdefault
  //   attributes.
  // params-(Object)AparamsobjecttobemergedintotheURLattribute.
  // params-(String)AURLcontainingfragment(hash)params,orparams
  //   stringtobemergedintotheURLattribute.
  // merge_mode-(Number)Mergebehaviordefaultsto0ifmerge_modeisnot
  //   specified,andisas-follows:
  //   
  //   *0:paramsintheparamsargumentwilloverrideanyparamsinattrURL.
  //   *1:anyparamsinattrURLwilloverrideparamsintheparamsargument.
  //   *2:paramsargumentwillcompletelyreplaceanyfragment(hash)inattr
  //        URL.
  //
  //Returns:
  //
  // (jQuery)TheinitialjQuerycollectionofelements,butwithmodifiedURL
  // attributevalues.
  
  functionjq_fn_sub(mode,force_attr,params,merge_mode){
    if(!is_string(params)&&typeofparams!=='object'){
      //force_attrnotspecified.
      merge_mode=params;
      params=force_attr;
      force_attr=undefined;
    }
    
    returnthis.each(function(){
      varthat=$(this),
        
        //Getattributespecified,ordefaultspecifiedvia$.elemUrlAttr.
        attr=force_attr||jq_elemUrlAttr()[(this.nodeName||'').toLowerCase()]||'',
        
        //GetURLvalue.
        url=attr&&that.attr(attr)||'';
      
      //UpdateattributewithnewURL.
      that.attr(attr,jq_param[mode](url,params,merge_mode));
    });
    
  };
  
  $.fn[str_querystring]=curry(jq_fn_sub,str_querystring);
  $.fn[str_fragment]   =curry(jq_fn_sub,str_fragment);
  
  //Section:History,hashchangeevent
  //
  //Method:jQuery.bbq.pushState
  //
  //Addsa'state'intothebrowserhistoryatthecurrentposition,setting
  //location.hashandtriggeringanybound<hashchangeevent>callbacks
  //(providedthenewstateisdifferentthanthepreviousstate).
  //
  //Ifnoargumentsarepassed,anemptystateiscreated,whichisjusta
  //shortcutforjQuery.bbq.pushState({},2).
  //
  //Usage:
  //
  //>jQuery.bbq.pushState([params[,merge_mode]]);
  //
  //Arguments:
  //
  // params-(String)Aserializedparamsstringorahashstringbeginning
  //   with#tomergeintolocation.hash.
  // params-(Object)Aparamsobjecttomergeintolocation.hash.
  // merge_mode-(Number)Mergebehaviordefaultsto0ifmerge_modeisnot
  //   specified(unlessahashstringbeginningwith#isspecified,inwhich
  //   casemergebehaviordefaultsto2),andisas-follows:
  //
  //   *0:paramsintheparamsargumentwilloverrideanyparamsinthe
  //        currentstate.
  //   *1:anyparamsinthecurrentstatewilloverrideparamsintheparams
  //        argument.
  //   *2:paramsargumentwillcompletelyreplacecurrentstate.
  //
  //Returns:
  //
  // Nothing.
  //
  //AdditionalNotes:
  //
  // *Settinganemptystatemaycausethebrowsertoscroll.
  // *Unlikethefragmentandquerystringmethods,ifahashstringbeginning
  //   with#isspecifiedastheparamsagrument,merge_modedefaultsto2.
  
  jq_bbq.pushState=jq_bbq_pushState=function(params,merge_mode){
    if(is_string(params)&&/^#/.test(params)&&merge_mode===undefined){
      //Paramsstringbeginswith#andmerge_modenotspecified,socompletely
      //overwritewindow.location.hash.
      merge_mode=2;
    }
    
    varhas_args=params!==undefined,
      //Mergeparamsintowindow.locationusing$.param.fragment.
      url=jq_param_fragment(location.href,
        has_args?params:{},has_args?merge_mode:2);
    
    //Setnewwindow.location.href.NotethatSafari3&Chromebarfon
    //location.hash='#'sotheentireURLisset.
    location.href=url;
  };
  
  //Method:jQuery.bbq.getState
  //
  //Retrievesthecurrent'state'fromthebrowserhistory,parsing
  //location.hashforaspecifickeyorreturninganobjectcontainingthe
  //entirestate,optionallycoercingnumbers,booleans,nullandundefined
  //values.
  //
  //Usage:
  //
  //>jQuery.bbq.getState([key][,coerce]);
  //
  //Arguments:
  //
  // key-(String)Anoptionalstatekeyforwhichtoreturnavalue.
  // coerce-(Boolean)Iftrue,coercesanynumbersortrue,false,null,and
  //   undefinedtotheiractualvalue.Defaultstofalse.
  //
  //Returns:
  //
  // (Anything)Ifkeyispassed,returnsthevaluecorrespondingwiththatkey
  //   inthelocation.hash'state',orundefined.Ifnot,anobject
  //   representingtheentire'state'isreturned.
  
  jq_bbq.getState=jq_bbq_getState=function(key,coerce){
    returnkey===undefined||typeofkey==='boolean'
      ?jq_deparam_fragment(key)//'key'reallymeans'coerce'here
      :jq_deparam_fragment(coerce)[key];
  };
  
  //Method:jQuery.bbq.removeState
  //
  //Removeoneormorekeysfromthecurrentbrowserhistory'state',creating
  //anewstate,settinglocation.hashandtriggeringanybound
  //<hashchangeevent>callbacks(providedthenewstateisdifferentthan
  //thepreviousstate).
  //
  //Ifnoargumentsarepassed,anemptystateiscreated,whichisjusta
  //shortcutforjQuery.bbq.pushState({},2).
  //
  //Usage:
  //
  //>jQuery.bbq.removeState([key[,key...]]);
  //
  //Arguments:
  //
  // key-(String)Oneormorekeyvaluestoremovefromthecurrentstate,
  //   passedasindividualarguments.
  // key-(Array)Asinglearrayargumentthatcontainsalistofkeyvalues
  //   toremovefromthecurrentstate.
  //
  //Returns:
  //
  // Nothing.
  //
  //AdditionalNotes:
  //
  // *Settinganemptystatemaycausethebrowsertoscroll.
  
  jq_bbq.removeState=function(arr){
    varstate={};
    
    //Ifoneormoreargumentsispassed..
    if(arr!==undefined){
      
      //Getthecurrentstate.
      state=jq_bbq_getState();
      
      //Foreachpassedkey,deletethecorrespondingpropertyfromthecurrent
      //state.
      $.each($.isArray(arr)?arr:arguments,function(i,v){
        deletestate[v];
      });
    }
    
    //Setthestate,completelyoverridinganyexistingstate.
    jq_bbq_pushState(state,2);
  };
  
  //Event:hashchangeevent(BBQ)
  //
  //UsageinjQuery1.4andnewer:
  //
  //InjQuery1.4andnewer,theeventobjectpassedintoanyhashchangeevent
  //callbackisaugmentedwithacopyofthelocation.hashfragmentatthetime
  //theeventwastriggeredasitsevent.fragmentproperty.Inaddition,the
  //event.getStatemethodoperatesonthisproperty(insteadoflocation.hash)
  //whichallowsthisfragment-as-a-statetobereferencedlater,evenafter
  //window.locationmayhavechanged.
  //
  //Notethatevent.fragmentandevent.getStatearenotdefinedaccordingto
  //W3C(oranyother)specification,butwillstillbeavailablewhetheror
  //notthehashchangeeventexistsnativelyinthebrowser,becauseofthe
  //utilitytheyprovide.
  //
  //Theevent.fragmentpropertycontainstheoutputof<jQuery.param.fragment>
  //andtheevent.getStatemethodisequivalenttothe<jQuery.bbq.getState>
  //method.
  //
  //>$(window).bind('hashchange',function(event){
  //>  varhash_str=event.fragment,
  //>    param_obj=event.getState(),
  //>    param_val=event.getState('param_name'),
  //>    param_val_coerced=event.getState('param_name',true);
  //>  ...
  //>});
  //
  //UsageinjQuery1.3.2:
  //
  //InjQuery1.3.2,theeventobjectcannottobeaugmentedasinjQuery1.4+,
  //sothefragmentstateisn'tboundtotheeventobjectandmustinsteadbe
  //parsedusingthe<jQuery.param.fragment>and<jQuery.bbq.getState>methods.
  //
  //>$(window).bind('hashchange',function(event){
  //>  varhash_str=$.param.fragment(),
  //>    param_obj=$.bbq.getState(),
  //>    param_val=$.bbq.getState('param_name'),
  //>    param_val_coerced=$.bbq.getState('param_name',true);
  //>  ...
  //>});
  //
  //AdditionalNotes:
  //
  //*DuetochangesinthespecialeventsAPI,jQueryBBQv1.2orneweris
  //  requiredtoenabletheaugmentedeventobjectinjQuery1.4.2andnewer.
  //*See<jQueryhashchangeevent>formoredetailedinformation.
  
  special[str_hashchange]=$.extend(special[str_hashchange],{
    
    //Augmentingtheeventobjectwiththe.fragmentpropertyand.getState
    //methodrequiresjQuery1.4ornewer.Note:with1.3.2,everythingwill
    //work,buttheeventwon'tbeaugmented)
    add:function(handleObj){
      varold_handler;
      
      functionnew_handler(e){
        //e.fragmentissettothevalueoflocation.hash(withanyleading#
        //removed)atthetimetheeventistriggered.
        varhash=e[str_fragment]=jq_param_fragment();
        
        //e.getState()worksjustlike$.bbq.getState(),butusesthe
        //e.fragmentpropertystoredontheeventobject.
        e.getState=function(key,coerce){
          returnkey===undefined||typeofkey==='boolean'
            ?jq_deparam(hash,key)//'key'reallymeans'coerce'here
            :jq_deparam(hash,coerce)[key];
        };
        
        old_handler.apply(this,arguments);
      };
      
      //Thismayseemalittlecomplicated,butitnormalizesthespecialevent
      //.addmethodbetweenjQuery1.4/1.4.1and1.4.2+
      if($.isFunction(handleObj)){
        //1.4,1.4.1
        old_handler=handleObj;
        returnnew_handler;
      }else{
        //1.4.2+
        old_handler=handleObj.handler;
        handleObj.handler=new_handler;
      }
    }
    
  });
  
})(jQuery,this);

/*!
 *jQueryhashchangeevent-v1.3-7/21/2010
 *http://benalman.com/projects/jquery-hashchange-plugin/
 *
 *Copyright(c)2010"Cowboy"BenAlman
 *DuallicensedundertheMITandGPLlicenses.
 *http://benalman.com/about/license/
 */

//Script:jQueryhashchangeevent
//
//*Version:1.3,Lastupdated:7/21/2010*
//
//ProjectHome-http://benalman.com/projects/jquery-hashchange-plugin/
//GitHub      -http://github.com/cowboy/jquery-hashchange/
//Source      -http://github.com/cowboy/jquery-hashchange/raw/master/jquery.ba-hashchange.js
//(Minified)  -http://github.com/cowboy/jquery-hashchange/raw/master/jquery.ba-hashchange.min.js(0.8kbgzipped)
//
//About:License
//
//Copyright(c)2010"Cowboy"BenAlman,
//DuallicensedundertheMITandGPLlicenses.
//http://benalman.com/about/license/
//
//About:Examples
//
//Theseworkingexamples,completewithfullycommentedcode,illustrateafew
//waysinwhichthisplugincanbeused.
//
//hashchangeevent-http://benalman.com/code/projects/jquery-hashchange/examples/hashchange/
//document.domain-http://benalman.com/code/projects/jquery-hashchange/examples/document_domain/
//
//About:SupportandTesting
//
//InformationaboutwhatversionorversionsofjQuerythispluginhasbeen
//testedwith,whatbrowsersithasbeentestedin,andwheretheunittests
//reside(soyoucantestityourself).
//
//jQueryVersions-1.2.6,1.3.2,1.4.1,1.4.2
//BrowsersTested-InternetExplorer6-8,Firefox2-4,Chrome5-6,Safari3.2-5,
//                  Opera9.6-10.60,iPhone3.1,Android1.6-2.2,BlackBerry4.6-5.
//UnitTests     -http://benalman.com/code/projects/jquery-hashchange/unit/
//
//About:Knownissues
//
//WhilethisjQueryhashchangeeventimplementationisquitestableand
//robust,thereareafewunfortunatebrowserbugssurroundingexpected
//hashchangeevent-basedbehaviors,independentofanyJavaScript
//window.onhashchangeabstraction.Seethefollowingexamplesformore
//information:
//
//Chrome:BackButton-http://benalman.com/code/projects/jquery-hashchange/examples/bug-chrome-back-button/
//Firefox:RemoteXMLHttpRequest-http://benalman.com/code/projects/jquery-hashchange/examples/bug-firefox-remote-xhr/
//WebKit:BackButtoninanIframe-http://benalman.com/code/projects/jquery-hashchange/examples/bug-webkit-hash-iframe/
//Safari:BackButtonfromadifferentdomain-http://benalman.com/code/projects/jquery-hashchange/examples/bug-safari-back-from-diff-domain/
//
//Alsonotethatshouldabrowsernativelysupportthewindow.onhashchange
//event,butnotreportthatitdoes,thefallbackpollingloopwillbeused.
//
//About:ReleaseHistory
//
//1.3  -(7/21/2010)ReorganizedIE6/7Iframecodetomakeitmore
//        "removable"formobile-onlydevelopment.AddedIE6/7document.title
//        support.AttemptedtomakeIframeashiddenaspossiblebyusing
//        techniquesfromhttp://www.paciellogroup.com/blog/?p=604.Added
//        supportforthe"shortcut"format$(window).hashchange(fn)and
//        $(window).hashchange()likejQueryprovidesforbuilt-inevents.
//        RenamedjQuery.hashchangeDelayto<jQuery.fn.hashchange.delay>and
//        lowereditsdefaultvalueto50.Added<jQuery.fn.hashchange.domain>
//        and<jQuery.fn.hashchange.src>propertiesplusdocument-domain.html
//        filetoaddressaccessdeniedissueswhensettingdocument.domainin
//        IE6/7.
//1.2  -(2/11/2010)Fixedabugwherecomingbacktoapageusingthisplugin
//        fromapageonanotherdomainwouldcauseanerrorinSafari4.Also,
//        IE6/7Iframeisnowinsertedafterthebody(thisactuallyworks),
//        whichpreventsthepagefromscrollingwhentheeventisfirstbound.
//        EventcanalsonowbeboundbeforeDOMready,butitwon'tbeusable
//        beforetheninIE6/7.
//1.1  -(1/21/2010)Incorporateddocument.documentModetesttofixIE8bug
//        wherebrowserversionisincorrectlyreportedas8.0,despite
//        inclusionoftheX-UA-CompatibleIE=EmulateIE7metatag.
//1.0  -(1/9/2010)InitialRelease.BrokeoutthejQueryBBQevent.special
//        window.onhashchangefunctionalityintoaseparatepluginforusers
//        whowantjustthebasicevent&backbuttonsupport,withoutallthe
//        extraawesomenessthatBBQprovides.Thispluginwillbeincludedas
//        partofjQueryBBQ,butalsobeavailableseparately.

(function($,window,undefined){
  '$:nomunge';//UsedbyYUIcompressor.
  
  //Reusedstring.
  varstr_hashchange='hashchange',
    
    //Method/objectreferences.
    doc=document,
    fake_onhashchange,
    special=$.event.special,
    
    //Doesthebrowsersupportwindow.onhashchange?NotethatIE8runningin
    //IE7compatibilitymodereportstruefor'onhashchange'inwindow,even
    //thoughtheeventisn'tsupported,soalsotestdocument.documentMode.
    doc_mode=doc.documentMode,
    supports_onhashchange='on'+str_hashchangeinwindow&&(doc_mode===undefined||doc_mode>7);
  
  //Getlocation.hash(orwhatyou'dexpectlocation.hashtobe)sansany
  //leading#.Thanksformakingthisnecessary,Firefox!
  functionget_fragment(url){
    url=url||location.href;
    return'#'+url.replace(/^[^#]*#?(.*)$/,'$1');
  };
  
  //Method:jQuery.fn.hashchange
  //
  //Bindahandlertothewindow.onhashchangeeventortriggerallbound
  //window.onhashchangeeventhandlers.Thisbehaviorisconsistentwith
  //jQuery'sbuilt-ineventhandlers.
  //
  //Usage:
  //
  //>jQuery(window).hashchange([handler]);
  //
  //Arguments:
  //
  // handler-(Function)Optionalhandlertobeboundtothehashchange
  //   event.Thisisa"shortcut"forthemoreverboseform:
  //   jQuery(window).bind('hashchange',handler).Ifhandlerisomitted,
  //   allboundwindow.onhashchangeeventhandlerswillbetriggered.This
  //   isashortcutforthemoreverbose
  //   jQuery(window).trigger('hashchange').Theseformsaredescribedin
  //   the<hashchangeevent>section.
  //
  //Returns:
  //
  // (jQuery)TheinitialjQuerycollectionofelements.
  
  //Allowthe"shortcut"format$(elem).hashchange(fn)forbindingand
  //$(elem).hashchange()fortriggering,likejQuerydoesforbuilt-inevents.
  $.fn[str_hashchange]=function(fn){
    returnfn?this.bind(str_hashchange,fn):this.trigger(str_hashchange);
  };
  
  //Property:jQuery.fn.hashchange.delay
  //
  //Thenumericinterval(inmilliseconds)atwhichthe<hashchangeevent>
  //pollingloopexecutes.Defaultsto50.
  
  //Property:jQuery.fn.hashchange.domain
  //
  //Ifyou'resettingdocument.domaininyourJavaScript,andyouwanthash
  //historytoworkinIE6/7,notonlymustthispropertybeset,butyoumust
  //alsosetdocument.domainBEFOREjQueryisloadedintothepage.This
  //propertyisonlyapplicableifyouaresupportingIE6/7(orIE8operating
  //in"IE7compatibility"mode).
  //
  //Inaddition,the<jQuery.fn.hashchange.src>propertymustbesettothe
  //pathoftheincluded"document-domain.html"file,whichcanberenamedor
  //modifiedifnecessary(notethatthedocument.domainspecifiedmustbethe
  //sameinbothyourmainJavaScriptaswellasinthisfile).
  //
  //Usage:
  //
  //jQuery.fn.hashchange.domain=document.domain;
  
  //Property:jQuery.fn.hashchange.src
  //
  //If,forsomereason,youneedtospecifyanIframesrcfile(forexample,
  //whensettingdocument.domainasin<jQuery.fn.hashchange.domain>),youcan
  //dosousingthisproperty.Notethatwhenusingthisproperty,history
  //won'tberecordedinIE6/7untiltheIframesrcfileloads.Thisproperty
  //isonlyapplicableifyouaresupportingIE6/7(orIE8operatingin"IE7
  //compatibility"mode).
  //
  //Usage:
  //
  //jQuery.fn.hashchange.src='path/to/file.html';
  
  $.fn[str_hashchange].delay=50;
  /*
  $.fn[str_hashchange].domain=null;
  $.fn[str_hashchange].src=null;
  */
  
  //Event:hashchangeevent
  //
  //Firedwhenlocation.hashchanges.Inbrowsersthatsupportit,thenative
  //HTML5window.onhashchangeeventisused,otherwiseapollingloopis
  //initialized,runningevery<jQuery.fn.hashchange.delay>millisecondsto
  //seeifthehashhaschanged.InIE6/7(andIE8operatingin"IE7
  //compatibility"mode),ahiddenIframeiscreatedtoallowthebackbutton
  //andhash-basedhistorytowork.
  //
  //Usageasdescribedin<jQuery.fn.hashchange>:
  //
  //>//Bindaneventhandler.
  //>jQuery(window).hashchange(function(e){
  //>  varhash=location.hash;
  //>  ...
  //>});
  //>
  //>//Manuallytriggertheeventhandler.
  //>jQuery(window).hashchange();
  //
  //Amoreverboseusagethatallowsforeventnamespacing:
  //
  //>//Bindaneventhandler.
  //>jQuery(window).bind('hashchange',function(e){
  //>  varhash=location.hash;
  //>  ...
  //>});
  //>
  //>//Manuallytriggertheeventhandler.
  //>jQuery(window).trigger('hashchange');
  //
  //AdditionalNotes:
  //
  //*ThepollingloopandIframearenotcreateduntilatleastonehandler
  //  isactuallyboundtothe'hashchange'event.
  //*Ifyouneedtheboundhandler(s)toexecuteimmediately,incaseswhere
  //  alocation.hashexistsonpageload,viabookmarkorpagerefreshfor
  //  example,usejQuery(window).hashchange()orthemoreverbose
  //  jQuery(window).trigger('hashchange').
  //*TheeventcanbeboundbeforeDOMready,butsinceitwon'tbeusable
  //  beforetheninIE6/7(duetothenecessaryIframe),recommendedusageis
  //  tobinditinsideaDOMreadyhandler.
  
  //Overrideexisting$.event.special.hashchangemethods(allowingthisplugin
  //tobedefinedafterjQueryBBQinBBQ'ssourcecode).
  special[str_hashchange]=$.extend(special[str_hashchange],{
    
    //Calledonlywhenthefirst'hashchange'eventisboundtowindow.
    setup:function(){
      //Ifwindow.onhashchangeissupportednatively,there'snothingtodo..
      if(supports_onhashchange){returnfalse;}
      
      //Otherwise,weneedtocreateourown.Andwedon'twanttocallthis
      //untiltheuserbindstotheevent,justincasetheyneverdo,sinceit
      //willcreateapollingloopandpossiblyevenahiddenIframe.
      $(fake_onhashchange.start);
    },
    
    //Calledonlywhenthelast'hashchange'eventisunboundfromwindow.
    teardown:function(){
      //Ifwindow.onhashchangeissupportednatively,there'snothingtodo..
      if(supports_onhashchange){returnfalse;}
      
      //Otherwise,weneedtostopours(ifpossible).
      $(fake_onhashchange.stop);
    }
    
  });
  
  //fake_onhashchangedoesalltheworkoftriggeringthewindow.onhashchange
  //eventforbrowsersthatdon'tnativelysupportit,includingcreatinga
  //pollinglooptowatchforhashchangesandinIE6/7creatingahidden
  //Iframetoenablebackandforward.
  fake_onhashchange=(function(){
    varself={},
      timeout_id,
      
      //Remembertheinitialhashsoitdoesn'tgettriggeredimmediately.
      last_hash=get_fragment(),
      
      fn_retval=function(val){returnval;},
      history_set=fn_retval,
      history_get=fn_retval;
    
    //Startthepollingloop.
    self.start=function(){
      timeout_id||poll();
    };
    
    //Stopthepollingloop.
    self.stop=function(){
      timeout_id&&clearTimeout(timeout_id);
      timeout_id=undefined;
    };
    
    //Thispollingloopchecksevery$.fn.hashchange.delaymillisecondstosee
    //iflocation.hashhaschanged,andtriggersthe'hashchange'eventon
    //windowwhennecessary.
    functionpoll(){
      varhash=get_fragment(),
        history_hash=history_get(last_hash);
      
      if(hash!==last_hash){
        history_set(last_hash=hash,history_hash);
        
        $(window).trigger(str_hashchange);
        
      }elseif(history_hash!==last_hash){
        location.href=location.href.replace(/#.*/,'')+history_hash;
      }
      
      timeout_id=setTimeout(poll,$.fn[str_hashchange].delay);
    };
    
    //vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
    //vvvvvvvvvvvvvvvvvvvREMOVEIFNOTSUPPORTINGIE6/7/8vvvvvvvvvvvvvvvvvvv
    //vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
    $.browser.msie&&!supports_onhashchange&&(function(){
      //NotonlydoIE6/7needthe"magical"Iframetreatment,butsodoesIE8
      //whenrunningin"IE7compatibility"mode.
      
      variframe,
        iframe_src;
      
      //WhentheeventisboundandpollingstartsinIE6/7,createahidden
      //Iframeforhistoryhandling.
      self.start=function(){
        if(!iframe){
          iframe_src=$.fn[str_hashchange].src;
          iframe_src=iframe_src&&iframe_src+get_fragment();
          
          //CreatehiddenIframe.AttempttomakeIframeashiddenaspossible
          //byusingtechniquesfromhttp://www.paciellogroup.com/blog/?p=604.
          iframe=$('<iframetabindex="-1"title="empty"/>').hide()
            
            //WhenIframehascompletelyloaded,initializethehistoryand
            //startpolling.
            .one('load',function(){
              iframe_src||history_set(get_fragment());
              poll();
            })
            
            //LoadIframesrcifspecified,otherwisenothing.
            .attr('src',iframe_src||'javascript:0')
            
            //AppendIframeaftertheendofthebodytopreventunnecessary
            //initialpagescrolling(yes,thisworks).
            .insertAfter('body')[0].contentWindow;
          
          //Whenever`document.title`changes,updatetheIframe'stitleto
          //prettifytheback/nexthistorymenuentries.SinceIEsometimes
          //errorswith"Unspecifiederror"theveryfirsttimethisisset
          //(yes,veryuseful)wrapthiswithatry/catchblock.
          doc.onpropertychange=function(){
            try{
              if(event.propertyName==='title'){
                iframe.document.title=doc.title;
              }
            }catch(e){}
          };
          
        }
      };
      
      //Overridethe"stop"methodsinceanIE6/7Iframewascreated.Even
      //iftherearenolongeranyboundeventhandlers,thepollingloop
      //isstillnecessaryforback/nexttoworkatall!
      self.stop=fn_retval;
      
      //GethistorybylookingatthehiddenIframe'slocation.hash.
      history_get=function(){
        returnget_fragment(iframe.location.href);
      };
      
      //SetanewhistoryitembyopeningandthenclosingtheIframe
      //document,*then*settingitslocation.hash.Ifdocument.domainhas
      //beenset,updatethataswell.
      history_set=function(hash,history_hash){
        variframe_doc=iframe.document,
          domain=$.fn[str_hashchange].domain;
        
        if(hash!==history_hash){
          //UpdateIframewithanyinitial`document.title`thatmightbeset.
          iframe_doc.title=doc.title;
          
          //OpeningtheIframe'sdocumentafterithasbeenclosediswhat
          //actuallyaddsahistoryentry.
          iframe_doc.open();
          
          //Setdocument.domainfortheIframedocumentaswell,ifnecessary.
          domain&&iframe_doc.write('<script>document.domain="'+domain+'"</script>');
          
          iframe_doc.close();
          
          //UpdatetheIframe'shash,forgreatjustice.
          iframe.location.hash=hash;
        }
      };
      
    })();
    //^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    //^^^^^^^^^^^^^^^^^^^REMOVEIFNOTSUPPORTINGIE6/7/8^^^^^^^^^^^^^^^^^^^
    //^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    
    returnself;
  })();
  
})(jQuery,this);
