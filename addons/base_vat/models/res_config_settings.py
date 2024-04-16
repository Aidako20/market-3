#-*-coding:utf-8-*-

fromflectraimportfields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    vat_check_vies=fields.Boolean(related='company_id.vat_check_vies',readonly=False,
        string='VerifyVATNumbers')
