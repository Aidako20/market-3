/*!
 *@fileOverviewTouchSwipe-jQueryPlugin
 *@version1.6.18
 *
 *@authorMattBrysonhttp://www.github.com/mattbryson
 *@seehttps://github.com/mattbryson/TouchSwipe-Jquery-Plugin
 *@seehttp://labs.rampinteractive.co.uk/touchSwipe/
 *@seehttp://plugins.jquery.com/project/touchSwipe
 *@license
 *Copyright(c)2010-2015MattBryson
 *DuallicensedundertheMITorGPLVersion2licenses.
 *
 */

/*
 *
 *Changelog
 *$Date:2010-12-12(Wed,12Dec2010)$
 *$version:1.0.0
 *$version:1.0.1-removedmultibytecomments
 *
 *$Date:2011-21-02(Mon,21Feb2011)$
 *$version:1.1.0	-addedallowPageScrollpropertytoallowswipingandscrollingofpage
 *					-changedhandlersignaturessoonehandlercanbeusedformultipleevents
 *$Date:2011-23-02(Wed,23Feb2011)$
 *$version:1.2.0	-addedclickhandler.Thisisfirediftheusersimplyclicksanddoesnotswipe.Theeventobjectandclicktargetarepassedtohandler.
 *					-Ifyouusethehttp://code.google.com/p/jquery-ui-for-ipad-and-iphone/plugin,youcanalsoassignjQuerymouseeventstochildrenofatouchSwipeobject.
 *$version:1.2.1	-removedconsolelog!
 *
 *$version:1.2.2	-Fixedbugwherescopewasnotpreservedincallbackmethods.
 *
 *$Date:2011-28-04(Thurs,28April2011)$
 *$version:1.2.4	-ChangedlicencetermstobeMITorGPLinlinewithjQuery.Addedcheckforsupportoftoucheventstostopnoncompatiblebrowserserroring.
 *
 *$Date:2011-27-09(Tues,27September2011)$
 *$version:1.2.5	-Addedsupportfortestingswipeswithmouseondesktopbrowser(thankstohttps://github.com/joelhy)
 *
 *$Date:2012-14-05(Mon,14May2012)$
 *$version:1.2.6	-AddedtimeThresholdbetweenstartandendtouch,sousercanignoreslowswipes(thankstoMarkChase).Defaultisnull,allswipesaredetected
 *
 *$Date:2012-05-06(Tues,05June2012)$
 *$version:1.2.7	-Changedtimethresholdtohavenulldefaultforbackwardscompatibility.Addeddurationparampassedbackinevents,andrefactoredhowtimeishandled.
 *
 *$Date:2012-05-06(Tues,05June2012)$
 *$version:1.2.8	-Addedthepossibilitytoreturnavaluelikenullorfalseinthetriggercallback.Inthatwaywecancontrolwhenthetouchstart/moveshouldtakeeffectornot(simplybyreturninginsomecasesreturnnull;orreturnfalse;)Thiseffectstheontouchstart/ontouchmoveevent.
 *
 *$Date:2012-06-06(Wed,06June2012)$
 *$version:1.3.0	-Refactoredwholeplugintoallowformethodstobeexecuted,aswellasexposeddefaultsforuseroverride.Added'enable','disable',and'destroy'methods
 *
 *$Date:2012-05-06(Fri,05June2012)$
 *$version:1.3.1	-Bugfixes -bind()withfalseaslastargumentisnolongersupportedinjQuery1.6,also,ifyoujustclick,thedurationisnowreturnedcorrectly.
 *
 *$Date:2012-29-07(Sun,29July2012)$
 *$version:1.3.2	-AddedfallbackToMouseEventsoptiontoNOTcapturemouseeventsonnontouchdevices.
 *			-Added"all"fingersvaluetothefingersproperty,soanycombinationoffingerstriggerstheswipe,allowingeventhandlerstocheckthefingercount
 *
 *$Date:2012-09-08(Thurs,9Aug2012)$
 *$version:1.3.3	-Codetidyprepforminefiedversion
 *
 *$Date:2012-04-10(wed,4Oct2012)$
 *$version:1.4.0	-Addedpinchsupport,pinchInandpinchOut
 *
 *$Date:2012-11-10(Thurs,11Oct2012)$
 *$version:1.5.0	-AddedexcludedElements,ajqueryselectorthatspecifieschildelementsthatdoNOTtriggerswipes.Bydefault,thisis.noSwipe
 *
 *$Date:2012-22-10(Mon,22Oct2012)$
 *$version:1.5.1	-FixedbugwithjQuery1.8andtrailingcommainexcludedElements
 *					-FixedbugwithIEandeventPreventDefault()
 *$Date:2013-01-12(Fri,12Jan2013)$
 *$version:1.6.0	-Fixedbugswithpinching,mainlywhenbothpinchandswipeenabled,aswellasaddingtimethresholdformultifingergestures,soreleasingonefingerbeofretheotherdoesnttriggerassinglefingergesture.
 *					-madethedemositeallstaticlocalHTMLpagessotheycanberunlocallybyadeveloper
 *					-addedjsDoccommentsandaddeddocumentationfortheplugin
 *					-codetidy
 *					-addedtriggerOnTouchLeavepropertythatwillendtheeventwhentheuserswipesofftheelement.
 *$Date:2013-03-23(Sat,23Mar2013)$
 *$version:1.6.1	-Addedsupportforie8touchevents
 *$version:1.6.2	-Addedsupportforeventsbindingwithon/off/bindinjQforallcallbacknames.
 *                  -Deprecatedthe'click'handlerinfavouroftap.
 *                  -addedcancelThresholdproperty
 *                  -addedoptionmethodtoupdateinitoptionsatruntime
 *$version1.6.3   -addeddoubletap,longtapeventsandlongTapThreshold,doubleTapThresholdproperty
 *
 *$Date:2013-04-04(Thurs,04April2013)$
 *$version1.6.4   -FixedbugwithcancelThresholdintroducedin1.6.3,whereswipestatusnolongerfiredstartevent,andstoppedonceswipingback.
 *
 *$Date:2013-08-24(Sat,24Aug2013)$
 *$version1.6.5   -Mergedafewpullrequestsfixingvariousbugs,addedAMDsupport.
 *
 *$Date:2014-06-04(Wed,04June2014)$
 *$version1.6.6	-Mergeofpullrequests.
 *   				-IE10touchsupport
 *   				-Onlypreventdefaulteventhandlingonvalidswipe
 *   				-Separatelicense/changelogcomment
 *   				-Detectiftheswipeisvalidattheendofthetouchevent.
 *   				-Passfingerdatatoeventhandlers.
 *   				-Add'hold'gesture
 *   				-Bemoretolerantaboutthetapdistance
 *   				-Typosandminorfixes
 *
 *$Date:2015-22-01(Thurs,22Jan2015)$
 *$version1.6.7   -Addedpatchfromhttps://github.com/mattbryson/TouchSwipe-Jquery-Plugin/issues/206tofixmemoryleak
 *
 *$Date:2015-2-2(Mon,2Feb2015)$
 *$version1.6.8   -AddedpreventDefaultEventsoptiontoproxyeventsregardless.
 *					-Fixedissuewithswipeandpinchnottriggeringatthesametime
 *
 *$Date:2015-9-6(Tues,9June2015)$
 *$version1.6.9   -AddedPRfromjdalton/hybridtofixpointerevents
 *					-Addedscrollingdemo
 *					-Addedversionpropertytoplugin
 *
 *$Date:2015-1-10(Wed,1October2015)$
 *$version1.6.10   -AddedPRfrombeatspacetofixtapevents
 *$version1.6.11   -AddedPRsfromindri-indri(Doctidyup),kkirsche(Bowertidyup),UziTech(preventDefaultEventsfixes)
 *					-Allowedsettingmultipleoptionsvia.swipe("options",options_hash)andmoresimply.swipe(options_hash)orexisitnginstances
 *$version1.6.12   -Fixedbugwithmultifingerreleasesabove2nottriggeringevents
 *
 *$Date:2015-12-18(Fri,18December2015)$
 *$version1.6.13   -AddedPRs
 *                   -Fixed#267allowPageScrollnotworkingcorrectly
 *$version1.6.14   -Fixed#220/#248doubletapnotfiringwithswipes,#223commonJScompatible
 *$version1.6.15   -Morebugfixes
 *
 *$Date:2016-04-29(Fri,29April2016)$
 *$version1.6.16   -Swipeswith0distancenowallowdefaulteventstotrigger. SotappinganyformelementsorAtagswillallowdefaultinteraction,butswipingwilltriggeraswipe.
                        Removedthea,input,selectetcfromtheexcludedChildrenlistasthe0distancetapsolvesthatissue.
*$Date:2016-05-19 (Fri,29April2016)$
*$version1.6.17    -Fixedcontextissuewhencallinginstancemethodsvia$("selector").swipe("method");
*$version1.6.18    -nowhonorsfallbackToMouseEvents=falseforMSPointereventswhenaMouseisused.

 */

/**
 *See(http://jquery.com/).
 *@name$
 *@class
 *SeethejQueryLibrary (http://jquery.com/)forfulldetails. Thisjust
 *documentsthefunctionandclassesthatareaddedtojQuerybythisplug-in.
 */

/**
 *See(http://jquery.com/)
 *@namefn
 *@class
 *SeethejQueryLibrary (http://jquery.com/)forfulldetails. Thisjust
 *documentsthefunctionandclassesthatareaddedtojQuerybythisplug-in.
 *@memberOf$
 */


