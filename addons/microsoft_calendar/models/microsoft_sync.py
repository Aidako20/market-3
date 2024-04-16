#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
fromcontextlibimportcontextmanager
fromfunctoolsimportwraps
importpytz
fromdateutil.parserimportparse

fromflectraimportapi,fields,models,registry
fromflectra.toolsimportormcache_context
fromflectra.exceptionsimportUserError
fromflectra.osvimportexpression

fromflectra.addons.microsoft_calendar.utils.microsoft_eventimportMicrosoftEvent
fromflectra.addons.microsoft_calendar.utils.microsoft_calendarimportMicrosoftCalendarService
fromflectra.addons.microsoft_calendar.utils.event_id_storageimportIDS_SEPARATOR,combine_ids,split_ids
fromflectra.addons.microsoft_account.models.microsoft_serviceimportTIMEOUT

_logger=logging.getLogger(__name__)

MAX_RECURRENT_EVENT=720

#APIrequestsaresenttoMicrosoftCalendarafterthecurrenttransactionends.
#ThisensureschangesaresenttoMicrosoftonlyiftheyreallyhappenedintheFlectradatabase.
#Itisparticularlyimportantforeventcreation,otherwisetheeventmightbecreated
#twiceinMicrosoftifthefirstcreationcrashedinFlectra.
defafter_commit(func):
    @wraps(func)
    defwrapped(self,*args,**kwargs):
        dbname=self.env.cr.dbname
        context=self.env.context
        uid=self.env.uid

        ifself.env.context.get('no_calendar_sync'):
            return

        @self.env.cr.postcommit.add
        defcalled_after():
            db_registry=registry(dbname)
            withapi.Environment.manage(),db_registry.cursor()ascr:
                env=api.Environment(cr,uid,context)
                try:
                    func(self.with_env(env),*args,**kwargs)
                exceptExceptionase:
                    _logger.warning("Couldnotsyncrecordnow:%s"%self)
                    _logger.exception(e)

    returnwrapped

@contextmanager
defmicrosoft_calendar_token(user):
    yielduser._get_microsoft_calendar_token()

