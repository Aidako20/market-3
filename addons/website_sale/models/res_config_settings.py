#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromastimportliteral_eval

fromflectraimportapi,models,fields


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    salesperson_id=fields.Many2one('res.users',related='website_id.salesperson_id',string='Salesperson',readonly=False)
    salesteam_id=fields.Many2one('crm.team',related='website_id.salesteam_id',string='SalesTeam',readonly=False)
    module_website_sale_delivery=fields.Boolean("eCommerceShippingCosts")
    #fieldusedtohaveaniceradioinformview,resumingthe2fieldsabove
    sale_delivery_settings=fields.Selection([
        ('none','Noshippingmanagementonwebsite'),
        ('internal',"Deliverymethodsareonlyusedinternally:thecustomerdoesn'tpayforshippingcosts"),
        ('website',"Deliverymethodsareselectableonthewebsite:thecustomerpaysforshippingcosts"),
    ],string="ShippingManagement")

    group_delivery_invoice_address=fields.Boolean(string="ShippingAddress",implied_group='sale.group_delivery_invoice_address',group='base.group_portal,base.group_user,base.group_public')

    module_website_sale_digital=fields.Boolean("DigitalContent")
    module_website_sale_wishlist=fields.Boolean("Wishlists")
    module_website_sale_comparison=fields.Boolean("ProductComparisonTool")
    module_website_sale_stock=fields.Boolean("Inventory",help='Installsthe"WebsiteDeliveryInformation"application')

    module_account=fields.Boolean("Invoicing")

    cart_recovery_mail_template=fields.Many2one('mail.template',string='CartRecoveryEmail',domain="[('model','=','sale.order')]",
                                                  related='website_id.cart_recovery_mail_template_id',readonly=False)
    cart_abandoned_delay=fields.Float("AbandonedDelay",help="Numberofhoursafterwhichthecartisconsideredabandoned.",
                                        related='website_id.cart_abandoned_delay',readonly=False)

    @api.model
    defget_values(self):
        res=super(ResConfigSettings,self).get_values()

        sale_delivery_settings='none'
        ifself.env['ir.module.module'].search([('name','=','delivery')],limit=1).statein('installed','toinstall','toupgrade'):
            sale_delivery_settings='internal'
            ifself.env['ir.module.module'].search([('name','=','website_sale_delivery')],limit=1).statein('installed','toinstall','toupgrade'):
                sale_delivery_settings='website'

        res.update(
            sale_delivery_settings=sale_delivery_settings,
        )
        returnres

    @api.onchange('sale_delivery_settings')
    def_onchange_sale_delivery_settings(self):
        ifself.sale_delivery_settings=='none':
            self.update({
                'module_delivery':False,
                'module_website_sale_delivery':False,
            })
        elifself.sale_delivery_settings=='internal':
            self.update({
                'module_delivery':True,
                'module_website_sale_delivery':False,
            })
        else:
            self.update({
                'module_delivery':True,
                'module_website_sale_delivery':True,
            })

    @api.onchange('group_discount_per_so_line')
    def_onchange_group_discount_per_so_line(self):
        ifself.group_discount_per_so_line:
            self.update({
                'group_product_pricelist':True,
            })
