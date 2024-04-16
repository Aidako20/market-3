#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporthttp
fromflectra.httpimportrequest


classMicrosoftCalendarController(http.Controller):

    @http.route('/microsoft_calendar/sync_data',type='json',auth='user')
    defsync_data(self,model,**kw):
        """Thisroute/functioniscalledwhenwewanttosynchronizeFlectra
            calendarwithMicrosoftCalendar.
            Functionreturnadictionarywiththestatus: need_config_from_admin,need_auth,
            need_refresh,sync_stopped,successifnotcalendar_event
            Thedictionarymaycontainsanurl,toallowFlectraClienttoredirectuseron
            thisURLforauthorizationforexample
        """
        ifmodel=='calendar.event':
            MicrosoftCal=request.env["calendar.event"]._get_microsoft_service()

            #CheckingthatadminhavealreadyconfiguredMicrosoftAPIformicrosoftsynchronization!
            client_id=request.env['ir.config_parameter'].sudo().get_param('microsoft_calendar_client_id')

            ifnotclient_idorclient_id=='':
                action_id=''
                ifMicrosoftCal._can_authorize_microsoft(request.env.user):
                    action_id=request.env.ref('base_setup.action_general_configuration').id
                return{
                    "status":"need_config_from_admin",
                    "url":'',
                    "action":action_id
                }

            #CheckingthatuserhavealreadyacceptedFlectratoaccesshiscalendar!
            ifnotMicrosoftCal.is_authorized(request.env.user):
                url=MicrosoftCal._microsoft_authentication_url(from_url=kw.get('fromurl'))
                return{
                    "status":"need_auth",
                    "url":url
                }
            #IfAppauthorized,anduseraccessaccepted,Welaunchthesynchronization
            need_refresh=request.env.user.sudo()._sync_microsoft_calendar()
            return{
                "status":"need_refresh"ifneed_refreshelse"no_new_event_from_microsoft",
                "url":''
            }

        return{"status":"success"}
