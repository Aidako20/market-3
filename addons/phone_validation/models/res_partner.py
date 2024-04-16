#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models


classPartner(models.Model):
    _name='res.partner'
    _inherit=['res.partner','phone.validation.mixin']

    @api.onchange('phone','country_id','company_id')
    def_onchange_phone_validation(self):
        ifself.phone:
            self.phone=self.phone_format(self.phone)

    @api.onchange('mobile','country_id','company_id')
    def_onchange_mobile_validation(self):
        ifself.mobile:
            self.mobile=self.phone_format(self.mobile)
