//    Backbone.js1.1.0

//    (c)2010-2011JeremyAshkenas,DocumentCloudInc.
//    (c)2011-2013JeremyAshkenas,DocumentCloudandInvestigativeReporters&Editors
//    BackbonemaybefreelydistributedundertheMITlicense.
//    Foralldetailsanddocumentation:
//    http://backbonejs.org

(function(){

  //InitialSetup
  //-------------

  //Saveareferencetotheglobalobject(`window`inthebrowser,`exports`
  //ontheserver).
  varroot=this;

  //Savethepreviousvalueofthe`Backbone`variable,sothatitcanbe
  //restoredlateron,if`noConflict`isused.
  varpreviousBackbone=root.Backbone;

  //Createlocalreferencestoarraymethodswe'llwanttouselater.
  vararray=[];
  varpush=array.push;
  varslice=array.slice;
  varsplice=array.splice;

  //Thetop-levelnamespace.AllpublicBackboneclassesandmoduleswill
  //beattachedtothis.Exportedforboththebrowserandtheserver.
  varBackbone;
  if(typeofexports!=='undefined'){
    Backbone=exports;
  }else{
    Backbone=root.Backbone={};
  }

  //Currentversionofthelibrary.Keepinsyncwith`package.json`.
  Backbone.VERSION='1.1.0';

  //RequireUnderscore,ifwe'reontheserver,andit'snotalreadypresent.
  var_=root._;
  if(!_&&(typeofrequire!=='undefined'))_=require('underscore');

  //ForBackbone'spurposes,jQuery,Zepto,Ender,orMyLibrary(kidding)owns
  //the`$`variable.
  Backbone.$=root.jQuery||root.Zepto||root.ender||root.$;

  //RunsBackbone.jsin*noConflict*mode,returningthe`Backbone`variable
  //toitspreviousowner.ReturnsareferencetothisBackboneobject.
  Backbone.noConflict=function(){
    root.Backbone=previousBackbone;
    returnthis;
  };

  //Turnon`emulateHTTP`tosupportlegacyHTTPservers.Settingthisoption
  //willfake`"PATCH"`,`"PUT"`and`"DELETE"`requestsviathe`_method`parameterand
  //seta`X-Http-Method-Override`header.
  Backbone.emulateHTTP=false;

  //Turnon`emulateJSON`tosupportlegacyserversthatcan'tdealwithdirect
  //`application/json`requests...willencodethebodyas
  //`application/x-www-form-urlencoded`insteadandwillsendthemodelina
  //formparamnamed`model`.
  Backbone.emulateJSON=false;

  //Backbone.Events
  //---------------

  //Amodulethatcanbemixedinto*anyobject*inordertoprovideitwith
  //customevents.Youmaybindwith`on`orremovewith`off`callback
  //functionstoanevent;`trigger`-inganeventfiresallcallbacksin
  //succession.
  //
  //    varobject={};
  //    _.extend(object,Backbone.Events);
  //    object.on('expand',function(){alert('expanded');});
  //    object.trigger('expand');
  //
  varEvents=Backbone.Events={

    //Bindaneventtoa`callback`function.Passing`"all"`willbind
    //thecallbacktoalleventsfired.
    on:function(name,callback,context){
      if(!eventsApi(this,'on',name,[callback,context])||!callback)returnthis;
      this._events||(this._events={});
      varevents=this._events[name]||(this._events[name]=[]);
      events.push({callback:callback,context:context,ctx:context||this});
      returnthis;
    },

    //Bindaneventtoonlybetriggeredasingletime.Afterthefirsttime
    //thecallbackisinvoked,itwillberemoved.
    once:function(name,callback,context){
      if(!eventsApi(this,'once',name,[callback,context])||!callback)returnthis;
      varself=this;
      varonce=_.once(function(){
        self.off(name,once);
        callback.apply(this,arguments);
      });
      once._callback=callback;
      returnthis.on(name,once,context);
    },

    //Removeoneormanycallbacks.If`context`isnull,removesall
    //callbackswiththatfunction.If`callback`isnull,removesall
    //callbacksfortheevent.If`name`isnull,removesallbound
    //callbacksforallevents.
    off:function(name,callback,context){
      varretain,ev,events,names,i,l,j,k;
      if(!this._events||!eventsApi(this,'off',name,[callback,context]))returnthis;
      if(!name&&!callback&&!context){
        this._events={};
        returnthis;
      }
      names=name?[name]:_.keys(this._events);
      for(i=0,l=names.length;i<l;i++){
        name=names[i];
        if(events=this._events[name]){
          this._events[name]=retain=[];
          if(callback||context){
            for(j=0,k=events.length;j<k;j++){
              ev=events[j];
              if((callback&&callback!==ev.callback&&callback!==ev.callback._callback)||
                  (context&&context!==ev.context)){
                retain.push(ev);
              }
            }
          }
          if(!retain.length)deletethis._events[name];
        }
      }

      returnthis;
    },

    //Triggeroneormanyevents,firingallboundcallbacks.Callbacksare
    //passedthesameargumentsas`trigger`is,apartfromtheeventname
    //(unlessyou'relisteningon`"all"`,whichwillcauseyourcallbackto
    //receivethetruenameoftheeventasthefirstargument).
    trigger:function(name){
      if(!this._events)returnthis;
      varargs=slice.call(arguments,1);
      if(!eventsApi(this,'trigger',name,args))returnthis;
      varevents=this._events[name];
      varallEvents=this._events.all;
      if(events)triggerEvents(events,args);
      if(allEvents)triggerEvents(allEvents,arguments);
      returnthis;
    },

    //Tellthisobjecttostoplisteningtoeitherspecificevents...or
    //toeveryobjectit'scurrentlylisteningto.
    stopListening:function(obj,name,callback){
      varlisteningTo=this._listeningTo;
      if(!listeningTo)returnthis;
      varremove=!name&&!callback;
      if(!callback&&typeofname==='object')callback=this;
      if(obj)(listeningTo={})[obj._listenId]=obj;
      for(varidinlisteningTo){
        obj=listeningTo[id];
        obj.off(name,callback,this);
        if(remove||_.isEmpty(obj._events))deletethis._listeningTo[id];
      }
      returnthis;
    }

  };

  //Regularexpressionusedtospliteventstrings.
  vareventSplitter=/\s+/;

  //ImplementfancyfeaturesoftheEventsAPIsuchasmultipleevent
  //names`"changeblur"`andjQuery-styleeventmaps`{change:action}`
  //intermsoftheexistingAPI.
  vareventsApi=function(obj,action,name,rest){
    if(!name)returntrue;

    //Handleeventmaps.
    if(typeofname==='object'){
      for(varkeyinname){
        obj[action].apply(obj,[key,name[key]].concat(rest));
      }
      returnfalse;
    }

    //Handlespaceseparatedeventnames.
    if(eventSplitter.test(name)){
      varnames=name.split(eventSplitter);
      for(vari=0,l=names.length;i<l;i++){
        obj[action].apply(obj,[names[i]].concat(rest));
      }
      returnfalse;
    }

    returntrue;
  };

  //Adifficult-to-believe,butoptimizedinternaldispatchfunctionfor
  //triggeringevents.Triestokeeptheusualcasesspeedy(mostinternal
  //Backboneeventshave3arguments).
  vartriggerEvents=function(events,args){
    varev,i=-1,l=events.length,a1=args[0],a2=args[1],a3=args[2];
    switch(args.length){
      case0:while(++i<l)(ev=events[i]).callback.call(ev.ctx);return;
      case1:while(++i<l)(ev=events[i]).callback.call(ev.ctx,a1);return;
      case2:while(++i<l)(ev=events[i]).callback.call(ev.ctx,a1,a2);return;
      case3:while(++i<l)(ev=events[i]).callback.call(ev.ctx,a1,a2,a3);return;
      default:while(++i<l)(ev=events[i]).callback.apply(ev.ctx,args);
    }
  };

  varlistenMethods={listenTo:'on',listenToOnce:'once'};

  //Inversion-of-controlversionsof`on`and`once`.Tell*this*objectto
  //listentoaneventinanotherobject...keepingtrackofwhatit's
  //listeningto.
  _.each(listenMethods,function(implementation,method){
    Events[method]=function(obj,name,callback){
      varlisteningTo=this._listeningTo||(this._listeningTo={});
      varid=obj._listenId||(obj._listenId=_.uniqueId('l'));
      listeningTo[id]=obj;
      if(!callback&&typeofname==='object')callback=this;
      obj[implementation](name,callback,this);
      returnthis;
    };
  });

  //Aliasesforbackwardscompatibility.
  Events.bind  =Events.on;
  Events.unbind=Events.off;

  //Allowthe`Backbone`objecttoserveasaglobaleventbus,forfolkswho
  //wantglobal"pubsub"inaconvenientplace.
  _.extend(Backbone,Events);

  //Backbone.Model
  //--------------

  //Backbone**Models**arethebasicdataobjectintheframework--
  //frequentlyrepresentingarowinatableinadatabaseonyourserver.
  //Adiscretechunkofdataandabunchofuseful,relatedmethodsfor
  //performingcomputationsandtransformationsonthatdata.

  //Createanewmodelwiththespecifiedattributes.Aclientid(`cid`)
  //isautomaticallygeneratedandassignedforyou.
  varModel=Backbone.Model=function(attributes,options){
    varattrs=attributes||{};
    options||(options={});
    this.cid=_.uniqueId('c');
    this.attributes={};
    if(options.collection)this.collection=options.collection;
    if(options.parse)attrs=this.parse(attrs,options)||{};
    attrs=_.defaults({},attrs,_.result(this,'defaults'));
    this.set(attrs,options);
    this.changed={};
    this.initialize.apply(this,arguments);
  };

  //AttachallinheritablemethodstotheModelprototype.
  _.extend(Model.prototype,Events,{

    //Ahashofattributeswhosecurrentandpreviousvaluediffer.
    changed:null,

    //Thevaluereturnedduringthelastfailedvalidation.
    validationError:null,

    //ThedefaultnamefortheJSON`id`attributeis`"id"`.MongoDBand
    //CouchDBusersmaywanttosetthisto`"_id"`.
    idAttribute:'id',

    //Initializeisanemptyfunctionbydefault.Overrideitwithyourown
    //initializationlogic.
    initialize:function(){},

    //Returnacopyofthemodel's`attributes`object.
    toJSON:function(options){
      return_.clone(this.attributes);
    },

    //Proxy`Backbone.sync`bydefault--butoverridethisifyouneed
    //customsyncingsemanticsfor*this*particularmodel.
    sync:function(){
      returnBackbone.sync.apply(this,arguments);
    },

    //Getthevalueofanattribute.
    get:function(attr){
      returnthis.attributes[attr];
    },

    //GettheHTML-escapedvalueofanattribute.
    escape:function(attr){
      return_.escape(this.get(attr));
    },

    //Returns`true`iftheattributecontainsavaluethatisnotnull
    //orundefined.
    has:function(attr){
      returnthis.get(attr)!=null;
    },

    //Setahashofmodelattributesontheobject,firing`"change"`.Thisis
    //thecoreprimitiveoperationofamodel,updatingthedataandnotifying
    //anyonewhoneedstoknowaboutthechangeinstate.Theheartofthebeast.
    set:function(key,val,options){
      varattr,attrs,unset,changes,silent,changing,prev,current;
      if(key==null)returnthis;

      //Handleboth`"key",value`and`{key:value}`-stylearguments.
      if(typeofkey==='object'){
        attrs=key;
        options=val;
      }else{
        (attrs={})[key]=val;
      }

      options||(options={});

      //Runvalidation.
      if(!this._validate(attrs,options))returnfalse;

      //Extractattributesandoptions.
      unset          =options.unset;
      silent         =options.silent;
      changes        =[];
      changing       =this._changing;
      this._changing =true;

      if(!changing){
        this._previousAttributes=_.clone(this.attributes);
        this.changed={};
      }
      current=this.attributes,prev=this._previousAttributes;

      //Checkforchangesof`id`.
      if(this.idAttributeinattrs)this.id=attrs[this.idAttribute];

      //Foreach`set`attribute,updateordeletethecurrentvalue.
      for(attrinattrs){
        val=attrs[attr];
        if(!_.isEqual(current[attr],val))changes.push(attr);
        if(!_.isEqual(prev[attr],val)){
          this.changed[attr]=val;
        }else{
          deletethis.changed[attr];
        }
        unset?deletecurrent[attr]:current[attr]=val;
      }

      //Triggerallrelevantattributechanges.
      if(!silent){
        if(changes.length)this._pending=true;
        for(vari=0,l=changes.length;i<l;i++){
          this.trigger('change:'+changes[i],this,current[changes[i]],options);
        }
      }

      //Youmightbewonderingwhythere'sa`while`loophere.Changescan
      //berecursivelynestedwithin`"change"`events.
      if(changing)returnthis;
      if(!silent){
        while(this._pending){
          this._pending=false;
          this.trigger('change',this,options);
        }
      }
      this._pending=false;
      this._changing=false;
      returnthis;
    },

    //Removeanattributefromthemodel,firing`"change"`.`unset`isanoop
    //iftheattributedoesn'texist.
    unset:function(attr,options){
      returnthis.set(attr,void0,_.extend({},options,{unset:true}));
    },

    //Clearallattributesonthemodel,firing`"change"`.
    clear:function(options){
      varattrs={};
      for(varkeyinthis.attributes)attrs[key]=void0;
      returnthis.set(attrs,_.extend({},options,{unset:true}));
    },

    //Determineifthemodelhaschangedsincethelast`"change"`event.
    //Ifyouspecifyanattributename,determineifthatattributehaschanged.
    hasChanged:function(attr){
      if(attr==null)return!_.isEmpty(this.changed);
      return_.has(this.changed,attr);
    },

    //Returnanobjectcontainingalltheattributesthathavechanged,or
    //falseiftherearenochangedattributes.Usefulfordeterminingwhat
    //partsofaviewneedtobeupdatedand/orwhatattributesneedtobe
    //persistedtotheserver.Unsetattributeswillbesettoundefined.
    //Youcanalsopassanattributesobjecttodiffagainstthemodel,
    //determiningifthere*wouldbe*achange.
    changedAttributes:function(diff){
      if(!diff)returnthis.hasChanged()?_.clone(this.changed):false;
      varval,changed=false;
      varold=this._changing?this._previousAttributes:this.attributes;
      for(varattrindiff){
        if(_.isEqual(old[attr],(val=diff[attr])))continue;
        (changed||(changed={}))[attr]=val;
      }
      returnchanged;
    },

    //Getthepreviousvalueofanattribute,recordedatthetimethelast
    //`"change"`eventwasfired.
    previous:function(attr){
      if(attr==null||!this._previousAttributes)returnnull;
      returnthis._previousAttributes[attr];
    },

    //Getalloftheattributesofthemodelatthetimeoftheprevious
    //`"change"`event.
    previousAttributes:function(){
      return_.clone(this._previousAttributes);
    },

    //Fetchthemodelfromtheserver.Iftheserver'srepresentationofthe
    //modeldiffersfromitscurrentattributes,theywillbeoverridden,
    //triggeringa`"change"`event.
    fetch:function(options){
      options=options?_.clone(options):{};
      if(options.parse===void0)options.parse=true;
      varmodel=this;
      varsuccess=options.success;
      options.success=function(resp){
        if(!model.set(model.parse(resp,options),options))returnfalse;
        if(success)success(model,resp,options);
        model.trigger('sync',model,resp,options);
      };
      wrapError(this,options);
      returnthis.sync('read',this,options);
    },

    //Setahashofmodelattributes,andsyncthemodeltotheserver.
    //Iftheserverreturnsanattributeshashthatdiffers,themodel's
    //statewillbe`set`again.
    save:function(key,val,options){
      varattrs,method,xhr,attributes=this.attributes;

      //Handleboth`"key",value`and`{key:value}`-stylearguments.
      if(key==null||typeofkey==='object'){
        attrs=key;
        options=val;
      }else{
        (attrs={})[key]=val;
      }

      options=_.extend({validate:true},options);

      //Ifwe'renotwaitingandattributesexist,saveactsas
      //`set(attr).save(null,opts)`withvalidation.Otherwise,checkif
      //themodelwillbevalidwhentheattributes,ifany,areset.
      if(attrs&&!options.wait){
        if(!this.set(attrs,options))returnfalse;
      }else{
        if(!this._validate(attrs,options))returnfalse;
      }

      //Settemporaryattributesif`{wait:true}`.
      if(attrs&&options.wait){
        this.attributes=_.extend({},attributes,attrs);
      }

      //Afterasuccessfulserver-sidesave,theclientis(optionally)
      //updatedwiththeserver-sidestate.
      if(options.parse===void0)options.parse=true;
      varmodel=this;
      varsuccess=options.success;
      options.success=function(resp){
        //Ensureattributesarerestoredduringsynchronoussaves.
        model.attributes=attributes;
        varserverAttrs=model.parse(resp,options);
        if(options.wait)serverAttrs=_.extend(attrs||{},serverAttrs);
        if(_.isObject(serverAttrs)&&!model.set(serverAttrs,options)){
          returnfalse;
        }
        if(success)success(model,resp,options);
        model.trigger('sync',model,resp,options);
      };
      wrapError(this,options);

      method=this.isNew()?'create':(options.patch?'patch':'update');
      if(method==='patch')options.attrs=attrs;
      xhr=this.sync(method,this,options);

      //Restoreattributes.
      if(attrs&&options.wait)this.attributes=attributes;

      returnxhr;
    },

    //Destroythismodelontheserverifitwasalreadypersisted.
    //Optimisticallyremovesthemodelfromitscollection,ifithasone.
    //If`wait:true`ispassed,waitsfortheservertorespondbeforeremoval.
    destroy:function(options){
      options=options?_.clone(options):{};
      varmodel=this;
      varsuccess=options.success;

      vardestroy=function(){
        model.trigger('destroy',model,model.collection,options);
      };

      options.success=function(resp){
        if(options.wait||model.isNew())destroy();
        if(success)success(model,resp,options);
        if(!model.isNew())model.trigger('sync',model,resp,options);
      };

      if(this.isNew()){
        options.success();
        returnfalse;
      }
      wrapError(this,options);

      varxhr=this.sync('delete',this,options);
      if(!options.wait)destroy();
      returnxhr;
    },

    //DefaultURLforthemodel'srepresentationontheserver--ifyou're
    //usingBackbone'srestfulmethods,overridethistochangetheendpoint
    //thatwillbecalled.
    url:function(){
      varbase=_.result(this,'urlRoot')||_.result(this.collection,'url')||urlError();
      if(this.isNew())returnbase;
      returnbase+(base.charAt(base.length-1)==='/'?'':'/')+encodeURIComponent(this.id);
    },

    //**parse**convertsaresponseintothehashofattributestobe`set`on
    //themodel.Thedefaultimplementationisjusttopasstheresponsealong.
    parse:function(resp,options){
      returnresp;
    },

    //Createanewmodelwithidenticalattributestothisone.
    clone:function(){
      returnnewthis.constructor(this.attributes);
    },

    //Amodelisnewifithasneverbeensavedtotheserver,andlacksanid.
    isNew:function(){
      returnthis.id==null;
    },

    //Checkifthemodeliscurrentlyinavalidstate.
    isValid:function(options){
      returnthis._validate({},_.extend(options||{},{validate:true}));
    },

    //Runvalidationagainstthenextcompletesetofmodelattributes,
    //returning`true`ifalliswell.Otherwise,firean`"invalid"`event.
    _validate:function(attrs,options){
      if(!options.validate||!this.validate)returntrue;
      attrs=_.extend({},this.attributes,attrs);
      varerror=this.validationError=this.validate(attrs,options)||null;
      if(!error)returntrue;
      this.trigger('invalid',this,error,_.extend(options,{validationError:error}));
      returnfalse;
    }

  });

  //UnderscoremethodsthatwewanttoimplementontheModel.
  varmodelMethods=['keys','values','pairs','invert','pick','omit'];

  //MixineachUnderscoremethodasaproxyto`Model#attributes`.
  _.each(modelMethods,function(method){
    Model.prototype[method]=function(){
      varargs=slice.call(arguments);
      args.unshift(this.attributes);
      return_[method].apply(_,args);
    };
  });

  //Backbone.Collection
  //-------------------

  //Ifmodelstendtorepresentasinglerowofdata,aBackboneCollectionis
  //moreanalagoustoatablefullofdata...orasmallsliceorpageofthat
  //table,oracollectionofrowsthatbelongtogetherforaparticularreason
  //--allofthemessagesinthisparticularfolder,allofthedocuments
  //belongingtothisparticularauthor,andsoon.Collectionsmaintain
  //indexesoftheirmodels,bothinorder,andforlookupby`id`.

  //Createanew**Collection**,perhapstocontainaspecifictypeof`model`.
  //Ifa`comparator`isspecified,theCollectionwillmaintain
  //itsmodelsinsortorder,asthey'readdedandremoved.
  varCollection=Backbone.Collection=function(models,options){
    options||(options={});
    if(options.model)this.model=options.model;
    if(options.comparator!==void0)this.comparator=options.comparator;
    this._reset();
    this.initialize.apply(this,arguments);
    if(models)this.reset(models,_.extend({silent:true},options));
  };

  //Defaultoptionsfor`Collection#set`.
  varsetOptions={add:true,remove:true,merge:true};
  varaddOptions={add:true,remove:false};

  //DefinetheCollection'sinheritablemethods.
  _.extend(Collection.prototype,Events,{

    //Thedefaultmodelforacollectionisjusta**Backbone.Model**.
    //Thisshouldbeoverriddeninmostcases.
    model:Model,

    //Initializeisanemptyfunctionbydefault.Overrideitwithyourown
    //initializationlogic.
    initialize:function(){},

    //TheJSONrepresentationofaCollectionisanarrayofthe
    //models'attributes.
    toJSON:function(options){
      returnthis.map(function(model){returnmodel.toJSON(options);});
    },

    //Proxy`Backbone.sync`bydefault.
    sync:function(){
      returnBackbone.sync.apply(this,arguments);
    },

    //Addamodel,orlistofmodelstotheset.
    add:function(models,options){
      returnthis.set(models,_.extend({merge:false},options,addOptions));
    },

    //Removeamodel,oralistofmodelsfromtheset.
    remove:function(models,options){
      varsingular=!_.isArray(models);
      models=singular?[models]:_.clone(models);
      options||(options={});
      vari,l,index,model;
      for(i=0,l=models.length;i<l;i++){
        model=models[i]=this.get(models[i]);
        if(!model)continue;
        deletethis._byId[model.id];
        deletethis._byId[model.cid];
        index=this.indexOf(model);
        this.models.splice(index,1);
        this.length--;
        if(!options.silent){
          options.index=index;
          model.trigger('remove',model,this,options);
        }
        this._removeReference(model);
      }
      returnsingular?models[0]:models;
    },

    //Updateacollectionby`set`-inganewlistofmodels,addingnewones,
    //removingmodelsthatarenolongerpresent,andmergingmodelsthat
    //alreadyexistinthecollection,asnecessary.Similarto**Model#set**,
    //thecoreoperationforupdatingthedatacontainedbythecollection.
    set:function(models,options){
      options=_.defaults({},options,setOptions);
      if(options.parse)models=this.parse(models,options);
      varsingular=!_.isArray(models);
      models=singular?(models?[models]:[]):_.clone(models);
      vari,l,id,model,attrs,existing,sort;
      varat=options.at;
      vartargetModel=this.model;
      varsortable=this.comparator&&(at==null)&&options.sort!==false;
      varsortAttr=_.isString(this.comparator)?this.comparator:null;
      vartoAdd=[],toRemove=[],modelMap={};
      varadd=options.add,merge=options.merge,remove=options.remove;
      varorder=!sortable&&add&&remove?[]:false;

      //Turnbareobjectsintomodelreferences,andpreventinvalidmodels
      //frombeingadded.
      for(i=0,l=models.length;i<l;i++){
        attrs=models[i];
        if(attrsinstanceofModel){
          id=model=attrs;
        }else{
          id=attrs[targetModel.prototype.idAttribute];
        }

        //Ifaduplicateisfound,preventitfrombeingaddedand
        //optionallymergeitintotheexistingmodel.
        if(existing=this.get(id)){
          if(remove)modelMap[existing.cid]=true;
          if(merge){
            attrs=attrs===model?model.attributes:attrs;
            if(options.parse)attrs=existing.parse(attrs,options);
            existing.set(attrs,options);
            if(sortable&&!sort&&existing.hasChanged(sortAttr))sort=true;
          }
          models[i]=existing;

        //Ifthisisanew,validmodel,pushittothe`toAdd`list.
        }elseif(add){
          model=models[i]=this._prepareModel(attrs,options);
          if(!model)continue;
          toAdd.push(model);

          //Listentoaddedmodels'events,andindexmodelsforlookupby
          //`id`andby`cid`.
          model.on('all',this._onModelEvent,this);
          this._byId[model.cid]=model;
          if(model.id!=null)this._byId[model.id]=model;
        }
        if(order)order.push(existing||model);
      }

      //Removenonexistentmodelsifappropriate.
      if(remove){
        for(i=0,l=this.length;i<l;++i){
          if(!modelMap[(model=this.models[i]).cid])toRemove.push(model);
        }
        if(toRemove.length)this.remove(toRemove,options);
      }

      //Seeifsortingisneeded,update`length`andspliceinnewmodels.
      if(toAdd.length||(order&&order.length)){
        if(sortable)sort=true;
        this.length+=toAdd.length;
        if(at!=null){
          for(i=0,l=toAdd.length;i<l;i++){
            this.models.splice(at+i,0,toAdd[i]);
          }
        }else{
          if(order)this.models.length=0;
          varorderedModels=order||toAdd;
          for(i=0,l=orderedModels.length;i<l;i++){
            this.models.push(orderedModels[i]);
          }
        }
      }

      //Silentlysortthecollectionifappropriate.
      if(sort)this.sort({silent:true});

      //Unlesssilenced,it'stimetofireallappropriateadd/sortevents.
      if(!options.silent){
        for(i=0,l=toAdd.length;i<l;i++){
          (model=toAdd[i]).trigger('add',model,this,options);
        }
        if(sort||(order&&order.length))this.trigger('sort',this,options);
      }
      
      //Returntheadded(ormerged)model(ormodels).
      returnsingular?models[0]:models;
    },

    //Whenyouhavemoreitemsthanyouwanttoaddorremoveindividually,
    //youcanresettheentiresetwithanewlistofmodels,withoutfiring
    //anygranular`add`or`remove`events.Fires`reset`whenfinished.
    //Usefulforbulkoperationsandoptimizations.
    reset:function(models,options){
      options||(options={});
      for(vari=0,l=this.models.length;i<l;i++){
        this._removeReference(this.models[i]);
      }
      options.previousModels=this.models;
      this._reset();
      models=this.add(models,_.extend({silent:true},options));
      if(!options.silent)this.trigger('reset',this,options);
      returnmodels;
    },

    //Addamodeltotheendofthecollection.
    push:function(model,options){
      returnthis.add(model,_.extend({at:this.length},options));
    },

    //Removeamodelfromtheendofthecollection.
    pop:function(options){
      varmodel=this.at(this.length-1);
      this.remove(model,options);
      returnmodel;
    },

    //Addamodeltothebeginningofthecollection.
    unshift:function(model,options){
      returnthis.add(model,_.extend({at:0},options));
    },

    //Removeamodelfromthebeginningofthecollection.
    shift:function(options){
      varmodel=this.at(0);
      this.remove(model,options);
      returnmodel;
    },

    //Sliceoutasub-arrayofmodelsfromthecollection.
    slice:function(){
      returnslice.apply(this.models,arguments);
    },

    //Getamodelfromthesetbyid.
    get:function(obj){
      if(obj==null)returnvoid0;
      returnthis._byId[obj.id]||this._byId[obj.cid]||this._byId[obj];
    },

    //Getthemodelatthegivenindex.
    at:function(index){
      returnthis.models[index];
    },

    //Returnmodelswithmatchingattributes.Usefulforsimplecasesof
    //`filter`.
    where:function(attrs,first){
      if(_.isEmpty(attrs))returnfirst?void0:[];
      returnthis[first?'find':'filter'](function(model){
        for(varkeyinattrs){
          if(attrs[key]!==model.get(key))returnfalse;
        }
        returntrue;
      });
    },

    //Returnthefirstmodelwithmatchingattributes.Usefulforsimplecases
    //of`find`.
    findWhere:function(attrs){
      returnthis.where(attrs,true);
    },

    //Forcethecollectiontore-sortitself.Youdon'tneedtocallthisunder
    //normalcircumstances,asthesetwillmaintainsortorderaseachitem
    //isadded.
    sort:function(options){
      if(!this.comparator)thrownewError('Cannotsortasetwithoutacomparator');
      options||(options={});

      //Runsortbasedontypeof`comparator`.
      if(_.isString(this.comparator)||this.comparator.length===1){
        this.models=this.sortBy(this.comparator,this);
      }else{
        this.models.sort(_.bind(this.comparator,this));
      }

      if(!options.silent)this.trigger('sort',this,options);
      returnthis;
    },

    //Pluckanattributefromeachmodelinthecollection.
    pluck:function(attr){
      return_.invoke(this.models,'get',attr);
    },

    //Fetchthedefaultsetofmodelsforthiscollection,resettingthe
    //collectionwhentheyarrive.If`reset:true`ispassed,theresponse
    //datawillbepassedthroughthe`reset`methodinsteadof`set`.
    fetch:function(options){
      options=options?_.clone(options):{};
      if(options.parse===void0)options.parse=true;
      varsuccess=options.success;
      varcollection=this;
      options.success=function(resp){
        varmethod=options.reset?'reset':'set';
        collection[method](resp,options);
        if(success)success(collection,resp,options);
        collection.trigger('sync',collection,resp,options);
      };
      wrapError(this,options);
      returnthis.sync('read',this,options);
    },

    //Createanewinstanceofamodelinthiscollection.Addthemodeltothe
    //collectionimmediately,unless`wait:true`ispassed,inwhichcasewe
    //waitfortheservertoagree.
    create:function(model,options){
      options=options?_.clone(options):{};
      if(!(model=this._prepareModel(model,options)))returnfalse;
      if(!options.wait)this.add(model,options);
      varcollection=this;
      varsuccess=options.success;
      options.success=function(model,resp,options){
        if(options.wait)collection.add(model,options);
        if(success)success(model,resp,options);
      };
      model.save(null,options);
      returnmodel;
    },

    //**parse**convertsaresponseintoalistofmodelstobeaddedtothe
    //collection.Thedefaultimplementationisjusttopassitthrough.
    parse:function(resp,options){
      returnresp;
    },

    //Createanewcollectionwithanidenticallistofmodelsasthisone.
    clone:function(){
      returnnewthis.constructor(this.models);
    },

    //Privatemethodtoresetallinternalstate.Calledwhenthecollection
    //isfirstinitializedorreset.
    _reset:function(){
      this.length=0;
      this.models=[];
      this._byId ={};
    },

    //Prepareahashofattributes(orothermodel)tobeaddedtothis
    //collection.
    _prepareModel:function(attrs,options){
      if(attrsinstanceofModel){
        if(!attrs.collection)attrs.collection=this;
        returnattrs;
      }
      options=options?_.clone(options):{};
      options.collection=this;
      varmodel=newthis.model(attrs,options);
      if(!model.validationError)returnmodel;
      this.trigger('invalid',this,model.validationError,options);
      returnfalse;
    },

    //Internalmethodtoseveramodel'stiestoacollection.
    _removeReference:function(model){
      if(this===model.collection)deletemodel.collection;
      model.off('all',this._onModelEvent,this);
    },

    //Internalmethodcalledeverytimeamodelinthesetfiresanevent.
    //Setsneedtoupdatetheirindexeswhenmodelschangeids.Allother
    //eventssimplyproxythrough."add"and"remove"eventsthatoriginate
    //inothercollectionsareignored.
    _onModelEvent:function(event,model,collection,options){
      if((event==='add'||event==='remove')&&collection!==this)return;
      if(event==='destroy')this.remove(model,options);
      if(model&&event==='change:'+model.idAttribute){
        deletethis._byId[model.previous(model.idAttribute)];
        if(model.id!=null)this._byId[model.id]=model;
      }
      this.trigger.apply(this,arguments);
    }

  });

  //UnderscoremethodsthatwewanttoimplementontheCollection.
  //90%ofthecoreusefulnessofBackboneCollectionsisactuallyimplemented
  //righthere:
  varmethods=['forEach','each','map','collect','reduce','foldl',
    'inject','reduceRight','foldr','find','detect','filter','select',
    'reject','every','all','some','any','include','contains','invoke',
    'max','min','toArray','size','first','head','take','initial','rest',
    'tail','drop','last','without','difference','indexOf','shuffle',
    'lastIndexOf','isEmpty','chain'];

  //MixineachUnderscoremethodasaproxyto`Collection#models`.
  _.each(methods,function(method){
    Collection.prototype[method]=function(){
      varargs=slice.call(arguments);
      args.unshift(this.models);
      return_[method].apply(_,args);
    };
  });

  //Underscoremethodsthattakeapropertynameasanargument.
  varattributeMethods=['groupBy','countBy','sortBy'];

  //Useattributesinsteadofproperties.
  _.each(attributeMethods,function(method){
    Collection.prototype[method]=function(value,context){
      variterator=_.isFunction(value)?value:function(model){
        returnmodel.get(value);
      };
      return_[method](this.models,iterator,context);
    };
  });

  //Backbone.View
  //-------------

  //BackboneViewsarealmostmoreconventionthantheyareactualcode.AView
  //issimplyaJavaScriptobjectthatrepresentsalogicalchunkofUIinthe
  //DOM.Thismightbeasingleitem,anentirelist,asidebarorpanel,or
  //eventhesurroundingframewhichwrapsyourwholeapp.Definingachunkof
  //UIasa**View**allowsyoutodefineyourDOMeventsdeclaratively,without
  //havingtoworryaboutrenderorder...andmakesiteasyfortheviewto
  //reacttospecificchangesinthestateofyourmodels.

  //CreatingaBackbone.ViewcreatesitsinitialelementoutsideoftheDOM,
  //ifanexistingelementisnotprovided...
  varView=Backbone.View=function(options){
    this.cid=_.uniqueId('view');
    options||(options={});
    _.extend(this,_.pick(options,viewOptions));
    this._ensureElement();
    this.initialize.apply(this,arguments);
    this.delegateEvents();
  };

  //Cachedregextosplitkeysfor`delegate`.
  vardelegateEventSplitter=/^(\S+)\s*(.*)$/;

  //Listofviewoptionstobemergedasproperties.
  varviewOptions=['model','collection','el','id','attributes','className','tagName','events'];

  //Setupallinheritable**Backbone.View**propertiesandmethods.
  _.extend(View.prototype,Events,{

    //Thedefault`tagName`ofaView'selementis`"div"`.
    tagName:'div',

    //jQuerydelegateforelementlookup,scopedtoDOMelementswithinthe
    //currentview.Thisshouldbepreferredtogloballookupswherepossible.
    $:function(selector){
      returnthis.$el.find(selector);
    },

    //Initializeisanemptyfunctionbydefault.Overrideitwithyourown
    //initializationlogic.
    initialize:function(){},

    //**render**isthecorefunctionthatyourviewshouldoverride,inorder
    //topopulateitselement(`this.el`),withtheappropriateHTML.The
    //conventionisfor**render**toalwaysreturn`this`.
    render:function(){
      returnthis;
    },

    //RemovethisviewbytakingtheelementoutoftheDOM,andremovingany
    //applicableBackbone.Eventslisteners.
    remove:function(){
      this.$el.remove();
      this.stopListening();
      returnthis;
    },

    //Changetheview'selement(`this.el`property),includingevent
    //re-delegation.
    setElement:function(element,delegate){
      if(this.$el)this.undelegateEvents();
      this.$el=elementinstanceofBackbone.$?element:Backbone.$(element);
      this.el=this.$el[0];
      if(delegate!==false)this.delegateEvents();
      returnthis;
    },

    //Setcallbacks,where`this.events`isahashof
    //
    //*{"eventselector":"callback"}*
    //
    //    {
    //      'mousedown.title': 'edit',
    //      'click.button':    'save',
    //      'click.open':      function(e){...}
    //    }
    //
    //pairs.Callbackswillbeboundtotheview,with`this`setproperly.
    //Useseventdelegationforefficiency.
    //Omittingtheselectorbindstheeventto`this.el`.
    //Thisonlyworksfordelegate-ableevents:not`focus`,`blur`,and
    //not`change`,`submit`,and`reset`inInternetExplorer.
    delegateEvents:function(events){
      if(!(events||(events=_.result(this,'events'))))returnthis;
      this.undelegateEvents();
      for(varkeyinevents){
        varmethod=events[key];
        if(!_.isFunction(method))method=this[events[key]];
        if(!method)continue;

        varmatch=key.match(delegateEventSplitter);
        vareventName=match[1],selector=match[2];
        method=_.bind(method,this);
        eventName+='.delegateEvents'+this.cid;
        if(selector===''){
          this.$el.on(eventName,method);
        }else{
          this.$el.on(eventName,selector,method);
        }
      }
      returnthis;
    },

    //Clearsallcallbackspreviouslyboundtotheviewwith`delegateEvents`.
    //Youusuallydon'tneedtousethis,butmaywishtoifyouhavemultiple
    //BackboneviewsattachedtothesameDOMelement.
    undelegateEvents:function(){
      this.$el.off('.delegateEvents'+this.cid);
      returnthis;
    },

    //EnsurethattheViewhasaDOMelementtorenderinto.
    //If`this.el`isastring,passitthrough`$()`,takethefirst
    //matchingelement,andre-assignitto`el`.Otherwise,create
    //anelementfromthe`id`,`className`and`tagName`properties.
    _ensureElement:function(){
      if(!this.el){
        varattrs=_.extend({},_.result(this,'attributes'));
        if(this.id)attrs.id=_.result(this,'id');
        if(this.className)attrs['class']=_.result(this,'className');
        var$el=Backbone.$('<'+_.result(this,'tagName')+'>').attr(attrs);
        this.setElement($el,false);
      }else{
        this.setElement(_.result(this,'el'),false);
      }
    }

  });

  //Backbone.sync
  //-------------

  //OverridethisfunctiontochangethemannerinwhichBackbonepersists
  //modelstotheserver.Youwillbepassedthetypeofrequest,andthe
  //modelinquestion.Bydefault,makesaRESTfulAjaxrequest
  //tothemodel's`url()`.Somepossiblecustomizationscouldbe:
  //
  //*Use`setTimeout`tobatchrapid-fireupdatesintoasinglerequest.
  //*SendupthemodelsasXMLinsteadofJSON.
  //*PersistmodelsviaWebSocketsinsteadofAjax.
  //
  //Turnon`Backbone.emulateHTTP`inordertosend`PUT`and`DELETE`requests
  //as`POST`,witha`_method`parametercontainingthetrueHTTPmethod,
  //aswellasallrequestswiththebodyas`application/x-www-form-urlencoded`
  //insteadof`application/json`withthemodelinaparamnamed`model`.
  //Usefulwheninterfacingwithserver-sidelanguageslike**PHP**thatmake
  //itdifficulttoreadthebodyof`PUT`requests.
  Backbone.sync=function(method,model,options){
    vartype=methodMap[method];

    //Defaultoptions,unlessspecified.
    _.defaults(options||(options={}),{
      emulateHTTP:Backbone.emulateHTTP,
      emulateJSON:Backbone.emulateJSON
    });

    //DefaultJSON-requestoptions.
    varparams={type:type,dataType:'json'};

    //EnsurethatwehaveaURL.
    if(!options.url){
      params.url=_.result(model,'url')||urlError();
    }

    //Ensurethatwehavetheappropriaterequestdata.
    if(options.data==null&&model&&(method==='create'||method==='update'||method==='patch')){
      params.contentType='application/json';
      params.data=JSON.stringify(options.attrs||model.toJSON(options));
    }

    //Forolderservers,emulateJSONbyencodingtherequestintoanHTML-form.
    if(options.emulateJSON){
      params.contentType='application/x-www-form-urlencoded';
      params.data=params.data?{model:params.data}:{};
    }

    //Forolderservers,emulateHTTPbymimickingtheHTTPmethodwith`_method`
    //Andan`X-HTTP-Method-Override`header.
    if(options.emulateHTTP&&(type==='PUT'||type==='DELETE'||type==='PATCH')){
      params.type='POST';
      if(options.emulateJSON)params.data._method=type;
      varbeforeSend=options.beforeSend;
      options.beforeSend=function(xhr){
        xhr.setRequestHeader('X-HTTP-Method-Override',type);
        if(beforeSend)returnbeforeSend.apply(this,arguments);
      };
    }

    //Don'tprocessdataonanon-GETrequest.
    if(params.type!=='GET'&&!options.emulateJSON){
      params.processData=false;
    }

    //Ifwe'resendinga`PATCH`request,andwe'reinanoldInternetExplorer
    //thatstillhasActiveXenabledbydefault,overridejQuerytousethat
    //forXHRinstead.RemovethislinewhenjQuerysupports`PATCH`onIE8.
    if(params.type==='PATCH'&&noXhrPatch){
      params.xhr=function(){
        returnnewActiveXObject("Microsoft.XMLHTTP");
      };
    }

    //Maketherequest,allowingtheusertooverrideanyAjaxoptions.
    varxhr=options.xhr=Backbone.ajax(_.extend(params,options));
    model.trigger('request',model,xhr,options);
    returnxhr;
  };

  varnoXhrPatch=typeofwindow!=='undefined'&&!!window.ActiveXObject&&!(window.XMLHttpRequest&&(newXMLHttpRequest).dispatchEvent);

  //MapfromCRUDtoHTTPforourdefault`Backbone.sync`implementation.
  varmethodMap={
    'create':'POST',
    'update':'PUT',
    'patch': 'PATCH',
    'delete':'DELETE',
    'read':  'GET'
  };

  //Setthedefaultimplementationof`Backbone.ajax`toproxythroughto`$`.
  //Overridethisifyou'dliketouseadifferentlibrary.
  Backbone.ajax=function(){
    returnBackbone.$.ajax.apply(Backbone.$,arguments);
  };

  //Backbone.Router
  //---------------

  //Routersmapfaux-URLstoactions,andfireeventswhenroutesare
  //matched.Creatinganewonesetsits`routes`hash,ifnotsetstatically.
  varRouter=Backbone.Router=function(options){
    options||(options={});
    if(options.routes)this.routes=options.routes;
    this._bindRoutes();
    this.initialize.apply(this,arguments);
  };

  //Cachedregularexpressionsformatchingnamedparampartsandsplatted
  //partsofroutestrings.
  varoptionalParam=/\((.*?)\)/g;
  varnamedParam   =/(\(\?)?:\w+/g;
  varsplatParam   =/\*\w+/g;
  varescapeRegExp =/[\-{}\[\]+?.,\\\^$|#\s]/g;

  //Setupallinheritable**Backbone.Router**propertiesandmethods.
  _.extend(Router.prototype,Events,{

    //Initializeisanemptyfunctionbydefault.Overrideitwithyourown
    //initializationlogic.
    initialize:function(){},

    //Manuallybindasinglenamedroutetoacallback.Forexample:
    //
    //    this.route('search/:query/p:num','search',function(query,num){
    //      ...
    //    });
    //
    route:function(route,name,callback){
      if(!_.isRegExp(route))route=this._routeToRegExp(route);
      if(_.isFunction(name)){
        callback=name;
        name='';
      }
      if(!callback)callback=this[name];
      varrouter=this;
      Backbone.history.route(route,function(fragment){
        varargs=router._extractParameters(route,fragment);
        callback&&callback.apply(router,args);
        router.trigger.apply(router,['route:'+name].concat(args));
        router.trigger('route',name,args);
        Backbone.history.trigger('route',router,name,args);
      });
      returnthis;
    },

    //Simpleproxyto`Backbone.history`tosaveafragmentintothehistory.
    navigate:function(fragment,options){
      Backbone.history.navigate(fragment,options);
      returnthis;
    },

    //Bindalldefinedroutesto`Backbone.history`.Wehavetoreversethe
    //orderoftheroutesheretosupportbehaviorwherethemostgeneral
    //routescanbedefinedatthebottomoftheroutemap.
    _bindRoutes:function(){
      if(!this.routes)return;
      this.routes=_.result(this,'routes');
      varroute,routes=_.keys(this.routes);
      while((route=routes.pop())!=null){
        this.route(route,this.routes[route]);
      }
    },

    //Convertaroutestringintoaregularexpression,suitableformatching
    //againstthecurrentlocationhash.
    _routeToRegExp:function(route){
      route=route.replace(escapeRegExp,'\\$&')
                   .replace(optionalParam,'(?:$1)?')
                   .replace(namedParam,function(match,optional){
                     returnoptional?match:'([^\/]+)';
                   })
                   .replace(splatParam,'(.*?)');
      returnnewRegExp('^'+route+'$');
    },

    //Givenaroute,andaURLfragmentthatitmatches,returnthearrayof
    //extracteddecodedparameters.Emptyorunmatchedparameterswillbe
    //treatedas`null`tonormalizecross-browserbehavior.
    _extractParameters:function(route,fragment){
      varparams=route.exec(fragment).slice(1);
      return_.map(params,function(param){
        returnparam?decodeURIComponent(param):null;
      });
    }

  });

  //Backbone.History
  //----------------

  //Handlescross-browserhistorymanagement,basedoneither
  //[pushState](http://diveintohtml5.info/history.html)andrealURLs,or
  //[onhashchange](https://developer.mozilla.org/en-US/docs/DOM/window.onhashchange)
  //andURLfragments.Ifthebrowsersupportsneither(oldIE,natch),
  //fallsbacktopolling.
  varHistory=Backbone.History=function(){
    this.handlers=[];
    _.bindAll(this,'checkUrl');

    //Ensurethat`History`canbeusedoutsideofthebrowser.
    if(typeofwindow!=='undefined'){
      this.location=window.location;
      this.history=window.history;
    }
  };

  //Cachedregexforstrippingaleadinghash/slashandtrailingspace.
  varrouteStripper=/^[#\/]|\s+$/g;

  //Cachedregexforstrippingleadingandtrailingslashes.
  varrootStripper=/^\/+|\/+$/g;

  //CachedregexfordetectingMSIE.
  varisExplorer=/msie[\w.]+/;

  //Cachedregexforremovingatrailingslash.
  vartrailingSlash=/\/$/;

  //Cachedregexforstrippingurlsofhashandquery.
  varpathStripper=/[?#].*$/;

  //Hasthehistoryhandlingalreadybeenstarted?
  History.started=false;

  //Setupallinheritable**Backbone.History**propertiesandmethods.
  _.extend(History.prototype,Events,{

    //Thedefaultintervaltopollforhashchanges,ifnecessary,is
    //twentytimesasecond.
    interval:50,

    //Getsthetruehashvalue.Cannotuselocation.hashdirectlyduetobug
    //inFirefoxwherelocation.hashwillalwaysbedecoded.
    getHash:function(window){
      varmatch=(window||this).location.href.match(/#(.*)$/);
      returnmatch?match[1]:'';
    },

    //Getthecross-browsernormalizedURLfragment,eitherfromtheURL,
    //thehash,ortheoverride.
    getFragment:function(fragment,forcePushState){
      if(fragment==null){
        if(this._hasPushState||!this._wantsHashChange||forcePushState){
          fragment=this.location.pathname;
          varroot=this.root.replace(trailingSlash,'');
          if(!fragment.indexOf(root))fragment=fragment.slice(root.length);
        }else{
          fragment=this.getHash();
        }
      }
      returnfragment.replace(routeStripper,'');
    },

    //Startthehashchangehandling,returning`true`ifthecurrentURLmatches
    //anexistingroute,and`false`otherwise.
    start:function(options){
      if(History.started)thrownewError("Backbone.historyhasalreadybeenstarted");
      History.started=true;

      //Figureouttheinitialconfiguration.Doweneedaniframe?
      //IspushStatedesired...isitavailable?
      this.options         =_.extend({root:'/'},this.options,options);
      this.root            =this.options.root;
      this._wantsHashChange=this.options.hashChange!==false;
      this._wantsPushState =!!this.options.pushState;
      this._hasPushState   =!!(this.options.pushState&&this.history&&this.history.pushState);
      varfragment         =this.getFragment();
      vardocMode          =document.documentMode;
      varoldIE            =(isExplorer.exec(navigator.userAgent.toLowerCase())&&(!docMode||docMode<=7));

      //Normalizeroottoalwaysincludealeadingandtrailingslash.
      this.root=('/'+this.root+'/').replace(rootStripper,'/');

      if(oldIE&&this._wantsHashChange){
        this.iframe=Backbone.$('<iframesrc="javascript:0"tabindex="-1"/>').hide().appendTo('body')[0].contentWindow;
        this.navigate(fragment);
      }

      //Dependingonwhetherwe'reusingpushStateorhashes,andwhether
      //'onhashchange'issupported,determinehowwechecktheURLstate.
      if(this._hasPushState){
        Backbone.$(window).on('popstate',this.checkUrl);
      }elseif(this._wantsHashChange&&('onhashchange'inwindow)&&!oldIE){
        Backbone.$(window).on('hashchange',this.checkUrl);
      }elseif(this._wantsHashChange){
        this._checkUrlInterval=setInterval(this.checkUrl,this.interval);
      }

      //Determineifweneedtochangethebaseurl,forapushStatelink
      //openedbyanon-pushStatebrowser.
      this.fragment=fragment;
      varloc=this.location;
      varatRoot=loc.pathname.replace(/[^\/]$/,'$&/')===this.root;

      //TransitionfromhashChangetopushStateorviceversaifbothare
      //requested.
      if(this._wantsHashChange&&this._wantsPushState){

        //Ifwe'vestartedoffwitharoutefroma`pushState`-enabled
        //browser,butwe'recurrentlyinabrowserthatdoesn'tsupportit...
        if(!this._hasPushState&&!atRoot){
          this.fragment=this.getFragment(null,true);
          this.location.replace(this.root+this.location.search+'#'+this.fragment);
          //Returnimmediatelyasbrowserwilldoredirecttonewurl
          returntrue;

        //Orifwe'vestartedoutwithahash-basedroute,butwe'recurrently
        //inabrowserwhereitcouldbe`pushState`-basedinstead...
        }elseif(this._hasPushState&&atRoot&&loc.hash){
          this.fragment=this.getHash().replace(routeStripper,'');
          this.history.replaceState({},document.title,this.root+this.fragment+loc.search);
        }

      }

      if(!this.options.silent)returnthis.loadUrl();
    },

    //DisableBackbone.history,perhapstemporarily.Notusefulinarealapp,
    //butpossiblyusefulforunittestingRouters.
    stop:function(){
      Backbone.$(window).off('popstate',this.checkUrl).off('hashchange',this.checkUrl);
      clearInterval(this._checkUrlInterval);
      History.started=false;
    },

    //Addaroutetobetestedwhenthefragmentchanges.Routesaddedlater
    //mayoverridepreviousroutes.
    route:function(route,callback){
      this.handlers.unshift({route:route,callback:callback});
    },

    //ChecksthecurrentURLtoseeifithaschanged,andifithas,
    //calls`loadUrl`,normalizingacrossthehiddeniframe.
    checkUrl:function(e){
      varcurrent=this.getFragment();
      if(current===this.fragment&&this.iframe){
        current=this.getFragment(this.getHash(this.iframe));
      }
      if(current===this.fragment)returnfalse;
      if(this.iframe)this.navigate(current);
      this.loadUrl();
    },

    //AttempttoloadthecurrentURLfragment.Ifaroutesucceedswitha
    //match,returns`true`.Ifnodefinedroutesmatchesthefragment,
    //returns`false`.
    loadUrl:function(fragment){
      fragment=this.fragment=this.getFragment(fragment);
      return_.any(this.handlers,function(handler){
        if(handler.route.test(fragment)){
          handler.callback(fragment);
          returntrue;
        }
      });
    },

    //Saveafragmentintothehashhistory,orreplacetheURLstateifthe
    //'replace'optionispassed.YouareresponsibleforproperlyURL-encoding
    //thefragmentinadvance.
    //
    //Theoptionsobjectcancontain`trigger:true`ifyouwishtohavethe
    //routecallbackbefired(notusuallydesirable),or`replace:true`,if
    //youwishtomodifythecurrentURLwithoutaddinganentrytothehistory.
    navigate:function(fragment,options){
      if(!History.started)returnfalse;
      if(!options||options===true)options={trigger:!!options};

      varurl=this.root+(fragment=this.getFragment(fragment||''));

      //Stripthefragmentofthequeryandhashformatching.
      fragment=fragment.replace(pathStripper,'');

      if(this.fragment===fragment)return;
      this.fragment=fragment;

      //Don'tincludeatrailingslashontheroot.
      if(fragment===''&&url!=='/')url=url.slice(0,-1);

      //IfpushStateisavailable,weuseittosetthefragmentasarealURL.
      if(this._hasPushState){
        this.history[options.replace?'replaceState':'pushState']({},document.title,url);

      //Ifhashchangeshaven'tbeenexplicitlydisabled,updatethehash
      //fragmenttostorehistory.
      }elseif(this._wantsHashChange){
        this._updateHash(this.location,fragment,options.replace);
        if(this.iframe&&(fragment!==this.getFragment(this.getHash(this.iframe)))){
          //OpeningandclosingtheiframetricksIE7andearliertopusha
          //historyentryonhash-tagchange. Whenreplaceistrue,wedon't
          //wantthis.
          if(!options.replace)this.iframe.document.open().close();
          this._updateHash(this.iframe.location,fragment,options.replace);
        }

      //Ifyou'vetoldusthatyouexplicitlydon'twantfallbackhashchange-
      //basedhistory,then`navigate`becomesapagerefresh.
      }else{
        returnthis.location.assign(url);
      }
      if(options.trigger)returnthis.loadUrl(fragment);
    },

    //Updatethehashlocation,eitherreplacingthecurrententry,oradding
    //anewonetothebrowserhistory.
    _updateHash:function(location,fragment,replace){
      if(replace){
        varhref=location.href.replace(/(javascript:|#).*$/,'');
        location.replace(href+'#'+fragment);
      }else{
        //Somebrowsersrequirethat`hash`containsaleading#.
        location.hash='#'+fragment;
      }
    }

  });

  //CreatethedefaultBackbone.history.
  Backbone.history=newHistory;

  //Helpers
  //-------

  //Helperfunctiontocorrectlysetuptheprototypechain,forsubclasses.
  //Similarto`goog.inherits`,butusesahashofprototypepropertiesand
  //classpropertiestobeextended.
  varextend=function(protoProps,staticProps){
    varparent=this;
    varchild;

    //Theconstructorfunctionforthenewsubclassiseitherdefinedbyyou
    //(the"constructor"propertyinyour`extend`definition),ordefaulted
    //byustosimplycalltheparent'sconstructor.
    if(protoProps&&_.has(protoProps,'constructor')){
      child=protoProps.constructor;
    }else{
      child=function(){returnparent.apply(this,arguments);};
    }

    //Addstaticpropertiestotheconstructorfunction,ifsupplied.
    _.extend(child,parent,staticProps);

    //Settheprototypechaintoinheritfrom`parent`,withoutcalling
    //`parent`'sconstructorfunction.
    varSurrogate=function(){this.constructor=child;};
    Surrogate.prototype=parent.prototype;
    child.prototype=newSurrogate;

    //Addprototypeproperties(instanceproperties)tothesubclass,
    //ifsupplied.
    if(protoProps)_.extend(child.prototype,protoProps);

    //Setaconveniencepropertyincasetheparent'sprototypeisneeded
    //later.
    child.__super__=parent.prototype;

    returnchild;
  };

  //Setupinheritanceforthemodel,collection,router,viewandhistory.
  Model.extend=Collection.extend=Router.extend=View.extend=History.extend=extend;

  //ThrowanerrorwhenaURLisneeded,andnoneissupplied.
  varurlError=function(){
    thrownewError('A"url"propertyorfunctionmustbespecified');
  };

  //Wrapanoptionalerrorcallbackwithafallbackerrorevent.
  varwrapError=function(model,options){
    varerror=options.error;
    options.error=function(resp){
      if(error)error(model,resp,options);
      model.trigger('error',model,resp,options);
    };
  };

}).call(this);
