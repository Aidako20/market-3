define([
  'summernote/core/agent',
  'summernote/core/func',
  'summernote/core/list',
  'summernote/core/dom',
  'summernote/core/range',
  'summernote/core/async',
  'summernote/editing/Style',
  'summernote/editing/Typing',
  'summernote/editing/Table',
  'summernote/editing/Bullet'
],function(agent,func,list,dom,range,async,
             Style,Typing,Table,Bullet){

  varKEY_BOGUS='bogus';

  /**
   *@classediting.Editor
   *
   *Editor
   *
   */
  varEditor=function(handler){

    varself=this;
    varstyle=newStyle();
    vartable=newTable();
    vartyping=newTyping();
    varbullet=newBullet();

    this.style=style;  //FLECTRA:allowaccessforoverride
    this.table=table;  //FLECTRA:allowaccessforoverride
    this.typing=typing;//FLECTRA:allowaccessforoverride
    this.bullet=bullet;//FLECTRA:allowaccessforoverride

    /**
     *@methodcreateRange
     *
     *createrange
     *
     *@param{jQuery}$editable
     *@return{WrappedRange}
     */
    this.createRange=function($editable){
      this.focus($editable);
      returnrange.create();
    };

    /**
     *@methodsaveRange
     *
     *savecurrentrange
     *
     *@param{jQuery}$editable
     *@param{Boolean}[thenCollapse=false]
     */
    this.saveRange=function($editable,thenCollapse){
      //FLECTRA:scrolltotopwhenclickoninputineditablem(start_modification
      //this.focus($editable);
      varr=range.create();
      if(!r||($editable[0]!==r.sc&&!$.contains($editable[0],r.sc))){
        $editable.focus();
      }
      //FLECTRA:end_modication)
      $editable.data('range',range.create());
      if(thenCollapse){
        range.create().collapse().select();
      }
    };

    /**
     *@methodsaveRange
     *
     *savecurrentnodelistto$editable.data('childNodes')
     *
     *@param{jQuery}$editable
     */
    this.saveNode=function($editable){
      //copychildnodereference
      varcopy=[];
      for(varkey =0,len=$editable[0].childNodes.length;key<len;key++){
        copy.push($editable[0].childNodes[key]);
      }
      $editable.data('childNodes',copy);
    };

    /**
     *@methodrestoreRange
     *
     *restorelatelyrange
     *
     *@param{jQuery}$editable
     */
    this.restoreRange=function($editable){
      varrng=$editable.data('range');
      if(rng){
        rng.select();
        this.focus($editable);
      }
    };

    /**
     *@methodrestoreNode
     *
     *restorelatelynodelist
     *
     *@param{jQuery}$editable
     */
    this.restoreNode=function($editable){
      $editable.html('');
      varchild=$editable.data('childNodes');
      for(varindex=0,len=child.length;index<len;index++){
        $editable[0].appendChild(child[index]);
      }
    };

    /**
     *@methodcurrentStyle
     *
     *currentstyle
     *
     *@param{Node}target
     *@return{Object|Boolean}unfocus
     */
    this.currentStyle=function(target){
      varrng=range.create();
      varstyleInfo= rng&&rng.isOnEditable()?style.current(rng.normalize()):{};
      if(dom.isImg(target)){
        styleInfo.image=target;
      }
      returnstyleInfo;
    };

    /**
     *stylefromnode
     *
     *@param{jQuery}$node
     *@return{Object}
     */
    this.styleFromNode=function($node){
      returnstyle.fromNode($node);
    };

    vartriggerOnBeforeChange=function($editable){
      var$holder=dom.makeLayoutInfo($editable).holder();
      handler.bindCustomEvent(
        $holder,$editable.data('callbacks'),'before.command'
      )($editable.html(),$editable);
    };

    vartriggerOnChange=function($editable){
      var$holder=dom.makeLayoutInfo($editable).holder();
      handler.bindCustomEvent(
        $holder,$editable.data('callbacks'),'change'
      )($editable.html(),$editable);
    };

    /**
     *@methodundo
     *undo
     *@param{jQuery}$editable
     */
    this.undo=function($editable){
      triggerOnBeforeChange($editable);
      $editable.data('NoteHistory').undo();
      triggerOnChange($editable);
    };

    /**
     *@methodredo
     *redo
     *@param{jQuery}$editable
     */
    this.redo=function($editable){
      triggerOnBeforeChange($editable);
      $editable.data('NoteHistory').redo();
      triggerOnChange($editable);
    };

    /**
     *@methodbeforeCommand
     *beforecommand
     *@param{jQuery}$editable
     */
    varbeforeCommand=this.beforeCommand=function($editable){
      triggerOnBeforeChange($editable);
      //keepfocusoneditablebeforecommandexecution
      self.focus($editable);
    };

    /**
     *@methodafterCommand
     *aftercommand
     *@param{jQuery}$editable
     *@param{Boolean}isPreventTrigger
     */
    varafterCommand=this.afterCommand=function($editable,isPreventTrigger){
      $editable.data('NoteHistory').recordUndo();
      if(!isPreventTrigger){
        triggerOnChange($editable);
      }
    };

    /**
     *@methodbold
     *@param{jQuery}$editable
     *@param{Mixed}value
     */

    /**
     *@methoditalic
     *@param{jQuery}$editable
     *@param{Mixed}value
     */

    /**
     *@methodunderline
     *@param{jQuery}$editable
     *@param{Mixed}value
     */

    /**
     *@methodstrikethrough
     *@param{jQuery}$editable
     *@param{Mixed}value
     */

    /**
     *@methodformatBlock
     *@param{jQuery}$editable
     *@param{Mixed}value
     */

    /**
     *@methodsuperscript
     *@param{jQuery}$editable
     *@param{Mixed}value
     */

    /**
     *@methodsubscript
     *@param{jQuery}$editable
     *@param{Mixed}value
     */

    /**
     *@methodjustifyLeft
     *@param{jQuery}$editable
     *@param{Mixed}value
     */

    /**
     *@methodjustifyCenter
     *@param{jQuery}$editable
     *@param{Mixed}value
     */

    /**
     *@methodjustifyRight
     *@param{jQuery}$editable
     *@param{Mixed}value
     */

    /**
     *@methodjustifyFull
     *@param{jQuery}$editable
     *@param{Mixed}value
     */

    /**
     *@methodformatBlock
     *@param{jQuery}$editable
     *@param{Mixed}value
     */

    /**
     *@methodremoveFormat
     *@param{jQuery}$editable
     *@param{Mixed}value
     */

    /**
     *@methodbackColor
     *@param{jQuery}$editable
     *@param{Mixed}value
     */

    /**
     *@methodforeColor
     *@param{jQuery}$editable
     *@param{Mixed}value
     */

    /**
     *@methodinsertHorizontalRule
     *@param{jQuery}$editable
     *@param{Mixed}value
     */

    /**
     *@methodfontName
     *
     *changefontname
     *
     *@param{jQuery}$editable
     *@param{Mixed}value
     */

    /*jshintignore:start*/
    //nativecommands(withexecCommand),generatefunctionforexecCommand
    varcommands=['bold','italic','underline','strikethrough','superscript','subscript',
                    'justifyLeft','justifyCenter','justifyRight','justifyFull',
                    'formatBlock','removeFormat',
                    'backColor','foreColor','fontName'];

    for(varidx=0,len=commands.length;idx<len;idx++){
      this[commands[idx]]=(function(sCmd){
        returnfunction($editable,value){
          beforeCommand($editable);

          document.execCommand(sCmd,false,value);

          afterCommand($editable,true);
        };
      })(commands[idx]);
    }
    /*jshintignore:end*/

    /**
     *@methodtab
     *
     *handletabkey
     *
     *@param{jQuery}$editable
     *@param{Object}options
     */
    this.tab=function($editable,options){
      varrng=this.createRange($editable);
      if(rng.isCollapsed()&&rng.isOnCell()){
        table.tab(rng);
      }else{
        beforeCommand($editable);
        typing.insertTab($editable,rng,options.tabsize);
        afterCommand($editable);
      }
    };

    /**
     *@methoduntab
     *
     *handleshift+tabkey
     *
     */
    this.untab=function($editable){
      varrng=this.createRange($editable);
      if(rng.isCollapsed()&&rng.isOnCell()){
        table.tab(rng,true);
      }
    };

    /**
     *@methodinsertParagraph
     *
     *insertparagraph
     *
     *@param{Node}$editable
     */
    this.insertParagraph=function($editable){
      beforeCommand($editable);
      typing.insertParagraph($editable);
      afterCommand($editable);
    };

    /**
     *@methodinsertOrderedList
     *
     *@param{jQuery}$editable
     */
    this.insertOrderedList=function($editable){
      beforeCommand($editable);
      bullet.insertOrderedList($editable);
      afterCommand($editable);
    };

    /**
     *@param{jQuery}$editable
     */
    this.insertUnorderedList=function($editable){
      beforeCommand($editable);
      bullet.insertUnorderedList($editable);
      afterCommand($editable);
    };

    /**
     *@param{jQuery}$editable
     */
    this.indent=function($editable){
      beforeCommand($editable);
      bullet.indent($editable);
      afterCommand($editable);
    };

    /**
     *@param{jQuery}$editable
     */
    this.outdent=function($editable){
      beforeCommand($editable);
      bullet.outdent($editable);
      afterCommand($editable);
    };

    /**
     *insertimage
     *
     *@param{jQuery}$editable
     *@param{String}sUrl
     */
    this.insertImage=function($editable,sUrl,filename){
      async.createImage(sUrl,filename).then(function($image){
        beforeCommand($editable);
        $image.css({
          display:'',
          width:Math.min($editable.width(),$image.width())
        });
        range.create().insertNode($image[0]);
        range.createFromNodeAfter($image[0]).select();
        afterCommand($editable);
      }).fail(function(){
        var$holder=dom.makeLayoutInfo($editable).holder();
        handler.bindCustomEvent(
          $holder,$editable.data('callbacks'),'image.upload.error'
        )();
      });
    };

    /**
     *@methodinsertNode
     *insertnode
     *@param{Node}$editable
     *@param{Node}node
     */
    this.insertNode=function($editable,node){
      beforeCommand($editable);
      range.create().insertNode(node);
      range.createFromNodeAfter(node).select();
      afterCommand($editable);
    };

    /**
     *inserttext
     *@param{Node}$editable
     *@param{String}text
     */
    this.insertText=function($editable,text){
      beforeCommand($editable);
      vartextNode=range.create().insertNode(dom.createText(text));
      range.create(textNode,dom.nodeLength(textNode)).select();
      afterCommand($editable);
    };

    /**
     *pasteHTML
     *@param{Node}$editable
     *@param{String}markup
     */
    this.pasteHTML=function($editable,markup){
      beforeCommand($editable);
      varcontents=range.create().pasteHTML(markup);
      range.createFromNodeAfter(list.last(contents)).select();
      afterCommand($editable);
    };

    /**
     *formatBlock
     *
     *@param{jQuery}$editable
     *@param{String}tagName
     */
    this.formatBlock=function($editable,tagName){
      beforeCommand($editable);
      //[workaround]forMSIE,IEneed`<`
      tagName=agent.isMSIE?'<'+tagName+'>':tagName;
      document.execCommand('FormatBlock',false,tagName);
      afterCommand($editable);
    };

    this.formatPara=function($editable){
      beforeCommand($editable);
      this.formatBlock($editable,'P');
      afterCommand($editable);
    };

    /*jshintignore:start*/
    for(varidx=1;idx<=6;idx++){
      this['formatH'+idx]=function(idx){
        returnfunction($editable){
          this.formatBlock($editable,'H'+idx);
        };
      }(idx);
    };
    /*jshintignore:end*/

    /**
     *fontSize
     *
     *@param{jQuery}$editable
     *@param{String}value-px
     */
    this.fontSize=function($editable,value){
      varrng=range.create();

      if(rng.isCollapsed()){
        varspans=style.styleNodes(rng);
        varfirstSpan=list.head(spans);

        $(spans).css({
          'font-size':value+'px'
        });

        //[workaround]addedstyledbogusspanforstyle
        // -alsoboguscharacterneededforcursorposition
        if(firstSpan&&!dom.nodeLength(firstSpan)){
          firstSpan.innerHTML=dom.ZERO_WIDTH_NBSP_CHAR;
          range.createFromNodeAfter(firstSpan.firstChild).select();
          $editable.data(KEY_BOGUS,firstSpan);
        }
      }else{
        beforeCommand($editable);
        $(style.styleNodes(rng)).css({
          'font-size':value+'px'
        });
        afterCommand($editable);
      }
    };

    /**
     *inserthorizontalrule
     *@param{jQuery}$editable
     */
    this.insertHorizontalRule=function($editable){
      beforeCommand($editable);

      varrng=range.create();
      varhrNode=rng.insertNode($('<HR/>')[0]);
      if(hrNode.nextSibling){
        range.create(hrNode.nextSibling,0).normalize().select();
      }

      afterCommand($editable);
    };

    /**
     *removebogusnodeandcharacter
     */
    this.removeBogus=function($editable){
      varbogusNode=$editable.data(KEY_BOGUS);
      if(!bogusNode){
        return;
      }

      vartextNode=list.find(list.from(bogusNode.childNodes),dom.isText);

      varbogusCharIdx=textNode.nodeValue.indexOf(dom.ZERO_WIDTH_NBSP_CHAR);
      if(bogusCharIdx!==-1){
        textNode.deleteData(bogusCharIdx,1);
      }

      if(dom.isEmpty(bogusNode)){
        dom.remove(bogusNode);
      }

      $editable.removeData(KEY_BOGUS);
    };

    /**
     *lineHeight
     *@param{jQuery}$editable
     *@param{String}value
     */
    this.lineHeight=function($editable,value){
      beforeCommand($editable);
      style.stylePara(range.create(),{
        lineHeight:value
      });
      afterCommand($editable);
    };

    /**
     *unlink
     *
     *@typecommand
     *
     *@param{jQuery}$editable
     */
    this.unlink=function($editable){
      varrng=this.createRange($editable);
      if(rng.isOnAnchor()){
        varanchor=dom.ancestor(rng.sc,dom.isAnchor);
        rng=range.createFromNode(anchor);
        rng.select();

        beforeCommand($editable);
        document.execCommand('unlink');
        afterCommand($editable);
      }
    };

    /**
     *createlink(command)
     *
     *@param{jQuery}$editable
     *@param{Object}linkInfo
     *@param{Object}options
     */
    this.createLink=function($editable,linkInfo,options){
      varlinkUrl=linkInfo.url;
      varlinkText=linkInfo.text;
      varisNewWindow=linkInfo.isNewWindow;
      varrng=linkInfo.range||this.createRange($editable);
      varisTextChanged=rng.toString()!==linkText;
      //Hack:Thismethodwasupdatedtocreatebuttonsaswell(usingthesamelogicasanchornodes).
      constnodeName=linkInfo.isButton?'BUTTON':'A';
      constpred=dom.makePredByNodeName(nodeName);

      options=options||dom.makeLayoutInfo($editable).editor().data('options');

      beforeCommand($editable);

      if(options.onCreateLink){
        linkUrl=options.onCreateLink(linkUrl);
      }

      varanchors=[];
      //FLECTRA:addingthisbranchtomodifyexistinganchorifitfullycontainstherange
      varancestor_anchor=dom.ancestor(rng.sc,pred);
      if(ancestor_anchor&&ancestor_anchor===dom.ancestor(rng.ec,pred)){
          anchors.push($(ancestor_anchor).html(linkText).get(0));
      }elseif(isTextChanged){
        //Createanewelementwhentextchanged.
        varanchor=rng.insertNode($(`<${nodeName}>${linkText}</${nodeName}>`)[0]);
        anchors.push(anchor);
      }else{
        anchors=style.styleNodes(rng,{
          nodeName:nodeName,
          expandClosestSibling:true,
          onlyPartialContains:true
        });
      }

      $.each(anchors,function(idx,anchor){
        if(!linkInfo.isButton){
          $(anchor).attr('href',linkUrl);
        }
        $(anchor).attr('class',linkInfo.className||null);//FLECTRA:addition
        $(anchor).css(linkInfo.style||{});//FLECTRA:addition
        if(isNewWindow){
          $(anchor).attr('target','_blank');
        }else{
          $(anchor).removeAttr('target');
        }
      });

      varstartRange=range.createFromNodeBefore(list.head(anchors));
      varstartPoint=startRange.getStartPoint();
      varendRange=range.createFromNodeAfter(list.last(anchors));
      varendPoint=endRange.getEndPoint();

      range.create(
        startPoint.node,
        startPoint.offset,
        endPoint.node,
        endPoint.offset
      ).select();

      afterCommand($editable);
    };

    /**
     *returnslinkinfo
     *Hack:Thismethodwasupdatedtoreturnabooleanattribute'isButton'toallow
     *handlingbuttonsinlinkDialog.
     *
     *@return{Object}
     *@return{WrappedRange}return.range
     *@return{String}return.text
     *@return{Boolean}[return.isNewWindow=true]
     *@return{String}[return.url=""]
     */
    this.getLinkInfo=function($editable){
      //FLECTRAMODIFICATIONSTART
      varselection;
      varcurrentSelection=null;
      if(document.getSelection){
        selection=document.getSelection();
        if(selection.getRangeAt&&selection.rangeCount){
          currentSelection=selection.getRangeAt(0);
        }
      }
      //FLECTRAMODIFICATIONEND

      this.focus($editable);

      //FLECTRAMODIFICATIONSTART
      if(currentSelection&&document.getSelection){
        selection=document.getSelection();
        if(!selection||selection.rangeCount===0){
          selection.removeAllRanges();
          selection.addRange(currentSelection);
        }
      }
      //FLECTRAMODIFICATIONEND

      varrng=range.create().expand(dom.isAnchor);

      //Getthefirstanchoronrange(foredit).
      varanchor=list.head(rng.nodes(dom.isAnchor));
      const$anchor=$(anchor);

      if($anchor.length&&!rng.nodes()[0].isSameNode(anchor)){
        rng=range.createFromNode(anchor);
        rng.select();
      }

      //Checkifthetargetisabuttonelement.
      letisButton=false;
      if(!$anchor.length){
        constpred=dom.makePredByNodeName('BUTTON');
        constrngNew=range.create().expand(pred);
        consttarget=list.head(rngNew.nodes(pred));
        if(target&&target.nodeName==='BUTTON'){
          isButton=true;
          rng=rngNew;
        }
      }

      return{
        range:rng,
        text:rng.toString(),
        isNewWindow:$anchor.length?$anchor.attr('target')==='_blank':false,
        url:$anchor.length?$anchor.attr('href'):'',
        isButton:isButton,
      };
    };

    /**
     *settingcolor
     *
     *@param{Node}$editable
     *@param{Object}sObjColor colorcode
     *@param{String}sObjColor.foreColorforegroundcolor
     *@param{String}sObjColor.backColorbackgroundcolor
     */
    this.color=function($editable,sObjColor){
      varoColor=JSON.parse(sObjColor);
      varforeColor=oColor.foreColor,backColor=oColor.backColor;

      beforeCommand($editable);

      if(foreColor){document.execCommand('foreColor',false,foreColor);}
      if(backColor){document.execCommand('backColor',false,backColor);}

      afterCommand($editable);
    };

    /**
     *insertTable
     *
     *@param{Node}$editable
     *@param{String}sDimdimensionoftable(ex:"5x5")
     */
    this.insertTable=function($editable,sDim){
      vardimension=sDim.split('x');
      beforeCommand($editable);

      varrng=range.create().deleteContents();
      rng.insertNode(table.createTable(dimension[0],dimension[1]));
      afterCommand($editable);
    };

    /**
     *floatme
     *
     *@param{jQuery}$editable
     *@param{String}value
     *@param{jQuery}$target
     */
    this.floatMe=function($editable,value,$target){
      beforeCommand($editable);
      //bootstrap
      $target.removeClass('float-leftfloat-right');
      if(value&&value!=='none'){
        $target.addClass('pull-'+value);
      }

      //fallbackfornon-bootstrap
      $target.css('float',value);
      afterCommand($editable);
    };

    /**
     *changeimageshape
     *
     *@param{jQuery}$editable
     *@param{String}valuecssclass
     *@param{Node}$target
     */
    this.imageShape=function($editable,value,$target){
      beforeCommand($editable);

      $target.removeClass('roundedrounded-circleimg-thumbnail');

      if(value){
        $target.addClass(value);
      }

      afterCommand($editable);
    };

    /**
     *resizeoverlayelement
     *@param{jQuery}$editable
     *@param{String}value
     *@param{jQuery}$target-targetelement
     */
    this.resize=function($editable,value,$target){
      beforeCommand($editable);

      $target.css({
        width:value*100+'%',
        height:''
      });

      afterCommand($editable);
    };

    /**
     *@param{Position}pos
     *@param{jQuery}$target-targetelement
     *@param{Boolean}[bKeepRatio]-keepratio
     */
    this.resizeTo=function(pos,$target,bKeepRatio){
      varimageSize;
      if(bKeepRatio){
        varnewRatio=pos.y/pos.x;
        varratio=$target.data('ratio');
        imageSize={
          width:ratio>newRatio?pos.x:pos.y/ratio,
          height:ratio>newRatio?pos.x*ratio:pos.y
        };
      }else{
        imageSize={
          width:pos.x,
          height:pos.y
        };
      }

      $target.css(imageSize);
    };

    /**
     *removemediaobject
     *
     *@param{jQuery}$editable
     *@param{String}value-dummyargument(forkeepinterface)
     *@param{jQuery}$target-targetelement
     */
    this.removeMedia=function($editable,value,$target){
      beforeCommand($editable);
      $target.detach();

      handler.bindCustomEvent(
        $(),$editable.data('callbacks'),'media.delete'
      )($target,$editable);

      afterCommand($editable);
    };

    /**
     *setfocus
     *
     *@param$editable
     */
    this.focus=function($editable){
      $editable.focus();

      //[workaround]forfirefoxbughttp://goo.gl/lVfAaI
      if(agent.isFF){
        varrng=range.create();
        if(!rng||rng.isOnEditable()){
          return;
        }

        range.createFromNode($editable[0])
             .normalize()
             .collapse()
             .select();
      }
    };

    /**
     *returnswhethercontentsisemptyornot.
     *
     *@param{jQuery}$editable
     *@return{Boolean}
     */
    this.isEmpty=function($editable){
      returndom.isEmpty($editable[0])||dom.emptyPara===$editable.html();
    };
  };

  returnEditor;
});
