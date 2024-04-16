#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging

fromflectraimportapi,fields,models,_

_logger=logging.getLogger(__name__)


classCalendarEvent(models.Model):
    _inherit='calendar.event'

    def_sms_get_default_partners(self):
        """Methodoverriddenfrommail.thread(definedinthesmsmodule).
            SMStextmessageswillbesenttoattendeesthathaven'tdeclinedtheevent(s).
        """
        returnself.mapped('attendee_ids').filtered(lambdaatt:att.state!='declined'andatt.partner_id.phone_sanitized).mapped('partner_id')

    def_do_sms_reminder(self):
        """SendanSMStextremindertoattendeesthathaven'tdeclinedtheevent"""
        foreventinself:
            event._message_sms_with_template(
                template_xmlid='calendar_sms.sms_template_data_calendar_reminder',
                template_fallback=_("Eventreminder:%(name)s,%(time)s.",name=event.name,time=event.display_time),
                partner_ids=self._sms_get_default_partners().ids,
                put_in_queue=False
            )


classCalendarAlarm(models.Model):
    _inherit='calendar.alarm'

    alarm_type=fields.Selection(selection_add=[
        ('sms','SMSTextMessage')
    ],ondelete={'sms':'setdefault'})


classAlarmManager(models.AbstractModel):
    _inherit='calendar.alarm_manager'

    @api.model
    defget_next_mail(self):
        """Cronmethod,overriddenheretosendSMSremindersaswell
        """
        result=super(AlarmManager,self).get_next_mail()

        cron=self.env.ref('calendar.ir_cron_scheduler_alarm',raise_if_not_found=False)
        ifnotcron:
            #Likethesupermethod,donothingifcrondoesn'texistanymore
            returnresult

        now=fields.Datetime.to_string(fields.Datetime.now())
        last_sms_cron=cron.lastcall

        interval_to_second={
            "weeks":7*24*60*60,
            "days":24*60*60,
            "hours":60*60,
            "minutes":60,
            "seconds":1
        }

        cron_interval=cron.interval_number*interval_to_second[cron.interval_type]
        events_data=self._get_next_potential_limit_alarm('sms',seconds=cron_interval)

        foreventinself.env['calendar.event'].browse(events_data):
            max_delta=events_data[event.id]['max_duration']
            event_start=fields.Datetime.from_string(event.start)
            foralertinself.do_check_alarm_for_one_date(event_start,event,max_delta,0,'sms',after=last_sms_cron,missing=True):
                event.browse(alert['event_id'])._do_sms_reminder()
        returnresult
