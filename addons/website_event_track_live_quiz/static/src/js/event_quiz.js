flectra.define('website_event_track_live_quiz.event_quiz',function(require){
'usestrict';

varQuiz=require('website_event_track_quiz.event.quiz');

varWebsiteEventTrackSuggestionQuiz=Quiz.include({
    xmlDependencies:Quiz.prototype.xmlDependencies.concat([
        '/website_event_track_live_quiz/static/src/xml/website_event_track_quiz_templates.xml',
    ]),

    /**
     *@override
     */
    willStart:function(){
        returnPromise.all([
            this._super(...arguments),
            this._getTrackSuggestion()
        ]);
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    _submitQuiz:function(){
        varself=this;
        returnthis._super(...arguments).then(function(data){
            if(data.quiz_completed){
                self.$('.o_quiz_js_quiz_next_track')
                    .removeClass('btn-light')
                    .addClass('btn-secondary');
            }

            returnPromise.resolve(data);
        });
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    _getTrackSuggestion:function(){
        varself=this;
        returnthis._rpc({
            route:'/event_track/get_track_suggestion',
            params:{
                track_id:this.track.id,
            }
        }).then(function(suggestion){
            self.nextSuggestion=suggestion;
            returnPromise.resolve();
        });
    }
});

returnWebsiteEventTrackSuggestionQuiz;

});
