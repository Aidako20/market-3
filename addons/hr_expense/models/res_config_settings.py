#-*-coding:utf-8-*-

fromflectraimportapi,fields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    expense_alias_prefix=fields.Char('DefaultAliasNameforExpenses',compute='_compute_expense_alias_prefix',
        store=True,readonly=False)
    use_mailgateway=fields.Boolean(string='Letyouremployeesrecordexpensesbyemail',
                                     config_parameter='hr_expense.use_mailgateway')

    module_hr_payroll_expense=fields.Boolean(string='ReimburseExpensesinPayslip')
    module_hr_expense_extract=fields.Boolean(string='SendbillstoOCRtogenerateexpenses')


    @api.model
    defget_values(self):
        res=super(ResConfigSettings,self).get_values()
        res.update(
            expense_alias_prefix=self.env.ref('hr_expense.mail_alias_expense').alias_name,
        )
        returnres

    defset_values(self):
        super(ResConfigSettings,self).set_values()
        self.env.ref('hr_expense.mail_alias_expense').write({'alias_name':self.expense_alias_prefix})

    @api.depends('use_mailgateway')
    def_compute_expense_alias_prefix(self):
        self.filtered(lambdaw:notw.use_mailgateway).update({'expense_alias_prefix':False})
