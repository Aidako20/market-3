define([
  'summernote/core/key'
],function(key){
  varImageDialog=function(handler){
    /**
     *togglebuttonstatus
     *
     *@private
     *@param{jQuery}$btn
     *@param{Boolean}isEnable
     */
    vartoggleBtn=function($btn,isEnable){
      $btn.toggleClass('disabled',!isEnable);
      $btn.attr('disabled',!isEnable);
    };

    /**
     *bindenterkey
     *
     *@private
     *@param{jQuery}$input
     *@param{jQuery}$btn
     */
    varbindEnterKey=function($input,$btn){
      $input.on('keypress',function(event){
        if(event.keyCode===key.code.ENTER){
          $btn.trigger('click');
        }
      });
    };

    this.show=function(layoutInfo){
      var$dialog=layoutInfo.dialog(),
          $editable=layoutInfo.editable();

      handler.invoke('editor.saveRange',$editable);
      this.showImageDialog($editable,$dialog).then(function(data){
        handler.invoke('editor.restoreRange',$editable);

        if(typeofdata==='string'){
          //imageurl
          handler.invoke('editor.insertImage',$editable,data);
        }else{
          //arrayoffiles
          handler.insertImages(layoutInfo,data);
        }
      }).fail(function(){
        handler.invoke('editor.restoreRange',$editable);
      });
    };

    /**
     *showimagedialog
     *
     *@param{jQuery}$editable
     *@param{jQuery}$dialog
     *@return{Promise}
     */
    this.showImageDialog=function($editable,$dialog){
      return$.Deferred(function(deferred){
        var$imageDialog=$dialog.find('.note-image-dialog');

        var$imageInput=$dialog.find('.note-image-input'),
            $imageUrl=$dialog.find('.note-image-url'),
            $imageBtn=$dialog.find('.note-image-btn');

        $imageDialog.one('shown.bs.modal',function(){
          //CloningimageInputtoclearelement.
          $imageInput.replaceWith($imageInput.clone()
            .on('change',function(){
              deferred.resolve(this.files||this.value);
              $imageDialog.modal('hide');
            })
            .val('')
          );

          $imageBtn.click(function(event){
            event.preventDefault();

            deferred.resolve($imageUrl.val());
            $imageDialog.modal('hide');
          });

          $imageUrl.on('keyuppaste',function(event){
            varurl;
            
            if(event.type==='paste'){
              url=event.originalEvent.clipboardData.getData('text');
            }else{
              url=$imageUrl.val();
            }
            
            toggleBtn($imageBtn,url);
          }).val('').trigger('focus');
          bindEnterKey($imageUrl,$imageBtn);
        }).one('hidden.bs.modal',function(){
          $imageInput.off('change');
          $imageUrl.off('keyuppastekeypress');
          $imageBtn.off('click');

          if(deferred.state()==='pending'){
            deferred.reject();
          }
        }).modal('show');
      });
    };
  };

  returnImageDialog;
});
