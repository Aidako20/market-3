define([
  'summernote/core/dom'
],function(dom){
  varDragAndDrop=function(handler){
    var$document=$(document);

    /**
     *attachDragandDropEvents
     *
     *@param{Object}layoutInfo-layoutInformations
     *@param{Object}options
     */
    this.attach=function(layoutInfo,options){
      if(options.airMode||options.disableDragAndDrop){
        //preventdefaultdropevent
        $document.on('drop',function(e){
          e.preventDefault();
        });
      }else{
        this.attachDragAndDropEvent(layoutInfo,options);
      }
    };

    /**
     *attachDragandDropEvents
     *
     *@param{Object}layoutInfo-layoutInformations
     *@param{Object}options
     */
    this.attachDragAndDropEvent=function(layoutInfo,options){
      varcollection=$(),
          $editor=layoutInfo.editor(),
          $dropzone=layoutInfo.dropzone(),
          $dropzoneMessage=$dropzone.find('.note-dropzone-message');

      //showdropzoneondragenterwhendraggingaobjecttodocument
      //-butonlyiftheeditorisvisible,i.e.hasapositivewidthandheight
      $document.on('dragenter',function(e){
        varisCodeview=handler.invoke('codeview.isActivated',layoutInfo);
        varhasEditorSize=$editor.width()>0&&$editor.height()>0;
        if(!isCodeview&&!collection.length&&hasEditorSize){
          $editor.addClass('dragover');
          $dropzone.width($editor.width());
          $dropzone.height($editor.height());
          $dropzoneMessage.text(options.langInfo.image.dragImageHere);
        }
        collection=collection.add(e.target);
      }).on('dragleave',function(e){
        collection=collection.not(e.target);
        if(!collection.length){
          $editor.removeClass('dragover');
        }
      }).on('drop',function(){
        collection=$();
        $editor.removeClass('dragover');
      });

      //changedropzone'smessageonhover.
      $dropzone.on('dragenter',function(){
        $dropzone.addClass('hover');
        $dropzoneMessage.text(options.langInfo.image.dropImage);
      }).on('dragleave',function(){
        $dropzone.removeClass('hover');
        $dropzoneMessage.text(options.langInfo.image.dragImageHere);
      });

      //attachdropImage
      $dropzone.on('drop',function(event){

        vardataTransfer=event.originalEvent.dataTransfer;
        varlayoutInfo=dom.makeLayoutInfo(event.currentTarget||event.target);

        /*FLECTRA:start_modification*/
        event.preventDefault();
        /*FLECTRA:end_modification*/

        if(dataTransfer&&dataTransfer.files&&dataTransfer.files.length){
          event.preventDefault();
          layoutInfo.editable().focus();
          handler.insertImages(layoutInfo,dataTransfer.files);
        }else{
          varinsertNodefunc=function(){
            layoutInfo.holder().summernote('insertNode',this);
          };

          for(vari=0,len=dataTransfer.types.length;i<len;i++){
            vartype=dataTransfer.types[i];
            varcontent=dataTransfer.getData(type);

            /*FLECTRA:start_modification*/
            if(type.toLowerCase().indexOf('_moz_')>-1){
              return;
            }
            /*FLECTRA:end_modification*/

            if(type.toLowerCase().indexOf('text')>-1){
              layoutInfo.holder().summernote('pasteHTML',content);
            }else{
              $(content).each(insertNodefunc);
            }
          }
        }
      }).on('dragover',false);//preventdefaultdragoverevent
    };
  };

  returnDragAndDrop;
});
