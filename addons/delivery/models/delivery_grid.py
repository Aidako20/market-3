#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields,api,_
fromflectra.tools.safe_evalimportsafe_eval
fromflectra.exceptionsimportUserError,ValidationError


classPriceRule(models.Model):
    _name="delivery.price.rule"
    _description="DeliveryPriceRules"
    _order='sequence,list_price,id'

    @api.depends('variable','operator','max_value','list_base_price','list_price','variable_factor')
    def_compute_name(self):
        forruleinself:
            name='if%s%s%.02fthen'%(rule.variable,rule.operator,rule.max_value)
            ifrule.list_base_priceandnotrule.list_price:
                name='%sfixedprice%.02f'%(name,rule.list_base_price)
            elifrule.list_priceandnotrule.list_base_price:
                name='%s%.02ftimes%s'%(name,rule.list_price,rule.variable_factor)
            else:
                name='%sfixedprice%.02fplus%.02ftimes%s'%(name,rule.list_base_price,rule.list_price,rule.variable_factor)
            rule.name=name

    name=fields.Char(compute='_compute_name')
    sequence=fields.Integer(required=True,default=10)
    carrier_id=fields.Many2one('delivery.carrier','Carrier',required=True,ondelete='cascade')

    variable=fields.Selection([('weight','Weight'),('volume','Volume'),('wv','Weight*Volume'),('price','Price'),('quantity','Quantity')],required=True,default='weight')
    operator=fields.Selection([('==','='),('<=','<='),('<','<'),('>=','>='),('>','>')],required=True,default='<=')
    max_value=fields.Float('MaximumValue',required=True)
    list_base_price=fields.Float(string='SaleBasePrice',digits='ProductPrice',required=True,default=0.0)
    list_price=fields.Float('SalePrice',digits='ProductPrice',required=True,default=0.0)
    variable_factor=fields.Selection([('weight','Weight'),('volume','Volume'),('wv','Weight*Volume'),('price','Price'),('quantity','Quantity')],'VariableFactor',required=True,default='weight')


classProviderGrid(models.Model):
    _inherit='delivery.carrier'

    delivery_type=fields.Selection(selection_add=[
        ('base_on_rule','BasedonRules'),
        ],ondelete={'base_on_rule':lambdarecs:recs.write({
            'delivery_type':'fixed','fixed_price':0,
        })})
    price_rule_ids=fields.One2many('delivery.price.rule','carrier_id','PricingRules',copy=True)

    defbase_on_rule_rate_shipment(self,order):
        carrier=self._match_address(order.partner_shipping_id)
        ifnotcarrier:
            return{'success':False,
                    'price':0.0,
                    'error_message':_('Error:thisdeliverymethodisnotavailableforthisaddress.'),
                    'warning_message':False}

        try:
            price_unit=self._get_price_available(order)
        exceptUserErrorase:
            return{'success':False,
                    'price':0.0,
                    'error_message':e.args[0],
                    'warning_message':False}

        price_unit=self._compute_currency(order,price_unit,'company_to_pricelist')

        return{'success':True,
                'price':price_unit,
                'error_message':False,
                'warning_message':False}

    def_get_conversion_currencies(self,order,conversion):
        ifconversion=='company_to_pricelist':
            from_currency,to_currency=order.company_id.currency_id,order.pricelist_id.currency_id
        elifconversion=='pricelist_to_company':
            from_currency,to_currency=order.currency_id,order.company_id.currency_id

        returnfrom_currency,to_currency

    def_compute_currency(self,order,price,conversion):
        from_currency,to_currency=self._get_conversion_currencies(order,conversion)
        iffrom_currency.id==to_currency.id:
            returnprice
        returnfrom_currency._convert(price,to_currency,order.company_id,order.date_orderorfields.Date.today())

    def_get_price_available(self,order):
        self.ensure_one()
        self=self.sudo()
        order=order.sudo()
        total=weight=volume=quantity=0
        total_delivery=0.0
        forlineinorder.order_line:
            ifline.state=='cancel':
                continue
            ifline.is_delivery:
                total_delivery+=line.price_total
            ifnotline.product_idorline.is_delivery:
                continue
            ifline.product_id.type=="service":
                continue
            qty=line.product_uom._compute_quantity(line.product_uom_qty,line.product_id.uom_id)
            weight+=(line.product_id.weightor0.0)*qty
            volume+=(line.product_id.volumeor0.0)*qty
            quantity+=qty
        total=(order.amount_totalor0.0)-total_delivery

        total=self._compute_currency(order,total,'pricelist_to_company')

        returnself._get_price_from_picking(total,weight,volume,quantity)

    def_get_price_dict(self,total,weight,volume,quantity):
        '''Hookallowingtoretrievedicttobeusedin_get_price_from_picking()function.
        Hooktobeoverriddenwhenweneedtoaddsomefieldtoproductanduseitinvariablefactorfrompricerules.'''
        return{
            'price':total,
            'volume':volume,
            'weight':weight,
            'wv':volume*weight,
            'quantity':quantity
        }

    def_get_price_from_picking(self,total,weight,volume,quantity):
        price=0.0
        criteria_found=False
        price_dict=self._get_price_dict(total,weight,volume,quantity)
        ifself.free_overandtotal>=self.amount:
            return0
        forlineinself.price_rule_ids:
            test=safe_eval(line.variable+line.operator+str(line.max_value),price_dict)
            iftest:
                price=line.list_base_price+line.list_price*price_dict[line.variable_factor]
                criteria_found=True
                break
        ifnotcriteria_found:
            raiseUserError(_("Nopricerulematchingthisorder;deliverycostcannotbecomputed."))

        returnprice

    defbase_on_rule_send_shipping(self,pickings):
        res=[]
        forpinpickings:
            carrier=self._match_address(p.partner_id)
            ifnotcarrier:
                raiseValidationError(_('Thereisnomatchingdeliveryrule.'))
            res=res+[{'exact_price':p.carrier_id._get_price_available(p.sale_id)ifp.sale_idelse0.0, #TODOcleanme
                          'tracking_number':False}]
        returnres

    defbase_on_rule_get_tracking_link(self,picking):
        returnFalse

    defbase_on_rule_cancel_shipment(self,pickings):
        raiseNotImplementedError()
