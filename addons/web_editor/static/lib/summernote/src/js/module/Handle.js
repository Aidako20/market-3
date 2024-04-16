define([
  'summernote/core/dom'
],function(dom){
  /**
   *@classmodule.Handle
   *
   *Handle
   */
  varHandle=function(handler){
    var$document=$(document);

    /**
     *`mousedown`eventhandleron$handle
     * -controlSizing:resizeimage
     *
     *@param{MouseEvent}event
     */
    varhHandleMousedown=function(event){
      if(dom.isControlSizing(event.target)){
        event.preventDefault();
        event.stopPropagation();

        varlayoutInfo=dom.makeLayoutInfo(event.target),
            $handle=layoutInfo.handle(),
            $popover=layoutInfo.popover(),
            $editable=layoutInfo.editable(),
            $editor=layoutInfo.editor();

        vartarget=$handle.find('.note-control-selection').data('target'),
            $target=$(target),posStart=$target.offset(),
            scrollTop=$document.scrollTop();

        varisAirMode=$editor.data('options').airMode;

        $document.on('mousemove',function(event){
          handler.invoke('editor.resizeTo',{
            x:event.clientX-posStart.left,
            y:event.clientY-(posStart.top-scrollTop)
          },$target,!event.shiftKey);

          handler.invoke('handle.update',$handle,{image:target},isAirMode);
          handler.invoke('popover.update',$popover,{image:target},isAirMode);
        }).one('mouseup',function(){
          $document.off('mousemove');
          handler.invoke('editor.afterCommand',$editable);
        });

        if(!$target.data('ratio')){//originalratio.
          $target.data('ratio',$target.height()/$target.width());
        }
      }
    };

    this.attach=function(layoutInfo){
      layoutInfo.handle().on('mousedown',hHandleMousedown);
    };

    /**
     *updatehandle
     *@param{jQuery}$handle
     *@param{Object}styleInfo
     *@param{Boolean}isAirMode
     */
    this.update=function($handle,styleInfo,isAirMode){
      var$selection=$handle.find('.note-control-selection');
      if(styleInfo.image){
        var$image=$(styleInfo.image);
        varpos=isAirMode?$image.offset():$image.position();

        //includemargin
        varimageSize={
          w:$image.outerWidth(true),
          h:$image.outerHeight(true)
        };

        $selection.css({
          display:'block',
          left:pos.left,
          top:pos.top,
          width:imageSize.w,
          height:imageSize.h
        }).data('target',styleInfo.image);//savecurrentimageelement.
        varsizingText=imageSize.w+'x'+imageSize.h;
        $selection.find('.note-control-selection-info').text(sizingText);
      }else{
        $selection.hide();
      }
    };

    /**
     *hide
     *
     *@param{jQuery}$handle
     */
    this.hide=function($handle){
      $handle.children().hide();
    };
  };

  returnHandle;
});
