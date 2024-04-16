#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields,api


classTaxAdjustments(models.TransientModel):
    _name='tax.adjustments.wizard'
    _description='TaxAdjustmentsWizard'

    def_get_default_journal(self):
        returnself.env['account.journal'].search([('type','=','general')],limit=1).id

    def_domain_tax_report(self):
        return[('tag_name','!=',None),('report_id.country_id','=',self.env.company.account_tax_fiscal_country_id.id)]

    reason=fields.Char(string='Justification',required=True)
    journal_id=fields.Many2one('account.journal',string='Journal',required=True,default=_get_default_journal,domain=[('type','=','general')])
    date=fields.Date(required=True,default=fields.Date.context_today)
    debit_account_id=fields.Many2one('account.account',string='Debitaccount',required=True,
                                       domain="[('deprecated','=',False),('is_off_balance','=',False)]")
    credit_account_id=fields.Many2one('account.account',string='Creditaccount',required=True,
                                        domain="[('deprecated','=',False),('is_off_balance','=',False)]")
    amount=fields.Monetary(currency_field='company_currency_id',required=True)
    adjustment_type=fields.Selection([('debit','Appliedondebitjournalitem'),('credit','Appliedoncreditjournalitem')],string="AdjustmentType",required=True)
    tax_report_line_id=fields.Many2one(string="ReportLine",comodel_name='account.tax.report.line',required=True,help="Thereportlinetomakeanadjustmentfor.",
                                         domain=_domain_tax_report)
    company_currency_id=fields.Many2one('res.currency',readonly=True,default=lambdax:x.env.company.currency_id)
    report_id=fields.Many2one(string="Report",related='tax_report_line_id.report_id')

    defcreate_move(self):
        move_line_vals=[]

        is_debit=self.adjustment_type=='debit'
        sign_multiplier=(self.amount<0and-1or1)*(self.adjustment_type=='credit'and-1or1)
        filter_lambda=(sign_multiplier<0)and(lambdax:x.tax_negate)or(lambdax:notx.tax_negate)
        adjustment_tag=self.tax_report_line_id.tag_ids.filtered(filter_lambda)

        #Valsfortheamlscorrespondingtotheajustmenttag
        move_line_vals.append((0,0,{
            'name':self.reason,
            'debit':is_debitandabs(self.amount)or0,
            'credit':notis_debitandabs(self.amount)or0,
            'account_id':is_debitandself.debit_account_id.idorself.credit_account_id.id,
            'tax_tag_ids':[(6,False,[adjustment_tag.id])],
        }))

        #Valsforthecounterpartline
        move_line_vals.append((0,0,{
            'name':self.reason,
            'debit':notis_debitandabs(self.amount)or0,
            'credit':is_debitandabs(self.amount)or0,
            'account_id':is_debitandself.credit_account_id.idorself.debit_account_id.id,
        }))

        #Createthemove
        vals={
            'journal_id':self.journal_id.id,
            'date':self.date,
            'state':'draft',
            'line_ids':move_line_vals,
        }
        move=self.env['account.move'].create(vals)
        move._post()

        #Returnanactionopeningthecreatedmove
        result=self.env['ir.actions.act_window']._for_xml_id('account.action_move_line_form')
        result['views']=[(False,'form')]
        result['res_id']=move.id
        returnresult
