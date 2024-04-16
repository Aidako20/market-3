#-*-coding:utf-8-*-
fromflectraimportapi,models


classAccountChartTemplate(models.Model):
    _inherit='account.chart.template'

    def_load(self,sale_tax_rate,purchase_tax_rate,company):
        """Removethepaymentmethodsthatarecreatedforthecompanybeforeinstallingthechartofaccounts.

        Keepingtheseexistingpos.payment.methodrecordsinterfereswiththeinstallationofchartofaccounts
        becausepos.payment.methodmodelhasfieldslinkedtoaccount.journalandaccount.accountrecordsthatare
        deletedduringtheloadingofchartofaccounts.
        """
        self.env['pos.payment.method'].search([('company_id','=',company.id)]).unlink()
        result=super(AccountChartTemplate,self)._load(sale_tax_rate,purchase_tax_rate,company)
        self.env['pos.config'].post_install_pos_localisation(companies=company)
        returnresult
