#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportapi,fields,models


classSaleOrderLine(models.Model):
    _inherit="sale.order.line"

    margin=fields.Float(
        "Margin",compute='_compute_margin',
        digits='ProductPrice',store=True,groups="base.group_user")
    margin_percent=fields.Float(
        "Margin(%)",compute='_compute_margin',store=True,groups="base.group_user",group_operator="avg")
    purchase_price=fields.Float(
        string='Cost',compute="_compute_purchase_price",
        digits='ProductPrice',store=True,readonly=False,
        groups="base.group_user")

    @api.depends('product_id','company_id','currency_id','product_uom')
    def_compute_purchase_price(self):
        forlineinself:
            ifnotline.product_id:
                line.purchase_price=0.0
                continue
            line=line.with_company(line.company_id)
            product=line.product_id
            product_cost=product.standard_price
            ifnotproduct_cost:
                #Ifthestandard_priceis0
                #Avoidunnecessarycomputations
                #andcurrencyconversions
                ifnotline.purchase_price:
                    line.purchase_price=0.0
                continue
            fro_cur=product.cost_currency_id
            to_cur=line.currency_idorline.order_id.currency_id
            ifline.product_uomandline.product_uom!=product.uom_id:
                product_cost=product.uom_id._compute_price(
                    product_cost,
                    line.product_uom,
                )
            line.purchase_price=fro_cur._convert(
                from_amount=product_cost,
                to_currency=to_cur,
                company=line.company_idorself.env.company,
                date=line.order_id.date_orderorfields.Date.today(),
                round=False,
            )ifto_curandproduct_costelseproduct_cost
            #Thepricelistmaynothavebeenset,thereforenoconversion
            #isneededbecausewedon'tknowthetargetcurrency..

    @api.depends('price_subtotal','product_uom_qty','purchase_price')
    def_compute_margin(self):
        forlineinself:
            line.margin=line.price_subtotal-(line.purchase_price*line.product_uom_qty)
            line.margin_percent=line.price_subtotalandline.margin/line.price_subtotal


classSaleOrder(models.Model):
    _inherit="sale.order"

    margin=fields.Monetary("Margin",compute='_compute_margin',store=True)
    margin_percent=fields.Float(
        "Margin(%)",compute='_compute_margin',store=True,group_operator='avg'
    )

    @api.depends('order_line.margin','amount_untaxed')
    def_compute_margin(self):
        ifnotall(self._ids):
            fororderinself:
                order.margin=sum(order.order_line.mapped('margin'))
                order.margin_percent=order.amount_untaxedandorder.margin/order.amount_untaxed
        else:
            self.env["sale.order.line"].flush(['margin'])
            #Onbatchrecordsrecomputation(e.g.atinstall),computethemargins
            #withasingleread_groupqueryforbetterperformance.
            #Thisisn'tdoneinanonchangeenvironmentbecause(partof)thedata
            #maynotbestoredindatabase(newrecordsorunsavedmodifications).
            grouped_order_lines_data=self.env['sale.order.line'].read_group(
                [
                    ('order_id','in',self.ids),
                ],['margin','order_id'],['order_id'])
            mapped_data={m['order_id'][0]:m['margin']formingrouped_order_lines_data}
            fororderinself:
                order.margin=mapped_data.get(order.id,0.0)
                order.margin_percent=order.amount_untaxedandorder.margin/order.amount_untaxed
