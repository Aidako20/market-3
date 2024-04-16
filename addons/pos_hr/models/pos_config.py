#-*-coding:utf-8-*-

fromfunctoolsimportpartial

fromflectraimportmodels,fields


classPosConfig(models.Model):
    _inherit='pos.config'

    employee_ids=fields.Many2many(
        'hr.employee',string="Employeeswithaccess",
        help='Ifleftempty,allemployeescanlogintothePoSsession')
