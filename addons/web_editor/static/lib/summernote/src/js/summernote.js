define([
  'summernote/core/agent',
  'summernote/core/list',
  'summernote/core/dom',
  'summernote/core/range',
  'summernote/defaults',
  'summernote/EventHandler',
  'summernote/Renderer',
  'summernote/core/key'//FLECTRA:changeforoverride
],function(agent,list,dom,range,
             defaults,EventHandler,Renderer,key){

  //jQuerynamespaceforsummernote
  /**
   *@class$.summernote
   *
   *summernoteattribute 
   *
   *@mixindefaults
   *@singleton 
   *
   */
  $.summernote=$.summernote||{};

  //extendsdefaultsettings
  // -$.summernote.version
  // -$.summernote.options
  // -$.summernote.lang
  $.extend($.summernote,defaults);

  varrenderer=newRenderer();
  vareventHandler=newEventHandler();

  $.extend($.summernote,{
    /**@property{Renderer}*/
    renderer:renderer,
    /**@property{EventHandler}*/
    eventHandler:eventHandler,
    /**
     *@property{Object}core
     *@property{core.agent}core.agent
     *@property{core.dom}core.dom
     *@property{core.range}core.range
     */
    core:{
      agent:agent,
      list:list,
      dom:dom,
      range:range,
      key:key//FLECTRA:changeforoverride
    },
    /**
     *@property{Object}
     *pluginEventseventlistforplugins
     *eventhasnameandcallbackfunction.
     *
     *```
     *$.summernote.addPlugin({
     *    events:{
     *         'hello':function(layoutInfo,value,$target){
     *             console.log('eventnameishello,valueis'+value);
     *         }
     *    }    
     *})
     *```
     *
     **eventnameisdata-eventproperty.
     **layoutInfoisasummernotelayoutinformation.
     **valueisdata-valueproperty.
     */
    pluginEvents:{},

    plugins:[]
  });

  /**
   *@methodaddPlugin
   *
   *addPlugininSummernote
   *
   *Summernotecanmakeaownplugin.
   *
   *###Defineplugin
   *```
   *//gettemplatefunction 
   *vartmpl=$.summernote.renderer.getTemplate();
   *
   *//addabutton  
   *$.summernote.addPlugin({
   *    buttons:{
   *       //"hello" isbutton'snamespace.     
   *       "hello":function(lang,options){
   *           //makeiconbuttonbytemplatefunction         
   *           returntmpl.iconButton(options.iconPrefix+'header',{
   *               //callbackfunctionnamewhenbuttonclicked
   *               event:'hello',
   *               //setdata-valueproperty                
   *               value:'hello',               
   *               hide:true
   *           });          
   *       }
   *    
   *    },
   *    
   *    events:{
   *       "hello":function(layoutInfo,value){
   *           //hereiseventcode
   *       }
   *    }    
   *});
   *```
   *###Useapluginintoolbar
   *
   *```
   *   $("#editor").summernote({
   *   ...
   *   toolbar:[
   *       //displayhellopluginintoolbar    
   *       ['group',['hello']]
   *   ]
   *   ...   
   *   });
   *```
   * 
   * 
   *@param{Object}plugin
   *@param{Object}[plugin.buttons]definepluginbutton.fordetail,seetoRenderer.addButtonInfo
   *@param{Object}[plugin.dialogs]defineplugindialog.fordetail,seetoRenderer.addDialogInfo
   *@param{Object}[plugin.events]addeventin$.summernote.pluginEvents
   *@param{Object}[plugin.langs]update$.summernote.lang
   *@param{Object}[plugin.options]update$.summernote.options
   */
  $.summernote.addPlugin=function(plugin){

    //savepluginlist
    $.summernote.plugins.push(plugin);

    if(plugin.buttons){
      $.each(plugin.buttons,function(name,button){
        renderer.addButtonInfo(name,button);
      });
    }

    if(plugin.dialogs){
      $.each(plugin.dialogs,function(name,dialog){
        renderer.addDialogInfo(name,dialog);
      });
    }

    if(plugin.events){
      $.each(plugin.events,function(name,event){
        $.summernote.pluginEvents[name]=event;
      });
    }

    if(plugin.langs){
      $.each(plugin.langs,function(locale,lang){
        if($.summernote.lang[locale]){
          $.extend($.summernote.lang[locale],lang);
        }
      });
    }

    if(plugin.options){
      $.extend($.summernote.options,plugin.options);
    }
  };

  /*
   *extend$.fn
   */
  $.fn.extend({
    /**
     *@method
     *Initializesummernote
     * -createeditorlayoutandattachMouseandkeyboardevents.
     *
     *```
     *$("#summernote").summernote({options..});
     *```
     *  
     *@member$.fn
     *@param{Object|String}optionsreferenceto$.summernote.options
     *@return{this}
     */
    summernote:function(){
      //checkfirstargument'stype
      // -{String}:ExternalAPIcall{{module}}.{{method}}
      // -{Object}:initoptions
      vartype=$.type(list.head(arguments));
      varisExternalAPICalled=type==='string';
      varhasInitOptions=type==='object';

      //extenddefaultoptionswithcustomuseroptions
      varoptions=hasInitOptions?list.head(arguments):{};

      options=$.extend({},$.summernote.options,options);
      options.icons=$.extend({},$.summernote.options.icons,options.icons);

      //IncludelangInfoinoptionsforlateruse,e.g.forimagedrag-n-drop
      //Setuplanguageinfowithen-USasdefault
      options.langInfo=$.extend(true,{},$.summernote.lang['en-US'],$.summernote.lang[options.lang]);

      //overridepluginoptions
      if(!isExternalAPICalled&&hasInitOptions){
        for(vari=0,len=$.summernote.plugins.length;i<len;i++){
          varplugin=$.summernote.plugins[i];

          if(options.plugin[plugin.name]){
            $.summernote.plugins[i]=$.extend(true,plugin,options.plugin[plugin.name]);
          }
        }
      }

      this.each(function(idx,holder){
        var$holder=$(holder);

        //iflayoutisn'tcreatedyet,createLayoutandattachevents
        if(!renderer.hasNoteEditor($holder)){
          renderer.createLayout($holder,options);

          varlayoutInfo=renderer.layoutInfoFromHolder($holder);
          $holder.data('layoutInfo',layoutInfo);

          eventHandler.attach(layoutInfo,options);
          eventHandler.attachCustomEvent(layoutInfo,options);
        }
      });

      var$first=this.first();
      if($first.length){
        varlayoutInfo=renderer.layoutInfoFromHolder($first);

        //externalAPI
        if(isExternalAPICalled){
          varmoduleAndMethod=list.head(list.from(arguments));
          varargs=list.tail(list.from(arguments));

          //TODOnowexternalAPIonlyworksforeditor
          varparams=[moduleAndMethod,layoutInfo.editable()].concat(args);
          returneventHandler.invoke.apply(eventHandler,params);
        }elseif(options.focus){
          //focusonfirsteditableelementforinitializeeditor
          layoutInfo.editable().focus();
        }
      }

      returnthis;
    },

    /**
     *@method
     *
     *gettheHTMLcontentsofnoteorsettheHTMLcontentsofnote.
     *
     **getcontents
     *```
     *varcontent=$("#summernote").code();
     *```
     **setcontents
     *
     *```
     *$("#summernote").code(html);
     *```
     *
     *@member$.fn
     *@param{String}[html]-HTMLcontents(optional,set)
     *@return{this|String}-context(set)orHTMLcontentsofnote(get).
     */
    code:function(html){
      //gettheHTMLcontentsofnote
      if(html===undefined){
        var$holder=this.first();
        if(!$holder.length){
          return;
        }

        varlayoutInfo=renderer.layoutInfoFromHolder($holder);
        var$editable=layoutInfo&&layoutInfo.editable();

        if($editable&&$editable.length){
          varisCodeview=eventHandler.invoke('codeview.isActivated',layoutInfo);
          eventHandler.invoke('codeview.sync',layoutInfo);
          returnisCodeview?layoutInfo.codable().val():
                              layoutInfo.editable().html();
        }
        returndom.value($holder);
      }

      //settheHTMLcontentsofnote
      this.each(function(i,holder){
        varlayoutInfo=renderer.layoutInfoFromHolder($(holder));
        var$editable=layoutInfo&&layoutInfo.editable();
        if($editable){
          $editable.html(html);
        }
      });

      returnthis;
    },

    /**
     *@method
     *
     *destroyEditorLayoutanddetachKeyandMouseEvent
     *
     *@member$.fn
     *@return{this}
     */
    destroy:function(){
      this.each(function(idx,holder){
        var$holder=$(holder);

        if(!renderer.hasNoteEditor($holder)){
          return;
        }

        varinfo=renderer.layoutInfoFromHolder($holder);
        varoptions=info.editor().data('options');

        eventHandler.detach(info,options);
        renderer.removeLayout($holder,info,options);
      });

      returnthis;
    }
  });
});
