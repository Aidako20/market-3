#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromrandomimportrandint

fromflectraimportfields,models


classEmployeeCategory(models.Model):

    _name="hr.employee.category"
    _description="EmployeeCategory"

    def_get_default_color(self):
        returnrandint(1,11)

    name=fields.Char(string="TagName",required=True)
    color=fields.Integer(string='ColorIndex',default=_get_default_color)
    employee_ids=fields.Many2many('hr.employee','employee_category_rel','category_id','emp_id',string='Employees')

    _sql_constraints=[
        ('name_uniq','unique(name)',"Tagnamealreadyexists!"),
    ]
