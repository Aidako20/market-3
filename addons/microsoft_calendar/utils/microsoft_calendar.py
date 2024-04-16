#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importrequests
importjson
importlogging

fromwerkzeugimporturls

fromflectraimportfields
fromflectra.addons.microsoft_calendar.utils.microsoft_eventimportMicrosoftEvent
fromflectra.addons.microsoft_account.models.microsoft_serviceimportTIMEOUT,RESOURCE_NOT_FOUND_STATUSES

_logger=logging.getLogger(__name__)

defrequires_auth_token(func):
    defwrapped(self,*args,**kwargs):
        ifnotkwargs.get('token'):
            raiseAttributeError("Anauthenticationtokenisrequired")
        returnfunc(self,*args,**kwargs)
    returnwrapped

classInvalidSyncToken(Exception):
    pass

#InOutlook,aneventcanbe:
#-a'singleInstance'event,
#-a'seriemaster'whichcontainsalltheinformationaboutaneventreccurrencesuchas
#-an'occurrence'whichisaneventfromareccurrence(serie)thatfollowsthisreccurrence
#-an'exception'whichisaneventfromareccurrence(serie)butsomedifferenceswiththereccurrencetemplate(couldbe
#  thename,thedayofoccurrence,...)
#
# Allthesekindsofeventsareidentifiedby:
# -aeventID(id)whichisspecifictoanOutlookcalendar.
# -aglobaleventID(iCalUId)whichiscommontoallOutlookcalendarscontainingthisevent.
#
# -'singleInstance'and'seriemaster'eventsareretrievedthroughtheend-point`/v1.0/me/calendarView/delta`whichprovides
# thelastmodified/deleteditemssincethelastsync(oralloftheseitemsatthefirsttime).
# -'occurrence'and'exception'eventsareretrievedthroughtheend-point`/v1.0/me/events/{serieMaster.id}/instances`,
# usingthecorrespondingseriemasterID.

