#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importwerkzeug

importflectra.httpashttp

fromflectra.httpimportrequest
fromflectra.tools.miscimportget_lang


classCalendarController(http.Controller):

    #YTINote:Keepidandkwargsonlyforretrocompatibilitypurpose
    @http.route('/calendar/meeting/accept',type='http',auth="calendar")
    defaccept_meeting(self,token,id,**kwargs):
        attendee=request.env['calendar.attendee'].sudo().search([
            ('access_token','=',token),
            ('state','!=','accepted')])
        attendee.do_accept()
        returnself.view_meeting(token,id)

    @http.route('/calendar/recurrence/accept',type='http',auth="calendar")
    defaccept_recurrence(self,token,id,**kwargs):
        attendee=request.env['calendar.attendee'].sudo().search([
            ('access_token','=',token),
            ('state','!=','accepted')])
        ifattendee:
            attendees=request.env['calendar.attendee'].sudo().search([
                ('event_id','in',attendee.event_id.recurrence_id.calendar_event_ids.ids),
                ('partner_id','=',attendee.partner_id.id),
                ('state','!=','accepted'),
            ])
            attendees.do_accept()
        returnself.view_meeting(token,id)

    @http.route('/calendar/meeting/decline',type='http',auth="calendar")
    defdecline_meeting(self,token,id,**kwargs):
        attendee=request.env['calendar.attendee'].sudo().search([
            ('access_token','=',token),
            ('state','!=','declined')])
        attendee.do_decline()
        returnself.view_meeting(token,id)

    @http.route('/calendar/recurrence/decline',type='http',auth="calendar")
    defdecline_recurrence(self,token,id,**kwargs):
        attendee=request.env['calendar.attendee'].sudo().search([
            ('access_token','=',token),
            ('state','!=','declined')])
        ifattendee:
            attendees=request.env['calendar.attendee'].sudo().search([
                ('event_id','in',attendee.event_id.recurrence_id.calendar_event_ids.ids),
                ('partner_id','=',attendee.partner_id.id),
                ('state','!=','declined'),
            ])
            attendees.do_decline()
        returnself.view_meeting(token,id)

    @http.route('/calendar/meeting/view',type='http',auth="calendar")
    defview_meeting(self,token,id,**kwargs):
        attendee=request.env['calendar.attendee'].sudo().search([
            ('access_token','=',token),
            ('event_id','=',int(id))])
        ifnotattendee:
            returnrequest.not_found()
        timezone=attendee.partner_id.tz
        lang=attendee.partner_id.langorget_lang(request.env).code
        event=request.env['calendar.event'].with_context(tz=timezone,lang=lang).sudo().browse(int(id))
        company=event.user_idandevent.user_id.company_idorevent.create_uid.company_id

        #Ifuserisinternalandlogged,redirecttoformviewofevent
        #otherwise,displaythesimplifyedwebpagewitheventinformations
        ifrequest.session.uidandrequest.env['res.users'].browse(request.session.uid).user_has_groups('base.group_user'):
            returnwerkzeug.utils.redirect('/web?db=%s#id=%s&view_type=form&model=calendar.event'%(request.env.cr.dbname,id))

        #NOTE:wedon'tuserequest.render()since:
        #-weneedatemplaterenderingwhichisnotlazy,torenderbeforecursorclosing
        #-weneedtodisplaythetemplateinthelanguageoftheuser(notpossiblewith
        #  request.render())
        response_content=request.env['ir.ui.view'].with_context(lang=lang)._render_template(
            'calendar.invitation_page_anonymous',{
                'company':company,
                'event':event,
                'attendee':attendee,
            })
        returnrequest.make_response(response_content,headers=[('Content-Type','text/html')])

    #Functionused,inRPCtocheckevery5minutes,ifnotificationtodoforaneventornot
    @http.route('/calendar/notify',type='json',auth="user")
    defnotify(self):
        returnrequest.env['calendar.alarm_manager'].get_next_notif()

    @http.route('/calendar/notify_ack',type='json',auth="user")
    defnotify_ack(self):
        returnrequest.env['res.partner'].sudo()._set_calendar_last_notif_ack()
