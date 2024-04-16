flectra.define('web.config',function(require){
"usestrict";

constBus=require('web.Bus');

constbus=newBus();

/**
 *Thismodulecontainsallthe(mostly)static'environmental'information.
 *Thisisoftennecessarytoallowtherestofthewebclienttoproperly
 *renderitself.
 *
 *Notethatmanyinformationcurrentlystoredinsessionshouldbemovedto
 *thisfilesomeday.
 */

constmaxTouchPoints=navigator.maxTouchPoints||1;
constisAndroid=/Android/i.test(navigator.userAgent);
constisIOS=/(iPad|iPhone|iPod)/i.test(navigator.userAgent)||(navigator.platform==='MacIntel'&&maxTouchPoints>1);
constisOtherMobileDevice=/(webOS|BlackBerry|WindowsPhone)/i.test(navigator.userAgent);

varconfig={
    device:{
        /**
        *bustouseinordertobeabletohandledeviceconfigrelatedevents
        *  -'size_changed':triggeredwhenwindowsizeis
        *    correspondingtoanewbootstrapbreakpoint.Thenewsize_class
         *   isprovided.
        */
        bus:bus,
        /**
         *touchisaboolean,trueifthedevicesupportstouchinteraction
         *
         *@typeBoolean
         */
        touch:'ontouchstart'inwindow||'onmsgesturechange'inwindow,
        /**
         *size_classisaninteger:0,1,2,3or4,dependingonthe(current)
         *sizeofthedevice. Thisisadynamicproperty,updatedwheneverthe
         *browserisresized
         *
         *@typeNumber
         */
        size_class:null,
        /**
         *MobileOS(Android)devicedetectionusinguserAgent.
         *Thisflagdoesn'tdependonthesize/resolutionofthescreen.
         *
         *@returnBoolean
         */
        isAndroid:isAndroid,
        /**
         *MobileOS(iOS)devicedetectionusinguserAgent.
         *Thisflagdoesn'tdependonthesize/resolutionofthescreen.
         *
         *@returnBoolean
         */
        isIOS:isIOS,
        /**
         *Afrequentusecaseistohaveadifferentrenderin'mobile'mode,
         *meaningwhenthescreenissmall. Thisflag(boolean)istruewhen
         *thesizeisXS/VSM/SM.Itisalsoupdateddynamically.
         *
         *@typeBoolean
         */
        isMobile:null,
        /**
         *MobiledevicedetectionusinguserAgent.
         *Thisflagdoesn'tdependonthesize/resolutionofthescreen.
         *Ittargetsmobiledeviceswhichsuggeststhatthereisavirtualkeyboard.
         *
         *@return{boolean}
         */
        isMobileDevice:isAndroid||isIOS||isOtherMobileDevice,
        /**
         *Mappingbetweenthenumbers0,1,2,3,4,5,6andsomedescriptions
         */
        SIZES:{XS:0,VSM:1,SM:2,MD:3,LG:4,XL:5,XXL:6},
    },
    /**
     *Stateswhetherthecurrentenvironmentisindebugornot.
     *
     *@paramdebugModethedebugmodetocheck,emptyforsimpledebugmode
     *@returns{boolean}
     */
    isDebug:function(debugMode){
        if(debugMode){
            returnflectra.debug&&flectra.debug.indexOf(debugMode)!==-1;
        }
        returnflectra.debug;
    },
};


varmedias=[
    window.matchMedia('(max-width:474px)'),
    window.matchMedia('(min-width:475px)and(max-width:575px)'),
    window.matchMedia('(min-width:576px)and(max-width:767px)'),
    window.matchMedia('(min-width:768px)and(max-width:991px)'),
    window.matchMedia('(min-width:992px)and(max-width:1199px)'),
    window.matchMedia('(min-width:1200px)and(max-width:1533px)'),
    window.matchMedia('(min-width:1534px)'),
];

/**
 *Returnthecurrentsizeclass
 *
 *@returns{integer}anumberbetween0and5,included
 */
function_getSizeClass(){
    for(vari=0;i<medias.length;i++){
        if(medias[i].matches){
            returni;
        }
    }
}
/**
 *Updatethesizedependantpropertiesintheconfigobject. Thismethod
 *shouldbecalledeverytimethesizeclasschanges.
 */
function_updateSizeProps(){
    varsc=_getSizeClass();
    if(sc!==config.device.size_class){
        config.device.size_class=sc;
        config.device.isMobile=config.device.size_class<=config.device.SIZES.SM;
        config.device.bus.trigger('size_changed',config.device.size_class);
    }
}

_.invoke(medias,'addListener',_updateSizeProps);
_updateSizeProps();

returnconfig;

});
