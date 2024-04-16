/**!
 *@fileOverviewKickasslibrarytocreateandplacepoppersneartheirreferenceelements.
 *@version1.14.3
 *@license
 *Copyright(c)2016FedericoZivoloandcontributors
 *
 *Permissionisherebygranted,freeofcharge,toanypersonobtainingacopy
 *ofthissoftwareandassociateddocumentationfiles(the"Software"),todeal
 *intheSoftwarewithoutrestriction,includingwithoutlimitationtherights
 *touse,copy,modify,merge,publish,distribute,sublicense,and/orsell
 *copiesoftheSoftware,andtopermitpersonstowhomtheSoftwareis
 *furnishedtodoso,subjecttothefollowingconditions:
 *
 *Theabovecopyrightnoticeandthispermissionnoticeshallbeincludedinall
 *copiesorsubstantialportionsoftheSoftware.
 *
 *THESOFTWAREISPROVIDED"ASIS",WITHOUTWARRANTYOFANYKIND,EXPRESSOR
 *IMPLIED,INCLUDINGBUTNOTLIMITEDTOTHEWARRANTIESOFMERCHANTABILITY,
 *FITNESSFORAPARTICULARPURPOSEANDNONINFRINGEMENT.INNOEVENTSHALLTHE
 *AUTHORSORCOPYRIGHTHOLDERSBELIABLEFORANYCLAIM,DAMAGESOROTHER
 *LIABILITY,WHETHERINANACTIONOFCONTRACT,TORTOROTHERWISE,ARISINGFROM,
 *OUTOFORINCONNECTIONWITHTHESOFTWAREORTHEUSEOROTHERDEALINGSINTHE
 *SOFTWARE.
 */
