define([
  'summernote/core/agent',
  'summernote/core/dom'
],function(agent,dom){

  varCodeMirror;
  if(agent.hasCodeMirror){
    if(agent.isSupportAmd){
      require(['CodeMirror'],function(cm){
        CodeMirror=cm;
      });
    }else{
      CodeMirror=window.CodeMirror;
    }
  }

  /**
   *@classCodeview
   */
  varCodeview=function(handler){

    this.sync=function(layoutInfo){
      varisCodeview=handler.invoke('codeview.isActivated',layoutInfo);
      if(isCodeview&&agent.hasCodeMirror){
        layoutInfo.codable().data('cmEditor').save();
      }
    };

    /**
     *@param{Object}layoutInfo
     *@return{Boolean}
     */
    this.isActivated=function(layoutInfo){
      var$editor=layoutInfo.editor();
      return$editor.hasClass('codeview');
    };

    /**
     *togglecodeview
     *
     *@param{Object}layoutInfo
     */
    this.toggle=function(layoutInfo){
      if(this.isActivated(layoutInfo)){
        this.deactivate(layoutInfo);
      }else{
        this.activate(layoutInfo);
      }
    };

    /**
     *activatecodeview
     *
     *@param{Object}layoutInfo
     */
    this.activate=function(layoutInfo){
      var$editor=layoutInfo.editor(),
          $toolbar=layoutInfo.toolbar(),
          $editable=layoutInfo.editable(),
          $codable=layoutInfo.codable(),
          $popover=layoutInfo.popover(),
          $handle=layoutInfo.handle();

      varoptions=$editor.data('options');

      $codable.val(dom.html($editable,options.prettifyHtml));
      $codable.height($editable.height());

      handler.invoke('toolbar.updateCodeview',$toolbar,true);
      handler.invoke('popover.hide',$popover);
      handler.invoke('handle.hide',$handle);

      $editor.addClass('codeview');

      $codable.focus();

      //activateCodeMirrorascodable
      if(agent.hasCodeMirror){
        varcmEditor=CodeMirror.fromTextArea($codable[0],options.codemirror);

        //CodeMirrorTernServer
        if(options.codemirror.tern){
          varserver=newCodeMirror.TernServer(options.codemirror.tern);
          cmEditor.ternServer=server;
          cmEditor.on('cursorActivity',function(cm){
            server.updateArgHints(cm);
          });
        }

        //CodeMirrorhasn'tPadding.
        cmEditor.setSize(null,$editable.outerHeight());
        $codable.data('cmEditor',cmEditor);
      }
    };

    /**
     *deactivatecodeview
     *
     *@param{Object}layoutInfo
     */
    this.deactivate=function(layoutInfo){
      var$holder=layoutInfo.holder(),
          $editor=layoutInfo.editor(),
          $toolbar=layoutInfo.toolbar(),
          $editable=layoutInfo.editable(),
          $codable=layoutInfo.codable();

      varoptions=$editor.data('options');

      //deactivateCodeMirrorascodable
      if(agent.hasCodeMirror){
        varcmEditor=$codable.data('cmEditor');
        $codable.val(cmEditor.getValue());
        cmEditor.toTextArea();
      }

      varvalue=dom.value($codable,options.prettifyHtml)||dom.emptyPara;
      varisChange=$editable.html()!==value;

      $editable.html(value);
      $editable.height(options.height?$codable.height():'auto');
      $editor.removeClass('codeview');

      if(isChange){
        handler.bindCustomEvent(
          $holder,$editable.data('callbacks'),'change'
        )($editable.html(),$editable);
      }

      $editable.focus();

      handler.invoke('toolbar.updateCodeview',$toolbar,false);
    };
  };

  returnCodeview;
});
