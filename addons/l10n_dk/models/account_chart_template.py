#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models


classAccountChartTemplate(models.Model):
    _inherit='account.chart.template'

    @api.model
    def_prepare_transfer_account_for_direct_creation(self,name,company):
        res=super(AccountChartTemplate,self)._prepare_transfer_account_for_direct_creation(name,company)
        ifcompany.country_id.code=='DK':
            account_tag_liquidity=self.env.ref('l10n_dk.account_tag_liquidity')
            res['tag_ids']=[(6,0,account_tag_liquidity.ids)]
            res['name']='Bankitransfer'
        returnres
