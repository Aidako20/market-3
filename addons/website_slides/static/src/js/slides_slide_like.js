flectra.define('website_slides.slides.slide.like',function(require){
'usestrict';

varcore=require('web.core');
varpublicWidget=require('web.public.widget');
require('website_slides.slides');

var_t=core._t;

varSlideLikeWidget=publicWidget.Widget.extend({
    events:{
        'click.o_wslides_js_slide_like_up':'_onClickUp',
        'click.o_wslides_js_slide_like_down':'_onClickDown',
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{Object}$el
     *@param{String}message
     */
    _popoverAlert:function($el,message){
        $el.popover({
            trigger:'focus',
            placement:'bottom',
            container:'body',
            html:true,
            content:function(){
                returnmessage;
            }
        }).popover('show');
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _onClick:function(slideId,voteType){
        varself=this;
        this._rpc({
            route:'/slides/slide/like',
            params:{
                slide_id:slideId,
                upvote:voteType==='like',
            },
        }).then(function(data){
            if(!data.error){
                self.$el.find('span.o_wslides_js_slide_like_upspan').text(data.likes);
                self.$el.find('span.o_wslides_js_slide_like_downspan').text(data.dislikes);
            }else{
                if(data.error==='public_user'){
                    varmessage=_t('Please<ahref="/web/login?redirect=%s">login</a>tovotethislesson');
                    varsignupAllowed=data.error_signup_allowed||false;
                    if(signupAllowed){
                        message=_t('Please<ahref="/web/signup?redirect=%s">createanaccount</a>tovotethislesson');
                    }
                    self._popoverAlert(self.$el,_.str.sprintf(message,encodeURIComponent(document.URL)));
                }elseif(data.error==='vote_done'){
                    self._popoverAlert(self.$el,_t('Youhavealreadyvotedforthislesson'));
                }elseif(data.error==='slide_access'){
                    self._popoverAlert(self.$el,_t('Youdon\'thaveaccesstothislesson'));
                }elseif(data.error==='channel_membership_required'){
                    self._popoverAlert(self.$el,_t('Youmustbememberofthiscoursetovote'));
                }elseif(data.error==='channel_comment_disabled'){
                    self._popoverAlert(self.$el,_t('Votesandcommentsaredisabledforthiscourse'));
                }elseif(data.error==='channel_karma_required'){
                    self._popoverAlert(self.$el,_t('Youdon\'thaveenoughkarmatovote'));
                }else{
                    self._popoverAlert(self.$el,_t('Unknownerror'));
                }
            }
        });
    },

    _onClickUp:function(ev){
        varslideId=$(ev.currentTarget).data('slide-id');
        returnthis._onClick(slideId,'like');
    },

    _onClickDown:function(ev){
        varslideId=$(ev.currentTarget).data('slide-id');
        returnthis._onClick(slideId,'dislike');
    },
});

publicWidget.registry.websiteSlidesSlideLike=publicWidget.Widget.extend({
    selector:'#wrapwrap',

    /**
     *@override
     *@param{Object}parent
     */
    start:function(){
        varself=this;
        vardefs=[this._super.apply(this,arguments)];
        $('.o_wslides_js_slide_like').each(function(){
            defs.push(newSlideLikeWidget(self).attachTo($(this)));
        });
        returnPromise.all(defs);
    },
});

return{
    slideLikeWidget:SlideLikeWidget,
    websiteSlidesSlideLike:publicWidget.registry.websiteSlidesSlideLike
};

});
