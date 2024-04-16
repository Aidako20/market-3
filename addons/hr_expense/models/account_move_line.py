#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classAccountMoveLine(models.Model):
    _inherit="account.move.line"

    expense_id=fields.Many2one('hr.expense',string='Expense',copy=False,help="Expensewherethemovelinecomefrom")

    defreconcile(self):
        #OVERRIDE
        not_paid_expenses=self.expense_id.filtered(lambdaexpense:expense.state!='done')
        not_paid_expense_sheets=not_paid_expenses.sheet_id
        res=super().reconcile()
        paid_expenses=not_paid_expenses.filtered(lambdaexpense:expense.currency_id.is_zero(expense.amount_residual))
        paid_expenses.write({'state':'done'})
        not_paid_expense_sheets.filtered(lambdasheet:all(expense.state=='done'forexpenseinsheet.expense_line_ids)).set_to_paid()
        returnres

    def_get_attachment_domains(self):
        attachment_domains=super(AccountMoveLine,self)._get_attachment_domains()
        ifself.expense_id:
            attachment_domains.append([('res_model','=','hr.expense'),('res_id','=',self.expense_id.id)])
        returnattachment_domains
