#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels

fromflectra.addons.microsoft_calendar.models.microsoft_syncimportmicrosoft_calendar_token
fromflectra.addons.microsoft_calendar.utils.microsoft_calendarimportMicrosoftCalendarService


classAttendee(models.Model):
    _name='calendar.attendee'
    _inherit='calendar.attendee'

    def_send_mail_to_attendees(self,template_xmlid,force_send=False,ignore_recurrence=False):
        """Overridethesupermethod
        IfnotsyncedwithMicrosoftOutlook,letFlectrainchargeofsendingemails
        Otherwise,MicrosoftOutlookwillsendthem
        """
        withmicrosoft_calendar_token(self.env.user.sudo())astoken:
            ifnottoken:
                super()._send_mail_to_attendees(template_xmlid,force_send,ignore_recurrence)

    defdo_tentative(self):
        #Synchronizeeventafterstatechange
        res=super().do_tentative()
        self._microsoft_sync_event('tentativelyAccept')
        returnres

    defdo_accept(self):
        #Synchronizeeventafterstatechange
        res=super().do_accept()
        self._microsoft_sync_event('accept')
        returnres

    defdo_decline(self):
        #Synchronizeeventafterstatechange
        res=super().do_decline()
        self._microsoft_sync_event('decline')
        returnres

    def_microsoft_sync_event(self,answer):
        params={"comment":"","sendResponse":True}
        #Microsoftpreventusertoanswerthemeetingwhentheyaretheorganizer
        linked_events=self.event_id._get_synced_events()
        foreventinlinked_events.filtered(lambdae:e.user_id!=self.env.user):
            event._microsoft_patch(
                event._get_organizer(),
                event.ms_organizer_event_id,
                event._microsoft_values(["attendee_ids"]),
            )
