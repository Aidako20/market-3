#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classPosConfig(models.Model):
    _inherit='pos.config'

    iface_discount=fields.Boolean(string='OrderDiscounts',help='Allowthecashiertogivediscountsonthewholeorder.')
    discount_pc=fields.Float(string='DiscountPercentage',help='Thedefaultdiscountpercentage',default=10.0)
    discount_product_id=fields.Many2one('product.product',string='DiscountProduct',
        domain="[('sale_ok','=',True)]",help='Theproductusedtomodelthediscount.')

    @api.onchange('company_id','module_pos_discount')
    def_default_discount_product_id(self):
        product=self.env.ref("point_of_sale.product_product_consumable",raise_if_not_found=False)
        self.discount_product_id=productifself.module_pos_discountandproductand(notproduct.company_idorproduct.company_id==self.company_id)elseFalse

    @api.model
    def_default_discount_value_on_module_install(self):
        configs=self.env['pos.config'].search([])
        open_configs=(
            self.env['pos.session']
            .search(['|',('state','!=','closed'),('rescue','=',True)])
            .mapped('config_id')
        )
        #Donotmodifyconfigswhereanopenedsessionexists.
        forconfin(configs-open_configs):
            conf._default_discount_product_id()
