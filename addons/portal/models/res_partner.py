#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classResPartner(models.Model):
    _inherit='res.partner'

    defcan_edit_vat(self):
        '''`vat`isacommercialfield,syncedbetweentheparent(commercial
        entity)andthechildren.Onlythecommercialentityshouldbeableto
        editit(asinbackend).'''
        returnnotself.parent_id
