#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
importpytz

fromdatetimeimportdatetime,date
fromdateutil.relativedeltaimportrelativedelta
fromwerkzeug.urlsimporturl_join

fromflectraimportapi,fields,models,tools,_
fromflectra.addons.base.models.ir_mail_serverimportMailDeliveryException
fromflectra.exceptionsimportAccessError
fromflectra.tools.float_utilsimportfloat_round

_logger=logging.getLogger(__name__)


classDigest(models.Model):
    _name='digest.digest'
    _description='Digest'

    #Digestdescription
    name=fields.Char(string='Name',required=True,translate=True)
    user_ids=fields.Many2many('res.users',string='Recipients',domain="[('share','=',False)]")
    periodicity=fields.Selection([('daily','Daily'),
                                    ('weekly','Weekly'),
                                    ('monthly','Monthly'),
                                    ('quarterly','Quarterly')],
                                   string='Periodicity',default='daily',required=True)
    next_run_date=fields.Date(string='NextSendDate')
    currency_id=fields.Many2one(related="company_id.currency_id",string='Currency',readonly=False)
    company_id=fields.Many2one('res.company',string='Company',default=lambdaself:self.env.company.id)
    available_fields=fields.Char(compute='_compute_available_fields')
    is_subscribed=fields.Boolean('Isusersubscribed',compute='_compute_is_subscribed')
    state=fields.Selection([('activated','Activated'),('deactivated','Deactivated')],string='Status',readonly=True,default='activated')
    #Firstbase-relatedKPIs
    kpi_res_users_connected=fields.Boolean('ConnectedUsers')
    kpi_res_users_connected_value=fields.Integer(compute='_compute_kpi_res_users_connected_value')
    kpi_mail_message_total=fields.Boolean('Messages')
    kpi_mail_message_total_value=fields.Integer(compute='_compute_kpi_mail_message_total_value')

    def_compute_is_subscribed(self):
        fordigestinself:
            digest.is_subscribed=self.env.userindigest.user_ids

    def_compute_available_fields(self):
        fordigestinself:
            kpis_values_fields=[]
            forfield_name,fieldindigest._fields.items():
                iffield.type=='boolean'andfield_name.startswith(('kpi_','x_kpi_','x_studio_kpi_'))anddigest[field_name]:
                    kpis_values_fields+=[field_name+'_value']
            digest.available_fields=','.join(kpis_values_fields)

    def_get_kpi_compute_parameters(self):
        returnfields.Date.to_string(self._context.get('start_date')),fields.Date.to_string(self._context.get('end_date')),self.env.company

    def_compute_kpi_res_users_connected_value(self):
        forrecordinself:
            start,end,company=record._get_kpi_compute_parameters()
            user_connected=self.env['res.users'].search_count([('company_id','=',company.id),('login_date','>=',start),('login_date','<',end)])
            record.kpi_res_users_connected_value=user_connected

    def_compute_kpi_mail_message_total_value(self):
        discussion_subtype_id=self.env.ref('mail.mt_comment').id
        forrecordinself:
            start,end,company=record._get_kpi_compute_parameters()
            total_messages=self.env['mail.message'].search_count([('create_date','>=',start),('create_date','<',end),('subtype_id','=',discussion_subtype_id),('message_type','in',['comment','email'])])
            record.kpi_mail_message_total_value=total_messages

    @api.onchange('periodicity')
    def_onchange_periodicity(self):
        self.next_run_date=self._get_next_run_date()

    @api.model
    defcreate(self,vals):
        digest=super(Digest,self).create(vals)
        ifnotdigest.next_run_date:
             digest.next_run_date=digest._get_next_run_date()
        returndigest

    #------------------------------------------------------------
    #ACTIONS
    #------------------------------------------------------------

    defaction_subscribe(self):
        ifself.env.user.has_group('base.group_user')andself.env.usernotinself.user_ids:
            self.sudo().user_ids|=self.env.user

    defaction_unsubcribe(self):
        ifself.env.user.has_group('base.group_user')andself.env.userinself.user_ids:
            self.sudo().user_ids-=self.env.user

    defaction_activate(self):
        self.state='activated'

    defaction_deactivate(self):
        self.state='deactivated'

    defaction_set_periodicity(self,periodicity):
        self.periodicity=periodicity

    defaction_send(self):
        to_slowdown=self._check_daily_logs()
        fordigestinself:
            foruserindigest.user_ids:
                digest.with_context(
                    digest_slowdown=digestinto_slowdown,
                    lang=user.lang
                )._action_send_to_user(user,tips_count=1)
            ifdigestinto_slowdown:
                digest.write({'periodicity':'weekly'})
            digest.next_run_date=digest._get_next_run_date()

    def_action_send_to_user(self,user,tips_count=1,consum_tips=True):
        web_base_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        rendered_body=self.env['mail.render.mixin']._render_template(
            'digest.digest_mail_main',
            'digest.digest',
            self.ids,
            engine='qweb',
            add_context={
                'title':self.name,
                'top_button_label':_('Connect'),
                'top_button_url':url_join(web_base_url,'/web/login'),
                'company':user.company_id,
                'user':user,
                'tips_count':tips_count,
                'formatted_date':datetime.today().strftime('%B%d,%Y'),
                'display_mobile_banner':True,
                'kpi_data':self.compute_kpis(user.company_id,user),
                'tips':self.compute_tips(user.company_id,user,tips_count=tips_count,consumed=consum_tips),
                'preferences':self.compute_preferences(user.company_id,user),
            },
            post_process=True
        )[self.id]
        full_mail=self.env['mail.render.mixin']._render_encapsulate(
            'digest.digest_mail_layout',
            rendered_body,
            add_context={
                'company':user.company_id,
                'user':user,
            },
        )
        #createamail_mailbasedonvalues,withoutattachments
        mail_values={
            'auto_delete':True,
            'email_from':(
                self.company_id.partner_id.email_formatted
                orself.env.user.email_formatted
                orself.env.ref('base.user_root').email_formatted
            ),
            'email_to':user.email_formatted,
            'body_html':full_mail,
            'state':'outgoing',
            'subject':'%s:%s'%(user.company_id.name,self.name),
        }
        mail=self.env['mail.mail'].sudo().create(mail_values)
        returnTrue

    @api.model
    def_cron_send_digest_email(self):
        digests=self.search([('next_run_date','<=',fields.Date.today()),('state','=','activated')])
        fordigestindigests:
            try:
                digest.action_send()
            exceptMailDeliveryExceptionase:
                _logger.warning('MailDeliveryExceptionwhilesendingdigest%d.Digestisnowscheduledfornextcronupdate.',digest.id)

    #------------------------------------------------------------
    #KPIS
    #------------------------------------------------------------

    defcompute_kpis(self,company,user):
        """ComputeKPIstodisplayinthedigesttemplate.Itisexpectedtobe
        alistofKPIs,eachcontainingvaluesfor3columnsdisplay.

        :returnlist:result[{
            'kpi_name':'kpi_mail_message',
            'kpi_fullname':'Messages', #translated
            'kpi_action':'crm.crm_lead_action_pipeline', #xmlidofanactiontoexecute
            'kpi_col1':{
                'value':'12.0',
                'margin':32.36,
                'col_subtitle':'Yesterday', #translated
            },
            'kpi_col2':{...},
            'kpi_col3': {...},
        },{...}]"""
        self.ensure_one()
        digest_fields=self._get_kpi_fields()
        invalid_fields=[]
        kpis=[
            dict(kpi_name=field_name,
                 kpi_fullname=self.env['ir.model.fields']._get(self._name,field_name).field_description,
                 kpi_action=False,
                 kpi_col1=dict(),
                 kpi_col2=dict(),
                 kpi_col3=dict(),
                 )
            forfield_nameindigest_fields
        ]
        kpis_actions=self._compute_kpis_actions(company,user)

        forcol_index,(tf_name,tf)inenumerate(self._compute_timeframes(company)):
            digest=self.with_context(start_date=tf[0][0],end_date=tf[0][1]).with_user(user).with_company(company)
            previous_digest=self.with_context(start_date=tf[1][0],end_date=tf[1][1]).with_user(user).with_company(company)
            forindex,field_nameinenumerate(digest_fields):
                kpi_values=kpis[index]
                kpi_values['kpi_action']=kpis_actions.get(field_name)
                try:
                    compute_value=digest[field_name+'_value']
                    #Contextstartandenddateisdifferenteachtimesoinvalidatetorecompute.
                    digest.invalidate_cache([field_name+'_value'])
                    previous_value=previous_digest[field_name+'_value']
                    #Contextstartandenddateisdifferenteachtimesoinvalidatetorecompute.
                    previous_digest.invalidate_cache([field_name+'_value'])
                exceptAccessError: #noaccessrights->justskipthatdigestdetailsfromthatuser'sdigestemail
                    invalid_fields.append(field_name)
                    continue
                margin=self._get_margin_value(compute_value,previous_value)
                ifself._fields['%s_value'%field_name].type=='monetary':
                    converted_amount=tools.format_decimalized_amount(compute_value)
                    compute_value=self._format_currency_amount(converted_amount,company.currency_id)
                kpi_values['kpi_col%s'%(col_index+1)].update({
                    'value':compute_value,
                    'margin':margin,
                    'col_subtitle':tf_name,
                })

        #filterfailedKPIs
        return[kpiforkpiinkpisifkpi['kpi_name']notininvalid_fields]

    defcompute_tips(self,company,user,tips_count=1,consumed=True):
        tips=self.env['digest.tip'].search([
            ('user_ids','!=',user.id),
            '|',('group_id','in',user.groups_id.ids),('group_id','=',False)
        ],limit=tips_count)
        tip_descriptions=[
            self.env['mail.render.mixin']._render_template(tools.html_sanitize(tip.tip_description),'digest.tip',tip.ids,post_process=True)[tip.id]
            fortipintips
        ]
        ifconsumed:
            tips.user_ids+=user
        returntip_descriptions

    def_compute_kpis_actions(self,company,user):
        """GiveanoptionalactiontodisplayindigestemaillinkedtosomeKPIs.

        :returndict:key:kpiname(fieldname),value:anactionthatwillbe
          concatenatedwith/web#action={action}
        """
        return{}

    defcompute_preferences(self,company,user):
        """Giveanoptionaltextforpreferences,likeashortcutforconfiguration.

        :returnstring:htmltoputintemplate
        """
        preferences=[]
        ifself._context.get('digest_slowdown'):
            preferences.append(_("Wehavenoticedyoudidnotconnecttheselastfewdayssowe'veautomaticallyswitchedyourpreferencetoweeklyDigests."))
        elifself.periodicity=='daily'anduser.has_group('base.group_erp_manager'):
            preferences.append('<p>%s<br/><ahref="/digest/%s/set_periodicity?periodicity=weekly"target="_blank"style="color:#009EFB;font-weight:bold;">%s</a></p>'%(
                _('Preferabroaderoverview?'),
                self.id,
                _('SwitchtoweeklyDigests')
            ))
        ifuser.has_group('base.group_erp_manager'):
            preferences.append('<p>%s<br/><ahref="/web#view_type=form&amp;model=%s&amp;id=%s"target="_blank"style="color:#009EFB;font-weight:bold;">%s</a></p>'%(
                _('Wanttocustomizethisemail?'),
                self._name,
                self.id,
                _('Choosethemetricsyoucareabout')
            ))

        returnpreferences

    def_get_next_run_date(self):
        self.ensure_one()
        ifself.periodicity=='daily':
            delta=relativedelta(days=1)
        ifself.periodicity=='weekly':
            delta=relativedelta(weeks=1)
        elifself.periodicity=='monthly':
            delta=relativedelta(months=1)
        elifself.periodicity=='quarterly':
            delta=relativedelta(months=3)
        returndate.today()+delta

    def_compute_timeframes(self,company):
        now=datetime.utcnow()
        tz_name=company.resource_calendar_id.tz
        iftz_name:
            now=pytz.timezone(tz_name).localize(now)
        start_date=now.date()
        return[
            (_('Yesterday'),(
                (start_date+relativedelta(days=-1),start_date),
                (start_date+relativedelta(days=-2),start_date+relativedelta(days=-1)))
            ),(_('Last7Days'),(
                (start_date+relativedelta(weeks=-1),start_date),
                (start_date+relativedelta(weeks=-2),start_date+relativedelta(weeks=-1)))
            ),(_('Last30Days'),(
                (start_date+relativedelta(months=-1),start_date),
                (start_date+relativedelta(months=-2),start_date+relativedelta(months=-1)))
            )
        ]

    #------------------------------------------------------------
    #FORMATTING/TOOLS
    #------------------------------------------------------------

    def_get_kpi_fields(self):
        return[field_nameforfield_name,fieldinself._fields.items()
                iffield.type=='boolean'andfield_name.startswith(('kpi_','x_kpi_','x_studio_kpi_'))andself[field_name]
               ]

    def_get_margin_value(self,value,previous_value=0.0):
        margin=0.0
        if(value!=previous_value)and(value!=0.0andprevious_value!=0.0):
            margin=float_round((float(value-previous_value)/previous_valueor1)*100,precision_digits=2)
        returnmargin

    def_check_daily_logs(self):
        three_days_ago=datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)-relativedelta(days=3)
        to_slowdown=self.env['digest.digest']
        fordigestinself.filtered(lambdadigest:digest.periodicity=='daily'):
            users_logs=self.env['res.users.log'].sudo().search_count([
                ('create_uid','in',digest.user_ids.ids),
                ('create_date','>=',three_days_ago)
            ])
            ifnotusers_logs:
                to_slowdown+=digest
        returnto_slowdown

    def_format_currency_amount(self,amount,currency_id):
        pre=currency_id.position=='before'
        symbol=u'{symbol}'.format(symbol=currency_id.symbolor'')
        returnu'{pre}{0}{post}'.format(amount,pre=symbolifpreelse'',post=symbolifnotpreelse'')
