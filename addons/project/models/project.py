#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importast
fromcollectionsimportdefaultdict
fromdatetimeimporttimedelta
fromrandomimportrandint

fromflectraimportapi,fields,models,tools,SUPERUSER_ID,_
fromflectra.exceptionsimportUserError,ValidationError
fromflectra.osv.expressionimportOR
fromflectra.tools.miscimportget_lang

from.project_task_recurrenceimportDAYS,WEEKS

classProjectTaskType(models.Model):
    _name='project.task.type'
    _description='TaskStage'
    _order='sequence,id'

    def_get_default_project_ids(self):
        default_project_id=self.env.context.get('default_project_id')
        return[default_project_id]ifdefault_project_idelseNone

    active=fields.Boolean('Active',default=True)
    name=fields.Char(string='StageName',required=True,translate=True)
    description=fields.Text(translate=True)
    sequence=fields.Integer(default=1)
    project_ids=fields.Many2many('project.project','project_task_type_rel','type_id','project_id',string='Projects',
        default=_get_default_project_ids)
    legend_blocked=fields.Char(
        'RedKanbanLabel',default=lambdas:_('Blocked'),translate=True,required=True,
        help='Overridethedefaultvaluedisplayedfortheblockedstateforkanbanselection,whenthetaskorissueisinthatstage.')
    legend_done=fields.Char(
        'GreenKanbanLabel',default=lambdas:_('Ready'),translate=True,required=True,
        help='Overridethedefaultvaluedisplayedforthedonestateforkanbanselection,whenthetaskorissueisinthatstage.')
    legend_normal=fields.Char(
        'GreyKanbanLabel',default=lambdas:_('InProgress'),translate=True,required=True,
        help='Overridethedefaultvaluedisplayedforthenormalstateforkanbanselection,whenthetaskorissueisinthatstage.')
    mail_template_id=fields.Many2one(
        'mail.template',
        string='EmailTemplate',
        domain=[('model','=','project.task')],
        help="Ifsetanemailwillbesenttothecustomerwhenthetaskorissuereachesthisstep.")
    fold=fields.Boolean(string='FoldedinKanban',
        help='Thisstageisfoldedinthekanbanviewwhentherearenorecordsinthatstagetodisplay.')
    rating_template_id=fields.Many2one(
        'mail.template',
        string='RatingEmailTemplate',
        domain=[('model','=','project.task')],
        help="Ifsetandiftheproject'sratingconfigurationis'Ratingwhenchangingstage',thenanemailwillbesenttothecustomerwhenthetaskreachesthisstep.")
    auto_validation_kanban_state=fields.Boolean('Automatickanbanstatus',default=False,
        help="Automaticallymodifythekanbanstatewhenthecustomerrepliestothefeedbackforthisstage.\n"
            "*Agoodfeedbackfromthecustomerwillupdatethekanbanstateto'readyforthenewstage'(greenbullet).\n"
            "*Amediumorabadfeedbackwillsetthekanbanstateto'blocked'(redbullet).\n")
    is_closed=fields.Boolean('ClosingStage',help="Tasksinthisstageareconsideredasclosed.")
    disabled_rating_warning=fields.Text(compute='_compute_disabled_rating_warning')

    defunlink_wizard(self,stage_view=False):
        self=self.with_context(active_test=False)
        #retrievesalltheprojectswithaleast1taskinthatstage
        #ataskcanbeinastageeveniftheprojectisnotassignedtothestage
        readgroup=self.with_context(active_test=False).env['project.task'].read_group([('stage_id','in',self.ids)],['project_id'],['project_id'])
        project_ids=list(set([project['project_id'][0]forprojectinreadgroup]+self.project_ids.ids))

        wizard=self.with_context(project_ids=project_ids).env['project.task.type.delete.wizard'].create({
            'project_ids':project_ids,
            'stage_ids':self.ids
        })

        context=dict(self.env.context)
        context['stage_view']=stage_view
        return{
            'name':_('DeleteStage'),
            'view_mode':'form',
            'res_model':'project.task.type.delete.wizard',
            'views':[(self.env.ref('project.view_project_task_type_delete_wizard').id,'form')],
            'type':'ir.actions.act_window',
            'res_id':wizard.id,
            'target':'new',
            'context':context,
        }

    defwrite(self,vals):
        if'active'invalsandnotvals['active']:
            self.env['project.task'].search([('stage_id','in',self.ids)]).write({'active':False})
        returnsuper(ProjectTaskType,self).write(vals)

    @api.depends('project_ids','project_ids.rating_active')
    def_compute_disabled_rating_warning(self):
        forstageinself:
            disabled_projects=stage.project_ids.filtered(lambdap:notp.rating_active)
            ifdisabled_projects:
                stage.disabled_rating_warning='\n'.join('-%s'%p.nameforpindisabled_projects)
            else:
                stage.disabled_rating_warning=False


