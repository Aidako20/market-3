#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

frombabel.datesimportformat_datetime

fromflectraimport_
fromflectra.httpimportrequest
fromflectra.addons.website_event.controllers.mainimportWebsiteEventController


classWebsiteEventController(WebsiteEventController):
    def_prepare_event_register_values(self,event,**post):
        values=super(WebsiteEventController,self)._prepare_event_register_values(event,**post)

        if"from_room_id"inpostandnotevent.is_ongoing:
            meeting_room=request.env["event.meeting.room"].browse(int(post["from_room_id"])).sudo().exists()
            ifmeeting_roomandmeeting_room.is_published:
                date_begin=format_datetime(event.with_context(tz=event.date_tz).date_begin,format="medium")

                values["toast_message"]=(
                    _('Theevent%sstartson%s(%s).\nJoinustheretochatabout"%s"!')
                    %(event.name,date_begin,event.date_tz,meeting_room.name)
                )

        returnvalues
