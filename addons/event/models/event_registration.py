#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdateutil.relativedeltaimportrelativedelta

fromflectraimport_,api,fields,models,SUPERUSER_ID
fromflectra.toolsimportformat_datetime,email_normalize,email_normalize_all
fromflectra.exceptionsimportAccessError,ValidationError


classEventRegistration(models.Model):
    _name='event.registration'
    _description='EventRegistration'
    _inherit=['mail.thread','mail.activity.mixin']
    _order='iddesc'

    #event
    event_id=fields.Many2one(
        'event.event',string='Event',required=True,
        readonly=True,states={'draft':[('readonly',False)]})
    event_ticket_id=fields.Many2one(
        'event.event.ticket',string='EventTicket',readonly=True,ondelete='restrict',
        states={'draft':[('readonly',False)]})
    #utminformations
    utm_campaign_id=fields.Many2one('utm.campaign','Campaign', index=True,ondelete='setnull')
    utm_source_id=fields.Many2one('utm.source','Source',index=True,ondelete='setnull')
    utm_medium_id=fields.Many2one('utm.medium','Medium',index=True,ondelete='setnull')
    #attendee
    partner_id=fields.Many2one(
        'res.partner',string='Bookedby',
        states={'done':[('readonly',True)]})
    name=fields.Char(
        string='AttendeeName',index=True,
        compute='_compute_name',readonly=False,store=True,tracking=10)
    email=fields.Char(string='Email',compute='_compute_email',readonly=False,store=True,tracking=11)
    phone=fields.Char(string='Phone',compute='_compute_phone',readonly=False,store=True,tracking=12)
    mobile=fields.Char(string='Mobile',compute='_compute_mobile',readonly=False,store=True,tracking=13)
    #organization
    date_open=fields.Datetime(string='RegistrationDate',readonly=True,default=lambdaself:fields.Datetime.now()) #weirdcrashisdirectlynow
    date_closed=fields.Datetime(
        string='AttendedDate',compute='_compute_date_closed',
        readonly=False,store=True)
    event_begin_date=fields.Datetime(string="EventStartDate",related='event_id.date_begin',readonly=True)
    event_end_date=fields.Datetime(string="EventEndDate",related='event_id.date_end',readonly=True)
    company_id=fields.Many2one(
        'res.company',string='Company',related='event_id.company_id',
        store=True,readonly=True,states={'draft':[('readonly',False)]})
    state=fields.Selection([
        ('draft','Unconfirmed'),('cancel','Cancelled'),
        ('open','Confirmed'),('done','Attended')],
        string='Status',default='draft',readonly=True,copy=False,tracking=True)

    @api.onchange('partner_id')
    def_onchange_partner_id(self):
        """Keepanexplicitonchangeonpartner_id.Rationale:ifuserexplicitly
        changesthepartnerininterface,hewanttoupdatethewholecustomer
        information.Ifpartner_idisupdatedincode(e.g.updatingyourpersonal
        informationafterhavingregisteredinwebsite_event_sale)fieldswitha
        valueshouldnotberesetaswedon'tknowwhichoneistherightone.

        Inotherwords
          *computedfieldsbasedonpartner_idshouldonlyupdatemissing
            information.Indeedautomatedcodecannotdecidewhichinformation
            ismoreaccurate;
          *interfaceshouldallowtoupdateallcustomerrelatedinformation
            atonce.Weconsidereventusersreallywanttoupdateallfields
            relatedtothepartner;
        """
        forregistrationinself:
            ifregistration.partner_id:
                registration.update(registration._synchronize_partner_values(registration.partner_id))

    @api.depends('partner_id')
    def_compute_name(self):
        forregistrationinself:
            ifnotregistration.nameandregistration.partner_id:
                registration.name=registration._synchronize_partner_values(
                    registration.partner_id,
                    fnames=['name']
                ).get('name')orFalse

    @api.depends('partner_id')
    def_compute_email(self):
        forregistrationinself:
            ifnotregistration.emailandregistration.partner_id:
                registration.email=registration._synchronize_partner_values(
                    registration.partner_id,
                    fnames=['email']
                ).get('email')orFalse

    @api.depends('partner_id')
    def_compute_phone(self):
        forregistrationinself:
            ifnotregistration.phoneandregistration.partner_id:
                registration.phone=registration._synchronize_partner_values(
                    registration.partner_id,
                    fnames=['phone']
                ).get('phone')orFalse

    @api.depends('partner_id')
    def_compute_mobile(self):
        forregistrationinself:
            ifnotregistration.mobileandregistration.partner_id:
                registration.mobile=registration._synchronize_partner_values(
                    registration.partner_id,
                    fnames=['mobile']
                ).get('mobile')orFalse

    @api.depends('state')
    def_compute_date_closed(self):
        forregistrationinself:
            ifnotregistration.date_closed:
                ifregistration.state=='done':
                    registration.date_closed=fields.Datetime.now()
                else:
                    registration.date_closed=False

    @api.constrains('event_id','state')
    def_check_seats_limit(self):
        forregistrationinself:
            ifregistration.event_id.seats_limitedandregistration.event_id.seats_maxandregistration.event_id.seats_available<(1ifregistration.state=='draft'else0):
                raiseValidationError(_('Nomoreseatsavailableforthisevent.'))

    @api.constrains('event_ticket_id','state')
    def_check_ticket_seats_limit(self):
        forrecordinself:
            ifrecord.event_ticket_id.seats_maxandrecord.event_ticket_id.seats_available<0:
                raiseValidationError(_('Nomoreavailableseatsforthisticket'))

    @api.constrains('event_id','event_ticket_id')
    def_check_event_ticket(self):
        ifany(registration.event_id!=registration.event_ticket_id.event_idforregistrationinselfifregistration.event_ticket_id):
            raiseValidationError(_('Invalidevent/ticketchoice'))

    def_synchronize_partner_values(self,partner,fnames=None):
        iffnamesisNone:
            fnames=['name','email','phone','mobile']
        ifpartner:
            contact_id=partner.address_get().get('contact',False)
            ifcontact_id:
                contact=self.env['res.partner'].browse(contact_id)
                returndict((fname,contact[fname])forfnameinfnamesifcontact[fname])
        return{}

    #------------------------------------------------------------
    #CRUD
    #------------------------------------------------------------

    @api.model_create_multi
    defcreate(self,vals_list):
        registrations=super(EventRegistration,self).create(vals_list)
        ifregistrations._check_auto_confirmation():
            registrations.sudo().action_confirm()

        returnregistrations

    defwrite(self,vals):
        ret=super(EventRegistration,self).write(vals)

        ifvals.get('state')=='open':
            #auto-triggerafter_sub(onsubscribe)mailschedulers,ifneeded
            onsubscribe_schedulers=self.mapped('event_id.event_mail_ids').filtered(lambdas:s.interval_type=='after_sub')
            onsubscribe_schedulers.with_user(SUPERUSER_ID).execute()

        returnret

    defname_get(self):
        """Customname_getimplementationtobetterdifferentiateregistrations
        linkedtoagivenpartnerbutwithdifferentname(onepartnerbuying
        severalregistrations)

          *name,partner_idhasnoname->takename
          *partner_idhasname,namevoidorsame->takepartnername
          *bothhavename:partner+name
        """
        ret_list=[]
        forregistrationinself:
            ifregistration.partner_id.name:
                ifregistration.nameandregistration.name!=registration.partner_id.name:
                    name='%s,%s'%(registration.partner_id.name,registration.name)
                else:
                    name=registration.partner_id.name
            else:
                name=registration.name
            ret_list.append((registration.id,name))
        returnret_list

    def_check_auto_confirmation(self):
        ifany(notregistration.event_id.auto_confirmor
               (notregistration.event_id.seats_availableandregistration.event_id.seats_limited)forregistrationinself):
            returnFalse
        returnTrue

    #------------------------------------------------------------
    #ACTIONS/BUSINESS
    #------------------------------------------------------------

    defaction_set_draft(self):
        self.write({'state':'draft'})

    defaction_confirm(self):
        self.write({'state':'open'})

    defaction_set_done(self):
        """CloseRegistration"""
        self.write({'state':'done'})

    defaction_cancel(self):
        self.write({'state':'cancel'})

    def_message_get_suggested_recipients(self):
        recipients=super(EventRegistration,self)._message_get_suggested_recipients()
        public_users=self.env['res.users'].sudo()
        public_groups=self.env.ref("base.group_public",raise_if_not_found=False)
        ifpublic_groups:
            public_users=public_groups.sudo().with_context(active_test=False).mapped("users")
        try:
            forattendeeinself:
                is_public=attendee.sudo().with_context(active_test=False).partner_id.user_idsinpublic_usersifpublic_userselseFalse
                ifattendee.partner_idandnotis_public:
                    attendee._message_add_suggested_recipient(recipients,partner=attendee.partner_id,reason=_('Customer'))
                elifattendee.email:
                    attendee._message_add_suggested_recipient(recipients,email=attendee.email,reason=_('CustomerEmail'))
        exceptAccessError:    #noreadaccessrights->ignoresuggestedrecipients
            pass
        returnrecipients

    def_message_get_default_recipients(self):
        #Prioritizeregistrationemailoverpartner_id,whichmaybesharedwhenasingle
        #partnerbookedmultipleseats
        return{r.id:
            {
                'partner_ids':[],
                'email_to':','.join(email_normalize_all(r.email))orr.email,
                'email_cc':False,
            }forrinself
        }

    def_message_post_after_hook(self,message,msg_vals):
        ifself.emailandnotself.partner_id:
            #weconsiderthatpostingamessagewithaspecifiedrecipient(notafollower,aspecificone)
            #onadocumentwithoutcustomermeansthatitwascreatedthroughthechatterusing
            #suggestedrecipients.ThisheuristicallowstoavoiduglyhacksinJS.
            email_normalized=email_normalize(self.email)
            new_partner=message.partner_ids.filtered(
                lambdapartner:partner.email==self.emailor(email_normalizedandpartner.email_normalized==email_normalized)
            )
            ifnew_partner:
                ifnew_partner[0].email_normalized:
                    email_domain=('email','in',[new_partner[0].email,new_partner[0].email_normalized])
                else:
                    email_domain=('email','=',new_partner[0].email)
                self.search([
                    ('partner_id','=',False),email_domain,('state','notin',['cancel']),
                ]).write({'partner_id':new_partner[0].id})
        returnsuper(EventRegistration,self)._message_post_after_hook(message,msg_vals)

    defaction_send_badge_email(self):
        """Openawindowtocomposeanemail,withthetemplate-'event_badge'
            messageloadedbydefault
        """
        self.ensure_one()
        template=self.env.ref('event.event_registration_mail_template_badge')
        compose_form=self.env.ref('mail.email_compose_message_wizard_form')
        ctx=dict(
            default_model='event.registration',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode='comment',
            custom_layout="mail.mail_notification_light",
        )
        return{
            'name':_('ComposeEmail'),
            'type':'ir.actions.act_window',
            'view_mode':'form',
            'res_model':'mail.compose.message',
            'views':[(compose_form.id,'form')],
            'view_id':compose_form.id,
            'target':'new',
            'context':ctx,
        }

    defget_date_range_str(self):
        self.ensure_one()
        today=fields.Datetime.now()
        event_date=self.event_begin_date
        diff=(event_date.date()-today.date())
        ifdiff.days<=0:
            return_('today')
        elifdiff.days==1:
            return_('tomorrow')
        elif(diff.days<7):
            return_('in%ddays')%(diff.days,)
        elif(diff.days<14):
            return_('nextweek')
        elifevent_date.month==(today+relativedelta(months=+1)).month:
            return_('nextmonth')
        else:
            return_('on%(date)s',date=format_datetime(self.env,self.event_begin_date,tz=self.event_id.date_tz,dt_format='medium'))

    def_get_registration_summary(self):
        self.ensure_one()
        return{
            'id':self.id,
            'name':self.name,
            'partner_id':self.partner_id.id,
            'ticket_name':self.event_ticket_id.nameor_('None'),
            'event_id':self.event_id.id,
            'event_display_name':self.event_id.display_name,
            'company_name':self.event_id.company_idandself.event_id.company_id.nameorFalse,
        }
