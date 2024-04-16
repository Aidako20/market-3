#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classAccountInvoiceReport(models.Model):
    _inherit='account.invoice.report'

    team_id=fields.Many2one('crm.team',string='SalesTeam')

    def_select(self):
        returnsuper(AccountInvoiceReport,self)._select()+",move.team_idasteam_id"
