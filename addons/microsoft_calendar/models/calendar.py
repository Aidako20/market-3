#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
importpytz
fromdatetimeimportdatetime
fromdateutil.parserimportparse
fromdateutil.relativedeltaimportrelativedelta

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError,ValidationError
fromflectra.toolsimporthtml2plaintext,is_html_empty,email_normalize
fromflectra.addons.microsoft_calendar.utils.event_id_storageimportcombine_ids

ATTENDEE_CONVERTER_O2M={
    'needsAction':'notresponded',
    'tentative':'tentativelyaccepted',
    'declined':'declined',
    'accepted':'accepted'
}
ATTENDEE_CONVERTER_M2O={
    'none':'needsAction',
    'notResponded':'needsAction',
    'tentativelyAccepted':'tentative',
    'declined':'declined',
    'accepted':'accepted',
    'organizer':'accepted',
}
MAX_RECURRENT_EVENT=720

_logger=logging.getLogger(__name__)

classMeeting(models.Model):
    _name='calendar.event'
    _inherit=['calendar.event','microsoft.calendar.sync']

    #containsorganizereventidanduniversaleventidseparatedbya':'
    microsoft_id=fields.Char('MicrosoftCalendarEventId')
    microsoft_recurrence_master_id=fields.Char('MicrosoftRecurrenceMasterId')

    def_get_organizer(self):
        returnself.user_id

    @api.model
    def_get_microsoft_synced_fields(self):
        return{'name','description','allday','start','date_end','stop',
                'user_id','privacy',
                'attendee_ids','alarm_ids','location','show_as','active'}

    @api.model_create_multi
    defcreate(self,vals_list):
        notify_context=self.env.context.get('dont_notify',False)

        #forarecurrentevent,wedonotcreateeventsseparatelybutwedirectly
        #createtherecurrencyfromthecorrespondingcalendar.recurrence.
        #That'swhy,eventsfromarecurrencyhavetheir`need_sync_m`attributesettoFalse.
        returnsuper(Meeting,self.with_context(dont_notify=notify_context)).create([
            dict(vals,need_sync_m=False)ifvals.get('recurrence_id')orvals.get('recurrency')elsevals
            forvalsinvals_list
        ])

    def_check_recurrence_overlapping(self,new_start):
        """
        Outlookdoesnotallowtomodifytimefieldsofaneventifthiseventcrosses
        oroverlapstherecurrence.Inthiscasea400errorwiththeOutlookcode"ErrorOccurrenceCrossingBoundary"
        isreturned.ThatmeansthattheupdateviolatesthefollowingOutlookrestrictiononrecurrenceexceptions:
        anoccurrencecannotbemovedtoorbeforethedayofthepreviousoccurrence,andcannotbemovedtoorafter
        thedayofthefollowingoccurrence.
        Forexample:E1E2E3E4cannotbecomesE1E3E2E4
        """
        before_count=len(self.recurrence_id.calendar_event_ids.filtered(
            lambdae:e.start.date()<self.start.date()ande!=self
        ))
        after_count=len(self.recurrence_id.calendar_event_ids.filtered(
            lambdae:e.start.date()<parse(new_start).date()ande!=self
        ))
        ifbefore_count!=after_count:
            raiseUserError(_(
                "Outlooklimitation:inarecurrence,aneventcannotbemovedtoorbeforethedayofthe"
                "previousevent,andcannotbemovedtoorafterthedayofthefollowingevent."
            ))

    def_is_matching_timeslot(self,start,stop,allday):
        """
        Checkifaneventmatcheswiththeprovidedtimeslot
        """
        self.ensure_one()

        event_start,event_stop=self._range()
        ifallday:
            event_start=datetime(event_start.year,event_start.month,event_start.day,0,0)
            event_stop=datetime(event_stop.year,event_stop.month,event_stop.day,0,0)

        return(event_start,event_stop)==(start,stop)

    defwrite(self,values):
        recurrence_update_setting=values.get('recurrence_update')

        #checkaOutlooklimitationinoverlappingtheactualrecurrence
        ifrecurrence_update_setting=='self_only'and'start'invalues:
            self._check_recurrence_overlapping(values['start'])

        #ifasingleeventbecomesthebaseeventofarecurrency,itshouldbefirst
        #removedfromtheOutlookcalendar.
        if'recurrency'invaluesandvalues['recurrency']:
            foreinself.filtered(lambdae:note.recurrencyandnote.recurrence_id):
                e._microsoft_delete(e._get_organizer(),e.ms_organizer_event_id,timeout=3)
                e.microsoft_id=False

        notify_context=self.env.context.get('dont_notify',False)
        res=super(Meeting,self.with_context(dont_notify=notify_context)).write(values)

        ifrecurrence_update_settingin('all_events',)andlen(self)==1\
           andvalues.keys()&self._get_microsoft_synced_fields():
            self.recurrence_id.need_sync_m=True
        returnres

    def_get_microsoft_sync_domain(self):
        #incaseoffullsync,limittoarangeof1yinpastand1yinthefuturebydefault
        ICP=self.env['ir.config_parameter'].sudo()
        day_range=int(ICP.get_param('microsoft_calendar.sync.range_days',default=365))
        lower_bound=fields.Datetime.subtract(fields.Datetime.now(),days=day_range)
        upper_bound=fields.Datetime.add(fields.Datetime.now(),days=day_range)
        return[
            ('partner_ids.user_ids','in',self.env.user.id),
            ('stop','>',lower_bound),
            ('start','<',upper_bound),
            #Donotsynceventsthatfollowtherecurrence,theyarealreadysyncedatrecurrencecreation
            '!','&','&',('recurrency','=',True),('recurrence_id','!=',False),('follow_recurrence','=',True)
        ]


    @api.model
    def_microsoft_to_flectra_values(self,microsoft_event,default_reminders=(),default_values=None,with_ids=False):
        ifmicrosoft_event.is_cancelled():
            return{'active':False}

        sensitivity_o2m={
            'normal':'public',
            'private':'private',
            'confidential':'confidential',
        }

        commands_attendee,commands_partner=self._flectra_attendee_commands_m(microsoft_event)
        timeZone_start=pytz.timezone(microsoft_event.start.get('timeZone'))
        timeZone_stop=pytz.timezone(microsoft_event.end.get('timeZone'))
        start=parse(microsoft_event.start.get('dateTime')).astimezone(timeZone_start).replace(tzinfo=None)
        ifmicrosoft_event.isAllDay:
            stop=parse(microsoft_event.end.get('dateTime')).astimezone(timeZone_stop).replace(tzinfo=None)-relativedelta(days=1)
        else:
            stop=parse(microsoft_event.end.get('dateTime')).astimezone(timeZone_stop).replace(tzinfo=None)
        values=default_valuesor{}
        values.update({
            'name':microsoft_event.subjector_("(Notitle)"),
            'description':microsoft_event.bodyandmicrosoft_event.body['content'],
            'location':microsoft_event.locationandmicrosoft_event.location.get('displayName')orFalse,
            'user_id':microsoft_event.owner_id(self.env),
            'privacy':sensitivity_o2m.get(microsoft_event.sensitivity,self.default_get(['privacy'])['privacy']),
            'attendee_ids':commands_attendee,
            'allday':microsoft_event.isAllDay,
            'start':start,
            'stop':stop,
            'show_as':'free'ifmicrosoft_event.showAs=='free'else'busy',
            'recurrency':microsoft_event.is_recurrent()
        })
        ifcommands_partner:
            #Addpartner_commandsonlyifsetfromMicrosoft.Thewritemethodoncalendar_eventswill
            #overrideattendeecommandsifthepartner_idscommandissetbutempty.
            values['partner_ids']=commands_partner

        ifmicrosoft_event.is_recurrent()andnotmicrosoft_event.is_recurrence():
            #Propagatethefollow_recurrenceaccordingtotheOutlookresult
            values['follow_recurrence']=notmicrosoft_event.is_recurrence_outlier()

        ifwith_ids:
            values['microsoft_id']=combine_ids(microsoft_event.id,microsoft_event.iCalUId)

        ifmicrosoft_event.is_recurrent():
            values['microsoft_recurrence_master_id']=microsoft_event.seriesMasterId

        alarm_commands=self._flectra_reminders_commands_m(microsoft_event)
        ifalarm_commands:
            values['alarm_ids']=alarm_commands

        returnvalues

    @api.model
    def_microsoft_to_flectra_recurrence_values(self,microsoft_event,default_values=None):
        timeZone_start=pytz.timezone(microsoft_event.start.get('timeZone'))
        timeZone_stop=pytz.timezone(microsoft_event.end.get('timeZone'))
        start=parse(microsoft_event.start.get('dateTime')).astimezone(timeZone_start).replace(tzinfo=None)
        ifmicrosoft_event.isAllDay:
            stop=parse(microsoft_event.end.get('dateTime')).astimezone(timeZone_stop).replace(tzinfo=None)-relativedelta(days=1)
        else:
            stop=parse(microsoft_event.end.get('dateTime')).astimezone(timeZone_stop).replace(tzinfo=None)
        values=default_valuesor{}
        values.update({
            'microsoft_id':combine_ids(microsoft_event.id,microsoft_event.iCalUId),
            'microsoft_recurrence_master_id':microsoft_event.seriesMasterId,
            'start':start,
            'stop':stop,
        })
        returnvalues

    @api.model
    def_flectra_attendee_commands_m(self,microsoft_event):
        commands_attendee=[]
        commands_partner=[]

        microsoft_attendees=microsoft_event.attendeesor[]
        emails=[
            a.get('emailAddress').get('address')
            forainmicrosoft_attendees
            ifemail_normalize(a.get('emailAddress').get('address'))
        ]
        existing_attendees=self.env['calendar.attendee']
        ifmicrosoft_event.match_with_flectra_events(self.env):
            existing_attendees=self.env['calendar.attendee'].search([
                ('event_id','=',microsoft_event.flectra_id(self.env)),
                ('email','in',emails)])
        elifself.env.user.partner_id.emailnotinemails:
            commands_attendee+=[(0,0,{'state':'accepted','partner_id':self.env.user.partner_id.id})]
            commands_partner+=[(4,self.env.user.partner_id.id)]
        partners=self.env['mail.thread']._mail_find_partner_from_emails(emails,records=self,force_create=True)
        attendees_by_emails={a.email:aforainexisting_attendees}
        foremail,partner,attendee_infoinzip(emails,partners,microsoft_attendees):
            state=ATTENDEE_CONVERTER_M2O.get(attendee_info.get('status').get('response'),'needsAction')

            ifemailinattendees_by_emails:
                #Updateexistingattendees
                commands_attendee+=[(1,attendees_by_emails[email].id,{'state':state})]
            else:
                #Createnewattendees
                commands_attendee+=[(0,0,{'state':state,'partner_id':partner.id})]
                commands_partner+=[(4,partner.id)]
                ifattendee_info.get('emailAddress').get('name')andnotpartner.name:
                    partner.name=attendee_info.get('emailAddress').get('name')
        forflectra_attendeeinattendees_by_emails.values():
            #Removeoldattendees
            ifflectra_attendee.emailnotinemails:
                commands_attendee+=[(2,flectra_attendee.id)]
                commands_partner+=[(3,flectra_attendee.partner_id.id)]
        returncommands_attendee,commands_partner

    @api.model
    def_flectra_reminders_commands_m(self,microsoft_event):
        reminders_commands=[]
        ifmicrosoft_event.isReminderOn:
            event_id=self.browse(microsoft_event.flectra_id(self.env))
            alarm_type_label=_("Notification")

            minutes=microsoft_event.reminderMinutesBeforeStartor0
            alarm=self.env['calendar.alarm'].search([
                ('alarm_type','=','notification'),
                ('duration_minutes','=',minutes)
            ],limit=1)
            ifalarmandalarmnotinevent_id.alarm_ids:
                reminders_commands=[(4,alarm.id)]
            elifnotalarm:
                ifminutes==0:
                    interval='minutes'
                    duration=minutes
                    name=_("%s-Attimeofevent",alarm_type_label)
                elifminutes%(60*24)==0:
                    interval='days'
                    duration=minutes/60/24
                    name=_(
                        "%(reminder_type)s-%(duration)sDays",
                        reminder_type=alarm_type_label,
                        duration=duration,
                    )
                elifminutes%60==0:
                    interval='hours'
                    duration=minutes/60
                    name=_(
                        "%(reminder_type)s-%(duration)sHours",
                        reminder_type=alarm_type_label,
                        duration=duration,
                    )
                else:
                    interval='minutes'
                    duration=minutes
                    name=_(
                        "%(reminder_type)s-%(duration)sMinutes",
                        reminder_type=alarm_type_label,
                        duration=duration,
                    )
                reminders_commands=[(0,0,{'duration':duration,'interval':interval,'name':name,'alarm_type':'notification'})]

            alarm_to_rm=event_id.alarm_ids.filtered(lambdaa:a.alarm_type=='notification'anda.id!=alarm.id)
            ifalarm_to_rm:
                reminders_commands+=[(3,a.id)forainalarm_to_rm]

        else:
            event_id=self.browse(microsoft_event.flectra_id(self.env))
            alarm_to_rm=event_id.alarm_ids.filtered(lambdaa:a.alarm_type=='notification')
            ifalarm_to_rm:
                reminders_commands=[(3,a.id)forainalarm_to_rm]
        returnreminders_commands

    def_get_attendee_status_o2m(self,attendee):
        ifself.user_idandself.user_id==attendee.partner_id.user_id:
            return'organizer'
        returnATTENDEE_CONVERTER_O2M.get(attendee.state,'None')

    def_microsoft_values(self,fields_to_sync,initial_values={}):
        values=dict(initial_values)
        ifnotfields_to_sync:
            returnvalues

        microsoft_guid=self.env['ir.config_parameter'].sudo().get_param('microsoft_calendar.microsoft_guid',False)

        ifself.microsoft_recurrence_master_idand'type'notinvalues:
            values['seriesMasterId']=self.microsoft_recurrence_master_id
            values['type']='exception'

        if'name'infields_to_sync:
            values['subject']=self.nameor''

        if'description'infields_to_sync:
            values['body']={
                'content':html2plaintext(self.description)ifnotis_html_empty(self.description)else'',
                'contentType':"text",
            }

        ifany(xinfields_to_syncforxin['allday','start','date_end','stop']):
            ifself.allday:
                start={'dateTime':self.start_date.isoformat(),'timeZone':'Europe/London'}
                end={'dateTime':(self.stop_date+relativedelta(days=1)).isoformat(),'timeZone':'Europe/London'}
            else:
                start={'dateTime':pytz.utc.localize(self.start).isoformat(),'timeZone':'Europe/London'}
                end={'dateTime':pytz.utc.localize(self.stop).isoformat(),'timeZone':'Europe/London'}

            values['start']=start
            values['end']=end
            values['isAllDay']=self.allday

        if'location'infields_to_sync:
            values['location']={'displayName':self.locationor''}

        if'alarm_ids'infields_to_sync:
            alarm_id=self.alarm_ids.filtered(lambdaa:a.alarm_type=='notification')[:1]
            values['isReminderOn']=bool(alarm_id)
            values['reminderMinutesBeforeStart']=alarm_id.duration_minutes

        if'user_id'infields_to_sync:
            values['organizer']={'emailAddress':{'address':self.user_id.emailor'','name':self.user_id.display_nameor''}}
            values['isOrganizer']=self.user_id==self.env.user

        if'attendee_ids'infields_to_sync:
            attendees=self.attendee_ids.filtered(lambdaatt:att.partner_idnotinself.user_id.partner_id)
            values['attendees']=[
                {
                    'emailAddress':{'address':attendee.emailor'','name':attendee.display_nameor''},
                    'status':{'response':self._get_attendee_status_o2m(attendee)}
                }forattendeeinattendees]

        if'privacy'infields_to_syncor'show_as'infields_to_sync:
            values['showAs']=self.show_as
            sensitivity_o2m={
                'public':'normal',
                'private':'private',
                'confidential':'confidential',
            }
            values['sensitivity']=sensitivity_o2m.get(self.privacy)

        if'active'infields_to_syncandnotself.active:
            values['isCancelled']=True

        ifvalues.get('type')=='seriesMaster':
            recurrence=self.recurrence_id
            pattern={
                'interval':recurrence.interval
            }
            ifrecurrence.rrule_typein['daily','weekly']:
                pattern['type']=recurrence.rrule_type
            else:
                prefix='absolute'ifrecurrence.month_by=='date'else'relative'
                pattern['type']=recurrence.rrule_typeandprefix+recurrence.rrule_type.capitalize()

            ifrecurrence.month_by=='date':
                pattern['dayOfMonth']=recurrence.day

            ifrecurrence.month_by=='day'orrecurrence.rrule_type=='weekly':
                pattern['daysOfWeek']=[
                    weekday_nameforweekday_name,weekdayin{
                        'monday':recurrence.mo,
                        'tuesday':recurrence.tu,
                        'wednesday':recurrence.we,
                        'thursday':recurrence.th,
                        'friday':recurrence.fr,
                        'saturday':recurrence.sa,
                        'sunday':recurrence.su,
                    }.items()ifweekday]
                pattern['firstDayOfWeek']='sunday'

            ifrecurrence.rrule_type=='monthly'andrecurrence.month_by=='day':
                byday_selection={
                    '1':'first',
                    '2':'second',
                    '3':'third',
                    '4':'fourth',
                    '-1':'last',
                }
                pattern['index']=byday_selection[recurrence.byday]

            dtstart=recurrence.dtstartorfields.Datetime.now()
            rule_range={
                'startDate':(dtstart.date()).isoformat()
            }

            ifrecurrence.end_type=='count': #e.g.stopafterXoccurence
                rule_range['numberOfOccurrences']=min(recurrence.count,MAX_RECURRENT_EVENT)
                rule_range['type']='numbered'
            elifrecurrence.end_type=='forever':
                rule_range['numberOfOccurrences']=MAX_RECURRENT_EVENT
                rule_range['type']='numbered'
            elifrecurrence.end_type=='end_date': #e.g.stopafter12/10/2020
                rule_range['endDate']=recurrence.until.isoformat()
                rule_range['type']='endDate'

            values['recurrence']={
                'pattern':pattern,
                'range':rule_range
            }

        returnvalues

    def_ensure_attendees_have_email(self):
        invalid_event_ids=self.env['calendar.event'].search_read(
            domain=[('id','in',self.ids),('attendee_ids.partner_id.email','=',False)],
            fields=['display_time','display_name'],
            order='start',
        )
        ifinvalid_event_ids:
            list_length_limit=50
            total_invalid_events=len(invalid_event_ids)
            invalid_event_ids=invalid_event_ids[:list_length_limit]
            invalid_events=['\t-%s:%s'%(event['display_time'],event['display_name'])
                              foreventininvalid_event_ids]
            invalid_events='\n'.join(invalid_events)
            details="(%d/%d)"%(list_length_limit,total_invalid_events)iflist_length_limit<total_invalid_eventselse"(%d)"%total_invalid_events
            raiseValidationError(_("ForacorrectsynchronizationbetweenFlectraandOutlookCalendar,"
                                    "allattendeesmusthaveanemailaddress.However,someeventsdo"
                                    "notrespectthiscondition.Aslongastheeventsareincorrect,"
                                    "thecalendarswillnotbesynchronized."
                                    "\nEitherupdatetheevents/attendeesorarchivetheseevents%s:"
                                    "\n%s",details,invalid_events))

    def_microsoft_values_occurence(self,initial_values={}):
        values=initial_values
        values['type']='occurrence'

        ifself.allday:
            start={'dateTime':self.start_date.isoformat(),'timeZone':'Europe/London'}
            end={'dateTime':(self.stop_date+relativedelta(days=1)).isoformat(),'timeZone':'Europe/London'}
        else:
            start={'dateTime':pytz.utc.localize(self.start).isoformat(),'timeZone':'Europe/London'}
            end={'dateTime':pytz.utc.localize(self.stop).isoformat(),'timeZone':'Europe/London'}

        values['start']=start
        values['end']=end
        values['isAllDay']=self.allday

        returnvalues

    def_cancel_microsoft(self):
        """
        CancelanMicrosoftevent.
        Thereare2cases:
          1)theorganizerisanFlectrauser:he'stheonlyoneabletodeletetheFlectraevent.Attendeescanjustdecline.
          2)theorganizerisNOTanFlectrauser:anyattendeeshouldremovetheFlectraevent.
        """
        user=self.env.user
        records=self.filtered(lambdae:note.user_idore.user_id==user)
        super(Meeting,records)._cancel_microsoft()
