#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classHrExpenseRefuseWizard(models.TransientModel):
    """Thiswizardcanbelaunchedfromanhe.expense(anexpenseline)
    orfromanhr.expense.sheet(Enexpensereport)
    'hr_expense_refuse_model'mustbepassedinthecontexttodifferentiate
    therightmodeltouse.
    """

    _name="hr.expense.refuse.wizard"
    _description="ExpenseRefuseReasonWizard"

    reason=fields.Char(string='Reason',required=True)
    hr_expense_ids=fields.Many2many('hr.expense')
    hr_expense_sheet_id=fields.Many2one('hr.expense.sheet')

    @api.model
    defdefault_get(self,fields):
        res=super(HrExpenseRefuseWizard,self).default_get(fields)
        active_ids=self.env.context.get('active_ids',[])
        refuse_model=self.env.context.get('hr_expense_refuse_model')
        ifrefuse_model=='hr.expense':
            res.update({
                'hr_expense_ids':active_ids,
                'hr_expense_sheet_id':False,
            })
        elifrefuse_model=='hr.expense.sheet':
            res.update({
                'hr_expense_sheet_id':active_ids[0]ifactive_idselseFalse,
                'hr_expense_ids':[],
            })
        returnres

    defexpense_refuse_reason(self):
        self.ensure_one()
        ifself.hr_expense_ids:
            self.hr_expense_ids.refuse_expense(self.reason)
        ifself.hr_expense_sheet_id:
            self.hr_expense_sheet_id.refuse_sheet(self.reason)

        return{'type':'ir.actions.act_window_close'}
