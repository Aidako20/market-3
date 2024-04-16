#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromrandomimportrandint

fromflectraimportapi,fields,models,tools,SUPERUSER_ID
fromflectra.tools.translateimport_
fromflectra.exceptionsimportUserError

AVAILABLE_PRIORITIES=[
    ('0','Normal'),
    ('1','Good'),
    ('2','VeryGood'),
    ('3','Excellent')
]


classRecruitmentSource(models.Model):
    _name="hr.recruitment.source"
    _description="SourceofApplicants"
    _inherits={"utm.source":"source_id"}

    source_id=fields.Many2one('utm.source',"Source",ondelete='cascade',required=True)
    email=fields.Char(related='alias_id.display_name',string="Email",readonly=True)
    job_id=fields.Many2one('hr.job',"Job",ondelete='cascade')
    alias_id=fields.Many2one('mail.alias',"AliasID")

    defcreate_alias(self):
        campaign=self.env.ref('hr_recruitment.utm_campaign_job')
        medium=self.env.ref('utm.utm_medium_email')
        forsourceinself:
            vals={
                'alias_parent_thread_id':source.job_id.id,
                'alias_model_id':self.env['ir.model']._get('hr.applicant').id,
                'alias_parent_model_id':self.env['ir.model']._get('hr.job').id,
                'alias_name':"%s+%s"%(source.job_id.alias_nameorsource.job_id.name,source.name),
                'alias_defaults':{
                    'job_id':source.job_id.id,
                    'campaign_id':campaign.id,
                    'medium_id':medium.id,
                    'source_id':source.source_id.id,
                },
            }
            source.alias_id=self.env['mail.alias'].create(vals)
            source.name=source.source_id.name

classRecruitmentStage(models.Model):
    _name="hr.recruitment.stage"
    _description="RecruitmentStages"
    _order='sequence'

    name=fields.Char("StageName",required=True,translate=True)
    sequence=fields.Integer(
        "Sequence",default=10,
        help="Givesthesequenceorderwhendisplayingalistofstages.")
    job_ids=fields.Many2many(
        'hr.job',string='JobSpecific',
        help='Specificjobsthatusesthisstage.Otherjobswillnotusethisstage.')
    requirements=fields.Text("Requirements")
    template_id=fields.Many2one(
        'mail.template',"EmailTemplate",
        help="Ifset,amessageispostedontheapplicantusingthetemplatewhentheapplicantissettothestage.")
    fold=fields.Boolean(
        "FoldedinKanban",
        help="Thisstageisfoldedinthekanbanviewwhentherearenorecordsinthatstagetodisplay.")
    legend_blocked=fields.Char(
        'RedKanbanLabel',default=lambdaself:_('Blocked'),translate=True,required=True)
    legend_done=fields.Char(
        'GreenKanbanLabel',default=lambdaself:_('ReadyforNextStage'),translate=True,required=True)
    legend_normal=fields.Char(
        'GreyKanbanLabel',default=lambdaself:_('InProgress'),translate=True,required=True)

    @api.model
    defdefault_get(self,fields):
        ifself._contextandself._context.get('default_job_id')andnotself._context.get('hr_recruitment_stage_mono',False):
            context=dict(self._context)
            context.pop('default_job_id')
            self=self.with_context(context)
        returnsuper(RecruitmentStage,self).default_get(fields)


classRecruitmentDegree(models.Model):
    _name="hr.recruitment.degree"
    _description="ApplicantDegree"
    _sql_constraints=[
        ('name_uniq','unique(name)','ThenameoftheDegreeofRecruitmentmustbeunique!')
    ]

    name=fields.Char("DegreeName",required=True,translate=True)
    sequence=fields.Integer("Sequence",default=1,help="Givesthesequenceorderwhendisplayingalistofdegrees.")


