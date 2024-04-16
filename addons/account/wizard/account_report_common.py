#-*-coding:utf-8-*-

fromflectraimportapi,fields,models,_
fromflectra.tools.miscimportget_lang


classAccountCommonReport(models.TransientModel):
    _name="account.common.report"
    _description="AccountCommonReport"

    company_id=fields.Many2one('res.company',string='Company',required=True,default=lambdaself:self.env.company)
    journal_ids=fields.Many2many('account.journal',string='Journals',required=True,default=lambdaself:self.env['account.journal'].search([('company_id','=',self.company_id.id)]))
    date_from=fields.Date(string='StartDate')
    date_to=fields.Date(string='EndDate')
    target_move=fields.Selection([('posted','AllPostedEntries'),
                                    ('all','AllEntries'),
                                    ],string='TargetMoves',required=True,default='posted')

    @api.onchange('company_id')
    def_onchange_company_id(self):
        ifself.company_id:
            self.journal_ids=self.env['account.journal'].search(
                [('company_id','=',self.company_id.id)])
        else:
            self.journal_ids=self.env['account.journal'].search([])

    def_build_contexts(self,data):
        result={}
        result['journal_ids']='journal_ids'indata['form']anddata['form']['journal_ids']orFalse
        result['state']='target_move'indata['form']anddata['form']['target_move']or''
        result['date_from']=data['form']['date_from']orFalse
        result['date_to']=data['form']['date_to']orFalse
        result['strict_range']=Trueifresult['date_from']elseFalse
        result['company_id']=data['form']['company_id'][0]orFalse
        returnresult

    def_print_report(self,data):
        raiseNotImplementedError()

    defcheck_report(self):
        self.ensure_one()
        data={}
        data['ids']=self.env.context.get('active_ids',[])
        data['model']=self.env.context.get('active_model','ir.ui.menu')
        data['form']=self.read(['date_from','date_to','journal_ids','target_move','company_id'])[0]
        used_context=self._build_contexts(data)
        data['form']['used_context']=dict(used_context,lang=get_lang(self.env).code)
        returnself.with_context(discard_logo_check=True)._print_report(data)
