#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields,api,_
fromflectra.exceptionsimportUserError


classSaleOrder(models.Model):
    _inherit='sale.order'

    carrier_id=fields.Many2one('delivery.carrier',string="DeliveryMethod",domain="['|',('company_id','=',False),('company_id','=',company_id)]",help="Fillthisfieldifyouplantoinvoicetheshippingbasedonpicking.")
    delivery_message=fields.Char(readonly=True,copy=False)
    delivery_rating_success=fields.Boolean(copy=False)
    delivery_set=fields.Boolean(compute='_compute_delivery_state')
    recompute_delivery_price=fields.Boolean('Deliverycostshouldberecomputed')
    is_all_service=fields.Boolean("ServiceProduct",compute="_compute_is_service_products")

    @api.depends('order_line')
    def_compute_is_service_products(self):
        forsoinself:
            so.is_all_service=all(line.product_id.type=='service'forlineinso.order_line.filtered(lambdax:notx.display_type))

    def_compute_amount_total_without_delivery(self):
        self.ensure_one()
        delivery_cost=sum([l.price_totalforlinself.order_lineifl.is_delivery])
        returnself.env['delivery.carrier']._compute_currency(self,self.amount_total-delivery_cost,'pricelist_to_company')

    @api.depends('order_line')
    def_compute_delivery_state(self):
        fororderinself:
            order.delivery_set=any(line.is_deliveryforlineinorder.order_line)

    @api.onchange('order_line','partner_id','partner_shipping_id')
    defonchange_order_line(self):
        self.ensure_one()
        delivery_line=self.order_line.filtered('is_delivery')
        ifdelivery_line:
            self.recompute_delivery_price=True

    def_get_update_prices_lines(self):
        """Excludedeliverylinesfrompricelistrecomputationbasedonproductinsteadofcarrier"""
        lines=super()._get_update_prices_lines()
        returnlines.filtered(lambdaline:notline.is_delivery)

    def_remove_delivery_line(self):
        delivery_lines=self.env['sale.order.line'].search([('order_id','in',self.ids),('is_delivery','=',True)])
        ifnotdelivery_lines:
            return
        to_delete=delivery_lines.filtered(lambdax:x.qty_invoiced==0)
        ifnotto_delete:
            raiseUserError(
                _('Youcannotupdatetheshippingcostsonanorderwhereitwasalreadyinvoiced!\n\nThefollowingdeliverylines(product,invoicedquantityandprice)havealreadybeenprocessed:\n\n')
                +'\n'.join(['-%s:%sx%s'%(line.product_id.with_context(display_default_code=False).display_name,line.qty_invoiced,line.price_unit)forlineindelivery_lines])
            )
        to_delete.unlink()

    defset_delivery_line(self,carrier,amount):

        #Removedeliveryproductsfromthesalesorder
        self._remove_delivery_line()

        fororderinself:
            order.carrier_id=carrier.id
            iforder.statein('sale','done'):
                pending_deliveries=order.picking_ids.filtered(
                    lambdap:p.statenotin('done','cancel')andnotany(m.origin_returned_move_idforminp.move_lines))
                pending_deliveries.carrier_id=carrier.id
            order._create_delivery_line(carrier,amount)
        returnTrue

    defaction_open_delivery_wizard(self):
        view_id=self.env.ref('delivery.choose_delivery_carrier_view_form').id
        ifself.env.context.get('carrier_recompute'):
            name=_('Updateshippingcost')
            carrier=self.carrier_id
        else:
            name=_('Addashippingmethod')
            carrier=(
                self.with_company(self.company_id).partner_shipping_id.property_delivery_carrier_id
                orself.with_company(self.company_id).partner_shipping_id.commercial_partner_id.property_delivery_carrier_id
            )
        return{
            'name':name,
            'type':'ir.actions.act_window',
            'view_mode':'form',
            'res_model':'choose.delivery.carrier',
            'view_id':view_id,
            'views':[(view_id,'form')],
            'target':'new',
            'context':{
                'default_order_id':self.id,
                'default_carrier_id':carrier.id,
            }
        }

    def_create_delivery_line(self,carrier,price_unit):
        SaleOrderLine=self.env['sale.order.line']
        context={}
        ifself.partner_id:
            #setdeliverydetailinthecustomerlanguage
            #usedinlocalscopetranslationprocess
            context['lang']=self.partner_id.lang
            carrier=carrier.with_context(lang=self.partner_id.lang)

        #Applyfiscalposition
        taxes=carrier.product_id.taxes_id.filtered(lambdat:t.company_id.id==self.company_id.id)
        taxes_ids=taxes.ids
        ifself.partner_idandself.fiscal_position_id:
            taxes_ids=self.fiscal_position_id.map_tax(taxes,carrier.product_id,self.partner_id).ids

        #Createthesalesorderline

        ifcarrier.product_id.description_sale:
            so_description='%s:%s'%(carrier.name,
                                        carrier.product_id.description_sale)
        else:
            so_description=carrier.name
        values={
            'order_id':self.id,
            'name':so_description,
            'product_uom_qty':1,
            'product_uom':carrier.product_id.uom_id.id,
            'product_id':carrier.product_id.id,
            'tax_id':[(6,0,taxes_ids)],
            'is_delivery':True,
        }
        ifcarrier.invoice_policy=='real':
            values['price_unit']=0
            values['name']+=_('(EstimatedCost:%s)',self._format_currency_amount(price_unit))
        else:
            values['price_unit']=price_unit
        ifcarrier.free_overandself.currency_id.is_zero(price_unit):
            values['name']+='\n'+_('FreeShipping')
        ifself.order_line:
            values['sequence']=self.order_line[-1].sequence+1
        sol=SaleOrderLine.sudo().create(values)
        delcontext
        returnsol

    def_format_currency_amount(self,amount):
        pre=post=u''
        ifself.currency_id.position=='before':
            pre=u'{symbol}\N{NO-BREAKSPACE}'.format(symbol=self.currency_id.symbolor'')
        else:
            post=u'\N{NO-BREAKSPACE}{symbol}'.format(symbol=self.currency_id.symbolor'')
        returnu'{pre}{0}{post}'.format(amount,pre=pre,post=post)

    @api.depends('order_line.is_delivery','order_line.is_downpayment')
    def_get_invoice_status(self):
        super()._get_invoice_status()
        fororderinself:
            iforder.invoice_statusin['no','invoiced']:
                continue
            order_lines=order.order_line.filtered(lambdax:notx.is_deliveryandnotx.is_downpaymentandnotx.display_type)
            ifall(line.product_id.invoice_policy=='delivery'andline.invoice_status=='no'forlineinorder_lines):
                order.invoice_status='no'

    def_get_estimated_weight(self):
        self.ensure_one()
        weight=0.0
        fororder_lineinself.order_line.filtered(lambdal:l.product_id.typein['product','consu']andnotl.is_deliveryandnotl.display_typeandl.product_uom_qty>0):
            weight+=order_line.product_qty*order_line.product_id.weight
        returnweight


