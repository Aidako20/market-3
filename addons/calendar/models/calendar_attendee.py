#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importuuid
importbase64
importlogging

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError

_logger=logging.getLogger(__name__)


classAttendee(models.Model):
    """CalendarAttendeeInformation"""
    _name='calendar.attendee'
    _rec_name='common_name'
    _description='CalendarAttendeeInformation'

    def_default_access_token(self):
        returnuuid.uuid4().hex

    STATE_SELECTION=[
        ('needsAction','NeedsAction'),
        ('tentative','Uncertain'),
        ('declined','Declined'),
        ('accepted','Accepted'),
    ]

    event_id=fields.Many2one(
        'calendar.event','Meetinglinked',required=True,ondelete='cascade')
    partner_id=fields.Many2one('res.partner','Contact',required=True,readonly=True)
    state=fields.Selection(STATE_SELECTION,string='Status',readonly=True,default='needsAction',
                             help="Statusoftheattendee'sparticipation")
    common_name=fields.Char('Commonname',compute='_compute_common_name',store=True)
    email=fields.Char('Email',related='partner_id.email',help="EmailofInvitedPerson")
    availability=fields.Selection(
        [('free','Free'),('busy','Busy')],'Free/Busy',readonly=True)
    access_token=fields.Char('InvitationToken',default=_default_access_token)
    recurrence_id=fields.Many2one('calendar.recurrence',related='event_id.recurrence_id')

    @api.depends('partner_id','partner_id.name','email')
    def_compute_common_name(self):
        forattendeeinself:
            attendee.common_name=attendee.partner_id.nameorattendee.email

    @api.model_create_multi
    defcreate(self,vals_list):
        forvaluesinvals_list:
            #bydefault,ifnostateisgivenfortheattendeecorrespondingtothecurrentuser
            #thatmeanshe'stheeventorganizersowecansethisstateto"accepted"
            if'state'notinvaluesandvalues.get('partner_id')==self.env.user.partner_id.id:
                values['state']='accepted'
            ifnotvalues.get("email")andvalues.get("common_name"):
                common_nameval=values.get("common_name").split(':')
                email=[xforxincommon_namevalif'@'inx]
                values['email']=email[0]ifemailelse''
                values['common_name']=values.get("common_name")
        attendees=super().create(vals_list)
        attendees._subscribe_partner()
        returnattendees

    defunlink(self):
        self._unsubscribe_partner()
        returnsuper().unlink()

    def_subscribe_partner(self):
        foreventinself.event_id:
            partners=(event.attendee_ids&self).partner_id-event.message_partner_ids
            #currentuserisautomaticallyaddedasfollowers,don'taddittwice.
            partners-=self.env.user.partner_id
            event.message_subscribe(partner_ids=partners.ids)

    def_unsubscribe_partner(self):
        foreventinself.event_id:
            partners=(event.attendee_ids&self).partner_id&event.message_partner_ids
            event.message_unsubscribe(partner_ids=partners.ids)

    @api.returns('self',lambdavalue:value.id)
    defcopy(self,default=None):
        raiseUserError(_('Youcannotduplicateacalendarattendee.'))

    def_send_mail_to_attendees(self,template_xmlid,force_send=False,ignore_recurrence=False):
        """Sendmailforeventinvitationtoeventattendees.
            :paramtemplate_xmlid:xmlidoftheemailtemplatetousetosendtheinvitation
            :paramforce_send:ifsettoTrue,themail(s)willbesentimmediately(insteadofthenextqueueprocessing)
            :paramignore_recurrence:ignoreeventrecurrence
        """
        res=False

        ifself.env['ir.config_parameter'].sudo().get_param('calendar.block_mail')orself._context.get("no_mail_to_attendees"):
            returnres

        calendar_view=self.env.ref('calendar.view_calendar_event_calendar')
        invitation_template=self.env.ref(template_xmlid,raise_if_not_found=False)
        ifnotinvitation_template:
            _logger.warning("Template%scouldnotbefound.%snotnotified."%(template_xmlid,self))
            return
        #geticsfileforallmeetings
        ics_files=self.mapped('event_id')._get_ics_file()

        #preparerenderingcontextformailtemplate
        rendering_context=dict(self._context)
        rendering_context.update({
            'colors':self._prepare_notification_calendar_colors(),
            'ignore_recurrence':ignore_recurrence,
            'action_id':self.env['ir.actions.act_window'].sudo().search([('view_id','=',calendar_view.id)],limit=1).id,
            'dbname':self._cr.dbname,
            'base_url':self.env['ir.config_parameter'].sudo().get_param('web.base.url',default='http://localhost:7073'),
        })

        self._notify_attendees(ics_files,invitation_template,rendering_context,force_send)

    def_notify_attendees(self,ics_files,mail_template,rendering_context,force_send):
        forattendeeinself:
            ifattendee.emailandattendee.partner_id!=self.env.user.partner_id:
                #FIXME:isics_filetextorbytes?
                event_id=attendee.event_id.id
                ics_file=ics_files.get(event_id)

                attachment_values=[]
                ifics_file:
                    attachment_values=attendee._prepare_notification_attachment_values(ics_file)
                try:
                    body=mail_template.with_context(rendering_context)._render_field(
                        'body_html',
                        attendee.ids,
                        compute_lang=True,
                        post_process=True)[attendee.id]
                exceptUserError: #TOBEREMOVEDINMASTER
                    body=mail_template.sudo().with_context(rendering_context)._render_field(
                        'body_html',
                        attendee.ids,
                        compute_lang=True,
                        post_process=True)[attendee.id]
                subject=mail_template.with_context(safe=True)._render_field(
                    'subject',
                    attendee.ids,
                    compute_lang=True)[attendee.id]
                attendee.event_id.with_context(no_document=True).message_notify(
                    email_from=attendee.event_id.user_id.email_formattedorself.env.user.email_formatted,
                    author_id=attendee.event_id.user_id.partner_id.idorself.env.user.partner_id.id,
                    body=body,
                    subject=subject,
                    partner_ids=attendee.partner_id.ids,
                    email_layout_xmlid='mail.mail_notification_light',
                    attachment_ids=attachment_values,
                    force_send=force_send)

    def_prepare_notification_calendar_colors(self):
        return{
            'needsAction':'grey',
            'accepted':'green',
            'tentative':'#FFFF00',
            'declined':'red'
        }

    def_prepare_notification_attachment_values(self,ics_file):
        return[
            (0,0,{'name':'invitation.ics',
                    'mimetype':'text/calendar',
                    'datas':base64.b64encode(ics_file)})
        ]

    defdo_tentative(self):
        """MakeseventinvitationasTentative."""
        returnself.write({'state':'tentative'})

    defdo_accept(self):
        """MarkseventinvitationasAccepted."""
        forattendeeinself:
            attendee.event_id.message_post(
                body=_("%shasacceptedinvitation")%(attendee.common_name),
                subtype_xmlid="calendar.subtype_invitation")
        returnself.write({'state':'accepted'})

    defdo_decline(self):
        """MarkseventinvitationasDeclined."""
        forattendeeinself:
            attendee.event_id.message_post(
                body=_("%shasdeclinedinvitation")%(attendee.common_name),
                subtype_xmlid="calendar.subtype_invitation")
        returnself.write({'state':'declined'})
