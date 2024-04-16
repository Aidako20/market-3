#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classEventMenu(models.Model):
    _inherit="website.event.menu"

    menu_type=fields.Selection(
        selection_add=[("meeting_room","EventMeetingRoomMenus")],
        ondelete={'meeting_room':'cascade'})
