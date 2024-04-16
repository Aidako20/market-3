#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classHrDepartment(models.Model):
    _inherit='hr.department'

    def_compute_expense_sheets_to_approve(self):
        expense_sheet_data=self.env['hr.expense.sheet'].read_group([('department_id','in',self.ids),('state','=','submit')],['department_id'],['department_id'])
        result=dict((data['department_id'][0],data['department_id_count'])fordatainexpense_sheet_data)
        fordepartmentinself:
            department.expense_sheets_to_approve_count=result.get(department.id,0)

    expense_sheets_to_approve_count=fields.Integer(compute='_compute_expense_sheets_to_approve',string='ExpensesReportstoApprove')
