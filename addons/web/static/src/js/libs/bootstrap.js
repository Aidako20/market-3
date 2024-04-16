flectra.define('web.bootstrap.extensions',function(){
'usestrict';

/**
 *Thebootstraplibraryextensionsandfixesshouldbedoneheretoavoid
 *patchinginplace.
 */

/**
 *ReviewBootstrapSanitization:leaveitenabledbydefaultbutextenditto
 *acceptmorecommontagnamesliketablesandbuttons,andcommonattributes
 *suchasstyleordata-.Ifaspecifictooltiporpopovermustacceptcustom
 *tagsorattributes,theymustbesuppliedthroughthewhitelistBS
 *parameterexplicitely.
 *
 *Wecannotdisablesanitizationbecausebootstrapusestooltip/popover
 *DOMattributesinan"unsafe"way.
 */
varbsSanitizeWhiteList=$.fn.tooltip.Constructor.Default.whiteList;

bsSanitizeWhiteList['*'].push('title','style',/^data-[\w-]+/);

bsSanitizeWhiteList.header=[];
bsSanitizeWhiteList.main=[];
bsSanitizeWhiteList.footer=[];

bsSanitizeWhiteList.caption=[];
bsSanitizeWhiteList.col=['span'];
bsSanitizeWhiteList.colgroup=['span'];
bsSanitizeWhiteList.table=[];
bsSanitizeWhiteList.thead=[];
bsSanitizeWhiteList.tbody=[];
bsSanitizeWhiteList.tfooter=[];
bsSanitizeWhiteList.tr=[];
bsSanitizeWhiteList.th=['colspan','rowspan'];
bsSanitizeWhiteList.td=['colspan','rowspan'];

bsSanitizeWhiteList.address=[];
bsSanitizeWhiteList.article=[];
bsSanitizeWhiteList.aside=[];
bsSanitizeWhiteList.blockquote=[];
bsSanitizeWhiteList.section=[];

bsSanitizeWhiteList.button=['type'];
bsSanitizeWhiteList.del=[];

/**
 *Returnsanextendedversionofbootstrapdefaultwhitelistforsanitization,
 *i.e.aversionwhere,foreachkey,theoriginalvalueisconcatenedwiththe
 *receivedversion'svalueandwherethereceivedversion'sextrakey/values
 *areadded.
 *
 *Note:thereturnedversion
 *
 *@param{Object}extensions
 *@returns{Object}/!\thereturnedwhitelistismadefroma*shallow*copyof
 *     thedefaultwhitelist,extendedwithgivenwhitelist.
 */
functionmakeExtendedSanitizeWhiteList(extensions){
    varwhiteList=_.clone($.fn.tooltip.Constructor.Default.whiteList);
    Object.keys(extensions).forEach(key=>{
        whiteList[key]=(whiteList[key]||[]).concat(extensions[key]);
    });
    returnwhiteList;
}

/*Bootstraptooltipdefaultsoverwrite*/
$.fn.tooltip.Constructor.Default.placement='auto';
$.fn.tooltip.Constructor.Default.fallbackPlacement=['bottom','right','left','top'];
$.fn.tooltip.Constructor.Default.html=true;
$.fn.tooltip.Constructor.Default.trigger='hover';
$.fn.tooltip.Constructor.Default.container='body';
$.fn.tooltip.Constructor.Default.boundary='window';
$.fn.tooltip.Constructor.Default.delay={show:1000,hide:0};

varbootstrapShowFunction=$.fn.tooltip.Constructor.prototype.show;
$.fn.tooltip.Constructor.prototype.show=function(){
    //Overwritebootstraptooltipmethodtopreventshowing2tooltipatthe
    //sametime
    $('.tooltip').remove();

    returnbootstrapShowFunction.call(this);
};

/*Bootstrapscrollspyfixfornon-bodytospy*/

constbootstrapSpyRefreshFunction=$.fn.scrollspy.Constructor.prototype.refresh;
$.fn.scrollspy.Constructor.prototype.refresh=function(){
    bootstrapSpyRefreshFunction.apply(this,arguments);
    if(this._scrollElement===window||this._config.method!=='offset'){
        return;
    }
    constbaseScrollTop=this._getScrollTop();
    for(leti=0;i<this._offsets.length;i++){
        this._offsets[i]+=baseScrollTop;
    }
};

/**
 *Insomecases,weneedtokeepthefirstelementofnavbarsselected.
 */
constbootstrapSpyProcessFunction=$.fn.scrollspy.Constructor.prototype._process;
$.fn.scrollspy.Constructor.prototype._process=function(){
    bootstrapSpyProcessFunction.apply(this,arguments);
    if(this._activeTarget===null&&this._config.alwaysKeepFirstActive){
        this._activate(this._targets[0]);
    }
};

/*Bootstrapmodalscrollbarcompensationonnon-body*/
constbsSetScrollbarFunction=$.fn.modal.Constructor.prototype._setScrollbar;
$.fn.modal.Constructor.prototype._setScrollbar=function(){
    const$scrollable=$().getScrollingElement();
    if(document.body.contains($scrollable[0])){
        $scrollable.compensateScrollbar(true);
    }
    returnbsSetScrollbarFunction.apply(this,arguments);
};
constbsResetScrollbarFunction=$.fn.modal.Constructor.prototype._resetScrollbar;
$.fn.modal.Constructor.prototype._resetScrollbar=function(){
    const$scrollable=$().getScrollingElement();
    if(document.body.contains($scrollable[0])){
        $scrollable.compensateScrollbar(false);
    }
    returnbsResetScrollbarFunction.apply(this,arguments);
};

return{
    makeExtendedSanitizeWhiteList:makeExtendedSanitizeWhiteList,
};
});
