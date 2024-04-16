#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classEventMenu(models.Model):
    _inherit="website.event.menu"

    menu_type=fields.Selection(
        selection_add=[('track','EventTracksMenus'),('track_proposal','EventProposalsMenus')],
        ondelete={'track':'cascade','track_proposal':'cascade'})
