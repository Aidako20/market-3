#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classEvent(models.Model):
    _inherit="event.event"

    meeting_room_ids=fields.One2many("event.meeting.room","event_id",string="Meetingrooms")
    meeting_room_count=fields.Integer("Roomcount",compute="_compute_meeting_room_count")
    meeting_room_allow_creation=fields.Boolean(
        "AllowRoomCreation",compute="_compute_meeting_room_allow_creation",
        readonly=False,store=True,
        help="LetVisitorsCreateRooms")

    @api.depends("event_type_id","website_menu","community_menu")
    def_compute_community_menu(self):
        """Attypeonchange:synchronize.Atwebsite_menuupdate:synchronize."""
        foreventinself:
            ifevent.event_type_idandevent.event_type_id!=event._origin.event_type_id:
                event.community_menu=event.event_type_id.community_menu
            elifevent.website_menuand(event.website_menu!=event._origin.website_menuornotevent.community_menu):
                event.community_menu=True
            elifnotevent.website_menu:
                event.community_menu=False

    @api.depends("meeting_room_ids")
    def_compute_meeting_room_count(self):
        meeting_room_count=self.env["event.meeting.room"].sudo().read_group(
            domain=[("event_id","in",self.ids)],
            fields=["id:count"],
            groupby=["event_id"],
        )

        meeting_room_count={
            result["event_id"][0]:result["event_id_count"]
            forresultinmeeting_room_count
        }

        foreventinself:
            event.meeting_room_count=meeting_room_count.get(event.id,0)

    @api.depends("event_type_id","community_menu","meeting_room_allow_creation")
    def_compute_meeting_room_allow_creation(self):
        foreventinself:
            ifevent.event_type_idandevent.event_type_id!=event._origin.event_type_id:
                event.meeting_room_allow_creation=event.event_type_id.meeting_room_allow_creation
            elifevent.community_menuandevent.community_menu!=event._origin.community_menu:
                event.meeting_room_allow_creation=True
            elifnotevent.community_menuornotevent.meeting_room_allow_creation:
                event.meeting_room_allow_creation=False
