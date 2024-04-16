#-*-coding:utf-8-*-

fromflectraimportapi,fields,models


classAccountCommonJournalReport(models.TransientModel):
    _name='account.common.journal.report'
    _description='CommonJournalReport'
    _inherit="account.common.report"

    amount_currency=fields.Boolean('WithCurrency',help="PrintReportwiththecurrencycolumnifthecurrencydiffersfromthecompanycurrency.")

    defpre_print_report(self,data):
        data['form'].update({'amount_currency':self.amount_currency})
        returndata
