#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError


classGamificationBadgeUser(models.Model):
    """Userhavingreceivedabadge"""
    _inherit='gamification.badge.user'

    employee_id=fields.Many2one('hr.employee',string='Employee')

    @api.constrains('employee_id')
    def_check_employee_related_user(self):
        forbadge_userinself:
            ifbadge_user.employee_idnotinbadge_user.user_id.employee_ids:
                raiseValidationError(_('Theselectedemployeedoesnotcorrespondtotheselecteduser.'))


classGamificationBadge(models.Model):
    _inherit='gamification.badge'

    granted_employees_count=fields.Integer(compute="_compute_granted_employees_count")

    @api.depends('owner_ids.employee_id')
    def_compute_granted_employees_count(self):
        forbadgeinself:
            badge.granted_employees_count=self.env['gamification.badge.user'].search_count([
                ('badge_id','=',badge.id),
                ('employee_id','!=',False)
            ])

    defget_granted_employees(self):
        employee_ids=self.mapped('owner_ids.employee_id').ids
        return{
            'type':'ir.actions.act_window',
            'name':'GrantedEmployees',
            'view_mode':'kanban,tree,form',
            'res_model':'hr.employee.public',
            'domain':[('id','in',employee_ids)]
        }
