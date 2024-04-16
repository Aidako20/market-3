#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importre
fromlxmlimportetree
fromflectra.tools.float_utilsimportfloat_compare
fromflectraimportmodels,fields,api,_
fromflectra.exceptionsimportUserError,ValidationError,RedirectWarning


classProject(models.Model):
    _inherit="project.project"

    allow_timesheets=fields.Boolean(
        "Timesheets",compute='_compute_allow_timesheets',store=True,readonly=False,
        default=True,help="Enabletimesheetingontheproject.")
    analytic_account_id=fields.Many2one(
        #note:replaces['|',('company_id','=',False),('company_id','=',company_id)]
        domain="""[
            '|',('company_id','=',False),('company_id','=',company_id),
            ('partner_id','=?',partner_id),
        ]"""
    )

    timesheet_ids=fields.One2many('account.analytic.line','project_id','AssociatedTimesheets')
    timesheet_encode_uom_id=fields.Many2one('uom.uom',related='company_id.timesheet_encode_uom_id')
    total_timesheet_time=fields.Integer(
        compute='_compute_total_timesheet_time',
        help="Totalnumberoftime(intheproperUoM)recordedintheproject,roundedtotheunit.")
    encode_uom_in_days=fields.Boolean(compute='_compute_encode_uom_in_days')

    def_compute_encode_uom_in_days(self):
        self.encode_uom_in_days=self.env.company.timesheet_encode_uom_id==self.env.ref('uom.product_uom_day')

    @api.depends('analytic_account_id')
    def_compute_allow_timesheets(self):
        without_account=self.filtered(lambdat:nott.analytic_account_idandt._origin)
        without_account.update({'allow_timesheets':False})

    @api.constrains('allow_timesheets','analytic_account_id')
    def_check_allow_timesheet(self):
        forprojectinself:
            ifproject.allow_timesheetsandnotproject.analytic_account_id:
                raiseValidationError(_('Toallowtimesheet,yourproject%sshouldhaveananalyticaccountset.',project.name))

    @api.depends('timesheet_ids')
    def_compute_total_timesheet_time(self):
        forprojectinself:
            total_time=0.0
            fortimesheetinproject.timesheet_ids:
                #Timesheetsmaybestoredinadifferentunitofmeasure,sofirst
                #weconvertallofthemtothereferenceunit
                total_time+=timesheet.unit_amount*timesheet.product_uom_id.factor_inv
            #Nowconverttotheproperunitofmeasuresetinthesettings
            total_time*=project.timesheet_encode_uom_id.factor
            project.total_timesheet_time=int(round(total_time))

    @api.model_create_multi
    defcreate(self,vals_list):
        """Createananalyticaccountifprojectallowtimesheetanddon'tprovideone
            Note:createitbeforecallingsuper()toavoidraisingtheValidationErrorfrom_check_allow_timesheet
        """
        defaults=self.default_get(['allow_timesheets','analytic_account_id'])
        forvaluesinvals_list:
            allow_timesheets=values.get('allow_timesheets',defaults.get('allow_timesheets'))
            analytic_account_id=values.get('analytic_account_id',defaults.get('analytic_account_id'))
            ifallow_timesheetsandnotanalytic_account_id:
                analytic_account=self._create_analytic_account_from_values(values)
                values['analytic_account_id']=analytic_account.id
        returnsuper(Project,self).create(vals_list)

    defwrite(self,values):
        #createtheAAforprojectstillallowingtimesheet
        ifvalues.get('allow_timesheets')andnotvalues.get('analytic_account_id'):
            forprojectinself:
                ifnotproject.analytic_account_id:
                    project._create_analytic_account()
        returnsuper(Project,self).write(values)

    @api.model
    def_init_data_analytic_account(self):
        self.search([('analytic_account_id','=',False),('allow_timesheets','=',True)])._create_analytic_account()

    defunlink(self):
        """
        Ifsomeprojectstounlinkhavesometimesheetsentries,these
        timesheetsentriesmustbeunlinkedfirst.
        Inthiscase,awarningmessageisdisplayedthroughaRedirectWarning
        andallowstheusertoseetimesheetsentriestounlink.
        """
        projects_with_timesheets=self.filtered(lambdap:p.timesheet_ids)
        ifprojects_with_timesheets:
            iflen(projects_with_timesheets)>1:
                warning_msg=_("Theseprojectshavesometimesheetentriesreferencingthem.Beforeremovingtheseprojects,youhavetoremovethesetimesheetentries.")
            else:
                warning_msg=_("Thisprojecthassometimesheetentriesreferencingit.Beforeremovingthisproject,youhavetoremovethesetimesheetentries.")
            raiseRedirectWarning(
                warning_msg,self.env.ref('hr_timesheet.timesheet_action_project').id,
                _('Seetimesheetentries'),{'active_ids':projects_with_timesheets.ids})
        returnsuper(Project,self).unlink()


