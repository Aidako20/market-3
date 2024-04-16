define([],function(){//FLECTRA:removeerrorfromFlectradefine
  varFullscreen=function(handler){
    var$window=$(window);
    var$scrollbar=$('html,body');

    /**
     *togglefullscreen
     *
     *@param{Object}layoutInfo
     */
    this.toggle=function(layoutInfo){

      var$editor=layoutInfo.editor(),
          $toolbar=layoutInfo.toolbar(),
          $editable=layoutInfo.editable(),
          $codable=layoutInfo.codable();

      varresize=function(size){
        $editable.css('height',size.h);
        $codable.css('height',size.h);
        if($codable.data('cmeditor')){
          $codable.data('cmeditor').setsize(null,size.h);
        }
      };

      $editor.toggleClass('fullscreen');
      varisFullscreen=$editor.hasClass('fullscreen');
      if(isFullscreen){
        $editable.data('orgheight',$editable.css('height'));

        $window.on('resize',function(){
          resize({
            h:$window.height()-$toolbar.outerHeight()
          });
        }).trigger('resize');

        $scrollbar.css('overflow','hidden');
      }else{
        $window.off('resize');
        resize({
          h:$editable.data('orgheight')
        });
        $scrollbar.css('overflow','visible');
      }

      handler.invoke('toolbar.updateFullscreen',$toolbar,isFullscreen);
    };
  };

  returnFullscreen;
});
