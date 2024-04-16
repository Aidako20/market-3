#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportapi,models,fields


classProductTemplate(models.Model):
    _inherit='product.template'

    product_add_mode=fields.Selection([
        ('configurator','ProductConfigurator'),
        ('matrix','OrderGridEntry'),
    ],string='Addproductmode',default='configurator',help="Configurator:chooseattributevaluestoaddthematching\
        productvarianttotheorder.\nGrid:addseveralvariantsatoncefromthegridofattributevalues")

    defget_single_product_variant(self):
        res=super(ProductTemplate,self).get_single_product_variant()
        ifself.has_configurable_attributes:
            res['mode']=self.product_add_mode
        else:
            res['mode']='configurator'
        returnres