classSaleOrderLine(models.Model):
    _inherit='sale.order.line'

    is_delivery=fields.Boolean(string="IsaDelivery",default=False)
    product_qty=fields.Float(compute='_compute_product_qty',string='ProductQty',digits='ProductUnitofMeasure')
    recompute_delivery_price=fields.Boolean(related='order_id.recompute_delivery_price')

    @api.depends('product_id','product_uom','product_uom_qty')
    def_compute_product_qty(self):
        forlineinself:
            ifnotline.product_idornotline.product_uomornotline.product_uom_qty:
                line.product_qty=0.0
                continue
            line.product_qty=line.product_uom._compute_quantity(line.product_uom_qty,line.product_id.uom_id)

    defunlink(self):
        forlineinself:
            ifline.is_delivery:
                line.order_id.carrier_id=False
        super(SaleOrderLine,self).unlink()

    def_is_delivery(self):
        self.ensure_one()
        returnself.is_delivery

    #overridetoallowdeletionofdeliverylineinaconfirmedorder
    def_check_line_unlink(self):
        """
        ExtendthealloweddeletionpolicyofSOlines.

        Linesthataredeliverylinescanbedeletedfromaconfirmedorder.

        :rtype:recordsetsale.order.line
        :returns:setoflinesthatcannotbedeleted
        """

        undeletable_lines=super()._check_line_unlink()
        returnundeletable_lines.filtered(lambdaline:notline.is_delivery)