classMicrosoftCalendarService():

    def__init__(self,microsoft_service):
        self.microsoft_service=microsoft_service

    @requires_auth_token
    def_get_events_from_paginated_url(self,url,token=None,params=None,timeout=TIMEOUT):
        """
        GetalistofeventsfromapaginatedURL.
        Eachpagecontainsalinktothenextpage,soloopoverallthepagestogetalltheevents.
        """
        headers={
            'Content-type':'application/json',
            'Authorization':'Bearer%s'%token,
            'Prefer':'outlook.body-content-type="text",odata.maxpagesize=50'
        }
        ifnotparams:
            params={
                'startDateTime':fields.Datetime.subtract(fields.Datetime.now(),years=2).strftime("%Y-%m-%dT00:00:00Z"),
                'endDateTime':fields.Datetime.add(fields.Datetime.now(),years=2).strftime("%Y-%m-%dT00:00:00Z"),
            }

        #getthefirstpageofevents
        _,data,_=self.microsoft_service._do_request(
            url,params,headers,method='GET',timeout=timeout
        )

        #andthen,looponotherpagestogetalltheevents
        events=data.get('value',[])
        next_page_token=data.get('@odata.nextLink')
        whilenext_page_token:
            _,data,_=self.microsoft_service._do_request(
                next_page_token,{},headers,preuri='',method='GET',timeout=timeout
            )
            next_page_token=data.get('@odata.nextLink')
            events+=data.get('value',[])

        token_url=data.get('@odata.deltaLink')
        next_sync_token=urls.url_parse(token_url).decode_query().get('$deltatoken',False)iftoken_urlelseNone

        returnevents,next_sync_token

    @requires_auth_token
    def_get_events_delta(self,sync_token=None,token=None,timeout=TIMEOUT):
        """
        Getasetofeventsthathavebeenadded,deletedorupdatedinatimerange.
        See:https://docs.microsoft.com/en-us/graph/api/event-delta?view=graph-rest-1.0&tabs=http
        """
        url="/v1.0/me/calendarView/delta"
        params={'$deltatoken':sync_token}ifsync_tokenelseNone

        try:
            events,next_sync_token=self._get_events_from_paginated_url(
                url,params=params,token=token,timeout=timeout)
        exceptrequests.HTTPErrorase:
            ife.response.status_code==410and'fullSyncRequired'instr(e.response.content)andsync_token:
                #retrywithafullsync
                returnself._get_events_delta(token=token,timeout=timeout)
            raisee

        #eventoccurrences(fromarecurrence)areretrievedseparatelytogetalltheirinfo,
        ##andmainlytheiCalUIdattributewhichisnotprovidedbythe'get_delta'apiendpoint
        events=[eforeineventsife.get('type')!='occurrence']

        returnMicrosoftEvent(events),next_sync_token

    @requires_auth_token
    def_get_occurrence_details(self,serieMasterId,token=None,timeout=TIMEOUT):
        """
        Getalloccurrencesdetailsfromaseriemaster.
        See:https://docs.microsoft.com/en-us/graph/api/event-list-instances?view=graph-rest-1.0&tabs=http
        """
        url=f"/v1.0/me/events/{serieMasterId}/instances"

        events,_=self._get_events_from_paginated_url(url,token=token,timeout=timeout)
        returnMicrosoftEvent(events)

    @requires_auth_token
    defget_events(self,sync_token=None,token=None,timeout=TIMEOUT):
        """
        Retrievealltheeventsthathavechanged(added/updated/removed)fromMicrosoftOutlook.
        Thisisdonein2steps:
        1)getmainchangedevents(sosingleeventsandseriemasters)
        2)getoccurrenceslinkedtoaseriemasters(toretrieveallneededdetailssuchasiCalUId)
        """
        events,next_sync_token=self._get_events_delta(sync_token=sync_token,token=token,timeout=timeout)

        #getoccurencesdetailsforallseriemasters
        formasterinfilter(lambdae:e.type=='seriesMaster',events):
            events|=self._get_occurrence_details(master.id,token=token,timeout=timeout)

        returnevents,next_sync_token

    @requires_auth_token
    definsert(self,values,token=None,timeout=TIMEOUT):
        url="/v1.0/me/calendar/events"
        headers={'Content-type':'application/json','Authorization':'Bearer%s'%token}
        _dummy,data,_dummy=self.microsoft_service._do_request(url,json.dumps(values),headers,method='POST',timeout=timeout)

        returndata['id'],data['iCalUId']

    @requires_auth_token
    defpatch(self,event_id,values,token=None,timeout=TIMEOUT):
        url="/v1.0/me/calendar/events/%s"%event_id
        headers={'Content-type':'application/json','Authorization':'Bearer%s'%token}
        try:
            status,_dummy,_dummy=self.microsoft_service._do_request(url,json.dumps(values),headers,method='PATCH',timeout=timeout)
        exceptrequests.HTTPError:
            _logger.info("Microsoftevent%shasnotbeenupdated",event_id)
            returnFalse

        returnstatusnotinRESOURCE_NOT_FOUND_STATUSES

    @requires_auth_token
    defdelete(self,event_id,token=None,timeout=TIMEOUT):
        url="/v1.0/me/calendar/events/%s"%event_id
        headers={'Authorization':'Bearer%s'%token}
        params={}
        try:
            status,_dummy,_dummy=self.microsoft_service._do_request(url,params,headers=headers,method='DELETE',timeout=timeout)
        exceptrequests.HTTPErrorase:
            #ForsomeunknownreasonMicrosoftcanalsoreturna403responsewhentheeventisalreadycancelled.
            status=e.response.status_code
            ifstatusin(410,403):
                _logger.info("Microsoftevent%swasalreadydeleted",event_id)
            else:
                raisee

        returnstatusnotinRESOURCE_NOT_FOUND_STATUSES

    @requires_auth_token
    defanswer(self,event_id,answer,values,token=None,timeout=TIMEOUT):
        url="/v1.0/me/calendar/events/%s/%s"%(event_id,answer)
        headers={'Content-type':'application/json','Authorization':'Bearer%s'%token}
        status,_dummy,_dummy=self.microsoft_service._do_request(url,json.dumps(values),headers,method='POST',timeout=timeout)

        returnstatusnotinRESOURCE_NOT_FOUND_STATUSES


    #####################################
    ## MANAGECONNEXIONTOMICROSOFT ##
    #####################################

    defis_authorized(self,user):
        returnbool(user.sudo().microsoft_calendar_rtoken)

    def_get_calendar_scope(self):
        return'offline_accessopenidCalendars.ReadWrite'

    def_microsoft_authentication_url(self,from_url='http://www.flectrahq.com'):
        returnself.microsoft_service._get_authorize_uri(from_url,service='calendar',scope=self._get_calendar_scope())

    def_can_authorize_microsoft(self,user):
        returnuser.has_group('base.group_erp_manager')
