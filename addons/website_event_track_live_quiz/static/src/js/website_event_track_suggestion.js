flectra.define('website_event_track_live_quiz.website_event_track_suggestion',function(require){
'usestrict';

varWebsiteEventTrackSuggestion=require('website_event_track_live.website_event_track_suggestion');

varWebsiteEventTrackSuggestionLiveQuiz=WebsiteEventTrackSuggestion.include({
    xmlDependencies:WebsiteEventTrackSuggestion.prototype.xmlDependencies.concat([
        '/website_event_track_live_quiz/static/src/xml/website_event_track_live_templates.xml',
    ]),
    events:_.extend({},WebsiteEventTrackSuggestion.prototype.events,{
        'click.owevent_track_suggestion_quiz':'_onQuizClick'
    }),

    init:function(parent,options){
        this._super(...arguments);
        this.currentTrack.showQuiz=options.current_track.show_quiz;
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Iftheusertakesthequiz,stopthenextsuggestiontimer
     */
    _onQuizClick:function(){
        clearInterval(this.timerInterval);
        this.$('.owevent_track_suggestion_timer_text_wrapper').remove();
    }
});

returnWebsiteEventTrackSuggestionLiveQuiz;

});
