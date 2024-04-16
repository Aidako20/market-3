#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classProduct(models.Model):
    _inherit="product.product"

    def_count_returned_sn_products(self,sn_lot):
        res=self.env['repair.line'].search_count([
            ('type','=','remove'),
            ('product_uom_qty','=',1),
            ('lot_id','=',sn_lot.id),
            ('state','=','done'),
            ('location_dest_id.usage','=','internal'),
        ])
        returnsuper()._count_returned_sn_products(sn_lot)+res
