#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    group_expiry_date_on_delivery_slip=fields.Boolean("DisplayExpirationDatesonDeliverySlips",
        implied_group='product_expiry.group_expiry_date_on_delivery_slip')

    @api.onchange('group_lot_on_delivery_slip')
    def_onchange_group_lot_on_delivery_slip(self):
        ifnotself.group_lot_on_delivery_slip:
            self.group_expiry_date_on_delivery_slip=False

    @api.onchange('module_product_expiry')
    def_onchange_module_product_expiry(self):
        ifnotself.module_product_expiry:
            self.group_expiry_date_on_delivery_slip=False
