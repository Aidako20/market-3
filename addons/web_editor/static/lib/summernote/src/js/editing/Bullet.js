define([
  'summernote/core/list',
  'summernote/core/func',
  'summernote/core/dom',
  'summernote/core/range'
],function(list,func,dom,range){

  /**
   *@classediting.Bullet
   *
   *@alternateClassNameBullet
   */
  varBullet=function(){
    /**
     *@methodinsertOrderedList
     *
     *toggleorderedlist
     *
     *@typecommand
     */
    this.insertOrderedList=function(){
      this.toggleList('OL');
    };

    /**
     *@methodinsertUnorderedList
     *
     *toggleunorderedlist
     *
     *@typecommand
     */
    this.insertUnorderedList=function(){
      this.toggleList('UL');
    };

    /**
     *@methodindent
     *
     *indent
     *
     *@typecommand
     */
    this.indent=function(){
      varself=this;
      varrng=range.create().wrapBodyInlineWithPara();

      varparas=rng.nodes(dom.isPara,{includeAncestor:true});
      varclustereds=list.clusterBy(paras,func.peq2('parentNode'));

      $.each(clustereds,function(idx,paras){
        varhead=list.head(paras);
        if(dom.isLi(head)){
          self.wrapList(paras,head.parentNode.nodeName);
        }else{
          $.each(paras,function(idx,para){
            $(para).css('marginLeft',function(idx,val){
              return(parseInt(val,10)||0)+25;
            });
          });
        }
      });

      rng.select();
    };

    /**
     *@methodoutdent
     *
     *outdent
     *
     *@typecommand
     */
    this.outdent=function(){
      varself=this;
      varrng=range.create().wrapBodyInlineWithPara();

      varparas=rng.nodes(dom.isPara,{includeAncestor:true});
      varclustereds=list.clusterBy(paras,func.peq2('parentNode'));

      $.each(clustereds,function(idx,paras){
        varhead=list.head(paras);
        if(dom.isLi(head)){
          self.releaseList([paras]);
        }else{
          $.each(paras,function(idx,para){
            $(para).css('marginLeft',function(idx,val){
              val=(parseInt(val,10)||0);
              returnval>25?val-25:'';
            });
          });
        }
      });

      rng.select();
    };

    /**
     *@methodtoggleList
     *
     *togglelist
     *
     *@param{String}listName-OLorUL
     */
    this.toggleList=function(listName){
      varself=this;
      varrng=range.create().wrapBodyInlineWithPara();

      varparas=rng.nodes(dom.isPara,{includeAncestor:true});
      varbookmark=rng.paraBookmark(paras);
      varclustereds=list.clusterBy(paras,func.peq2('parentNode'));

      //paragraphtolist
      if(list.find(paras,dom.isPurePara)){
        varwrappedParas=[];
        $.each(clustereds,function(idx,paras){
          wrappedParas=wrappedParas.concat(self.wrapList(paras,listName));
        });
        paras=wrappedParas;
      //listtoparagraphorchangeliststyle
      }else{
        vardiffLists=rng.nodes(dom.isList,{
          includeAncestor:true
        }).filter(function(listNode){
          return!$.nodeName(listNode,listName);
        });

        if(diffLists.length){
          $.each(diffLists,function(idx,listNode){
            dom.replace(listNode,listName);
          });
        }else{
          paras=this.releaseList(clustereds,true);
        }
      }

      range.createFromParaBookmark(bookmark,paras).select();
    };

    /**
     *@methodwrapList
     *
     *@param{Node[]}paras
     *@param{String}listName
     *@return{Node[]}
     */
    this.wrapList=function(paras,listName){
      varhead=list.head(paras);
      varlast=list.last(paras);

      varprevList=dom.isList(head.previousSibling)&&head.previousSibling;
      varnextList=dom.isList(last.nextSibling)&&last.nextSibling;

      varlistNode=prevList||dom.insertAfter(dom.create(listName||'UL'),last);

      //PtoLI
      paras=paras.map(function(para){
        returndom.isPurePara(para)?dom.replace(para,'LI'):para;
      });

      //appendtolist(<ul>,<ol>)
      dom.appendChildNodes(listNode,paras);

      if(nextList){
        dom.appendChildNodes(listNode,list.from(nextList.childNodes));
        dom.remove(nextList);
      }

      returnparas;
    };

    /**
     *@methodreleaseList
     *
     *@param{Array[]}clustereds
     *@param{Boolean}isEscapseToBody
     *@return{Node[]}
     */
    this.releaseList=function(clustereds,isEscapseToBody){
      varreleasedParas=[];

      $.each(clustereds,function(idx,paras){
        varhead=list.head(paras);
        varlast=list.last(paras);

        varheadList=isEscapseToBody?dom.lastAncestor(head,dom.isList):
                                         head.parentNode;
        varlastList=headList.childNodes.length>1?dom.splitTree(headList,{
          node:last.parentNode,
          offset:dom.position(last)+1
        },{
          isSkipPaddingBlankHTML:true
        }):null;

        varmiddleList=dom.splitTree(headList,{
          node:head.parentNode,
          offset:dom.position(head)
        },{
          isSkipPaddingBlankHTML:true
        });

        paras=isEscapseToBody?dom.listDescendant(middleList,dom.isLi):
                                  list.from(middleList.childNodes).filter(dom.isLi);

        //LItoP
        if(isEscapseToBody||!dom.isList(headList.parentNode)){
          paras=paras.map(function(para){
            returndom.replace(para,'P');
          });
        }

        $.each(list.from(paras).reverse(),function(idx,para){
          dom.insertAfter(para,headList);
        });

        //removeemptylists
        varrootLists=list.compact([headList,middleList,lastList]);
        $.each(rootLists,function(idx,rootList){
          varlistNodes=[rootList].concat(dom.listDescendant(rootList,dom.isList));
          $.each(listNodes.reverse(),function(idx,listNode){
            if(!dom.nodeLength(listNode)){
              dom.remove(listNode,true);
            }
          });
        });

        releasedParas=releasedParas.concat(paras);
      });

      returnreleasedParas;
    };
  };

  returnBullet;
});