(function(factory){
  if(typeofdefine==='function'&&define.amd&&define.amd.jQuery){
    //AMD.Registerasanonymousmodule.
    define(['jquery'],factory);
  }elseif(typeofmodule!=='undefined'&&module.exports){
    //CommonJSModule
    factory(require("jquery"));
  }else{
    //Browserglobals.
    factory(jQuery);
  }
}(function($){
  "usestrict";

  //Constants
  varVERSION="1.6.18",
    LEFT="left",
    RIGHT="right",
    UP="up",
    DOWN="down",
    IN="in",
    OUT="out",

    NONE="none",
    AUTO="auto",

    SWIPE="swipe",
    PINCH="pinch",
    TAP="tap",
    DOUBLE_TAP="doubletap",
    LONG_TAP="longtap",
    HOLD="hold",

    HORIZONTAL="horizontal",
    VERTICAL="vertical",

    ALL_FINGERS="all",

    DOUBLE_TAP_THRESHOLD=10,

    PHASE_START="start",
    PHASE_MOVE="move",
    PHASE_END="end",
    PHASE_CANCEL="cancel",

    SUPPORTS_TOUCH='ontouchstart'inwindow,

    SUPPORTS_POINTER_IE10=window.navigator.msPointerEnabled&&!window.navigator.pointerEnabled&&!SUPPORTS_TOUCH,

    SUPPORTS_POINTER=(window.navigator.pointerEnabled||window.navigator.msPointerEnabled)&&!SUPPORTS_TOUCH,

    PLUGIN_NS='TouchSwipe';



  /**
  *Thedefaultconfiguration,andavailableoptionstoconfiguretouchswipewith.
  *Youcansetthedefaultvaluesbyupdatinganyofthepropertiespriortoinstantiation.
  *@name$.fn.swipe.defaults
  *@namespace
  *@property{int}[fingers=1]Thenumberoffingerstodetectinaswipe.AnyswipesthatdonotmeetthisrequirementwillNOTtriggerswipehandlers.
  *@property{int}[threshold=75]Thenumberofpixelsthattheusermustmovetheirfingerbybeforeitisconsideredaswipe.
  *@property{int}[cancelThreshold=null]Thenumberofpixelsthattheusermustmovetheirfingerbackfromtheoriginalswipedirectiontocancelthegesture.
  *@property{int}[pinchThreshold=20]Thenumberofpixelsthattheusermustpinchtheirfingerbybeforeitisconsideredapinch.
  *@property{int}[maxTimeThreshold=null]Time,inmilliseconds,betweentouchStartandtouchEndmustNOTexceedinordertobeconsideredaswipe.
  *@property{int}[fingerReleaseThreshold=250]Timeinmillisecondsbetweenreleasingmultiplefingers. If2fingersaredown,andarereleasedoneaftertheother,iftheyarewithinthisthreshold,itcountsasasimultaneousrelease.
  *@property{int}[longTapThreshold=500]Timeinmillisecondsbetweentapandreleaseforalongtap
  *@property{int}[doubleTapThreshold=200]Timeinmillisecondsbetween2tapstocountasadoubletap
  *@property{function}[swipe=null]Ahandlertocatchallswipes.See{@link$.fn.swipe#event:swipe}
  *@property{function}[swipeLeft=null]Ahandlerthatistriggeredfor"left"swipes.See{@link$.fn.swipe#event:swipeLeft}
  *@property{function}[swipeRight=null]Ahandlerthatistriggeredfor"right"swipes.See{@link$.fn.swipe#event:swipeRight}
  *@property{function}[swipeUp=null]Ahandlerthatistriggeredfor"up"swipes.See{@link$.fn.swipe#event:swipeUp}
  *@property{function}[swipeDown=null]Ahandlerthatistriggeredfor"down"swipes.See{@link$.fn.swipe#event:swipeDown}
  *@property{function}[swipeStatus=null]Ahandlertriggeredforeveryphaseoftheswipe.See{@link$.fn.swipe#event:swipeStatus}
  *@property{function}[pinchIn=null]Ahandlertriggeredforpinchinevents.See{@link$.fn.swipe#event:pinchIn}
  *@property{function}[pinchOut=null]Ahandlertriggeredforpinchoutevents.See{@link$.fn.swipe#event:pinchOut}
  *@property{function}[pinchStatus=null]Ahandlertriggeredforeveryphaseofapinch.See{@link$.fn.swipe#event:pinchStatus}
  *@property{function}[tap=null]Ahandlertriggeredwhenauserjusttapsontheitem,ratherthanswipesit.Iftheydonotmove,tapistriggered,iftheydomove,itisnot.
  *@property{function}[doubleTap=null]Ahandlertriggeredwhenauserdoubletapsontheitem.ThedelaybetweentapscanbesetwiththedoubleTapThresholdproperty.See{@link$.fn.swipe.defaults#doubleTapThreshold}
  *@property{function}[longTap=null]Ahandlertriggeredwhenauserlongtapsontheitem.ThedelaybetweenstartandendcanbesetwiththelongTapThresholdproperty.See{@link$.fn.swipe.defaults#longTapThreshold}
  *@property(function)[hold=null]AhandlertriggeredwhenauserreacheslongTapThresholdontheitem.See{@link$.fn.swipe.defaults#longTapThreshold}
  *@property{boolean}[triggerOnTouchEnd=true]Iftrue,theswipeeventsaretriggeredwhenthetouchendeventisreceived(userreleasesfinger). Iffalse,itwillbetriggeredonreachingthethreshold,andthencancelthetoucheventautomatically.
  *@property{boolean}[triggerOnTouchLeave=false]Iftrue,thenwhentheuserleavestheswipeobject,theswipewillendandtriggerappropriatehandlers.
  *@property{string|undefined}[allowPageScroll='auto']HowthebrowserhandlespagescrollswhentheuserisswipingonatouchSwipeobject.See{@link$.fn.swipe.pageScroll}. <br/><br/>
  									<code>"auto"</code>:allundefinedswipeswillcausethepagetoscrollinthatdirection.<br/>
  									<code>"none"</code>:thepagewillnotscrollwhenuserswipes.<br/>
  									<code>"horizontal"</code>:willforcepagetoscrollonhorizontalswipes.<br/>
  									<code>"vertical"</code>:willforcepagetoscrollonverticalswipes.<br/>
  *@property{boolean}[fallbackToMouseEvents=true]Iftruemouseeventsareusedwhenrunonanontouchdevice,falsewillstopswipesbeingtriggeredbymouseeventsonnontocuhdevices.
  *@property{string}[excludedElements=".noSwipe"]AjqueryselectorthatspecifieschildelementsthatdoNOTtriggerswipes.Bydefaultthisexcludeselementswiththeclass.noSwipe.
  *@property{boolean}[preventDefaultEvents=true]bydefaultdefaulteventsarecancelled,sothepagedoesn'tmove. Youcandissablethissobothnativeeventsfireaswellasyourhandlers.

  */
  vardefaults={
    fingers:1,
    threshold:75,
    cancelThreshold:null,
    pinchThreshold:20,
    maxTimeThreshold:null,
    fingerReleaseThreshold:250,
    longTapThreshold:500,
    doubleTapThreshold:200,
    swipe:null,
    swipeLeft:null,
    swipeRight:null,
    swipeUp:null,
    swipeDown:null,
    swipeStatus:null,
    pinchIn:null,
    pinchOut:null,
    pinchStatus:null,
    click:null,//Deprecatedsince1.6.2
    tap:null,
    doubleTap:null,
    longTap:null,
    hold:null,
    triggerOnTouchEnd:true,
    triggerOnTouchLeave:false,
    allowPageScroll:"auto",
    fallbackToMouseEvents:true,
    excludedElements:".noSwipe",
    preventDefaultEvents:true
  };



  /**
   *AppliesTouchSwipebehaviourtooneormorejQueryobjects.
   *TheTouchSwipeplugincanbeinstantiatedviathismethod,ormethodswithin
   *TouchSwipecanbeexecutedviathismethodasperjQuerypluginarchitecture.
   *Anexistingplugincanhaveitsoptionschangedsimplybyrecalling.swipe(options)
   *@seeTouchSwipe
   *@class
   *@param{Mixed}methodIfthecurrentDOMNodeisaTouchSwipeobject,and<code>method</code>isaTouchSwipemethod,then
   *the<code>method</code>isexecuted,andanyfollowingargumentsarepassedtotheTouchSwipemethod.
   *If<code>method</code>isanobject,thentheTouchSwipeclassisinstantiatedonthecurrentDOMNode,passingthe
   *configurationpropertiesdefinedintheobject.SeeTouchSwipe
   *
   */
  $.fn.swipe=function(method){
    var$this=$(this),
      plugin=$this.data(PLUGIN_NS);

    //Checkifwearealreadyinstantiatedandtryingtoexecuteamethod
    if(plugin&&typeofmethod==='string'){
      if(plugin[method]){
        returnplugin[method].apply(plugin,Array.prototype.slice.call(arguments,1));
      }else{
        $.error('Method'+method+'doesnotexistonjQuery.swipe');
      }
    }

    //Elseupdateexistingpluginwithnewoptionshash
    elseif(plugin&&typeofmethod==='object'){
      plugin['option'].apply(plugin,arguments);
    }

    //Elsenotinstantiatedandtryingtopassinitobject(ornothing)
    elseif(!plugin&&(typeofmethod==='object'||!method)){
      returninit.apply(this,arguments);
    }

    return$this;
  };

  /**
   *Theversionoftheplugin
   *@readonly
   */
  $.fn.swipe.version=VERSION;



  //Exposeourdefaultssoausercouldoverridetheplugindefaults
  $.fn.swipe.defaults=defaults;

  /**
   *Thephasesthatatoucheventgoesthrough. The<code>phase</code>ispassedtotheeventhandlers.
   *Thesepropertiesarereadonly,attemptingtochangethemwillnotalterthevaluespassedtotheeventhandlers.
   *@namespace
   *@readonly
   *@property{string}PHASE_STARTConstantindicatingthestartphaseofthetouchevent.Valueis<code>"start"</code>.
   *@property{string}PHASE_MOVEConstantindicatingthemovephaseofthetouchevent.Valueis<code>"move"</code>.
   *@property{string}PHASE_ENDConstantindicatingtheendphaseofthetouchevent.Valueis<code>"end"</code>.
   *@property{string}PHASE_CANCELConstantindicatingthecancelphaseofthetouchevent.Valueis<code>"cancel"</code>.
   */
  $.fn.swipe.phases={
    PHASE_START:PHASE_START,
    PHASE_MOVE:PHASE_MOVE,
    PHASE_END:PHASE_END,
    PHASE_CANCEL:PHASE_CANCEL
  };

  /**
   *Thedirectionconstantsthatarepassedtotheeventhandlers.
   *Thesepropertiesarereadonly,attemptingtochangethemwillnotalterthevaluespassedtotheeventhandlers.
   *@namespace
   *@readonly
   *@property{string}LEFTConstantindicatingtheleftdirection.Valueis<code>"left"</code>.
   *@property{string}RIGHTConstantindicatingtherightdirection.Valueis<code>"right"</code>.
   *@property{string}UPConstantindicatingtheupdirection.Valueis<code>"up"</code>.
   *@property{string}DOWNConstantindicatingthedowndirection.Valueis<code>"cancel"</code>.
   *@property{string}INConstantindicatingtheindirection.Valueis<code>"in"</code>.
   *@property{string}OUTConstantindicatingtheoutdirection.Valueis<code>"out"</code>.
   */
  $.fn.swipe.directions={
    LEFT:LEFT,
    RIGHT:RIGHT,
    UP:UP,
    DOWN:DOWN,
    IN:IN,
    OUT:OUT
  };

  /**
   *Thepagescrollconstantsthatcanbeusedtosetthevalueof<code>allowPageScroll</code>option
   *Thesepropertiesarereadonly
   *@namespace
   *@readonly
   *@see$.fn.swipe.defaults#allowPageScroll
   *@property{string}NONEConstantindicatingnopagescrollingisallowed.Valueis<code>"none"</code>.
   *@property{string}HORIZONTALConstantindicatinghorizontalpagescrollingisallowed.Valueis<code>"horizontal"</code>.
   *@property{string}VERTICALConstantindicatingverticalpagescrollingisallowed.Valueis<code>"vertical"</code>.
   *@property{string}AUTOConstantindicatingeitherhorizontalorverticalwillbeallowed,dependingontheswipehandlersregistered.Valueis<code>"auto"</code>.
   */
  $.fn.swipe.pageScroll={
    NONE:NONE,
    HORIZONTAL:HORIZONTAL,
    VERTICAL:VERTICAL,
    AUTO:AUTO
  };

  /**
   *Constantsrepresentingthenumberoffingersusedinaswipe. Theseareusedtosetboththevalueof<code>fingers</code>inthe
   *optionsobject,aswellasthevalueofthe<code>fingers</code>eventproperty.
   *Thesepropertiesarereadonly,attemptingtochangethemwillnotalterthevaluespassedtotheeventhandlers.
   *@namespace
   *@readonly
   *@see$.fn.swipe.defaults#fingers
   *@property{string}ONEConstantindicating1fingeristobedetected/wasdetected.Valueis<code>1</code>.
   *@property{string}TWOConstantindicating2fingersaretobedetected/weredetected.Valueis<code>2</code>.
   *@property{string}THREEConstantindicating3fingeraretobedetected/weredetected.Valueis<code>3</code>.
   *@property{string}FOURConstantindicating4fingeraretobedetected/weredetected.Notalldevicessupportthis.Valueis<code>4</code>.
   *@property{string}FIVEConstantindicating5fingeraretobedetected/weredetected.Notalldevicessupportthis.Valueis<code>5</code>.
   *@property{string}ALLConstantindicatinganycombinationoffingeraretobedetected. Valueis<code>"all"</code>.
   */
  $.fn.swipe.fingers={
    ONE:1,
    TWO:2,
    THREE:3,
    FOUR:4,
    FIVE:5,
    ALL:ALL_FINGERS
  };

  /**
   *InitialisethepluginforeachDOMelementmatched
   *ThiscreatesanewinstanceofthemainTouchSwipeclassforeachDOMelement,andthen
   *savesareferencetothatinstanceintheelementsdataproperty.
   *@internal
   */
  functioninit(options){
    //Prepandextendtheoptions
    if(options&&(options.allowPageScroll===undefined&&(options.swipe!==undefined||options.swipeStatus!==undefined))){
      options.allowPageScroll=NONE;
    }

    //Checkfordeprecatedoptions
    //Ensurethatanyoldclickhandlersareassignedtothenewtap,unlesswehaveatap
    if(options.click!==undefined&&options.tap===undefined){
      options.tap=options.click;
    }

    if(!options){
      options={};
    }

    //passemptyobjectsowedontmodifythedefaults
    options=$.extend({},$.fn.swipe.defaults,options);

    //Foreachelementinstantiatetheplugin
    returnthis.each(function(){
      var$this=$(this);

      //Checkwehaventalreadyinitialisedtheplugin
      varplugin=$this.data(PLUGIN_NS);

      if(!plugin){
        plugin=newTouchSwipe(this,options);
        $this.data(PLUGIN_NS,plugin);
      }
    });
  }

  /**
   *MainTouchSwipePluginClass.
   *DonotusethistoconstructyourTouchSwipeobject,usethejQuerypluginmethod$.fn.swipe();{@link$.fn.swipe}
   *@private
   *@nameTouchSwipe
   *@param{DOMNode}elementTheHTMLDOMobjecttoapplytopluginto
   *@param{Object}optionsTheoptionstoconfigurethepluginwith. @link{$.fn.swipe.defaults}
   *@see$.fh.swipe.defaults
   *@see$.fh.swipe
   *@class
   */
  functionTouchSwipe(element,options){

    //takealocal/instacnelevelcopyoftheoptions-shouldmakeitthis.optionsreally...
    varoptions=$.extend({},options);

    varuseTouchEvents=(SUPPORTS_TOUCH||SUPPORTS_POINTER||!options.fallbackToMouseEvents),
      START_EV=useTouchEvents?(SUPPORTS_POINTER?(SUPPORTS_POINTER_IE10?'MSPointerDown':'pointerdown'):'touchstart'):'mousedown',
      MOVE_EV=useTouchEvents?(SUPPORTS_POINTER?(SUPPORTS_POINTER_IE10?'MSPointerMove':'pointermove'):'touchmove'):'mousemove',
      END_EV=useTouchEvents?(SUPPORTS_POINTER?(SUPPORTS_POINTER_IE10?'MSPointerUp':'pointerup'):'touchend'):'mouseup',
      LEAVE_EV=useTouchEvents?(SUPPORTS_POINTER?'mouseleave':null):'mouseleave',//wemanuallydetectleaveontouchdevices,sonulleventhere
      CANCEL_EV=(SUPPORTS_POINTER?(SUPPORTS_POINTER_IE10?'MSPointerCancel':'pointercancel'):'touchcancel');



    //touchproperties
    vardistance=0,
      direction=null,
      currentDirection=null,
      duration=0,
      startTouchesDistance=0,
      endTouchesDistance=0,
      pinchZoom=1,
      pinchDistance=0,
      pinchDirection=0,
      maximumsMap=null;



    //jQuerywrappedelementforthisinstance
    var$element=$(element);

    //Currentphaseofthtouchcycle
    varphase="start";

    //thecurrentnumberoffingersbeingused.
    varfingerCount=0;

    //trackmousepoints/delta
    varfingerData={};

    //tracktimes
    varstartTime=0,
      endTime=0,
      previousTouchEndTime=0,
      fingerCountAtRelease=0,
      doubleTapStartTime=0;

    //Timeouts
    varsingleTapTimeout=null,
      holdTimeout=null;

    //Addgesturestoallswipableareasifsupported
    try{
      $element.bind(START_EV,touchStart);
      $element.bind(CANCEL_EV,touchCancel);
    }catch(e){
      $.error('eventsnotsupported'+START_EV+','+CANCEL_EV+'onjQuery.swipe');
    }

    //
    //Publicmethods
    //

    /**
     *re-enablestheswipepluginwiththepreviousconfiguration
     *@function
     *@name$.fn.swipe#enable
     *@return{DOMNode}TheDomelementthatwasregisteredwithTouchSwipe
     *@example$("#element").swipe("enable");
     */
    this.enable=function(){
      //Incasewearealreadyenabled,cleanup...
      this.disable();
      $element.bind(START_EV,touchStart);
      $element.bind(CANCEL_EV,touchCancel);
      return$element;
    };

    /**
     *disablestheswipeplugin
     *@function
     *@name$.fn.swipe#disable
     *@return{DOMNode}TheDomelementthatisnowregisteredwithTouchSwipe
     *@example$("#element").swipe("disable");
     */
    this.disable=function(){
      removeListeners();
      return$element;
    };

    /**
     *Destroytheswipeplugincompletely.Touseanyswipemethods,youmustreinitialisetheplugin.
     *@function
     *@name$.fn.swipe#destroy
     *@example$("#element").swipe("destroy");
     */
    this.destroy=function(){
      removeListeners();
      $element.data(PLUGIN_NS,null);
      $element=null;
    };


    /**
     *Allowsruntimeupdatingoftheswipeconfigurationoptions.
     *@function
     *@name$.fn.swipe#option
     *@param{String}propertyTheoptionpropertytogetorset,orahasofmultipleoptionstoset
     *@param{Object}[value]Thevaluetosetthepropertyto
     *@return{Object}Ifonlyapropertynameispassed,thenthatpropertyvalueisreturned.Ifnothingispassedthecurrentoptionshashisreturned.
     *@example$("#element").swipe("option","threshold");//returnthethreshold
     *@example$("#element").swipe("option","threshold",100);//setthethresholdafterinit
     *@example$("#element").swipe("option",{threshold:100,fingers:3});//setmultiplepropertiesafterinit
     *@example$("#element").swipe({threshold:100,fingers:3});//setmultiplepropertiesafterinit-the"option"methodisoptional!
     *@example$("#element").swipe("option");//Returnthecurrentoptionshash
     *@see$.fn.swipe.defaults
     *
     */
    this.option=function(property,value){

      if(typeofproperty==='object'){
        options=$.extend(options,property);
      }elseif(options[property]!==undefined){
        if(value===undefined){
          returnoptions[property];
        }else{
          options[property]=value;
        }
      }elseif(!property){
        returnoptions;
      }else{
        $.error('Option'+property+'doesnotexistonjQuery.swipe.options');
      }

      returnnull;
    }



    //
    //Privatemethods
    //

    //
    //EVENTS
    //
    /**
     *Eventhandlerforatouchstartevent.
     *Stopsthedefaultclickeventfromtriggeringandstoreswherewetouched
     *@inner
     *@param{object}jqEventThenormalisedjQueryeventobject.
     */
    functiontouchStart(jqEvent){

      //Ifwealreadyinatouchevent(afingeralreadyinuse)thenignoresubsequentones..
      if(getTouchInProgress()){
        return;
      }

      //Checkifthiselementmatchesanyintheexcludedelementsselectors, oritsparentisexcluded,ifso,DON'Tswipe
      if($(jqEvent.target).closest(options.excludedElements,$element).length>0){
        return;
      }

      //AsweuseJquerybindforevents,weneedtotargettheoriginaleventobject
      //Iftheseeventsarebeingprogrammaticallytriggered,wedon'thaveanoriginaleventobject,sousetheJqone.
      varevent=jqEvent.originalEvent?jqEvent.originalEvent:jqEvent;


      //Ifwehaveapointerevent,whoestypeis'mouse'andwehavesaidNOmouseevents,thendontdoanything.
      if(event.pointerType&&event.pointerType=="mouse"&&options.fallbackToMouseEvents==false){
        return;
      };

      varret,
        touches=event.touches,
        evt=touches?touches[0]:event;

      phase=PHASE_START;

      //Ifwesupporttouches,getthefingercount
      if(touches){
        //getthetotalnumberoffingerstouchingthescreen
        fingerCount=touches.length;
      }
      //Elsethisisthedesktop,sostopthebrowserfromdraggingcontent
      elseif(options.preventDefaultEvents!==false){
        jqEvent.preventDefault();//callthisonjqeventsowearecrossbrowser
      }

      //clearvars..
      distance=0;
      direction=null;
      currentDirection=null;
      pinchDirection=null;
      duration=0;
      startTouchesDistance=0;
      endTouchesDistance=0;
      pinchZoom=1;
      pinchDistance=0;
      maximumsMap=createMaximumsData();
      cancelMultiFingerRelease();

      //Createthedefaultfingerdata
      createFingerData(0,evt);

      //checkthenumberoffingersiswhatwearelookingfor,orwearecapturingpinches
      if(!touches||(fingerCount===options.fingers||options.fingers===ALL_FINGERS)||hasPinches()){
        //getthecoordinatesofthetouch
        startTime=getTimeStamp();

        if(fingerCount==2){
          //Keeptrackoftheinitialpinchdistance,sowecancalculatethedifflater
          //Storesecondfingerdataasstart
          createFingerData(1,touches[1]);
          startTouchesDistance=endTouchesDistance=calculateTouchesDistance(fingerData[0].start,fingerData[1].start);
        }

        if(options.swipeStatus||options.pinchStatus){
          ret=triggerHandler(event,phase);
        }
      }else{
        //Atouchwithmoreorlessthanthefingerswearelookingfor,socancel
        ret=false;
      }

      //Ifwehaveareturnvaluefromtheusershandler,thenreturnandcancel
      if(ret===false){
        phase=PHASE_CANCEL;
        triggerHandler(event,phase);
        returnret;
      }else{
        if(options.hold){
          holdTimeout=setTimeout($.proxy(function(){
            //Triggertheevent
            $element.trigger('hold',[event.target]);
            //Firethecallback
            if(options.hold){
              ret=options.hold.call($element,event,event.target);
            }
          },this),options.longTapThreshold);
        }

        setTouchInProgress(true);
      }

      returnnull;
    };



    /**
     *Eventhandlerforatouchmoveevent.
     *Ifwechangefingersduringmove,thencanceltheevent
     *@inner
     *@param{object}jqEventThenormalisedjQueryeventobject.
     */
    functiontouchMove(jqEvent){

      //AsweuseJquerybindforevents,weneedtotargettheoriginaleventobject
      //Iftheseeventsarebeingprogrammaticallytriggered,wedon'thaveanoriginaleventobject,sousetheJqone.
      varevent=jqEvent.originalEvent?jqEvent.originalEvent:jqEvent;

      //Ifweareending,cancelling,orwithinthethresholdof2fingersbeingreleased,don'ttrackanything..
      if(phase===PHASE_END||phase===PHASE_CANCEL||inMultiFingerRelease())
        return;

      varret,
        touches=event.touches,
        evt=touches?touches[0]:event;


      //Updatethe fingerdata
      varcurrentFinger=updateFingerData(evt);
      endTime=getTimeStamp();

      if(touches){
        fingerCount=touches.length;
      }

      if(options.hold){
        clearTimeout(holdTimeout);
      }

      phase=PHASE_MOVE;

      //Ifwehave2fingersgetTouchesdistanceaswell
      if(fingerCount==2){

        //Keeptrackoftheinitialpinchdistance,sowecancalculatethedifflater
        //Wedothishereaswellasthestartevent,incasetheystartwith1finger,andthepress2fingers
        if(startTouchesDistance==0){
          //Createsecondfingerifthisisthefirsttime...
          createFingerData(1,touches[1]);

          startTouchesDistance=endTouchesDistance=calculateTouchesDistance(fingerData[0].start,fingerData[1].start);
        }else{
          //Elsejustupdatethesecondfinger
          updateFingerData(touches[1]);

          endTouchesDistance=calculateTouchesDistance(fingerData[0].end,fingerData[1].end);
          pinchDirection=calculatePinchDirection(fingerData[0].end,fingerData[1].end);
        }

        pinchZoom=calculatePinchZoom(startTouchesDistance,endTouchesDistance);
        pinchDistance=Math.abs(startTouchesDistance-endTouchesDistance);
      }

      if((fingerCount===options.fingers||options.fingers===ALL_FINGERS)||!touches||hasPinches()){

        //Theoveralldirectionoftheswipe.Fromstarttonow.
        direction=calculateDirection(currentFinger.start,currentFinger.end);

        //Theimmediatedirectionoftheswipe,directionbetweenthelastmovementandthisone.
        currentDirection=calculateDirection(currentFinger.last,currentFinger.end);

        //Checkifweneedtopreventdefaultevent(pagescroll/pinchzoom)ornot
        validateDefaultEvent(jqEvent,currentDirection);

        //Distanceanddurationarealloffthemainfinger
        distance=calculateDistance(currentFinger.start,currentFinger.end);
        duration=calculateDuration();

        //Cachethemaximumdistancewemadeinthisdirection
        setMaxDistance(direction,distance);

        //Triggerstatushandler
        ret=triggerHandler(event,phase);


        //Ifwetriggerendeventswhenthresholdaremet,ortriggereventswhentouchleaveselement
        if(!options.triggerOnTouchEnd||options.triggerOnTouchLeave){

          varinBounds=true;

          //Ifcheckingifweleavetheelement,runtheboundscheck(wecanusetouchleaveasitsnotsupportedonwebkit)
          if(options.triggerOnTouchLeave){
            varbounds=getbounds(this);
            inBounds=isInBounds(currentFinger.end,bounds);
          }

          //Triggerendhandlesasweswipeifthresholdsmetorifwehavelefttheelementiftheuserhasaskedtocheckthese..
          if(!options.triggerOnTouchEnd&&inBounds){
            phase=getNextPhase(PHASE_MOVE);
          }
          //Weendifoutofboundshere,sosetcurrentphasetoEND,andcheckifitsmodified
          elseif(options.triggerOnTouchLeave&&!inBounds){
            phase=getNextPhase(PHASE_END);
          }

          if(phase==PHASE_CANCEL||phase==PHASE_END){
            triggerHandler(event,phase);
          }
        }
      }else{
        phase=PHASE_CANCEL;
        triggerHandler(event,phase);
      }

      if(ret===false){
        phase=PHASE_CANCEL;
        triggerHandler(event,phase);
      }
    }




    /**
     *Eventhandlerforatouchendevent.
     *Calculatethedirectionandtriggerevents
     *@inner
     *@param{object}jqEventThenormalisedjQueryeventobject.
     */
    functiontouchEnd(jqEvent){
      //AsweuseJquerybindforevents,weneedtotargettheoriginaleventobject
      //Iftheseeventsarebeingprogrammaticallytriggered,wedon'thaveanoriginaleventobject,sousetheJqone.
      varevent=jqEvent.originalEvent?jqEvent.originalEvent:jqEvent,
        touches=event.touches;

      //Ifwearestillinatouchwiththedevicewaitafractionandseeiftheotherfingercomesup
      //ifitdoeswithinthethreshold,thenwetreatitasamultirelease,notasinglereleaseandendthetouch/swipe
      if(touches){
        if(touches.length&&!inMultiFingerRelease()){
          startMultiFingerRelease(event);
          returntrue;
        }elseif(touches.length&&inMultiFingerRelease()){
          returntrue;
        }
      }

      //Ifapreviousfingerhasbeenreleased,checkhowlongago,ifwithinthethreshold,thenassumeitwasamultifingerrelease.
      //Thisisusedtoallow2fingerstoreleasefractionallyaftereachother,whilstmaintainingtheeventascontaining2fingers,not1
      if(inMultiFingerRelease()){
        fingerCount=fingerCountAtRelease;
      }

      //Setendofswipe
      endTime=getTimeStamp();

      //Getdurationincasemovewasneverfired
      duration=calculateDuration();

      //IfwetriggerhandlersatendofswipeOR,wetriggerduring,buttheydidnttriggerandwearestillinthemovephase
      if(didSwipeBackToCancel()||!validateSwipeDistance()){
        phase=PHASE_CANCEL;
        triggerHandler(event,phase);
      }elseif(options.triggerOnTouchEnd||(options.triggerOnTouchEnd===false&&phase===PHASE_MOVE)){
        //callthisonjqeventsowearecrossbrowser
        if(options.preventDefaultEvents!==false){
          jqEvent.preventDefault();
        }
        phase=PHASE_END;
        triggerHandler(event,phase);
      }
      //Specialcases-Atapshouldalwaysfireontouchendregardless,
      //Soherewemanuallytriggerthetapendhandlerbyitself
      //Wedontruntriggerhandlerasitwillre-triggereventsthatmayhavefiredalready
      elseif(!options.triggerOnTouchEnd&&hasTap()){
        //Triggerthepinchevents...
        phase=PHASE_END;
        triggerHandlerForGesture(event,phase,TAP);
      }elseif(phase===PHASE_MOVE){
        phase=PHASE_CANCEL;
        triggerHandler(event,phase);
      }

      setTouchInProgress(false);

      returnnull;
    }



    /**
     *Eventhandlerforatouchcancelevent.
     *Clearscurrentvars
     *@inner
     */
    functiontouchCancel(){
      //resetthevariablesbacktodefaultvalues
      fingerCount=0;
      endTime=0;
      startTime=0;
      startTouchesDistance=0;
      endTouchesDistance=0;
      pinchZoom=1;

      //Ifwewereinprogressoftrackingapossiblemultitouchend,thenresetit.
      cancelMultiFingerRelease();

      setTouchInProgress(false);
    }


    /**
     *Eventhandlerforatouchleaveevent.
     *Thisisonlytriggeredondesktops,intouchweworkthisoutmanually
     *asthetouchleaveeventisnotsupportedinwebkit
     *@inner
     */
    functiontouchLeave(jqEvent){
      //Iftheseeventsarebeingprogrammaticallytriggered,wedon'thaveanoriginaleventobject,sousetheJqone.
      varevent=jqEvent.originalEvent?jqEvent.originalEvent:jqEvent;

      //Ifwehavethetriggeronleavepropertyset....
      if(options.triggerOnTouchLeave){
        phase=getNextPhase(PHASE_END);
        triggerHandler(event,phase);
      }
    }

    /**
     *Removesalllistenersthatwereassociatedwiththeplugin
     *@inner
     */
    functionremoveListeners(){
      $element.unbind(START_EV,touchStart);
      $element.unbind(CANCEL_EV,touchCancel);
      $element.unbind(MOVE_EV,touchMove);
      $element.unbind(END_EV,touchEnd);

      //weonlyhaveleaveeventsondesktop,wemanuallycalculateleaveontouchasitsnotsupportedinwebkit
      if(LEAVE_EV){
        $element.unbind(LEAVE_EV,touchLeave);
      }

      setTouchInProgress(false);
    }


    /**
     *Checksifthetimeanddistancethresholdshavebeenmet,andifsothentheappropriatehandlersarefired.
     */
    functiongetNextPhase(currentPhase){

      varnextPhase=currentPhase;

      //Ensurewehavevalidswipe(undertimeandoverdistance andcheckifweareoutofbound...)
      varvalidTime=validateSwipeTime();
      varvalidDistance=validateSwipeDistance();
      vardidCancel=didSwipeBackToCancel();

      //Ifwehaveexceededourtime,thencancel
      if(!validTime||didCancel){
        nextPhase=PHASE_CANCEL;
      }
      //Elseifwearemoving,andhavereacheddistancethenend
      elseif(validDistance&&currentPhase==PHASE_MOVE&&(!options.triggerOnTouchEnd||options.triggerOnTouchLeave)){
        nextPhase=PHASE_END;
      }
      //Elseifwehaveendedbyleavinganddidn'treachdistance,thencancel
      elseif(!validDistance&&currentPhase==PHASE_END&&options.triggerOnTouchLeave){
        nextPhase=PHASE_CANCEL;
      }

      returnnextPhase;
    }


    /**
     *Triggertherelevanteventhandler
     *Thehandlersarepassedtheoriginalevent,theelementthatwasswiped,andinthecaseofthecatchallhandler,thedirectionthatwasswiped,"left","right","up",or"down"
     *@param{object}eventtheoriginaleventobject
     *@param{string}phasethephaseoftheswipe(start,endcanceletc){@link$.fn.swipe.phases}
     *@inner
     */
    functiontriggerHandler(event,phase){



      varret,
        touches=event.touches;

      //SWIPEGESTURES
      if(didSwipe()||hasSwipes()){
          ret=triggerHandlerForGesture(event,phase,SWIPE);
      }

      //PINCHGESTURES(iftheabovedidn'tcancel)
      if((didPinch()||hasPinches())&&ret!==false){
          ret=triggerHandlerForGesture(event,phase,PINCH);
      }

      //CLICK/TAP(iftheabovedidn'tcancel)
      if(didDoubleTap()&&ret!==false){
        //Triggerthetapevents...
        ret=triggerHandlerForGesture(event,phase,DOUBLE_TAP);
      }

      //CLICK/TAP(iftheabovedidn'tcancel)
      elseif(didLongTap()&&ret!==false){
        //Triggerthetapevents...
        ret=triggerHandlerForGesture(event,phase,LONG_TAP);
      }

      //CLICK/TAP(iftheabovedidn'tcancel)
      elseif(didTap()&&ret!==false){
        //Triggerthetapevent..
        ret=triggerHandlerForGesture(event,phase,TAP);
      }



      //Ifwearecancellingthegesture,thenmanuallytriggertheresethandler
      if(phase===PHASE_CANCEL){

        touchCancel(event);
      }




      //Ifweareendingthegesture,thenmanuallytriggertheresethandlerIFallfingersareoff
      if(phase===PHASE_END){
        //Ifwesupporttouch,thencheckthatallfingersareoffbeforewecancel
        if(touches){
          if(!touches.length){
            touchCancel(event);
          }
        }else{
          touchCancel(event);
        }
      }

      returnret;
    }



    /**
     *Triggertherelevanteventhandler
     *Thehandlersarepassedtheoriginalevent,theelementthatwasswiped,andinthecaseofthecatchallhandler,thedirectionthatwasswiped,"left","right","up",or"down"
     *@param{object}eventtheoriginaleventobject
     *@param{string}phasethephaseoftheswipe(start,endcanceletc){@link$.fn.swipe.phases}
     *@param{string}gesturethegesturetotriggerahandlerfor:PINCHorSWIPE{@link$.fn.swipe.gestures}
     *@returnBooleanFalse,toindicatethattheeventshouldstoppropagation,orvoid.
     *@inner
     */
    functiontriggerHandlerForGesture(event,phase,gesture){

      varret;

      //SWIPES....
      if(gesture==SWIPE){
        //Triggerstatuseverytime..
        $element.trigger('swipeStatus',[phase,direction||null,distance||0,duration||0,fingerCount,fingerData,currentDirection]);

        if(options.swipeStatus){
          ret=options.swipeStatus.call($element,event,phase,direction||null,distance||0,duration||0,fingerCount,fingerData,currentDirection);
          //Ifthestatuscancels,thendontrunthesubsequenteventhandlers..
          if(ret===false)returnfalse;
        }

        if(phase==PHASE_END&&validateSwipe()){

          //Cancelanytapsthatwereinprogress...
          clearTimeout(singleTapTimeout);
          clearTimeout(holdTimeout);

          $element.trigger('swipe',[direction,distance,duration,fingerCount,fingerData,currentDirection]);

          if(options.swipe){
            ret=options.swipe.call($element,event,direction,distance,duration,fingerCount,fingerData,currentDirection);
            //Ifthestatuscancels,thendontrunthesubsequenteventhandlers..
            if(ret===false)returnfalse;
          }

          //triggerdirectionspecificeventhandlers
          switch(direction){
            caseLEFT:
              $element.trigger('swipeLeft',[direction,distance,duration,fingerCount,fingerData,currentDirection]);

              if(options.swipeLeft){
                ret=options.swipeLeft.call($element,event,direction,distance,duration,fingerCount,fingerData,currentDirection);
              }
              break;

            caseRIGHT:
              $element.trigger('swipeRight',[direction,distance,duration,fingerCount,fingerData,currentDirection]);

              if(options.swipeRight){
                ret=options.swipeRight.call($element,event,direction,distance,duration,fingerCount,fingerData,currentDirection);
              }
              break;

            caseUP:
              $element.trigger('swipeUp',[direction,distance,duration,fingerCount,fingerData,currentDirection]);

              if(options.swipeUp){
                ret=options.swipeUp.call($element,event,direction,distance,duration,fingerCount,fingerData,currentDirection);
              }
              break;

            caseDOWN:
              $element.trigger('swipeDown',[direction,distance,duration,fingerCount,fingerData,currentDirection]);

              if(options.swipeDown){
                ret=options.swipeDown.call($element,event,direction,distance,duration,fingerCount,fingerData,currentDirection);
              }
              break;
          }
        }
      }


      //PINCHES....
      if(gesture==PINCH){
        $element.trigger('pinchStatus',[phase,pinchDirection||null,pinchDistance||0,duration||0,fingerCount,pinchZoom,fingerData]);

        if(options.pinchStatus){
          ret=options.pinchStatus.call($element,event,phase,pinchDirection||null,pinchDistance||0,duration||0,fingerCount,pinchZoom,fingerData);
          //Ifthestatuscancels,thendontrunthesubsequenteventhandlers..
          if(ret===false)returnfalse;
        }

        if(phase==PHASE_END&&validatePinch()){

          switch(pinchDirection){
            caseIN:
              $element.trigger('pinchIn',[pinchDirection||null,pinchDistance||0,duration||0,fingerCount,pinchZoom,fingerData]);

              if(options.pinchIn){
                ret=options.pinchIn.call($element,event,pinchDirection||null,pinchDistance||0,duration||0,fingerCount,pinchZoom,fingerData);
              }
              break;

            caseOUT:
              $element.trigger('pinchOut',[pinchDirection||null,pinchDistance||0,duration||0,fingerCount,pinchZoom,fingerData]);

              if(options.pinchOut){
                ret=options.pinchOut.call($element,event,pinchDirection||null,pinchDistance||0,duration||0,fingerCount,pinchZoom,fingerData);
              }
              break;
          }
        }
      }

      if(gesture==TAP){
        if(phase===PHASE_CANCEL||phase===PHASE_END){

          clearTimeout(singleTapTimeout);
          clearTimeout(holdTimeout);

          //IfwearealsolookingfordoubelTaps,waitincasethisisone...
          if(hasDoubleTap()&&!inDoubleTap()){
            doubleTapStartTime=getTimeStamp();

            //Nowwaitforthedoubletaptimeout,andtriggerthissingletap
            //ifitsnotcancelledbyadoubletap
            singleTapTimeout=setTimeout($.proxy(function(){
              doubleTapStartTime=null;
              $element.trigger('tap',[event.target]);

              if(options.tap){
                ret=options.tap.call($element,event,event.target);
              }
            },this),options.doubleTapThreshold);

          }else{
            doubleTapStartTime=null;
            $element.trigger('tap',[event.target]);
            if(options.tap){
              ret=options.tap.call($element,event,event.target);
            }
          }
        }
      }elseif(gesture==DOUBLE_TAP){
        if(phase===PHASE_CANCEL||phase===PHASE_END){
          clearTimeout(singleTapTimeout);
          clearTimeout(holdTimeout);
          doubleTapStartTime=null;
          $element.trigger('doubletap',[event.target]);

          if(options.doubleTap){
            ret=options.doubleTap.call($element,event,event.target);
          }
        }
      }elseif(gesture==LONG_TAP){
        if(phase===PHASE_CANCEL||phase===PHASE_END){
          clearTimeout(singleTapTimeout);
          doubleTapStartTime=null;

          $element.trigger('longtap',[event.target]);
          if(options.longTap){
            ret=options.longTap.call($element,event,event.target);
          }
        }
      }

      returnret;
    }


    //
    //GESTUREVALIDATION
    //

    /**
     *Checkstheuserhasswipefarenough
     *@returnBooleanif<code>threshold</code>hasbeenset,returntrueifthethresholdwasmet,elsefalse.
     *Ifnothresholdwasset,thenwereturntrue.
     *@inner
     */
    functionvalidateSwipeDistance(){
      varvalid=true;
      //Ifwemadeitpasttheminswipedistance..
      if(options.threshold!==null){
        valid=distance>=options.threshold;
      }

      returnvalid;
    }

    /**
     *Checkstheuserhasswipedbacktocancel.
     *@returnBooleanif<code>cancelThreshold</code>hasbeenset,returntrueifthecancelThresholdwasmet,elsefalse.
     *IfnocancelThresholdwasset,thenwereturntrue.
     *@inner
     */
    functiondidSwipeBackToCancel(){
      varcancelled=false;
      if(options.cancelThreshold!==null&&direction!==null){
        cancelled=(getMaxDistance(direction)-distance)>=options.cancelThreshold;
      }

      returncancelled;
    }

    /**
     *Checkstheuserhaspinchedfarenough
     *@returnBooleanif<code>pinchThreshold</code>hasbeenset,returntrueifthethresholdwasmet,elsefalse.
     *Ifnothresholdwasset,thenwereturntrue.
     *@inner
     */
    functionvalidatePinchDistance(){
      if(options.pinchThreshold!==null){
        returnpinchDistance>=options.pinchThreshold;
      }
      returntrue;
    }

    /**
     *Checksthatthetimetakentoswipemeetstheminimum/maximumrequirements
     *@returnBoolean
     *@inner
     */
    functionvalidateSwipeTime(){
      varresult;
      //Ifnotimeset,thenreturntrue
      if(options.maxTimeThreshold){
        if(duration>=options.maxTimeThreshold){
          result=false;
        }else{
          result=true;
        }
      }else{
        result=true;
      }

      returnresult;
    }


    /**
     *ChecksdirectionoftheswipeandthevalueallowPageScrolltoseeifweshouldalloworpreventthedefaultbehaviourfromoccurring.
     *ThiswillessentiallyallowpagescrollingornotwhentheuserisswipingonatouchSwipeobject.
     *@param{object}jqEventThenormalisedjQueryrepresentationoftheeventobject.
     *@param{string}directionThedirectionoftheevent.See{@link$.fn.swipe.directions}
     *@see$.fn.swipe.directions
     *@inner
     */
    functionvalidateDefaultEvent(jqEvent,direction){

      //Iftheoptionisset,allwaysallowtheeventtobubbleup(letuserhandleweirdness)
      if(options.preventDefaultEvents===false){
        return;
      }

      if(options.allowPageScroll===NONE){
        jqEvent.preventDefault();
      }else{
        varauto=options.allowPageScroll===AUTO;

        switch(direction){
          caseLEFT:
            if((options.swipeLeft&&auto)||(!auto&&options.allowPageScroll!=HORIZONTAL)){
              jqEvent.preventDefault();
            }
            break;

          caseRIGHT:
            if((options.swipeRight&&auto)||(!auto&&options.allowPageScroll!=HORIZONTAL)){
              jqEvent.preventDefault();
            }
            break;

          caseUP:
            if((options.swipeUp&&auto)||(!auto&&options.allowPageScroll!=VERTICAL)){
              jqEvent.preventDefault();
            }
            break;

          caseDOWN:
            if((options.swipeDown&&auto)||(!auto&&options.allowPageScroll!=VERTICAL)){
              jqEvent.preventDefault();
            }
            break;

          caseNONE:

            break;
        }
      }
    }


    //PINCHES
    /**
     *Returnstrueofthecurrentpinchmeetsthethresholds
     *@returnBoolean
     *@inner
     */
    functionvalidatePinch(){
      varhasCorrectFingerCount=validateFingers();
      varhasEndPoint=validateEndPoint();
      varhasCorrectDistance=validatePinchDistance();
      returnhasCorrectFingerCount&&hasEndPoint&&hasCorrectDistance;

    }

    /**
     *ReturnstrueifanyPincheventshavebeenregistered
     *@returnBoolean
     *@inner
     */
    functionhasPinches(){
      //Enurewedontreturn0ornullforfalsevalues
      return!!(options.pinchStatus||options.pinchIn||options.pinchOut);
    }

    /**
     *Returnstrueifwearedetectingpinches,andhaveone
     *@returnBoolean
     *@inner
     */
    functiondidPinch(){
      //Enurewedontreturn0ornullforfalsevalues
      return!!(validatePinch()&&hasPinches());
    }




    //SWIPES
    /**
     *Returnstrueifthecurrentswipemeetsthethresholds
     *@returnBoolean
     *@inner
     */
    functionvalidateSwipe(){
      //Checkvalidityofswipe
      varhasValidTime=validateSwipeTime();
      varhasValidDistance=validateSwipeDistance();
      varhasCorrectFingerCount=validateFingers();
      varhasEndPoint=validateEndPoint();
      vardidCancel=didSwipeBackToCancel();

      //iftheuserswipedmorethantheminimumlength,performtheappropriateaction
      //hasValidDistanceisnullwhennodistanceisset
      varvalid=!didCancel&&hasEndPoint&&hasCorrectFingerCount&&hasValidDistance&&hasValidTime;

      returnvalid;
    }

    /**
     *ReturnstrueifanySwipeeventshavebeenregistered
     *@returnBoolean
     *@inner
     */
    functionhasSwipes(){
      //Enurewedontreturn0ornullforfalsevalues
      return!!(options.swipe||options.swipeStatus||options.swipeLeft||options.swipeRight||options.swipeUp||options.swipeDown);
    }


    /**
     *Returnstrueifwearedetectingswipesandhaveone
     *@returnBoolean
     *@inner
     */
    functiondidSwipe(){
      //Enurewedontreturn0ornullforfalsevalues
      return!!(validateSwipe()&&hasSwipes());
    }

    /**
     *Returnstrueifwehavematchedthenumberoffingerswearelookingfor
     *@returnBoolean
     *@inner
     */
    functionvalidateFingers(){
      //Thenumberoffingerswewantwerematched,orondesktopweignore
      return((fingerCount===options.fingers||options.fingers===ALL_FINGERS)||!SUPPORTS_TOUCH);
    }

    /**
     *Returnstrueifwehaveanendpointfortheswipe
     *@returnBoolean
     *@inner
     */
    functionvalidateEndPoint(){
      //Wehaveanendvalueforthefinger
      returnfingerData[0].end.x!==0;
    }

    //TAP/CLICK
    /**
     *Returnstrueifaclick/tapeventshavebeenregistered
     *@returnBoolean
     *@inner
     */
    functionhasTap(){
      //Enurewedontreturn0ornullforfalsevalues
      return!!(options.tap);
    }

    /**
     *Returnstrueifadoubletapeventshavebeenregistered
     *@returnBoolean
     *@inner
     */
    functionhasDoubleTap(){
      //Enurewedontreturn0ornullforfalsevalues
      return!!(options.doubleTap);
    }

    /**
     *Returnstrueifanylongtapeventshavebeenregistered
     *@returnBoolean
     *@inner
     */
    functionhasLongTap(){
      //Enurewedontreturn0ornullforfalsevalues
      return!!(options.longTap);
    }

    /**
     *Returnstrueifwecouldbeintheprocessofadoubletap(onetaphasoccurred,wearelisteningfordoubletaps,andthethresholdhasn'tpast.
     *@returnBoolean
     *@inner
     */
    functionvalidateDoubleTap(){
      if(doubleTapStartTime==null){
        returnfalse;
      }
      varnow=getTimeStamp();
      return(hasDoubleTap()&&((now-doubleTapStartTime)<=options.doubleTapThreshold));
    }

    /**
     *Returnstrueifwecouldbeintheprocessofadoubletap(onetaphasoccurred,wearelisteningfordoubletaps,andthethresholdhasn'tpast.
     *@returnBoolean
     *@inner
     */
    functioninDoubleTap(){
      returnvalidateDoubleTap();
    }


    /**
     *Returnstrueifwehaveavalidtap
     *@returnBoolean
     *@inner
     */
    functionvalidateTap(){
      return((fingerCount===1||!SUPPORTS_TOUCH)&&(isNaN(distance)||distance<options.threshold));
    }

    /**
     *Returnstrueifwehaveavalidlongtap
     *@returnBoolean
     *@inner
     */
    functionvalidateLongTap(){
      //slightthresholdonmovingfinger
      return((duration>options.longTapThreshold)&&(distance<DOUBLE_TAP_THRESHOLD));
    }

    /**
     *Returnstrueifwearedetectingtapsandhaveone
     *@returnBoolean
     *@inner
     */
    functiondidTap(){
      //Enurewedontreturn0ornullforfalsevalues
      return!!(validateTap()&&hasTap());
    }


    /**
     *Returnstrueifwearedetectingdoubletapsandhaveone
     *@returnBoolean
     *@inner
     */
    functiondidDoubleTap(){
      //Enurewedontreturn0ornullforfalsevalues
      return!!(validateDoubleTap()&&hasDoubleTap());
    }

    /**
     *Returnstrueifwearedetectinglongtapsandhaveone
     *@returnBoolean
     *@inner
     */
    functiondidLongTap(){
      //Enurewedontreturn0ornullforfalsevalues
      return!!(validateLongTap()&&hasLongTap());
    }




    //MULTIFINGERTOUCH
    /**
     *Startstrackingthetimebetween2fingerreleases,andkeepstrackofhowmanyfingersweinitiallyhadup
     *@inner
     */
    functionstartMultiFingerRelease(event){
      previousTouchEndTime=getTimeStamp();
      fingerCountAtRelease=event.touches.length+1;
    }

    /**
     *Cancelsthetrackingoftimebetween2fingerreleases,andresetscounters
     *@inner
     */
    functioncancelMultiFingerRelease(){
      previousTouchEndTime=0;
      fingerCountAtRelease=0;
    }

    /**
     *Checksifweareinthethresholdbetween2fingersbeingreleased
     *@returnBoolean
     *@inner
     */
    functioninMultiFingerRelease(){

      varwithinThreshold=false;

      if(previousTouchEndTime){
        vardiff=getTimeStamp()-previousTouchEndTime
        if(diff<=options.fingerReleaseThreshold){
          withinThreshold=true;
        }
      }

      returnwithinThreshold;
    }


    /**
     *getsadataflagtoindicatethatatouchisinprogress
     *@returnBoolean
     *@inner
     */
    functiongetTouchInProgress(){
      //strictequalitytoensureonlytrueandfalsearereturned
      return!!($element.data(PLUGIN_NS+'_intouch')===true);
    }

    /**
     *Setsadataflagtoindicatethatatouchisinprogress
     *@param{boolean}valThevaluetosetthepropertyto
     *@inner
     */
    functionsetTouchInProgress(val){

      //Ifdestroyiscalledinaneventhandler,wehavenoel,andwehavealreadycleanedup,soreturn.
      if(!$element){return;}

      //Addorremoveeventlistenersdependingontouchstatus
      if(val===true){
        $element.bind(MOVE_EV,touchMove);
        $element.bind(END_EV,touchEnd);

        //weonlyhaveleaveeventsondesktop,wemanuallycalcuateleaveontouchasitsnotsupportedinwebkit
        if(LEAVE_EV){
          $element.bind(LEAVE_EV,touchLeave);
        }
      }else{

        $element.unbind(MOVE_EV,touchMove,false);
        $element.unbind(END_EV,touchEnd,false);

        //weonlyhaveleaveeventsondesktop,wemanuallycalcuateleaveontouchasitsnotsupportedinwebkit
        if(LEAVE_EV){
          $element.unbind(LEAVE_EV,touchLeave,false);
        }
      }


      //strictequalitytoensureonlytrueandfalsecanupdatethevalue
      $element.data(PLUGIN_NS+'_intouch',val===true);
    }


    /**
     *Createsthefingerdataforthetouch/fingerintheeventobject.
     *@param{int}idTheidtostorethefingerdataunder(usuallytheorderthefingerswerepressed)
     *@param{object}evtTheeventobjectcontainingfingerdata
     *@returnfingerdataobject
     *@inner
     */
    functioncreateFingerData(id,evt){
      varf={
        start:{
          x:0,
          y:0
        },
        last:{
          x:0,
          y:0
        },
        end:{
          x:0,
          y:0
        }
      };
      f.start.x=f.last.x=f.end.x=evt.pageX||evt.clientX;
      f.start.y=f.last.y=f.end.y=evt.pageY||evt.clientY;
      fingerData[id]=f;
      returnf;
    }

    /**
     *Updatesthefingerdataforaparticulareventobject
     *@param{object}evtTheeventobjectcontainingthetouch/fingerdatatoupadte
     *@returnafingerdataobject.
     *@inner
     */
    functionupdateFingerData(evt){
      varid=evt.identifier!==undefined?evt.identifier:0;
      varf=getFingerData(id);

      if(f===null){
        f=createFingerData(id,evt);
      }

      f.last.x=f.end.x;
      f.last.y=f.end.y;

      f.end.x=evt.pageX||evt.clientX;
      f.end.y=evt.pageY||evt.clientY;

      returnf;
    }

    /**
     *ReturnsafingerdataobjectbyitseventID.
     *Eachtoucheventhasanidentifierproperty,whichisused
     *totrackrepeattouches
     *@param{int}idTheuniqueidofthefingerinthesequenceoftouchevents.
     *@returnafingerdataobject.
     *@inner
     */
    functiongetFingerData(id){
      returnfingerData[id]||null;
    }


    /**
     *Setsthemaximumdistanceswipedinthegivendirection.
     *Ifthenewvalueislowerthanthecurrentvalue,themaxvalueisnotchanged.
     *@param{string} directionThedirectionoftheswipe
     *@param{int} distanceThedistanceoftheswipe
     *@inner
     */
    functionsetMaxDistance(direction,distance){
      if(direction==NONE)return;
      distance=Math.max(distance,getMaxDistance(direction));
      maximumsMap[direction].distance=distance;
    }

    /**
     *getsthemaximumdistanceswipedinthegivendirection.
     *@param{string} directionThedirectionoftheswipe
     *@returnint Thedistanceoftheswipe
     *@inner
     */
    functiongetMaxDistance(direction){
      if(maximumsMap[direction])returnmaximumsMap[direction].distance;
      returnundefined;
    }

    /**
     *Creatsamapofdirectionstomaximumswipedvalues.
     *@returnObjectAdictionaryofmaximumvalues,indexedbydirection.
     *@inner
     */
    functioncreateMaximumsData(){
      varmaxData={};
      maxData[LEFT]=createMaximumVO(LEFT);
      maxData[RIGHT]=createMaximumVO(RIGHT);
      maxData[UP]=createMaximumVO(UP);
      maxData[DOWN]=createMaximumVO(DOWN);

      returnmaxData;
    }

    /**
     *Createsamapmaximumswipedvaluesforagivenswipedirection
     *@param{string}Thedirectionthatthesevalueswillbeassociatedwith
     *@returnObjectMaximumvalues
     *@inner
     */
    functioncreateMaximumVO(dir){
      return{
        direction:dir,
        distance:0
      }
    }


    //
    //MATHS/UTILS
    //

    /**
     *Calculatethedurationoftheswipe
     *@returnint
     *@inner
     */
    functioncalculateDuration(){
      returnendTime-startTime;
    }

    /**
     *Calculatethedistancebetween2touches(pinch)
     *@param{point}startPointApointobjectcontainingxandyco-ordinates
     *@param{point}endPointApointobjectcontainingxandyco-ordinates
     *@returnint;
     *@inner
     */
    functioncalculateTouchesDistance(startPoint,endPoint){
      vardiffX=Math.abs(startPoint.x-endPoint.x);
      vardiffY=Math.abs(startPoint.y-endPoint.y);

      returnMath.round(Math.sqrt(diffX*diffX+diffY*diffY));
    }

    /**
     *Calculatethezoomfactorbetweenthestartandenddistances
     *@param{int}startDistanceDistance(between2fingers)theuserstartedpinchingat
     *@param{int}endDistanceDistance(between2fingers)theuserendedpinchingat
     *@returnfloatThezoomvaluefrom0to1.
     *@inner
     */
    functioncalculatePinchZoom(startDistance,endDistance){
      varpercent=(endDistance/startDistance)*1;
      returnpercent.toFixed(2);
    }


    /**
     *Returnsthepinchdirection,eitherINorOUTforthegivenpoints
     *@returnstringEither{@link$.fn.swipe.directions.IN}or{@link$.fn.swipe.directions.OUT}
     *@see$.fn.swipe.directions
     *@inner
     */
    functioncalculatePinchDirection(){
      if(pinchZoom<1){
        returnOUT;
      }else{
        returnIN;
      }
    }


    /**
     *Calculatethelength/distanceoftheswipe
     *@param{point}startPointApointobjectcontainingxandyco-ordinates
     *@param{point}endPointApointobjectcontainingxandyco-ordinates
     *@returnint
     *@inner
     */
    functioncalculateDistance(startPoint,endPoint){
      returnMath.round(Math.sqrt(Math.pow(endPoint.x-startPoint.x,2)+Math.pow(endPoint.y-startPoint.y,2)));
    }

    /**
     *Calculatetheangleoftheswipe
     *@param{point}startPointApointobjectcontainingxandyco-ordinates
     *@param{point}endPointApointobjectcontainingxandyco-ordinates
     *@returnint
     *@inner
     */
    functioncalculateAngle(startPoint,endPoint){
      varx=startPoint.x-endPoint.x;
      vary=endPoint.y-startPoint.y;
      varr=Math.atan2(y,x);//radians
      varangle=Math.round(r*180/Math.PI);//degrees

      //ensurevalueispositive
      if(angle<0){
        angle=360-Math.abs(angle);
      }

      returnangle;
    }

    /**
     *Calculatethedirectionoftheswipe
     *ThiswillalsocallcalculateAngletogetthelatestangleofswipe
     *@param{point}startPointApointobjectcontainingxandyco-ordinates
     *@param{point}endPointApointobjectcontainingxandyco-ordinates
     *@returnstringEither{@link$.fn.swipe.directions.LEFT}/{@link$.fn.swipe.directions.RIGHT}/{@link$.fn.swipe.directions.DOWN}/{@link$.fn.swipe.directions.UP}
     *@see$.fn.swipe.directions
     *@inner
     */
    functioncalculateDirection(startPoint,endPoint){

      if(comparePoints(startPoint,endPoint)){
        returnNONE;
      }

      varangle=calculateAngle(startPoint,endPoint);

      if((angle<=45)&&(angle>=0)){
        returnLEFT;
      }elseif((angle<=360)&&(angle>=315)){
        returnLEFT;
      }elseif((angle>=135)&&(angle<=225)){
        returnRIGHT;
      }elseif((angle>45)&&(angle<135)){
        returnDOWN;
      }else{
        returnUP;
      }
    }


    /**
     *ReturnsaMStimestampofthecurrenttime
     *@returnint
     *@inner
     */
    functiongetTimeStamp(){
      varnow=newDate();
      returnnow.getTime();
    }



    /**
     *Returnsaboundsobjectwithleft,right,topandbottompropertiesfortheelementspecified.
     *@param{DomNode}TheDOMnodetogettheboundsfor.
     */
    functiongetbounds(el){
      el=$(el);
      varoffset=el.offset();

      varbounds={
        left:offset.left,
        right:offset.left+el.outerWidth(),
        top:offset.top,
        bottom:offset.top+el.outerHeight()
      }

      returnbounds;
    }


    /**
     *Checksifthepointobjectisintheboundsobject.
     *@param{object}pointApointobject.
     *@param{int}point.xThexvalueofthepoint.
     *@param{int}point.yThexvalueofthepoint.
     *@param{object}boundsTheboundsobjecttotest
     *@param{int}bounds.leftTheleftmostvalue
     *@param{int}bounds.rightTherighttmostvalue
     *@param{int}bounds.topThetopmostvalue
     *@param{int}bounds.bottomThebottommostvalue
     */
    functionisInBounds(point,bounds){
      return(point.x>bounds.left&&point.x<bounds.right&&point.y>bounds.top&&point.y<bounds.bottom);
    };

    /**
     *Checksifthetwopointsareequal
     *@param{object}pointApointobject.
     *@param{object}pointBpointobject.
     *@returntrueofthepointsmatch
     */
    functioncomparePoints(pointA,pointB){
      return(pointA.x==pointB.x&&pointA.y==pointB.y);
    }


  }




  /**
   *Acatchallhandlerthatistriggeredforallswipedirections.
   *@name$.fn.swipe#swipe
   *@event
   *@defaultnull
   *@param{EventObject}eventTheoriginaleventobject
   *@param{int}directionThedirectiontheuserswipedin.See{@link$.fn.swipe.directions}
   *@param{int}distanceThedistancetheuserswiped
   *@param{int}durationThedurationoftheswipeinmilliseconds
   *@param{int}fingerCountThenumberoffingersused.See{@link$.fn.swipe.fingers}
   *@param{object}fingerDataThecoordinatesoffingersinevent
   *@param{string}currentDirectionThecurrentdirectiontheuserisswiping.
   */




  /**
   *Ahandlerthatistriggeredfor"left"swipes.
   *@name$.fn.swipe#swipeLeft
   *@event
   *@defaultnull
   *@param{EventObject}eventTheoriginaleventobject
   *@param{int}directionThedirectiontheuserswipedin.See{@link$.fn.swipe.directions}
   *@param{int}distanceThedistancetheuserswiped
   *@param{int}durationThedurationoftheswipeinmilliseconds
   *@param{int}fingerCountThenumberoffingersused.See{@link$.fn.swipe.fingers}
   *@param{object}fingerDataThecoordinatesoffingersinevent
   *@param{string}currentDirectionThecurrentdirectiontheuserisswiping.
   */

  /**
   *Ahandlerthatistriggeredfor"right"swipes.
   *@name$.fn.swipe#swipeRight
   *@event
   *@defaultnull
   *@param{EventObject}eventTheoriginaleventobject
   *@param{int}directionThedirectiontheuserswipedin.See{@link$.fn.swipe.directions}
   *@param{int}distanceThedistancetheuserswiped
   *@param{int}durationThedurationoftheswipeinmilliseconds
   *@param{int}fingerCountThenumberoffingersused.See{@link$.fn.swipe.fingers}
   *@param{object}fingerDataThecoordinatesoffingersinevent
   *@param{string}currentDirectionThecurrentdirectiontheuserisswiping.
   */

  /**
   *Ahandlerthatistriggeredfor"up"swipes.
   *@name$.fn.swipe#swipeUp
   *@event
   *@defaultnull
   *@param{EventObject}eventTheoriginaleventobject
   *@param{int}directionThedirectiontheuserswipedin.See{@link$.fn.swipe.directions}
   *@param{int}distanceThedistancetheuserswiped
   *@param{int}durationThedurationoftheswipeinmilliseconds
   *@param{int}fingerCountThenumberoffingersused.See{@link$.fn.swipe.fingers}
   *@param{object}fingerDataThecoordinatesoffingersinevent
   *@param{string}currentDirectionThecurrentdirectiontheuserisswiping.
   */

  /**
   *Ahandlerthatistriggeredfor"down"swipes.
   *@name$.fn.swipe#swipeDown
   *@event
   *@defaultnull
   *@param{EventObject}eventTheoriginaleventobject
   *@param{int}directionThedirectiontheuserswipedin.See{@link$.fn.swipe.directions}
   *@param{int}distanceThedistancetheuserswiped
   *@param{int}durationThedurationoftheswipeinmilliseconds
   *@param{int}fingerCountThenumberoffingersused.See{@link$.fn.swipe.fingers}
   *@param{object}fingerDataThecoordinatesoffingersinevent
   *@param{string}currentDirectionThecurrentdirectiontheuserisswiping.
   */

  /**
   *Ahandlertriggeredforeveryphaseoftheswipe.Thishandlerisconstantlyfiredforthedurationofthepinch.
   *Thisistriggeredregardlessofswipethresholds.
   *@name$.fn.swipe#swipeStatus
   *@event
   *@defaultnull
   *@param{EventObject}eventTheoriginaleventobject
   *@param{string}phaseThephaseoftheswipeevent.See{@link$.fn.swipe.phases}
   *@param{string}directionThedirectiontheuserswipedin.Thisisnulliftheuserhasyettomove.See{@link$.fn.swipe.directions}
   *@param{int}distanceThedistancetheuserswiped.Thisis0iftheuserhasyettomove.
   *@param{int}durationThedurationoftheswipeinmilliseconds
   *@param{int}fingerCountThenumberoffingersused.See{@link$.fn.swipe.fingers}
   *@param{object}fingerDataThecoordinatesoffingersinevent
   *@param{string}currentDirectionThecurrentdirectiontheuserisswiping.
   */

  /**
   *Ahandlertriggeredforpinchinevents.
   *@name$.fn.swipe#pinchIn
   *@event
   *@defaultnull
   *@param{EventObject}eventTheoriginaleventobject
   *@param{int}directionThedirectiontheuserpinchedin.See{@link$.fn.swipe.directions}
   *@param{int}distanceThedistancetheuserpinched
   *@param{int}durationThedurationoftheswipeinmilliseconds
   *@param{int}fingerCountThenumberoffingersused.See{@link$.fn.swipe.fingers}
   *@param{int}zoomThezoom/scaleleveltheuserpinchedtoo,0-1.
   *@param{object}fingerDataThecoordinatesoffingersinevent
   */

  /**
   *Ahandlertriggeredforpinchoutevents.
   *@name$.fn.swipe#pinchOut
   *@event
   *@defaultnull
   *@param{EventObject}eventTheoriginaleventobject
   *@param{int}directionThedirectiontheuserpinchedin.See{@link$.fn.swipe.directions}
   *@param{int}distanceThedistancetheuserpinched
   *@param{int}durationThedurationoftheswipeinmilliseconds
   *@param{int}fingerCountThenumberoffingersused.See{@link$.fn.swipe.fingers}
   *@param{int}zoomThezoom/scaleleveltheuserpinchedtoo,0-1.
   *@param{object}fingerDataThecoordinatesoffingersinevent
   */

  /**
   *Ahandlertriggeredforallpinchevents.Thishandlerisconstantlyfiredforthedurationofthepinch.Thisistriggeredregardlessofthresholds.
   *@name$.fn.swipe#pinchStatus
   *@event
   *@defaultnull
   *@param{EventObject}eventTheoriginaleventobject
   *@param{int}directionThedirectiontheuserpinchedin.See{@link$.fn.swipe.directions}
   *@param{int}distanceThedistancetheuserpinched
   *@param{int}durationThedurationoftheswipeinmilliseconds
   *@param{int}fingerCountThenumberoffingersused.See{@link$.fn.swipe.fingers}
   *@param{int}zoomThezoom/scaleleveltheuserpinchedtoo,0-1.
   *@param{object}fingerDataThecoordinatesoffingersinevent
   */

  /**
   *Aclickhandlertriggeredwhenausersimplyclicks,ratherthanswipesonanelement.
   *Thisisdeprecatedsinceversion1.6.2,anyassignmenttoclickwillbeassignedtothetaphandler.
   *Youcannotuse<code>on</code>tobindtothiseventasthedefaultjQ<code>click</code>eventwillbetriggered.
   *Usethe<code>tap</code>eventinstead.
   *@name$.fn.swipe#click
   *@event
   *@deprecatedsinceversion1.6.2,pleaseuse{@link$.fn.swipe#tap}instead
   *@defaultnull
   *@param{EventObject}eventTheoriginaleventobject
   *@param{DomObject}targetTheelementclickedon.
   */

  /**
   *Aclick/taphandlertriggeredwhenausersimplyclicksortaps,ratherthanswipesonanelement.
   *@name$.fn.swipe#tap
   *@event
   *@defaultnull
   *@param{EventObject}eventTheoriginaleventobject
   *@param{DomObject}targetTheelementclickedon.
   */

  /**
   *Adoubletaphandlertriggeredwhenauserdoubleclicksortapsonanelement.
   *Youcansetthetimedelayforadoubletapwiththe{@link$.fn.swipe.defaults#doubleTapThreshold}property.
   *Note:Ifyousetboth<code>doubleTap</code>and<code>tap</code>handlers,the<code>tap</code>eventwillbedelayedbythe<code>doubleTapThreshold</code>
   *asthescriptneedstocheckifitsadoubletap.
   *@name$.fn.swipe#doubleTap
   *@see $.fn.swipe.defaults#doubleTapThreshold
   *@event
   *@defaultnull
   *@param{EventObject}eventTheoriginaleventobject
   *@param{DomObject}targetTheelementclickedon.
   */

  /**
   *AlongtaphandlertriggeredonceataphasbeenreleaseifthetapwaslongerthanthelongTapThreshold.
   *Youcansetthetimedelayforalongtapwiththe{@link$.fn.swipe.defaults#longTapThreshold}property.
   *@name$.fn.swipe#longTap
   *@see $.fn.swipe.defaults#longTapThreshold
   *@event
   *@defaultnull
   *@param{EventObject}eventTheoriginaleventobject
   *@param{DomObject}targetTheelementclickedon.
   */

  /**
   *AholdtaphandlertriggeredassoonasthelongTapThresholdisreached
   *Youcansetthetimedelayforalongtapwiththe{@link$.fn.swipe.defaults#longTapThreshold}property.
   *@name$.fn.swipe#hold
   *@see $.fn.swipe.defaults#longTapThreshold
   *@event
   *@defaultnull
   *@param{EventObject}eventTheoriginaleventobject
   *@param{DomObject}targetTheelementclickedon.
   */

}));
