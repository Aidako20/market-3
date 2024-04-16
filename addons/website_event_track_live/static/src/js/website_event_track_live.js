varonYouTubeIframeAPIReady;

flectra.define('website_event_track_live.website_event_youtube_embed',function(require){
'usestrict';

varpublicWidget=require('web.public.widget');
varTrackSuggestionWidget=require('website_event_track_live.website_event_track_suggestion');

varYOUTUBE_VIDEO_ENDED=0;
varYOUTUBE_VIDEO_PLAYING=1;
varYOUTUBE_VIDEO_PAUSED=2;

publicWidget.registry.websiteEventTrackLive=publicWidget.Widget.extend({
    selector:'.o_wevent_event_track_live',
    custom_events:_.extend({},publicWidget.Widget.prototype.custom_events,{
        'video-ended':'_onVideoEnded'
    }),

    start:function(){
        varself=this;
        returnthis._super(...arguments).then(function(){
            self._setupYoutubePlayer();
            self.isFullScreen=!!document.fullscreenElement;
        });
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    _onPlayerReady:function(){
        $(window).on('resize',this._onResize.bind(this));
        this.$('.o_wevent_event_track_live_loading').remove();
    },

    _onPlayerStateChange:function(event){
        if(event.data===YOUTUBE_VIDEO_ENDED){
            this.trigger('video-ended');
        }elseif(event.data===YOUTUBE_VIDEO_PLAYING){
            this.trigger('video-playing');
        }elseif(event.data===YOUTUBE_VIDEO_PAUSED){
            this.trigger('video-paused');
        }
    },

    _onVideoEnded:function(){
        if(this.$el.data('hasNextSuggestion')){
            //ifwehaveanupcomingsuggestion,addacoveringblocktoavoid
            //showingYoutubesuggestionswhilewefetchtheappropriatesuggestion
            //usingarpc.Thisallowsavoidinga'flicker'effect.
            this.$el.append($('<div/>',{
                class:'owevent_track_suggestion_loadingposition-absolutew-100'
            }));
        }

        varself=this;
        this._rpc({
            route:'/event_track/get_track_suggestion',
            params:{
                track_id:this.$el.data('trackId'),
            }
        }).then(function(suggestion){
            self.nextSuggestion=suggestion;
            self._showSuggestion();
        });
    },

    _onReplay:function(){
        this.youtubePlayer.seekTo(0);
        this.youtubePlayer.playVideo();
        this.$('.owevent_track_suggestion_loading').remove();
        if(this.trackSuggestion){
            deletethis.trackSuggestion;
        }
    },

    /**
     *The'fullscreenchange'eventisprobablyabetterfitbutitisunfortunately
     *nottriggeredwhenYoutubeentersfullscreenmode.
     *However,theglobalwindow'resize'is.
     */
    _onResize:function(){
        this.isFullScreen=!!document.fullscreenElement;
        this._showSuggestion();
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    _setupYoutubePlayer:function(){
        varself=this;

        varyoutubeId=self.$el.data('youtubeVideoId');
        var$youtubeElement=$('<script/>',{src:'https://www.youtube.com/iframe_api'});
        $(document.head).append($youtubeElement);

        onYouTubeIframeAPIReady=function(){
            self.youtubePlayer=newYT.Player('o_wevent_youtube_iframe_container',{
                height:'100%',
                width:'100%',
                videoId:youtubeId,
                playerVars:{
                    autoplay:1,
                    enablejsapi:1,
                    rel:0,
                    origin:window.location.origin,
                    widget_referrer:window.location.origin,
                },
                events:{
                    'onReady':self._onPlayerReady.bind(self),
                    'onStateChange':self._onPlayerStateChange.bind(self)
                }
            });
        };
    },

    /**
     *Automaticallylaunchesthenextsuggestedtrackwhenthisoneends
     *andtheuserisnotinfullscreenmode.
     */
    _showSuggestion:function(){
        if(this.nextSuggestion&&!this.isFullScreen&&!this.trackSuggestion){
            this.trackSuggestion=newTrackSuggestionWidget(this,this.nextSuggestion);
            this.trackSuggestion.appendTo(this.$el);
            this.trackSuggestion.on('replay',null,this._onReplay.bind(this));
        }
    }
});

});
