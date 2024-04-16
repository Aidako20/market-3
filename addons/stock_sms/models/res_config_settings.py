#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    stock_move_sms_validation=fields.Boolean(
        related='company_id.stock_move_sms_validation',
        string='SMSValidationwithstockmove',readonly=False)
    stock_sms_confirmation_template_id=fields.Many2one(
        related='company_id.stock_sms_confirmation_template_id',readonly=False)
