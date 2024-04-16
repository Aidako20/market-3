#-*-coding:utf-8-*-
fromflectraimportfields,models


classResPartner(models.Model):
    _inherit='res.partner'

    iap_enrich_info=fields.Text('IAPEnrichInfo',help='StoresadditionalinforetrievedfromIAPinJSON')