classMicrosoftSync(models.AbstractModel):
    _name='microsoft.calendar.sync'
    _description="SynchronizearecordwithMicrosoftCalendar"

    microsoft_id=fields.Char('MicrosoftCalendarId',copy=False)

    ms_organizer_event_id=fields.Char(
        'OrganizereventId',
        compute='_compute_organizer_event_id',
        inverse='_set_event_id',
        search='_search_organizer_event_id',
    )
    ms_universal_event_id=fields.Char(
        'UniversaleventId',
        compute='_compute_universal_event_id',
        inverse='_set_event_id',
        search='_search_universal_event_id',
    )

    #Thisfieldhelpstoknowwhenamicrosofteventneedtoberesynced
    need_sync_m=fields.Boolean(default=True,copy=False)
    active=fields.Boolean(default=True)

    defwrite(self,vals):
        if'ms_universal_event_id'invals:
            self._from_uids.clear_cache(self)

        fields_to_sync=[xforxinvals.keys()ifxinself._get_microsoft_synced_fields()]
        iffields_to_syncand'need_sync_m'notinvals:
            vals['need_sync_m']=True

        result=super().write(vals)

        forrecordinself.filtered(lambdae:e.need_sync_mande.ms_organizer_event_id):
            ifnotvals.get('active',True):
                #Weneedtodeletetheevent.Cancelisnotsufficant.Errorsmayoccurs
                record._microsoft_delete(record._get_organizer(),record.ms_organizer_event_id,timeout=3)
            eliffields_to_sync:
                values=record._microsoft_values(fields_to_sync)
                ifnotvalues:
                    continue
                record._microsoft_patch(record._get_organizer(),record.ms_organizer_event_id,values,timeout=3)

        returnresult

    @api.model_create_multi
    defcreate(self,vals_list):
        records=super().create(vals_list)

        records_to_sync=records.filtered(lambdar:r.need_sync_mandr.active)
        forrecordinrecords_to_sync:
            record._microsoft_insert(record._microsoft_values(self._get_microsoft_synced_fields()),timeout=3)
        returnrecords

    @api.depends('microsoft_id')
    def_compute_organizer_event_id(self):
        foreventinself:
            event.ms_organizer_event_id=split_ids(event.microsoft_id)[0]ifevent.microsoft_idelseFalse

    @api.depends('microsoft_id')
    def_compute_universal_event_id(self):
        foreventinself:
            event.ms_universal_event_id=split_ids(event.microsoft_id)[1]ifevent.microsoft_idelseFalse

    def_set_event_id(self):
        foreventinself:
            event.microsoft_id=combine_ids(event.ms_organizer_event_id,event.ms_universal_event_id)

    def_search_event_id(self,operator,value,with_uid):
        def_domain(v):
            return('microsoft_id','=like',f'%{IDS_SEPARATOR}{v}'ifwith_uidelsef'{v}%')

        ifoperator=='='andnotvalue:
            return(
                ['|',('microsoft_id','=',False),('microsoft_id','=ilike',f'%{IDS_SEPARATOR}')]
                ifwith_uid
                else[('microsoft_id','=',False)]
            )
        elifoperator=='!='andnotvalue:
            return(
                [('microsoft_id','ilike',f'{IDS_SEPARATOR}_')]
                ifwith_uid
                else[('microsoft_id','!=',False)]
            )
        return(
            ['|']*(len(value)-1)+[_domain(v)forvinvalue]
            ifoperator.lower()=='in'
            else[_domain(value)]
        )

    def_search_organizer_event_id(self,operator,value):
        returnself._search_event_id(operator,value,with_uid=False)

    def_search_universal_event_id(self,operator,value):
        returnself._search_event_id(operator,value,with_uid=True)

    @api.model
    def_get_microsoft_service(self):
        returnMicrosoftCalendarService(self.env['microsoft.service'])

    def_get_synced_events(self):
        """
        GeteventsalreadysyncedwithMicrosoftOutlook.
        """
        returnself.filtered(lambdae:e.ms_universal_event_id)

    defunlink(self):
        synced=self._get_synced_events()
        forevinsynced:
            ev._microsoft_delete(ev._get_organizer(),ev.ms_organizer_event_id)
        returnsuper().unlink()

    def_write_from_microsoft(self,microsoft_event,vals):
        self.write(vals)

    @api.model
    def_create_from_microsoft(self,microsoft_event,vals_list):
        returnself.create(vals_list)

    @api.model
    @ormcache_context('uids',keys=('active_test',))
    def_from_uids(self,uids):
        ifnotuids:
            returnself.browse()
        returnself.search([('ms_universal_event_id','in',uids)])

    def_sync_flectra2microsoft(self):
        ifnotself:
            return
        ifself._active_name:
            records_to_sync=self.filtered(self._active_name)
        else:
            records_to_sync=self
        cancelled_records=self-records_to_sync

        records_to_sync._ensure_attendees_have_email()
        updated_records=records_to_sync._get_synced_events()
        new_records=records_to_sync-updated_records

        forrecordincancelled_records._get_synced_events():
            record._microsoft_delete(record._get_organizer(),record.ms_organizer_event_id)
        forrecordinnew_records:
            values=record._microsoft_values(self._get_microsoft_synced_fields())
            ifisinstance(values,dict):
                record._microsoft_insert(values)
            else:
                forvalueinvalues:
                    record._microsoft_insert(value)
        forrecordinupdated_records.filtered('need_sync_m'):
            values=record._microsoft_values(self._get_microsoft_synced_fields())
            ifnotvalues:
                continue
            record._microsoft_patch(record._get_organizer(),record.ms_organizer_event_id,values)

    def_cancel_microsoft(self):
        self.microsoft_id=False
        self.unlink()

    def_sync_recurrence_microsoft2flectra(self,microsoft_events,new_events=None):
        recurrent_masters=new_events.filter(lambdae:e.is_recurrence())ifnew_eventselse[]
        recurrents=new_events.filter(lambdae:e.is_recurrent_not_master())ifnew_eventselse[]
        default_values={'need_sync_m':False}

        new_recurrence=self.env['calendar.recurrence']
        updated_events=self.env['calendar.event']

        #---createnewrecurrencesandassociatedevents---
        forrecurrent_masterinrecurrent_masters:
            new_calendar_recurrence=dict(
                self.env['calendar.recurrence']._microsoft_to_flectra_values(recurrent_master,default_values,with_ids=True),
                need_sync_m=False
            )
            to_create=recurrents.filter(
                lambdae:e.seriesMasterId==new_calendar_recurrence['ms_organizer_event_id']
            )
            recurrents-=to_create
            base_values=dict(
                self.env['calendar.event']._microsoft_to_flectra_values(recurrent_master,default_values,with_ids=True),
                need_sync_m=False
            )
            to_create_values=[]
            ifnew_calendar_recurrence.get('end_type',False)in['count','forever']:
                to_create=list(to_create)[:MAX_RECURRENT_EVENT]
            forrecurrent_eventinto_create:
                ifrecurrent_event.type=='occurrence':
                    value=self.env['calendar.event']._microsoft_to_flectra_recurrence_values(recurrent_event,base_values)
                else:
                    value=self.env['calendar.event']._microsoft_to_flectra_values(recurrent_event,default_values)

                to_create_values+=[dict(value,need_sync_m=False)]

            new_calendar_recurrence['calendar_event_ids']=[(0,0,to_create_value)forto_create_valueinto_create_values]
            new_recurrence_flectra=self.env['calendar.recurrence'].create(new_calendar_recurrence)
            new_recurrence_flectra.base_event_id=new_recurrence_flectra.calendar_event_ids[0]ifnew_recurrence_flectra.calendar_event_idselseFalse
            new_recurrence|=new_recurrence_flectra

        #---updateeventsinexistingrecurrences---
        #Importantnote:
        #Tomapexistingrecurrenceswitheventstoupdate,wemustusetheuniversalid
        #(alsoknownasICalUIdintheMicrosoftAPI),as'seriesMasterId'attributeofevents
        #isspecifictotheMicrosoftusercalendar.
        ms_recurrence_ids=list({x.seriesMasterIdforxinrecurrents})
        ms_recurrence_uids={r.id:r.iCalUIdforrinmicrosoft_eventsifr.idinms_recurrence_ids}

        recurrences=self.env['calendar.recurrence'].search([
            ('ms_universal_event_id','in',ms_recurrence_uids.values())
        ])
        forrecurrent_master_idinms_recurrence_ids:
            recurrence_id=recurrences.filtered(
                lambdaev:ev.ms_universal_event_id==ms_recurrence_uids[recurrent_master_id]
            )
            to_update=recurrents.filter(lambdae:e.seriesMasterId==recurrent_master_id)
            forrecurrent_eventinto_update:
                ifrecurrent_event.type=='occurrence':
                    value=self.env['calendar.event']._microsoft_to_flectra_recurrence_values(
                        recurrent_event,{'need_sync_m':False}
                    )
                else:
                    value=self.env['calendar.event']._microsoft_to_flectra_values(recurrent_event,default_values)
                existing_event=recurrence_id.calendar_event_ids.filtered(
                    lambdae:e._is_matching_timeslot(value['start'],value['stop'],recurrent_event.isAllDay)
                )
                ifnotexisting_event:
                    continue
                value.pop('start')
                value.pop('stop')
                existing_event._write_from_microsoft(recurrent_event,value)
                updated_events|=existing_event
            new_recurrence|=recurrence_id
        returnnew_recurrence,updated_events

    def_update_microsoft_recurrence(self,recurrence,events):
        """
        UpdateFlectraeventsfromOutlookrecurrenceandevents.
        """
        #getthelistofeventstoupdate...
        events_to_update=events.filter(lambdae:e.seriesMasterId==self.ms_organizer_event_id)
        ifself.end_typein['count','forever']:
            events_to_update=list(events_to_update)[:MAX_RECURRENT_EVENT]

        #...andupdatethem
        rec_values={}
        update_events=self.env['calendar.event']
        foreinevents_to_update:
            ife.type=="exception":
                event_values=self.env['calendar.event']._microsoft_to_flectra_values(e)
            elife.type=="occurrence":
                event_values=self.env['calendar.event']._microsoft_to_flectra_recurrence_values(e)
            else:
                event_values=None

            ifevent_values:
                #keepeventvaluestoupdatetherecurrencelater
                ifany(fforfin('start','stop')iffinevent_values):
                    rec_values[(self.id,event_values.get('start'),event_values.get('stop'))]=dict(
                        event_values,need_sync_m=False
                    )

                flectra_event=self.env['calendar.event'].browse(e.flectra_id(self.env)).exists().with_context(
                    no_mail_to_attendees=True,mail_create_nolog=True
                )
                flectra_event.write(dict(event_values,need_sync_m=False))
                update_events|=flectra_event

        #updatetherecurrence
        detached_events=self._apply_recurrence(rec_values)
        detached_events._cancel_microsoft()

        returnupdate_events

    @api.model
    def_sync_microsoft2flectra(self,microsoft_events:MicrosoftEvent):
        """
        SynchronizeMicrosoftrecurrencesinFlectra.
        Createsnewrecurrences,updatesexistingones.
        :return:synchronizedflectra
        """
        existing=microsoft_events.match_with_flectra_events(self.env)
        cancelled=microsoft_events.cancelled()
        new=microsoft_events-existing-cancelled
        new_recurrence=new.filter(lambdae:e.is_recurrent())

        #createneweventsandreccurrences
        flectra_values=[
            dict(self._microsoft_to_flectra_values(e,with_ids=True),need_sync_m=False)
            forein(new-new_recurrence)
        ]
        synced_events=self.with_context(dont_notify=True)._create_from_microsoft(new,flectra_values)
        synced_recurrences,updated_events=self._sync_recurrence_microsoft2flectra(existing,new_recurrence)
        synced_events|=updated_events

        #removecancelledeventsandrecurrences
        cancelled_recurrences=self.env['calendar.recurrence'].search([
            '|',
            ('ms_universal_event_id','in',cancelled.uids),
            ('ms_organizer_event_id','in',cancelled.ids),
        ])
        cancelled_events=self.browse([
            e.flectra_id(self.env)
            foreincancelled
            ife.idnotin[r.ms_organizer_event_idforrincancelled_recurrences]
        ])
        cancelled_recurrences._cancel_microsoft()
        cancelled_events=cancelled_events.exists()
        cancelled_events._cancel_microsoft()

        synced_recurrences|=cancelled_recurrences
        synced_events|=cancelled_events|cancelled_recurrences.calendar_event_ids

        #updateotherevents
        formeventin(existing-cancelled).filter(lambdae:e.lastModifiedDateTime):
            #Lastupdatedwins.
            #Thiscouldbedangerousifmicrosoftservertimeandflectraservertimearedifferent
            ifmevent.is_recurrence():
                flectra_event=self.env['calendar.recurrence'].browse(mevent.flectra_id(self.env)).exists()
            else:
                flectra_event=self.browse(mevent.flectra_id(self.env)).exists()

            ifflectra_event:
                flectra_event_updated_time=pytz.utc.localize(flectra_event.write_date)
                ms_event_updated_time=parse(mevent.lastModifiedDateTime)

                ifms_event_updated_time>=flectra_event_updated_time:
                    vals=dict(flectra_event._microsoft_to_flectra_values(mevent),need_sync_m=False)
                    flectra_event._write_from_microsoft(mevent,vals)

                    ifflectra_event._name=='calendar.recurrence':
                        update_events=flectra_event._update_microsoft_recurrence(mevent,microsoft_events)
                        synced_recurrences|=flectra_event
                        synced_events|=update_events
                    else:
                        synced_events|=flectra_event

        returnsynced_events,synced_recurrences

    def_impersonate_user(self,user_id):
        """Impersonateauser(mainlytheeventorganizer)tobeabletocalltheOutlookAPIwithitstoken"""
        returnuser_id.with_user(user_id)

    @after_commit
    def_microsoft_delete(self,user_id,event_id,timeout=TIMEOUT):
        """
        OncetheeventhasbeenreallyremovedfromtheFlectradatabase,removeitfromtheOutlookcalendar.

        Notethatallselfattributestouseinthismethodmustbeprovidedasmethodparametersbecause
        'self'won'texistwhenthismethodwillbereallycalleddueto@after_commitdecorator.
        """
        microsoft_service=self._get_microsoft_service()
        withmicrosoft_calendar_token(self._impersonate_user(user_id).sudo())astoken:
            iftoken:
                microsoft_service.delete(event_id,token=token,timeout=timeout)

    @after_commit
    def_microsoft_patch(self,user_id,event_id,values,timeout=TIMEOUT):
        """
        OncetheeventhasbeenreallymodifiedintheFlectradatabase,modifyitintheOutlookcalendar.

        Notethatallselfattributestouseinthismethodmustbeprovidedasmethodparametersbecause
        'self'mayhavebeenmodifiedbetweenthecallof'_microsoft_patch'anditsexecution,
        dueto@after_commitdecorator.
        """
        microsoft_service=self._get_microsoft_service()
        withmicrosoft_calendar_token(self._impersonate_user(user_id).sudo())astoken:
            iftoken:
                self._ensure_attendees_have_email()
                res=microsoft_service.patch(event_id,values,token=token,timeout=timeout)
                self.write({
                    'need_sync_m':notres,
                })

    @after_commit
    def_microsoft_insert(self,values,timeout=TIMEOUT):
        """
        OncetheeventhasbeenreallyaddedintheFlectradatabase,additintheOutlookcalendar.

        Notethatallselfattributestouseinthismethodmustbeprovidedasmethodparametersbecause
        'self'mayhavebeenmodifiedbetweenthecallof'_microsoft_insert'anditsexecution,
        dueto@after_commitdecorator.
        """
        ifnotvalues:
            return
        microsoft_service=self._get_microsoft_service()
        withmicrosoft_calendar_token(self.env.user.sudo())astoken:
            iftoken:
                self._ensure_attendees_have_email()
                event_id,uid=microsoft_service.insert(values,token=token,timeout=timeout)
                self.write({
                    'microsoft_id':combine_ids(event_id,uid),
                    'need_sync_m':False,
                })

    def_microsoft_attendee_answer(self,answer,params,timeout=TIMEOUT):
        ifnotanswer:
            return
        microsoft_service=self._get_microsoft_service()
        withmicrosoft_calendar_token(self.env.user.sudo())astoken:
            iftoken:
                self._ensure_attendees_have_email()
                microsoft_service.answer(
                    self.ms_organizer_event_id,
                    answer,params,token=token,timeout=timeout
                )
                self.write({
                    'need_sync_m':False,
                })

    def_get_microsoft_records_to_sync(self,full_sync=False):
        """
        ReturnrecordsthatshouldbesyncedfromFlectratoMicrosoft
        :paramfull_sync:IfTrue,alleventsattendedbytheuserarereturned
        :return:events
        """
        domain=self._get_microsoft_sync_domain()
        ifnotfull_sync:
            is_active_clause=(self._active_name,'=',True)ifself._active_nameelseexpression.TRUE_LEAF
            domain=expression.AND([domain,[
                '|',
                '&',('ms_universal_event_id','=',False),is_active_clause,
                ('need_sync_m','=',True),
            ]])
        returnself.with_context(active_test=False).search(domain)

    @api.model
    def_microsoft_to_flectra_values(
        self,microsoft_event:MicrosoftEvent,default_reminders=(),default_values=None,with_ids=False
    ):
        """
        ImplementsthismethodtoreturnadictofFlectravaluescorresponding
        totheMicrosofteventgivenasparameter
        :return:dictofFlectraformattedvalues
        """
        raiseNotImplementedError()

    def_microsoft_values(self,fields_to_sync):
        """
        Implementsthismethodtoreturnadictwithvaluesformatted
        accordingtotheMicrosoftCalendarAPI
        :return:dictofMicrosoftformattedvalues
        """
        raiseNotImplementedError()

    def_ensure_attendees_have_email(self):
        raiseNotImplementedError()

    def_get_microsoft_sync_domain(self):
        """
        Returnadomainusedtosearchrecordstosynchronize.
        e.g.returnadomaintosynchronizerecordsownedbythecurrentuser.
        """
        raiseNotImplementedError()

    def_get_microsoft_synced_fields(self):
        """
        Returnasetoffieldnames.Changingoneofthesefields
        markstherecordtobere-synchronized.
        """
        raiseNotImplementedError()
