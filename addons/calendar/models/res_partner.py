#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime

fromflectraimportapi,fields,models


classPartner(models.Model):
    _inherit='res.partner'

    calendar_last_notif_ack=fields.Datetime(
        'LastnotificationmarkedasreadfrombaseCalendar',default=fields.Datetime.now)

    defget_attendee_detail(self,meeting_id):
        """Returnalistoftuple(id,name,status)
            Usedbybase_calendar.js:Many2ManyAttendee
        """
        datas=[]
        meeting=None
        ifmeeting_id:
            meeting=self.env['calendar.event'].browse(meeting_id)

        forpartnerinself:
            data=partner.name_get()[0]
            data=[data[0],data[1],False,partner.color]
            ifmeeting:
                forattendeeinmeeting.attendee_ids:
                    ifattendee.partner_id.id==partner.id:
                        data[2]=attendee.state
            datas.append(data)
        returndatas

    @api.model
    def_set_calendar_last_notif_ack(self):
        partner=self.env['res.users'].browse(self.env.context.get('uid',self.env.uid)).partner_id
        partner.write({'calendar_last_notif_ack':datetime.now()})
