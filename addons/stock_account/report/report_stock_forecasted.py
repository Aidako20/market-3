#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels
fromflectra.tools.float_utilsimportfloat_is_zero,float_repr


classReplenishmentReport(models.AbstractModel):
    _inherit='report.stock.report_product_product_replenishment'

    def_compute_draft_quantity_count(self,product_template_ids,product_variant_ids,wh_location_ids):
        """Overridestocomputesthevaluationsofthestock."""
        res=super()._compute_draft_quantity_count(product_template_ids,product_variant_ids,wh_location_ids)
        ifnotself.user_has_groups('stock.group_stock_manager'):
            returnres
        domain=self._product_domain(product_template_ids,product_variant_ids)
        company=self.env['stock.location'].browse(wh_location_ids).mapped('company_id')
        svl=self.env['stock.valuation.layer'].search(domain+[('company_id','=',company.id)])
        domain_quants=[
            ('company_id','=',company.id),
            ('location_id','in',wh_location_ids)
        ]
        ifproduct_template_ids:
            domain_quants+=[('product_id.product_tmpl_id','in',product_template_ids)]
        else:
            domain_quants+=[('product_id','in',product_variant_ids)]
        quants=self.env['stock.quant'].search(domain_quants)
        currency=svl.currency_idorself.env.company.currency_id
        total_quantity=sum(svl.mapped('quantity'))
        #Becausewecanhavenegativequantities,`total_quantity`maybeequaltozeroevenifthewarehouse's`quantity`ispositive.
        ifsvlandnotfloat_is_zero(total_quantity,precision_rounding=svl.product_id.uom_id.rounding):
            value=sum(svl.mapped('value'))*(sum(quants.mapped('quantity'))/total_quantity)
        else:
            value=0
        value=float_repr(value,precision_digits=currency.decimal_places)
        ifcurrency.position=='after':
            value='%s%s'%(value,currency.symbol)
        else:
            value='%s%s'%(currency.symbol,value)
        res['value']=value
        returnres
