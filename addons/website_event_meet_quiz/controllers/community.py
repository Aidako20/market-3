#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromwerkzeug.exceptionsimportForbidden

fromflectraimporthttp
fromflectra.addons.website_event.controllers.communityimportEventCommunityController
fromflectra.httpimportrequest


classWebsiteEventTrackQuizMeetController(EventCommunityController):

    @http.route(['/event/<model("event.event"):event>/community'],type='http',auth="public",website=True,sitemap=False)
    defcommunity(self,event,page=1,lang=None,**kwargs):
        ifnotevent.can_access_from_current_website():
            raiseForbidden()

        #website_event_track_quiz
        values=self._get_community_leaderboard_render_values(event,kwargs.get('search'),page)

        #website_event_meet
        values.update(self._event_meeting_rooms_get_values(event,lang=lang))
        returnrequest.render('website_event_meet.event_meet',values)
