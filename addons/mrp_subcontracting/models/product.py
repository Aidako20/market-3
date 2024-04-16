#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classSupplierInfo(models.Model):
    _inherit='product.supplierinfo'

    is_subcontractor=fields.Boolean('Subcontracted',compute='_compute_is_subcontractor',help="Chooseavendoroftypesubcontractorifyouwanttosubcontracttheproduct")

    @api.depends('name','product_id','product_tmpl_id')
    def_compute_is_subcontractor(self):
        forsupplierinself:
            boms=supplier.product_id.variant_bom_ids
            boms|=supplier.product_tmpl_id.bom_ids.filtered(lambdab:notb.product_id)
            supplier.is_subcontractor=supplier.nameinboms.subcontractor_ids