(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
    typeofdefine==='function'&&define.amd?define(factory):
    (global.Popper=factory());
}(this,(function(){'usestrict';

varisBrowser=typeofwindow!=='undefined'&&typeofdocument!=='undefined';

varlongerTimeoutBrowsers=['Edge','Trident','Firefox'];
vartimeoutDuration=0;
for(vari=0;i<longerTimeoutBrowsers.length;i+=1){
  if(isBrowser&&navigator.userAgent.indexOf(longerTimeoutBrowsers[i])>=0){
    timeoutDuration=1;
    break;
  }
}

functionmicrotaskDebounce(fn){
  varcalled=false;
  returnfunction(){
    if(called){
      return;
    }
    called=true;
    window.Promise.resolve().then(function(){
      called=false;
      fn();
    });
  };
}

functiontaskDebounce(fn){
  varscheduled=false;
  returnfunction(){
    if(!scheduled){
      scheduled=true;
      setTimeout(function(){
        scheduled=false;
        fn();
      },timeoutDuration);
    }
  };
}

varsupportsMicroTasks=isBrowser&&window.Promise;

/**
*Createadebouncedversionofamethod,that'sasynchronouslydeferred
*butcalledintheminimumtimepossible.
*
*@method
*@memberofPopper.Utils
*@argument{Function}fn
*@returns{Function}
*/
vardebounce=supportsMicroTasks?microtaskDebounce:taskDebounce;

/**
 *Checkifthegivenvariableisafunction
 *@method
 *@memberofPopper.Utils
 *@argument{Any}functionToCheck-variabletocheck
 *@returns{Boolean}answerto:isafunction?
 */
functionisFunction(functionToCheck){
  vargetType={};
  returnfunctionToCheck&&getType.toString.call(functionToCheck)==='[objectFunction]';
}

/**
 *GetCSScomputedpropertyofthegivenelement
 *@method
 *@memberofPopper.Utils
 *@argument{Eement}element
 *@argument{String}property
 */
functiongetStyleComputedProperty(element,property){
  if(element.nodeType!==1){
    return[];
  }
  //NOTE:1DOMaccesshere
  varcss=getComputedStyle(element,null);
  returnproperty?css[property]:css;
}

/**
 *ReturnstheparentNodeorthehostoftheelement
 *@method
 *@memberofPopper.Utils
 *@argument{Element}element
 *@returns{Element}parent
 */
functiongetParentNode(element){
  if(element.nodeName==='HTML'){
    returnelement;
  }
  returnelement.parentNode||element.host;
}

/**
 *Returnsthescrollingparentofthegivenelement
 *@method
 *@memberofPopper.Utils
 *@argument{Element}element
 *@returns{Element}scrollparent
 */
functiongetScrollParent(element){
  //Returnbody,`getScroll`willtakecaretogetthecorrect`scrollTop`fromit
  if(!element){
    returndocument.body;
  }

  switch(element.nodeName){
    case'HTML':
    case'BODY':
      returnelement.ownerDocument.body;
    case'#document':
      returnelement.body;
  }

  //Firefoxwantustocheck`-x`and`-y`variationsaswell

  var_getStyleComputedProp=getStyleComputedProperty(element),
      overflow=_getStyleComputedProp.overflow,
      overflowX=_getStyleComputedProp.overflowX,
      overflowY=_getStyleComputedProp.overflowY;

  if(/(auto|scroll|overlay)/.test(overflow+overflowY+overflowX)){
    returnelement;
  }

  returngetScrollParent(getParentNode(element));
}

varisIE11=isBrowser&&!!(window.MSInputMethodContext&&document.documentMode);
varisIE10=isBrowser&&/MSIE10/.test(navigator.userAgent);

/**
 *DeterminesifthebrowserisInternetExplorer
 *@method
 *@memberofPopper.Utils
 *@param{Number}versiontocheck
 *@returns{Boolean}isIE
 */
functionisIE(version){
  if(version===11){
    returnisIE11;
  }
  if(version===10){
    returnisIE10;
  }
  returnisIE11||isIE10;
}

/**
 *Returnstheoffsetparentofthegivenelement
 *@method
 *@memberofPopper.Utils
 *@argument{Element}element
 *@returns{Element}offsetparent
 */
functiongetOffsetParent(element){
  if(!element){
    returndocument.documentElement;
  }

  varnoOffsetParent=isIE(10)?document.body:null;

  //NOTE:1DOMaccesshere
  varoffsetParent=element.offsetParent;
  //Skiphiddenelementswhichdon'thaveanoffsetParent
  while(offsetParent===noOffsetParent&&element.nextElementSibling){
    offsetParent=(element=element.nextElementSibling).offsetParent;
  }

  varnodeName=offsetParent&&offsetParent.nodeName;

  if(!nodeName||nodeName==='BODY'||nodeName==='HTML'){
    returnelement?element.ownerDocument.documentElement:document.documentElement;
  }

  //.offsetParentwillreturntheclosestTDorTABLEincase
  //nooffsetParentispresent,Ihatethisjob...
  if(['TD','TABLE'].indexOf(offsetParent.nodeName)!==-1&&getStyleComputedProperty(offsetParent,'position')==='static'){
    returngetOffsetParent(offsetParent);
  }

  returnoffsetParent;
}

functionisOffsetContainer(element){
  varnodeName=element.nodeName;

  if(nodeName==='BODY'){
    returnfalse;
  }
  returnnodeName==='HTML'||getOffsetParent(element.firstElementChild)===element;
}

/**
 *Findstherootnode(document,shadowDOMroot)ofthegivenelement
 *@method
 *@memberofPopper.Utils
 *@argument{Element}node
 *@returns{Element}rootnode
 */
functiongetRoot(node){
  if(node.parentNode!==null){
    returngetRoot(node.parentNode);
  }

  returnnode;
}

/**
 *Findstheoffsetparentcommontothetwoprovidednodes
 *@method
 *@memberofPopper.Utils
 *@argument{Element}element1
 *@argument{Element}element2
 *@returns{Element}commonoffsetparent
 */
functionfindCommonOffsetParent(element1,element2){
  //Thischeckisneededtoavoiderrorsincaseoneoftheelementsisn'tdefinedforanyreason
  if(!element1||!element1.nodeType||!element2||!element2.nodeType){
    returndocument.documentElement;
  }

  //Herewemakesuretogiveas"start"theelementthatcomesfirstintheDOM
  varorder=element1.compareDocumentPosition(element2)&Node.DOCUMENT_POSITION_FOLLOWING;
  varstart=order?element1:element2;
  varend=order?element2:element1;

  //Getcommonancestorcontainer
  varrange=document.createRange();
  range.setStart(start,0);
  range.setEnd(end,0);
  varcommonAncestorContainer=range.commonAncestorContainer;

  //Bothnodesareinside#document

  if(element1!==commonAncestorContainer&&element2!==commonAncestorContainer||start.contains(end)){
    if(isOffsetContainer(commonAncestorContainer)){
      returncommonAncestorContainer;
    }

    returngetOffsetParent(commonAncestorContainer);
  }

  //oneofthenodesisinsideshadowDOM,findwhichone
  varelement1root=getRoot(element1);
  if(element1root.host){
    returnfindCommonOffsetParent(element1root.host,element2);
  }else{
    returnfindCommonOffsetParent(element1,getRoot(element2).host);
  }
}

/**
 *Getsthescrollvalueofthegivenelementinthegivenside(topandleft)
 *@method
 *@memberofPopper.Utils
 *@argument{Element}element
 *@argument{String}side`top`or`left`
 *@returns{number}amountofscrolledpixels
 */
functiongetScroll(element){
  varside=arguments.length>1&&arguments[1]!==undefined?arguments[1]:'top';

  varupperSide=side==='top'?'scrollTop':'scrollLeft';
  varnodeName=element.nodeName;

  if(nodeName==='BODY'||nodeName==='HTML'){
    varhtml=element.ownerDocument.documentElement;
    varscrollingElement=element.ownerDocument.scrollingElement||html;
    returnscrollingElement[upperSide];
  }

  returnelement[upperSide];
}

/*
 *Sumorsubtracttheelementscrollvalues(leftandtop)fromagivenrectobject
 *@method
 *@memberofPopper.Utils
 *@param{Object}rect-Rectobjectyouwanttochange
 *@param{HTMLElement}element-Theelementfromthefunctionreadsthescrollvalues
 *@param{Boolean}subtract-settotrueifyouwanttosubtractthescrollvalues
 *@return{Object}rect-Themodifierrectobject
 */
functionincludeScroll(rect,element){
  varsubtract=arguments.length>2&&arguments[2]!==undefined?arguments[2]:false;

  varscrollTop=getScroll(element,'top');
  varscrollLeft=getScroll(element,'left');
  varmodifier=subtract?-1:1;
  rect.top+=scrollTop*modifier;
  rect.bottom+=scrollTop*modifier;
  rect.left+=scrollLeft*modifier;
  rect.right+=scrollLeft*modifier;
  returnrect;
}

/*
 *Helpertodetectbordersofagivenelement
 *@method
 *@memberofPopper.Utils
 *@param{CSSStyleDeclaration}styles
 *Resultof`getStyleComputedProperty`onthegivenelement
 *@param{String}axis-`x`or`y`
 *@return{number}borders-Theborderssizeofthegivenaxis
 */

functiongetBordersSize(styles,axis){
  varsideA=axis==='x'?'Left':'Top';
  varsideB=sideA==='Left'?'Right':'Bottom';

  returnparseFloat(styles['border'+sideA+'Width'],10)+parseFloat(styles['border'+sideB+'Width'],10);
}

functiongetSize(axis,body,html,computedStyle){
  returnMath.max(body['offset'+axis],body['scroll'+axis],html['client'+axis],html['offset'+axis],html['scroll'+axis],isIE(10)?html['offset'+axis]+computedStyle['margin'+(axis==='Height'?'Top':'Left')]+computedStyle['margin'+(axis==='Height'?'Bottom':'Right')]:0);
}

functiongetWindowSizes(){
  varbody=document.body;
  varhtml=document.documentElement;
  varcomputedStyle=isIE(10)&&getComputedStyle(html);

  return{
    height:getSize('Height',body,html,computedStyle),
    width:getSize('Width',body,html,computedStyle)
  };
}

varclassCallCheck=function(instance,Constructor){
  if(!(instanceinstanceofConstructor)){
    thrownewTypeError("Cannotcallaclassasafunction");
  }
};

varcreateClass=function(){
  functiondefineProperties(target,props){
    for(vari=0;i<props.length;i++){
      vardescriptor=props[i];
      descriptor.enumerable=descriptor.enumerable||false;
      descriptor.configurable=true;
      if("value"indescriptor)descriptor.writable=true;
      Object.defineProperty(target,descriptor.key,descriptor);
    }
  }

  returnfunction(Constructor,protoProps,staticProps){
    if(protoProps)defineProperties(Constructor.prototype,protoProps);
    if(staticProps)defineProperties(Constructor,staticProps);
    returnConstructor;
  };
}();





vardefineProperty=function(obj,key,value){
  if(keyinobj){
    Object.defineProperty(obj,key,{
      value:value,
      enumerable:true,
      configurable:true,
      writable:true
    });
  }else{
    obj[key]=value;
  }

  returnobj;
};

var_extends=Object.assign||function(target){
  for(vari=1;i<arguments.length;i++){
    varsource=arguments[i];

    for(varkeyinsource){
      if(Object.prototype.hasOwnProperty.call(source,key)){
        target[key]=source[key];
      }
    }
  }

  returntarget;
};

/**
 *Givenelementoffsets,generateanoutputsimilartogetBoundingClientRect
 *@method
 *@memberofPopper.Utils
 *@argument{Object}offsets
 *@returns{Object}ClientRectlikeoutput
 */
functiongetClientRect(offsets){
  return_extends({},offsets,{
    right:offsets.left+offsets.width,
    bottom:offsets.top+offsets.height
  });
}

/**
 *Getboundingclientrectofgivenelement
 *@method
 *@memberofPopper.Utils
 *@param{HTMLElement}element
 *@return{Object}clientrect
 */
functiongetBoundingClientRect(element){
  varrect={};

  //IE1010FIX:Please,don'task,theelementisn't
  //consideredinDOMinsomecircumstances...
  //Thisisn'treproducibleinIE10compatibilitymodeofIE11
  try{
    if(isIE(10)){
      rect=element.getBoundingClientRect();
      varscrollTop=getScroll(element,'top');
      varscrollLeft=getScroll(element,'left');
      rect.top+=scrollTop;
      rect.left+=scrollLeft;
      rect.bottom+=scrollTop;
      rect.right+=scrollLeft;
    }else{
      rect=element.getBoundingClientRect();
    }
  }catch(e){}

  varresult={
    left:rect.left,
    top:rect.top,
    width:rect.right-rect.left,
    height:rect.bottom-rect.top
  };

  //subtractscrollbarsizefromsizes
  varsizes=element.nodeName==='HTML'?getWindowSizes():{};
  varwidth=sizes.width||element.clientWidth||result.right-result.left;
  varheight=sizes.height||element.clientHeight||result.bottom-result.top;

  varhorizScrollbar=element.offsetWidth-width;
  varvertScrollbar=element.offsetHeight-height;

  //ifanhypotheticalscrollbarisdetected,wemustbesureit'snota`border`
  //wemakethischeckconditionalforperformancereasons
  if(horizScrollbar||vertScrollbar){
    varstyles=getStyleComputedProperty(element);
    horizScrollbar-=getBordersSize(styles,'x');
    vertScrollbar-=getBordersSize(styles,'y');

    result.width-=horizScrollbar;
    result.height-=vertScrollbar;
  }

  returngetClientRect(result);
}

functiongetOffsetRectRelativeToArbitraryNode(children,parent){
  varfixedPosition=arguments.length>2&&arguments[2]!==undefined?arguments[2]:false;

  varisIE10=isIE(10);
  varisHTML=parent.nodeName==='HTML';
  varchildrenRect=getBoundingClientRect(children);
  varparentRect=getBoundingClientRect(parent);
  varscrollParent=getScrollParent(children);

  varstyles=getStyleComputedProperty(parent);
  varborderTopWidth=parseFloat(styles.borderTopWidth,10);
  varborderLeftWidth=parseFloat(styles.borderLeftWidth,10);

  //Incaseswheretheparentisfixed,wemustignorenegativescrollinoffsetcalc
  if(fixedPosition&&parent.nodeName==='HTML'){
    parentRect.top=Math.max(parentRect.top,0);
    parentRect.left=Math.max(parentRect.left,0);
  }
  varoffsets=getClientRect({
    top:childrenRect.top-parentRect.top-borderTopWidth,
    left:childrenRect.left-parentRect.left-borderLeftWidth,
    width:childrenRect.width,
    height:childrenRect.height
  });
  offsets.marginTop=0;
  offsets.marginLeft=0;

  //SubtractmarginsofdocumentElementincaseit'sbeingusedasparent
  //wedothisonlyonHTMLbecauseit'stheonlyelementthatbehaves
  //differentlywhenmarginsareappliedtoit.Themarginsareincludedin
  //theboxofthedocumentElement,intheothercasesnot.
  if(!isIE10&&isHTML){
    varmarginTop=parseFloat(styles.marginTop,10);
    varmarginLeft=parseFloat(styles.marginLeft,10);

    offsets.top-=borderTopWidth-marginTop;
    offsets.bottom-=borderTopWidth-marginTop;
    offsets.left-=borderLeftWidth-marginLeft;
    offsets.right-=borderLeftWidth-marginLeft;

    //AttachmarginTopandmarginLeftbecauseinsomecircumstanceswemayneedthem
    offsets.marginTop=marginTop;
    offsets.marginLeft=marginLeft;
  }

  if(isIE10&&!fixedPosition?parent.contains(scrollParent):parent===scrollParent&&scrollParent.nodeName!=='BODY'){
    offsets=includeScroll(offsets,parent);
  }

  returnoffsets;
}

functiongetViewportOffsetRectRelativeToArtbitraryNode(element){
  varexcludeScroll=arguments.length>1&&arguments[1]!==undefined?arguments[1]:false;

  varhtml=element.ownerDocument.documentElement;
  varrelativeOffset=getOffsetRectRelativeToArbitraryNode(element,html);
  varwidth=Math.max(html.clientWidth,window.innerWidth||0);
  varheight=Math.max(html.clientHeight,window.innerHeight||0);

  varscrollTop=!excludeScroll?getScroll(html):0;
  varscrollLeft=!excludeScroll?getScroll(html,'left'):0;

  varoffset={
    top:scrollTop-relativeOffset.top+relativeOffset.marginTop,
    left:scrollLeft-relativeOffset.left+relativeOffset.marginLeft,
    width:width,
    height:height
  };

  returngetClientRect(offset);
}

/**
 *Checkifthegivenelementisfixedorisinsideafixedparent
 *@method
 *@memberofPopper.Utils
 *@argument{Element}element
 *@argument{Element}customContainer
 *@returns{Boolean}answerto"isFixed?"
 */
functionisFixed(element){
  varnodeName=element.nodeName;
  if(nodeName==='BODY'||nodeName==='HTML'){
    returnfalse;
  }
  if(getStyleComputedProperty(element,'position')==='fixed'){
    returntrue;
  }
  returnisFixed(getParentNode(element));
}

/**
 *Findsthefirstparentofanelementthathasatransformedpropertydefined
 *@method
 *@memberofPopper.Utils
 *@argument{Element}element
 *@returns{Element}firsttransformedparentordocumentElement
 */

functiongetFixedPositionOffsetParent(element){
  //Thischeckisneededtoavoiderrorsincaseoneoftheelementsisn'tdefinedforanyreason
  if(!element||!element.parentElement||isIE()){
    returndocument.documentElement;
  }
  varel=element.parentElement;
  while(el&&getStyleComputedProperty(el,'transform')==='none'){
    el=el.parentElement;
  }
  returnel||document.documentElement;
}

/**
 *Computedtheboundarieslimitsandreturnthem
 *@method
 *@memberofPopper.Utils
 *@param{HTMLElement}popper
 *@param{HTMLElement}reference
 *@param{number}padding
 *@param{HTMLElement}boundariesElement-Elementusedtodefinetheboundaries
 *@param{Boolean}fixedPosition-Isinfixedpositionmode
 *@returns{Object}Coordinatesoftheboundaries
 */
functiongetBoundaries(popper,reference,padding,boundariesElement){
  varfixedPosition=arguments.length>4&&arguments[4]!==undefined?arguments[4]:false;

  //NOTE:1DOMaccesshere

  varboundaries={top:0,left:0};
  varoffsetParent=fixedPosition?getFixedPositionOffsetParent(popper):findCommonOffsetParent(popper,reference);

  //Handleviewportcase
  if(boundariesElement==='viewport'){
    boundaries=getViewportOffsetRectRelativeToArtbitraryNode(offsetParent,fixedPosition);
  }else{
    //HandleothercasesbasedonDOMelementusedasboundaries
    varboundariesNode=void0;
    if(boundariesElement==='scrollParent'){
      boundariesNode=getScrollParent(getParentNode(reference));
      if(boundariesNode.nodeName==='BODY'){
        boundariesNode=popper.ownerDocument.documentElement;
      }
    }elseif(boundariesElement==='window'){
      boundariesNode=popper.ownerDocument.documentElement;
    }else{
      boundariesNode=boundariesElement;
    }

    varoffsets=getOffsetRectRelativeToArbitraryNode(boundariesNode,offsetParent,fixedPosition);

    //IncaseofHTML,weneedadifferentcomputation
    if(boundariesNode.nodeName==='HTML'&&!isFixed(offsetParent)){
      var_getWindowSizes=getWindowSizes(),
          height=_getWindowSizes.height,
          width=_getWindowSizes.width;

      boundaries.top+=offsets.top-offsets.marginTop;
      boundaries.bottom=height+offsets.top;
      boundaries.left+=offsets.left-offsets.marginLeft;
      boundaries.right=width+offsets.left;
    }else{
      //foralltheotherDOMelements,thisoneisgood
      boundaries=offsets;
    }
  }

  //Addpaddings
  boundaries.left+=padding;
  boundaries.top+=padding;
  boundaries.right-=padding;
  boundaries.bottom-=padding;

  returnboundaries;
}

functiongetArea(_ref){
  varwidth=_ref.width,
      height=_ref.height;

  returnwidth*height;
}

/**
 *Utilityusedtotransformthe`auto`placementtotheplacementwithmore
 *availablespace.
 *@method
 *@memberofPopper.Utils
 *@argument{Object}data-Thedataobjectgeneratedbyupdatemethod
 *@argument{Object}options-Modifiersconfigurationandoptions
 *@returns{Object}Thedataobject,properlymodified
 */
functioncomputeAutoPlacement(placement,refRect,popper,reference,boundariesElement){
  varpadding=arguments.length>5&&arguments[5]!==undefined?arguments[5]:0;

  if(placement.indexOf('auto')===-1){
    returnplacement;
  }

  varboundaries=getBoundaries(popper,reference,padding,boundariesElement);

  varrects={
    top:{
      width:boundaries.width,
      height:refRect.top-boundaries.top
    },
    right:{
      width:boundaries.right-refRect.right,
      height:boundaries.height
    },
    bottom:{
      width:boundaries.width,
      height:boundaries.bottom-refRect.bottom
    },
    left:{
      width:refRect.left-boundaries.left,
      height:boundaries.height
    }
  };

  varsortedAreas=Object.keys(rects).map(function(key){
    return_extends({
      key:key
    },rects[key],{
      area:getArea(rects[key])
    });
  }).sort(function(a,b){
    returnb.area-a.area;
  });

  varfilteredAreas=sortedAreas.filter(function(_ref2){
    varwidth=_ref2.width,
        height=_ref2.height;
    returnwidth>=popper.clientWidth&&height>=popper.clientHeight;
  });

  varcomputedPlacement=filteredAreas.length>0?filteredAreas[0].key:sortedAreas[0].key;

  varvariation=placement.split('-')[1];

  returncomputedPlacement+(variation?'-'+variation:'');
}

/**
 *Getoffsetstothereferenceelement
 *@method
 *@memberofPopper.Utils
 *@param{Object}state
 *@param{Element}popper-thepopperelement
 *@param{Element}reference-thereferenceelement(thepopperwillberelativetothis)
 *@param{Element}fixedPosition-isinfixedpositionmode
 *@returns{Object}Anobjectcontainingtheoffsetswhichwillbeappliedtothepopper
 */
functiongetReferenceOffsets(state,popper,reference){
  varfixedPosition=arguments.length>3&&arguments[3]!==undefined?arguments[3]:null;

  varcommonOffsetParent=fixedPosition?getFixedPositionOffsetParent(popper):findCommonOffsetParent(popper,reference);
  returngetOffsetRectRelativeToArbitraryNode(reference,commonOffsetParent,fixedPosition);
}

/**
 *Gettheoutersizesofthegivenelement(offsetsize+margins)
 *@method
 *@memberofPopper.Utils
 *@argument{Element}element
 *@returns{Object}objectcontainingwidthandheightproperties
 */
functiongetOuterSizes(element){
  varstyles=getComputedStyle(element);
  varx=parseFloat(styles.marginTop)+parseFloat(styles.marginBottom);
  vary=parseFloat(styles.marginLeft)+parseFloat(styles.marginRight);
  varresult={
    width:element.offsetWidth+y,
    height:element.offsetHeight+x
  };
  returnresult;
}

/**
 *Gettheoppositeplacementofthegivenone
 *@method
 *@memberofPopper.Utils
 *@argument{String}placement
 *@returns{String}flippedplacement
 */
functiongetOppositePlacement(placement){
  varhash={left:'right',right:'left',bottom:'top',top:'bottom'};
  returnplacement.replace(/left|right|bottom|top/g,function(matched){
    returnhash[matched];
  });
}

/**
 *Getoffsetstothepopper
 *@method
 *@memberofPopper.Utils
 *@param{Object}position-CSSpositionthePopperwillgetapplied
 *@param{HTMLElement}popper-thepopperelement
 *@param{Object}referenceOffsets-thereferenceoffsets(thepopperwillberelativetothis)
 *@param{String}placement-oneofthevalidplacementoptions
 *@returns{Object}popperOffsets-Anobjectcontainingtheoffsetswhichwillbeappliedtothepopper
 */
functiongetPopperOffsets(popper,referenceOffsets,placement){
  placement=placement.split('-')[0];

  //Getpoppernodesizes
  varpopperRect=getOuterSizes(popper);

  //Addposition,widthandheighttoouroffsetsobject
  varpopperOffsets={
    width:popperRect.width,
    height:popperRect.height
  };

  //dependingbythepopperplacementwehavetocomputeitsoffsetsslightlydifferently
  varisHoriz=['right','left'].indexOf(placement)!==-1;
  varmainSide=isHoriz?'top':'left';
  varsecondarySide=isHoriz?'left':'top';
  varmeasurement=isHoriz?'height':'width';
  varsecondaryMeasurement=!isHoriz?'height':'width';

  popperOffsets[mainSide]=referenceOffsets[mainSide]+referenceOffsets[measurement]/2-popperRect[measurement]/2;
  if(placement===secondarySide){
    popperOffsets[secondarySide]=referenceOffsets[secondarySide]-popperRect[secondaryMeasurement];
  }else{
    popperOffsets[secondarySide]=referenceOffsets[getOppositePlacement(secondarySide)];
  }

  returnpopperOffsets;
}

/**
 *Mimicsthe`find`methodofArray
 *@method
 *@memberofPopper.Utils
 *@argument{Array}arr
 *@argumentprop
 *@argumentvalue
 *@returnsindexor-1
 */
functionfind(arr,check){
  //usenativefindifsupported
  if(Array.prototype.find){
    returnarr.find(check);
  }

  //use`filter`toobtainthesamebehaviorof`find`
  returnarr.filter(check)[0];
}

/**
 *Returntheindexofthematchingobject
 *@method
 *@memberofPopper.Utils
 *@argument{Array}arr
 *@argumentprop
 *@argumentvalue
 *@returnsindexor-1
 */
functionfindIndex(arr,prop,value){
  //usenativefindIndexifsupported
  if(Array.prototype.findIndex){
    returnarr.findIndex(function(cur){
      returncur[prop]===value;
    });
  }

  //use`find`+`indexOf`if`findIndex`isn'tsupported
  varmatch=find(arr,function(obj){
    returnobj[prop]===value;
  });
  returnarr.indexOf(match);
}

/**
 *Looptroughthelistofmodifiersandruntheminorder,
 *eachofthemwilltheneditthedataobject.
 *@method
 *@memberofPopper.Utils
 *@param{dataObject}data
 *@param{Array}modifiers
 *@param{String}ends-Optionalmodifiernameusedasstopper
 *@returns{dataObject}
 */
functionrunModifiers(modifiers,data,ends){
  varmodifiersToRun=ends===undefined?modifiers:modifiers.slice(0,findIndex(modifiers,'name',ends));

  modifiersToRun.forEach(function(modifier){
    if(modifier['function']){
      //eslint-disable-linedot-notation
      console.warn('`modifier.function`isdeprecated,use`modifier.fn`!');
    }
    varfn=modifier['function']||modifier.fn;//eslint-disable-linedot-notation
    if(modifier.enabled&&isFunction(fn)){
      //AddpropertiestooffsetstomakethemacompleteclientRectobject
      //wedothisbeforeeachmodifiertomakesurethepreviousonedoesn't
      //messwiththesevalues
      data.offsets.popper=getClientRect(data.offsets.popper);
      data.offsets.reference=getClientRect(data.offsets.reference);

      data=fn(data,modifier);
    }
  });

  returndata;
}

/**
 *Updatesthepositionofthepopper,computingthenewoffsetsandapplying
 *thenewstyle.<br/>
 *Prefer`scheduleUpdate`over`update`becauseofperformancereasons.
 *@method
 *@memberofPopper
 */
functionupdate(){
  //ifpopperisdestroyed,don'tperformanyfurtherupdate
  if(this.state.isDestroyed){
    return;
  }

  vardata={
    instance:this,
    styles:{},
    arrowStyles:{},
    attributes:{},
    flipped:false,
    offsets:{}
  };

  //computereferenceelementoffsets
  data.offsets.reference=getReferenceOffsets(this.state,this.popper,this.reference,this.options.positionFixed);

  //computeautoplacement,storeplacementinsidethedataobject,
  //modifierswillbeabletoedit`placement`ifneeded
  //andrefertooriginalPlacementtoknowtheoriginalvalue
  data.placement=computeAutoPlacement(this.options.placement,data.offsets.reference,this.popper,this.reference,this.options.modifiers.flip.boundariesElement,this.options.modifiers.flip.padding);

  //storethecomputedplacementinside`originalPlacement`
  data.originalPlacement=data.placement;

  data.positionFixed=this.options.positionFixed;

  //computethepopperoffsets
  data.offsets.popper=getPopperOffsets(this.popper,data.offsets.reference,data.placement);

  data.offsets.popper.position=this.options.positionFixed?'fixed':'absolute';

  //runthemodifiers
  data=runModifiers(this.modifiers,data);

  //thefirst`update`willcall`onCreate`callback
  //theotheroneswillcall`onUpdate`callback
  if(!this.state.isCreated){
    this.state.isCreated=true;
    this.options.onCreate(data);
  }else{
    this.options.onUpdate(data);
  }
}

/**
 *Helperusedtoknowifthegivenmodifierisenabled.
 *@method
 *@memberofPopper.Utils
 *@returns{Boolean}
 */
functionisModifierEnabled(modifiers,modifierName){
  returnmodifiers.some(function(_ref){
    varname=_ref.name,
        enabled=_ref.enabled;
    returnenabled&&name===modifierName;
  });
}

/**
 *Gettheprefixedsupportedpropertyname
 *@method
 *@memberofPopper.Utils
 *@argument{String}property(camelCase)
 *@returns{String}prefixedproperty(camelCaseorPascalCase,dependingonthevendorprefix)
 */
functiongetSupportedPropertyName(property){
  varprefixes=[false,'ms','Webkit','Moz','O'];
  varupperProp=property.charAt(0).toUpperCase()+property.slice(1);

  for(vari=0;i<prefixes.length;i++){
    varprefix=prefixes[i];
    vartoCheck=prefix?''+prefix+upperProp:property;
    if(typeofdocument.body.style[toCheck]!=='undefined'){
      returntoCheck;
    }
  }
  returnnull;
}

/**
 *Destroythepopper
 *@method
 *@memberofPopper
 */
functiondestroy(){
  this.state.isDestroyed=true;

  //touchDOMonlyif`applyStyle`modifierisenabled
  if(isModifierEnabled(this.modifiers,'applyStyle')){
    this.popper.removeAttribute('x-placement');
    this.popper.style.position='';
    this.popper.style.top='';
    this.popper.style.left='';
    this.popper.style.right='';
    this.popper.style.bottom='';
    this.popper.style.willChange='';
    this.popper.style[getSupportedPropertyName('transform')]='';
  }

  this.disableEventListeners();

  //removethepopperifuserexplicityaskedforthedeletionondestroy
  //donotuse`remove`becauseIE11doesn'tsupportit
  if(this.options.removeOnDestroy){
    this.popper.parentNode.removeChild(this.popper);
  }
  returnthis;
}

/**
 *Getthewindowassociatedwiththeelement
 *@argument{Element}element
 *@returns{Window}
 */
functiongetWindow(element){
  varownerDocument=element.ownerDocument;
  returnownerDocument?ownerDocument.defaultView:window;
}

functionattachToScrollParents(scrollParent,event,callback,scrollParents){
  varisBody=scrollParent.nodeName==='BODY';
  vartarget=isBody?scrollParent.ownerDocument.defaultView:scrollParent;
  target.addEventListener(event,callback,{passive:true});

  if(!isBody){
    attachToScrollParents(getScrollParent(target.parentNode),event,callback,scrollParents);
  }
  scrollParents.push(target);
}

/**
 *Setupneededeventlistenersusedtoupdatethepopperposition
 *@method
 *@memberofPopper.Utils
 *@private
 */
functionsetupEventListeners(reference,options,state,updateBound){
  //Resizeeventlisteneronwindow
  state.updateBound=updateBound;
  getWindow(reference).addEventListener('resize',state.updateBound,{passive:true});

  //Scrolleventlisteneronscrollparents
  varscrollElement=getScrollParent(reference);
  attachToScrollParents(scrollElement,'scroll',state.updateBound,state.scrollParents);
  state.scrollElement=scrollElement;
  state.eventsEnabled=true;

  returnstate;
}

/**
 *Itwilladdresize/scrolleventsandstartrecalculating
 *positionofthepopperelementwhentheyaretriggered.
 *@method
 *@memberofPopper
 */
functionenableEventListeners(){
  if(!this.state.eventsEnabled){
    this.state=setupEventListeners(this.reference,this.options,this.state,this.scheduleUpdate);
  }
}

/**
 *Removeeventlistenersusedtoupdatethepopperposition
 *@method
 *@memberofPopper.Utils
 *@private
 */
functionremoveEventListeners(reference,state){
  //Removeresizeeventlisteneronwindow
  getWindow(reference).removeEventListener('resize',state.updateBound);

  //Removescrolleventlisteneronscrollparents
  state.scrollParents.forEach(function(target){
    target.removeEventListener('scroll',state.updateBound);
  });

  //Resetstate
  state.updateBound=null;
  state.scrollParents=[];
  state.scrollElement=null;
  state.eventsEnabled=false;
  returnstate;
}

/**
 *Itwillremoveresize/scrolleventsandwon'trecalculatepopperposition
 *whentheyaretriggered.Italsowon'ttriggeronUpdatecallbackanymore,
 *unlessyoucall`update`methodmanually.
 *@method
 *@memberofPopper
 */
functiondisableEventListeners(){
  if(this.state.eventsEnabled){
    cancelAnimationFrame(this.scheduleUpdate);
    this.state=removeEventListeners(this.reference,this.state);
  }
}

/**
 *Tellsifagiveninputisanumber
 *@method
 *@memberofPopper.Utils
 *@param{*}inputtocheck
 *@return{Boolean}
 */
functionisNumeric(n){
  returnn!==''&&!isNaN(parseFloat(n))&&isFinite(n);
}

/**
 *Setthestyletothegivenpopper
 *@method
 *@memberofPopper.Utils
 *@argument{Element}element-Elementtoapplythestyleto
 *@argument{Object}styles
 *Objectwithalistofpropertiesandvalueswhichwillbeappliedtotheelement
 */
functionsetStyles(element,styles){
  Object.keys(styles).forEach(function(prop){
    varunit='';
    //addunitifthevalueisnumericandisoneofthefollowing
    if(['width','height','top','right','bottom','left'].indexOf(prop)!==-1&&isNumeric(styles[prop])){
      unit='px';
    }
    element.style[prop]=styles[prop]+unit;
  });
}

/**
 *Settheattributestothegivenpopper
 *@method
 *@memberofPopper.Utils
 *@argument{Element}element-Elementtoapplytheattributesto
 *@argument{Object}styles
 *Objectwithalistofpropertiesandvalueswhichwillbeappliedtotheelement
 */
functionsetAttributes(element,attributes){
  Object.keys(attributes).forEach(function(prop){
    varvalue=attributes[prop];
    if(value!==false){
      element.setAttribute(prop,attributes[prop]);
    }else{
      element.removeAttribute(prop);
    }
  });
}

/**
 *@function
 *@memberofModifiers
 *@argument{Object}data-Thedataobjectgeneratedby`update`method
 *@argument{Object}data.styles-Listofstyleproperties-valuestoapplytopopperelement
 *@argument{Object}data.attributes-Listofattributeproperties-valuestoapplytopopperelement
 *@argument{Object}options-Modifiersconfigurationandoptions
 *@returns{Object}Thesamedataobject
 */
functionapplyStyle(data){
  //anypropertypresentin`data.styles`willbeappliedtothepopper,
  //inthiswaywecanmakethe3rdpartymodifiersaddcustomstylestoit
  //Beaware,modifierscouldoverridethepropertiesdefinedintheprevious
  //linesofthismodifier!
  setStyles(data.instance.popper,data.styles);

  //anypropertypresentin`data.attributes`willbeappliedtothepopper,
  //theywillbesetasHTMLattributesoftheelement
  setAttributes(data.instance.popper,data.attributes);

  //ifarrowElementisdefinedandarrowStyleshassomeproperties
  if(data.arrowElement&&Object.keys(data.arrowStyles).length){
    setStyles(data.arrowElement,data.arrowStyles);
  }

  returndata;
}

/**
 *Setthex-placementattributebeforeeverythingelsebecauseitcouldbeused
 *toaddmarginstothepoppermarginsneedstobecalculatedtogetthe
 *correctpopperoffsets.
 *@method
 *@memberofPopper.modifiers
 *@param{HTMLElement}reference-Thereferenceelementusedtopositionthepopper
 *@param{HTMLElement}popper-TheHTMLelementusedaspopper
 *@param{Object}options-Popper.jsoptions
 */
functionapplyStyleOnLoad(reference,popper,options,modifierOptions,state){
  //computereferenceelementoffsets
  varreferenceOffsets=getReferenceOffsets(state,popper,reference,options.positionFixed);

  //computeautoplacement,storeplacementinsidethedataobject,
  //modifierswillbeabletoedit`placement`ifneeded
  //andrefertooriginalPlacementtoknowtheoriginalvalue
  varplacement=computeAutoPlacement(options.placement,referenceOffsets,popper,reference,options.modifiers.flip.boundariesElement,options.modifiers.flip.padding);

  popper.setAttribute('x-placement',placement);

  //Apply`position`topopperbeforeanythingelsebecause
  //withoutthepositionappliedwecan'tguaranteecorrectcomputations
  setStyles(popper,{position:options.positionFixed?'fixed':'absolute'});

  returnoptions;
}

/**
 *@function
 *@memberofModifiers
 *@argument{Object}data-Thedataobjectgeneratedby`update`method
 *@argument{Object}options-Modifiersconfigurationandoptions
 *@returns{Object}Thedataobject,properlymodified
 */
functioncomputeStyle(data,options){
  varx=options.x,
      y=options.y;
  varpopper=data.offsets.popper;

  //RemovethislegacysupportinPopper.jsv2

  varlegacyGpuAccelerationOption=find(data.instance.modifiers,function(modifier){
    returnmodifier.name==='applyStyle';
  }).gpuAcceleration;
  if(legacyGpuAccelerationOption!==undefined){
    console.warn('WARNING:`gpuAcceleration`optionmovedto`computeStyle`modifierandwillnotbesupportedinfutureversionsofPopper.js!');
  }
  vargpuAcceleration=legacyGpuAccelerationOption!==undefined?legacyGpuAccelerationOption:options.gpuAcceleration;

  varoffsetParent=getOffsetParent(data.instance.popper);
  varoffsetParentRect=getBoundingClientRect(offsetParent);

  //Styles
  varstyles={
    position:popper.position
  };

  //Avoidblurrytextbyusingfullpixelintegers.
  //Forpixel-perfectpositioning,top/bottomprefersrounded
  //values,whileleft/rightprefersflooredvalues.
  varoffsets={
    left:Math.floor(popper.left),
    top:Math.round(popper.top),
    bottom:Math.round(popper.bottom),
    right:Math.floor(popper.right)
  };

  varsideA=x==='bottom'?'top':'bottom';
  varsideB=y==='right'?'left':'right';

  //ifgpuAccelerationissetto`true`andtransformissupported,
  // weuse`translate3d`toapplythepositiontothepopperwe
  //automaticallyusethesupportedprefixedversionifneeded
  varprefixedProperty=getSupportedPropertyName('transform');

  //now,let'smakeastepbackandlookatthiscodeclosely(wtf?)
  //Ifthecontentofthepoppergrowsonceit'sbeenpositioned,it
  //mayhappenthatthepoppergetsmisplacedbecauseofthenewcontent
  //overflowingitsreferenceelement
  //Toavoidthisproblem,weprovidetwooptions(xandy),whichallow
  //theconsumertodefinetheoffsetorigin.
  //Ifwepositionapopperontopofareferenceelement,wecanset
  //`x`to`top`tomakethepoppergrowtowardsitstopinsteadof
  //itsbottom.
  varleft=void0,
      top=void0;
  if(sideA==='bottom'){
    top=-offsetParentRect.height+offsets.bottom;
  }else{
    top=offsets.top;
  }
  if(sideB==='right'){
    left=-offsetParentRect.width+offsets.right;
  }else{
    left=offsets.left;
  }
  if(gpuAcceleration&&prefixedProperty){
    styles[prefixedProperty]='translate3d('+left+'px,'+top+'px,0)';
    styles[sideA]=0;
    styles[sideB]=0;
    styles.willChange='transform';
  }else{
    //othwerise,weusethestandard`top`,`left`,`bottom`and`right`properties
    varinvertTop=sideA==='bottom'?-1:1;
    varinvertLeft=sideB==='right'?-1:1;
    styles[sideA]=top*invertTop;
    styles[sideB]=left*invertLeft;
    styles.willChange=sideA+','+sideB;
  }

  //Attributes
  varattributes={
    'x-placement':data.placement
  };

  //Update`data`attributes,stylesandarrowStyles
  data.attributes=_extends({},attributes,data.attributes);
  data.styles=_extends({},styles,data.styles);
  data.arrowStyles=_extends({},data.offsets.arrow,data.arrowStyles);

  returndata;
}

/**
 *Helperusedtoknowifthegivenmodifierdependsfromanotherone.<br/>
 *Itchecksiftheneededmodifierislistedandenabled.
 *@method
 *@memberofPopper.Utils
 *@param{Array}modifiers-listofmodifiers
 *@param{String}requestingName-nameofrequestingmodifier
 *@param{String}requestedName-nameofrequestedmodifier
 *@returns{Boolean}
 */
functionisModifierRequired(modifiers,requestingName,requestedName){
  varrequesting=find(modifiers,function(_ref){
    varname=_ref.name;
    returnname===requestingName;
  });

  varisRequired=!!requesting&&modifiers.some(function(modifier){
    returnmodifier.name===requestedName&&modifier.enabled&&modifier.order<requesting.order;
  });

  if(!isRequired){
    var_requesting='`'+requestingName+'`';
    varrequested='`'+requestedName+'`';
    console.warn(requested+'modifierisrequiredby'+_requesting+'modifierinordertowork,besuretoincludeitbefore'+_requesting+'!');
  }
  returnisRequired;
}

/**
 *@function
 *@memberofModifiers
 *@argument{Object}data-Thedataobjectgeneratedbyupdatemethod
 *@argument{Object}options-Modifiersconfigurationandoptions
 *@returns{Object}Thedataobject,properlymodified
 */
functionarrow(data,options){
  var_data$offsets$arrow;

  //arrowdependsonkeepTogetherinordertowork
  if(!isModifierRequired(data.instance.modifiers,'arrow','keepTogether')){
    returndata;
  }

  vararrowElement=options.element;

  //ifarrowElementisastring,supposeit'saCSSselector
  if(typeofarrowElement==='string'){
    arrowElement=data.instance.popper.querySelector(arrowElement);

    //ifarrowElementisnotfound,don'trunthemodifier
    if(!arrowElement){
      returndata;
    }
  }else{
    //ifthearrowElementisn'taqueryselectorwemustcheckthatthe
    //providedDOMnodeischildofitspoppernode
    if(!data.instance.popper.contains(arrowElement)){
      console.warn('WARNING:`arrow.element`mustbechildofitspopperelement!');
      returndata;
    }
  }

  varplacement=data.placement.split('-')[0];
  var_data$offsets=data.offsets,
      popper=_data$offsets.popper,
      reference=_data$offsets.reference;

  varisVertical=['left','right'].indexOf(placement)!==-1;

  varlen=isVertical?'height':'width';
  varsideCapitalized=isVertical?'Top':'Left';
  varside=sideCapitalized.toLowerCase();
  varaltSide=isVertical?'left':'top';
  varopSide=isVertical?'bottom':'right';
  vararrowElementSize=getOuterSizes(arrowElement)[len];

  //
  //extendskeepTogetherbehaviormakingsurethepopperandits
  //referencehaveenoughpixelsinconjuction
  //

  //top/leftside
  if(reference[opSide]-arrowElementSize<popper[side]){
    data.offsets.popper[side]-=popper[side]-(reference[opSide]-arrowElementSize);
  }
  //bottom/rightside
  if(reference[side]+arrowElementSize>popper[opSide]){
    data.offsets.popper[side]+=reference[side]+arrowElementSize-popper[opSide];
  }
  data.offsets.popper=getClientRect(data.offsets.popper);

  //computecenterofthepopper
  varcenter=reference[side]+reference[len]/2-arrowElementSize/2;

  //ComputethesideValueusingtheupdatedpopperoffsets
  //takepoppermargininaccountbecausewedon'thavethisinfoavailable
  varcss=getStyleComputedProperty(data.instance.popper);
  varpopperMarginSide=parseFloat(css['margin'+sideCapitalized],10);
  varpopperBorderSide=parseFloat(css['border'+sideCapitalized+'Width'],10);
  varsideValue=center-data.offsets.popper[side]-popperMarginSide-popperBorderSide;

  //preventarrowElementfrombeingplacednotcontiguouslytoitspopper
  sideValue=Math.max(Math.min(popper[len]-arrowElementSize,sideValue),0);

  data.arrowElement=arrowElement;
  data.offsets.arrow=(_data$offsets$arrow={},defineProperty(_data$offsets$arrow,side,Math.round(sideValue)),defineProperty(_data$offsets$arrow,altSide,''),_data$offsets$arrow);

  returndata;
}

/**
 *Gettheoppositeplacementvariationofthegivenone
 *@method
 *@memberofPopper.Utils
 *@argument{String}placementvariation
 *@returns{String}flippedplacementvariation
 */
functiongetOppositeVariation(variation){
  if(variation==='end'){
    return'start';
  }elseif(variation==='start'){
    return'end';
  }
  returnvariation;
}

/**
 *Listofacceptedplacementstouseasvaluesofthe`placement`option.<br/>
 *Validplacementsare:
 *-`auto`
 *-`top`
 *-`right`
 *-`bottom`
 *-`left`
 *
 *Eachplacementcanhaveavariationfromthislist:
 *-`-start`
 *-`-end`
 *
 *Variationsareinterpretedeasilyifyouthinkofthemasthelefttoright
 *writtenlanguages.Horizontally(`top`and`bottom`),`start`isleftand`end`
 *isright.<br/>
 *Vertically(`left`and`right`),`start`istopand`end`isbottom.
 *
 *Somevalidexamplesare:
 *-`top-end`(ontopofreference,rightaligned)
 *-`right-start`(onrightofreference,topaligned)
 *-`bottom`(onbottom,centered)
 *-`auto-right`(onthesidewithmorespaceavailable,alignmentdependsbyplacement)
 *
 *@static
 *@type{Array}
 *@enum{String}
 *@readonly
 *@methodplacements
 *@memberofPopper
 */
varplacements=['auto-start','auto','auto-end','top-start','top','top-end','right-start','right','right-end','bottom-end','bottom','bottom-start','left-end','left','left-start'];

//Getridof`auto``auto-start`and`auto-end`
varvalidPlacements=placements.slice(3);

/**
 *Givenaninitialplacement,returnsallthesubsequentplacements
 *clockwise(orcounter-clockwise).
 *
 *@method
 *@memberofPopper.Utils
 *@argument{String}placement-Avalidplacement(itacceptsvariations)
 *@argument{Boolean}counter-Settotruetowalktheplacementscounterclockwise
 *@returns{Array}placementsincludingtheirvariations
 */
functionclockwise(placement){
  varcounter=arguments.length>1&&arguments[1]!==undefined?arguments[1]:false;

  varindex=validPlacements.indexOf(placement);
  vararr=validPlacements.slice(index+1).concat(validPlacements.slice(0,index));
  returncounter?arr.reverse():arr;
}

varBEHAVIORS={
  FLIP:'flip',
  CLOCKWISE:'clockwise',
  COUNTERCLOCKWISE:'counterclockwise'
};

/**
 *@function
 *@memberofModifiers
 *@argument{Object}data-Thedataobjectgeneratedbyupdatemethod
 *@argument{Object}options-Modifiersconfigurationandoptions
 *@returns{Object}Thedataobject,properlymodified
 */
functionflip(data,options){
  //if`inner`modifierisenabled,wecan'tusethe`flip`modifier
  if(isModifierEnabled(data.instance.modifiers,'inner')){
    returndata;
  }

  if(data.flipped&&data.placement===data.originalPlacement){
    //seemslikeflipistryingtoloop,probablythere'snotenoughspaceonanyoftheflippablesides
    returndata;
  }

  varboundaries=getBoundaries(data.instance.popper,data.instance.reference,options.padding,options.boundariesElement,data.positionFixed);

  varplacement=data.placement.split('-')[0];
  varplacementOpposite=getOppositePlacement(placement);
  varvariation=data.placement.split('-')[1]||'';

  varflipOrder=[];

  switch(options.behavior){
    caseBEHAVIORS.FLIP:
      flipOrder=[placement,placementOpposite];
      break;
    caseBEHAVIORS.CLOCKWISE:
      flipOrder=clockwise(placement);
      break;
    caseBEHAVIORS.COUNTERCLOCKWISE:
      flipOrder=clockwise(placement,true);
      break;
    default:
      flipOrder=options.behavior;
  }

  flipOrder.forEach(function(step,index){
    if(placement!==step||flipOrder.length===index+1){
      returndata;
    }

    placement=data.placement.split('-')[0];
    placementOpposite=getOppositePlacement(placement);

    varpopperOffsets=data.offsets.popper;
    varrefOffsets=data.offsets.reference;

    //usingfloorbecausethereferenceoffsetsmaycontaindecimalswearenotgoingtoconsiderhere
    varfloor=Math.floor;
    varoverlapsRef=placement==='left'&&floor(popperOffsets.right)>floor(refOffsets.left)||placement==='right'&&floor(popperOffsets.left)<floor(refOffsets.right)||placement==='top'&&floor(popperOffsets.bottom)>floor(refOffsets.top)||placement==='bottom'&&floor(popperOffsets.top)<floor(refOffsets.bottom);

    varoverflowsLeft=floor(popperOffsets.left)<floor(boundaries.left);
    varoverflowsRight=floor(popperOffsets.right)>floor(boundaries.right);
    varoverflowsTop=floor(popperOffsets.top)<floor(boundaries.top);
    varoverflowsBottom=floor(popperOffsets.bottom)>floor(boundaries.bottom);

    varoverflowsBoundaries=placement==='left'&&overflowsLeft||placement==='right'&&overflowsRight||placement==='top'&&overflowsTop||placement==='bottom'&&overflowsBottom;

    //flipthevariationifrequired
    varisVertical=['top','bottom'].indexOf(placement)!==-1;
    varflippedVariation=!!options.flipVariations&&(isVertical&&variation==='start'&&overflowsLeft||isVertical&&variation==='end'&&overflowsRight||!isVertical&&variation==='start'&&overflowsTop||!isVertical&&variation==='end'&&overflowsBottom);

    if(overlapsRef||overflowsBoundaries||flippedVariation){
      //thisbooleantodetectanyfliploop
      data.flipped=true;

      if(overlapsRef||overflowsBoundaries){
        placement=flipOrder[index+1];
      }

      if(flippedVariation){
        variation=getOppositeVariation(variation);
      }

      data.placement=placement+(variation?'-'+variation:'');

      //thisobjectcontains`position`,wewanttopreserveitalongwith
      //anyadditionalpropertywemayaddinthefuture
      data.offsets.popper=_extends({},data.offsets.popper,getPopperOffsets(data.instance.popper,data.offsets.reference,data.placement));

      data=runModifiers(data.instance.modifiers,data,'flip');
    }
  });
  returndata;
}

/**
 *@function
 *@memberofModifiers
 *@argument{Object}data-Thedataobjectgeneratedbyupdatemethod
 *@argument{Object}options-Modifiersconfigurationandoptions
 *@returns{Object}Thedataobject,properlymodified
 */
functionkeepTogether(data){
  var_data$offsets=data.offsets,
      popper=_data$offsets.popper,
      reference=_data$offsets.reference;

  varplacement=data.placement.split('-')[0];
  varfloor=Math.floor;
  varisVertical=['top','bottom'].indexOf(placement)!==-1;
  varside=isVertical?'right':'bottom';
  varopSide=isVertical?'left':'top';
  varmeasurement=isVertical?'width':'height';

  if(popper[side]<floor(reference[opSide])){
    data.offsets.popper[opSide]=floor(reference[opSide])-popper[measurement];
  }
  if(popper[opSide]>floor(reference[side])){
    data.offsets.popper[opSide]=floor(reference[side]);
  }

  returndata;
}

/**
 *Convertsastringcontainingvalue+unitintoapxvaluenumber
 *@function
 *@memberof{modifiers~offset}
 *@private
 *@argument{String}str-Value+unitstring
 *@argument{String}measurement-`height`or`width`
 *@argument{Object}popperOffsets
 *@argument{Object}referenceOffsets
 *@returns{Number|String}
 *Valueinpixels,ororiginalstringifnovalueswereextracted
 */
functiontoValue(str,measurement,popperOffsets,referenceOffsets){
  //separatevaluefromunit
  varsplit=str.match(/((?:\-|\+)?\d*\.?\d*)(.*)/);
  varvalue=+split[1];
  varunit=split[2];

  //Ifit'snotanumberit'sanoperator,Iguess
  if(!value){
    returnstr;
  }

  if(unit.indexOf('%')===0){
    varelement=void0;
    switch(unit){
      case'%p':
        element=popperOffsets;
        break;
      case'%':
      case'%r':
      default:
        element=referenceOffsets;
    }

    varrect=getClientRect(element);
    returnrect[measurement]/100*value;
  }elseif(unit==='vh'||unit==='vw'){
    //ifisavhorvw,wecalculatethesizebasedontheviewport
    varsize=void0;
    if(unit==='vh'){
      size=Math.max(document.documentElement.clientHeight,window.innerHeight||0);
    }else{
      size=Math.max(document.documentElement.clientWidth,window.innerWidth||0);
    }
    returnsize/100*value;
  }else{
    //ifisanexplicitpixelunit,wegetridoftheunitandkeepthevalue
    //ifisanimplicitunit,it'spx,andwereturnjustthevalue
    returnvalue;
  }
}

/**
 *Parsean`offset`stringtoextrapolate`x`and`y`numericoffsets.
 *@function
 *@memberof{modifiers~offset}
 *@private
 *@argument{String}offset
 *@argument{Object}popperOffsets
 *@argument{Object}referenceOffsets
 *@argument{String}basePlacement
 *@returns{Array}atwocellsarraywithxandyoffsetsinnumbers
 */
functionparseOffset(offset,popperOffsets,referenceOffsets,basePlacement){
  varoffsets=[0,0];

  //Useheightifplacementisleftorrightandindexis0otherwiseusewidth
  //inthiswaythefirstoffsetwilluseanaxisandthesecondone
  //willusetheotherone
  varuseHeight=['right','left'].indexOf(basePlacement)!==-1;

  //Splittheoffsetstringtoobtainalistofvaluesandoperands
  //Theregexaddressesvalueswiththeplusorminussigninfront(+10,-20,etc)
  varfragments=offset.split(/(\+|\-)/).map(function(frag){
    returnfrag.trim();
  });

  //Detectiftheoffsetstringcontainsapairofvaluesorasingleone
  //theycouldbeseparatedbycommaorspace
  vardivider=fragments.indexOf(find(fragments,function(frag){
    returnfrag.search(/,|\s/)!==-1;
  }));

  if(fragments[divider]&&fragments[divider].indexOf(',')===-1){
    console.warn('Offsetsseparatedbywhitespace(s)aredeprecated,useacomma(,)instead.');
  }

  //Ifdividerisfound,wedividethelistofvaluesandoperandstodivide
  //thembyofsetXandY.
  varsplitRegex=/\s*,\s*|\s+/;
  varops=divider!==-1?[fragments.slice(0,divider).concat([fragments[divider].split(splitRegex)[0]]),[fragments[divider].split(splitRegex)[1]].concat(fragments.slice(divider+1))]:[fragments];

  //Convertthevalueswithunitstoabsolutepixelstoallowourcomputations
  ops=ops.map(function(op,index){
    //Mostoftheunitsrelyontheorientationofthepopper
    varmeasurement=(index===1?!useHeight:useHeight)?'height':'width';
    varmergeWithPrevious=false;
    returnop
    //Thisaggregatesany`+`or`-`signthataren'tconsideredoperators
    //e.g.:10++5=>[10,+,+5]
    .reduce(function(a,b){
      if(a[a.length-1]===''&&['+','-'].indexOf(b)!==-1){
        a[a.length-1]=b;
        mergeWithPrevious=true;
        returna;
      }elseif(mergeWithPrevious){
        a[a.length-1]+=b;
        mergeWithPrevious=false;
        returna;
      }else{
        returna.concat(b);
      }
    },[])
    //Hereweconvertthestringvaluesintonumbervalues(inpx)
    .map(function(str){
      returntoValue(str,measurement,popperOffsets,referenceOffsets);
    });
  });

  //Looptroughtheoffsetsarraysandexecutetheoperations
  ops.forEach(function(op,index){
    op.forEach(function(frag,index2){
      if(isNumeric(frag)){
        offsets[index]+=frag*(op[index2-1]==='-'?-1:1);
      }
    });
  });
  returnoffsets;
}

/**
 *@function
 *@memberofModifiers
 *@argument{Object}data-Thedataobjectgeneratedbyupdatemethod
 *@argument{Object}options-Modifiersconfigurationandoptions
 *@argument{Number|String}options.offset=0
 *Theoffsetvalueasdescribedinthemodifierdescription
 *@returns{Object}Thedataobject,properlymodified
 */
functionoffset(data,_ref){
  varoffset=_ref.offset;
  varplacement=data.placement,
      _data$offsets=data.offsets,
      popper=_data$offsets.popper,
      reference=_data$offsets.reference;

  varbasePlacement=placement.split('-')[0];

  varoffsets=void0;
  if(isNumeric(+offset)){
    offsets=[+offset,0];
  }else{
    offsets=parseOffset(offset,popper,reference,basePlacement);
  }

  if(basePlacement==='left'){
    popper.top+=offsets[0];
    popper.left-=offsets[1];
  }elseif(basePlacement==='right'){
    popper.top+=offsets[0];
    popper.left+=offsets[1];
  }elseif(basePlacement==='top'){
    popper.left+=offsets[0];
    popper.top-=offsets[1];
  }elseif(basePlacement==='bottom'){
    popper.left+=offsets[0];
    popper.top+=offsets[1];
  }

  data.popper=popper;
  returndata;
}

/**
 *@function
 *@memberofModifiers
 *@argument{Object}data-Thedataobjectgeneratedby`update`method
 *@argument{Object}options-Modifiersconfigurationandoptions
 *@returns{Object}Thedataobject,properlymodified
 */
functionpreventOverflow(data,options){
  varboundariesElement=options.boundariesElement||getOffsetParent(data.instance.popper);

  //IfoffsetParentisthereferenceelement,wereallywantto
  //goonestepupandusethenextoffsetParentasreferenceto
  //avoidtomakethismodifiercompletelyuselessandlooklikebroken
  if(data.instance.reference===boundariesElement){
    boundariesElement=getOffsetParent(boundariesElement);
  }

  //NOTE:DOMaccesshere
  //resetsthepopper'spositionsothatthedocumentsizecanbecalculatedexcluding
  //thesizeofthepopperelementitself
  vartransformProp=getSupportedPropertyName('transform');
  varpopperStyles=data.instance.popper.style;//assignmenttohelpminification
  vartop=popperStyles.top,
      left=popperStyles.left,
      transform=popperStyles[transformProp];

  popperStyles.top='';
  popperStyles.left='';
  popperStyles[transformProp]='';

  varboundaries=getBoundaries(data.instance.popper,data.instance.reference,options.padding,boundariesElement,data.positionFixed);

  //NOTE:DOMaccesshere
  //restorestheoriginalstylepropertiesaftertheoffsetshavebeencomputed
  popperStyles.top=top;
  popperStyles.left=left;
  popperStyles[transformProp]=transform;

  options.boundaries=boundaries;

  varorder=options.priority;
  varpopper=data.offsets.popper;

  varcheck={
    primary:functionprimary(placement){
      varvalue=popper[placement];
      if(popper[placement]<boundaries[placement]&&!options.escapeWithReference){
        value=Math.max(popper[placement],boundaries[placement]);
      }
      returndefineProperty({},placement,value);
    },
    secondary:functionsecondary(placement){
      varmainSide=placement==='right'?'left':'top';
      varvalue=popper[mainSide];
      if(popper[placement]>boundaries[placement]&&!options.escapeWithReference){
        value=Math.min(popper[mainSide],boundaries[placement]-(placement==='right'?popper.width:popper.height));
      }
      returndefineProperty({},mainSide,value);
    }
  };

  order.forEach(function(placement){
    varside=['left','top'].indexOf(placement)!==-1?'primary':'secondary';
    popper=_extends({},popper,check[side](placement));
  });

  data.offsets.popper=popper;

  returndata;
}

/**
 *@function
 *@memberofModifiers
 *@argument{Object}data-Thedataobjectgeneratedby`update`method
 *@argument{Object}options-Modifiersconfigurationandoptions
 *@returns{Object}Thedataobject,properlymodified
 */
functionshift(data){
  varplacement=data.placement;
  varbasePlacement=placement.split('-')[0];
  varshiftvariation=placement.split('-')[1];

  //ifshiftshiftvariationisspecified,runthemodifier
  if(shiftvariation){
    var_data$offsets=data.offsets,
        reference=_data$offsets.reference,
        popper=_data$offsets.popper;

    varisVertical=['bottom','top'].indexOf(basePlacement)!==-1;
    varside=isVertical?'left':'top';
    varmeasurement=isVertical?'width':'height';

    varshiftOffsets={
      start:defineProperty({},side,reference[side]),
      end:defineProperty({},side,reference[side]+reference[measurement]-popper[measurement])
    };

    data.offsets.popper=_extends({},popper,shiftOffsets[shiftvariation]);
  }

  returndata;
}

/**
 *@function
 *@memberofModifiers
 *@argument{Object}data-Thedataobjectgeneratedbyupdatemethod
 *@argument{Object}options-Modifiersconfigurationandoptions
 *@returns{Object}Thedataobject,properlymodified
 */
functionhide(data){
  if(!isModifierRequired(data.instance.modifiers,'hide','preventOverflow')){
    returndata;
  }

  varrefRect=data.offsets.reference;
  varbound=find(data.instance.modifiers,function(modifier){
    returnmodifier.name==='preventOverflow';
  }).boundaries;

  if(refRect.bottom<bound.top||refRect.left>bound.right||refRect.top>bound.bottom||refRect.right<bound.left){
    //AvoidunnecessaryDOMaccessifvisibilityhasn'tchanged
    if(data.hide===true){
      returndata;
    }

    data.hide=true;
    data.attributes['x-out-of-boundaries']='';
  }else{
    //AvoidunnecessaryDOMaccessifvisibilityhasn'tchanged
    if(data.hide===false){
      returndata;
    }

    data.hide=false;
    data.attributes['x-out-of-boundaries']=false;
  }

  returndata;
}

/**
 *@function
 *@memberofModifiers
 *@argument{Object}data-Thedataobjectgeneratedby`update`method
 *@argument{Object}options-Modifiersconfigurationandoptions
 *@returns{Object}Thedataobject,properlymodified
 */
functioninner(data){
  varplacement=data.placement;
  varbasePlacement=placement.split('-')[0];
  var_data$offsets=data.offsets,
      popper=_data$offsets.popper,
      reference=_data$offsets.reference;

  varisHoriz=['left','right'].indexOf(basePlacement)!==-1;

  varsubtractLength=['top','left'].indexOf(basePlacement)===-1;

  popper[isHoriz?'left':'top']=reference[basePlacement]-(subtractLength?popper[isHoriz?'width':'height']:0);

  data.placement=getOppositePlacement(placement);
  data.offsets.popper=getClientRect(popper);

  returndata;
}

/**
 *Modifierfunction,eachmodifiercanhaveafunctionofthistypeassigned
 *toits`fn`property.<br/>
 *Thesefunctionswillbecalledoneachupdate,thismeansthatyoumust
 *makesuretheyareperformantenoughtoavoidperformancebottlenecks.
 *
 *@functionModifierFn
 *@argument{dataObject}data-Thedataobjectgeneratedby`update`method
 *@argument{Object}options-Modifiersconfigurationandoptions
 *@returns{dataObject}Thedataobject,properlymodified
 */

/**
 *Modifiersarepluginsusedtoalterthebehaviorofyourpoppers.<br/>
 *Popper.jsusesasetof9modifierstoprovideallthebasicfunctionalities
 *neededbythelibrary.
 *
 *Usuallyyoudon'twanttooverridethe`order`,`fn`and`onLoad`props.
 *Alltheotherpropertiesareconfigurationsthatcouldbetweaked.
 *@namespacemodifiers
 */
varmodifiers={
  /**
   *Modifierusedtoshiftthepopperonthestartorendofitsreference
   *element.<br/>
   *Itwillreadthevariationofthe`placement`property.<br/>
   *Itcanbeoneeither`-end`or`-start`.
   *@memberofmodifiers
   *@inner
   */
  shift:{
    /**@prop{number}order=100-Indexusedtodefinetheorderofexecution*/
    order:100,
    /**@prop{Boolean}enabled=true-Whetherthemodifierisenabledornot*/
    enabled:true,
    /**@prop{ModifierFn}*/
    fn:shift
  },

  /**
   *The`offset`modifiercanshiftyourpopperonbothitsaxis.
   *
   *Itacceptsthefollowingunits:
   *-`px`orunitless,interpretedaspixels
   *-`%`or`%r`,percentagerelativetothelengthofthereferenceelement
   *-`%p`,percentagerelativetothelengthofthepopperelement
   *-`vw`,CSSviewportwidthunit
   *-`vh`,CSSviewportheightunit
   *
   *Forlengthisintendedthemainaxisrelativetotheplacementofthepopper.<br/>
   *Thismeansthatiftheplacementis`top`or`bottom`,thelengthwillbethe
   *`width`.Incaseof`left`or`right`,itwillbetheheight.
   *
   *Youcanprovideasinglevalue(as`Number`or`String`),orapairofvalues
   *as`String`dividedbyacommaorone(ormore)whitespaces.<br/>
   *Thelatterisadeprecatedmethodbecauseitleadstoconfusionandwillbe
   *removedinv2.<br/>
   *Additionally,itacceptsadditionsandsubtractionsbetweendifferentunits.
   *Notethatmultiplicationsanddivisionsaren'tsupported.
   *
   *Validexamplesare:
   *```
   *10
   *'10%'
   *'10,10'
   *'10%,10'
   *'10+10%'
   *'10-5vh+3%'
   *'-10px+5vh,5px-6%'
   *```
   *>**NB**:Ifyoudesiretoapplyoffsetstoyourpoppersinawaythatmaymakethemoverlap
   *>withtheirreferenceelement,unfortunately,youwillhavetodisablethe`flip`modifier.
   *>Moreonthis[readingthisissue](https://github.com/FezVrasta/popper.js/issues/373)
   *
   *@memberofmodifiers
   *@inner
   */
  offset:{
    /**@prop{number}order=200-Indexusedtodefinetheorderofexecution*/
    order:200,
    /**@prop{Boolean}enabled=true-Whetherthemodifierisenabledornot*/
    enabled:true,
    /**@prop{ModifierFn}*/
    fn:offset,
    /**@prop{Number|String}offset=0
     *Theoffsetvalueasdescribedinthemodifierdescription
     */
    offset:0
  },

  /**
   *Modifierusedtopreventthepopperfrombeingpositionedoutsidetheboundary.
   *
   *Anscenarioexistswherethereferenceitselfisnotwithintheboundaries.<br/>
   *Wecansayithas"escapedtheboundaries"—orjust"escaped".<br/>
   *Inthiscaseweneedtodecidewhetherthepoppershouldeither:
   *
   *-detachfromthereferenceandremain"trapped"intheboundaries,or
   *-ifitshouldignoretheboundaryand"escapewithitsreference"
   *
   *When`escapeWithReference`issetto`true`andreferenceiscompletely
   *outsideitsboundaries,thepopperwilloverflow(orcompletelyleave)
   *theboundariesinordertoremainattachedtotheedgeofthereference.
   *
   *@memberofmodifiers
   *@inner
   */
  preventOverflow:{
    /**@prop{number}order=300-Indexusedtodefinetheorderofexecution*/
    order:300,
    /**@prop{Boolean}enabled=true-Whetherthemodifierisenabledornot*/
    enabled:true,
    /**@prop{ModifierFn}*/
    fn:preventOverflow,
    /**
     *@prop{Array}[priority=['left','right','top','bottom']]
     *Popperwilltrytopreventoverflowfollowingtheseprioritiesbydefault,
     *then,itcouldoverflowontheleftandontopofthe`boundariesElement`
     */
    priority:['left','right','top','bottom'],
    /**
     *@prop{number}padding=5
     *Amountofpixelusedtodefineaminimumdistancebetweentheboundaries
     *andthepopperthismakessurethepopperhasalwaysalittlepadding
     *betweentheedgesofitscontainer
     */
    padding:5,
    /**
     *@prop{String|HTMLElement}boundariesElement='scrollParent'
     *Boundariesusedbythemodifier,canbe`scrollParent`,`window`,
     *`viewport`oranyDOMelement.
     */
    boundariesElement:'scrollParent'
  },

  /**
   *Modifierusedtomakesurethereferenceanditspopperstayneareachothers
   *withoutleavinganygapbetweenthetwo.Expeciallyusefulwhenthearrowis
   *enabledandyouwanttoassureittopointtoitsreferenceelement.
   *Itcaresonlyaboutthefirstaxis,youcanstillhavepopperswithmargin
   *betweenthepopperanditsreferenceelement.
   *@memberofmodifiers
   *@inner
   */
  keepTogether:{
    /**@prop{number}order=400-Indexusedtodefinetheorderofexecution*/
    order:400,
    /**@prop{Boolean}enabled=true-Whetherthemodifierisenabledornot*/
    enabled:true,
    /**@prop{ModifierFn}*/
    fn:keepTogether
  },

  /**
   *Thismodifierisusedtomovethe`arrowElement`ofthepoppertomake
   *sureitispositionedbetweenthereferenceelementanditspopperelement.
   *Itwillreadtheoutersizeofthe`arrowElement`nodetodetecthowmany
   *pixelsofconjuctionareneeded.
   *
   *Ithasnoeffectifno`arrowElement`isprovided.
   *@memberofmodifiers
   *@inner
   */
  arrow:{
    /**@prop{number}order=500-Indexusedtodefinetheorderofexecution*/
    order:500,
    /**@prop{Boolean}enabled=true-Whetherthemodifierisenabledornot*/
    enabled:true,
    /**@prop{ModifierFn}*/
    fn:arrow,
    /**@prop{String|HTMLElement}element='[x-arrow]'-Selectorornodeusedasarrow*/
    element:'[x-arrow]'
  },

  /**
   *Modifierusedtoflipthepopper'splacementwhenitstartstooverlapits
   *referenceelement.
   *
   *Requiresthe`preventOverflow`modifierbeforeitinordertowork.
   *
   ***NOTE:**thismodifierwillinterruptthecurrentupdatecycleandwill
   *restartitifitdetectstheneedtofliptheplacement.
   *@memberofmodifiers
   *@inner
   */
  flip:{
    /**@prop{number}order=600-Indexusedtodefinetheorderofexecution*/
    order:600,
    /**@prop{Boolean}enabled=true-Whetherthemodifierisenabledornot*/
    enabled:true,
    /**@prop{ModifierFn}*/
    fn:flip,
    /**
     *@prop{String|Array}behavior='flip'
     *Thebehaviorusedtochangethepopper'splacement.Itcanbeoneof
     *`flip`,`clockwise`,`counterclockwise`oranarraywithalistofvalid
     *placements(withoptionalvariations).
     */
    behavior:'flip',
    /**
     *@prop{number}padding=5
     *Thepopperwillflipifithitstheedgesofthe`boundariesElement`
     */
    padding:5,
    /**
     *@prop{String|HTMLElement}boundariesElement='viewport'
     *Theelementwhichwilldefinetheboundariesofthepopperposition,
     *thepopperwillneverbeplacedoutsideofthedefinedboundaries
     *(exceptifkeepTogetherisenabled)
     */
    boundariesElement:'viewport'
  },

  /**
   *Modifierusedtomakethepopperflowtowardtheinnerofthereferenceelement.
   *Bydefault,whenthismodifierisdisabled,thepopperwillbeplacedoutside
   *thereferenceelement.
   *@memberofmodifiers
   *@inner
   */
  inner:{
    /**@prop{number}order=700-Indexusedtodefinetheorderofexecution*/
    order:700,
    /**@prop{Boolean}enabled=false-Whetherthemodifierisenabledornot*/
    enabled:false,
    /**@prop{ModifierFn}*/
    fn:inner
  },

  /**
   *Modifierusedtohidethepopperwhenitsreferenceelementisoutsideofthe
   *popperboundaries.Itwillseta`x-out-of-boundaries`attributewhichcan
   *beusedtohidewithaCSSselectorthepopperwhenitsreferenceis
   *outofboundaries.
   *
   *Requiresthe`preventOverflow`modifierbeforeitinordertowork.
   *@memberofmodifiers
   *@inner
   */
  hide:{
    /**@prop{number}order=800-Indexusedtodefinetheorderofexecution*/
    order:800,
    /**@prop{Boolean}enabled=true-Whetherthemodifierisenabledornot*/
    enabled:true,
    /**@prop{ModifierFn}*/
    fn:hide
  },

  /**
   *Computesthestylethatwillbeappliedtothepopperelementtogets
   *properlypositioned.
   *
   *NotethatthismodifierwillnottouchtheDOM,itjustpreparesthestyles
   *sothat`applyStyle`modifiercanapplyit.Thisseparationisuseful
   *incaseyouneedtoreplace`applyStyle`withacustomimplementation.
   *
   *Thismodifierhas`850`as`order`valuetomaintainbackwardcompatibility
   *withpreviousversionsofPopper.js.Expectthemodifiersorderingmethod
   *tochangeinfuturemajorversionsofthelibrary.
   *
   *@memberofmodifiers
   *@inner
   */
  computeStyle:{
    /**@prop{number}order=850-Indexusedtodefinetheorderofexecution*/
    order:850,
    /**@prop{Boolean}enabled=true-Whetherthemodifierisenabledornot*/
    enabled:true,
    /**@prop{ModifierFn}*/
    fn:computeStyle,
    /**
     *@prop{Boolean}gpuAcceleration=true
     *Iftrue,itusestheCSS3dtransformationtopositionthepopper.
     *Otherwise,itwillusethe`top`and`left`properties.
     */
    gpuAcceleration:true,
    /**
     *@prop{string}[x='bottom']
     *WheretoanchortheXaxis(`bottom`or`top`).AKAXoffsetorigin.
     *Changethisifyourpoppershouldgrowinadirectiondifferentfrom`bottom`
     */
    x:'bottom',
    /**
     *@prop{string}[x='left']
     *WheretoanchortheYaxis(`left`or`right`).AKAYoffsetorigin.
     *Changethisifyourpoppershouldgrowinadirectiondifferentfrom`right`
     */
    y:'right'
  },

  /**
   *Appliesthecomputedstylestothepopperelement.
   *
   *AlltheDOMmanipulationsarelimitedtothismodifier.Thisisusefulincase
   *youwanttointegratePopper.jsinsideaframeworkorviewlibraryandyou
   *wanttodelegatealltheDOMmanipulationstoit.
   *
   *Notethatifyoudisablethismodifier,youmustmakesurethepopperelement
   *hasitspositionsetto`absolute`beforePopper.jscandoitswork!
   *
   *Justdisablethismodifieranddefineyouowntoachievethedesiredeffect.
   *
   *@memberofmodifiers
   *@inner
   */
  applyStyle:{
    /**@prop{number}order=900-Indexusedtodefinetheorderofexecution*/
    order:900,
    /**@prop{Boolean}enabled=true-Whetherthemodifierisenabledornot*/
    enabled:true,
    /**@prop{ModifierFn}*/
    fn:applyStyle,
    /**@prop{Function}*/
    onLoad:applyStyleOnLoad,
    /**
     *@deprecatedsinceversion1.10.0,thepropertymovedto`computeStyle`modifier
     *@prop{Boolean}gpuAcceleration=true
     *Iftrue,itusestheCSS3dtransformationtopositionthepopper.
     *Otherwise,itwillusethe`top`and`left`properties.
     */
    gpuAcceleration:undefined
  }
};

/**
 *The`dataObject`isanobjectcontainingalltheinformationsusedbyPopper.js
 *thisobjectgetpassedtomodifiersandtothe`onCreate`and`onUpdate`callbacks.
 *@namedataObject
 *@property{Object}data.instanceThePopper.jsinstance
 *@property{String}data.placementPlacementappliedtopopper
 *@property{String}data.originalPlacementPlacementoriginallydefinedoninit
 *@property{Boolean}data.flippedTrueifpopperhasbeenflippedbyflipmodifier
 *@property{Boolean}data.hideTrueifthereferenceelementisoutofboundaries,usefultoknowwhentohidethepopper.
 *@property{HTMLElement}data.arrowElementNodeusedasarrowbyarrowmodifier
 *@property{Object}data.stylesAnyCSSpropertydefinedherewillbeappliedtothepopper,itexpectstheJavaScriptnomenclature(eg.`marginBottom`)
 *@property{Object}data.arrowStylesAnyCSSpropertydefinedherewillbeappliedtothepopperarrow,itexpectstheJavaScriptnomenclature(eg.`marginBottom`)
 *@property{Object}data.boundariesOffsetsofthepopperboundaries
 *@property{Object}data.offsetsThemeasurementsofpopper,referenceandarrowelements.
 *@property{Object}data.offsets.popper`top`,`left`,`width`,`height`values
 *@property{Object}data.offsets.reference`top`,`left`,`width`,`height`values
 *@property{Object}data.offsets.arrow]`top`and`left`offsets,onlyoneofthemwillbedifferentfrom0
 */

/**
 *DefaultoptionsprovidedtoPopper.jsconstructor.<br/>
 *Thesecanbeoverriddenusingthe`options`argumentofPopper.js.<br/>
 *Tooverrideanoption,simplypassas3rdargumentanobjectwiththesame
 *structureofthisobject,example:
 *```
 *newPopper(ref,pop,{
 *  modifiers:{
 *    preventOverflow:{enabled:false}
 *  }
 *})
 *```
 *@type{Object}
 *@static
 *@memberofPopper
 */
varDefaults={
  /**
   *Popper'splacement
   *@prop{Popper.placements}placement='bottom'
   */
  placement:'bottom',

  /**
   *Setthistotrueifyouwantpoppertopositionitselfin'fixed'mode
   *@prop{Boolean}positionFixed=false
   */
  positionFixed:false,

  /**
   *Whetherevents(resize,scroll)areinitiallyenabled
   *@prop{Boolean}eventsEnabled=true
   */
  eventsEnabled:true,

  /**
   *Settotrueifyouwanttoautomaticallyremovethepopperwhen
   *youcallthe`destroy`method.
   *@prop{Boolean}removeOnDestroy=false
   */
  removeOnDestroy:false,

  /**
   *Callbackcalledwhenthepopperiscreated.<br/>
   *Bydefault,issettono-op.<br/>
   *AccessPopper.jsinstancewith`data.instance`.
   *@prop{onCreate}
   */
  onCreate:functiononCreate(){},

  /**
   *Callbackcalledwhenthepopperisupdated,thiscallbackisnotcalled
   *ontheinitialization/creationofthepopper,butonlyonsubsequent
   *updates.<br/>
   *Bydefault,issettono-op.<br/>
   *AccessPopper.jsinstancewith`data.instance`.
   *@prop{onUpdate}
   */
  onUpdate:functiononUpdate(){},

  /**
   *Listofmodifiersusedtomodifytheoffsetsbeforetheyareappliedtothepopper.
   *TheyprovidemostofthefunctionalitiesofPopper.js
   *@prop{modifiers}
   */
  modifiers:modifiers
};

/**
 *@callbackonCreate
 *@param{dataObject}data
 */

/**
 *@callbackonUpdate
 *@param{dataObject}data
 */

//Utils
//Methods
varPopper=function(){
  /**
   *CreateanewPopper.jsinstance
   *@classPopper
   *@param{HTMLElement|referenceObject}reference-Thereferenceelementusedtopositionthepopper
   *@param{HTMLElement}popper-TheHTMLelementusedaspopper.
   *@param{Object}options-Yourcustomoptionstooverridetheonesdefinedin[Defaults](#defaults)
   *@return{Object}instance-ThegeneratedPopper.jsinstance
   */
  functionPopper(reference,popper){
    var_this=this;

    varoptions=arguments.length>2&&arguments[2]!==undefined?arguments[2]:{};
    classCallCheck(this,Popper);

    this.scheduleUpdate=function(){
      returnrequestAnimationFrame(_this.update);
    };

    //makeupdate()debounced,sothatitonlyrunsatmostonce-per-tick
    this.update=debounce(this.update.bind(this));

    //with{}wecreateanewobjectwiththeoptionsinsideit
    this.options=_extends({},Popper.Defaults,options);

    //initstate
    this.state={
      isDestroyed:false,
      isCreated:false,
      scrollParents:[]
    };

    //getreferenceandpopperelements(allowjQuerywrappers)
    this.reference=reference&&reference.jquery?reference[0]:reference;
    this.popper=popper&&popper.jquery?popper[0]:popper;

    //Deepmergemodifiersoptions
    this.options.modifiers={};
    Object.keys(_extends({},Popper.Defaults.modifiers,options.modifiers)).forEach(function(name){
      _this.options.modifiers[name]=_extends({},Popper.Defaults.modifiers[name]||{},options.modifiers?options.modifiers[name]:{});
    });

    //Refactoringmodifiers'list(Object=>Array)
    this.modifiers=Object.keys(this.options.modifiers).map(function(name){
      return_extends({
        name:name
      },_this.options.modifiers[name]);
    })
    //sortthemodifiersbyorder
    .sort(function(a,b){
      returna.order-b.order;
    });

    //modifiershavetheabilitytoexecutearbitrarycodewhenPopper.jsgetinited
    //suchcodeisexecutedinthesameorderofitsmodifier
    //theycouldaddnewpropertiestotheiroptionsconfiguration
    //BEAWARE:don'taddoptionsto`options.modifiers.name`butto`modifierOptions`!
    this.modifiers.forEach(function(modifierOptions){
      if(modifierOptions.enabled&&isFunction(modifierOptions.onLoad)){
        modifierOptions.onLoad(_this.reference,_this.popper,_this.options,modifierOptions,_this.state);
      }
    });

    //firethefirstupdatetopositionthepopperintherightplace
    this.update();

    vareventsEnabled=this.options.eventsEnabled;
    if(eventsEnabled){
      //setupeventlisteners,theywilltakecareofupdatethepositioninspecificsituations
      this.enableEventListeners();
    }

    this.state.eventsEnabled=eventsEnabled;
  }

  //Wecan'tuseclasspropertiesbecausetheydon'tgetlistedinthe
  //classprototypeandbreakstufflikeSinonstubs


  createClass(Popper,[{
    key:'update',
    value:functionupdate$$1(){
      returnupdate.call(this);
    }
  },{
    key:'destroy',
    value:functiondestroy$$1(){
      returndestroy.call(this);
    }
  },{
    key:'enableEventListeners',
    value:functionenableEventListeners$$1(){
      returnenableEventListeners.call(this);
    }
  },{
    key:'disableEventListeners',
    value:functiondisableEventListeners$$1(){
      returndisableEventListeners.call(this);
    }

    /**
     *Scheduleanupdate,itwillrunonthenextUIupdateavailable
     *@methodscheduleUpdate
     *@memberofPopper
     */


    /**
     *Collectionofutilitiesusefulwhenwritingcustommodifiers.
     *Startingfromversion1.7,thismethodisavailableonlyifyou
     *include`popper-utils.js`before`popper.js`.
     *
     ***DEPRECATION**:ThiswaytoaccessPopperUtilsisdeprecated
     *andwillberemovedinv2!UsethePopperUtilsmoduledirectlyinstead.
     *DuetothehighinstabilityofthemethodscontainedinUtils,wecan't
     *guaranteethemtofollowsemver.Usethematyourownrisk!
     *@static
     *@private
     *@type{Object}
     *@deprecatedsinceversion1.8
     *@memberUtils
     *@memberofPopper
     */

  }]);
  returnPopper;
}();

/**
 *The`referenceObject`isanobjectthatprovidesaninterfacecompatiblewithPopper.js
 *andletsyouuseitasreplacementofarealDOMnode.<br/>
 *Youcanusethismethodtopositionapopperrelativelytoasetofcoordinates
 *incaseyoudon'thaveaDOMnodetouseasreference.
 *
 *```
 *newPopper(referenceObject,popperNode);
 *```
 *
 *NB:Thisfeatureisn'tsupportedinInternetExplorer10
 *@namereferenceObject
 *@property{Function}data.getBoundingClientRect
 *Afunctionthatreturnsasetofcoordinatescompatiblewiththenative`getBoundingClientRect`method.
 *@property{number}data.clientWidth
 *AnES6getterthatwillreturnthewidthofthevirtualreferenceelement.
 *@property{number}data.clientHeight
 *AnES6getterthatwillreturntheheightofthevirtualreferenceelement.
 */


Popper.Utils=(typeofwindow!=='undefined'?window:global).PopperUtils;
Popper.placements=placements;
Popper.Defaults=Defaults;

returnPopper;

})));
