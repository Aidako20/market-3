#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
importrequests
fromflectra.addons.google_calendar.models.google_syncimportgoogle_calendar_token
fromdatetimeimporttimedelta


fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError
fromflectra.loglevelsimportexception_to_unicode
fromflectra.addons.google_account.models.google_serviceimportGOOGLE_TOKEN_ENDPOINT
fromflectra.addons.google_calendar.utils.google_calendarimportGoogleCalendarService,InvalidSyncToken

_logger=logging.getLogger(__name__)

classUser(models.Model):
    _inherit='res.users'

    google_calendar_rtoken=fields.Char('RefreshToken',copy=False,groups="base.group_system")
    google_calendar_token=fields.Char('Usertoken',copy=False,groups="base.group_system")
    google_calendar_token_validity=fields.Datetime('TokenValidity',copy=False)
    google_calendar_sync_token=fields.Char('NextSyncToken',copy=False)
    google_calendar_cal_id=fields.Char('CalendarID',copy=False,help='LastCalendarIDwhohasbeensynchronized.Ifitischanged,weremovealllinksbetweenGoogleIDandFlectraGoogleInternalID')

    def_set_auth_tokens(self,access_token,refresh_token,ttl):
        self.write({
            'google_calendar_rtoken':refresh_token,
            'google_calendar_token':access_token,
            'google_calendar_token_validity':fields.Datetime.now()+timedelta(seconds=ttl)ifttlelseFalse,
        })

    def_google_calendar_authenticated(self):
        returnbool(self.sudo().google_calendar_rtoken)

    def_get_google_calendar_token(self):
        self.ensure_one()
        ifself._is_google_calendar_valid():
            self._refresh_google_calendar_token()
        returnself.google_calendar_token

    def_is_google_calendar_valid(self):
        returnself.google_calendar_token_validityandself.google_calendar_token_validity<(fields.Datetime.now()+timedelta(minutes=1))

    def_refresh_google_calendar_token(self):
        #LULTODOsimilarcodeexistsingoogle_drive.Shouldbefactorizedingoogle_account
        self.ensure_one()
        get_param=self.env['ir.config_parameter'].sudo().get_param
        client_id=get_param('google_calendar_client_id')
        client_secret=get_param('google_calendar_client_secret')

        ifnotclient_idornotclient_secret:
            raiseUserError(_("TheaccountfortheGoogleCalendarserviceisnotconfigured."))

        headers={"content-type":"application/x-www-form-urlencoded"}
        data={
            'refresh_token':self.google_calendar_rtoken,
            'client_id':client_id,
            'client_secret':client_secret,
            'grant_type':'refresh_token',
        }

        try:
            dummy,response,dummy=self.env['google.service']._do_request(GOOGLE_TOKEN_ENDPOINT,params=data,headers=headers,method='POST',preuri='')
            ttl=response.get('expires_in')
            self.write({
                'google_calendar_token':response.get('access_token'),
                'google_calendar_token_validity':fields.Datetime.now()+timedelta(seconds=ttl),
            })
        exceptrequests.HTTPErroraserror:
            iferror.response.status_codein(400,401): #invalidgrantorinvalidclient
                #Deleterefreshtokenandmakesureit'scommited
                self.env.cr.rollback()
                self._set_auth_tokens(False,False,0)
                self.env.cr.commit()
            error_key=error.response.json().get("error","nc")
            error_msg=_("Somethingwentwrongduringyourtokengeneration.MaybeyourAuthorizationCodeisinvalidoralreadyexpired[%s]",error_key)
            raiseUserError(error_msg)

    def_sync_google_calendar(self,calendar_service:GoogleCalendarService):
        self.ensure_one()
        full_sync=notbool(self.google_calendar_sync_token)
        withgoogle_calendar_token(self)astoken:
            try:
                events,next_sync_token,default_reminders=calendar_service.get_events(self.google_calendar_sync_token,token=token)
            exceptInvalidSyncToken:
                events,next_sync_token,default_reminders=calendar_service.get_events(token=token)
                full_sync=True
        self.google_calendar_sync_token=next_sync_token

        #Google->Flectra
        events.clear_type_ambiguity(self.env)
        recurrences=events.filter(lambdae:e.is_recurrence())
        synced_recurrences=self.env['calendar.recurrence']._sync_google2flectra(recurrences)
        synced_events=self.env['calendar.event']._sync_google2flectra(events-recurrences,default_reminders=default_reminders)

        #Flectra->Google
        send_updates=notfull_sync
        recurrences=self.env['calendar.recurrence']._get_records_to_sync(full_sync=full_sync)
        recurrences-=synced_recurrences
        recurrences.with_context(send_updates=send_updates)._sync_flectra2google(calendar_service)
        synced_events|=recurrences.calendar_event_ids-recurrences._get_outliers()
        synced_events|=synced_recurrences.calendar_event_ids-synced_recurrences._get_outliers()
        events=self.env['calendar.event']._get_records_to_sync(full_sync=full_sync)
        (events-synced_events).with_context(send_updates=send_updates)._sync_flectra2google(calendar_service)

        returnbool(events|synced_events)orbool(recurrences|synced_recurrences)

    @api.model
    def_sync_all_google_calendar(self):
        """Cronjob"""
        users=self.env['res.users'].search([('google_calendar_rtoken','!=',False)])
        google=GoogleCalendarService(self.env['google.service'])
        foruserinusers:
            _logger.info("CalendarSynchro-Startingsynchronizationfor%s",user)
            try:
                user.with_user(user).sudo()._sync_google_calendar(google)
                self.env.cr.commit()
            exceptExceptionase:
                _logger.exception("[%s]CalendarSynchro-Exception:%s!",user,exception_to_unicode(e))
                self.env.cr.rollback()
