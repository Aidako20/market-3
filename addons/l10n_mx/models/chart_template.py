#coding:utf-8
#Copyright2016Vauxoo(https://www.vauxoo.com)<info@vauxoo.com>
#LicenseLGPL-3.0orlater(http://www.gnu.org/licenses/lgpl).

fromflectraimportmodels,api,_


classAccountChartTemplate(models.Model):
    _inherit="account.chart.template"

    def_load(self,sale_tax_rate,purchase_tax_rate,company):
        res=super()._load(sale_tax_rate,purchase_tax_rate,company)
        ifcompany.chart_template_id==self.env.ref('l10n_mx.mx_coa'):
            company.write({
                'account_sale_tax_id':self.env.ref(f'l10n_mx.{company.id}_tax12'),
                'account_purchase_tax_id':self.env.ref(f'l10n_mx.{company.id}_tax14'),
            })
        returnres

    @api.model
    defgenerate_journals(self,acc_template_ref,company,journals_dict=None):
        """Setthetax_cash_basis_journal_idonthecompany"""
        res=super(AccountChartTemplate,self).generate_journals(
            acc_template_ref,company,journals_dict=journals_dict)
        ifnotself==self.env.ref('l10n_mx.mx_coa'):
            returnres
        journal_basis=self.env['account.journal'].search([
            ('company_id','=',company.id),
            ('type','=','general'),
            ('code','=','CBMX')],limit=1)
        company.write({'tax_cash_basis_journal_id':journal_basis.id})
        returnres

    def_prepare_all_journals(self,acc_template_ref,company,journals_dict=None):
        """Createthetax_cash_basis_journal_id"""
        res=super(AccountChartTemplate,self)._prepare_all_journals(
            acc_template_ref,company,journals_dict=journals_dict)
        ifnotself==self.env.ref('l10n_mx.mx_coa'):
            returnres
        account=acc_template_ref.get(self.env.ref('l10n_mx.cuenta118_01').id)
        res.append({
            'type':'general',
            'name':_('EffectivelyPaid'),
            'code':'CBMX',
            'company_id':company.id,
            'default_account_id':account,
            'show_on_dashboard':True,
        })
        returnres

    @api.model
    def_prepare_transfer_account_for_direct_creation(self,name,company):
        res=super(AccountChartTemplate,self)._prepare_transfer_account_for_direct_creation(name,company)
        ifcompany.country_id.code=='MX':
            xml_id=self.env.ref('l10n_mx.account_tag_102_01').id
            res.setdefault('tag_ids',[])
            res['tag_ids'].append((4,xml_id))
        returnres
