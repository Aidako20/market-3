define([
  'summernote/core/dom',
  'summernote/core/range',
  'summernote/editing/Bullet'
],function(dom,range,Bullet){

  /**
   *@classediting.Typing
   *
   *Typing
   *
   */
  varTyping=function(){

    //aBulletinstancetotogglelistsoff
    varbullet=newBullet();

    /**
     *inserttab
     *
     *@param{jQuery}$editable
     *@param{WrappedRange}rng
     *@param{Number}tabsize
     */
    this.insertTab=function($editable,rng,tabsize){
      vartab=dom.createText(newArray(tabsize+1).join(dom.NBSP_CHAR));
      rng=rng.deleteContents();
      rng.insertNode(tab,true);

      rng=range.create(tab,tabsize);
      rng.select();
    };

    /**
     *insertparagraph
     */
    this.insertParagraph=function(){
      varrng=range.create();

      //deleteContentsonrange.
      rng=rng.deleteContents();

      //Wraprangeifitneedstobewrappedbyparagraph
      rng=rng.wrapBodyInlineWithPara();

      //findingparagraph
      varsplitRoot=dom.ancestor(rng.sc,dom.isPara);

      varnextPara;
      //onparagraph:splitparagraph
      if(splitRoot){
        //ifitisanemptylinewithli
        if(dom.isEmpty(splitRoot)&&dom.isLi(splitRoot)){
          //disableUL/OLandescape!
          bullet.toggleList(splitRoot.parentNode.nodeName);
          return;
        //ifnewlinehascontent(notalinebreak)
        }else{
          nextPara=dom.splitTree(splitRoot,rng.getStartPoint());

          varemptyAnchors=dom.listDescendant(splitRoot,dom.isEmptyAnchor);
          emptyAnchors=emptyAnchors.concat(dom.listDescendant(nextPara,dom.isEmptyAnchor));

          $.each(emptyAnchors,function(idx,anchor){
            dom.remove(anchor);
          });
        }
      //noparagraph:insertemptyparagraph
      }else{
        varnext=rng.sc.childNodes[rng.so];
        nextPara=$(dom.emptyPara)[0];
        if(next){
          rng.sc.insertBefore(nextPara,next);
        }else{
          rng.sc.appendChild(nextPara);
        }
      }

      range.create(nextPara,0).normalize().select();

    };

  };

  returnTyping;
});
