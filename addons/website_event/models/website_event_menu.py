#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classEventMenu(models.Model):
    _name="website.event.menu"
    _description="WebsiteEventMenu"

    menu_id=fields.Many2one('website.menu',string='Menu',ondelete='cascade')
    event_id=fields.Many2one('event.event',string='Event',ondelete='cascade')
    menu_type=fields.Selection([
        ('community','CommunityMenu')],string="MenuType",
        ondelete={'community':'cascade'},required=True)
