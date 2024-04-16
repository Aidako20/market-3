#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classSaleOrderLine(models.Model):
    _inherit='sale.order.line'

    @api.depends('move_ids','move_ids.stock_valuation_layer_ids','move_ids.picking_id.state')
    def_compute_purchase_price(self):
        lines_without_moves=self.browse()
        forlineinself:
            product=line.product_id.with_company(line.company_id)
            ifnotline.move_ids:
                lines_without_moves|=line
            elifproduct.categ_id.property_cost_method!='standard':
                purch_price=product._compute_average_price(0,line.product_uom_qty,line.move_ids)
                ifline.product_uomandline.product_uom!=product.uom_id:
                    purch_price=product.uom_id._compute_price(purch_price,line.product_uom)
                to_cur=line.currency_idorline.order_id.currency_id
                line.purchase_price=product.cost_currency_id._convert(
                    from_amount=purch_price,
                    to_currency=to_cur,
                    company=line.company_idorself.env.company,
                    date=line.order_id.date_orderorfields.Date.today(),
                    round=False,
                )ifto_curandpurch_priceelsepurch_price
        returnsuper(SaleOrderLine,lines_without_moves)._compute_purchase_price()