classApplicant(models.Model):
    _name="hr.applicant"
    _description="Applicant"
    _order="prioritydesc,iddesc"
    _inherit=['mail.thread.cc','mail.activity.mixin','utm.mixin']

    name=fields.Char("Subject/ApplicationName",required=True,help="Emailsubjectforapplicationssentviaemail")
    active=fields.Boolean("Active",default=True,help="Iftheactivefieldissettofalse,itwillallowyoutohidethecasewithoutremovingit.")
    description=fields.Text("Description")
    email_from=fields.Char("Email",size=128,help="Applicantemail",compute='_compute_partner_phone_email',
        inverse='_inverse_partner_email',store=True)
    probability=fields.Float("Probability")
    partner_id=fields.Many2one('res.partner',"Contact",copy=False)
    create_date=fields.Datetime("CreationDate",readonly=True,index=True)
    stage_id=fields.Many2one('hr.recruitment.stage','Stage',ondelete='restrict',tracking=True,
                               compute='_compute_stage',store=True,readonly=False,
                               domain="['|',('job_ids','=',False),('job_ids','=',job_id)]",
                               copy=False,index=True,
                               group_expand='_read_group_stage_ids')
    last_stage_id=fields.Many2one('hr.recruitment.stage',"LastStage",
                                    help="Stageoftheapplicantbeforebeinginthecurrentstage.Usedforlostcasesanalysis.")
    categ_ids=fields.Many2many('hr.applicant.category',string="Tags")
    company_id=fields.Many2one('res.company',"Company",compute='_compute_company',store=True,readonly=False,tracking=True)
    user_id=fields.Many2one(
        'res.users',"Recruiter",compute='_compute_user',
        tracking=True,store=True,readonly=False)
    date_closed=fields.Datetime("Closed",compute='_compute_date_closed',store=True,index=True)
    date_open=fields.Datetime("Assigned",readonly=True,index=True)
    date_last_stage_update=fields.Datetime("LastStageUpdate",index=True,default=fields.Datetime.now)
    priority=fields.Selection(AVAILABLE_PRIORITIES,"Appreciation",default='0')
    job_id=fields.Many2one('hr.job',"AppliedJob",domain="['|',('company_id','=',False),('company_id','=',company_id)]",tracking=True,index=True)
    salary_proposed_extra=fields.Char("ProposedSalaryExtra",help="SalaryProposedbytheOrganisation,extraadvantages",tracking=True)
    salary_expected_extra=fields.Char("ExpectedSalaryExtra",help="SalaryExpectedbyApplicant,extraadvantages",tracking=True)
    salary_proposed=fields.Float("ProposedSalary",group_operator="avg",help="SalaryProposedbytheOrganisation",tracking=True)
    salary_expected=fields.Float("ExpectedSalary",group_operator="avg",help="SalaryExpectedbyApplicant",tracking=True)
    availability=fields.Date("Availability",help="Thedateatwhichtheapplicantwillbeavailabletostartworking",tracking=True)
    partner_name=fields.Char("Applicant'sName")
    partner_phone=fields.Char("Phone",size=32,compute='_compute_partner_phone_email',
        inverse='_inverse_partner_phone',store=True)
    partner_mobile=fields.Char("Mobile",size=32,compute='_compute_partner_phone_email',
        inverse='_inverse_partner_mobile',store=True)
    type_id=fields.Many2one('hr.recruitment.degree',"Degree")
    department_id=fields.Many2one(
        'hr.department',"Department",compute='_compute_department',store=True,readonly=False,
        domain="['|',('company_id','=',False),('company_id','=',company_id)]",tracking=True)
    day_open=fields.Float(compute='_compute_day',string="DaystoOpen",compute_sudo=True)
    day_close=fields.Float(compute='_compute_day',string="DaystoClose",compute_sudo=True)
    delay_close=fields.Float(compute="_compute_day",string='DelaytoClose',readonly=True,group_operator="avg",help="Numberofdaystoclose",store=True)
    color=fields.Integer("ColorIndex",default=0)
    emp_id=fields.Many2one('hr.employee',string="Employee",help="Employeelinkedtotheapplicant.",copy=False)
    user_email=fields.Char(related='user_id.email',string="UserEmail",readonly=True)
    attachment_number=fields.Integer(compute='_get_attachment_number',string="NumberofAttachments")
    employee_name=fields.Char(related='emp_id.name',string="EmployeeName",readonly=False,tracking=False)
    attachment_ids=fields.One2many('ir.attachment','res_id',domain=[('res_model','=','hr.applicant')],string='Attachments')
    kanban_state=fields.Selection([
        ('normal','Grey'),
        ('done','Green'),
        ('blocked','Red')],string='KanbanState',
        copy=False,default='normal',required=True)
    legend_blocked=fields.Char(related='stage_id.legend_blocked',string='KanbanBlocked')
    legend_done=fields.Char(related='stage_id.legend_done',string='KanbanValid')
    legend_normal=fields.Char(related='stage_id.legend_normal',string='KanbanOngoing')
    application_count=fields.Integer(compute='_compute_application_count',help='Applicationswiththesameemail')
    meeting_count=fields.Integer(compute='_compute_meeting_count',help='MeetingCount')
    refuse_reason_id=fields.Many2one('hr.applicant.refuse.reason',string='RefuseReason',tracking=True)

    @api.depends('date_open','date_closed')
    def_compute_day(self):
        forapplicantinself:
            ifapplicant.date_open:
                date_create=applicant.create_date
                date_open=applicant.date_open
                applicant.day_open=(date_open-date_create).total_seconds()/(24.0*3600)
            else:
                applicant.day_open=False
            ifapplicant.date_closed:
                date_create=applicant.create_date
                date_closed=applicant.date_closed
                applicant.day_close=(date_closed-date_create).total_seconds()/(24.0*3600)
                applicant.delay_close=applicant.day_close-applicant.day_open
            else:
                applicant.day_close=False
                applicant.delay_close=False

    @api.depends('email_from')
    def_compute_application_count(self):
        application_data=self.env['hr.applicant'].with_context(active_test=False).read_group([
            ('email_from','in',list(set(self.mapped('email_from'))))],['email_from'],['email_from'])
        application_data_mapped=dict((data['email_from'],data['email_from_count'])fordatainapplication_data)
        applicants=self.filtered(lambdaapplicant:applicant.email_from)
        forapplicantinapplicants:
            applicant.application_count=application_data_mapped.get(applicant.email_from,1)-1
        (self-applicants).application_count=False

    def_compute_meeting_count(self):
        ifself.ids:
            meeting_data=self.env['calendar.event'].sudo().read_group(
                [('applicant_id','in',self.ids)],
                ['applicant_id'],
                ['applicant_id']
            )
            mapped_data={m['applicant_id'][0]:m['applicant_id_count']forminmeeting_data}
        else:
            mapped_data=dict()
        forapplicantinself:
            applicant.meeting_count=mapped_data.get(applicant.id,0)

    def_get_attachment_number(self):
        read_group_res=self.env['ir.attachment'].read_group(
            [('res_model','=','hr.applicant'),('res_id','in',self.ids)],
            ['res_id'],['res_id'])
        attach_data=dict((res['res_id'],res['res_id_count'])forresinread_group_res)
        forrecordinself:
            record.attachment_number=attach_data.get(record.id,0)

    @api.model
    def_read_group_stage_ids(self,stages,domain,order):
        #retrievejob_idfromthecontextandwritethedomain:ids+contextualcolumns(jobordefault)
        job_id=self._context.get('default_job_id')
        search_domain=[('job_ids','=',False)]
        ifjob_id:
            search_domain=['|',('job_ids','=',job_id)]+search_domain
        ifstages:
            search_domain=['|',('id','in',stages.ids)]+search_domain

        stage_ids=stages._search(search_domain,order=order,access_rights_uid=SUPERUSER_ID)
        returnstages.browse(stage_ids)

    @api.depends('job_id','department_id')
    def_compute_company(self):
        forapplicantinself:
            company_id=False
            ifapplicant.department_id:
                company_id=applicant.department_id.company_id.id
            ifnotcompany_idandapplicant.job_id:
                company_id=applicant.job_id.company_id.id
            applicant.company_id=company_idorself.env.company.id

    @api.depends('job_id')
    def_compute_department(self):
        forapplicantinself:
            applicant.department_id=applicant.job_id.department_id.id

    @api.depends('job_id')
    def_compute_stage(self):
        forapplicantinself:
            ifapplicant.job_id:
                ifnotapplicant.stage_id:
                    stage_ids=self.env['hr.recruitment.stage'].search([
                        '|',
                        ('job_ids','=',False),
                        ('job_ids','=',applicant.job_id.id),
                        ('fold','=',False)
                    ],order='sequenceasc',limit=1).ids
                    applicant.stage_id=stage_ids[0]ifstage_idselseFalse
            else:
                applicant.stage_id=False

    @api.depends('job_id')
    def_compute_user(self):
        forapplicantinself:
            applicant.user_id=applicant.job_id.user_id.idorself.env.uid

    @api.depends('partner_id')
    def_compute_partner_phone_email(self):
        forapplicantinself:
            applicant.partner_phone=applicant.partner_id.phone
            applicant.partner_mobile=applicant.partner_id.mobile
            applicant.email_from=applicant.partner_id.email

    def_inverse_partner_email(self):
        forapplicantinself.filtered(lambdaa:a.partner_idanda.email_fromandnota.partner_id.email):
            applicant.partner_id.email=applicant.email_from

    def_inverse_partner_phone(self):
        forapplicantinself.filtered(lambdaa:a.partner_idanda.partner_phoneandnota.partner_id.phone):
            applicant.partner_id.phone=applicant.partner_phone

    def_inverse_partner_mobile(self):
        forapplicantinself.filtered(lambdaa:a.partner_idanda.partner_mobileandnota.partner_id.mobile):
            applicant.partner_id.mobile=applicant.partner_mobile

    @api.depends('stage_id')
    def_compute_date_closed(self):
        forapplicantinself:
            ifapplicant.stage_idandapplicant.stage_id.fold:
                applicant.date_closed=fields.datetime.now()
            else:
                applicant.date_closed=False

    @api.model
    defcreate(self,vals):
        ifvals.get('department_id')andnotself._context.get('default_department_id'):
            self=self.with_context(default_department_id=vals.get('department_id'))
        ifvals.get('user_id'):
            vals['date_open']=fields.Datetime.now()
        ifvals.get('email_from'):
            vals['email_from']=vals['email_from'].strip()
        returnsuper(Applicant,self).create(vals)

    defwrite(self,vals):
        #user_idchange:updatedate_open
        ifvals.get('user_id'):
            vals['date_open']=fields.Datetime.now()
        ifvals.get('email_from'):
            vals['email_from']=vals['email_from'].strip()
        #stage_id:tracklaststagebeforeupdate
        if'stage_id'invals:
            vals['date_last_stage_update']=fields.Datetime.now()
            if'kanban_state'notinvals:
                vals['kanban_state']='normal'
            forapplicantinself:
                vals['last_stage_id']=applicant.stage_id.id
                res=super(Applicant,self).write(vals)
        else:
            res=super(Applicant,self).write(vals)
        returnres

    defget_empty_list_help(self,help):
        if'active_id'inself.env.contextandself.env.context.get('active_model')=='hr.job':
            alias_id=self.env['hr.job'].browse(self.env.context['active_id']).alias_id
        else:
            alias_id=False

        nocontent_values={
            'help_title':_('Noapplicationyet'),
            'para_1':_('Letpeopleapplybyemailtosavetime.'),
            'para_2':_('Attachments,likeresumes,getindexedautomatically.'),
        }
        nocontent_body="""
            <pclass="o_view_nocontent_empty_folder">%(help_title)s</p>
            <p>%(para_1)s<br/>%(para_2)s</p>"""

        ifalias_idandalias_id.alias_domainandalias_id.alias_name:
            email=alias_id.display_name
            email_link="<ahref='mailto:%s'>%s</a>"%(email,email)
            nocontent_values['email_link']=email_link
            nocontent_body+="""<pclass="o_copy_paste_email">%(email_link)s</p>"""

        returnnocontent_body%nocontent_values

    defaction_makeMeeting(self):
        """ThisopensMeeting'scalendarviewtoschedulemeetingoncurrentapplicant
            @return:DictionaryvalueforcreatedMeetingview
        """
        self.ensure_one()
        partners=self.partner_id|self.user_id.partner_id|self.department_id.manager_id.user_id.partner_id

        category=self.env.ref('hr_recruitment.categ_meet_interview')
        res=self.env['ir.actions.act_window']._for_xml_id('calendar.action_calendar_event')
        res['context']={
            'default_applicant_id':self.id,
            'default_partner_ids':partners.ids,
            'default_user_id':self.env.uid,
            'default_name':self.name,
            'default_categ_ids':categoryand[category.id]orFalse,
        }
        returnres

    defaction_get_attachment_tree_view(self):
        action=self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        action['context']={'default_res_model':self._name,'default_res_id':self.ids[0]}
        action['domain']=str(['&',('res_model','=',self._name),('res_id','in',self.ids)])
        action['search_view_id']=(self.env.ref('hr_recruitment.ir_attachment_view_search_inherit_hr_recruitment').id,)
        returnaction

    defaction_applications_email(self):
        return{
            'type':'ir.actions.act_window',
            'name':_('Applications'),
            'res_model':self._name,
            'view_mode':'kanban,tree,form,pivot,graph,calendar,activity',
            'domain':[('email_from','in',self.mapped('email_from'))],
            'context':{
                'active_test':False
            },
        }

    def_track_template(self,changes):
        res=super(Applicant,self)._track_template(changes)
        applicant=self[0]
        if'stage_id'inchangesandapplicant.stage_id.template_id:
            res['stage_id']=(applicant.stage_id.template_id,{
                'auto_delete_message':True,
                'subtype_id':self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'),
                'email_layout_xmlid':'mail.mail_notification_light'
            })
        returnres

    def_creation_subtype(self):
        returnself.env.ref('hr_recruitment.mt_applicant_new')

    def_track_subtype(self,init_values):
        record=self[0]
        if'stage_id'ininit_valuesandrecord.stage_id:
            returnself.env.ref('hr_recruitment.mt_applicant_stage_changed')
        returnsuper(Applicant,self)._track_subtype(init_values)

    def_notify_get_reply_to(self,default=None,records=None,company=None,doc_names=None):
        """Overridetosetaliasofapplicantstotheirjobdefinitionifany."""
        aliases=self.mapped('job_id')._notify_get_reply_to(default=default,records=None,company=company,doc_names=None)
        res={app.id:aliases.get(app.job_id.id)forappinself}
        leftover=self.filtered(lambdarec:notrec.job_id)
        ifleftover:
            res.update(super(Applicant,leftover)._notify_get_reply_to(default=default,records=None,company=company,doc_names=doc_names))
        returnres

    def_message_get_suggested_recipients(self):
        recipients=super(Applicant,self)._message_get_suggested_recipients()
        forapplicantinself:
            ifapplicant.partner_id:
                applicant._message_add_suggested_recipient(recipients,partner=applicant.partner_id,reason=_('Contact'))
            elifapplicant.email_from:
                email_from=tools.email_normalize(applicant.email_from)
                ifapplicant.partner_name:
                    email_from=tools.formataddr((applicant.partner_name,email_from))
                applicant._message_add_suggested_recipient(recipients,email=email_from,reason=_('ContactEmail'))
        returnrecipients

    @api.model
    defmessage_new(self,msg,custom_values=None):
        """Overridesmail_threadmessage_newthatiscalledbythemailgateway
            throughmessage_process.
            Thisoverrideupdatesthedocumentaccordingtotheemail.
        """
        #removedefaultauthorwhengoingthroughthemailgateway.Indeedwe
        #donotwanttoexplicitlysetuser_idtoFalse;howeverwedonot
        #wantthegatewayusertoberesponsibleifnootherresponsibleis
        #found.
        self=self.with_context(default_user_id=False)
        stage=False
        ifcustom_valuesand'job_id'incustom_values:
            stage=self.env['hr.job'].browse(custom_values['job_id'])._get_first_stage()
        val=msg.get('from').split('<')[0]
        defaults={
            'name':msg.get('subject')or_("NoSubject"),
            'partner_name':val,
            'email_from':msg.get('from'),
            'partner_id':msg.get('author_id',False),
        }
        ifmsg.get('priority'):
            defaults['priority']=msg.get('priority')
        ifstageandstage.id:
            defaults['stage_id']=stage.id
        ifcustom_values:
            defaults.update(custom_values)
        returnsuper(Applicant,self).message_new(msg,custom_values=defaults)

    def_message_post_after_hook(self,message,msg_vals):
        ifself.email_fromandnotself.partner_id:
            #weconsiderthatpostingamessagewithaspecifiedrecipient(notafollower,aspecificone)
            #onadocumentwithoutcustomermeansthatitwascreatedthroughthechatterusing
            #suggestedrecipients.ThisheuristicallowstoavoiduglyhacksinJS.
            email_normalized=tools.email_normalize(self.email_from)
            new_partner=message.partner_ids.filtered(
                lambdapartner:partner.email==self.email_fromor(email_normalizedandpartner.email_normalized==email_normalized)
            )
            ifnew_partner:
                ifnew_partner[0].create_date.date()==fields.Date.today():
                    new_partner[0].write({
                        'type':'private',
                        'phone':self.partner_phone,
                        'mobile':self.partner_mobile,
                    })
                ifnew_partner[0].email_normalized:
                    email_domain=('email_from','in',[new_partner[0].email,new_partner[0].email_normalized])
                else:
                    email_domain=('email_from','=',new_partner[0].email)
                self.search([
                    ('partner_id','=',False),email_domain,('stage_id.fold','=',False)
                ]).write({'partner_id':new_partner[0].id})
        returnsuper(Applicant,self)._message_post_after_hook(message,msg_vals)

    defcreate_employee_from_applicant(self):
        """Createanhr.employeefromthehr.applicants"""
        employee=False
        forapplicantinself:
            contact_name=False
            ifapplicant.partner_id:
                address_id=applicant.partner_id.address_get(['contact'])['contact']
                contact_name=applicant.partner_id.display_name
            else:
                ifnotapplicant.partner_name:
                    raiseUserError(_('YoumustdefineaContactNameforthisapplicant.'))
                new_partner_id=self.env['res.partner'].create({
                    'is_company':False,
                    'type':'private',
                    'name':applicant.partner_name,
                    'email':applicant.email_from,
                    'phone':applicant.partner_phone,
                    'mobile':applicant.partner_mobile
                })
                applicant.partner_id=new_partner_id
                address_id=new_partner_id.address_get(['contact'])['contact']
            ifapplicant.partner_nameorcontact_name:
                employee_data={
                    'default_name':applicant.partner_nameorcontact_name,
                    'default_job_id':applicant.job_id.id,
                    'default_job_title':applicant.job_id.name,
                    'default_address_home_id':address_id,
                    'default_department_id':applicant.department_id.idorFalse,
                    'default_address_id':applicant.company_idandapplicant.company_id.partner_id
                            andapplicant.company_id.partner_id.idorFalse,
                    'default_work_email':applicant.department_idandapplicant.department_id.company_id
                            andapplicant.department_id.company_id.emailorFalse,
                    'default_work_phone':applicant.department_id.company_id.phone,
                    'form_view_initial_mode':'edit',
                    'default_applicant_id':applicant.ids,
                    }
                    
        dict_act_window=self.env['ir.actions.act_window']._for_xml_id('hr.open_view_employee_list')
        dict_act_window['context']=employee_data
        returndict_act_window

    defarchive_applicant(self):
        return{
            'type':'ir.actions.act_window',
            'name':_('RefuseReason'),
            'res_model':'applicant.get.refuse.reason',
            'view_mode':'form',
            'target':'new',
            'context':{'default_applicant_ids':self.ids,'active_test':False},
            'views':[[False,'form']]
        }

    defreset_applicant(self):
        """Reinserttheapplicantintotherecruitmentpipeinthefirststage"""
        default_stage=dict()
        forjob_idinself.mapped('job_id'):
            default_stage[job_id.id]=self.env['hr.recruitment.stage'].search(
                ['|',
                    ('job_ids','=',False),
                    ('job_ids','=',job_id.id),
                    ('fold','=',False)
                ],order='sequenceasc',limit=1).id
        forapplicantinself:
            applicant.write(
                {'stage_id':applicant.job_id.idanddefault_stage[applicant.job_id.id],
                 'refuse_reason_id':False})

    deftoggle_active(self):
        res=super(Applicant,self).toggle_active()
        applicant_active=self.filtered(lambdaapplicant:applicant.active)
        ifapplicant_active:
            applicant_active.reset_applicant()
        applicant_inactive=self.filtered(lambdaapplicant:notapplicant.active)
        ifapplicant_inactive:
            returnapplicant_inactive.archive_applicant()
        returnres


classApplicantCategory(models.Model):
    _name="hr.applicant.category"
    _description="Categoryofapplicant"

    def_get_default_color(self):
        returnrandint(1,11)

    name=fields.Char("TagName",required=True)
    color=fields.Integer(string='ColorIndex',default=_get_default_color)

    _sql_constraints=[
            ('name_uniq','unique(name)',"Tagnamealreadyexists!"),
    ]


classApplicantRefuseReason(models.Model):
    _name="hr.applicant.refuse.reason"
    _description='RefuseReasonofApplicant'

    name=fields.Char('Description',required=True,translate=True)
    active=fields.Boolean('Active',default=True)
