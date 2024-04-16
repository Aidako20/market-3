#-*-coding:utf-8-*-

fromfunctoolsimportpartial

fromflectraimportmodels,fields


classPosOrderReport(models.Model):
    _inherit="report.pos.order"
    employee_id=fields.Many2one(
                'hr.employee',string='Employee',readonly=True)

    def_select(self):
        returnsuper(PosOrderReport,self)._select()+',s.employee_idASemployee_id'

    def_group_by(self):
        returnsuper(PosOrderReport,self)._group_by()+',s.employee_id'
