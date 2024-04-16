#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromuuidimportuuid4
importrequests
importjson
importlogging

fromflectraimportapi,_
fromflectra.toolsimportexception_to_unicode
fromflectra.addons.google_calendar.utils.google_eventimportGoogleEvent
fromflectra.addons.google_account.models.google_serviceimportTIMEOUT


_logger=logging.getLogger(__name__)

defrequires_auth_token(func):
    defwrapped(self,*args,**kwargs):
        ifnotkwargs.get('token'):
            raiseAttributeError("Anauthenticationtokenisrequired")
        returnfunc(self,*args,**kwargs)
    returnwrapped

classInvalidSyncToken(Exception):
    pass

classGoogleCalendarService():

    def__init__(self,google_service):
        self.google_service=google_service

    @requires_auth_token
    defget_events(self,sync_token=None,token=None,timeout=TIMEOUT):
        url="/calendar/v3/calendars/primary/events"
        headers={'Content-type':'application/json'}
        params={'access_token':token}
        ifsync_token:
            params['syncToken']=sync_token
        try:
            status,data,time=self.google_service._do_request(url,params,headers,method='GET',timeout=timeout)
        exceptrequests.HTTPErrorase:
            ife.response.status_code==410and'fullSyncRequired'instr(e.response.content):
                raiseInvalidSyncToken("Invalidsynctoken.Fullsyncrequired")
            raisee

        events=data.get('items',[])
        next_page_token=data.get('nextPageToken')
        whilenext_page_token:
            params={'access_token':token,'pageToken':next_page_token}
            status,data,time=self.google_service._do_request(url,params,headers,method='GET',timeout=timeout)
            next_page_token=data.get('nextPageToken')
            events+=data.get('items',[])

        next_sync_token=data.get('nextSyncToken')
        default_reminders=data.get('defaultReminders')

        returnGoogleEvent(events),next_sync_token,default_reminders

    @requires_auth_token
    definsert(self,values,token=None,timeout=TIMEOUT):
        send_updates=self.google_service._context.get('send_updates',True)
        url="/calendar/v3/calendars/primary/events?sendUpdates=%s"%("all"ifsend_updateselse"none")
        headers={'Content-type':'application/json','Authorization':'Bearer%s'%token}
        ifnotvalues.get('id'):
            values['id']=uuid4().hex
        self.google_service._do_request(url,json.dumps(values),headers,method='POST',timeout=timeout)
        returnvalues['id']

    @requires_auth_token
    defpatch(self,event_id,values,token=None,timeout=TIMEOUT):
        url="/calendar/v3/calendars/primary/events/%s?sendUpdates=all"%event_id
        headers={'Content-type':'application/json','Authorization':'Bearer%s'%token}
        self.google_service._do_request(url,json.dumps(values),headers,method='PATCH',timeout=timeout)

    @requires_auth_token
    defdelete(self,event_id,token=None,timeout=TIMEOUT):
        url="/calendar/v3/calendars/primary/events/%s?sendUpdates=all"%event_id
        headers={'Content-type':'application/json'}
        params={'access_token':token}
        try:
            self.google_service._do_request(url,params,headers=headers,method='DELETE',timeout=timeout)
        exceptrequests.HTTPErrorase:
            #ForsomeunknownreasonGooglecanalsoreturna403responsewhentheeventisalreadycancelled.
            ife.response.status_codenotin(410,403):
                raisee
            _logger.info("Googleevent%swasalreadydeleted"%event_id)


    #################################
    ## MANAGECONNEXIONTOGMAIL ##
    #################################


    defis_authorized(self,user):
        returnbool(user.sudo().google_calendar_rtoken)

    def_get_calendar_scope(self,RO=False):
        readonly='.readonly'ifROelse''
        return'https://www.googleapis.com/auth/calendar%s'%(readonly)

    def_google_authentication_url(self,from_url='http://www.flectrahq.com'):
        returnself.google_service._get_authorize_uri(from_url,service='calendar',scope=self._get_calendar_scope())

    def_can_authorize_google(self,user):
        returnuser.has_group('base.group_erp_manager')
