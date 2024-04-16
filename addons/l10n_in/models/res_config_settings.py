#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    group_l10n_in_reseller=fields.Boolean(implied_group='l10n_in.group_l10n_in_reseller',string="ManageReseller(E-Commerce)")
