#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classRecurrenceRule(models.Model):
    _name='calendar.recurrence'
    _inherit=['calendar.recurrence','microsoft.calendar.sync']


    #Don'tsyncbydefault.Synconlywhentherecurrenceisapplied
    need_sync_m=fields.Boolean(default=False)

    microsoft_id=fields.Char('MicrosoftCalendarRecurrenceId')

    def_compute_rrule(self):
        #Note:'need_sync_m'issettoFalsetoavoidsyncingtheupdatedrecurrencewith
        #Outlook,asthisupdatemayalreadycomefromOutlook.Ifnot,thismodificationwill
        #bealreadysyncedthroughthecalendar.event.write()
        forrecurrenceinself:
            ifrecurrence.rrule!=recurrence._rrule_serialize():
                recurrence.write({'rrule':recurrence._rrule_serialize()})

    def_inverse_rrule(self):
        #Note:'need_sync_m'issettoFalsetoavoidsyncingtheupdatedrecurrencewith
        #Outlook,asthisupdatemainlycomesfromOutlook(the'rrule'fieldisnotdirectly
        #modifiedinFlectrabutcomputedfromotherfields).
        forrecurrenceinself.filtered('rrule'):
            values=self._rrule_parse(recurrence.rrule,recurrence.dtstart)
            recurrence.write(dict(values,need_sync_m=False))

    def_apply_recurrence(self,specific_values_creation=None,no_send_edit=False):
        events=self.filtered('need_sync_m').calendar_event_ids
        detached_events=super()._apply_recurrence(specific_values_creation,no_send_edit)

        #Ifasyncedeventbecomesarecurrence,theeventneedstobedeletedfrom
        #Microsoftsinceit'snowtherecurrencewhichissynced.
        vals=[]
        foreventinevents._get_synced_events():
            ifevent.activeandevent.ms_universal_event_idandnotevent.recurrence_id.ms_universal_event_id:
                vals+=[{
                    'name':event.name,
                    'microsoft_id':event.microsoft_id,
                    'start':event.start,
                    'stop':event.stop,
                    'active':False,
                    'need_sync_m':True,
                }]
                event._microsoft_delete(event.user_id,event.ms_organizer_event_id)
                event.ms_universal_event_id=False
        self.env['calendar.event'].create(vals)
        self.calendar_event_ids.need_sync_m=False
        returndetached_events

    def_write_events(self,values,dtstart=None):
        #Ifonlysomeeventsareupdated,syncthoseevents.
        #Ifalleventsareupdated,synctherecurrenceinstead.
        values['need_sync_m']=bool(dtstart)orvalues.get("need_sync_m",True)
        returnsuper()._write_events(values,dtstart=dtstart)

    def_get_organizer(self):
        returnself.base_event_id.user_id

    def_get_rrule(self,dtstart=None):
        ifnotdtstartandself.dtstart:
            dtstart=self.dtstart
        returnsuper()._get_rrule(dtstart)

    def_get_microsoft_synced_fields(self):
        return{'rrule'}|self.env['calendar.event']._get_microsoft_synced_fields()

    def_has_base_event_time_fields_changed(self,new):
        """
        Indicatesifatleastonetimefieldofthebaseeventhaschanged,based
        onprovided`new`values.
        Note:foralldayeventcomparison,hours/minutesareignored.
        """
        def_convert(value,to_convert):
            returnvalue.date()ifto_convertelsevalue

        old=self.base_event_idandself.base_event_id.read(['start','stop','allday'])[0]
        returnoldand(
            old['allday']!=new['allday']
            orany(
                _convert(new[f],new['allday'])!=_convert(old[f],old['allday'])
                forfin('start','stop')
            )
        )

    def_write_from_microsoft(self,microsoft_event,vals):
        current_rrule=self.rrule
        #event_tziswrittenoneventinMicrosoftbutonrecurrenceinFlectra
        vals['event_tz']=microsoft_event.start.get('timeZone')
        super()._write_from_microsoft(microsoft_event,vals)
        new_event_values=self.env["calendar.event"]._microsoft_to_flectra_values(microsoft_event)
        ifself._has_base_event_time_fields_changed(new_event_values):
            #weneedtorecreatetherecurrence,time_fieldsweremodified.
            base_event_id=self.base_event_id
            #Wearchivetheoldeventstorecomputetherecurrence.TheseeventsarealreadydeletedonMicrosoftside.
            #Wecan'tcall_cancelbecauseeventswithoutuser_idwouldnotbedeleted
            (self.calendar_event_ids-base_event_id).microsoft_id=False
            (self.calendar_event_ids-base_event_id).unlink()
            base_event_id.with_context(dont_notify=True).write(dict(
                new_event_values,microsoft_id=False,need_sync_m=False
            ))
            ifself.rrule==current_rrule:
                #iftherrulehaschanged,itwillberecalculatedbelow
                #Thereisnodetachedeventnow
                self.with_context(dont_notify=True)._apply_recurrence()
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
                },need_sync_m=False)
            )
        #Weapplytherrulecheckafterthetime_fieldcheckbecausethemicrosoftidsaregeneratedaccording
        #tobase_eventstartdatetime.
        ifself.rrule!=current_rrule:
            detached_events=self._apply_recurrence()
            detached_events.microsoft_id=False
            detached_events.unlink()

    def_get_microsoft_sync_domain(self):
        #Emptyrrulemayexistsinhistoricaldata.Itisnotadesiredbehaviorbutitcouldhavebeencreatedwith
        #olderversionsofthemodule.Whensynced,theserecurrencemaycomebackfromMicrosoftafterdatabasecleaning
        #andtriggererrorsastherecordsarenotproperlypopulated.
        #Wealsopreventsyncofotheruserrecurrentevents.
        return[('calendar_event_ids.user_id','=',self.env.user.id),('rrule','!=',False)]

    def_cancel_microsoft(self):
        self.calendar_event_ids._cancel_microsoft()
        super()._cancel_microsoft()

    @api.model
    def_microsoft_to_flectra_values(self,microsoft_recurrence,default_reminders=(),default_values=None,with_ids=False):
        recurrence=microsoft_recurrence.get_recurrence()

        ifwith_ids:
            recurrence={
                **recurrence,
                'ms_organizer_event_id':microsoft_recurrence.id,
                'ms_universal_event_id':microsoft_recurrence.iCalUId,
            }

        returnrecurrence

    def_microsoft_values(self,fields_to_sync):
        """
        GetvaluestoupdatethewholeOutlookeventrecurrence.
        (donethroughthefirsteventoftheOutlookrecurrence).
        """
        returnself.base_event_id._microsoft_values(fields_to_sync,initial_values={'type':'seriesMaster'})

    def_ensure_attendees_have_email(self):
        self.calendar_event_ids.filtered(lambdae:e.active)._ensure_attendees_have_email()
