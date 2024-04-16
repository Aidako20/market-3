define([
  'summernote/core/list',
  'summernote/core/dom',
  'summernote/module/Button'
],function(list,dom,Button){
  /**
   *@classmodule.Toolbar
   *
   *Toolbar
   */
  varToolbar=function(){
    varbutton=newButton();

    this.button=button;//FLECTRA:allowaccessforoverride

    this.update=function($toolbar,styleInfo){
      button.update($toolbar,styleInfo);
    };

    /**
     *@param{Node}button
     *@param{String}eventName
     *@param{String}value
     */
    this.updateRecentColor=function(buttonNode,eventName,value){
      button.updateRecentColor(buttonNode,eventName,value);
    };

    /**
     *activatebuttonsexcludecodeview
     *@param{jQuery}$toolbar
     */
    this.activate=function($toolbar){
      $toolbar.find('button')
              .not('button[data-event="codeview"]')
              .removeClass('disabled');
    };

    /**
     *deactivatebuttonsexcludecodeview
     *@param{jQuery}$toolbar
     */
    this.deactivate=function($toolbar){
      $toolbar.find('button')
              .not('button[data-event="codeview"]')
              .addClass('disabled');
    };

    /**
     *@param{jQuery}$container
     *@param{Boolean}[bFullscreen=false]
     */
    this.updateFullscreen=function($container,bFullscreen){
      var$btn=$container.find('button[data-event="fullscreen"]');
      $btn.toggleClass('active',bFullscreen);
    };

    /**
     *@param{jQuery}$container
     *@param{Boolean}[isCodeview=false]
     */
    this.updateCodeview=function($container,isCodeview){
      var$btn=$container.find('button[data-event="codeview"]');
      $btn.toggleClass('active',isCodeview);

      if(isCodeview){
        this.deactivate($container);
      }else{
        this.activate($container);
      }
    };

    /**
     *getbuttonintoolbar
     *
     *@param{jQuery}$editable
     *@param{String}name
     *@return{jQuery}
     */
    this.get=function($editable,name){
      var$toolbar=dom.makeLayoutInfo($editable).toolbar();

      return$toolbar.find('[data-name='+name+']');
    };

    /**
     *setbuttonstate
     *@param{jQuery}$editable
     *@param{String}name
     *@param{Boolean}[isActive=true]
     */
    this.setButtonState=function($editable,name,isActive){
      isActive=(isActive===false)?false:true;

      var$button=this.get($editable,name);
      $button.toggleClass('active',isActive);
    };
  };

  returnToolbar;
});
