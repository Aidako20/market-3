#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classHrEmployeeBase(models.AbstractModel):
    _inherit="hr.employee.base"

    goal_ids=fields.One2many('gamification.goal',string='EmployeeHRGoals',compute='_compute_employee_goals')
    badge_ids=fields.One2many(
        'gamification.badge.user',string='EmployeeBadges',compute='_compute_employee_badges',
        help="Allemployeebadges,linkedtotheemployeeeitherdirectlyorthroughtheuser"
    )
    has_badges=fields.Boolean(compute='_compute_employee_badges')
    #necessaryforcorrectdependenciesofbadge_idsandhas_badges
    direct_badge_ids=fields.One2many(
        'gamification.badge.user','employee_id',
        help="Badgesdirectlylinkedtotheemployee")

    @api.depends('user_id.goal_ids.challenge_id.challenge_category')
    def_compute_employee_goals(self):
        foremployeeinself:
            employee.goal_ids=self.env['gamification.goal'].search([
                ('user_id','=',employee.user_id.id),
                ('challenge_id.challenge_category','=','hr'),
            ])

    @api.depends('direct_badge_ids','user_id.badge_ids.employee_id')
    def_compute_employee_badges(self):
        foremployeeinself:
            badge_ids=self.env['gamification.badge.user'].search([
                '|',('employee_id','=',employee.id),
                     '&',('employee_id','=',False),
                          ('user_id','=',employee.user_id.id)
            ])
            employee.has_badges=bool(badge_ids)
            employee.badge_ids=badge_ids
