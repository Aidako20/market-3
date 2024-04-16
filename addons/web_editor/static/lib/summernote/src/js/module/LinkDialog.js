define([
  'summernote/core/key'
],function(key){
  varLinkDialog=function(handler){

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

    /**
     *Showlinkdialogandseteventhandlersondialogcontrols.
     *
     *@param{jQuery}$editable
     *@param{jQuery}$dialog
     *@param{Object}linkInfo
     *@return{Promise}
     */
    this.showLinkDialog=function($editable,$dialog,linkInfo){
      return$.Deferred(function(deferred){
        var$linkDialog=$dialog.find('.note-link-dialog');

        var$linkText=$linkDialog.find('.note-link-text'),
        $linkUrl=$linkDialog.find('.note-link-url'),
        $linkBtn=$linkDialog.find('.note-link-btn'),
        $openInNewWindow=$linkDialog.find('input[type=checkbox]');

        $linkDialog.one('shown.bs.modal',function(){
          $linkText.val(linkInfo.text);

          $linkText.on('input',function(){
            toggleBtn($linkBtn,$linkText.val()&&$linkUrl.val());
            //iflinktextwasmodifiedbykeyup,
            //stopcloningtextfromlinkUrl
            linkInfo.text=$linkText.val();
          });

          //ifnourlwasgiven,copytexttourl
          if(!linkInfo.url){
            linkInfo.url=linkInfo.text||'http://';
            toggleBtn($linkBtn,linkInfo.text);
          }

          $linkUrl.on('input',function(){
            toggleBtn($linkBtn,$linkText.val()&&$linkUrl.val());
            //displaysamelinkon`Texttodisplay`input
            //whencreateanewlink
            if(!linkInfo.text){
              $linkText.val($linkUrl.val());
            }
          }).val(linkInfo.url).trigger('focus').trigger('select');

          bindEnterKey($linkUrl,$linkBtn);
          bindEnterKey($linkText,$linkBtn);

          $openInNewWindow.prop('checked',linkInfo.isNewWindow);

          $linkBtn.one('click',function(event){
            event.preventDefault();

            deferred.resolve({
              range:linkInfo.range,
              url:$linkUrl.val(),
              text:$linkText.val(),
              isNewWindow:$openInNewWindow.is(':checked')
            });
            $linkDialog.modal('hide');
          });
        }).one('hidden.bs.modal',function(){
          //detachevents
          $linkText.off('inputkeypress');
          $linkUrl.off('inputkeypress');
          $linkBtn.off('click');

          if(deferred.state()==='pending'){
            deferred.reject();
          }
        }).modal('show');
      }).promise();
    };

    /**
     *@param{Object}layoutInfo
     */
    this.show=function(layoutInfo){
      var$editor=layoutInfo.editor(),
          $dialog=layoutInfo.dialog(),
          $editable=layoutInfo.editable(),
          $popover=layoutInfo.popover(),
          linkInfo=handler.invoke('editor.getLinkInfo',$editable);

      varoptions=$editor.data('options');

      handler.invoke('editor.saveRange',$editable);
      this.showLinkDialog($editable,$dialog,linkInfo).then(function(linkInfo){
        handler.invoke('editor.restoreRange',$editable);
        handler.invoke('editor.createLink',$editable,linkInfo,options);
        //hidepopoveraftercreatinglink
        handler.invoke('popover.hide',$popover);
      }).fail(function(){
        handler.invoke('editor.restoreRange',$editable);
      });
    };
  };

  returnLinkDialog;
});
