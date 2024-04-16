#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError


classHrPlanActivityType(models.Model):
    _name='hr.plan.activity.type'
    _description='Planactivitytype'
    _rec_name='summary'

    activity_type_id=fields.Many2one(
        'mail.activity.type','ActivityType',
        default=lambdaself:self.env.ref('mail.mail_activity_data_todo'),
        domain=lambdaself:['|',('res_model_id','=',False),('res_model_id','=',self.env['ir.model']._get('hr.employee').id)],
        ondelete='restrict'
    )
    summary=fields.Char('Summary',compute="_compute_default_summary",store=True,readonly=False)
    responsible=fields.Selection([
        ('coach','Coach'),
        ('manager','Manager'),
        ('employee','Employee'),
        ('other','Other')],default='employee',string='Responsible',required=True)
    responsible_id=fields.Many2one('res.users','ResponsiblePerson',help='Specificresponsibleofactivityifnotlinkedtotheemployee.')
    note=fields.Html('Note')

    @api.depends('activity_type_id')
    def_compute_default_summary(self):
        forplan_typeinself:
            ifnotplan_type.summaryandplan_type.activity_type_idandplan_type.activity_type_id.summary:
                plan_type.summary=plan_type.activity_type_id.summary

    defget_responsible_id(self,employee):
        ifself.responsible=='coach':
            ifnotemployee.coach_id:
                raiseUserError(_('Coachofemployee%sisnotset.',employee.name))
            responsible=employee.coach_id.user_id
            ifnotresponsible:
                raiseUserError(_('Userofcoachofemployee%sisnotset.',employee.name))
        elifself.responsible=='manager':
            ifnotemployee.parent_id:
                raiseUserError(_('Managerofemployee%sisnotset.',employee.name))
            responsible=employee.parent_id.user_id
            ifnotresponsible:
                raiseUserError(_('Userofmanagerofemployee%sisnotset.',employee.name))
        elifself.responsible=='employee':
            responsible=employee.user_id
            ifnotresponsible:
                raiseUserError(_('Userlinkedtoemployee%sisrequired.',employee.name))
        elifself.responsible=='other':
            responsible=self.responsible_id
            ifnotresponsible:
                raiseUserError(_('Nospecificusergivenonactivity%s.',self.activity_type_id.name))
        returnresponsible


classHrPlan(models.Model):
    _name='hr.plan'
    _description='plan'

    name=fields.Char('Name',required=True)
    plan_activity_type_ids=fields.Many2many('hr.plan.activity.type',string='Activities')
    active=fields.Boolean(default=True)
