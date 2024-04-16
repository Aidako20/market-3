#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importlogging

fromflectraimportapi,fields,models

_logger=logging.getLogger(__name__)


classSaleOrder(models.Model):
    _inherit='sale.order'

    amount_delivery=fields.Monetary(
        compute='_compute_amount_delivery',
        string='DeliveryAmount',
        help="Theamountwithouttax.",store=True,tracking=True)

    def_compute_website_order_line(self):
        super(SaleOrder,self)._compute_website_order_line()
        fororderinself:
            order.website_order_line=order.website_order_line.filtered(lambdal:notl.is_delivery)

    @api.depends('order_line.price_unit','order_line.tax_id','order_line.discount','order_line.product_uom_qty')
    def_compute_amount_delivery(self):
        fororderinself:
            ifself.env.user.has_group('account.group_show_line_subtotals_tax_excluded'):
                order.amount_delivery=sum(order.order_line.filtered('is_delivery').mapped('price_subtotal'))
            else:
                order.amount_delivery=sum(order.order_line.filtered('is_delivery').mapped('price_total'))

    def_check_carrier_quotation(self,force_carrier_id=None):
        self.ensure_one()
        DeliveryCarrier=self.env['delivery.carrier']

        ifself.only_services:
            self.write({'carrier_id':None})
            self._remove_delivery_line()
            returnTrue
        else:
            self=self.with_company(self.company_id)
            #attempttousepartner'spreferredcarrier
            ifnotforce_carrier_idandself.partner_shipping_id.property_delivery_carrier_id:
                force_carrier_id=self.partner_shipping_id.property_delivery_carrier_id.id

            carrier=force_carrier_idandDeliveryCarrier.browse(force_carrier_id)orself.carrier_id
            available_carriers=self._get_delivery_methods()
            ifcarrier:
                ifcarriernotinavailable_carriers:
                    carrier=DeliveryCarrier
                else:
                    #settheforcedcarrieratthebeginningofthelisttobeverfiedfirstbelow
                    available_carriers-=carrier
                    available_carriers=carrier+available_carriers
            ifforce_carrier_idornotcarrierorcarriernotinavailable_carriers:
                fordeliveryinavailable_carriers:
                    verified_carrier=delivery._match_address(self.partner_shipping_id)
                    ifverified_carrier:
                        carrier=delivery
                        break
                self.write({'carrier_id':carrier.id})
            self._remove_delivery_line()
            ifcarrier:
                res=carrier.rate_shipment(self)
                ifres.get('success'):
                    self.set_delivery_line(carrier,res['price'])
                    self.delivery_rating_success=True
                    self.delivery_message=res['warning_message']
                else:
                    self.set_delivery_line(carrier,0.0)
                    self.delivery_rating_success=False
                    self.delivery_message=res['error_message']

        returnbool(carrier)

    def_get_delivery_methods(self):
        address=self.partner_shipping_id
        #searchingonwebsite_publishedwillalsosearchforavailablewebsite(_searchmethodoncomputedfield)
        returnself.env['delivery.carrier'].sudo().search([('website_published','=',True)]).available_carriers(address)

    def_cart_update(self,product_id=None,line_id=None,add_qty=0,set_qty=0,**kwargs):
        """Overridetoupdatecarrierquotationifquantitychanged"""

        self._remove_delivery_line()

        #Whenyouupdateacart,itisnotenouftoremovethe"deliverycost"line
        #Thecarriermightalsobeinvalid,eg:ifyouboughtthingsthataretooheavy
        #->thismaycauseabugifyougotothecheckoutscreen,chooseacarrier,
        #   thenupdateyourcart(thecartbecomesuneditable)
        self.write({'carrier_id':False})

        values=super(SaleOrder,self)._cart_update(product_id,line_id,add_qty,set_qty,**kwargs)

        returnvalues
