#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
fromcontextlibimportcontextmanager
fromfunctoolsimportwraps
importrequests
importpytz
fromdateutil.parserimportparse

fromflectraimportapi,fields,models,registry,_
fromflectra.toolsimportormcache_context
fromflectra.exceptionsimportUserError
fromflectra.osvimportexpression

fromflectra.addons.google_calendar.utils.google_eventimportGoogleEvent
fromflectra.addons.google_calendar.utils.google_calendarimportGoogleCalendarService
fromflectra.addons.google_account.models.google_serviceimportTIMEOUT

_logger=logging.getLogger(__name__)


#APIrequestsaresenttoGoogleCalendarafterthecurrenttransactionends.
#ThisensureschangesaresenttoGoogleonlyiftheyreallyhappenedintheFlectradatabase.
#Itisparticularlyimportantforeventcreation,otherwisetheeventmightbecreated
#twiceinGoogleifthefirstcreationcrashedinFlectra.
defafter_commit(func):
    @wraps(func)
    defwrapped(self,*args,**kwargs):
        dbname=self.env.cr.dbname
        context=self.env.context
        uid=self.env.uid

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
defgoogle_calendar_token(user):
    try:
        yielduser._get_google_calendar_token()
    exceptrequests.HTTPErrorase:
        ife.response.status_code==401: #Invalidtoken.
            #Thetransactionshouldberolledback,buttheuser'stokens
            #shouldbereset.Theuserwillbeaskedtoauthenticateagainnexttime.
            #Rollbackmanuallyfirsttoavoidconcurrentaccesserrors/deadlocks.
            user.env.cr.rollback()
            withuser.pool.cursor()ascr:
                env=user.env(cr=cr)
                user.with_env(env)._set_auth_tokens(False,False,0)
        raisee

