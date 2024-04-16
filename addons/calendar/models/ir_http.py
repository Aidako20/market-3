#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromwerkzeug.exceptionsimportBadRequest

fromflectraimportmodels
fromflectra.httpimportrequest


classIrHttp(models.AbstractModel):
    _inherit='ir.http'

    @classmethod
    def_auth_method_calendar(cls):
        token=request.params.get('token','')

        error_message=False

        attendee=request.env['calendar.attendee'].sudo().search([('access_token','=',token)],limit=1)
        ifnotattendee:
            error_message="""InvalidInvitationToken."""
        elifrequest.session.uidandrequest.session.login!='anonymous':
            #ifvalidsessionbutuserisnotmatch
            user=request.env['res.users'].sudo().browse(request.session.uid)
            ifattendee.partner_id!=user.partner_id:
                error_message="""Invitationcannotbeforwardedviaemail.Thisevent/meetingbelongsto%sandyouareloggedinas%s.Pleaseaskorganizertoaddyou."""%(attendee.email,user.email)
        iferror_message:
            raiseBadRequest(error_message)

        cls._auth_method_public()
