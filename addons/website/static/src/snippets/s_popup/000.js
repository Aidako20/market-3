flectra.define('website.s_popup',function(require){
'usestrict';

constconfig=require('web.config');
constdom=require('web.dom');
constpublicWidget=require('web.public.widget');
constutils=require('web.utils');

constPopupWidget=publicWidget.Widget.extend({
    selector:'.s_popup',
    events:{
        'click.js_close_popup':'_onCloseClick',
        'hide.bs.modal':'_onHideModal',
        'show.bs.modal':'_onShowModal',
    },

    /**
     *@override
     */
    start:function(){
        this._popupAlreadyShown=!!utils.get_cookie(this.$el.attr('id'));
        if(!this._popupAlreadyShown){
            this._bindPopup();
        }
        returnthis._super(...arguments);
    },
    /**
     *@override
     */
    destroy:function(){
        this._super.apply(this,arguments);
        $(document).off('mouseleave.open_popup');
        this.$target.find('.modal').modal('hide');
        clearTimeout(this.timeout);
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _bindPopup:function(){
        const$main=this.$target.find('.modal');

        letdisplay=$main.data('display');
        letdelay=$main.data('showAfter');

        if(config.device.isMobile){
            if(display==='mouseExit'){
                display='afterDelay';
                delay=5000;
            }
            this.$('.modal').removeClass('s_popup_middle').addClass('s_popup_bottom');
        }

        if(display==='afterDelay'){
            this.timeout=setTimeout(()=>this._showPopup(),delay);
        }else{
            $(document).on('mouseleave.open_popup',()=>this._showPopup());
        }
    },
    /**
     *@private
     */
    _hidePopup:function(){
        this.$target.find('.modal').modal('hide');
    },
    /**
     *@private
     */
    _showPopup:function(){
        if(this._popupAlreadyShown){
            return;
        }
        this.$target.find('.modal').modal('show');
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _onCloseClick:function(){
        this._hidePopup();
    },
    /**
     *@private
     */
    _onHideModal:function(){
        constnbDays=this.$el.find('.modal').data('consentsDuration');
        utils.set_cookie(this.$el.attr('id'),true,nbDays*24*60*60);
        this._popupAlreadyShown=true;

        this.$target.find('.media_iframe_videoiframe').each((i,iframe)=>{
            iframe.src='';
        });
    },
    /**
     *@private
     */
    _onShowModal(){
        this.el.querySelectorAll('.media_iframe_video').forEach(media=>{
            constiframe=media.querySelector('iframe');
            iframe.src=media.dataset.oeExpression||media.dataset.src;//TODOstilloeExpressiontoremovesomeday
        });
    },
});

publicWidget.registry.popup=PopupWidget;

//Trytoupdatethescrollbarbasedonthecurrentcontext(modalstate)
//andonlyifthemodaloverflowinghaschanged

function_updateScrollbar(ev){
    constcontext=ev.data;
    constisOverflowing=dom.hasScrollableContent(context._element);
    if(context._isOverflowingWindow!==isOverflowing){
        context._isOverflowingWindow=isOverflowing;
        context._checkScrollbar();
        context._setScrollbar();
        if(isOverflowing){
            document.body.classList.add('modal-open');
        }else{
            document.body.classList.remove('modal-open');
            context._resetScrollbar();
        }
    }
}

//Preventbootstraptopreventscrollingandtoaddthestrangebody
//padding-righttheyaddifthepopupdoesnotuseabackdrop(especially
//importantfordefaultcookiebar).

const_baseShowElement=$.fn.modal.Constructor.prototype._showElement;
$.fn.modal.Constructor.prototype._showElement=function(){
    _baseShowElement.apply(this,arguments);

    if(this._element.classList.contains('s_popup_no_backdrop')){
        //Updatethescrollbarifthecontentchangesorifthewindowhasbeen
        //resized.Notethiscouldtechnicallybedoneforallmodalsandnot
        //onlytheoneswiththes_popup_no_backdropclassbutthatwouldbe
        //uselessasallowingcontentscrollwhileamodalwiththatclassis
        //openedisaveryspecificFlectrabehavior.
        $(this._element).on('content_changed.update_scrollbar',this,_updateScrollbar);
        $(window).on('resize.update_scrollbar',this,_updateScrollbar);

        this._flectraLoadEventCaptureHandler=_.debounce(()=>_updateScrollbar({data:this},100));
        this._element.addEventListener('load',this._flectraLoadEventCaptureHandler,true);

        _updateScrollbar({data:this});
    }
};

const_baseHideModal=$.fn.modal.Constructor.prototype._hideModal;
$.fn.modal.Constructor.prototype._hideModal=function(){
    _baseHideModal.apply(this,arguments);

    //Note:dothisinallcases,notonlyforpopupwiththe
    //s_popup_no_backdropclass,asthemodalmayhavelostthatclassduring
    //editionbeforebeingclosed.
    this._element.classList.remove('s_popup_overflow_page');

    $(this._element).off('content_changed.update_scrollbar');
    $(window).off('resize.update_scrollbar');

    if(this._flectraLoadEventCaptureHandler){
        this._element.removeEventListener('load',this._flectraLoadEventCaptureHandler,true);
        deletethis._flectraLoadEventCaptureHandler;
    }
};

const_baseSetScrollbar=$.fn.modal.Constructor.prototype._setScrollbar;
$.fn.modal.Constructor.prototype._setScrollbar=function(){
    if(this._element.classList.contains('s_popup_no_backdrop')){
        this._element.classList.toggle('s_popup_overflow_page',!!this._isOverflowingWindow);

        if(!this._isOverflowingWindow){
            return;
        }
    }
    return_baseSetScrollbar.apply(this,arguments);
};

const_baseGetScrollbarWidth=$.fn.modal.Constructor.prototype._getScrollbarWidth;
$.fn.modal.Constructor.prototype._getScrollbarWidth=function(){
    if(this._element.classList.contains('s_popup_no_backdrop')&&!this._isOverflowingWindow){
        return0;
    }
    return_baseGetScrollbarWidth.apply(this,arguments);
};

returnPopupWidget;
});
