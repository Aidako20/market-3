#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importre

fromflectra.addons.website_event_track.controllers.event_trackimportEventTrackController
fromflectra.httpimportrequest


classWebsiteEventSessionLiveController(EventTrackController):

    def_event_track_page_get_values(self,event,track,**options):
        if'widescreen'notinoptions:
            options['widescreen']=track.youtube_video_urland(track.is_youtube_replayortrack.is_track_soonortrack.is_track_liveortrack.is_track_done)
        values=super(WebsiteEventSessionLiveController,self)._event_track_page_get_values(event,track,**options)
        #Youtubedisablesthechatembedonallmobiledevices
        #Thisregexisanaiveattemptatmatchingtheirbehavior(shouldworkformostcases)
        values['is_mobile_chat_disabled']=bool(re.match(
            r'^.*(Android|iPad|iPhone).*',
            request.httprequest.headers.get('User-Agent',request.httprequest.headers.get('user-agent',''))))
        returnvalues
