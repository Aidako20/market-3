flectra.define('website_slides.slides',function(require){
'usestrict';

varpublicWidget=require('web.public.widget');
vartime=require('web.time');

publicWidget.registry.websiteSlides=publicWidget.Widget.extend({
    selector:'#wrapwrap',

    /**
     *@override
     *@param{Object}parent
     */
    start:function(parent){
        vardefs=[this._super.apply(this,arguments)];

        _.each($("timeago.timeago"),function(el){
            vardatetime=$(el).attr('datetime');
            vardatetimeObj=time.str_to_datetime(datetime);
            //ifpresentation7days,24hours,60min,60second,1000millisold(oneweek)
            //thenreturnfixformatestringelsetimeago
            vardisplayStr='';
            if(datetimeObj&&newDate().getTime()-datetimeObj.getTime()>7*24*60*60*1000){
                displayStr=moment(datetimeObj).format('ll');
            }else{
                displayStr=moment(datetimeObj).fromNow();
            }
            $(el).text(displayStr);
        });

        returnPromise.all(defs);
    },
});

returnpublicWidget.registry.websiteSlides;

});

//==============================================================================

flectra.define('website_slides.slides_embed',function(require){
'usestrict';

varpublicWidget=require('web.public.widget');
require('website_slides.slides');

varSlideSocialEmbed=publicWidget.Widget.extend({
    events:{
        'changeinput':'_onChangePage',
    },
    /**
     *@constructor
     *@param{Object}parent
     *@param{Number}maxPage
     */
    init:function(parent,maxPage){
        this._super.apply(this,arguments);
        this.max_page=maxPage||false;
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{Number}page
     */
    _updateEmbeddedCode:function(page){
        var$embedInput=this.$('.slide_embed_code');
        varnewCode=$embedInput.val().replace(/(page=).*?([^\d]+)/,'$1'+page+'$2');
        $embedInput.val(newCode);
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{Object}ev
     */
    _onChangePage:function(ev){
        ev.preventDefault();
        varinput=this.$('input');
        varpage=parseInt(input.val());
        if(this.max_page&&!(page>0&&page<=this.max_page)){
            page=1;
        }
        this._updateEmbeddedCode(page);
    },
});

publicWidget.registry.websiteSlidesEmbed=publicWidget.Widget.extend({
    selector:'#wrapwrap',

    /**
     *@override
     *@param{Object}parent
     */
    start:function(parent){
        vardefs=[this._super.apply(this,arguments)];
        $('iframe.o_wslides_iframe_viewer').on('ready',this._onIframeViewerReady.bind(this));
        returnPromise.all(defs);
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{Event}ev
     */
    _onIframeViewerReady:function(ev){
        //TODO:makeitwork.Fornow,oncetheiframeisloaded,thevalueof#page_countis
        //stillnowset(thepdfisstillloading)
        var$iframe=$(ev.currentTarget);
        varmaxPage=$iframe.contents().find('#page_count').val();
        newSlideSocialEmbed(this,maxPage).attachTo($('.oe_slide_js_embed_code_widget'));
    },
});

});
