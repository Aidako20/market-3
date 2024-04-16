#-*-coding:utf-8-*-

fromflectraimportapi,fields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    sale_tax_id=fields.Many2one('account.tax',string="DefaultSaleTax",related='company_id.account_sale_tax_id',readonly=False)
    module_pos_mercury=fields.Boolean(string="VantivPaymentTerminal",help="ThetransactionsareprocessedbyVantiv.SetyourVantivcredentialsontherelatedpaymentmethod.")
    module_pos_adyen=fields.Boolean(string="AdyenPaymentTerminal",help="ThetransactionsareprocessedbyAdyen.SetyourAdyencredentialsontherelatedpaymentmethod.")
    module_pos_six=fields.Boolean(string="SixPaymentTerminal",help="ThetransactionsareprocessedbySix.SettheIPaddressoftheterminalontherelatedpaymentmethod.")
    update_stock_quantities=fields.Selection(related="company_id.point_of_sale_update_stock_quantities",readonly=False)

    defset_values(self):
        super(ResConfigSettings,self).set_values()
        ifnotself.group_product_pricelist:
            configs=self.env['pos.config'].search([('use_pricelist','=',True)])
            forconfiginconfigs:
                config.use_pricelist=False
