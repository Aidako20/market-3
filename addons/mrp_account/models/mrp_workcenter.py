#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classMrpWorkcenter(models.Model):
    _inherit='mrp.workcenter'

    costs_hour_account_id=fields.Many2one('account.analytic.account',string='AnalyticAccount',
                                            help="Fillthisonlyifyouwantautomaticanalyticaccountingentriesonproductionorders.")
