define([
  'summernote/core/func',
  'summernote/core/list',
  'summernote/core/agent'
],function(func,list,agent){

  varNBSP_CHAR=String.fromCharCode(160);
  varZERO_WIDTH_NBSP_CHAR='\ufeff';

  /**
   *@classcore.dom
   *
   *Domfunctions
   *
   *@singleton
   *@alternateClassNamedom
   */
  vardom=(function(){
    /**
     *@methodisEditable
     *
     *returnswhethernodeis`note-editable`ornot.
     *
     *@param{Node}node
     *@return{Boolean}
     */
    varisEditable=function(node){
      returnnode&&$(node).hasClass('note-editable');
    };

    /**
     *@methodisControlSizing
     *
     *returnswhethernodeis`note-control-sizing`ornot.
     *
     *@param{Node}node
     *@return{Boolean}
     */
    varisControlSizing=function(node){
      returnnode&&$(node).hasClass('note-control-sizing');
    };

    /**
     *@method buildLayoutInfo
     *
     *buildlayoutInfofrom$editor(.note-editor)
     *
     *@param{jQuery}$editor
     *@return{Object}
     *@return{Function}return.editor
     *@return{Node}return.dropzone
     *@return{Node}return.toolbar
     *@return{Node}return.editable
     *@return{Node}return.codable
     *@return{Node}return.popover
     *@return{Node}return.handle
     *@return{Node}return.dialog
     */
    varbuildLayoutInfo=function($editor){
      varmakeFinder;

      //airmode
      if($editor.hasClass('note-air-editor')){
        //FLECTRA:editoron[data-note-id]attribute
        //varid=list.last($editor.attr('id').split('-'));
        varid=list.last($editor.attr('data-note-id').split('-'));
        makeFinder=function(sIdPrefix){
          returnfunction(){return$(sIdPrefix+id);};
        };

        return{
          editor:function(){return$editor;},
          holder:function(){return$editor.data('holder');},
          editable:function(){return$editor;},
          popover:makeFinder('#note-popover-'),
          handle:makeFinder('#note-handle-'),
          dialog:makeFinder('#note-dialog-')
        };

        //framemode
      }else{
        makeFinder=function(className,$base){
          $base=$base||$editor;
          returnfunction(){return$base.find(className);};
        };

        varoptions=$editor.data('options');
        var$dialogHolder=(options&&options.dialogsInBody)?$(document.body):null;

        return{
          editor:function(){return$editor;},
          holder:function(){return$editor.data('holder');},
          dropzone:makeFinder('.note-dropzone'),
          toolbar:makeFinder('.note-toolbar'),
          editable:makeFinder('.note-editable'),
          codable:makeFinder('.note-codable'),
          statusbar:makeFinder('.note-statusbar'),
          popover:makeFinder('.note-popover'),
          handle:makeFinder('.note-handle'),
          dialog:makeFinder('.note-dialog',$dialogHolder)
        };
      }
    };

    /**
     *returnsmakeLayoutInfofromeditor'sdescendantnode.
     *
     *@private
     *@param{Node}descendant
     *@return{Object}
     */
    varmakeLayoutInfo=function(descendant){
      var$target=$(descendant).closest('.note-editor,.note-air-editor,.note-air-layout');

      if(!$target.length){
        returnnull;
      }

      var$editor;
      if($target.is('.note-editor,.note-air-editor')){
        $editor=$target;
      }else{
        //FLECTRA:editoron[data-note-id]attribute
        //$editor=$('#note-editor-'+list.last($target.attr('id').split('-')));
        $editor=$('[data-note-id="'+list.last($target.attr('id').split('-'))+'"]');
      }

      returnbuildLayoutInfo($editor);
    };

    /**
     *@methodmakePredByNodeName
     *
     *returnspredicatewhichjudgewhethernodeNameissame
     *
     *@param{String}nodeName
     *@return{Function}
     */
    varmakePredByNodeName=function(nodeName){
      nodeName=nodeName.toUpperCase();
      returnfunction(node){
        returnnode&&node.nodeName.toUpperCase()===nodeName;
      };
    };

    /**
     *@methodisText
     *
     *
     *
     *@param{Node}node
     *@return{Boolean}trueifnode'stypeistext(3)
     */
    varisText=function(node){
      returnnode&&node.nodeType===3;
    };

    /**
     *ex)br,col,embed,hr,img,input,...
     *@seehttp://www.w3.org/html/wg/drafts/html/master/syntax.html#void-elements
     */
    varisVoid=function(node){
      returnnode&&/^BR|^IMG|^HR|^IFRAME|^BUTTON/.test(node.nodeName.toUpperCase());
    };

    varisPara=function(node){
      if(isEditable(node)){
        returnfalse;
      }

      //Chrome(v31.0),FF(v25.0.1)useDIVforparagraph
      returnnode&&/^DIV|^P|^LI|^H[1-7]/.test(node.nodeName.toUpperCase());
    };

    varisLi=makePredByNodeName('LI');

    varisPurePara=function(node){
      returnisPara(node)&&!isLi(node);
    };

    varisTable=makePredByNodeName('TABLE');

    varisInline=function(node){
      return!isBodyContainer(node)&&
             !isList(node)&&
             !isHr(node)&&
             !isPara(node)&&
             !isTable(node)&&
             !isBlockquote(node);
    };

    varisList=function(node){
      returnnode&&/^UL|^OL/.test(node.nodeName.toUpperCase());
    };

    varisHr=makePredByNodeName('HR');

    varisCell=function(node){
      returnnode&&/^TD|^TH/.test(node.nodeName.toUpperCase());
    };

    varisBlockquote=makePredByNodeName('BLOCKQUOTE');

    varisBodyContainer=function(node){
      returnisCell(node)||isBlockquote(node)||isEditable(node);
    };

    varisAnchor=makePredByNodeName('A');

    varisParaInline=function(node){
      returnisInline(node)&&!!ancestor(node,isPara);
    };

    varisBodyInline=function(node){
      returnisInline(node)&&!ancestor(node,isPara);
    };

    varisBody=makePredByNodeName('BODY');

    /**
     *returnswhethernodeBisclosestsiblingofnodeA
     *
     *@param{Node}nodeA
     *@param{Node}nodeB
     *@return{Boolean}
     */
    varisClosestSibling=function(nodeA,nodeB){
      returnnodeA.nextSibling===nodeB||
             nodeA.previousSibling===nodeB;
    };

    /**
     *returnsarrayofclosestsiblingswithnode
     *
     *@param{Node}node
     *@param{function}[pred]-predicatefunction
     *@return{Node[]}
     */
    varwithClosestSiblings=function(node,pred){
      pred=pred||func.ok;

      varsiblings=[];
      if(node.previousSibling&&pred(node.previousSibling)){
        siblings.push(node.previousSibling);
      }
      siblings.push(node);
      if(node.nextSibling&&pred(node.nextSibling)){
        siblings.push(node.nextSibling);
      }
      returnsiblings;
    };

    /**
     *blankHTMLforcursorposition
     *-[workaround]oldIEonlyworkswith&nbsp;
     *-[workaround]IE11andotherbrowserworkswithbogusbr
     */
    varblankHTML=agent.isMSIE&&agent.browserVersion<11?'&nbsp;':'<br>';

    /**
     *@methodnodeLength
     *
     *returns#text'stextsizeorelement'schildNodessize
     *
     *@param{Node}node
     */
    varnodeLength=function(node){
      if(isText(node)){
        returnnode.nodeValue.length;
      }

      returnnode.childNodes.length;
    };

    /**
     *returnswhethernodeisemptyornot.
     *
     *@param{Node}node
     *@return{Boolean}
     */
    varisEmpty=function(node){
      varlen=nodeLength(node);

      if(len===0){
        returntrue;
      }elseif(!isText(node)&&len===1&&node.innerHTML===blankHTML){
        //ex)<p><br></p>,<span><br></span>
        returntrue;
      }elseif(list.all(node.childNodes,isText)&&node.innerHTML===''){
        //ex)<p></p>,<span></span>
        returntrue;
      }

      returnfalse;
    };

    /**
     *paddingblankHTMLifnodeisempty(forcursorposition)
     */
    varpaddingBlankHTML=function(node){
      if(!isVoid(node)&&!nodeLength(node)){
        node.innerHTML=blankHTML;
      }
    };

    /**
     *findnearestancestorpredicatehit
     *
     *@param{Node}node
     *@param{Function}pred-predicatefunction
     */
    varancestor=function(node,pred){
      while(node){
        if(pred(node)){returnnode;}
        if(isEditable(node)){break;}

        node=node.parentNode;
      }
      returnnull;
    };

    /**
     *findnearestancestoronlysinglechildbloodlineandpredicatehit
     *
     *@param{Node}node
     *@param{Function}pred-predicatefunction
     */
    varsingleChildAncestor=function(node,pred){
      node=node.parentNode;

      while(node){
        if(nodeLength(node)!==1){break;}
        if(pred(node)){returnnode;}
        if(isEditable(node)){break;}

        node=node.parentNode;
      }
      returnnull;
    };

    /**
     *returnsnewarrayofancestornodes(untilpredicatehit).
     *
     *@param{Node}node
     *@param{Function}[optional]pred-predicatefunction
     */
    varlistAncestor=function(node,pred){
      pred=pred||func.fail;

      varancestors=[];
      ancestor(node,function(el){
        if(!isEditable(el)){
          ancestors.push(el);
        }

        returnpred(el);
      });
      returnancestors;
    };

    /**
     *findfarthestancestorpredicatehit
     */
    varlastAncestor=function(node,pred){
      varancestors=listAncestor(node);
      returnlist.last(ancestors.filter(pred));
    };

    /**
     *returnscommonancestornodebetweentwonodes.
     *
     *@param{Node}nodeA
     *@param{Node}nodeB
     */
    varcommonAncestor=function(nodeA,nodeB){
      varancestors=listAncestor(nodeA);
      for(varn=nodeB;n;n=n.parentNode){
        if($.inArray(n,ancestors)>-1){returnn;}
      }
      returnnull;//differencedocumentarea
    };

    /**
     *listingallprevioussiblings(untilpredicatehit).
     *
     *@param{Node}node
     *@param{Function}[optional]pred-predicatefunction
     */
    varlistPrev=function(node,pred){
      pred=pred||func.fail;

      varnodes=[];
      while(node){
        if(pred(node)){break;}
        nodes.push(node);
        node=node.previousSibling;
      }
      returnnodes;
    };

    /**
     *listingnextsiblings(untilpredicatehit).
     *
     *@param{Node}node
     *@param{Function}[pred]-predicatefunction
     */
    varlistNext=function(node,pred){
      pred=pred||func.fail;

      varnodes=[];
      while(node){
        if(pred(node)){break;}
        nodes.push(node);
        node=node.nextSibling;
      }
      returnnodes;
    };

    /**
     *listingdescendantnodes
     *
     *@param{Node}node
     *@param{Function}[pred]-predicatefunction
     */
    varlistDescendant=function(node,pred){
      vardescendents=[];
      pred=pred||func.ok;

      //startDFS(depthfirstsearch)withnode
      (functionfnWalk(current){
        if(node!==current&&pred(current)){
          descendents.push(current);
        }
        for(varidx=0,len=current.childNodes.length;idx<len;idx++){
          fnWalk(current.childNodes[idx]);
        }
      })(node);

      returndescendents;
    };

    /**
     *wrapnodewithnewtag.
     *
     *@param{Node}node
     *@param{Node}tagNameofwrapper
     *@return{Node}-wrapper
     */
    varwrap=function(node,wrapperName){
      varparent=node.parentNode;
      varwrapper=$('<'+wrapperName+'>')[0];

      parent.insertBefore(wrapper,node);
      wrapper.appendChild(node);

      returnwrapper;
    };

    /**
     *insertnodeafterpreceding
     *
     *@param{Node}node
     *@param{Node}preceding-predicatefunction
     */
    varinsertAfter=function(node,preceding){
      varnext=preceding.nextSibling,parent=preceding.parentNode;
      if(next){
        parent.insertBefore(node,next);
      }else{
        parent.appendChild(node);
      }
      returnnode;
    };

    /**
     *appendelements.
     *
     *@param{Node}node
     *@param{Collection}aChild
     */
    varappendChildNodes=function(node,aChild){
      $.each(aChild,function(idx,child){
        node.appendChild(child);
      });
      returnnode;
    };

    /**
     *returnswhetherboundaryPointisleftedgeornot.
     *
     *@param{BoundaryPoint}point
     *@return{Boolean}
     */
    varisLeftEdgePoint=function(point){
      returnpoint.offset===0;
    };

    /**
     *returnswhetherboundaryPointisrightedgeornot.
     *
     *@param{BoundaryPoint}point
     *@return{Boolean}
     */
    varisRightEdgePoint=function(point){
      returnpoint.offset===nodeLength(point.node);
    };

    /**
     *returnswhetherboundaryPointisedgeornot.
     *
     *@param{BoundaryPoint}point
     *@return{Boolean}
     */
    varisEdgePoint=function(point){
      returnisLeftEdgePoint(point)||isRightEdgePoint(point);
    };

    /**
     *returnswheternodeisleftedgeofancestorornot.
     *
     *@param{Node}node
     *@param{Node}ancestor
     *@return{Boolean}
     */
    varisLeftEdgeOf=function(node,ancestor){
      while(node&&node!==ancestor){
        if(position(node)!==0){
          returnfalse;
        }
        node=node.parentNode;
      }

      returntrue;
    };

    /**
     *returnswhethernodeisrightedgeofancestorornot.
     *
     *@param{Node}node
     *@param{Node}ancestor
     *@return{Boolean}
     */
    varisRightEdgeOf=function(node,ancestor){
      while(node&&node!==ancestor){
        if(position(node)!==nodeLength(node.parentNode)-1){
          returnfalse;
        }
        node=node.parentNode;
      }

      returntrue;
    };

    /**
     *returnswhetherpointisleftedgeofancestorornot.
     *@param{BoundaryPoint}point
     *@param{Node}ancestor
     *@return{Boolean}
     */
    varisLeftEdgePointOf=function(point,ancestor){
      returnisLeftEdgePoint(point)&&isLeftEdgeOf(point.node,ancestor);
    };

    /**
     *returnswhetherpointisrightedgeofancestorornot.
     *@param{BoundaryPoint}point
     *@param{Node}ancestor
     *@return{Boolean}
     */
    varisRightEdgePointOf=function(point,ancestor){
      returnisRightEdgePoint(point)&&isRightEdgeOf(point.node,ancestor);
    };

    /**
     *returnsoffsetfromparent.
     *
     *@param{Node}node
     */
    varposition=function(node){
      varoffset=0;
      while((node=node.previousSibling)){
        offset+=1;
      }
      returnoffset;
    };

    varhasChildren=function(node){
      return!!(node&&node.childNodes&&node.childNodes.length);
    };

    /**
     *returnspreviousboundaryPoint
     *
     *@param{BoundaryPoint}point
     *@param{Boolean}isSkipInnerOffset
     *@return{BoundaryPoint}
     */
    varprevPoint=function(point,isSkipInnerOffset){
      varnode,offset;

      if(point.offset===0){
        if(isEditable(point.node)){
          returnnull;
        }

        node=point.node.parentNode;
        offset=position(point.node);
      }elseif(hasChildren(point.node)){
        node=point.node.childNodes[point.offset-1];
        offset=nodeLength(node);
      }else{
        node=point.node;
        offset=isSkipInnerOffset?0:point.offset-1;
      }

      return{
        node:node,
        offset:offset
      };
    };

    /**
     *returnsnextboundaryPoint
     *
     *@param{BoundaryPoint}point
     *@param{Boolean}isSkipInnerOffset
     *@return{BoundaryPoint}
     */
    varnextPoint=function(point,isSkipInnerOffset){
      varnode,offset;

      if(nodeLength(point.node)===point.offset){
        if(isEditable(point.node)){
          returnnull;
        }

        node=point.node.parentNode;
        offset=position(point.node)+1;
      }elseif(hasChildren(point.node)){
        node=point.node.childNodes[point.offset];
        offset=0;
      }else{
        node=point.node;
        offset=isSkipInnerOffset?nodeLength(point.node):point.offset+1;
      }

      return{
        node:node,
        offset:offset
      };
    };

    /**
     *returnswhetherpointAandpointBissameornot.
     *
     *@param{BoundaryPoint}pointA
     *@param{BoundaryPoint}pointB
     *@return{Boolean}
     */
    varisSamePoint=function(pointA,pointB){
      returnpointA.node===pointB.node&&pointA.offset===pointB.offset;
    };

    /**
     *returnswhetherpointisvisible(cansetcursor)ornot.
     *
     *@param{BoundaryPoint}point
     *@return{Boolean}
     */
    varisVisiblePoint=function(point){
      if(isText(point.node)||!hasChildren(point.node)||isEmpty(point.node)){
        returntrue;
      }

      varleftNode=point.node.childNodes[point.offset-1];
      varrightNode=point.node.childNodes[point.offset];
      if((!leftNode||isVoid(leftNode))&&(!rightNode||isVoid(rightNode))){
        returntrue;
      }

      returnfalse;
    };

    /**
     *@methodprevPointUtil
     *
     *@param{BoundaryPoint}point
     *@param{Function}pred
     *@return{BoundaryPoint}
     */
    varprevPointUntil=function(point,pred){
      while(point){
        if(pred(point)){
          returnpoint;
        }

        point=prevPoint(point);
      }

      returnnull;
    };

    /**
     *@methodnextPointUntil
     *
     *@param{BoundaryPoint}point
     *@param{Function}pred
     *@return{BoundaryPoint}
     */
    varnextPointUntil=function(point,pred){
      while(point){
        if(pred(point)){
          returnpoint;
        }

        point=nextPoint(point);
      }

      returnnull;
    };

    /**
     *returnswhetherpointhascharacterornot.
     *
     *@param{Point}point
     *@return{Boolean}
     */
    varisCharPoint=function(point){
      if(!isText(point.node)){
        returnfalse;
      }

      varch=point.node.nodeValue.charAt(point.offset-1);
      returnch&&(ch!==''&&ch!==NBSP_CHAR);
    };

    /**
     *@methodwalkPoint
     *
     *@param{BoundaryPoint}startPoint
     *@param{BoundaryPoint}endPoint
     *@param{Function}handler
     *@param{Boolean}isSkipInnerOffset
     */
    varwalkPoint=function(startPoint,endPoint,handler,isSkipInnerOffset){
      varpoint=startPoint;

      while(point){
        handler(point);

        if(isSamePoint(point,endPoint)){
          break;
        }

        varisSkipOffset=isSkipInnerOffset&&
                           startPoint.node!==point.node&&
                           endPoint.node!==point.node;
        point=nextPoint(point,isSkipOffset);
      }
    };

    /**
     *@methodmakeOffsetPath
     *
     *returnoffsetPath(arrayofoffset)fromancestor
     *
     *@param{Node}ancestor-ancestornode
     *@param{Node}node
     */
    varmakeOffsetPath=function(ancestor,node){
      varancestors=listAncestor(node,func.eq(ancestor));
      returnancestors.map(position).reverse();
    };

    /**
     *@methodfromOffsetPath
     *
     *returnelementfromoffsetPath(arrayofoffset)
     *
     *@param{Node}ancestor-ancestornode
     *@param{array}offsets-offsetPath
     */
    varfromOffsetPath=function(ancestor,offsets){
      varcurrent=ancestor;
      for(vari=0,len=offsets.length;i<len;i++){
        if(current.childNodes.length<=offsets[i]){
          current=current.childNodes[current.childNodes.length-1];
        }else{
          current=current.childNodes[offsets[i]];
        }
      }
      returncurrent;
    };

    /**
     *@methodsplitNode
     *
     *splitelementor#text
     *
     *@param{BoundaryPoint}point
     *@param{Object}[options]
     *@param{Boolean}[options.isSkipPaddingBlankHTML]-default:false
     *@param{Boolean}[options.isNotSplitEdgePoint]-default:false
     *@return{Node}rightnodeofboundaryPoint
     */
    varsplitNode=function(point,options){
      varisSkipPaddingBlankHTML=options&&options.isSkipPaddingBlankHTML;
      varisNotSplitEdgePoint=options&&options.isNotSplitEdgePoint;

      //edgecase
      if(isEdgePoint(point)&&(isText(point.node)||isNotSplitEdgePoint)){
        if(isLeftEdgePoint(point)){
          returnpoint.node;
        }elseif(isRightEdgePoint(point)){
          returnpoint.node.nextSibling;
        }
      }

      //split#text
      if(isText(point.node)){
        returnpoint.node.splitText(point.offset);
      }else{
        varchildNode=point.node.childNodes[point.offset];
        varclone=insertAfter(point.node.cloneNode(false),point.node);
        appendChildNodes(clone,listNext(childNode));

        if(!isSkipPaddingBlankHTML){
          paddingBlankHTML(point.node);
          paddingBlankHTML(clone);
        }

        returnclone;
      }
    };

    /**
     *@methodsplitTree
     *
     *splittreebypoint
     *
     *@param{Node}root-splitroot
     *@param{BoundaryPoint}point
     *@param{Object}[options]
     *@param{Boolean}[options.isSkipPaddingBlankHTML]-default:false
     *@param{Boolean}[options.isNotSplitEdgePoint]-default:false
     *@return{Node}rightnodeofboundaryPoint
     */
    varsplitTree=function(root,point,options){
      //ex)[#text,<span>,<p>]
      varancestors=listAncestor(point.node,func.eq(root));

      if(!ancestors.length){
        returnnull;
      }elseif(ancestors.length===1){
        returnsplitNode(point,options);
      }

      returnancestors.reduce(function(node,parent){
        if(node===point.node){
          node=splitNode(point,options);
        }

        returnsplitNode({
          node:parent,
          offset:node?dom.position(node):nodeLength(parent)
        },options);
      });
    };

    /**
     *splitpoint
     *
     *@param{Point}point
     *@param{Boolean}isInline
     *@return{Object}
     */
    varsplitPoint=function(point,isInline){
      //findsplitRoot,container
      // -inline:splitRootisachildofparagraph
      // -block:splitRootisachildofbodyContainer
      varpred=isInline?isPara:isBodyContainer;
      varancestors=listAncestor(point.node,pred);
      vartopAncestor=list.last(ancestors)||point.node;

      varsplitRoot,container;
      if(pred(topAncestor)){
        splitRoot=ancestors[ancestors.length-2];
        container=topAncestor;
      }else{
        splitRoot=topAncestor;
        container=splitRoot.parentNode;
      }

      //ifsplitRootisexists,splitwithsplitTree
      varpivot=splitRoot&&splitTree(splitRoot,point,{
        isSkipPaddingBlankHTML:isInline,
        isNotSplitEdgePoint:isInline
      });

      //ifcontainerispoint.node,findpivotwithpoint.offset
      if(!pivot&&container===point.node){
        pivot=point.node.childNodes[point.offset];
      }

      return{
        rightNode:pivot,
        container:container
      };
    };

    varcreate=function(nodeName){
      returndocument.createElement(nodeName);
    };

    varcreateText=function(text){
      returndocument.createTextNode(text);
    };

    /**
     *@methodremove
     *
     *removenode,(isRemoveChild:removechildornot)
     *
     *@param{Node}node
     *@param{Boolean}isRemoveChild
     */
    varremove=function(node,isRemoveChild){
      if(!node||!node.parentNode){return;}
      if(node.removeNode){returnnode.removeNode(isRemoveChild);}

      varparent=node.parentNode;
      if(!isRemoveChild){
        varnodes=[];
        vari,len;
        for(i=0,len=node.childNodes.length;i<len;i++){
          nodes.push(node.childNodes[i]);
        }

        for(i=0,len=nodes.length;i<len;i++){
          parent.insertBefore(nodes[i],node);
        }
      }

      parent.removeChild(node);
    };

    /**
     *@methodremoveWhile
     *
     *@param{Node}node
     *@param{Function}pred
     */
    varremoveWhile=function(node,pred){
      while(node){
        if(isEditable(node)||!pred(node)){
          break;
        }

        varparent=node.parentNode;
        remove(node);
        node=parent;
      }
    };

    /**
     *@methodreplace
     *
     *replacenodewithprovidednodeName
     *
     *@param{Node}node
     *@param{String}nodeName
     *@return{Node}-newnode
     */
    varreplace=function(node,nodeName){
      if(node.nodeName.toUpperCase()===nodeName.toUpperCase()){
        returnnode;
      }

      varnewNode=create(nodeName);

      if(node.style.cssText){
        newNode.style.cssText=node.style.cssText;
      }

      appendChildNodes(newNode,list.from(node.childNodes));
      insertAfter(newNode,node);
      remove(node);

      returnnewNode;
    };

    varisTextarea=makePredByNodeName('TEXTAREA');

    /**
     *@param{jQuery}$node
     *@param{Boolean}[stripLinebreaks]-default:false
     */
    varvalue=function($node,stripLinebreaks){
      varval=isTextarea($node[0])?$node.val():$node.html();
      if(stripLinebreaks){
        returnval.replace(/[\n\r]/g,'');
      }
      returnval;
    };

    /**
     *@methodhtml
     *
     *gettheHTMLcontentsofnode
     *
     *@param{jQuery}$node
     *@param{Boolean}[isNewlineOnBlock]
     */
    varhtml=function($node,isNewlineOnBlock){
      varmarkup=value($node);

      if(isNewlineOnBlock){
        varregexTag=/<(\/?)(\b(?!!)[^>\s]*)(.*?)(\s*\/?>)/g;
        markup=markup.replace(regexTag,function(match,endSlash,name){
          name=name.toUpperCase();
          varisEndOfInlineContainer=/^DIV|^TD|^TH|^P|^LI|^H[1-7]/.test(name)&&
                                       !!endSlash;
          varisBlockNode=/^BLOCKQUOTE|^TABLE|^TBODY|^TR|^HR|^UL|^OL/.test(name);

          returnmatch+((isEndOfInlineContainer||isBlockNode)?'\n':'');
        });
        markup=$.trim(markup);
      }

      returnmarkup;
    };

    return{
      /**@property{String}NBSP_CHAR*/
      NBSP_CHAR:NBSP_CHAR,
      /**@property{String}ZERO_WIDTH_NBSP_CHAR*/
      ZERO_WIDTH_NBSP_CHAR:ZERO_WIDTH_NBSP_CHAR,
      /**@property{String}blank*/
      blank:blankHTML,
      /**@property{String}emptyPara*/
      emptyPara:'<p>'+blankHTML+'</p>',
      makePredByNodeName:makePredByNodeName,
      isEditable:isEditable,
      isControlSizing:isControlSizing,
      buildLayoutInfo:buildLayoutInfo,
      makeLayoutInfo:makeLayoutInfo,
      isText:isText,
      isVoid:isVoid,
      isPara:isPara,
      isPurePara:isPurePara,
      isInline:isInline,
      isBlock:func.not(isInline),
      isBodyInline:isBodyInline,
      isBody:isBody,
      isParaInline:isParaInline,
      isList:isList,
      isTable:isTable,
      isCell:isCell,
      isBlockquote:isBlockquote,
      isBodyContainer:isBodyContainer,
      isAnchor:isAnchor,
      isDiv:makePredByNodeName('DIV'),
      isLi:isLi,
      isBR:makePredByNodeName('BR'),
      isSpan:makePredByNodeName('SPAN'),
      isB:makePredByNodeName('B'),
      isU:makePredByNodeName('U'),
      isS:makePredByNodeName('S'),
      isI:makePredByNodeName('I'),
      isImg:makePredByNodeName('IMG'),
      isTextarea:isTextarea,
      isEmpty:isEmpty,
      isEmptyAnchor:func.and(isAnchor,isEmpty),
      isClosestSibling:isClosestSibling,
      withClosestSiblings:withClosestSiblings,
      nodeLength:nodeLength,
      isLeftEdgePoint:isLeftEdgePoint,
      isRightEdgePoint:isRightEdgePoint,
      isEdgePoint:isEdgePoint,
      isLeftEdgeOf:isLeftEdgeOf,
      isRightEdgeOf:isRightEdgeOf,
      isLeftEdgePointOf:isLeftEdgePointOf,
      isRightEdgePointOf:isRightEdgePointOf,
      prevPoint:prevPoint,
      nextPoint:nextPoint,
      isSamePoint:isSamePoint,
      isVisiblePoint:isVisiblePoint,
      prevPointUntil:prevPointUntil,
      nextPointUntil:nextPointUntil,
      isCharPoint:isCharPoint,
      walkPoint:walkPoint,
      ancestor:ancestor,
      singleChildAncestor:singleChildAncestor,
      listAncestor:listAncestor,
      lastAncestor:lastAncestor,
      listNext:listNext,
      listPrev:listPrev,
      listDescendant:listDescendant,
      commonAncestor:commonAncestor,
      wrap:wrap,
      insertAfter:insertAfter,
      appendChildNodes:appendChildNodes,
      position:position,
      hasChildren:hasChildren,
      makeOffsetPath:makeOffsetPath,
      fromOffsetPath:fromOffsetPath,
      splitTree:splitTree,
      splitPoint:splitPoint,
      create:create,
      createText:createText,
      remove:remove,
      removeWhile:removeWhile,
      replace:replace,
      html:html,
      value:value
    };
  })();

  returndom;
});
