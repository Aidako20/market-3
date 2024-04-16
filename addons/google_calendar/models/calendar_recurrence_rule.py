#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importre
fromdateutil.relativedeltaimportrelativedelta

fromflectraimportapi,fields,models

fromflectra.addons.google_calendar.utils.google_calendarimportGoogleCalendarService


classRecurrenceRule(models.Model):
    _name='calendar.recurrence'
    _inherit=['calendar.recurrence','google.calendar.sync']


    def_apply_recurrence(self,specific_values_creation=None,no_send_edit=False):
        events=self.filtered('need_sync').calendar_event_ids
        detached_events=super()._apply_recurrence(specific_values_creation,no_send_edit)

        google_service=GoogleCalendarService(self.env['google.service'])

        #Ifasyncedeventbecomesarecurrence,theeventneedstobedeletedfrom
        #Googlesinceit'snowtherecurrencewhichissynced.
        #Thoseeventsarekeptinthedatabaseandtheirgoogle_idisupdated
        #accordingtotherecurrencegoogle_id,thereforeweneedtokeepaninactivecopy
        #ofthoseeventswiththeoriginalgoogleid.Thenextsyncwillthencorrectly
        #deletethoseeventsfromGoogle.
        vals=[]
        foreventinevents.filtered('google_id'):
            ifevent.activeandevent.google_id!=event.recurrence_id._get_event_google_id(event):
                vals+=[{
                    'name':event.name,
                    'google_id':event.google_id,
                    'start':event.start,
                    'stop':event.stop,
                    'active':False,
                    'need_sync':True,
                }]
                event.with_user(event._get_event_user())._google_delete(google_service,event.google_id)
                event.google_id=False
        self.env['calendar.event'].create(vals)

        self.calendar_event_ids.need_sync=False
        returndetached_events

    def_get_event_google_id(self,event):
        """ReturntheGoogleidofrecurringevent.
        Googleidsofrecurrenceinstancesareformattedas:{recurrencegoogle_id}_{UTCstartingtimeincompactedISO8601}
        """
        ifself.google_id:
            ifevent.allday:
                time_id=event.start_date.isoformat().replace('-','')
            else:
                #'-'and':'areoptionalinISO8601
                start_compacted_iso8601=event.start.isoformat().replace('-','').replace(':','')
                #ZattheendforUTC
                time_id='%sZ'%start_compacted_iso8601
            return'%s_%s'%(self.google_id,time_id)
        returnFalse

    def_write_events(self,values,dtstart=None):
        values.pop('google_id',False)
        #Ifonlysomeeventsareupdated,syncthoseevents.
        values['need_sync']=bool(dtstart)
        returnsuper()._write_events(values,dtstart=dtstart)

    def_cancel(self):
        self.calendar_event_ids._cancel()
        super()._cancel()

    def_get_google_synced_fields(self):
        return{'rrule'}

    def_write_from_google(self,gevent,vals):
        current_rrule=self.rrule
        #event_tziswrittenoneventinGooglebutonrecurrenceinFlectra
        vals['event_tz']=gevent.start.get('timeZone')
        super()._write_from_google(gevent,vals)

        base_event_time_fields=['start','stop','allday']
        new_event_values=self.env["calendar.event"]._flectra_values(gevent)
        old_event_values=self.base_event_idandself.base_event_id.read(base_event_time_fields)[0]
        ifold_event_valuesandany(new_event_values[key]!=old_event_values[key]forkeyinbase_event_time_fields):
            #weneedtorecreatetherecurrence,time_fieldsweremodified.
            base_event_id=self.base_event_id
            #Wearchivetheoldeventstorecomputetherecurrence.TheseeventsarealreadydeletedonGoogleside.
            #Wecan'tcall_cancelbecauseeventswithoutuser_idwouldnotbedeleted
            (self.calendar_event_ids-base_event_id).google_id=False
            (self.calendar_event_ids-base_event_id).unlink()
            base_event_id.write(dict(new_event_values,google_id=False,need_sync=False))
            ifself.rrule==current_rrule:
                #iftherrulehaschanged,itwillberecalculatedbelow
                #Thereisnodetachedeventnow
                self._apply_recurrence()
        else:
            time_fields=(
                    self.env["calendar.event"]._get_time_fields()
                    |self.env["calendar.event"]._get_recurrent_fields()
            )
            #Weavoidtowritetime_fieldsbecausetheyarenotsharedbetweenevents.
            self._write_events(dict({
                field:value
                forfield,valueinnew_event_values.items()
                iffieldnotintime_fields
                },need_sync=False)
            )

        #Weapplytherrulecheckafterthetime_fieldcheckbecausethegoogle_idaregeneratedaccording
        #tobase_eventstartdatetime.
        ifself.rrule!=current_rrule:
            detached_events=self._apply_recurrence()
            detached_events.google_id=False
            detached_events.unlink()

    def_create_from_google(self,gevents,vals_list):
        forgevent,valsinzip(gevents,vals_list):
            base_values=dict(
                self.env['calendar.event']._flectra_values(gevent), #FIXMEdefaultreminders
                need_sync=False,
            )
            #IfweconvertasingleeventintoarecurrencyonGoogle,weshouldreusethiseventonFlectra
            #Googlereusetheeventgoogle_idtoidentifytherecurrenceinthatcase
            base_event=self.env['calendar.event'].search([('google_id','=',vals['google_id'])])
            ifnotbase_event:
                base_event=self.env['calendar.event'].create(base_values)
            else:
                #Weoverridethebase_eventvaluesbecausetheycouldhavebeenchangedinGoogleinterface
                #Theeventgoogle_idwillberecalculatedoncetherecurrenceiscreated
                base_event.write(dict(base_values,google_id=False))
            vals['base_event_id']=base_event.id
            vals['calendar_event_ids']=[(4,base_event.id)]
            #event_tziswrittenoneventinGooglebutonrecurrenceinFlectra
            vals['event_tz']=gevent.start.get('timeZone')
        recurrence=super(RecurrenceRule,self.with_context(dont_notify=True))._create_from_google(gevents,vals_list)
        recurrence.with_context(dont_notify=True)._apply_recurrence()
        ifnotrecurrence._context.get("dont_notify"):
            recurrence._notify_attendees()
        returnrecurrence

    def_get_sync_domain(self):
        return[('calendar_event_ids.user_id','=',self.env.user.id)]

    @api.model
    def_flectra_values(self,google_recurrence,default_reminders=()):
        return{
            'rrule':google_recurrence.rrule,
            'google_id':google_recurrence.id,
        }

    def_google_values(self):
        event=self._get_first_event()
        ifnotevent:
            return{}
        values=event._google_values()
        values['id']=self.google_id

        ifnotself._is_allday():
            values['start']['timeZone']=self.event_tz
            values['end']['timeZone']=self.event_tz

        #DTSTARTisnotallowedbyGoogleCalendarAPI.
        #Eventstartandendtimesarespecifiedinthestartandendfields.
        rrule=re.sub('DTSTART:[0-9]{8}T[0-9]{1,8}\\n','',self.rrule)
        #UNTILmustbeinUTC(appendingZ)
        #Wewanttoonlyadda'Z'tononUTCUNTILvaluesandavoidaddingasecond.
        #'RRULE:FREQ=DAILY;UNTIL=20210224T235959;INTERVAL=3-->matchUNTIL=20210224T235959
        #'RRULE:FREQ=DAILY;UNTIL=20210224T235959-->match
        rrule=re.sub(r"(UNTIL=\d{8}T\d{6})($|;)",r"\1Z\2",rrule)
        values['recurrence']=['RRULE:%s'%rrule]if'RRULE:'notinrruleelse[rrule]
        property_location='shared'ifevent.user_idelse'private'
        values['extendedProperties']={
            property_location:{
                '%s_flectra_id'%self.env.cr.dbname:self.id,
            },
        }
        returnvalues

    def_notify_attendees(self):
        recurrences=self.filtered(
            lambdarecurrence:recurrence.base_event_id.alarm_idsand(
                notrecurrence.untilorrecurrence.until>=fields.Date.today()-relativedelta(days=1)
            )and(max(recurrence.calendar_event_ids.mapped('stop'))>=fields.Datetime.now())
        )
        partners=recurrences.base_event_id.partner_ids
        ifpartners:
            self.env['calendar.alarm_manager']._notify_next_alarm(partners.ids)

    def_get_event_user(self):
        self.ensure_one()
        event=self._get_first_event()
        ifevent:
            returnevent._get_event_user()
        returnself.env.user
