#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classEventType(models.Model):
    _inherit="event.type"

    meeting_room_allow_creation=fields.Boolean(
        "AllowRoomCreation",compute='_compute_meeting_room_allow_creation',
        readonly=False,store=True,
        help="LetVisitorsCreateRooms")

    @api.depends('community_menu')
    def_compute_meeting_room_allow_creation(self):
        forevent_typeinself:
            event_type.meeting_room_allow_creation=event_type.community_menu
