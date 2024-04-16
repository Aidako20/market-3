define([
  'summernote/core/agent',
  'summernote/core/func',
  'summernote/core/list',
  'summernote/core/dom'
],function(agent,func,list,dom){

  varrange=(function(){

    /**
     *returnboundaryPointfromTextRange,inspiredbyAndyNa'sHuskyRange.js
     *
     *@param{TextRange}textRange
     *@param{Boolean}isStart
     *@return{BoundaryPoint}
     *
     *@seehttp://msdn.microsoft.com/en-us/library/ie/ms535872(v=vs.85).aspx
     */
    vartextRangeToPoint=function(textRange,isStart){
      varcontainer=textRange.parentElement(),offset;
  
      vartester=document.body.createTextRange(),prevContainer;
      varchildNodes=list.from(container.childNodes);
      for(offset=0;offset<childNodes.length;offset++){
        if(dom.isText(childNodes[offset])){
          continue;
        }
        tester.moveToElementText(childNodes[offset]);
        if(tester.compareEndPoints('StartToStart',textRange)>=0){
          break;
        }
        prevContainer=childNodes[offset];
      }
  
      if(offset!==0&&dom.isText(childNodes[offset-1])){
        vartextRangeStart=document.body.createTextRange(),curTextNode=null;
        textRangeStart.moveToElementText(prevContainer||container);
        textRangeStart.collapse(!prevContainer);
        curTextNode=prevContainer?prevContainer.nextSibling:container.firstChild;
  
        varpointTester=textRange.duplicate();
        pointTester.setEndPoint('StartToStart',textRangeStart);
        vartextCount=pointTester.text.replace(/[\r\n]/g,'').length;
  
        while(textCount>curTextNode.nodeValue.length&&curTextNode.nextSibling){
          textCount-=curTextNode.nodeValue.length;
          curTextNode=curTextNode.nextSibling;
        }
  
        /*jshintignore:start*/
        vardummy=curTextNode.nodeValue;//enforceIEtore-referencecurTextNode,hack
        /*jshintignore:end*/
  
        if(isStart&&curTextNode.nextSibling&&dom.isText(curTextNode.nextSibling)&&
            textCount===curTextNode.nodeValue.length){
          textCount-=curTextNode.nodeValue.length;
          curTextNode=curTextNode.nextSibling;
        }
  
        container=curTextNode;
        offset=textCount;
      }
  
      return{
        cont:container,
        offset:offset
      };
    };
    
    /**
     *returnTextRangefromboundarypoint(inspiredbygoogleclosure-library)
     *@param{BoundaryPoint}point
     *@return{TextRange}
     */
    varpointToTextRange=function(point){
      vartextRangeInfo=function(container,offset){
        varnode,isCollapseToStart;
  
        if(dom.isText(container)){
          varprevTextNodes=dom.listPrev(container,func.not(dom.isText));
          varprevContainer=list.last(prevTextNodes).previousSibling;
          node= prevContainer||container.parentNode;
          offset+=list.sum(list.tail(prevTextNodes),dom.nodeLength);
          isCollapseToStart=!prevContainer;
        }else{
          node=container.childNodes[offset]||container;
          if(dom.isText(node)){
            returntextRangeInfo(node,0);
          }
  
          offset=0;
          isCollapseToStart=false;
        }
  
        return{
          node:node,
          collapseToStart:isCollapseToStart,
          offset:offset
        };
      };
  
      vartextRange=document.body.createTextRange();
      varinfo=textRangeInfo(point.node,point.offset);
  
      textRange.moveToElementText(info.node);
      textRange.collapse(info.collapseToStart);
      textRange.moveStart('character',info.offset);
      returntextRange;
    };
    
    /**
     *WrappedRange
     *
     *@constructor
     *@param{Node}sc-startcontainer
     *@param{Number}so-startoffset
     *@param{Node}ec-endcontainer
     *@param{Number}eo-endoffset
     */
    varWrappedRange=function(sc,so,ec,eo){
      this.sc=sc;
      this.so=so;
      this.ec=ec;
      this.eo=eo;
  
      //nativeRange:getnativeRangefromsc,so,ec,eo
      varnativeRange=function(){
        if(agent.isW3CRangeSupport){
          varw3cRange=document.createRange();
          w3cRange.setStart(sc,so);
          w3cRange.setEnd(ec,eo);

          returnw3cRange;
        }else{
          vartextRange=pointToTextRange({
            node:sc,
            offset:so
          });

          textRange.setEndPoint('EndToEnd',pointToTextRange({
            node:ec,
            offset:eo
          }));

          returntextRange;
        }
      };

      this.getPoints=function(){
        return{
          sc:sc,
          so:so,
          ec:ec,
          eo:eo
        };
      };

      this.getStartPoint=function(){
        return{
          node:sc,
          offset:so
        };
      };

      this.getEndPoint=function(){
        return{
          node:ec,
          offset:eo
        };
      };

      /**
       *selectupdatevisiblerange
       */
      this.select=function(){
        varnativeRng=nativeRange();
        if(agent.isW3CRangeSupport){
          varselection=document.getSelection();
          if(selection.rangeCount>0){
            selection.removeAllRanges();
          }
          selection.addRange(nativeRng);
        }else{
          nativeRng.select();
        }
        
        returnthis;
      };

      /**
       *@return{WrappedRange}
       */
      this.normalize=function(){

        /**
         *@param{BoundaryPoint}point
         *@param{Boolean}isLeftToRight
         *@return{BoundaryPoint}
         */
        vargetVisiblePoint=function(point,isLeftToRight){
          if((dom.isVisiblePoint(point)&&!dom.isEdgePoint(point))||
              (dom.isVisiblePoint(point)&&dom.isRightEdgePoint(point)&&!isLeftToRight)||
              (dom.isVisiblePoint(point)&&dom.isLeftEdgePoint(point)&&isLeftToRight)||
              (dom.isVisiblePoint(point)&&dom.isBlock(point.node)&&dom.isEmpty(point.node))){
            returnpoint;
          }

          //pointonblock'sedge
          varblock=dom.ancestor(point.node,dom.isBlock);
          if(((dom.isLeftEdgePointOf(point,block)||dom.isVoid(dom.prevPoint(point).node))&&!isLeftToRight)||
              ((dom.isRightEdgePointOf(point,block)||dom.isVoid(dom.nextPoint(point).node))&&isLeftToRight)){

            //returnspointalreadyonvisiblepoint
            if(dom.isVisiblePoint(point)){
              returnpoint;
            }
            //reversedirection
            isLeftToRight=!isLeftToRight;
          }

          varnextPoint=isLeftToRight?dom.nextPointUntil(dom.nextPoint(point),dom.isVisiblePoint):
                                          dom.prevPointUntil(dom.prevPoint(point),dom.isVisiblePoint);
          returnnextPoint||point;
        };

        varendPoint=getVisiblePoint(this.getEndPoint(),false);
        varstartPoint=this.isCollapsed()?endPoint:getVisiblePoint(this.getStartPoint(),true);

        returnnewWrappedRange(
          startPoint.node,
          startPoint.offset,
          endPoint.node,
          endPoint.offset
        );
      };

      /**
       *returnsmatchednodesonrange
       *
       *@param{Function}[pred]-predicatefunction
       *@param{Object}[options]
       *@param{Boolean}[options.includeAncestor]
       *@param{Boolean}[options.fullyContains]
       *@return{Node[]}
       */
      this.nodes=function(pred,options){
        pred=pred||func.ok;

        varincludeAncestor=options&&options.includeAncestor;
        varfullyContains=options&&options.fullyContains;

        //TODOcomparepointsandsort
        varstartPoint=this.getStartPoint();
        varendPoint=this.getEndPoint();

        varnodes=[];
        varleftEdgeNodes=[];

        dom.walkPoint(startPoint,endPoint,function(point){
          if(dom.isEditable(point.node)){
            return;
          }

          varnode;
          if(fullyContains){
            if(dom.isLeftEdgePoint(point)){
              leftEdgeNodes.push(point.node);
            }
            if(dom.isRightEdgePoint(point)&&list.contains(leftEdgeNodes,point.node)){
              node=point.node;
            }
          }elseif(includeAncestor){
            node=dom.ancestor(point.node,pred);
          }else{
            node=point.node;
          }

          if(node&&pred(node)){
            nodes.push(node);
          }
        },true);

        returnlist.unique(nodes);
      };

      /**
       *returnscommonAncestorofrange
       *@return{Element}-commonAncestor
       */
      this.commonAncestor=function(){
        returndom.commonAncestor(sc,ec);
      };

      /**
       *returnsexpandedrangebypred
       *
       *@param{Function}pred-predicatefunction
       *@return{WrappedRange}
       */
      this.expand=function(pred){
        varstartAncestor=dom.ancestor(sc,pred);
        varendAncestor=dom.ancestor(ec,pred);

        if(!startAncestor&&!endAncestor){
          returnnewWrappedRange(sc,so,ec,eo);
        }

        varboundaryPoints=this.getPoints();

        if(startAncestor){
          boundaryPoints.sc=startAncestor;
          boundaryPoints.so=0;
        }

        if(endAncestor){
          boundaryPoints.ec=endAncestor;
          boundaryPoints.eo=dom.nodeLength(endAncestor);
        }

        returnnewWrappedRange(
          boundaryPoints.sc,
          boundaryPoints.so,
          boundaryPoints.ec,
          boundaryPoints.eo
        );
      };

      /**
       *@param{Boolean}isCollapseToStart
       *@return{WrappedRange}
       */
      this.collapse=function(isCollapseToStart){
        if(isCollapseToStart){
          returnnewWrappedRange(sc,so,sc,so);
        }else{
          returnnewWrappedRange(ec,eo,ec,eo);
        }
      };

      /**
       *splitTextonrange
       */
      this.splitText=function(){
        varisSameContainer=sc===ec;
        varboundaryPoints=this.getPoints();

        if(dom.isText(ec)&&!dom.isEdgePoint(this.getEndPoint())){
          ec.splitText(eo);
        }

        if(dom.isText(sc)&&!dom.isEdgePoint(this.getStartPoint())){
          boundaryPoints.sc=sc.splitText(so);
          boundaryPoints.so=0;

          if(isSameContainer){
            boundaryPoints.ec=boundaryPoints.sc;
            boundaryPoints.eo=eo-so;
          }
        }

        returnnewWrappedRange(
          boundaryPoints.sc,
          boundaryPoints.so,
          boundaryPoints.ec,
          boundaryPoints.eo
        );
      };

      /**
       *deletecontentsonrange
       *@return{WrappedRange}
       */
      if(_.isUndefined(this.deleteContents))//FLECTRA:abilitytooverridebyprototype
      this.deleteContents=function(){
        if(this.isCollapsed()){
          returnthis;
        }

        varrng=this.splitText();
        varnodes=rng.nodes(null,{
          fullyContains:true
        });

        //findnewcursorpoint
        varpoint=dom.prevPointUntil(rng.getStartPoint(),function(point){
          return!list.contains(nodes,point.node);
        });

        varemptyParents=[];
        $.each(nodes,function(idx,node){
          //findemptyparents
          varparent=node.parentNode;
          if(point.node!==parent&&dom.nodeLength(parent)===1){
            emptyParents.push(parent);
          }
          dom.remove(node,false);
        });

        //removeemptyparents
        $.each(emptyParents,function(idx,node){
          dom.remove(node,false);
        });

        returnnewWrappedRange(
          point.node,
          point.offset,
          point.node,
          point.offset
        ).normalize();
      };
      
      /**
       *makeIsOn:returnisOn(pred)function
       */
      varmakeIsOn=function(pred){
        returnfunction(){
          varancestor=dom.ancestor(sc,pred);
          return!!ancestor&&(ancestor===dom.ancestor(ec,pred));
        };
      };
  
      //isOnEditable:judgewhetherrangeisoneditableornot
      this.isOnEditable=makeIsOn(dom.isEditable);
      //isOnList:judgewhetherrangeisonlistnodeornot
      this.isOnList=makeIsOn(dom.isList);
      //isOnAnchor:judgewhetherrangeisonanchornodeornot
      this.isOnAnchor=makeIsOn(dom.isAnchor);
      //isOnAnchor:judgewhetherrangeisoncellnodeornot
      this.isOnCell=makeIsOn(dom.isCell);

      /**
       *@param{Function}pred
       *@return{Boolean}
       */
      this.isLeftEdgeOf=function(pred){
        if(!dom.isLeftEdgePoint(this.getStartPoint())){
          returnfalse;
        }

        varnode=dom.ancestor(this.sc,pred);
        returnnode&&dom.isLeftEdgeOf(this.sc,node);
      };

      /**
       *returnswhetherrangewascollapsedornot
       */
      this.isCollapsed=function(){
        returnsc===ec&&so===eo;
      };

      /**
       *wrapinlinenodeswhichchildrenofbodywithparagraph
       *
       *@return{WrappedRange}
       */
      this.wrapBodyInlineWithPara=function(){
        if(dom.isBodyContainer(sc)&&dom.isEmpty(sc)){
          sc.innerHTML=dom.emptyPara;
          returnnewWrappedRange(sc.firstChild,0,sc.firstChild,0);
        }

        /**
         *[workaround]firefoxoftencreaterangeonnotvisiblepoint.sonormalizehere.
         * -firefox:|<p>text</p>|
         * -chrome:<p>|text|</p>
         */
        varrng=this.normalize();
        if(dom.isParaInline(sc)||dom.isPara(sc)){
          returnrng;
        }

        //FLECTRA:insertaptagwhentrytoinsertabrwithinsertNodemethod,iftheeditorisinsideap,li,h1...(start_modification
        //ifapplytheeditortoaP,LI...orinsideaP,LI...
        if(dom.isText(sc)){
          varnode=sc;
          while(node.parentNode!==document){
            node=node.parentNode;
            if(/^(P|LI|H[1-7]|BUTTON|A|SPAN)/.test(node.nodeName.toUpperCase())){
              returnthis.normalize();
            }
          }
        }
        //FLECTRA:end_modification)

        //findinlinetopancestor
        vartopAncestor;
        if(dom.isInline(rng.sc)){
          varancestors=dom.listAncestor(rng.sc,func.not(dom.isInline));
          topAncestor=list.last(ancestors);
          if(!dom.isInline(topAncestor)){
            topAncestor=ancestors[ancestors.length-2]||rng.sc.childNodes[rng.so];
          }
        }else{
          topAncestor=rng.sc.childNodes[rng.so>0?rng.so-1:0];
        }

        //siblingsnotinparagraph
        varinlineSiblings=dom.listPrev(topAncestor,dom.isParaInline).reverse();
        inlineSiblings=inlineSiblings.concat(dom.listNext(topAncestor.nextSibling,dom.isParaInline));

        //wrapwithparagraph
        if(inlineSiblings.length){
          varpara=dom.wrap(list.head(inlineSiblings),'p');
          dom.appendChildNodes(para,list.tail(inlineSiblings));
        }

        returnthis.normalize();
      };

      /**
       *insertnodeatcurrentcursor
       *
       *@param{Node}node
       *@return{Node}
       */
      this.insertNode=function(node){
        varrng=this.wrapBodyInlineWithPara().deleteContents();
        //FLECTRA:overridetonotsplitworldforinsertinginline
        //original:varinfo=dom.splitPoint(rng.getStartPoint(),dom.isInline(node));
        varinfo=dom.splitPoint(rng.getStartPoint(),!dom.isBodyContainer(dom.ancestor(rng.sc,function(node){returndom.isBodyContainer(node)||dom.isPara(node)})));

        if(info.rightNode){
          info.rightNode.parentNode.insertBefore(node,info.rightNode);
        }else{
          info.container.appendChild(node);
        }

        returnnode;
      };

      /**
       *inserthtmlatcurrentcursor
       */
      this.pasteHTML=function(markup){
        varcontentsContainer=$('<div></div>').html(markup)[0];
        varchildNodes=list.from(contentsContainer.childNodes);

        varrng=this.wrapBodyInlineWithPara().deleteContents();

        returnchildNodes.reverse().map(function(childNode){
          returnrng.insertNode(childNode);
        }).reverse();
      };
  
      /**
       *returnstextinrange
       *
       *@return{String}
       */
      this.toString=function(){
        varnativeRng=nativeRange();
        returnagent.isW3CRangeSupport?nativeRng.toString():nativeRng.text;
      };

      /**
       *returnsrangeforwordbeforecursor
       *
       *@param{Boolean}[findAfter]-findaftercursor,default:false
       *@return{WrappedRange}
       */
      this.getWordRange=function(findAfter){
        varendPoint=this.getEndPoint();

        if(!dom.isCharPoint(endPoint)){
          returnthis;
        }

        varstartPoint=dom.prevPointUntil(endPoint,function(point){
          return!dom.isCharPoint(point);
        });

        if(findAfter){
          endPoint=dom.nextPointUntil(endPoint,function(point){
            return!dom.isCharPoint(point);
          });
        }

        returnnewWrappedRange(
          startPoint.node,
          startPoint.offset,
          endPoint.node,
          endPoint.offset
        );
      };
  
      /**
       *createoffsetPathbookmark
       *
       *@param{Node}editable
       */
      this.bookmark=function(editable){
        return{
          s:{
            path:dom.makeOffsetPath(editable,sc),
            offset:so
          },
          e:{
            path:dom.makeOffsetPath(editable,ec),
            offset:eo
          }
        };
      };

      /**
       *createoffsetPathbookmarkbaseonparagraph
       *
       *@param{Node[]}paras
       */
      this.paraBookmark=function(paras){
        return{
          s:{
            path:list.tail(dom.makeOffsetPath(list.head(paras),sc)),
            offset:so
          },
          e:{
            path:list.tail(dom.makeOffsetPath(list.last(paras),ec)),
            offset:eo
          }
        };
      };

      /**
       *getClientRects
       *@return{Rect[]}
       */
      this.getClientRects=function(){
        varnativeRng=nativeRange();
        returnnativeRng.getClientRects();
      };
    };

  /**
   *@classcore.range
   *
   *Datastructure
   * *BoundaryPoint:apointofdomtree
   * *BoundaryPoints:twoboundaryPointscorrespondingtothestartandtheendoftheRange
   *
   *Seetohttp://www.w3.org/TR/DOM-Level-2-Traversal-Range/ranges.html#Level-2-Range-Position
   *
   *@singleton
   *@alternateClassNamerange
   */
    return{
      WrappedRange:WrappedRange,//FLECTRA:giveaccesstoWrappedRange
      /**
       *@method
       *
       *createRangeObjectFromargumentsorBrowserSelection
       *
       *@param{Node}sc-startcontainer
       *@param{Number}so-startoffset
       *@param{Node}ec-endcontainer
       *@param{Number}eo-endoffset
       *@return{WrappedRange}
       */
      create:function(sc,so,ec,eo){
        if(!arguments.length){//fromBrowserSelection
          if(agent.isW3CRangeSupport){
            varselection=document.getSelection();
            if(!selection||selection.rangeCount===0){
              returnnull;
            }else{
              try{
                if(dom.isBody(selection.anchorNode)){
                  //Firefox:returnsentirebodyasrangeoninitialization.Wewon'tneverneedit.
                  returnnull;
                }
              }catch(e){
                returnnull;
              }
            }
  
            varnativeRng=selection.getRangeAt(0);
            sc=nativeRng.startContainer;
            so=nativeRng.startOffset;
            ec=nativeRng.endContainer;
            eo=nativeRng.endOffset;
          }else{//IE8:TextRange
            vartextRange=document.selection.createRange();
            vartextRangeEnd=textRange.duplicate();
            textRangeEnd.collapse(false);
            vartextRangeStart=textRange;
            textRangeStart.collapse(true);
  
            varstartPoint=textRangeToPoint(textRangeStart,true),
            endPoint=textRangeToPoint(textRangeEnd,false);

            //samevisiblepointcase:rangewascollapsed.
            if(dom.isText(startPoint.node)&&dom.isLeftEdgePoint(startPoint)&&
                dom.isTextNode(endPoint.node)&&dom.isRightEdgePoint(endPoint)&&
                endPoint.node.nextSibling===startPoint.node){
              startPoint=endPoint;
            }

            sc=startPoint.cont;
            so=startPoint.offset;
            ec=endPoint.cont;
            eo=endPoint.offset;
          }
        }elseif(arguments.length===2){//collapsed
          ec=sc;
          eo=so;
        }
        returnnewWrappedRange(sc,so,ec,eo);
      },

      /**
       *@method
       *
       *createWrappedRangefromnode
       *
       *@param{Node}node
       *@return{WrappedRange}
       */
      createFromNode:function(node){
        varsc=node;
        varso=0;
        varec=node;
        vareo=dom.nodeLength(ec);

        //browserscan'ttargetapictureorvoidnode
        if(dom.isVoid(sc)){
          so=dom.listPrev(sc).length-1;
          sc=sc.parentNode;
        }
        if(dom.isBR(ec)){
          eo=dom.listPrev(ec).length-1;
          ec=ec.parentNode;
        }elseif(dom.isVoid(ec)){
          eo=dom.listPrev(ec).length;
          ec=ec.parentNode;
        }

        returnthis.create(sc,so,ec,eo);
      },

      /**
       *createWrappedRangefromnodeafterposition
       *
       *@param{Node}node
       *@return{WrappedRange}
       */
      createFromNodeBefore:function(node){
        returnthis.createFromNode(node).collapse(true);
      },

      /**
       *createWrappedRangefromnodeafterposition
       *
       *@param{Node}node
       *@return{WrappedRange}
       */
      createFromNodeAfter:function(node){
        returnthis.createFromNode(node).collapse();
      },

      /**
       *@method
       *
       *createWrappedRangefrombookmark
       *
       *@param{Node}editable
       *@param{Object}bookmark
       *@return{WrappedRange}
       */
      createFromBookmark:function(editable,bookmark){
        varsc=dom.fromOffsetPath(editable,bookmark.s.path);
        varso=bookmark.s.offset;
        varec=dom.fromOffsetPath(editable,bookmark.e.path);
        vareo=bookmark.e.offset;
        returnnewWrappedRange(sc,so,ec,eo);
      },

      /**
       *@method
       *
       *createWrappedRangefromparaBookmark
       *
       *@param{Object}bookmark
       *@param{Node[]}paras
       *@return{WrappedRange}
       */
      createFromParaBookmark:function(bookmark,paras){
        varso=bookmark.s.offset;
        vareo=bookmark.e.offset;
        varsc=dom.fromOffsetPath(list.head(paras),bookmark.s.path);
        varec=dom.fromOffsetPath(list.last(paras),bookmark.e.path);

        returnnewWrappedRange(sc,so,ec,eo);
      }
    };
  })();

  returnrange;
});
