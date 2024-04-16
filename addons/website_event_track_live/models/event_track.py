#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importre

fromflectraimportapi,fields,models


classTrack(models.Model):
    _inherit='event.track'

    youtube_video_url=fields.Char('YoutubeVideoURL',
        help="ConfigurethisURLsothateventattendeescanseeyourTrackinvideo!")
    youtube_video_id=fields.Char('YoutubevideoID',compute='_compute_youtube_video_id',
        help="ExtractedfromthevideoURLandusedtoinfervariouslinks(embed/thumbnail/...)")
    is_youtube_replay=fields.Boolean('IsYoutubeReplay',
        help="CheckthisoptionifthevideoisalreadyavailableonYoutubetoavoidshowing'Direct'options(Chat,...)")
    is_youtube_chat_available=fields.Boolean('IsChatAvailable',compute='_compute_is_youtube_chat_available')

    @api.depends('youtube_video_url')
    def_compute_youtube_video_id(self):
        fortrackinself:
            iftrack.youtube_video_url:
                regex=r'^.*(youtu.be\/|v\/|u\/\w\/|embed\/|live\/|watch\?v=|&v=)([^#&?]*).*'
                match=re.match(regex,track.youtube_video_url)
                ifmatchandlen(match.groups())==2andlen(match.group(2))==11:
                    track.youtube_video_id=match.group(2)

            ifnottrack.youtube_video_id:
                track.youtube_video_id=False

    @api.depends('youtube_video_id','is_youtube_replay','date_end','is_track_done')
    def_compute_website_image_url(self):
        youtube_thumbnail_tracks=self.filtered(lambdatrack:nottrack.website_imageandtrack.youtube_video_id)
        super(Track,self-youtube_thumbnail_tracks)._compute_website_image_url()
        fortrackinyoutube_thumbnail_tracks:
            track.website_image_url=f'https://img.youtube.com/vi/{track.youtube_video_id}/maxresdefault.jpg'

    @api.depends('youtube_video_url','is_youtube_replay','date','date_end','is_track_upcoming','is_track_live')
    def_compute_is_youtube_chat_available(self):
        fortrackinself:
            track.is_youtube_chat_available=track.youtube_video_urlandnottrack.is_youtube_replayand(track.is_track_soonortrack.is_track_live)
