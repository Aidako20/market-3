#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    group_discount_per_so_line=fields.Boolean("Discounts",implied_group='product.group_discount_per_so_line')
    group_uom=fields.Boolean("UnitsofMeasure",implied_group='uom.group_uom')
    group_product_variant=fields.Boolean("Variants",implied_group='product.group_product_variant')
    module_sale_product_configurator=fields.Boolean("ProductConfigurator")
    module_sale_product_matrix=fields.Boolean("SalesGridEntry")
    group_stock_packaging=fields.Boolean('ProductPackagings',
        implied_group='product.group_stock_packaging')
    group_product_pricelist=fields.Boolean("Pricelists",
        implied_group='product.group_product_pricelist')
    group_sale_pricelist=fields.Boolean("AdvancedPricelists",
        implied_group='product.group_sale_pricelist',
        help="""Allowstomanagedifferentpricesbasedonrulespercategoryofcustomers.
                Example:10%forretailers,promotionof5EURonthisproduct,etc.""")
    product_pricelist_setting=fields.Selection([
            ('basic','Multiplepricesperproduct'),
            ('advanced','Advancedpricerules(discounts,formulas)')
            ],default='basic',string="PricelistsMethod",config_parameter='product.product_pricelist_setting',
            help="Multipleprices:Pricelistswithfixedpricerulesbyproduct,\nAdvancedrules:enablesadvancedpricerulesforpricelists.")
    product_weight_in_lbs=fields.Selection([
        ('0','Kilograms'),
        ('1','Pounds'),
    ],'Weightunitofmeasure',config_parameter='product.weight_in_lbs',default='0')
    product_volume_volume_in_cubic_feet=fields.Selection([
        ('0','CubicMeters'),
        ('1','CubicFeet'),
    ],'Volumeunitofmeasure',config_parameter='product.volume_in_cubic_feet',default='0')

    @api.onchange('group_product_variant')
    def_onchange_group_product_variant(self):
        """TheproductConfiguratorrequirestheproductvariantsactivated.
        Iftheuserdisablestheproductvariants->disabletheproductconfiguratoraswell"""
        ifself.module_sale_product_configuratorandnotself.group_product_variant:
            self.module_sale_product_configurator=False
        ifself.module_sale_product_matrixandnotself.group_product_variant:
            self.module_sale_product_matrix=False

    @api.onchange('module_sale_product_configurator')
    def_onchange_module_sale_product_configurator(self):
        """TheproductConfiguratorrequirestheproductvariantsactivated
        Iftheuserenablestheproductconfigurator->enabletheproductvariantsaswell"""
        ifself.module_sale_product_configuratorandnotself.group_product_variant:
            self.group_product_variant=True

    @api.onchange('group_multi_currency')
    def_onchange_group_multi_currency(self):
        ifself.group_multi_currency:
            self.group_product_pricelist=True

    @api.onchange('group_product_pricelist')
    def_onchange_group_sale_pricelist(self):
        ifnotself.group_product_pricelistandself.group_sale_pricelist:
            self.group_sale_pricelist=False

    @api.onchange('product_pricelist_setting')
    def_onchange_product_pricelist_setting(self):
        ifself.product_pricelist_setting=='basic':
            self.group_sale_pricelist=False
        else:
            self.group_sale_pricelist=True

    defset_values(self):
        super(ResConfigSettings,self).set_values()
        ifnotself.group_discount_per_so_line:
            pl=self.env['product.pricelist'].search([('discount_policy','=','without_discount')])
            pl.write({'discount_policy':'with_discount'})

    @api.onchange('module_sale_product_matrix')
    def_onchange_module_module_sale_product_matrix(self):
        """TheproductGridConfiguratorrequirestheproductConfiguratoractivated
        IftheuserenablestheGridConfigurator->enabletheproductConfiguratoraswell"""
        ifself.module_sale_product_matrixandnotself.module_sale_product_configurator:
            self.module_sale_product_configurator=True