classTask(models.Model):
    _name="project.task"
    _inherit="project.task"

    analytic_account_active=fields.Boolean("ActiveAnalyticAccount",compute='_compute_analytic_account_active')
    allow_timesheets=fields.Boolean("Allowtimesheets",related='project_id.allow_timesheets',help="Timesheetscanbeloggedonthistask.",readonly=True)
    remaining_hours=fields.Float("RemainingHours",compute='_compute_remaining_hours',store=True,readonly=True,help="Totalremainingtime,canbere-estimatedperiodicallybytheassigneeofthetask.")
    effective_hours=fields.Float("HoursSpent",compute='_compute_effective_hours',compute_sudo=True,store=True,help="Timespentonthistask,excludingitssub-tasks.")
    total_hours_spent=fields.Float("TotalHours",compute='_compute_total_hours_spent',store=True,help="Timespentonthistask,includingitssub-tasks.")
    progress=fields.Float("Progress",compute='_compute_progress_hours',store=True,group_operator="avg",help="Displayprogressofcurrenttask.")
    overtime=fields.Float(compute='_compute_progress_hours',store=True)
    subtask_effective_hours=fields.Float("Sub-tasksHoursSpent",compute='_compute_subtask_effective_hours',store=True,help="Timespentonthesub-tasks(andtheirownsub-tasks)ofthistask.")
    timesheet_ids=fields.One2many('account.analytic.line','task_id','Timesheets')
    encode_uom_in_days=fields.Boolean(compute='_compute_encode_uom_in_days',default=lambdaself:self._uom_in_days())

    def_uom_in_days(self):
        returnself.env.company.timesheet_encode_uom_id==self.env.ref('uom.product_uom_day')

    def_compute_encode_uom_in_days(self):
        self.encode_uom_in_days=self._uom_in_days()

    @api.depends('project_id.analytic_account_id.active')
    def_compute_analytic_account_active(self):
        """Overriddeninsale_timesheet"""
        fortaskinself:
            task.analytic_account_active=task.project_id.analytic_account_id.active

    @api.depends('timesheet_ids.unit_amount')
    def_compute_effective_hours(self):
        ifnotany(self._ids):
            fortaskinself:
                task.effective_hours=sum(task.timesheet_ids.mapped('unit_amount'))
            return
        timesheet_read_group=self.env['account.analytic.line'].read_group([('task_id','in',self.ids)],['unit_amount','task_id'],['task_id'])
        timesheets_per_task={res['task_id'][0]:res['unit_amount']forresintimesheet_read_group}
        fortaskinself:
            task.effective_hours=timesheets_per_task.get(task.id,0.0)

    @api.depends('effective_hours','subtask_effective_hours','planned_hours')
    def_compute_progress_hours(self):
        fortaskinself:
            if(task.planned_hours>0.0):
                task_total_hours=task.effective_hours+task.subtask_effective_hours
                task.overtime=max(task_total_hours-task.planned_hours,0)
                iffloat_compare(task_total_hours,task.planned_hours,precision_digits=2)>=0:
                    task.progress=100
                else:
                    task.progress=round(100.0*task_total_hours/task.planned_hours,2)
            else:
                task.progress=0.0
                task.overtime=0

    @api.depends('effective_hours','subtask_effective_hours','planned_hours')
    def_compute_remaining_hours(self):
        fortaskinself:
            task.remaining_hours=task.planned_hours-task.effective_hours-task.subtask_effective_hours

    @api.depends('effective_hours','subtask_effective_hours')
    def_compute_total_hours_spent(self):
        fortaskinself:
            task.total_hours_spent=task.effective_hours+task.subtask_effective_hours

    @api.depends('child_ids.effective_hours','child_ids.subtask_effective_hours')
    def_compute_subtask_effective_hours(self):
        fortaskinself:
            task.subtask_effective_hours=sum(child_task.effective_hours+child_task.subtask_effective_hoursforchild_taskintask.child_ids)

    defaction_view_subtask_timesheet(self):
        self.ensure_one()
        tasks=self._get_all_subtasks()
        return{
            'type':'ir.actions.act_window',
            'name':_('Timesheets'),
            'res_model':'account.analytic.line',
            'view_mode':'list,form',
            'domain':[('project_id','!=',False),('task_id','in',tasks.ids)],
        }

    def_get_timesheet(self):
        #Isoverrideinsale_timesheet
        returnself.timesheet_ids

    defwrite(self,values):
        #atimesheetmusthaveananalyticaccount(andaproject)
        if'project_id'invaluesandnotvalues.get('project_id')andself._get_timesheet():
            raiseUserError(_('Thistaskmustbepartofaprojectbecausetherearesometimesheetslinkedtoit.'))
        res=super(Task,self).write(values)

        if'project_id'invalues:
            project=self.env['project.project'].browse(values.get('project_id'))
            ifproject.allow_timesheets:
                #Wewriteonallnonyetinvoicedtimesheetthenewproject_id(ifprojectallowtimesheet)
                self._get_timesheet().write({'project_id':values.get('project_id')})

        returnres

    defname_get(self):
        ifself.env.context.get('hr_timesheet_display_remaining_hours'):
            name_mapping=dict(super().name_get())
            fortaskinself:
                iftask.allow_timesheetsandtask.planned_hours>0andtask.encode_uom_in_days:
                    days_left=_("(%sdaysremaining)")%task._convert_hours_to_days(task.remaining_hours)
                    name_mapping[task.id]=name_mapping.get(task.id,'')+"‒"+days_left
                eliftask.allow_timesheetsandtask.planned_hours>0:
                    hours,mins=(str(int(duration)).rjust(2,'0')fordurationindivmod(abs(task.remaining_hours)*60,60))
                    hours_left=_(
                        "(%(sign)s%(hours)s:%(minutes)sremaining)",
                        sign='-'iftask.remaining_hours<0else'',
                        hours=hours,
                        minutes=mins,
                    )
                    name_mapping[task.id]=name_mapping.get(task.id,'')+"‒"+hours_left
            returnlist(name_mapping.items())
        returnsuper().name_get()

    @api.model
    def_fields_view_get(self,view_id=None,view_type='form',toolbar=False,submenu=False):
        """Setthecorrectlabelfor`unit_amount`,dependingoncompanyUoM"""
        result=super(Task,self)._fields_view_get(view_id=view_id,view_type=view_type,toolbar=toolbar,submenu=submenu)
        result['arch']=self.env['account.analytic.line']._apply_timesheet_label(result['arch'])

        ifview_type=='tree'andself.env.company.timesheet_encode_uom_id==self.env.ref('uom.product_uom_day'):
            result['arch']=self._apply_time_label(result['arch'])
        returnresult

    @api.model
    def_apply_time_label(self,view_arch):
        doc=etree.XML(view_arch)
        encoding_uom=self.env.company.timesheet_encode_uom_id
        fornodeindoc.xpath("//field[@widget='timesheet_uom'][not(@string)]|//field[@widget='timesheet_uom_no_toggle'][not(@string)]"):
            name_with_uom=re.sub(_('Hours')+"|Hours",encoding_uom.nameor'',self._fields[node.get('name')]._description_string(self.env),flags=re.IGNORECASE)
            node.set('string',name_with_uom)

        returnetree.tostring(doc,encoding='unicode')

    defunlink(self):
        """
        Ifsometaskstounlinkhavesometimesheetsentries,these
        timesheetsentriesmustbeunlinkedfirst.
        Inthiscase,awarningmessageisdisplayedthroughaRedirectWarning
        andallowstheusertoseetimesheetsentriestounlink.
        """
        tasks_with_timesheets=self.filtered(lambdat:t.timesheet_ids)
        iftasks_with_timesheets:
            iflen(tasks_with_timesheets)>1:
                warning_msg=_("Thesetaskshavesometimesheetentriesreferencingthem.Beforeremovingthesetasks,youhavetoremovethesetimesheetentries.")
            else:
                warning_msg=_("Thistaskhassometimesheetentriesreferencingit.Beforeremovingthistask,youhavetoremovethesetimesheetentries.")
            raiseRedirectWarning(
                warning_msg,self.env.ref('hr_timesheet.timesheet_action_task').id,
                _('Seetimesheetentries'),{'active_ids':tasks_with_timesheets.ids})
        returnsuper(Task,self).unlink()

    def_convert_hours_to_days(self,time):
        uom_hour=self.env.ref('uom.product_uom_hour')
        uom_day=self.env.ref('uom.product_uom_day')
        returnround(uom_hour._compute_quantity(time,uom_day,raise_if_failure=False),2)
