define([
  'summernote/core/agent',
  'summernote/core/func',
  'summernote/core/dom',
  'summernote/core/async',
  'summernote/core/key',
  'summernote/core/list',
  'summernote/editing/History',
  'summernote/module/Editor',
  'summernote/module/Toolbar',
  'summernote/module/Statusbar',
  'summernote/module/Popover',
  'summernote/module/Handle',
  'summernote/module/Fullscreen',
  'summernote/module/Codeview',
  'summernote/module/DragAndDrop',
  'summernote/module/Clipboard',
  'summernote/module/LinkDialog',
  'summernote/module/ImageDialog',
  'summernote/module/HelpDialog'
],function(agent,func,dom,async,key,list,History,
             Editor,Toolbar,Statusbar,Popover,Handle,Fullscreen,Codeview,
             DragAndDrop,Clipboard,LinkDialog,ImageDialog,HelpDialog){

  /**
   *@classEventHandler
   *
   *EventHandler
   * -TODO:newinstanceperaeditor
   */
  varEventHandler=function(){
    varself=this;

    /**
     *Modules
     */
    varmodules=this.modules={
      editor:newEditor(this),
      toolbar:newToolbar(this),
      statusbar:newStatusbar(this),
      popover:newPopover(this),
      handle:newHandle(this),
      fullscreen:newFullscreen(this),
      codeview:newCodeview(this),
      dragAndDrop:newDragAndDrop(this),
      clipboard:newClipboard(this),
      linkDialog:newLinkDialog(this),
      imageDialog:newImageDialog(this),
      helpDialog:newHelpDialog(this)
    };

    /**
     *invokemodule'smethod
     *
     *@param{String}moduleAndMethod-ex)'editor.redo'
     *@param{...*}arguments-argumentsofmethod
     *@return{*}
     */
    this.invoke=function(){
      varmoduleAndMethod=list.head(list.from(arguments));
      varargs=list.tail(list.from(arguments));

      varsplits=moduleAndMethod.split('.');
      varhasSeparator=splits.length>1;
      varmoduleName=hasSeparator&&list.head(splits);
      varmethodName=hasSeparator?list.last(splits):list.head(splits);

      varmodule=this.getModule(moduleName);
      varmethod=module[methodName];

      returnmethod&&method.apply(module,args);
    };

    /**
     *returnsmodule
     *
     *@param{String}moduleName-nameofmodule
     *@return{Module}-defaultsiseditor
     */
    this.getModule=function(moduleName){
      returnthis.modules[moduleName]||this.modules.editor;
    };

    /**
     *@param{jQuery}$holder
     *@param{Object}callbacks
     *@param{String}eventNamespace
     *@returns{Function}
     */
    varbindCustomEvent=this.bindCustomEvent=function($holder,callbacks,eventNamespace){
      returnfunction(){
        varcallback=callbacks[func.namespaceToCamel(eventNamespace,'on')];
        if(callback){
          callback.apply($holder[0],arguments);
        }
        return$holder.trigger('summernote.'+eventNamespace,arguments);
      };
    };

    /**
     *insertImagesfromfilearray.
     *
     *@private
     *@param{Object}layoutInfo
     *@param{File[]}files
     */
    this.insertImages=function(layoutInfo,files){
      var$editor=layoutInfo.editor(),
          $editable=layoutInfo.editable(),
          $holder=layoutInfo.holder();

      varcallbacks=$editable.data('callbacks');
      varoptions=$editor.data('options');

      //IfonImageUploadoptionssetted
      if(callbacks.onImageUpload){
        bindCustomEvent($holder,callbacks,'image.upload')(files);
      //elseinsertImageasdataURL
      }else{
        $.each(files,function(idx,file){
          varfilename=file.name;
          if(options.maximumImageFileSize&&options.maximumImageFileSize<file.size){
            bindCustomEvent($holder,callbacks,'image.upload.error')(options.langInfo.image.maximumFileSizeError);
          }else{
            async.readFileAsDataURL(file).then(function(sDataURL){
              modules.editor.insertImage($editable,sDataURL,filename);
            }).fail(function(){
              bindCustomEvent($holder,callbacks,'image.upload.error')(options.langInfo.image.maximumFileSizeError);
            });
          }
        });
      }
    };

    varcommands={
      /**
       *@param{Object}layoutInfo
       */
      showLinkDialog:function(layoutInfo){
        modules.linkDialog.show(layoutInfo);
      },

      /**
       *@param{Object}layoutInfo
       */
      showImageDialog:function(layoutInfo){
        modules.imageDialog.show(layoutInfo);
      },

      /**
       *@param{Object}layoutInfo
       */
      showHelpDialog:function(layoutInfo){
        modules.helpDialog.show(layoutInfo);
      },

      /**
       *@param{Object}layoutInfo
       */
      fullscreen:function(layoutInfo){
        modules.fullscreen.toggle(layoutInfo);
      },

      /**
       *@param{Object}layoutInfo
       */
      codeview:function(layoutInfo){
        modules.codeview.toggle(layoutInfo);
      }
    };

    varhMousedown=function(event){
      //preventDefaultSelectionforFF,IE8+
      if(dom.isImg(event.target)){
        event.preventDefault();
      }
    };

    varhKeyupAndMouseup=function(event){
      varlayoutInfo=dom.makeLayoutInfo(event.currentTarget||event.target);
      modules.editor.removeBogus(layoutInfo.editable());
      hToolbarAndPopoverUpdate(event);
    };

    /**
     *updatesytleinfo
     *@param{Object}styleInfo
     *@param{Object}layoutInfo
     */
    this.updateStyleInfo=function(styleInfo,layoutInfo){
      if(!styleInfo){
        return;
      }
      varisAirMode=(layoutInfo.editor().data('options')||{}).airMode;
      if(!isAirMode){
        modules.toolbar.update(layoutInfo.toolbar(),styleInfo);
      }

      modules.popover.update(layoutInfo.popover(),styleInfo,isAirMode);
      modules.handle.update(layoutInfo.handle(),styleInfo,isAirMode);
    };

    varhToolbarAndPopoverUpdate=function(event){
      vartarget=event.target;
      //delayforrangeaftermouseup
      setTimeout(function(){
        varlayoutInfo=dom.makeLayoutInfo(target);
        /*FLECTRA:(start_modification*/
        if(!layoutInfo){
            return;
        }
        var$editable=layoutInfo.editable();
        if(event.setStyleInfoFromEditable){
            varstyleInfo=modules.editor.styleFromNode($editable);
        }else{
            if(!event.isDefaultPrevented()){
              modules.editor.saveRange($editable);
            }
            varstyleInfo=modules.editor.currentStyle(target);
        }
        /*FLECTRA:end_modification)*/
        self.updateStyleInfo(styleInfo,layoutInfo);
      },0);
    };

    varhScroll=function(event){
      varlayoutInfo=dom.makeLayoutInfo(event.currentTarget||event.target);
      //hidepopoverandhandlewhenscrolled
      modules.popover.hide(layoutInfo.popover());
      modules.handle.hide(layoutInfo.handle());
    };

    varhToolbarAndPopoverMousedown=function(event){
      //preventdefaulteventwheninsertTable(FF,Webkit)
      var$btn=$(event.target).closest('[data-event]');
      if($btn.length){
        event.preventDefault();
      }
    };

    varhToolbarAndPopoverClick=function(event){
      var$btn=$(event.target).closest('[data-event]');

      if(!$btn.length){
        return;
      }

      vareventName=$btn.attr('data-event'),
          value=$btn.attr('data-value'),
          hide=$btn.attr('data-hide');

      varlayoutInfo=dom.makeLayoutInfo(event.target);

      //beforecommand:detectcontrolselectionelement($target)
      var$target;
      if($.inArray(eventName,['resize','floatMe','removeMedia','imageShape'])!==-1){
        var$selection=layoutInfo.handle().find('.note-control-selection');
        $target=$($selection.data('target'));
      }

      //Ifrequested,hidethepopoverwhenthebuttonisclicked.
      //UsefulforthingslikeshowHelpDialog.
      if(hide){
        $btn.parents('.popover').hide();
      }

      if($.isFunction($.summernote.pluginEvents[eventName])){
        $.summernote.pluginEvents[eventName](event,modules.editor,layoutInfo,value);
      }elseif(modules.editor[eventName]){//oncommand
        var$editable=layoutInfo.editable();
        $editable.focus();
        modules.editor[eventName]($editable,value,$target);
        event.preventDefault();
      }elseif(commands[eventName]){
        commands[eventName].call(this,layoutInfo);
        event.preventDefault();
      }

      //aftercommand
      if($.inArray(eventName,['backColor','foreColor'])!==-1){
        varoptions=layoutInfo.editor().data('options',options);
        varmodule=options.airMode?modules.popover:modules.toolbar;
        module.updateRecentColor(list.head($btn),eventName,value);
      }

      hToolbarAndPopoverUpdate(event);
    };

    varPX_PER_EM=18;
    varhDimensionPickerMove=function(event,options){
      var$picker=$(event.target.parentNode);//targetismousecatcher
      var$dimensionDisplay=$picker.next();
      var$catcher=$picker.find('.note-dimension-picker-mousecatcher');
      var$highlighted=$picker.find('.note-dimension-picker-highlighted');
      var$unhighlighted=$picker.find('.note-dimension-picker-unhighlighted');

      varposOffset;
      //HTML5withjQuery-e.offsetXisundefinedinFirefox
      if(event.offsetX===undefined){
        varposCatcher=$(event.target).offset();
        posOffset={
          x:event.pageX-posCatcher.left,
          y:event.pageY-posCatcher.top
        };
      }else{
        posOffset={
          x:event.offsetX,
          y:event.offsetY
        };
      }

      vardim={
        c:Math.ceil(posOffset.x/PX_PER_EM)||1,
        r:Math.ceil(posOffset.y/PX_PER_EM)||1
      };

      $highlighted.css({width:dim.c+'em',height:dim.r+'em'});
      $catcher.attr('data-value',dim.c+'x'+dim.r);

      if(3<dim.c&&dim.c<options.insertTableMaxSize.col){
        $unhighlighted.css({width:dim.c+1+'em'});
      }

      if(3<dim.r&&dim.r<options.insertTableMaxSize.row){
        $unhighlighted.css({height:dim.r+1+'em'});
      }

      $dimensionDisplay.html(dim.c+'x'+dim.r);
    };
    
    /**
     *bindKeyMaponkeydown
     *
     *@param{Object}layoutInfo
     *@param{Object}keyMap
     */
    this.bindKeyMap=function(layoutInfo,keyMap){
      var$editor=layoutInfo.editor();
      var$editable=layoutInfo.editable();

      $editable.on('keydown',function(event){
        varkeys=[];

        //modifier
        if(event.metaKey){keys.push('CMD');}
        if(event.ctrlKey&&!event.altKey){keys.push('CTRL');}
        if(event.shiftKey){keys.push('SHIFT');}

        //keycode
        varkeyName=key.nameFromCode[event.keyCode];
        if(keyName){
          keys.push(keyName);
        }

        varpluginEvent;
        varkeyString=keys.join('+');
        vareventName=keyMap[keyString];

        //FLECTRA:(start_modification
        //flectrachange:addvisibleeventtooverwritethebrowsercomportment
        varkeycode=event.keyCode;
        if(!eventName&&
            !event.ctrlKey&&!event.metaKey&&(//specialcode/command
            (keycode>47&&keycode<58)  ||//numberkeys
            keycode==32||keycode==13  ||//spacebar&return
            (keycode>64&&keycode<91)  ||//letterkeys
            (keycode>95&&keycode<112) ||//numpadkeys
            (keycode>185&&keycode<193)||//;=,-./`(inorder)
            (keycode>218&&keycode<223))){  //[\]'(inorder))
          eventName='visible';
        }elseif(!keycode&&event.key!=='Dead'){
          self.invoke('restoreRange',$editable);
        }
        //FLECTRA:end_modification)

        if(eventName){
          //FIXMESummernotedoesn'tsupporteventpipelineyet.
          // -Plugin->BaseCode
          pluginEvent=$.summernote.pluginEvents[keyString];
          if($.isFunction(pluginEvent)){
            if(pluginEvent(event,modules.editor,layoutInfo)){
              returnfalse;
            }
          }

          pluginEvent=$.summernote.pluginEvents[eventName];

          if($.isFunction(pluginEvent)){
            pluginEvent(event,modules.editor,layoutInfo);
          }elseif(modules.editor[eventName]){
            modules.editor[eventName]($editable,$editor.data('options'));
            event.preventDefault();
          }elseif(commands[eventName]){
            commands[eventName].call(this,layoutInfo);
            event.preventDefault();
          }
        }elseif(key.isEdit(event.keyCode)){
          modules.editor.afterCommand($editable);
        }
      });
    };

    /**
     *attacheventhandler
     *
     *@param{Object}layoutInfo-layoutInformations
     *@param{Object}options-useroptionsincludecustomeventhandlers
     */
    this.attach=function(layoutInfo,options){
      //handlersforeditable
      if(options.shortcuts){
        this.bindKeyMap(layoutInfo,options.keyMap[agent.isMac?'mac':'pc']);
      }
      layoutInfo.editable().on('mousedown',hMousedown);
      layoutInfo.editable().on('keyupmouseup',hKeyupAndMouseup);
      layoutInfo.editable().on('scroll',hScroll);

      //handlerforclipboard
      modules.clipboard.attach(layoutInfo,options);

      //handlerforhandleandpopover
      modules.handle.attach(layoutInfo,options);
      layoutInfo.popover().on('click',hToolbarAndPopoverClick);
      layoutInfo.popover().on('mousedown',hToolbarAndPopoverMousedown);

      //handlerfordraganddrop
      modules.dragAndDrop.attach(layoutInfo,options);

      //handlersforframemode(toolbar,statusbar)
      if(!options.airMode){
        //handlerfortoolbar
        layoutInfo.toolbar().on('click',hToolbarAndPopoverClick);
        layoutInfo.toolbar().on('mousedown',hToolbarAndPopoverMousedown);

        //handlerforstatusbar
        modules.statusbar.attach(layoutInfo,options);
      }

      //handlerfortabledimension
      var$catcherContainer=options.airMode?layoutInfo.popover():
                                                layoutInfo.toolbar();
      var$catcher=$catcherContainer.find('.note-dimension-picker-mousecatcher');
      $catcher.css({
        width:options.insertTableMaxSize.col+'em',
        height:options.insertTableMaxSize.row+'em'
      }).on('mousemove',function(event){
        hDimensionPickerMove(event,options);
      });

      //saveoptionsoneditor
      layoutInfo.editor().data('options',options);

      //retstyleWithCSSforbackColor/foreColorclearingwith'inherit'.
      if(!agent.isMSIE){
        //[workaround]forFirefox
        // -protectFFError:NS_ERROR_FAILURE:Failure
        setTimeout(function(){
          document.execCommand('styleWithCSS',0,options.styleWithSpan);
        },0);
      }

      //History
      varhistory=newHistory(layoutInfo.editable());
      layoutInfo.editable().data('NoteHistory',history);

      //Alleditorstatuswillbesavedoneditablewithjquery'sdata
      //forsupportmultipleeditorwithsingletonobject.
      layoutInfo.editable().data('callbacks',{
        onInit:options.onInit,
        onFocus:options.onFocus,
        onBlur:options.onBlur,
        onKeydown:options.onKeydown,
        onKeyup:options.onKeyup,
        onMousedown:options.onMousedown,
        onEnter:options.onEnter,
        onPaste:options.onPaste,
        onBeforeCommand:options.onBeforeCommand,
        onChange:options.onChange,
        onImageUpload:options.onImageUpload,
        onImageUploadError:options.onImageUploadError,
        onMediaDelete:options.onMediaDelete,
        onToolbarClick:options.onToolbarClick,
        onUpload:options.onUpload,
      });

      varstyleInfo=modules.editor.styleFromNode(layoutInfo.editable());
      this.updateStyleInfo(styleInfo,layoutInfo);
    };

    /**
     *attachjquerycustomevent
     *
     *@param{Object}layoutInfo-layoutInformations
     */
    this.attachCustomEvent=function(layoutInfo,options){
      var$holder=layoutInfo.holder();
      var$editable=layoutInfo.editable();
      varcallbacks=$editable.data('callbacks');

      $editable.focus(bindCustomEvent($holder,callbacks,'focus'));
      $editable.blur(bindCustomEvent($holder,callbacks,'blur'));

      $editable.keydown(function(event){
        if(event.keyCode===key.code.ENTER){
          bindCustomEvent($holder,callbacks,'enter').call(this,event);
        }
        bindCustomEvent($holder,callbacks,'keydown').call(this,event);
      });
      $editable.keyup(bindCustomEvent($holder,callbacks,'keyup'));

      $editable.on('mousedown',bindCustomEvent($holder,callbacks,'mousedown'));
      $editable.on('mouseup',bindCustomEvent($holder,callbacks,'mouseup'));
      $editable.on('scroll',bindCustomEvent($holder,callbacks,'scroll'));

      $editable.on('paste',bindCustomEvent($holder,callbacks,'paste'));
      
      //[workaround]IEdoesn'thaveinputeventsforcontentEditable
      // -see:https://goo.gl/4bfIvA
      varchangeEventName=agent.isMSIE?'DOMCharacterDataModifiedDOMSubtreeModifiedDOMNodeInserted':'input';
      $editable.on(changeEventName,function(){
        bindCustomEvent($holder,callbacks,'change')($editable.html(),$editable);
      });

      if(!options.airMode){
        layoutInfo.toolbar().click(bindCustomEvent($holder,callbacks,'toolbar.click'));
        layoutInfo.popover().click(bindCustomEvent($holder,callbacks,'popover.click'));
      }

      //Textarea:autofillingthecodebeforeformsubmit.
      if(dom.isTextarea(list.head($holder))){
        $holder.closest('form').submit(function(e){
          layoutInfo.holder().val(layoutInfo.holder().code());
          bindCustomEvent($holder,callbacks,'submit').call(this,e,$holder.code());
        });
      }

      //textareaautosync
      if(dom.isTextarea(list.head($holder))&&options.textareaAutoSync){
        $holder.on('summernote.change',function(){
          layoutInfo.holder().val(layoutInfo.holder().code());
        });
      }

      //fireinitevent
      bindCustomEvent($holder,callbacks,'init')(layoutInfo);

      //fireplugininitevent
      for(vari=0,len=$.summernote.plugins.length;i<len;i++){
        if($.isFunction($.summernote.plugins[i].init)){
          $.summernote.plugins[i].init(layoutInfo);
        }
      }
    };
      
    this.detach=function(layoutInfo,options){
      layoutInfo.holder().off();
      layoutInfo.editable().off();

      layoutInfo.popover().off();
      layoutInfo.handle().off();
      layoutInfo.dialog().off();

      if(!options.airMode){
        layoutInfo.dropzone().off();
        layoutInfo.toolbar().off();
        layoutInfo.statusbar().off();
      }
    };
  };

  returnEventHandler;
});
