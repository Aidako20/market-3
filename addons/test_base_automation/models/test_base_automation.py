#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdateutilimportrelativedelta
fromflectraimportfields,models,api


classLeadTest(models.Model):
    _name="base.automation.lead.test"
    _description="AutomatedRuleTest"

    name=fields.Char(string='Subject',required=True,index=True)
    user_id=fields.Many2one('res.users',string='Responsible')
    state=fields.Selection([('draft','New'),('cancel','Cancelled'),('open','InProgress'),
                              ('pending','Pending'),('done','Closed')],
                             string="Status",readonly=True,default='draft')
    active=fields.Boolean(default=True)
    partner_id=fields.Many2one('res.partner',string='Partner')
    date_action_last=fields.Datetime(string='LastAction',readonly=True)
    employee=fields.Boolean(compute='_compute_employee_deadline',store=True)
    line_ids=fields.One2many('base.automation.line.test','lead_id')

    priority=fields.Boolean()
    deadline=fields.Boolean(compute='_compute_employee_deadline',store=True)
    is_assigned_to_admin=fields.Boolean(string='Assignedtoadminuser')

    @api.depends('partner_id.employee','priority')
    def_compute_employee_deadline(self):
        #thismethodcomputestwofieldsonpurpose;don'tsplitit
        forrecordinself:
            record.employee=record.partner_id.employee
            ifnotrecord.priority:
                record.deadline=False
            else:
                record.deadline=record.create_date+relativedelta.relativedelta(days=3)

    defwrite(self,vals):
        result=super().write(vals)
        #forcerecomputationoffield'deadline'via'employee':theaction
        #basedon'deadline'mustbetriggered
        self.mapped('employee')
        returnresult


classLineTest(models.Model):
    _name="base.automation.line.test"
    _description="AutomatedRuleLineTest"

    name=fields.Char()
    lead_id=fields.Many2one('base.automation.lead.test',ondelete='cascade')
    user_id=fields.Many2one('res.users')


classModelWithAccess(models.Model):
    _name="base.automation.link.test"
    _description="AutomatedRuleLinkTest"

    name=fields.Char()
    linked_id=fields.Many2one('base.automation.linked.test',ondelete='cascade')


classModelWithoutAccess(models.Model):
    _name="base.automation.linked.test"
    _description="AutomatedRuleLinkedTest"

    name=fields.Char()
    another_field=fields.Char()


classProject(models.Model):
    _name=_description='test_base_automation.project'

    name=fields.Char()
    task_ids=fields.One2many('test_base_automation.task','project_id')


classTask(models.Model):
    _name=_description='test_base_automation.task'

    name=fields.Char()
    parent_id=fields.Many2one('test_base_automation.task')
    project_id=fields.Many2one(
        'test_base_automation.project',
        compute='_compute_project_id',recursive=True,store=True,readonly=False,
    )

    @api.depends('parent_id.project_id')
    def_compute_project_id(self):
        fortaskinself:
            ifnottask.project_id:
                task.project_id=task.parent_id.project_id
