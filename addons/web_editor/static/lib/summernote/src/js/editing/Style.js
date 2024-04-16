define([
  'summernote/core/agent',
  'summernote/core/func',
  'summernote/core/list',
  'summernote/core/dom'
],function(agent,func,list,dom){
  /**
   *@classediting.Style
   *
   *Style
   *
   */
  varStyle=function(){
    /**
     *@methodjQueryCSS
     *
     *[workaround]foroldjQuery
     *passinganarrayofstylepropertiesto.css()
     *willresultinanobjectofproperty-valuepairs.
     *(compabilitywithversion<1.9)
     *
     *@private
     *@param {jQuery}$obj
     *@param {Array}propertyNames-AnarrayofoneormoreCSSproperties.
     *@return{Object}
     */
    varjQueryCSS=function($obj,propertyNames){
      if(agent.jqueryVersion<1.9){
        varresult={};
        $.each(propertyNames,function(idx,propertyName){
          result[propertyName]=$obj.css(propertyName);
        });
        returnresult;
      }
      return$obj.css.call($obj,propertyNames);
    };

    /**
     *returnsstyleobjectfromnode
     *
     *@param{jQuery}$node
     *@return{Object}
     */
    this.fromNode=function($node){
      varproperties=['font-family','font-size','text-align','list-style-type','line-height'];
      varstyleInfo=jQueryCSS($node,properties)||{};
      styleInfo['font-size']=parseInt(styleInfo['font-size'],10);
      returnstyleInfo;
    };

    /**
     *paragraphlevelstyle
     *
     *@param{WrappedRange}rng
     *@param{Object}styleInfo
     */
    this.stylePara=function(rng,styleInfo){
      $.each(rng.nodes(dom.isPara,{
        includeAncestor:true
      }),function(idx,para){
        $(para).css(styleInfo);
      });
    };

    /**
     *insertandreturnsstyleNodesonrange.
     *
     *@param{WrappedRange}rng
     *@param{Object}[options]-optionsforstyleNodes
     *@param{String}[options.nodeName]-default:`SPAN`
     *@param{Boolean}[options.expandClosestSibling]-default:`false`
     *@param{Boolean}[options.onlyPartialContains]-default:`false`
     *@return{Node[]}
     */
    this.styleNodes=function(rng,options){
      rng=rng.splitText();

      varnodeName=options&&options.nodeName||'SPAN';
      varexpandClosestSibling=!!(options&&options.expandClosestSibling);
      varonlyPartialContains=!!(options&&options.onlyPartialContains);

      if(rng.isCollapsed()){
        return[rng.insertNode(dom.create(nodeName))];
      }

      varpred=dom.makePredByNodeName(nodeName);
      varnodes=rng.nodes(dom.isText,{
        fullyContains:true
      }).map(function(text){
        returndom.singleChildAncestor(text,pred)||dom.wrap(text,nodeName);
      });

      if(expandClosestSibling){
        if(onlyPartialContains){
          varnodesInRange=rng.nodes();
          //composewithpartialcontainspredication
          pred=func.and(pred,function(node){
            returnlist.contains(nodesInRange,node);
          });
        }

        returnnodes.map(function(node){
          varsiblings=dom.withClosestSiblings(node,pred);
          varhead=list.head(siblings);
          vartails=list.tail(siblings);
          $.each(tails,function(idx,elem){
            dom.appendChildNodes(head,elem.childNodes);
            dom.remove(elem);
          });
          returnlist.head(siblings);
        });
      }else{
        returnnodes;
      }
    };

    /**
     *getcurrentstyleoncursor
     *
     *@param{WrappedRange}rng
     *@return{Object}-objectcontainsstyleproperties.
     */
    this.current=function(rng){
      var$cont=$(dom.isText(rng.sc)?rng.sc.parentNode:rng.sc);
      varstyleInfo=this.fromNode($cont);

      //document.queryCommandStatefortogglestate
      styleInfo['font-bold']=document.queryCommandState('bold')?'bold':'normal';
      styleInfo['font-italic']=document.queryCommandState('italic')?'italic':'normal';
      styleInfo['font-underline']=document.queryCommandState('underline')?'underline':'normal';
      styleInfo['font-strikethrough']=document.queryCommandState('strikeThrough')?'strikethrough':'normal';
      styleInfo['font-superscript']=document.queryCommandState('superscript')?'superscript':'normal';
      styleInfo['font-subscript']=document.queryCommandState('subscript')?'subscript':'normal';

      //list-style-typetolist-style(unordered,ordered)
      if(!rng.isOnList()){
        styleInfo['list-style']='none';
      }else{
        varaOrderedType=['circle','disc','disc-leading-zero','square'];
        varisUnordered=$.inArray(styleInfo['list-style-type'],aOrderedType)>-1;
        styleInfo['list-style']=isUnordered?'unordered':'ordered';
      }

      varpara=dom.ancestor(rng.sc,dom.isPara);
      if(para&&para.style['line-height']){
        styleInfo['line-height']=para.style.lineHeight;
      }else{
        varlineHeight=parseInt(styleInfo['line-height'],10)/parseInt(styleInfo['font-size'],10);
        styleInfo['line-height']=lineHeight.toFixed(1);
      }

      styleInfo.anchor=rng.isOnAnchor()&&dom.ancestor(rng.sc,dom.isAnchor);
      styleInfo.ancestors=dom.listAncestor(rng.sc,dom.isEditable);
      styleInfo.range=rng;

      returnstyleInfo;
    };
  };

  returnStyle;
});
