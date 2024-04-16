#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,api,_
fromflectra.exceptionsimportUserError


classChooseDeliveryCarrier(models.TransientModel):
    _name='choose.delivery.carrier'
    _description='DeliveryCarrierSelectionWizard'

    order_id=fields.Many2one('sale.order',required=True,ondelete="cascade")
    partner_id=fields.Many2one('res.partner',related='order_id.partner_id',required=True)
    carrier_id=fields.Many2one(
        'delivery.carrier',
        string="ShippingMethod",
        help="Choosethemethodtodeliveryourgoods",
        required=True,
    )
    delivery_type=fields.Selection(related='carrier_id.delivery_type')
    delivery_price=fields.Float()
    display_price=fields.Float(string='Cost',readonly=True)
    currency_id=fields.Many2one('res.currency',related='order_id.currency_id')
    company_id=fields.Many2one('res.company',related='order_id.company_id')
    available_carrier_ids=fields.Many2many("delivery.carrier",compute='_compute_available_carrier',string="AvailableCarriers")
    invoicing_message=fields.Text(compute='_compute_invoicing_message')
    delivery_message=fields.Text(readonly=True)

    @api.onchange('carrier_id')
    def_onchange_carrier_id(self):
        self.delivery_message=False
        ifself.delivery_typein('fixed','base_on_rule'):
            vals=self._get_shipment_rate()
            ifvals.get('error_message'):
                return{'error':vals['error_message']}
        else:
            self.display_price=0
            self.delivery_price=0

    @api.onchange('order_id')
    def_onchange_order_id(self):
        #fixedandbase_on_ruledeliverypricewillcomputedoneachcarrierchangesononeedtorecomputehere
        ifself.carrier_idandself.order_id.delivery_setandself.delivery_typenotin('fixed','base_on_rule'):
            vals=self._get_shipment_rate()
            ifvals.get('error_message'):
                warning={
                    'title':'%sError'%self.carrier_id.name,
                    'message':vals.get('error_message'),
                    'type':'notification',
                }
                return{'warning':warning}

    @api.depends('carrier_id')
    def_compute_invoicing_message(self):
        self.ensure_one()
        ifself.carrier_id.invoice_policy=='real':
            self.invoicing_message=_('Theshippingpricewillbesetoncethedeliveryisdone.')
        else:
            self.invoicing_message=""

    @api.depends('partner_id')
    def_compute_available_carrier(self):
        forrecinself:
            carriers=self.env['delivery.carrier'].search(['|',('company_id','=',False),('company_id','=',rec.order_id.company_id.id)])
            rec.available_carrier_ids=carriers.available_carriers(rec.order_id.partner_shipping_id)ifrec.partner_idelsecarriers

    def_get_shipment_rate(self):
        vals=self.carrier_id.rate_shipment(self.order_id)
        ifvals.get('success'):
            self.delivery_message=vals.get('warning_message',False)
            self.delivery_price=vals['price']
            self.display_price=vals['carrier_price']
            return{}
        return{'error_message':vals['error_message']}

    defupdate_price(self):
        vals=self._get_shipment_rate()
        ifvals.get('error_message'):
            raiseUserError(vals.get('error_message'))
        return{
            'name':_('Addashippingmethod'),
            'type':'ir.actions.act_window',
            'view_mode':'form',
            'res_model':'choose.delivery.carrier',
            'res_id':self.id,
            'target':'new',
        }

    defbutton_confirm(self):
        self.order_id.set_delivery_line(self.carrier_id,self.delivery_price)
        self.order_id.write({
            'recompute_delivery_price':False,
            'delivery_message':self.delivery_message,
        })
