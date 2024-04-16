#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classEventType(models.Model):
    _inherit='event.type'

    website_track=fields.Boolean(
        string='TracksonWebsite',compute='_compute_website_menu_data',
        readonly=False,store=True)
    website_track_proposal=fields.Boolean(
        string='TracksProposalsonWebsite',compute='_compute_website_menu_data',
        readonly=False,store=True)

    @api.depends('website_menu')
    def_compute_website_menu_data(self):
        """Simplyactivateorde-activateallmenusatonce."""
        forevent_typeinself:
            event_type.website_track=event_type.website_menu
            event_type.website_track_proposal=event_type.website_menu
