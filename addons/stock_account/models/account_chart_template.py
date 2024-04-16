#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models,_

importlogging
_logger=logging.getLogger(__name__)


classAccountChartTemplate(models.Model):
    _inherit="account.chart.template"

    @api.model
    defgenerate_journals(self,acc_template_ref,company,journals_dict=None):
        journal_to_add=[{'name':_('InventoryValuation'),'type':'general','code':'STJ','favorite':False,'sequence':8}]
        returnsuper(AccountChartTemplate,self).generate_journals(acc_template_ref=acc_template_ref,company=company,journals_dict=journal_to_add)

    defgenerate_properties(self,acc_template_ref,company,property_list=None):
        res=super(AccountChartTemplate,self).generate_properties(acc_template_ref=acc_template_ref,company=company)
        PropertyObj=self.env['ir.property'] #PropertyStockJournal
        value=self.env['account.journal'].search([('company_id','=',company.id),('code','=','STJ'),('type','=','general')],limit=1)
        ifvalue:
            PropertyObj._set_default("property_stock_journal","product.category",value,company)

        todo_list=[ #PropertyStockAccounts
            'property_stock_account_input_categ_id',
            'property_stock_account_output_categ_id',
            'property_stock_valuation_account_id',
        ]
        categ_values={category.id:Falseforcategoryinself.env['product.category'].search([])}
        forfieldintodo_list:
            account=self[field]
            value=acc_template_ref[account.id]ifaccountelseFalse
            PropertyObj._set_default(field,"product.category",value,company)
            PropertyObj._set_multi(field,"product.category",categ_values,True)

        returnres