classProject(models.Model):
    _name="project.project"
    _description="Project"
    _inherit=['portal.mixin','mail.alias.mixin','mail.thread','rating.parent.mixin']
    _order="sequence,name,id"
    _rating_satisfaction_days=False #takesallexistingratings
    _check_company_auto=True

    def_compute_attached_docs_count(self):
        Attachment=self.env['ir.attachment']
        forprojectinself:
            project.doc_count=Attachment.search_count([
                '|',
                '&',
                ('res_model','=','project.project'),('res_id','=',project.id),
                '&',
                ('res_model','=','project.task'),('res_id','in',project.task_ids.ids)
            ])

    def_compute_task_count(self):
        task_data=self.env['project.task'].read_group([('project_id','in',self.ids),'|','&',('stage_id.is_closed','=',False),('stage_id.fold','=',False),('stage_id','=',False)],['project_id'],['project_id'])
        result=dict((data['project_id'][0],data['project_id_count'])fordataintask_data)
        forprojectinself:
            project.task_count=result.get(project.id,0)

    defattachment_tree_view(self):
        action=self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        action['domain']=str([
            '|',
            '&',
            ('res_model','=','project.project'),
            ('res_id','in',self.ids),
            '&',
            ('res_model','=','project.task'),
            ('res_id','in',self.task_ids.ids)
        ])
        action['context']="{'default_res_model':'%s','default_res_id':%d}"%(self._name,self.id)
        returnaction

    def_compute_is_favorite(self):
        forprojectinself:
            project.is_favorite=self.env.userinproject.favorite_user_ids

    def_inverse_is_favorite(self):
        favorite_projects=not_fav_projects=self.env['project.project'].sudo()
        forprojectinself:
            ifself.env.userinproject.favorite_user_ids:
                favorite_projects|=project
            else:
                not_fav_projects|=project

        #ProjectUserhasnowriteaccessforproject.
        not_fav_projects.write({'favorite_user_ids':[(4,self.env.uid)]})
        favorite_projects.write({'favorite_user_ids':[(3,self.env.uid)]})

    def_get_default_favorite_user_ids(self):
        return[(6,0,[self.env.uid])]

    name=fields.Char("Name",index=True,required=True,tracking=True)
    description=fields.Html()
    active=fields.Boolean(default=True,
        help="IftheactivefieldissettoFalse,itwillallowyoutohidetheprojectwithoutremovingit.")
    sequence=fields.Integer(default=10,help="GivesthesequenceorderwhendisplayingalistofProjects.")
    partner_id=fields.Many2one('res.partner',string='Customer',auto_join=True,tracking=True,domain="['|',('company_id','=',False),('company_id','=',company_id)]")
    partner_email=fields.Char(
        compute='_compute_partner_email',inverse='_inverse_partner_email',
        string='Email',readonly=False,store=True,copy=False)
    partner_phone=fields.Char(
        compute='_compute_partner_phone',inverse='_inverse_partner_phone',
        string="Phone",readonly=False,store=True,copy=False)
    company_id=fields.Many2one('res.company',string='Company',required=True,default=lambdaself:self.env.company)
    currency_id=fields.Many2one('res.currency',related="company_id.currency_id",string="Currency",readonly=True)
    analytic_account_id=fields.Many2one('account.analytic.account',string="AnalyticAccount",copy=False,ondelete='setnull',
        domain="['|',('company_id','=',False),('company_id','=',company_id)]",check_company=True,
        help="Analyticaccounttowhichthisprojectislinkedforfinancialmanagement."
             "Useananalyticaccounttorecordcostandrevenueonyourproject.")

    favorite_user_ids=fields.Many2many(
        'res.users','project_favorite_user_rel','project_id','user_id',
        default=_get_default_favorite_user_ids,
        string='Members')
    is_favorite=fields.Boolean(compute='_compute_is_favorite',inverse='_inverse_is_favorite',string='ShowProjectondashboard',
        help="Whetherthisprojectshouldbedisplayedonyourdashboard.")
    label_tasks=fields.Char(string='UseTasksas',default='Tasks',help="Labelusedforthetasksoftheproject.",translate=True)
    tasks=fields.One2many('project.task','project_id',string="TaskActivities")
    resource_calendar_id=fields.Many2one(
        'resource.calendar',string='WorkingTime',
        related='company_id.resource_calendar_id')
    type_ids=fields.Many2many('project.task.type','project_task_type_rel','project_id','type_id',string='TasksStages')
    task_count=fields.Integer(compute='_compute_task_count',string="TaskCount")
    task_ids=fields.One2many('project.task','project_id',string='Tasks',
                               domain=['|',('stage_id.fold','=',False),('stage_id','=',False)])
    color=fields.Integer(string='ColorIndex')
    user_id=fields.Many2one('res.users',string='ProjectManager',default=lambdaself:self.env.user,tracking=True)
    alias_enabled=fields.Boolean(string='Useemailalias',compute='_compute_alias_enabled',readonly=False)
    alias_id=fields.Many2one('mail.alias',string='Alias',ondelete="restrict",required=True,
        help="Internalemailassociatedwiththisproject.Incomingemailsareautomaticallysynchronized"
             "withTasks(oroptionallyIssuesiftheIssueTrackermoduleisinstalled).")
    privacy_visibility=fields.Selection([
            ('followers','Invitedinternalusers'),
            ('employees','Allinternalusers'),
            ('portal','Invitedportalusersandallinternalusers'),
        ],
        string='Visibility',required=True,
        default='portal',
        help="Peopletowhomthisprojectanditstaskswillbevisible.\n\n"
            "-Invitedinternalusers:whenfollowingaproject,internaluserswillgetaccesstoallofitstaskswithoutdistinction."
            "Otherwise,theywillonlygetaccesstothespecifictaskstheyarefollowing.\n"
            "Auserwiththeproject>administratoraccessrightlevelcanstillaccessthisprojectanditstasks,eveniftheyarenotexplicitlypartofthefollowers.\n\n"
            "-Allinternalusers:allinternaluserscanaccesstheprojectandallofitstaskswithoutdistinction.\n\n"
            "-Invitedportalusersandallinternalusers:allinternaluserscanaccesstheprojectandallofitstaskswithoutdistinction.\n"
            "Whenfollowingaproject,portaluserswillgetaccesstoallofitstaskswithoutdistinction.Otherwise,theywillonlygetaccesstothespecifictaskstheyarefollowing.")

    allowed_user_ids=fields.Many2many('res.users',compute='_compute_allowed_users',inverse='_inverse_allowed_user')
    allowed_internal_user_ids=fields.Many2many('res.users','project_allowed_internal_users_rel',
                                                 string="AllowedInternalUsers",default=lambdaself:self.env.user,domain=[('share','=',False)])
    allowed_portal_user_ids=fields.Many2many('res.users','project_allowed_portal_users_rel',string="AllowedPortalUsers",domain=[('share','=',True)])
    doc_count=fields.Integer(compute='_compute_attached_docs_count',string="Numberofdocumentsattached")
    date_start=fields.Date(string='StartDate')
    date=fields.Date(string='ExpirationDate',index=True,tracking=True)
    subtask_project_id=fields.Many2one('project.project',string='Sub-taskProject',ondelete="restrict",
        help="Projectinwhichsub-tasksofthecurrentprojectwillbecreated.Itcanbethecurrentprojectitself.")
    allow_subtasks=fields.Boolean('Sub-tasks',default=lambdaself:self.env.user.has_group('project.group_subtask_project'))
    allow_recurring_tasks=fields.Boolean('RecurringTasks',default=lambdaself:self.env.user.has_group('project.group_project_recurring_tasks'))

    #ratingfields
    rating_request_deadline=fields.Datetime(compute='_compute_rating_request_deadline',store=True)
    rating_active=fields.Boolean('CustomerRatings',default=lambdaself:self.env.user.has_group('project.group_project_rating'))
    rating_status=fields.Selection(
        [('stage','Ratingwhenchangingstage'),
         ('periodic','PeriodicalRating')
        ],'CustomerRatingsStatus',default="stage",required=True,
        help="Howtogetcustomerfeedback?\n"
             "-Ratingwhenchangingstage:anemailwillbesentwhenataskispulledinanotherstage.\n"
             "-PeriodicalRating:emailwillbesentperiodically.\n\n"
             "Don'tforgettosetupthemailtemplatesonthestagesforwhichyouwanttogetthecustomer'sfeedbacks.")
    rating_status_period=fields.Selection([
        ('daily','Daily'),
        ('weekly','Weekly'),
        ('bimonthly','TwiceaMonth'),
        ('monthly','OnceaMonth'),
        ('quarterly','Quarterly'),
        ('yearly','Yearly')],'RatingFrequency',required=True,default='monthly')

    _sql_constraints=[
        ('project_date_greater','check(date>=date_start)','Error!projectstart-datemustbelowerthanprojectend-date.')
    ]

    @api.depends('partner_id.email')
    def_compute_partner_email(self):
        forprojectinself:
            ifproject.partner_idandproject.partner_id.email!=project.partner_email:
                project.partner_email=project.partner_id.email

    def_inverse_partner_email(self):
        forprojectinself:
            ifproject.partner_idandproject.partner_email!=project.partner_id.email:
                project.partner_id.email=project.partner_email

    @api.depends('partner_id.phone')
    def_compute_partner_phone(self):
        forprojectinself:
            ifproject.partner_idandproject.partner_phone!=project.partner_id.phone:
                project.partner_phone=project.partner_id.phone

    def_inverse_partner_phone(self):
        forprojectinself:
            ifproject.partner_idandproject.partner_phone!=project.partner_id.phone:
                project.partner_id.phone=project.partner_phone

    @api.onchange('alias_enabled')
    def_onchange_alias_name(self):
        ifnotself.alias_enabled:
            self.alias_name=False

    def_compute_alias_enabled(self):
        forprojectinself:
            project.alias_enabled=project.alias_domainandproject.alias_id.alias_name

    @api.depends('allowed_internal_user_ids','allowed_portal_user_ids')
    def_compute_allowed_users(self):
        forprojectinself:
            users=project.allowed_internal_user_ids|project.allowed_portal_user_ids
            project.allowed_user_ids=users

    def_inverse_allowed_user(self):
        forprojectinself:
            allowed_users=project.allowed_user_ids
            project.allowed_portal_user_ids=allowed_users.filtered('share')
            project.allowed_internal_user_ids=allowed_users-project.allowed_portal_user_ids

    def_compute_access_url(self):
        super(Project,self)._compute_access_url()
        forprojectinself:
            project.access_url='/my/project/%s'%project.id

    def_compute_access_warning(self):
        super(Project,self)._compute_access_warning()
        forprojectinself.filtered(lambdax:x.privacy_visibility!='portal'):
            project.access_warning=_(
                "Theprojectcannotbesharedwiththerecipient(s)becausetheprivacyoftheprojectistoorestricted.Settheprivacyto'Visiblebyfollowingcustomers'inordertomakeitaccessiblebytherecipient(s).")

    @api.depends('rating_status','rating_status_period')
    def_compute_rating_request_deadline(self):
        periods={'daily':1,'weekly':7,'bimonthly':15,'monthly':30,'quarterly':90,'yearly':365}
        forprojectinself:
            project.rating_request_deadline=fields.datetime.now()+timedelta(days=periods.get(project.rating_status_period,0))

    @api.model
    def_map_tasks_default_valeus(self,task,project):
        """getthedefaultvalueforthecopiedtaskonprojectduplication"""
        return{
            'stage_id':task.stage_id.id,
            'name':task.name,
            'company_id':project.company_id.id,
        }

    defmap_tasks(self,new_project_id):
        """copyandmaptasksfromoldtonewproject"""
        project=self.browse(new_project_id)
        tasks=self.env['project.task']
        #Wewanttocopyarchivedtask,butdonotpropagateanactive_testcontextkey
        task_ids=self.env['project.task'].with_context(active_test=False).search([('project_id','=',self.id)],order='parent_id').ids
        old_to_new_tasks={}
        fortaskinself.env['project.task'].browse(task_ids):
            #preservetasknameandstage,normallyalteredduringcopy
            defaults=self._map_tasks_default_valeus(task,project)
            iftask.parent_id:
                #settheparenttotheduplicatedtask
                defaults['parent_id']=old_to_new_tasks.get(task.parent_id.id,False)
            new_task=task.copy(defaults)
            #Ifchildarecreatedbeforeparent(exsub_sub_tasks)
            new_child_ids=[old_to_new_tasks[child.id]forchildintask.child_idsifchild.idinold_to_new_tasks]
            tasks.browse(new_child_ids).write({'parent_id':new_task.id})
            old_to_new_tasks[task.id]=new_task.id
            tasks+=new_task

        returnproject.write({'tasks':[(6,0,tasks.ids)]})

    @api.returns('self',lambdavalue:value.id)
    defcopy(self,default=None):
        ifdefaultisNone:
            default={}
        ifnotdefault.get('name'):
            default['name']=_("%s(copy)")%(self.name)
        project=super(Project,self).copy(default)
        ifself.subtask_project_id==self:
            project.subtask_project_id=project
        forfollowerinself.message_follower_ids:
            project.message_subscribe(partner_ids=follower.partner_id.ids,subtype_ids=follower.subtype_ids.ids)
        if'tasks'notindefault:
            self.map_tasks(project.id)
        returnproject

    @api.model
    defcreate(self,vals):
        #Preventdoubleprojectcreation
        self=self.with_context(mail_create_nosubscribe=True)
        project=super(Project,self).create(vals)
        ifnotvals.get('subtask_project_id'):
            project.subtask_project_id=project.id
        ifproject.privacy_visibility=='portal'andproject.partner_id.user_ids:
            project.allowed_user_ids|=project.partner_id.user_ids
        returnproject

    defwrite(self,vals):
        allowed_users_changed='allowed_portal_user_ids'invalsor'allowed_internal_user_ids'invals
        ifallowed_users_changed:
            allowed_users={project:project.allowed_user_idsforprojectinself}
        #directlycomputeis_favoritetododgeallowwriteaccessright
        if'is_favorite'invals:
            vals.pop('is_favorite')
            self._fields['is_favorite'].determine_inverse(self)
        res=super(Project,self).write(vals)ifvalselseTrue

        ifallowed_users_changed:
            forprojectinself:
                permission_removed=allowed_users.get(project)-project.allowed_user_ids
                allowed_portal_users_removed=permission_removed.filtered('share')
                project.message_unsubscribe(allowed_portal_users_removed.partner_id.commercial_partner_id.ids)
                fortaskinproject.task_ids:
                    task.allowed_user_ids-=permission_removed

        if'allow_recurring_tasks'invalsandnotvals.get('allow_recurring_tasks'):
            self.env['project.task'].search([('project_id','in',self.ids),('recurring_task','=',True)]).write({'recurring_task':False})

        if'active'invals:
            #archiving/unarchivingaprojectdoesitonitstasks,too
            self.with_context(active_test=False).mapped('tasks').write({'active':vals['active']})
        ifvals.get('partner_id')orvals.get('privacy_visibility'):
            forprojectinself.filtered(lambdaproject:project.privacy_visibility=='portal'):
                project.allowed_user_ids|=project.partner_id.user_ids

        returnres

    defaction_unlink(self):
        wizard=self.env['project.delete.wizard'].create({
            'project_ids':self.ids
        })

        return{
            'name':_('Confirmation'),
            'view_mode':'form',
            'res_model':'project.delete.wizard',
            'views':[(self.env.ref('project.project_delete_wizard_form').id,'form')],
            'type':'ir.actions.act_window',
            'res_id':wizard.id,
            'target':'new',
            'context':self.env.context,
        }

    defunlink(self):
        #Checkprojectisempty
        forprojectinself.with_context(active_test=False):
            ifproject.tasks:
                raiseUserError(_('Youcannotdeleteaprojectcontainingtasks.Youcaneitherarchiveitorfirstdeleteallofitstasks.'))
        #Deletetheemptyrelatedanalyticaccount
        analytic_accounts_to_delete=self.env['account.analytic.account']
        forprojectinself:
            ifproject.analytic_account_idandnotproject.analytic_account_id.line_ids:
                analytic_accounts_to_delete|=project.analytic_account_id
        result=super(Project,self).unlink()
        analytic_accounts_to_delete.unlink()
        returnresult

    defmessage_subscribe(self,partner_ids=None,channel_ids=None,subtype_ids=None):
        """
        Subscribetoallexistingactivetaskswhensubscribingtoaproject
        Andaddtheportalusersubscribedtoallowedportalusers
        """
        res=super(Project,self).message_subscribe(partner_ids=partner_ids,channel_ids=channel_ids,subtype_ids=subtype_ids)
        project_subtypes=self.env['mail.message.subtype'].browse(subtype_ids)ifsubtype_idselseNone
        task_subtypes=(project_subtypes.mapped('parent_id')|project_subtypes.filtered(lambdasub:sub.internalorsub.default)).idsifproject_subtypeselseNone
        ifnotsubtype_idsortask_subtypes:
            self.mapped('tasks').message_subscribe(
                partner_ids=partner_ids,channel_ids=channel_ids,subtype_ids=task_subtypes)
        ifpartner_ids:
            all_users=self.env['res.partner'].browse(partner_ids).user_ids
            portal_users=all_users.filtered('share')
            internal_users=all_users-portal_users
            self.allowed_portal_user_ids|=portal_users
            self.allowed_internal_user_ids|=internal_users
        returnres

    defmessage_unsubscribe(self,partner_ids=None,channel_ids=None):
        """Unsubscribefromalltaskswhenunsubscribingfromaproject"""
        self.mapped('tasks').message_unsubscribe(partner_ids=partner_ids,channel_ids=channel_ids)
        returnsuper(Project,self).message_unsubscribe(partner_ids=partner_ids,channel_ids=channel_ids)

    def_alias_get_creation_values(self):
        values=super(Project,self)._alias_get_creation_values()
        values['alias_model_id']=self.env['ir.model']._get('project.task').id
        ifself.id:
            values['alias_defaults']=defaults=ast.literal_eval(self.alias_defaultsor"{}")
            defaults['project_id']=self.id
        returnvalues

    #---------------------------------------------------
    # Actions
    #---------------------------------------------------

    deftoggle_favorite(self):
        favorite_projects=not_fav_projects=self.env['project.project'].sudo()
        forprojectinself:
            ifself.env.userinproject.favorite_user_ids:
                favorite_projects|=project
            else:
                not_fav_projects|=project

        #ProjectUserhasnowriteaccessforproject.
        not_fav_projects.write({'favorite_user_ids':[(4,self.env.uid)]})
        favorite_projects.write({'favorite_user_ids':[(3,self.env.uid)]})

    defaction_view_tasks(self):
        action=self.with_context(active_id=self.id,active_ids=self.ids)\
            .env.ref('project.act_project_project_2_project_task_all')\
            .sudo().read()[0]
        action['display_name']=self.name
        returnaction

    defaction_view_account_analytic_line(self):
        """returntheactiontoseealltheanalyticlinesoftheproject'sanalyticaccount"""
        action=self.env["ir.actions.actions"]._for_xml_id("analytic.account_analytic_line_action")
        action['context']={'default_account_id':self.analytic_account_id.id}
        action['domain']=[('account_id','=',self.analytic_account_id.id)]
        returnaction

    defaction_view_all_rating(self):
        """returntheactiontoseealltheratingoftheprojectandactivatedefaultfilters"""
        action=self.env['ir.actions.act_window']._for_xml_id('project.rating_rating_action_view_project_rating')
        action['name']=_('Ratingsof%s')%(self.name,)
        action_context=ast.literal_eval(action['context'])ifaction['context']else{}
        action_context.update(self._context)
        action_context['search_default_parent_res_name']=self.name
        action_context.pop('group_by',None)
        returndict(action,context=action_context)

    #---------------------------------------------------
    # BusinessMethods
    #---------------------------------------------------

    @api.model
    def_create_analytic_account_from_values(self,values):
        analytic_account=self.env['account.analytic.account'].create({
            'name':values.get('name',_('UnknownAnalyticAccount')),
            'company_id':values.get('company_id')orself.env.company.id,
            'partner_id':values.get('partner_id'),
            'active':True,
        })
        returnanalytic_account

    def_create_analytic_account(self):
        forprojectinself:
            analytic_account=self.env['account.analytic.account'].create({
                'name':project.name,
                'company_id':project.company_id.id,
                'partner_id':project.partner_id.id,
                'active':True,
            })
            project.write({'analytic_account_id':analytic_account.id})

    #---------------------------------------------------
    #Ratingbusiness
    #---------------------------------------------------

    #Thismethodshouldbecalledonceadaybythescheduler
    @api.model
    def_send_rating_all(self):
        projects=self.search([
            ('rating_active','=',True),
            ('rating_status','=','periodic'),
            ('rating_request_deadline','<=',fields.Datetime.now())
        ])
        forprojectinprojects:
            project.task_ids._send_task_rating_mail()
            project._compute_rating_request_deadline()
            self.env.cr.commit()


