#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportfields,models


classResCompany(models.Model):
    _inherit='res.company'

    account_edi_proxy_client_ids=fields.One2many('account_edi_proxy_client.user',inverse_name='company_id')
