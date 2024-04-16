#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    module_stock_dropshipping=fields.Boolean("Dropshipping")
    days_to_purchase=fields.Float(
        related='company_id.days_to_purchase',readonly=False)

    is_installed_sale=fields.Boolean(string="IstheSaleModuleInstalled")

    defget_values(self):
        res=super(ResConfigSettings,self).get_values()
        res.update(
            is_installed_sale=self.env['ir.module.module'].search([('name','=','sale'),('state','=','installed')]).id,
        )
        returnres
