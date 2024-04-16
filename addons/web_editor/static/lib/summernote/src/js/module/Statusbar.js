define([
  'summernote/core/dom'
],function(dom){
  varEDITABLE_PADDING=24;

  varStatusbar=function(){
    var$document=$(document);

    this.attach=function(layoutInfo,options){
      if(!options.disableResizeEditor){
        layoutInfo.statusbar().on('mousedown',hStatusbarMousedown);
      }
    };

    /**
     *`mousedown`eventhandleronstatusbar
     *
     *@param{MouseEvent}event
     */
    varhStatusbarMousedown=function(event){
      event.preventDefault();
      event.stopPropagation();

      var$editable=dom.makeLayoutInfo(event.target).editable();
      vareditableTop=$editable.offset().top-$document.scrollTop();

      varlayoutInfo=dom.makeLayoutInfo(event.currentTarget||event.target);
      varoptions=layoutInfo.editor().data('options');

      $document.on('mousemove',function(event){
        varnHeight=event.clientY-(editableTop+EDITABLE_PADDING);

        nHeight=(options.minHeight>0)?Math.max(nHeight,options.minHeight):nHeight;
        nHeight=(options.maxHeight>0)?Math.min(nHeight,options.maxHeight):nHeight;

        $editable.height(nHeight);
      }).one('mouseup',function(){
        $document.off('mousemove');
      });
    };
  };

  returnStatusbar;
});
