#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporthttp
fromflectra.httpimportrequest
fromflectra.addons.google_calendar.utils.google_calendarimportGoogleCalendarService


classGoogleCalendarController(http.Controller):

    @http.route('/google_calendar/sync_data',type='json',auth='user')
    defsync_data(self,model,**kw):
        """Thisroute/functioniscalledwhenwewanttosynchronizeFlectra
            calendarwithGoogleCalendar.
            Functionreturnadictionarywiththestatus: need_config_from_admin,need_auth,
            need_refresh,successifnotcalendar_event
            Thedictionarymaycontainsanurl,toallowFlectraClienttoredirectuseron
            thisURLforauthorizationforexample
        """
        ifmodel=='calendar.event':
            base_url=request.httprequest.url_root.strip('/')
            GoogleCal=GoogleCalendarService(request.env['google.service'].with_context(base_url=base_url))

            #CheckingthatadminhavealreadyconfiguredGoogleAPIforgooglesynchronization!
            client_id=request.env['ir.config_parameter'].sudo().get_param('google_calendar_client_id')

            ifnotclient_idorclient_id=='':
                action_id=''
                ifGoogleCal._can_authorize_google(request.env.user):
                    action_id=request.env.ref('base_setup.action_general_configuration').id
                return{
                    "status":"need_config_from_admin",
                    "url":'',
                    "action":action_id
                }

            #CheckingthatuserhavealreadyacceptedFlectratoaccesshiscalendar!
            ifnotGoogleCal.is_authorized(request.env.user):
                url=GoogleCal._google_authentication_url(from_url=kw.get('fromurl'))
                return{
                    "status":"need_auth",
                    "url":url
                }
            #IfAppauthorized,anduseraccessaccepted,Welaunchthesynchronization
            need_refresh=request.env.user.sudo()._sync_google_calendar(GoogleCal)
            return{
                "status":"need_refresh"ifneed_refreshelse"no_new_event_from_google",
                "url":''
            }

        return{"status":"success"}
