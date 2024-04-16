#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
importrequests
fromflectra.addons.microsoft_calendar.models.microsoft_syncimportmicrosoft_calendar_token
fromdatetimeimporttimedelta

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError
fromflectra.loglevelsimportexception_to_unicode
fromflectra.addons.microsoft_account.models.microsoft_serviceimportMICROSOFT_TOKEN_ENDPOINT
fromflectra.addons.microsoft_calendar.utils.microsoft_calendarimportInvalidSyncToken

_logger=logging.getLogger(__name__)


classUser(models.Model):
    _inherit='res.users'

    microsoft_calendar_sync_token=fields.Char('MicrosoftNextSyncToken',copy=False)

    def_microsoft_calendar_authenticated(self):
        returnbool(self.sudo().microsoft_calendar_rtoken)

    def_get_microsoft_calendar_token(self):
        self.ensure_one()
        ifself.microsoft_calendar_rtokenandnotself._is_microsoft_calendar_valid():
            self._refresh_microsoft_calendar_token()
        returnself.microsoft_calendar_token

    def_is_microsoft_calendar_valid(self):
        returnself.microsoft_calendar_token_validityandself.microsoft_calendar_token_validity>=(fields.Datetime.now()+timedelta(minutes=1))

    def_refresh_microsoft_calendar_token(self):
        self.ensure_one()
        get_param=self.env['ir.config_parameter'].sudo().get_param
        client_id=get_param('microsoft_calendar_client_id')
        client_secret=get_param('microsoft_calendar_client_secret')

        ifnotclient_idornotclient_secret:
            raiseUserError(_("TheaccountfortheOutlookCalendarserviceisnotconfigured."))

        headers={"content-type":"application/x-www-form-urlencoded"}
        data={
            'refresh_token':self.microsoft_calendar_rtoken,
            'client_id':client_id,
            'client_secret':client_secret,
            'grant_type':'refresh_token',
        }

        try:
            dummy,response,dummy=self.env['microsoft.service']._do_request(
                MICROSOFT_TOKEN_ENDPOINT,params=data,headers=headers,method='POST',preuri=''
            )
            ttl=response.get('expires_in')
            self.write({
                'microsoft_calendar_token':response.get('access_token'),
                'microsoft_calendar_token_validity':fields.Datetime.now()+timedelta(seconds=ttl),
            })
        exceptrequests.HTTPErroraserror:
            iferror.response.status_codein(400,401): #invalidgrantorinvalidclient
                #Deleterefreshtokenandmakesureit'scommited
                self.env.cr.rollback()
                self.write({
                    'microsoft_calendar_rtoken':False,
                    'microsoft_calendar_token':False,
                    'microsoft_calendar_token_validity':False,
                    'microsoft_calendar_sync_token':False,
                })
                self.env.cr.commit()
            error_key=error.response.json().get("error","nc")
            error_msg=_(
                "Anerroroccurredwhilegeneratingthetoken.Yourauthorizationcodemaybeinvalidorhasalreadyexpired[%s]."
                "YoushouldcheckyourClientIDandsecretontheMicrosoftAzureportalortrytostopandrestartyourcalendarsynchronisation.",
                error_key)
            raiseUserError(error_msg)

    def_sync_microsoft_calendar(self):
        self.ensure_one()
        calendar_service=self.env["calendar.event"]._get_microsoft_service()
        full_sync=notbool(self.microsoft_calendar_sync_token)
        withmicrosoft_calendar_token(self)astoken:
            try:
                events,next_sync_token=calendar_service.get_events(self.microsoft_calendar_sync_token,token=token)
            exceptInvalidSyncToken:
                events,next_sync_token=calendar_service.get_events(token=token)
                full_sync=True
        self.microsoft_calendar_sync_token=next_sync_token

        #Microsoft->Flectra
        synced_events,synced_recurrences=self.env['calendar.event']._sync_microsoft2flectra(events)ifeventselse(self.env['calendar.event'],self.env['calendar.recurrence'])

        #Flectra->Microsoft
        recurrences=self.env['calendar.recurrence']._get_microsoft_records_to_sync(full_sync=full_sync)
        recurrences-=synced_recurrences
        recurrences._sync_flectra2microsoft()
        synced_events|=recurrences.calendar_event_ids

        events=self.env['calendar.event']._get_microsoft_records_to_sync(full_sync=full_sync)
        (events-synced_events)._sync_flectra2microsoft()

        returnbool(events|synced_events)orbool(recurrences|synced_recurrences)

    @api.model
    def_sync_all_microsoft_calendar(self):
        """Cronjob"""
        users=self.env['res.users'].search([('microsoft_calendar_rtoken','!=',False)])
        foruserinusers:
            _logger.info("CalendarSynchro-Startingsynchronizationfor%s",user)
            try:
                user.with_user(user).sudo()._sync_microsoft_calendar()
                self.env.cr.commit()
            exceptExceptionase:
                _logger.exception("[%s]CalendarSynchro-Exception:%s!",user,exception_to_unicode(e))
                self.env.cr.rollback()
