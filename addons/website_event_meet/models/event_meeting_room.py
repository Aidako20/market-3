#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importdatetime

fromflectraimportapi,fields,models
fromflectra.addons.http_routing.models.ir_httpimportslug


classEventMeetingRoom(models.Model):
    _name="event.meeting.room"
    _description="EventMeetingRoom"
    _order="is_pinnedDESC,id"
    _inherit=[
        'chat.room.mixin',
        'website.published.mixin',
    ]

    _DELAY_CLEAN=datetime.timedelta(hours=4)

    name=fields.Char("Topic",required=True,translate=True)
    active=fields.Boolean('Active',default=True)
    is_published=fields.Boolean(copy=True) #maketheinheritedfieldcopyable
    event_id=fields.Many2one("event.event",string="Event",required=True,ondelete="cascade")
    is_pinned=fields.Boolean("IsPinned")
    chat_room_id=fields.Many2one("chat.room",required=True,ondelete="restrict")
    summary=fields.Char("Summary",translate=True)
    target_audience=fields.Char("Audience",translate=True)

    @api.depends('name','event_id.name')
    def_compute_website_url(self):
        super(EventMeetingRoom,self)._compute_website_url()
        formeeting_roominself:
            ifmeeting_room.id:
                base_url=meeting_room.event_id.get_base_url()
                meeting_room.website_url='%s/event/%s/meeting_room/%s'%(base_url,slug(meeting_room.event_id),slug(meeting_room))

    @api.model_create_multi
    defcreate(self,values_list):
        forvaluesinvalues_list:
            ifnotvalues.get("chat_room_id")andnotvalues.get('room_name'):
                values['room_name']='flectra-room-%s'%(values['name'])
        returnsuper(EventMeetingRoom,self).create(values_list)

    @api.autovacuum
    def_archive_meeting_rooms(self):
        """Archiveallnon-pinnedroomwith0participantifnobodyhasjoineditforamoment."""
        self.sudo().search([
            ("is_pinned","=",False),
            ("active","=",True),
            ("room_participant_count","=",0),
            ("room_last_activity","<",fields.Datetime.now()-self._DELAY_CLEAN),
        ]).active=False