classTask(models.Model):
    _name="project.task"
    _description="Task"
    _date_name="date_assign"
    _inherit=['portal.mixin','mail.thread.cc','mail.activity.mixin','rating.mixin']
    _mail_post_access='read'
    _order="prioritydesc,sequence,iddesc"
    _check_company_auto=True

    def_get_default_stage_id(self):
        """Givesdefaultstage_id"""
        project_id=self.env.context.get('default_project_id')
        ifnotproject_id:
            returnFalse
        returnself.stage_find(project_id,[('fold','=',False),('is_closed','=',False)])

    @api.model
    def_default_company_id(self):
        ifself._context.get('default_project_id'):
            returnself.env['project.project'].browse(self._context['default_project_id']).company_id
        returnself.env.company

    @api.model
    def_read_group_stage_ids(self,stages,domain,order):
        search_domain=[('id','in',stages.ids)]
        if'default_project_id'inself.env.context:
            search_domain=['|',('project_ids','=',self.env.context['default_project_id'])]+search_domain

        stage_ids=stages._search(search_domain,order=order,access_rights_uid=SUPERUSER_ID)
        returnstages.browse(stage_ids)

    active=fields.Boolean(default=True)
    name=fields.Char(string='Title',tracking=True,required=True,index=True)
    description=fields.Html(string='Description')
    priority=fields.Selection([
        ('0','Normal'),
        ('1','Important'),
    ],default='0',index=True,string="Priority")
    sequence=fields.Integer(string='Sequence',index=True,default=10,
        help="Givesthesequenceorderwhendisplayingalistoftasks.")
    stage_id=fields.Many2one('project.task.type',string='Stage',compute='_compute_stage_id',
        store=True,readonly=False,ondelete='restrict',tracking=True,index=True,
        default=_get_default_stage_id,group_expand='_read_group_stage_ids',
        domain="[('project_ids','=',project_id)]",copy=False)
    tag_ids=fields.Many2many('project.tags',string='Tags')
    kanban_state=fields.Selection([
        ('normal','InProgress'),
        ('done','Ready'),
        ('blocked','Blocked')],string='KanbanState',
        copy=False,default='normal',required=True)
    kanban_state_label=fields.Char(compute='_compute_kanban_state_label',string='KanbanStateLabel',tracking=True)
    create_date=fields.Datetime("CreatedOn",readonly=True,index=True)
    write_date=fields.Datetime("LastUpdatedOn",readonly=True,index=True)
    date_end=fields.Datetime(string='EndingDate',index=True,copy=False)
    date_assign=fields.Datetime(string='AssigningDate',index=True,copy=False,readonly=True)
    date_deadline=fields.Date(string='Deadline',index=True,copy=False,tracking=True)
    date_last_stage_update=fields.Datetime(string='LastStageUpdate',
        index=True,
        copy=False,
        readonly=True)
    project_id=fields.Many2one('project.project',string='Project',
        compute='_compute_project_id',store=True,readonly=False,
        index=True,tracking=True,check_company=True,change_default=True)
    planned_hours=fields.Float("InitiallyPlannedHours",help='Timeplannedtoachievethistask(includingitssub-tasks).',tracking=True)
    subtask_planned_hours=fields.Float("Sub-tasksPlannedHours",compute='_compute_subtask_planned_hours',help="Sumofthetimeplannedofallthesub-taskslinkedtothistask.Usuallylessorequaltotheinitiallytimeplannedofthistask.")
    user_id=fields.Many2one('res.users',
        string='Assignedto',
        default=lambdaself:self.env.uid,
        index=True,tracking=True)
    partner_id=fields.Many2one('res.partner',
        string='Customer',
        compute='_compute_partner_id',store=True,readonly=False,
        domain="['|',('company_id','=',False),('company_id','=',company_id)]")
    partner_is_company=fields.Boolean(related='partner_id.is_company',readonly=True)
    commercial_partner_id=fields.Many2one(related='partner_id.commercial_partner_id')
    partner_email=fields.Char(
        compute='_compute_partner_email',inverse='_inverse_partner_email',
        string='Email',readonly=False,store=True,copy=False)
    partner_phone=fields.Char(
        compute='_compute_partner_phone',inverse='_inverse_partner_phone',
        string="Phone",readonly=False,store=True,copy=False)
    ribbon_message=fields.Char('Ribbonmessage',compute='_compute_ribbon_message')
    partner_city=fields.Char(related='partner_id.city',readonly=False)
    manager_id=fields.Many2one('res.users',string='ProjectManager',related='project_id.user_id',readonly=True)
    company_id=fields.Many2one(
        'res.company',string='Company',compute='_compute_company_id',store=True,readonly=False,
        required=True,copy=True,default=_default_company_id)
    color=fields.Integer(string='ColorIndex')
    user_email=fields.Char(related='user_id.email',string='UserEmail',readonly=True,related_sudo=False)
    attachment_ids=fields.One2many('ir.attachment',compute='_compute_attachment_ids',string="MainAttachments",
        help="Attachmentthatdon'tcomefrommessage.")
    #Inthedomainofdisplayed_image_id,wecouln'tuseattachment_idsbecauseaone2manyisrepresentedasalistofcommandssoweusedres_model&res_id
    displayed_image_id=fields.Many2one('ir.attachment',domain="[('res_model','=','project.task'),('res_id','=',id),('mimetype','ilike','image')]",string='CoverImage')
    legend_blocked=fields.Char(related='stage_id.legend_blocked',string='KanbanBlockedExplanation',readonly=True,related_sudo=False)
    legend_done=fields.Char(related='stage_id.legend_done',string='KanbanValidExplanation',readonly=True,related_sudo=False)
    legend_normal=fields.Char(related='stage_id.legend_normal',string='KanbanOngoingExplanation',readonly=True,related_sudo=False)
    is_closed=fields.Boolean(related="stage_id.is_closed",string="ClosingStage",readonly=True,related_sudo=False)
    parent_id=fields.Many2one('project.task',string='ParentTask',index=True)
    child_ids=fields.One2many('project.task','parent_id',string="Sub-tasks",context={'active_test':False})
    subtask_project_id=fields.Many2one('project.project',related="project_id.subtask_project_id",string='Sub-taskProject',readonly=True)
    allow_subtasks=fields.Boolean(string="AllowSub-tasks",related="project_id.allow_subtasks",readonly=True)
    subtask_count=fields.Integer("Sub-taskcount",compute='_compute_subtask_count')
    email_from=fields.Char(string='EmailFrom',help="Thesepeoplewillreceiveemail.",index=True,
        compute='_compute_email_from',store="True",readonly=False,copy=False)
    allowed_user_ids=fields.Many2many('res.users',string="Visibleto",groups='project.group_project_manager',compute='_compute_allowed_user_ids',store=True,readonly=False,copy=False)
    project_privacy_visibility=fields.Selection(related='project_id.privacy_visibility',string="ProjectVisibility")
    #Computedfieldaboutworkingtimeelapsedbetweenrecordcreationandassignation/closing.
    working_hours_open=fields.Float(compute='_compute_elapsed',string='Workinghourstoassign',store=True,group_operator="avg")
    working_hours_close=fields.Float(compute='_compute_elapsed',string='Workinghourstoclose',store=True,group_operator="avg")
    working_days_open=fields.Float(compute='_compute_elapsed',string='Workingdaystoassign',store=True,group_operator="avg")
    working_days_close=fields.Float(compute='_compute_elapsed',string='Workingdaystoclose',store=True,group_operator="avg")
    #customerportal:includecommentandincomingemailsincommunicationhistory
    website_message_ids=fields.One2many(domain=lambdaself:[('model','=',self._name),('message_type','in',['email','comment'])])

    #recurrencefields
    allow_recurring_tasks=fields.Boolean(related='project_id.allow_recurring_tasks')
    recurring_task=fields.Boolean(string="Recurrent")
    recurring_count=fields.Integer(string="TasksinRecurrence",compute='_compute_recurring_count')
    recurrence_id=fields.Many2one('project.task.recurrence',copy=False)
    recurrence_update=fields.Selection([
        ('this','Thistask'),
        ('subsequent','Thisandfollowingtasks'),
        ('all','Alltasks'),
    ],default='this',store=False)
    recurrence_message=fields.Char(string='NextRecurrencies',compute='_compute_recurrence_message')

    repeat_interval=fields.Integer(string='RepeatEvery',default=1,compute='_compute_repeat',readonly=False)
    repeat_unit=fields.Selection([
        ('day','Days'),
        ('week','Weeks'),
        ('month','Months'),
        ('year','Years'),
    ],default='week',compute='_compute_repeat',readonly=False)
    repeat_type=fields.Selection([
        ('forever','Forever'),
        ('until','EndDate'),
        ('after','NumberofRepetitions'),
    ],default="forever",string="Until",compute='_compute_repeat',readonly=False)
    repeat_until=fields.Date(string="EndDate",compute='_compute_repeat',readonly=False)
    repeat_number=fields.Integer(string="Repetitions",default=1,compute='_compute_repeat',readonly=False)

    repeat_on_month=fields.Selection([
        ('date','DateoftheMonth'),
        ('day','DayoftheMonth'),
    ],default='date',compute='_compute_repeat',readonly=False)

    repeat_on_year=fields.Selection([
        ('date','DateoftheYear'),
        ('day','DayoftheYear'),
    ],default='date',compute='_compute_repeat',readonly=False)

    mon=fields.Boolean(string="Mon",compute='_compute_repeat',readonly=False)
    tue=fields.Boolean(string="Tue",compute='_compute_repeat',readonly=False)
    wed=fields.Boolean(string="Wed",compute='_compute_repeat',readonly=False)
    thu=fields.Boolean(string="Thu",compute='_compute_repeat',readonly=False)
    fri=fields.Boolean(string="Fri",compute='_compute_repeat',readonly=False)
    sat=fields.Boolean(string="Sat",compute='_compute_repeat',readonly=False)
    sun=fields.Boolean(string="Sun",compute='_compute_repeat',readonly=False)

    repeat_day=fields.Selection([
        (str(i),str(i))foriinrange(1,32)
    ],compute='_compute_repeat',readonly=False)
    repeat_week=fields.Selection([
        ('first','First'),
        ('second','Second'),
        ('third','Third'),
        ('last','Last'),
    ],default='first',compute='_compute_repeat',readonly=False)
    repeat_weekday=fields.Selection([
        ('mon','Monday'),
        ('tue','Tuesday'),
        ('wed','Wednesday'),
        ('thu','Thursday'),
        ('fri','Friday'),
        ('sat','Saturday'),
        ('sun','Sunday'),
    ],string='DayOfTheWeek',compute='_compute_repeat',readonly=False)
    repeat_month=fields.Selection([
        ('january','January'),
        ('february','February'),
        ('march','March'),
        ('april','April'),
        ('may','May'),
        ('june','June'),
        ('july','July'),
        ('august','August'),
        ('september','September'),
        ('october','October'),
        ('november','November'),
        ('december','December'),
    ],compute='_compute_repeat',readonly=False)

    repeat_show_dow=fields.Boolean(compute='_compute_repeat_visibility')
    repeat_show_day=fields.Boolean(compute='_compute_repeat_visibility')
    repeat_show_week=fields.Boolean(compute='_compute_repeat_visibility')
    repeat_show_month=fields.Boolean(compute='_compute_repeat_visibility')

    @api.model
    def_get_recurrence_fields(self):
        return['repeat_interval','repeat_unit','repeat_type','repeat_until','repeat_number',
                'repeat_on_month','repeat_on_year','mon','tue','wed','thu','fri','sat',
                'sun','repeat_day','repeat_week','repeat_month','repeat_weekday']

    @api.depends('recurring_task','repeat_unit','repeat_on_month','repeat_on_year')
    def_compute_repeat_visibility(self):
        fortaskinself:
            task.repeat_show_day=task.recurring_taskand(task.repeat_unit=='month'andtask.repeat_on_month=='date')or(task.repeat_unit=='year'andtask.repeat_on_year=='date')
            task.repeat_show_week=task.recurring_taskand(task.repeat_unit=='month'andtask.repeat_on_month=='day')or(task.repeat_unit=='year'andtask.repeat_on_year=='day')
            task.repeat_show_dow=task.recurring_taskandtask.repeat_unit=='week'
            task.repeat_show_month=task.recurring_taskandtask.repeat_unit=='year'

    @api.depends('recurring_task')
    def_compute_repeat(self):
        rec_fields=self._get_recurrence_fields()
        defaults=self.default_get(rec_fields)
        fortaskinself:
            forfinrec_fields:
                iftask.recurrence_id:
                    task[f]=task.recurrence_id[f]
                else:
                    iftask.recurring_task:
                        task[f]=defaults.get(f)
                    else:
                        task[f]=False

    def_get_weekdays(self,n=1):
        self.ensure_one()
        ifself.repeat_unit=='week':
            return[fn(n)forday,fninDAYS.items()ifself[day]]
        return[DAYS.get(self.repeat_weekday)(n)]

    def_get_recurrence_start_date(self):
        returnfields.Date.today()

    @api.depends(
        'recurring_task','repeat_interval','repeat_unit','repeat_type','repeat_until',
        'repeat_number','repeat_on_month','repeat_on_year','mon','tue','wed','thu','fri',
        'sat','sun','repeat_day','repeat_week','repeat_month','repeat_weekday')
    def_compute_recurrence_message(self):
        self.recurrence_message=False
        fortaskinself.filtered(lambdat:t.recurring_taskandt._is_recurrence_valid()):
            date=task._get_recurrence_start_date()
            number_occurrences=min(5,task.repeat_numberiftask.repeat_type=='after'else5)
            delta=task.repeat_intervaliftask.repeat_unit=='day'else1
            recurring_dates=self.env['project.task.recurrence']._get_next_recurring_dates(
                date+timedelta(days=delta),
                task.repeat_interval,
                task.repeat_unit,
                task.repeat_type,
                task.repeat_until,
                task.repeat_on_month,
                task.repeat_on_year,
                task._get_weekdays(WEEKS.get(task.repeat_week)),
                task.repeat_day,
                task.repeat_week,
                task.repeat_month,
                count=number_occurrences)
            date_format=self.env['res.lang']._lang_get(self.env.user.lang).date_formatorget_lang(self.env).date_format
            task.recurrence_message='<ul>'
            fordateinrecurring_dates[:5]:
                task.recurrence_message+='<li>%s</li>'%date.strftime(date_format)
            iftask.repeat_type=='after'andtask.repeat_number>5ortask.repeat_type=='forever'orlen(recurring_dates)>5:
                task.recurrence_message+='<li>...</li>'
            task.recurrence_message+='</ul>'
            iftask.repeat_type=='until':
                task.recurrence_message+=_('<p><em>Numberoftasks:%(tasks_count)s</em></p>')%{'tasks_count':len(recurring_dates)}

    def_is_recurrence_valid(self):
        self.ensure_one()
        returnself.repeat_interval>0and\
                (notself.repeat_show_doworself._get_weekdays())and\
                (self.repeat_type!='after'orself.repeat_number)and\
                (self.repeat_type!='until'orself.repeat_untilandself.repeat_until>fields.Date.today())

    @api.depends('recurrence_id')
    def_compute_recurring_count(self):
        self.recurring_count=0
        recurring_tasks=self.filtered(lambdal:l.recurrence_id)
        count=self.env['project.task'].read_group([('recurrence_id','in',recurring_tasks.recurrence_id.ids)],['id'],'recurrence_id')
        tasks_count={c.get('recurrence_id')[0]:c.get('recurrence_id_count')forcincount}
        fortaskinrecurring_tasks:
            task.recurring_count=tasks_count.get(task.recurrence_id.id,0)

    @api.depends('partner_id.email')
    def_compute_partner_email(self):
        fortaskinself:
            iftask.partner_idandtask.partner_id.email!=task.partner_email:
                task.partner_email=task.partner_id.email

    def_inverse_partner_email(self):
        fortaskinself:
            iftask.partner_idandtask.partner_email!=task.partner_id.email:
                task.partner_id.email=task.partner_email

    @api.depends('partner_id.phone')
    def_compute_partner_phone(self):
        fortaskinself:
            iftask.partner_idandtask.partner_phone!=task.partner_id.phone:
                task.partner_phone=task.partner_id.phone

    def_inverse_partner_phone(self):
        fortaskinself:
            iftask.partner_idandtask.partner_phone!=task.partner_id.phone:
                task.partner_id.phone=task.partner_phone

    @api.depends('partner_email','partner_phone','partner_id')
    def_compute_ribbon_message(self):
        fortaskinself:
            will_write_email=task.partner_idandtask.partner_email!=task.partner_id.email
            will_write_phone=task.partner_idandtask.partner_phone!=task.partner_id.phone

            ifwill_write_emailandwill_write_phone:
                task.ribbon_message=_('Bysavingthischange,thecustomeremailandphonenumberwillalsobeupdated.')
            elifwill_write_email:
                task.ribbon_message=_('Bysavingthischange,thecustomeremailwillalsobeupdated.')
            elifwill_write_phone:
                task.ribbon_message=_('Bysavingthischange,thecustomerphonenumberwillalsobeupdated.')
            else:
                task.ribbon_message=False

    @api.constrains('parent_id')
    def_check_parent_id(self):
        ifnotself._check_recursion():
            raiseValidationError(_('Error!Youcannotcreaterecursivehierarchyoftasks.'))

    @api.constrains('allowed_user_ids')
    def_check_no_portal_allowed(self):
        fortaskinself.filtered(lambdat:t.project_id.privacy_visibility!='portal'):
            portal_users=task.allowed_user_ids.filtered('share')
            ifportal_users:
                user_names=','.join(portal_users[:10].mapped('name'))
                raiseValidationError(_("Theprojectvisibilitysettingdoesn'tallowportaluserstoseetheproject'stasks.(%s)",user_names))

    def_compute_attachment_ids(self):
        fortaskinself:
            attachment_ids=self.env['ir.attachment'].search([('res_id','=',task.id),('res_model','=','project.task')]).ids
            message_attachment_ids=task.mapped('message_ids.attachment_ids').ids #frommail_thread
            task.attachment_ids=[(6,0,list(set(attachment_ids)-set(message_attachment_ids)))]

    @api.depends('project_id.allowed_user_ids','project_id.privacy_visibility')
    def_compute_allowed_user_ids(self):
        fortaskinself.with_context(prefetch_fields=False):
            portal_users=task.allowed_user_ids.filtered('share')
            internal_users=task.allowed_user_ids-portal_users
            iftask.project_id.privacy_visibility=='followers':
                task.allowed_user_ids|=task.project_id.allowed_internal_user_ids
                task.allowed_user_ids-=portal_users
            eliftask.project_id.privacy_visibility=='portal':
                task.allowed_user_ids|=task.project_id.allowed_portal_user_ids
            iftask.project_id.privacy_visibility!='portal':
                task.allowed_user_ids-=portal_users
            eliftask.project_id.privacy_visibility!='followers':
                task.allowed_user_ids-=internal_users

    @api.depends('create_date','date_end','date_assign')
    def_compute_elapsed(self):
        task_linked_to_calendar=self.filtered(
            lambdatask:task.project_id.resource_calendar_idandtask.create_date
        )
        fortaskintask_linked_to_calendar:
            dt_create_date=fields.Datetime.from_string(task.create_date)

            iftask.date_assign:
                dt_date_assign=fields.Datetime.from_string(task.date_assign)
                duration_data=task.project_id.resource_calendar_id.get_work_duration_data(dt_create_date,dt_date_assign,compute_leaves=True)
                task.working_hours_open=duration_data['hours']
                task.working_days_open=duration_data['days']
            else:
                task.working_hours_open=0.0
                task.working_days_open=0.0

            iftask.date_end:
                dt_date_end=fields.Datetime.from_string(task.date_end)
                duration_data=task.project_id.resource_calendar_id.get_work_duration_data(dt_create_date,dt_date_end,compute_leaves=True)
                task.working_hours_close=duration_data['hours']
                task.working_days_close=duration_data['days']
            else:
                task.working_hours_close=0.0
                task.working_days_close=0.0

        (self-task_linked_to_calendar).update(dict.fromkeys(
            ['working_hours_open','working_hours_close','working_days_open','working_days_close'],0.0))

    @api.depends('stage_id','kanban_state')
    def_compute_kanban_state_label(self):
        fortaskinself:
            iftask.kanban_state=='normal':
                task.kanban_state_label=task.legend_normal
            eliftask.kanban_state=='blocked':
                task.kanban_state_label=task.legend_blocked
            else:
                task.kanban_state_label=task.legend_done

    def_compute_access_url(self):
        super(Task,self)._compute_access_url()
        fortaskinself:
            task.access_url='/my/task/%s'%task.id

    def_compute_access_warning(self):
        super(Task,self)._compute_access_warning()
        fortaskinself.filtered(lambdax:x.project_id.privacy_visibility!='portal'):
            task.access_warning=_(
                "Thetaskcannotbesharedwiththerecipient(s)becausetheprivacyoftheprojectistoorestricted.Settheprivacyoftheprojectto'Visiblebyfollowingcustomers'inordertomakeitaccessiblebytherecipient(s).")

    @api.depends('child_ids.planned_hours')
    def_compute_subtask_planned_hours(self):
        fortaskinself:
            task.subtask_planned_hours=sum(child_task.planned_hours+child_task.subtask_planned_hoursforchild_taskintask.child_ids)

    @api.depends('child_ids')
    def_compute_subtask_count(self):
        fortaskinself:
            task.subtask_count=len(task._get_all_subtasks())

    @api.onchange('company_id')
    def_onchange_task_company(self):
        ifself.project_id.company_id!=self.company_id:
            self.project_id=False

    @api.depends('project_id.company_id')
    def_compute_company_id(self):
        fortaskinself.filtered(lambdatask:task.project_id):
            task.company_id=task.project_id.company_id

    @api.depends('project_id')
    def_compute_stage_id(self):
        fortaskinself:
            iftask.project_id:
                iftask.project_idnotintask.stage_id.project_ids:
                    task.stage_id=task.stage_find(task.project_id.id,[
                        ('fold','=',False),('is_closed','=',False)])
            else:
                task.stage_id=False

    @api.returns('self',lambdavalue:value.id)
    defcopy(self,default=None):
        ifdefaultisNone:
            default={}
        ifnotdefault.get('name'):
            default['name']=_("%s(copy)",self.name)
        ifself.recurrence_id:
            default['recurrence_id']=self.recurrence_id.copy().id
        returnsuper(Task,self).copy(default)

    @api.constrains('parent_id')
    def_check_parent_id(self):
        fortaskinself:
            ifnottask._check_recursion():
                raiseValidationError(_('Error!Youcannotcreaterecursivehierarchyoftask(s).'))

    @api.model
    defget_empty_list_help(self,help):
        tname=_("task")
        project_id=self.env.context.get('default_project_id',False)
        ifproject_id:
            name=self.env['project.project'].browse(project_id).label_tasks
            ifname:tname=name.lower()

        self=self.with_context(
            empty_list_help_id=self.env.context.get('default_project_id'),
            empty_list_help_model='project.project',
            empty_list_help_document_name=tname,
        )
        returnsuper(Task,self).get_empty_list_help(help)

    defmessage_subscribe(self,partner_ids=None,channel_ids=None,subtype_ids=None):
        """
        Addtheuserssubscribedtoallowedportalusers
        """
        res=super(Task,self).message_subscribe(partner_ids=partner_ids,channel_ids=channel_ids,subtype_ids=subtype_ids)
        ifpartner_ids:
            new_allowed_users=self.env['res.partner'].browse(partner_ids).user_ids.filtered('share')
            tasks=self.filtered(lambdatask:task.project_id.privacy_visibility=='portal')
            tasks.sudo().allowed_user_ids|=new_allowed_users
        returnres

    #----------------------------------------
    #Casemanagement
    #----------------------------------------

    defstage_find(self,section_id,domain=[],order='sequence'):
        """Overrideofthebase.stagemethod
            Parameterofthestagesearchtakenfromthelead:
            -section_id:ifset,stagesmustbelongtothissectionor
              beadefaultstage;ifnotset,stagesmustbedefault
              stages
        """
        #collectallsection_ids
        section_ids=[]
        ifsection_id:
            section_ids.append(section_id)
        section_ids.extend(self.mapped('project_id').ids)
        search_domain=[]
        ifsection_ids:
            search_domain=[('|')]*(len(section_ids)-1)
            forsection_idinsection_ids:
                search_domain.append(('project_ids','=',section_id))
        search_domain+=list(domain)
        #performsearch,returnthefirstfound
        returnself.env['project.task.type'].search(search_domain,order=order,limit=1).id

    #------------------------------------------------
    #CRUDoverrides
    #------------------------------------------------
    @api.model
    defdefault_get(self,default_fields):
        vals=super(Task,self).default_get(default_fields)

        days=list(DAYS.keys())
        week_start=fields.Datetime.today().weekday()

        ifall(dindefault_fieldsfordindays):
            vals[days[week_start]]=True
        if'repeat_day'indefault_fields:
            vals['repeat_day']=str(fields.Datetime.today().day)
        if'repeat_month'indefault_fields:
            vals['repeat_month']=self._fields.get('repeat_month').selection[fields.Datetime.today().month-1][0]
        if'repeat_until'indefault_fields:
            vals['repeat_until']=fields.Date.today()+timedelta(days=7)
        if'repeat_weekday'indefault_fields:
            vals['repeat_weekday']=self._fields.get('repeat_weekday').selection[week_start][0]

        returnvals

    @api.model_create_multi
    defcreate(self,vals_list):
        default_stage=dict()
        forvalsinvals_list:
            project_id=vals.get('project_id')orself.env.context.get('default_project_id')
            ifproject_idandnot"company_id"invals:
                vals["company_id"]=self.env["project.project"].browse(
                    project_id
                ).company_id.idorself.env.company.id
            ifproject_idand"stage_id"notinvals:
                #1)Allowskeepingthebatchcreationoftasks
                #2)Ensurethedefaultsarecorrect(andcomputedoncebyproject),
                #byusingdefaultget(insteadof_get_default_stage_idor_stage_find),
                ifproject_idnotindefault_stage:
                    default_stage[project_id]=self.with_context(
                        default_project_id=project_id
                    ).default_get(['stage_id']).get('stage_id')
                vals["stage_id"]=default_stage[project_id]
            #user_idchange:updatedate_assign
            ifvals.get('user_id'):
                vals['date_assign']=fields.Datetime.now()
            #Stagechange:Updatedate_endiffoldedstageanddate_last_stage_update
            ifvals.get('stage_id'):
                vals.update(self.update_date_end(vals['stage_id']))
                vals['date_last_stage_update']=fields.Datetime.now()
            #recurrence
            rec_fields=vals.keys()&self._get_recurrence_fields()
            ifrec_fieldsandvals.get('recurring_task')isTrue:
                rec_values={rec_field:vals[rec_field]forrec_fieldinrec_fields}
                rec_values['next_recurrence_date']=fields.Datetime.today()
                recurrence=self.env['project.task.recurrence'].create(rec_values)
                vals['recurrence_id']=recurrence.id
        tasks=super().create(vals_list)
        fortaskintasks:
            iftask.project_id.privacy_visibility=='portal':
                task._portal_ensure_token()
        returntasks

    def_load_records_create(self,values):
        tasks=super()._load_records_create(values)
        stage_ids_per_project=defaultdict(list)
        fortaskintasks:
            iftask.stage_idandtask.stage_idnotintask.project_id.type_idsandtask.stage_id.idnotinstage_ids_per_project[task.project_id]:
                stage_ids_per_project[task.project_id].append(task.stage_id.id)

        forproject,stage_idsinstage_ids_per_project.items():
            project.write({'type_ids':[(4,stage_id)forstage_idinstage_ids]})

        returntasks

    defwrite(self,vals):
        now=fields.Datetime.now()
        if'parent_id'invalsandvals['parent_id']inself.ids:
            raiseUserError(_("Sorry.Youcan'tsetataskasitsparenttask."))
        if'active'invalsandnotvals.get('active')andany(self.mapped('recurrence_id')):
            #TODO:showadialogtostoptherecurrence
            raiseUserError(_('Youcannotarchiverecurringtasks.Please,disabletherecurrencefirst.'))
        #stagechange:updatedate_last_stage_update
        if'stage_id'invals:
            vals.update(self.update_date_end(vals['stage_id']))
            vals['date_last_stage_update']=now
            #resetkanbanstatewhenchangingstage
            if'kanban_state'notinvals:
                vals['kanban_state']='normal'
        #user_idchange:updatedate_assign
        ifvals.get('user_id')and'date_assign'notinvals:
            vals['date_assign']=now

        #recurrencefields
        rec_fields=vals.keys()&self._get_recurrence_fields()
        ifrec_fields:
            rec_values={rec_field:vals[rec_field]forrec_fieldinrec_fields}
            fortaskinself:
                iftask.recurrence_id:
                    task.recurrence_id.write(rec_values)
                elifvals.get('recurring_task'):
                    rec_values['next_recurrence_date']=fields.Datetime.today()
                    recurrence=self.env['project.task.recurrence'].create(rec_values)
                    task.recurrence_id=recurrence.id

        ifnotvals.get('recurring_task',True)andself.recurrence_id:
            tasks_in_recurrence=self.recurrence_id.task_ids
            self.recurrence_id.unlink()
            tasks_in_recurrence.write({'recurring_task':False})

        tasks=self
        recurrence_update=vals.pop('recurrence_update','this')
        ifrecurrence_update!='this':
            recurrence_domain=[]
            ifrecurrence_update=='subsequent':
                fortaskinself:
                    recurrence_domain=OR([recurrence_domain,['&',('recurrence_id','=',task.recurrence_id.id),('create_date','>=',task.create_date)]])
            else:
                recurrence_domain=[('recurrence_id','in',self.recurrence_id.ids)]
            tasks|=self.env['project.task'].search(recurrence_domain)

        result=super(Task,tasks).write(vals)
        #ratingonstage
        if'stage_id'invalsandvals.get('stage_id'):
            self.filtered(lambdax:x.project_id.rating_activeandx.project_id.rating_status=='stage')._send_task_rating_mail(force_send=True)
        returnresult

    defupdate_date_end(self,stage_id):
        project_task_type=self.env['project.task.type'].browse(stage_id)
        ifproject_task_type.foldorproject_task_type.is_closed:
            return{'date_end':fields.Datetime.now()}
        return{'date_end':False}

    defunlink(self):
        ifany(self.mapped('recurrence_id')):
            #TODO:showadialogtostoptherecurrence
            raiseUserError(_('Youcannotdeleterecurringtasks.Please,disabletherecurrencefirst.'))
        returnsuper().unlink()

    #---------------------------------------------------
    #Subtasks
    #---------------------------------------------------

    @api.depends('parent_id.partner_id','project_id.partner_id')
    def_compute_partner_id(self):
        """
        Ifataskhasnopartner_id,usetheprojectpartner_idifany,orelsetheparenttaskpartner_id.
        Oncethetaskpartner_idhasbeenset:
            1)iftheprojectpartner_idchanges,thetaskpartner_idisautomaticallychangedalso.
            2)iftheparenttaskpartner_idchanges,thetaskpartner_idremainsthesame.
        """
        fortaskinself:
            iftask.partner_id:
                iftask.project_id.partner_id:
                    task.partner_id=task.project_id.partner_id
            else:
                task.partner_id=task.project_id.partner_idortask.parent_id.partner_id

    @api.depends('partner_id.email','parent_id.email_from')
    def_compute_email_from(self):
        fortaskinself:
            task.email_from=task.partner_id.emailor((task.partner_idortask.parent_id)andtask.email_from)ortask.parent_id.email_from

    @api.depends('parent_id.project_id.subtask_project_id')
    def_compute_project_id(self):
        fortaskinself:
            ifnottask.project_id:
                task.project_id=task.parent_id.project_id.subtask_project_id

    #---------------------------------------------------
    #Mailgateway
    #---------------------------------------------------

    def_track_template(self,changes):
        res=super(Task,self)._track_template(changes)
        test_task=self[0]
        if'stage_id'inchangesandtest_task.stage_id.mail_template_id:
            res['stage_id']=(test_task.stage_id.mail_template_id,{
                'auto_delete_message':True,
                'subtype_id':self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'),
                'email_layout_xmlid':'mail.mail_notification_light'
            })
        returnres

    def_creation_subtype(self):
        returnself.env.ref('project.mt_task_new')

    def_track_subtype(self,init_values):
        self.ensure_one()
        if'kanban_state_label'ininit_valuesandself.kanban_state=='blocked':
            returnself.env.ref('project.mt_task_blocked')
        elif'kanban_state_label'ininit_valuesandself.kanban_state=='done':
            returnself.env.ref('project.mt_task_ready')
        elif'stage_id'ininit_values:
            returnself.env.ref('project.mt_task_stage')
        returnsuper(Task,self)._track_subtype(init_values)

    def_notify_get_groups(self,msg_vals=None):
        """Handleprojectusersandmanagersrecipientsthatcanassign
        tasksandcreatenewonedirectlyfromnotificationemails.Alsogive
        accessbuttontoportalusersandportalcustomers.Iftheyarenotified
        theyshouldprobablyhaveaccesstothedocument."""
        groups=super(Task,self)._notify_get_groups(msg_vals=msg_vals)
        local_msg_vals=dict(msg_valsor{})
        self.ensure_one()

        project_user_group_id=self.env.ref('project.group_project_user').id
        project_manager_group_id=self.env.ref('project.group_project_manager').id

        group_func=lambdapdata:pdata['type']=='user'andproject_user_group_idinpdata['groups']
        ifself.project_id.privacy_visibility=='followers':
            allowed_user_ids=self.project_id.allowed_internal_user_ids.partner_id.ids
            group_func=lambdapdata:\
                pdata['type']=='user'\
                and(
                        project_manager_group_idinpdata['groups']\
                        or(project_user_group_idinpdata['groups']andpdata['id']inallowed_user_ids)
                )
        new_group=('group_project_user',group_func,{})

        ifnotself.user_idandnotself.stage_id.fold:
            take_action=self._notify_get_action_link('assign',**local_msg_vals)
            project_actions=[{'url':take_action,'title':_('Itakeit')}]
            new_group[2]['actions']=project_actions

        groups=[new_group]+groups

        ifself.project_id.privacy_visibility=='portal':
            allowed_user_ids=self.project_id.allowed_portal_user_ids.partner_id.ids
            groups.insert(0,(
                'allowed_portal_users',
                lambdapdata:pdata['type']=='portal'andpdata['id']inallowed_user_ids,
                {}
            ))

        portal_privacy=self.project_id.privacy_visibility=='portal'
        forgroup_name,group_method,group_dataingroups:
            ifgroup_namein('customer','user')orgroup_name=='portal_customer'andnotportal_privacy:
                group_data['has_button_access']=False
            elifgroup_name=='portal_customer'andportal_privacy:
                group_data['has_button_access']=True

        returngroups

    def_notify_get_reply_to(self,default=None,records=None,company=None,doc_names=None):
        """Overridetosetaliasoftaskstotheirprojectifany."""
        aliases=self.sudo().mapped('project_id')._notify_get_reply_to(default=default,records=None,company=company,doc_names=None)
        res={task.id:aliases.get(task.project_id.id)fortaskinself}
        leftover=self.filtered(lambdarec:notrec.project_id)
        ifleftover:
            res.update(super(Task,leftover)._notify_get_reply_to(default=default,records=None,company=company,doc_names=doc_names))
        returnres

    defemail_split(self,msg):
        email_list=tools.email_split((msg.get('to')or'')+','+(msg.get('cc')or''))
        #checkleft-partisnotalreadyanalias
        aliases=self.mapped('project_id.alias_name')
        return[xforxinemail_listifx.split('@')[0]notinaliases]

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
        create_context=dict(self.env.contextor{})
        create_context['default_user_id']=False
        ifcustom_valuesisNone:
            custom_values={}
        defaults={
            'name':msg.get('subject')or_("NoSubject"),
            'email_from':msg.get('from'),
            'planned_hours':0.0,
            'partner_id':msg.get('author_id')
        }
        defaults.update(custom_values)

        task=super(Task,self.with_context(create_context)).message_new(msg,custom_values=defaults)
        email_list=task.email_split(msg)
        partner_ids=[p.idforpinself.env['mail.thread']._mail_find_partner_from_emails(email_list,records=task,force_create=False)ifp]
        customer_ids=[p.idforpinself.env['mail.thread']._mail_find_partner_from_emails(tools.email_split(defaults['email_from']),records=task)ifp]
        partner_ids+=customer_ids
        task.message_subscribe(partner_ids)
        returntask

    defmessage_update(self,msg,update_vals=None):
        """Overridetoupdatethetaskaccordingtotheemail."""
        email_list=self.email_split(msg)
        partner_ids=[p.idforpinself.env['mail.thread']._mail_find_partner_from_emails(email_list,records=self,force_create=False)ifp]
        self.message_subscribe(partner_ids)
        returnsuper(Task,self).message_update(msg,update_vals=update_vals)

    def_message_get_suggested_recipients(self):
        recipients=super(Task,self)._message_get_suggested_recipients()
        fortaskinself:
            iftask.partner_id:
                reason=_('CustomerEmail')iftask.partner_id.emailelse_('Customer')
                task._message_add_suggested_recipient(recipients,partner=task.partner_id,reason=reason)
            eliftask.email_from:
                task._message_add_suggested_recipient(recipients,email=task.email_from,reason=_('CustomerEmail'))
        returnrecipients

    def_notify_email_header_dict(self):
        headers=super(Task,self)._notify_email_header_dict()
        ifself.project_id:
            current_objects=[hforhinheaders.get('X-Flectra-Objects','').split(',')ifh]
            current_objects.insert(0,'project.project-%s,'%self.project_id.id)
            headers['X-Flectra-Objects']=','.join(current_objects)
        ifself.tag_ids:
            headers['X-Flectra-Tags']=','.join(self.tag_ids.mapped('name'))
        returnheaders

    def_message_post_after_hook(self,message,msg_vals):
        ifmessage.attachment_idsandnotself.displayed_image_id:
            image_attachments=message.attachment_ids.filtered(lambdaa:a.mimetype=='image')
            ifimage_attachments:
                self.displayed_image_id=image_attachments[0]

        ifself.email_fromandnotself.partner_id:
            #weconsiderthatpostingamessagewithaspecifiedrecipient(notafollower,aspecificone)
            #onadocumentwithoutcustomermeansthatitwascreatedthroughthechatterusing
            #suggestedrecipients.ThisheuristicallowstoavoiduglyhacksinJS.
            email_normalized=tools.email_normalize(self.email_from)
            new_partner=message.partner_ids.filtered(
                lambdapartner:partner.email==self.email_fromor(email_normalizedandpartner.email_normalized==email_normalized)
            )
            ifnew_partner:
                ifnew_partner[0].email_normalized:
                    email_domain=('email_from','in',[new_partner[0].email,new_partner[0].email_normalized])
                else:
                    email_domain=('email_from','=',new_partner[0].email)
                self.search([
                    ('partner_id','=',False),email_domain,('stage_id.fold','=',False)
                ]).write({'partner_id':new_partner[0].id})
        returnsuper(Task,self)._message_post_after_hook(message,msg_vals)

    defaction_assign_to_me(self):
        self.write({'user_id':self.env.user.id})

    #Ifdepth==1,returnonlydirectchildren
    #Ifdepth==3,returnchildrentothirdgeneration
    #Ifdepth<=0,returnallchildrenwithoutdepthlimit
    def_get_all_subtasks(self,depth=0):
        children=self.mapped('child_ids').filtered(lambdachildren:children.active)
        ifnotchildren:
            returnself.env['project.task']
        ifdepth==1:
            returnchildren
        returnchildren+children._get_all_subtasks(depth-1)

    defaction_open_parent_task(self):
        return{
            'name':_('ParentTask'),
            'view_mode':'form',
            'res_model':'project.task',
            'res_id':self.parent_id.id,
            'type':'ir.actions.act_window',
            'context':dict(self._context,create=False)
        }

    defaction_subtask(self):
        action=self.env["ir.actions.actions"]._for_xml_id("project.project_task_action_sub_task")

        #displayallsubtasksofcurrenttask
        action['domain']=[('id','child_of',self.id),('id','!=',self.id)]

        #updatecontext,withalldefaultvaluesas'quick_create'doesnotcontainsallfieldinitsview
        ifself._context.get('default_project_id'):
            default_project=self.env['project.project'].browse(self.env.context['default_project_id'])
        else:
            default_project=self.project_id.subtask_project_idorself.project_id
        ctx=dict(self.env.context)
        ctx={k:vfork,vinctx.items()ifnotk.startswith('search_default_')}
        ctx.update({
            'default_name':self.env.context.get('name',self.name)+':',
            'default_parent_id':self.id, #willgivedefaultsubtaskfieldin`default_get`
            'default_company_id':default_project.company_id.idifdefault_projectelseself.env.company.id,
        })

        action['context']=ctx

        returnaction

    defaction_recurring_tasks(self):
        return{
            'name':'TasksinRecurrence',
            'type':'ir.actions.act_window',
            'res_model':'project.task',
            'view_mode':'tree,form',
            'domain':[('recurrence_id','in',self.recurrence_id.ids)],
        }

    #---------------------------------------------------
    #Ratingbusiness
    #---------------------------------------------------

    def_send_task_rating_mail(self,force_send=False):
        fortaskinself:
            rating_template=task.stage_id.rating_template_id
            ifrating_template:
                task.rating_send_request(rating_template,lang=task.partner_id.lang,force_send=force_send)

    defrating_get_partner_id(self):
        res=super(Task,self).rating_get_partner_id()
        ifnotresandself.project_id.partner_id:
            returnself.project_id.partner_id
        returnres

    defrating_apply(self,rate,token=None,feedback=None,subtype_xmlid=None):
        returnsuper(Task,self).rating_apply(rate,token=token,feedback=feedback,subtype_xmlid="project.mt_task_rating")

    def_rating_get_parent_field_name(self):
        return'project_id'


classProjectTags(models.Model):
    """Tagsofproject'stasks"""
    _name="project.tags"
    _description="ProjectTags"

    def_get_default_color(self):
        returnrandint(1,11)

    name=fields.Char('Name',required=True)
    color=fields.Integer(string='Color',default=_get_default_color)

    _sql_constraints=[
        ('name_uniq','unique(name)',"Tagnamealreadyexists!"),
    ]
