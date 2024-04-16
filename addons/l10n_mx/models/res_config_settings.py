#-*-coding:utf-8-*-

fromflectraimportfields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    module_l10n_mx_edi=fields.Boolean('MexicanElectronicInvoicing')