classGoogleSync(models.AbstractModel):
    _name='google.calendar.sync'
    _description="SynchronizearecordwithGoogleCalendar"

    google_id=fields.Char('GoogleCalendarId',copy=False)
    need_sync=fields.Boolean(default=True,copy=False)
    active=fields.Boolean(default=True)

    defwrite(self,vals):
        google_service=GoogleCalendarService(self.env['google.service'])
        if'google_id'invals:
            self._event_ids_from_google_ids.clear_cache(self)
        synced_fields=self._get_google_synced_fields()
        if'need_sync'notinvalsandvals.keys()&synced_fields:
            vals['need_sync']=True

        result=super().write(vals)
        forrecordinself.filtered('need_sync'):
            ifrecord.google_id:
                record.with_user(record._get_event_user())._google_patch(google_service,record.google_id,record._google_values(),timeout=3)

        returnresult

    @api.model_create_multi
    defcreate(self,vals_list):
        ifany(vals.get('google_id')forvalsinvals_list):
            self._event_ids_from_google_ids.clear_cache(self)
        records=super().create(vals_list)

        google_service=GoogleCalendarService(self.env['google.service'])
        records_to_sync=records.filtered(lambdar:r.need_syncandr.active)
        forrecordinrecords_to_sync:
            record.with_user(record._get_event_user())._google_insert(google_service,record._google_values(),timeout=3)
        returnrecords

    defunlink(self):
        """Wecan'tdeleteaneventthatisalsoinGoogleCalendar.Otherwisewewould
        havenocluethattheeventmustmustdeletedfromGoogleCalendaratthenextsync.
        """
        synced=self.filtered('google_id')
        #LULTODOfindawaytogetridofthiscontextkey
        ifself.env.context.get('archive_on_error')andself._active_name:
            synced.write({self._active_name:False})
            self=self-synced
        elifsynced:
            #Sincewecannotdeletesuchanevent(seemethodcomment),wearchiveit.
            #NoticethatarchivinganeventwilldeletetheassociatedeventonGoogle.
            #Then,sinceithasbeendeletedonGoogle,theeventisalsodeletedonFlectraDB(_sync_google2flectra).
            self.action_archive()
            returnTrue
        returnsuper().unlink()

    def_from_google_ids(self,google_ids):
        ifnotgoogle_ids:
            returnself.browse()
        returnself.browse(self._event_ids_from_google_ids(google_ids))

    @api.model
    @ormcache_context('google_ids',keys=('active_test',))
    def_event_ids_from_google_ids(self,google_ids):
        returnself.search([('google_id','in',google_ids)]).ids

    def_sync_flectra2google(self,google_service:GoogleCalendarService):
        ifnotself:
            return
        ifself._active_name:
            records_to_sync=self.filtered(self._active_name)
        else:
            records_to_sync=self
        cancelled_records=self-records_to_sync

        updated_records=records_to_sync.filtered('google_id')
        new_records=records_to_sync-updated_records
        forrecordincancelled_records.filtered('google_id'):
            record.with_user(record._get_event_user())._google_delete(google_service,record.google_id)
        forrecordinnew_records:
            record.with_user(record._get_event_user())._google_insert(google_service,record._google_values())
        forrecordinupdated_records:
            record.with_user(record._get_event_user())._google_patch(google_service,record.google_id,record._google_values())

    def_cancel(self):
        self.google_id=False
        self.unlink()

    @api.model
    def_sync_google2flectra(self,google_events:GoogleEvent,default_reminders=()):
        """SynchronizeGooglerecurrencesinFlectra.Createsnewrecurrences,updates
        existingones.

        :paramgoogle_recurrences:GooglerecurrencestosynchronizeinFlectra
        :return:synchronizedflectrarecurrences
        """
        existing=google_events.exists(self.env)
        new=google_events-existing-google_events.cancelled()

        flectra_values=[
            dict(self._flectra_values(e,default_reminders),need_sync=False)
            foreinnew
        ]
        new_flectra=self.with_context(dont_notify=True)._create_from_google(new,flectra_values)
        #Syncedrecurrencesattendeeswillbenotifiedonce_apply_recurrenceiscalled.
        ifnotself._context.get("dont_notify")andall(note.is_recurrence()foreingoogle_events):
            new_flectra._notify_attendees()

        cancelled=existing.cancelled()
        cancelled_flectra=self.browse(cancelled.flectra_ids(self.env))
        cancelled_flectra._cancel()
        synced_records=(new_flectra+cancelled_flectra).with_context(dont_notify=self._context.get("dont_notify",False))
        forgeventinexisting-cancelled:
            #Lastupdatedwins.
            #Thiscouldbedangerousifgoogleservertimeandflectraservertimearedifferent
            updated=parse(gevent.updated)
            flectra_record=self.browse(gevent.flectra_id(self.env))
            #Migrationfrom13.4doesnotfillwrite_date.Therefore,weforcetheupdatefromGoogle.
            ifnotflectra_record.write_dateorupdated>=pytz.utc.localize(flectra_record.write_date):
                vals=dict(self._flectra_values(gevent,default_reminders),need_sync=False)
                flectra_record._write_from_google(gevent,vals)
                synced_records|=flectra_record

        returnsynced_records

    @after_commit
    def_google_delete(self,google_service:GoogleCalendarService,google_id,timeout=TIMEOUT):
        withgoogle_calendar_token(self.env.user.sudo())astoken:
            iftoken:
                google_service.delete(google_id,token=token,timeout=timeout)
                #Whentherecordhasbeendeletedonourside,weneedtodeleteitongooglebutwedon'twant
                #toraiseanerrorbecausetherecorddon'texistsanymore.
                self.exists().need_sync=False

    @after_commit
    def_google_patch(self,google_service:GoogleCalendarService,google_id,values,timeout=TIMEOUT):
        withgoogle_calendar_token(self.env.user.sudo())astoken:
            iftoken:
                google_service.patch(google_id,values,token=token,timeout=timeout)
                self.need_sync=False

    @after_commit
    def_google_insert(self,google_service:GoogleCalendarService,values,timeout=TIMEOUT):
        ifnotvalues:
            return
        withgoogle_calendar_token(self.env.user.sudo())astoken:
            iftoken:
                send_updates=self._context.get('send_updates',True)
                google_service.google_service=google_service.google_service.with_context(send_updates=send_updates)
                google_id=google_service.insert(values,token=token,timeout=timeout)
                self.write({
                    'google_id':google_id,
                    'need_sync':False,
                })

    def_get_records_to_sync(self,full_sync=False):
        """ReturnrecordsthatshouldbesyncedfromFlectratoGoogle

        :paramfull_sync:IfTrue,alleventsattendedbytheuserarereturned
        :return:events
        """
        domain=self._get_sync_domain()
        ifnotfull_sync:
            is_active_clause=(self._active_name,'=',True)ifself._active_nameelseexpression.TRUE_LEAF
            domain=expression.AND([domain,[
                '|',
                    '&',('google_id','=',False),is_active_clause,
                    ('need_sync','=',True),
            ]])
        returnself.with_context(active_test=False).search(domain)

    def_write_from_google(self,gevent,vals):
        self.write(vals)

    @api.model
    def_create_from_google(self,gevents,vals_list):
        returnself.create(vals_list)

    @api.model
    def_flectra_values(self,google_event:GoogleEvent,default_reminders=()):
        """ImplementsthismethodtoreturnadictofFlectravaluescorresponding
        totheGoogleeventgivenasparameter
        :return:dictofFlectraformattedvalues
        """
        raiseNotImplementedError()

    def_google_values(self):
        """Implementsthismethodtoreturnadictwithvaluesformatted
        accordingtotheGoogleCalendarAPI
        :return:dictofGoogleformattedvalues
        """
        raiseNotImplementedError()

    def_get_sync_domain(self):
        """Returnadomainusedtosearchrecordstosynchronize.
        e.g.returnadomaintosynchronizerecordsownedbythecurrentuser.
        """
        raiseNotImplementedError()

    def_get_google_synced_fields(self):
        """Returnasetoffieldnames.Changingoneofthesefields
        markstherecordtobere-synchronized.
        """
        raiseNotImplementedError()

    def_notify_attendees(self):
        """Notifycalendareventpartners.
        Thisiscalledwhencreatingnewcalendareventsin_sync_google2flectra.
        Attheinitializationofasyncedcalendar,Flectrarequestsalleventsforaspecific
        GoogleCalendar.Amongthosetherewillprobablybelotsofeventsthatwillnevertriggersanotification
        (e.g.singleeventsthatoccuredinthepast).Processingalltheseeventsthroughthenotificationprocedure
        ofcalendar.event.createisapossibleperformancebottleneck.Thismethodaimedatalleviatingthat.
        """
        raiseNotImplementedError()

    def_get_event_user(self):
        """ReturnthecorrectusertosendtherequesttoGoogle.
        It'spossiblethatausercreatesaneventandsetsanotheruserastheorganizer.Usingself.env.userwill
        causesomeissues,andItmightnotbepossibletousethisuserforsendingtherequest,sothismethodgets
        theappropriateuseraccordingly.
        """
        raiseNotImplementedError()
