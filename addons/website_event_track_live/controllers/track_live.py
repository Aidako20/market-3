#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporthttp

fromflectra.addons.website_event_track.controllers.event_trackimportEventTrackController


classEventTrackLiveController(EventTrackController):

    @http.route('/event_track/get_track_suggestion',type='json',auth='public',website=True)
    defget_next_track_suggestion(self,track_id):
        track=self._fetch_track(track_id)
        track_suggestion=track._get_track_suggestions(
            restrict_domain=[('youtube_video_url','!=',False),('is_published','=',True)],
            limit=1)
        ifnottrack_suggestion:
            returnFalse
        track_suggestion_sudo=track_suggestion.sudo()
        track_sudo=track.sudo()
        returnself._prepare_track_suggestion_values(track_sudo,track_suggestion_sudo)

    def_prepare_track_suggestion_values(self,track,track_suggestion):
        return{
            'current_track':{
                'name':track.name,
                'website_image_url':track.website_image_url,
            },
            'suggestion':{
                'id':track_suggestion.id,
                'name':track_suggestion.name,
                'speaker_name':track_suggestion.partner_name,
                'website_url':track_suggestion.website_url
            }
        }
