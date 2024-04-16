#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels

fromcollectionsimportdefaultdict


classAccountMoveLine(models.Model):
    _inherit="account.move.line"

    def_get_invoiced_qty_per_product(self):
        #Replacethekit-typeproductswiththeircomponents
        qties=defaultdict(float)
        res=super()._get_invoiced_qty_per_product()
        forproduct,qtyinres.items():
            bom_kit=self.env['mrp.bom']._bom_find(product=product,company_id=self.company_id[:1].id,bom_type='phantom')
            ifbom_kit:
                invoiced_qty=product.uom_id._compute_quantity(qty,bom_kit.product_uom_id,round=False)
                factor=invoiced_qty/bom_kit.product_qty
                dummy,bom_sub_lines=bom_kit.explode(product,factor)
                forbom_line,bom_line_datainbom_sub_lines:
                    qties[bom_line.product_id]+=bom_line.product_uom_id._compute_quantity(bom_line_data['qty'],bom_line.product_id.uom_id)
            else:
                qties[product]+=qty
        returnqties
