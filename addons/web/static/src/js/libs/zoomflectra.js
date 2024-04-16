flectra.define('web.zoomflectra',function(require){
'usestrict';

/**
    ThiscodehasbeenmorethatwidelyinspiredbyeasyZoomlibrary.

    Copyright2013MattHinchliffe

    Permissionisherebygranted,freeofcharge,toanypersonobtaining
    acopyofthissoftwareandassociateddocumentationfiles(the
    "Software"),todealintheSoftwarewithoutrestriction,including
    withoutlimitationtherightstouse,copy,modify,merge,publish,
    distribute,sublicense,and/orsellcopiesoftheSoftware,andto
    permitpersonstowhomtheSoftwareisfurnishedtodoso,subjectto
    thefollowingconditions:

    Theabovecopyrightnoticeandthispermissionnoticeshallbe
    includedinallcopiesorsubstantialportionsoftheSoftware.
**/

vardw,dh,rw,rh,lx,ly;

vardefaults={

    //AttributetoretrievethezoomimageURLfrom.
    linkTag:'a',
    linkAttribute:'data-zoom-image',

    //eventtotriggerzoom
    event:'click',//ormouseenter

    //Timerbeforetriggerzoom
    timer:0,

    //Preventclicksonthezoomimagelink.
    preventClicks:true,

    //disableonmobile
    disabledOnMobile:true,

    //Callbackfunctiontoexecutebeforetheflyoutisdisplayed.
    beforeShow:$.noop,

    //Callbackfunctiontoexecutebeforetheflyoutisremoved.
    beforeHide:$.noop,

    //Callbackfunctiontoexecutewhentheflyoutisdisplayed.
    onShow:$.noop,

    //Callbackfunctiontoexecutewhentheflyoutisremoved.
    onHide:$.noop,

    //Callbackfunctiontoexecutewhenthecursorismovedwhileovertheimage.
    onMove:$.noop,

    //Callbackfunctiontoexecutewhentheflyoutisattachedtothetarget.
    beforeAttach:$.noop

};

/**
 *ZoomFlectra
 *@constructor
 *@param{Object}target
 *@param{Object}options(Optional)
 */
functionZoomFlectra(target,options){
    this.$target=$(target);
    this.opts=$.extend({},defaults,options,this.$target.data());

    if(this.isOpen===undefined){
        this._init();
    }
}

/**
 *Init
 *@private
 */
ZoomFlectra.prototype._init=function(){
    if(window.outerWidth>467||!this.opts.disabledOnMobile){
        this.$link =this.$target.find(this.opts.linkTag).length&&this.$target.find(this.opts.linkTag)||this.$target;
        this.$image =this.$target.find('img').length&&this.$target.find('img')||this.$target;
        this.$flyout=$('<divclass="zoomflectra-flyout"/>');

        var$attach=this.$target;
        if(this.opts.attach!==undefined&&this.$target.closest(this.opts.attach).length){
            $attach=this.$target.closest(this.opts.attach);
        }
        $attach.parent().on('mousemove.zoomflectratouchmove.zoomflectra',$.proxy(this._onMove,this));
        $attach.parent().on('mouseleave.zoomflectratouchend.zoomflectra',$.proxy(this._onLeave,this));
        this.$target.on(this.opts.event+'.zoomflectratouchstart.zoomflectra',$.proxy(this._onEnter,this));

        if(this.opts.preventClicks){
            this.$target.on('click.zoomflectra',function(e){e.preventDefault();});
        }else{
            varself=this;
            this.$target.on('click.zoomflectra',function(){self.hide();self.$target.unbind();});
        }
    }
};

/**
 *Show
 *@param{MouseEvent|TouchEvent}e
 *@param{Boolean}testMouseOver(Optional)
 */
ZoomFlectra.prototype.show=function(e,testMouseOver){
    varw1,h1,w2,h2;
    varself=this;

    if(this.opts.beforeShow.call(this)===false)return;

    if(!this.isReady){
        returnthis._loadImage(this.$link.attr(this.opts.linkAttribute),function(){
            if(self.isMouseOver||!testMouseOver){
                self.show(e);
            }
        });
    }

    var$attach=this.$target;
    if(this.opts.attach!==undefined&&this.$target.closest(this.opts.attach).length){
        $attach=this.$target.closest(this.opts.attach);
    }

    //Preventshavingmultiplezoomflyouts
    $attach.parent().find('.zoomflectra-flyout').remove();
    this.$flyout.removeAttr('style');
    $attach.parent().append(this.$flyout);

    if(this.opts.attachToTarget){
        this.opts.beforeAttach.call(this);

        //Besurethattheflyoutisattop0,left0toensurecorrectcomputation
        //e.g.employeeskanbanondashboard
        this.$flyout.css('position','fixed');
        varflyoutOffset=this.$flyout.offset();
        if(flyoutOffset.left>0){
            varflyoutLeft=parseFloat(this.$flyout.css('left').replace('px',''));
            this.$flyout.css('left',flyoutLeft-flyoutOffset.left+'px');
        }
        if(flyoutOffset.top>0){
            varflyoutTop=parseFloat(this.$flyout.css('top').replace('px',''));
            this.$flyout.css('top',flyoutTop-flyoutOffset.top+'px');
        }

        if(this.$zoom.height()<this.$flyout.height()){
             this.$flyout.css('height',this.$zoom.height()+'px');
        }
        if(this.$zoom.width()<this.$flyout.width()){
             this.$flyout.css('width',this.$zoom.width()+'px');
        }

        varoffset=this.$target.offset();
        varleft=offset.left-this.$flyout.width();
        vartop=offset.top;

        //Positionthezoomontherightsideofthetarget
        //ifthere'snotenoughroomontheleft
        if(left<0){
            if(offset.left<($(document).width()/2)){
                left=offset.left+this.$target.width();
            }else{
                left=0;
            }
        }

        //Preventstheflyouttooverflow
        if(left+this.$flyout.width()>$(document).width()){
            this.$flyout.css('width', $(document).width()-left+'px');
        }elseif(left===0){//Limitthemaxwidthifdisplayedontheleft
            this.$flyout.css('width',offset.left+'px');
        }

        //Preventsthezoomtobedisplayedoutsidethecurrentviewport
        if((top+this.$flyout.height())>$(document).height()){
            top=$(document).height()-this.$flyout.height();
        }

        this.$flyout.css('transform','translate3d('+left+'px,'+top+'px,0px)');
    }else{
        //Computingflyoutmax-widthdependingtotheavailablespaceontherighttoavoidoverflow-xissues
        //e.g.widthtoohighsoarightzoomedelementisnotvisible(needtoscrollonxaxis)
        varrightAvailableSpace=document.body.clientWidth-this.$flyout[0].getBoundingClientRect().left;
        this.$flyout.css('max-width',rightAvailableSpace);
    }

    w1=this.$target[0].offsetWidth;
    h1=this.$target[0].offsetHeight;

    w2=this.$flyout.width();
    h2=this.$flyout.height();

    dw=this.$zoom.width()-w2;
    dh=this.$zoom.height()-h2;

    //Forthecasewherethezoomimageisactuallysmallerthan
    //theflyout.
    if(dw<0)dw=0;
    if(dh<0)dh=0;

    rw=dw/w1;
    rh=dh/h1;

    this.isOpen=true;

    this.opts.onShow.call(this);

    if(e){
        this._move(e);
    }
};

/**
 *Onenter
 *@private
 *@param{Event}e
 */
ZoomFlectra.prototype._onEnter=function(e){
    varself=this;
    vartouches=e.originalEvent.touches;
    e.preventDefault();
    this.isMouseOver=true;

    setTimeout(function(){
        if(self.isMouseOver&&(!touches||touches.length===1)){
            self.show(e,true);
        }
      },this.opts.timer);

};

/**
 *Onmove
 *@private
 *@param{Event}e
 */
ZoomFlectra.prototype._onMove=function(e){
    if(!this.isOpen)return;

    e.preventDefault();
    this._move(e);
};

/**
 *Onleave
 *@private
 */
ZoomFlectra.prototype._onLeave=function(){
    this.isMouseOver=false;
    if(this.isOpen){
        this.hide();
    }
};

/**
 *Onload
 *@private
 *@param{Event}e
 */
ZoomFlectra.prototype._onLoad=function(e){
    //IEmayfirealoadeventevenonerrorsotesttheimagedimensions
    if(!e.currentTarget.width)return;

    this.isReady=true;

    this.$flyout.html(this.$zoom);

    if(e.data.call){
        e.data();
    }
};

/**
 *Loadimage
 *@private
 *@param{String}href
 *@param{Function}callback
 */
ZoomFlectra.prototype._loadImage=function(href,callback){
    varzoom=newImage();

    this.$zoom=$(zoom).on('load',callback,$.proxy(this._onLoad,this));

    zoom.style.position='absolute';
    zoom.src=href;
};

/**
 *Move
 *@private
 *@param{Event}e
 */
ZoomFlectra.prototype._move=function(e){
    if(e.type.indexOf('touch')===0){
        vartouchlist=e.touches||e.originalEvent.touches;
        lx=touchlist[0].pageX;
        ly=touchlist[0].pageY;
    }else{
        lx=e.pageX||lx;
        ly=e.pageY||ly;
    }

    varoffset =this.$target.offset();
    varpt=ly-offset.top;
    varpl=lx-offset.left;
    varxt=Math.ceil(pt*rh);
    varxl=Math.ceil(pl*rw);

    //Closeifoutside
    if(!this.opts.attachToTarget&&(xl<0||xt<0||xl>dw||xt>dh||lx>(offset.left+this.$target.outerWidth()))){
        this.hide();
    }else{
        vartop=xt*-1;
        varleft=xl*-1;

        this.$zoom.css({
            top:top,
            left:left
        });

        this.opts.onMove.call(this,top,left);
    }

};

/**
 *Hide
 */
ZoomFlectra.prototype.hide=function(){
    if(!this.isOpen)return;
    if(this.opts.beforeHide.call(this)===false)return;

    this.$flyout.detach();
    this.isOpen=false;

    this.opts.onHide.call(this);
};

//jQuerypluginwrapper
$.fn.zoomFlectra=function(options){
    returnthis.each(function(){
        varapi=$.data(this,'zoomFlectra');

        if(!api){
            $.data(this,'zoomFlectra',newZoomFlectra(this,options));
        }elseif(api.isOpen===undefined){
            api._init();
        }
    });
};
});
