/*!
 *jQueryUITouchPunch0.2.3
 *
 *Copyright2011–2014,DaveFurfero
 *DuallicensedundertheMITorGPLVersion2licenses.
 *
 *Depends:
 * jquery.ui.widget.js
 * jquery.ui.mouse.js
 */
(function($){

    //Detecttouchsupport
    $.support.touch=(
      'ontouchend'indocument||//Defaultcheck
      //FlectrafixforChrome
      //See:https://github.com/furf/jquery-ui-touch-punch/issues/309
      'ontouchstart'indocument||
      'ontouchstart'inwindow||
      navigator.maxTouchPoints>0||
      navigator.msMaxTouchPoints>0
    );
  
    //Ignorebrowserswithouttouchsupport
    if(!$.support.touch){
      return;
    }
  
    varmouseProto=$.ui.mouse.prototype,
        _mouseInit=mouseProto._mouseInit,
        _mouseDestroy=mouseProto._mouseDestroy,
        touchHandled;
  
    /**
     *Simulateamouseeventbasedonacorrespondingtouchevent
     *@param{Object}eventAtouchevent
     *@param{String}simulatedTypeThecorrespondingmouseevent
     */
    functionsimulateMouseEvent(event,simulatedType){
  
      //Ignoremulti-touchevents
      if(event.originalEvent.touches.length>1){
        return;
      }
  
      event.preventDefault();
  
      vartouch=event.originalEvent.changedTouches[0],
          simulatedEvent=document.createEvent('MouseEvents');
      
      //Initializethesimulatedmouseeventusingthetouchevent'scoordinates
      simulatedEvent.initMouseEvent(
        simulatedType,   //type
        true,            //bubbles                   
        true,            //cancelable                
        window,          //view                      
        1,               //detail                    
        touch.screenX,   //screenX                   
        touch.screenY,   //screenY                   
        touch.clientX,   //clientX                   
        touch.clientY,   //clientY                   
        false,           //ctrlKey                   
        false,           //altKey                    
        false,           //shiftKey                  
        false,           //metaKey                   
        0,               //button                    
        null             //relatedTarget             
      );
  
      //Dispatchthesimulatedeventtothetargetelement
      event.target.dispatchEvent(simulatedEvent);
    }
  
    /**
     *HandlethejQueryUIwidget'stouchstartevents
     *@param{Object}eventThewidgetelement'stouchstartevent
     */
    mouseProto._touchStart=function(event){
  
      varself=this;
  
      //Ignoretheeventifanotherwidgetisalreadybeinghandled
      if(touchHandled||!self._mouseCapture(event.originalEvent.changedTouches[0])){
        return;
      }
  
      //Settheflagtopreventotherwidgetsfrominheritingthetouchevent
      touchHandled=true;
  
      //Trackmovementtodetermineifinteractionwasaclick
      self._touchMoved=false;
  
      //Simulatethemouseoverevent
      simulateMouseEvent(event,'mouseover');
  
      //Simulatethemousemoveevent
      simulateMouseEvent(event,'mousemove');
  
      //Simulatethemousedownevent
      simulateMouseEvent(event,'mousedown');
    };
  
    /**
     *HandlethejQueryUIwidget'stouchmoveevents
     *@param{Object}eventThedocument'stouchmoveevent
     */
    mouseProto._touchMove=function(event){
  
      //Ignoreeventifnothandled
      if(!touchHandled){
        return;
      }
  
      //Interactionwasnotaclick
      this._touchMoved=true;
  
      //Simulatethemousemoveevent
      simulateMouseEvent(event,'mousemove');
    };
  
    /**
     *HandlethejQueryUIwidget'stouchendevents
     *@param{Object}eventThedocument'stouchendevent
     */
    mouseProto._touchEnd=function(event){
  
      //Ignoreeventifnothandled
      if(!touchHandled){
        return;
      }
  
      //Simulatethemouseupevent
      simulateMouseEvent(event,'mouseup');
  
      //Simulatethemouseoutevent
      simulateMouseEvent(event,'mouseout');
  
      //Ifthetouchinteractiondidnotmove,itshouldtriggeraclick
      if(!this._touchMoved){
  
        //Simulatetheclickevent
        simulateMouseEvent(event,'click');
      }
  
      //Unsettheflagtoallowotherwidgetstoinheritthetouchevent
      touchHandled=false;
    };
  
    /**
     *Aduckpunchofthe$.ui.mouse_mouseInitmethodtosupporttouchevents.
     *Thismethodextendsthewidgetwithboundtoucheventhandlersthat
     *translatetoucheventstomouseeventsandpassthemtothewidget's
     *originalmouseeventhandlingmethods.
     */
    mouseProto._mouseInit=function(){
      
      varself=this;
  
      //Delegatethetouchhandlerstothewidget'selement
      self.element.bind({
        touchstart:$.proxy(self,'_touchStart'),
        touchmove:$.proxy(self,'_touchMove'),
        touchend:$.proxy(self,'_touchEnd')
      });
  
      //Calltheoriginal$.ui.mouseinitmethod
      _mouseInit.call(self);
    };
  
    /**
     *Removethetoucheventhandlers
     */
    mouseProto._mouseDestroy=function(){
      
      varself=this;
  
      //Delegatethetouchhandlerstothewidget'selement
      self.element.unbind({
        touchstart:$.proxy(self,'_touchStart'),
        touchmove:$.proxy(self,'_touchMove'),
        touchend:$.proxy(self,'_touchEnd')
      });
  
      //Calltheoriginal$.ui.mousedestroymethod
      _mouseDestroy.call(self);
    };
  
  })(jQuery);