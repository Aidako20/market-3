#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields


classProductTemplate(models.Model):
    _inherit='product.template'

    hs_code=fields.Char(
        string="HSCode",
        help="Standardizedcodeforinternationalshippingandgoodsdeclaration.Atthemoment,onlyusedfortheFedExshippingprovider.",
    )
