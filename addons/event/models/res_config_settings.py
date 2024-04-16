#-*-coding:utf-8-*-

fromflectraimportapi,fields,models

classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    module_event_sale=fields.Boolean("Tickets")
    module_website_event_meet=fields.Boolean("DiscussionRooms")
    module_website_event_track=fields.Boolean("TracksandAgenda")
    module_website_event_track_live=fields.Boolean("LiveMode")
    module_website_event_track_quiz=fields.Boolean("QuizonTracks")
    module_website_event_track_exhibitor=fields.Boolean("AdvancedSponsors")
    module_website_event_questions=fields.Boolean("RegistrationSurvey")
    module_event_barcode=fields.Boolean("Barcode")
    module_website_event_sale=fields.Boolean("OnlineTicketing")

    @api.onchange('module_website_event_track')
    def_onchange_module_website_event_track(self):
        """Resetsub-modules,otherwiseyoumayhavetracktoFalsebutstill
        havetrack_liveortrack_quiztoTrue,meaningtrackwillcomebackdue
        todependenciesofmodules."""
        forconfiginself:
            ifnotconfig.module_website_event_track:
                config.module_website_event_track_live=False
                config.module_website_event_track_quiz=False
                config.module_website_event_track_exhibitor=False
