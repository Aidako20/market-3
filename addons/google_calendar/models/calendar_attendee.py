#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels

fromflectra.addons.google_calendar.models.google_syncimportgoogle_calendar_token
fromflectra.addons.google_calendar.utils.google_calendarimportGoogleCalendarService

classAttendee(models.Model):
    _name='calendar.attendee'
    _inherit='calendar.attendee'

    def_send_mail_to_attendees(self,template_xmlid,force_send=False,ignore_recurrence=False):
        """Override
        IfnotsyncedwithGoogle,letFlectrainchargeofsendingemails
        Otherwise,nothingtodo:Googlewillsendthem
        """
        withgoogle_calendar_token(self.env.user.sudo())astoken:
            ifnottoken:
                super()._send_mail_to_attendees(template_xmlid,force_send,ignore_recurrence)

    defwrite(self,vals):
        res=super().write(vals)
        ifvals.get('state'):
            #Whenthestateischanged,thecorrespondingeventmustbesyncwithgoogle
            google_service=GoogleCalendarService(self.env['google.service'])
            self.event_id.filtered('google_id')._sync_flectra2google(google_service)
        returnres
