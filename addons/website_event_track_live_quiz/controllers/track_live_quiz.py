#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.website_event_track_live.controllers.track_liveimportEventTrackLiveController


classEventTrackLiveQuizController(EventTrackLiveController):

    def_prepare_track_suggestion_values(self,track,track_suggestion):
        res=super(EventTrackLiveQuizController,self)._prepare_track_suggestion_values(track,track_suggestion)
        res['current_track']['show_quiz']=bool(track.quiz_id)andnottrack.is_quiz_completed
        returnres
