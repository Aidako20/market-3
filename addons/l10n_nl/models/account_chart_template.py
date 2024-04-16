#-*-coding:utf-8-*-

fromflectraimportapi,fields,models,_


classAccountChartTemplate(models.Model):
    _inherit='account.chart.template'

    def_load(self,sale_tax_rate,purchase_tax_rate,company):
        #Addtagto999999account
        res=super(AccountChartTemplate,self)._load(sale_tax_rate,purchase_tax_rate,company)
        ifcompany.country_id.code=='NL':
            account=self.env['account.account'].search([('code','=','999999'),('company_id','=',self.env.company.id)])
            ifaccount:
                account.tag_ids=[(4,self.env.ref('l10n_nl.account_tag_12').id)]
        returnres

    @api.model
    def_prepare_transfer_account_for_direct_creation(self,name,company):
        res=super(AccountChartTemplate,self)._prepare_transfer_account_for_direct_creation(name,company)
        ifcompany.country_id.code=='NL':
            xml_id=self.env.ref('l10n_nl.account_tag_25').id
            res.setdefault('tag_ids',[])
            res['tag_ids'].append((4,xml_id))
        returnres
