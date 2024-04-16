define([
  'summernote/core/func',
  'summernote/core/list',
  'summernote/module/Button'
],function(func,list,Button){
  /**
   *@classmodule.Popover
   *
   *Popover(http://getbootstrap.com/javascript/#popovers)
   *
   */
  varPopover=function(){
    varbutton=newButton();

    this.button=button;//FLECTRA:allowaccessforoverride

    /**
     *returnspositionfromplaceholder
     *
     *@private
     *@param{Node}placeholder
     *@param{Object}options
     *@param{Boolean}options.isAirMode
     *@return{Position}
     */
    varposFromPlaceholder=function(placeholder,options){
      varisAirMode=options&&options.isAirMode;
      varisLeftTop=options&&options.isLeftTop;

      var$placeholder=$(placeholder);
      varpos=isAirMode?$placeholder.offset():$placeholder.position();
      varheight=isLeftTop?0:$placeholder.outerHeight(true);//includemargin

      //popoverbelowplaceholder.
      return{
        left:pos.left,
        top:pos.top+height
      };
    };

    /**
     *showpopover
     *
     *@private
     *@param{jQuery}popover
     *@param{Position}pos
     */
    varshowPopover=function($popover,pos){
      $popover.css({
        display:'block',
        left:pos.left,
        top:pos.top
      });
    };

    varPX_POPOVER_ARROW_OFFSET_X=20;

    /**
     *updatecurrentstate
     *@param{jQuery}$popover-popovercontainer
     *@param{Object}styleInfo-styleobject
     *@param{Boolean}isAirMode
     */
    this.update=function($popover,styleInfo,isAirMode){
      button.update($popover,styleInfo);

      var$linkPopover=$popover.find('.note-link-popover');
      if(styleInfo.anchor){
        var$anchor=$linkPopover.find('a');
        varhref=$(styleInfo.anchor).attr('href');
        vartarget=$(styleInfo.anchor).attr('target');
        $anchor.attr('href',href).text(href);
        if(!target){
          $anchor.removeAttr('target');
        }else{
          $anchor.attr('target','_blank');
        }
        showPopover($linkPopover,posFromPlaceholder(styleInfo.anchor,{
          isAirMode:isAirMode
        }));
      }else{
        $linkPopover.hide();
      }

      var$imagePopover=$popover.find('.note-image-popover');
      if(styleInfo.image){
        showPopover($imagePopover,posFromPlaceholder(styleInfo.image,{
          isAirMode:isAirMode,
          isLeftTop:true
        }));
      }else{
        $imagePopover.hide();
      }

      var$airPopover=$popover.find('.note-air-popover');
      if(isAirMode&&styleInfo.range&&!styleInfo.range.isCollapsed()){
        varrect=list.last(styleInfo.range.getClientRects());
        if(rect){
          varbnd=func.rect2bnd(rect);
          showPopover($airPopover,{
            left:Math.max(bnd.left+bnd.width/2-PX_POPOVER_ARROW_OFFSET_X,0),
            top:bnd.top+bnd.height
          });
        }
      }else{
        $airPopover.hide();
      }
    };

    /**
     *@param{Node}button
     *@param{String}eventName
     *@param{String}value
     */
    this.updateRecentColor=function(button,eventName,value){
      button.updateRecentColor(button,eventName,value);
    };

    /**
     *hideallpopovers
     *@param{jQuery}$popover-popovercontainer
     */
    this.hide=function($popover){
      $popover.children().hide();
    };
  };

  returnPopover;
});
