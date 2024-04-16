#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
fromdatetimeimporttimedelta

fromflectraimportapi,fields,models

_logger=logging.getLogger(__name__)


classAlarmManager(models.AbstractModel):
    _name='calendar.alarm_manager'
    _description='EventAlarmManager'

    def_get_next_potential_limit_alarm(self,alarm_type,seconds=None,partners=None):
        result={}
        delta_request="""
            SELECT
                rel.calendar_event_id,max(alarm.duration_minutes)ASmax_delta,min(alarm.duration_minutes)ASmin_delta
            FROM
                calendar_alarm_calendar_event_relASrel
            LEFTJOINcalendar_alarmASalarmONalarm.id=rel.calendar_alarm_id
            WHEREalarm.alarm_type=%s
            GROUPBYrel.calendar_event_id
        """
        base_request="""
                    SELECT
                        cal.id,
                        cal.start-interval'1'minute *calcul_delta.max_deltaASfirst_alarm,
                        CASE
                            WHENcal.recurrencyTHENrrule.until-interval'1'minute *calcul_delta.min_delta
                            ELSEcal.stop-interval'1'minute *calcul_delta.min_delta
                        ENDaslast_alarm,
                        cal.startasfirst_event_date,
                        CASE
                            WHENcal.recurrencyTHENrrule.until
                            ELSEcal.stop
                        ENDaslast_event_date,
                        calcul_delta.min_delta,
                        calcul_delta.max_delta,
                        rrule.rruleASrule
                    FROM
                        calendar_eventAScal
                    RIGHTJOINcalcul_deltaONcalcul_delta.calendar_event_id=cal.id
                    LEFTJOINcalendar_recurrenceasrruleONrrule.id=cal.recurrence_id
             """

        filter_user="""
                RIGHTJOINcalendar_event_res_partner_relASpart_relONpart_rel.calendar_event_id=cal.id
                    ANDpart_rel.res_partner_idIN%s
        """

        #Addfilteronalarmtype
        tuple_params=(alarm_type,)

        #Addfilteronpartner_id
        ifpartners:
            base_request+=filter_user
            tuple_params+=(tuple(partners.ids),)

        #Upperboundonfirst_alarmofrequestedevents
        first_alarm_max_value=""
        ifsecondsisNone:
            #firstalarminthefuture+3minutesifthereisone,nowotherwise
            first_alarm_max_value="""
                COALESCE((SELECTMIN(cal.start-interval'1'minute *calcul_delta.max_delta)
                FROMcalendar_eventcal
                RIGHTJOINcalcul_deltaONcalcul_delta.calendar_event_id=cal.id
                WHEREcal.start-interval'1'minute *calcul_delta.max_delta>now()attimezone'utc'
            )+interval'3'minute,now()attimezone'utc')"""
        else:
            #now+givenseconds
            first_alarm_max_value="(now()attimezone'utc'+interval'%s'second)"
            tuple_params+=(seconds,)

        self._cr.execute("""
            WITHcalcul_deltaAS(%s)
            SELECT*
                FROM(%sWHEREcal.active=True)ASALL_EVENTS
               WHEREALL_EVENTS.first_alarm<%s
                 ANDALL_EVENTS.last_event_date>(now()attimezone'utc')
        """%(delta_request,base_request,first_alarm_max_value),tuple_params)

        forevent_id,first_alarm,last_alarm,first_meeting,last_meeting,min_duration,max_duration,ruleinself._cr.fetchall():
            result[event_id]={
                'event_id':event_id,
                'first_alarm':first_alarm,
                'last_alarm':last_alarm,
                'first_meeting':first_meeting,
                'last_meeting':last_meeting,
                'min_duration':min_duration,
                'max_duration':max_duration,
                'rrule':rule
            }

        #determineaccessibleevents
        events=self.env['calendar.event'].browse(result)
        result={
            key:result[key]
            forkeyinset(events._filter_access_rules('read').ids)
        }
        returnresult

    defdo_check_alarm_for_one_date(self,one_date,event,event_maxdelta,in_the_next_X_seconds,alarm_type,after=False,missing=False):
        """Searchforsomealarmsintheintervaloftimedeterminedbysomeparameters(after,in_the_next_X_seconds,...)
            :paramone_date:dateoftheeventtocheck(notthesamethatintheeventbrowseifrecurrent)
            :paramevent:Eventbrowserecord
            :paramevent_maxdelta:biggestdurationfromalarmsforthisevent
            :paramin_the_next_X_seconds:lookinginthefuture(inseconds)
            :paramafter:ifnotFalse:willreturnalertifafterthisdate(dateasstring-todo:changeinmaster)
            :parammissing:ifnotFalse:willreturnalertevenifwearetoolate
            :paramnotif:Lookingfortypenotification
            :parammail:lookingfortypeemail
        """
        result=[]
        #TODO:removeevent_maxdeltaandifusingit
        ifone_date-timedelta(minutes=(missing*event_maxdelta))<fields.Datetime.now()+timedelta(seconds=in_the_next_X_seconds): #ifanalarmispossibleforthisdate
            foralarminevent.alarm_ids:
                ifalarm.alarm_type==alarm_typeand\
                    one_date-timedelta(minutes=(missing*alarm.duration_minutes))<fields.Datetime.now()+timedelta(seconds=in_the_next_X_seconds)and\
                        (notafterorone_date-timedelta(minutes=alarm.duration_minutes)>fields.Datetime.from_string(after)):
                    alert={
                        'alarm_id':alarm.id,
                        'event_id':event.id,
                        'notify_at':one_date-timedelta(minutes=alarm.duration_minutes),
                    }
                    result.append(alert)
        returnresult

    @api.model
    defget_next_mail(self):
        returnself._get_partner_next_mail(partners=None)

    @api.model
    def_get_partner_next_mail(self,partners=None):
        self=self.with_context(mail_notify_force_send=True)
        last_notif_mail=fields.Datetime.to_string(self.env.context.get('lastcall')orfields.Datetime.now())

        cron=self.env.ref('calendar.ir_cron_scheduler_alarm',raise_if_not_found=False)
        ifnotcron:
            _logger.error("Cronfor"+self._name+"cannotbeidentified!")
            returnFalse

        interval_to_second={
            "weeks":7*24*60*60,
            "days":24*60*60,
            "hours":60*60,
            "minutes":60,
            "seconds":1
        }

        ifcron.interval_typenotininterval_to_second:
            _logger.error("Crondelaycannotbecomputed!")
            returnFalse

        cron_interval=cron.interval_number*interval_to_second[cron.interval_type]

        all_meetings=self._get_next_potential_limit_alarm('email',seconds=cron_interval,partners=partners)

        formeetinginself.env['calendar.event'].browse(all_meetings):
            max_delta=all_meetings[meeting.id]['max_duration']
            in_date_format=meeting.start
            last_found=self.do_check_alarm_for_one_date(in_date_format,meeting,max_delta,0,'email',after=last_notif_mail,missing=True)
            foralertinlast_found:
                self.do_mail_reminder(alert)

    @api.model
    defget_next_notif(self):
        partner=self.env.user.partner_id
        all_notif=[]

        ifnotpartner:
            return[]

        all_meetings=self._get_next_potential_limit_alarm('notification',partners=partner)
        time_limit=3600*24 #returnalarmsofthenext24hours
        forevent_idinall_meetings:
            max_delta=all_meetings[event_id]['max_duration']
            meeting=self.env['calendar.event'].browse(event_id)
            in_date_format=fields.Datetime.from_string(meeting.start)
            last_found=self.do_check_alarm_for_one_date(in_date_format,meeting,max_delta,time_limit,'notification',after=partner.calendar_last_notif_ack)
            iflast_found:
                foralertinlast_found:
                    all_notif.append(self.do_notif_reminder(alert))
        returnall_notif

    defdo_mail_reminder(self,alert):
        meeting=self.env['calendar.event'].browse(alert['event_id'])
        alarm=self.env['calendar.alarm'].browse(alert['alarm_id'])

        result=False
        ifalarm.alarm_type=='email':
            result=meeting.attendee_ids.filtered(lambdar:r.state!='declined')._send_mail_to_attendees('calendar.calendar_template_meeting_reminder',force_send=True,ignore_recurrence=True)
        returnresult

    defdo_notif_reminder(self,alert):
        alarm=self.env['calendar.alarm'].browse(alert['alarm_id'])
        meeting=self.env['calendar.event'].browse(alert['event_id'])

        ifalarm.alarm_type=='notification':
            message=meeting.display_time

            delta=alert['notify_at']-fields.Datetime.now()
            delta=delta.seconds+delta.days*3600*24

            return{
                'alarm_id':alarm.id,
                'event_id':meeting.id,
                'title':meeting.name,
                'message':message,
                'timer':delta,
                'notify_at':fields.Datetime.to_string(alert['notify_at']),
            }

    def_notify_next_alarm(self,partner_ids):
        """Sendsthroughthebusthenextalarmofgivenpartners"""
        notifications=[]
        users=self.env['res.users'].search([('partner_id','in',tuple(partner_ids))])
        foruserinusers:
            notif=self.with_user(user).with_context(allowed_company_ids=user.company_ids.ids).get_next_notif()
            notifications.append([(self._cr.dbname,'calendar.alarm',user.partner_id.id),notif])
        iflen(notifications)>0:
            self.env['bus.bus'].sendmany(notifications)
