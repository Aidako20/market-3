#-*-coding:utf-8-*-

fromflectraimportapi,fields,models,_


classAccountChartTemplate(models.Model):
    _inherit='account.chart.template'

    def_create_bank_journals(self,company,acc_template_ref):
        res=super(AccountChartTemplate,self)._create_bank_journals(company,acc_template_ref)

        #Trytogeneratethemissingjournals
        returnres+self.env['payment.acquirer']._create_missing_journal_for_acquirers(company=company)
